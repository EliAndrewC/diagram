"""Every question a modal's `Entry:` names exists (feature 292, the GM, 2026-10-01: *"I don't want to leave those links
broken now that we have changed and remade these sections"*).

`research_questions` lists a modal's references from the questions its `Entry:` names, and one that names no fragment
simply drops out of the list - so a modal whose other questions still resolve kept passing
`test_every_class_entry_resolves`, its stale pointer invisible. This test holds each named question, not just each
entry. Since feature 301 an `Entry:` names FRAGMENTS (`research/<page>/<prefix>-<heading id>.html`), so the check is
that each named file is there.
"""

from __future__ import annotations

import os

from l7r.diagram.interactive.classes import CLASSES
from l7r.diagram.interactive.compound_kinds import COMPOUND_CLASSES
from l7r.diagram.interactive.sources import RESEARCH_DIR, entry_fragments


def stale_titles(entry: str, research_dir: str = RESEARCH_DIR) -> list[str]:
    """The questions an entry names that are not in the record."""
    return [f"{d}/{n}" for d, n in entry_fragments(entry) if not os.path.isfile(os.path.join(research_dir, d, n))]


def test_every_named_question_of_every_modal_exists() -> None:
    bad = {k: s for k, fc in {**CLASSES, **COMPOUND_CLASSES}.items() if (s := stale_titles(fc.entry))}
    assert bad == {}, f"{len(bad)} modal(s) name a question the record does not hold: {bad}"


def test_the_check_sees_a_stale_question() -> None:
    entry = "research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html, research/homesteads/999-not-there.html"
    assert stale_titles(entry) == ["homesteads/999-not-there.html"]
