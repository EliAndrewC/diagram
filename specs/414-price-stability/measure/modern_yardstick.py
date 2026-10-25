#!/usr/bin/env python3
"""Feature 414 (diagram#15): how far prices move today, under paper money - this project's arithmetic from the DBnomics
mirror of the US Bureau of Labor Statistics and the Statistics Bureau of Japan, the yardstick beside the Edo and Qing series.

    python3 -I modern_yardstick.py <dbnomics.json> <rough-rice.json>

The first file is the response of this URL (one request, every series in it, fetched 2026-10-24):
https://api.db.nomics.world/v22/series?series_ids=BLS/cu/CUUR0000SA0,BLS/ap/APU0000701312,BLS/ap/APU0000701111,BLS/ap/APU0000708111,STATJP/CPIa/001,STATJP/CPIm/001,STATJP/CPIm/003&observations=1&format=json
The second is Yahoo Finance's daily chart of CBOT rough rice futures (the front contract, ten years to 2026-10-23):
https://query1.finance.yahoo.com/v8/finance/chart/ZR=F?range=10y&interval=1d
Its day and week are trading days (a week is five of them), and a continuous front-month series steps when one contract
rolls into the next, so its SD carries those steps too.
The measure is the one mitsui_stability.py uses, the standard deviation of log changes (population SD, as a percent):
month to month between consecutive months both present, over 12 months between the same month a year apart, and year to
year between annual means (the mean of a year's 12 months; a year short of a month has none). Drift is the mean log
change a year, a decade and a century from the first value to the last. The US series are not seasonally adjusted, so
the monthly SD carries the seasons; the 12-month SD does not.
"""

from __future__ import annotations

import json
import math
import statistics
import sys


def load(path: str) -> dict[str, dict[str, float]]:
    """{series code: {period: value}} - every numeric observation of every series in one DBnomics response."""
    docs = json.load(open(path, encoding="utf-8"))["series"]["docs"]
    return {f"{d['dataset_code']}/{d['series_code']}": {p: v for p, v in zip(d["period"], d["value"]) if isinstance(v, (int, float))}
            for d in docs}


def ym(p: str) -> tuple[int, int]:
    y, m = p.split("-")
    return int(y), int(m)


def key(y: int, m: int) -> str:
    return f"{y}-{m:02d}"


def sd(xs: list[float]) -> str:
    return f"{100 * statistics.pstdev(xs):.2f}% ({len(xs)})" if len(xs) > 1 else f"- ({len(xs)})"


def lag_changes(s: dict[str, float], lo: int, hi: int, months: int) -> list[float]:
    """log changes over `months` between monthly values both present, the later one dated lo..hi (years)."""
    out = []
    for p, v in s.items():
        y, m = ym(p)
        if not lo <= y <= hi:
            continue
        t = (y * 12 + m - 1) - months
        q = key(t // 12, t % 12 + 1)
        if q in s and s[q] > 0 and v > 0:
            out.append(math.log(v / s[q]))
    return out


def annual_means(s: dict[str, float]) -> dict[int, float]:
    years: dict[int, list[float]] = {}
    for p, v in s.items():
        years.setdefault(ym(p)[0], []).append(v)
    return {y: sum(v) / 12 for y, v in years.items() if len(v) == 12}


def year_changes(a: dict[int, float], lo: int, hi: int) -> list[float]:
    return [math.log(a[y] / a[y - 1]) for y in range(lo, hi + 1) if y in a and y - 1 in a]


def drift(first: tuple[str, float], last: tuple[str, float], years: float) -> str:
    r = math.log(last[1] / first[1]) / years
    return (f"{first[0]} {first[1]:g} to {last[0]} {last[1]:g}: x{last[1] / first[1]:.2f}, {100 * (math.exp(r) - 1):.1f}%/yr, "
            f"{100 * (math.exp(10 * r) - 1):.0f}%/decade")


def main(db_path: str, zr_path: str) -> None:
    bls = jp = load(db_path)
    cpi = bls["cu/CUUR0000SA0"]
    print("## United States, CPI-U all items (BLS CUUR0000SA0, 1982-84 = 100, not seasonally adjusted)\n")
    print(f"- drift: {drift(('1971-08', cpi['1971-08']), ('2024-12', cpi['2024-12']), 53 + 4 / 12)}")
    for d0 in range(1970, 2030, 10):
        d1 = min(d0 + 10, 2024)
        print(f"- December {d0} to December {d1}: x{cpi[key(d1, 12)] / cpi[key(d0, 12)]:.2f}")
    a = annual_means(cpi)
    print("\n| years | month to month | over 12 months | year to year (annual means) |\n|---|---|---|---|")
    for lo, hi in ((1972, 2024), (1984, 2019), (1914, 1970)):
        print(f"| {lo}-{hi} | {sd(lag_changes(cpi, lo, hi, 1))} | {sd(lag_changes(cpi, lo, hi, 12))} | {sd(year_changes(a, lo, hi))} |")

    print("\n## United States, average retail prices of three staples (BLS Average Price series), 1981-2024\n")
    print("| staple | first and last | month to month | over 12 months | largest 12-month rise and fall |\n|---|---|---|---|---|")
    for code, name in (("ap/APU0000701312", "Rice, white, long grain, uncooked, per lb."), ("ap/APU0000701111", "Flour, white, all purpose, per lb."),
                       ("ap/APU0000708111", "Eggs, grade A, large, per doz.")):
        s = bls[code]
        twelve = lag_changes(s, 1981, 2024, 12)
        print(f"| {name} | 1980-01 ${s['1980-01']} to 2025-01 ${s['2025-01']} | {sd(lag_changes(s, 1981, 2024, 1))} | {sd(twelve)} | "
              f"{100 * (math.exp(max(twelve)) - 1):+.0f}%, {100 * (math.exp(min(twelve)) - 1):+.0f}% |")
    real = {p: v / cpi[p] for p, v in bls["ap/APU0000701312"].items() if p in cpi}
    print(f"\nRice against the CPI (its price over the CPI), over 12 months, 1981-2024: {sd(lag_changes(real, 1981, 2024, 12))}")

    ja, jm, jc = jp["CPIa/001"], jp["CPIm/001"], jp["CPIm/003"]
    print("\n## Japan, CPI all items (Statistics Bureau, STATJP CPIa/001 annual, CPIm/001 monthly, 2020 = 100)\n")
    print(f"- drift: {drift(('1971', ja['1971']), ('2024', ja['2024']), 53)}")
    for d0 in range(1970, 2030, 10):
        d1 = min(d0 + 10, 2024)
        print(f"- {d0} to {d1}: x{ja[str(d1)] / ja[str(d0)]:.3f}")
    aa = {int(y): v for y, v in ja.items()}
    print("\n| years | month to month | over 12 months | year to year (annual series) |\n|---|---|---|---|")
    for lo, hi in ((1971, 2024), (1995, 2019)):
        print(f"| {lo}-{hi} | {sd(lag_changes(jm, lo, hi, 1))} | {sd(lag_changes(jm, lo, hi, 12))} | {sd(year_changes(aa, lo, hi))} |")
    print(f"\nJapan, CPI cereals (CPIm/003), 1972-2023: month to month {sd(lag_changes(jc, 1972, 2023, 1))}, over 12 months "
          f"{sd(lag_changes(jc, 1972, 2023, 12))}; 2023-06 {jc.get('2023-06')}, 2025-12 {jc.get('2025-12')}")


    r = json.load(open(zr_path, encoding="utf-8"))["chart"]["result"][0]
    closes = [c for c in r["indicators"]["quote"][0]["close"] if c]
    print(f"\n## CBOT rough rice futures, daily close ({r['meta'].get('shortName')}, {len(closes)} trading days)\n")
    for lag, name in ((1, "1 trading day"), (5, "5 trading days")):
        print(f"- {name}: {sd([math.log(closes[i] / closes[i - lag]) for i in range(lag, len(closes))])}")
    print(f"- first and last close: {closes[0]:.2f}, {closes[-1]:.2f} (in the chart's currency, USD)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
