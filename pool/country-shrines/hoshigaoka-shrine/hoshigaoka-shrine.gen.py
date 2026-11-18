#!/usr/bin/env python3
"""hoshigaoka-shrine.gen.py - render the hand-authored country shrine plan and its interactive page (features 254, 277).

Mode A plans are hand-authored svg SOURCE (tracked in git); the png and the page are derived. This gen is the
pool wiring that keeps both fresh: render-sync regenerates every `pool/*/*/*.gen.py` from its own directory. It
writes the png and `<map>.html` from the one tracked svg - every element carries its `data-kind`, and the page
reads each kind's explanation from the registry (`compound_kinds/`), as a magistracy's does. The svg is never
touched.

DRAWN BY THE MODE A ENGINE (feature 449 T151, the engine port's step 3a): the captions placed by the one placer (feature
286), the png rendered from the placed text unless `DIAGRAM_SKIP_RENDER=1`, the page written (feature 277) and the census
judged, all by `l7r-mode-a hand-sheet` (`rust/mode_a/src/sheet/hand.rs`); this file stays the pool's wiring and the
generation cache's entry, `draw_hand_sheet` opening every file the engine read so the cache sees them.

Run:  python3 pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.gen.py   (from the skill dir)
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))  # <tree>/<tier>/<map>/

from l7r.diagram.interactive.sheet import draw_hand_sheet  # noqa: E402

SVG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hoshigaoka-shrine.svg")


def main() -> int:
    # the sheet drawn whole - captions, picture, page and census - and the generator's exit the engine's (feature 449 T151)
    return draw_hand_sheet(SVG)


if __name__ == "__main__":
    raise SystemExit(main())
