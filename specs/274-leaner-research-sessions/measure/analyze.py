#!/usr/bin/env python3
import json, pathlib, collections, statistics, sys
H = pathlib.Path(__file__).parent
S = json.loads((H / "sessions.json").read_text())
M = 1e6


def atot(s):
    return sum(a["tot"] for a in s["agents"])


def things(ss):
    q = sum(s["q"] for s in ss if s["kind"] in ("check", "owed"))
    k = sum(s["k"] for s in ss if s["kind"] in ("check", "owed"))
    m = sum(sum(1 for a in s["agents"] if a["type"] == "entry-drift") for s in ss)
    return q, m, k


groups = collections.OrderedDict()
for s in sorted(S, key=lambda s: s["start"]):
    groups.setdefault(s["group"], []).append(s)

rows = []
for g, ss in groups.items():
    main = sum(s["tot"] for s in ss)
    turns = sum(s["turns"] for s in ss)
    ag = [a for s in ss for a in s["agents"]]
    agt = sum(a["tot"] for a in ag)
    q, m, k = things(ss)
    th = q + m + k
    tot = main + agt
    rows.append({"group": g, "start": ss[0]["start"][:16], "sessions": len(ss), "kinds": dict(collections.Counter(s["kind"] for s in ss)),
                 "checks": sum(1 for s in ss if s["kind"] == "check"), "q": q, "m": m, "k": k, "things": th,
                 "total": tot, "main": main, "agents": agt, "runs": len(ag), "mean_agent": agt / max(len(ag), 1),
                 "peak": max(s["peak"] for s in ss), "mean_turn": main / max(turns, 1), "per_thing": tot / th if th else None,
                 "resumes": sum(len(s["gaps"]) for s in ss)})

sel = sys.argv[1] if len(sys.argv) > 1 else "table"
if sel == "table":
    print(f"{'group':<44}{'start':<17}{'ses':>4}{'chk':>4}{'q/m/k':>9}{'total M':>9}{'main':>7}{'agt':>7}{'runs':>5}{'mAg K':>7}{'peak K':>7}{'mTurn K':>8}{'/thing M':>9}{'res':>4}")
    for r in rows:
        pt = f"{r['per_thing']/M:.2f}" if r["per_thing"] else "-"
        print(f"{r['group'][:43]:<44}{r['start']:<17}{r['sessions']:>4}{r['checks']:>4}{str(r['q'])+'/'+str(r['m'])+'/'+str(r['k']):>9}{r['total']/M:>9.2f}{r['main']/M:>7.2f}{r['agents']/M:>7.2f}{r['runs']:>5}{r['mean_agent']/1e3:>7.0f}{r['peak']/1e3:>7.0f}{r['mean_turn']/1e3:>8.0f}{pt:>9}{r['resumes']:>4}")
    (H / "groups.json").write_text(json.dumps(rows, indent=1))
