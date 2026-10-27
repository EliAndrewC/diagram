"""Self time in the scalar geometry primitives (and math builtins) against each stage profile's total."""
import pstats, sys
GEOM = "_geom/primitives.py"
for path in sys.argv[1:]:
    st = pstats.Stats(path)
    prim = sum(v[2] for (fn, ln, name), v in st.stats.items() if GEOM in fn)
    mathb = sum(v[2] for (fn, ln, name), v in st.stats.items() if name.startswith("<built-in method math.") or name in ("<built-in method builtins.min>", "<built-in method builtins.max>", "<built-in method builtins.abs>"))
    gens = sum(v[2] for (fn, ln, name), v in st.stats.items() if name == "<genexpr>")
    top = sorted(((v[2], f"{fn.split('l7r/diagram/')[-1]}:{ln}({name})") for (fn, ln, name), v in st.stats.items()), reverse=True)[:8]
    print(f"== {path.split('-')[-1]}: total {st.total_tt:.2f}s; primitives.py self {prim:.3f}s ({100*prim/st.total_tt:.1f}%); math/min/max/abs builtins {mathb:.3f}s; generator expressions {gens:.3f}s ({100*gens/st.total_tt:.1f}%)")
    for t, k in top:
        print(f"    {t:6.3f}s self  {k}")
