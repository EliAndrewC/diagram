"""Split from hamletgen/hinterland.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

from typing import Any

from l7r.diagram.settlement import Settlement

from ..plan import SitePlan


def content_box(s: Settlement, plan: SitePlan, pad: float = 0.0) -> tuple[float, float, float, float]:
    """The bounding box of everything the crop will frame to - the field, its hem, the homesteads and
    the pond - grown by `pad`. Read from the manifest, so it tracks whatever actually got drawn."""
    xs: list[float] = [p[0] for p in plan.envelope]
    ys: list[float] = [p[1] for p in plan.envelope]
    for d in s.M.get("dry_plots", []):
        xs += [float(v[0]) for v in d["poly"]]
        ys += [float(v[1]) for v in d["poly"]]
    for h in s.M.get("houses", []):
        xs.append(h["x"])
        ys.append(h["y"])
    pond = s.M.get("pond")
    if pond:
        xs += [pond[0] - pond[2], pond[0] + pond[2]]
        ys += [pond[1] - pond[3], pond[1] + pond[3]]
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


def brook_beside_the_field(s: Settlement) -> list[tuple[float, float, float, float]]:
    """The brook's stations beside the field, as crop content: a box of the brook's own width round each vertex that lies
    within `BROOK_FRAME_MARGIN` of the field and its dry hem.

    THE BROOK PASSING THE FIELD IS PART OF THE PICTURE (feature 230, settlement-review pass 10). The crop ignores
    watercourses because a stream is a runner that trails off the edge, and that is still true of the reach leaving the
    map - so only the stations abreast of the cultivated ground are reserved, and the exit legs are not. `brook_skirt`
    holds every such station inside that same box, so the reservation grows the frame by at most the margin on the brook's
    flank (about 45 px on the pool), and is what lets the margin be wide enough not to fight the skirt. ONE body, read by
    `stage_frame` and by `scatter_frame`, because the scatter throws inside a PREDICTION of the frame and a reservation
    one of them did not know about is a view past the prediction (`test_no_shipped_hamlet_breaches_its_scatter_frame`,
    which is how this was found)."""
    from ..consts import BROOK_FRAME_MARGIN  # noqa: PLC0415 - kept beside its one use

    rings = [list(f.get("outline") or []) for f in s.M.get("fields") or []] + [list(d.get("poly") or []) for d in s.M.get("dry_plots") or []]
    xs = [float(q[0]) for r in rings for q in r]
    ys = [float(q[1]) for r in rings for q in r]
    if not xs:
        return []
    m = BROOK_FRAME_MARGIN + 1.0  # the box `brook_skirt` holds its stations inside, and a pixel for the rounding
    out: list[tuple[float, float, float, float]] = []
    for st in s.M.get("streams") or []:
        hw = float(st.get("w", 6)) / 2.0
        for qx, qy in st.get("stations") or st.get("poly") or []:  # the stations, not a rounded course's added vertices
            if min(xs) - m <= qx <= max(xs) + m and min(ys) - m <= qy <= max(ys) + m:
                out.append((qx - hw, qy - hw, qx + hw, qy + hw))
    return out


#: How far past the predicted frame the scatter still throws. 120 in feature 224 (D2), for a hard feature placed after the
#: hinterland that lands outside everything known; 224's own R3 then enumerated every such placer and found none that grows
#: the crop laterally (the pool's tightest side was the pad exactly, the prediction's non-pad part coinciding with the
#: view), so laterally the pad's only job is to let a mark centered just outside the view still paint into it - the widest
#: mark is the wet tint at `MARSH_TINT_R` 28 px. 40 covers it with room (feature 225 FR-002, D2); the north keeps the band
#: allowance below. The breach record, the pool test, the cohort and the report line say so if a later placer breaks this.
SCATTER_PAD = 40.0
#: ...and the TITLE BAND on the north side (feature 224, the 48-map cohort): a sheet with no room for its name grows a
#: band above the map sized to the placard (`Settlement.title`, 30 * 1.2 + 46 + 24 + 32 = 138 px) AFTER the crop, and
#: on four of 48 seeds it reached 6 px past the pad - so the prediction's top edge carries the band's full height too.
TITLE_BAND_ALLOWANCE = 140.0


TITLE_POCKET_RISE = 30 * 1.2 + 46 + 24 + 12 + 8 + 48  # ft: the pocket's height (`title_pocket`'s placard) with its 8 ft gap and 48 ft of step-out


def frame_extras(s: Settlement, plan: SitePlan) -> list[tuple[float, float, float, float]]:
    """The ground a hamlet's frame reserves as CONTENT beyond the crop's own boxes (x0, y0, x1, y1): an OUTSIDE title
    pocket, the confluence with a trunk's length round it, and the brook's reach beside the field. `stage_frame` used to
    assemble these itself; `frame_for` reads them now, so the view decided early carries them (feature 287, M6)."""
    from ..sink import BROOK_JOIN_TRUNK  # noqa: PLC0415 - sink imports the hinterland package

    pocket = title_pocket(s, plan)  # the pocket the belt was dented around (feature 150) - reserved once
    extra = [pocket] if plan.title_pocket_outside else []  # an OUTSIDE reservation is content the crop must take in; an inside one changes nothing
    # ...AND THE CONFLUENCE, WITH A LENGTH OF ITS TRUNK (feature 230, settlement-review passes 6 and 7). Where the drain
    # meets the passing brook, that junction is a FEATURE - the thing the third sink exists to show - and the crop ignores
    # watercourses because they are runners that trail off the edge, so Sawada's was drawn 7.4 ft outside the sheet with
    # none of its 359 ft of trunk in view. The junction and a trunk's length round it are reserved as content, the
    # mechanism the title pocket uses.
    if plan.confluence is not None:
        _cx, _cy = plan.confluence
        _t = BROOK_JOIN_TRUNK * 0.5  # half the trunk each way: the junction, and enough brook below it to read as one
        extra.append((_cx - _t, _cy - _t, _cx + _t, _cy + _t))
    return extra + brook_beside_the_field(s)  # ...and the brook's reach beside the field, which is picture, not a runner off the edge


def frame_for(s: Settlement, plan: SitePlan) -> tuple[float, float, float, float]:
    """THE VIEW, as the crop would frame the map as it stands now: the crop's frame-setting boxes (`_crop_boxes`, the
    source `crop_to_content` reads), `frame_extras`, `CROP_MARGIN`, clamped to the canvas - `content_view`, the crop's own
    body. Called ONCE into `plan.view` at the end of `stage_hinterland`'s seating, after the last frame-setting feature
    (the belt, whose inner face sets the frame - GM 2026-08-26), and `stage_frame` sets exactly that view (feature 287,
    M6). Before the decision it is also the frame a placer asks "will this be on the page" of (`frame_bounds`)."""
    from l7r.diagram.settlement.core import content_view  # noqa: PLC0415 - kept beside its one use

    from .parcels import CROP_MARGIN  # noqa: PLC0415 - parcels imports this module

    return content_view(s._crop_boxes(city=False), frame_extras(s, plan), CROP_MARGIN, s.W, s.H)


def frame_bounds(s: Settlement, plan: SitePlan) -> tuple[float, float, float, float]:
    """The view as (x0, y0, x1, y1): `plan.view` once it is decided, and until then `frame_for` of the map as it stands -
    ONE function for every placer that asks where the page will be (feature 287, M6)."""
    vx, vy, vw, vh = plan.view if plan.view is not None else frame_for(s, plan)
    return (vx, vy, vx + vw, vy + vh)


def scatter_frame(s: Settlement, plan: SitePlan) -> tuple[float, float, float, float]:
    """The frame the scatter predicts and throws within (feature 224, GM 2026-09-11: "the scatter still throws its
    off-map blades"): the crop's own frame-setting boxes at this moment (`_crop_boxes`, the source `crop_to_content`
    reads), the belt, the woodland patches and the bamboo seats already scanned, and the title pocket when one is
    reserved - grown by the crop's margin and `SCATTER_PAD`. The same prediction `stage_windbreak` makes for the
    belt's clumps, with the reserved polygons added because this runs earlier. Recorded on the settlement so
    `finish()` can say whether the view stayed inside it (`meta.scatter_frame_breach`). A convention this sets: the file's
    scatter is a function of this frame, not of the parcel - a map re-cropped wider than its recorded view finds bare
    ground from `SCATTER_PAD` out (settlement-review, 2026-09-11)."""
    from .parcels import CROP_MARGIN  # noqa: PLC0415 - parcels imports this module

    if plan.view is not None:
        # THE VIEW IS DECIDED (feature 287, M6): the scatter throws within it and `SCATTER_PAD` past it, nothing predicted -
        # the pad for a mark centered just outside that still paints in, the north's allowance for the title band, which
        # `title()`'s last rung grows above the map after the crop
        vx, vy, vw, vh = plan.view
        return (vx - SCATTER_PAD, vy - SCATTER_PAD - TITLE_BAND_ALLOWANCE, vx + vw + SCATTER_PAD, vy + vh + SCATTER_PAD)
    # BEFORE THE DECISION - the marsh's throw, which the view depends on (the title pocket's search reads the marsh) - the
    # frame is still a prediction, and the breach record (`finish`) audits it
    boxes = s._crop_boxes(city=False)
    xs = [v for b in boxes for v in (b[0], b[1])]
    ys = [v for b in boxes for v in (b[2], b[3])]
    for poly in [plan.belt or [], *plan.woodland_polys, *plan.bamboo_polys]:
        xs += [float(q[0]) for q in poly]
        ys += [float(q[1]) for q in poly]
    if plan.title_pocket is not None:
        xs += [plan.title_pocket[0], plan.title_pocket[2]]
        ys += [plan.title_pocket[1], plan.title_pocket[3]]
    elif ys and min(ys) - TITLE_POCKET_RISE < 0.0:
        # ...AND, BEFORE THE POCKET IS RESERVED, WHERE IT WILL GO (feature 261, cohort seed 45): the pocket tries above the
        # content first and goes below it when every seat above is off the canvas, and the first scatter is thrown before
        # it is reserved - so the prediction takes in the band below the content in that case, as `TITLE_BAND_ALLOWANCE`
        # takes in the one above. Seed 45's houses stood at the canvas top, its pocket went under the field, and the view
        # reached 41 px past the prediction.
        ys.append(max(ys) + TITLE_POCKET_RISE)
    for b in brook_beside_the_field(s):  # the frame reserves it, so the prediction must too
        xs += [b[0], b[2]]
        ys += [b[1], b[3]]
    if plan.confluence is not None:  # ...and the confluence with its trunk, which the frame reserves too (feature 261: cohort
        # seed 45's moved with the brook's walk and the view reached 41 px past a prediction that did not know it)
        from ..sink import BROOK_JOIN_TRUNK  # noqa: PLC0415 - kept beside its one use

        _t = BROOK_JOIN_TRUNK * 0.5
        xs += [plan.confluence[0] - _t, plan.confluence[0] + _t]
        ys += [plan.confluence[1] - _t, plan.confluence[1] + _t]
    if not xs:
        return (0.0, 0.0, float(s.W), float(s.H))  # pragma: no cover - a hamlet has its field and houses by now [224: the empty case keeps the throw whole]
    grow = CROP_MARGIN + SCATTER_PAD
    return (min(xs) - grow, min(ys) - grow - TITLE_BAND_ALLOWANCE, max(xs) + grow, max(ys) + grow)


def throw_to_the_view(s: Settlement, frame: tuple[float, float, float, float]) -> None:
    """Every scatter thrown before the view was decided, thrown again into the strips of its parcel past the frame it
    predicted and inside `frame` - the scatter frame of the DECIDED view (`scatter_frame` once `plan.view` is set) - and its
    frame then recorded as `frame` (feature 287, M6 and water W52). So the scatter and the view agree by construction: the
    marsh is laid before the decision (the title pocket's search and the woodland scan read it) and thrown within a
    prediction of the view, and on cohort seed 8 the decided view reached 87 px past that prediction's foot - a strip of
    marsh with no reeds, which `finish` recorded as `scatter_frame_breach`. The re-throws are those the throwers offered
    (`land.wet.offer_rethrow`) while `stage_hinterland` held `s._scatter_catchup` open; it is closed here, so no closure over
    the settlement outlives the stage."""
    from l7r.diagram.settlement.finish import scatter_strips  # noqa: PLC0415 - the one strip computation, kept beside its use

    reg = vars(s).pop("_scatter_catchup", None) or {}
    fx0, fy0, fx1, fy1 = frame
    for k, rethrow in sorted(reg.items()):
        old, parcel = s._scatter_frames[k]
        for strip in scatter_strips(old, parcel, (fx0, fy0, fx1 - fx0, fy1 - fy0)):
            rethrow(strip)
        s._scatter_frames[k] = (frame, parcel)


TITLE_POCKET_CLEAR_FT = 40.0
"""How far the title's pocket keeps from a feature GLYPH (feature 287, water W58; future-work, "The burial ground beside the
title placard": Kashikawa's burial glyph stood 23 ft left of the placard on its center line and read as its ornament). A
GUESS, and a map drawing convention rather than a fact about a place: no page gives a figure for how far a cartouche stands
from a symbol, and 40 ft is a little under twice the distance that read wrong."""

#: The manifest keys whose records are feature GLYPHS a title must not read as ornamented by - the burial ground, a shrine
#: or temple, a wellhead, the notice board, a torii. Ground (a clearing, a field, cover) is not a glyph.
TITLE_GLYPH_KEYS = ("cemeteries", "religious", "shrines", "wells", "kosatsuba")


def pocket_clear_of_features(pocket: tuple[float, float, float, float], M: Any, clearance: float) -> bool:
    """THE ONE PREDICATE of the title pocket's keep-clear (feature 287, water W58): the pocket (x0, y0, x1, y1), grown by
    `clearance` each way, meets no feature glyph's box (`TITLE_GLYPH_KEYS`, a record's `w`/`h` or its drawn radius) and
    no torii (recorded as a bare point, its glyph about 38 x 28)."""
    x0, y0, x1, y1 = pocket[0] - clearance, pocket[1] - clearance, pocket[2] + clearance, pocket[3] + clearance
    boxes: list[tuple[float, float, float, float]] = []
    for k in TITLE_GLYPH_KEYS:
        for o in M.get(k) or []:
            if "x" not in o:
                continue
            hw = float(o.get("w", 2.0 * float(o.get("vr", o.get("r", 8.0))))) / 2.0
            hh = float(o.get("h", 2.0 * float(o.get("vr", o.get("r", 8.0))))) / 2.0
            boxes.append((float(o["x"]) - hw, float(o["y"]) - hh, float(o["x"]) + hw, float(o["y"]) + hh))
    boxes += [(float(t[0]) - 19.0, float(t[1]) - 10.0, float(t[0]) + 19.0, float(t[1]) + 18.0) for t in M.get("torii") or []]
    return not any(bx0 < x1 and bx1 > x0 and by0 < y1 and by1 > y0 for bx0, by0, bx1, by1 in boxes)


def clear_pocket_spot(s: Settlement, window: tuple[float, float, float, float], w: float, h: float, planned: Any, clearance: float) -> tuple[float, float] | None:
    """The first box of `w` x `h` in `window` (x, y, w, h), scanned as `title()` scans (`Settlement._blank_label_spot`: 22 px
    in from the window, a 24 px step, top to bottom and left to right), that clears every title obstacle AND keeps
    `clearance` from every feature glyph (`pocket_clear_of_features`) - the pocket search's own scan, so the keep-clear is
    decided where the pocket is chosen (feature 287, water W58). None where no box does."""
    obs = s._title_obstacles(planned=planned)
    vx0, vy0, vw, vh = window
    y = vy0 + 22.0
    while y + h <= vy0 + vh - 22.0:
        x = vx0 + 22.0
        while x + w <= vx0 + vw - 22.0:
            if s._box_clear(x, y, x + w, y + h, obs) and pocket_clear_of_features((x, y, x + w, y + h), s.M, clearance):
                return (x, y)
            x += 24.0
        y += 24.0
    return None


def title_pocket(s: Settlement, plan: SitePlan, w: float = 300.0, h: float = 190.0) -> tuple[float, float, float, float]:
    """Ground held back so the map has somewhere to put its NAME.

    `title()` scans the framed window for a box clearing every feature and falls back to a corner
    overlap when there is none - and on a hamlet the blank ground is a short list: the field takes
    the middle, the hem the high margin, the marsh the whole low toe, the cluster and its grove one
    flank. That leaves the lateral corners, which is exactly where the coppice scan wants to go
    (`open_ground_patches` prefers the nearest qualifying ground). Both cannot have them.

    So one corner of the map's content is reserved before the coppice is sited. The corner chosen is
    the one furthest from the field's middle AND from the houses - the emptiest quarter of the sheet,
    which is where a reader would expect the cartouche anyway. It is a reservation, not a placement:
    `title()` still does its own search and may well sit somewhere else."""
    # RESERVED ONCE (feature 150, Kuwabata seed 21): four callers ask for the pocket at four stages, and each
    # ask re-ran the blank-box search against the obstacles of ITS moment - the belt was dented around one
    # answer, the coppice kept out of another, and the frame's answer (after the crop, with the belt and the
    # groves on the sheet) came back degenerate, so the placard fell back to the corner ON the belt. The
    # first answer is the reservation; every later caller gets the same rectangle.
    if plan.title_pocket is not None:
        return plan.title_pocket
    x0, y0, x1, y1 = content_box(s, plan, pad=30.0)
    # ASK THE ENGINE WHICH GROUND IS ACTUALLY BLANK, rather than assuming a corner is.
    #
    # `_blank_label_spot` is the same scan `title()` will run, so this reserves ground the title can
    # really use. Picking "the corner furthest from the field and the houses" was tried first and is
    # not the same thing: on the reference map that corner already held the reed marsh - which IS a
    # title obstacle, being a distinct wet surface rather than sparse ground cover - so the pocket
    # was reserved over ground the title could never have taken, the coppice went somewhere else for
    # nothing, and the title still landed on the fallback corner. Reserving what is blank NOW works
    # because this runs after the water, the crops, the houses and the hinterland and before the
    # only two things left that could fill it (the coppice and the grove).
    _planned = [list(plan.belt)] if plan.belt else []  # the belt is not drawn yet; see `_title_obstacles(planned=...)`
    # ...AND KEPT CLEAR OF THE FEATURE GLYPHS by `TITLE_POCKET_CLEAR_FT` (feature 287, water W58): the same scan, asked the
    # keep-clear as well, so a pocket beside the burial ground is refused for the next one (`clear_pocket_spot`)
    _clear = s.px(TITLE_POCKET_CLEAR_FT)
    spot = clear_pocket_spot(s, (x0, y0, x1 - x0, y1 - y0), w, h, _planned, _clear)
    if spot is None:
        # A SMALLER POCKET BEFORE NONE (feature 150 T50 fallout, Kuwabata seed 21): with a sixteenth house
        # on the sheet's right flank the 300 x 190 reservation found no home, nothing was held back, the
        # coppice took the last blank corner, and `title()` - finding no clear box either - fell back to
        # that corner ON the grove (`title_clear_of_features`). The placard itself is ~195 x 106, so a
        # 210 x 120 pocket is still a real reservation; only when even that fails is nothing reserved.
        w, h = 210.0, 120.0
        spot = clear_pocket_spot(s, (x0, y0, x1 - x0, y1 - y0), w, h, _planned, _clear)
    if spot is None:
        # THE SHEET HAS NO ROOM FOR ITS NAME (feature 150 T50 fallout, Kuwabata seed 21): with the cluster
        # seated clear of the reed fringe, the houses, the fringe and the connector left no blank box the
        # placard's size anywhere inside the content, and `title()` fell back to a corner ON the windbreak.
        # The frame's margin is capped at 56 px by `crop_hugs_content`, so the answer is not a wider margin:
        # the pocket is reserved just OUTSIDE the content on the emptiest side - HERE, at the first ask,
        # before the belt is dented and the coppice sited, because by the frame stage the belt has grown
        # over the only outside band - and `stage_frame` hands it to the crop as content (the placard is
        # something the reader needs on the sheet as much as a house is; `crop_hugs_content` counts it as
        # frame-setting for the same reason). Tried in the order a reader scans: above-left, above-right,
        # below-left, below-right; the first that clears every title obstacle (a connector leaving the
        # sheet, a marsh, the field) is the reservation. Each try is recorded in the manifest.
        _cx0, _cy0, _cx1, _cy1 = content_box(s, plan, pad=0.0)
        _bw = max(s._text_width(plan.spec.name, 30) + 4, 100.0) + 24 + 12  # the placard's own size (settlement.title) + 6 px each side
        _bh = 30 * 1.2 + 46 + 24 + 12
        _obs = s._title_obstacles(planned=_planned)
        _tries: list[list[float]] = []
        # ...stepping outward up to 48 px per corner: the content box is the field's envelope, and a house
        # seated on its edge stands 14 px past it, so the first offset can land on a roof.
        for _px, _py0, _out in ((_cx0, _cy0 - _bh - 8, -1.0), (_cx1 - _bw, _cy0 - _bh - 8, -1.0), (_cx0, _cy1 + 8, 1.0), (_cx1 - _bw, _cy1 + 8, 1.0)):
            for _shift in (0.0, 16.0, 32.0, 48.0):
                _py = _py0 + _out * _shift
                _ok = s._box_clear(_px, _py, _px + _bw, _py + _bh, _obs) and pocket_clear_of_features((_px, _py, _px + _bw, _py + _bh), s.M, _clear)
                _tries.append([round(_px, 1), round(_py, 1), round(_px + _bw, 1), round(_py + _bh, 1), float(_ok)])
                if _ok:
                    plan.title_pocket = (_px, _py, _px + _bw, _py + _bh)
                    plan.title_pocket_outside = True
                    break
            if plan.title_pocket_outside:
                break
        s.M["meta"]["title_pocket_tries"] = _tries
        if plan.title_pocket is None:
            plan.title_pocket = (x0, y0, x0, y0)  # pragma: no cover - the map is already too full to title; nothing to reserve [174: KEPT, not deletable - it assigns the pocket the caller returns]
    else:
        plan.title_pocket = (spot[0], spot[1], spot[0] + w, spot[1] + h)
    return plan.title_pocket
