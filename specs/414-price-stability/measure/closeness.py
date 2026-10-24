#!/usr/bin/env python3
"""Feature 414 (diagram#15), plan D4: the closeness rule's measured no-note bound - this project's derivation.

    python3 -I closeness.py <Japan_1710-1871.xls>

An era row converts any year inside its ten-year span at one price level, so the SD of log change at 5 years (half the span) is
the uncertainty the conversion table already accepts: the WITHIN-ERA SPREAD. A borrowed era needs no note while the SD at its
gap in years is no larger than that spread, within the spread's own sampling error: SD_gap <= spread + 2 SE, SE = spread /
sqrt(2 n), the usual standard error of a standard deviation on n pairs. The no-note bound is the last gap of an unbroken run
from 5 years (5, 10, 15, 20, 25, 30, 40, 50) that meets this, each gap resting on at least MIN_PAIRS pairs - a gap past the
first one that fails is not counted, however its SD falls again. For each good and city of Mitsui Bunko (to 1858, before the
treaty-port break) it prints the curve, the spread, the tolerance and the bound, with the pairs each figure rests on. Place: a city whose spread to Kyoto (the SD of the yearly log
ratio, 1818-1858) is no larger than the within-era spread needs no note. The breaks (the 1859 opening, a recoinage that changed
the money's silver, a change of money system) are the do-not-convert bound and are not computed here; a numeric limit beyond the
no-note bound is the GM's choice (plan D4), so the full curve is printed for him.
"""

from __future__ import annotations

import math
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mitsui_stability as ms  # noqa: E402

GAPS = (5, 10, 15, 20, 25, 30, 40, 50)
MIN_PAIRS = 20
#: Series left out of the rule: Kyoto's salt runs at a third of Edo's and Osaka's from 1791, a unit or grade change in the
#: series, not a price (spec edge case; the place table below still shows it, as the break it is).
BROKEN = {("Kyoto", "Salt")}
GOODS = ("White rice", "Salt", "Miso", "Soy sauce", "Sake", "Burning wood", "Charcoal", "Lamp oil", "Day laborers")


def curve(s: dict[tuple[int, int], float], last: int = 1858) -> dict[int, tuple[float, int]]:
    y = {t: v for t, v in ms.yearly(s).items() if t <= last}
    out = {}
    for g in GAPS:
        ch = [math.log(y[t + g] / y[t]) for t in sorted(y) if t + g in y]
        out[g] = (statistics.stdev(ch) if len(ch) > 2 else float("nan"), len(ch))
    return out


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
            limit = spread * (1 + 2 / math.sqrt(2 * n5))
            bound = "-"
            for g in GAPS:
                v, n = c[g]
                if math.isnan(v) or n < MIN_PAIRS or v > limit:
                    break
                bound = f"{g} yr"
            cells = [("-" if math.isnan(v) else f"{100 * v:.1f}%") + f" ({n})" for g, (v, n) in c.items()]
            print(f"| {city} | {good} | {100 * spread:.1f}% ({n5}); limit {100 * limit:.1f}% | " + " | ".join(cells) + f" | {bound} |")
    print("\nLeft out: " + ", ".join(f"{c} {g}" for c, g in sorted(BROKEN)) + " (a unit change in the series from 1791).")
    print("\n## Place: the spread to Kyoto against Kyoto's within-era spread, 1818-1858\n")
    print("| good | Kyoto within-era spread | Edo: SD of log(Edo/Kyoto) | Osaka: SD of log(Osaka/Kyoto) |")
    print("|---|---|---|---|")
    for good in GOODS:
        if good not in data["Kyoto"]:
            continue
        spread = curve(data["Kyoto"][good])[5][0]
        ky = ms.yearly(data["Kyoto"][good])
        cells = []
        for city in ("Edo", "Osaka"):
            other = ms.yearly(data[city].get(good, {}))
            r = [math.log(other[t] / ky[t]) for t in range(1818, 1859) if t in other and t in ky]
            if len(r) > 2:
                sd = statistics.stdev(r)
                cells.append(f"{100 * sd:.1f}% ({len(r)}) - {'within' if sd <= spread else 'beyond'}")
            else:
                cells.append("-")
        print(f"| {good} | {100 * spread:.1f}% | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main(sys.argv[1])
