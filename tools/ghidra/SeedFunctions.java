// Seed manually verified callback entry points that auto-analysis missed.
// Arguments: addresses in the current program's address space, e.g. 000007b8.
// @category Firmware
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class SeedFunctions extends GhidraScript {
    public void run() throws Exception {
        for (String arg : getScriptArgs()) {
            Address address = toAddr(arg);
            if (address == null || !currentProgram.getMemory().contains(address)) {
                throw new IllegalArgumentException("Address outside program memory: " + arg);
            }
            Function function = getFunctionAt(address);
            if (function == null) {
                disassemble(address);
                function = createFunction(address, null);
            }
            if (function == null) {
                throw new IllegalStateException("Cannot create function at " + address);
            }
            println("SEEDED " + function.getEntryPoint());
        }
    }
}
