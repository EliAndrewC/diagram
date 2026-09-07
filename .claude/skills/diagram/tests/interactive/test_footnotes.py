"""Feature 194 (GM 2026-09-06): a reference QUOTES the passage that supports the assertion - the mechanical half.

The record's citation form (research/CLAUDE.md): `<sup class="fn"><a id="fnref-n" href="citations/<name>.html#fn-n">n</a></sup>`
after an assertion, and - since feature 211 (GM 2026-09-07: the notes moved out of the research page into
`research/citations/<name>.html`) - on the page's CITATIONS PAGE a `<li id="fn-n">` with the key link and the quote. What a test can hold: every reference points at its own
citations page and resolves there, and every note is referenced; every note names a registry key and carries a quotation; every key on a section's
`**Sources:**` roster is quoted by a footnote in that section ("no point in including a reference if it is not
being quoted"). What only the `quote-check` agent can hold - the quote is verbatim on the page, it supports the
assertion, and every assertion has one - is its job, before a research edit lands."""

from __future__ import annotations

import html
import os
import pathlib
import re

import pytest

from l7r.diagram.interactive.citations import citations_page, notes
from l7r.diagram.interactive.sources import RESEARCH_DIR

#: a second reference to the same note carries no id (ids are unique; the back-link returns to the first); the href
#: names the citations page (feature 211) - `_REF_TARGET` checks WHICH page below
_REF = re.compile(r'<sup class="fn"><a (?:id="fnref-(?:\d+)" )?href="[^"#]*#fn-(\d+)">\1</a></sup>')
_REF_TARGET = re.compile(r'<sup class="fn"><a (?:id="fnref-\d+" )?href="([^"#]*)#fn-\d+">')
_KEY_LINK = re.compile(r'<a href="[^"]*"><code>([a-z0-9][a-z0-9-]*)</code></a>')
_QUOTE = re.compile(r"[\"“「『]([^\"”」』]{12,})[\"”」』]")
_HEADING = re.compile(r"<h([2-4])[ >]")
_ROSTER = re.compile(r"<p><strong>Sources:</strong>(.*?)</p>", re.S)
_ROSTER_KEY = re.compile(r"<code>([a-z0-9][a-z0-9-]*)</code>")
#: Files that hold the record's FINDINGS. The registry and the indexes carry no assertions to footnote.
_NOT_FINDINGS = {"SOURCES.html"}


def _finding_files() -> list[pathlib.Path]:
    root = pathlib.Path(RESEARCH_DIR)
    return [p for p in sorted(root.glob("*.html")) + sorted((root / "cities").glob("*.html")) if p.name not in _NOT_FINDINGS]


def _rel(path: pathlib.Path) -> str:
    return str(path.relative_to(RESEARCH_DIR)).replace(os.sep, "/")


def citations_of(path: pathlib.Path) -> pathlib.Path:
    """The citations page of a research page (feature 211)."""
    return pathlib.Path(RESEARCH_DIR, citations_page(_rel(path)))


def footnotes(text: str, citations: str) -> tuple[list[str], dict[str, str]]:
    """(reference ids in reading order - the research page's, then the ones a note makes to another note on the
    citations page; {note id: body} from the citations page)."""
    return [m.group(1) for m in _REF.finditer(text)] + [m.group(1) for m in _REF.finditer(citations)], dict(notes(citations))


def registry_keys() -> set[str]:
    src = pathlib.Path(RESEARCH_DIR, "SOURCES.html").read_text(encoding="utf-8")
    return set(re.findall(r'<h3 id="([a-z0-9][a-z0-9-]*)"', src))


#: Feature 195 (GM 2026-09-06): a footnote CITES only a page on the public internet where its quote can be read, or
#: it is an ABSENCE note - no key, no link, what was searched. The one carve-out, by KEY: the GM's own campaign
#: notes (`l7r.md`, `budgets.md`), canon rather than a source claimed to support a historical point, keep their
#: registry link - the GM's ruling of 2026-09-07 ("it is correct to make L7R setting notes an exception to the
#: citation rule"). Derived from the registry rather than listed, so a new canon key is covered the day it lands.
_ABSENCE = re.compile(r"^no publicly readable source \(searched \d{4}-\d{2}-\d{2}:")
_ENTRY = re.compile(r'<h3 id="([a-z0-9][a-z0-9-]*)">.*?</h3>\s*<p>(.*?)</p>', re.S)
_HREF_OF_KEY = re.compile(r'<a href="([^"]*)"><code>[a-z0-9][a-z0-9-]*</code></a>')


def canon_keys() -> set[str]:
    src = pathlib.Path(RESEARCH_DIR, "SOURCES.html").read_text(encoding="utf-8")
    return {m.group(1) for m in _ENTRY.finditer(src) if re.search(r"\bl7r\.md\b|\bbudgets\.md\b", m.group(2))}


def footnote_form(body: str, canon: set[str]) -> str | None:
    """'citation', 'absence', or the defect (feature 195 FR-002). A citation links its key to an http(s) page - the
    registry is not a page where a quote can be read - unless the key is canon; an absence note carries no key link
    and no URL at all (its only anchor is the back link, which since feature 211 names the research page)."""
    body = re.sub(r'<a class="fnback" href="[^"]*">back</a>', "", body)
    if _ABSENCE.match(body):
        if "<code>" in body or 'href="' in body:
            return "an absence note carries no key and no link"
        return "absence"
    key = _KEY_LINK.search(body)
    href = _HREF_OF_KEY.search(body)
    if not key or not href:
        return None
    target = href.group(1)
    if target.startswith(("http://", "https://")):
        return "citation"
    if "SOURCES.html#" in target and key.group(1) in canon:
        return "citation"
    return f"links the key to {target!r}, which is not a page on the public internet where the quote can be read"


@pytest.mark.parametrize("path", _finding_files(), ids=lambda p: p.name)
def test_every_footnote_resolves_and_every_definition_quotes_a_registered_source(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    cpath = citations_of(path)
    assert cpath.exists(), f"{path.name}: no citations page at {cpath} (feature 211: every research page has one)"
    refs, defs = footnotes(text, cpath.read_text(encoding="utf-8"))
    want = "../" * _rel(path).count("/") + citations_page(_rel(path))
    wrong = sorted({t for t in _REF_TARGET.findall(text) if t != want}) + sorted({t for t in _REF_TARGET.findall(cpath.read_text(encoding="utf-8")) if t})
    assert not wrong, f"{path.name}: references pointing somewhere other than its citations page {want!r}: {wrong}"
    keys = registry_keys()
    assert set(refs) <= set(defs), f"{path.name}: references without a note on {cpath.name}: {sorted(set(refs) - set(defs))}"
    assert set(defs) <= set(refs), f"{path.name}: notes on {cpath.name} nothing references: {sorted(set(defs) - set(refs))}"
    canon = canon_keys()
    bad = []
    for fid, body in defs.items():
        form = footnote_form(body, canon)
        if form == "absence":
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
    assert footnote_form("no publicly readable source (searched 2026-09-06: x)" + ' <a class="fnback" href="../cities/p.html#fnref-1">back</a>', canon) == "absence", "a back link to the research page (feature 211)"
    assert footnote_form('<a href="SOURCES.html#k-2"><code>k-2</code></a> - 「a summary, not a page」' + fnback, canon).startswith("links the key to")
    assert footnote_form('no publicly readable source (searched 2026-09-06: x) <a href="https://x.y"><code>k</code></a>' + fnback, canon) == "an absence note carries no key and no link"
    assert footnote_form("something else entirely" + fnback, canon) is None


@pytest.mark.parametrize("path", _finding_files(), ids=lambda p: p.name)
def test_every_key_on_a_sources_roster_is_quoted_by_a_footnote_in_its_section(path: pathlib.Path) -> None:
    """The roster is what the modal reads; the footnotes are where the quotes live; a key on the roster that no
    footnote of the section quotes is a reference that is not being quoted."""
    text = path.read_text(encoding="utf-8")
    _refs, defs = footnotes(text, citations_of(path).read_text(encoding="utf-8"))
    body = text.split('<section class="citations">')[0]
    heads = [(m.start(), int(m.group(1))) for m in _HEADING.finditer(body)]
    unquoted = []
    for i, (a, level) in enumerate(heads):
        # a section runs to the next heading of the SAME or a HIGHER level: an <h2>'s roster is quoted anywhere in
        # its <h3> subsections too (the servant-housing entry of cities/government.html keeps its roster at the top)
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
_TRANSLATION_NOTE = re.compile(r"\((?:[^()]*;\s*)?(?:translated from the|machine translation|the source.s own English|translation:)", re.I)
_BLOCK = re.compile(r"<(p|li|h[2-4])\b[^>]*>(.*?)</\1>", re.S)
#: English quotes carry macrons (daimyō), curly quotes and the source's own dashes, so "not ASCII" is not "foreign".
#: Foreign is a NON-LATIN script (CJK, kana, hangul, Cyrillic, Greek...) or, for a Latin-script language, a run of its
#: function words - German is the one the record quotes (the `waldrand-dewiki` fixture). The stated limit (spec 202
#: FR-002): a Latin-script foreign quote outside that list reads as English here; the sweep and quote-check carry it.
_NON_LATIN = re.compile(r"[\u0370-\u03ff\u0400-\u04ff\u0590-\u06ff\u0e00-\u0e7f\u1100-\u11ff\u3000-\u30ff\u3400-\u9fff\uac00-\ud7af\uf900-\ufaff\uff00-\uffef]")
_GERMAN = re.compile(r"\b(und|der|die|das|von|mit|nach|sich|ist|ein|eine|nicht|auch|bei|zum|zur|des|dem|wird|werden|oder)\b")


def _looks_foreign(passage: str) -> bool:
    return bool(_NON_LATIN.search(passage)) or len(_GERMAN.findall(passage)) >= 2


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


@pytest.mark.parametrize("path", _finding_files() + [citations_of(p) for p in _finding_files()] + [pathlib.Path(RESEARCH_DIR, "SOURCES.html")], ids=lambda p: str(p.relative_to(RESEARCH_DIR)))
def test_a_foreign_language_quote_is_a_marked_translation(path: pathlib.Path) -> None:
    bad = unmarked_foreign_quotes(path.read_text(encoding="utf-8"))
    assert not bad, f"{path.name}: {len(bad)} foreign-language quote(s) with no translation note (feature 202):\n" + "\n".join(bad[:8])


def test_the_translation_form_is_told_apart() -> None:
    """The German and Korean fixtures fire; the marked form and the anchor pass; ASCII passes."""
    de = "<li>「Ein idealer Waldrand gliedert sich von außen nach innen」 (an ideal forest edge)</li>"
    ko = "<li>「동구숲 7,149 727」 (Table 8)</li>"
    ok = "<li>「An ideal forest edge is layered from outside in」 (translated from the German by this project; original: 「Ein idealer Waldrand gliedert sich von außen nach innen」)</li>"
    assert unmarked_foreign_quotes(de) and unmarked_foreign_quotes(ko)
    assert unmarked_foreign_quotes(ok) == [] and unmarked_foreign_quotes("<p>「plain ascii quote here」</p>") == []
    assert unmarked_foreign_quotes("<li>「the daimyō’s rice — stored (1603–1867)」 (English with macrons and the source's dashes)</li>") == []
