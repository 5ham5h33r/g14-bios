"""Check research metadata, inventories, source hashes and relative links."""
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


releases = load("data/releases.json")
for version, item in releases["releases"].items():
    for key in ("zip_sha256", "capsule_sha256"):
        check(bool(re.fullmatch(r"[0-9a-f]{64}", item[key])), f"Invalid {key} for {version}")
    check(item["url"].startswith("https://dlcdnets.asus.com/"), f"Unexpected source host for {version}")

for version in ("310", "312"):
    rows = load(f"data/310-312/{version}-inventory.json")
    check(len({r["key"] for r in rows}) == len(rows), f"Duplicate inventory keys in {version}")
    check(next(r["sha256"] for r in rows if r["key"] == "root") == releases["releases"][version]["uefi_body_sha256"],
          f"UEFI-body inventory hash mismatch for {version}")

dbx = load("data/310-312/dbx-diff.json")
check(len(dbx["added"]) == 59 and not dbx["removed"], "Unexpected dbx entry delta")
check(dbx["new_count"] - dbx["old_count"] == 59, "Inconsistent dbx counts")
for table in load("data/310-312/battery-policy-tables.json"):
    raw = bytes(x for row in table["rows"] for x in row)
    check(hashlib.sha256(raw).hexdigest() == table["sha256"], "Policy table checksum mismatch")
    check(len(table["rows"]) == 9 and all(len(row) == 8 for row in table["rows"]), "Invalid policy table shape")
coverage = load("data/310-312/ghidra-coverage.json")
check(len(coverage["images"]) == 20, "Ghidra coverage does not contain 20 completed exports")
for field, total in (("recovered_functions", "total_recovered_functions"),
                     ("decompiled_functions", "total_decompiled_functions")):
    check(sum(image[field] for image in coverage["images"]) == coverage[total],
          f"Inconsistent Ghidra total: {total}")

patches = load("data/310-312/security-patch-matches.json")
check(len(patches) == 5, "Expected TLS and four firmware-update patch records")
for patch in patches:
    for version, key in (("310", "old_module_sha256"), ("312", "new_module_sha256")):
        rows = load(f"data/310-312/{version}-inventory.json")
        check(any(row["sha256"] == patch[key] and patch["file_guid"] in row["key"].upper()
                  for row in rows), f"Patch module missing from inventory: {patch['module']} / {version}")
    check(patch["delta_crl"]["old_guard_pattern_count"] == 0
          and patch["delta_crl"]["new_guard_pattern_count"] == 1,
          f"Inconsistent guard counts: {patch['module']}")

for path in ROOT.rglob("*.md"):
    if any(part in (".git", "local", ".venv") for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8")
    check("—" not in text, f"Em dash in prose: {path.relative_to(ROOT)}")
    check(not re.search(r"C:[/\\]Users[/\\]", text, re.I), f"Local user path in {path.relative_to(ROOT)}")
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
        if target.startswith(("https://", "http://", "#", "mailto:")):
            continue
        local = unquote(target.split("#", 1)[0]).strip("<>")
        check((path.parent / local).exists(), f"Broken link in {path.relative_to(ROOT)}: {target}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)
print("Research metadata, evidence counts and document links pass.")
