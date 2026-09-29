#!/usr/bin/env python3
"""hoshigaoka-shrine.gen.py - render the hand-authored country shrine plan and its interactive page (features 254, 277).

Mode A plans are hand-authored svg SOURCE (tracked in git); the png and the page are derived. This gen is the
pool wiring that keeps both fresh: render-sync regenerates every `pool/*/*/*.gen.py` from its own directory. It
writes the png and `<map>.html` from the one tracked svg - every element carries its `data-kind`, and the page
reads each kind's explanation from the registry (`compound_kinds/`), as a magistracy's does. The svg is never
touched.

Run:  python3 pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.gen.py   (from the skill dir)
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))  # <tree>/<tier>/<map>/

from l7r.diagram.interactive.compound_kinds import COMPOUND_CLASSES  # noqa: E402
from l7r.diagram.interactive.sheet import write_sheet_page  # noqa: E402
from l7r.diagram.labels.hand_sheet import placed, render  # noqa: E402

SVG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hoshigaoka-shrine.svg")


def main() -> int:
    # THE CAPTIONS (feature 286): placed by the one placer from the sheet's declarations - their text and what they
    # name - and the picture and the page rendered from the placed text; the tracked svg is never touched
    with open(SVG, encoding="utf-8") as fh:
        text = placed(fh.read())
    if os.environ.get("DIAGRAM_SKIP_RENDER") != "1":
        render(text, SVG[:-4] + ".png")
    # the interactive page (feature 277): the same tracked svg the png is rendered from
    census = write_sheet_page(SVG, COMPOUND_CLASSES, svg=text)
    if census.unclassed or census.unregistered:
        print(f"{os.path.basename(SVG)}: untagged ink {census.unclassed}; unknown kinds {census.unregistered}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
