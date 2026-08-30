"""The earth that holds the water in (feature 166).

Carries nine rules the retired battery re-measured on every finished map: `paddy_bunds_clear_the_collector`,
`paddy_bunds_clear_the_supply_channels`, `paddy_plot_seams_shared`, `bund_beans_on_bunds`,
`dry_plot_furrows_vary`, `polder_dike_is_earthwork`, `polder_channels_clear_of_dike`,
`structures_clear_of_dike` and `waterward_strips_run_off_the_frame`.

A BUND IS THE WALL BETWEEN TWO THINGS, AND EVERY RULE HERE IS ABOUT WHICH TWO. An aze holds one basin's
water in while the ditch beside it carries other water past, so the two can only ABUT - at the bank. A
polder's dike holds the whole settlement's water OUT, so nothing is built on it and no channel is cut
through it. The physical claim never changes; only which body of water is on which side.

THE GM READ THE COLLECTOR DEFECT OFF A SHEET (2026-08-15, on Inashiro): "the earth bunds which border the
irrigated channel ... are actually in the middle of the water instead of along the water's edge. I think
they are supposed to be along the water's edge." They were: `_carve`'s bund routine returns thread
CENTERLINES and the supply strokes are drawn centered on those same lines, so the first and last column of
every sector carried bunds running down the middle of the drawn water. 266 sampled bund-edge points sat
inside a supply stroke, the worst 6.1 px deep in a ~12 px channel.

THE PREDICATE IS THE ENGINE'S OWN, NOT A RESTATEMENT. `supply_bank_clearance` is the same call `_carve`'s
`clear_supply` makes when it lays the bund, which is the whole shape of this feature: the placer and the
check were asking one function the same question, and only the placer needs to.
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache
from l7r.diagram.waterfields.banks import supply_bank_clearance

INASHIRO = hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")
KUWABATA = hg.HamletSpec(name="Kuwabata", seed=21, households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic", dike_crop="mulberry")

DIKE_IRREGULARITY = 1.4
"""How much wider a dike's widest stretch must be than its narrowest. A uniform-width band reads as a
post-1949 ruled rectangle; a hand-piled fish-scale polder dike is irregular because it was built by
carrying baskets of spoil, and every year's repair added where the water took most."""

SAME_ROW_RAD = 0.10
"""Two furrow directions within ~6 degrees read as the SAME row direction. `theta` is in RADIANS, and the
comparison is modulo pi because a furrow has no head and tail."""


def _seg_dist(px: float, py: float, a, b) -> float:
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def _cum(pts):
    out = [0.0]
    for i in range(len(pts) - 1):
        out.append(out[-1] + math.dist(pts[i], pts[i + 1]))
    return out


def _point_in(pt, ring) -> bool:
    x, y = float(pt[0]), float(pt[1])
    inside, n = False, len(ring)
    for i in range(n):
        x0, y0 = float(ring[i][0]), float(ring[i][1])
        x1, y1 = float(ring[(i + 1) % n][0]), float(ring[(i + 1) % n][1])
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            inside = not inside
    return inside


@pytest.fixture(scope="module")
def comb():
    return rollcache.hamlet(INASHIRO)


@pytest.fixture(scope="module")
def polder():
    return rollcache.hamlet(KUWABATA)


def test_no_bund_is_drawn_down_the_middle_of_a_supply_channel(comb) -> None:
    """`paddy_bunds_clear_the_supply_channels`. A paddy's canal-side bund IS the supply channel's bank -
    the bund holds the basin's water in and the channel carries other water past, so the two can only
    abut. A bund down the middle of the water is the drawing having forgotten which side of the wall each
    body of water is on.

    Measured perpendicular to the stroke with its taper honored, and vertices projecting past a stroke's
    ENDS are skipped: ground beyond the span is not governed by it - a delivery ditch's takeoff sits ON
    its parent canal, which governs there in its own right."""
    _plan, M = comb
    field = next((f for f in (M.get("fields") or []) if f.get("plot_rings")), None)
    assert field, "the roll carved no plot rings, so this rule would judge nothing"
    supplies = [d for d in (M.get("field_ditches") or []) if d.get("role") in ("main", "branch") and d.get("field") == field.get("name")]
    assert supplies, "the fan has no supply channel, so this rule would judge nothing"
    judged, inside = 0, []
    for fd in supplies:
        pts = [(float(p[0]), float(p[1])) for p in (fd.get("poly") or [])]
        if len(pts) < 2:
            continue
        w0 = float(fd.get("w", 2.0))
        w1 = float(fd.get("w_tail", w0))
        cum = _cum(pts)
        for ring in field["plot_rings"]:
            for q in ring:
                _gap, _half, on_span, _a, _b = supply_bank_clearance((float(q[0]), float(q[1])), pts, w0, w1, cum)
                if not on_span:
                    continue
                judged += 1
                if _gap < 0:
                    inside.append((round(float(q[0])), round(float(q[1]))))
    assert judged, "no bund vertex fell along a supply stroke's span, so this rule judged nothing"
    assert not inside, f"{len(inside)} bund vertex/vertices are drawn INSIDE a supply channel's stroke: {inside[:4]}"


def test_no_bund_is_drawn_across_the_collector(comb) -> None:
    """`paddy_bunds_clear_the_collector`. The supply half's twin, one ditch over: a paddy's LOW bund is
    the collector's bank, so the field hems ONTO the drain with its bunds running WITH it, never across
    it. A bund crossing the collector would dam the thing that drains the field."""
    _plan, M = comb
    field = next((f for f in (M.get("fields") or []) if f.get("plot_rings")), None)
    assert field, "the roll carved no plot rings"
    drains = [d for d in (M.get("field_ditches") or []) if d.get("role") == "drain" and d.get("field") == field.get("name")]
    assert drains, "the fan has no collector, so this rule would judge nothing"
    across = []
    for d in drains:
        pts = [(float(p[0]), float(p[1])) for p in d["poly"]]
        half = max(float(d.get("w", 3.0)), float(d.get("w_tail", 3.0))) / 2.0
        for ring in field["plot_rings"]:
            n = len(ring)
            for k in range(n):
                a = (float(ring[k][0]), float(ring[k][1]))
                b = (float(ring[(k + 1) % n][0]), float(ring[(k + 1) % n][1]))
                # a SEGMENT that starts one side of the drain and ends the other has crossed it
                if min(_seg_dist(a[0], a[1], pts[i], pts[i + 1]) for i in range(len(pts) - 1)) < half * 0.5 and min(
                    _seg_dist(b[0], b[1], pts[i], pts[i + 1]) for i in range(len(pts) - 1)
                ) < half * 0.5 and math.dist(a, b) > 2 * half:
                    across.append((round(a[0]), round(a[1])))
    assert not across, f"{len(across)} paddy bund(s) run across the collector rather than along it: {across[:4]}"


def test_every_bund_bead_sits_on_visible_ground(comb) -> None:
    """`bund_beans_on_bunds`. Azemame - soybeans grown along the bund tops - are drawn as beads on the
    wall. A bead laid on a bund stroke that a later-drawn plot fill or a water stroke paints OVER is a
    bead floating on somebody else's paint: the record carries ink the finished page does not show, and
    the reader sees beans apparently growing on water.

    The wedge fillers lap their neighbors ON PURPOSE (that lap is what makes a shared bund read as one
    wall), so the burial is a consequence of a deliberate choice elsewhere and has to be filtered at the
    bead, not fixed by unlapping the plots."""
    _plan, M = comb
    field = next((f for f in (M.get("fields") or []) if f.get("bund_beans")), None)
    assert field, "the roll laid no bund beads, so this rule would judge nothing"
    beads = [(float(b[0]), float(b[1])) for b in field["bund_beans"]]
    assert beads, "the field records an empty bead list"
    # THE BAR IS THE STROKE'S OWN HALF-WIDTH, not a flat tolerance. A bead legitimately sits on the bund
    # that IS a ditch's bank, so it is close to the centerline by construction; what buries it is being
    # inside the drawn water. My first draft used a flat 2 px and reported one false burial - measured,
    # zero beads of 621 are inside any stroke.
    water = [([(float(q[0]), float(q[1])) for q in d["poly"]], max(float(d.get("w", 3.0)), float(d.get("w_tail", 3.0))) / 2.0) for d in (M.get("field_ditches") or [])]
    water += [([(float(q[0]), float(q[1])) for q in c["poly"]], float(c.get("w", 3.0)) / 2.0) for c in (M.get("channels") or [])]
    drowned = []
    for bx, by in beads:
        for poly, half in water:
            if min(_seg_dist(bx, by, poly[i], poly[i + 1]) for i in range(len(poly) - 1)) < half:
                drowned.append((round(bx), round(by)))
                break
    pond = M.get("pond")
    if pond:
        drowned += [(round(bx), round(by)) for bx, by in beads if ((bx - pond[0]) / pond[2]) ** 2 + ((by - pond[1]) / pond[3]) ** 2 <= 1.0]
    assert not drowned, f"{len(drowned)} azemame bead(s) sit on water rather than on visible bund: {drowned[:4]}"


def test_neighboring_dry_plots_are_ploughed_at_different_angles(comb) -> None:
    """`dry_plot_furrows_vary`. Dry plots carry a furrow direction, and edge-adjacent plots ploughed at
    the same angle read as one machine-cut block rather than as separate households' ground. Each holding
    was ploughed to its OWN plot's shape by its own household with its own team.

    THE ADJACENCY RADIUS DERIVES FROM THE PLOTS' OWN SIZE, and that is the whole history of this rule. It
    used to be a flat 50 px cap, which made the check VACUOUS: mean plot side on the scripted hamlets is
    81-87 ft, so the formula wants ~102 and the cap forced 50 - below every map's closest plot spacing
    (54-59 ft), so it compared ZERO pairs on all four maps and had been doing so for as long as the plots
    had been that size. It went blind in the same moment and for the same reason as the GENERATOR feeding
    it, whose own adjacency radius was also a flat pixel figure: the two were calibrated against each
    other rather than against the plots, so when the plots outgrew both, neither could catch the other."""
    _plan, M = comb
    plots = [p for p in (M.get("dry_plots") or []) if p.get("poly") and p.get("theta") is not None]
    assert len(plots) >= 4, f"the roll drew {len(plots)} angled dry plots - too few for adjacency to mean anything"
    cents = [(sum(v[0] for v in p["poly"]) / len(p["poly"]), sum(v[1] for v in p["poly"]) / len(p["poly"])) for p in plots]
    sides = []
    for p in plots:
        pp = p["poly"]
        n = len(pp)
        area = abs(sum(pp[i][0] * pp[(i + 1) % n][1] - pp[(i + 1) % n][0] * pp[i][1] for i in range(n))) / 2
        sides.append(area**0.5)
    radius = 1.25 * (sum(sides) / len(sides))
    # `theta` IS IN RADIANS. My first draft compared it in degrees, called all 24 adjacent pairs identical
    # and reported a defect that is not there - the live spread is -0.9 to +0.8 rad, i.e. -52 to +46 deg.
    # Two plots read as the same row direction within ~6 deg (0.10 rad), modulo pi because a furrow has
    # no head and tail.
    pairs, same = 0, []
    for a in range(len(plots)):
        for b in range(a + 1, len(plots)):
            if math.dist(cents[a], cents[b]) >= radius:
                continue
            pairs += 1
            d = abs(float(plots[a]["theta"]) - float(plots[b]["theta"])) % math.pi
            if min(d, math.pi - d) <= 0.10:
                same.append((round(cents[a][0]), round(cents[a][1])))
    assert pairs, f"no dry-plot pair fell inside the derived adjacency radius of {radius:.0f} px - the rule is blind again"
    assert not same, f"{len(same)} adjacent dry-plot pair(s) run their furrows the same way: {same[:3]}"


def test_the_polder_dike_is_a_hand_piled_earthwork(polder) -> None:
    """`polder_dike_is_earthwork`. A polder dike is a band of VARYING width. It was built by carrying
    baskets of spoil and repaired every year where the water took most, so it is irregular by
    construction; a uniform-width band reads as a post-1949 ruled rectangle rather than as a hand-piled
    fish-scale polder."""
    _plan, M = polder
    dikes = M.get("dikes") or []
    assert dikes, "the polder roll drew no dike, so this rule would judge nothing"
    for dk in dikes:
        wmn, wmx = float(dk.get("w_min", 0.0)), float(dk.get("w_max", 0.0))
        assert wmn > 0 and wmx >= DIKE_IRREGULARITY * wmn, f"the dike is {wmn:.0f}-{wmx:.0f} px wide - too uniform to read as hand-piled earth"


def test_nothing_is_built_on_the_dike(polder) -> None:
    """`structures_clear_of_dike`. The dike is what keeps the water out; it is walked, repaired and
    watched, and a house on it is a house on the one earthwork the settlement cannot afford to weaken.
    The keepout the dike records is exactly the ground the placer must leave alone."""
    _plan, M = polder
    dikes = [dk for dk in (M.get("dikes") or []) if dk.get("keepout")]
    assert dikes, "the polder roll recorded no dike keepout, so this rule would judge nothing"
    built = []
    for key in ("houses", "farm_sheds", "byres", "threshing_yards"):
        for r in M.get(key) or []:
            if "x" not in r:
                continue
            for dk in dikes:
                ring = [(float(p[0]), float(p[1])) for p in dk["keepout"]]
                if _point_in((float(r["x"]), float(r["y"])), ring):
                    built.append((key, round(float(r["x"])), round(float(r["y"]))))
    assert not built, f"structure(s) stand inside the dike's keepout: {built[:4]}"


def test_no_channel_is_cut_through_the_dike_except_at_its_gaps(polder) -> None:
    """`polder_channels_clear_of_dike`. Water crosses a dike only where the settlement decided it should -
    at the inlet sluice and the outfall, which the dike records as its GAPS. A channel cut through
    anywhere else is a breach, and a breach in a polder dike is the end of the polder."""
    _plan, M = polder
    dikes = [dk for dk in (M.get("dikes") or []) if dk.get("crest")]
    assert dikes, "the polder roll recorded no dike crest, so this rule would judge nothing"
    courses = [[(float(p[0]), float(p[1])) for p in d["poly"]] for d in (M.get("field_ditches") or []) if d.get("poly")]
    courses += [[(float(p[0]), float(p[1])) for p in c["poly"]] for c in (M.get("channels") or []) if c.get("poly")]
    assert courses, "the polder roll drew no channel, so this rule would judge nothing"
    breaches = []
    for dk in dikes:
        crest = [(float(p[0]), float(p[1])) for p in dk["crest"]]
        gaps = [(float(g[0]), float(g[1])) for g in (dk.get("gaps") or [])]
        for poly in courses:
            for i in range(len(poly) - 1):
                mid = ((poly[i][0] + poly[i + 1][0]) / 2, (poly[i][1] + poly[i + 1][1]) / 2)
                if min(_seg_dist(mid[0], mid[1], crest[k], crest[k + 1]) for k in range(len(crest) - 1)) > 3.0:
                    continue
                if gaps and min(math.dist(mid, g) for g in gaps) <= 60.0:
                    continue  # the sluice or the outfall - a decided crossing
                breaches.append((round(mid[0]), round(mid[1])))
    assert not breaches, f"channel(s) cross the dike away from its gaps: {sorted(set(breaches))[:4]}"


def test_the_waterward_reed_strip_runs_off_the_frame(polder) -> None:
    """`waterward_strips_run_off_the_frame`. On the waterward side the map shows the edge of a bigger
    water than it draws, and the reed fringe along it must run OFF the picture. Cut to a band that stops
    inside the frame, it gives the reader a straight line where wild water stops being wild - a lake with
    a ruled edge.

    The rule exists because the fix for an earlier defect introduced this one: the strip was changed from
    "drawn to the canvas edge" to a fixed depth band, and a band can end inside the view."""
    _plan, M = polder
    faces = M["meta"].get("waterward") or []
    view = M["meta"].get("view")
    strips = [m for m in (M.get("marshes") or []) if m.get("role") == "waterside" and m.get("poly")]
    assert faces and view and strips, "the roll declares no waterward face, view or reed strip, so this rule would judge nothing"
    vx0, vy0, vw, vh = (float(v) for v in view)
    short = []
    for m in strips:
        xs = [float(q[0]) for q in m["poly"]]
        ys = [float(q[1]) for q in m["poly"]]
        reach = {"W": min(xs) <= vx0, "E": max(xs) >= vx0 + vw, "N": min(ys) <= vy0, "S": max(ys) >= vy0 + vh}
        if not any(reach[f] for f in faces if f in reach):
            short.append((round(min(xs)), round(min(ys))))
    assert not short, f"waterside reed strip(s) stop inside the frame: {short[:4]}"
