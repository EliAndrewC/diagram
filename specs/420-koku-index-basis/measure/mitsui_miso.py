"""Row dumps and this project's arithmetic on the Mitsui Kyoto miso and soy sauce cells, 1745-1754, for feature 420 S1.

The file is J.-P. Bassino's transcription of Mitsui Bunko (1989) Table 6 for the Global Price and Income History Group:
https://gpih.ucdavis.edu/files/Japan_1710-1871.xls (sheet "Mitsui Bunko Kyoto T6"). As in feature 412's
mitsui_basket.py, every cell read is a QUARTERLY one ("Spring"/"Fall"), never the file's yearly averages; row numbers
are the sheet's, counted from 1.

What it prints, each figure this project's arithmetic: the sheet's header rows (to show which column is which), the
twenty seasons of miso (silver monme for 10 kan) and soy sauce (silver monme a koku) with rice, salt, firewood, lamp
oil and the day wage beside them, their means and ranges, and the miso and soy sauce means in grams of silver a kg and
a liter at Bassino and Ma's 3.11 g of silver a monme (their paper's rate; the sheet itself uses 3.75), the file's
1 kan = 3.75 kg and 1 koku = 180.891 liters. The soybean proxy it is set beside is the paper's 1.49 g a kg.

Run on the archived copy (archive d3/d31a02b796e1, 2026-10-24):
  python3 -I specs/420-koku-index-basis/measure/mitsui_miso.py <Japan_1710-1871.xls>
Its output is mitsui_miso.out.txt beside it.
"""

from __future__ import annotations

import statistics
import sys

import xlrd

KYOTO = "Mitsui Bunko Kyoto T6"
G_A_MONME = 3.11  # Bassino and Ma 2005, the source note to Table 3: "3.11 g of pure silver per monme"
KG_A_KAN = 3.75  # the file's "1 kan = 3.75 kg"
LITERS_A_KOKU = 180.891  # the file's "1 koku = 180.891 liters"


def seasons(sheet):
    year = None
    for r in range(8, sheet.nrows):
        vals = sheet.row_values(r)
        if isinstance(vals[0], float):
            year = int(vals[0])
        if year is not None and vals[2] in ("Spring", "Fall"):
            yield r + 1, year, vals[2], vals


def main(path: str) -> None:
    k = xlrd.open_workbook(path).sheet_by_name(KYOTO)
    print("== header rows 1-8, columns 0-17")
    for r in range(0, 8):
        print(f"row {r + 1}: " + " | ".join(f"{c}:{v!r}" for c, v in enumerate(k.row_values(r)[:18]) if v != ""))
    cols = {"rice": 3, "salt": 6, "miso": 7, "soy sauce": 8, "firewood": 13, "lamp oil": 14, "wage": 16}
    print("\n== row dump, 1745-1754: " + ", ".join(f"{n} (col {c})" for n, c in cols.items()))
    got = {n: [] for n in cols}
    for row, year, season, vals in seasons(k):
        if 1745 <= year <= 1754:
            print(f"row {row}: {year} {season} | " + " | ".join(f"{n} {vals[c]!r}" for n, c in cols.items()))
            for n, c in cols.items():
                if isinstance(vals[c], float):
                    got[n].append(vals[c])
    print("\n== means of the quarterly cells, 1745-1754")
    for n, xs in got.items():
        print(f"{n}: mean {statistics.mean(xs):.3f}, range {min(xs)}-{max(xs)}, n {len(xs)}")
    miso, soy = got["miso"], got["soy sauce"]
    kg = 10 * KG_A_KAN
    print(f"\nmiso a kg at {G_A_MONME} g a monme: mean {statistics.mean(miso) * G_A_MONME / kg:.2f} g,"
          f" range {min(miso) * G_A_MONME / kg:.2f}-{max(miso) * G_A_MONME / kg:.2f}")
    print(f"soy sauce a liter: mean {statistics.mean(soy) * G_A_MONME / LITERS_A_KOKU:.2f} g,"
          f" range {min(soy) * G_A_MONME / LITERS_A_KOKU:.2f}-{max(soy) * G_A_MONME / LITERS_A_KOKU:.2f}")
    print(f"miso a kg in monme: {statistics.mean(miso) / kg:.3f}; soy sauce a sho (1/100 koku):"
          f" {statistics.mean(soy) / 100:.3f} monme")


if __name__ == "__main__":
    main(sys.argv[1])
