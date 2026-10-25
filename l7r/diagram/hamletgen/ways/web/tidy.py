"""The web's END TRIMS: every lane end tidied to what it serves (the collapsed-lane drop and the overrun cut went in feature 417 T26, the connector's pull-back in T19). Split from `ways/web.py` at the 1,000-line bar (feature 405 T57).

Research: web plumbing - NONE"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_dist

from ...consts import (
    WEB_REACH_FT,
    Poly,
)
from ..bund import run_lanes_on_to_the_bund, worked_ground_of
from ..fabric import _WEB_MIN_FT
from ..geom import _components, _trim_to_service, lane_houses, polyline_len, steading_footprints


def tidy_lane_ends(s: Settlement, envelope: Poly, streets: bool = False) -> None:
    """THE LAST PASS OVER EVERY LANE END, after the joins: pull back anything that still reaches nothing.

    A ROW'S STREETS ARE TRIMMED APART, with `streets=True`, once the door paths are laid (feature 291 plan D17): a row
    farm stands a frame's depth off its street and is reached by its door path, laid after this pass, so trimmed with
    the rest a street was cut back to the first farm near enough to count (Kashikawa's, from 2,800 ft to 1,400).

    LIFTED TO MODULE LEVEL (feature 227, the GM's 2026-08-28 ruling on inner functions and testability). It was the
    tail of `stage_web`, and its shortening branch had no reader but the shipped rolls - so the moment the end rule
    learned to see a tread that had ARRIVED at a dooryard, no pool map needed shortening and the branch went
    uncovered. That is the right outcome for the maps and the wrong way to test a safety net: it still has to work
    for the seed that needs it. Everything it needs comes from the settlement and the crop's envelope, so it takes
    those two and nothing else.

    Research:
        lane end reaches something - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: pulled back to a way, a house or the bund
        end carried on to the bund - research/questions/0014-bunds-between-the-paddies-aze.drawing.html
        lane serving nothing dropped - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane, or a stretch of
            one, that serves nothing is not drawn (the page's GUESS, on Mencius 14.21 and the Tang Code art. 404) - unless it is the only link in
            the web, which serves the ways it joins (405 T15)
        a tail kept as a house's only way - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: never for a household reached across a neighbor's land, owed none (`geom.lane_houses`)
        the track out not trimmed here - research/questions/0081-village-lanes.drawing.html: the track out is laid by its own placer (`stage_track`), and whether its end meets the ways is asked of the finished map (`checks.track_ends_off_the_web`)
        a row's street not dropped for serving nothing - research/questions/0033-row-villages-resson.drawing.html: the street is the road the row stands on, laid before the farms and running on off the map; a street is laid as one way along its row and its farms are reached by door paths laid after this pass (feature 291 plan D17), so it is never dropped here
        shortest lane kept - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); a trim leaving a lane under _WEB_MIN_FT, 30 ft, is not applied, or the lane is dropped
        only-way reach - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a house with no other way within WEB_REACH_FT, 100 ft, keeps its tail
    """
    _final_houses = [(float(h["x"]), float(h["y"])) for h in s.M.get("houses", [])]
    _owed = lane_houses(s.M)  # the houses a lane may be kept as the only way to
    _final_steadings = steading_footprints(s.M)  # a tread that stops at a dooryard has arrived there (feature 227 D11)

    _nowhere: list[int] = []  # lanes that serve nothing at either end - dropped after the loop, back to front
    # THE FIELD AS DRAWN, not the plan's envelope (feature 261): an end serves the field where it reaches the paddy a reader
    # sees - the bar the pool's lane-end test holds - and the envelope stands well out from it on a polder, so a skeleton
    # arm into Kuwabata's scrub 481 ft from any paddy counted as reaching the field. The envelope stands in where no field
    # outline is recorded.
    # ...AND AN END THAT MAKES FOR THE FIELD IS CARRIED ON TO ITS BUND FIRST (269 B04/B17): the trim below counts the bund, not
    # "within 60 ft of the field", so an end left short of it would be pulled back to a dooryard it had walked away from.
    _ground = worked_ground_of(s, envelope)
    run_lanes_on_to_the_bund(s, _ground)
    for _i, _ln in enumerate(list(s.M.get("lanes", []))):
        # KEPT AND NOT REACHABLE TODAY, deliberately (feature 146). Every pass that can empty a lane
        # DELETES the record with the ink (feature 145's "the husk goes with the ink"), so no husk
        # survives to here - and injecting one to prove it fails earlier, in the orphan joiner, which
        # cannot handle a one-point way at all. As of feature 155 that is true of the knot-collapse
        # drop BELOW this line as well, which used to be the exception this comment pointed at. The
        # guard stays because a future reorder would hand one straight to `_ln["pts"][0]`, and because
        # three separate passes have now had to learn this rule one at a time.
        if len(_ln.get("pts") or []) < 2:  # pragma: no cover - see above
            continue
        if bool(_ln.get("street")) != streets:
            continue
        _pts = [(float(x), float(y)) for x, y in _ln["pts"]]
        _others = [
            sg
            for _o in s.M.get("lanes", [])
            if _o is not _ln and len(_o.get("pts") or []) >= 2
            for sg in zip([(float(x), float(y)) for x, y in _o["pts"]], [(float(x), float(y)) for x, y in _o["pts"]][1:], strict=False)
        ]
        # THE LATE PASS HOLDS THE GATE'S OWN BAR (feature 227 D11). It used to keep the loose 90 ft house
        # bar, and so could pull an end back to a point 63-68 px from anything - past the 60 px
        # `WAY_END_REACH_FT` the gate asks of every internal end - which is how a map that refused a
        # straggler path at draw time shipped a dangling end anyway. The houses this lane is the ONLY way to
        # are named so the tidy-up cannot strand one (cohort seed 39's farmhouse, `_trim_to_service`).
        # ...never a household reached across a neighbor's yard, which is owed no way of its own (`geom.lane_houses`, feature 317)
        _keep = [_h for _h in _owed if all(seg_dist(_h[0], _h[1], _a, _b) > WEB_REACH_FT for _a, _b in _others)]
        # ...BUT THE TRACK OUT STAYS AS IT WAS LAID (feature 320; the exit strip's rule before it, feature 287 wave 6): every
        # household's way reaches it at the way out's gate, and pulled back to service its start left them all off the network
        # (the reference hamlet: 85 ft). Its inner end's walk on to the network (`_pull_back_to_service`) went in feature 417
        # T19: measured needless - with it off no fixed, pinned or pool verdict moved and no finished map's end was off the web
        if _ln.get("connector"):
            continue
        _kept = _trim_to_service(_pts, _others, _final_houses, _ground, keep=_keep, steadings=_final_steadings)
        if len(_kept) >= 2 and polyline_len(_kept) >= _WEB_MIN_FT and _kept != _pts:
            _ln["pts"] = [[round(x, 1), round(y, 1)] for x, y in _kept]
            # AND THE INK WITH IT - see `Settlement.reink_lane`. Shortening the record alone left the
            # drawn lane longer than the checked one, which is the quietest kind of wrong there is.
            s.reink_lane(_i)
        elif (
            not _ln.get("street")
            and (
                len(_kept) < 2
                # trimmed to a nub too short to be a lane (Kashikawa's field spur kept 2 ft past the tread it stopped on) that is
                # no house's only way: the nub serves nothing the tread it leaves does not
                or (polyline_len(_kept) < _WEB_MIN_FT and not any(min(seg_dist(_h[0], _h[1], _a, _b) for _a, _b in zip(_pts, _pts[1:], strict=False)) <= WEB_REACH_FT for _h in _keep))
            )
        ):
            _nowhere.append(_i)
    # ...AND A LANE THAT SERVES NOTHING AT EITHER END GOES (feature 261, once main's placer re-laid the pool): trimmed to
    # service it keeps a single point, and this pass used to leave such a lane whole - a skeleton arm run into the scrub on
    # Kuwabata, and on Kashikawa a field spur whose far end another lane had joined and taken over, its head a plank over
    # the brook to nothing. A lane that is some house's only way names that house in `keep` and never trims to a point, so
    # nothing it serves is stranded; the planks are laid after this stage, so none is left behind.
    # ...BUT A LANE THAT IS THE ONLY LINK BETWEEN TWO PARTS OF THE WEB SERVES THEM BOTH, and stays: this is the last pass
    # that drops a lane and nothing rejoins after it, so on Inashiro at the 269 landing (the house bearings re-laid) it
    # dropped the lane that tied a skeleton arm to the rest, and the map shipped two networks (`lanes_form_one_network`).
    s.drop_lanes(unsplitting_drops(s.M.get("lanes", []), _nowhere))


def unsplitting_drops(lanes: Sequence[Mapping[str, Any]], drops: Sequence[int]) -> list[int]:
    """The lanes of `drops` that can go without parting the web: each is dropped only if the lanes left after it fall into
    no more networks (at the 4 ft ink tolerance) than before - tried back to front, each against the drops already taken.

    Research: web kept one network - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html"""
    ways = [[(float(x), float(y)) for x, y in ln.get("pts") or []] for ln in lanes]
    gone: set[int] = set()

    def networks(skip: set[int]) -> int:
        live = [w for k, w in enumerate(ways) if k not in skip and len(w) >= 2]
        return len(set(_components(live, 4.0)))

    for i in sorted(drops, reverse=True):
        if networks(gone | {i}) <= networks(gone):
            gone.add(i)
    return sorted(gone)
