# Method

## Confidence

| Label | Evidence |
|---|---|
| Confirmed bytes | The published images contain the stated values or entries. |
| Confirmed code | Disassembly establishes the condition, write or call. |
| Inferred effect | Code and a known interface support the interpretation; a hardware test is missing. |
| Unresolved | A difference remains, but its role is unclear. |

A match to an OpenSSL patch establishes the code change. It does not establish firmware reachability, a working attack or the complete OpenSSL version. Likewise, a different power-policy selector does not establish a measured wattage on a running laptop.

## Inputs

Use the EZ Flash ZIP packages from ASUS. Check the ZIP against ASUS's published SHA-256 before unpacking it. Record the capsule hash too: ZIP compression or repackaging can change the archive while leaving its member unchanged.

The initial 310 image contains a November 21, 2025 BIOS build date, despite ASUS's July 22, 2026 posting date. Keep build dates and download-page dates separate.

The work here compares distributed images. A laptop's current flash can contain different NVRAM, board data or enrolled Secure Boot variables.

## Address conventions

ASUS wraps each 32 MiB image in a 2,048-byte capsule header.

| Address | Meaning |
|---|---|
| Capsule-file offset | Byte offset in the unzipped `GA403WRAS.310` or `.312`, including the header |
| UEFI-body offset | Capsule-file offset minus `0x800` |
| DSDT offset | Offset inside the decompressed DSDT section |
| Module RVA | Address inside a decompressed PE executable; independent of its capsule position |
| EC code address | Address in the raw EC image; add `0x81800` to get the capsule-file offset |
| EC RAM address | RISC-V runtime memory, such as `0x00800370`; this is not a file offset |

For example, new EC code address `0x15C64` corresponds to capsule offset `0x97464`. `lui a5, 0x800` loads `0x00800000`; it does not load `0x08000000`.

## Comparison passes

1. Verify the downloads and extract the capsule members.
2. Use UEFIExtract to unpack the firmware tree. Compare leaf payloads, retaining GUIDs and repeated instances.
3. Compare PE section payloads after relocation. A changed PE-header location can change a hash while leaving the code and data untouched.
4. Decode TE sections using their `StrippedSize`. Check differences against each image's load address. Several early-boot sections in this comparison contain rebased pointers and no remaining payload difference.
5. Parse authenticated EFI signature lists. Compare signature type, owner and signature bytes; ignore the authentication timestamp when counting new entries.
6. Use iASL for ACPI and PSPTool for the AMD directory entries it recognizes. Compare full payload bytes, not PSPTool's abbreviated digest display.
7. Disassemble x86 code and the EC's RV32IMC code. Use Ghidra for function recovery and decompilation, then check significant conditions against instructions.
8. Match library changes against upstream source patches. Cite the exact commit when the source match is clear.

## Function matching limits

The Ghidra export records recovered functions, instruction counts and heuristic hashes. A mnemonic hash can help find a moved routine. It can also hide changed constants or callees. The matcher is a review aid, not an equivalence proof.

Ghidra splits some shared tails and misidentifies code in data. Its function count depends on the loader, entry points and analysis settings. The EC import also generates warnings around unmodeled peripheral addresses and a few data boundaries. Coverage counts describe the tool run; they do not count source functions with certainty.

## Publication

Keep firmware downloads, full disassembly and full decompiler output in `local/`. Publish hashes, changed offsets, short relevant instruction sequences and original explanations. Keep the reproduction tools separate from conclusions so another reader can disagree with an interpretation without having to repeat acquisition work.
