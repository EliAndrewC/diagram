import io, os, sys, time
from contextlib import redirect_stdout
sys.path.insert(0, os.environ["ROOT"] + "/.claude/skills/diagram")
from l7r.diagram.hamletgen import HamletSpec, plan_site
from l7r.diagram.hamletgen.driver import STAGES, roll_scope
from l7r.diagram.hamletgen.plan import beyond_the_band
from l7r.diagram.settlement import Settlement
REF = {"name": "Inashiro", "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated", "fixtures_min": {"shrine": 1}}
h, seed = int(sys.argv[1]), int(sys.argv[2])
with beyond_the_band():
    plan = plan_site(HamletSpec(seed=seed, households=h, **REF))
s = Settlement(W=plan.W, H=plan.H, seed=seed)
out = []
with roll_scope(plan.spec):
    for st in STAGES:
        t0 = time.perf_counter()
        with redirect_stdout(io.StringIO()):
            st(s, plan)
        out.append((st.__name__.replace("stage_", ""), time.perf_counter() - t0))
print(" ".join(f"{n}={t:.2f}" for n, t in out if t > 0.05), f"| lanes={len(s.M.get('lanes') or [])} corridors={len(s.M.get('access_corridors') or [])} legs={sum(len(c.get('pts') or []) - 1 for c in s.M.get('access_corridors') or [])}")
