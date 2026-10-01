"""`record/confusables.py` - *Not to be confused with:* (feature 292, FR-016; the GM, 2026-09-29: a section a reader
could mistake for another opens with the list, each entry the other section's title, linked, and the record's
definition of it; the pairs are data, always two-way). Since feature 303 a pair names question pages by file."""

from __future__ import annotations

import json
import pathlib
import re

import pytest

from l7r.diagram.interactive.record import confusables, store
from l7r.diagram.interactive.record import questions as qs
from l7r.diagram.interactive.sources import RESEARCH_DIR, record_text
from tests import _flat_record as fr


def _record(tmp: pathlib.Path, pairs: list[dict[str, str]] | None = None) -> pathlib.Path:
    rec = fr.write(tmp)
    fr.edit(rec, "0003-rows.html", "<p>Shops in a row.", '<!-- a session note. With a full stop. -->\n<p>Shops in a row.<sup class="fn" data-note="k"></sup> Then more.')
    (rec / "questions" / "0005-bare.html").write_text('<h2 id="bare">No opening</h2>\n<!-- tags: subject=ways; setting=city; level=detail -->\n<ul><li>only bullets</li></ul>\n', encoding="utf-8")
    if pairs is not None:
        (rec / confusables.DATA).write_text(json.dumps(pairs), encoding="utf-8")
    return rec


def test_one_pair_puts_an_entry_under_both_sections_each_linking_the_other(tmp_path: pathlib.Path) -> None:
    """Declared once, listed twice: each entry is the OTHER section's title, linked by its file, and the first sentence
    of the other section's opening - its footnotes, tags and comments dropped; a page no pair touches is untouched."""
    rec = _record(tmp_path)
    record = qs.load(str(rec))
    pairs = confusables.load(str(rec))
    assert pairs == [confusables.Pair("0001-lanes.html#lanes", "0003-rows.html#rows")]
    assert confusables.unresolved(pairs, record) == []
    page = confusables.write('<h2 id="lanes">Lanes</h2>\n<p>x</p>', "0001-lanes.html", pairs, record)
    assert '<h2 id="lanes">Lanes</h2>\n<div class="confusables"><p><em>Not to be confused with:</em></p>' in page
    assert '<li><a href="0003-rows.html">Rows</a> - Shops in a row.</li>' in page
    other = confusables.write('<h2 id="rows">Rows</h2>\n<p>y</p>', "0003-rows.html", pairs, record)
    assert '<li><a href="0001-lanes.html">Lanes</a> - A lane is narrow.</li>' in other
    assert confusables.write("<p>z</p>", "0002-bridges.html", pairs, record) == "<p>z</p>"
    assert confusables.write('<h2 id="other">o</h2>', "0001-lanes.html", pairs, record) == '<h2 id="other">o</h2>', "a missing target is left to `unresolved`"


def test_a_section_with_no_opening_paragraph_is_listed_by_title_alone(tmp_path: pathlib.Path) -> None:
    rec = _record(tmp_path, [{"a": "0001-lanes.html#lanes", "b": "0005-bare.html#bare", "why": "w"}])
    page = confusables.write('<h2 id="lanes">G</h2>', "0001-lanes.html", confusables.load(str(rec)), qs.load(str(rec)))
    assert '<li><a href="0005-bare.html">No opening</a></li>' in page
    assert confusables.definition("no heading, no paragraph") == "" and confusables.title("no heading") == ""


def test_a_pair_naming_no_section_or_itself_is_named_and_refuses_the_build(tmp_path: pathlib.Path) -> None:
    rec = _record(
        tmp_path,
        [
            {"a": "0001-lanes.html#lanes", "b": "0001-lanes.html#nowhere", "why": "w"},
            {"a": "0001-lanes.html#lanes", "b": "0001-lanes.html#lanes", "why": "w"},
            {"a": "0001-lanes.html#lanes", "b": "0009-nopage.html#x", "why": "w"},
        ],
    )
    record = qs.load(str(rec))
    assert confusables.unresolved(confusables.load(str(rec)), record) == [
        "`0001-lanes.html#nowhere` (paired with `0001-lanes.html#lanes`) - no such section",
        "`0001-lanes.html#lanes` is paired with itself",
        "`0009-nopage.html#x` (paired with `0001-lanes.html#lanes`) - no such section",
    ]
    with pytest.raises(store.RecordError, match="nowhere"):
        store.page_html(record, record.by_file["0001-lanes.html"], str(rec))


def test_no_data_file_means_no_lists(tmp_path: pathlib.Path) -> None:
    rec = _record(tmp_path)
    (rec / confusables.DATA).unlink()
    record = qs.load(str(rec))
    assert confusables.load(str(rec)) == []
    assert "confusables" not in store.page_html(record, record.by_file["0001-lanes.html"], str(rec))


# ---- the record itself ----


def _data() -> list[dict[str, str]]:
    with open(pathlib.Path(RESEARCH_DIR) / confusables.DATA, encoding="utf-8") as fh:
        return json.load(fh)


def test_every_pair_in_the_record_names_two_different_sections_that_exist_once() -> None:
    """FR-016: a test fails on a pair naming a section that does not exist; and a pair is kept once."""
    data = _data()
    assert data, "the record keeps its confusable pairs"
    assert confusables.unresolved(confusables.load(RESEARCH_DIR), qs.load(RESEARCH_DIR)) == []
    seen = [frozenset((d["a"], d["b"])) for d in data]
    assert len(seen) == len(set(seen)), "a pair listed twice"
    assert all(d.get("why") for d in data), "every pair says what makes the two confusable"


def test_every_page_carries_both_entries_of_every_pair() -> None:
    """Two-way on the pages a reader opens: under each paired section, a link to the other."""
    for d in _data():
        for here, there in ((d["a"], d["b"]), (d["b"], d["a"])):
            file, anchor = here.split("#")
            text = record_text(f"questions/{file}")
            m = re.search(rf'<h2 id="{re.escape(anchor)}">.*?</h2>\n<div class="confusables">(.*?)</div>', text, re.S)
            assert m, f"{here}: no list under its heading"
            assert f'href="{there.split("#")[0]}"' in m.group(1), f"{here}: no entry for {there}"
