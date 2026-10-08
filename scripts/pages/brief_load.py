#!/usr/bin/env python3
"""How many research questions a page-session brief ASSIGNS (feature 274 D1): the one count the write cap rests on.

    brief_load.py <record dir> <brief> ...     prints `<kind or write> <count> <brief>` and the sections counted

WHY (feature 274, research R1). After feature 250 the cost per thing checked held, but the largest context doubled,
and it was the write sessions: a write session's cost follows its turn count (r = 0.92), groups had grown to twice
R11's size, and because every turn re-reads the context so far a session's cost grows roughly with the square of its
length. One 272 write session cost 24.5 M over 109 turns. So a WRITE session takes at most four questions (CAP), and
the runner counts every brief with this helper before it starts one, whatever generator wrote it (spec, round 3: a
required declaration would have broken the other features' generators until each changed).

WHAT IS COUNTED - only what the brief assigns (spec, round 4): the `## Your items` section (to the next `## `), and
the `**Your questions:**` and `**Your pairs**` lines or blocks. Never a "do not edit" paragraph, which names other
sessions' sections and would count them. Since feature 303 a question is named by its stem number, which is unique
across the record (`research/questions/NNNN-<slug>.html`):
  - in the check-brief form, `Q=NNNN` (or `Q=NNNN, NNNN`) counts one each; a pair (`KIND=X (Q=NNNN)`) one per question;
  - in an item line, every four-digit number inside a backtick span (`0412`, `0215, 0221`) that is a stem on disk;
    code and fact-check references (`file.py:195-304`, `fc:2113`) are stripped first;
  - a line naming no question counts one question per distinct item id (`B30`, `D52`), and at least one.
It errs toward over-counting, the safe side for a cap. Prototyped on the real briefs of 269, 271 and 272 (plan D1).

THE EXEMPT KINDS (spec, Edge Cases). A brief that is not a group's writing declares one line,
`<!-- page-load: kind=<kind> -->`: `check` (a check-and-apply session, which the cap does not cover), `assertions`
(feature 250's FR-002 briefs, many assertions inside existing questions), `split` (splitting an over-cap question) or
`handover` (a group handed to another feature). Any other kind is refused, and so is a brief that assigns nothing
countable and declares no kind: the count never fails open.
"""

from __future__ import annotations

import math
import pathlib
import re
import sys

CAP = 4
KINDS = ("check", "assertions", "split", "handover")
KIND_LINE = re.compile(r"<!--\s*page-load:\s*kind=([\w-]+)\s*-->")
STEM = re.compile(r"^(\d{4})-[^.]+(?:\.drawing)?\.html$")
CODE_REF = re.compile(r"[\w/.-]+\.(?:py|json|md|js|svg|txt|sh)(?::[\d,-]+)?|\b[a-z]+:\d[\d,-]*")
Q_LIST = re.compile(r"Q=(\d{4}(?:\s*,\s*\d{4})*)")
NUMBER = re.compile(r"(?<![\d.])\d{4}(?![\d])")
ITEM_ID = re.compile(r"\b[A-Z]{1,2}\d{2,3}\b")


def stems(record: pathlib.Path) -> set[int]:
    """Every question's number in the record (`<record>/questions/NNNN-<slug>.html`). Derived, never listed, so a
    question added later is counted without an edit here."""
    q = record / "questions"
    return {int(m.group(1)) for f in q.glob("[0-9][0-9][0-9][0-9]-*.html") if (m := STEM.match(f.name))} if q.is_dir() else set()


def declared(text: str) -> str:
    """The kind the brief declares, or "" when it declares none."""
    m = KIND_LINE.search(text)
    return m.group(1) if m else ""


def assignment_lists(text: str) -> tuple[str, str]:
    """(the `## Your items` section, the `**Your questions:**` and `**Your pairs**` blocks) - all a brief assigns."""
    m = re.search(r"^## Your items[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    items = m.group(1) if m else ""
    blocks = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"\*\*Your (?:questions|pairs)\b", line):
            block = [line]
            for nxt in lines[i + 1 :]:
                if not nxt.strip() or re.match(r"\*\*|#|\d+\.\s", nxt):
                    break
                block.append(nxt)
            blocks.append("\n".join(block))
    return items, "\n".join(blocks)


def count(text: str, record: pathlib.Path) -> tuple[int, list[str]]:
    """(questions assigned, what was counted: `NNNN` for a question, the item id for a new question)."""
    on_disk = stems(record)
    items, blocks = assignment_lists(text)
    found: set[int] = {int(n) for m in Q_LIST.finditer(blocks) for n in re.findall(r"\d{4}", m.group(1))}
    new: list[str] = []
    for line in re.split(r"\n(?=- )", items):
        if not line.startswith("- "):
            continue
        clean = CODE_REF.sub(" ", line)
        got = {int(n) for m in Q_LIST.finditer(clean) for n in re.findall(r"\d{4}", m.group(1))}
        got |= {int(n) for span in re.findall(r"`([^`]*)`", clean) for n in NUMBER.findall(span)}
        got &= on_disk
        if got:
            found |= got
        else:
            ids = list(dict.fromkeys(ITEM_ID.findall(line.split("**")[0])))
            new += ids or [line[2:].split()[0]]
    detail = [f"{n:04d}" for n in sorted(found)] + new
    return len(found) + len(new), detail


def load(text: str, record: pathlib.Path) -> tuple[str, int, list[str]]:
    """(the declared kind or "", questions assigned, what was counted)."""
    n, detail = count(text, record)
    return declared(text), n, detail


def split_names(brief: pathlib.Path, n: int) -> list[str]:
    """The briefs a group of `n` questions splits into, at most CAP each: `v2-write.md` -> `v2a-write.md`, `v2b-...`."""
    stem = brief.stem
    group, tail = (stem[: -len("-write")], "-write") if stem.endswith("-write") else (stem, "")
    return [f"{group}{chr(97 + i)}{tail}{brief.suffix}" for i in range(math.ceil(n / CAP))]


def refusal(brief: pathlib.Path, text: str, record: pathlib.Path) -> str:
    """Why the runner must not start this brief, or "" when it may."""
    kind, n, detail = load(text, record)
    if kind:
        return "" if kind in KINDS else f"it declares kind={kind}, which is not an exempt kind ({', '.join(KINDS)})"
    if n == 0:
        return ("it assigns nothing the count can read (no `## Your items`, `**Your questions:**` or `**Your pairs**` naming "
                f"a question) and declares no kind - add `<!-- page-load: kind=<{'|'.join(KINDS)}> -->` if it is not a group's writing")
    if n > CAP:
        parts = split_names(brief, n)
        return (f"it assigns {n} questions ({', '.join(detail)}); a write session takes at most {CAP} (feature 274: a write "
                f"session's cost grows with the square of its length). Split it into {len(parts)} briefs of at most {CAP} - "
                f"{', '.join(parts)} - each with its own handoff, and queue them one after another; or, for a deliberate larger "
                "load, set WRITE_CAP_OK='<reason>'")
    return ""


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: brief_load.py <record dir> <brief> ...", file=sys.stderr)
        return 2
    record = pathlib.Path(argv[0])
    bad = 0
    for b in map(pathlib.Path, argv[1:]):
        text = b.read_text(encoding="utf-8")
        kind, n, detail = load(text, record)
        why = refusal(b, text, record)
        bad += bool(why)
        print(f"{kind or 'write'} {n} {b.name}: {', '.join(detail) or '-'}" + (f"\n  REFUSED: {why}" if why else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
