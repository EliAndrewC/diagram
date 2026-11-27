# phases.py EVENTLOG CLONE SINCE_UTC_ISO [UNTIL_UTC_ISO]: the gate's Phase lines of one tree in a window, seconds summed by step
import sys,json,collections,datetime
log,clone,since=sys.argv[1:4]; until=sys.argv[4] if len(sys.argv)>4 else "9"
p=lambda s: datetime.datetime.fromisoformat(s.replace("Z","+00:00"))
tot=collections.Counter(); n=collections.Counter()
for l in open(log,errors="replace"):
    if '"Phase"' not in l or clone not in l: continue
    try: r=json.loads(l)
    except ValueError: continue
    if r.get("clone","").rsplit("/",1)[-1]!=clone or not (since<=r["t0"]<until): continue
    tot[r["step"]]+=(p(r["t1"])-p(r["t0"])).total_seconds(); n[r["step"]]+=1
print("  ".join(f"{s}: {n[s]} lines {tot[s]:.1f}s" for s in sorted(tot)) or "no Phase lines")
