"""The parts the seating laid, held in the registry of what stands until they are drawn (feature 287 M8)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement

#: The laid fixtures drawn as a record of their own, and so held until drawn: the farmstead fixtures and the retirement house.
HELD_KINDS = frozenset({"privy", "manure", "bath", "coop", "woodpile", "shrine", "retirement"})


def hold_laid_parts(s: Settlement, houses: Sequence[Mapping[str, Any]]) -> int:
    """HOLD WHAT THE SEATING LAID UNTIL IT IS DRAWN (feature 287 M8). A household's well pocket and its farmstead fixtures
    are laid in its bundle at seating and drawn later - the pocket and most fixtures in `stage_appurtenances`, after the
    track, a flexible form's laid seat after the web (`_draw_pending`). A way laid in between could not see them: cohort
    1-60 drew 8 fixtures and a wellhead on a lane so. So each is stood in the registry of what stands (`Standing.hold`) at
    the seating's end, as the record it will be drawn as - the pocket as its wellhead, a fixture as its seat's box - and
    every way the track and the web lay keeps off it by the overlap matrix; drawn, it is released and recorded as itself.
    Returns the parts held."""
    held: dict[Any, Any] = {}
    vr = float(s._well_vr())
    for h in houses:
        hx, hy = float(h["x"]), float(h["y"])
        if h.get("well_pocket"):
            wx, wy = round(float(h["well_pocket"][0]), 1), round(float(h["well_pocket"][1]), 1)
            held[("wells", wx, wy)] = s.standing.hold("wells", {"x": wx, "y": wy, "r": 8, "vr": vr})
        for f in h.get("fixtures") or ():
            if f.get("kind") not in HELD_KINDS or not f.get("box"):
                continue  # a persimmon is held off by its trunk (`law.fixture_quads`); a bath's corridor is drawn with its bath
            bx = f["box"]
            key = "retirement_houses" if f.get("kind") == "retirement" else "farm_fixtures"
            held[(key, id(f))] = s.standing.hold(key, {"x": float(bx[0]), "y": float(bx[1]), "w": float(bx[2]), "h": float(bx[3]), "of": [round(hx, 1), round(hy, 1)]})
    s._held_parts = held  # type: ignore[attr-defined]
    return len(held)


def release_held(s: Settlement, key: str, *ident: Any) -> None:
    """Take down the hold on a part about to be drawn (`hold_laid_parts`): a pocket by its (x, y), a fixture by its seat."""
    held = getattr(s, "_held_parts", None) or {}
    k = (key, *((round(float(ident[0]), 1), round(float(ident[1]), 1)) if key == "wells" else (id(ident[0]),)))
    rec = held.pop(k, None)
    if rec is not None:
        s.standing.release(key, rec)
