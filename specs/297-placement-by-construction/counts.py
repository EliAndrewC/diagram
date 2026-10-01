"""Feature 297 (281's counts.py): the mechanism counts, read from the harness's saved profiles - no engine run, so no make target is needed.

    python3 specs/297-placement-by-construction/counts.py <profile dir> <engine root (the l7r/diagram of the tree measured)>

A count is the number of calls to a CALLEE made from a CALLER, both named by file and function. Call counts do not
depend on the machine's load. A generator expression or lambda has no name of its own and its line moves with every
edit, so it is credited to the function that encloses it (found in the measured tree's source): `fouled.<genexpr>`
is the same count before and after however the lines move. Prints JSON: {map: {label: count}}.
"""

from __future__ import annotations

import ast
import collections
import json
import pstats
import sys
from pathlib import Path

MAPS = ("inashiro", "kashikawa", "kuwabata", "mizuguchi", "sawada")

# label: (callee file suffix, callee function, caller file suffix or None, caller function or None). A None caller
# counts every call to the callee.
COUNTS: dict[str, tuple[str, str, str | None, str | None]] = {
    "seg_dist": ("primitives.py", "seg_dist", None, None),
    "try_place": ("houses.py", "try_place", None, None),
    "parts_fit": ("rolling/fit.py", "_parts_fit", None, None),
    "access_corridor": ("rolling/access.py", "access_corridor", None, None),
    "bundle_geom": ("rolling/bundle.py", "_bundle_geom", None, None),
    "drain_bank_clearance": ("banks.py", "drain_bank_clearance", None, None),
    "marsh_sparse": ("wet.py", "_sparse", None, None),
    "grove_static_clear": ("grove_blocks.py", "static_clear", None, None),
    "grove_too_near": ("grove_blocks.py", "too_near", None, None),
    "open_ground_ok": ("parcels.py", "_ok", None, None),
    "index_near": ("indexes.py", "near", None, None),
    "lanes_breaking": ("ways/last_resort.py", "lanes_breaking", None, None),
    "unsettled": ("ways/settle.py", "unsettled", None, None),
    "carve_comb": ("comb.py", "carve_comb", None, None),
    "builds": ("driver.py", "build", None, None),
}

_ANON = ("<genexpr>", "<lambda>", "<listcomp>", "<dictcomp>", "<setcomp>")


class _Encloser:
    """file -> {line: enclosing function name}, from the measured tree's source."""

    def __init__(self) -> None:
        self.cache: dict[str, dict[int, str]] = {}

    def name(self, path: str, line: int, fn: str) -> str:
        if fn not in _ANON:
            return fn
        table = self.cache.get(path)
        if table is None:
            table = {}
            try:
                tree = ast.parse(Path(path).read_text())
            except (OSError, SyntaxError):
                tree = None
            if tree is not None:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        for ln in range(node.lineno, (node.end_lineno or node.lineno) + 1):
                            # the innermost def wins: a nested def is walked after its parent
                            if ln not in table or table[ln][1] < node.lineno:
                                table[ln] = (node.name, node.lineno)  # type: ignore[assignment]
            self.cache[path] = table
        hit = table.get(line)
        return f"{hit[0] if hit else '?'}.{fn}"  # type: ignore[index]


def counts(prof: Path, enc: _Encloser) -> dict[str, int]:
    stats = pstats.Stats(str(prof)).stats  # type: ignore[attr-defined]
    out = collections.Counter()
    for (f, line, fn), (_cc, nc, _tt, _ct, callers) in stats.items():
        callee = enc.name(f, line, fn)
        for label, (cf, cfn, kf, kfn) in COUNTS.items():
            if not (f.endswith(cf) and callee == cfn):
                continue
            if kf is None:
                out[label] += nc
                continue
            for (f2, line2, fn2), (_c, n2, _t, _u) in callers.items():
                if f2.endswith(kf) and enc.name(f2, line2, fn2) == kfn:
                    out[label] += n2
    return {k: int(out.get(k, 0)) for k in COUNTS}


def main() -> None:
    d = Path(sys.argv[1])
    enc = _Encloser()
    print(json.dumps({m: counts(d / f"{m}.prof", enc) for m in MAPS if (d / f"{m}.prof").exists()}, indent=2))


if __name__ == "__main__":
    main()
