# 309 → 310 evidence

All files contain research metadata or short relevant excerpts. Firmware images, full ASL/C exports and local hardware diagnostics are excluded.

| File | Contents |
|---|---|
| [inventory-sources.json](inventory-sources.json) | Inventory locations; the 310 inventory reuses the identical published file under `310-312` |
| [309-inventory.json](309-inventory.json) | Complete extracted-tree inventory with hashes and instance keys |
| [changes.json](changes.json) | Paired changed/new/removed nodes, including a leaf flag and PE-section comparisons |
| [pe-triage.json](pe-triage.json) | Changed PE instances, architecture and heuristic instruction-diff counts |
| [te-triage.json](te-triage.json) | Changed TE instances and exact section-payload hashes |
| [acpi changes](acpi/changes.json) | All seven changed templates; per-version inventories and small ASL diffs in the same directory |
| [microcode.json](microcode.json) | Raw microcode copies, processor-revision identifiers, dates, hashes and capsule offsets |
| [agesa.json](agesa.json) | AGESA identification strings with module hashes and file offsets |
| [psp-comparison.json](psp-comparison.json) | PSPTool range identities, header versions, lengths and complete payload hashes |
| [psptool-warnings.json](psptool-warnings.json) | Parser coverage warnings |
| [setup-cores.json](setup-cores.json) | New form questions, opcode excerpts, defaults and variable mapping |
| [ec-review.json](ec-review.json) | EC identity, metadata initializer and relocation-review measurements |
| [dbx-diff.json](dbx-diff.json) | Canonical Secure Boot revocation-entry comparison |
| [ghidra-coverage.json](ghidra-coverage.json) | Imported image identities, recovered boundaries, C-output counts and omissions |
| [summary.json](summary.json) | Inventory and analysis totals |

The `function-candidates/` files contain heuristic matches, including unmatched boundaries. Their `semantic_sha256` label describes the matching algorithm, not proven semantic equivalence. Review changed constants, callees, globals and data consumers before using a match as a finding.

PSP and microcode capsule offsets include the `0x800` capsule prefix. PE RVAs, extracted-file offsets and EC-relative addresses are different coordinate systems; the research notes label each. UEFIExtract calls the microcode header's processor-revision identifier “CPU signature”; it is not a CPUID EAX value.

Raw hash differences can come from authentication data, headers, rebasing, rebuilt containers or changed payloads. Overlap byte-difference counts in the PSP records do not account for inserted bytes or explain behavior.
