# Reproduce the 309 → 310 comparison

Use the [release manifest](../data/releases.json) and the [shared method](method.md). These steps read distributed files. They do not flash a laptop, access EC ports or change NVRAM.

## Acquire and inventory

Install the dependencies from `requirements.txt` in a Python 3.12+ environment. Obtain [UEFIExtract A76](https://github.com/LongSoft/UEFITool/releases/tag/A76) and [iASL 20260408](https://github.com/open-acpica/acpica/releases/tag/20260408) for your OS.

```sh
python -m pip install -r requirements.txt
python tools/firmware.py download 309 310
python tools/firmware.py extract local/firmware/GA403WRAS.309 --uefiextract /path/to/UEFIExtract
python tools/firmware.py extract local/firmware/GA403WRAS.310 --uefiextract /path/to/UEFIExtract
python tools/firmware.py inventory local/firmware/GA403WRAS.309.dump local/309-inventory.json
python tools/firmware.py inventory local/firmware/GA403WRAS.310.dump local/310-inventory.json
python tools/firmware.py diff local/309-inventory.json local/310-inventory.json local/309-310-changes.json
python tools/firmware.py ec-info local/firmware/GA403WRAS.309
python tools/firmware.py ec-info local/firmware/GA403WRAS.310
```

Use `UEFIExtract.exe` on Windows and quote paths containing spaces. Keep extraction warnings and input hashes. Both capsules contain an `0x800`-byte prefix followed by a 32 MiB UEFI image. Header/volume warnings do not themselves identify a change in behavior.

The published 310 inventory is identical to a fresh inventory for this pair, so [inventory-sources.json](../data/309-310/inventory-sources.json) references the existing copy.

## ACPI templates

```sh
python tools/acpi_tables.py inventory local/firmware/GA403WRAS.309.dump local/309-inventory.json 309 local/309-tables.json --aml-dir local/acpi-309
python tools/acpi_tables.py inventory local/firmware/GA403WRAS.310.dump local/310-inventory.json 310 local/310-tables.json --aml-dir local/acpi-310
python tools/acpi_tables.py diff local/309-tables.json local/310-tables.json local/acpi-changes.json
```

Expect **83 distinct tables per image** and **seven changes**. Run `iasl -d` on each `.aml` file in the two local output directories. Compare from `DefinitionBlock` onward so the disassembler's date and local pathname do not inflate the diff. Decompilation synthesizes external declarations; do not interpret those declarations as executable changes.

Pair tables with the inventory's complete `key`, including raw-section instances. Fifteen distinct tables share the `AmdCpmDisplayFeatureDxe` file. Removing all numeric directory ordinals without preserving instance identities would silently discard tables.

The helper finds valid DSDT/SSDT headers at the start of an extracted `body.bin`, bounds the declared length, checks the checksum and deduplicates identical complete table bytes. It does not scan every byte of executables or reconstruct the tables installed by a running BIOS.

## Secure Boot and AMD directories

For each version, copy the decompressed `dbx` raw body under GUID `9D7A05E9-F740-44C3-858B-75586A8F9C8E` into the corresponding local file, then run:

```sh
python tools/firmware.py dbx local/309-dbx.bin local/310-dbx.bin local/dbx-diff.json
python -m psptool -E -j local/firmware/GA403WRAS.309 > local/309-psp.json
python -m psptool -E -j local/firmware/GA403WRAS.310 > local/310-psp.json
```

The dbx parser should report 372 canonical records in each image, with no additions or removals. Its records include the X.509 certificate as well as SHA-256 hashes.

Retain PSPTool's stderr. Match directory positions only after checking their magic, entry counts and entry types; collapse repeated references by address/size within each input. Hash the complete declared range using the parser's capsule-file address. This pass yields 143 distinct nonzero ranges, 80 equal and 63 changed. Protected bodies and unfamiliar generation IDs remain a coverage limit.

UEFIExtract's four `AMD microcode` nodes identify two processor-revision IDs duplicated in the image. Compare `info.txt` and payload hashes; distinguish those raw payloads from PSPTool's larger wrapped entries.

## Setup forms

Obtain [IFRExtractor RS 1.6.1](https://github.com/LongSoft/IFRExtractor-RS/releases/tag/v1.6.1). Its Windows archive URL and hash are in [setup-cores.json](../data/309-310/setup-cores.json).

Copy the decompressed PE body for `Setup`, GUID `899407D7-99FE-43D8-9A21-79EC328CAC21`, from each tree into local `.efi` files. Run:

```sh
ifrextractor local/309-Setup.efi verbose
ifrextractor local/310-Setup.efi verbose
```

The tool writes IFR text beside its input. Use the string package that resolves the ASUS setup prompts, rather than the alternative package with blank labels. Check “Active Performance-cores” and “Active Efficient-cores,” their backing variables, parent conditions and option defaults. The recorded `0x12F1E6` and `0x12F29A` addresses are **file offsets in the extracted 310 Setup body**.

Do not infer a displayed menu from strings alone. IFR describes controls and conditions; setup-browser policy can further affect visibility.

## Code review

The [coverage file](../data/309-310/ghidra-coverage.json) lists each selected image, FFS GUID, input hash and export count. Copy each matching decompressed PE body into an ignored local directory. Ghidra 12.2's PE loader selects the architecture from its header.

```sh
analyzeHeadless local/projects usb4-309 -import local/309-AmdUsb4Dxe.efi -scriptPath tools/ghidra -postScript ExportFunctions.java local/decompiled -analysisTimeoutPerFile 600 -max-cpu 2
analyzeHeadless local/projects usb4-310 -import local/310-AmdUsb4Dxe.efi -scriptPath tools/ghidra -postScript ExportFunctions.java local/decompiled -analysisTimeoutPerFile 600 -max-cpu 2
python tools/match_functions.py local/decompiled/309-AmdUsb4Dxe.efi local/decompiled/310-AmdUsb4Dxe.efi local/usb4-candidates.json --name AmdUsb4Dxe
```

For the new core-sync module, seed the verified indirect callbacks after auto-analysis:

```sh
analyzeHeadless local/projects core-sync-310 -import local/310-AsusActiveEfficientCoresSyncToAmd.efi -scriptPath tools/ghidra -postScript SeedFunctions.java 000007b8 00000a00 00000d44 -postScript ExportFunctions.java local/decompiled -analysisTimeoutPerFile 600 -max-cpu 2
```

The [shared reproduction guide](reproduce.md#ghidra) covers EC extraction and the `InitializeEc.java` loader. Repeat it for 309 and 310 with the Binary loader, `RISCV:LE:32:default`, compiler `gcc`, ROM base zero and RAM at `0x00800000`. Compare actual instructions and data references after candidate pairing; heuristic hashes discard addresses and constants.

For whole-PE instruction triage, use Capstone 5.0.9 and the PE machine type: `0x14C` means IA32, `0x8664` means x86-64. The GOP, recovery and CryptoPPI instances include IA32 code. Disassemble executable sections using their RVAs; the recorded filter removes NOP/INT3, direct branch/call addresses and x86-64 RIP-relative targets before sequence comparison. This filter ranks candidates and does not prove equivalence. TE section bytes also need their stripped-header adjustment when locating raw section data.

Keep complete C/ASM/IFR/ASL exports in `local/`. Publish short relevant excerpts, original interpretation, hashes and coverage. Run:

```sh
python -m unittest discover -s tests -v
python tools/validate.py
```
