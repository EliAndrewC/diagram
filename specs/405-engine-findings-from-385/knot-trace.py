"""Trace every gather settle_knots' judge is asked for one knotted manifest, with why each is refused (405 T26, 2026-10-23).

A RECONSTRUCTION of the judge, not the judge: the whole-web counts are asked with `WebMemo.count`, where `settle_knots` asks the
incremental `trial_count`; its reasons matched the earlier part-B trace. Run from a checkout root: python3 <this> <manifest.json> [v]"""
import json, sys, types
sys.path.insert(0, ".")
from l7r.diagram.hamletgen.ways import knots as K, law
from l7r.diagram.hamletgen.ways.settle import Lawful
from l7r.diagram.hamletgen.consts import WEB_CROP_GAP
M = json.load(open(sys.argv[1]))
lanes = M["lanes"]
ftpx = float(M["meta"].get("ftpx") or 1.0)
s = types.SimpleNamespace(M=M, px=lambda ft: ft / ftpx)
lawful = Lawful(s); lawful.fence_gap = WEB_CROP_GAP
memo = K.WebMemo()
ways = [K._pts(ln) for ln in lanes]; ids = memo.ids(ways)
nets0, joined0, un0 = memo.web(M, ways, ids)
base = {n: memo.count(n, M, ways, ids) for n in K._WHOLE_RULES}
def judge(edits):
    trial = {**M, "lanes": [dict(ln) for ln in lanes]}
    tw = list(ways)
    for i, p in edits.items():
        trial["lanes"][i]["pts"] = [[x, y] for x, y in p]; tw[i] = K._pts(trial["lanes"][i])
    ti = memo.ids(tw)
    nets, joined, un = memo.web(trial, tw, ti)
    why = []
    if not joined0 <= joined: why.append("splits from connector")
    if nets > nets0: why.append(f"nets {nets0}->{nets}")
    if un > un0: why.append(f"unreached {un0}->{un}")
    lawful.M = trial
    for i, p in edits.items():
        f = lawful.fault(p, float(lanes[i].get("w") or 3.0), skip=i)
        if f: why.append(f"lane {i}: {f}")
    lawful.M = M
    for n in K._WHOLE_RULES:
        c = memo.count(n, trial, tw, ti)
        if c > base[n]: why.append(f"{n} {base[n]}->{c}")
    print(sorted(edits), {i: [tuple(round(v, 1) for v in q) for q in p] for i, p in edits.items()} if len(sys.argv) > 2 else "", "->", why or "ADMITTED")
    return False
K.next_gather(lanes, judge, apart=K.ground_apart(M, s))
