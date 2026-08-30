"""Two rules about what a hamlet's map may and must contain (feature 166).

Carries `hamlet_has_no_headman` and `all_ink_is_ruled_on`.

THESE TWO ARE NOT GEOMETRY, WHICH IS WHY THEY SHARE A MODULE. One is a fact about the settlement's
society and the other is a fact about the drawing's completeness, and neither is a clearance any placer
holds. They are properties of the FINISHED map, and the spec's destination list allows exactly that.
"""

from __future__ import annotations

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache

SPEC = hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")


@pytest.fixture(scope="module")
def rolled():
    return rollcache.hamlet(SPEC)


def test_a_hamlet_has_no_headman_of_its_own(rolled) -> None:
    """`hamlet_has_no_headman`. A hamlet is not an administrative unit. The village headman (shoya /
    nanushi) answers for the VILLAGE - it is the village that is assessed, that owes the tax rice, and
    that holds the land register - and a hamlet is a cluster of houses inside one. Drawing a headman's
    house in a hamlet promotes it to a village on the sheet, and the reader takes the settlement for
    something it is not.

    The assertion runs on the whole house list rather than on a count, so a house that acquires the role
    under a new name is still caught."""
    _plan, M = rolled
    assert M["meta"].get("scale") == "hamlet", "this roll is not a hamlet, so the rule does not apply to it"
    houses = M.get("houses") or []
    assert houses, "the roll seated no house, so this rule would judge nothing"
    headmen = [(round(h["x"]), round(h["y"])) for h in houses if h.get("role") == "headman"]
    assert not headmen, f"a hamlet has no peasant headman of its own, but one is drawn at {headmen}"


def test_every_mark_on_the_map_has_been_ruled_on(rolled) -> None:
    """`all_ink_is_ruled_on`. The interactive map owes its reader an answer for every feature they can
    click: what it is, why it is there, and whether that is accurate, a deliberate deviation, or a guess.
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
