#!/usr/bin/env python3
"""What a pattern can find on a research page, listed for `record-format` (feature 251, FR-005).

WHY. `record-format` reads a page as its casual reader does and reports three things that reader should
not meet: vocabulary the glossary does not define, visible text addressed to a session, and the
document's own history (feature 209, GM 2026-09-07). Two of those have a mechanical half - a `Grounds:`
field, a task id, a module path and a run of kanji are found by a regular expression, exactly and for
no tokens - and the census of feature 251 (research R1) measured `record-format` as the second most
expensive check per run, nearly all of it input re-read turn after turn. So the listing is done here
and handed over; the agent confirms or dismisses each line and keeps what no pattern can find: a
history passage, an instruction to a future session, a hard word in plain English.

WHAT IT READS. The page's VISIBLE text only - HTML comments are where session notes belong, so what is
inside one is already right and is never listed. A vocabulary candidate the glossary covers, as a term
or as a variant, is dropped: every occurrence of it is already a hover tooltip.

This decides nothing and never edits. A line here is a CANDIDATE: `<code>` holds source keys as well as
engine identifiers, and an `<em>` holds a quoted ruling as often as a Japanese word.
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import sys

GLOSSARY = ".claude/skills/diagram/l7r/diagram/interactive/assets/glossary.json"
RESEARCH = ".claude/skills/diagram/research"

#: (label, pattern) over a section's visible text - the session-note shapes `record-format` names.
SESSION_NOTES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("field", re.compile(r"\b(?:Grounds|Evidence)\s*:")),
    ("feature number", re.compile(r"\b[Ff]eature\s+\d{2,3}\b|\bF\d{3}\b")),
    ("task id", re.compile(r"\bT\d{2,3}\b")),
    ("spec path", re.compile(r"\bspecs/\d{3}-[\w-]+")),
    # a hyphenated target, or one of the bare ones - "make sure" in a quoted ruling is not a make target
    ("make target", re.compile(r"\bmake\s+(?:[a-z][a-z0-9]*(?:-[a-z0-9]+)+|quick|done|maps|map|audit|claim|tick|verify|soak)\b")),
    ("file path", re.compile(r"(?<![\w/.:-])(?:[\w.-]+/)+[\w.-]+\.(?:py|sh|json|md)\b|\b[\w-]+\.(?:py|sh)\b")),
    ("fetch verdict", re.compile(r"\b(?:SUMMARY-ONLY|UNFETCHABLE|NOT-FOUND|CONTRADICTED|NOT-READABLE|READ)\b|\bnot re-sourced\b|\bleftover\b")),
)
IDENTIFIER = re.compile(r"^[A-Za-z_][\w.]*(?:\(\))?$")
CJK = re.compile(r"[぀-ヿ㐀-䶿一-鿿가-힯]{2,}")
#: a Latin binomial is recognized only where the page italicizes it - as plain text the shape matches
#: any capitalized word followed by a lower-case one, and a noisy candidate costs the agent tokens.
BINOMIAL = re.compile(r"[A-Z][a-z]{3,} [a-z]{4,}")


def strip_comments(markup: str) -> str:
    return re.sub(r"<!--.*?-->", "", markup, flags=re.S)


def text_of(markup: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", markup))).strip()


def sections(markup: str) -> list[tuple[str, str]]:
    """(heading, body markup) per `<h2>`/`<h3>`; what precedes the first heading is `(top)`."""
    body = strip_comments(re.sub(r"<(script|style)\b.*?</\1>", "", markup, flags=re.S | re.I))
    parts = re.split(r"(<h[23]\b[^>]*>.*?</h[23]>)", body, flags=re.S | re.I)
    out, heading = [], "(top)"
    for part in parts:
        if re.match(r"<h[23]\b", part, re.I):
            heading = text_of(part)
        elif part.strip():
            out.append((heading, part))
    return out


def sentence_around(text: str, start: int, end: int) -> str:
    left = max(text.rfind(". ", 0, start), text.rfind("? ", 0, start)) + 1
    right = text.find(". ", end)
    return text[left : right + 1 if right >= 0 else len(text)].strip()[:240]


def known_terms(glossary: dict) -> set[str]:
    """Every glossary term and variant, case-folded."""
    known: set[str] = set()
    for term, entry in glossary.items():
        known.add(term.casefold())
        known.update(str(v).casefold() for v in (entry.get("variants") or []))
    return known


def session_notes(markup: str) -> list[dict]:
    text = text_of(markup)
    found = [{"class": "SESSION NOTE", "label": label, "match": m.group(0), "sentence": sentence_around(text, m.start(), m.end())} for label, pat in SESSION_NOTES for m in pat.finditer(text)]
    for m in re.finditer(r"<code>([^<]+)</code>", markup):
        inner = html.unescape(m.group(1)).strip()
        linked = re.search(r"<a\b[^>]*>\s*$", markup[: m.start()]) is not None
        if not linked and IDENTIFIER.match(inner) and ("_" in inner or "." in inner or inner.endswith("()")):
            at = text.find(inner)
            found.append({"class": "SESSION NOTE", "label": "engine identifier", "match": inner, "sentence": sentence_around(text, max(at, 0), max(at, 0) + len(inner))})
    return found


def vocabulary(markup: str, known: set[str]) -> list[dict]:
    text = text_of(markup)
    seen: set[str] = set()
    found: list[dict] = []

    def add(label: str, term: str) -> None:
        key = term.casefold()
        if key in seen or key in known or not term:
            return
        seen.add(key)
        at = text.find(term)
        found.append({"class": "VOCABULARY", "label": label, "match": term, "sentence": sentence_around(text, max(at, 0), max(at, 0) + len(term))})

    for m in re.finditer(r"<(em|i)\b[^>]*>(.*?)</\1>", markup, flags=re.S | re.I):
        term = text_of(m.group(2))
        if 0 < len(term.split()) <= 3 and not re.search(r"[\"“”.:!?]", term):
            add("binomial" if BINOMIAL.fullmatch(term) else "italic term", term)
    for m in CJK.finditer(text):
        add("CJK term", m.group(0))
    return found


def prepass(markup: str, glossary: dict) -> list[dict]:
    """Per section: its heading and the candidate lines, session notes first."""
    known = known_terms(glossary)
    return [{"section": heading, "items": session_notes(body) + vocabulary(body, known)} for heading, body in sections(markup)]


def render(page: str, listing: list[dict]) -> str:
    total = sum(len(s["items"]) for s in listing)
    lines = [f"record-prepass: {page} - {len(listing)} sections, {total} candidates (each is for record-format to confirm or dismiss)"]
    for sec in listing:
        if not sec["items"]:
            continue
        lines.append(f"## {sec['section']}")
        for it in sec["items"]:
            lines.append(f"  {it['class']} [{it['label']}] {it['match']!r} - {it['sentence']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("page", help="a research page name: hamlets, cities/tango, citations/hamlets, SOURCES")
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", default="")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root)
    name = args.page.removesuffix(".html")
    path = root / RESEARCH / f"{name}.html"
    if not path.is_file():
        print(f"record-prepass: no such page - wanted {path}", file=sys.stderr)
        return 2
    gloss_path = root / GLOSSARY
    glossary = json.loads(gloss_path.read_text(encoding="utf-8")) if gloss_path.is_file() else {}
    listing = prepass(path.read_text(encoding="utf-8"), glossary)
    print(render(name, listing))
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps({"page": name, "sections": listing}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
