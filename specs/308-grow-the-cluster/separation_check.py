import io, sys, math
from contextlib import redirect_stdout
sys.path.insert(0, "/diagram/.clones/diagram-performance/.claude/skills/diagram")
from l7r.diagram.hamletgen import HamletSpec, plan_site
from l7r.diagram.hamletgen.driver import STAGES, roll_scope
from l7r.diagram.hamletgen.plan import beyond_the_band
from l7r.diagram.hamletgen.homesteads import growth as G
from l7r.diagram.settlement import Settlement
import l7r.diagram.hamletgen.homesteads.stages as ST
REF = {"name": "Inashiro", "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated", "fixtures_min": {"shrine": 1}}
src = {}; rows = []
real_ss = G.settled_seat
def ss(center, standing, guess, angle, gap, scale, reach_at):
    q = real_ss(center, standing, guess, angle, gap, scale, reach_at)
    if q is not None: src[(round(q[0],3), round(q[1],3))] = (center, standing, reach_at(q))
    return q
G.settled_seat = ss
def sep(c1, r1, c2, r2):
    # boxes from reaches (w,e,n,s); separation = max of the two axis gaps
    a = (c1[0]-r1[0], c1[0]+r1[1], c1[1]-r1[2], c1[1]+r1[3]); b = (c2[0]-r2[0], c2[0]+r2[1], c2[1]-r2[2], c2[1]+r2[3])
    gx = max(b[0]-a[1], a[0]-b[1]); gy = max(b[2]-a[3], a[2]-b[3])
    return (max(gx, gy), gx, gy)
for seed in [int(x) for x in sys.argv[2].split(",")]:
    with beyond_the_band():
        plan = plan_site(HamletSpec(seed=seed, households=int(sys.argv[1]), **REF))
    s = Settlement(W=plan.W, H=plan.H, seed=seed)
    tp = s.try_place; ingrow=[False]
    real_gm = getattr(G, "_real", G.grow_the_margin); G._real = real_gm
    def gm(*a, **k):
        ingrow[0] = True
        try: return real_gm(*a, **k)
        finally: ingrow[0] = False
    G.grow_the_margin = gm; ST.grow_the_margin = gm
    def counted(x, y, *a, **k):
        info = src.get((round(x,3), round(y,3))) if ingrow[0] and s.M.get("houses") else None
        before = len(s.M.get("houses") or [])
        ok = tp(x, y, *a, **k)
        if info is not None and ok and len(s.M["houses"]) > before:
            rec = s.M["houses"][-1]; c = (float(rec["x"]), float(rec["y"]))
            mv = math.hypot(c[0]-x, c[1]-y)
            act = G.box_reach(c, rec["geom"]["bbox"])
            want = G.household_reach(s, (x, y), (s.px(46)*1.35, s.px(28)*1.1)) if False else info[2]
            sp = sep(info[0], info[1], c, act)
            exc = max(a_-w_ for a_, w_ in zip(act, want))
            rows.append((seed, mv, sp[0], G.grow_gap(s), sp[1], sp[2], exc, math.degrees(math.atan2(c[1]-y, c[0]-x)), math.degrees(math.atan2(y-info[0][1], x-info[0][0]))))
        return ok
    s.try_place = counted
    with roll_scope(plan.spec):
        for st in STAGES:
            with redirect_stdout(io.StringIO()):
                st(s, plan)
            if st.__name__ == "stage_homesteads": break
    print("SEED", seed, "rows so far", len(rows), {k: v for k, v in s._seat_search.items() if not isinstance(v,(list,dict))}, flush=True)
moved = [r for r in rows if r[1] > 1e-6]; still = [r for r in rows if r[1] <= 1e-6]
gap = rows[0][3]
for name, rs in (("unmoved", still), ("moved", moved)):
    under = [r for r in rs if r[2] < r[3] - 1e-6]
    print(name, len(rs), "drawn envelope closer to its source's footprint than the gap:", len(under), "min separation", round(min(r[2] for r in rs),2) if rs else None, "gap", gap)
    for r in sorted(under, key=lambda r: r[2])[:12]: print("   seed", r[0], "moved px", round(r[1],1), "sep", round(r[2],2), "gx", round(r[4],2), "gy", round(r[5],2), "euclid", round(math.hypot(max(r[4],0),max(r[5],0)),2), "excess", round(r[6],2), "move dir", round(r[7]), "grow dir", round(r[8]))
    if name == "moved":
        print("   moves px:", sorted(round(r[1],1) for r in rs))
        print("   exceeders (excess>0): n", sum(r[6] > 1e-6 for r in rs), "their moves px", sorted(round(r[1],1) for r in rs if r[6] > 1e-6))
