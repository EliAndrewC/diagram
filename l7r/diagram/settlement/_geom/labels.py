"""Caption typography: how far a label stands off its subject, how big it is set, and which way it
tilts.

ONE tilt rule since 2026-08-27 (GM, feature 133 T38): a caption lies at exactly the angle of the
thing it names, normalized so it never reads upside down (`aligned_tilt`). `label_tilt` and
`linear_tilt` are kept as names for their call sites and both return it; their docstrings carry the
two earlier rules they superseded (the mod-90 fold of 2026-08-02, the 45-degree clamp of
2026-08-08) so the history is not lost.

Split from settlement/_geom.py by feature 117 - see settlement/_geom/CLAUDE.md for the index.

Research: caption typography - CONVENTION: standoff, size and tilt of map captions
"""

import math
from collections.abc import Sequence
from typing import Any

from .base import Poly

# ---- LABEL STANDOFF LADDER (GM 2026-07-26) ----------------------------------------------------
# The label doctrine was "empty ground wins" (see research/contents.json#map-conventions), scored by
# `_label_hits` - a COUNT of the footprints a candidate box would cover. Overlaps were the only
# term, so every clear candidate tied at zero and the winner fell out of generation order: a
# caption could float 50+px out in bare ground and score exactly as well as one tucked against the
# thing it names. Tango showed both halves of the failure at once - "Imperial Road" sat 55px off
# the roadway, and "gate market" 42px east of its stall rows, ending up nearer the execution
# ground than the market it labels. The fix is a SECOND term: among candidates that cover nothing,
# the NEAREST wins, searched over a ladder of standoffs instead of at one hand-guessed distance.
#
# WHY THESE ARE PIXELS AND NOT FEET (the usual unit in this engine): this is a LEGIBILITY rule,
# and label type does not scale with the map grain - captions are 9-14px at 1, 2 and 3 ft/px
# alike - so the air a caption needs to read as "beside, but not touching" is a constant number of
# pixels at every scale. Expressed in feet it would be 5 ft at hamlet grain and 15 ft in a city,
# which is exactly backwards.
LABEL_MIN_AIR = 5.0  # clear air between a caption's box and its subject's. Calibrated to the
#                      hand-tuned captions already in the engine, which this must not visibly
#                      change: a size-9 label drawn at `y + h/2 + 11` puts its glyph top 3.8px
#                      below the subject's edge, and one at `y - h/2 - 9` its descender 6.75px
#                      above - so ~5px is the house standoff, arrived at by eye over many maps.
LABEL_AIR_STEP = 6.0  # ladder rung: fine enough to find a slot between crowded features, coarse
#                      enough that nine rungs still reach past a dense frontage band.
LABEL_AIR_RINGS = 9  # ~53px of reach. Past that a caption has lost its subject anyway, so the
#                      placer stops searching and takes the least-covered seat it found.
LABEL_AIR_CAP = 3.0  # x font size - how far a placed caption may END UP from its subject before
#                      `label_hugs_its_referent` calls it adrift. A BACKSTOP, not the mechanism:
#                      the ladder does the real work, and this only catches a caption that ran the
#                      whole ladder and still landed nowhere near its subject. Calibrated against
#                      the Tango numbers: it fires on the two captions the GM caught (55px on a
#                      12px "Imperial Road", 42px on a 10px "gate market") and passes the tightest
#                      seat the ladder can actually find for that road caption (29px - Tango's
#                      north roadway is flanked by market stalls the whole length of the segment,
#                      so 29px IS the nearest clear ground, and a cap that failed it would be
#                      demanding a placement no map can make).


def label_tilt(rot: float) -> float:
    """The angle a caption takes to lie ALIGNED with the feature it names when that feature is
    drawn at `rot` degrees (GM 2026-08-02: an angled building's label carries the building's own
    tilt - "caravan inn" runs along its rot=-16 inn, not as level text beside a diagonal glyph).
    Folded mod 90 into [-45, 45): the text aligns with whichever of the building's two edge
    families lies nearer the horizontal, so a caption never tilts past 45 degrees (legibility),
    and a SQUARE-rotated building (0/90/180/270) keeps its level caption EXACTLY as before - the
    fold is what keeps every level caption in the pool byte-stable. Rounded to 0.1 degree (the
    grain the glyph transforms use); float noise under half that grain snaps level.

    SUPERSEDED 2026-08-27 (GM, feature 133 T38, the project's general rule): *"I would also like for
    labels to be aligned with the thing that they are labeling. So for example, the notice board is
    at an angle, therefore, the notice board label should be at exactly the same angle."* A caption
    now carries its subject's OWN angle, normalized to [-90, 90) so the text never renders upside
    down (a rotation and its reverse are the same line of text). No fold to the nearer edge family,
    no 45-degree clamp: the mod-90 fold sent a 102-degree yard's caption to 12 degrees - aligned with
    an edge, not with the thing - and `linear_tilt`'s clamp (below) left Inashiro's notice board
    level beside a glyph at 57 degrees. Level subjects (0/180) still get a level caption, so a map
    with no rotated feature is byte-identical."""
    return aligned_tilt(rot)


def aligned_tilt(rot: float) -> float:
    """The one alignment rule (GM 2026-08-27): the subject's angle, normalized to [-90, 90), rounded
    to the 0.1-degree grain the glyph transforms use; float noise under half that grain snaps level.

    ONE INTERPRETATION, recorded so the GM can reverse it: a subject at a SQUARE rotation (0, 90,
    180, 270) keeps a level caption. Such a thing has a horizontal edge, so level text is aligned
    with it - the rule is "aligned with the thing", and a 90-degree box read level is; it is also
    what keeps every level caption in the pool byte-identical. Everything else - the notice board at
    -122.8, a 72-degree road, a 102-degree yard - carries its exact angle."""
    t = (rot + 90.0) % 180.0 - 90.0
    if abs(t) < 0.05 or abs(abs(t) - 90.0) < 0.05:
        return 0.0
    return round(t, 1)


def linear_tilt_full(rot: float) -> float:
    """The GM's 2026-08-09 EXTENSION of the linear-caption rule: a LINE subject's caption may
    carry its FULL tilt, past linear_tilt's 45-degree go-level clamp - the cartographic
    along-feature convention (a river's name lies along the river at whatever bearing the river
    runs). Opt-in per call site (label(full_tilt=True)): the clamp stays the default, so every
    existing road caption in the pool - including Hoshizora's level "Imperial Road", the ruling
    that set the clamp - is byte-identical. Normalized to [-90, 90) so a bearing and its reverse
    caption identically and the text never renders upside down. Since 2026-08-27 this is simply
    the general rule (`aligned_tilt`); kept as a name so its call sites read as they were written."""
    return aligned_tilt(rot)


def linear_tilt(rot: float) -> float:
    """The caption tilt for a LINEAR subject - a road, a street, a row of shopfronts laid along
    one (GM 2026-08-08: Hoshizora's "Imperial Road" and "merchant houses & shops" read level
    beside a roadbed running at -27 degrees). A line has ONE axis, not a building's two edge
    families, so this CLAMPS where `label_tilt` FOLDS, and the two must never be swapped:

    - The angle is normalized to [-90, 90) - a bearing and its reverse describe the same line,
      so a road stored SW-to-NE and the same road stored NE-to-SW caption identically.
    - Past 45 degrees the caption goes LEVEL rather than tilting. That is the GM's own rule for
      a north-south road ("it is reasonable to have the label still read left-to-right"), and it
      generalizes: text steeper than 45 degrees is hard to read, and unlike a building there is
      no second edge family to fall back on - a near-vertical road's cross direction is not an
      axis of anything drawn. Folding a 72-degree road (Nagahara's Imperial approach) to -18
      would tilt the caption to match NOTHING on the map, which is worse than level.

    The 45-degree cutoff is therefore a discontinuity by design: a 44-degree road tilts, a
    46-degree one does not. It never shows WITHIN a map (a caption names one stretch of one
    road), and legibility is the thing being protected at the boundary either way.

    SUPERSEDED 2026-08-27 (GM, feature 133 T38): a caption is aligned with the thing it names, at
    exactly its angle - so the clamp is gone and this is `aligned_tilt`. The 2026-08-08 ruling it
    encoded (a north-south road may keep a level caption) is reversed by the general rule; if the
    GM wants that exception back it is one line here, and the record says which line."""
    return aligned_tilt(rot)


def label_quad(L: Sequence[Any]) -> Poly:
    """The drawn corner ring of a recorded label. Elements [0..3] are the caption's UNROTATED box
    (what `_record_label` has always written); a TILTED caption (element [7], degrees - see
    `label_tilt`) is that box rotated about its own center, exactly the SVG transform `label()`
    emits, so a check reads the true glyph run straight off the record. A level record returns
    its plain corners."""
    x0, y0, x1, y1 = float(L[0]), float(L[1]), float(L[2]), float(L[3])
    cs: Poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    t = float(L[7]) if len(L) > 7 and L[7] else 0.0
    if not t:
        return cs
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    ca, sa = math.cos(math.radians(t)), math.sin(math.radians(t))
    return [(cx + (qx - cx) * ca - (qy - cy) * sa, cy + (qx - cx) * sa + (qy - cy) * ca) for qx, qy in cs]


def label_aabb(L: Sequence[Any]) -> tuple[float, float, float, float]:
    """A recorded label's axis-aligned bounds - what the CONTAINMENT consumers (frame clipping,
    the crop's must-include list, blocker lists, the title search) test. Identical to elements
    [0..3] for a level record; for a tilted one it is the rotated quad's AABB - the honest
    'ground this text can reach'."""
    q = label_quad(L)
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    return (min(xs), min(ys), max(xs), max(ys))
