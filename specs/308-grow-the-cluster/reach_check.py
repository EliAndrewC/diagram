import io, sys
from contextlib import redirect_stdout
sys.path.insert(0, "/diagram/.clones/diagram-performance/.claude/skills/diagram")
from l7r.diagram.hamletgen import HamletSpec, plan_site
from l7r.diagram.hamletgen.driver import STAGES, roll_scope
from l7r.diagram.hamletgen.plan import beyond_the_band
from l7r.diagram.hamletgen.homesteads import growth as G
from l7r.diagram.settlement import Settlement
REF = {"name": "Inashiro", "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated", "fixtures_min": {"shrine": 1}}
worst = [-1e9]*4; n = 0; over = 0; moved = 0
for seed in [int(x) for x in sys.argv[2].split(",")]:
    with beyond_the_band():
        plan = plan_site(HamletSpec(seed=seed, households=int(sys.argv[1]), **REF))
    s = Settlement(W=plan.W, H=plan.H, seed=seed)
    tp = s.try_place
    largest = (s.px(46) * 1.35, s.px(28) * 1.10)
    ingrow = [False]
    real_gm = getattr(G, "_real", G.grow_the_margin); G._real = real_gm
    def gm(*a, **k):
        ingrow[0] = True
        try: return real_gm(*a, **k)
        finally: ingrow[0] = False
    G.grow_the_margin = gm
    import l7r.diagram.hamletgen.homesteads.stages as ST
    ST.grow_the_margin = gm
    def counted(x, y, *a, **k):
        global n, over, moved
        before = len(s.M.get("houses") or [])
        want = G.household_reach(s, (x, y), largest) if ingrow[0] and before else None
        ok = tp(x, y, *a, **k)
        if ok and ingrow[0] and len(s.M["houses"]) > before:
            rec = s.M["houses"][-1]
            hx, hy = float(rec["x"]), float(rec["y"])
            act = G.box_reach((hx, hy), rec["geom"]["bbox"])
            if want is None: return ok
            d = [a_ - w_ for a_, w_ in zip(act, want)]
            n += 1
            if abs(hx - x) > 1e-6 or abs(hy - y) > 1e-6: moved += 1
            if max(d) > 1e-6:
                over += 1
                bx = rec["geom"].get("boxes") or {}
                parts = {k: v for k, v in bx.items() if isinstance(v, (tuple, list)) and len(v) == 4 and not isinstance(v[0], (tuple, list))}
                for i, gg in enumerate(bx.get("gardens") or ()): parts[f"bed{i}"] = gg
                for f, r in (bx.get("fixtures") or {}).items(): parts["fx:" + f] = r
                side = max(range(4), key=lambda i: d[i])
                drivers = sorted(((G.box_reach((hx, hy), r)[side], k) for k, r in parts.items() if r is not None), reverse=True)[:3]
                if over < 25: print("   side", "wens"[side], "drivers", [(k, round(v, 1)) for v, k in drivers], "want", round(want[side], 1), file=sys.stderr)
                print(f"seed {seed} seat ({x:.0f},{y:.0f}) house ({hx:.0f},{hy:.0f}) w={rec.get('w')} h={rec.get('h')} excess wens={[round(v,1) for v in d]} byre={rec.get('byre') is not None} well={bool(rec.get('well'))}", file=sys.stderr)
            for i in range(4): worst[i] = max(worst[i], d[i])
        return ok
    s.try_place = counted
    with roll_scope(plan.spec):
        for st in STAGES:
            with redirect_stdout(io.StringIO()):
                st(s, plan)
            if st.__name__ == "stage_homesteads": break
    print(f"seed {seed}: houses={len(s.M.get('houses') or [])}", flush=True)
print(f"grown placements={n} moved={moved} exceeding the largest-house envelope at the seat={over} worst excess (w,e,n,s)={[round(v,1) for v in worst]}")
