"""Count the work per addition at each feature 387 site from `make perf-profile` raw profiles (SC-001).

    python3 specs/387-scale-the-placement-loops/count_work.py <log dir> <label>

<log dir> holds `<stage>-<households>.log`, each the output of
`make perf-profile SEED=4 STAGE=<stage> HOUSEHOLDS=<households>`, whose `raw:` line names the profile. Prints the counts and
merges them into `measurements.json` beside this file under `<label>`. Call counts, not seconds: they do not move with the load.
"""

from __future__ import annotations

import json
import os
import pstats
import re
import sys
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# (stage, name, file:function regexes counted) - the work, and what it is per
COUNTS: dict[str, list[tuple[str, str]]] = {
    "homesteads": [
        ("tree_candidates", r"ways/tree.py:\d+\(judge\)|tree.py:\d+\(judge\)"),
        ("tree_lays", r"tree.py:\d+\(lay\)"),
        ("fronting_pairs", r"law.py:\d+\(<genexpr>\)@fronting"),
        ("faces_judged", r"law.py:\d+\(is_needle\)"),
        ("ends_reached", r"law.py:\d+\(reach_to_steading\)"),
    ],
    "web": [
        ("field_runs", r"corridors.py:\d+\(field_runs\)"),
        ("run_on_target", r"bund.py:\d+\(run_on_target\)"),
        ("knot_trials", r"knots.py:\d+\(judge\)"),
        ("doorstep_ends", r"law.py:\d+\(doorstep_ends\)"),
        ("knot_pair_asks", r"knots.py:\d+\(pair\)"),
        ("faces_judged", r"law.py:\d+\(is_needle\)"),
    ],
    "field": [
        ("merges", r"waterfields/settle.py:\d+\(merge\)|settle.py:\d+\(merge\)"),
        ("shared_length", r"settle.py:\d+\(shared_length\)"),
    ],
    "windbreak": [
        ("sun_asks", r"keepouts.py:\d+\(_sun_keepouts\)"),
        ("plot_box", r"tree_shade.py:\d+\(plot_box\)"),
    ],
    "hinterland": [
        ("strip_candidates", r"bamboo.py:\d+\(_strip_blocked\)"),
        ("strip_items", r"bamboo.py:\d+\(<genexpr>\)"),
    ],
}


def _calls(prof: str, pattern: str) -> int:
    st = pstats.Stats(prof).stats  # type: ignore[attr-defined]
    want, _, caller = pattern.partition("@")
    rx = re.compile(want)
    n = 0
    for fn, (_cc, nc, _tt, _ct, callers) in st.items():
        name = f"{fn[0]}:{fn[1]}({fn[2]})"
        if not rx.search(name):
            continue
        if caller and not any(caller in c[2] for c in callers):
            continue
        n += nc
    return n


def main(argv: list[str]) -> int:
    logs, label = argv[1], argv[2]
    out: dict[str, Any] = {}
    for fname in sorted(os.listdir(logs)):
        m = re.fullmatch(r"(\w+)-(\d+)\.log", fname)
        if not m or m.group(1) not in COUNTS:
            continue
        stage, hh = m.group(1), m.group(2)
        raw = next((ln.split()[1] for ln in open(os.path.join(logs, fname)) if ln.startswith("raw:")), None)
        if raw is None:
            continue
        prof = os.path.join(ROOT, raw)
        out.setdefault(stage, {})[hh] = {name: _calls(prof, pat) for name, pat in COUNTS[stage]}
    print(json.dumps(out, indent=1, sort_keys=True))
    path = os.path.join(HERE, "measurements.json")
    rec = json.load(open(path)) if os.path.exists(path) else {}
    rec[label] = {"command": "make perf-profile SEED=4 STAGE=<stage> HOUSEHOLDS=<10|20|40>; " + " ".join(argv), "counts": out}
    json.dump(rec, open(path, "w"), indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
