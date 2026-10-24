"""What a historical amount of money was worth, shown on hover (feature 413, diagram#14).

The GM, 2026-10-24, through gm-assistant: *"I think that I am going to want a tooltip where we don't just explain that
this was the copper coin, but we translate the amount of money based on different ways of understanding it."* So an
amount the author marks - `<span class="money" data-amount="20" data-coin="mon">20 mon</span>`, its era named by
`data-era` on the span or on the nearest element around it that carries one - is converted here, at build time, into the
text its hover box shows: goods dollars (what it bought), wage dollars (the same share of a laborer's day) and Rokugani
coin, each the per-unit figure of gm-assistant's table times the amount ("Multiply by the amount shown", the issue).

THE TABLE IS GM-ASSISTANT'S. `research/assets/money-conversions.json` is a copy of its
`webapp/l7r/money/data/conversions.json`, refreshed by `make money-conversions` (`scripts/record/money_conversions.py`);
nothing here computes a price. An era it has not built yet may be marked only when `research/assets/money-eras-awaiting.json`
lists it (FR-008), so a typo is never taken for an era to come; such an amount keeps the glossary tooltip alone.

THE ERA IS THE AUTHOR'S CHOICE, NEVER THE BUILD'S (the asker, #14: *"no automatic fallback in the build. Choosing the era is
a judgment the author makes while marking the amount, not something the build infers"*). An amount paid in another place or
time than its era carries `data-paid="<place> <year>"`; the box then says "at <era> prices". How far an era may be borrowed
is NOT a check here: the asker's first default, "within about 25 years", was withdrawn by the GM as having no basis (#14,
2026-10-24), and the rule waits on the measured price stability of diagram#15. The money system is checked as the coin being
one of the era's units.

Research: money conversion on the record's site - NONE: presentation of gm-assistant's conversion table
"""

from __future__ import annotations

import html
import json
import os
import re
from dataclasses import dataclass, field
from typing import Any

CONVERSIONS = "money-conversions.json"
AWAITING = "money-eras-awaiting.json"
#: Rokugani coin, in sen (gm-assistant's `coins.py`: 1 koku = 10 bu = 100 zeni = 1,000 sen; the canon is `l7r.md` "Money").
COINS = (("koku", 1000), ("bu", 100), ("zeni", 10), ("sen", 1))
SEN_PER = dict(COINS)

_TAG = re.compile(r"<(/?)([a-zA-Z][\w-]*)((?:\"[^\"]*\"|'[^']*'|[^'\">])*)>")
_ATTR = re.compile(r'([\w-]+)\s*=\s*"([^"]*)"')
_VOID = frozenset({"br", "hr", "img", "meta", "link", "input", "wbr", "col", "source"})
#: Elements the record leaves unclosed: one ends where the next of its kind opens (`record_units.py`'s _BLOCK reads them so).
_AUTO = frozenset({"p", "li", "td", "th", "tr", "dd", "dt"})
_AMOUNT = re.compile(r"^\s*(\d[\d,]*(?:\.\d+)?)\s*(?:-\s*(\d[\d,]*(?:\.\d+)?))?\s*$")
_YEARS = re.compile(r"(\d{3,4})(?:\s*-\s*(\d{1,4}))?")


@dataclass(frozen=True)
class Table:
    """The vendored conversion table's eras, and the era ids awaiting their row."""

    eras: dict[str, Any] = field(default_factory=dict)
    awaiting: dict[str, Any] = field(default_factory=dict)


def _read_json(path: str) -> dict[str, Any]:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return {}
    return data if isinstance(data, dict) else {}


def load(record_dir: str) -> Table:
    """The table and the awaiting list beside the record; a missing file reads as empty."""
    assets = os.path.join(record_dir, "assets")
    return Table(_read_json(os.path.join(assets, CONVERSIONS)).get("eras", {}), _read_json(os.path.join(assets, AWAITING)))


def years(text: str) -> tuple[int, int] | None:
    """The span a text names, '1745-1754', '1745-54' or '1766', as (first, last); None when it names no year."""
    found = list(_YEARS.finditer(text))
    if not found:
        return None
    m = found[-1]
    first = int(m.group(1))
    if not m.group(2):
        return first, first
    tail = m.group(2)
    last = int(str(first)[: len(str(first)) - len(tail)] + tail) if len(tail) < len(str(first)) else int(tail)
    return first, last


def short_years(text: str) -> str:
    """'1745-1754' -> '1745-54', as the asker wrote it; anything else as written."""
    span = years(text)
    if span is None or span[0] == span[1] or str(span[0])[:2] != str(span[1])[:2]:
        return text
    return f"{span[0]}-{str(span[1])[2:]}"


def fmt(sen: int) -> str:
    """Exact Rokugani coin: 3215 -> '3 koku 2 bu 1 zeni 5 sen' (gm-assistant's `coins.fmt`)."""
    parts = []
    for coin, per in COINS:
        count, sen = divmod(sen, per)
        if count:
            parts.append(f"{count:,} {coin}")
    return " ".join(parts) or "0 sen"


def everyday(sen: int) -> str:
    """The two largest coins an amount needs, rounded, 'about' when rounded (gm-assistant's `coins.everyday`)."""
    if sen < SEN_PER["bu"]:
        return fmt(sen)
    names = [c for c, _ in COINS]
    big = next(c for c, per in COINS if sen >= per)
    small = names[names.index(big) + 1]
    rounded = round(sen / SEN_PER[small]) * SEN_PER[small]
    text = fmt(rounded)
    return text if rounded == sen else f"about {text}"


def rokugani(sen: float) -> str:
    """A Rokugani sum: under 10 sen to a tenth of a sen, else `everyday` (gm-assistant's `conversions.rokugani`)."""
    return f"{sen:.1f} sen" if sen < 10 else everyday(round(sen))


def dollars(x: float, scale: float | None = None) -> str:
    """To the cent under $100 (the issue's worked example: $41.71), the dollar under $10,000, three figures above; `scale`
    (a range's larger end) sets the precision, so both ends of a range read alike."""
    big = x if scale is None else scale
    if big < 100:
        return f"${x:,.2f}"
    if big < 10000:
        return f"${round(x):,}"
    return f"${round(x, 3 - len(str(int(big)))):,.0f}"


def _dollars(ends: tuple[float, ...]) -> str:
    return "-".join(dollars(e, max(ends)) for e in ends)


def box(amount: tuple[float, ...], label: str, unit: dict[str, Any], era: dict[str, Any], borrowed: bool) -> str:
    """The hover box's text for one amount (one figure, or the two ends of a range) at one era's row."""
    goods = _dollars(tuple(a * unit["goods_dollars"] for a in amount))
    wages = _dollars(tuple(a * unit["wage_dollars"] for a in amount))
    sen = " to ".join(rokugani(a * unit["rokugan_sen"]) for a in amount)
    lines = [f"{label}: about {goods} in goods, {wages} in wages, {sen} in Rokugan"]
    if borrowed:
        lines.append(f"at {era['place']} {short_years(era['years'])} prices")
    left = era.get("goods_left_out") or []
    lines.append(f"{era['place']} {era['years']}: {era.get('basket_coverage', '')}" + (f"; leaves out {', '.join(g.lower() for g in left)}" if left else ""))
    if era.get("confidence"):
        lines.append(era["confidence"])
    return "\n".join(lines)


def _attrs(raw: str) -> dict[str, str]:
    return {k: html.unescape(v) for k, v in _ATTR.findall(raw)}


def _inherited(stack: list[dict[str, str]], own: dict[str, str], name: str) -> str | None:
    if name in own:
        return own[name]
    for attrs in reversed(stack):
        if name in attrs:
            return attrs[name]
    return None


def _check(own: dict[str, str], stack: list[dict[str, str]], text: str, where: str, table: Table) -> tuple[str | None, str | None]:
    """(the box text, None) for an amount converted; (None, the refusal) for a bad mark; (None, None) for an amount whose
    era is awaiting its row, which keeps the glossary tooltip alone (FR-005)."""
    said = f"{where}: the amount {text!r}"
    era_id = _inherited(stack, own, "data-era")
    if not era_id:
        return None, f"{said} names no era - put data-era=\"<era id>\" on it or on an element around it (feature 413)"
    m = _AMOUNT.match(own.get("data-amount", ""))
    if not m:
        return None, f"{said} has data-amount={own.get('data-amount', '')!r} - a number, or two joined by a hyphen (\"15-20\")"
    amount = tuple(float(g.replace(",", "")) for g in m.groups() if g)
    coin = own.get("data-coin", "")
    paid = _inherited(stack, own, "data-paid")
    era = table.eras.get(era_id)
    if era is None:
        if era_id in table.awaiting:
            return None, None
        known = ", ".join(sorted([*table.eras, *table.awaiting])) or "none"
        return None, f"{said} names era {era_id!r}, which the conversion table does not have and research/assets/{AWAITING} does not list (known: {known})"
    unit = era.get("units", {}).get(coin)
    if unit is None:
        return None, f"{said} names coin {coin!r}, which era {era_id!r} has no unit for (it has: {', '.join(era.get('units', {}))})"
    if paid is not None and years(paid) is None:
        return None, f"{said} has data-paid={paid!r} with no year - write \"<place> <year>\" or \"<place> <year>-<year>\""
    return box(amount, text, unit, era, paid is not None), None


def annotate(markup: str, where: str, table: Table) -> tuple[str, list[str]]:
    """`markup` with each converted amount's box text written into its span as `data-def`, and the refusals, each naming
    `where` and the amount. Markup with no `class="money"` is returned as it is."""
    if 'class="money"' not in markup:
        return markup, []
    out: list[str] = []
    errors: list[str] = []
    stack: list[tuple[str, dict[str, str]]] = []
    last = 0
    for m in _TAG.finditer(markup):
        closing, name, raw = m.group(1), m.group(2).lower(), m.group(3)
        if closing:
            names = [n for n, _ in stack]
            if name in names:
                while stack and stack.pop()[0] != name:
                    pass
            continue
        if name in _VOID or raw.rstrip().endswith("/"):
            continue
        if name in _AUTO and stack and stack[-1][0] == name:
            stack.pop()
        own = _attrs(raw)
        if name == "span" and own.get("class") == "money":
            end = markup.find("</span>", m.end())
            text = re.sub(r"<[^>]+>", "", markup[m.end() : end if end >= 0 else len(markup)]).strip()
            text = html.unescape(text)
            tip, error = _check(own, [a for _, a in stack], text, where, table)
            if error:
                errors.append(error)
            if tip is not None:
                out.append(markup[last : m.end() - 1])
                out.append(f' data-def="{html.escape(tip)}">')
                last = m.end()
        stack.append((name, own))
    out.append(markup[last:])
    return "".join(out), errors
