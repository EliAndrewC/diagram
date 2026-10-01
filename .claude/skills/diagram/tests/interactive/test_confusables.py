"""`record/confusables.py` - *Not to be confused with:* (feature 292, FR-016; the GM, 2026-09-29: a section a reader
could mistake for another opens with the list, each entry the other section's title, linked, and the record's
definition of it; the pairs are data, always two-way)."""

from __future__ import annotations

import json
import pathlib
import re

import pytest

from l7r.diagram.interactive.record import confusables, store
from l7r.diagram.interactive.sources import RESEARCH_DIR


def _record(tmp: pathlib.Path, pairs: list[dict[str, str]] | None = None) -> pathlib.Path:
    (tmp / "homesteads").mkdir()
    (tmp / "homesteads" / "010-groves.html").write_text(
        '<h2 id="groves">Groves of trees (<em>yashikirin</em>)</h2>\n<!-- a session note. With a full stop. -->\n'
        '<p>A farm\'s own wood.<sup class="fn" data-note="k"></sup> It stood on the windward sides.</p>\n', encoding="utf-8")
    (tmp / "cities" / "fabric").mkdir(parents=True)
    (tmp / "cities" / "fabric" / "010-belts.html").write_text('<h2 id="belts">Shelter belts</h2>\n<p>A belt shared by a village</p>\n', encoding="utf-8")
    (tmp / "cities" / "fabric" / "020-bare.html").write_text('<h2 id="bare">No opening</h2>\n<ul><li>only bullets</li></ul>\n', encoding="utf-8")
    data = pairs if pairs is not None else [{"a": "homesteads.html#groves", "b": "cities/fabric.html#belts", "why": "two woods"}]
    (tmp / confusables.DATA).write_text(json.dumps(data), encoding="utf-8")
    return tmp


def test_one_pair_puts_an_entry_under_both_sections_each_linking_the_other(tmp_path: pathlib.Path) -> None:
    """Declared once, listed twice: each entry is the OTHER section's title, linked relative to its own page, and the
    first sentence of the other section's opening - its footnotes, tags and comments dropped; a page no pair touches
    is untouched."""
    rec = str(_record(tmp_path))
    pairs = confusables.load(rec)
    assert pairs == [confusables.Pair("homesteads.html#groves", "cities/fabric.html#belts")]
    assert confusables.unresolved(pairs, rec) == []
    page = confusables.write('<h2 id="groves">Groves</h2>\n<p>x</p>', "homesteads.html", pairs, rec)
    assert '<h2 id="groves">Groves</h2>\n<div class="confusables"><p><em>Not to be confused with:</em></p>' in page
    assert '<li><a href="cities/fabric.html#belts">Shelter belts</a> - A belt shared by a village</li>' in page
    other = confusables.write('<h2 id="belts">Shelter belts</h2>\n<p>y</p>', "cities/fabric.html", pairs, rec)
    assert '<li><a href="../homesteads.html#groves">Groves of trees (yashikirin)</a> - A farm\'s own wood.</li>' in other
    assert confusables.write("<p>z</p>", "ways.html", pairs, rec) == "<p>z</p>"
    assert confusables.write('<h2 id="other">o</h2>', "homesteads.html", pairs, rec) == '<h2 id="other">o</h2>', "a missing target is left to `unresolved`"


def test_a_section_with_no_opening_paragraph_is_listed_by_title_alone(tmp_path: pathlib.Path) -> None:
    rec = str(_record(tmp_path, [{"a": "homesteads.html#groves", "b": "cities/fabric.html#bare", "why": "w"}]))
    page = confusables.write('<h2 id="groves">G</h2>', "homesteads.html", confusables.load(rec), rec)
    assert '<li><a href="cities/fabric.html#bare">No opening</a></li>' in page
    assert confusables.definition("no heading, no paragraph") == "" and confusables.title("no heading") == ""


def test_a_pair_naming_no_section_or_itself_is_named_and_refuses_the_build(tmp_path: pathlib.Path) -> None:
    rec = str(_record(tmp_path, [{"a": "homesteads.html#groves", "b": "homesteads.html#nowhere", "why": "w"},
                                 {"a": "homesteads.html#groves", "b": "homesteads.html#groves", "why": "w"},
                                 {"a": "homesteads.html#groves", "b": "nopage.html#x", "why": "w"}]))
    bad = confusables.unresolved(confusables.load(rec), rec)
    assert bad == ["`homesteads.html#nowhere` (paired with `homesteads.html#groves`) - no such section",
                   "`homesteads.html#groves` is paired with itself",
                   "`nopage.html#x` (paired with `homesteads.html#groves`) - no such section"]
    with pytest.raises(store.RecordError, match="nowhere"):
        store._confusables("<p>page</p>", "homesteads.html", rec)


def test_no_data_file_means_no_lists(tmp_path: pathlib.Path) -> None:
    assert confusables.load(str(tmp_path)) == []
    assert store._confusables("<p>page</p>", "homesteads.html", str(tmp_path)) == "<p>page</p>"


# ---- the record itself ----

def _data() -> list[dict[str, str]]:
    with open(pathlib.Path(RESEARCH_DIR) / confusables.DATA, encoding="utf-8") as fh:
        return json.load(fh)


def test_every_pair_in_the_record_names_two_different_sections_that_exist_once() -> None:
    """FR-016: a test fails on a pair naming a section that does not exist; and a pair is kept once - the same two
    sections either way round are one pair, since one declaration already writes both entries."""
    data = _data()
    assert data, "the record keeps its confusable pairs"
    assert confusables.unresolved(confusables.load(RESEARCH_DIR), RESEARCH_DIR) == []
    seen = [frozenset((d["a"], d["b"])) for d in data]
    assert len(seen) == len(set(seen)), "a pair listed twice"
    assert all(d.get("why") for d in data), "every pair says what makes the two confusable"


def test_every_assembled_page_carries_both_entries_of_every_pair() -> None:
    """Two-way on the pages a reader opens: under each paired section, a link to the other."""
    for d in _data():
        for here, there in ((d["a"], d["b"]), (d["b"], d["a"])):
            page, anchor = here.split("#")
            text = (pathlib.Path(RESEARCH_DIR) / page).read_text(encoding="utf-8")
            m = re.search(rf'<h2 id="{re.escape(anchor)}">.*?</h2>\n<div class="confusables">(.*?)</div>', text, re.S)
            assert m, f"{here}: no list under its heading"
            tpage, tanchor = there.split("#")
            assert f"#{tanchor}\"" in m.group(1), f"{here}: no entry for {there}"
