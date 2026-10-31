"""The comb's sector bounds and its dry hem: `_bnd` and `_root_f` - where a sector's two threads run at a given fall, which the
partition's lattice is drawn between (`partition.py`, feature 302) - then `_dry_fields`, the dry-crop hem tiling, and
`_bund_beans`, the azemame bead accents.

Feature 302 retired the plot carve that lived here (`_carve`, one `_carve_sector` per thread pair and its supply-bank and drain
guards, `sector_rows.py`, the `_hem_pass`): the plots are laid as a partition of the planted region, so nothing cuts quads and
leaves ground for a repair.

Research: sector bounds - NONE: where a thread runs at a given fall, and its root fall
"""

from .frame import Pt, _at_f, _Frame, _Thread


def _bnd(t: _Thread, f: float, F: _Frame) -> Pt:
    """Where thread `t` runs at fall `f`, down to its own end: its parent's path above its takeoff, else its own course (the
    sector a partition's lattice is drawn between). Past its end the partition runs the bound straight down the fall itself
    (`partition.Sectors.bound`); the carve's bound along the collector's bank went with the carve (feature 302)."""
    if f < t.f0 and t.fallback is not None:
        fb = t.fallback
        return _at_f(F, fb if isinstance(fb, list) else fb.pts, f)
    return _at_f(F, t.pts, f)


def _root_f(t: _Thread, F: _Frame) -> float:
    while isinstance(t.fallback, _Thread):
        t = t.fallback
    if isinstance(t.fallback, list):
        return min(t.f0, F.to_uf(*t.fallback[0])[1])
    return t.f0


# A BEADED BUND SEGMENT SHOWS AT LEAST TWO BEADS (GM 2026-09-14, feature 247: "On any segment of earthen
# bunds which has bund beans, I would like at least 2 glyphs. I currently see some segments with only 1
# glyph."). A rendering convention only - the beans are sub-pixel and the beads stand for them - so the
# number claims nothing physical; one bead does not read as a row of anything. The forms priced, and the
# one taken, are in specs/247-two-beads-per-bund/research.md R2.
