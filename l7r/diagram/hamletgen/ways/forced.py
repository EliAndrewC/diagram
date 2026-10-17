"""A TURN OR A MEETING THE GROUND FORCES (feature 385 T01, plan D2): the lane law's angle rules describe open ground.

The lane page's principle is that a worn path takes the shortest or easiest way, with the fewest turns, never doubling back
(research/questions/0081-village-lanes.html). Its numbers - a hairpin at 140 degrees, two 50 degree turns within 40 ft, a 12
ft hook, a needle under 20 degrees - are drawing conventions, "chosen at the scale of a dozen paces, not measured"
(0081's drawing page). Where a house, another household's yard or garden, a grove, a fixture, a field or water stands
across the straighter line, the easiest way IS the sharper one: a walker goes round what stands there (the GM, 2026-10-17:
"if I'm walking through the forest and there's a rock ... then things will come together at different angles"). So each
angle rule asks, where it would refuse a shape, whether the straighter way was open:

- a TURN (a kink, a hairpin, a hook, a folded joint, a hairpin at the track's start) is forced when the chord past it - the
  vertex before it to the vertex after, at the lane's width - is not lawful ground for a footpath;
- a MEETING (a needle) is forced when a rung across the sliver between the arriving end leg and the tread it meets is not.

"Lawful ground" is the settle's own test (`settle.Lawful.on_lawful_ground`: no foul of the fabric, no field, dry plot or
marsh underfoot, no crossing fault), so the law cannot refuse a shape the settle bent round something, nor admit one it
would not draw. The ground is read once per manifest while its registries stand (`ground`).

Research: a forced turn is lawful - DEVIATION research/questions/0081-village-lanes.drawing.html: the angle limits read as describing open ground; a turn or meeting whose straighter way the mapped ground blocks is drawn as walked (the GM, 2026-10-17)
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from typing import Any

from l7r.diagram.settlement import seg_closest

from ..consts import Pt

Blocked = Callable[[Pt, Pt, float], bool]
"""Is the straight way from one point to another, at a width, NOT lawful ground for a footpath?"""

RUNG_SHARES = (1.0 / 3.0, 2.0 / 3.0, 1.0)
"""Where along a needle's end leg, from its end, a rung is laid across the sliver to the tread: a third, two thirds and the
leg's far vertex - enough that a fence or a corner standing in the wedge lies across one.

Research: rungs across a needle - NONE: probe points for the ground test, nothing drawn"""


class _View:
    """A manifest seen as the settlement `settle.Lawful` reads: its `M` (`_homestead_polys`, `memo_ground`) and its scale
    (`px`, a well's verge), from the manifest's own `meta.ftpx` - for a reader that has only the manifest.

    Research: plumbing - NONE: a view of the manifest"""

    def __init__(self, M: Mapping[str, Any]) -> None:
        """Research: plumbing - NONE: stores the manifest and its scale"""
        self.M = M
        self.ftpx = float((M.get("meta") or {}).get("ftpx") or 1.0)

    def px(self, ft: float) -> float:
        """Research: plumbing - NONE: feet to pixels at the map's scale"""
        return ft / self.ftpx


_GROUND: list[tuple[Any, tuple[int, ...], Blocked]] = []
"""The ground test per manifest, newest last, at most `_GROUND_MAX`: kept while the registries it reads stand unchanged.

Research: plumbing - NONE: a cache"""
_GROUND_MAX = 4
"""Research: plumbing - NONE: the cache's size"""


def _registries(M: Mapping[str, Any]) -> tuple[int, ...]:
    """What the ground reads, by count: every list registry but the lanes (the ground stands whatever lanes are drawn).

    Research: plumbing - NONE: a cache signature"""
    return tuple(len(v) for k, v in sorted(M.items()) if k != "lanes" and isinstance(v, list))


def ground(M: Mapping[str, Any], s: Any = None) -> Blocked:
    """The ground test of manifest `M` (`settle.Lawful.on_lawful_ground` turned round), built once while its registries
    stand. `s`, where the caller has the settlement, is read in place of the manifest's view."""
    sig = _registries(M)
    for owner, had, test in _GROUND:
        if owner is M and had == sig:
            return test
    from .settle import Lawful  # bound here: `settle` imports the law, which imports this module

    lawful = Lawful(s if s is not None else _View(M))

    def blocked(a: Pt, b: Pt, width: float) -> bool:
        return math.dist(a, b) > 1e-6 and not lawful.on_lawful_ground([a, b], width)

    _GROUND[:] = [g for g in _GROUND if g[0] is not M][-(_GROUND_MAX - 1) :] + [(M, sig, blocked)]
    return blocked


def forced_turn(blocked: Blocked | None, before: Pt, after: Pt, width: float) -> bool:
    """Is a turn between `before` and `after` (the vertices either side of it) forced - the chord between them not lawful
    ground? With no ground (`None`) nothing is forced, and every angle rule reads as it did before feature 385."""
    return blocked is not None and blocked(before, after, width)


def forced_meeting(blocked: Blocked | None, end: Pt, back: Pt, u: Pt, v: Pt, width: float) -> bool:
    """Is a needle forced - a rung across the sliver between the end leg `back` -> `end` and the tread `u`-`v` it meets,
    at `RUNG_SHARES` along the leg from its end, not lawful ground?"""
    if blocked is None:
        return False
    for t in RUNG_SHARES:
        q = (end[0] + (back[0] - end[0]) * t, end[1] + (back[1] - end[1]) * t)
        f = seg_closest(q[0], q[1], u, v)
        if math.dist(q, f) > 1.0 and blocked(q, f, width):
            return True
    return False


def lazy_ground(M: Mapping[str, Any], s: Any = None) -> Blocked:
    """`ground(M, s)`, built only when first asked - an angle rule asks it only of a shape it would refuse, so a web with
    none builds nothing.

    Research: plumbing - NONE: a lazy build of `ground`"""
    made: list[Blocked] = []

    def blocked(a: Pt, b: Pt, width: float) -> bool:
        if not made:
            made.append(ground(M, s))
        return made[0](a, b, width)

    return blocked
