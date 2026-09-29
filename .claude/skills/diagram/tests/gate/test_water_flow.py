"""Which way the water runs on a rolled map (feature 166): what is left of it after feature 287.

Feature 166 carried seven rules here that the retired battery re-measured on every finished map. Feature 287 moved four
into their placers, each with a unit test on the violating case, and retired their finished-map tests
(specs/287-placer-guarantees/research.md R8): `drain_flows_downhill` (`waterfields/comb.py:_comb_drain`),
`drainage_discharges_downhill` for the pond and the drain's run (`hamletgen/sink.py`'s route refusals and pond seat),
`streams_avoid_fields` (`hamletgen/water/brook.py:feed_brook`, `brook_violations`) and `fields_show_water_source`
(`fields/comb.py:draw_comb_field`).

KEPT, because no placer guarantees them yet:
- `channels_flow_downhill`: only the sink's routes are decided by `runs_downhill`; the feed and head-race record and the
  comb's own drain run reach `channels` with no downhill decision and no unit test.
- `stream_source_anchored` / `stream_end_anchored`: `brook_violations` asks the source end only; the exit end rests on
  `brook_skirt`'s construction, and no test has the violating case.

WATER IS THE ONE THING ON A MAP THAT CANNOT BE PLACED BY EYE. Every other feature can be wrong and merely
look odd; a channel running uphill is a claim about the world that is false. That is why the fall is
DECLARED (`meta.down_deg`, or a per-field `down_deg`) rather than inferred, and why each rule below is
stated against the declaration instead of against the page - a rule measured in the page's frame passes
at one orientation and fails at another, which is the defect family `dev/gate.md` collects.

THE GEOMETRY IS CARRIED HERE, NOT IMPORTED FROM THE GATE. These tests outlive `check_village`, so a
helper that lived in the battery would be deleted underneath them. Each predicate below is a few lines of
plain arithmetic stated where it is used, which is also what makes the rule readable at the assertion.
"""

from __future__ import annotations

import math

import pytest

from tests import rolls
from tests.gate import _pool

SPEC = rolls.REFERENCE  # the pool's brief (feature 215)

DOWNHILL_FRACTION = 0.2
"""How much of a channel's run must be down-fall before it counts as flowing downhill. Deliberately not
1.0: a delivery channel legitimately traverses to reach the head of a fan, so what is forbidden is a
course whose net travel is UPHILL or level, not one that takes an oblique line."""

ANCHOR_TOL = 24.0
"""A declared endpoint is "anchored" when it sits within this of the thing it names. The record stores
rounded pixel coordinates and a bank is a band rather than a line, so an exact match would be asserting
the rounding, not the anchoring."""


def _fall_vector(deg: float) -> tuple[float, float]:
    return (math.cos(math.radians(deg)), math.sin(math.radians(deg)))


@pytest.fixture(scope="module")
def rolled():
    return _pool.rolled_map(SPEC)


def test_the_map_declares_the_fall_every_rule_below_is_measured_against(rolled) -> None:
    """The non-vacuity assertion the whole module rests on. A map declaring no fall SKIPS every rule here
    while still looking green, so the declaration is asserted before anything is judged by it."""
    _plan, M = rolled
    assert M["meta"].get("down_deg") is not None, "the roll declares no land fall, so no flow rule below can judge anything"


def test_every_channel_runs_downhill(rolled) -> None:
    """`channels_flow_downhill`. A channel's source must be uphill of the field it feeds; gravity is the
    only thing moving the water. Judged against the fall the field itself declares where it has one, and
    the map's otherwise - a channel feeding a field with its own fall is that field's problem, not the
    map's."""
    _plan, M = rolled
    channels = M.get("channels") or []
    assert channels, "the roll drew no channel, so this rule would judge nothing"
    falls = {f.get("name"): f.get("down_deg") for f in (M.get("fields") or []) if f.get("down_deg") is not None}
    map_fall = M["meta"]["down_deg"]
    uphill = []
    for c in channels:
        to = (c.get("to") or {}).get("name")
        dvec = _fall_vector(float(falls.get(to, map_fall)))
        (sx, sy), (ex, ey) = c["poly"][0], c["poly"][-1]
        vx, vy = ex - sx, ey - sy
        L = math.hypot(vx, vy)
        if L > 0 and (vx * dvec[0] + vy * dvec[1]) < DOWNHILL_FRACTION * L:
            uphill.append((c.get("to") or {}).get("name", "?"))
    assert not uphill, f"channel(s) not running downhill: {sorted(set(uphill))}"


def test_every_stream_end_is_anchored_to_what_it_declares(rolled) -> None:
    """`stream_source_anchored` and `stream_end_anchored`. A stream declares where it comes FROM and where
    it goes TO, and the drawn polyline must actually reach them. The declaration is what every other water
    rule reads, so a stream whose record says "from the pond" while its ink starts sixty feet away makes
    every downstream rule judge a map that is not the one on the page."""
    _plan, M = rolled
    streams = M.get("streams") or []
    assert streams, "the roll drew no stream"
    W, H = float(M["meta"]["W"]), float(M["meta"]["H"])
    judged = 0
    for st in streams:
        poly, frm, to = st["poly"], st.get("frm"), st.get("to")
        for end, decl in ((poly[0], frm), (poly[-1], to)):
            if not decl:
                continue
            judged += 1
            kind = decl.get("kind")
            if kind == "offmap":
                off = end[0] < 0 or end[1] < 0 or (W and end[0] > W) or (H and end[1] > H)
                assert off, f"the stream declares an off-map end but {end} is inside the canvas"
            elif kind == "pond" and M.get("pond"):
                px, py, rx, ry = M["pond"][:4]
                assert ((end[0] - px) / rx) ** 2 + ((end[1] - py) / ry) ** 2 <= 1.2, f"the stream declares a pond end but {end} is not on the pond"
    assert judged, "no stream declared an end, so this rule judged nothing"
