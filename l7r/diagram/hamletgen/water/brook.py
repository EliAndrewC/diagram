"""THE BROOK (feature 230) - the stream that is tapped at an intake and runs on past the fan, and what stands at the tap.

Split from `hamletgen/water.py` by feature 230 (constitution X clause 13); bodies verbatim.
See `CLAUDE.md` in this directory. The course as drawn - its bends rounded, its taps and confluences held - is Rust's since
feature 444 T26 (`rust/phases/src/course.rs`).

Research: plumbing - NONE: geometry, tolerances and the repair's bounds; every unit that decides something carries its own claims
"""

from __future__ import annotations

from l7r.diagram.settlement._knobs import Knob, register_knob

from ..consts import (
    WEIR_THICK_FT,
)

# THE WEIR'S FORM (269 B22; research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html): a fence of stakes woven with brushwood (feature 280 M36: the woven stake
# fence is in the Man'yoshu, the reed weave only in a present-day weir - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.html), a frame of stakes and logs packed
# with clay, a crib of timber packed with stone, or a course of stone-filled baskets, each drawn at its own thickness
# (`WEIR_THICK_FT`). "The rule the map follows: a weir hamlet's weir takes one of four forms, rolled per settlement
# with an even chance" - the EVEN chance a GUESS, no source counting them. `crib` is the default because it is the
# one form the glyph drew before the knob. Declared as `meta.weir_form` on a weir hamlet only.
WEIR_FORM = register_knob(Knob("weir_form", list(WEIR_THICK_FT), default="crib"))
"""Research: weir form - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: fence, frame, crib or gabion rolled per weir hamlet with even odds, crib the default"""
