import io, os, sys, time
from contextlib import redirect_stdout
sys.path.insert(0, os.environ["ROOT"] + "/.claude/skills/diagram")
from l7r.diagram.hamletgen import HamletSpec, plan_site
from l7r.diagram.hamletgen.driver import STAGES, roll_scope
from l7r.diagram.hamletgen.plan import beyond_the_band
from l7r.diagram.settlement import Settlement
from l7r.diagram.hamletgen.ways.checks import unreached_houses
REF = {"name": "Inashiro", "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated", "fixtures_min": {"shrine": 1}}
h = int(sys.argv[1])
for seed in [int(x) for x in sys.argv[2].split(",")]:
    with beyond_the_band():
        plan = plan_site(HamletSpec(seed=seed, households=h, **REF))
    s = Settlement(W=plan.W, H=plan.H, seed=seed)
    t0 = time.perf_counter(); err = ""
    try:
        with roll_scope(plan.spec):
            for st in STAGES:
                with redirect_stdout(io.StringIO()):
                    st(s, plan)
    except Exception as e:
        err = f"{type(e).__name__}: {str(e)[:120]}"
    m = s.M.get("meta") or {}
    print(seed, f"{time.perf_counter()-t0:.1f}s", "houses", len(s.M.get("houses") or []), "share", m.get("passage_share"), "reached_across", m.get("passage_reached"), "budget", int((m.get("passage_share") or 0) * h), "unreached", len(unreached_houses(s.M)), err, flush=True)
