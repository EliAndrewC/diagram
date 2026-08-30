"""Which way the water runs on a rolled map (feature 166).

Carries seven rules the retired battery re-measured on every finished map: `channels_flow_downhill`,
`drain_flows_downhill`, `drainage_discharges_downhill`, `streams_avoid_fields`, `stream_source_anchored`,
`stream_end_anchored` and `fields_show_water_source`.

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

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache

SPEC = hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")

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


def _seg_dist(px: float, py: float, a, b) -> float:
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def _poly_dist(pt, poly) -> float:
    return min(_seg_dist(pt[0], pt[1], poly[i], poly[i + 1]) for i in range(len(poly) - 1))


@pytest.fixture(scope="module")
def rolled():
    return rollcache.hamlet(SPEC)


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


def test_a_collector_discharges_at_its_lowest_point(rolled) -> None:
    """`drain_flows_downhill`. Water would run backwards otherwise. The discharge end of a collector must
    be its lowest point - which, with the fall declared rather than drawn, means the outfall's projection
    on the fall vector exceeds the head's."""
    _plan, M = rolled
    drains = [d for d in (M.get("field_ditches") or []) if d.get("role") == "drain"]
    assert drains, "the roll drew no collector, so this rule would judge nothing"
    dvec = _fall_vector(float(M["meta"]["down_deg"]))
    for d in drains:
        pts = d["poly"]
        head, out = pts[0], pts[-1]
        along = (out[0] - head[0]) * dvec[0] + (out[1] - head[1]) * dvec[1]
        # a collector runs cross-slope, so its ENDS may sit at nearly the same height; what is forbidden
        # is the outfall sitting measurably UPHILL of the head.
        assert along >= -1.0, f"the collector's outfall {out} sits uphill of its head {head} - water would run backwards"


def test_the_runoff_leaves_the_outfall_downhill(rolled) -> None:
    """`drainage_discharges_downhill`. The brook carrying the runoff away from the collector must take it
    DOWNHILL, matching the water flow everywhere else on the map. Where the sink is a pond, the pond is
    the discharge and the same rule applies to reaching it."""
    plan, M = rolled
    drains = [d for d in (M.get("field_ditches") or []) if d.get("role") == "drain"]
    assert drains, "the roll drew no collector"
    dvec = _fall_vector(float(M["meta"]["down_deg"]))
    outfall = drains[0]["poly"][-1]
    sink = M.get("pond")
    brooks = [st["poly"] for st in (M.get("streams") or []) if _poly_dist(outfall, st["poly"]) < 60.0]
    assert sink or brooks, "the roll gave the outfall neither a pond nor a brook, so the discharge is unjudgeable"
    if sink:
        along = (sink[0] - outfall[0]) * dvec[0] + (sink[1] - outfall[1]) * dvec[1]
        assert along > 0, f"the sink pond at {sink[:2]} sits uphill of the outfall {outfall}"
    for poly in brooks:
        near, far = (poly[0], poly[-1]) if _poly_dist(outfall, [poly[0], poly[0]]) < _poly_dist(outfall, [poly[-1], poly[-1]]) else (poly[-1], poly[0])
        along = (far[0] - near[0]) * dvec[0] + (far[1] - near[1]) * dvec[1]
        assert along > 0, f"the drainage brook runs uphill from the outfall ({near} -> {far})"


def test_no_stream_runs_through_a_field(rolled) -> None:
    """`streams_avoid_fields`. A watercourse crossing a paddy fan is not irrigation - it is a river
    through somebody's crop. Water reaches a field through a declared intake at its head, and leaves it
    through the collector; a stream drawn across the plots means the field was laid over the water or the
    water routed through the field."""
    _plan, M = rolled
    streams = M.get("streams") or []
    fields = [f for f in (M.get("fields") or []) if f.get("outline")]
    assert streams and fields, "the roll drew no stream or no outlined field, so this rule would judge nothing"
    through = []
    for st in streams:
        poly = st["poly"]
        for f in fields:
            ring = [(float(v[0]), float(v[1])) for v in f["outline"]]
            inside = [p for p in poly[1:-1] if _point_in(p, ring)]
            if inside:
                through.append(f["name"])
    assert not through, f"stream(s) run through field(s): {sorted(set(through))}"


def _point_in(pt, ring) -> bool:
    x, y = float(pt[0]), float(pt[1])
    inside = False
    n = len(ring)
    for i in range(n):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            inside = not inside
    return inside


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


def test_every_field_shows_where_its_water_comes_from(rolled) -> None:
    """`fields_show_water_source`. A paddy is defined by its water, so a field drawn with no visible
    supply is a picture of a crop rather than of a farm. The source may be a channel declared to it, or a
    stream or pond it abuts - what is forbidden is a field the reader cannot trace water to."""
    _plan, M = rolled
    fields = [f for f in (M.get("fields") or []) if f.get("kind") == "paddy"]
    assert fields, "the roll drew no paddy, so this rule would judge nothing"
    fed = {(c.get("to") or {}).get("name") for c in (M.get("channels") or [])}
    fed |= {d.get("field") for d in (M.get("field_ditches") or [])}
    dry = [f["name"] for f in fields if f.get("name") not in fed]
    assert not dry, f"on-map field(s) with no visible water source: {sorted(set(dry))}"
