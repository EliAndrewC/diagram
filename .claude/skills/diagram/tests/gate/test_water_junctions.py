"""Where water meets water on a rolled map (feature 166).

Carries eight rules the retired battery re-measured on every finished map: `channels_join_water_not_cross`,
`water_channels_join_not_cross`, `channels_join_streams_at_confluence`, `channels_join_not_cross_at_fork`,
`waterways_merge_at_crossings`, `pond_connected_to_field` and `pond_fill_covers_channel_mouths`, plus
`field_ditches_reach_source_and_sink`, `field_ditch_tips_land_on_the_trunk` and
`field_ponds_sunk_into_one_plot`. (`pond_fed_from_edge` is a recorded DROP: no live map's pond is fed by
a stream, so the rule has no scripted executor to hold - see the migration record.)

ONE PHYSICAL RULE UNDERLIES ALL OF THEM: WATER JOINS WATER AT A CONFLUENCE. A watercourse never runs
straight across another like a painted line, and it never stops in the grass beside a bank. Two courses
that meet become one course; a course that reaches a body of water ends AT it. Everything below is that
statement measured a different way - across the centerlines, at a declared mouth, at a fork, in the paint
stack, and at the pond.

THE PAINT STACK IS PART OF THE PHYSICS HERE, WHICH IS UNUSUAL AND WORTH THE NOTE. `waterways_merge_at_crossings`
and `pond_fill_covers_channel_mouths` are about z-order, not position: a higher-drawn bed painting over
another course's sheen stacks into a dark seam, and a pond whose fill is drawn UNDER the mouths joining
it shows those mouths poking through its surface. Both read as a drawing error rather than as a place, so
the ordering the engine records (`bedz`, `sheenz`, `late`) is asserted as a fact about the map.
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache

SPEC = hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")

TRUNK_TOL = 13.0
"""How near a delivery ditch's end must come to the trunk it discharges into. A trunk is a stroke with
width, not a line, so the tolerance is the band rather than a snap tolerance."""

RIM = 1.06
"""The pond's rim zone, as a scale on its ellipse. A course "joins the pond" when an end falls inside it -
slightly outside the drawn edge, because a mouth reaches INTO the water rather than stopping on the line."""


def _seg_dist(px: float, py: float, a, b) -> float:
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def _poly_dist(pt, poly) -> float:
    return min(_seg_dist(pt[0], pt[1], poly[i], poly[i + 1]) for i in range(len(poly) - 1))


def _crosses(a0, a1, b0, b1) -> bool:
    """Do the two OPEN segments properly cross? A shared endpoint is a junction, not a crossing."""

    def side(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    d1, d2 = side(a0, a1, b0), side(a0, a1, b1)
    d3, d4 = side(b0, b1, a0), side(b0, b1, a1)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


def _in_ellipse(pt, e, scale: float = 1.0) -> bool:
    px, py, rx, ry = e[0], e[1], e[2] * scale, e[3] * scale
    return ((pt[0] - px) / rx) ** 2 + ((pt[1] - py) / ry) ** 2 <= 1.0


KUWABATA = hg.HamletSpec(name="Kuwabata", seed=21, households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic", dike_crop="mulberry")


@pytest.fixture(scope="module")
def rolled():
    return rollcache.hamlet(SPEC)


@pytest.fixture(scope="module")
def kuwabata():
    """The one live roll that lays laterals - see the lateral test for why a second roll is worth its
    seconds here."""
    return rollcache.hamlet(KUWABATA)


def test_every_lateral_lands_on_a_trunk_at_both_ends(kuwabata) -> None:
    """`field_ditches_reach_source_and_sink` and `field_ditch_tips_land_on_the_trunk`. A lateral that
    dead-ends inside a field waters nothing past its tip, and one that overshoots its trunk toward the
    edge stubs past the water it was meant to join. Both ends must land ON the main canal or the
    collector - the lateral is a rung of the network, not a line drawn near it.

    THE ROLL IS KUWABATA, NOT THE REFERENCE HAMLET, AND THAT IS THE WHOLE REASON THIS TEST EXISTS HERE.
    Only one live map lays laterals; on Inashiro the comb lays `main`, `branch` and `drain` only, so this
    rule asserted against the reference roll would pass on an empty list for ever - the exact shape
    `dev/gate.md` warns about, where a rule that cannot fire looks identical to a rule that passes. A
    delivery `branch` is deliberately NOT held to the same bar: a branch dies in the plots it waters,
    which is what it is for.
    """
    _plan, M = kuwabata
    ditches = M.get("field_ditches") or []
    laterals = [d for d in ditches if d.get("role") == "lateral"]
    assert laterals, "the Kuwabata roll laid no lateral, so this rule would judge nothing"
    dangling = []
    for lat in laterals:
        trunks = [d["poly"] for d in ditches if d.get("field") == lat.get("field") and d.get("role") in ("main", "drain")]
        assert trunks, f"the lateral on {lat.get('field')} has no trunk to land on"
        for end in (lat["poly"][0], lat["poly"][-1]):
            if min(_poly_dist(end, t) for t in trunks) > TRUNK_TOL:
                dangling.append((round(end[0]), round(end[1])))
    assert not dangling, f"lateral(s) dead-end or overshoot inside the field at {sorted(set(dangling))[:5]}"


def test_no_watercourse_crosses_another_mid_run(rolled) -> None:
    """`channels_join_water_not_cross`, `water_channels_join_not_cross` and
    `channels_join_not_cross_at_fork`. Water joins water at a CONFLUENCE - the mouth ends at the bank,
    engine-trimmed and water-colored. It never runs straight across the open water like a painted line.

    A shared endpoint is deliberately NOT a crossing: that is the confluence itself, and a predicate that
    could not tell the two apart would forbid the very thing the rule exists to require."""
    _plan, M = rolled
    water = [[(float(p[0]), float(p[1])) for p in s["poly"]] for s in (M.get("streams") or [])]
    joiners = [[(float(p[0]), float(p[1])) for p in c["poly"]] for c in (M.get("channels") or [])]
    joiners += [[(float(p[0]), float(p[1])) for p in d["poly"]] for d in (M.get("field_ditches") or [])]
    assert water and joiners, "the roll drew no open water or nothing joining it, so nothing could cross"
    crossings = []
    for w in water:
        for j in joiners:
            for i in range(len(j) - 1):
                for k in range(len(w) - 1):
                    if not _crosses(j[i], j[i + 1], w[k], w[k + 1]):
                        continue
                    # the mouth ENDING on the bed is the confluence; a crossing away from the joiner's
                    # own ends is the painted line the rule forbids
                    if min(_poly_dist(e, w) for e in (j[0], j[-1])) < TRUNK_TOL:
                        continue
                    crossings.append((round(j[i][0]), round(j[i][1])))
    assert not crossings, f"watercourse(s) cross the open water mid-run at {sorted(set(crossings))[:4]} instead of joining it"


def test_a_channel_declaring_a_stream_actually_reaches_its_bed(rolled) -> None:
    """`channels_join_streams_at_confluence`. An intake or drain culvert joins its stream at a confluence -
    the mouth reaches INTO the water, like a road junction - never dying in the grass beside the bank. The
    declaration is what every downstream rule reads, so a mouth that stops short makes the record describe
    a map that is not the one on the page."""
    _plan, M = rolled
    streams = [[(float(p[0]), float(p[1])) for p in s["poly"]] for s in (M.get("streams") or [])]
    declared = [c for c in (M.get("channels") or []) if "stream" in ((c.get("frm") or {}).get("kind"), (c.get("to") or {}).get("kind"))]
    assert streams and declared, "no channel declares a stream end, so this rule would judge nothing"
    dry = []
    for c in declared:
        poly = c["poly"]
        if min(min(_poly_dist(end, s) for s in streams) for end in (poly[0], poly[-1])) > TRUNK_TOL:
            dry.append((round(poly[0][0]), round(poly[0][1])))
    assert not dry, f"channel mouth(s) declared to a stream stop short of the bed at {dry[:4]}"


def test_courses_that_meet_are_composited_as_one_confluence(rolled) -> None:
    """`waterways_merge_at_crossings`. Every watercourse is drawn as a bed with a sheen over it. Two
    courses that meet must go through the shared bed and sheen groups so the pair composites as ONE
    confluence; a course drawn as its own stack paints its bed over its neighbor's sheen and the join
    reads as a dark seam rather than as water meeting water.

    The assertion is on the RECORD of that ordering - every drawn course carries a bed position, and the
    sheen sits above every bed - because the seam is a compositing fact, not a position."""
    _plan, M = rolled
    drawn = [dc for dc in (M.get("drawn_channels") or []) if dc.get("bedz") is not None]
    assert drawn, "the roll recorded no drawn watercourse, so the stack cannot be judged"
    beds = [float(dc["bedz"]) for dc in drawn]
    sheens = [float(s["sheenz"]) for s in (M.get("streams") or []) if s.get("sheenz") is not None]
    sheens += [float((M.get("pond_layer") or {}).get("sheenz"))] if (M.get("pond_layer") or {}).get("sheenz") is not None else []
    assert sheens, "no sheen position is recorded, so nothing establishes that water composites as one surface"
    assert max(sheens) > max(beds), f"a bed at z={max(beds)} is drawn over the topmost sheen at z={max(sheens)} - the join would read as a dark seam"


def test_the_pond_is_connected_to_the_field_it_serves(rolled) -> None:
    """`pond_connected_to_field`. A source pond must FEED the field through an irrigation channel; a
    drainage pond is fed by the field's DRAIN. Either way the pond is part of the water system or it is a
    puddle the map drew for decoration, and which of the two it is is declared (`meta.pond_role`)."""
    _plan, M = rolled
    pond = M.get("pond")
    assert pond, "the roll drew no pond, so this rule would judge nothing"
    role = M["meta"].get("pond_role", "source")
    if role == "source":
        polys = [c["poly"] for c in (M.get("channels") or []) if "pond" in ((c.get("frm") or {}).get("kind"), (c.get("to") or {}).get("kind"))]
        why = "a source pond must FEED the field through an irrigation channel, but none connects to it"
    else:
        polys = [d["poly"] for d in (M.get("field_ditches") or []) if d.get("role") == "drain"]
        polys += [c["poly"] for c in (M.get("channels") or []) if "pond" in ((c.get("frm") or {}).get("kind"), (c.get("to") or {}).get("kind"))]
        why = "a drainage pond is fed by the field's DRAIN, but nothing reaches the water"
    assert polys, f"the map declares pond_role={role} and drew no course of the kind that role requires"
    assert any(_in_ellipse(p, pond, 1.12) for poly in polys for p in (poly[0], poly[-1])), why


def test_the_pond_fill_is_drawn_over_the_mouths_that_join_it(rolled) -> None:
    """`pond_fill_covers_channel_mouths`. A mouth reaching into the pond is drawn as a stroke with a bed;
    if the pond's fill goes down FIRST, every one of those strokes pokes through its surface and the pond
    reads as a puddle with sticks in it. So the fill is drawn late, above every course that joins it."""
    _plan, M = rolled
    pond, layer = M.get("pond"), M.get("pond_layer") or {}
    assert pond, "the roll drew no pond"
    joining = [float(dc["bedz"]) for dc in (M.get("drawn_channels") or []) if dc.get("bedz") is not None and any(_in_ellipse(pt, pond, RIM) for pt in (dc["pts"][0], dc["pts"][-1]))]
    joining += [float(s["bedz"]) for s in (M.get("streams") or []) if s.get("bedz") is not None and any(_in_ellipse(pt, pond, RIM) for pt in (s["poly"][0], s["poly"][-1]))]
    assert joining, "no recorded course joins the pond, so this rule would judge nothing"
    assert layer.get("bedz") is not None, "a course joins the pond but the map records no fill position for it"
    assert float(layer["bedz"]) > max(joining), f"the pond fill at z={layer['bedz']} is drawn under a mouth at z={max(joining)} - the mouth would poke through the water"


def test_a_field_pond_is_sunk_into_one_plot(rolled) -> None:
    """`field_ponds_sunk_into_one_plot`. A field pond is a low pocket dug INTO one basin, with the field
    tiling around it. An ellipse spanning plots is crossed by the bunds between them, and what the reader
    sees is not a pocket but a flood - water standing over walls that should be holding it back."""
    _plan, M = rolled
    ponds = M.get("field_ponds") or []
    assert ponds, "the roll dug no field pond, so this rule would judge nothing"
    spilled = []
    for fp in ponds:
        e = (fp["x"], fp["y"], fp["rx"], fp["ry"])
        for fld in M.get("fields") or []:
            rings = (fld.get("plot_rings") or []) + (fld.get("drain_hem") or [])
            for ring in rings:
                n = len(ring)
                crossed = [k for k in range(n) if _in_ellipse(ring[k], e) != _in_ellipse(ring[(k + 1) % n], e)]
                if crossed:
                    spilled.append([fp["x"], fp["y"]])
                    break
            if spilled and spilled[-1] == [fp["x"], fp["y"]]:
                break
    assert not spilled, f"{len(spilled)} field pond(s) are crossed by bund/hem lines (e.g. {spilled[:2]}) - that reads as a flood, not a low pocket"
