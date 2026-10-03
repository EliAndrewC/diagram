"""The parts the seating laid, held in the registry of what stands until they are drawn (feature 287 M8).

Research: registry holds - NONE: bookkeeping of what stands
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling.lot import HELD_KINDS as HELD_KINDS
from l7r.diagram.settlement.rolling.lot import held_part_records


def hold_laid_parts(s: Settlement, houses: Sequence[Mapping[str, Any]]) -> int:
    """HOLD WHAT THE SEATING LAID UNTIL IT IS DRAWN (feature 287 M8). A household's well pocket and its farmstead fixtures
    are laid in its bundle at seating and drawn later - the pocket and most fixtures in `stage_appurtenances`, after the
    track, a flexible form's laid seat after the web (`_draw_pending`). A way laid in between could not see them: cohort
    1-60 drew 8 fixtures and a wellhead on a lane so. So each is stood in the registry of what stands (`Standing.hold`) at
    the seating's end, as the record it will be drawn as - the pocket as its wellhead, a fixture as its seat's box - and
    every way the track and the web lay keeps off it by the overlap matrix; drawn, it is released and recorded as itself.
    Each is the record the seat asked the registry about before it chose (`rolling/lot.py:bundle_admitted`, water W53), so a
    hold never lands on what the matrix forbids. Returns the parts held."""
    held: dict[Any, Any] = {}
    vr = float(s._well_vr())
    for h in houses:
        fixtures = [f for f in h.get("fixtures") or () if f.get("kind") in HELD_KINDS and f.get("box")]
        recs = held_part_records(float(h["x"]), float(h["y"]), h.get("well_pocket"), [(f["kind"], f["box"]) for f in fixtures], vr)
        if h.get("well_pocket"):
            key, rec = recs.pop(0)
            held[(key, rec["x"], rec["y"])] = s.standing.hold(key, rec)
        for f, (key, rec) in zip(fixtures, recs, strict=True):
            held[(key, id(f))] = s.standing.hold(key, rec)
    s._held_parts = held  # type: ignore[attr-defined]
    return len(held)


def release_held(s: Settlement, key: str, *ident: Any) -> None:
    """Take down the hold on a part about to be drawn (`hold_laid_parts`): a pocket by its (x, y), a fixture by its seat."""
    held = getattr(s, "_held_parts", None) or {}
    k = (key, *((round(float(ident[0]), 1), round(float(ident[1]), 1)) if key == "wells" else (id(ident[0]),)))
    rec = held.pop(k, None)
    if rec is not None:
        s.standing.release(key, rec)
