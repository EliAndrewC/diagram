"""cProfile the homesteads stage of one reference seed: python3 prof.py <households> <seed> [out.txt]"""
import cProfile
import io
import os
import pstats
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refusals  # noqa: E402

h, seed = int(sys.argv[1]), int(sys.argv[2])
from l7r.diagram.hamletgen.homesteads import stages as ST  # noqa: E402

if os.environ.get("NOPASS") and hasattr(ST, "passage_share"):  # feature 317: the passage's share rolled at none
    ST.passage_share = lambda seed: 0.0

import l7r.diagram.hamletgen.driver as D0

_want = "stage_" + os.environ.get("STAGE", "homesteads")
inner = next(st for st in D0.STAGES if st.__name__ == _want)
prof = cProfile.Profile()


def profiled(*a, **k):
    prof.enable()
    try:
        return inner(*a, **k)
    finally:
        prof.disable()


import l7r.diagram.hamletgen.driver as D  # noqa: E402

D.STAGES = tuple(profiled if st is inner else st for st in D.STAGES)
refusals.STAGES = D.STAGES
import io as _io
import time as _time
from contextlib import redirect_stdout as _rs

from l7r.diagram.hamletgen import HamletSpec as _HS, plan_site as _ps
from l7r.diagram.hamletgen.driver import roll_scope as _scope
from l7r.diagram.hamletgen.plan import beyond_the_band as _bb
from l7r.diagram.settlement import Settlement as _S

with _bb():
    _plan = _ps(_HS(seed=seed, households=h, **refusals.REF))
_s = _S(W=_plan.W, H=_plan.H, seed=seed)
took = 0.0
with _scope(_plan.spec):
    for _st in D.STAGES:
        _t0 = _time.perf_counter()
        with _rs(_io.StringIO()):
            _st(_s, _plan)
        if _st is profiled:
            took = _time.perf_counter() - _t0
            break
houses = len(_s.M.get("houses") or [])
out = io.StringIO()
st = pstats.Stats(prof, stream=out)
st.sort_stats("cumulative").print_stats(45)
st.sort_stats("tottime").print_stats(30)
for name in os.environ.get("CALLERS", "").split(","):
    if name:
        st.sort_stats("cumulative").print_callers(name)
for name in os.environ.get("CALLEES", "").split(","):
    if name:
        st.sort_stats("cumulative").print_callees(name)
print(f"stage {took:.2f} s, {houses} houses")
print(out.getvalue())
