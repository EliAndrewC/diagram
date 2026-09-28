"""The cartographic standard for placing a caption, as numbers (feature 266, GM 2026-09-27).

The GM: *"adopt this standard into our project, after looking up the details enough to be able to implement it
faithfully."* Every constant here is either the standard's own - with the page it is read from - or a calibration
this project chose where the standard names a rule and leaves its number to the mapmaker; each says which. The
finding is research/presentation.html, "Where does a caption sit"; the evidence is specs/266-*/research.md R1.
"""

from __future__ import annotations

import math

# THE RANKED POSITIONS AROUND A POINT FEATURE, best first. QGIS's documented default order, which it takes from
# Krygier and Wood's textbook: "top right top left bottom right bottom left middle right middle left top, slightly
# right bottom, slightly left" (qgis-label-settings); a ranked set of eight positions is the standard formulation
# (christensen-marks-shieber-1995, after Yoeli 1972). Each is (name, sx, sy) in the SUBJECT'S OWN frame as the
# words read: sx -1/0/+1 is left/center/right and sy -1/0/+1 is above/level/below. A fractional sx on the last two
# is "slightly": the block's center sits sx times the block's width off center - a quarter width, our reading of
# the word (plan P3, a calibration; the sources name the position, not the amount).
POSITIONS: tuple[tuple[str, float, float], ...] = (
    ("upper right", 1.0, -1.0),
    ("upper left", -1.0, -1.0),
    ("lower right", 1.0, 1.0),
    ("lower left", -1.0, 1.0),
    ("right", 1.0, 0.0),
    ("left", -1.0, 0.0),
    ("above, slightly right", 0.25, -1.0),
    ("below, slightly left", -0.25, 1.0),
)

# THE GAP, measured from the subject's drawn edge to the caption's nearest edge ("The offset is measured from the
# boundary of the feature symbol to the outer edge of the label", esri-offset-point-labels). No readable source
# fixes the number - Esri and QGIS leave it to the mapmaker, and the cartography course says "Most important is
# maintaining consistency throughout your map design" (psu-geog486-point-labels). Half the caption's font size is
# our CALIBRATION (spec D2): about the air the engine's house standoff gave a caption by eye (LABEL_MIN_AIR, 5 px on
# a 9 pt caption), the same for every caption of a size.
PREFERRED_OFFSET_EM = 0.5

# NEARER FIRST (QGIS's default, "Prefer closer labels"): every position at the preferred offset is tried before any
# seat further out, then ring by ring outward. The step and the reach are CALIBRATIONS (plan P2): half an em a ring,
# out to eight ems - 64 ft for a hamlet board's 8 pt caption, past the 53 px the old standoff ladder reached and well
# inside the gate's hug cap. Past the reach the least-cost seat inside it is taken; a caption is never dropped (the
# GM, 2026-09-27: "we'll treat labels as mandatory").
RING_STEP_EM = 0.5
REACH_EM = 8.0

# THE WEIGHTS, on Esri's scale: "A feature weight of 0 indicates that the feature should be treated as available
# space, while a weight of 1,000 indicates that the feature is considered an obstacle" (esri-weight-labels-features).
# Free space first; when none is left, the least total weight. Which families are obstacles, which are free, and the
# 500 a way crossed costs (so crossing one beats crossing two - "they only cross one road instead of several",
# esri-prevent-label-overlap - and two ways cost as much as one obstacle) are our CALIBRATION (spec D4).
WEIGHT_OBSTACLE = 1000.0
WEIGHT_WAY = 500.0
WEIGHT_FREE = 0.0

# ASSOCIATION: a caption standing as close to a neighbor as to its own subject is not plainly its subject's (the
# point label's second job, "association", psu-geog486-point-labels). So a block nearer than the preferred offset to
# any obstacle but its subject counts as covering it. A CALIBRATION (plan P1).
CLEAR_EM = PREFERRED_OFFSET_EM

# A way is crossed when the block comes within its drawn half-width plus this notch: the caption's halo paints out
# what is under it, and a halo on a tread reads as a bite out of the path (the gate's NOTCH_CLEARANCE, 2 ft).
WAY_NOTCH = 2.0

# THE TEXT METRICS `label()` draws with - one source for the placer, the settlement engine and the tools: a line is
# 0.55 em a character wide, one line 1.05 em tall, lines 1.15 em apart, and the block's center 0.275 em above the
# first line's baseline.
CHAR_W_EM = 0.55
LINE_H_EM = 1.05
PITCH_EM = 1.15
CENTER_ABOVE_BASELINE_EM = 0.275


def upright(angle: float) -> float:
    """An angle in degrees turned into (-90, 90], so the words never read upside down (psu-geog486-point-labels:
    "don't write upside down"). A feature at 126 degrees and one at -54 carry their caption the same way."""
    a = math.fmod(angle, 180.0)
    if a <= -90.0:
        a += 180.0
    elif a > 90.0:
        a -= 180.0
    return a


def block_half(lines: list[str] | tuple[str, ...], size: float, char_w: float = CHAR_W_EM) -> tuple[float, float]:
    """The half-width and half-height of a caption set on `lines` at `size` - the block `label()` records. `char_w` is
    the width per character in ems, the standard's unless a caller measured its text as wider."""
    w = max(len(ln) for ln in lines) * size * char_w
    h = size * LINE_H_EM + (len(lines) - 1) * size * PITCH_EM
    return w / 2.0, h / 2.0
