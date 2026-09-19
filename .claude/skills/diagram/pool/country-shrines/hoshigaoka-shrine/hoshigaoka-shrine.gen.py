#!/usr/bin/env python3
"""hoshigaoka-shrine.gen.py - rasterize the hand-authored country shrine plan (feature 254).

Mode A plans are hand-authored svg SOURCE (tracked in git); only the png is derived. This gen is the
pool wiring that keeps the gitignored png fresh: render-sync regenerates every `pool/*/*/*.gen.py`
from its own directory. It writes nothing but the png - the tracked svg is never touched.

Run:  python3 pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.gen.py   (from anywhere)
"""

from __future__ import annotations

import os
import subprocess

SVG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hoshigaoka-shrine.svg")


def main() -> int:
    if os.environ.get("DIAGRAM_SKIP_RENDER") != "1":
        subprocess.run(
            ["resvg", "--width", "2400", "--serif-family", "DejaVu Serif", SVG, SVG[:-4] + ".png"],
            check=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
