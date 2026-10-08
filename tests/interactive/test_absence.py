"""`record/absence.py` - an absence note's opening words, kept in one place (feature 292, GM 2026-09-29: *"the
replacement text for 'no publicly available source' should be stored in a single place so that if we update it later we
are updating a single line of text"*)."""

from __future__ import annotations

import pathlib

from l7r.diagram.interactive.citations import ABSENCE, footnote_form
from l7r.diagram.interactive.record import absence, store
from l7r.diagram.interactive.sources import RESEARCH_DIR


def test_the_marker_is_shown_as_the_lead_and_a_reader_of_markup_gets_it_back() -> None:
    written = "no publicly readable source<!-- searched 2026-09-29: x --> None counts them."
    shown = absence.render(written)
    assert shown.startswith(f'<span class="sep">no publicly readable source</span><span class="absence-lead">{absence.LEAD}</span>')
    assert absence.unrender(shown) == written
    assert absence.render("「A」 (translated)") == "「A」 (translated)", "any other note is left alone"
    assert absence.render("  " + written).startswith("  <span"), "leading space is kept"


def test_the_new_form_and_the_old_are_both_absence_notes_and_so_is_the_rendered_page() -> None:
    new = "no publicly readable source<!-- searched 2026-09-29: x --> None counts them."
    old = "no publicly readable source (searched 2026-09-06: x)"
    assert ABSENCE.match(new) and ABSENCE.match(old)
    assert footnote_form(new, set()) == footnote_form(absence.render(new), set()) == "absence"
    assert footnote_form(absence.render(old), set()) == "absence"


def test_the_lead_is_written_once_and_every_rendered_note_carries_it() -> None:
    """The sentence lives in `absence.LEAD` alone: no hand-authored file of the record writes it, and the assembled
    grove page shows it for each of its absence notes."""
    record = pathlib.Path(RESEARCH_DIR)
    hand = [p for p in record.rglob("[0-9]*.html") if "site" not in p.parts and absence.LEAD in p.read_text(encoding="utf-8")]
    assert hand == [], hand
    grove = next(f for f in (record / "questions").glob("*-groves-of-trees-around-farmhouses-yashikirin.html"))
    notes = "".join(store.page_notes(grove.name).values())
    assert notes.count(absence.LEAD) == notes.count('<span class="sep">no publicly readable source</span>') > 0
