import os,re,sys,subprocess
R="/diagram/.clones/diagram-backlog-t271/"
def ntests(p):
    try: return len(re.findall(r"#\[test\]",open(p).read()))
    except FileNotFoundError: return 0
def files_under(d):
    out=[]
    for root,_,fs in os.walk(d):
        out+= [os.path.join(root,f) for f in fs if f.endswith(".rs")]
    return out
CR={"land":"rust/gate/crates/land/src/land","rustc":"rust/gate/crates/rustc/src/rustc","plan":"rust/gate/crates/plan/src/plan",
    "task":"rust/gate/crates/task/src","shared":"rust/guard/shared/src","guard":"rust/guard/src"}
def crate_of(f):
    for c,d in CR.items():
        base=d.rsplit("/src",1)[0]+"/src/"
        if f.startswith(base): return c
def modset(c,f):
    """return the set of test files a selection by top module would run, or None for whole crate"""
    d=CR[c]; src=d.rsplit("/src",1)[0]+"/src"
    if c in ("task","shared","guard"):
        top=src if c!="guard" else src
        rel=os.path.relpath(f,src).split("/")
        if c=="guard" and rel[0]=="guards" and len(rel)>1: # guards::<name>
            name=rel[1][:-3] if rel[1].endswith(".rs") else rel[1]
            return ("guards::"+name,[f"{src}/guards/{name}.rs"]+files_under(R+f"{src}/guards/{name}"))
        if len(rel)==1 and rel[0] in ("lib.rs","main.rs","guards.rs"): return None
        name=rel[0][:-3] if rel[0].endswith(".rs") else rel[0]
        return (name,[f"{src}/{name}.rs"]+files_under(R+f"{src}/{name}"))
    rel=os.path.relpath(f,d)
    if rel.startswith(".."): return None   # crate root file (land.rs, lib.rs)
    parts=rel.split("/")
    if parts[0]=="tests" or parts[0]=="tests.rs":
        if len(parts)==1: return None
        name=parts[1][:-3] if parts[1].endswith(".rs") else parts[1]
    else:
        name=parts[0][:-3] if parts[0].endswith(".rs") else parts[0]
    fs=[f"{d}/{name}.rs"]+files_under(R+f"{d}/{name}")+[f"{d}/tests/{name}.rs"]+files_under(R+f"{d}/tests/{name}")
    return (name,fs)
commits=sys.argv[1:]
for cm in commits:
    subj=subprocess.run(["git","-C",R,"log","-1","--format=%s",cm],capture_output=True,text=True).stdout[:50]
    fl=subprocess.run(["git","-C",R,"show","--name-only","--format=",cm],capture_output=True,text=True).stdout.split()
    fl=[x for x in fl if x.endswith(".rs")]
    per={}
    for f in fl:
        c=crate_of(f)
        if not c: continue
        per.setdefault(c,{"whole":False,"mods":{}})
        m=modset(c,f)
        if m is None: per[c]["whole"]=True
        else: per[c]["mods"][m[0]]=m[1]
    print(f"== {cm} {subj}")
    for c,v in per.items():
        src=CR[c].rsplit("/src",1)[0]+"/src"
        tot=sum(ntests(p) for p in files_under(R+src))
        sel=set()
        for fs in v["mods"].values(): sel.update(fs)
        n=sum(ntests(p if p.startswith("/") else R+p) for p in sel)
        print(f"  {c}: crate tests {tot}; modules {sorted(v['mods'])} tests {n} ({100*n/tot:.0f}%); root file touched: {v['whole']} -> conservative selection {tot if v['whole'] else n}")
