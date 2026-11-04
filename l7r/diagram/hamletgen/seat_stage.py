"""STAGE 4a - where the settlement sits, in Rust (feature 444 T27 D1): a thin Python function that gathers what the seat reads, calls
`l7r_phases.stage_seat`, and writes what it returns - the seat and its ladder (`plan.seat`), the brook's fords and the crossing
cost every later way pays, the watercourses the ways are routed against, the side of the field the houses stand on - with every
rule of the seat asked in Rust (`rust/phases/src/seat/`). Nothing is drawn.

Research:
    the seat's seam - NONE: the stage's plumbing; each rule's claim is at the Rust that decides it (`rust/phases/src/seat/`)
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram import work_counts
from l7r.diagram.settlement.land.wet import marsh_ground
from l7r.diagram.sitegen.geom import crop_polys

from .cluster import SeatRefused, exit_walls
from .consts import BROOK_CROSSING_COST_FT, FORD_BEND_DEG, FORD_HALF, FORD_SPACING, WIND_BACK_MIN_DOT, Poly, Pt
from .phases_ext import phases
from .plan import band_extent
from .ways.route import set_crossing

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from .plan import SitePlan


def _segs(recs: Any, key: str) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Each record's polyline under `key`, as segments."""
    return [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for rec in recs for a, b in zip(rec[key], rec[key][1:], strict=False)]


def _seated(plan: SitePlan, plots: Sequence[Poly], toe: Poly | None, wet: Sequence[Poly], brook: Sequence[Pt], lines: Sequence[tuple[Pt, Pt]], streams: Sequence[Sequence[Pt]]) -> dict[str, Any]:
    """The Rust seat asked of what is gathered: its frames, the fords and the streams gapped at them; refused by name."""
    walls, exit_lines = exit_walls(plan, toe, wet)
    try:
        out: dict[str, Any] = phases().stage_seat(
            (float(plan.W), float(plan.H)),
            plan.fall,
            plan.wind,
            WIND_BACK_MIN_DOT,
            list(plan.envelope),
            band_extent(plan.spec.households, plan.cluster_shape),
            [list(p) for p in plots],
            list(toe or []),
            [list(w) for w in wet],
            [(float(x), float(y)) for x, y in brook],
            walls,
            [*exit_lines, *lines],
            [list(c) for c in streams],
            (FORD_SPACING, FORD_HALF, FORD_BEND_DEG),
        )
    except ValueError as e:
        raise SeatRefused(f"{plan.spec.name} (seed {plan.spec.seed}): {str(e).replace('the wind', f'the {plan.windward} wind')} - the site has no seat (plan D3)") from e
    return out


def _frames(out: dict[str, Any]) -> dict[str, Any]:
    """The seat as the plan holds it: the chosen frame, its ladder after it."""
    frames = [{**f, "along": tuple(f["along"]), "out": tuple(f["out"]), "anchor": tuple(f["anchor"])} for f in out["frames"]]
    return {**frames[0], "ladder": frames[1:]}


def seat_cluster(plan: SitePlan, dry_plots: Sequence[Poly] = (), toe: Poly | None = None, wet: Sequence[Poly] = (), brook: Sequence[Pt] = ()) -> dict[str, Any]:
    """The seat frame and its ladder for `plan` on what stands - the dry plots, the wet toe, the reed fringe and the brook - as the
    seat stage decides it (the Rust seat), with no fords opened and `plan.watercourses` as they stand: the seat the house seating
    and its tests start from.

    Research:
        the seat - NONE: the Rust seat's own claims, asked here without the stage's fords"""
    return _frames(_seated(plan, dry_plots, toe, wet, brook, list(plan.watercourses), []))


def stage_seat(s: Settlement, plan: SitePlan) -> None:
    """Where the settlement will sit: the band on the field's margin with its back to the wind, ranked with the margins the house
    seating falls back down, decided in Rust and written here; the brook's fords opened first, so every way is routed over the brook
    there and nowhere else. NOTHING IS DRAWN, and no ground is reserved: the stage runs before the houses without constraining them.

    Steps:
        l7r.diagram.settlement.Settlement.toe_band
        l7r.diagram.hamletgen.ways.route.set_crossing

    Research:
        every way pays the crossing - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: `BROOK_CROSSING_COST_FT` set on the router for the whole roll
        the wind is kept - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a seat off the wind is recorded, never the wind renamed
        the side the houses stand on - NONE: the field tests from here on measure the outline's chords facing the seat (`field_face`)
        the way out off the wet ground laid - research/questions/0081-village-lanes.drawing.html: every way keeps off every marsh's reeds; at the seat the wet toe and a pond's reed fringe are the marsh laid, the hinterland's marshes laid after it (`STAGES`)
        the way out off the ditches - research/questions/0081-village-lanes.drawing.html: lanes keep to the bunds and dry ground; the seat's way out may not cross a field ditch, a channel or a drawn channel, a GUESS of the page's dry ground that leaves the ditches' planks to the ways
    """
    M = s.M
    toe = s.toe_band() or None
    wet = marsh_ground(M, only=("pond_fringe",))
    # the lines the way out keeps off, but for the brook: the Rust gaps the brook at its fords and adds it (`exit_walls` reads
    # `plan.watercourses`, written below, for the ladder's rungs the house seating asks later)
    ditches = _segs(list(M.get("field_ditches", [])) + list(M.get("channels", [])), "poly")
    drawn = _segs(M.get("drawn_channels", []), "pts")
    plan.watercourses = []
    # the course as first laid, not the rounded one (feature 287, M2): the fords, the crossing band and the ways read it
    streams = [[(float(q[0]), float(q[1])) for q in (st.get("stations") or st.get("poly") or [])] for st in M.get("streams", [])]
    out = _seated(plan, crop_polys(s), toe, wet, plan.brook or [], ditches + drawn, streams)
    for k, n in (out.get("counts") or {}).items():
        work_counts.OPS[k] += n
    s.brook_fords = [(float(x), float(y)) for x, y in out["fords"]]  # type: ignore[attr-defined]
    set_crossing(plan.brook or [], FORD_HALF, s.px(BROOK_CROSSING_COST_FT))
    M["meta"]["brook_fords"] = [[round(x, 1), round(y, 1)] for x, y in s.brook_fords]  # type: ignore[attr-defined]
    plan.watercourses = ditches + [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for a, b in out["stream_segs"]] + drawn
    plan.seat = _frames(out)
    M["meta"]["seat_offwind"] = bool(plan.seat["offwind"])
    M["meta"]["lane_skeleton"] = plan.lane_skeleton
    s.field_face = (float(plan.seat["cx"]), float(plan.seat["cy"]))
