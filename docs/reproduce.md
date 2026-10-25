# Reproduce the 310 → 312 comparison

These commands reproduce the initial release pair. For a new version, follow the [release workflow](release-workflow.md) and verify its layout before reusing extraction offsets.

Use Python 3.12 or later. The helper scripts read files; they do not access EC ports, change NVRAM or flash firmware.

```sh
python -m venv .venv
# Activate the environment for your shell.
python -m pip install -r requirements.txt
python tools/firmware.py download 310 312
```

The download command checks both archive and capsule hashes against [the manifest](../data/releases.json). It writes to the ignored `local/firmware/` directory.

## Extract and compare

Get [UEFIExtract A76](https://github.com/LongSoft/UEFITool/releases/tag/A76) for your operating system, then run:

```sh
python tools/firmware.py extract local/firmware/GA403WRAS.310 --uefiextract /path/to/UEFIExtract
python tools/firmware.py extract local/firmware/GA403WRAS.312 --uefiextract /path/to/UEFIExtract
python tools/firmware.py inventory local/firmware/GA403WRAS.310.dump local/310-inventory.json
python tools/firmware.py inventory local/firmware/GA403WRAS.312.dump local/312-inventory.json
python tools/firmware.py diff local/310-inventory.json local/312-inventory.json local/changes.json
python tools/firmware.py ec-info local/firmware/GA403WRAS.312
```

On Windows, replace `/path/to/UEFIExtract` with the quoted path to `UEFIExtract.exe`.

UEFIExtract warns about an Aptio capsule signature, non-UEFI section data and a volume-top file inside a compressed item for these images. Those messages do not mean that this procedure changed the capsule. Keep the original file hash available for checking.

The inventory uses parent identities, GUIDs and an instance ordinal. It preserves duplicate firmware files. Its JSON output has no absolute local paths.

## ACPI and Secure Boot

Find the raw DSDT section in firmware file GUID `C118F50D-391D-45F4-B3D3-11BC931AA56D`. Copy each decompressed `body.bin` into `local/310-dsdt.aml` and `local/312-dsdt.aml`. Use [iASL 20260408](https://github.com/open-acpica/acpica/releases/tag/20260408):

```sh
iasl -d local/310-dsdt.aml
iasl -d local/312-dsdt.aml
```

Find the decompressed raw section under `9D7A05E9-F740-44C3-858B-75586A8F9C8E` for each image. Save the bodies as `local/310-dbx.bin` and `local/312-dbx.bin`, then run:

```sh
python tools/firmware.py dbx local/310-dbx.bin local/312-dbx.bin local/dbx-diff.json
python -m psptool -E -j local/firmware/GA403WRAS.310 > local/310-psp.json
python -m psptool -E -j local/firmware/GA403WRAS.312 > local/312-psp.json
```

PSPTool 3.7 warns about unfamiliar generation IDs in these images. Retain the parsed entries and record those warnings as a coverage limit.

## Ghidra

The recorded pass used **Ghidra 12.2** with **Temurin JDK 25.0.1**. Ghidra's PE loader recognizes the extracted `.efi` module bodies. Export a pair with:

```sh
analyzeHeadless local/projects tls-310 -import local/310-TlsDxe.efi -scriptPath tools/ghidra -postScript ExportFunctions.java local/decompiled -analysisTimeoutPerFile 600 -max-cpu 3
```

Use a different project name for each imported module. The post-script writes full assembly, C output and a function index under the ignored output directory. A script error can occur after Ghidra reports a successful import; check for `EXPORT_DONE` and the resulting `functions.json` before treating the export as complete.

Generate candidate function pairs after exporting both versions:

```sh
python tools/match_functions.py local/decompiled/310-TlsDxe.efi local/decompiled/312-TlsDxe.efi local/TlsDxe-candidates.json --name TlsDxe
```

The matcher removes addresses from heuristic hashes and normalized C. It can hide changed constants or pair unrelated wrappers. Check the instructions and callers before treating a pair as equivalent or naming a behavior change.

For the EC, extract the raw image and entry-point candidates, then import with the Binary loader, `RISCV:LE:32:default`, compiler `gcc`, and base address zero:

```sh
python tools/prepare_ec.py local/firmware/GA403WRAS.312 local/ec-312.bin
analyzeHeadless local/projects ec-312 -import local/ec-312.bin -loader BinaryLoader -processor RISCV:LE:32:default -cspec gcc -scriptPath tools/ghidra -preScript InitializeEc.java local/ec-312.bin.entries -postScript ExportFunctions.java local/decompiled -analysisTimeoutPerFile 600 -max-cpu 3
```

Repeat for 310. `InitializeEc` maps EC RAM at `0x00800000`. It leaves peripheral definitions unresolved.

Full decompilation output belongs in `local/`; commit the short excerpts or original pseudocode needed to support a finding.

## Add another release

Follow the [release workflow](release-workflow.md). Add a pair-specific changelog, evidence directory and coverage record. Update the release index and README, and use the [template](changelog-template.md) to keep the plain-language takeaway ahead of technical findings.

Run the checks before committing:

```sh
python -m unittest discover -s tests -v
python tools/validate.py
```

The GitHub workflow checks scripts, evidence metadata and document links. It does not download or execute firmware. It also does not create a changelog claim from a hash difference.
