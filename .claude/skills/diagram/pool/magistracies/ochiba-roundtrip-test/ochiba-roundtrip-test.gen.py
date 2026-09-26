#!/usr/bin/env python3
"""ochiba-roundtrip-test.gen.py - round-trip TEST of the perimeter-first placer (feature 008).

Encode the EXISTING hand-authored Ochiba magistracy (pool/magistracies/ochiba-magistracy/ochiba-magistracy.svg) as a
feet-first CompoundProgram - its real envelope, its real court-spine, and its real building
masses measured off the finished SVG at 3 px = 1 ft - then run it through compound.place()
and compound.emit_svg(). The point is not to replace Ochiba but to see whether the placer,
given Ochiba's ACTUAL program, composes it the way the GM hand-composed it, and to surface
exactly where the two diverge (that divergence is the finding of the test).

Garden pavilions and point features (bath, wells, latrines, privy, fire-tubs, the notice board) are
NOT massed perimeter buildings - the placer arranges the wall-ranging masses and the emitter seats
the point features against them (feature 254: a draft in the pool is swept by the gate with the
whole program, so it carries the whole program).

Run:  python3 pool/magistracies/ochiba-roundtrip-test/ochiba-roundtrip-test.gen.py   (from the skill dir)
"""

from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))  # <tree>/<tier>/<map>/ - one level deeper since feature 161 gave every map its own folder

from l7r.diagram import compound as C  # noqa: E402
from l7r.diagram.interactive.compound_kinds import COMPOUND_CLASSES  # noqa: E402
from l7r.diagram.interactive.sheet import write_sheet_page  # noqa: E402

# cwd-INDEPENDENT output path (fixed 2026-07-21): the old cwd-relative "pool/..." wrote a stray
# file at the pool ROOT when run from the skill dir and crashed when run from this dir - anchor
# to __file__ like every Mode B gen, so the render-sync regen (which runs each gen from its own
# directory) and any hand run land the outputs HERE, beside the gen.
OUT_SVG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ochiba-roundtrip-test.svg")


def ochiba_program() -> C.CompoundProgram:
    env = C.Envelope(w_ft=267.0, h_ft=200.0, divider_ft=100.0, gate_w_ft=13.3)
    # real open courts measured off the finished map
    spine = (
        C.CourtZone("garden", 107.0, 53.0, 97.0, 45.0),  # inner garden (center of inner court)
        C.CourtZone("oshirasu", 73.0, 139.0, 120.0, 35.0),  # the sanded hearing court
        C.CourtZone("forecourt", 95.0, 180.0, 76.0, 17.0),  # just inside the main gate
        C.CourtZone("practice ground", 200.0, 104.0, 30.0, 30.0),  # beside the E-wall barracks, as on the sheet (feature 254: the whole program)
    )
    b = C.BuildingSpec
    buildings = (
        # inner (residence) court
        b("residence (W)", "lord", 90.0, 25.0, "inner", "N", order=10, feature="residence"),
        b("residence (E)", "lord", 93.0, 25.0, "inner", "N", order=9, feature="residence"),
        b("servants", "service", 73.0, 13.0, "inner", "N", order=2, rank=2, feature="servants' quarters"),  # rear service strip
        b("kitchen", "service", 40.0, 33.0, "inner", "W", order=5, feature="kitchen"),
        b("Inari shrine", "shrine", 37.0, 31.0, "inner", "E", order=5, feature="compound shrine"),
        b("cinnabar workshop", "shrine", 37.0, 24.0, "inner", "E", order=4, feature="cinnabar workshop"),
        b("karo's house", "lord", 37.0, 23.0, "inner", "divider", order=3, feature="karo's house"),
        # outer (administrative) court
        b("office hall", "lord", 120.0, 28.0, "outer", "divider", order=10, feature="office hall"),
        b("tax archive", "kura", 32.0, 28.0, "outer", "W", order=6, feature="tax archive"),
        b("senior retainers", "service", 51.0, 17.0, "outer", "W", order=4, feature="retainers' quarters"),
        b("granary", "kura", 50.0, 26.0, "outer", "E", order=6, feature="granary"),
        b("barracks", "service", 31.0, 33.0, "outer", "E", order=4, feature="barracks"),
        b("cell", "cell", 18.0, 15.0, "outer", "E", order=1, feature="cell"),
        b("gatehouse", "dark", 40.0, 14.0, "outer", "S", order=8, feature="gatehouse"),
        b("stables", "service", 29.0, 22.0, "outer", "S", order=5, feature="stables"),
        b("clerks' room", "service", 28.0, 18.0, "outer", "W", order=3, feature="clerks' room"),  # a room of the hall on the sheet; a mass here (feature 254)
        b("guest room", "lord", 22.0, 15.0, "inner", "E", order=2, feature="guest quarters"),  # a room of the residence on the sheet; a mass here (feature 254)
    )
    return C.CompoundProgram("Ochiba County Magistracy (placer round-trip)", env, spine, buildings)


def main() -> int:
    program = ochiba_program()
    result = C.place(program)
    with open(OUT_SVG, "w", encoding="utf-8") as fh:
        fh.write(C.emit_svg(program, result))
    print(f"wrote {OUT_SVG}: {len(result.placed)} placed, {len(result.overflow)} overflow")
    for p in sorted(result.placed, key=lambda p: (p.spec.court, p.spec.wall, p.x_ft, p.y_ft)):
        print(f"  placed  {p.spec.name:22s} {p.spec.court:5s} {p.spec.wall:7s} @ ({p.x_ft:.0f},{p.y_ft:.0f})")
    for s in result.overflow:
        print(f"  OVERFLOW {s.name:21s} {s.court:5s} {s.wall:7s} ({s.w_ft:.0f}x{s.h_ft:.0f} ft)")
    if os.environ.get("DIAGRAM_SKIP_RENDER") != "1":
        subprocess.run(
            ["resvg", "--width", "2400", "--serif-family", "DejaVu Serif", OUT_SVG, OUT_SVG[:-4] + ".png"],
            check=True,
        )
    # the interactive page (feature 262): the emitter wrote each element's kind, so the page reads the draft as it
    # reads a hand-drawn sheet
    census = write_sheet_page(OUT_SVG, COMPOUND_CLASSES)
    if census.unclassed or census.unregistered:
        print(f"{os.path.basename(OUT_SVG)}: untagged ink {census.unclassed}; unknown kinds {census.unregistered}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
