"""Which callers' calls into the scalar geometry primitives hold the most time, across stage profiles."""
import pstats, sys, collections
PRIMS = ("seg_dist", "seg_closest", "point_in_poly", "edge_dist", "poly_gap", "sat_overlap", "rot_rect", "point_quad_dist", "quad_hits_poly", "quad_hits_seg", "segments_cross", "seg_intersect", "hypot")
agg = collections.Counter(); calls = collections.Counter(); totals = {}
for path in sys.argv[1:]:
    st = pstats.Stats(path)
    totals[path] = st.total_tt
    for (fn, ln, name), (cc, nc, tt, ct, callers) in st.stats.items():
        if name not in PRIMS and not (name == "<built-in method math.hypot>"):
            continue
        for (cfn, cln, cname), v in callers.items():
            key = (path.split("-")[-1].removesuffix(".prof"), name, f"{cfn.split('l7r/diagram/')[-1]}:{cln}({cname})")
            agg[key] += v[3]; calls[key] += v[0]
for k, t in agg.most_common(25):
    print(f"{t:6.3f}s {calls[k]:>8} {k[0]:<11} {k[1]:<16} {k[2]}")
print({p.split('-')[-1]: round(t, 2) for p, t in totals.items()})
