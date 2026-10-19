"""Decade means of the Osaka gold and copper-coin rates in the Kobe RIEB / Mitsui Bunko early-modern database.

Feature 401 (research/questions/0277-what-was-copper-coin-worth-in-silver.html). Reads the database's Excel file
(https://www.rieb.kobe-u.ac.jp/project/kinsei-db/data/data_180301.xlsx, sheet 相場帳: one row a day of the Mitsui Osaka
exchange office's diary, 1787-1871) and prints, per year and per decade, the days used and the mean of:

- 銭相場: silver monme for 1 kanmon (1,000 mon) of copper coin, the Kitahama floor's closing rate;
- 金相場: silver monme for 1 ryo of gold, the closing rate.

The method, which the question states beside the table:
- a day's value is the mean of its minimum and maximum cells where both are numbers, else the one number given; a cell
  holding text (a range written as "9.49～9.5", a note) is not read, and the count of such cells is printed;
- a decade's mean is the mean of every day's value in it, all days weighted alike (not a mean of yearly means);
- mon per monme is 1,000 divided by the decade's mean monme per kanmon; mon per ryo is 1,000 times the decade's mean
  monme per ryo divided by its mean monme per kanmon - both this project's arithmetic;
- the days from 1843-04-13 (the day after the order of 1843-04-12 forbade trading copper under 10 monme a kanmon,
  which the diary records that day) to the end of 1850's second month (the last run at 10.00) are an administered floor, printed apart and left
  out of the 1840s and 1850s market means (months and days are the diary's own, in the Japanese calendar);
- gold from 1859-06-01 on is left out: from that day the database quotes gold in the subsidiary coins in circulation
  rather than in koban, so no mon-per-ryo figure is given past it. The table stops at 1859.

Run on the archived copy (research archive d2/d2aae944e8db/20261019T161020Z/served.xlsx, sha256 592ee2b3...e6df):
  python3 -P specs/401-knives-and-copper-rate/measure/rieb_decades.py <served.xlsx>
Its output is rieb_decades.out.txt beside it.
"""

from __future__ import annotations

import re
import statistics
import sys
from collections import defaultdict

import openpyxl

FLOOR = ((1843, 4, 13), (1850, 3, 1))  # from the day after the order to the end of the last run at 10.00
LAST_YEAR = 1859
GOLD_CUTOFF = (1859, 6)  # gold quoted in subsidiary coins from 1859-06-01


def num(v: object) -> float | None:
    """A cell's number, or None for an empty or text cell."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return None


def day_value(lo: object, hi: object) -> float | None:
    a, b = num(lo), num(hi)
    if a is not None and b is not None:
        return (a + b) / 2
    return a if a is not None else b


def main(path: str) -> None:
    ws = openpyxl.load_workbook(path, read_only=True).worksheets[0]
    zeni: dict[int, list[float]] = defaultdict(list)
    gold: dict[int, list[float]] = defaultdict(list)
    # the same days split into market days (by year) and floor days, for the decade blocks
    mz: dict[int, list[float]] = defaultdict(list)
    mg: dict[int, list[float]] = defaultdict(list)
    fz: list[float] = []
    fg: list[float] = []
    text_cells = 0
    for row in ws.iter_rows(min_row=3, values_only=True):
        m = re.match(r"(\d{4})", str(row[1] or ""))
        if not m:
            continue
        year = int(m.group(1))
        if year > LAST_YEAR:
            continue
        mm = re.match(r"閏?(\d+)月(\d+)日", str(row[2] or ""))
        month, day = (int(mm.group(1)), int(mm.group(2))) if mm else (0, 0)
        floor = FLOOR[0] <= (year, month, day) < FLOOR[1]
        for c in (7, 8, 10, 11):
            if isinstance(row[c], str) and row[c].strip():
                text_cells += 1
        z = day_value(row[10], row[11])
        if z is not None:
            zeni[year].append(z)
            (fz if floor else mz[year]).append(z)
        g = day_value(row[7], row[8])
        if g is not None and (year, month) < GOLD_CUTOFF:
            gold[year].append(g)
            (fg if floor else mg[year]).append(g)

    years = range(1787, LAST_YEAR + 1)
    print("year | days (copper) | monme per kanmon | days (gold) | monme per ryo | days at exactly 10.0")
    for y in years:
        if not zeni[y] and not gold[y]:
            print(f"{y} | no rates in the diary")
            continue
        zm = f"{statistics.mean(zeni[y]):.2f}" if zeni[y] else "-"
        gm = f"{statistics.mean(gold[y]):.2f}" if gold[y] else "-"
        tens = sum(1 for v in zeni[y] if v == 10.0)
        print(f"{y} | {len(zeni[y])} | {zm} | {len(gold[y])} | {gm} | {tens}")
    missing = [y for y in years if not zeni[y]]
    print(f"\nyears with no copper rate: {missing}")
    print(f"text cells not read (1787-{LAST_YEAR}): {text_cells}")

    def block(label: str, ys: list[int], z: list[float] | None = None, g: list[float] | None = None) -> None:
        if z is None:
            z = [v for y in ys for v in mz[y]]
            g = [v for y in ys for v in mg[y]]
            have = [y for y in ys if mz[y]]
        else:
            have = [y for y in ys if zeni[y]]
        if not z:
            return
        zm = statistics.mean(z)
        line = f"{label} | years {have[0]}-{have[-1]}, {len(have)} with rates | {len(z)} days | {zm:.2f} monme/kanmon"
        line += f" | {1000 / zm:.1f} mon/monme"
        if g:
            gm = statistics.mean(g)
            line += f" | {len(g)} days | {gm:.2f} monme/ryo | {1000 * gm / zm:,.0f} mon/ryo"
        print(line)

    print("\ndecade | years | copper days | monme per kanmon | mon per monme | gold days | monme per ryo | mon per ryo")
    block("1787-1789", [1787, 1788, 1789])
    for d in range(1790, 1860, 10):
        block(f"{d}s" + (" (floor days left out)" if d in (1840, 1850) else ""), list(range(d, d + 10)))
    block("1843-04-13 to 1850-02 (administered floor)", list(range(1843, 1851)), fz, fg)
    block("1850-1854 (floor days left out)", list(range(1850, 1855)))
    block("1855-1859", list(range(1855, 1860)))
    block("1804 (anchor for 1802-04)", [1804])
    block("1842 (anchor)", [1842])


if __name__ == "__main__":
    main(sys.argv[1])
