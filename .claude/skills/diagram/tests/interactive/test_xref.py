"""`record/xref.py` - the research <-> rendering links the assembly writes (feature 292, GM 2026-09-29: *"the two of
them should definitely link to each other. And I think that linking should be automated rather than something that we
write"*)."""

from __future__ import annotations

import pathlib

import pytest

from l7r.diagram.interactive.record import store, xref
from l7r.diagram.interactive.sources import COLLECTIONS, RESEARCH_DIR, collection_pages


def _record(tmp: pathlib.Path, about: str = "homesteads.html#groves") -> pathlib.Path:
    (tmp / "homesteads").mkdir()
    (tmp / "homesteads" / "010-groves.html").write_text('<h2 id="groves">Groves</h2>\n<p>history</p>\n', encoding="utf-8")
    (tmp / "rendering" / "homesteads").mkdir(parents=True)
    (tmp / "rendering" / "homesteads" / "010-drawn.html").write_text(f'<h2 id="drawn">Drawn</h2>\n<!-- about: {about} -->\n<p>maps</p>\n', encoding="utf-8")
    (tmp / "rendering" / "homesteads" / "_front.html").write_text("<!-- about: nowhere.html#x -->", encoding="utf-8")
    return tmp


def test_one_declaration_links_both_sections_each_to_the_other(tmp_path: pathlib.Path) -> None:
    """The declaration is made once, in the rendering section; the link appears under BOTH headings, each pointing at the
    other, relative to its own page - two-way by construction. A comment in an unprefixed file declares nothing."""
    rec = _record(tmp_path)
    pairs = xref.pairs(str(rec))
    assert pairs == [xref.Pair("rendering/homesteads.html", "drawn", "homesteads.html", "groves")]
    research = xref.link('<h2 id="groves">Groves</h2>\n<p>history</p>\n', "homesteads.html", pairs)
    assert '<h2 id="groves">Groves</h2>\n<p class="xref"><a href="rendering/homesteads.html#drawn">How our maps draw it</a></p>\n<p>history' in research
    rendering = xref.link('<h2 id="drawn">Drawn</h2>\n<!-- about: homesteads.html#groves -->\n', "rendering/homesteads.html", pairs)
    assert '<p class="xref"><a href="../homesteads.html#groves">The history behind it</a></p>' in rendering
    assert xref.link("<p>unrelated</p>", "ways.html", pairs) == "<p>unrelated</p>"
    assert xref.link('<h2 id="other">x</h2>\n', "homesteads.html", pairs) == '<h2 id="other">x</h2>\n', "a missing target is left to `unresolved`"
    assert xref.unresolved(pairs, str(rec)) == []


def test_a_declaration_naming_a_missing_section_is_named_and_refuses_the_build(tmp_path: pathlib.Path) -> None:
    rec = _record(tmp_path, about="homesteads.html#no-such-section")
    bad = xref.unresolved(xref.pairs(str(rec)), str(rec))
    assert bad == ["rendering/homesteads.html: `about: homesteads.html#no-such-section` - no section `no-such-section` on homesteads.html"]
    with pytest.raises(store.RecordError, match="no-such-section"):
        store._cross_linked("<p>page</p>", "homesteads.html", str(rec))
    assert store._cross_linked("<p>page</p>", "ways.html", str(rec)) == "<p>page</p>", "a page no declaration touches is untouched"
    elsewhere = xref.unresolved([xref.Pair("rendering/homesteads.html", "drawn", "ways.html", "x")], str(rec))
    assert elsewhere == ["rendering/homesteads.html: `about: ways.html#x` - no section `x` on ways.html"], "a page with no fragments has no sections"


def test_a_record_with_no_rendering_collection_has_no_pairs(tmp_path: pathlib.Path) -> None:
    assert xref.pairs(str(tmp_path)) == []


def test_the_record_s_collections_are_listed_from_one_place(tmp_path: pathlib.Path) -> None:
    """`sources.COLLECTIONS` is the one list; every reader of the record takes its pages from it."""
    assert COLLECTIONS == ("cities", "rendering")
    for c in COLLECTIONS:
        (tmp_path / c).mkdir()
    (tmp_path / "rendering" / "b.html").write_text("", encoding="utf-8")
    (tmp_path / "cities" / "a.html").write_text("", encoding="utf-8")
    (tmp_path / "cities" / "notes.txt").write_text("", encoding="utf-8")
    assert collection_pages(str(tmp_path)) == ["cities/a.html", "rendering/b.html"]
    assert collection_pages(str(tmp_path / "no-record-here")) == []
    assert "rendering/homesteads.html" in store.record_pages(RESEARCH_DIR)


def test_the_committed_grove_sections_link_each_other() -> None:
    """The pilot's pair, on the committed pages: the research section links its rendering section and back."""
    research = pathlib.Path(RESEARCH_DIR, "homesteads.html").read_text(encoding="utf-8")
    rendering = pathlib.Path(RESEARCH_DIR, "rendering", "homesteads.html").read_text(encoding="utf-8")
    assert 'href="rendering/homesteads.html#how-our-maps-draw-the-groves-around-farmhouses">How our maps draw it' in research
    assert 'href="../homesteads.html#groves-of-trees-around-farmhouses-yashikirin">The history behind it' in rendering
