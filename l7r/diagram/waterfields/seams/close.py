"""Split from waterfields/seams.py by feature 173 - see this package's CLAUDE.md for the index.

Research: re-hold plumbing - NONE: lazy shapely binding and the split loop's bound
"""

from __future__ import annotations

import math
from collections.abc import Collection
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # shapely's names for the type checker; `_load_shapely` binds the runtime ones
    from shapely.geometry import Polygon

from ..banks import (
    _TOE_MIN_APEX,
    _TOE_MIN_AREA,
    is_chevron,
    jog_vertices,
    pointed_ring,
)
from ..frame import Pt
from ..ring_rules import MAX_STEPS, RingContext, as_recorded, ring_area, ring_violations
from ..settle import PINHOLE, welded
from .geoms import GeomTree, ring_polygons
from .pockets import _parts, _ring

_SHAPELY_LOADED = False


def _load_shapely() -> None:
    """Bind shapely's names into this module, on first use rather than at import (feature 237, FR-010).

    WHY. `import shapely` costs 16.3 MiB of resident memory - it pulls numpy in with it - and a module-level
    import here made all ten gate workers pay that merely to COLLECT this package, whichever one of them ran
    the geometry (`specs/237-lean-test-collection/research.md` R9). Only a worker that builds a map needs it.

    WHY NOT AN `import` INSIDE THE FUNCTIONS THEMSELVES. Several of them run per plot, per seam or per
    candidate, and an `import` statement re-enters `__import__` on every call. Binding the names into this
    module's own globals ONCE leaves every call site the plain global lookup it already was, so the deferral
    costs nothing in steady state (spec D6); the sentinel makes a repeat call two bytecodes. An increase on
    any seed is not waiverable for this item - the bookends are `make perf LABEL=237-start|-end`.
    """
    global _SHAPELY_LOADED, Polygon  # binding this module's own names is the point
    if _SHAPELY_LOADED:
        return
    from shapely.geometry import Polygon

    _SHAPELY_LOADED = True


# past that the 'repair' is moving more ground than the step it retires, which is a land grab wearing a
# repair's clothes. Feature 152 T18; the lever itself was recorded untried (the jog residue it was for went with feature 302).


# A STAIRCASE IS CUT AT MOST THIS MANY TIMES. Each cut takes one step off a ring and hands back two rings with fewer
# steps between them, so a ring with n steps needs n - 1 cuts; 32 is far past any ring the pool carries (the worst the
# record names is cohort seed 12's four) and exists only so a degenerate ring cannot loop.
_SPLIT_LIMIT = 32


def hold_ring_rules(plots: list[dict[str, Any]], ctx: RingContext, only: Collection[int] | None = None) -> None:
    """The seam pass's last word on the rings (feature 287, water W16-W27): after it, every plot ring - judged AS THE
    MANIFEST RECORDS IT, rounded to 0.1 px - keeps every rule `ring_rules.ring_violations` asks in `ctx`.

    A ring that breaks one is not kept as it stands, whatever made it (a carved ring no seam step touched, a weld the
    ladder had no clean host for, a repair). Its ground goes one of three ways, in this order:

    1. SPLIT, where the ring is a staircase (W23, one of the GM's five): cut along the line that continues the step's
       hop across the basin - the GM's own description of the right form, the wall "continuing on and meeting at the
       four way intersection" instead of going "sharply to the left before going down" (Inashiro, 2026-08-18). Each part
       that keeps every rule is a basin of its own.
    2. WELDED into the neighbor it shares the most bund with, when the union keeps every rule - research/contents.json#fields 'Bunds
       are shared': the odd scrap is "taken into the basin beside it rather than walled off on its own".
    3. BARE, under the fan floor `comb_base_fill` draws - "the odd corner left unpaddied" the same research describes,
       which the Sawada review confirmed invisible in ink (`pockets._absorb`'s last branch).

    Never a violating ring kept because nothing better was found (FR-005). No draw from any random stream: split parts
    keep their parent's fill, so the count of plots may change but no color re-rolls. `only` confines the judgment to the plots
    it names (a later stage that reshaped a few rings - the grave island's carve - asks of those alone); welds still reach
    any neighbor.

    Research:
        staircase split on its hop - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a bund never steps sideways and carries on, so the step is carried straight across
        scrap welded to its neighbor - research/questions/0014-bunds-between-the-paddies-aze.drawing.html, research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: into the basin it shares the most bund with
        scrap left bare - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: what no weld makes lawful stays bare, the fan floor drawn under it
        judged at the placer's lines - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a ring it keeps, split or welded, holds `held_faults` - the gate's rules and the placer's 25 deg, quarter cell and arrowhead under them
    """
    _load_shapely()
    bad = [k for k in (range(len(plots)) if only is None else sorted(only)) if held_faults(as_recorded(plots[k]["poly"]), ctx)]
    if not bad:
        return
    scraps: list[Polygon] = []
    added: list[dict[str, Any]] = []
    gone: set[int] = set()
    for k in bad:
        p = plots[k]
        ring = as_recorded(p["poly"])
        pieces = [q for part in (_parts(Polygon(ring).buffer(0)) if len(ring) >= 3 else []) for q in (_split_steps(part, ctx) if ctx.g else [part])]
        kept = [q for q in pieces if not held_faults(_ring(q), ctx)]
        scraps += [q for q in pieces if q not in kept]
        if kept:
            p["poly"] = _ring(kept[0])
            added += [{**p, "poly": _ring(q)} for q in kept[1:]]
        else:
            gone.add(k)
    plots[:] = [p for k, p in enumerate(plots) if k not in gone] + added
    geoms: list[Any] = ring_polygons([p["poly"] for p in plots])
    tree = GeomTree(geoms)
    for scrap in sorted(scraps, key=lambda q: (round(q.bounds[0], 1), round(q.bounds[1], 1))):
        _weld_within_rules(scrap, plots, geoms, tree, ctx)


def held_faults(ring: Any, ctx: RingContext) -> set[str]:
    """What a ring the re-hold keeps must not break: every rule `ring_violations` asks (the gate's lines), and the placer's own
    lines under them - no point sharper than `_TOE_MIN_APEX`, no basin under `_TOE_MIN_AREA` of the design cell, no
    arrowhead at `is_chevron`'s 40 deg and 0.90 (feature 328 wave 78: the re-hold kept welds and split pieces at the gate's
    15 deg and 0.20, which leave the margin a checker needs, not the basin 0005 draws).

    Research: held at the placer's lines - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: no basin tapers to a point sharper than 25 degrees, none is under a quarter of its design cell, none is an arrowhead
    """
    faults = set(ring_violations(ring, ctx))
    if len(ring) >= 3 and pointed_ring(ring, _TOE_MIN_APEX):
        faults.add("needle")
    if ctx.cell and ring_area(ring) < _TOE_MIN_AREA * ctx.cell:
        faults.add("area")
    if len(ring) >= 3 and is_chevron(ring):
        faults.add("arrowhead")
    return faults


def _weld_within_rules(scrap: Polygon, plots: list[dict[str, Any]], geoms: list[Any], tree: GeomTree, ctx: RingContext) -> bool:
    """Weld `scrap` into the plot it shares the most bund with, among those whose union keeps every ring rule; False,
    and the scrap left bare, when none does. The union is taken as `_absorb` takes it - the scrap grown by 0.02 px so
    two polygons that only touch merge, welded where a hairline or a pinhole remains (`settle.welded`), and simplified at 0.05
    px only when that stays a simple polygon.

    Research: weld host - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: the lawful neighbor sharing the most bund, else bare
    """
    reach = scrap.buffer(0.4)
    grown = scrap.buffer(0.02)
    ranked = sorted((-geoms[j].boundary.intersection(reach).length, j) for j in tree.near(scrap.bounds, pad=1.0))
    for neg, j in ranked:
        if neg >= 0.0:
            break  # sorted: every host after this one shares no bund with the scrap either
        merged = geoms[j].union(grown).buffer(0)
        if not isinstance(merged, Polygon) or any(Polygon(r).area < PINHOLE for r in merged.interiors):
            merged = welded(merged)  # a hairline or a pinhole the grid left is not a gap between basins (feature 328 wave 77)
        if not isinstance(merged, Polygon) or merged.interiors:
            continue
        simplified = merged.simplify(0.05)
        candidate = simplified if isinstance(simplified, Polygon) and simplified.is_valid and not simplified.interiors else merged
        ring = _ring(candidate)
        if held_faults(ring, ctx):
            continue
        plots[j]["poly"] = ring
        geoms[j] = Polygon(ring).buffer(0)
        tree.replaced(j)
        return True
    return False


def _split_steps(poly: Polygon, ctx: RingContext) -> list[Polygon]:
    """`poly` cut, one step at a time, until no part carries more than `ring_rules.MAX_STEPS` sideways steps (W23).

    Each cut continues a step's hop across the basin (`_cut_on_hop`). WHICH HOP: a staircase of even treads and risers
    reads both ways - each tread is also the hop between two risers - so every hop is tried and the cut kept is the one
    leaving the fewest parts that break a rule other than the steps still to be cut, then the one whose smallest part is
    largest (first on a tie, in ring order): the cut that makes basins, not scraps - a riser carried across the whole
    basin, not a tread shaved off it. A ring none of whose hops can be cut is handed back whole, and the caller judges it
    as it stands - a staircase goes to the scrap path, never onto the map.

    Research: no sideways step - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: cut until no part steps more than MAX_STEPS times, the cut that makes basins not scraps
    """
    g = float(ctx.g or 0.0)
    done: list[Polygon] = []
    todo = [poly]
    for _ in range(_SPLIT_LIMIT):
        if not todo:
            break
        q = todo.pop()
        hops = jog_vertices(_ring(q), g)
        cuts = [cut for b, c in hops for cut in [_cut_on_hop(q, b, c)] if cut] if len(hops) > MAX_STEPS else []
        if cuts:
            todo += min(cuts, key=lambda cut: (sum(1 for part in cut if ring_violations(_ring(part), ctx) - {"steps"}), -min(part.area for part in cut)))
        else:
            done.append(q)
    return done + todo


def _cut_on_hop(poly: Polygon, b: Pt, c: Pt) -> list[Polygon]:
    """`poly` split along its hop `b`-`c` continued into the basin until it meets the far bund - or [] where it cannot be.

    The hop runs between a wall and the same wall resumed a few feet over, so exactly one of its two ends is the reflex
    corner the basin's floor lies beyond: the knife starts there and runs on, in the hop's own direction, to where it
    first leaves the basin. That is the wall the step should have been - carried straight on to the junction.

    Research: wall carried on to the junction - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: the hop continued straight across the basin to the far bund
    """
    from shapely.geometry import LineString as _Line
    from shapely.geometry import Point as _Point
    from shapely.ops import split

    x0, y0, x1, y1 = poly.bounds
    far = 2.0 * math.hypot(x1 - x0, y1 - y0) + 10.0
    for s, r in ((b, c), (c, b)):
        length = math.dist(s, r)  # never zero: `jog_vertices` names a hop only when it has length
        ux, uy = (r[0] - s[0]) / length, (r[1] - s[1]) / length
        if not poly.contains(_Point(r[0] + 0.5 * ux, r[1] + 0.5 * uy)):
            continue  # this end's continuation runs outside the basin: the other end is the reflex corner
        inside = _Line([r, (r[0] + far * ux, r[1] + far * uy)]).intersection(poly)
        runs = sorted((q for q in getattr(inside, "geoms", [inside]) if isinstance(q, _Line) and not q.is_empty), key=lambda q: q.distance(_Point(r)))
        for first in runs[:1]:  # the stretch that starts at the corner - a concave basin can be re-entered further on
            reach = max(math.dist(r, q) for q in first.coords)
            knife = _Line([r, (r[0] + (reach + 1.0) * ux, r[1] + (reach + 1.0) * uy)])
            parts = _parts(split(poly, knife))
            if len(parts) >= 2:
                return parts
    return []
