"""Feature 211 (GM 2026-09-07): a work's write-up is typed once, in the registry, and what a page shows of it is DERIVED.

The GM: *"we do not want to have multiple different write ups of a single paper ... drawing from a single data
source."* What a test can hold: every work a question's notes cite has both write-ups in its registry entry (a source
is not cited without one); the works block at the foot of a page is derived from the registry; the reader and the
derivation behave on plain strings. Feature 211's per-page citations pages went with the page directories (feature
303): a question's notes are at the foot of its own page. What only the `source-applicability` agent can hold - whether
a write-up is honest about the work's era, place and kind - is its job, before a source lands."""

from __future__ import annotations

import json
import pathlib

import pytest

from l7r.diagram.interactive.citations import WORKS_CLOSE, WORKS_OPEN, cited_keys, works_html
from l7r.diagram.interactive.record import site, store
from l7r.diagram.interactive.record import source_tags as st
from l7r.diagram.interactive.sources import RESEARCH_DIR, WHAT_LABEL, WHY_LABEL, canon_keys, record_text, registry_entries
from tests import _flat_record as fr

_PAGES = store.load(RESEARCH_DIR).pages()


@pytest.fixture(scope="module")
def catalog() -> st.Catalog:
    """The real registry's tags and sections (feature 305), read once."""
    return st.Catalog(RESEARCH_DIR, {i.id: i.html for i in site.Registry(RESEARCH_DIR).items()}, canon_keys(), store.REGISTRY_DIR)


@pytest.mark.parametrize("page", _PAGES, ids=lambda p: p.file)
def test_every_cited_work_has_both_write_ups(page: store.qs.Page, catalog: st.Catalog) -> None:
    """The works block is derived from the registry; a cited key whose entry lacks a write-up fails here."""
    keys = cited_keys(list(store.page_notes(page.file).items()))
    _block, missing = works_html(keys, registry_entries(), "", catalog)
    assert not missing, f"{page.file}: cited keys whose registry entry has no `{WHAT_LABEL}` / `{WHY_LABEL}` write-up (feature 211: a source is not cited without one): {missing}"


def test_a_work_cited_from_two_pages_has_one_write_up() -> None:
    """Spec 211 SC-004: the hand-authored paragraph is in the registry and in no question's files."""
    what = registry_entries()["visit-toyama-sankyoson"]["what"]
    citing = [p.file for p in _PAGES if "visit-toyama-sankyoson" in cited_keys(list(store.page_notes(p.file).items()))]
    assert len(citing) >= 2, "the example is cited from two pages"
    assert what and what in record_text("SOURCES.html")
    root = pathlib.Path(RESEARCH_DIR) / "questions"
    assert not [f.name for f in root.iterdir() if what in f.read_text(encoding="utf-8")], "the write-up is typed in exactly one place"


# ---- the reader and the derivation, on plain strings --------------------------------------------------------------

_NOTES = [
    ("1", '<a href="https://x.y/z"><code>k-1</code></a> - 「twelve characters here」'),
    ("2", '<a href="../SOURCES.html#canon"><code>canon</code></a> - 「the GM wrote this」 (see <a href="0001-x.html">water</a>)'),
    ("3", '<a href="https://x.y/z"><code>k-1</code></a> - 「again」'),
]


def test_keys_are_deduplicated_in_first_citation_order() -> None:
    assert cited_keys(_NOTES) == ["k-1", "canon"] and cited_keys([]) == []


def test_the_works_block_reports_a_key_with_no_write_up_and_links_a_key_as_feature_190_does(tmp_path: pathlib.Path) -> None:
    entries = {
        "k-1": {"cite": "Paper X (https://x.y/z)", "line": "Paper X (https://x.y/z) READ", "what": "A paper.", "why": "It applies.", "used": "u"},
        "k-2": {"cite": "Paper Y (https://a.b; SUMMARY-ONLY)", "line": "Paper Y (https://a.b; SUMMARY-ONLY)", "what": "A paper.", "why": "It applies.", "used": "u"},
        "k-3": {"cite": "Paper Z", "line": "Paper Z", "what": "", "why": "", "used": "u"},
    }
    (tmp_path / st.VOCABULARY).write_text(json.dumps(fr.SOURCE_TAGS), encoding="utf-8")
    (tmp_path / st.SECTIONS).write_text(json.dumps(fr.SOURCE_SECTIONS), encoding="utf-8")
    tagged = {"k-1": "<!-- tags: period=premodern; region=japan; kind=primary -->", "k-2": "<!-- tags: period=present-day; region=china; kind=reference -->"}
    block, missing = works_html(["k-2", "k-1", "k-3", "k-4"], entries, "../", st.Catalog(str(tmp_path), tagged, set(), "sources"))
    assert missing == ["k-3", "k-4"]
    assert block.startswith(WORKS_OPEN) and block.endswith(WORKS_CLOSE)
    assert '<h4 id="work-k-1"><a href="https://x.y/z"><code>k-1</code></a></h4>\n<p class="srctags">' in block and "</p>\n<p>Paper X (https://x.y/z)</p>" in block
    assert '<h4 id="work-k-2"><a href="../SOURCES.html#k-2"><code>k-2</code></a></h4>' in block, "a not-read document links its registry entry"
    assert block.index("Premodern Japan") < block.index("work-k-1") < block.index('id="page-works-present-day"') < block.index("work-k-2"), "grouped by section, not by citation order"
    assert f"<p><em>{WHY_LABEL}</em> It applies.</p>" in block and "k-3" not in block


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
