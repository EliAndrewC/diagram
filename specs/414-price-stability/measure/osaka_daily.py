#!/usr/bin/env python3
"""Feature 414 (diagram#15): how far Osaka's rice price moved day to day, week to week, month to month and season to season -
this project's arithmetic from the RIEB early-modern economic database (近世経済データベース), which takes the Mitsui house's
Osaka exchange office diary (日記録): the day's rice price (米相場) from 1787 to 1871.

    python3 -I osaka_daily.py <path to the database's .xlsx>

The archived copy: /diagram/.specify/source-archive/d2/d2aae944e8db/20261019T161020Z/served.xlsx (sheet 相場帳; columns 和暦,
西暦, 月日, ..., 米相場). Dates are lunar: a day's index is year*360 + (month-1)*30 + day, so a lag of 30 is one lunar month,
360 one lunar year. Rows of an intercalary month (閏) are left out - their index would collide with the month they repeat. A
pair is two quoted days exactly the lag apart; the measure is the standard deviation of their log change, the same as
mitsui_stability.py's. "to 1858" leaves out 1859-1871 (the treaty-port inflation). Miyamoto 1975 warns that the brand of rice
quoted changed from year to year, so lags of a year and more mix brands; the short lags are within a year's quotes.
"""

from __future__ import annotations

import math
import re
import statistics
import sys

import openpyxl

LAGS = {"1 day": 1, "7 days": 7, "1 month": 30, "3 months": 90, "6 months": 180, "1 year": 360}
_YEAR = re.compile(r"(\d{4})")
_MD = re.compile(r"^(\d{1,2})月(\d{1,2})日$")


def prices(path: str) -> dict[int, tuple[int, float]]:
    """{day index: (year, rice price)} for every day with a quoted rice price, intercalary months left out."""
    ws = openpyxl.load_workbook(path, read_only=True)["相場帳"]
    rows = ws.iter_rows(values_only=True)
    header = None
    out: dict[int, tuple[int, float]] = {}
    for row in rows:
        if header is None:
            if row and row[0] == "和暦":
                header = list(row)
            continue
        y = _YEAR.search(str(row[1] or ""))
        md = _MD.match(str(row[2] or "").strip())
        rice = row[header.index("米相場")]
        if not (y and md) or not isinstance(rice, (int, float)) or rice <= 0:
            continue
        year, month, day = int(y.group(1)), int(md.group(1)), int(md.group(2))
        out[year * 360 + (month - 1) * 30 + day] = (year, float(rice))
    return out


def table(p: dict[int, tuple[int, float]], last: int) -> list[str]:
    q = {k: v for k, v in p.items() if v[0] <= last}
    lines = ["| lag | SD of log change | pairs |", "|---|---|---|"]
    for label, lag in LAGS.items():
        ch = [math.log(q[k + lag][1] / v[1]) for k, v in q.items() if k + lag in q]
        sd = statistics.stdev(ch) if len(ch) > 2 else float("nan")
        lines.append(f"| {label} | {100 * sd:.1f}% | {len(ch)} |")
    return lines


def main(path: str) -> None:
    p = prices(path)
    years = sorted({v[0] for v in p.values()})
    print(f"Osaka rice, the Mitsui exchange office's daily quotes: {len(p)} days, {years[0]}-{years[-1]}\n")
    for last, label in ((1858, "to 1858"), (1871, "whole")):
        print(f"## {label}\n")
        print("\n".join(table(p, last)))
        print()


if __name__ == "__main__":
    main(sys.argv[1])
