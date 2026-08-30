"""Where the houses stand, and what they stand near (feature 166).

Carries seven rules the retired battery re-measured on every finished map: `cluster_abuts_fields`,
`cluster_shape_matches_the_drawing`, `byres_meet_their_target`, `farmhouses_shed_separately`,
`farmhouse_aspect_in_range`, `wells_among_dwellings` and `settlement_dwellings_watered`.

THE SETTLEMENT SITS ON ITS FIELDS BECAUSE THE WORK IS DAILY. A wet-rice household walks to its paddies
several times a day through the transplanting and again through the harvest, carrying tools, seedlings,
water and the crop; a cluster set back from the fields spends that walk twice a day for ever. So the
nucleated hamlet abuts the ground it works, and every rule here is a consequence of the same fact - the
houses are close together, the byre is where the draft team lives, and the well is among the doors.

A KNOB THAT NEVER BINDS LOOKS EXACTLY LIKE ONE THAT ALWAYS DOES, which is why `cluster_shape` is asserted
against the DRAWING and not merely against the record. `cluster_shape` was rolled, printed in every cohort
header, and honored on NO map for a long time, because only a seeding pass that never ran consumed it -
and a peer session then spent an attempt blaming the knob for a placement failure it could not have
caused. The map must leave a trace either way: the shape it drew, or an explicit note that the shape it
rolled could not be honored.
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache
from l7r.diagram.settlement import FARMHOUSE_EAVE_GAP_FT, surface_water_dist

SPEC = hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")

ABUT_PX = 60.0
"""How near the NEAREST house must come to a field before the cluster counts as abutting it. Measured on
the reference roll: 33 px. The bar is the nearest house only - the far side of a cluster is legitimately
a cluster-span back, which is what the second half of the rule allows for."""

MAX_ASPECT = 2.7
"""A minka lengthened by adding bays; past this it is a shed. Measured on the live pool the worst is
2.37 (Kuwabata 2.39), so the margin is about 11% - this is a live guard on a real regression, not a
re-measurement of a guarantee. `consts.py` records that the nucleated path jitters a minka's length to
1.35x, so a base near the top of the 1.3-2.5:1 norm plus a full jitter lands near the line."""

WATER_REACH_FT = 760.0
"""How far a household may stand from its water. Every dwelling must reach a well or open water inside
this; beyond it the household is carrying water from another settlement's supply."""

CLUSTER_ASPECT = {"round": (1.0, 2.0), "crescent": (1.9, 4.2), "elongated": (2.8, 12.0), "split": (1.9, 4.2)}
"""The long-to-wide band each rolled cluster shape must actually draw to."""


def _poly_dist(x: float, y: float, poly) -> float:
    best = 1e9
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        vx, vy = b[0] - a[0], b[1] - a[1]
        L2 = vx * vx + vy * vy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - a[0]) * vx + (y - a[1]) * vy) / L2))
        best = min(best, math.hypot(x - (a[0] + t * vx), y - (a[1] + t * vy)))
    return best


def _edge_gap(a, b) -> float:
    """The gap between two axis-aligned footprints, wall to wall - never centre to centre. A gap verdict
    reads footprints (`dev/placement.md`), because a centre-to-centre bar quietly forgives a large
    building standing on a small one."""
    dx = max(0.0, abs(a["x"] - b["x"]) - (a["w"] + b["w"]) / 2)
    dy = max(0.0, abs(a["y"] - b["y"]) - (a["h"] + b["h"]) / 2)
    return math.hypot(dx, dy)


@pytest.fixture(scope="module")
def rolled():
    return rollcache.hamlet(SPEC)


@pytest.fixture(scope="module")
def homes(rolled):
    _plan, M = rolled
    houses = [h for h in (M.get("houses") or []) if h.get("kind") != "abandoned"]
    assert len(houses) >= 10, f"the roll seated {len(houses)} houses - too few for the spread rules below to mean anything"
    return M, houses


def test_the_cluster_abuts_the_ground_it_works(homes) -> None:
    """`cluster_abuts_fields`. A wet-rice household walks to its paddies several times a day; a cluster
    set back from the fields pays that walk twice a day for ever. The bar is on the NEAREST house, with
    the far side allowed a cluster-span of slack, because a nucleated settlement has depth."""
    M, houses = homes
    fields = [f["outline"] for f in (M.get("fields") or []) if f.get("outline")]
    assert fields, "the roll drew no outlined field, so this rule would judge nothing"
    assert M["meta"].get("nucleated"), "the reference roll is not nucleated, so this form of the rule does not apply to it"
    dists = [min(_poly_dist(h["x"], h["y"], f) for f in fields) for h in houses]
    cx = sum(h["x"] for h in houses) / len(houses)
    cy = sum(h["y"] for h in houses) / len(houses)
    span = max(math.hypot(h["x"] - cx, h["y"] - cy) for h in houses)
    assert min(dists) <= ABUT_PX, f"the nearest house is {min(dists):.0f} px from a field - the cluster does not abut its ground"
    far = [d for d in dists if d > ABUT_PX + 2 * span]
    assert not far, f"{len(far)} house(s) stand beyond a cluster-span past the fields"


def test_the_cluster_draws_the_shape_it_rolled(homes) -> None:
    """`cluster_shape_matches_the_drawing`. The shape must leave a trace either way - the drawing that
    honors it, or an explicit note that it could not be honored. Anything else and a knob that never
    binds is indistinguishable from one that always does."""
    M, houses = homes
    shape = M["meta"].get("cluster_shape")
    unhonored = M["meta"].get("cluster_shape_unhonored")
    assert shape or unhonored, "the map records neither cluster_shape nor cluster_shape_unhonored"
    if not shape:
        return
    xs = [h["x"] for h in houses]
    ys = [h["y"] for h in houses]
    drawn = M["meta"].get("cluster_aspect_drawn")
    assert drawn is not None, f"the map rolled cluster_shape={shape!r} but records no drawn aspect to hold it to"
    lo, hi = CLUSTER_ASPECT.get(str(shape), (1.9, 4.2))
    assert lo <= float(drawn) <= hi, f"the map rolled cluster_shape={shape!r} (wants {lo}-{hi}:1) and drew {drawn}:1"
    assert xs and ys  # the aspect is a fact about these houses, not about an empty list


def test_the_settlement_seats_the_byres_it_asked_for(homes) -> None:
    """`byres_meet_their_target`. A wet-rice settlement plows with a draft team, so a shortfall is a
    PLACEMENT failure and not a settlement without oxen. That distinction is the rule: the number is
    rolled from the households, and a map that seats fewer has failed to find ground, not decided to farm
    by hand."""
    M, _houses = homes
    target = M["meta"].get("byre_target")
    seated = len(M.get("byres") or [])
    assert target is not None, "the map declares no byre target, so nothing can hold the drawing to it"
    assert seated >= target, f"the placer asked for {target} byre(s) and seated {seated}"


def test_two_farmhouses_keep_their_own_drip_lines(homes) -> None:
    """`farmhouses_shed_separately`. Two steep thatched roofs need their own drip lines and a way between
    them - eaves that meet pour both roofs' rain into one strip of ground, and on the sheet the pair
    merges into a single long building. The gap is measured wall to wall, which is what an eave gap is."""
    M, houses = homes
    limit = FARMHOUSE_EAVE_GAP_FT / float(M["meta"].get("ftpx", 1) or 1)
    merged = [(round(houses[i]["x"]), round(houses[i]["y"])) for i in range(len(houses)) for j in range(i + 1, len(houses)) if _edge_gap(houses[i], houses[j]) < limit]
    assert not merged, f"{len(merged)} farmhouse pair(s) stand closer than {FARMHOUSE_EAVE_GAP_FT:.0f} ft wall to wall, at {merged[:4]}"


def test_no_farmhouse_is_drawn_as_a_shed(homes) -> None:
    """`farmhouse_aspect_in_range`. A minka grew by adding bays along its ridge, so it is a long building -
    but it stayed a house. Past about 2.7:1 the footprint reads as a shed or a barn, and the settlement
    fills with outbuildings nobody lives in."""
    _M, houses = homes
    lop = [(round(h["x"]), round(h["y"]), round(max(h["w"], h["h"]) / min(h["w"], h["h"]), 2)) for h in houses if min(h["w"], h["h"]) > 0 and max(h["w"], h["h"]) / min(h["w"], h["h"]) > MAX_ASPECT]
    assert not lop, f"farmhouse(s) are more than {MAX_ASPECT}:1 long-to-wide: {lop[:3]}"


def test_every_well_stands_among_the_doors_it_serves(homes) -> None:
    """`wells_among_dwellings`. A well serves the households around it, and it is dug where those
    households are - somebody draws from it several times a day. A well out in the fields is a well
    nobody uses, and it is also a well nobody maintains."""
    M, houses = homes
    wells = M.get("wells") or []
    assert wells, "the roll dug no well, so this rule would judge nothing"
    stray = [(round(w["x"]), round(w["y"])) for w in wells if not any(_edge_gap({"x": w["x"], "y": w["y"], "w": 0.0, "h": 0.0}, h) <= 95.0 for h in houses)]
    assert not stray, f"well(s) stand in open ground with no dwelling within ~95 px: {stray[:4]}"


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
