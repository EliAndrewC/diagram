"""`record/originals.py` and its place in the assembly - a translated quotation's original, stored apart (feature 292, GM
2026-09-29: *"can we store the original text separately as well? ... the original text should be collapsed by
default"*)."""

from __future__ import annotations

import pathlib

import pytest

from l7r.diagram.interactive.record import originals, store
from l7r.diagram.tools import record_asset

NOTE = (
    '<li data-note="k">「A」 (translated from the Japanese by this project; original: 「甲「乙」丙」)</li>\n'
    '<li data-note="j">「B」 and 「C」 (translated from the Chinese by this project; original: 「丁」 and original: 「戊」); '
    "(the source's own English)</li>\n"
    '<li data-note="h">"plain English" (the source\'s own English)</li>\n'
)


def test_split_moves_each_original_run_out_and_restore_puts_it_back_exactly() -> None:
    """A run is `original: 「...」` with the originals joined to it; nested brackets close at depth zero. The notes keep a
    placeholder; restoring bare reproduces the bytes, restoring wrapped marks each run for the page's toggle."""
    notes, stored = originals.split(NOTE)
    assert "甲" not in notes and "丁" not in notes and "戊" not in notes, "no original is left in the notes a check reads"
    assert notes.count('<span class="orig" data-orig="') == 2
    assert stored == '<li data-orig="k#1">original: 「甲「乙」丙」</li>\n<li data-orig="j#1">original: 「丁」 and original: 「戊」</li>\n'
    assert originals.restore(notes, stored, wrapped=False) == NOTE
    assert '<span class="orig">original: 「甲「乙」丙」</span>)' in originals.restore(notes, stored)
    assert originals.has_placeholder(notes) and not originals.has_placeholder(NOTE)


def test_a_new_inline_original_is_numbered_after_the_note_s_and_a_moved_one_stays() -> None:
    notes, stored = originals.split(NOTE)
    grown = notes.replace("(the source's own English)</li>\n<li data-note=\"h\">", "; 「D」 (translated from the Japanese by this project; original: 「己」)</li>\n<li data-note=\"h\">")
    again, stored2 = originals.split(grown, stored)
    assert stored2.startswith(stored) and stored2.endswith('<li data-orig="j#2">original: 「己」</li>\n')
    assert originals.split(again, stored2) == (again, stored2), "nothing inline is left to move"


def test_half_width_brackets_nest_and_an_unclosed_bracket_ends_the_scan() -> None:
    """water/620 quotes a source whose own inner brackets are half-width - `「表１ 玉川上水の分水(「上水記｣ から）」`."""
    text = "x (translated from the Japanese by this project; original: 「表(「上水記｣ から)」)"
    assert originals.units(text) == [(text.index("original"), len(text) - 1)]
    assert originals.units("original: 「never closed") == []


def test_a_placeholder_with_no_stored_original_refuses() -> None:
    with pytest.raises(KeyError, match="k#9"):
        originals.restore('<li data-note="k">x <span class="orig" data-orig="k#9"></span></li>', "")


def _page(tmp: pathlib.Path, notes: str, originals_file: str | None = None) -> pathlib.Path:
    (tmp / "p").mkdir()
    (tmp / "p.html").write_text("", encoding="utf-8")
    (tmp / "p" / "_front.html").write_text("<main>\n", encoding="utf-8")
    (tmp / "p" / "_tail.html").write_text("</main>\n", encoding="utf-8")
    (tmp / "p" / "010-q.html").write_text('<h2 id="q">Q</h2>\n<p>x<sup class="fn" data-note="k"></sup></p>\n', encoding="utf-8")
    (tmp / "p" / "010-q.notes.html").write_text(notes, encoding="utf-8")
    if originals_file is not None:
        (tmp / "p" / "010-q.originals.html").write_text(originals_file, encoding="utf-8")
    return tmp


def test_make_record_moves_an_inline_original_and_the_check_names_it(tmp_path: pathlib.Path) -> None:
    rec = _page(tmp_path, '<li data-note="k">「A」 (translated from the Japanese by this project; original: 「甲」)</li>\n')
    assert store.split_originals(str(rec), write=False) == ["p/010-q.notes.html"]
    assert "original: 「甲」" in (rec / "p" / "010-q.notes.html").read_text(encoding="utf-8"), "a check writes nothing"
    assert store.split_originals(str(rec)) == ["p/010-q.notes.html"]
    assert (rec / "p" / "010-q.originals.html").read_text(encoding="utf-8") == '<li data-orig="k#1">original: 「甲」</li>\n'
    assert store.split_originals(str(rec)) == [], "moved once"
    (rec / "nofragments.html").write_text("", encoding="utf-8")
    assert store.split_originals(str(rec)) == [], "a page with no fragment directory is passed over"
    assert '<span class="orig">original: 「甲」</span>' in store.read_notes("p.html", str(rec))["k"]


def test_a_placeholder_without_its_originals_file_or_its_entry_refuses_the_assembly(tmp_path: pathlib.Path) -> None:
    held = '<li data-note="k">「A」 (translated from the Japanese by this project; <span class="orig" data-orig="k#1"></span>)</li>\n'
    rec = _page(tmp_path, held)
    with pytest.raises(store.RecordError, match="010-q.originals.html is missing"):
        store.read_notes("p.html", str(rec))
    (rec / "p" / "010-q.originals.html").write_text("", encoding="utf-8")
    with pytest.raises(store.RecordError, match="no original stored for `k#1`"):
        store.read_notes("p.html", str(rec))


def test_the_record_tool_moves_originals_before_it_writes_and_its_check_reports_one_inline(tmp_path: pathlib.Path, capsys) -> None:  # noqa: ANN001
    rec = _page(tmp_path, '<li data-note="k">「A」 (translated from the Japanese by this project; original: 「甲」)</li>\n')
    assert record_asset._check(str(rec)) == 1
    assert "an original still inline" in capsys.readouterr().err
    record_asset._write("", str(rec))
    assert "moved the originals of 1 notes file(s)" in capsys.readouterr().out
