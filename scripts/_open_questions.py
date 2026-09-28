#!/usr/bin/env python3
"""`make open-questions` - every guess and every unfound source, read from where they are marked (feature 285).

WHY DERIVED. The GM, 2026-09-28: "a make target which assembles a list of guesses that could use a research pass is
better than trying to assemble something by hand, which then will drift out of date due to repeating ourselves in
multiple places." The record already labels each GUESS and writes an absence note for each source not found
(research/CLAUDE.md), so the list is those labels, collected; closing one in the record removes it here.

WHAT IT READS (specs/285 plan):
- the research record's QUESTION FRAGMENTS (`research/**/NNN-<id>.html` and the `.notes.html` beside each) - never an
  assembled page or a citations page, which repeat them (D1). HTML comments are session notes and are stripped (D2).
- every other tracked text file of the skill, outside `research/` and `tests/`, for a whole-word GUESS: a guess is
  sometimes marked only where it is coded or drawn (D7; research.md R2 found `compound.py`'s postern and two in the
  hand-drawn magistracy plans). Only the tooling's own logs are skipped: they repeat what a session typed elsewhere.

A QUESTION'S MAP FEATURES (D3), by three routes: a class's `Entry:` names it; a question a class names links to it
(one hop); an engine `.py` file quotes its anchor or its heading.

Usage: _open_questions.py --root <repo>
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

SKILL = ".claude/skills/diagram"
#: a question fragment: a three-digit prefix, the heading id, `.html` - its notes are the `.notes.html` beside it
_FRAGMENT = re.compile(r"^\d{3}-.+\.html$")
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_TAG = re.compile(r"<[^>]+>")
_HEADING = re.compile(r'<h2 id="([^"]+)">(.*?)</h2>', re.S)
_GUESS = re.compile(r"\bGUESS(?:ES)?\b")  # the label and its plural ("the shares are GUESSES")
_ABSENCE = "no publicly readable source"
_SETTLED = re.compile(r"\bsettled \d{4}-\d{2}-\d{2}\b")
_NOTE_LI = re.compile(r'<li data-note="([^"]+)"[^>]*>(.*?)</li>', re.S)
_LINK = re.compile(r'href="[^"#]*#([^"]+)"')
#: a block boundary: a paragraph, list item, heading or cell opens or closes - text on either side is a separate passage
_BOUNDARY = re.compile(r"</?(?:p|li|ul|ol|h[1-6]|td|th|tr|table|dd|dt|dl|blockquote|div|section)\b[^>]*>")
_SENTENCE_END = re.compile(r"(?<=[.?!])\s+(?=[A-Z(\"'])")
#: tracked files outside the record that repeat a source or are the tooling's own logs (D7)
_SKIP_OUTSIDE = re.compile(r"^(research|tests)/|^dev/(bypass-log|run-log|perf-log)/")


def visible(html: str) -> str:
    """The text a reader sees: comments dropped, tags dropped, whitespace folded."""
    return re.sub(r"\s+", " ", _TAG.sub("", _COMMENT.sub("", html))).strip()


def sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_END.split(text) if s.strip()]


def passages(html: str) -> list[str]:
    """The question's text split at block boundaries, comments dropped, tags still in (a note's marker is a tag)."""
    return [p for p in _BOUNDARY.split(_COMMENT.sub("", html)) if p.strip()]


def guess_sentences(html: str) -> list[str]:
    """Each sentence of the question's visible text carrying a GUESS label, once however many it carries."""
    out: list[str] = []
    for inner in passages(html):
        for s in sentences(visible(inner)):
            if _GUESS.search(s) and s not in out:
                out.append(s)
    return out


def claim_of(html: str, key: str) -> str:
    """The sentence of the question that carries the note `key`, or '' when none does."""
    mark = f'data-note="{key}"'
    for inner in passages(html):
        if mark not in inner:
            continue
        # the sentence is the text up to and including the marker, split as the reader reads it
        at = inner.index(mark)
        before = inner[: max(inner.rfind("<", 0, at), 0)]
        text = visible(before)
        parts = sentences(text)
        return parts[-1] if parts else text
    return ""


@dataclass
class Item:
    kind: str  # guess | absence | absence-settled
    text: str
    claim: str = ""


@dataclass
class Question:
    page: str
    anchor: str
    heading: str
    path: str
    links: set[str] = field(default_factory=set)
    items: list[Item] = field(default_factory=list)


def read_question(path: Path, root: Path) -> Question | None:
    html = path.read_text(encoding="utf-8")
    m = _HEADING.search(html)
    if not m:
        return None
    rel = path.relative_to(root / SKILL / "research")
    page = str(rel.parent)
    q = Question(page=page, anchor=m.group(1), heading=visible(m.group(2)), path=str(path.relative_to(root)))
    q.links = set(_LINK.findall(_COMMENT.sub("", html)))
    q.items = [Item("guess", s) for s in guess_sentences(html)]
    notes = path.with_name(path.name[: -len(".html")] + ".notes.html")
    if notes.exists():
        for key, li in _NOTE_LI.findall(_COMMENT.sub("", notes.read_text(encoding="utf-8"))):
            text = visible(li)
            if _ABSENCE in text:
                kind = "absence-settled" if _SETTLED.search(text) else "absence"
                q.items.append(Item(kind, text, claim_of(html, key)))
    return q


def questions(root: Path) -> list[Question]:
    base = root / SKILL / "research"
    out = []
    for path in sorted(base.rglob("*.html")):
        if path.name.endswith(".notes.html") or not _FRAGMENT.match(path.name):
            continue
        q = read_question(path, root)
        if q is not None:
            out.append(q)
    return out


def class_routes(entries: dict[str, list[str]], qs: Sequence[Question]) -> dict[str, list[str]]:
    """anchor -> the classes a question feeds: its own (`Entry:` names it) and, one hop, those of a question that links
    to it ('<class> (through <heading>)'). `entries` is class key -> the anchors its `Entry:` resolves to."""
    direct: dict[str, list[str]] = {}
    for key, anchors in sorted(entries.items()):
        for a in anchors:
            direct.setdefault(a, []).append(key)
    by_anchor = {q.anchor: q for q in qs}
    out: dict[str, list[str]] = {a: list(ks) for a, ks in direct.items()}
    for a, ks in direct.items():
        src = by_anchor.get(a)
        if src is None:
            continue
        for target in sorted(src.links):
            if target == a or target not in by_anchor:
                continue
            for k in ks:
                label = f"{k} (through '{src.heading}')"
                if k not in out.get(target, []) and label not in out.get(target, []):
                    out.setdefault(target, []).append(label)
    return out


def heading_key(question: str) -> str:
    """What a code comment quotes of a heading: the question up to its first '?' (a heading may carry its answer
    after it). No length floor: the short headings are cited by the engine too (plan review 2026-09-28: capitals
    240's "A castle has TWO gates" is cited by its heading alone), and research.md R5 found no stray match."""
    return question.split("?", 1)[0] + "?" if "?" in question else question


def code_citations(sources: dict[str, str], q: Question, heading_key: str) -> list[str]:
    """`file:line` of every engine line quoting the question's anchor or its heading."""
    out = []
    for path, text in sources.items():
        # most files quote neither: a whole-text search first keeps the line walk to the few that do (plan D6)
        if q.anchor not in text and not (heading_key and heading_key in text):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if q.anchor in line or (heading_key and heading_key in line):
                out.append(f"{path}:{n}")
    return out


def outside_guesses(files: dict[str, str]) -> list[tuple[str, int, str]]:
    out = []
    for path, text in sorted(files.items()):
        for n, line in enumerate(text.splitlines(), 1):
            if _GUESS.search(line):
                out.append((path, n, line.strip()))
    return out


def tracked(root: Path) -> list[str]:
    """The skill's tracked files, relative to the skill."""
    res = subprocess.run(["git", "-C", str(root / SKILL), "ls-files", "-z"], capture_output=True, text=True, check=True)
    return [p for p in res.stdout.split("\0") if p]


def outside_files(root: Path, names: Iterable[str]) -> dict[str, str]:
    out = {}
    for rel in names:
        if _SKIP_OUTSIDE.search(rel):
            continue
        try:
            out[rel] = (root / SKILL / rel).read_text(encoding="utf-8")
        except UnicodeDecodeError:  # a binary file (an image, a font) holds no label
            continue
    return out


def _engine(root: Path):  # noqa: ANN202 - the class registry and the one Entry: resolver
    skill = str(root / SKILL)
    if skill not in sys.path:
        sys.path.insert(0, skill)
    from l7r.diagram.interactive.classes import CLASSES
    from l7r.diagram.interactive.sources import question_text, research_questions

    return CLASSES, research_questions, question_text


def report(qs: Sequence[Question], routes: dict[str, list[str]], cites: dict[str, list[str]], outside: Sequence[tuple[str, int, str]]) -> str:
    open_qs = [q for q in qs if q.items]
    lines = ["OPEN RESEARCH QUESTIONS - read from the record and the tracked files now (feature 285)", ""]
    pages: dict[str, list[Question]] = {}
    for q in open_qs:
        pages.setdefault(q.page, []).append(q)
    tot = {"questions": 0, "guess": 0, "absence": 0, "absence-settled": 0}
    lines.append(f"{'page':<34} {'questions':>9} {'guesses':>8} {'absences':>9} {'settled':>8}")
    for page, pqs in sorted(pages.items()):
        c = {k: sum(1 for q in pqs for i in q.items if i.kind == k) for k in ("guess", "absence", "absence-settled")}
        lines.append(f"{page:<34} {len(pqs):>9} {c['guess']:>8} {c['absence']:>9} {c['absence-settled']:>8}")
        tot["questions"] += len(pqs)
        for k in c:
            tot[k] += c[k]
    lines.append(f"{'TOTAL':<34} {tot['questions']:>9} {tot['guess']:>8} {tot['absence']:>9} {tot['absence-settled']:>8}")
    areas: dict[str, int] = {}
    for path, _n, _t in outside:
        area = path.split("/")[0] if "/" in path else path
        areas[area] = areas.get(area, 0) + 1
    lines.append("")
    lines.append(f"GUESS lines outside the record: {len(outside)} ({', '.join(f'{a} {n}' for a, n in sorted(areas.items()))})")
    for page, pqs in sorted(pages.items()):
        lines += ["", "=" * 100, f"research/{page}", "=" * 100]
        for q in pqs:
            lines += ["", f"## {q.heading}", f"   {q.path}"]
            feeds = routes.get(q.anchor, []) + cites.get(q.anchor, [])
            lines.append("   map features: " + ("; ".join(feeds) if feeds else "no map feature found depending on it"))
            for it in q.items:
                if it.kind == "guess":
                    lines.append(f"   - GUESS: {it.text}")
                else:
                    tag = "UNSOURCED (searched twice, settled)" if it.kind == "absence-settled" else "UNSOURCED"
                    lines.append(f"   - {tag}: {it.claim or '(the claim is not marked in the text)'}")
                    lines.append(f"       {it.text}")
    lines += ["", "=" * 100, "GUESSES MARKED OUTSIDE THE RECORD", "=" * 100]
    last = None
    for path, n, text in outside:
        if path != last:
            lines += ["", path]
            last = path
        lines.append(f"   {n}: {text}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, required=True)
    args = ap.parse_args(argv)
    root = args.root.resolve()
    classes, research_questions, question_text = _engine(root)
    qs = questions(root)
    entries = {k: [q["url"].rsplit("#", 1)[1] for q in research_questions(fc.entry)] for k, fc in classes.items()}
    routes = class_routes(entries, qs)
    names = tracked(root)
    engine = {rel: (root / SKILL / rel).read_text(encoding="utf-8") for rel in names if rel.startswith("l7r/") and rel.endswith(".py")}
    cites = {q.anchor: code_citations(engine, q, heading_key(question_text(q.heading))) for q in qs if q.items}
    sys.stdout.write(report(qs, routes, cites, outside_guesses(outside_files(root, names))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
