"""Feature 281: the mechanism counts, read from the harness's saved profiles - no engine run, so no make target is needed.

    python3 specs/281-third-hotspot-pass/counts.py <profile dir> <engine root (the l7r/diagram of the tree measured)>

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
    "clip_seg_dist": ("primitives.py", "seg_dist", "ways/clearance.py", "fouled.<genexpr>"),
    "clip_pip": ("primitives.py", "point_in_poly", "ways/clearance.py", "fouled.<genexpr>"),
    "ring_index_builds": ("indexes.py", "__init__", "clearance.py", "__init__"),
    "brook_band_tests": ("~", "<method 'get' of 'dict' objects>", "ways/route.py", "in_brook_band.<genexpr>"),
    "handover_seg_dist": ("primitives.py", "seg_dist", "fixtures/_helpers.py", "outermost_join.<genexpr>"),
    "home_bank_cross": ("primitives.py", "segments_cross", "ways/sweeps.py", "_link_home_bank.<genexpr>"),
    "routes_missed_dist": ("~", "<built-in method math.hypot>", "fixtures/_helpers.py", "routes_missed.<genexpr>"),
    "caption_lane_seg_dist": ("primitives.py", "seg_dist", "structures/captions.py", "label_seat_clear"),
    "stream_rect_seg_dist": ("primitives.py", "seg_dist", "rolling/fit.py", "_rect_on_stream.<genexpr>"),
    "stream_rect_cross": ("primitives.py", "segments_cross", "rolling/fit.py", "_rect_on_stream.<genexpr>"),
    "marsh_sparse": ("wet.py", "_sparse", None, None),
    "grove_inside": ("grove_blocks.py", "inside", None, None),
    "grove_inside_reseat": ("grove_blocks.py", "inside", "homestead_parts/stands.py", "_reseat"),
    "grove_hard": ("grove_blocks.py", "hard", None, None),
    "quad_in_supply": ("carve.py", "_quad_in_supply", None, None),
    "supply_clearance": ("banks.py", "clearance", None, None),
    "absorb": ("pockets.py", "_absorb", None, None),
    "page_extent": ("page.py", "_extent", None, None),
    "carve_comb": ("comb.py", "carve_comb", None, None),
    "carve_edge": ("carve.py", "edge", None, None),
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
