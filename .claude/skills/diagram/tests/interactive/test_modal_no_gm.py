"""No map modal shows a ruling of the GM's (feature 292, FR-014; the GM, 2026-09-29: *"We should not have anything like
this in our research writeup ... it is okay to capture my rulings in our checked-in repository for your own
understanding ... you could keep it by having it be hidden. Like, this is in an HTML comment ... when explaining this to
a human reading this later, you should not refer to this as a GM ruling. Rather, you should describe it the way this
project has chosen to render the variety of settlements that we know existed historically."*).

A modal IS its class's docstring (feature 189), so its visible text is every docstring field a reader sees. A ruling,
its date and its words belong in a `#` comment above the class, which the page never shows; the visible text says what
the decision is, as this project's choice. The setting's own notes are "the setting's notes", not the GM's.
"""

from __future__ import annotations

import re

from l7r.diagram.interactive.classes import CLASSES
from l7r.diagram.interactive.compound_kinds import COMPOUND_CLASSES

_GM = re.compile(r"\bGM\b")


def visible_gm(text: str) -> list[str]:
    """Each sentence of a modal's visible text that names the GM."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if _GM.search(s)]


def _visible(fc: object) -> str:
    return " ".join(str(getattr(fc, f, "") or "") for f in ("what", "why", "label_note", "caveat", "name"))


def test_no_modal_shows_a_ruling_of_the_gm() -> None:
    bad = {k: visible_gm(_visible(fc)) for k, fc in {**CLASSES, **COMPOUND_CLASSES}.items() if visible_gm(_visible(fc))}
    assert bad == {}, f"{len(bad)} modal(s) name the GM in visible text: {bad}"


def test_the_check_sees_the_gm_and_not_a_word_containing_it() -> None:
    assert visible_gm("The yard lines up with its house. The GM ruled that it does.") == ["The GM ruled that it does."]
    assert visible_gm("A GMT-like word, a SIGMA, a programmed figure.") == []
