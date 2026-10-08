"""`interactive/sources.py` - reading a research page's headings and the keys those sections cite.

The record is HTML since feature 194 (GM 2026-09-06); the first cases here are defects that SHIPPED on the
Markdown record and were invisible in the artifact - the page still rendered a plausible list of sources,
just not the right one - and they hold on the page form too."""

from __future__ import annotations

import html
import pathlib
import re

from l7r.diagram.interactive.record import store
from l7r.diagram.interactive.sources import (
    QUESTION_PAGES,
    RESEARCH_DIR,
    SITE_PAGES,
    citation_lines,
    entry_fragments,
    footnote_sources,
    link_target,
    not_read,
    parse_sections,
    record_text,
    registry_entries,
    research_questions,
    research_sources,
    section_sources,
)
from tests import _flat_record as fr
from tests._record_pages import text_of


def test_an_entry_names_a_question_page_and_links_its_small_page() -> None:
    """Feature 180, spec FR-012a, and since feature 303 the flat layout: an entry names the question's FILE, and its
    link is the question's small page in the record's site, whatever section the question sits in."""
    record = store.load(RESEARCH_DIR)
    page = next(p for p in record.pages("research") if p.heading_id == "the-citys-street-front-continuous-rows-of-shophouses-machiya")
    entry = f"research/questions/{page.file}"
    qs = research_questions(entry)
    assert len(qs) == 1 and qs[0]["url"] == SITE_PAGES + QUESTION_PAGES + page.heading_id + ".html", qs
    assert research_sources(entry), "and its sources resolve too"


def test_a_heading_inside_a_code_sample_is_escaped_text_not_a_section() -> None:
    """On the Markdown record a heading inside a fence had to be skipped explicitly; on a page a heading shown
    as a sample is escaped (`&lt;h2&gt;`), so only a real `<h2>`/`<h3>` opens a section - and a `<h4>` does not."""
    page = '<h2 id="real">Real</h2><p>a</p><pre><code>&lt;h2 id="fake"&gt;Fake&lt;/h2&gt;</code></pre><h4 id="sub">Sub</h4><h3 id="also">Also</h3>'
    assert [h for h, _b, _i in parse_sections(page)] == ["Real", "Also"]


def test_an_entry_names_its_questions_in_order_once_each_however_they_are_joined() -> None:
    """Feature 301: an `Entry:` is a list of fragment paths, joined by `, ` or `; ` (a question's research page, then its
    drawing page), read in the author's order - the primary question first (spec 180 D4) - once each."""
    entry = "research/questions/0430-a.html, research/questions/0280-b.html; research/questions/0430-a.drawing.html, research/questions/0430-a.html"
    assert entry_fragments(entry) == ["0430-a.html", "0280-b.html", "0430-a.drawing.html"]
    assert entry_fragments("research/contents.json#water (the section)") == [], "a section names no question"


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
    """(text, where) for everything a key may be cited in: every question page as its reader sees it, and every notes
    file, where the footnotes are. Both are written in `questions/`, so a link to the registry is `../SOURCES.html`."""
    out = []
    root = pathlib.Path(RESEARCH_DIR) / "questions"
    for page in store.load(RESEARCH_DIR).pages():
        out.append((text_of(f"questions/{page.file}"), page.file))
        notes = root / page.notes_file
        if notes.is_file():
            out.append((notes.read_text(encoding="utf-8"), page.notes_file))
    return out


def test_the_registry_has_one_entry_per_key() -> None:
    """D6: two keys had two headings each, which gives one anchor two bodies and a citation two citation lines
    to choose from. Merged by feature 190; this keeps it so."""
    heads = re.findall(r'<h3 id="([a-z0-9][a-z0-9-]*)">', record_text("SOURCES.html"))
    dupes = sorted({h for h in heads if heads.count(h) > 1})
    assert not dupes, dupes


def test_every_registry_key_cited_in_a_research_page_is_a_link_to_the_right_target() -> None:
    """Feature 190 (GM 2026-09-06: "I want all of our references to be links ... Any reference to an external
    document which we were able to read in order to do our research should be a link to that external
    document"). Every registry key in every research page - in a Sources roster, a footnote or a finding's
    prose - is inside a link, and the link goes where the classifier says. A new entry written with a bare
    key fails here; so does a link to the registry for a document that was read."""
    cites = citation_lines(record_text("SOURCES.html"))
    assert len(cites) > 300, "the registry parsed"
    bare, wrong = [], []
    checked = 0
    for text, name in research_pages():
        for m in _BARE.finditer(text):
            if m.group(1) in cites:
                bare.append(f"{name}: <code>{m.group(1)}</code>")
        for m in _LINKED.finditer(text):
            target, key = html.unescape(m.group(1)), m.group(2)
            if key in cites:
                checked += 1
                want = link_target(key, cites[key], "../")
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


#: The markers `sources.not_read` reads, in the exact case it reads them. A guard that matches a literal cannot
#: fire on a different case, and one that silently does not fire is worse than no guard: `sendai-igune-list`'s
#: citation line carried `summary-only 2026-09-06` and classified as READ the whole time it did, which is how a
#: footnote comes to link a page its passage cannot be read on. So no CITATION LINE - the text `not_read`
#: actually reads, comments included - may spell a marker in a case the classifier cannot see. Write it as the
#: classifier reads it, or take it out as stale. Prose elsewhere in the file may discuss the concept freely.
CLASSIFIER_MARKERS = ("SUMMARY-ONLY", "URL: none")


def marker_case_faults(lines: dict[str, str]) -> list[str]:
    """Every citation line that spells a classifier marker in a case `not_read` would miss."""
    faults = []
    for key, line in sorted(lines.items()):
        for marker in CLASSIFIER_MARKERS:
            for m in re.finditer(re.escape(marker), line, re.I):
                if m.group(0) != marker:
                    faults.append(f"{key}: {m.group(0)!r} - the classifier reads {marker!r}")
    return faults


def test_no_classifier_marker_hides_in_a_case_the_classifier_cannot_see() -> None:
    faults = marker_case_faults({k: e["line"] for k, e in registry_entries().items()})
    assert not faults, "a marker on a citation line that the classifier would miss:\n" + "\n".join(faults[:10])


def test_the_marker_case_rule_fires() -> None:
    assert marker_case_faults({"k": "a line, summary-only 2026-09-06, and another"}) == ["k: 'summary-only' - the classifier reads 'SUMMARY-ONLY'"]
    assert marker_case_faults({"k": "url: none - the work is a book"}) == ["k: 'url: none' - the classifier reads 'URL: none'"]
    assert marker_case_faults({"k": "SUMMARY-ONLY; URL: none"}) == []


def test_a_section_with_no_roster_takes_its_sources_from_its_footnotes(tmp_path: pathlib.Path) -> None:
    """Feature 292 FR-004: a restyled section carries no `Sources:` roster, so the references behind a modal are read
    from the keys its footnotes cite - in order of first citation, once each, a key-less (absence) note contributing
    nothing - and a section that still has a roster is read from the roster, as before. Since feature 303 a page's
    notes are its own."""
    q = tmp_path / "questions"
    q.mkdir()
    ref = '<sup class="fn" data-note="{0}"></sup>'
    (q / "0010-t.html").write_text(f'<h2 id="t">Topic</h2>\n<p>one{ref.format("b-2")} two{ref.format("absent")} three{ref.format("a-1")}</p>\n', encoding="utf-8")
    (q / "0010-t.notes.html").write_text(
        '<li data-note="b-2"><a href="https://x"><code>b-2</code></a> - 「q」</li>\n<li data-note="absent">no publicly readable source<!-- searched 2026-09-29: x --> nothing</li>\n'
        '<li data-note="a-1"><a href="https://y"><code>a-1</code></a> - 「r」; <a href="https://x"><code>b-2</code></a> - 「s」</li>\n',
        encoding="utf-8",
    )
    (q / "0020-r.html").write_text(f'<h2 id="r">Rostered</h2>\n<p><strong>Sources:</strong> <a href="https://z"><code>c-3</code></a></p><p>x{ref.format("b-2")}</p>\n', encoding="utf-8")
    assert research_sources("research/questions/0010-t.html", str(tmp_path)) == ["b-2", "a-1"]
    assert research_sources("research/questions/0020-r.html", str(tmp_path)) == ["c-3"]
    assert footnote_sources("<p>no references</p>", "0010-t.html", str(tmp_path)) == []
    assert research_sources("research/questions/0030-gone.html", str(tmp_path)) == [], "a question that is not there yields nothing"
    assert research_questions("research/questions/0030-gone.html", str(tmp_path)) == []
    assert record_text("questions/0099-none.html", str(tmp_path)) == "" and record_text("SOURCES.html", str(tmp_path)) == ""


# ------------------------------------------------------------------------------- the record loaded once (feature 322)


def _counted_loads(monkeypatch) -> list[str]:  # type: ignore[no-untyped-def]
    """Every `store.load` from here on, by directory; the caches start empty and are left empty."""
    from l7r.diagram.interactive import sources  # noqa: PLC0415

    sources.clear_caches()
    loads: list[str] = []
    real = store.load

    def counted(research_dir: str):  # type: ignore[no-untyped-def]
        loads.append(research_dir)
        return real(research_dir)

    monkeypatch.setattr(store, "load", counted)
    return loads


def _fresh(rec: pathlib.Path, name: str) -> str:
    """A question page rendered from a record loaded for it alone - what every read did before feature 322."""
    record = store.qs.load(str(rec))
    return store.page_html(record, record.by_file[name], str(rec))


def test_reading_every_question_page_loads_the_record_once(tmp_path: pathlib.Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """322 FR-001, FR-004, SC-001: N pages, one load, each page byte-identical to a fresh render."""
    from l7r.diagram.interactive.sources import clear_caches  # noqa: PLC0415

    rec = fr.write(tmp_path)
    names = sorted(store.qs.load(str(rec)).by_file)
    assert len(names) >= 3, "non-vacuity"
    loads = _counted_loads(monkeypatch)
    texts = {n: record_text(f"questions/{n}", str(rec)) for n in names}
    assert loads == [str(rec)], loads
    assert texts == {n: _fresh(rec, n) for n in names}
    record_text("SOURCES.html", str(rec))
    assert len(loads) == 1, "the registry does not load the record"
    clear_caches()


def test_two_record_directories_never_share_a_record(tmp_path: pathlib.Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """322 FR-002, SC-002: each directory is loaded once, and a page comes from its own record."""
    from l7r.diagram.interactive.sources import clear_caches  # noqa: PLC0415

    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    a, b = fr.write(tmp_path / "a"), fr.write(tmp_path / "b")
    fr.edit(b, "0003-rows.html", "Shops in a row.", "Shops in a long row.")
    loads = _counted_loads(monkeypatch)
    for rec in (a, b, a, b):
        for name in ("0001-lanes.html", "0003-rows.html"):
            assert record_text(f"questions/{name}", str(rec)) == _fresh(rec, name), (rec.name, name)
    assert sorted(loads) == sorted([str(a), str(b)]), loads
    assert "long row" in record_text("questions/0003-rows.html", str(b)) and "long row" not in record_text("questions/0003-rows.html", str(a))
    clear_caches()


def test_a_page_not_yet_read_shows_an_edit_made_before_clear_caches(tmp_path: pathlib.Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """322 FR-003, SC-003: the record is held between reads - so an edit is seen after `clear_caches()`, as a build calls it."""
    from l7r.diagram.interactive.sources import clear_caches  # noqa: PLC0415

    rec = fr.write(tmp_path)
    loads = _counted_loads(monkeypatch)
    record_text("questions/0001-lanes.html", str(rec))
    fr.edit(rec, "0003-rows.html", "Shops in a row.", "Shops in a long row.")
    clear_caches()
    assert "long row" in record_text("questions/0003-rows.html", str(rec))
    assert len(loads) == 2, "loaded again after clear_caches"
    clear_caches()
