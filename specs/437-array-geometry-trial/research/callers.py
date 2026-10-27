"""Which callers' calls into `settlement/_geom/primitives.py` hold the most time, across stage profiles - every function the module
defines, read by the file it lives in (feature 437 FR-001)."""
import pstats, sys, collections
GEOM = "settlement/_geom/primitives.py"  # FR-001's search space: every function this module defines (the scalar predicates among them)
agg = collections.Counter(); calls = collections.Counter(); totals = {}
for path in sys.argv[1:]:
    st = pstats.Stats(path)
    totals[path] = st.total_tt
    for (fn, ln, name), (cc, nc, tt, ct, callers) in st.stats.items():
        if GEOM not in fn:
            continue
        for (cfn, cln, cname), v in callers.items():
            key = (path.split("-")[-1].removesuffix(".prof"), name, f"{cfn.split('l7r/diagram/')[-1]}:{cln}({cname})")
            agg[key] += v[3]; calls[key] += v[0]
for k, t in agg.most_common(25):
    print(f"{t:6.3f}s {calls[k]:>8} {k[0]:<11} {k[1]:<16} {k[2]}")
print({p.split('-')[-1]: round(t, 2) for p, t in totals.items()})
