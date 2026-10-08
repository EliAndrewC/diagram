"""What a hamlet's map must contain (feature 166): `all_ink_is_ruled_on`.

KEPT through feature 287 because no single placer owns it: every layer's ink must carry a class, so it is a property of
the finished drawing as a whole (the census at `settlement/finish.py`). Its sibling `hamlet_has_no_headman` was retired
by feature 287 - `settlement/rolling/place.py:PlacerMixin.headman` refuses the role on a hamlet
(`tests/settlement/test_rolling.py::test_a_hamlet_scale_map_can_draw_no_headman`; specs/287-placer-guarantees/research.md R8).
"""

from __future__ import annotations

import pytest

from tests import rolls
from tests.gate import _pool

SPEC = rolls.REFERENCE  # the pool's brief (feature 215)


@pytest.fixture(scope="module")
def rolled():
    return _pool.rolled_map(SPEC)


def test_every_mark_on_the_map_has_been_ruled_on(rolled) -> None:
    """`all_ink_is_ruled_on`. The interactive map owes its reader an answer for every feature they can
    click: what it is, why it is there, and whether that is accurate, a deliberate deviation, a map drawing convention, or a guess.
    A glyph drawn with no class has no answer, and the reader who clicks it gets silence - which is worse
    than an admitted guess, because it looks like the map simply has nothing to say.

    So the rule is not "most ink is classified". Every emit site either carries a class key, or is ruled
    OUT explicitly (`cls="-"` with a row saying why it is not highlighted). Both are rulings; only
    unruled ink is a failure, and it is a failure that arrives silently whenever a new glyph is added."""
    _plan, M = rolled
    assert M["meta"].get("generated_by") == "hamletgen", "this rule is about the scripted path's own ink"
    unclassed = list(M.get("unclassed_ink") or [])
    unregistered = [f"unregistered class {k!r}" for k in (M.get("unregistered_classes") or [])]
    assert M.get("ink_classes"), "the roll recorded no ink classes at all, so this rule would pass on an empty page"
    assert not (unclassed + unregistered), f"ink nobody ruled on: {(unclassed + unregistered)[:3]}"
