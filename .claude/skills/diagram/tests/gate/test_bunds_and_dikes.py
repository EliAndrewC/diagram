"""The earth that holds the water in (feature 166): what is left of it after feature 287.

Feature 166 carried nine rules here that the retired battery re-measured on every finished map. Feature 287 moved eight
of them into their placers, each with a unit test on constructed input that includes the violating case, and retired the
tests that re-read them on a finished map (specs/287-placer-guarantees/research.md R8): the bund beside the supply and
across the collector (`seams/close.py:hold_ring_rules`, `tests/waterfields/test_ring_guarantees.py`), the bead on
visible ground and two beads a segment (`fields/comb.py:settle_beads`, `waterfields/carve.py:bead_runs`), the tract's
row direction (`waterfields/hem.py`, `tests/waterfields/test_furrows.py`), and the dike's earthwork, keep-out and gaps
(`land/dikes.py`, `hamletgen/water/polder.py:gaps_for_courses`, `hamletgen/sink.py:breaches_any_dike`).

KEPT, because no placer guarantees it yet: `waterward_strips_run_off_the_frame`. `hamletgen/frame.py:waterward_to_the_frame`
extends the strip to the decided view but never re-judges it; where the band has no open ground nothing is added, so a
strip can still stop inside the frame.
"""

from __future__ import annotations

import pytest

from tests import rolls
from tests.gate import _pool

KUWABATA = rolls.KUWABATA


@pytest.fixture(scope="module")
def polder():
    return _pool.rolled_map(KUWABATA)


def test_the_waterward_reed_strip_runs_off_the_frame(polder) -> None:
    """`waterward_strips_run_off_the_frame`. On the waterward side the map shows the edge of a bigger
    water than it draws, and the reed fringe along it must run OFF the picture. Cut to a band that stops
    inside the frame, it gives the reader a straight line where wild water stops being wild - a lake with
    a ruled edge.

    The rule exists because the fix for an earlier defect introduced this one: the strip was changed from
    "drawn to the canvas edge" to a fixed depth band, and a band can end inside the view."""
    _plan, M = polder
    faces = M["meta"].get("waterward") or []
    view = M["meta"].get("view")
    strips = [m for m in (M.get("marshes") or []) if m.get("role") == "waterside" and m.get("poly")]
    assert faces and view and strips, "the roll declares no waterward face, view or reed strip, so this rule would judge nothing"
    vx0, vy0, vw, vh = (float(v) for v in view)
    short = []
    for m in strips:
        xs = [float(q[0]) for q in m["poly"]]
        ys = [float(q[1]) for q in m["poly"]]
        reach = {"W": min(xs) <= vx0, "E": max(xs) >= vx0 + vw, "N": min(ys) <= vy0, "S": max(ys) >= vy0 + vh}
        if not any(reach[f] for f in faces if f in reach):
            short.append((round(min(xs)), round(min(ys))))
    assert not short, f"waterside reed strip(s) stop inside the frame: {short[:4]}"
