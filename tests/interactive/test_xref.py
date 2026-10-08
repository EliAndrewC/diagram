"""`record/xref.py` - the research <-> drawing links the build writes (feature 292, GM 2026-09-29: *"the two of them
should definitely link to each other. And I think that linking should be automated rather than something that we
write"*). Since feature 303 the pairing is the stem, and a second drawing page's `about:`."""

from __future__ import annotations

import pathlib

from l7r.diagram.interactive.record import questions as qs
from l7r.diagram.interactive.record import xref
from l7r.diagram.interactive.sources import RESEARCH_DIR, github_anchor, heading_text, page_text, record_text
from tests import _flat_record as fr


def test_the_stem_and_an_about_pair_the_pages_and_each_links_the_other(tmp_path: pathlib.Path) -> None:
    record = qs.load(str(fr.write(tmp_path)))
    pairs = xref.pairs(record)
    assert pairs == [xref.Pair("0001-lanes.drawing.html", "0001-lanes.html"), xref.Pair("0004-wide-lanes.drawing.html", "0001-lanes.html")]
    lanes = record.by_file["0001-lanes.html"]
    out = xref.link(lanes.text, lanes, pairs)
    assert '<h2 id="lanes"><span class="xref"><a href="0001-lanes.drawing.html">How it\'s drawn</a> - <a href="0004-wide-lanes.drawing.html">How it\'s drawn</a></span>Lanes</h2>' in out
    wide = record.by_file["0004-wide-lanes.drawing.html"]
    assert '<span class="xref"><a href="0001-lanes.html">The history behind it</a></span>' in xref.link(wide.text, wide, pairs)
    rows = record.by_file["0003-rows.html"]
    assert xref.link(rows.text, rows, pairs) == rows.text, "a page with no pair is untouched"


def test_a_lone_drawing_question_with_its_own_tags_pairs_with_nothing(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    fr.edit(rec, "0004-wide-lanes.drawing.html", "<!-- about: 0001-lanes -->", "<!-- tags: subject=ways; setting=city; level=detail -->")
    assert xref.pairs(qs.load(str(rec))) == [xref.Pair("0001-lanes.drawing.html", "0001-lanes.html")]


def test_the_committed_grove_pages_link_each_other() -> None:
    """The pilot's pair, on the real record: the research page links its drawing page and back."""
    record = qs.load(RESEARCH_DIR)
    grove = next(p for p in record.pages("research") if p.heading_id == "groves-of-trees-around-farmhouses-yashikirin")
    research = record_text(f"questions/{grove.file}")
    drawing = record_text(f"questions/{grove.stem}.drawing.html")
    assert f'href="{grove.stem}.drawing.html">How it\'s drawn' in research
    assert f'href="{grove.file}">The history behind it' in drawing


def test_a_heading_s_text_does_not_include_its_link() -> None:
    """The link is inside the heading so it can sit on the heading's line; a heading's TEXT - the anchor rule, the
    question a modal lists - never includes it."""
    h = '<span class="xref"><a href="0001-x.drawing.html">How it\'s drawn</a></span>Groves of trees (yashikirin)'
    assert page_text(h) == heading_text(h) == "Groves of trees (yashikirin)"
    assert github_anchor(heading_text(h)) == "groves-of-trees-yashikirin"
