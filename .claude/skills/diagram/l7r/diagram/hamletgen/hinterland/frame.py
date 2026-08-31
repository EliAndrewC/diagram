"""Split from hamletgen/hinterland.py by feature 173 - see this package's CLAUDE.md for the index."""

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
    spot = s._blank_label_spot(x0, y0, x1 - x0, y1 - y0, w, h)
    if spot is None:
        # A SMALLER POCKET BEFORE NONE (feature 150 T50 fallout, Kuwabata seed 21): with a sixteenth house
        # on the sheet's right flank the 300 x 190 reservation found no home, nothing was held back, the
        # coppice took the last blank corner, and `title()` - finding no clear box either - fell back to
        # that corner ON the grove (`title_clear_of_features`). The placard itself is ~195 x 106, so a
        # 210 x 120 pocket is still a real reservation; only when even that fails is nothing reserved.
        w, h = 210.0, 120.0
        spot = s._blank_label_spot(x0, y0, x1 - x0, y1 - y0, w, h)
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
        _obs = s._title_obstacles()
        _tries: list[list[float]] = []
        # ...stepping outward up to 48 px per corner: the content box is the field's envelope, and a house
        # seated on its edge stands 14 px past it, so the first offset can land on a roof.
        for _px, _py0, _out in ((_cx0, _cy0 - _bh - 8, -1.0), (_cx1 - _bw, _cy0 - _bh - 8, -1.0), (_cx0, _cy1 + 8, 1.0), (_cx1 - _bw, _cy1 + 8, 1.0)):
            for _shift in (0.0, 16.0, 32.0, 48.0):
                _py = _py0 + _out * _shift
                _ok = s._box_clear(_px, _py, _px + _bw, _py + _bh, _obs)
                _tries.append([round(_px, 1), round(_py, 1), round(_px + _bw, 1), round(_py + _bh, 1), float(_ok)])
                if _ok:
                    plan.title_pocket = (_px, _py, _px + _bw, _py + _bh)
                    plan.title_pocket_outside = True
                    break
            if plan.title_pocket_outside:
                break
        s.M["meta"]["title_pocket_tries"] = _tries
        if plan.title_pocket is None:  # pragma: no cover - the map is already too full to title; nothing to reserve
            plan.title_pocket = (x0, y0, x0, y0)
    else:
        plan.title_pocket = (spot[0], spot[1], spot[0] + w, spot[1] + h)
    return plan.title_pocket
