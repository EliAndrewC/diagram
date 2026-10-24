#!/usr/bin/env python3
"""Feature 414 (diagram#15, the GM's addition to question 2): each Mitsui Bunko good's price in each Edo sub-period the
series reaches, in silver monme and in days of the same city's unskilled day wage - this project's arithmetic from the
GPIH transcription (Bassino 2006) of Mitsui Bunko 1989, Tables 6-8.

    python3 -I mitsui_periods.py <path to Japan_1710-1871.xls>

The sub-periods follow the series' own spans and the dated events of the record's 0290: Kyoto 1741-1762 and 1791-1817
(after the 1736 recoinage, before the 1818 one), 1818-1829 (the recoinage years), 1830-1858 (the Tenpo famine and after,
to the treaty ports), 1859-1871 (the open ports' inflation); Edo's four years of 1710-1716 (debased coin) stand alone.
A period's figure is the mean of its yearly means (a year's two seasons averaged). Days of wage: the period's mean price
over its mean day wage in the same city (Kyoto and Edo; Osaka has no wage column, so it is given in monme only). The
change between periods is the ratio of their means. Kyoto's salt changes its unit in 1791 (the series falls to a third
in one year), so Kyoto salt before 1791 is left out. Reads the sheets through mitsui_stability.py's own reader.
"""

from __future__ import annotations

import importlib.util
import pathlib
import statistics
import sys

import xlrd

_spec = importlib.util.spec_from_file_location("mitsui_stability", pathlib.Path(__file__).with_name("mitsui_stability.py"))
ms = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ms)

PERIODS = {
    "Kyoto": ((1741, 1762), (1791, 1817), (1818, 1829), (1830, 1858), (1859, 1871)),
    "Edo": ((1710, 1716), (1818, 1829), (1830, 1858), (1859, 1871)),
    "Osaka": ((1818, 1829), (1830, 1858), (1859, 1871)),
}
UNITS = {"White rice": "koku", "Mugi": "koku", "White wheat": "koku", "Glutinous rice": "koku", "Salt": "koku",
         "Miso": "10 kan", "Soy sauce": "koku", "Vinegar": "koku", "Sake": "koku", "Tea (zencha)": "kin", "Tobacco": "kin",
         "Charcoal": "10 kan", "Burning wood": "10 kan", "Lamp oil": "koku", "Candle": "100 monme", "Day laborers": "day"}


def period_mean(y: dict[int, float], lo: int, hi: int) -> tuple[float, int]:
    v = [p for t, p in y.items() if lo <= t <= hi]
    return (statistics.fmean(v), len(v)) if v else (float("nan"), 0)


def main(path: str) -> None:
    book = xlrd.open_workbook(path)
    data = {city: ms.series(book, sheet) for city, sheet in ms.SHEETS.items()}
    for city, periods in PERIODS.items():
        wage = ms.yearly(data[city].get("Day laborers", {}))
        print(f"\n## {city}: mean price in silver monme (days of the city's day wage) [years]\n")
        print("| good (unit) | " + " | ".join(f"{a}-{b}" for a, b in periods) + " | last pre-1859 period over first |")
        print("|---|" + "---|" * (len(periods) + 1))
        for good, s in data[city].items():
            y = ms.yearly(s)
            if city == "Kyoto" and good == "Salt":
                y = {t: v for t, v in y.items() if t >= 1791}
            cells, means = [], []
            for lo, hi in periods:
                m, n = period_mean(y, lo, hi)
                w, wn = period_mean(wage, lo, hi)
                means.append(m)
                if n == 0:
                    cells.append("-")
                elif wn and good != "Day laborers":
                    cells.append(f"{m:.3g} ({m / w:.3g} d) [{n}]")
                else:
                    cells.append(f"{m:.3g} [{n}]")
            pre = [m for (lo, hi), m in zip(periods, means) if hi <= 1858 and m == m]
            ratio = f"x{pre[-1] / pre[0]:.2f}" if len(pre) > 1 else "-"
            print(f"| {good} ({UNITS.get(good, '?')}) | " + " | ".join(cells) + f" | {ratio} |")


if __name__ == "__main__":
    main(sys.argv[1])
