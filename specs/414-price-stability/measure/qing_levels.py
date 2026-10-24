#!/usr/bin/env python3
"""Feature 414 (diagram#15, question 3): how far apart Allen et al.'s bare-bones basket cost stood in Beijing, Suzhou and
Canton in the same year - this project's arithmetic from the GPIH file.

    python3 -I qing_levels.py <path to China_1730-1933_Allen_et_al.xls>

The file: https://gpih.ucdavis.edu/files/China_1730-1933_Allen_et_al.xls, sheet "Figures2-6", the bare-bones basket in grams
of silver a man a year (read through qing_stability.py's own reader). Per decade to 1850: the mean of log(Canton / Suzhou)
and log(Beijing / Suzhou) over the years all carry, as a percent above or below Suzhou. Beijing's basket is a
reconstruction (its rice is the Yangzi series rescaled, its oils indexed to flour), so its level against Suzhou is the
authors' construction more than a measured gap; said beside it wherever it is used.
"""

from __future__ import annotations

import importlib.util
import math
import pathlib
import statistics
import sys

_spec = importlib.util.spec_from_file_location("qing_stability", pathlib.Path(__file__).with_name("qing_stability.py"))
qs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(qs)


def main(path: str) -> None:
    b = qs.allen(path)
    print("| years | Canton over Suzhou (years) | Beijing over Suzhou (years) |")
    print("|---|---|---|")
    spans = [(lo, lo + 9) for lo in range(1730, 1850, 10)] + [(1730, 1799), (1800, 1849)]
    for lo, hi in spans:
        cells = []
        for city in ("Canton", "Beijing"):
            r = [math.log(b[city][t] / b["Suzhou"][t]) for t in range(lo, hi + 1) if t in b[city] and t in b["Suzhou"]]
            cells.append(f"{100 * (math.exp(statistics.fmean(r)) - 1):+.0f}% ({len(r)})" if r else "-")
        print(f"| {lo}-{hi} | " + " | ".join(cells) + " |")

if __name__ == "__main__":
    main(sys.argv[1])
