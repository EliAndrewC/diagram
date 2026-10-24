#!/usr/bin/env python3
"""Feature 414 (diagram#15): how far Mitsui Bunko's prices moved at each time scale, good by good, and how far the three
cities stood apart - this project's arithmetic from the GPIH transcription (Bassino 2006) of Mitsui Bunko 1989, Tables 6-8.

    python3 -I mitsui_stability.py <path to Japan_1710-1871.xls>

The file: https://gpih.ucdavis.edu/files/Japan_1710-1871.xls (spring and autumn quarterly averages, silver monme; Kyoto
1713, 1741-1762, 1791-1871; Edo 1710-1716, 1818-1871; Osaka 1713, 1818-1871). The measure is the standard deviation of
log changes, the one Jacks, O'Rourke and Williamson use (NBER w14748): over half a year (consecutive seasons), and over 1,
5, 10, 25 and 50 years between yearly means (the mean of a year's two seasons; a year with one season takes that one).
Each lag is computed over the year pairs both present, so a gap in the series shortens a lag's sample rather than bridging
it. "to 1858" leaves out the treaty-port inflation of 1859-1871; "whole" keeps it. Seasonality: the mean log of autumn
over spring in the same year. Spreads: per good, the mean and SD of log(Edo/Kyoto) and log(Osaka/Kyoto) in the years
1818-1858 all three carry. Prices are in each city's own unit per the sheet's headers (the same for the three cities).
"""

from __future__ import annotations

import math
import statistics
import sys

import xlrd

SHEETS = {"Kyoto": "Mitsui Bunko Kyoto T6", "Edo": "Mitsui Bunko Edo T7", "Osaka": "Mitsui Bunko Osaka T8"}
GOODS = ("White rice", "Mugi", "Salt", "Miso", "Soy sauce", "Sake", "Charcoal", "Burning wood", "Buring wood", "Lamp oil", "Candle", "Day laborers")
LAGS = (1, 5, 10, 25, 50)


def series(book: xlrd.Book, sheet: str) -> dict[str, dict[tuple[int, int], float]]:
    """{good: {(year, season 0 spring / 1 autumn): price}} from the quarterly block (the columns before the yearly block)."""
    s = book.sheet_by_name(sheet)
    names = [str(c.value).strip() for c in s.row(3)]
    stop = next(i for i in range(4, len(names)) if names[i] == "" and i > 3)
    cols = {i: names[i] for i in range(3, stop) if names[i]}
    out: dict[str, dict[tuple[int, int], float]] = {}
    year = None
    for r in range(6, s.nrows):
        row = s.row(r)
        if isinstance(row[0].value, float) and row[0].value > 1000:
            year = int(row[0].value)
        season = {"Spring": 0, "Fall": 1}.get(str(row[2].value).strip())
        if year is None or season is None:
            continue
        for i, name in cols.items():
            v = row[i].value
            if isinstance(v, float) and v > 0:
                good = next((g for g in GOODS if name.startswith(g)), name)
                out.setdefault("Burning wood" if good == "Buring wood" else good, {})[(year, season)] = v
    return out


def yearly(s: dict[tuple[int, int], float]) -> dict[int, float]:
    by: dict[int, list[float]] = {}
    for (y, _), v in s.items():
        by.setdefault(y, []).append(v)
    return {y: statistics.fmean(vs) for y, vs in by.items()}


def sd_log(pairs: list[tuple[float, float]]) -> tuple[float, int]:
    ch = [math.log(b / a) for a, b in pairs]
    return (statistics.stdev(ch) if len(ch) > 2 else float("nan")), len(ch)


def stability(s: dict[tuple[int, int], float], last: int) -> dict[str, tuple[float, int]]:
    s = {k: v for k, v in s.items() if k[0] <= last}
    keys = sorted(s)
    half = [(s[a], s[b]) for a, b in zip(keys, keys[1:]) if (b[0] * 2 + b[1]) - (a[0] * 2 + a[1]) == 1]
    out = {"half-year": sd_log(half)}
    y = yearly(s)
    for lag in LAGS:
        out[f"{lag} yr"] = sd_log([(y[t], y[t + lag]) for t in sorted(y) if t + lag in y])
    seas = [math.log(s[(t, 1)] / s[(t, 0)]) for t in sorted({k[0] for k in s}) if (t, 0) in s and (t, 1) in s]
    out["autumn/spring"] = ((statistics.fmean(seas) if seas else float("nan")), len(seas))
    return out


def pct(x: float) -> str:
    return "-" if math.isnan(x) else f"{100 * x:.1f}%"


def main(path: str) -> None:
    book = xlrd.open_workbook(path)
    data = {city: series(book, sheet) for city, sheet in SHEETS.items()}
    for last, label in ((1858, "to 1858"), (1871, "whole")):
        print(f"\n## SD of log changes, {label} (n = pairs)\n")
        print("| city | good | half-year | 1 yr | 5 yr | 10 yr | 25 yr | 50 yr | autumn over spring |")
        print("|---|---|---|---|---|---|---|---|---|")
        for city, goods in data.items():
            for good, s in goods.items():
                st = stability(s, last)
                cells = [f"{pct(v)} ({n})" for k, (v, n) in st.items() if k != "autumn/spring"]
                m, n = st["autumn/spring"]
                print(f"| {city} | {good} | " + " | ".join(cells) + f" | {pct(m)} ({n}) |")
    print("\n## Spreads between cities, 1818-1858: mean and SD of the log ratio to Kyoto (n = years)\n")
    print("| good | Edo / Kyoto | Osaka / Kyoto |")
    print("|---|---|---|")
    ky = {g: yearly(s) for g, s in data["Kyoto"].items()}
    for good in ky:
        cells = []
        for city in ("Edo", "Osaka"):
            other = yearly(data[city].get(good, {}))
            r = [math.log(other[t] / ky[good][t]) for t in range(1818, 1859) if t in other and t in ky[good]]
            cells.append(f"{100 * (math.exp(statistics.fmean(r)) - 1):+.0f}% (SD {pct(statistics.stdev(r))}, {len(r)})" if len(r) > 2 else "-")
        print(f"| {good} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main(sys.argv[1])
