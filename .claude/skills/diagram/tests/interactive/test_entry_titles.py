"""Every title a modal's `Entry:` quotes names a section that exists (feature 292, the GM, 2026-10-01: *"I don't want to
leave those links broken now that we have changed and remade these sections"*).

`research_questions` lists a modal's references from the titles its `Entry:` quotes, and a quoted title that matches no
heading simply drops out of the list - so a modal whose other titles still resolve kept passing
`test_every_class_entry_resolves`, its stale title invisible. The sweep folded some 660 sections into 239 topics and
renamed nearly every heading; this test holds each quoted title, not just each entry.
"""

from __future__ import annotations

import os

from l7r.diagram.interactive.classes import CLASSES
from l7r.diagram.interactive.compound_kinds import COMPOUND_CLASSES
from l7r.diagram.interactive.sources import _ENTRY_FILE, RESEARCH_DIR, _entry_headings, _names, _parsed


def stale_titles(entry: str, research_dir: str = RESEARCH_DIR) -> list[str]:
    """The quoted titles of an entry that name no heading on any page the entry names."""
    files = _ENTRY_FILE.findall(entry)
    heads = [h for f in files for h, _b, _a in _parsed(os.path.join(research_dir, f))]
    return [q for q in _entry_headings(entry) if not any(_names(h, q) for h in heads)]


def test_every_quoted_title_of_every_modal_names_a_section() -> None:
    bad = {k: s for k, fc in {**CLASSES, **COMPOUND_CLASSES}.items() if (s := stale_titles(fc.entry))}
    assert bad == {}, f"{len(bad)} modal(s) quote a title no section carries: {bad}"


def test_the_check_sees_a_stale_title() -> None:
    entry = "research/homesteads.html - 'Groves of trees around farmhouses (yashikirin)', 'A heading that is not there'"
    assert stale_titles(entry) == ["A heading that is not there"]
