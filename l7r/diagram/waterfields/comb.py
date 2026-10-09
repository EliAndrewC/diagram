"""build_comb - the water-first comb field builder (pond sluice, head-race, supply canals, delivery-ditch threads, carved paddies).

Research: comb plumbing - NONE: the carve/finish record, thread construction and stage hand-offs
"""

import math
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from .banks import cell_area, dedup_ring, floor_overhang, round_channel_joints
from .frame import (
    CANAL_A_FT,
    CANAL_B_FT,
    DELIVERY_FT,
    DELIVERY_PARENT_FRAC,
    DF,
    DRAIN_FT,
    GAP,
    HEAD_RACE_FT,
    SUB_PARENT_FRAC,
    Poly,
    Pt,
    _drain_bank,
    _dug_polyline,
    _f_at_u,
    _Frame,
    _point_along,
    _poly_area,
    _seg_x,
    _Thread,
    chan_px,
)
from .hem import _comb_dry_and_beans  # the dry hem and the wild middle's reserve, split out at the 1,000-line bar (feature 287, W36)
from .palette import RICE_GREENS
from .partition import Sectors, cut, planted_region, region_rings
from .ring_rules import fan_context, simple_outline
from .settle import ring_of, settle_cells
from .tint import judge_tint, mark_low
from .trunks import DRAIN_MIN_LEG, anchor_trunk_ends, drop_stub_pieces
from .twins import drop_twin_deliveries


@dataclass
class CombCarve:
    """A comb between its carve and its finish (feature 220) - the skeleton, the channels, the envelope and the PLANTED
    REGION (feature 302: the ground the finish will tile with plots), the random generator where the carve left it, and every
    input the finish needs. `fit_field` scores these (`net`, `region.area`) and finishes only the winner."""

    R: random.Random
    F: _Frame
    fork: Any
    a_pts: Poly
    bc: Any
    threads: Any
    dpts: Poly
    brook: Any
    drain_bank: Any
    channels: list[dict[str, Any]]
    region: Any
    envelope: Poly
    W: float
    H: float
    down_deg: float
    plot_across: float
    row_step: tuple[float, float]
    dry_keepout: Sequence[tuple[float, float, float]]
    dry_band: tuple[float, float]
    bean_frac: float
    furrow_spread: float
    grain_drift: float
    grain: float
    fan_middle: str = "cleared"  # 269 B07: see `fan_toe_hem`
    supply_banks: bool = False  # the stroke rule (W16) holds the plots' bunds off the supply strokes, not only the drain
    seed: int = 0  # the row wander's own stream (`seed ^ 0x12005`), separate so the skeleton is unmoved

    @property
    def net(self) -> dict[str, Any]:
        """What the fit's scorers read of a carve before any plot is cut: the channels, and the planted region's outline standing
        for the plots' extent - the only thing the legality tests read of them (`tail_dangles`' bounding box,
        `flanks_commanded`'s offsets across the fall; feature 302, plan D2)."""
        return {"plots": [{"poly": r} for r in region_rings(self.region)], "channels": self.channels}


def carve_comb(
    W: float,
    H: float,
    sluice: Pt,
    seed: int,
    down_deg: float = 45,
    canal_a_len: tuple[float, float] = (1250, 1450),
    canal_b_len: tuple[float, float] = (680, 800),
    offtakes_a: Sequence[float] = (0.22, 0.45, 0.68, 0.88),
    offtakes_b: Sequence[float] = (0.45, 0.8),
    plot_across: float = 48,
    row_step: tuple[float, float] = (26, 36),
    dry_keepout: Sequence[tuple[float, float, float]] = (),
    dry_band: tuple[float, float] = (70, 132),
    bean_frac: float = 0.28,
    field_fall: float | None = None,
    furrow_spread: float = 1.1,
    grain_drift: float = 0.0,
    grain: float = 1.0,
    supply_banks: bool = False,
    head_deg: float | None = None,
    head_len: float = 90.0,
    fan_middle: str = "cleared",
) -> CombCarve:
    """The CARVE half of `build_comb` (feature 220): everything up to the planted plots and the
    envelope, before the seams are closed - what `fit_field`'s search measures. Returns a
    `CombCarve`; `finish_comb` turns it into the net `build_comb` returns. ONE body: `build_comb`
    is `finish_comb(carve_comb(...))`, so every other caller is unchanged.

    Research:
        water first - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: the head race, canals, ditch threads and drain laid before any plot, the paddies cut between them
        bends swept before clearing - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: every continuation rounded before any ground is cleared against it
        default skeleton - UNRESEARCHED: canal A 1250-1450 px, canal B 680-800 px, offtakes at 0.22/0.45/0.68/0.88 and 0.45/0.8 of their canals
        default paddy grain - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: strips 48 px across, rows 26-36 px apart
        default hem depth - UNRESEARCHED: the dry hem 70-132 px deep
        default bund-bean share - UNRESEARCHED: 0.28 of the bunds carry a bean row
        fan middle - UNRESEARCHED: the fan's middle takes the "cleared" form by default (`fan_middle`)
    """
    R = random.Random(seed)
    F = _Frame(down_deg)
    DOWN = F.down
    channels: list[dict[str, Any]] = []

    fork, a_pts = _comb_skeleton(R, F, DOWN, sluice, canal_a_len, canal_b_len, W, H, grain, channels, head_deg, head_len)
    threads, bc, spawns = _comb_threads(R, F, DOWN, fork, a_pts, canal_b_len, offtakes_a, offtakes_b, plot_across)
    # ---- the lockstep march (no thread may cross another or pinch under GAP)
    _comb_march(R, F, DOWN, threads, spawns, W, H, field_fall)
    dpts = _comb_drain(R, F, threads, W, H, grain, channels)
    brook = _comb_brook(R, F, dpts, W, H)

    drain_bank = _drain_bank(F, dpts, grain)  # the ditch's own edge, the one line the field may not cross
    _comb_clip_and_cap(R, F, threads, dpts, drain_bank)
    _n0 = len(channels)
    _comb_canal_pieces(F, threads, bc, a_pts, offtakes_a, fork, grain, channels)
    # A PIECE TOO SHORT TO BE A CHANNEL IS DROPPED (feature 287, water W56): the remainder a canal cut leaves near a piece's
    # own end was kept only for the ground it held against a garden, which the bundle fit now keeps off every ditch itself.
    _kept = {id(c) for c in drop_stub_pieces([c for c in channels[_n0:] if c["role"] == "main"])}
    channels[_n0:] = [c for c in channels[_n0:] if c["role"] != "main" or id(c) in _kept]
    # SWEEP THE BENDS BEFORE ANYTHING CLEARS GROUND AGAINST THEM (2026-08-17). This used to run
    # after `_carve`, which meant the carve hemmed its bunds onto UN-SWEPT channel centerlines and
    # the sweep then moved the drawn water sideways underneath them - so a bund the carve had
    # cleared ended up inside a branch's swept bend. That is the identical defect the note below
    # records against `close_seams`, one call earlier and unnoticed: cohort seed 24 carried a bund
    # vertex 0.6 px from a branch ditch, buried in the stroke the map actually paints.
    # `_comb_canal_pieces` is the last thing that appends to `channels`, and neither
    # `_comb_floor_and_winding` nor `_comb_toe_and_hem` reads them, so this is the earliest point
    # the list is complete - and the latest one that is still before any consumer.
    # PLACEMENT AND ITS CHECK MUST READ THE SAME SOURCE, AND THE SOURCE IS WHAT GETS PAINTED.
    round_channel_joints(channels)  # earthen water turns on a swept bend, not a mitred corner

    # THE PLANTED REGION, NOT THE PLOTS (feature 302): the envelope less its water and the ground it cannot command - the ground
    # the finish tiles with plots (`partition.py`), and whose area IS the acreage the fit scores. No plot is cut here.
    envelope = _comb_envelope(threads, a_pts, dpts, F)
    anchor_trunk_ends(channels, envelope, W, H)  # no main or collector end left in bare ground (feature 287, water W15)
    region = planted_region(F, envelope, channels, a_pts, dpts, grain, drain_bank)
    return CombCarve(
        R=R,
        F=F,
        fork=fork,
        a_pts=a_pts,
        bc=bc,
        threads=threads,
        dpts=dpts,
        brook=brook,
        drain_bank=drain_bank,
        channels=channels,
        region=region,
        envelope=envelope,
        W=W,
        H=H,
        down_deg=down_deg,
        plot_across=plot_across,
        row_step=row_step,
        dry_keepout=dry_keepout,
        dry_band=dry_band,
        bean_frac=bean_frac,
        furrow_spread=furrow_spread,
        grain_drift=grain_drift,
        grain=grain,
        fan_middle=fan_middle,
        supply_banks=supply_banks,
        seed=seed,
    )


def finish_comb(c: CombCarve) -> dict[str, Any]:
    """The FINISH half of `build_comb` (feature 220): tile the planted region with plots, hold them to the ring rules, mark the
    low ground and its tint, measure the acreage, lay the dry plots and the bund beans, and assemble the net. Consumes the
    carve's own random generator from where the carve left it - each build seeds its own `R`, so a carve kept during a search
    and finished later sees the state an inline finish would have seen.

    Research:
        plots by partition - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: the planted region tiled with shared bunds and held to the ring rules
        one rice green - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: every plot drawn from RICE_GREENS
        furrows vary - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: neighboring dry plots owe a seam only where the spread is 0.3 rad or more
        paddy acreage scale - NONE: measured at a fixed 2 ft/px (4 sq ft per px^2) whatever the grain, 4x high at 1 ft/px unless the caller rescales
    """
    R, F, channels, envelope, a_pts, dpts, grain = c.R, c.F, c.channels, c.envelope, c.a_pts, c.dpts, c.grain
    W, H, down_deg, plot_across, row_step, fork, bc, threads, brook = c.W, c.H, c.down_deg, c.plot_across, c.row_step, c.fork, c.bc, c.threads, c.brook
    dry_keepout, dry_band, bean_frac, furrow_spread, grain_drift = c.dry_keepout, c.dry_band, c.bean_frac, c.furrow_spread, c.grain_drift
    # THE PLOTS BY CONSTRUCTION (feature 302). The region is cut by every bund at once (`partition.cut`), so the plots tile it
    # with every bund SHARED as laid - what `close_seams` used to reach by finding each scrap the carve left and planting or
    # absorbing it: a real cascade fan wasted nothing, its fork wedges terraced into small IRREGULAR paddies and the odd
    # unplantable scrap taken into the basin beside it (`settle`: split, merged, or left bare - research/contents.json#fields, the fabric).
    sectors = Sectors(F, threads, c.region, R, random.Random(c.seed ^ 0x12005), plot_across, row_step, grain)
    cell = cell_area(plot_across, row_step)
    ctx = fan_context(channels if c.supply_banks else [ch for ch in channels if ch.get("role") == "drain"], grain, cell)
    cells, _scraps = settle_cells(cut(sectors), ctx, plot_across, cell)
    plots: list[dict[str, Any]] = [{"poly": ring_of(q), "fill": R.choice(RICE_GREENS)} for q in cells]
    mark_low(plots, dpts, plot_across, row_step, R)
    judge_tint(plots, dpts, plot_across, grain)
    acres = sum(_poly_area(p["poly"]) for p in plots) * 4 / 43560  # 1px=2ft -> 4 sq ft/px^2

    dry_plots, dry_acres, bund_bean_runs, dry_reserve = _comb_dry_and_beans(
        R, F, a_pts, bc, plots, channels, W, H, dry_keepout, dry_band, bean_frac, grain, furrow_spread, grain_drift, fan_middle=c.fan_middle, fork=fork
    )
    # furrows_vary tells the checker whether to REQUIRE neighboring dry plots to differ in row direction: a
    # gentle-valley village spreads them (the patchwork quilt, default); a STEEP/terraced village narrows the
    # spread so the rows converge back onto the contour (ridge-along-contour erosion control) and no variation
    # is required. Threshold at ~0.3 rad (~17 deg): above it the plots visibly fan, below it they read aligned.
    return {
        "down_deg": down_deg,  # the LOCAL fall this fan was carved to - recorded so the drainage-slope
        # checks can judge each drain against ITS OWN field rather than one map-level constant (a city
        # ringed by farmland genuinely drains several ways at once; GM 2026-07-25)
        "fork": fork,  # the bunsuiguchi division point - recorded so comb_supply_commands_both_flanks
        # can measure each flank's planted extent and drawn-supply reach FROM the point the model
        # itself divides at (placement and check reading the same source; GM 2026-08-16)
        # THE DESIGN CELL this fan was carved to, recorded so `paddy_basins_are_worth_their_bund`
        # judges each basin against the reference the PLACER used rather than one it re-derives.
        # It cannot be re-derived from `meta.ftpx`: `plot_texture` scales the target per map
        # (small_irregular 0.72x, medium 1.0x, large_block 1.35x, strip long-and-narrow), so a gate
        # computing `paddy_grain(ftpx)` for itself would hold a textured fan to a cell it never
        # aimed at.
        "cell": cell_area(plot_across, row_step),
        "supply_banks": c.supply_banks,  # the rings hem onto the supply strokes, so a later carve holds them to the stroke rule
        "channels": channels,
        "plots": plots,
        "threads": threads,
        "drain": dpts,
        "brook": brook,
        "envelope": envelope,
        "acres": acres,
        "dry_plots": dry_plots,
        "dry_acres": dry_acres,
        "dry_reserve": dry_reserve,  # a wild middle's hem, nearest the toe first, for the draw's coarse-grain top-up (W36)
        # THE RUNS ARE THE ENGINE'S OWN STRUCTURE, NEVER RECORDED (feature 247): the draw site drops beads
        # under pond and recorded-ditch water per run and re-flattens; the manifest carries the flat list
        # and the plot rings, from which the gate derives the runs (spec D3).
        "bund_bean_runs": bund_bean_runs,
        "bund_beans": [q for run in bund_bean_runs for q in run],
        "furrows_vary": furrow_spread >= 0.3,
        "fan_middle": c.fan_middle,
    }


def build_comb(
    W: float,
    H: float,
    sluice: Pt,
    seed: int,
    down_deg: float = 45,
    canal_a_len: tuple[float, float] = (1250, 1450),
    canal_b_len: tuple[float, float] = (680, 800),
    offtakes_a: Sequence[float] = (0.22, 0.45, 0.68, 0.88),
    offtakes_b: Sequence[float] = (0.45, 0.8),
    plot_across: float = 48,
    row_step: tuple[float, float] = (26, 36),
    dry_keepout: Sequence[tuple[float, float, float]] = (),
    dry_band: tuple[float, float] = (70, 132),
    bean_frac: float = 0.28,
    field_fall: float | None = None,
    furrow_spread: float = 1.1,
    grain_drift: float = 0.0,
    grain: float = 1.0,
    supply_banks: bool = False,
) -> dict[str, Any]:
    """The COMB layout (the historical default - Kishu school / Chinese canal doctrine):
    the sluice's head-race forks at one division point into TWO supply canals hugging the
    high margins (canal A runs cross-slope at down-37 deg, canal B down the other margin at
    down+58 deg), delivery ditches drop downhill off them (a couple splitting once), and one
    drain collector (akusui) crosses the LOW side and leaves the map. Paddies are carved
    between the ditch threads; water cascades plot-to-plot within each block (tagoshi).

    Returns {"channels": [{pts, w, role}], "plots": [{poly, fill}], "threads", "drain",
    "envelope", "acres"} - the caller draws it (px are map px; acres assume 1px = 2ft).

    `grain` scales the PLOT-GEOMETRY thresholds in the carve (minimum sector/row/plot sizes,
    canal berms, drain set-backs, the gap-closer margins) AND the channel widths. They are
    REAL-FEET quantities that were tuned at the village grain of 1px = 2ft; the principled
    value is therefore grain = 2 / ftpx, so a "too narrow to plant" test means the same
    real-world size on every map.

    WHAT THE HAND-AUTHORED HAMLETS PASS is 1.0, not 2.0. That was recorded as a silent
    inconsistency for a long time - at 1 ft/px it makes their "too narrow to plant" thresholds
    mean half the real size they mean on a village sheet, and their irrigation ditches half the
    width - and it has now been settled by testing rather than by preference (2026-08-12).

    THE PRINCIPLED VALUE WORKS AT THIS TIER. Two obstacles used to stop it, and both are fixed.
    The first was the bridge arithmetic: wider ditches produced planks and carried-way decks whose
    abutments stood in the channel, because both paths sized a deck from a nominal width rather
    than from the water actually beneath it. `channel_footbridges` now sizes a plank to the widest
    course under it, junctions included, and `bridges()` grows a carried-way deck until its corners
    clear the crossed polyline. The second was the communal WINDBREAK: at the coarser grain the
    crop geometry shifts enough that a belt derived from the house cloud's EXTREMES could land off
    the cluster altogether on a tall narrow settlement (measured: 9 surviving clumps, 350 px from
    the nearest farmhouse). A belt sampled as a PROFILE across the wind instead of a box around the
    extremes does not have that failure mode.

    With both fixed, the scripted hamlet tier passes the principled 2.0 and a 36-map cohort gates
    clean on it (`hamletgen.py`, `GRAIN`, which carries the same reasoning).

    THE POOL'S HAND-AUTHORED HAMLETS ARE STILL AT 1.0, and moving them is a separate job rather
    than a leftover: it re-rolls every comb map in the pool and each one needs a `settlement-review`
    pass, since the change is visible (ditches at their true width, coarser minimum plots). So the
    disagreement is no longer silent - the principled value is demonstrated, the cost of adopting
    it pool-wide is named, and a hamlet gen passing 1.0 is doing so knowingly.

    Left unscaled, a city's carve dropped
    sectors, head plots, and closers that a village would have planted, leaving parchment
    holes inside the fan - the white-spots bug the villages fixed once (canal-side closers,
    the closing rank) and the cities then re-exposed at their coarser grain (2026-07-21).
    The canal/thread/drain SKELETON is deliberately NOT scaled here: its lengths arrive
    pre-scaled from the caller, and the map-edge margins (8px) are canvas facts, not feet.

    Research:
        comb layout - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: a head race forking into two supply canals on the high margins, deliveries down the slope, one collector on the low line
        water passes plot to plot - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html: below each delivery's end the plots take their water over the bunds
        default skeleton - UNRESEARCHED: canal A 1250-1450 px, canal B 680-800 px, offtakes at 0.22/0.45/0.68/0.88 and 0.45/0.8 of their canals
        default paddy grain - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: strips 48 px across, rows 26-36 px apart
        default hem depth - UNRESEARCHED: the dry hem 70-132 px deep
        default bund-bean share - UNRESEARCHED: 0.28 of the bunds carry a bean row
    """
    return finish_comb(
        carve_comb(
            W=W,
            H=H,
            sluice=sluice,
            seed=seed,
            down_deg=down_deg,
            canal_a_len=canal_a_len,
            canal_b_len=canal_b_len,
            offtakes_a=offtakes_a,
            offtakes_b=offtakes_b,
            plot_across=plot_across,
            row_step=row_step,
            dry_keepout=dry_keepout,
            dry_band=dry_band,
            bean_frac=bean_frac,
            field_fall=field_fall,
            furrow_spread=furrow_spread,
            grain_drift=grain_drift,
            grain=grain,
            supply_banks=supply_banks,
        )
    )


def _canal_ft(tier: tuple[float, float], i: int, n: int) -> float:
    """A supply canal's TRUE width in feet at cut `i` of `n` - Tabayashi's taper, in real units.

    The canal sheds flow into each offtake it passes, so it steps down at every cut and dies as a
    thread past the last one. Shared by the drawing pass and by `_comb_threads`, which needs the
    parent's width AT a takeoff to size the delivery leaving there (`DELIVERY_PARENT_FRAC`); the
    two used to be one formula written out and one written nowhere, which is how a delivery came to
    be drawn wider than the canal feeding it.

    A FIX THAT FAILED (feature 328 wave 69, 2026-10-09): 0069 narrows a canal by the square-root law, not in equal linear
    steps, and `taper_w(tier[0], tier[1], i / n)` here does exactly that - but the wider mid-run canal moved the field's
    geometry, and the 48-seed cohort went 48 -> 45 (seeds 04, 12, 40, 902 and 905 newly refused: a farm off its street twice,
    a needle loop, a farmstead across the brook, a farm without its channel; 22 and 33 newly passing). Reverted; the row is
    E3 (a change that ripples into placement), its work the layouts that broke (m:wave69-canal-taper-reverted).

    Research: canal narrows at each offtake - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html, research/questions/0069-how-our-maps-draw-a-channel-narrowing-along-its-run.drawing.html: head to tail tier in equal linear steps, one per cut
    """
    return tier[0] - (tier[0] - tier[1]) * i / n


def _mk_thread(
    F: _Frame,
    DOWN: float,
    px: float,
    py: float,
    heading: float,
    ditch_len: float,
    decay: float = 110.0,
    fallback: Poly | _Thread | None = None,
) -> _Thread:
    tu, tf = F.to_uf(px, py)
    h = max(-1.2, min(1.2, heading - DOWN))
    # du/df = -tan(h): a heading LEFT of the fall line (h<0) moves u POSITIVE
    return _Thread(tu, tf, -math.tan(h), tf + ditch_len * max(0.2, math.cos(h)), decay, fallback)


def _comb_skeleton(
    R: random.Random,
    F: _Frame,
    DOWN: float,
    sluice: Pt,
    canal_a_len: tuple[float, float],
    canal_b_len: tuple[float, float],
    W: float,
    H: float,
    grain: float,
    channels: list[dict[str, Any]],
    head_deg: float | None = None,
    head_len: float = 90.0,
) -> tuple[Pt, Poly]:
    """The water skeleton's head: head-race to the division point, then canal A's dug polyline
    (canal B's is drawn and discarded - its RNG draw is part of the frozen stream).

    `head_deg` is the bearing the head race LEAVES THE INTAKE on and `head_len` how far it runs to the
    division point. Both are the caller's since feature 230: a scripted hamlet's brook keeps its own
    course past the fan, and the race leaves its bank at an acute angle pointing downstream (the
    record's offtake rule) over a distance derived from the fan rather than pinned. The default -
    no bearing, 90 px - is the shape every other caller has drawn since this builder was written:
    straight down the fall from a sluice, which is right for a pond's outlet and for a city fan
    tapping a moat, neither of which has a brook to leave.

    Research:
        head race - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: from the intake on the caller's bearing, or straight down the fall, `head_len` px to the fork
        head race width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: HEAD_RACE_FT
        supply along the high margin - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: canal A dug cross-slope from the fork
        canal A heading - UNRESEARCHED: 42 deg off the fall, a dug polyline of 95-125 px segments
    """
    # head-race: the intake -> the division point (bunsuiguchi), on the caller's bearing or down the fall.
    # Every width below goes through `chan_px`, which converts a TRUE width in feet to pixels at
    # this map's scale (and floors it at the visibility minimum) - so the net is to scale, and the
    # same real channel is the same real size on every sheet that draws it.
    hd = F.d if head_deg is None else (math.cos(math.radians(head_deg)), math.sin(math.radians(head_deg)))
    hr = [sluice, (sluice[0] + head_len / 2 * hd[0], sluice[1] + head_len / 2 * hd[1]), (sluice[0] + head_len * hd[0], sluice[1] + head_len * hd[1])]
    channels.append({"pts": hr, "w": chan_px(HEAD_RACE_FT, grain), "role": "main"})
    fork = hr[-1]

    # supply canal A: cross-slope along the high margin, descending gently
    a_pts = _dug_polyline(R, F, fork[0], fork[1], DOWN - math.radians(42), R.uniform(*canal_a_len), 0.045, (95, 125), W, H)
    # supply canal B: down the other margin (steeper heading, the west canal on Kikuta). Its polyline is
    # discarded - canal B is redrawn below as the `bc` boundary thread - but the call stays (its RNG draw is
    # part of the frozen stream that keeps every map byte-identical); `_`-prefixed so it reads as intentional.
    _b_pts = _dug_polyline(R, F, fork[0], fork[1], DOWN + math.radians(58), R.uniform(*canal_b_len), 0.05, (90, 120), W, H)
    return fork, a_pts


def _comb_threads(
    R: random.Random,
    F: _Frame,
    DOWN: float,
    fork: Pt,
    a_pts: Poly,
    canal_b_len: tuple[float, float],
    offtakes_a: Sequence[float],
    offtakes_b: Sequence[float],
    plot_across: float,
) -> tuple[list[_Thread], _Thread, list[list[Any]]]:
    """Boundary + delivery threads off the two canals, and the spawn events for mid-march offtakes.

    Research:
        second supply canal - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: canal B down the other flank, feeding at least one delivery
        canal B heading - UNRESEARCHED: 58 deg off the fall
        offtake spacing - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: an offtake within two plot widths of another, or of canal B, is skipped
        delivery takeoff - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html, research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: each delivery heads down the fall, -0.15 to +0.1 rad, off a canal running 42 deg off it
        delivery length - UNRESEARCHED: 420-620 px off canal A, 340-560 off canal B
        sub-ditches - UNRESEARCHED: each interior delivery splits once, high on its run, diverging 0.5-0.66 rad
        sub-ditch length - UNRESEARCHED: 300-430 px
        canal B delivery takeoff - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html, research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: each heads -0.2 to 0 rad off the fall, 58-70 deg off its canal
        canal B tail - UNRESEARCHED: its thread ends 22 px past its last offtake
        delivery widths - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: capped at DELIVERY_PARENT_FRAC of the canal there, a sub at SUB_PARENT_FRAC of its delivery's head
    """
    # canal B is itself the far-side boundary thread (its dug prefix IS the canal)
    bc = _mk_thread(F, DOWN, fork[0], fork[1], DOWN + math.radians(58), R.uniform(*canal_b_len), decay=170.0)
    bc.head_ft = CANAL_B_FT[0]  # bc is a SUPPLY canal, not a delivery - it carries its own tier
    threads = [bc]
    # delivery ditches are MIN-SPACED: two ditches closer than ~2 plot-columns would water the same
    # ground twice (a redundant near-pair that reads as an artifact, not design), so drop the closer.
    min_gap = 2.0 * plot_across
    placed_u = [bc.u0]  # canal B is a SUPPLY canal - deliveries must not hug it either
    a_ths = []
    # canal A is cut at every offtake, so offtake j leaves where the canal has already stepped down
    # to cut j+1 of its len(offtakes_a)+1 pieces - the same profile `_comb_canal_pieces` draws.
    n_a_cuts = len(offtakes_a) + 1
    for j, frac in enumerate(offtakes_a):  # delivery ditches off canal A
        bx, by = _point_along(a_pts, frac)
        tu = F.to_uf(bx, by)[0]
        if any(abs(tu - pu) < min_gap for pu in placed_u):
            continue  # redundant near-pair - skip it (keeps the net sparse)
        placed_u.append(tu)
        th = _mk_thread(F, DOWN, bx, by, DOWN + R.uniform(-0.15, 0.1), R.uniform(420, 620), fallback=a_pts)
        th.head_ft = min(DELIVERY_FT[0], _canal_ft(CANAL_A_FT, j + 1, n_a_cuts) * DELIVERY_PARENT_FRAC)
        a_ths.append(th)
        threads.append(th)
    for th in a_ths[1:-1]:  # only the INTERIOR (widest) blocks split once
        th.spawn_sub = True
    rb = _mk_thread(F, DOWN, a_pts[-1][0], a_pts[-1][1], DOWN, 0, fallback=a_pts)  # far boundary (bund only)
    threads.append(rb)
    threads.sort(key=lambda t: t.u0)

    # spawn events: west-canal offtakes + mid-block subs take off ON their parent's path
    spawns: list[list[Any]] = []  # [f_at, parent_thread, heading, ditch_len, side, head_ft] - heterogeneous
    bc.offtake_fs = []
    n_b_cuts = len(offtakes_b) + 1
    for j, frac in enumerate(offtakes_b):
        f_at = bc.f0 + (sum(canal_b_len) / 2 * frac) * math.cos(math.radians(58))
        bc.offtake_fs.append(f_at)
        head_ft = min(DELIVERY_FT[0], _canal_ft(CANAL_B_FT, j + 1, n_b_cuts) * DELIVERY_PARENT_FRAC)
        spawns.append([f_at, bc, DOWN + R.uniform(-0.2, 0.0), R.uniform(340, 560), +1, head_ft])
    # a sub takes off HIGH on its parent and DIVERGES steeply (bigger heading, longer run) so the two
    # channels end up > ~2 columns apart - a real Y-junction serving a distinct sub-block, NOT two
    # ditches running adjacent for a stretch (which read as a redundant artifact, per the GM).
    for th in [t for t in threads if getattr(t, "spawn_sub", False)]:
        f_at = th.f0 + (th.ditch_f - th.f0) * R.uniform(0.24, 0.38)
        side = R.choice((-1, 1))
        # A sub-ditch is sized against its parent's HEAD, deliberately - not its local width there.
        # `settlement-review` (2026-08-17) flagged the divergence between this and the docs, which
        # said LOCAL, and the docs have been corrected to match rather than the other way round,
        # because the local version was TRIED and is worse: at true scale a delivery's local width a
        # third of the way down is ~2.2 ft, so 0.75 of it is 1.64 - against a 1.5 px floor, a
        # sub-ditch with 0.14 px of room to taper in. `delivery_ditches_taper` (w_tail < 0.85*w)
        # correctly rejected that on 22 of 24 cohort maps: a ditch that cannot taper should not be
        # drawn claiming to. Sizing off the head keeps the sub a real tier below its parent while
        # leaving it somewhere to dwindle to.
        spawns.append([f_at, th, DOWN + side * R.uniform(0.5, 0.66), R.uniform(300, 430), side, th.head_ft * SUB_PARENT_FRAC])
    bc.ditch_f = max([e[0] for e in spawns if e[1] is bc], default=bc.f0 + 40) + 22
    return threads, bc, spawns


def _comb_march(R: random.Random, F: _Frame, DOWN: float, threads: list[_Thread], spawns: list[list[Any]], W: float, H: float, field_fall: float | None) -> None:
    """The lockstep march (no thread may cross another or pinch under GAP), spawning children mid-march.

    Research:
        no channel crosses another - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: threads marched in lockstep, never crossing
        field depth - research/questions/0010-farmland-around-towns-and-cities.drawing.html: capped at `field_fall`, else grown downhill off the frame
        outfall margin - UNRESEARCHED: a capped field held inside the frame with a low-side margin for the outfall and brook
    """
    for t in threads:
        t.pts = [F.to_xy(t.u0, t.f0)]
    f = min(t.f0 for t in threads)
    # By default the field grows downhill until the threads leave the map (fills the frame to the low
    # corner, then spills off it). `field_fall` CAPS the downhill depth instead, so the field is sized
    # to the population and BOUNDED within the frame - leaving a low-side margin for the drain's outfall
    # + brook to discharge into open land (see research/questions/0010-farmland-around-towns-and-cities.html). None = the old fill-to-edge.
    f_stop = max(F.to_uf(0, 0)[1], F.to_uf(W, 0)[1], F.to_uf(0, H)[1], F.to_uf(W, H)[1]) + 300
    if field_fall is not None:
        f_stop = min(f_stop, f + field_fall)
    while f < f_stop:
        f += DF
        for ev in [e for e in spawns if e[0] <= f]:
            spawns.remove(ev)
            _, par, head, dlen, side, head_ft = ev
            px, py = par.pts[-1]
            child = _mk_thread(F, DOWN, px, py, head, dlen, fallback=par)
            child.head_ft = head_ft  # sized against its parent's local width, never wider than it
            child.u0 = child.u = par.u + GAP * 0.55 * side
            child.pts = [(px, py)]
            threads.insert(threads.index(par) + (1 if side > 0 else 0), child)
        prev_u = None
        for t in threads:
            if f <= t.f0:
                continue
            nu = t.step(f, R)
            if prev_u is not None and nu < prev_u + GAP:
                nu = prev_u + GAP
            t.u = nu
            t.pts.append(F.to_xy(nu, f))
            prev_u = nu
        if all(not (-60 < F.to_xy(t.u, f)[0] < W + 60 and -60 < F.to_xy(t.u, f)[1] < H + 60) for t in threads):
            break


def _comb_drain(R: random.Random, F: _Frame, threads: list[_Thread], W: float, H: float, grain: float, channels: list[dict[str, Any]]) -> Poly:
    """DRAIN (akusui): the collector is DUG along the fields' low boundary, so its route
    is the ENVELOPE of the delivery ditches' dug ends (each column drains just below where
    its ditch stops) - a u-sorted polyline through (u_bot, f_bot + margin), smoothed, and
    extended past both ends so the whole system empties off the map.

    Research:
        collector on the low line - research/questions/0060-field-drains-akusuiro.drawing.html: dug below the deepest delivery ends, starting at the first delivery's bottom
        across the slope - research/questions/0060-field-drains-akusuiro.drawing.html: a fitted line falling 0.06-0.35 per unit along the contour toward its outfall
        set below the ditch ends - UNRESEARCHED: 32-48 px below the deepest end, the outfall 40 px past the last
        wandering line - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html: sampled every 120-170 ft with up to 6 ft of jitter, at the map's scale
        drain widens - research/questions/0060-field-drains-akusuiro.drawing.html, research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: DRAIN_FT, a thread at its head, full at the outfall
        straight last leg - UNRESEARCHED: no jittered sample within `DRAIN_MIN_LEG` (84 px) of the outfall
        collector above the frame - UNRESEARCHED: the fitted collector lifted to stand 40 px (unscaled) above the frame's bottom edge
    """
    bots = []
    for t in threads:
        if t.ditch_f <= t.f0 + 10:
            continue  # bund-only boundaries have no ditch
        bot = t.pts[0]
        for p in t.pts:
            if F.to_uf(*p)[1] <= t.ditch_f:
                bot = p
        bots.append(F.to_uf(*bot))
    # A collector is dug below the DEEPEST delivery ends; shallower columns simply cascade
    # further to reach it (the prototype look the GM approved). Fit a gently-descending line
    # f = a + b*u through the ditch bottoms (b clamped so the drain always falls toward its
    # exit on the high-u side - water never runs uphill), pushed down to clear every end.
    n = len(bots)
    mu = sum(b[0] for b in bots) / n
    mf = sum(b[1] for b in bots) / n
    var = sum((b[0] - mu) ** 2 for b in bots) or 1.0
    b_fit = sum((b[0] - mu) * (b[1] - mf) for b in bots) / var
    b_fit = max(0.06, min(0.35, b_fit))
    a_fit = max(b[1] + R.uniform(32, 48) - b_fit * b[0] for b in bots)
    # the head begins AT the westmost delivery ditch's bottom (inside the field), NOT extended out to
    # the boundary thread and beyond into bare ground - a collector starts where the first field drains
    # in, and the hem pass covers any sliver at the SW corner. (This was a dangling stub before.)
    lo_u = min(b[0] for b in bots)
    hi_u = max(b[0] for b in bots) + 40  # the OUTFALL, just past the SE-most ditch bottom
    # keep the collector INSIDE the frame: lower the line if an end would dip off the map edge (a
    # delivery ditch that then reaches it simply discharges into the collector - correct hydrology)
    for uc in (lo_u, hi_u):
        yc = F.to_xy(uc, a_fit + b_fit * uc)[1]
        if yc > H - 40:
            a_fit -= (yc - (H - 40)) / max(0.35, abs(F.d[1]))
    # THE HEAD ON THE FITTED LINE, NO SAMPLE WITHIN `DRAIN_MIN_LEG` OF THE OUTFALL (feature 287, W13/W14; why: `trunks.DRAIN_MIN_LEG`).
    # Every draw is still taken, the unused ones discarded, so the random stream is unmoved.
    duf = []
    u = lo_u
    while u < hi_u:
        jitter = R.uniform(-6, 6) * grain / 2.0  # 6 ft either way, in pixels at the map's scale (grain is 2 / ftpx)
        if u == lo_u:
            duf.append((u, a_fit + b_fit * u))
        elif u < hi_u - DRAIN_MIN_LEG:
            duf.append((u, a_fit + b_fit * u + jitter))
        u += R.uniform(120, 170) * grain / 2.0  # a sample every 120-170 ft
    duf.append((hi_u, a_fit + b_fit * hi_u))  # the outfall point (drain's downhill end)
    duf.sort(key=lambda q: q[0])
    dpts = [F.to_xy(u, f) for u, f in duf]
    # the collector WIDENS downstream - the mirror of the supply taper (GM 2026-07-23): a supply
    # canal sheds water as it goes and dwindles; the akusui GATHERS the plots' tail-water as it
    # crosses the low side, so it starts as a thread at its head and carries the fan's whole
    # runoff at the outfall (duf is u-sorted with the outfall appended at hi_u, so pts[-1] is
    # the downhill end the gens anchor to the brook/moat/offmap).
    # The head is a THREAD - the same 1.5*grain the delivery ditches taper down to (GM 2026-07-25).
    # At its high end a collector is draining the toe of ONE paddy, so there is no flow there to carry:
    # the width has to come from what the ditch must BE, not from what it moves, and a hand-dug earthen
    # ditch that gets cleaned out every year needs a bottom you can put a hoe into (~1 ft) plus standing
    # side slopes, i.e. ~1.5 ft across the top. Below that it is not a maintained ditch at all, it is the
    # seasonal furrow a farmer re-cuts at each drawdown. So the hydraulic floor and the maintenance floor
    # meet exactly at the finest ditch the supply side already draws, and the drain starts there.
    channels.append({"pts": dpts, "w": chan_px(DRAIN_FT[0], grain), "w_tail": chan_px(DRAIN_FT[1], grain), "role": "drain"})
    return dpts


def _comb_brook(R: random.Random, F: _Frame, dpts: Poly, W: float, H: float) -> Poly:
    """The akusui does NOT just stop: it empties at its outfall into a natural valley BROOK that
    carries the water off the map downhill (reused by the next village downstream / rejoining the
    river). Water IN (the pond feeder) and water OUT (this brook). BUT a brook is only added when
    the outfall sits INSIDE the frame - if the field itself already runs to the map edge, the drain
    discharges off-map directly (a brook grown from there would just run back through the field, as
    the streams_avoid_fields check correctly flags). A field bounded within the frame gets the brook.

    Research:
        a brook from the outfall - research/questions/0060-field-drains-akusuiro.drawing.html: a brook grown from an outfall inside the frame, none where the drain reaches the edge
        brook curves out of the collector - research/questions/0060-field-drains-akusuiro.drawing.html: from the drain's exit heading toward pure downhill over four steps
        brook course - UNRESEARCHED: 88 px steps, then 72-105 px down the fall with -22 to +40 across, until it leaves the map
    """
    outfall = dpts[-1]  # the drain's downhill (highest-u) end
    brook = []
    if 14 < outfall[0] < W - 14 and 14 < outfall[1] < H - 14:
        u0, f0 = F.to_uf(*outfall)
        um, fm = F.to_uf(*dpts[-2])  # the drain's EXIT heading (u/f) at the outfall
        eu, ef = u0 - um, f0 - fm
        el = math.hypot(eu, ef) or 1.0
        eu, ef = eu / el, ef / el  # unit exit heading (mostly cross-slope, slight fall)
        ou, of = u0, f0
        brook = [outfall]
        for i in range(40):
            # the brook does NOT turn a hard ~90 deg corner off the collector: it CURVES from the drain's
            # exit heading toward pure downhill over the first few steps, so the junction reads as the
            # collector turning down the valley INTO the stream (a smooth bend, not a right angle).
            w = min(1.0, i / 4.0)
            ou += (1 - w) * eu * 88 + w * R.uniform(-22, 40)
            of += (1 - w) * ef * 88 + w * R.uniform(72, 105)  # w->1 quickly: pure downhill off the map
            p = F.to_xy(ou, of)
            brook.append(p)
            if not (12 < p[0] < W - 12 and 12 < p[1] < H - 12):
                break  # ran off the map edge = the runoff sink
    return brook


def _comb_clip_and_cap(R: random.Random, F: _Frame, threads: list[_Thread], dpts: Poly, drain_bank: Callable[[float], float]) -> None:
    """Clip every thread to the drain's BANK, then cap each column's cascade tail.

    Research:
        threads end at the bank - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html: a thread clipped at the collector's bank, never its centerline
        cascade length - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html: a delivery extended to end 250-330 px, and at least 55, above the collector
    """
    for t in threads:  # clip every thread to the drain
        clipped = [t.pts[0]]
        for i in range(len(t.pts) - 1):
            a, b = t.pts[i], t.pts[i + 1]
            hit = None
            for j in range(len(dpts) - 1):
                hit = _seg_x(a, b, dpts[j], dpts[j + 1])
                if hit:
                    break
            if hit:
                # a thread ENDS AT THE COLLECTOR'S BANK, not on its centerline. `bnd` hands the
                # clipped endpoint back as a plot-boundary point for any fall at or below it, so a
                # clip on the centerline plants a paddy corner in the water - Ubame's west fan had
                # exactly one, 0.25px off the line, and it was the last thing standing between the
                # comb and a clean hem (2026-08-08). The dug PREFIX is unaffected: `ditch_f` stops
                # a couple of hundred px above this point, so the drawn blue never reaches the clip.
                hu = F.to_uf(*hit)[0]
                hf = _f_at_u(F, dpts, hu)
                clipped.append(hit if hf is None else F.to_xy(hu, hf - drain_bank(hu)))
                break
            clipped.append(b)
        t.pts = clipped

    # cascade-tail cap: a column should cascade no more than ~8-11 rows past its ditch's
    # end (the recorded norm is "a few to ~10 paddies" per string) - extend any dug ditch
    # whose tail to the collector would run longer. Only extends, never shortens; the
    # deepest ends (which set the drain fit) are already within reach of it.
    for t in threads:
        if t.ditch_f <= t.f0 + 10:
            continue
        fd_ = _f_at_u(F, dpts, F.to_uf(*t.pts[-1])[0])
        if fd_ is not None:
            t.ditch_f = min(max(t.ditch_f, fd_ - R.uniform(250, 330)), fd_ - 55)


def _comb_canal_pieces(F: _Frame, threads: list[_Thread], bc: _Thread, a_pts: Poly, offtakes_a: Sequence[float], fork: Pt, grain: float, channels: list[dict[str, Any]]) -> None:
    """Drawable canals: A tapers past each offtake ("main canals gradually decrease in
    size as they are tapped by branch canals" - Tabayashi 1986), and it tapers ALL THE WAY DOWN
    to a ditch-tail thread (1.6) at its far end (GM 2026-07-23): the supply canal sheds its whole
    flow into the offtakes and plots along its run, so past the last offtake it carries almost
    nothing and "slowly disappears" exactly like the delivery ditches - the old stepped 6.2 -> 4.0
    taper left the top channel reading near-constant beside the dwindling ditches. Each piece now
    carries w -> w_tail so the narrowing is continuous within pieces, not a stair of blunt steps.

    Research:
        supply canals narrow to a thread - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: canals A and B step down at each offtake and dwindle past the last
        no delivery at the fork - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: a delivery starting within 40 px of the fork is not drawn
        delivery narrows - research/questions/0069-how-our-maps-draw-a-channel-narrowing-along-its-run.drawing.html: from its capped head to DELIVERY_FT's tail
        no twin deliveries - research/questions/0067-do-two-ditches-run-side-by-side-across-the-fields-not-in-the-old-forms-the-map-draws.html: a delivery running beside another course is dropped
    """
    first = len(channels)
    cuts = [0.0] + list(offtakes_a) + [1.0]
    n_a = len(cuts) - 1
    for i in range(len(cuts) - 1):
        piece = [_point_along(a_pts, cuts[i] + (cuts[i + 1] - cuts[i]) * t / 6) for t in range(7)]
        channels.append({"pts": piece, "w": chan_px(_canal_ft(CANAL_A_FT, i, n_a), grain), "w_tail": chan_px(_canal_ft(CANAL_A_FT, i + 1, n_a), grain), "role": "main"})
    bc_cuts = sorted(F.to_uf(*e[1].pts[0])[1] if False else e[0] for e in []) if False else sorted([bc.f0] + [f for f in getattr(bc, "offtake_fs", [])] + [bc.ditch_f])
    for t in threads:
        pre = [p for p in t.pts if F.to_uf(*p)[1] <= t.ditch_f]
        if len(pre) < 2:
            continue
        if t is bc and len(bc_cuts) > 2:
            # canal B is a SUPPLY canal (role "main", like canal A) that narrows past each offtake it
            # feeds - and, like A, dwindles to a ditch-tail thread at its far end (GM 2026-07-23; see
            # the canal-A taper note above).
            m_b = len(bc_cuts) - 1

            def _bc_at(ft: float, pre: Poly = pre) -> Pt | None:  # noqa: B008 - bind the loop's `pre` at definition
                """The point ON `pre` where the fall coordinate crosses `ft`, by interpolation.
                A vertex filter alone drops a whole piece when its cut window is shorter than the
                polyline's ~90-120 px vertex spacing - which is exactly the thread-tail window
                (last offtake -> ditch_f, ~22 px), so Kashikawa's arm ended in a blunt 7.2 ft cap
                where the research promises a taper to a thread (settlement-review 2026-08-16).
                Interpolating the window's endpoints makes every piece drawable regardless of
                where the dug vertices happen to fall, and the pieces meet exactly at the cuts."""
                _fs = [F.to_uf(*p)[1] for p in pre]
                for j in range(len(pre) - 1):
                    fa, fb = _fs[j], _fs[j + 1]
                    if (fa <= ft <= fb) or (fb <= ft <= fa):
                        t = 0.0 if fb == fa else (ft - fa) / (fb - fa)
                        return (pre[j][0] + (pre[j + 1][0] - pre[j][0]) * t, pre[j][1] + (pre[j + 1][1] - pre[j][1]) * t)
                # past the polyline's span: CLAMP to the nearer end rather than dropping the piece.
                # Sawada's dug arm ends a few px short of ditch_f, and returning None there cost the
                # map its thread tail while the other three drew theirs (2026-08-16).
                return pre[-1] if abs(ft - _fs[-1]) < abs(ft - _fs[0]) else pre[0]

            for i in range(len(bc_cuts) - 1):
                piece = [p for p in pre if bc_cuts[i] < F.to_uf(*p)[1] < bc_cuts[i + 1]]
                _pa, _pb = _bc_at(bc_cuts[i]), _bc_at(bc_cuts[i + 1])
                if _pa is not None:
                    piece = [_pa, *piece]
                if _pb is not None:
                    piece = [*piece, _pb]
                if len(piece) >= 2 and math.dist(piece[0], piece[-1]) > 2.0:
                    channels.append({"pts": piece, "w": chan_px(_canal_ft(CANAL_B_FT, i, m_b), grain), "w_tail": chan_px(_canal_ft(CANAL_B_FT, i + 1, m_b), grain), "role": "main"})
        elif math.hypot(pre[0][0] - fork[0], pre[0][1] - fork[1]) < 40.0:
            # a delivery must take off WELL DOWNSTREAM of the head fork. A delivery sprouting AT the
            # division point (a short canal B whose single offtake lands ~0px from the fork - Tango's
            # nw1, Hoshizora's west field) turns the clean 3-way bunsuiguchi division into a 4-way STAR
            # that reads as a crossroads, not water feeding the next channel (GM 2026-07-22). Skip drawing
            # it - the plots it shapes keep their bunds, only the blue ditch clutter at the fork goes. The
            # gap between the two offenders (0-1px) and the nearest legitimate delivery (76px) makes 40 a
            # safe cut across every scale. Gated by channels_join_not_cross_at_fork.
            continue
        else:
            # a delivery ditch TAPERS as it descends: it sheds water into the paddies it feeds all
            # along its length, so its flow - and width - decreases from full at the canal takeoff to a
            # THREAD at the delivery point where it stops (continuously "tapped by the plots it feeds",
            # extending Tabayashi's supply-canal taper rule to the delivery ditches). w_tail marks the
            # narrow end so the gen draws it dwindling, not a blunt constant-width stub that stops dead.
            # `head_ft` was capped against the parent's LOCAL width where this ditch takes off, so a
            # delivery can never be drawn wider than the canal feeding it (DELIVERY_PARENT_FRAC).
            channels.append({"pts": pre, "w": chan_px(t.head_ft, grain), "w_tail": chan_px(DELIVERY_FT[1], grain), "role": "branch"})
    # ...AND NO DELIVERY RUNS BESIDE ANOTHER COURSE AS ITS TWIN (feature 294 B4, `twins.py`): a delivery taking off from the
    # second canal ran down beside it 12-32 ft away for 190-310 ft on four of the five hamlets; its plots take their water over
    # their bunds instead (tagoshi), as at the head fork above
    drop_twin_deliveries(channels, first, 2.0 / grain)


def _comb_envelope(threads: list[_Thread], a_pts: Poly, dpts: Poly, F: _Frame) -> Poly:
    """The fan's envelope - the canal, the outer threads, the drain - its floor trimmed to the command area.

    Research: floor ends at the collector - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: the envelope's vertices past the level-extended drain line pulled back onto it
    """
    envelope = [p for p in a_pts] + [p for p in threads[-1].pts] + list(reversed(dpts)) + list(reversed(threads[0].pts))

    # TRIM THE FLOOR TO THE COMMAND AREA (known-open ledger 2026-08-16, Mizuguchi's SE needle -
    # and the same class on all four live hamlets: 0.7-1.8% of floor area, measured with no plot
    # vertex more than 0.8 px past the line). Where the collector stops short of the outer
    # threads, the raw ring closes across ground down-fall of the (flat-extended) drain line -
    # ground that cannot drain and is never planted (the wedge filler refuses it by the same
    # extension rule), so it renders as bare field color: a dead needle hanging off the fan.
    # Pull every vertex past the line back up-fall onto it. `floor_overhang` is the shared
    # predicate the gate reads too (comb_floor_ends_at_the_collector); the 0.5 px floor keeps
    # already-clear vertices byte-identical - the envelope's low edge IS the drain polyline, and
    # a float round-trip must not dirty it.
    _fo = floor_overhang(envelope, dpts, math.degrees(F.down))
    envelope = [(p[0] - o * F.d[0], p[1] - o * F.d[1]) if o > 0.5 else p for p, o in zip(envelope, _fo, strict=True)]
    # ...then merge the near-duplicate vertices the clamp deposits where the cut meets the old
    # boundary (merged-roll review 2026-08-16, Kashikawa: ~12 points with reversals in a ~5 px
    # span at the trim corner) - data hygiene for every later consumer of the ring.
    envelope = simple_outline(dedup_ring(envelope, 1.0))  # ...which cannot merge a fold of points 1-3 px apart (feature 287)
    return envelope
