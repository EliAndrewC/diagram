"""A seat's geometry and the cluster's drawn shape, split from `stages.py` (feature 316): how far a box moves off the water,
how far a turned house's seat moves out, which bank of the brook a point stands on, and the cluster shape the houses draw.
Bodies moved verbatim; `stages.py` re-exports every name, so callers and tests are unchanged.

Research: seat geometry - NONE: distances, sides and aspects measured; the rules that decide are each unit's own"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from l7r.diagram.settlement import seg_dist

from ..consts import CLUSTER_DRAWN_ASPECT, CLUSTER_SHAPES, Pt
from ..plan import _roll
from .seats import cluster_aspect


def bank_of(x: float, y: float, brook: Sequence[Pt]) -> int:
    """Which side of the brook a point stands on: the sign of its offset from the NEAREST reach of the course.

    A CROSSING TEST IS NOT A SIDE TEST, and that mistake cost two rolls. Asking whether the line from one house
    to another crosses the brook reads a curving course wrongly - the brook comes down one flank and wraps the
    field's toe, so two houses on the same bank can have the water between them as the crow flies, and every
    candidate after the first was refused (1 house of 15 seated on three maps). The side of the nearest reach is
    local, so a bend cannot invert it."""
    j = min(range(len(brook) - 1), key=lambda i: seg_dist(x, y, brook[i], brook[i + 1]))
    (ax, ay), (bx, by) = brook[j], brook[j + 1]
    return 1 if (bx - ax) * (y - ay) - (by - ay) * (x - ax) >= 0 else -1


def shapes_drawn_at(drawn: float) -> list[str]:
    """The cluster shapes whose drawn band (`CLUSTER_DRAWN_ASPECT`) holds a drawn aspect - a shape other than round only
    past round's ceiling (the settlement-review of Inashiro, feature 261: crescent's band starts at 1.9 and round's ends
    at 2.0, and a quarter-disc of houses drawn at 1.97 is round). Past every band, the nearest band's shape.

    Research:
        shapes a drawing admits - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the shapes the page names (lump, string, crescent, split)
        aspect bands and round first - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass B, 2026-10-25); round 1.0-2.0, crescent and split 1.9-4.2, elongated 2.8-12; another shape only past round's ceiling; past every band, the nearest band's
    """
    ceiling = CLUSTER_DRAWN_ASPECT["round"][1]
    held = [k for k, (lo, hi) in CLUSTER_DRAWN_ASPECT.items() if (lo if k == "round" else max(lo, ceiling + 1e-9)) <= drawn <= hi]
    return held or [min(CLUSTER_DRAWN_ASPECT, key=lambda k: min(abs(drawn - CLUSTER_DRAWN_ASPECT[k][0]), abs(drawn - CLUSTER_DRAWN_ASPECT[k][1])))]


def declare_cluster_shape(houses: Sequence[dict[str, Any]], shape: str | None, seed: int) -> dict[str, Any]:
    """The cluster shape the manifest declares, and the plan keeps: the rolled shape wherever the houses draw it, and
    otherwise the knob RESOLVED OVER THE SHAPES THE DRAWING ADMITS (feature 287, homes H05, plan D4) - `shapes_drawn_at`,
    rolled from the map's seed with the knob's own weights (`CLUSTER_SHAPES`). The drawn shape is the declared shape on
    every map; there is no `cluster_shape_unhonored` record. The stage and its unit test read this one function.

    D4'S OTHER HALF WAS TRIED FIRST AND MEASURED A NO-OP (2026-09-29): steering the rank rounds toward the rolled shape -
    the along-the-field ends offered before the ranks while the standing houses draw rounder than the shape's band - left
    31 of 64 maps (pool and cohort 1-60) drawing a crescent or a string rounder than its band, the same 31 as without it:
    the front row, the brook's far bank and the field's chords seat the cluster, and the ends are refused where the ranks
    were. The record of three earlier failed bindings (`CLUSTER_BAND_ASPECT`) says the same. So the knob is narrowed to
    what the band draws, which D4 allows: on that measurement round is declared on 57 of the 64 maps, crescent on
    6, elongated on 1.

    Research:
        cluster shape knob - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the rolled shape kept where the houses draw it, else rolled again, with the knob's weights, over the shapes the drawing admits
    """
    drawn = cluster_aspect([h["x"] for h in houses] or [0.0], [h["y"] for h in houses] or [0.0])
    space = shapes_drawn_at(drawn)
    rolled = shape or "crescent"
    resolved = rolled if rolled in space else str(_roll(seed, "cluster_shape", tuple(v for v in CLUSTER_SHAPES if v in space) or tuple(space)))
    return {"cluster_shape": resolved, "cluster_aspect_drawn": round(drawn, 2)}
