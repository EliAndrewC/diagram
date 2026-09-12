"""Feature 211 (GM 2026-09-07): the notes live on a CITATIONS PAGE, and what the two pages share is DERIVED.

The GM: *"All of the citations at the end of a research file can be moved into the citations document. We should be
careful to avoid duplicating content ... move our citations into a third location that can be loaded by both of the
different pages."* And of the works list at the top: *"we do not want to have multiple different write ups of a single
paper ... drawing from a single data source."* What a test can hold: every research page has its citations page and
loads its derived script; every committed script and every works section equals its derivation (so a note is typed
once, on the citations page, and a write-up once, in the registry); every cited key's entry carries both write-ups;
the reader and the derivation behave on plain strings. What only the `source-applicability` agent can hold - whether
a write-up is honest about the work's era, place and kind - is its job, before a source lands."""

from __future__ import annotations

import pathlib

import pytest

from l7r.diagram.interactive.citations import (
    WORKS_CLOSE,
    WORKS_OPEN,
    citations_page,
    cited_keys,
    derive,
    note_for_script,
    notes,
    rel_to_research,
    research_pages,
    script_js,
    script_path,
    with_works,
    works_html,
)
from l7r.diagram.interactive.sources import RESEARCH_DIR, WHAT_LABEL, WHY_LABEL, registry_entries


def _read(rel: str) -> str:
    return pathlib.Path(RESEARCH_DIR, rel).read_text(encoding="utf-8")


def test_the_record_s_pages_are_found_and_the_registry_and_citations_pages_are_not() -> None:
    pages = research_pages()
    assert "homesteads.html" in pages and "cities/fabric.html" in pages
    assert "SOURCES.html" not in pages and not any(p.startswith("citations/") for p in pages)
    assert len(pages) == 19, pages  # 15 pages until feature 229 added settlements, ways, presentation and cities/sizing


def test_the_paths_beside_a_research_page() -> None:
    assert citations_page("homesteads.html") == "citations/homesteads.html"
    assert citations_page("cities/fabric.html") == "citations/cities/fabric.html"
    assert script_path("cities/fabric.html") == "citations/cities/fabric.js"
    assert rel_to_research("citations/homesteads.html") == "../" and rel_to_research("citations/cities/fabric.html") == "../../"


@pytest.mark.parametrize("page", research_pages())
def test_every_research_page_has_a_citations_page_and_loads_its_derived_script(page: str) -> None:
    text = _read(page)
    assert pathlib.Path(RESEARCH_DIR, citations_page(page)).exists(), f"{page}: no citations page"
    down = "../" * page.count("/")
    tag = f'<script src="{down}{script_path(page)}" defer></script>'
    record = f'<script src="{down}assets/record.js" defer></script>'
    assert 0 <= text.find(tag) < text.find(record), f"{page}: loads its citations script before record.js (both deferred, so document order is run order)"
    assert '<section class="footnotes">' not in text, f"{page}: the notes' bytes are on the citations page, not here"
    assert f'<a href="{down}{citations_page(page)}">' in text, f"{page}: links its citations page where the notes were"


@pytest.mark.parametrize("page", research_pages())
def test_the_committed_script_and_works_section_are_the_derivation(page: str) -> None:
    """`make citations` writes both; a note or a write-up edited without the run fails here with the command."""
    js, html, missing = derive(page)
    assert _read(script_path(page)) == js, f"{script_path(page)} is stale against its citations page - run `make citations`"
    assert _read(citations_page(page)) == html, f"{citations_page(page)}: the works section is stale against SOURCES.html - run `make citations`"
    assert not missing, f"{page}: cited keys whose registry entry has no `{WHAT_LABEL}` / `{WHY_LABEL}` write-up (feature 211: a source is not cited without one): {missing}"


def test_every_citations_page_carries_its_works_and_its_notes_in_that_order() -> None:
    """The GM: the works list comes *"at the top of the citations page, before we begin listing the number of citations"*."""
    for page in research_pages():
        text = _read(citations_page(page))
        assert 0 < text.find(WORKS_OPEN) < text.find(WORKS_CLOSE) < text.find('<section class="footnotes">'), page
        assert '<a href="' + "../" * citations_page(page).count("/") + page + '">' in text, f"{citations_page(page)}: links back to its research page"
        # NON-VACUITY, and what it cannot ask of a page with nothing to cite (feature 229): a research page of
        # map drawing conventions - `presentation.html` - rests on the GM's rulings and this project's own
        # measurements, so it carries no reference and its citations page carries no note. A page that DOES
        # reference something must have the note behind it.
        if '<sup class="fn">' in _read(page):
            assert notes(text), f"{citations_page(page)}: no notes (non-vacuity)"


def test_the_works_section_names_every_cited_work_once_in_order_of_first_citation() -> None:
    text = _read("citations/homesteads.html")
    keys = cited_keys(notes(text))
    assert keys[0] == "kashima-kainyo-1987" and len(keys) == len(set(keys)) and len(keys) > 30
    works = text[text.find(WORKS_OPEN) : text.find(WORKS_CLOSE)]
    heads = [line for line in works.splitlines() if line.startswith('<h3 id="work-')]
    assert [h.split('"')[1][len("work-") :] for h in heads] == keys
    entries = registry_entries()
    assert f"<p><em>{WHAT_LABEL}</em> {entries['wang-ochiai-2022']['what']}</p>" in works, "the registry's own text, verbatim (one write-up, derived)"
    assert works.count("<p><em>What it is:</em>") == len(keys)


def test_a_work_cited_from_two_pages_has_one_write_up_and_both_pages_show_it() -> None:
    """Spec SC-004: the hand-authored paragraph is in the registry; every other occurrence is between the markers."""
    # `visit-toyama-sankyoson` is cited from homesteads and vegetation (the spec's example pair, wang-ochiai-2022 on
    # homesteads AND fields, was the GM's hypothetical - that key is cited from homesteads alone)
    what = registry_entries()["visit-toyama-sankyoson"]["what"]
    assert what and what in _read("SOURCES.html")
    for page in ("citations/homesteads.html", "citations/vegetation.html"):
        text = _read(page)
        assert what in text[text.find(WORKS_OPEN) : text.find(WORKS_CLOSE)], page
    outside = [p for p in pathlib.Path(RESEARCH_DIR).glob("*.html") if what in p.read_text(encoding="utf-8")]
    assert outside == [pathlib.Path(RESEARCH_DIR, "SOURCES.html")], "the write-up is typed in exactly one place outside research/citations/"


# ---- the reader and the derivation, on plain strings --------------------------------------------------------------

_NOTES = '<li id="fn-1"><a href="https://x.y/z"><code>k-1</code></a> - 「twelve characters here」 <a class="fnback" href="../p.html#fnref-1">back</a></li>\n<li id="fn-2"><a href="../SOURCES.html#canon"><code>canon</code></a> - 「the GM wrote this」 (see <a href="../water.html#x">water</a>) <a class="fnback" href="../p.html#fnref-2">back</a></li>\n<li id="fn-3"><a href="https://x.y/z"><code>k-1</code></a> - 「again」 <a class="fnback" href="../p.html#fnref-3">back</a></li>'


def test_notes_are_read_in_order_and_keys_deduplicated_in_first_citation_order() -> None:
    ns = notes(_NOTES)
    assert [n for n, _b in ns] == ["1", "2", "3"]
    assert cited_keys(ns) == ["k-1", "canon"]
    assert notes("<p>no notes</p>") == [] and cited_keys([]) == []


def test_a_note_for_the_script_loses_its_back_link_and_is_rebased_to_the_research_page() -> None:
    body = notes(_NOTES)[1][1]
    out = note_for_script(body)
    assert "fnback" not in out and 'href="SOURCES.html#canon"' in out and 'href="water.html#x"' in out
    assert "https://x.y/z" in note_for_script(notes(_NOTES)[0][1]), "an absolute link is untouched"
    js = script_js("p.html", notes(_NOTES))
    assert js.startswith("// DERIVED FILE") and "window.RECORD_CITATIONS = {" in js and '"fn-2": "<a href=\\"SOURCES.html#canon\\">' in js
    assert "fnback" not in js


def test_the_works_block_reports_a_key_with_no_write_up_and_links_a_key_as_feature_190_does() -> None:
    entries = {
        "k-1": {"cite": "Paper X (https://x.y/z)", "line": "Paper X (https://x.y/z) READ", "what": "A paper.", "why": "It applies.", "used": "u"},
        "k-2": {"cite": "Paper Y (https://a.b; SUMMARY-ONLY)", "line": "Paper Y (https://a.b; SUMMARY-ONLY)", "what": "A paper.", "why": "It applies.", "used": "u"},
        "k-3": {"cite": "Paper Z", "line": "Paper Z", "what": "", "why": "", "used": "u"},
    }
    block, missing = works_html(["k-1", "k-2", "k-3", "k-4"], entries, "../")
    assert missing == ["k-3", "k-4"]
    assert block.startswith(WORKS_OPEN) and block.endswith(WORKS_CLOSE)
    assert '<h3 id="work-k-1"><a href="https://x.y/z"><code>k-1</code></a></h3>\n<p>Paper X (https://x.y/z)</p>' in block
    assert '<h3 id="work-k-2"><a href="../SOURCES.html#k-2"><code>k-2</code></a></h3>' in block, "a not-read document links its registry entry"
    assert f"<p><em>{WHY_LABEL}</em> It applies.</p>" in block and "k-3" not in block


def test_the_works_region_is_replaced_between_its_markers_and_a_page_without_them_is_refused() -> None:
    page = f"<h1>x</h1>\n{WORKS_OPEN}\nold\n{WORKS_CLOSE}\n<ol></ol>"
    assert with_works(page, f"{WORKS_OPEN}\nnew\n{WORKS_CLOSE}") == f"<h1>x</h1>\n{WORKS_OPEN}\nnew\n{WORKS_CLOSE}\n<ol></ol>"
    with pytest.raises(ValueError):
        with_works("<h1>x</h1>", "block")


def test_registry_entries_read_the_citation_line_and_the_write_ups(tmp_path: pathlib.Path) -> None:
    src = (
        '<main><h3 id="k-1"><code>k-1</code></h3>\n<p><!-- READ 2026-09-06 -->Paper X, <em>J</em> (https://x.y/z)<!-- T03 --></p>\n'
        f"<p><em>{WHAT_LABEL}</em> A paper about <em>things</em>.</p>\n<p><em>{WHY_LABEL}</em> Because.</p>\n<p><em>Used for:</em> the number</p>\n"
        '<h3 id="k-2"><code>k-2</code></h3>\n<p>Bare (URL: none - unpublished)</p>\n</main>'
    )
    (tmp_path / "SOURCES.html").write_text(src, encoding="utf-8")
    entries = registry_entries(str(tmp_path))
    assert entries["k-1"]["cite"] == "Paper X, <em>J</em> (https://x.y/z)" and "READ 2026-09-06" in entries["k-1"]["line"]
    assert entries["k-1"]["what"] == "A paper about <em>things</em>." and entries["k-1"]["why"] == "Because." and entries["k-1"]["used"] == "the number"
    assert entries["k-2"] == {"cite": "Bare (URL: none - unpublished)", "line": "Bare (URL: none - unpublished)", "what": "", "why": "", "used": ""}
    assert registry_entries(str(tmp_path / "nowhere")) == {}
