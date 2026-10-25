"""Suggest function pairs from Ghidra exports for manual review.

Hashes remove operands and addresses; a match does not prove equivalent code.
"""
import argparse
import pathlib,json,collections,re,difflib
def normal_c(path):
    if not path.exists():return ''
    t=path.read_text(errors='replace')
    t=re.sub(r'\b(?:FUN|LAB|DAT|UNK|PTR|BYTE|WORD|DWORD|QWORD)_[0-9a-f]+\b','ADDRESS',t)
    t=re.sub(r'\b(?:FUN|LAB)_ram_[0-9a-f]+\b','ADDRESS',t)
    t=re.sub(r'\bDAT_ram_000[0-9a-f]+\b','ROM_ADDRESS',t)
    t=re.sub(r'_[0-9a-f]{8}\b','_ADDR',t)
    return t
def match(old, new, output, name):
    aa=json.loads((old/'functions.json').read_text());bb=json.loads((new/'functions.json').read_text())
    a={r['entry']:r for r in aa};b={r['entry']:r for r in bb};pairs=[]
    for field in ['semantic_sha256','shape_sha256']:
        ca=collections.defaultdict(list);cb=collections.defaultdict(list)
        for k,r in a.items():ca[r[field]].append(k)
        for k,r in b.items():cb[r[field]].append(k)
        for h in ca.keys()&cb.keys():
            if len(ca[h])==len(cb[h]):
                for ka,kb in zip(ca[h],cb[h]):pairs.append((ka,kb,field));a.pop(ka);b.pop(kb)
    def cfile(folder,k):return folder/(k.replace(':','_')+'.c')
    ca=collections.defaultdict(list);cb=collections.defaultdict(list)
    for k,r in a.items():ca[normal_c(cfile(old,k))].append(k)
    for k,r in b.items():cb[normal_c(cfile(new,k))].append(k)
    for t in ca.keys()&cb.keys():
        if t and len(ca[t])==len(cb[t]):
            for ka,kb in zip(ca[t],cb[t]):pairs.append((ka,kb,'normalized_c'));a.pop(ka);b.pop(kb)
    # Match similar unmatched function bodies, retaining a score for manual review.
    for ka in list(a):
        ta=normal_c(cfile(old,ka))
        best=(0,None)
        for kb in b:
            tb=normal_c(cfile(new,kb))
            if not ta or not tb or min(len(ta),len(tb))/max(len(ta),len(tb))<.5:continue
            seq=difflib.SequenceMatcher(None,ta,tb)
            if seq.quick_ratio()<best[0]:continue
            score=seq.ratio()
            if score>best[0]:best=(score,kb)
        if best[0]>.55:
            kb=best[1];pairs.append((ka,kb,'similar_c:'+str(round(best[0],3))));a.pop(ka);b.pop(kb)
    changes=[]
    for ka,kb,method in pairs:
        ta,tb=normal_c(cfile(old,ka)),normal_c(cfile(new,kb))
        if ta!=tb:changes.append({'old':ka,'new':kb,'match':method,'old_bytes':next(r['body_bytes'] for r in aa if r['entry']==ka),'new_bytes':next(r['body_bytes'] for r in bb if r['entry']==kb)})
    result={'module':name,'old_function_count':len(aa),'new_function_count':len(bb),'matched':len(pairs),'changed_normalized_c':sorted(changes,key=lambda r:r['old']),'unmatched_old':list(a),'unmatched_new':list(b),'pairs':pairs}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result,indent=2) + '\n')
    print(name,'old/new',len(aa),len(bb),'matched',len(pairs),'changed C',len(changes),'unmatched',list(a),list(b),flush=True)
    print(json.dumps(result['changed_normalized_c'],indent=2),flush=True)
if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("old", type=pathlib.Path, help="Old export directory containing functions.json and C files")
    p.add_argument("new", type=pathlib.Path, help="New export directory")
    p.add_argument("output", type=pathlib.Path)
    p.add_argument("--name", default="module")
    args = p.parse_args()
    match(args.old, args.new, args.output, args.name)
