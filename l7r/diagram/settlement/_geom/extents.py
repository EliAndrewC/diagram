"""A recorded feature's DRAWN extent, read back off the manifest.

One subject, and it is a doctrine rather than a shape: each of these is the SINGLE definition of
where some ink actually is, so that the placer and the check that grades it cannot disagree
(skill CLAUDE.md, 'Placement and its check must read the SAME manifest source').

Split from settlement/_geom.py by feature 117 - see settlement/_geom/CLAUDE.md for the index.

Research: drawn-extent readers - NONE: read a recorded feature's ink back off the manifest
"""

import math
from collections.abc import Mapping, Sequence
from typing import Any

from .base import Manifest, Poly


def forest_reveal_x(forest: Poly, edge: Poly | None, reveal: float, w: float) -> list[float]:
    """The x-values a canvas-filling FOREST contributes to the crop frame (mirrored by
    check_village.forest_reveal_x - keep the two in sync; the crop and the check that gates the
    crop's tightness must read the same rule from the same manifest fields).

    The wood is drawn all the way to the canvas edge, but the frame only REVEALS a shallow band of
    it past the tree line: the tree line itself plus `reveal` px of canopy behind it. Deeper in it
    is identical crowns, and a frame held open for them is wasted image (GM 2026-07-25). Without a
    recorded tree line (M['forest_edge']) the whole clamped polygon sets the frame, as it used to."""
    if not edge:
        return [min(max(p[0], 0), w) for p in forest]
    ex = [min(max(p[0], 0), w) for p in edge]
    return ex + [min(x + reveal, w) for x in ex]


def forest_frame_span(vals: Sequence[float], limit: float, other: Sequence[float]) -> tuple[float, float]:
    """One axis of the EDGE forest's frame contribution (mirrored by check_village's crop_hugs_content -
    keep the two in sync). `vals` are the wood's already-clamped values on that axis, `limit` the canvas
    size, `other` every value the REST of the content contributes there.

    A tree line that runs off BOTH ends of an axis is running ALONG it, not bounding anything: the wood
    continues past whatever frame we choose, so pinning that edge to the canvas holds the view open for
    more of the same crowns - the identical waste the reveal band already rejects on the axis the wood
    FACES (GM 2026-07-25: Moritono's north edge sat at the canvas top because the Shirin Forest, an
    east-edge wood drawn from y=-10 to y=1510, spanned the full height, while the northernmost real
    content - a well - stood 157px in; the tree line still runs off a tighter north edge, which is the
    reading we want). On such an axis the wood takes the span the rest of the content sets, so it can
    neither extend nor shrink the frame. Otherwise its own span is content, as before."""
    lo, hi = min(vals), max(vals)
    if lo <= 0 and hi >= limit and len(other):
        return max(0.0, min(other)), min(limit, max(other))
    return min(max(lo, 0.0), limit), min(max(hi, 0.0), limit)


def paddy_wet_rings(M: Manifest) -> list[Poly]:
    """The rings that are a paddy field's WATER - the ground a wellhead may not stand in.

    `Settlement._well_ground_clear` (placement) and `wells_clear_of_paddies` (the verdict) both read
    this ONE function, so the siter and the check cannot disagree about where the water is - the trap
    recorded in this skill's CLAUDE.md under "Placement and its check must read the SAME manifest
    source".

    PREFER THE DRAWN PLOTS. `plot_polys` holds the individual bunded basins as they are drawn, so it
    is the ink a reader sees, and reading it leaves the fan's unplanted RIM SLACK available - which
    matters, because the smoothed `outline` is an ENVELOPE claiming more ground than the crop fills,
    and that margin was exactly where the town tier's farm wells (retired by feature 392) seated the well of a steading
    boxed in by crop. Treating the envelope as water refuses legitimate
    margin, and on Tango's east fan it left a steading with no legal seat anywhere.

    FALL BACK TO THE OUTLINE where a field records no plots, rather than skipping that field. Only
    the three provincial cities record `plot_polys` today; all 23 rural paddy fields in the pool
    record just an outline, so a plots-only rule would silently never run on a single hamlet,
    village or town - and a check that never runs looks exactly like a check that passes (same
    CLAUDE.md). Where the plots are not recorded the fan is drawn as one wet body anyway, so its
    outline IS the edge of the water. The fallback costs nothing today: swept across the pool, no
    well on any map stands inside a paddy outline."""
    rings: list[Poly] = []
    for fl in M.get("fields") or []:
        if fl.get("kind") != "paddy":
            continue
        drawn = [r for r in ([(float(p[0]), float(p[1])) for p in q] for q in (fl.get("plot_polys") or [])) if len(r) > 2]
        if drawn:
            rings.extend(drawn)
            continue
        ring = [(float(p[0]), float(p[1])) for p in (fl.get("outline") or [])]
        if len(ring) > 2:
            rings.append(ring)
    return rings


def tower_quad(t: Mapping[str, Any], grow: float = 0.0) -> Poly:
    """A wall tower's drawn footprint: its `w` x `h` mamian rect turned onto the wall's local
    tangent (`rot`). The default 38 x 38 is the pre-to-scale mamian, for a legacy record."""
    hw_, hh_ = t.get("w", 38) / 2 + grow, t.get("h", 38) / 2 + grow
    a = math.radians(t.get("rot", 0))
    ca, sa = math.cos(a), math.sin(a)
    return [(t["x"] + dx * ca - dy * sa, t["y"] + dx * sa + dy * ca) for dx, dy in ((-hw_, -hh_), (hw_, -hh_), (hw_, hh_), (-hw_, hh_))]
