#!/usr/bin/env python3
"""Every amount of money in the record a built era could convert, and whether it is marked (feature 413, plan D6).

The tooltip converts an amount only when its author marks it (`<span class="money" ...>`, `record/money.py`). This lists
every amount still unmarked in any fragment under `research/questions/` - questions, drawing pages and their notes - whose
coin is a coin word of these money systems, with the years its block names (else its page's heading, or for a note the sentence
citing it) and how many years it stands from the nearest built era carrying its coin, nearest first. The order decides nothing:
the GM withdrew the 25-year default (#14, 2026-10-24) and diagram#15 will measure a rule, so no distance in years is compared
here. EVERY amount listed is owed a decision: marked, or named in `specs/413-money-tooltip-on-the-record/backfill.md` with
the reason it is passed over, one line each: `- <file stem> | <amount as written> | <reason>`, or `- <file stem> | * | <reason>`
where one reason, the author's, covers every amount the fragment still holds unmarked.

    money_candidates.py           list them                                   `make money-candidates`
    money_candidates.py --check   exit 1 while one is neither marked nor named `make money-candidates CHECK=1`
    money_candidates.py --all --stem 0255 --context   one question's amounts, passed-over ones tagged, each with its text
                                                      `make money-candidates ALL=1 Q=0255 CONTEXT=1`
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
#: The era ids awaiting their row (FR-008): an amount may be marked with one now, so it counts as built here, carrying every coin
#: of COINS_ALSO until its row names its units (feature 412: the marks pass ran before gm-assistant's rows were vendored).
AWAITING = os.path.join("research", "assets", "money-eras-awaiting.json")
#: The awaiting eras' places whose money is these coins; any other place's era carries none of them until its row is vendored.
JAPAN_PLACES = frozenset({"Edo", "Kyoto", "Osaka"})
BACKFILL = os.path.join("specs", "413-money-tooltip-on-the-record", "backfill.md")
#: The period's other Japanese coin words, listed whether or not a built era's row has a unit for them (the plan review of
#: 2026-10-24: an amount in a coin its row lacks, a gold bu at Kyoto 1745-54, is passed over with that reason, never unseen).
COINS_ALSO = ("mon", "monme", "kanmon", "ryo", "bu", "shu", "koban", "yen", "sen", "rin")
#: The Chinese awaiting eras' coins, as gm-assistant confirmed them on diagram#13 (issuecomment-6390801447): `tael` (silver),
#: `cash` (copper; a string marked as its count) and `dollar` (the foreign silver dollar, cents its hundredths).
CHINA_COINS = ("tael", "cash", "dollar")
#: The places whose awaiting era carries them; the dollar only where it circulated in an era's years (Canton's 1830s trade,
#: Beijing's 1900s), never the inland Lower Yangzi eras of the 1680s and 1750s.
CHINA_PLACES = frozenset({"Beijing", "Songjiang", "Suzhou", "Canton"})
DOLLAR_PLACES = frozenset({"Canton", "Beijing"})
#: Each Chinese coin word the scanner finds, and the coin it is marked in: mace and candareens are tenths and hundredths of a
#: tael, wen, strings, guan and tiao count cash, cents are hundredths of a dollar. A Japanese word is its own coin.
CHINA_WORDS = {
    "tael": "tael", "taels": "tael", "mace": "tael", "candareen": "tael", "candareens": "tael",
    "cash": "cash", "wen": "cash", "string": "cash", "strings": "cash", "guan": "cash", "tiao": "cash", "diao": "cash",
    "dollar": "dollar", "dollars": "dollar", "cent": "dollar", "cents": "dollar",
}

_COMMENT = re.compile(r"<!--.*?-->", re.S)
_BLOCK = re.compile(r"<(p|li|blockquote|td|dd|h[1-4])\b([^>]*)>(.*?)(?:</\1>|(?=<(?:p|li|blockquote|td|dd|h[1-4])\b)|\Z)", re.S)
_HEADING = re.compile(r"<h[12][^>]*>(.*?)</h[12]>", re.S)
_TAG = re.compile(r"<[^>]+>")
_MARKED = re.compile(r'<span class="money"[^>]*>(.*?)</span>', re.S)
_NUMBER = r"\d[\d,]*(?:\.\d+)?(?:\s*-\s*\d[\d,]*(?:\.\d+)?)?"
_DOLLAR = r"\d[\d,]*(?:\.\d+)?(?:\s*-\s*\$?\d[\d,]*(?:\.\d+)?)?"
_YEAR = re.compile(r"(?<!\d)(1[0-9]{3})(?!\d)")
_NOTE_MARK = re.compile(r'data-note="([^"]+)"')
_ROW = re.compile(r"^-\s*(?P<stem>[^|]+?)\s*\|\s*(?P<amount>[^|]+?)\s*\|\s*(?P<reason>.+?)\s*$")


@dataclass(frozen=True)
class Amount:
    stem: str
    text: str
    years: tuple[int, ...]
    near: str  # the nearest built era carrying its coin, or "" (no year, or no era carries it)
    gap: int | None = None  # years from that era's span, 0 inside it
    context: str = ""  # the text around it, the amount in [[ ]]


def _plain(markup: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub("", markup))).strip()


def _read(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return {}
    return data if isinstance(data, dict) else {}


def _eras(root: str) -> dict[str, tuple[int, int, frozenset[str]]]:
    """{era id: (first year, last year, its coins)} - the vendored table's eras, then the awaiting ones it does not have yet."""
    eras = dict(_read(os.path.join(root, TABLE)).get("eras", {}))
    for era_id, row in _read(os.path.join(root, AWAITING)).items():
        if era_id not in eras and isinstance(row, dict):
            # a Chinese place's era carries the Chinese coins, never the Japanese: given them, a Japanese 1600 mon read 0 years
            # from beijing-1615, and record/money.py takes an awaiting era's coin on trust, so a wrong mark would build
            place = row.get("place")
            if place in JAPAN_PLACES:
                coins: tuple[str, ...] = COINS_ALSO
            elif place in CHINA_PLACES:
                coins = tuple(c for c in CHINA_COINS if c != "dollar" or place in DOLLAR_PLACES)
            else:
                coins = ()
            eras[era_id] = {"years": row.get("years", ""), "units": dict.fromkeys(coins)}
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
    """Every unmarked amount in a coin of these money systems, nearest a built era first (the order decides nothing)."""
    eras = _eras(root)
    coins = sorted({*COINS_ALSO, *CHINA_WORDS, *(c for _, _, units in eras.values() for c in units)}, key=len, reverse=True)
    # a dollar is written "$1.50" as often as "2 dollars": the sign is a coin word of its own (feature 412, session 6)
    amount_re = re.compile(rf"(?<![\w.]){_NUMBER}\s+(?:{'|'.join(map(re.escape, coins))})(?![\w])|(?<![\w$])\${_DOLLAR}")
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
                coin = "dollar" if found.startswith("$") else CHINA_WORDS.get(found.split()[-1], found.split()[-1])
                gaps = [(max(a - y, y - b, 0), e) for e, (a, b, units) in eras.items() if coin in units for y in years]
                gap, near = min(gaps) if gaps else (None, "")
                context = plain[max(0, m.start() - 240) : m.start()] + "[[" + found + "]]" + plain[m.end() : m.end() + 60]
                out.append(Amount(stem, found, years, near, gap=gap, context=context))
    return sorted(out, key=lambda a: (a.gap is None, a.gap if a.gap is not None else 0, a.stem))


def passed_over(root: str = ".") -> set[tuple[str, str]]:
    try:
        with open(os.path.join(root, BACKFILL), encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except FileNotFoundError:
        return set()
    return {(m["stem"], m["amount"]) for m in map(_ROW.match, lines) if m}


def _named(a: Amount, named: set[tuple[str, str]]) -> bool:
    """Passed over by its own line, or by its fragment's `*` line (one reason for every amount the fragment holds)."""
    # a `*` line covers every amount its fragment holds unmarked: no distance in years decides what it may cover (the plan review
    # of 2026-10-24 after the GM withdrew the 25-year default - a 25-year cut here was the withdrawn number under another name)
    return (a.stem, a.text) in named or (a.stem, "*") in named


def main(argv: list[str] | None = None, root: str = ".") -> int:
    ap = argparse.ArgumentParser(description="every unmarked amount of money a built era could convert")
    ap.add_argument("--check", action="store_true", help="exit 1 while an amount is neither marked nor named in backfill.md")
    ap.add_argument("--all", action="store_true", help="list the amounts backfill.md passes over too, each tagged [passed over]")
    ap.add_argument("--stem", default="", help="only the fragments whose file stem starts with this (a question's number)")
    ap.add_argument("--context", action="store_true", help="print the text around each amount under it, the amount in [[ ]]")
    args = ap.parse_args(argv)
    named = passed_over(root)
    found = [a for a in amounts(root) if a.stem.startswith(args.stem)]
    owed = [a for a in found if not _named(a, named)]
    for a in found if args.all else owed:
        years = ",".join(map(str, a.years[:4])) or "no year"
        where = f"{a.gap} yr from {a.near}" if a.gap is not None else "no year or no era"
        tag = " [passed over]" if _named(a, named) else ""
        print(f"{where:<28} {a.stem} | {a.text} | {years}{tag}")
        if args.context:
            print(f"    {a.context}")
    if args.check and owed:
        print(f"money-candidates: {len(owed)} amount(s) neither marked nor named in {BACKFILL} - mark each (feature 413, record/money.py) or add `- <stem> | <amount> | <reason>`", file=sys.stderr)
        return 1
    print(f"money-candidates: {len(owed)} amount(s) owed a decision")
    return 0


if __name__ == "__main__":
    sys.exit(main())
