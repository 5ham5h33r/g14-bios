# 309 → 310: coverage and open questions

Inputs are the official GA403WR EZ Flash capsules in the [release manifest](../data/releases.json). The public report contains no live machine logs, firmware dump from a running machine, BIOS flash operation or before/after hardware test.

## Completed work

| Area | Completed pass | Limit |
|---|---|---|
| Package identity | Official ZIP download, ZIP/capsule hashes, 32 MiB UEFI-body hashes | Posting and embedded build dates differ |
| UEFI tree | 3,385 / 3,393 inventory nodes; 808 changed nodes, 400 changed leaves | Container deltas repeat child changes |
| PE executables | 140 changed/new instances; section hashes and Capstone text triage | Linear disassembly includes padding/data and misses indirect-flow semantics |
| TE executables | 176 changed instances; section layout/hash comparison | Six have identical section payloads; remaining changes include rebasing and configuration numbering, with incomplete semantic coverage |
| ACPI templates | 83 distinct header-start DSDT/SSDT bodies per image; all decompiled; seven changed | Excludes tables embedded at nonzero offsets or generated at boot; installed-table selection untested |
| Setup forms | IFR extraction in both images; core questions, defaults, backing variables and suppression expressions checked | Menu visibility and hardware core changes untested |
| CPU microcode | Four extracted copies per image; two processor-revision IDs | No per-advisory patch attribution |
| PSP directories | 143 distinct nonzero ranges; 80 equal, 63 changed | Unfamiliar generation IDs; protected bodies not disassembled |
| Secure Boot | Parsed all default dbx signature lists | Enrolled runtime variables may differ |
| EC | RV32IMC recovery, function candidates and instruction review | Incomplete indirect-flow recovery and peripheral definitions |
| Selected UEFI code | Ghidra exports, function pairing and manual review of reported paths | Exporting C does not mean every routine received a semantic audit |

The [machine-readable summary](../data/309-310/summary.json) and [coverage JSON](../data/309-310/ghidra-coverage.json) record **47 image exports**, **15,154 recovered boundaries** and **15,118 C outputs**. This pass produced 46 exports; it reuses the matching 310 EC export from the earlier comparison after checking the input-region hash. An export can omit C for failed or skipped functions; the coverage file retains each entry. Counts describe Ghidra's output, not source functions, fixes or test results.

The selected images cover the EC pair; both versions of AMITSE, Setup, two distinct CpuDxe modules, AMD CCX/NBIO/USB4/FCH/graphics modules, PCI root bridge, IPv6, ASUS setup/WMI/flashing modules, CBS/AOD SMM and Quanta wrappers; plus the new core-sync driver. Module identities and hashes disambiguate repeated names.

Capstone uses **IA32 for six PE instances** and **x86-64 for 134**. Twelve of the 140 have matching normalized instruction text. One PE instance is new. `SmmPciRbIo` has matching section payloads despite a different whole-file hash. Normalization removes some addresses and targets; a match alone cannot establish unchanged behavior.

## Questions for further work

| Question | Starting evidence | Needed next |
|---|---|---|
| Does the NVIDIA ordering change apply to a given machine? | Changed `OemNv2T`; unchanged `Opt2Tabl` | Installed-table identities and firmware selection path for the relevant hardware/configuration |
| Does any change reduce random freezes? | GPU ordering and USB4 startup-polling deltas; NVPS wait remains | Reproducible trigger, traces during the failure and controlled before/after observations |
| Are the new core controls visible and functional? | IFR, variables, AMD sync callback and GNVS fields agree | BIOS-screen check; read-only WMI/CPU topology comparison before considering configuration tests |
| Which UMA size indices map to which allocations? | Five-bit encoding; SMM index bound and lookup | Decode the platform lookup table and its configuration source |
| What changed inside PSP/SMU/MP2 bodies? | Full payload hashes and header versions | Supported disassembly/decryption where applicable, or AMD release documentation |
| What does the changed APCB body configure? | One changed 13,312-byte copy | Decode its type/token records with a matching platform schema |
| What else changes in EZ Flash and setup code? | Expanded code and unmatched candidates | Trace callers, error exits and format/validation consumers |
| Does the SMM clearing change address a named issue? | New zeroing path and SMM register sequence | A matching advisory or upstream/vendor patch with the same trigger and fix |
| Is the IPv6 buffer rewrite sufficient on every error path? | New allocation, resizing and cleanup | Full capacity, overflow and allocation-failure audit |

Hardware testing remains pending for crash rate, sleep residency, docks, battery life, charging, fan behavior and performance. A changed firmware component can motivate a test; its name cannot supply the result.

## Reproduction and tools

Tools: UEFIExtract A76, iASL 20260408, PSPTool 3.7, pefile 2024.8.26, Capstone 5.0.9, IFRExtractor RS 1.6.1, Ghidra 12.2 and Temurin JDK 25.0.1. See the [pair-specific reproduction guide](../docs/reproduce-309-310.md).

The [310 → 312 coverage](coverage.md) applies to the later pair. Its hardware gaps and patch matches should not be treated as measurements of 309 → 310.
