"""The web settles itself - the settle's driver: the reach, the husks, the step order (`STEPS`) and `settle_the_web`. Split from `ways/settle.py` at the 1,000-line bar (feature 405 T54, under T53's rule); the package docstring (`settle/__init__.py`) is the whole account.

Research: settle plumbing - NONE"""

from __future__ import annotations

import time
from typing import Any

from .. import law
from ..checks import unreached_houses
from ..geom import memo_ground, worked_ground
from ..keeper import unsettled
from ..knots import settle_knots
from ..reach import settle_field, settle_targets
from ..squaring import (
    square_every_crossing,
)
from ..tree import prune_the_tree, settle_defer, settle_tree
from .ends import settle_ends, settle_fragments, settle_joins, settle_needles, settle_network, settle_shadows, settle_street_ends, settle_widths
from .lawful import Lawful
from .shapes import SETTLE_ROUNDS, settle_shapes, settle_way_outs


def settle_reach(s: Any) -> int:
    """Step 4: the reach the web owes - every household's way (laid in the gaps, `gap_ways`, feature 318), drawn as the gap
    pass judged them (`tree.settle_tree`); a spur to each way target (`settle_targets`); and the field way where no way
    reaches the field (`settle_field`).

    Research:
        every farmhouse served - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: every household's way, laid once the last house stands, drawn as a lane of its own
        the field reached - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a way runs to the field's bund
        a path runs to the graves - UNRESEARCHED: claimed at `settle_targets`"""
    drawn = settle_tree(s)  # every household's way, reached or not (feature 318, `tree.owed`); each drawn once
    if not (unreached_houses(s.M) or law.unreached_targets(s.M) or law.field_unreached(s.M)):
        return drawn
    lawful = Lawful(s, tree=True)
    return drawn + settle_tree(s) + settle_targets(s, lawful) + settle_field(s, lawful)


def settle_husks(s: Any) -> int:
    """Drop every lane record that draws nothing (ways W04)."""
    gone = law.husks(s.M)
    if gone:
        s.drop_lanes(gone)
    return len(gone)


# ---- the loop ----------------------------------------------------------------------------------------------------------


STEPS = (
    settle_husks,
    square_every_crossing,
    settle_shapes,
    settle_way_outs,
    settle_ends,
    settle_street_ends,
    settle_shadows,
    settle_joins,
    settle_needles,
    settle_reach,
    settle_defer,
    settle_network,
    settle_fragments,
    prune_the_tree,
    settle_knots,
    settle_widths,
    settle_husks,
)


def settle_the_web(s: Any, rounds: int = SETTLE_ROUNDS) -> dict[str, Any]:
    """Repair the web until every rule of the lane law holds (see the module docstring) and report what it took: `rounds`,
    `seconds`, `changed` (lane edits), `dropped` (ORDINARY lanes the last resort dropped whole - never a tree lane,
    `last_resort.py`), and `unreached_before` / `_after` (`unreached_houses`, the houses the corridor is owed). A web that
    only the tree could mend, or that leaves a farmhouse or the reserved field unreached, is refused by name
    (`last_resort.WebRefused`) - the map is not produced, and nothing is recorded as a failure on it (FR-005)."""
    from ..last_resort import last_resort, refuse_unreached

    t0 = time.perf_counter()
    before = len(unreached_houses(s.M))
    changed = dropped = done = 0
    settled = False
    while done < rounds and not settled:
        done += 1
        n = sum(step(s) for step in STEPS)
        changed += n
        settled = not n
    # (feature 297, research R12: later rounds asking the law and running only the steps for what it named broken were measured
    # SLOWER on two of three pool maps - the law asked each round cost more than the steps it skipped - and were withdrawn)
    if not settled or unsettled(s.M, memo_ground(s, "worked", worked_ground)):
        dropped = last_resort(s)
    # ...AND NO HOUSE OR RESERVED FIELD IS SHIPPED UNREACHED, whichever way the settle ended (ways W01, W03): refused here,
    # so the driver has no unreached house to record (`meta.roll_failures`, deleted with its writer)
    refuse_unreached(s.M)
    return {
        "rounds": done,
        "seconds": round(time.perf_counter() - t0, 3),
        "changed": changed,
        "dropped": dropped,
        "unreached_before": before,
        "unreached_after": len(unreached_houses(s.M)),
        "targets_unreached": len(law.unreached_targets(s.M)),
        "field_unreached": law.field_unreached(s.M),
    }
