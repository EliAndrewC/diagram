#!/usr/bin/env python3
"""Feature 414 (diagram#15), plan D4: the closeness rule's measured no-note bound - this project's derivation.

    python3 -I closeness.py <Japan_1710-1871.xls> <China_rice_prices_961-1910.xls> <China_1730-1933_Allen_et_al.xls>

An era row converts any year inside its ten-year span at one price level, so the SD of log change at 5 years (half the span) is
the uncertainty the conversion table already accepts: the WITHIN-ERA SPREAD. A borrowed era needs no note while the SD at its
gap in years is no larger than that spread, within the spread's own sampling error: SD_gap <= spread + 2 SE, SE = spread /
sqrt(2 n), the usual standard error of a standard deviation on n pairs. The no-note bound is the last gap of an unbroken run
from 5 years (5, 10, 15, 20, 25, 30, 40, 50) that meets this, each gap resting on at least MIN_PAIRS pairs - a gap past the
first one that fails is not counted, however its SD falls again. For each good and city of Mitsui Bunko (to 1858, before the
treaty-port break) it prints the curve, the spread, the tolerance and the bound, with the pairs each figure rests on. Place: a city needs no note where
its gap to Kyoto, 1818-1858, both MOVED no more than the within-era spread (the SD of the yearly log ratio) and STOOD no wider
than it (the mean log ratio) - a steady gap wider than the era's own swing misprices every amount by that gap (session 3: the
plan's test was the SD alone, which passed Edo's miso at 29% below Kyoto's). The breaks (the 1859 opening, a recoinage that changed
the money's silver, a change of money system) are the do-not-convert bound and are not computed here; a numeric limit beyond the
no-note bound is the GM's choice (plan D4), so the full curve is printed for him.

China (plan D4): the same rule on `qing_stability.py`'s series - Allen et al.'s Suzhou and Canton basket costs in grams of
silver, to 1850 (both end in 1833), Beijing's beside them as the reconstruction it is, and Kishimoto's Suzhou-area rice
(1584-1766). Those baskets are composites, so a per-good bound would need a per-good series: the only one in the files is
Allen et al.'s "Beijing prices" sheet, and for each of its goods the count of distinct values and of years whose value
repeats the year before is printed, the measured reason it gives no bound of its own.
"""

from __future__ import annotations

import math
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mitsui_stability as ms  # noqa: E402
import qing_stability as qs  # noqa: E402

GAPS = (5, 10, 15, 20, 25, 30, 40, 50)
MIN_PAIRS = 20
#: Series left out of the rule: Kyoto's salt runs at a third of Edo's and Osaka's from 1791, a unit or grade change in the
#: series, not a price (spec edge case; the place table below still shows it, as the break it is).
BROKEN = {("Kyoto", "Salt")}
GOODS = ("White rice", "Salt", "Miso", "Soy sauce", "Sake", "Burning wood", "Charcoal", "Lamp oil", "Day laborers")


def curve(s: dict[tuple[int, int], float], last: int = 1858) -> dict[int, tuple[float, int]]:
    return gap_curve(ms.yearly(s), last)


def gap_curve(yearly: dict[int, float], last: int) -> dict[int, tuple[float, int]]:
    y = {t: v for t, v in yearly.items() if t <= last}
    out = {}
    for g in GAPS:
        ch = [math.log(y[t + g] / y[t]) for t in sorted(y) if t + g in y]
        out[g] = (statistics.stdev(ch) if len(ch) > 2 else float("nan"), len(ch))
    return out


def no_note(c: dict[int, tuple[float, int]]) -> tuple[float, str]:
    """The tolerance (spread + 2 SE) and the no-note bound of one curve."""
    spread, n5 = c[5]
    limit = spread * (1 + 2 / math.sqrt(2 * n5)) if n5 else float("nan")
    bound = "-"
    for g in GAPS:
        v, n = c[g]
        if math.isnan(v) or n < MIN_PAIRS or v > limit:
            break
        bound = f"{g} yr"
    return limit, bound


def curve_cells(c: dict[int, tuple[float, int]]) -> list[str]:
    return [("-" if math.isnan(v) else f"{100 * v:.1f}%") + f" ({n})" for v, n in c.values()]


def china(rice: str, basket: str) -> None:
    import xlrd

    print("\n## China: the same curve and bound (SD of log change between yearly values; n = pairs)\n")
    print("| series | within-era spread (5 yr); limit | " + " | ".join(f"{g} yr" for g in GAPS) + " | no-note bound |")
    print("|---|---|" + "---|" * len(GAPS) + "---|")
    k = qs.kishimoto(rice)
    rows = [("Kishimoto, Suzhou-area rice, taels a shi, 1584-1766", k, 1766)]
    for city, y in qs.allen(basket).items():
        note = " (a reconstruction)" if city == "Beijing" else ""
        rows.append((f"Allen et al., {city} bare-bones basket, g of silver{note}, to 1850", y, 1850))
    for label, y, last in rows:
        c = gap_curve(y, last)
        spread, n5 = c[5]
        limit, bound = no_note(c)
        head = "-" if math.isnan(spread) else f"{100 * spread:.1f}% ({n5}); limit {100 * limit:.1f}%"
        print(f"| {label} | {head} | " + " | ".join(curve_cells(c)) + f" | {bound} |")
    print(f"\nKishimoto's series has {len(k)} years with a price in {min(k)}-{max(k)}.")
    s = xlrd.open_workbook(basket).sheet_by_name("Beijing prices")
    print("\n## China: Allen et al.'s Beijing goods, 1738-1850 - how many values are their own\n")
    print("| good | years | distinct values | years equal to the year before | its ratio to wheat flour, lowest-highest |")
    print("|---|---|---|---|---|")
    goods: dict[str, dict[int, float]] = {}
    for col in range(1, s.ncols - 1):
        name = " ".join(str(s.cell_value(r, col)).strip() for r in (8, 9)).strip()
        y = {}
        for r in range(10, s.nrows):
            t, v = s.cell_value(r, 0), s.cell_value(r, col)
            if isinstance(t, float) and t <= 1850 and isinstance(v, float) and v > 0:
                y[int(t)] = v
        if y:
            goods[name] = y
    flour = goods["wheat flour"]
    for name, y in goods.items():
        same = sum(1 for t in y if t - 1 in y and abs(y[t] - y[t - 1]) < 1e-12)
        ratio = [y[t] / flour[t] for t in y if t in flour]
        print(f"| {name} | {len(y)} | {len({round(v, 12) for v in y.values()})} | {same} | {min(ratio):.4f}-{max(ratio):.4f} |")
    print("\nA good whose ratio to wheat flour is one figure every year is flour's series scaled, not a price series of its own.")


def main(path: str) -> None:
    import xlrd

    book = xlrd.open_workbook(path)
    data = {city: ms.series(book, sheet) for city, sheet in ms.SHEETS.items()}
    print("## The swing-by-gap curve and the no-note bound, to 1858 (SD of log change; n = pairs)\n")
    print("| city | good | within-era spread (5 yr); limit | " + " | ".join(f"{g} yr" for g in GAPS) + " | no-note bound |")
    print("|---|---|---|" + "---|" * len(GAPS) + "---|")
    for city, goods in data.items():
        for good in GOODS:
            if good not in goods or (city, good) in BROKEN:
                continue
            c = curve(goods[good])
            spread, n5 = c[5]
            if math.isnan(spread):
                continue
            limit, bound = no_note(c)
            print(f"| {city} | {good} | {100 * spread:.1f}% ({n5}); limit {100 * limit:.1f}% | " + " | ".join(curve_cells(c)) + f" | {bound} |")
    print("\nLeft out: " + ", ".join(f"{c} {g}" for c, g in sorted(BROKEN)) + " (a unit change in the series from 1791).")
    print("\n## Place: the gap to Kyoto against Kyoto's within-era spread, 1818-1858\n")
    print("How far the gap MOVED (the SD of the yearly log ratio) and how WIDE it stood (the mean log ratio, as a log percent),")
    print("each against Kyoto's within-era spread. A borrowed city needs no note only where both are within it: a steady gap")
    print("that stands wider than the era's own swing still misprices every amount by that gap.\n")
    print("| good | Kyoto within-era spread | Edo: SD; mean of log(Edo/Kyoto) | Osaka: SD; mean of log(Osaka/Kyoto) |")
    print("|---|---|---|---|")
    for good in GOODS:
        if good not in data["Kyoto"] or ("Kyoto", good) in BROKEN:
            continue
        spread = curve(data["Kyoto"][good])[5][0]
        ky = ms.yearly(data["Kyoto"][good])
        cells = []
        for city in ("Edo", "Osaka"):
            other = ms.yearly(data[city].get(good, {}))
            r = [math.log(other[t] / ky[t]) for t in range(1818, 1859) if t in other and t in ky]
            if len(r) > 2:
                sd, mean = statistics.stdev(r), statistics.mean(r)
                verdict = "within" if sd <= spread and abs(mean) <= spread else "beyond"
                cells.append(f"{100 * sd:.1f}%; {100 * mean:+.1f}% ({len(r)}) - {verdict}")
            else:
                cells.append("-")
        print(f"| {good} | {100 * spread:.1f}% | " + " | ".join(cells) + " |")
    print("\nLeft out: Kyoto Salt, as above.")


if __name__ == "__main__":
    main(sys.argv[1])
    if len(sys.argv) > 3:
        china(sys.argv[2], sys.argv[3])
