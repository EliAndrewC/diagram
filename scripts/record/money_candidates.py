#!/usr/bin/env python3
"""Every amount of money in the record a built era could convert, and whether it is marked (feature 413, plan D6).

The tooltip converts an amount only when its author marks it (`<span class="money" ...>`, `record/money.py`). This lists
every amount still unmarked in any fragment under `research/questions/` - questions, drawing pages and their notes - whose
coin is a unit of an era the vendored table carries, with the years its block names (else its page's heading), those within
`CLOSE_YEARS` of a built era first. EVERY amount listed is owed a decision (the plan review of 2026-10-24: the duty must not
stop at the ones whose years match): marked, or named in `specs/413-money-tooltip-on-the-record/backfill.md` with the reason
it is passed over, one line each: `- <file stem> | <amount as written> | <reason>`, or `- <file stem> | * | <reason>` where
one reason covers every amount the fragment still holds unmarked - never one within CLOSE_YEARS of a built era, each of which
is named on its own line.

    money_candidates.py           list them                                   `make money-candidates`
    money_candidates.py --check   exit 1 while one is neither marked nor named `make money-candidates CHECK=1`
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass

QUESTIONS = os.path.join("research", "questions")
TABLE = os.path.join("research", "assets", "money-conversions.json")
BACKFILL = os.path.join("specs", "413-money-tooltip-on-the-record", "backfill.md")
CLOSE_YEARS = 25
#: The period's other Japanese coin words, listed whether or not a built era's row has a unit for them (the plan review of
#: 2026-10-24: an amount in a coin its row lacks, a gold bu at Kyoto 1745-54, is passed over with that reason, never unseen).
COINS_ALSO = ("mon", "monme", "kanmon", "ryo", "bu", "shu", "koban", "yen", "sen", "rin")

_COMMENT = re.compile(r"<!--.*?-->", re.S)
_BLOCK = re.compile(r"<(p|li|blockquote|td|dd|h[1-4])\b([^>]*)>(.*?)(?:</\1>|(?=<(?:p|li|blockquote|td|dd|h[1-4])\b)|\Z)", re.S)
_HEADING = re.compile(r"<h[12][^>]*>(.*?)</h[12]>", re.S)
_TAG = re.compile(r"<[^>]+>")
_MARKED = re.compile(r'<span class="money"[^>]*>(.*?)</span>', re.S)
_NUMBER = r"\d[\d,]*(?:\.\d+)?(?:\s*-\s*\d[\d,]*(?:\.\d+)?)?"
_YEAR = re.compile(r"(?<!\d)(1[0-9]{3})(?!\d)")
_NOTE_MARK = re.compile(r'data-note="([^"]+)"')
_ROW = re.compile(r"^-\s*(?P<stem>[^|]+?)\s*\|\s*(?P<amount>[^|]+?)\s*\|\s*(?P<reason>.+?)\s*$")


@dataclass(frozen=True)
class Amount:
    stem: str
    text: str
    years: tuple[int, ...]
    near: str  # the built era within CLOSE_YEARS of its years, or ""
    context: str = ""  # the text around it, the amount in [[ ]]


def _plain(markup: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub("", markup))).strip()


def _eras(root: str) -> dict[str, tuple[int, int, frozenset[str]]]:
    try:
        with open(os.path.join(root, TABLE), encoding="utf-8") as fh:
            eras = json.load(fh).get("eras", {})
    except FileNotFoundError:
        return {}
    out = {}
    for era_id, row in eras.items():
        ys = [int(y) for y in _YEAR.findall(row.get("years", ""))]
        if ys:
            out[era_id] = (min(ys), max(ys), frozenset(row.get("units", {})))
    return out


def _cited_years(folder: str, page: str) -> dict[str, tuple[int, ...]]:
    """{note key: the years named by the body blocks of `page` that cite it}."""
    try:
        with open(os.path.join(folder, page), encoding="utf-8") as fh:
            text = _COMMENT.sub("", fh.read())
    except FileNotFoundError:
        return {}
    out: dict[str, tuple[int, ...]] = {}
    for block in _BLOCK.finditer(text):
        years = tuple(int(y) for y in _YEAR.findall(_plain(block.group(3))))
        for key in _NOTE_MARK.findall(block.group(3)):
            out[key] = out.get(key, ()) + years
    return out


def amounts(root: str = ".") -> list[Amount]:
    """Every unmarked amount in a coin a built era carries, those near a built era first."""
    eras = _eras(root)
    coins = sorted({*COINS_ALSO, *(c for _, _, units in eras.values() for c in units)}, key=len, reverse=True)
    amount_re = re.compile(rf"(?<![\w.]){_NUMBER}\s+(?:{'|'.join(map(re.escape, coins))})(?![\w])")
    out: list[Amount] = []
    folder = os.path.join(root, QUESTIONS)
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".html") or name.endswith(".originals.html"):
            continue
        with open(os.path.join(folder, name), encoding="utf-8") as fh:
            text = _COMMENT.sub("", fh.read())
        stem = name[: -len(".html")]
        heading = _HEADING.search(text)
        page_years = tuple(int(y) for y in _YEAR.findall(_plain(heading.group(1)))) if heading else ()
        # a note's years are those of the sentence that cites it: the body blocks carrying its mark, in the page it belongs to
        cited = _cited_years(folder, name[: -len(".notes.html")] + ".html") if name.endswith(".notes.html") else {}
        for block in _BLOCK.finditer(text):
            raw = block.group(3)
            note = _NOTE_MARK.search(block.group(2))
            # every amount inside a marked span counts as marked: "9 ryo 2 bu" is one amount, marked once as 9.5 ryo
            marked = Counter(x.group(0) for m in _MARKED.findall(raw) for x in amount_re.finditer(_plain(m)))
            plain = _plain(raw)
            years = tuple(int(y) for y in _YEAR.findall(plain)) or (cited.get(note.group(1), ()) if note else ()) or page_years
            for m in amount_re.finditer(plain):
                found = m.group(0)
                if marked[found] > 0:
                    marked[found] -= 1
                    continue
                coin = found.split()[-1]
                near = next((e for e, (a, b, units) in eras.items() if coin in units and any(a - CLOSE_YEARS <= y <= b + CLOSE_YEARS for y in years)), "")
                context = plain[max(0, m.start() - 240) : m.start()] + "[[" + found + "]]" + plain[m.end() : m.end() + 60]
                out.append(Amount(stem, found, years, near, context))
    return sorted(out, key=lambda a: (a.near == "", a.stem))


def passed_over(root: str = ".") -> set[tuple[str, str]]:
    try:
        with open(os.path.join(root, BACKFILL), encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except FileNotFoundError:
        return set()
    return {(m["stem"], m["amount"]) for m in map(_ROW.match, lines) if m}


def _named(a: Amount, named: set[tuple[str, str]]) -> bool:
    """Passed over by its own line, or by its fragment's `*` line (one reason for every amount the fragment holds)."""
    # ...never a `*` line for an amount near a built era (the plan review of 2026-10-24, round 3): the era is a judgment made
    # per amount, so each of those is marked or named on its own line
    # nor for an amount whose years the script cannot find, which it cannot show to be far (the plan review's round 4)
    return (a.stem, a.text) in named or (not a.near and bool(a.years) and (a.stem, "*") in named)


def main(argv: list[str] | None = None, root: str = ".") -> int:
    ap = argparse.ArgumentParser(description="every unmarked amount of money a built era could convert")
    ap.add_argument("--check", action="store_true", help="exit 1 while an amount is neither marked nor named in backfill.md")
    args = ap.parse_args(argv)
    named = passed_over(root)
    owed = [a for a in amounts(root) if not _named(a, named)]
    for a in owed:
        years = ",".join(map(str, a.years[:4])) or "no year"
        print(f"{'NEAR ' + a.near if a.near else 'far':<20} {a.stem} | {a.text} | {years}")
    if args.check and owed:
        print(f"money-candidates: {len(owed)} amount(s) neither marked nor named in {BACKFILL} - mark each (feature 413, record/money.py) or add `- <stem> | <amount> | <reason>`", file=sys.stderr)
        return 1
    print(f"money-candidates: {len(owed)} amount(s) owed a decision")
    return 0


if __name__ == "__main__":
    sys.exit(main())
