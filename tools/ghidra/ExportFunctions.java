// Ghidra headless post-script. Keep full decompilation output local.
// @category Firmware
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import com.google.gson.Gson;

public class ExportFunctions extends GhidraScript {
    String hash(String s) throws Exception {
        byte[] d=MessageDigest.getInstance("SHA-256").digest(s.getBytes(StandardCharsets.UTF_8));
        return HexFormat.of().formatHex(d);
    }
    public void run() throws Exception {
        String[] args=getScriptArgs();
        Path out=Paths.get(args[0],currentProgram.getName());Files.createDirectories(out);
        boolean decompile=args.length<2 || !args[1].equals("index");
        DecompInterface dec=new DecompInterface();
        if(decompile){dec.toggleCCode(true);dec.toggleSyntaxTree(false);dec.openProgram(currentProgram);}
        ArrayList<Map<String,Object>> index=new ArrayList<>();
        FunctionIterator it=currentProgram.getFunctionManager().getFunctions(true);
        int count=0,success=0;
        while(it.hasNext() && !monitor.isCancelled()){
            Function f=it.next();String entry=f.getEntryPoint().toString();String filename=entry.replace(':','_');
            StringBuilder asm=new StringBuilder(),shape=new StringBuilder(),semantic=new StringBuilder();
            InstructionIterator ii=currentProgram.getListing().getInstructions(f.getBody(),true);
            int n=0;
            while(ii.hasNext()){
                Instruction i=ii.next();n++;
                asm.append(i.getAddress()).append(" ").append(i).append("\n");
                shape.append(i.getMnemonicString()).append("/").append(i.getNumOperands()).append("\n");
                String text=i.toString();
                if(i.getFlowType().isCall() || i.getFlowType().isJump())text=i.getMnemonicString()+" TARGET";
                text=text.replaceAll("0x[0-9a-fA-F]+", "#");semantic.append(text).append("\n");
            }
            Map<String,Object> row=new LinkedHashMap<>();row.put("entry",entry);row.put("name",f.getName());
            row.put("body_bytes",f.getBody().getNumAddresses());row.put("instructions",n);
            row.put("shape_sha256",hash(shape.toString()));row.put("semantic_sha256",hash(semantic.toString()));
            row.put("decompiled",false);
            Files.writeString(out.resolve(filename+".asm"),asm.toString());
            if(decompile && !f.isThunk()){
                DecompileResults r=dec.decompileFunction(f,20,monitor);
                if(r.decompileCompleted() && r.getDecompiledFunction()!=null){
                    Files.writeString(out.resolve(filename+".c"),r.getDecompiledFunction().getC());
                    row.put("decompiled",true);success++;
                }else{row.put("decompile_error",r.getErrorMessage());}
            }
            index.add(row);count++;
            if(count%500==0)println("EXPORTED "+currentProgram.getName()+" "+count);
        }
        Files.writeString(out.resolve("functions.json"),new Gson().toJson(index));
        println("EXPORT_DONE "+currentProgram.getName()+" functions="+count+" decompiled="+success);
        dec.dispose();
    }
}
