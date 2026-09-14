#!/usr/bin/env python3
"""Feature 242's work list for ONE page: the bare items the readers named, by tier, located in the HTML.

Usage: python3 specs/242-cite-the-unfootnoted-assertions/measure/worklist.py <page.html> [--json]

Imports the census's own parsers (`inventory_census.py`) so this is exactly FR-001's filter applied to
one page - never a second reading. For each item it extracts the sentence the reader quoted (the first
quoted span of the block), strips tags and normalizes whitespace, and looks for a distinctive window of
it in the research page's visible text; it prints the line the window lands on, or NOT-LOCATED, so the
`<sup>` can be placed mechanically where the match is unambiguous and by hand where it is not. An item
whose located sentence already carries a `<sup class="fn">` is flagged FOOTNOTED (an R7 closure or work
already done) so it is skipped rather than double-noted.
"""
from __future__ import annotations

import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from inventory_census import REPORTS, TIERS, carries_marker, confidence, items, page_of  # noqa: E402

RESEARCH = HERE.parents[2] / ".claude" / "skills" / "diagram" / "research"


def quoted(block: str) -> str:
    m = re.search(r'"(.+?)"\s+(?:-|—|–)\s', block) or re.search(r'"(.+?)"', block)
    return m.group(1) if m else ""


def visible(s: str) -> str:
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def section_of(text: str, upto: int) -> str:
    sec = ""
    for m in re.finditer(r"(?m)^###\s+(?:§\s*)?(.+)$", text[:upto]):
        sec = m.group(1).strip()
    return sec


MARK = "⟦fn⟧"  # what a `<sup class="fn">` becomes in the marked rendering below
_BLOCK_START = re.compile(r"^\s*<(?:p|li|h[1-6]|td|th|dd|dt)\b")


def marked(s: str) -> str:
    """The visible text with every footnote mark kept as one MARK token, so a sentence can be asked
    whether it carries a note wherever the mark fell - on the line the window matched, on the wrapped
    continuation, or after the sentence's own period."""
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r'<sup\b[^>]*class="fn"[^>]*>.*?</sup>', MARK, s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def block_of(lines: list[str], hit: int) -> str:
    """The raw block element (a `<p>`, `<li>`, heading or cell) the hit line belongs to, joined."""
    lo = hit
    while lo > 0 and not _BLOCK_START.match(lines[lo]):
        lo -= 1
    hi = hit + 1
    while hi < len(lines) and not _BLOCK_START.match(lines[hi]):
        hi += 1
    return "\n".join(lines[lo:hi])


def sentence_status(block: str, window: str) -> str:
    """FOOTNOTED when the SENTENCE holding `window` carries a mark - inside it or immediately after its
    closing period - else LOCATED. The test used to be per LINE (`'<sup class="fn">' in lines[hit]`), and
    the handoff of 2026-09-14 found that reading noisy: most LOCATED items were marks on a wrapped
    continuation line or a mark placed after the period, so the residue could not be counted."""
    text = marked(block)
    i = text.find(window)
    if i < 0:
        return "LOCATED"
    starts = [text.rfind(sep, 0, i) for sep in (". ", "。", "! ", "? ")]
    start = max(starts) + 1 if max(starts) >= 0 else 0
    m = re.compile(r"[.。!?](?=\s|$)").search(text, i + len(window))
    end = m.end() if m else len(text)
    tail = re.match(r"(?:\s*" + re.escape(MARK) + r")*", text[end:])
    end += tail.end() if tail else 0
    return "FOOTNOTED" if MARK in text[start:end] else "LOCATED"


def locate(sentence: str, lines: list[str]) -> tuple[int, str]:
    """(1-based line, status) - the line whose visible text holds the longest clean window of the
    sentence, and whether that SENTENCE carries a footnote mark (`sentence_status`)."""
    s = visible(sentence).replace("...", " ").strip(" .")
    words = s.split()
    if len(words) < 4:
        return 0, "TOO-SHORT"
    vis = [visible(ln) for ln in lines]
    for size in (12, 9, 7, 5, 4):
        if len(words) < size:
            continue
        for start in range(0, len(words) - size + 1):
            window = " ".join(words[start : start + size])
            hits = [i for i, v in enumerate(vis) if window in v]
            if len(hits) == 1:
                return hits[0] + 1, sentence_status(block_of(lines, hits[0]), window)
            if len(hits) > 1:
                return hits[0] + 1, f"AMBIGUOUS({len(hits)})"
    return 0, "NOT-LOCATED"


def worklist(page: str) -> list[dict]:
    out: list[dict] = []
    page_path = RESEARCH / page
    lines = page_path.read_text(encoding="utf-8").splitlines() if page_path.is_file() else []
    for path in sorted(REPORTS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for block in items(text):
            at = text.index(block[:120])
            if page_of(text, at) != page or carries_marker(block):
                continue
            sentence = quoted(block)
            line, status = locate(sentence, lines) if lines else (0, "NO-PAGE")
            out.append(
                {
                    "tier": confidence(block),
                    "section": section_of(text, at),
                    "sentence": visible(sentence),
                    "line": line,
                    "status": status,
                    "block": re.sub(r"\s+", " ", block).strip(),
                    "report": path.name,
                }
            )
    order = {t: i for i, t in enumerate(TIERS)}
    out.sort(key=lambda d: (order.get(d["tier"], 99), d["line"] or 10**6))
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    page = sys.argv[1]
    rows = worklist(page)
    if "--json" in sys.argv:
        json.dump(rows, sys.stdout, ensure_ascii=False, indent=1)
        return 0
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"].split("(")[0]] = counts.get(r["status"].split("(")[0], 0) + 1
    print(f"{page}: {len(rows)} bare items; " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    for i, r in enumerate(rows, 1):
        print(f"{i:3}. [{r['tier']}] L{r['line']} {r['status']} | {r['section'][:50]} | {r['sentence'][:140]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
