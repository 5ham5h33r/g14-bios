"""Extract the known GA403WR EC region and generate RV32IMC entry candidates."""
import argparse
from pathlib import Path
import capstone

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("capsule", type=Path)
p.add_argument("output", type=Path)
args = p.parse_args()
data = args.capsule.read_bytes()
if b"ITE51300-SB-V.00" not in data[0x81800:0x81900] or b"ASUS NJT(GA403W_MB1)" not in data[0x897A0:0x89800]:
    raise SystemExit("The expected GA403W EC layout is missing; inspect this release before choosing offsets.")
ec = data[0x81800:0xD1800]
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_bytes(ec)
cs = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
cs.skipdata = True
entries = set()
for ins in cs.disasm(ec[0x8000:0x42000], 0x8000):
    if ((ins.mnemonic == "c.addi" and ins.op_str.startswith("sp, -"))
        or ins.mnemonic == "c.addi16sp"
        or (ins.mnemonic == "addi" and ins.op_str.startswith("sp, sp, -"))):
        entries.add(ins.address)
    if ins.mnemonic in ("jal", "c.jal"):
        try:
            entries.add(ins.address + int(ins.op_str, 0))
        except ValueError:
            pass
entries = sorted(x for x in entries if 0x8000 <= x < 0x42000)
args.output.with_suffix(args.output.suffix + ".entries").write_text("\n".join(f"{x:x}" for x in entries) + "\n")
print(f"Wrote {len(ec)} bytes and {len(entries)} entry candidates; review function boundaries in Ghidra.")
