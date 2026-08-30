"""The paddy fabric a rolled comb fan must produce (feature 166).

Carries eight rules the retired battery re-measured on every finished map: `paddy_fan_has_floor`,
`comb_floor_ends_at_the_collector`, `comb_supply_commands_both_flanks`, `paddy_plots_are_workable_basins`,
`flooded_plots_read_as_basins`, `paddy_basins_are_worth_their_bund`,
`paddy_plot_rings_overcount_stays_marginal` and `paddy_bunds_do_not_stagger`.

THREE OF THESE ALREADY DELEGATED TO AN ENGINE PREDICATE, AND THAT IS THE WHOLE MIGRATION. The retired
segments for the floor's overhang, the needle basins and the bank clearance each imported
`floor_overhang` / `pointed_ring` / `supply_bank_clearance` and said, in their own comments, that the
predicate was "imported from the engine and NOT restated - the same call the carve makes". So the check
and the placer were always asking one function the same question; the only thing the check added was
asking it again, once per map generated, for ever. Here the predicate is unit-tested directly and the
carve's output is asserted once per code change.

WHY A ROLLED MAP AND NOT A HAND-BUILT MANIFEST. Every rule here is a property of the CARVE - of what
`build_comb` and `close_seams` produce out of a real fan - and a hand-built ring lattice would be the
test author asserting against their own drawing. The roll comes from the roll cache, so it costs nothing
while nothing it executes has changed.

NON-VACUITY IS ASSERTED, NOT ASSUMED. Every one of these rules is of the shape the gate doc warns about -
"a check that never RUNS looks exactly like a check that passes" - because each skips a field with no
fork, no outline, no rings or no cell. `dry_plot_furrows_vary` went blind for months in exactly that way
when its radius stopped reaching any pair. So each test states what it found before it states that the
found thing is well formed.
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache
from l7r.diagram.waterfields.banks import _GATE_MIN_AREA, floor_overhang, jog_vertices, pointed_ring

SPEC = hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")

FLOOR_OVERHANG_FT = 16.0
"""The retired check's tolerance, and its reasoning: a fan's outline legitimately runs ON the collector
centerline (the basin's low edge IS the drain polyline), so only a protrusion well past the drawn water -
max half-width 6 px - can fire."""

NEEDLE_DEG = 15.0
"""The carve demotes a ring tapering below 25 deg; the rule fires at 15, so a borderline plot the carve
deliberately allowed cannot be read as a failure. Both numbers live on `pointed_ring`."""

OVERCOUNT_CEILING = 0.04
"""`plot_rings` is a paint-order STACK, not a partition - a later basin paints out the stretch of bund it
laps, which is what makes the pair read as the single shared wall a real fan has. So the ring areas
double-count the lapped ground, and this is a CEILING on that over-count rather than a ban on the lap.
Measured over the four scripted hamlets and a 48-seed cohort in 2026-08-17: 0.53-1.06% on the pool, cohort
median ~0.9%, tail to 2.49%. 4% is ~1.6x the worst live map and fires on a doubling of it."""


def _ring_area(ring) -> float:
    n = len(ring)
    return abs(sum(ring[i][0] * ring[(i + 1) % n][1] - ring[(i + 1) % n][0] * ring[i][1] for i in range(n))) / 2.0


@pytest.fixture(scope="module")
def rolled():
    return rollcache.hamlet(SPEC)


@pytest.fixture(scope="module")
def fan(rolled):
    """The comb fan itself - a paddy field carrying a fork, an outline, rings and a design cell.

    A map with no such field would make every test below vacuously true, so finding one is the first
    assertion rather than a silent `continue`."""
    _plan, M = rolled
    fans = [f for f in (M.get("fields") or []) if f.get("kind") == "paddy" and f.get("fork") and f.get("plot_rings")]
    assert fans, "the reference roll produced no comb paddy fan, so every rule in this module would pass on nothing"
    return M, fans[0]


def test_every_ditched_paddy_has_a_floor_under_its_plots(fan) -> None:
    """`paddy_fan_has_floor`. The carve cuts plots between marched warp threads and leaves bare parchment
    triangles at the canal junctions - the head-race fork, the outfall corner, the confluences - unless a
    base fill is drawn under them first. Without it the reader sees the page showing through the field."""
    M, _f = fan
    floors = M.get("comb_floors") or {}
    ditched = {d.get("field") for d in (M.get("field_ditches") or [])}
    assert ditched, "no field carries a ditch, so this rule would judge nothing"
    bare = [f.get("name") for f in M["fields"] if f.get("kind") == "paddy" and f.get("name") in ditched and f.get("name") not in floors]
    assert not bare, f"comb paddy fan(s) with no field floor: {bare}"


def test_the_floor_stops_where_the_command_area_does(fan) -> None:
    """`comb_floor_ends_at_the_collector`. Ground down-fall of the collector - extended LEVEL beyond the
    drain's drawn ends, exactly as the wedge filler extends it - cannot drain and is never planted, so
    floor there is dead ground wearing the field's color. The motivating defect was Mizuguchi's SE wedge,
    whose raw envelope closed across ~350 ft of bare ground and read as a green needle past the drain."""
    M, f = fan
    outline = [(float(v[0]), float(v[1])) for v in (f.get("outline") or [])]
    assert len(outline) >= 3, "the fan records no outline, so its overhang cannot be measured"
    drains = [d for d in (M.get("field_ditches") or []) if d.get("role") == "drain" and d.get("field") == f.get("name")]
    assert drains, "the fan records no collector, so the rule would judge nothing"
    down = float(f.get("down_deg", M["meta"].get("down_deg", 90.0)))
    for d in drains:
        pts = [(float(q[0]), float(q[1])) for q in (d.get("poly") or [])]
        worst = max(floor_overhang(outline, pts, down))
        assert worst <= FLOOR_OVERHANG_FT, f"the floor runs {worst:.0f} px past the collector - dead ground wearing the field's color"


def test_the_supply_commands_both_flanks_of_the_fan(fan) -> None:
    """`comb_supply_commands_both_flanks`. Water enters at the fork and must be able to reach BOTH sides
    of it; a fan whose delivery ditches all run to one side has half its plots painted as irrigated with
    nothing to irrigate them. Flank membership is the SIGN of a vertex's cross-slope offset from the fork -
    an aggregate bearing question, which is legitimate on vertices because every quantity here is an
    EXTENT, not a gap verdict."""
    M, f = fan
    ftpx = float(M["meta"].get("ftpx") or 1.0)
    fork = f.get("fork")
    down = float(f.get("down_deg", M["meta"].get("down_deg")))
    cross = (-math.sin(math.radians(down)), math.cos(math.radians(down)))

    def offset(v):
        return (v[0] - fork[0]) * cross[0] + (v[1] - fork[1]) * cross[1]

    extent = [0.0, 0.0]
    for ring in f.get("plot_rings") or []:
        for v in ring:
            s = offset(v)
            extent[0 if s >= 0 else 1] = max(extent[0 if s >= 0 else 1], abs(s))
    reach = [0.0, 0.0]
    for d in M.get("field_ditches") or []:
        if d.get("field") != f.get("name") or d.get("role") not in ("main", "branch"):
            continue
        for v in d["poly"]:
            s = offset(v)
            reach[0 if s >= 0 else 1] = max(reach[0 if s >= 0 else 1], abs(s))
    assert min(extent) > 150.0 / ftpx, f"the fan is one-sided ({extent}), so this rule would judge only one flank"
    for i in (0, 1):
        floor = max(80.0 / ftpx, 0.3 * extent[i])
        assert reach[i] >= floor, f"the {'+' if i == 0 else '-'}cross flank has {round(extent[i] * ftpx)} ft of plots and only {round(reach[i] * ftpx)} ft of supply"


def test_no_basin_tapers_to_a_point(fan) -> None:
    """`paddy_plots_are_workable_basins`. A paddy is a LEVEL, BUNDED, PUDDLED unit holding standing water
    at an even depth. Narrowness is authentic - the strips at Shiroyone Senmaida really are a few feet
    wide - and so is radial convergence, because a cascade fan genuinely narrows to its outfall. What no
    real basin does is taper to ZERO: a 7.5 deg wedge is 2.6 ft wide 20 ft back from its point while an
    aze is ~1.5 ft of puddled mud on EACH side, so the last yards are two bunds with no floor between
    them. Real systems truncate the point instead - a headland strip along the collector, or the corner
    left unpaddied."""
    _M, f = fan
    rings = f["plot_rings"]
    needles = [i for i, r in enumerate(rings) if pointed_ring([(float(a), float(b)) for a, b in r], NEEDLE_DEG)]
    assert not needles, f"{len(needles)} of {len(rings)} basins taper below {NEEDLE_DEG} deg"


def test_a_flooded_plot_reads_as_a_basin_and_not_as_a_pond(fan) -> None:
    """`flooded_plots_read_as_basins`. At a fan seam the closing rank's converging sub-columns taper to
    sharp apexes, and the ones carrying the FLOODED tint read as tiny triangular PONDS at fit zoom - which
    was conspicuous on Sawada, whose brief is "no pond". `flooded_plots` is the PICTURE record (which
    plots are painted blue); `wet_plots` is the topography."""
    M, f = fan
    flooded = M.get("flooded_plots") or []
    assert flooded, "the roll painted no flooded plot, so this rule would judge nothing"
    rings = [[(float(a), float(b)) for a, b in r] for r in f["plot_rings"]]
    cents = [(sum(p[0] for p in r) / len(r), sum(p[1] for p in r) / len(r)) for r in rings]
    matched = 0
    for w in flooded:
        wx, wy = float(w[0]), float(w[1])
        best, dist = None, 3.0  # vertex-mean vs recorded centroid: a couple of px of slack
        for i, (cx, cy) in enumerate(cents):
            d = math.hypot(cx - wx, cy - wy)
            if d < dist:
                best, dist = i, d
        if best is None:
            continue  # a fill path that recorded no ring - not judgeable
        matched += 1
        assert not pointed_ring(rings[best], NEEDLE_DEG), f"the flooded plot at ({round(wx)}, {round(wy)}) is a needle, so it reads as a pond"
    assert matched, "no flooded plot matched a recorded ring, so the rule judged nothing"


def test_no_basin_is_too_small_to_be_worth_its_own_bund(fan) -> None:
    """`paddy_basins_are_worth_their_bund`. The GM's question was about "a few very small triangles" among
    otherwise rectangular paddies; the triangularity was the symptom - a clipped corner where the plot
    lattice meets the fan boundary - and the size is the cause, so the rule is written on size.

    THERE IS NO ABSOLUTE MINIMUM. Shiroyone Senmaida works 1,004 basins averaging ~18-20 m2, the smallest
    about half a meter square, and a floor in acres would condemn them. The floor is a RATIO to the fan's
    OWN design cell, which `build_comb` writes onto the field because `plot_texture` scales the target per
    map - recomputing the grain here would hold a `small_irregular` fan to a cell it never aimed at."""
    _M, f = fan
    cell = f.get("cell")
    assert cell, "the fan records no design cell, so the ratio has no denominator and the rule would skip"
    ratios = sorted(_ring_area(r) / float(cell) for r in f["plot_rings"])
    assert ratios[0] >= _GATE_MIN_AREA, f"the smallest basin is {ratios[0]:.3f} of the design cell, under the {_GATE_MIN_AREA} floor"


def test_the_rings_double_count_only_marginally(fan) -> None:
    """`paddy_plot_rings_overcount_stays_marginal`. Each paddy is one polygon carrying fill AND stroke,
    emitted in index order, so a later basin paints out the stretch of bund it laps - which is what makes
    the pair read as the single shared wall a real fan has. The record is therefore honest about the INK
    and is NOT a partition: sum the ring areas and the lapped ground is counted twice.

    The cost is latent - nothing measures acreage off these rings today - and it lands on the first future
    rule that does. What the ceiling buys is that an acreage read off the undissolved stack stays wrong by
    less than one significant figure, which is what makes "dissolve before you measure" a small documented
    approximation rather than a trap."""
    shapely = pytest.importorskip("shapely.geometry")
    _M, f = fan
    rings = [shapely.Polygon([(float(a), float(b)) for a, b in r]).buffer(0) for r in f["plot_rings"]]
    from shapely.ops import unary_union

    union = unary_union(rings)
    assert union.area > 0, "the rings union to nothing, so the over-count has no denominator"
    over = (sum(r.area for r in rings) - union.area) / union.area
    assert over < OVERCOUNT_CEILING, f"the plot rings over-count the fan by {over:.1%}, past the {OVERCOUNT_CEILING:.0%} ceiling"


def test_a_bund_does_not_build_a_flight_of_steps(fan) -> None:
    """`paddy_bunds_do_not_stagger`. The GM read it off Inashiro: a wall running south "instead of just
    continuing on and meeting at the four way intersection ... goes sharply to the left before going down,
    thus making these extremely irregular shapes. This really, really looks like a rendering error." It
    was one - `close_seams` made it and the carve does not, which snapshotting the pass's input and output
    proved: 0 steps on Inashiro's 543 carved rings, 26 on the 634 it handed back.

    THE RULE IS "MORE THAN ONE ON A RING", NOT "ANY AT ALL", and that is the thing to understand before
    retuning it. The shape reported is a STAIRCASE - a wall that steps, steps again, and steps again - and
    that is what a weld pitch out of register with the fabric produces. A SINGLE step is a different
    animal: one awkward corner where a scrap of ground had exactly one home and the repair pass could not
    move the wall without breaking another rule. Seven of those survive across the pool, each ledgered
    with the guard that refuses it.

    The grain conversion is the engine's own (`grain = 2 / ftpx`), taken from `tools/jogs.py` rather than
    restated as a second rule of thumb that would drift."""
    M, f = fan
    grain = 2.0 / float(M["meta"].get("ftpx") or 1.0)
    staircases = [i for i, r in enumerate(f["plot_rings"]) if len(jog_vertices([(float(a), float(b)) for a, b in r], grain)) > 1]
    assert not staircases, f"{len(staircases)} plot ring(s) carry more than one step - a staircase, not a nudge"
