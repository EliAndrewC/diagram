import sys,json,re,glob,bisect,statistics as st,collections
from datetime import datetime,timezone
EV="/diagram/.clones/diagram-backlog/.git/l7r-events/"
OUT=sys.argv[1]
f=lambda s: datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()
# load samples
S=[]
for l in open(EV+"samples/mem-samples.jsonl"):
    try: e=json.loads(l); S.append((f(e["utc"]),e["load1"],len(e.get("held",[]))))
    except: pass
for p in glob.glob(EV+"mem-samples*.log"):
    for l in open(p):
        m=re.match(r"(\S+Z) .*load=([\d.]+)(?: builders=(\d+))?",l)
        if m: S.append((f(m.group(1)),float(m.group(2)),int(m.group(3) or -1)))
S.sort(); ts=[s[0] for s in S]
def load(t0,t1):
    i=bisect.bisect_left(ts,t0-15); j=bisect.bisect_right(ts,t1+15)
    v=[S[k][1] for k in range(i,j)]
    return (max(v),S[i][2]) if v else (None,None)
seen=set(); runs=collections.defaultdict(lambda: {"crates":set(),"t1":0,"code":0})
for p in glob.glob(EV+"*.jsonl"):
  for l in open(p):
    if '"Phase"' not in l: continue
    try: e=json.loads(l)
    except: continue
    if e.get("task")=="T342" or e["t0"]>="2026-11-27T04:58" or e["t"]<"2026-11-26T17:00" or e.get("step")!="test" or e.get("make") not in ("rust-test","builder-checks"): continue
    if not re.search(r"diagram-backlog-(t\d+|b\d+)$",e.get("clone","")): continue
    k=(e["t0"],e["t1"],e["clone"],e["make"],tuple(e.get("crates",[])))
    if k in seen: continue
    seen.add(k)
    r=runs[(e["clone"].split("/")[-1],e["make"],e["t0"])]
    r["crates"].update(c.split("/")[-1] for c in e.get("crates",[]))
    r["t1"]=max(r["t1"],f(e["t1"])); r["code"]=max(r["code"],e["code"]); r["task"]=e.get("task","")
rows=[]
for (cl,mk,t0),r in sorted(runs.items(),key=lambda x:x[0][2]):
    w=r["t1"]-f(t0); L,h=load(f(t0),r["t1"])
    rows.append((t0,cl,mk,"+".join(sorted(r["crates"])),round(w,2),r["code"],r["task"],L,h))
with open(OUT,"w") as o:
    print("t0\ttree\tmake\tcrates\twall_s\tcode\ttask\tload1_max\theld",file=o)
    for x in rows: print("\t".join(map(str,x)),file=o)
print("runs",len(rows),"total wall s",round(sum(x[4] for x in rows),1))
hang=[x for x in rows if x[4]>300]; print("over 300 s",len(hang),round(sum(x[4] for x in hang),1))
rr=[x for x in rows if x[4]<=300]
w=sorted(x[4] for x in rr); print("non-hang runs",len(rr),"sum",round(sum(w),1),"median",st.median(w),"p90",w[int(.9*(len(w)-1))])
withL=[x for x in rr if x[7] is not None]; print("with load",len(withL))
for lo,hi in [(0,8),(8,22),(22,44),(44,999)]:
    g=sorted(x[4] for x in withL if lo<=x[7]<hi)
    if g: print(f"load {lo}-{hi}: n={len(g)} median {st.median(g)} p90 {g[int(.9*(len(g)-1))]} sum {round(sum(g),1)}")
for mk in ("rust-test","builder-checks"):
    g=sorted(x[4] for x in rr if x[2]==mk); print(mk,len(g),"sum",round(sum(g),1),"median",st.median(g))
pc=collections.defaultdict(list)
for x in rr:
    for c in x[3].split("+"): pc[c].append(x[4]) if "+" not in x[3] else None
for c,v in sorted(pc.items(),key=lambda z:-sum(z[1]))[:8]:
    v=sorted(v); print("single-crate",c,len(v),"sum",round(sum(v),1),"median",st.median(v),"p90",v[int(.9*(len(v)-1))])
