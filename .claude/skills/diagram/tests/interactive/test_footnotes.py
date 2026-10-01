"""Feature 194 (GM 2026-09-06): a reference QUOTES the passage that supports the assertion - the mechanical half.

The record's citation form (research/CLAUDE.md): a reference `<sup class="fn" data-note="<key>"></sup>` after an
assertion, and in the page's own notes file (features 211, 258, 303) a `<li data-note="<key>">` with the key link and the
quote; the build numbers both, from 1 on each question's page. What a test can hold: every reference resolves in its
page's notes, and every note is referenced; every note names a registry key and carries a quotation; every key on a section's
`**Sources:**` roster is quoted by a footnote in that section ("no point in including a reference if it is not
being quoted"). What only the `quote-check` agent can hold - the quote is verbatim on the page, it supports the
assertion, and every assertion has one - is its job, before a research edit lands."""

from __future__ import annotations

import html
import pathlib
import re

import pytest

from l7r.diagram.interactive.citations import GROUNDS_REASONS, footnote_form, grounds_reasons, is_settled
from l7r.diagram.interactive.record import absence, store
from l7r.diagram.interactive.record.notes import REFERENCE
from l7r.diagram.interactive.sources import RESEARCH_DIR, canon_keys, registry_keys
from tests._record_pages import notes_text, numbered, page, question_pages

#: a second reference to the same note carries no id (ids are unique; the back-link returns to the first); the href
#: names the citations page (feature 211) - `_REF_TARGET` checks WHICH page below
# A REFERENCE ID MAY CARRY AN ORDINAL (feature 258): where one note is cited more than once on a page,
# the assembly allocates `fnref-N`, `fnref-N-2`, so that every id in the document is unique and every
# reference can be returned to. Before it, a repeat was either a DUPLICATED id (2 pages) or a hand-made
# suffix (`fnref-75b` on `water.html`) - and this pattern matched neither, so those references were
# invisible to every check in this file.
_REF = re.compile(r'<sup class="fn"><a (?:id="fnref-(?:\d+(?:-\d+)?)" )?href="[^"#]*#fn-(\d+)">\1</a></sup>')
_REF_TARGET = re.compile(r'<sup class="fn"><a (?:id="fnref-\d+(?:-\d+)?" )?href="([^"#]*)#fn-\d+">')
_KEY_LINK = re.compile(r'<a href="[^"]*"><code>([a-z0-9][a-z0-9-]*)</code></a>')
_QUOTE = re.compile(r"[\"“「『]([^\"”」』]{12,})[\"”」』]")
_HEADING = re.compile(r"<h([2-4])[ >]")
_ROSTER = re.compile(r"<p><strong>Sources:</strong>(.*?)</p>", re.S)
_ROSTER_KEY = re.compile(r"<code>([a-z0-9][a-z0-9-]*)</code>")
#: Files that hold the record's FINDINGS. The registry and the indexes carry no assertions to footnote.
_NOT_FINDINGS = {"SOURCES.html"}


def _finding_files() -> list[pathlib.Path]:
    """Every question page of both halves, read from its fragments (features 301, 303)."""
    return list(question_pages())


def footnotes(path: pathlib.Path) -> tuple[str, list[str], dict[str, str]]:
    """(the page with its references numbered, the reference numbers in reading order, {note number: body})."""
    body, defs = numbered(path)
    return body, [m.group(1) for m in _REF.finditer(body)], defs


#: THE FORMS A FOOTNOTE MAY TAKE live in the engine (`interactive/citations.py`), not here: the gate, the
#: `footnote-census` tool and any later reader must not be able to disagree about what a note is, and engine
#: code may not import from `tests/`. This file holds what the RECORD owes on top of the form - that a citation
#: names a registered key and carries a quotation, and that every note is referenced.
@pytest.mark.parametrize("path", _finding_files(), ids=lambda p: p.name)
def test_every_footnote_resolves_and_every_definition_quotes_a_registered_source(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    body, refs, defs = footnotes(path)
    wrong = sorted({t for t in _REF_TARGET.findall(body) if t})
    assert not wrong, f"{path.name}: references pointing off their own page: {wrong}"
    keys = registry_keys()
    assert set(refs) == set(defs), f"{path.name}: a reference without its note, or the reverse"
    orphans = sorted(set(store.page_notes(path.name)) - set(REFERENCE.findall(text)))
    assert not orphans, f"{path.name}: notes nothing references: {orphans}"
    canon = canon_keys()
    bad = []
    for fid, body in defs.items():
        form = footnote_form(body, canon)
        # A GROUNDS note owes no key, no link and no quotation, exactly as an absence note does - naming the
        # classifier without teaching THIS loop was feature 235's near miss: the first grounds note would have
        # failed here whatever `footnote_form` returned, and the requirement would have been discovered as a red
        # gate rather than written down.
        if form in ("absence", "grounds"):
            continue
        if absence.unrender(body).lstrip().startswith(("no source is owed:", "no publicly readable source")):
            # a malformed note of either sourceless form is reported AS that form's defect: saying "no registry
            # key link" about a grounds note whose reason is misspelled sends the next reader to look for a key
            bad.append(f"[^{fid}]: {form}")
            continue
        key = _KEY_LINK.search(body)
        if not key or key.group(1) not in keys:
            bad.append(f"[^{fid}]: no registry key link")
        elif not _QUOTE.search(body):
            bad.append(f"[^{fid}]: no quotation (a passage of 12+ characters in quotation marks)")
        elif form != "citation":
            bad.append(f"[^{fid}]: {form}")
    assert not bad, f"{path.name}:\n" + "\n".join(bad)


def test_the_footnote_forms_are_told_apart() -> None:
    """Feature 195 FR-002, the classifier on plain strings: the two forms pass, the three defects are named."""
    canon = {"l7r-median-domain"}
    fnback = ' <a class="fnback" href="#fnref-1">back</a>'
    assert footnote_form('<a href="https://x.y/z"><code>k-1</code></a> - 「twelve characters here」' + fnback, canon) == "citation"
    assert footnote_form('<a href="../SOURCES.html#l7r-median-domain"><code>l7r-median-domain</code></a> - 「the GM wrote this」' + fnback, canon) == "citation"
    assert footnote_form("no publicly readable source (searched 2026-09-06: doi 403; the passage came from registry entry k-1)" + fnback, canon) == "absence"
    assert footnote_form("no publicly readable source (searched 2026-09-06: x)" + ' <a class="fnback" href="../cities/p.html#fnref-1">back</a>', canon) == "absence", (
        "a back link to the research page (feature 211)"
    )
    assert footnote_form('<a href="SOURCES.html#k-2"><code>k-2</code></a> - 「a summary, not a page」' + fnback, canon).startswith("links the key to")
    assert footnote_form('no publicly readable source (searched 2026-09-06: x) <a href="https://x.y"><code>k</code></a>' + fnback, canon) == "an absence note carries no key and no link"
    # THE THIRD FORM (feature 235): a reason from the closed six, no key, no link, no quotation
    assert footnote_form("no source is owed: measured on our own maps" + fnback, canon) == "grounds"
    assert footnote_form("no source is owed: physical necessity; a drawing convention" + fnback, canon) == "grounds"
    assert grounds_reasons("no source is owed: physical necessity; a drawing convention" + fnback) == ["physical necessity", "a drawing convention"]
    assert footnote_form("no source is owed: it seemed fine" + fnback, canon).startswith("names a reason that is not one of the six")
    assert footnote_form('no source is owed: physical necessity <a href="https://x.y"><code>k</code></a>' + fnback, canon) == "a grounds note carries no key and no link"
    assert footnote_form("no source is owed:" + fnback, canon) == "a grounds note names at least one of the six reasons"
    assert grounds_reasons("no publicly readable source (searched 2026-09-12: x)") == []
    assert len(set(GROUNDS_REASONS)) == 6, "the list is closed; a seventh reason is a change to the spec"
    assert footnote_form("something else entirely" + fnback, canon) is None


#: The three openers a note may have. A note is ONE kind (feature 235 FR-009), so no note may open as two.
_OPENERS = ("no source is owed:", "no publicly readable source")
#: A settled absence carries two dated passes and the marker (FR-004). What the dates cannot say - that each pass
#: named its tools and the later named one the earlier lacked - is `record-format`'s judgment, not a regex's.
_SEARCHED = re.compile(r"searched (\d{4}-\d{2}-\d{2})")


def sourceless_shape_faults(page_notes: dict[str, str]) -> list[str]:
    """FR-009's mechanical half, over one page's notes: a reason from the six, one kind per note, and a settled
    note carrying two DIFFERENT dated passes beside its marker."""
    faults = []
    for fid, body in page_notes.items():
        stripped = absence.unrender(re.sub(r'<a class="fnback" href="[^"]*">back</a>', "", body)).strip()
        if sum(stripped.startswith(o) for o in _OPENERS) > 1:
            faults.append(f"[^{fid}]: opens as two kinds at once")
        if stripped.startswith("no source is owed:"):
            unknown = [r for r in grounds_reasons(stripped) if r not in GROUNDS_REASONS]
            if unknown:
                faults.append(f"[^{fid}]: reason not one of the six: {unknown!r}")
        if is_settled(stripped):
            if not stripped.startswith("no publicly readable source"):
                faults.append(f"[^{fid}]: only an absence note can be settled")
            dates = sorted(set(_SEARCHED.findall(stripped)))
            if len(dates) < 2:
                faults.append(f"[^{fid}]: settled on {len(dates)} dated pass(es); FR-004 wants two on different dates")
    return faults


@pytest.mark.parametrize("path", _finding_files(), ids=lambda p: p.name)
def test_the_sourceless_footnote_forms_keep_their_shape(path: pathlib.Path) -> None:
    faults = sourceless_shape_faults(store.page_notes(path.name))
    assert not faults, f"{path.name} (feature 235 FR-009):\n" + "\n".join(faults)


def test_the_sourceless_shape_rule_fires() -> None:
    """Non-vacuity: the record has no settled note and one grounds note, so the rule is proved on strings."""
    good = {
        "1": "no source is owed: measured on our own maps",
        "2": "no publicly readable source (searched 2026-09-01: a; searched 2026-09-12: b, settled 2026-09-12)",
    }
    assert sourceless_shape_faults(good) == []
    bad = {
        "3": "no source is owed: it seemed fine",
        "4": "no publicly readable source (searched 2026-09-12: a, settled 2026-09-12)",
        "5": "no source is owed: physical necessity, settled 2026-09-12",
    }
    assert sourceless_shape_faults(bad) == [
        "[^3]: reason not one of the six: ['it seemed fine']",
        "[^4]: settled on 1 dated pass(es); FR-004 wants two on different dates",
        # the settled marker is swept into the reason, which is itself the fault: a grounds note has no search
        "[^5]: reason not one of the six: ['physical necessity, settled 2026-09-12']",
        "[^5]: only an absence note can be settled",
        "[^5]: settled on 0 dated pass(es); FR-004 wants two on different dates",
    ]


@pytest.mark.parametrize("path", _finding_files(), ids=lambda p: p.name)
def test_every_key_on_a_sources_roster_is_quoted_by_a_footnote_in_its_section(path: pathlib.Path) -> None:
    """The roster is what the modal reads; the footnotes are where the quotes live; a key on the roster that no
    footnote of the section quotes is a reference that is not being quoted."""
    body, _refs, defs = footnotes(path)
    heads = [(m.start(), int(m.group(1))) for m in _HEADING.finditer(body)]
    unquoted = []
    for i, (a, level) in enumerate(heads):
        # a section runs to the next heading of the SAME or a HIGHER level: an <h2>'s roster is quoted anywhere in
        # its <h3> subsections too (an entry with <h3> subsections keeps its roster at the top)
        b = next((s for s, lv in heads[i + 1 :] if lv <= level), len(body))
        section = body[a:b]
        roster = _ROSTER.search(section)
        if not roster:
            continue
        quoted = {k for fid in _REF.findall(section) for k in _KEY_LINK.findall(defs.get(fid, ""))}
        for key in _ROSTER_KEY.findall(roster.group(1)):
            if key not in quoted:
                unquoted.append(f"{section.splitlines()[0][:60]!r}: `{key}`")
    assert not unquoted, f"{path.name}: roster keys no footnote in the section quotes:\n" + "\n".join(unquoted)


#: Feature 202 (GM 2026-09-07): "for foreign language things we want to quote the English translation rather than the
#: original text but we also want to note that it is a translation." A 「」 quote in a research page is either ASCII-only
#: or is followed, in the same footnote / paragraph / registry entry, by a translation note; the original after
#: "original:" is the anchor and is exempt. Derived from the NOTE, not the script - the record quotes German and Korean
#: as well as Japanese and Chinese. The limit, stated in the spec: a Latin-script foreign quote with no non-ASCII
#: character reads as English here; the sweep and the quote-check carry those.
_QUOTE_SPAN = re.compile(r"「([^」]+)」")
_TRANSLATION_NOTE = re.compile(r"\((?:[^()]*;\s*)?(?:(?:title\s+)?translated\b|machine translation|translation:)", re.I)
_BLOCK = re.compile(r"<(p|li|h[2-4])\b[^>]*>(.*?)</\1>", re.S)
#: English quotes carry macrons (daimyō), curly quotes and the source's own dashes, so "not ASCII" is not "foreign".
#: Foreign is a NON-LATIN script (CJK, kana, hangul, Cyrillic, Greek...) or, for a Latin-script language, a run of its
#: function words - German is the one the record quotes (the `waldrand-dewiki` fixture). The stated limit (spec 202
#: FR-002): a Latin-script foreign quote outside that list reads as English here; the sweep and quote-check carry it.
_NON_LATIN = re.compile(r"[\u0370-\u03ff\u0400-\u04ff\u0590-\u06ff\u0e00-\u0e7f\u1100-\u11ff\u3000-\u30ff\u3400-\u9fff\uac00-\ud7af\uf900-\ufaff\uff00-\uffef]")
_GERMAN = re.compile(r"\b(und|der|die|das|von|mit|nach|sich|ist|ein|eine|nicht|auch|bei|zum|zur|des|dem|wird|werden|oder)\b")


#: An English page's own gloss of a term in its native script - "Satoyama (里山) is..." on en.wikipedia - is not a
#: foreign quote: a parenthesis holding no Latin letter is dropped before the script test (feature 269, V1 check).
_GLOSS = re.compile(r"[(（][^()（）A-Za-z]*[)）]")


def _looks_foreign(passage: str) -> bool:
    """Since feature 292 (GM 2026-09-29: *"we should presume the source is in English unless ... stated otherwise"*) an
    English quote carries no marker, so an English passage with a native-script gloss run into it ("the Senju 千住 area")
    must read as English by itself: foreign is MOSTLY non-Latin - over 30% of its letters - or a run of German."""
    text = _GLOSS.sub("", passage)
    letters = [c for c in text if c.isalpha()]
    non_latin = sum(1 for c in letters if _NON_LATIN.match(c))
    return (bool(letters) and non_latin / len(letters) > 0.3) or len(_GERMAN.findall(passage)) >= 2


def _anchor_spans(block: str) -> list[tuple[int, int]]:
    """The [start, end) of every `original: 「...」` anchor, closed at bracket depth zero - an original may itself
    quote (「A「B」C」), and everything inside the anchor is the source's text, exempt from the note rule."""
    spans = []
    for m in re.finditer(r"original: 「", block):
        depth = 0
        for j in range(m.end() - 1, len(block)):
            if block[j] == "「":
                depth += 1
            elif block[j] == "」":
                depth -= 1
                if depth == 0:
                    spans.append((m.start(), j + 1))
                    break
    return spans


def unmarked_foreign_quotes(text: str) -> list[str]:
    """The 「」 quotes that are not ASCII and carry no translation note in their block, original anchors excluded."""
    bad = []
    for m in _BLOCK.finditer(text):
        block = m.group(2)
        anchors = _anchor_spans(block)
        for q in _QUOTE_SPAN.finditer(block):
            passage = html.unescape(q.group(1))
            if not _looks_foreign(passage):
                continue
            if any(a <= q.start() < b for a, b in anchors):
                continue
            after = html.unescape(block[q.end() : q.end() + 400])
            if _TRANSLATION_NOTE.search(after):
                continue
            bad.append(passage[:60])
    return bad


@pytest.mark.parametrize("path", [*_finding_files(), page("SOURCES.html")], ids=lambda p: str(p.relative_to(RESEARCH_DIR)))
def test_a_foreign_language_quote_is_a_marked_translation(path: pathlib.Path) -> None:
    """On the page and in its notes file."""
    bad = unmarked_foreign_quotes(path.read_text(encoding="utf-8")) + unmarked_foreign_quotes(notes_text(path))
    assert not bad, f"{path.name}: {len(bad)} foreign-language quote(s) with no translation note (feature 202):\n" + "\n".join(bad[:8])


#: The forms feature 292 retired from the record (GM 2026-09-29): English is presumed, and so is this project as the
#: translator - a translation by anyone else names them, and one that says more than the language keeps its words.
_RETIRED = re.compile(r"the source(?:'|&#x27;|’)s own English|translated from the (?:[a-z]+ )?[A-Z][A-Za-z ()-]* by this project")


@pytest.mark.parametrize("path", _finding_files(), ids=lambda p: str(p.relative_to(RESEARCH_DIR)))
def test_no_note_says_the_source_s_own_english_or_by_this_project(path: pathlib.Path) -> None:
    hits = [m.group(0) for m in _RETIRED.finditer(path.read_text(encoding="utf-8") + notes_text(path))]
    assert not hits, f"{path.name}: write `(translated; original: ...)` and leave English unmarked (feature 292): {hits[:3]}"


def test_an_english_passage_with_a_gloss_is_english_and_a_japanese_one_is_not() -> None:
    assert not _looks_foreign("cremation grounds clustered in the Senju 千住 area of Edo")
    assert _looks_foreign("昭和６２年の砺波市鹿島での調査によると")
    assert not _looks_foreign("")
    assert _RETIRED.search("(the source's own English)") and _RETIRED.search("(translated from the classical Chinese by this project;")
    assert not _RETIRED.search("(the paper's own English title; original: 「x」)"), "a paper's own English title says something"


def test_the_translation_form_is_told_apart() -> None:
    """The German and Korean fixtures fire; the marked form and the anchor pass; ASCII passes."""
    de = "<li>「Ein idealer Waldrand gliedert sich von außen nach innen」 (an ideal forest edge)</li>"
    ko = "<li>「동구숲 7,149 727」 (Table 8)</li>"
    ok = "<li>「An ideal forest edge is layered from outside in」 (translated from the German by this project; original: 「Ein idealer Waldrand gliedert sich von außen nach innen」)</li>"
    assert unmarked_foreign_quotes(de) and unmarked_foreign_quotes(ko)
    assert unmarked_foreign_quotes(ok) == [] and unmarked_foreign_quotes("<p>「plain ascii quote here」</p>") == []
    assert unmarked_foreign_quotes("<li>「the daimyō’s rice — stored (1603–1867)」 (English with macrons and the source's dashes)</li>") == []
    assert unmarked_foreign_quotes("<li>「Satoyama (里山) is a Japanese term」 (English, glossing a term)</li>") == []
    assert unmarked_foreign_quotes("<li>「屋敷林（やしきりん）とは」 (no note)</li>")
