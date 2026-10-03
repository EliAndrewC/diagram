"""*Not to be confused with:* - the list under a section a reader could mistake for another (feature 292, FR-016).

The GM, 2026-09-29: a section whose subject a reader could confuse with another's opens with *Not to be confused
with:* - each entry the other section's title, linked, and the record's definition of it - and the pairs are data,
kept once and always two-way, written by `make record` and never by hand.

So the pairs live in ONE file, `research/confusables.json` - a list of `{"a": "NNNN-<slug>.html#<id>", "b": "...",
"why": "<the difference>"}` - and a pair declared once puts an entry under BOTH sections. An entry is the other
section's heading, linked, and its definition: the first sentence of that section's opening paragraph, read from its
fragment at assembly, so it can never drift from what the section says. The `why` is for the next session (it says
what made the pair confusable); it is not shown.

A pair naming a section that does not exist is a refusal, not a silently missing list.

Research: plumbing - NONE
"""

from __future__ import annotations

import html
import json
import os
import re
from dataclasses import dataclass

from l7r.diagram.interactive.record import questions as qs

#: The pairs, kept once, beside the questions they join.
DATA = "confusables.json"
LABEL = "Not to be confused with:"
_H2 = re.compile(r'<h2 id="([^"]+)">(.*?)</h2>', re.S)
_P = re.compile(r"<p>(.*?)</p>", re.S)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_SUP = re.compile(r"<sup\b[^>]*>.*?</sup>", re.S)
_TAG = re.compile(r"<[^>]+>")
_SENTENCE = re.compile(r"(.+?[.!?])(?:\s|$)", re.S)


@dataclass(frozen=True)
class Pair:
    """Two sections a reader could mistake for each other: `NNNN-<slug>[.drawing].html#<heading id>` each."""

    a: str
    b: str


def load(record_dir: str) -> list[Pair]:
    """Every pair in the data file, in file order (none when there is no file)."""
    path = os.path.join(record_dir, DATA)
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [Pair(x["a"], x["b"]) for x in json.load(fh)]


def _split(ref: str) -> tuple[str, str]:
    page, _, anchor = ref.partition("#")
    return page, anchor


def _section(record: qs.Record, ref: str) -> str | None:
    """The text of the page `ref` names, when its heading is the anchor; else None."""
    file, anchor = _split(ref)
    page = record.by_file.get(file)
    return page.text if page is not None and page.heading_id == anchor else None


def _text(fragment_html: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub("", _SUP.sub("", fragment_html)))).strip()


def title(section: str) -> str:
    """A section's heading as its reader sees it."""
    m = _H2.search(section)
    return _text(m.group(2)) if m else ""


def definition(section: str) -> str:
    """The first sentence of a section's opening paragraph - the record's own definition of its subject."""
    body = _COMMENT.sub("", section)
    m = _P.search(body)
    if m is None:
        return ""
    text = _text(m.group(1))
    s = _SENTENCE.match(text)
    return s.group(1) if s else text


def unresolved(pairs: list[Pair], record: qs.Record) -> list[str]:
    """A message for each side of a pair that names no section, and for a pair joining a section to itself."""
    bad = []
    for p in pairs:
        if p.a == p.b:
            bad.append(f"`{p.a}` is paired with itself")
        for ref in (p.a, p.b):
            if _section(record, ref) is None:
                bad.append(f"`{ref}` (paired with `{p.b if ref == p.a else p.a}`) - no such section")
    return bad


def entries(file: str, pairs: list[Pair], record: qs.Record) -> dict[str, list[str]]:
    """{section id on this page: [entry html]} - each pair adds an entry under both of its sections. A link is written
    as the other page's file name, which the site resolves like any link in the record."""
    out: dict[str, list[str]] = {}
    for p in pairs:
        for here, there in ((p.a, p.b), (p.b, p.a)):
            page, anchor = _split(here)
            if page != file:
                continue
            other = _section(record, there) or ""
            entry = f'<li><a href="{_split(there)[0]}">{html.escape(title(other), quote=False)}</a>'
            gloss = definition(other)
            out.setdefault(anchor, []).append(entry + (f" - {html.escape(gloss, quote=False)}</li>" if gloss else "</li>"))
    return out


def write(page_html: str, file: str, pairs: list[Pair], record: qs.Record) -> str:
    """The page with the list written right after each paired section's heading."""
    for anchor, items in entries(file, pairs, record).items():
        m = re.search(rf'<h2 id="{re.escape(anchor)}">.*?</h2>', page_html, re.S)
        if m is None:
            continue  # `unresolved` has already refused a pair naming no section
        block = f'\n<div class="confusables"><p><em>{LABEL}</em></p>\n<ul>\n' + "\n".join(items) + "\n</ul></div>"
        page_html = page_html[: m.end()] + block + page_html[m.end() :]
    return page_html
