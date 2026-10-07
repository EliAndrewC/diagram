"""The comb's DRY HEM and a wild fan middle's reserve (split out of `comb.py` at its 1,000-line bar, feature 287 W36).

`_comb_dry_and_beans` lays the hem of dry fields above the supply canal and the bund beans; `fan_toe_hem` keeps a wild
fan's hem on the toe; `middle_reserve` offers the whole wild middle, cleared deep and nearest the toe first, for the
coarse-grain top-up the draw makes (`settlement/fields/grain.py`, research/contents.json#fields 0011).

Research: hem plumbing - NONE: the canal's run above a cut, ring means, overlap tests and their box index
"""

import math
import random
from collections.abc import Sequence
from typing import Any

from .carve import _bund_beans, _dry_fields
from .frame import Poly, Pt, _Frame, _poly_area, _Thread
from .furrows import STEEP_SPREAD_RAD, settle_tract_seams


def _comb_dry_and_beans(
    R: random.Random,
    F: _Frame,
    a_pts: Poly,
    bc: _Thread,
    plots: list[dict[str, Any]],
    channels: list[dict[str, Any]],
    W: float,
    H: float,
    dry_keepout: Sequence[tuple[float, float, float]],
    dry_band: tuple[float, float],
    bean_frac: float,
    grain: float,
    furrow_spread: float,
    grain_drift: float,
    fan_middle: str,
    fork: Pt,
) -> tuple[list[dict[str, Any]], float, list[Poly], list[dict[str, Any]]]:
    """DRY FIELDS (hatake) on the uncommanded upslope margin above the supply canal, and
    BUND BEANS (azemame) beaded along a fraction of the paddy bunds - see research/questions/0014-bunds-between-the-paddies-aze.html.

    Research:
        dry hem above the canal - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the hem laid upslope of supply canal A
        fork triangle planted dry - research/questions/0010-farmland-around-towns-and-cities.drawing.html: on a city's coarse grain (`grain < 1.0`) a second band along canal B's stretch above its first offtake
        fork band depth - UNRESEARCHED: 0.6 of the hem's depth
        fork band skipped on villages - UNRESEARCHED: grain 1.0 maps leave the triangle to the scrub
        wild middle - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a wild fan keeps its drawn hem on the toe, the middle held in reserve
        seams settled - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: every band's tracts read apart where the rows spread
        bund beans - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: beads along a share of the paddy bunds
        dry acreage scale - NONE: measured at a fixed 2 ft/px whatever the grain
    """
    # The hem's stand-off is derived from the SUPPLY strokes' drawn banks (`CANAL_BERM_FT`), so the
    # drawn channels have to be in hand - they are, because this pass runs after `_comb_canal_pieces`
    # and after `round_channel_joints`, i.e. against the geometry that will actually be painted.
    _supply_strokes = [c for c in channels if c.get("role") != "drain"]
    dry_plots = _dry_fields(R, F, a_pts, W, H, dry_keepout, band=dry_band, g=grain, furrow_spread=furrow_spread, grain_drift=grain_drift, supply=_supply_strokes)
    hem = list(dry_plots)  # the a-side hem whole: a wild middle's share is split off AFTER the seams are settled (feature 287, W36)
    if grain < 1.0:  # a city's grain only (0010), never a hamlet's or a village's
        # the INTER-ARM FORK TRIANGLE (coarse grains only): the ground between the two supply
        # canals just below the fork is commanded by neither (it sits upslope of canal B), and
        # on a village map the scrub matrix textures it - a city map has no scrub, so it read
        # as the blank wedge the GM circled at every fan head (2026-07-21). Historically it is
        # prime dry-crop ground beside the head-race, so quilt it: a second hem band along
        # canal B's SUPPLY stretch, whose upslope normal points INTO the triangle. Village
        # maps skip this (byte-stability; their scrub already covers the same ground).
        # ...and the band spans only the stretch that BORDERS the triangle: up to bc's first
        # offtake, where the paddy bc itself commands begins. When canal B carries offtakes
        # (every scripted row since 2026-08-16), running the band to ditch_f strings hem plots
        # along ground that is now carved RICE - Cohort-41 dropped a soy plot square on the
        # paddy and its delivery ditch that way. With no offtakes the two bounds coincide.
        _bc_tri_f = min(list(getattr(bc, "offtake_fs", []) or []) + [bc.ditch_f])
        _bc_supply = [p for p in bc.pts if F.to_uf(*p)[1] <= _bc_tri_f]
        if len(_bc_supply) >= 2:
            dry_plots += _dry_fields(
                R,
                F,
                _bc_supply,
                W,
                H,
                dry_keepout,
                band=(dry_band[0] * 0.6, dry_band[1] * 0.6),
                g=grain,
                furrow_spread=furrow_spread,
                grain_drift=grain_drift,
                supply=_supply_strokes,
                tract0=1 + max((p["tract"] for p in dry_plots), default=-1),
            )  # thinner than the a-side hem: it only needs to cover the fork triangle, and a full-depth band crowds the farmhouse ring off the fan's visible edge
    reserve: list[dict[str, Any]] = []
    if fan_middle == "wild":  # the toe's strip is drawn; the whole wild middle is held in reserve (feature 287, W36)
        _toe = {id(d) for d in fan_toe_hem(hem, F, fork, plots)}
        dry_plots = [d for d in dry_plots if id(d) in _toe or all(d is not h for h in hem)]
        _tract0 = 1 + max((p["tract"] for p in dry_plots), default=-1)
        reserve = middle_reserve(R, F, a_pts, fork, plots, dry_plots, W, H, dry_keepout, grain, furrow_spread, grain_drift, _supply_strokes, _tract0)
    if furrow_spread >= STEEP_SPREAD_RAD:  # the patchwork's seams read tract against tract, every band and the reserve (feature 287, W35)
        settle_tract_seams(dry_plots + reserve)
    dry_acres = sum(_poly_area(p["poly"]) for p in dry_plots) * 4 / 43560
    return dry_plots, dry_acres, _bund_beans(R, plots, bean_frac, channels=channels), reserve


# WHERE A FAN'S DRY BAND LIES (269 B07; research/questions/0006-dry-fields-and-their-crops-hatake.html,
# 0006). On an alluvial fan the middle, where the river sinks underground, is too short of water for paddy and was
# often left as coppice or wild ground until late in the early modern period, while the spring-fed toe was settled early
# with paddy beside it. The record calls that a tendency, not a rule - in old heartlands fans were cleared from early
# times - so it is a KNOB, `fan_middle` (hamletgen/water/fit.py): "wild" draws the hem only on the toe's stretch of the fan's edge and
# holds the middle's in reserve for the coarse-grain top-up (`middle_reserve`, 0011), "cleared" hems the whole canal. The comb IS
# the fan (apex the division point, toe the collector), so the stretch is read along the fall from the fork to the lowest paddy; the fork-triangle
# band is the fan's HEAD and stays. FAN_TOE_FROM: where the toe begins, a share of that fall - the record gives no proportions, equal thirds is a GUESS.
FAN_TOE_FROM = 2.0 / 3.0
"""Research: where the toe begins - GUESS: two-thirds of the fall from the fork to the lowest paddy"""


def fan_toe_hem(dry_plots: list[dict[str, Any]], F: _Frame, fork: Pt, plots: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """The hem plots whose center lies at or below the toe's cut (`toe_cut`); all of them on a fan with no fall.

    Research: hem on the toe - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: where the middle stays wild the hem keeps to the fan's toe
    """
    cut = toe_cut(F, fork, plots)
    return dry_plots if cut is None else [d for d in dry_plots if F.to_uf(*_ring_mean(d["poly"]))[1] >= cut]


def toe_cut(F: _Frame, fork: Pt, plots: Sequence[dict[str, Any]]) -> float | None:
    """The fall at which the toe begins (`FAN_TOE_FROM` of the way from the fork to the lowest paddy); None on a fan with no fall.

    Research: toe cut - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: FAN_TOE_FROM of the fall from the fork to the lowest paddy
    """
    f0 = F.to_uf(*fork)[1]
    f1 = max((F.to_uf(float(v[0]), float(v[1]))[1] for p in plots for v in p["poly"]), default=f0)
    return None if f1 - f0 <= 0 else f0 + (f1 - f0) * FAN_TOE_FROM


def middle_stretch(F: _Frame, a_pts: Poly, cut: float) -> Poly:
    """The canal's run above the toe: its points while the fall is short of `cut`, ended where the canal crosses it."""
    out: list[Pt] = []
    for a, b in zip(a_pts, a_pts[1:], strict=False):
        fa, fb = F.to_uf(*a)[1], F.to_uf(*b)[1]
        if fa >= cut:
            break
        out.append(a)
        if fb >= cut:
            t = (cut - fa) / (fb - fa)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            return out
    return out + ([a_pts[-1]] if out and F.to_uf(*a_pts[-1])[1] < cut else [])


# HOW DEEP THE WILD MIDDLE IS OFFERED (W36): the whole of it, out to the canvas - `MIDDLE_DEPTH_OF_CANVAS` of the canvas
# diagonal from the canal, which reaches every edge, and `_dry_fields` drops a plot within 12 px of one. The draw takes
# only what the grain needs, so the depth offered costs plots laid and filtered, not ground drawn.
MIDDLE_DEPTH_OF_CANVAS = 1.0
"""Research: middle offered to the canvas edge - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: the plots may climb out as far from the canal as the ground runs"""


def middle_reserve(
    R: random.Random,
    F: _Frame,
    a_pts: Poly,
    fork: Pt,
    paddies: Sequence[dict[str, Any]],
    drawn: Sequence[dict[str, Any]],
    W: float,
    H: float,
    keepout: Sequence[tuple[float, float, float]],
    g: float,
    furrow_spread: float,
    grain_drift: float,
    supply: Sequence[dict[str, Any]],
    tract0: int,
) -> list[dict[str, Any]]:
    """THE WHOLE WILD MIDDLE, as dry plots the coarse-grain top-up may clear (feature 287, W36; 0011): the hem's
    columns along the canal's run above the toe, laid out to the canvas edge, less any plot on the fan's own paddy or on a
    dry plot already drawn - ordered nearest the toe first (down the fall first), the top-up's order, a GUESS.

    Research:
        the wild middle as reserve - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: hem columns along the canal above the toe, off the paddy and the drawn hem
        clearing order - GUESS: nearest the toe first
    """
    cut = toe_cut(F, fork, paddies)
    run = middle_stretch(F, a_pts, cut) if cut is not None else []
    if len(run) < 2:
        return []
    depth = math.hypot(W, H) * MIDDLE_DEPTH_OF_CANVAS
    deep = _dry_fields(random.Random(R.getrandbits(32)), F, run, W, H, keepout, band=(depth, depth), g=g, furrow_spread=furrow_spread, grain_drift=grain_drift, supply=supply, tract0=tract0)
    taken = BoxedRings([p["poly"] for p in paddies if len(p["poly"]) >= 3] + [d["poly"] for d in drawn])
    keep = [d for d in deep if not overlaps_any(d["poly"], taken)]
    return sorted(keep, key=lambda d: -F.to_uf(*_ring_mean(d["poly"]))[1])


class BoxedRings:
    """`overlaps_any`'s rings with each one's box taken once and its cleaned polygon built at most once, the first time a
    plot's box meets it (feature 287 perf: the wild middle's every plot re-derived every paddy's box and re-built its
    polygon - 474 plots on the reference seed 4). The same boxes and the same polygons, so the same verdicts."""

    __slots__ = ("boxes", "polys", "rings")

    def __init__(self, rings: Sequence[Poly]) -> None:
        self.rings = list(rings)
        self.boxes = [(min(q[0] for q in r), min(q[1] for q in r), max(q[0] for q in r), max(q[1] for q in r)) for r in self.rings]
        self.polys: list[Any] = [None] * len(self.rings)

    def poly(self, k: int) -> Any:
        from shapely.geometry import Polygon

        if self.polys[k] is None:
            self.polys[k] = Polygon(self.rings[k]).buffer(0)
        return self.polys[k]


def overlaps_any(poly: Poly, rings: Sequence[Poly] | BoxedRings) -> bool:
    """Does `poly` share more than a square pixel of ground with any of `rings` (a seam shared edge to edge does not count)?"""
    from shapely.geometry import Polygon

    boxed = rings if isinstance(rings, BoxedRings) else BoxedRings(rings)
    a = Polygon(poly).buffer(0)
    x0, y0, x1, y1 = a.bounds
    for k, (rx0, ry0, rx1, ry1) in enumerate(boxed.boxes):
        if rx1 < x0 or rx0 > x1 or ry1 < y0 or ry0 > y1:
            continue
        if a.intersection(boxed.poly(k)).area > 1.0:
            return True
    return False


def _ring_mean(ring: Sequence[Pt]) -> Pt:  # where `fan_toe_hem` reads a hem plot to stand
    return sum(v[0] for v in ring) / len(ring), sum(v[1] for v in ring) / len(ring)
