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

inner = ST.stage_homesteads
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
took, houses = refusals.run(h, seed)
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
