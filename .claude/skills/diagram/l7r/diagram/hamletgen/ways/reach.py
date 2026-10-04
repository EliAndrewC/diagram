"""THE REACH THE WEB DRAWS AS TREE LANES (lifted out of `settle.py` at the 1,000-line bar, feature 320; `settle` re-exports
it): a spur to each way target no way reaches (`settle_targets`) and, where no way reaches the field on a brook map, the
field way (`settle_field`) - each the first run that keeps the law, judged by the settle's `Lawful` handed in, and drawn as
a tree lane no repair cuts.

Research: the reach drawn as tree lanes - NONE: claimed at each step
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

from ..consts import WEB_CLEARANCE, Poly
from . import law
from .bund import BRANCH_WIDTH, paddy_ground
from .checks import served_network
from .corridors import ACCESS_WIDTH, FIELD_ROLE, ROUTED_FIELD_STARTS, TARGET_ROLE, field_router, field_runs, routed_field_runs, spur_runs
from .geom import memo_ground, worked_ground

Judge = Callable[..., bool]
"""The settle's `Lawful` as these steps ask it: `(run, width)` -> does a tree lane along `run` keep the law."""


def _rounded(p: Poly) -> list[list[float]]:
    return [[round(float(x), 1), round(float(y), 1)] for x, y in p]


def _draw_tree_lane(s: Any, run: Poly, width: float, role: str, **extra: Any) -> None:
    s.lane(_rounded(run), width=width, clearance=WEB_CLEARANCE, worn=True)
    s.M["lanes"][-1].update({"role": role, **extra})


def settle_targets(s: Any, lawful: Judge) -> int:
    """Step 4b (homes H36): a spur from the network to every way target it does not reach (`law.unreached_targets` - a
    burial ground's near edge), the shortest straight run that keeps the law (`Lawful`), drawn as a tree lane, once. A
    target no such run reaches stays unreached - never drawn to by a least-bad spur (FR-005) - and the settle's report
    names it.

    Research: a path runs to the graves - UNRESEARCHED: the shortest lawful straight spur from the network, once"""
    M = s.M
    done = {tuple(ln["to"]) for ln in M.get("lanes") or [] if ln.get("role") == TARGET_ROLE and ln.get("to")}
    n = 0
    for t in law.unreached_targets(M):
        key = (round(t[0], 1), round(t[1], 1))
        if key in done:
            continue
        run = next((r for r in spur_runs(served_network(M.get("lanes") or []), t) if lawful(r, ACCESS_WIDTH)), None)
        if run is not None:
            _draw_tree_lane(s, run, ACCESS_WIDTH, TARGET_ROLE, to=list(key))
            n += 1
    return n


def settle_field(s: Any, lawful: Judge) -> int:
    """Step 4c: THE FIELD WAY, where no way of the hamlet's own reaches the field on a brook map (`law.field_unreached`): the
    first run from the network on to the bund that keeps the law (`Lawful`, as a tree lane, squared at its crossings) - straight, or over the brook
    square at a ford (`field_runs`), then threaded round the steadings by the web's router (`routed_field_runs`,
    `field_router`), the paddy's ground first and then the worked ground's - drawn as a tree lane (`FIELD_ROLE`), so no
    repair cuts it. Returns 1 where one is drawn, else 0, and the settle refuses a field left unreached
    (`last_resort.refuse_unreached`).

    WHY HERE (feature 320, FR-004): the same search used to reserve the field's corridor before any house stood; with nothing
    reserved, the web's own straight field path (`bund.a_way_onto_the_bund`) can be left off the network and dropped
    (`settle_network`; Sawada: its field path stood apart from the lanes, and the nearest way ended 167 ft from the field).

    Research:
        the field reached - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a way runs from the network to the field's bund
        over the brook at a ford - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: square, at the ford that makes the walk shortest"""
    M = s.M
    if not law.field_unreached(M):
        return 0
    brook = next(iter(law._brooks(M)), [])
    grounds = [g for g in (paddy_ground(s), memo_ground(s, "worked", worked_ground)) if g.edge is not None]
    segs = served_network(M.get("lanes") or [])
    if not grounds or not segs:
        return 0
    fords = [(float(x), float(y)) for x, y in (M.get("meta") or {}).get("brook_fords") or []]

    def candidates() -> Iterator[Poly]:
        yield from field_runs(segs, grounds, BRANCH_WIDTH / 2.0, brook, fords)
        route = field_router(s, brook)
        for ground in grounds:
            yield from routed_field_runs(segs, ground, BRANCH_WIDTH / 2.0, route, brook, fords, starts=ROUTED_FIELD_STARTS)

    # ...EACH SQUARED AT ITS WATER CROSSINGS before it is judged and drawn (`Lawful.squared`, as the seating judged the field's
    # corridor until feature 320): a run over the brook at a ford is judged as the web draws it
    square = getattr(lawful, "squared", lambda r: r)
    run = next((q for r in candidates() if len(r) >= 2 and lawful(q := square(r), BRANCH_WIDTH)), None)
    if run is None:
        return 0
    _draw_tree_lane(s, run, BRANCH_WIDTH, FIELD_ROLE)
    return 1
