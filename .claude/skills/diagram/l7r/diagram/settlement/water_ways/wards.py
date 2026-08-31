"""Split from settlement/water_ways.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from typing import TYPE_CHECKING, Any

from .._geom import (
    WARD_BARRED_KINDS,
    Poly,
    point_in_poly,
    seg_closest,
    seg_intersect,
    segments_cross,
    ward_interior,
)

if TYPE_CHECKING:
    from ..core import Settlement


class WardsMixin:
    _WARD_STROKE = 5.0  # the fence's drawn width; recorded so check_village measures the ink, not the vertex

    def _ward_ends_on_wall(self: Settlement, boundary: Poly, reach: float = 24.0) -> Poly:  # type: ignore[misc]
        """JOIN, DON'T INTERSECT: snap each ward-fence END onto the city rampart's centerline.

        The placement half of the rule `city_ward_fence_joins_wall_not_crosses` gates (GM 2026-07-27,
        on Minami: "the neighborhood walls stick out the other side of the city walls"). A ward fence
        ENDS at the wall - the rampart is what seals the ward, so a palisade continuing out through it
        into the berm encloses nothing and draws as two walls crossing at an intersection. This is the
        wall member of the family the ways and the watercourses already had: a lane terminates at the
        through-lane it meets rather than poking a stub out the far side, and a watercourse joins at a
        T or a Y rather than crossing.

        A gen hand-places the fence's ends, and getting one onto the wall line by eye is hopeless -
        Minami's were 4.2-4.9px outside, Tango's 2.9-4.0px, none of it visible in a gen and all of it
        inside `city_ward_fence_meets_wall`'s 10px tolerance. So the engine puts them there instead:
        the end is EXTENDED (or trimmed) ALONG ITS OWN TERMINAL SEGMENT to where that line crosses the
        wall ring - the same "extend along its own axis, never diagonally to the nearest point" rule
        `city_streets_meet_through_lanes` states for a lane meeting a through-lane, because a
        perpendicular snap would swing the last stretch of fence off the line the gen drew. Where the
        terminal segment runs parallel to the wall and never meets it, the nearest point on the ring is
        the honest fallback. An end further than `reach` from the wall is left exactly as placed: that
        is not a junction at all but a fence that fails to reach the rampart, which is
        `city_ward_fence_meets_wall`'s defect to report, and silently dragging it 200px would hide it.
        """
        wall = self.M.get("wall")
        if not wall or len(boundary) < 2:
            return boundary
        ring: Poly = [(x, y) for x, y in wall]
        ring = ring + [ring[0]]
        out = list(boundary)
        for idx, inward in ((0, 1), (len(out) - 1, len(out) - 2)):
            end, prev = out[idx], out[inward]
            near = min((seg_closest(end[0], end[1], ring[i], ring[i + 1]) for i in range(len(ring) - 1)), key=lambda c: math.hypot(c[0] - end[0], c[1] - end[1]))
            if math.hypot(near[0] - end[0], near[1] - end[1]) > reach:
                continue  # not an abutting end - city_ward_fence_meets_wall reports that gap
            dx, dy = end[0] - prev[0], end[1] - prev[1]
            dl = math.hypot(dx, dy) or 1.0
            far = (end[0] + dx / dl * reach, end[1] + dy / dl * reach)
            back = (end[0] - dx / dl * reach, end[1] - dy / dl * reach)
            hits = [ip for i in range(len(ring) - 1) if segments_cross(back, far, ring[i], ring[i + 1]) and (ip := seg_intersect(back, far, ring[i], ring[i + 1])) is not None]
            out[idx] = min(hits, key=lambda p: math.hypot(p[0] - end[0], p[1] - end[1])) if hits else near
        return out

    def ward(self: Settlement, name: str, boundary: Any, gates: Any) -> None:  # type: ignore[misc]
        """An internal WARD boundary - a light earthwork/palisade fence (NOT a city rampart) that
        SEALS a quarter (the samurai/government ward) off the commoner streets, so its kido gates
        cannot simply be walked around: the fence is continuous between the gates, its ends abut
        the city wall, and a street may pierce it ONLY at a gate. `boundary` is the fence polyline;
        `gates` are (x, y) kido seats where a street crosses it (a legacy third element - the old
        horizontal flag - is accepted and ignored). PLACEMENT RULE (GM 2026-07-26, refining the
        2026-07-24 fence rule): each kido SQUARES TO THE LANE RUNNING THROUGH IT - a gate exists to
        shut a way, so the bar stands across the roadbed and the fence meets it obliquely if that is
        how the fence runs. Only a gate with no lane through it falls back to the LOCAL FENCE
        TANGENT (never an axis-aligned stamp on a slanted run). Its guard box stands on the
        WARD-INTERIOR flank (the gate watch belongs to the ward it seals), nudged clear of the
        roadbed by s.kido. Records M['wards']."""
        boundary = self._ward_ends_on_wall([(p[0], p[1]) for p in boundary])
        dd = 'M' + ' L'.join(f'{x},{y}' for x, y in boundary)
        fz = self.add(f'<path d="{dd}" fill="none" stroke="#9C8A5E" stroke-width="{self._WARD_STROKE:g}" opacity="0.9" stroke-linejoin="round" stroke-linecap="round"/>')
        self.add(f'<path d="{dd}" fill="none" stroke="#4A3A22" stroke-width="1.3" stroke-dasharray="2,7" opacity="0.85"/>')  # palisade
        self.corridors.append((boundary, 11))  # buildings keep off the fence line
        # the fence ends ABUT the city wall: lay a short wall-stroke CAP over each end so the rampart
        # renders ON TOP of the fence there (the fence runs UNDER the wall), not the fence over the wall.
        # The cap FOLLOWS the wall (arc-length +/-16 px through any vertex in the span) rather than being a
        # single straight tangent: a fence that abuts AT a wall corner used to get a straight stub tangent to
        # one segment only, which juts past the bend and reads as a second wall section overlapping the first
        # (Nagahara SW, GM 2026-07). A wall-following cap stays flush at both corners and flat runs.
        caps: list[Any] = []
        wall = self.M.get("wall")
        if wall:
            pts_w = [(x, y) for x, y in wall]
            ring = pts_w + [pts_w[0]]
            perim = self._wall_perimeter(pts_w)
            n_w = len(pts_w)
            varcs = []  # cumulative arc of each wall vertex, to fold corners into the cap span
            _acc = 0.0
            for i in range(n_w):
                varcs.append(_acc)
                _acc += math.hypot(ring[i + 1][0] - ring[i][0], ring[i + 1][1] - ring[i][1])
            for ex, ey in (boundary[0], boundary[-1]):
                best: Any = None
                for i in range(len(ring) - 1):
                    cx, cy = seg_closest(ex, ey, ring[i], ring[i + 1])
                    d = math.hypot(cx - ex, cy - ey)
                    if best is None or d < best[0]:
                        best = (d, (cx, cy))
                if best and best[0] < 24:  # the end abuts the wall - cap it
                    px, py = best[1]
                    arc = self._wall_arc_of(pts_w, (px, py))
                    a0, a1 = arc - 16, arc + 16
                    span: list[tuple[float, tuple[float, float]]] = [
                        (a0, self._wall_point_at_arc(pts_w, a0)[:2]),
                        (arc, (px, py)),
                        (a1, self._wall_point_at_arc(pts_w, a1)[:2]),
                    ]
                    for vi in range(n_w):  # fold in any wall vertex the cap crosses, so the cap bends WITH the rampart
                        for va in (varcs[vi] - perim, varcs[vi], varcs[vi] + perim):
                            if a0 < va < a1:
                                span.append((va, (pts_w[vi][0], pts_w[vi][1])))
                    cappts = [(round(x, 1), round(y, 1)) for _, (x, y) in sorted(span, key=lambda s: s[0])]
                    dd_cap = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in cappts)
                    cz = self.add(f'<path d="{dd_cap}" fill="none" stroke="#3A352C" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>')
                    caps.append({"x": round(px, 1), "y": round(py, 1), "z": cz, "pts": [[x, y] for x, y in cappts]})
        # "stroke" is the fence's DRAWN width: the palisade is stroked with a round linecap, so its ink
        # runs half of this past the last recorded vertex, and city_ward_fence_joins_wall_not_crosses
        # has to test that tip rather than the coordinate to see an overshoot through the rampart
        self.M.setdefault("wards", []).append({"name": name, "boundary": [[round(x, 1), round(y, 1)] for x, y in boundary], "z": fz, "stroke": self._WARD_STROKE, "wall_caps": caps})
        # THE FENCE SEALS COMMONERS OUT, so from this moment s.building refuses their dwellings and
        # shops inside it (WARD_BARRED_KINDS; GM 2026-08-02, Minami). ORDERING-CRITICAL: only
        # placements AFTER s.ward are guarded - a commoner already standing inside when the fence
        # goes up is a gen-ordering bug (hoist s.ward ahead of every commoner pack), and it fails
        # LOUDLY here rather than shipping and waiting for the gate to notice.
        if name == "samurai":
            interior = ward_interior([(p[0], p[1]) for p in boundary], [(p[0], p[1]) for p in (wall or [])])
            if interior:
                self._samurai_ward_interiors.append(interior)
                early = [(b["kind"], round(b["x"]), round(b["y"])) for b in self.M.get("buildings", []) if b["kind"] in WARD_BARRED_KINDS and point_in_poly(b["x"], b["y"], interior)]
                if early:
                    raise ValueError(f"commoner building(s) already inside the {name} ward when its fence was declared - hoist s.ward ahead of the commoner packs: {early[:8]}")
        for gate in gates:
            gx, gy = gate[0], gate[1]
            grot, gside = self.kido_seat(gx, gy, boundary)  # square to the lane it bars (the fence only where no lane runs through); guard box toward the ward interior
            self.kido(gx, gy, rot=grot, guard_side=gside)
        self._assert_walls_clear_of_torii(f"the {name} ward fence")  # a fence laid across a standing arch (Nagahara 2026-07-25)

    _QUARTER_ZONES = ("residential", "civic", "mixed", "reserve", "castle", "samurai")
    # "castle" and "samurai" are CAPITAL vocabulary (feature 021): the citadel's own ground and
    # the senior-compound bands. Both are deliberately outside the residential density body
    # (a C_YASHIKI compound is ~0.24 dwellings/1000px^2, legitimately under the machi floor)
    # and outside the civic-openness and reserve-cap rules; the tiling check counts them like
    # any quarter, so the interior stays fully declared.
    _RESERVE_KINDS = ("drill_ground", "garden", "agricultural_district")

    def quarter(self: Settlement, poly: Any, zone: str, kind: Any = None, label: Any = None) -> None:  # type: ignore[misc]
        """Declare a city QUARTER as a first-class zoned region (feature 006). A walled city is a
        set of quarters tiling its interior, each with a ZONE - `residential`, `civic`, `mixed`, or
        `reserve` - so density is judged PER QUARTER (an empty block in a residential quarter is a
        defect; the same emptiness in a declared civic/reserve quarter is intentional). Purely
        DECLARATIVE: it records the region + zone into M['quarters'] and does NOT move or place any
        building. A `reserve` quarter also carries a `kind` and is DRAWN as that visible feature
        (so open ground reads as a deliberate drill ground / garden / farmland, not accidental
        emptiness). Declare reserves BEFORE the packs so the surface renders under later features
        (like fields and streets). `poly` is a list of (x, y); `label` is an optional map label."""
        if zone not in self._QUARTER_ZONES:
            raise ValueError(f"quarter zone must be one of {self._QUARTER_ZONES}, got {zone!r}")
        if zone == "reserve":
            if kind not in self._RESERVE_KINDS:
                raise ValueError(f"a reserve quarter needs kind in {self._RESERVE_KINDS}, got {kind!r}")
            self._draw_reserve(poly, kind)
        elif kind is not None:
            raise ValueError(f"only a reserve quarter may carry a kind (got zone={zone!r}, kind={kind!r})")
        self.M["quarters"].append({"poly": [[round(x, 1), round(y, 1)] for x, y in poly], "zone": zone, "kind": kind, "name": label})
        if label:
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            self.label(sum(xs) / len(xs), sum(ys) / len(ys), label, 9, italic=True, color="#5A4326")

    def _draw_reserve(self: Settlement, poly: Any, kind: str) -> None:  # type: ignore[misc]
        """Render a reserve quarter's ground as its declared kind. A drill_ground is bare packed
        earth with a dashed muster perimeter; a garden is a planted green sward. An
        agricultural_district draws NOTHING here (GM 2026-07-22): its own combs, farmhouses, and
        label ARE the rendering - the faint dashed boundary this used to add read as a stray dotted
        line cutting through the in-wall farmhouses and across the Imperial road above the burakumin
        neighborhood. The quarter stays DECLARED in M['quarters'] either way (recorded by quarter(),
        not here), so per-quarter density judging is unaffected."""
        if kind == "agricultural_district":
            return  # no boundary line - the generator's fields carry the whole visual
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in poly)
        if kind == "drill_ground":
            # a muster / archery field: flat swept earth, a dashed perimeter, a few faint rake lines
            self.add(f'<polygon points="{pts}" fill="#D6C79E" stroke="#A9925C" stroke-width="1.4" stroke-dasharray="6,4"/>')
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            for k in range(1, 5):
                ry = y0 + (y1 - y0) * k / 5
                self.add(f'<line x1="{x0 + 6:.1f}" y1="{ry:.1f}" x2="{x1 - 6:.1f}" y2="{ry:.1f}" stroke="#BBA76E" stroke-width="0.8" opacity="0.6"/>')
        elif kind == "garden":
            # an ornamental / kitchen garden sward: soft green with planted rows
            self.add(f'<polygon points="{pts}" fill="#C4D3A0" stroke="#6E8A44" stroke-width="1.3"/>')
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            for k in range(1, 4):
                ry = y0 + (y1 - y0) * k / 4
                self.add(f'<line x1="{x0 + 6:.1f}" y1="{ry:.1f}" x2="{x1 - 6:.1f}" y2="{ry:.1f}" stroke="#6E9A40" stroke-width="2.0" stroke-linecap="round" opacity="0.75"/>')
