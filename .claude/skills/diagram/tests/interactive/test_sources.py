"""`interactive/sources.py` - reading a research page's headings and the keys those sections cite.

The record is HTML since feature 194 (GM 2026-09-06); the first cases here are defects that SHIPPED on the
Markdown record and were invisible in the artifact - the page still rendered a plausible list of sources,
just not the right one - and they hold on the page form too."""

from __future__ import annotations

import html
import os
import pathlib
import re

from l7r.diagram.interactive.citations import citations_page
from l7r.diagram.interactive.citations import research_pages as _record_pages
from l7r.diagram.interactive.sources import RESEARCH_DIR, RESEARCH_PAGES, _sections, citation_lines, link_target, not_read, research_questions, research_sources, section_sources


def test_an_entry_may_name_a_research_file_one_directory_down() -> None:
    """Feature 180, spec FR-012a - a latent defect the spec review noticed, fixed under Principle XIV. The
    file pattern could not match `research/cities/fabric.html`, so such an entry resolved to no sources and
    no questions with nothing said; the question URL is built from the same match, so the silent miss would
    have become a silent broken link when the town and city vocabulary arrives."""
    entry = "research/cities/fabric.html - 'Urban commoners built in continuous street walls'"
    qs = research_questions(entry)
    assert len(qs) == 1 and qs[0]["url"] == RESEARCH_PAGES + "cities/fabric.html#urban-commoners-built-in-continuous-street-walls", qs
    assert research_sources(entry), "and its sources resolve too"


def test_a_heading_inside_a_code_sample_is_escaped_text_not_a_section(tmp_path: pathlib.Path) -> None:
    """On the Markdown record a heading inside a fence had to be skipped explicitly; on a page a heading shown
    as a sample is escaped (`&lt;h2&gt;`), so only a real `<h2>`/`<h3>` opens a section - and a `<h4>` does not."""
    page = tmp_path / "p.html"
    page.write_text('<h2 id="real">Real</h2><p>a</p><pre><code>&lt;h2 id="fake"&gt;Fake&lt;/h2&gt;</code></pre><h4 id="sub">Sub</h4><h3 id="also">Also</h3>', encoding="utf-8")
    assert [h for h, _b in _sections(str(page))] == ["Real", "Also"]


def test_a_double_quoted_research_heading_is_read_like_a_single_quoted_one() -> None:
    """A registry entry quotes a heading 'like this' - and "like this" when the heading itself carries
    an apostrophe, which the single-quote form cannot hold. Both must resolve to the same section.

    The defect this pins shipped: the marsh class names research/water.html's "A reservoir's shore is
    reeded, and its EMBANKMENT is mown", and with only the single-quote form the run of characters
    BETWEEN the two double quotes matched as one giant heading that no section is named, so the entry
    contributed nothing and swallowed the one after it."""
    entry = "research/water.html - \"A reservoir's shore is reeded, and its EMBANKMENT is mown\""
    assert "mineta-2007-tameike" in research_sources(entry)


def test_a_sources_roster_is_read_whole_and_deduplicated() -> None:
    """The roster is one `<p>` on the page (feature 194), so the 2026-08-29 wrap defect - keys past the first
    physical line of a `**Sources:**` paragraph dropped invisibly - cannot recur; the keys are still read in
    order and once each, linked or bare."""
    body = '<p>text</p>\n<p><strong>Sources:</strong> <a href="https://x"><code>alpha-one</code></a>, <code>beta-two</code>,\n<a href="SOURCES.html#gamma-three"><code>gamma-three</code></a> (a note), <code>alpha-one</code>.</p>\n<p><code>not-a-source</code></p>\n'
    assert section_sources(body) == ["alpha-one", "beta-two", "gamma-three"]
    assert section_sources("<p>no roster here</p>") == []


# ---- feature 190: every source in a research finding is a link ------------------------------------------------
# The classifier is THE rule (spec 190 FR-001/FR-005, D5) and has one body: since feature 211 it lives in
# `interactive/sources.py` (`citation_lines`, `not_read`, `link_target`), because `make citations` derives the works
# section of every citations page with it and a tool under l7r/ does not import from tests/. It reads the CITATION
# LINE - the first paragraph of an entry, WITH its comments' text (the READ markers moved into comments in feature 209)
# - never the *Used for:* notes, which can say SUMMARY-ONLY about a different claim drawn from a read document.

_LINKED = re.compile(r'<a href="([^"]*)"><code>([a-z0-9][a-z0-9-]*)</code></a>')
_BARE = re.compile(r'(?<!">)<code>([a-z0-9][a-z0-9-]*)</code>')


def research_pages() -> list[tuple[str, str]]:
    """(path, the prefix that reaches research/ from it) for every page a key may be cited on: the research pages and,
    since feature 211, their citations pages - where the footnotes are, and the derived works section."""
    out = []
    for rel in _record_pages():
        out.append((os.path.join(RESEARCH_DIR, rel), "../" * rel.count("/")))
        crel = citations_page(rel)
        out.append((os.path.join(RESEARCH_DIR, crel), "../" * crel.count("/")))
    return out


def test_the_registry_has_one_entry_per_key() -> None:
    """D6: two keys had two headings each, which gives one anchor two bodies and a citation two citation lines
    to choose from. Merged by feature 190; this keeps it so."""
    heads = re.findall(r'<h3 id="([a-z0-9][a-z0-9-]*)">', pathlib.Path(RESEARCH_DIR, "SOURCES.html").read_text(encoding="utf-8"))
    dupes = sorted({h for h in heads if heads.count(h) > 1})
    assert not dupes, dupes


def test_every_registry_key_cited_in_a_research_page_is_a_link_to_the_right_target() -> None:
    """Feature 190 (GM 2026-09-06: "I want all of our references to be links ... Any reference to an external
    document which we were able to read in order to do our research should be a link to that external
    document"). Every registry key in every research page - in a Sources roster, a footnote or a finding's
    prose - is inside a link, and the link goes where the classifier says. A new entry written with a bare
    key fails here; so does a link to the registry for a document that was read."""
    cites = citation_lines(pathlib.Path(RESEARCH_DIR, "SOURCES.html").read_text(encoding="utf-8"))
    assert len(cites) > 300, "the registry parsed"
    bare, wrong = [], []
    checked = 0
    for path, rel in research_pages():
        text = pathlib.Path(path).read_text(encoding="utf-8")
        name = os.path.relpath(path, RESEARCH_DIR)
        for m in _BARE.finditer(text):
            if m.group(1) in cites:
                bare.append(f"{name}: <code>{m.group(1)}</code>")
        for m in _LINKED.finditer(text):
            target, key = html.unescape(m.group(1)), m.group(2)
            if key in cites:
                checked += 1
                want = link_target(key, cites[key], rel)
                if target != want:
                    wrong.append(f"{name}: {key} -> {target} (want {want})")
    assert checked > 1000, "the record's citations were found - the rosters, the notes and the works sections (non-vacuity)"
    assert not bare, "bare keys (write them as <a href=...><code>key</code></a>):\n" + "\n".join(bare)
    assert not wrong, "mis-targeted keys:\n" + "\n".join(wrong)


def test_the_classifier_reads_the_citation_line_and_the_read_marker_governs() -> None:
    assert not_read("Paper X (https://a.b/c; SUMMARY-ONLY 2026-08-28)")
    assert not_read("The GM's notes (URL: none - unpublished)")
    assert not_read("Site Y (https://a.b/c; unfetched 2026-08-28)"), "an unfetched URL with no READ is not read"
    assert not not_read("Site Y - text READ via the API (https://a.b/c; unfetched 2026-08-28)"), "READ governs"
    assert not not_read("Paper Z (READ 2026-08-27) (https://a.b/c)")
    assert link_target("k", "Paper Z (READ) (https://a.b/c). More (https://d.e/f)", "") == "https://a.b/c", "the FIRST URL"
    assert link_target("k", "ja.wikipedia 塀 (https://ja.wikipedia.org/wiki/塀_(城郭); READ)", "") == "https://ja.wikipedia.org/wiki/塀_(城郭)", "balanced parens kept"
    assert link_target("k", "Paper X (https://a.b/c; SUMMARY-ONLY)", "../") == "../SOURCES.html#k"
    assert link_target("k", "Nothing with a URL at all", "") == "SOURCES.html#k"
