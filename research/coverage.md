# 310 → 312: coverage and open questions

This comparison covers the official 310 and 312 EZ Flash packages in [the release manifest](../data/releases.json). Each future release pair gets its own coverage record through the [release workflow](../docs/release-workflow.md).

## Completed passes

| Region | Work completed | Limits |
|---|---|---|
| Capsule and UEFI tree | Unpacked both images; hashed payloads and recorded GUID instances | Container differences repeat changes in child sections |
| PE modules | Compared section payloads and disassembled changed code | Relocation/header differences need separate treatment |
| Early-boot TE modules | Checked section layouts and eight-byte address shifts | Targeted to this release pair |
| DSDT | Decompiled and compared the complete table | Windows-driver interpretation needs a hardware test |
| Secure Boot defaults | Parsed signature lists and compared entries | New hashes have not all been mapped to executables |
| AMD directories | Compared full bytes for enumerated entries | PSPTool warns about unfamiliar generation IDs |
| EC application | RV32IMC disassembly, function recovery and targeted call-chain review | Peripheral definitions and some shared tails remain unresolved |
| Setup/TLS/update code | Ghidra export and function matching, with manual review of significant candidates | Heuristic matching can pair unrelated wrappers |

The [Ghidra coverage record](../data/310-312/ghidra-coverage.json) contains counts for 20 imports: old/new EC, AMITSE, TlsDxe, four FmpDxe variants, SbRun, SbRunSmm and PrjDxe. A recovered function count is a tool result, not a source-function count or a count of fixes.

The public candidate-pair files under `data/310-312/function-candidates/` retain addresses and matching methods. Full C and assembly exports remain local. Address removal in a heuristic hash can hide a changed callee or constant; the changelog includes only changes that received additional review.

## Open questions

| Question | Starting point | Evidence needed |
|---|---|---|
| Does the new care latch change custom 60% limits? | EC-01/02 | Charge/current traces under both releases with the same settings |
| Does tier 3 persist after unplugging? | EC-03 | Budget telemetry through the transition and after settling |
| What do the two omitted status transfers represent? | EC-04 | Register definitions or a live trace of the source and destination words |
| What cleanup do the changed error exits perform? | EC-05 | Better function boundaries and names for the peripheral routines |
| Which setup properties changed on screen? | UI-01 | Field definitions or before/after BIOS screenshots |
| Does `$SETUPPASSWDANY` have a functional change? | AMITSE data/reference review | A call-path or data-consumer explanation |
| Which binaries match the 59 new dbx hashes? | `dbx-diff.json` | A match against an identified upstream revocation dataset |
| Are the DANE and delta-CRL paths reachable? | LIB-01/02 | Firmware configuration and a call-path analysis to an exposed flow |

## Hardware claims

Hardware validation is pending for charging, fan curves, CPU/GPU wattage, performance, sleep behavior and GPU crash rates. The EC power-selector change supports a battery-policy hypothesis that needs before/after telemetry.

Inputs are distributed update images. This comparison includes no live flash-chip dump or EC trace.

## Corrections to the initial notes

The second pass resolves the early SoC/startup differences as address rebasing, identifies the two OpenSSL patch matches, and traces the battery-transition policy reset. It also corrects EC RAM notation to `0x0080xxxx`; capsule-file offsets in the initial notes retain their meaning.

The [release index](../changelog/README.md) tracks published comparisons and pending analysis. Coverage begins with 310 → 312; subsequent releases need separate evidence and coverage notes.
