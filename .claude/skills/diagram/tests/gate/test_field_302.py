"""Feature 302 SC-003 on the shipped hamlets: a comb field built by construction leaves no bare ground in its planted region.

The glyph check of the paddy on Inashiro measured it from the manifest and found a 6,377 sq ft wedge at the head of the east
sector (0.79% of the planted area, against the spec's 0.5%): rows noded at every column's point, the thinned ones too, folded and
toothed where the sector narrowed, and the settle left the cells bare. This holds the bound on every shipped comb field.

THE MEASURE: the comb floor less the plots and less the water as the engine claims it (`seams._water`, every drawn course with
its bank, read off `drawn_channels`), OPENED by `OPEN_FT` - a gap narrower than six feet is the few px between a channel's drawn
taper and the engine's, a hairline the bund stroke covers, and it is not ground a reader sees bare. Unopened, every shipped field
read about 1% bare in such strips along its canals (2026-10-01); opened, the four comb fields read 0.00-0.07%, the field the
glyph check flagged 0.91%, and main's Inashiro 0%.
"""

from __future__ import annotations

import glob
import json
import os

from shapely.geometry import Polygon
from shapely.ops import unary_union

_SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_HAMLETS = sorted(glob.glob(os.path.join(_SKILL, "pool", "hamlets", "*", "*.gen.py")))

BARE_MAX = 0.005
"""SC-003's bound: bare ground under 0.5% of the planted area (the rounding of recorded rings - a bound the spec chose)."""

OPEN_FT = 3.0
"""Bare ground is counted after an opening by this many feet: a gap under twice it wide is a hairline, not bare ground."""


def bare_share(M: dict) -> dict[str, float]:
    """Each COMB field's bare ground (one with a `fork`; a polder is not built by the partition) over its planted area."""
    from l7r.diagram.waterfields.seams import _water

    g = 1.0 / float((M.get("meta") or {}).get("ftpx") or 1.0)
    courses = [{"pts": d["pts"], "w": float(d.get("w0") or 2.0), "w_tail": float(d.get("w1") or d.get("w0") or 2.0)} for d in M.get("drawn_channels") or [] if len(d.get("pts") or []) >= 2]
    water = _water(courses, g) if courses else Polygon()
    out = {}
    for f in M.get("fields") or []:
        floor = (M.get("comb_floors") or {}).get(f.get("name"))
        if not floor or not f.get("plot_rings") or "fork" not in f:
            continue
        plots = unary_union([Polygon(r).buffer(0) for r in f["plot_rings"] if len(r) >= 3])
        bare = Polygon(floor).buffer(0).difference(plots).difference(water).buffer(-OPEN_FT * g).buffer(OPEN_FT * g)
        out[f["name"]] = bare.area / plots.area
    return out


def test_bare_share_reads_the_floor_less_the_plots_and_the_water_opened() -> None:
    M = {
        "meta": {"ftpx": 1.0},
        "comb_floors": {"f": [(0, 0), (100, 0), (100, 100), (0, 100)]},
        "fields": [{"name": "f", "fork": [0, 0], "plot_rings": [[(0, 0), (100, 0), (100, 47), (0, 47)], [(0, 53), (100, 53), (100, 90), (0, 90)], [(0, 92), (100, 92), (100, 100), (0, 100)]]}],
        "drawn_channels": [{"pts": [(0, 50), (100, 50)], "w0": 4, "w1": 4}],
    }
    assert bare_share(M)["f"] < 1e-6, "the canal's bank is water, and the 2 ft strip under the last plot is a hairline"
    M["fields"][0]["plot_rings"].pop()
    assert abs(bare_share(M)["f"] - 1000.0 / 8400.0) < 0.01, "a 10 ft strip is bare ground"
    assert bare_share({"fields": [{"name": "g", "fork": [0, 0], "plot_rings": [[(0, 0), (1, 0), (1, 1)]]}]}) == {}, "no floor, no comb field"
    M["fields"][0].pop("fork")
    assert bare_share(M) == {}, "a field with no fork is no comb (Kuwabata's polder)"


def test_every_shipped_comb_field_leaves_no_bare_ground() -> None:
    from tests.gate import _pool

    shares = {}
    for gen in _HAMLETS:
        with open(_pool.obtain(gen), encoding="utf-8") as fh:
            for name, share in bare_share(json.load(fh)).items():
                shares[f"{os.path.basename(gen)}:{name}"] = share
    assert len(shares) >= 4, f"non-vacuity: the comb hamlets' fields were found ({sorted(shares)})"
    over = {k: round(100 * v, 3) for k, v in shares.items() if v >= BARE_MAX}
    assert not over, f"bare ground over {100 * BARE_MAX}% of the planted area (percent): {over}"
