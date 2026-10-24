#!/usr/bin/env python3
"""Feature 414 (diagram#15): how far Chinese prices moved at 1, 5, 10, 25 and 50 years, and their drift - this project's
arithmetic from two GPIH files.

    python3 -I qing_stability.py <China_rice_prices_961-1910.xls> <China_1730-1933_Allen_et_al.xls>

1. Kishimoto's Lower Yangzi rice, Suzhou area, 1584-1766, silver taels a shi (GPIH `China_rice_prices_961-1910.xls`, sheet
   "Kishmoto rice series", as transcribed by Lindert 2006 from Kishimoto 1997, Table 3.1) - a market series, year by year.
2. Allen et al.'s bare-bones basket cost in grams of silver for Suzhou, Canton and Beijing (`China_1730-1933_Allen_et_al.xls`,
   sheet "Figures2-6", the second block) - a reconstruction: Beijing's rice is the Yangzi series rescaled and its oils indexed to
   flour (Allen et al. 2011 say so), so its swings are not Beijing's own; said beside every figure from it.

The measure is the standard deviation of log changes between yearly values, as in `mitsui_stability.py`; each lag counts only
year pairs both present. Drift: the mean change a decade and a century from the first to the last value of each span.
"""

from __future__ import annotations

import math
import statistics
import sys

import xlrd

LAGS = (1, 5, 10, 25, 50)


def kishimoto(path: str) -> dict[int, float]:
    s = xlrd.open_workbook(path).sheet_by_name("Kishmoto rice series")
    out = {}
    for r in range(5, s.nrows):
        y, v = s.cell_value(r, 0), s.cell_value(r, 1)
        if isinstance(y, float) and isinstance(v, float) and v > 0:
            out[int(y)] = v
    return out


def allen(path: str) -> dict[str, dict[int, float]]:
    s = xlrd.open_workbook(path).sheet_by_name("Figures2-6")
    names = [str(c.value).strip() for c in s.row(7)]
    cols = {i: names[i] for i in range(11, 19) if names[i] in ("Beijing", "Suzhou", "Canton")}
    out: dict[str, dict[int, float]] = {n: {} for n in cols.values()}
    for r in range(8, s.nrows):
        y = s.cell_value(r, 10)
        if not isinstance(y, float):
            continue
        for i, n in cols.items():
            v = s.cell_value(r, i)
            if isinstance(v, float) and v > 0:
                out[n][int(y)] = v
    return out


def row(label: str, y: dict[int, float], last: int) -> str:
    y = {t: v for t, v in y.items() if t <= last}
    cells = []
    for lag in LAGS:
        ch = [math.log(y[t + lag] / y[t]) for t in sorted(y) if t + lag in y]
        cells.append(f"{100 * statistics.stdev(ch):.1f}% ({len(ch)})" if len(ch) > 2 else f"- ({len(ch)})")
    a, b = min(y), max(y)
    per = math.log(y[b] / y[a]) / (b - a)
    drift = f"{100 * (math.exp(10 * per) - 1):+.1f}%/decade, {100 * (math.exp(100 * per) - 1):+.0f}%/century ({a}-{b}, {len(y)} years)"
    return f"| {label} | " + " | ".join(cells) + f" | {drift} |"


def main(rice: str, basket: str) -> None:
    print("## SD of log change between yearly values (n = pairs), and drift\n")
    print("| series | 1 yr | 5 yr | 10 yr | 25 yr | 50 yr | drift |")
    print("|---|---|---|---|---|---|---|")
    print(row("Kishimoto, Suzhou-area rice, taels a shi (market)", kishimoto(rice), 1766))
    for city, y in allen(basket).items():
        note = " (reconstruction)" if city == "Beijing" else ""
        print(row(f"Allen et al., {city} bare-bones basket, g of silver{note}, to 1850", y, 1850))
        print(row(f"Allen et al., {city} bare-bones basket, g of silver{note}, to 1910", y, 1910))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
