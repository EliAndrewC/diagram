"""Feature 194 (GM 2026-09-06): a reference QUOTES the passage that supports the assertion - the mechanical half.

The record's citation form (research/CLAUDE.md): `<sup class="fn"><a id="fnref-n" href="#fn-n">n</a></sup>` after an
assertion, and in the page's `<section class="footnotes"><ol>` a `<li id="fn-n">` with the key link and the quote. What a test can hold: every reference resolves and every
definition is used; every definition names a registry key and carries a quotation; every key on a section's
`**Sources:**` roster is quoted by a footnote in that section ("no point in including a reference if it is not
being quoted"). What only the `quote-check` agent can hold - the quote is verbatim on the page, it supports the
assertion, and every assertion has one - is its job, before a research edit lands."""

from __future__ import annotations

import pathlib
import re

import pytest

from l7r.diagram.interactive.sources import RESEARCH_DIR

#: a second reference to the same note carries no id (ids are unique; the back-link returns to the first)
_REF = re.compile(r'<sup class="fn"><a (?:id="fnref-(?:\d+)" )?href="#fn-(\d+)">\1</a></sup>')
_DEF = re.compile(r'<li id="fn-(\d+)">(.*?)</li>', re.S)
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


def footnotes(text: str) -> tuple[list[str], dict[str, str]]:
    """(reference ids in reading order, {definition id: body})."""
    defs = {m.group(1): m.group(2).strip() for m in _DEF.finditer(text)}
    return [m.group(1) for m in _REF.finditer(text)], defs


def registry_keys() -> set[str]:
    src = pathlib.Path(RESEARCH_DIR, "SOURCES.html").read_text(encoding="utf-8")
    return set(re.findall(r'<h3 id="([a-z0-9][a-z0-9-]*)"', src))


#: Feature 195 (GM 2026-09-06): a footnote CITES only a page on the public internet where its quote can be read, or
#: it is an ABSENCE note - no key, no link, what was searched. The one carve-out, by KEY: the GM's own campaign
#: notes (`l7r.md`, `budgets.md`), canon rather than a source claimed to support a historical point, keep their
#: registry link. Derived from the registry rather than listed, so a new canon key is covered the day it lands.
_ABSENCE = re.compile(r"^no publicly readable source \(searched \d{4}-\d{2}-\d{2}:")
_ENTRY = re.compile(r'<h3 id="([a-z0-9][a-z0-9-]*)">.*?</h3>\s*<p>(.*?)</p>', re.S)
_HREF_OF_KEY = re.compile(r'<a href="([^"]*)"><code>[a-z0-9][a-z0-9-]*</code></a>')


def canon_keys() -> set[str]:
    src = pathlib.Path(RESEARCH_DIR, "SOURCES.html").read_text(encoding="utf-8")
    return {m.group(1) for m in _ENTRY.finditer(src) if re.search(r"\bl7r\.md\b|\bbudgets\.md\b", m.group(2))}


def footnote_form(body: str, canon: set[str]) -> str | None:
    """'citation', 'absence', or the defect (feature 195 FR-002). A citation links its key to an http(s) page - the
    registry is not a page where a quote can be read - unless the key is canon; an absence note carries no key link
    and no URL at all (its only anchor is the back link)."""
    if _ABSENCE.match(body):
        if "<code>" in body or re.search(r'href="(?!#fnref-)', body):
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
    refs, defs = footnotes(text)
    keys = registry_keys()
    assert set(refs) <= set(defs), f"{path.name}: references without a definition: {sorted(set(refs) - set(defs))}"
    assert set(defs) <= set(refs), f"{path.name}: definitions nothing references: {sorted(set(defs) - set(refs))}"
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
    assert footnote_form('<a href="SOURCES.html#k-2"><code>k-2</code></a> - 「a summary, not a page」' + fnback, canon).startswith("links the key to")
    assert footnote_form('no publicly readable source (searched 2026-09-06: x) <a href="https://x.y"><code>k</code></a>' + fnback, canon) == "an absence note carries no key and no link"
    assert footnote_form("something else entirely" + fnback, canon) is None


@pytest.mark.parametrize("path", _finding_files(), ids=lambda p: p.name)
def test_every_key_on_a_sources_roster_is_quoted_by_a_footnote_in_its_section(path: pathlib.Path) -> None:
    """The roster is what the modal reads; the footnotes are where the quotes live; a key on the roster that no
    footnote of the section quotes is a reference that is not being quoted."""
    text = path.read_text(encoding="utf-8")
    _refs, defs = footnotes(text)
    body = text.split('<section class="footnotes">')[0]
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
