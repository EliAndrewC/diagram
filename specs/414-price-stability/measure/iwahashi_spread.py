#!/usr/bin/env python3
"""Feature 414 (diagram#15, question 3): how far apart the price of a koku of rice stood from place to place in the same
year - this project's arithmetic from the GPIH transcription of Iwahashi 1981, Appendix Table 1 (14 places, 1620-1867).

    python3 -I iwahashi_spread.py <path to Japan_rice_P_1620-1867.xls>

The file: https://gpih.ucdavis.edu/files/Japan_rice_P_1620-1867.xls (sheet "koku of rice"). Its places are in two coins:
silver monme (columns B-I: Osaka, Otsu, rural Banshu, Fukuchiyama, Hiroshima, Bocho, Saga, Kumamoto) and gold ryo (J-O:
Edo, Osaka converted at Osaka's gold-silver rate, Nagoya, Shinshu, Aizu, Dewa). A place is compared only with Osaka in its
own coin, so no gold-silver rate but Osaka's own enters. Per place: the years it and Osaka both carry, the mean of
log(place / Osaka) shown as a percent above or below Osaka, the SD of that log ratio over the years, the mean absolute
log gap, and the correlation of its year-to-year log changes with Osaka's (consecutive years both present). Per year: the
spread across all the places carrying the year in the silver block, and in the gold block, as the SD of log price and the
highest over the lowest; summarized as the median year in a span. The sheet's notes say most places but Osaka, Otsu and
rural Banshu are domain (han) or shogunate prices that probably damped year-to-year swings: their price type is printed
beside them. Spans: 1701-1800 and 1801-1858 (before the open ports' inflation), and the whole sheet.
"""

from __future__ import annotations

import math
import statistics
import sys

import xlrd

SILVER = "BCDEFGHI"
GOLD = "JKLMNO"
SPANS = ((1701, 1800), (1801, 1858), (1620, 1867))


def col(letter: str) -> int:
    return ord(letter) - ord("A")


def read(path: str) -> tuple[dict[str, str], dict[str, str], dict[str, dict[int, float]]]:
    s = xlrd.open_workbook(path).sheet_by_name("koku of rice")
    names = {c: str(s.cell_value(7, col(c))).strip() for c in SILVER + GOLD}
    kinds = {c: str(s.cell_value(6, col(c))).strip() for c in SILVER + GOLD}
    data: dict[str, dict[int, float]] = {c: {} for c in SILVER + GOLD}
    for r in range(8, s.nrows):
        y = s.cell_value(r, 0)
        if not isinstance(y, float):
            continue
        for c in SILVER + GOLD:
            v = s.cell_value(r, col(c))
            if isinstance(v, float) and v > 0:
                data[c][int(y)] = v
    return names, kinds, data


def place_rows(names, kinds, data, base: str, block: str, lo: int, hi: int) -> list[str]:
    out = []
    b = data[base]
    for c in block:
        if c == base:
            continue
        p = data[c]
        yrs = [y for y in sorted(p) if y in b and lo <= y <= hi]
        if len(yrs) < 3:
            continue
        r = [math.log(p[y] / b[y]) for y in yrs]
        ch = [(math.log(p[y + 1] / p[y]), math.log(b[y + 1] / b[y])) for y in yrs if y + 1 in p and y + 1 in b and y + 1 <= hi]
        corr = statistics.correlation([a for a, _ in ch], [d for _, d in ch]) if len(ch) > 2 else float("nan")
        out.append(
            f"| {names[c]} | {kinds[c]} | {yrs[0]}-{yrs[-1]} ({len(yrs)}) | {100 * (math.exp(statistics.fmean(r)) - 1):+.1f}% "
            f"| {100 * statistics.stdev(r):.1f}% | {100 * statistics.fmean(abs(x) for x in r):.1f}% | {corr:.2f} ({len(ch)}) |"
        )
    return out


def cross(data, block: str, lo: int, hi: int) -> str:
    sds, ratios, ns = [], [], []
    for y in range(lo, hi + 1):
        v = [data[c][y] for c in block if y in data[c] and not (block == GOLD and c == "K")]
        if len(v) < 4:
            continue
        lv = [math.log(x) for x in v]
        sds.append(statistics.stdev(lv))
        ratios.append(max(v) / min(v))
        ns.append(len(v))
    if not sds:
        return "- (0 years with 4 or more places)"
    q = statistics.quantiles(sds, n=4) if len(sds) > 3 else [float("nan")] * 3
    return (
        f"{len(sds)} years with 4+ places (median {statistics.median(ns):.0f} places); SD of log price median "
        f"{100 * statistics.median(sds):.1f}% (quartiles {100 * q[0]:.1f}%-{100 * q[2]:.1f}%); highest over lowest median "
        f"{statistics.median(ratios):.2f}x (largest {max(ratios):.2f}x)"
    )


def main(path: str) -> None:
    names, kinds, data = read(path)
    for lo, hi in SPANS:
        print(f"\n## {lo}-{hi}: each place against Osaka in its own coin\n")
        print("| place | price type | years (n) | mean gap to Osaka | SD of log ratio | mean absolute gap | corr. of yearly change with Osaka (pairs) |")
        print("|---|---|---|---|---|---|---|")
        for row in place_rows(names, kinds, data, "B", SILVER, lo, hi) + place_rows(names, kinds, data, "K", GOLD, lo, hi):
            print(row)
        print(f"\nSilver places (B-I), spread across places in one year: {cross(data, SILVER, lo, hi)}")
        print(f"\nGold places (J, L-O; Osaka's converted column left out): {cross(data, GOLD, lo, hi)}")


if __name__ == "__main__":
    main(sys.argv[1])
