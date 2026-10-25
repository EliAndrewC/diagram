"""Row dumps and this project's arithmetic on the Mitsui miso and soy sauce cells, era by era, for feature 422 S1.

The file is J.-P. Bassino's transcription of Mitsui Bunko (1989) Tables 6-8 for the Global Price and Income History
Group: https://gpih.ucdavis.edu/files/Japan_1710-1871.xls (sheets "Mitsui Bunko Kyoto T6", "... Edo T7", "... Osaka T8").
As in feature 420's mitsui_miso.py, every cell read is a half-yearly one ("Spring"/"Fall"), never the file's yearly
averages; row numbers are the sheet's, counted from 1. Column H is miso (silver monme for 10 kan), column I soy sauce
(silver monme a koku).

What it prints, each figure this project's arithmetic: per era of research/assets/money-conversions.json that the sheets
reach, the cells in its years (row, year, season, miso, soy sauce), their count, mean and range, and the means in grams
of silver a kg and a liter at the era's own units.monme.silver_g (from question 0287) and at Bassino and Ma's 3.11 g,
with the file's 1 kan = 3.75 kg (10 kan = 37.5 kg) and 1 koku = 180.891 liters.

Run on the archived copy (archive d3/d31a02b796e1, 2026-10-24):
  python3 -I specs/422-miso-soy-and-the-opening/measure/mitsui_eras.py <Japan_1710-1871.xls>
Its output is mitsui_eras.out.txt beside it.
"""

from __future__ import annotations

import statistics
import sys

import xlrd

# era: (first year, last year, grams of pure silver a monme, money-conversions.json units.monme.silver_g)
ERAS = {
    "osaka-1706": (1706, 1711, 1.875),
    "osaka-1712": (1712, 1718, 1.5),
    "kyoto-1745": (1745, 1754, 1.725),
    "kyoto-1790": (1790, 1799, 1.725),
    "kyoto-1800": (1800, 1817, 1.725),
    "edo-1818": (1818, 1829, 1.35),
    "edo-1830": (1830, 1844, 0.975),
    "edo-1850": (1850, 1859, 0.975),
    "edo-1860": (1860, 1867, 0.4875),
}
KG = 37.5
LITERS = 180.891
SHEETS = ("Mitsui Bunko Kyoto T6", "Mitsui Bunko Edo T7", "Mitsui Bunko Osaka T8")


def main(path: str) -> None:
    book = xlrd.open_workbook(path)
    for name in SHEETS:
        sheet = book.sheet_by_name(name)
        print(f"## {name}: header rows 4-6, columns H and I")
        for r in range(3, 6):
            print(f"  row {r + 1}: H={sheet.cell_value(r, 7)!r} I={sheet.cell_value(r, 8)!r}")
        rows, year = [], None
        for r in range(sheet.nrows):
            v = sheet.row_values(r)
            if isinstance(v[0], float):
                year = int(v[0])
            if len(v) > 8 and v[2] in ("Spring", "Fall"):
                rows.append((r + 1, year, v[2], v[7], v[8]))
        for era, (first, last, grams) in ERAS.items():
            sel = [x for x in rows if x[1] is not None and first <= x[1] <= last]
            if not sel:
                continue
            print(f"\n### {name} / {era} ({first}-{last}), {grams} g a monme")
            for row, yr, season, miso, soy in sel:
                print(f"  row {row} {yr} {season}: miso {miso!r} soy {soy!r}")
            for i, good, unit, div in ((3, "miso", "10 kan", KG), (4, "soy sauce", "koku", LITERS)):
                xs = [x[i] for x in sel if isinstance(x[i], float)]
                if not xs:
                    print(f"  {good}: no cells")
                    continue
                m = statistics.mean(xs)
                per = "kg" if good == "miso" else "liter"
                print(
                    f"  {good}: n={len(xs)} sum {sum(xs):.2f} mean {m:.2f} range {min(xs)}-{max(xs)} monme a {unit};"
                    f" at {grams} g: {m * grams / div:.3f} g a {per} (range {min(xs) * grams / div:.3f}-"
                    f"{max(xs) * grams / div:.3f}); at 3.11 g: {m * 3.11 / div:.3f}"
                )


if __name__ == "__main__":
    main(sys.argv[1])
