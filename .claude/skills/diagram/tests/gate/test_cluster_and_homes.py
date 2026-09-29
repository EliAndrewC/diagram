"""Where the houses stand, and what they stand near (feature 166): what is left of it after feature 287.

Feature 166 carried seven rules here that the retired battery re-measured on every finished map. Feature 287 moved them
into the seating (`settlement/rolling/fit.py`, `lot.py`, `bundle.py`, `hamletgen/homesteads/stages.py` and `wells.py`,
`settlement/houses.py`, `homestead_parts/yards.py`), each with a unit test on the violating case, and retired the
finished-map tests of the cluster abutting its fields, the byres seated, the drip lines, the yard square to its house, the
shed-long farmhouse and the well among the doors (specs/287-placer-guarantees/research.md R8).

KEPT, because no placer guarantees them yet:
- the drawn aspect inside the declared shape's band: `stages.py:shapes_drawn_at` declares `elongated` for any string
  past every band, so a string longer than 12:1 is declared and drawn without a refusal;
- `settlement_dwellings_watered`: `lot.py:needs_pocket` is asked at the seek point, not the placed center, so a house the
  nucleated placer moves can land past the reach with no well pocket, and no unit test seats one near the limit.
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram.settlement import surface_water_dist
from tests import rolls
from tests.gate import _pool

SPEC = rolls.REFERENCE  # the pool's brief (feature 215)

WATER_REACH_FT = 760.0
"""How far a household may stand from its water. Every dwelling must reach a well or open water inside
this; beyond it the household is carrying water from another settlement's supply."""

CLUSTER_ASPECT = {"round": (1.0, 2.0), "crescent": (1.9, 4.2), "elongated": (2.8, 12.0), "split": (1.9, 4.2)}
"""The long-to-wide band each rolled cluster shape must actually draw to."""


@pytest.fixture(scope="module")
def homes():
    _plan, M = _pool.rolled_map(SPEC)
    houses = [h for h in (M.get("houses") or []) if h.get("kind") != "abandoned"]
    assert len(houses) >= 10, f"the roll seated {len(houses)} houses - too few for the spread rules below to mean anything"
    return M, houses


def test_the_cluster_draws_inside_the_band_of_the_shape_it_declared(homes) -> None:
    """`cluster_shape_matches_the_drawing`, its band half: the aspect the cluster draws lies inside the band of the shape
    the map declares (the declaration itself is the drawing's since feature 287 - `stages.py:declare_cluster_shape`)."""
    M, _houses = homes
    shape = M["meta"]["cluster_shape"]
    drawn = float(M["meta"]["cluster_aspect_drawn"])
    lo, hi = CLUSTER_ASPECT.get(str(shape), (1.9, 4.2))
    assert lo <= drawn <= hi, f"the map declared cluster_shape={shape!r} (wants {lo}-{hi}:1) and drew {drawn}:1"


def test_every_household_can_reach_water(homes) -> None:
    """`settlement_dwellings_watered`. A household that cannot reach a well or open water is a household
    carrying its water from somewhere the map does not show. The reach is generous on purpose - this is a
    floor on the settlement being habitable, not a comfort standard."""
    M, houses = homes
    wells = M.get("wells") or []
    reach = WATER_REACH_FT / float(M["meta"].get("ftpx") or 1.0)
    dry = []
    for h in houses:
        d = min((math.hypot(h["x"] - w["x"], h["y"] - w["y"]) for w in wells), default=1e9)
        d = min(d, surface_water_dist(M, h["x"], h["y"]))
        if d > reach:
            dry.append((round(h["x"]), round(h["y"]), round(d)))
    assert not dry, f"household(s) stand more than {WATER_REACH_FT:.0f} ft from any water: {dry[:4]}"
