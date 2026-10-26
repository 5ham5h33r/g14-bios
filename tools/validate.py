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

# Historical 309 -> 310 coverage; retain all checks for the later pair above.
sources = load("data/309-310/inventory-sources.json")
pair_inventories = {}
for version, source in sources.items():
    rows = load("data/309-310/" + source)
    pair_inventories[version] = {row["key"]: row for row in rows}
    check(len(pair_inventories[version]) == len(rows), f"Duplicate historical inventory key: {version}")
    check(pair_inventories[version]["root"]["sha256"] == releases["releases"][version]["uefi_body_sha256"],
          f"Historical root hash mismatch: {version}")

summary = load("data/309-310/summary.json")
changes = load("data/309-310/changes.json")
check(len(changes) == summary["changed_nodes"] == 808, "Historical changed-node count mismatch")
check(sum(row["leaf"] for row in changes) == summary["changed_leaves"] == 400,
      "Historical changed-leaf count mismatch")
for version, side in (("309", "old"), ("310", "new")):
    check(len(pair_inventories[version]) == summary["inventory_nodes"][version],
          f"Historical inventory count mismatch: {version}")
    for change in changes:
        if change[side] is not None:
            check(change[side] == pair_inventories[version].get(change["key"]),
                  f"Changed node does not match inventory: {version}/{change['key']}")

tables_by_version = {}
for version in ("309", "310"):
    rows = load(f"data/309-310/acpi/{version}-tables.json")
    tables_by_version[version] = {row["key"]: row for row in rows}
    check(len(rows) == len(tables_by_version[version]) == 83, f"ACPI instance/count mismatch: {version}")
    check(len({row["sha256"] for row in rows}) == 83, f"Duplicate ACPI bytes: {version}")
    for row in rows:
        check(row["sha256"] == pair_inventories[version][row["key"]]["sha256"],
              f"ACPI hash does not match raw inventory: {version}/{row['oem_table']}")
acpi_changes = load("data/309-310/acpi/changes.json")
check(len(acpi_changes) == summary["changed_acpi_tables"] == 7, "Expected seven ACPI template changes")
computed_keys = {key for key in tables_by_version["309"]
                 if tables_by_version["309"][key]["sha256"] != tables_by_version["310"][key]["sha256"]}
check({row["key"] for row in acpi_changes} == computed_keys, "ACPI diff omits or invents an instance")
wait = load("data/309-310/acpi/gpu-wait.json")
check(len(wait) == 2 and wait[0]["snippet"] == wait[1]["snippet"], "GPU wait excerpt differs")
for row in wait:
    check(hashlib.sha256(row["snippet"].encode()).hexdigest() == row["sha256"], "GPU excerpt hash mismatch")

pe = load("data/309-310/pe-triage.json")
te = load("data/309-310/te-triage.json")
check(len(pe) == summary["changed_pe_instances"] == 140, "PE triage count mismatch")
check(sum(row["machine"] == "0x14c" for row in pe) == 6, "IA32 triage coverage mismatch")
check(sum(row["machine"] == "0x8664" for row in pe) == 134, "x86-64 triage coverage mismatch")
check(sum(row["normalized_text_matches"] for row in pe) == summary["pe_normalized_text_matches"] == 12,
      "PE normalized-text count mismatch")
check(len(te) == summary["changed_te_instances"] == 176, "TE triage count mismatch")
check(sum(row["section_payloads_identical"] for row in te) == summary["te_exact_section_payload_matches"] == 6,
      "TE section count mismatch")
for rows in (pe, te):
    for row in rows:
        for version, side in (("309", "old"), ("310", "new")):
            if row[side + "_sha256"] is not None:
                check(pair_inventories[version][row["key"]]["sha256"] == row[side + "_sha256"],
                      f"Executable hash mismatch: {version}/{row['key']}")

coverage = load("data/309-310/ghidra-coverage.json")
check(len(coverage["images"]) == summary["ghidra_images"] == 47, "Historical Ghidra image count mismatch")
for field, total in (("recovered_functions", "total_recovered_functions"),
                     ("decompiled_functions", "total_decompiled_functions")):
    check(sum(row[field] for row in coverage["images"]) == coverage[total], f"Historical total mismatch: {total}")
for row in coverage["images"]:
    check(bool(re.fullmatch(r"[0-9a-f]{64}", row["sha256"])), f"Invalid Ghidra input hash: {row['input']}")
    check(row["recovered_functions"] - row["decompiled_functions"] == len(row["export_errors"]),
          f"Historical C-output omissions mismatch: {row['input']}")
    if row["module"] != "EC":
        check(any(item["sha256"] == row["sha256"] and row["file_guid"] in key.upper()
                  for key, item in pair_inventories[row["version"]].items()),
              f"Ghidra image missing from inventory: {row['input']}")
candidate_paths = list((ROOT / "data/309-310/function-candidates").glob("*.json"))
check(len(candidate_paths) == 23, "Expected 23 paired-image candidate records")
for path in candidate_paths:
    row = json.loads(path.read_text(encoding="utf-8"))
    check(len(row["pairs"]) == row["matched"], f"Candidate-pair count mismatch: {path.name}")
    check(row["matched"] + len(row["unmatched_old"]) == row["old_function_count"],
          f"Old candidate coverage mismatch: {path.name}")
    check(row["matched"] + len(row["unmatched_new"]) == row["new_function_count"],
          f"New candidate coverage mismatch: {path.name}")

psp = load("data/309-310/psp-comparison.json")
check(len(psp) == 143 and sum(row["same"] for row in psp) == 80, "PSP range comparison mismatch")
dbx = load("data/309-310/dbx-diff.json")
check(dbx["old_count"] == dbx["new_count"] == 372 and not dbx["added"] and not dbx["removed"],
      "Historical dbx content delta mismatch")
for row in load("data/309-310/microcode.json") + load("data/309-310/agesa.json"):
    check(pair_inventories[row["version"]][row["key"]]["sha256"] == row["sha256"],
          "Component evidence hash mismatch")
setup = load("data/309-310/setup-cores.json")
check(len(setup["questions"]) == 2 and all(row["default"] == 255 for row in setup["questions"]),
      "Core-control default/coverage mismatch")

for path in ROOT.rglob("*.md"):
    if any(part in (".git", "local", ".venv") for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8")
    if path.parent == ROOT / "changelog" and re.fullmatch(r"\d+-to-\d+\.md", path.name):
        sections = re.findall(r"^## (.+)$", text, re.M)
        check(bool(sections) and sections[0] == "Plain-language takeaway",
              f"Changelog must open with a plain-language takeaway: {path.name}")
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
