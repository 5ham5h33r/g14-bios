// @category Firmware
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import java.nio.file.*;
public class InitializeEc extends GhidraScript {
 public void run() throws Exception {
    MemoryBlock ram=currentProgram.getMemory().createUninitializedBlock("EC_RAM",toAddr(0x800000L),0x10000,false);
    ram.setRead(true);ram.setWrite(true);ram.setExecute(false);
    for(String line:Files.readAllLines(Paths.get(getScriptArgs()[0]))){
       if(line.isBlank())continue;
       Address address=toAddr(Long.parseLong(line.trim(),16));
       disassemble(address);
       if(getFunctionAt(address)==null && getFunctionContaining(address)==null)createFunction(address,null);
    }
 }
}
