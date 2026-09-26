#!/usr/bin/env python3
"""hayakawa-magistracy.gen.py - rasterize the hand-authored manor plan.

Mode A magistracy plans are hand-authored svg SOURCE (tracked in git); only the png is
derived. This gen is the pool wiring that keeps the gitignored png fresh in main:
render-sync regenerates every `pool/*/*.gen.py` from its own directory, and a render
with no gen wrapper is a one-off hand render that silently goes stale (the
county-magistracy-example png did exactly that; caught 2026-07-24). This gen writes the png
and, since feature 262, the interactive page beside it (`<map>.html`, from the sheet's own `data-kind`
tags) - the tracked svg is never touched.

Run:  python3 pool/magistracies/hayakawa-magistracy/hayakawa-magistracy.gen.py   (from anywhere)
"""

from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))  # <skill>/pool/<tier>/<map>/

from l7r.diagram.interactive.compound_kinds import COMPOUND_CLASSES  # noqa: E402
from l7r.diagram.interactive.sheet import write_sheet_page  # noqa: E402

SVG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hayakawa-magistracy.svg")


def main() -> int:
    if os.environ.get("DIAGRAM_SKIP_RENDER") != "1":
        subprocess.run(
            ["resvg", "--width", "2400", "--serif-family", "DejaVu Serif", SVG, SVG[:-4] + ".png"],
            check=True,
        )
    # THE PAGE (feature 262): the interactive map, read from the sheet's own `data-kind` tags. A sheet with ink no
    # kind covers, or a kind nobody wrote up, fails here as loudly as the pool test does.
    census = write_sheet_page(SVG, COMPOUND_CLASSES)
    if census.unclassed or census.unregistered:
        print(f"{os.path.basename(SVG)}: untagged ink {census.unclassed}; unknown kinds {census.unregistered}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
