"""Acquire and inspect GA403WR firmware. No device access or flash operations."""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import urllib.request
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verified(data: bytes, expected: str) -> bytes:
    actual = sha256(data)
    if actual != expected.lower():
        raise ValueError(f"SHA-256 mismatch: expected {expected}, received {actual}")
    return data


def parse_info(path: Path) -> dict:
    """UEFIExtract repeats Type fields; retain the first human-readable value."""
    info = {}
    for key, value in re.findall(r"^([^:\n]+): (.*)$", path.read_text(errors="replace"), re.M):
        info.setdefault(key.strip(), value.strip())
    return info


def parse_signature_lists(data: bytes, authenticated=True) -> list[dict]:
    """Parse EFI_SIGNATURE_LIST records after optional AUTHENTICATION_2."""
    offset = 0
    if authenticated:
        if len(data) < 40:
            raise ValueError("Truncated authentication header")
        auth_size = struct.unpack_from("<I", data, 16)[0]
        if auth_size < 24 or auth_size > len(data) - 16:
            raise ValueError("Invalid authentication certificate length")
        offset = 16 + auth_size
    records = []
    while offset < len(data):
        if len(data) - offset < 28:
            raise ValueError("Truncated signature-list header")
        kind = str(uuid.UUID(bytes_le=data[offset:offset + 16]))
        size, header_size, signature_size = struct.unpack_from("<III", data, offset + 16)
        payload_start = offset + 28 + header_size
        end = offset + size
        if size < 28 + header_size or end > len(data) or signature_size <= 16:
            raise ValueError("Invalid signature-list bounds")
        if (end - payload_start) % signature_size:
            raise ValueError("Signature-list payload is not an integral number of entries")
        for pos in range(payload_start, end, signature_size):
            records.append({"type": kind,
                            "owner": str(uuid.UUID(bytes_le=data[pos:pos + 16])),
                            "signature": data[pos + 16:pos + signature_size].hex()})
        offset = end
    return records


def pe_sections(data: bytes) -> list[dict] | None:
    if data[:2] != b"MZ" and data[:4] != b"PE\0\0":
        return None
    import pefile
    try:
        pe = pefile.PE(data=data)
        pe.relocate_image(0)
        # Compare payloads instead of changing DOS/NT header locations.
        return [{"name": s.Name.rstrip(b"\0").decode("ascii", errors="replace"),
                 "size": len(s.get_data()), "sha256": sha256(s.get_data())}
                for s in pe.sections]
    except pefile.PEFormatError:
        return None


def inventory(dump: Path) -> list[dict]:
    rows = []

    def visit(directory: Path, key: str):
        info_path = directory / "info.txt"
        meta = parse_info(info_path) if info_path.exists() else {}
        body = directory / "body.bin"
        if body.exists():
            data = body.read_bytes()
            row = {"key": key, "display_path": directory.relative_to(dump).as_posix(),
                   "type": meta.get("Type"), "subtype": meta.get("Subtype"),
                   "metadata": meta, "size": len(data), "sha256": sha256(data)}
            sections = pe_sections(data)
            if sections is not None:
                row["pe_sections"] = sections
            rows.append(row)
        counts = collections.Counter()
        children = sorted((p for p in directory.iterdir() if p.is_dir()),
                          key=lambda p: (int(p.name.split(" ", 1)[0])
                                         if p.name.split(" ", 1)[0].isdigit() else 10**9, p.name))
        for child in children:
            inf = child / "info.txt"
            cm = parse_info(inf) if inf.exists() else {}
            identity = ":".join(str(x) for x in
                                [cm.get("Type", "node"), cm.get("Subtype", ""),
                                 cm.get("File GUID") or cm.get("Section GUID")
                                 or cm.get("Variable GUID") or cm.get("Text") or ""])
            counts[identity] += 1
            visit(child, f"{key}/{identity}#{counts[identity]}")
    visit(dump, "root")
    return rows


def download(args):
    releases = load_json(args.manifest)["releases"]
    args.dest.mkdir(parents=True, exist_ok=True)
    for version in args.versions:
        item = releases[version]
        target = args.dest / f"GA403WRAS{version}.zip"
        data = target.read_bytes() if target.exists() else urllib.request.urlopen(item["url"], timeout=60).read()
        verified(data, item["zip_sha256"])
        target.write_bytes(data)
        # Write the named member only; never trust arbitrary archive paths.
        with zipfile.ZipFile(target) as archive:
            payload = archive.read(item["member"])
        verified(payload, item["capsule_sha256"])
        (args.dest / item["member"]).write_bytes(payload)
        print(f"{version}: ZIP and capsule hashes match")


def difference(args):
    old = {x["key"]: x for x in load_json(args.old)}
    new = {x["key"]: x for x in load_json(args.new)}
    rows = []
    for key in sorted(old.keys() | new.keys()):
        a, b = old.get(key), new.get(key)
        if a and b and a["sha256"] == b["sha256"]:
            continue
        row = {"key": key, "old": a, "new": b,
               "status": "added" if a is None else "removed" if b is None else "changed"}
        if a and b and a.get("pe_sections") is not None and b.get("pe_sections") is not None:
            row["pe_section_payloads_match"] = a["pe_sections"] == b["pe_sections"]
        rows.append(row)
    save_json(args.output, rows)
    print(f"{len(rows)} changed tree nodes; parent containers repeat changes in their children")


def dbx(args):
    old, new = [parse_signature_lists(p.read_bytes()) for p in (args.old, args.new)]
    canonical = lambda rows: {json.dumps(r, sort_keys=True) for r in rows}
    a, b = canonical(old), canonical(new)
    save_json(args.output, {"old_count": len(old), "new_count": len(new),
                           "added": [json.loads(x) for x in sorted(b - a)],
                           "removed": [json.loads(x) for x in sorted(a - b)]})


def ec_info(args):
    data = args.capsule.read_bytes()
    board = re.search(rb"ASUS NJT\(GA403W_MB1\)[ #]*", data)
    version = re.search(rb"03\.[0-9]{2}F#", data)
    date = re.search(rb"20[0-9]{2}/[0-9]{2}/[0-9]{2} b[0-9]{2}#", data)
    if not all((board, version, date)):
        raise ValueError("Expected GA403W EC identifiers were not found")
    print(json.dumps({"capsule_sha256": sha256(data),
                      "board": board.group().decode(), "version": version.group().decode(),
                      "build": date.group().decode(), "version_file_offset": hex(version.start())}, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    q = sub.add_parser("download")
    q.add_argument("versions", nargs="+")
    q.add_argument("--manifest", type=Path, default=ROOT / "data/releases.json")
    q.add_argument("--dest", type=Path, default=ROOT / "local/firmware")
    q.set_defaults(run=download)
    q = sub.add_parser("extract")
    q.add_argument("capsule", type=Path)
    q.add_argument("--uefiextract", required=True)
    q.set_defaults(run=lambda a: subprocess.run([a.uefiextract, str(a.capsule), "all"], check=True))
    q = sub.add_parser("inventory")
    q.add_argument("dump", type=Path)
    q.add_argument("output", type=Path)
    q.set_defaults(run=lambda a: save_json(a.output, inventory(a.dump)))
    q = sub.add_parser("diff")
    q.add_argument("old", type=Path)
    q.add_argument("new", type=Path)
    q.add_argument("output", type=Path)
    q.set_defaults(run=difference)
    q = sub.add_parser("dbx")
    q.add_argument("old", type=Path)
    q.add_argument("new", type=Path)
    q.add_argument("output", type=Path)
    q.set_defaults(run=dbx)
    q = sub.add_parser("ec-info")
    q.add_argument("capsule", type=Path)
    q.set_defaults(run=ec_info)
    args = p.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
