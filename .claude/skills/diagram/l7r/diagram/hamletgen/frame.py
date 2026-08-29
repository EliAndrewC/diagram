"""STAGE 8: the crossings, the notice board, and the map frame.

Split from hamletgen.py by feature 111; bodies verbatim. See hamletgen/CLAUDE.md.
"""

from __future__ import annotations

import math

from l7r.diagram.settlement import Settlement, seg_dist
from l7r.diagram.settlement.structures.fixtures import KOSATSUBA_MARKER_MIN_PX, KOSATSUBA_VERGE_FT, kosatsuba_anchor

from .consts import POLDER_ARCHETYPES
from .hinterland import CROP_MARGIN, title_pocket
from .plan import SitePlan
from .water import polder_crossing_caps

# THE RE-SEAT PROBE MUST MEASURE THE BOARD THAT IS DRAWN (feature 134 T50, 2026-08-29). This was pinned
# at 14 x 8 while `Settlement.kosatsuba` draws the researched 12 x 5 - not even the same aspect - and the
# probe offsets the seat by HALF THE DEPTH, so every re-seated board stood (8 - 5) / 2 = 1.5 ft further
# from its lane than the verge rule intends. On a 5 ft lane that is 12.5 ft from the centerline where the
# rule asks 11.0, and `kosatsuba_by_the_road` measures against 12.0: gate seed 44 failed by half a foot
# for a board the placer believed it had put exactly on the verge. Derived from the same expression the
# drawing uses, so the two cannot drift again - this engine's standing rule is DERIVE, NEVER PIN.
_BOARD_FT_W, _BOARD_FT_H = 12.0, 5.0  # the researched plank; see `Settlement.kosatsuba`


def _board_footprint(s: Settlement) -> tuple[float, float]:
    """The board's drawn footprint, exactly as `place_kosatsuba` computes it.

    The frame test drives this path with a stub that has no scale, so `px` is optional; without it the
    true feet ARE the pixels, which is the hamlet grain this re-seat exists for."""
    _px = getattr(s, "px", None)
    _w = max(_px(_BOARD_FT_W), KOSATSUBA_MARKER_MIN_PX) if _px else _BOARD_FT_W
    return _w, _w * _BOARD_FT_H / _BOARD_FT_W


# ---- STAGE 8: crossings, the board, and the frame ------------------------------------------------


def stage_crossings(s: Settlement, plan: SitePlan) -> None:
    """Bridges where a way crosses water, and plank footbridges over the long irrigation ditches.

    After every way and every watercourse, because a crossing added later leaves an unbridged one -
    the engine's own `bridges()` docstring says so and the `roads_bridge_water` check enforces it."""
    s.bridges()
    if s.M.get("field_ditches"):
        if plan.field_archetype in POLDER_ARCHETYPES:
            # A POLDER'S RING CANAL is crossed where the village is (feature 150; the rule the
            # hand-authored polders carried, `polder_crossing_caps`): planks cluster on the
            # settlement-side toe collector, one per interior lateral, none on the feeder, the far
            # toe or the drain. Spacing as the hand-authored maps had it.
            s.channel_footbridges(spacing=320, seg_caps=polder_crossing_caps(plan))
            s.dike_gates()  # a sluice gate at every cut of the perimeter dike, snapped to the recorded water (feature 150 A7)
        else:
            s.channel_footbridges(spacing=300)


def stage_notice(s: Settlement, plan: SitePlan) -> None:
    """The official notice board, on a lane verge at the busiest node.

    EVERY settlement tier posts the state's standing law, hamlets included - the ofuregaki circulars
    reached the peasantry through this board, read out by the one required-literate person (a
    hamlet's senior farmer, answering to the village headman). `place_kosatsuba` sites it itself,
    deterministically, from the same route records the validator reads.

    It runs BEFORE the ground cover and the woods, not with the framing, because it needs a clear
    verge and it competes for the same ground the scrub scatter and the grove clumps take. Sited
    after them it silently found nowhere to go on one cohort map in six and the gate reported a
    hamlet with no notice board - a failure of ORDER, not of siting."""
    spot = s.place_kosatsuba()
    # ...AND IT MUST STAND WHERE THE FRAME WILL KEEP IT. `place_kosatsuba` maximizes passing traffic
    # (dwellings within ~260 px) along the whole way network, and a lane ARM that runs past the
    # cluster still sees the whole cluster from its far end - so on a held-out cohort hamlet the
    # board landed 87 px north of the northernmost farmhouse, on a stretch of lane serving nobody.
    # `crop_to_content` frames the HARD features and deliberately ignores linear runners like lanes,
    # so the board and its caption fell outside the sheet (`labels_within_image`). Adding the board
    # to the crop's hard set was tried and is worse: it then holds the frame open by itself, which is
    # what `crop_not_held_open_by_one_feature` exists to stop. The board belongs among the houses it
    # is read by, so if the engine's traffic score sends it outside them, re-seat it on the nearest
    # verge that is inside the cloud.
    # THE GUARD NOW TESTS THE FRAME ITSELF, because the frame exists (GM 2026-08-29). This stage runs
    # after `stage_frame`, so `meta.view` is already decided - and the requirement was always
    # `labels_within_image`, never "among the houses". The house-cloud bbox was standing in for the
    # crop because the crop had not been computed yet, and standing in badly: it refused every seat
    # outside the built ground, which is exactly where an `entrance` board belongs, so it threw away
    # the placement the knob had rolled on two of three maps and put the board back at the busiest
    # node while the manifest went on claiming `entrance`.
    hs = s.M.get("houses", [])
    _view = (s.M.get("meta") or {}).get("view")
    if spot is not None and (_view or hs):
        if _view:
            _vx, _vy, _vw, _vh = (float(_q) for _q in _view)
            hx0, hy0, hx1, hy1 = _vx, _vy, _vx + _vw, _vy + _vh
        else:  # no crop recorded (the frame test drives this stage with a stub) - fall back to the cloud
            hx0, hx1 = min(h["x"] for h in hs), max(h["x"] for h in hs)
            hy0, hy1 = min(h["y"] for h in hs), max(h["y"] for h in hs)
        if not (hx0 - 30 <= spot[0] <= hx1 + 30 and hy0 - 30 <= spot[1] <= hy1 + 30):
            board = s.M["kosatsuba"].pop()
            # ...AND ITS INK (feature 133 T48). Popping the record and the caption left the first
            # board's GLYPH in the top layer, so a map whose engine seat fell outside the cloud
            # shipped two boards with one record - found the day the household bamboo strips moved
            # the engine's seat. `kosatsuba` records its `add_top` z; blank that entry.
            _top = getattr(s, "top", None)
            _zi = int(board.get("z", -1)) - int(getattr(s, "TOPZ", 0))
            if _top is not None and 0 <= _zi < len(_top):
                _top[_zi] = ""
            # ...and its CAPTION with it. `kosatsuba` records the board and calls `self.label`, so
            # popping only the board leaves an orphan "notice board" caption sitting where the board
            # used to be - which is the very label the frame could not hold, still failing
            # `labels_within_image` after the board itself had moved.
            for _li in range(len(s.M.get("labels", [])) - 1, -1, -1):
                if len(s.M["labels"][_li]) > 5 and s.M["labels"][_li][5] == "notice board":
                    _lab = s.M["labels"].pop(_li)
                    # ...and the caption's INK, in the label layer (T48, the same defect one layer up)
                    _tl = getattr(s, "toplabels", None)
                    _lz = int(_lab[4]) - int(getattr(s, "LABELZ", 0))
                    if _tl is not None and 0 <= _lz < len(_tl):
                        _tl[_lz] = ""
                    break
            # THE RE-SEAT MUST OBEY THE SAME TWO RULES THE SITER DOES, and it obeyed neither
            # (settlement-review, feature 154). It ran after `place_kosatsuba` and ranked purely by
            # traffic over every non-connector lane, so on Sawada and Kashikawa it silently threw away
            # the `entrance` seat the knob had rolled and put the board back at the interior busiest
            # node - the map RECORDED a placement it had not drawn, and the interactive page told a
            # clicking reader so. It also seated on a 3 ft `web` straggler, which is exactly what
            # `place_kosatsuba`'s own comment forbids: "A SERVICE LANE IS NOT A PLACE TO POST THE
            # STATE'S NOTICE ... a side lane's busiest node is still a side lane, so scoring must never
            # see it."
            #
            # So: MAIN WAYS FIRST, web lanes only if nothing else takes a board; and where the map
            # declares an anchored placement, rank by nearness to that anchor rather than by traffic.
            _seat = str((s.M.get("meta") or {}).get("kosatsuba_seat") or "center")
            _anchor = kosatsuba_anchor(s.M, _seat)
            _lanes = [ln for ln in s.M.get("lanes", []) if not ln.get("connector")]
            _ranked = [ln for ln in _lanes if not ln.get("web")] or _lanes
            best: tuple[float, float, float, float] | None = None
            for lane in _ranked:
                if lane.get("connector"):  # pragma: no cover - filtered above; kept so the loop reads on its own
                    continue
                pts = lane["pts"]
                for i in range(len(pts) - 1):
                    (ax, ay), (bx, by) = pts[i], pts[i + 1]
                    seg = math.hypot(bx - ax, by - ay) or 1.0
                    ux, uy = -(by - ay) / seg, (bx - ax) / seg
                    rot = math.degrees(math.atan2(by - ay, bx - ax))
                    for t in range(int(seg // 12) + 1):
                        mx, my = ax + (bx - ax) * (t * 12 / seg), ay + (by - ay) * (t * 12 / seg)
                        # ROADSIDE, per T13's verge (feature 133 T48): the old 16 px offset stood the
                        # board outside `kosatsuba_by_the_road`'s band the first time this path ran
                        # on the reference hamlet. Tread half-width + the verge + the board's half depth.
                        _pxf = getattr(s, "px", None)  # the frame test drives this with a stub that has no scale
                        _bw, _bh = _board_footprint(s)
                        _off = float(lane.get("w", 3)) / 2 + (_pxf(KOSATSUBA_VERGE_FT) if _pxf else KOSATSUBA_VERGE_FT) + _bh / 2
                        for side in (1.0, -1.0):
                            cx2, cy2 = mx + ux * _off * side, my + uy * _off * side
                            if not (hx0 <= cx2 <= hx1 and hy0 <= cy2 <= hy1):
                                continue
                            # THE WAY IT FRONTS IS THE WAY IT IS NEAREST (T48): at a junction a verge
                            # of lane A can lie nearer lane B, and `kosatsuba_faces_the_road` measures
                            # the board against its NEAREST way - so a board aligned to A read 90
                            # degrees off B. Refuse a seat whose nearest way runs across this one.
                            _nb = _nearest_way_bearing(s, cx2, cy2)
                            if _nb is not None and min(abs((_nb - rot) % 180.0), 180.0 - abs((_nb - rot) % 180.0)) > 15.0:
                                continue
                            if not s._fits(cx2, cy2, _bw, _bh, corridors=False):
                                continue
                            # ...AND NOT IN THE WATER. `_fits(corridors=False)` is required here - the
                            # corridor test is a HOUSE setback from the tread and would refuse every
                            # verge - but it also switches off the watercourse clearance bundled into
                            # the same call, so this probe would seat a plank board in a stream.
                            # ONE predicate, shared with `place_kosatsuba`, which had the identical
                            # hole and shipped it on cohort seed 13.
                            if not s.fixture_clear_of_water(cx2, cy2, math.hypot(_bw, _bh) / 2):
                                continue
                            # nearest the declared placement where there is one, else the busiest node
                            _rank = math.hypot(cx2 - _anchor[0], cy2 - _anchor[1]) if _anchor is not None else -sum(1 for h in hs if math.hypot(cx2 - h["x"], cy2 - h["y"]) < 260)
                            if best is None or _rank < best[0]:
                                best = (_rank, cx2, cy2, rot)
            if best is not None:
                s.kosatsuba(best[1], best[2], rot=best[3])
            else:  # pragma: no cover - no verge inside the cloud takes a board; keep the engine's seat rather than none
                s.M["kosatsuba"].append(board)


def _nearest_way_bearing(s: Settlement, x: float, y: float) -> float | None:
    """The bearing (degrees) of the nearest lane segment to (x, y), or None with no lanes."""
    best: tuple[float, float] | None = None
    for ln in s.M.get("lanes") or []:
        pts = ln.get("pts") or []
        for k in range(len(pts) - 1):
            a, b = (float(pts[k][0]), float(pts[k][1])), (float(pts[k + 1][0]), float(pts[k + 1][1]))
            d = seg_dist(x, y, a, b)
            if best is None or d < best[0]:
                best = (d, math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
    return None if best is None else best[1]


def stage_frame(s: Settlement, plan: SitePlan) -> None:
    """The crop, then the title.

    In that order: the title searches the FRAMED window for blank space to sit in, so the frame has
    to exist first."""
    # The margin leaves the TITLE somewhere to stand: `title()` scans the framed window for a box
    # that clears every feature and falls back to a corner overlap when the map is too full, which
    # `title_clear_of_features` then fails. But it is bounded above as well as below - `crop_hugs_
    # content` allows at most 56 px of view past the frame-setting content, because a band whose
    # only extra is open ground is wasted image. 64 was tried and fails all twelve. 48 is the most
    # air the frame will give the title.
    _pocket = title_pocket(s, plan)  # the pocket the belt was dented around (feature 150) - reserved once, see hinterland.title_pocket
    _extra = [_pocket] if plan.title_pocket_outside else []  # an OUTSIDE reservation is content the crop must take in; an inside one changes nothing
    s.crop_to_content(margin=CROP_MARGIN, extra=_extra)
    s.M["meta"]["title_pocket"] = [round(v, 1) for v in _pocket]  # recorded so a placard that fell back can be read against the reservation
    s.title(plan.spec.name, prefer=_pocket)
