"""Inventory header-start DSDT/SSDT templates in a UEFIExtract tree.

Embedded tables inside executables or larger raw blobs are outside this scan.
Keep the inventory's section-instance key: stripping directory ordinals alone
would collapse different raw sections in the same firmware file.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def table_metadata(data):
    if len(data) < 36 or data[:4] not in (b"DSDT", b"SSDT"):
        return None
    size = struct.unpack_from("<I", data, 4)[0]
    if size < 36 or size > len(data):
        return None
    table = data[:size]
    if sum(table) % 256:
        return None
    return {
        "signature": table[:4].decode("ascii"),
        "oem_id": table[10:16].decode("ascii", errors="replace").strip(" \0"),
        "oem_table": table[16:24].decode("ascii", errors="replace").strip(" \0"),
        "bytes": size,
        "sha256": hashlib.sha256(table).hexdigest(),
    }


def scan(dump, inventory, version, aml_dir=None):
    dump = dump.resolve()
    seen = set()
    records = []
    if aml_dir:
        aml_dir.mkdir(parents=True, exist_ok=True)
    for row in inventory:
        path = (dump / row["display_path"] / "body.bin").resolve()
        if not path.is_relative_to(dump):
            raise ValueError("Inventory path escapes extraction directory")
        if not path.is_file():
            continue
        with path.open("rb") as stream:
            header = stream.read(36)
            if len(header) < 36 or header[:4] not in (b"DSDT", b"SSDT"):
                continue
            size = struct.unpack_from("<I", header, 4)[0]
            if size < 36 or size > path.stat().st_size:
                continue
            data = header + stream.read(size - 36)
        metadata = table_metadata(data)
        if metadata is None or metadata["sha256"] in seen:
            continue
        seen.add(metadata["sha256"])
        metadata.update(version=version, key=row["key"],
                        source=path.relative_to(dump).as_posix())
        records.append(metadata)
        if aml_dir:
            (aml_dir / (metadata["sha256"] + ".aml")).write_bytes(data)
    return records


def compare(old, new):
    a, b = [{row["key"]: row for row in rows} for rows in (old, new)]
    if len(a) != len(old) or len(b) != len(new):
        raise ValueError("Duplicate ACPI instance key")
    return [{"key": key, "old": a.get(key), "new": b.get(key)}
            for key in sorted(a.keys() | b.keys())
            if key not in a or key not in b or a[key]["sha256"] != b[key]["sha256"]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inv = sub.add_parser("inventory")
    inv.add_argument("dump", type=Path)
    inv.add_argument("inventory", type=Path)
    inv.add_argument("version")
    inv.add_argument("output", type=Path)
    inv.add_argument("--aml-dir", type=Path)
    diff = sub.add_parser("diff")
    diff.add_argument("old", type=Path)
    diff.add_argument("new", type=Path)
    diff.add_argument("output", type=Path)
    args = parser.parse_args()
    def read(path):
        return json.loads(path.read_text(encoding="utf-8"))
    if args.command == "inventory":
        result = scan(args.dump, read(args.inventory), args.version, args.aml_dir)
    else:
        result = compare(read(args.old), read(args.new))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(len(result), "records")


if __name__ == "__main__":
    main()
