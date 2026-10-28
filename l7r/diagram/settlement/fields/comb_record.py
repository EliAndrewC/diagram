"""The comb field's records: the field and its ditches written to the manifest, the source channel from the sluice, and the
furrows drawn on a plot.

Split from `comb.py` by feature 443 T09 (the 1,000-line bar, constitution Principle X clause 13): a counter of the work its
hem's refusal test does took `comb.py` to 1,004 lines. `FieldsMixin` composes this beside `CombMixin`, so every method is
reached through `self.` as before.

Research: plumbing - NONE: geometry, indexing, tolerances and manifest records
"""

import math
from typing import TYPE_CHECKING, Any

from l7r.diagram.overlap.registry import refuse_unadmitted
from l7r.diagram.work_counts import OPS

from .._geom import (
    point_in_poly,
    seg_closest,
    seg_dist,
    seg_reach_index,
    within_reach,
)
from .._knobs import _centroid, _sharp_corners
from .comb import channel_end_on_stream, feed_stub
from .landuse import line_cuts
from .outfall import CURVE_LEG_PX as CURVE_LEG_PX
from .outfall import DOWNHILL_FRACTION as DOWNHILL_FRACTION
from .outfall import outfall_run as outfall_run
from .outfall import runs_downhill as runs_downhill

if TYPE_CHECKING:
    from ..core import Settlement


class CombRecordMixin:
    """The comb field's manifest records, its source channel and its furrows (`FieldsMixin` composes it)."""

    def _comb_record_field(self: Settlement, net: dict[str, Any], name: str) -> None:  # type: ignore[misc]
        """Assemble and append this fan's M['fields'] record: envelope, per-plot dims, drain-hem rings,
        plot rings in draw order and the bead points.

        Research:
            its salts, guards and sentinels - NONE: they decide nothing about the place - 30 (manifest band for recording plots near the drain)
        """
        env = [[round(x, 1), round(y, 1)] for x, y in net["envelope"]]
        exs, eys = [p[0] for p in env], [p[1] for p in env]
        pvx = [v[0] for p in net["plots"] for v in p["poly"]]
        pvy = [v[1] for p in net["plots"] for v in p["poly"]]
        # Per-plot [along-fall span, cross-fall span, centroid x, centroid y, vertex count, count of
        # still-square corners], so parcel-fabric checks (polder_parcels_vary, polder_parcels_front_water,
        # polder_parcels_are_organic) measure the DRAWN geometry from the manifest rather than trusting
        # a builder self-report. The last two are the OUTLINE shape: a ruled quad is 4 vertices with all
        # 4 corners square, while a hand-piled parcel carries a densely sampled, wandering outline on
        # which most - not all - corners have eased. The pair separates earth from CAD without recording
        # every vertex (the full outlines would roughly double a polder manifest for no extra teeth).
        ddp = float(self.M["meta"].get("down_deg", 90))
        pdx, pdy = math.cos(math.radians(ddp)), math.sin(math.radians(ddp))
        pdims = []
        for p in net["plots"]:
            al = [vx * pdx + vy * pdy for vx, vy in p["poly"]]
            cr = [vx * pdy - vy * pdx for vx, vy in p["poly"]]
            pcx, pcy = _centroid(p["poly"])
            pdims.append([round(max(al) - min(al), 1), round(max(cr) - min(cr), 1), round(pcx, 1), round(pcy, 1), len(p["poly"]), _sharp_corners(p["poly"])])
        # THE BUNDS ALONG THE COLLECTOR, recorded so the gate can actually see them (2026-08-08).
        # `pdims` above is extents-and-a-centroid: it cannot express "this bund is drawn ACROSS the
        # drainage ditch", which is precisely the defect the GM caught on Hoshizora - the hem plots
        # were laid on the contour while the collector runs at up to ~19 deg to it, so every hem
        # bund started above the ditch and ended below it. `paddy_bunds_clear_the_collector` needs
        # the real outlines to judge that, so the SMALL SET of plots that actually border this fan's
        # drain carries its polygon into the manifest - a dozen-odd rings per fan, not a second copy
        # of the field. Band is generous (a plot merely NEAR the ditch is cheap to record and a plot
        # the band misses is invisible to the check, which is the failure that matters).
        _dch = next((c for c in net["channels"] if c["role"] == "drain" and len(c["pts"]) >= 2), None)
        _hem_rings: list[list[list[float]]] = []
        if _dch is not None:
            _dpp = _dch["pts"]
            _band = 30.0 + max(_dch["w"], _dch.get("w_tail", _dch["w"]))
            _dx0, _dy0 = min(q[0] for q in _dpp) - _band, min(q[1] for q in _dpp) - _band
            _dx1, _dy1 = max(q[0] for q in _dpp) + _band, max(q[1] for q in _dpp) + _band
            # THE DRAIN'S SEGMENTS FROM AN INDEX (feature 306, the GM: a check against many things means a line was not
            # drawn to stay beside). Each vertex of each plot near the drain measured its distance to EVERY drain segment -
            # 12,263 `seg_dist` a call on the pool - for a yes/no that only the segments within `_band` can answer. Each
            # segment is filed by its box widened by the band (and a pixel, so a rounding cannot drop one), the vertex asks
            # the ones whose widened box holds it, and `seg_dist <= _band` decides as before: the minimum over every
            # segment is within the band exactly when some segment is.
            _hem = seg_reach_index([(_dpp, 1.0)], _band)
            for p in net["plots"]:
                if any(_dx0 <= vx <= _dx1 and _dy0 <= vy <= _dy1 for vx, vy in p["poly"]) and any(within_reach(_hem, vx, vy, _band) for vx, vy in p["poly"]):
                    _hem_rings.append([[round(vx, 1), round(vy, 1)] for vx, vy in p["poly"]])
        _fld: dict[str, Any] = {
            "name": name,
            "kind": "paddy",
            "outline": env,
            "bbox": [min(exs), min(eys), max(exs), max(eys)],
            "vis_bbox": [min(pvx), min(pvy), max(pvx), max(pvy)],
            "plots": pdims,
            "drain_hem": _hem_rings,
            # THE PLOT RINGS, IN DRAW ORDER, plus the azemame bead points (GM 2026-08-15). `pdims`
            # above deliberately compacts each plot to extents-and-a-centroid, but that record
            # cannot express "this plot is painted OVER that one's bund" - `_fill_wedges`' fillers
            # lap up to ~12 real ft onto a neighbor and paint last, and the bead line laid along
            # the buried stretch surfaced as green dots floating mid-paddy on Inashiro. A check can
            # only judge bead-on-visible-bund from the real rings in paint order, so they are
            # recorded in full (bund_beans_on_bunds reads both; draw order IS list order).
            #
            # THIS IS A PAINT-ORDER STACK, NOT A PARTITION - DISSOLVE BEFORE YOU MEASURE ANYTHING
            # (GM decision 2026-08-17). Rings LAP: a filler painted later covers part of its
            # neighbor, which is exactly why the pair reads as the one shared aze a real fan has,
            # and the stack is the honest record of the INK. It is NOT an area record. Summing
            # these areas double-counts the lapped ground (0.4-2.5% of the fabric, measured over
            # the scripted hamlets and a 48-seed cohort), and treating two rings as adjacent
            # because they touch says nothing about
            # which of them the reader can see. So anything computing acreage, per-field yield or
            # basin-to-basin adjacency must dissolve the stack first (later ring wins) rather than
            # trusting the list. Trimming each ring to its visible extent here - which would make
            # this a true partition - was priced and DECLINED: it would re-derive
            # `bund_beans_on_bunds`, which is built ON the burial, and put polygon booleans on the
            # gate's path. The ceiling that keeps the lap small enough for this note to stay true
            # is `paddy_plot_rings_overcount_stays_marginal`; the full decision, with both declined
            # alternatives, is in git history (the backlog entry since closed).
            "plot_rings": [[[round(vx, 1), round(vy, 1)] for vx, vy in p["poly"]] for p in net["plots"]],
            "bund_beans": [[round(bx, 1), round(by, 1)] for bx, by in net["bund_beans"]],
        }
        if net.get("cell") is not None:
            # THE DESIGN CELL this fan was carved to, in px^2 (the comb only - the terrace, ribbon
            # and polder engines record none, and the size floor is deliberately comb-only). Carried
            # so `paddy_basins_are_worth_their_bund` measures each basin against the reference the
            # PLACER used instead of re-deriving one from `meta.ftpx`, which `plot_texture` makes
            # wrong. Legacy manifests lack it and the check skips them.
            _fld["cell"] = round(float(net["cell"]), 1)
        if net.get("down_deg") is not None:
            _fld["down_deg"] = net["down_deg"]  # this fan's LOCAL fall (see `carve_comb`)
        if net.get("fork") is not None:
            # the bunsuiguchi division point (the comb only - a polder net records none), read by
            # comb_supply_commands_both_flanks; legacy manifests lack it, so the check skips them
            _fld["fork"] = [round(net["fork"][0], 1), round(net["fork"][1], 1)]
        self.M["fields"].append(_fld)

    def _comb_record_ditches(self: Settlement, net: dict[str, Any], name: str) -> None:  # type: ignore[misc]
        """Record one field_ditch per channel, carrying the trimmed and polder-side tags.

        A RECORD DOES NOT CARRY A POINT TWICE (settlement-review, feature 230 pass 12). The head race is traced to the
        fork it ends at, and where the trace already stood there the fork was appended again - so three pool maps
        shipped a ditch whose last two points are identical, and on two of them the whole record WAS that duplicate
        plus a lead: Inashiro's was 3.2 ft of "main" and Mizuguchi's 21.9, each drawn as its own stroke, each a hover
        region a reader could meet, each reading on the sheet as a blunt stub of ditch stopping in the bare hem. What
        is dropped here is only ink nothing is losing: a run under a foot has no course to show.

        Research:
            its salts, guards and sentinels - NONE: they decide nothing about the place - 0.05 (duplicate-point tolerance)
        """
        for c in net["channels"]:
            _pts = [q for i, q in enumerate(c["pts"]) if i == 0 or math.dist(q, c["pts"][i - 1]) > 0.05]
            rec = {"poly": [[round(x, 1), round(y, 1)] for x, y in _pts], "role": c["role"], "field": name, "w": round(c["w"], 1), "w_tail": round(c.get("w_tail", c["w"]), 1)}
            if c.get("trimmed"):  # a TRIMMED in-wall drain is a conduit stub, not a contour collector
                rec["trimmed"] = True
            if c.get("seg"):  # a polder ring-side tag (feeder/e_toe/w_toe/drain/lateral), so footbridge placement can be side-aware
                rec["seg"] = c["seg"]
            refuse_unadmitted(self.M, "field_ditches", rec)  # the skeleton, recorded before the ground that asks against it (W53)
            self.M["field_ditches"].append(rec)

    def _comb_source_channel(self: Settlement, net: dict[str, Any], name: str, source: dict[str, Any], sluice: Any, pond_rec: Any) -> None:  # type: ignore[misc]
        """Record the hairline SOURCE -> field feed channel that carries the water topology.

        Keeps its own `kind != 'cascade'` guard: a cascade field is fed plot-to-plot from an
        upstream field and its caller records that connector itself.

        Research:
            feed joins the brook - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the intake snapped onto a brook within 30 px, else sourced at the sluice
            feed runs downhill - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a feed whose net travel is level or uphill is refused, and the snap onto a stream taken only where it still runs down (`runs_downhill`)
            a stream of no recorded width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.html: taken as the village brook's 7 ft in the mouth-in-the-water test, as `stream` draws it
            feed recorded width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: recorded at the drawn width of the channel it traces - the comb's head race, or the polder's main canal from the reservoir's rim (feature 328: both were recorded at the head race's 6.0)
            its salts, guards and sentinels - NONE: they decide nothing about the place - 70 (step from the fork into the crop); 12 (clearance test for the pulled end); 20 (bow off the chord); 14 (pull off the edge)
        """
        if source.get("kind") != "cascade":
            hr = net["channels"][0]["pts"]
            fork = hr[-1]
            dd = self.M["meta"].get("down_deg", 90)
            dx, dy = math.cos(math.radians(dd)), math.sin(math.radians(dd))
            din = (fork[0] + dx * 70, fork[1] + dy * 70)
            # ...AND IT MUST LAND INSIDE THE CROP, whatever the field's shape (2026-08-15).
            #
            # `channel_field_anchored` wants this end inside the outline and >= 10 px clear of its
            # edge, "so the field paints over the end". Stepping 70 px downhill from the main
            # channel's last point is a COMB's geometry: a head-race ends at the field's head, so
            # downhill goes into the crop. A POLDER's main is the perimeter ring running ALONG the
            # high edge, so its last point is a corner and the same step skims the boundary - the
            # mouth landed 2.6 px inside on two scripted seeds in three, and no amount of moving the
            # SLUICE changed it, because this end is constructed here rather than taken from the
            # anchor. Fixed by asking the envelope: if the downhill step is already well inside,
            # nothing moves (every comb map is byte-identical); otherwise the end is pulled in along
            # the nearest edge's inward normal until it clears.
            _env_in = net.get("envelope") or []
            # ...and near a CORNER the pull runs again (feature 150 T51): pulled 14 px off the top edge, the
            # polder's mouth stood 9 px from the west edge. Up to three rounds, each on the now-nearest edge;
            # a comb's first round does not fire, so every comb map is still byte-identical.
            for _pull_round in range(3 if len(_env_in) >= 3 else 0):
                if __debug__:
                    OPS["candidate@_comb_source_channel"] += 1
                _n_in = len(_env_in)
                _din_d = min(seg_dist(din[0], din[1], _env_in[_k], _env_in[(_k + 1) % _n_in]) for _k in range(_n_in))
                if point_in_poly(din[0], din[1], _env_in) and _din_d >= 12.0:
                    break
                _best_in = min(
                    ((seg_closest(din[0], din[1], _env_in[_k], _env_in[(_k + 1) % _n_in]), _env_in[_k], _env_in[(_k + 1) % _n_in]) for _k in range(_n_in)),
                    key=lambda t: math.hypot(t[0][0] - din[0], t[0][1] - din[1]),
                )
                _q_in, _a_in, _b_in = _best_in
                _ex_in, _ey_in = -(_b_in[1] - _a_in[1]), _b_in[0] - _a_in[0]
                _el_in = math.hypot(_ex_in, _ey_in) or 1.0
                _nx_in, _ny_in = _ex_in / _el_in, _ey_in / _el_in
                _cx_in = sum(q[0] for q in _env_in) / _n_in
                _cy_in = sum(q[1] for q in _env_in) / _n_in
                if _nx_in * (_q_in[0] - _cx_in) + _ny_in * (_q_in[1] - _cy_in) > 0:  # point it INWARD
                    (
                        _nx_in,
                        _ny_in,
                    ) = (  # pragma: no cover - the winding-order guard; build_polder winds its envelope so the raw edge normal already points inward [174: KEPT, not deletable - it flips a normal - removing it changes geometry, not just a skip]
                        -_nx_in,
                        -_ny_in,
                    )
                din = (_q_in[0] + _nx_in * 14.0, _q_in[1] + _ny_in * 14.0)
            start = pond_rec if pond_rec else (sluice[0], sluice[1])
            frm = {"kind": "pond"} if pond_rec else {"kind": "stream"}
            _fdd = math.radians(float(net["down_deg"]) if net.get("down_deg") is not None else float(dd))
            _feed_fall = (math.cos(_fdd), math.sin(_fdd))  # the field's own fall, as the channel rule reads it (its record's `down_deg`)
            if not pond_rec:
                # snap the intake's START onto the nearest stream centerline (within the 30px anchor
                # band): an offtake JOINS its stream at a confluence like any junction - the symmetric
                # case of the drain-culvert rule (channels_join_streams_at_confluence) - rather than
                # beginning in the grass beside it. A comb fed by its OWN feeder brook ending AT the
                # sluice is already joined (distance ~0) and is left alone.
                nearest: Any = None
                for st_ in self.M.get("streams", []):
                    sp_ = st_["poly"]
                    for si_ in range(len(sp_) - 1):
                        fq = seg_closest(start[0], start[1], sp_[si_], sp_[si_ + 1])
                        dq = math.hypot(start[0] - fq[0], start[1] - fq[1])
                        if nearest is None or dq < nearest[0]:
                            nearest = (dq, fq)
                # ...ONLY WHERE THE FEED STILL RUNS DOWNHILL FROM IT (feature 287, water:W10): the record runs from `start` to the
                # fork, so a snap that left its net travel level or uphill is not taken and the feed keeps the sluice
                if nearest and 0.5 < nearest[0] <= 30 and runs_downhill([nearest[1], fork], _feed_fall):
                    start = nearest[1]
                # ...AND IT DECLARES A STREAM ONLY WHERE IT REACHES ONE (feature 287, labels L16): beyond the anchor band
                # the intake is not snapped, so its mouth stood in the grass while the record said it joined the brook.
                # Such a feed is sourced from the sluice itself, and says so.
                if not any(channel_end_on_stream(start, st_["poly"], float(st_.get("w") or self.px(7.0))) for st_ in self.M.get("streams", []) if len(st_.get("poly") or ()) >= 2):
                    frm = {"kind": "sluice"}
            vx, vy = din[0] - start[0], din[1] - start[1]
            vl = math.hypot(vx, vy) or 1.0
            midx, midy = (start[0] + din[0]) / 2 - vy / vl * 20, (start[1] + din[1]) / 2 + vx / vl * 20
            # THE RING HEAD IS TOUCHED, not merely passed near (2026-08-15).
            #
            # `watercourse_ends_reach_water` lets a main/drain end outside the crop stand only if it
            # JOINS another watercourse, within ~12 px. On a comb that is free: the sluice IS the
            # head-race's end, so this channel starts on it. On a POLDER the ring canal's end is a
            # corner of the block and the reservoir sits uphill of it, so the run passes NEAR the
            # head - measured 17.6 px - and the ring's end reads as dangling. The bow is what does
            # it: the polyline kinks 20 px off the chord at its midpoint, and the head lies ON the
            # chord, so the drawn line bends away from exactly the point it needs to meet.
            #
            # Straightening the bow is not available - `channel_winds_gently` requires 5-50 px of
            # deviation, and a dead-straight cut fails it. So the head is INSERTED as a vertex when
            # the drawn run does not already reach it. On every comb map the run starts on the head,
            # the distance is ~0, and nothing is inserted: the pool is byte-identical.
            _ch_poly = [[round(start[0], 1), round(start[1], 1)], [round(midx, 1), round(midy, 1)], [round(din[0], 1), round(din[1], 1)]]
            if not pond_rec:
                # THE RECORD TRACES THE HEAD RACE THAT IS DRAWN (settlement-review, feature 230 pass 10). Before the brook was
                # tapped this bowed line WAS the drawn feed; since the head race is carved at its offtake angle (`hr`, the
                # net's own first channel) the bow traced a course 50 px from any ink, and the site boundary kept houses off
                # water that was not there. Sluice, the race's own vertices to the fork, then the step into the field that
                # anchors the topology.
                _ch_poly = [[round(start[0], 1), round(start[1], 1)], *[[round(float(q[0]), 1), round(float(q[1]), 1)] for q in hr[1:]]]
                # ...and it ENDS AT THE FORK, where the drawn race ends. An extra step into the field was kept to anchor the topology,
                # and it was a record of water that is not there - a 70 ft tail past the ink on the reference hamlet and Sawada
                # (pass 11); nothing reads the channel's field end as more than the field it names.
            else:
                # THE POND'S FEED TRACES ITS DRAWN STUB TOO (feature 294 B1, record against ink). The bowed line above was the
                # polder's record while the drawn inlet is the feeder's stub, run onto the reservoir's rim (`inlet_to_rim`): on
                # Kuwabata the record jogged 20 ft west of the stub for 101 ft (the record-against-ink class the reviews caught
                # five times). The pond's center, then the stub from the rim back down to the first point inside the crop - the
                # ring's corner - where the drawn feed meets the field.
                _ch_poly = [[round(start[0], 1), round(start[1], 1)], *[[round(float(q[0]), 1), round(float(q[1]), 1)] for q in reversed(feed_stub(hr, _env_in))]]
            # THE RING HEAD IS TOUCHED BY CONSTRUCTION NOW (feature 294 B1). The head used to be INSERTED as a vertex when a
            # polder's bowed record passed near the ring's corner without meeting it (2026-08-15, feature 150 T51: `join_head`,
            # passed by the polder path alone). Both records now trace what is drawn - the race to its fork, the pond's stub to
            # the ring's corner (`feed_stub`) - so the record ends on the head and the insertion never fired on the pool or the
            # gate's cohort rolls; it was removed rather than kept as a repair with nothing to repair.
            # THE FEED RUNS DOWNHILL OR IS NOT RECORDED (feature 287, water:W10): from the sluice the race leaves at the offtake
            # angle (35 degrees off the brook's downstream heading, 0054, which runs down the fall, so its net travel runs 0.82 of its length down it) and a polder's reservoir
            # stands above the block's high corner, so by construction it always does; a feed that climbs is refused by
            # name here, never recorded as water running uphill
            if not runs_downhill(_ch_poly, _feed_fall):
                raise ValueError(f"{name}: the feed from its {frm['kind']} to the field runs level or uphill ({_ch_poly[0]} -> {_ch_poly[-1]})")
            # ...AND IT NAMES THE FIELD IT FEEDS (feature 287, water W53): it traces the head race, and a field's own water may
            # lie along its own resting basin (`_MATRIX_SAME_PARENT_OK`); a stranger's may not. Asked before it is recorded.
            _feed = {"poly": _ch_poly, "frm": frm, "to": {"kind": "field", "name": name}, "w": float(net["channels"][0].get("w") or 6.0), "field": name}
            refuse_unadmitted(self.M, "channels", _feed)
            self.M["channels"].append(_feed)

    def _draw_furrows(self: Settlement, poly: Any, color: str, theta: float, cls: str | None = None) -> None:  # type: ignore[misc]
        """Stylised ridge/furrow lines within a dry-field plot (dry crops are row-cultivated).

        Research:
            furrowed rows - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: every dry plot drawn in ridged rows
            furrow spacing - GUESS: 5 px between rows
            furrow ink - CONVENTION: 0.8 stroke at 0.8 opacity"""
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
        dx, dy = math.cos(theta), math.sin(theta)
        nx, ny = -dy, dx
        # THE ROWS ARE CUT TO THE PLOT AT WRITE TIME (feature 225 FR-004): each row is a line at `theta` and the plot a
        # convex quadrilateral, so the row's ends are its two crossings of the plot's edges (`line_cuts`) and the
        # `<clipPath>` the rows sat in - a layer per plot in resvg, 29 on Inashiro, a quarter tile 0.74 -> 0.44 s
        # without them (specs/225 research R1) - is not needed; a plot a row meets other than twice keeps the clip.
        rows: list[tuple[float, float, float, float]] = []
        ts = -diag / 2
        clip = False
        while ts <= diag / 2:
            mx, my = cx + nx * ts, cy + ny * ts
            cut = line_cuts(poly, mx, my, dx, dy)
            if cut is None:
                clip = True
                break
            rows += [(mx + dx * t0, my + dy * t0, mx + dx * t1, my + dy * t1) for t0, t1 in cut]
            ts += 5
        if clip:
            cid = self._cid("dry")
            pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in poly)
            g = [f'<clipPath id="{cid}"><polygon points="{pts}"/></clipPath>', f'<g clip-path="url(#{cid})">']
            t = -diag / 2
            while t <= diag / 2:
                mx, my = cx + nx * t, cy + ny * t
                g.append(
                    f'<line x1="{mx - dx * diag / 2:.1f}" y1="{my - dy * diag / 2:.1f}" x2="{mx + dx * diag / 2:.1f}" y2="{my + dy * diag / 2:.1f}" stroke="{color}" stroke-width="0.8" opacity="0.8"/>'
                )
                t += 5
            g.append("</g>")
            self.add("".join(g), cls=cls)
            return
        self.add("".join(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{color}" stroke-width="0.8" opacity="0.8"/>' for ax, ay, bx, by in rows), cls=cls)
