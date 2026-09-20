"""Numbers nobody types (feature 258, stage 3; spec FR-017 to FR-022, SC-004, SC-006).

On plain strings, before any of the record moves: a note is named, the numbers are allocated in the
order the references appear, and the two defects the record carries today - a reference with no id, a
reference id used twice - cannot be written by construction.
"""

from __future__ import annotations

import pytest

from l7r.diagram.interactive.record.notes import (
    NoteError,
    allocate,
    derive_key,
    merge,
    notes_of,
    number_references,
    render_note,
)

PAGE = (
    '<p>Rape never stands beside rice.<sup class="fn" data-note="aburana"></sup></p>\n'
    '<p>The dike is the pond\'s own spoil.<sup class="fn" data-note="gmrb-sangji"></sup> '
    'Dredged in the seventh month.<sup class="fn" data-note="gmrb-sangji"></sup></p>\n'
    '<p>Tea sits on the lower slope.<sup class="fn" data-note="fortune"></sup></p>\n'
)
NOTES = {"fortune": "Fortune, 1843 - the lower slopes", "aburana": "ja.wikipedia - the rotation", "gmrb-sangji": "Guangming Daily - dug and heaped"}


def test_numbers_follow_the_reader_not_the_author() -> None:
    """FR-019: allocation is by the order references APPEAR, whatever order the notes were written in."""
    _, placed = allocate(PAGE, NOTES, "water")
    assert [(p.key, p.number) for p in placed] == [("aburana", 1), ("gmrb-sangji", 2), ("fortune", 3)]


def test_a_note_referenced_twice_gets_one_number_and_two_ids() -> None:
    """FR-021, and the fix for the 2 pages that carry a duplicated reference id today (R4)."""
    _, placed = allocate(PAGE, NOTES, "water")
    numbered = number_references(PAGE, placed, "citations/water.html")
    assert numbered.count('id="fnref-2"') == 1 and numbered.count('id="fnref-2-2"') == 1
    ids = [m for m in numbered.split('id="')[1:]]
    assert len(ids) == len({i.split('"')[0] for i in ids}), "every id on the page is unique"


def test_every_reference_carries_an_id_so_a_back_link_can_return() -> None:
    """The other defect (R5): 4 references in the record carry no id at all."""
    _, placed = allocate(PAGE, NOTES, "water")
    numbered = number_references(PAGE, placed, "citations/water.html")
    assert numbered.count("<sup class=\"fn\">") == 4
    assert numbered.count('id="fnref-') == 4


def test_the_back_link_points_at_the_first_reference() -> None:
    _, placed = allocate(PAGE, NOTES, "water")
    note = render_note(placed[1], "../water.html")
    assert 'href="../water.html#fnref-2"' in note and 'id="fn-2"' in note


def test_a_reference_to_a_key_no_note_defines_is_refused() -> None:
    with pytest.raises(NoteError, match="`fortune`, which no note"):
        allocate(PAGE, {k: v for k, v in NOTES.items() if k != "fortune"}, "water")


def test_a_note_nothing_references_is_refused_rather_than_dropped() -> None:
    with pytest.raises(NoteError, match="referenced nowhere"):
        allocate(PAGE, {**NOTES, "orphan": "nobody cites this"}, "water")


def test_a_key_defined_twice_is_refused_in_one_file_and_across_two() -> None:
    with pytest.raises(NoteError, match="defined twice in one file"):
        notes_of('<li data-note="a">one</li>\n<li data-note="a">two</li>', "water/010-x.notes.html")
    with pytest.raises(NoteError, match="unique within its page"):
        merge([("010-x.notes.html", {"a": "one"}), ("020-y.notes.html", {"a": "two"})])


def test_a_key_that_is_not_lower_case_kebab_is_refused() -> None:
    with pytest.raises(NoteError, match="not a note key"):
        notes_of('<li data-note="Fei_1939">x</li>', "water/010-x.notes.html")


def test_a_note_is_read_with_its_body_verbatim() -> None:
    body = '<a href="http://x"><code>fei-1939</code></a> - 「a quotation」 (the gloss)'
    assert notes_of(f'<li data-note="fei-1939">{body}</li>') == {"fei-1939": body}


def test_the_splitter_derives_a_key_from_the_source_and_then_an_ordinal() -> None:
    """R5: 1,524 notes lead with a source key, a page repeats one 635 times, 326 lead with none."""
    taken: set[str] = set()
    for want, source in [("fei-1939", "fei-1939"), ("fei-1939-2", "fei-1939"), ("fei-1939-3", "fei-1939")]:
        got = derive_key(source, "how-deep-the-water-stands", taken)
        assert got == want
        taken.add(got)
    assert derive_key(None, "how-deep-the-water-stands", taken) == "how-deep-the-water-stands"
    taken.add("how-deep-the-water-stands")
    assert derive_key(None, "how-deep-the-water-stands", taken) == "how-deep-the-water-stands-2"
