"""The ground the seating RESERVED, in the registry of what stands (feature 287 M8; plan M3's keep-out, woods W25).

Two reservations outlive the seating that makes them, and every later placer owes them a keep-out:

- THE ACCESS CORRIDORS (plan M3): each household is admitted only with a clear strip from its dooryard to the access tree,
  and "every later placement refuses to cover a corridor". The seating's own envelopes did (`AccessTree.covers_box`); the
  placers after it - the communal wells, the shared byres, the retirement houses, the title's pocket - did not, and cohort
  1-60 laid wells on four corridors the web then could not draw.
- THE RESERVED WOOD SEATS (woods W25, plan D9): each household's share of the wood floor, the copse seats it reserved.
  The copse plants them first, but it plants a seat only where its own tests admit it on the map as finished, and the
  web's lanes and the title's pocket, laid after the seating, took 14.7% of them on cohort 1-60 (lanes 2,866 seats, the
  pocket 95).

A reservation is not a drawn feature, so the overlap matrix does not class it; what keeps off it, and by how much, is the
reservation's own rule, written here once and asked by every placer through `Standing.conflicts` - the same question the
matrix is asked by, so a placer's `admits` answers both.

THE CORRIDOR'S RULE. No SOLID, ANNEX or GROUND record stands within the corridor's half-width of its line - but the parts
of the household it serves (its own yard, where its door stands). A way (WAY), water and a fixture on a way (a bridge) are
what a corridor carries or crosses.

THE SEAT'S RULE is the copse's own planting test, so a seat kept clear here is a seat the copse plants: a clump is refused
within a house's, a yard's, a bed's, a byre's, a shed's, a kura's or a retirement house's occupancy disc (half its
diagonal, the clump's radius and 2 px - `village_grove`'s `occ`), within a wellhead's (its drawn half-size, 1.05 clumps
and 1 px), and within a lane's half-width and the copse's lane buffer of its line (`_corridor_buffers`).

Research: reservation bookkeeping - NONE: binning, release and geometry
"""

from __future__ import annotations

import math
from collections.abc import Iterator, Sequence
from typing import Any

from l7r.diagram.settlement._geom import point_in_poly, seg_dist, segments_cross

from .taxonomy import OVERLAP_CLASS, _mx_same

Poly = Sequence[Sequence[float]]

#: The classes a corridor is kept clear of: built and worked ground. A way runs along it; water and a deck cross it.
CORRIDOR_KEEPERS = frozenset({"SOLID", "ANNEX", "GROUND"})
"""Research: a lane to every house - research/questions/0081-village-lanes.drawing.html: built and worked ground keeps off a household's access corridor; the paddy is no keeper because no corridor is laid on it (`access.corridor_clear` keeps every corridor off the field)"""

#: The records whose occupancy disc a copse clump may not stand in (`village_grove`'s `occ`), the kura among them - a crown
#: may not stand on a store either (`CANOPY_STRUCT_KEYS`).
SEAT_OCCUPIERS = frozenset({"houses", "threshing_yards", "gardens", "byres", "farm_sheds", "retirement_houses", "storehouses"})
"""Research: no clump on a roof, yard or bed - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: the records a copse clump keeps off"""

CELL = 120.0


def poly_seg_gap(poly: Poly, a: Sequence[float], b: Sequence[float]) -> float:
    """The least distance between a closed polygon and the segment a-b; 0 where they meet or one holds the other."""
    ring = [(float(q[0]), float(q[1])) for q in poly]
    u, v = (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))
    n = len(ring)
    if point_in_poly(u[0], u[1], ring) or point_in_poly(v[0], v[1], ring):
        return 0.0
    edges = [(ring[i], ring[(i + 1) % n]) for i in range(n)]
    if any(segments_cross(u, v, p, q) for p, q in edges):
        return 0.0
    return min(min(seg_dist(p[0], p[1], u, v) for p in ring), min(seg_dist(q[0], q[1], p, r) for q in (u, v) for p, r in edges))


def seat_radius(key: str, o: Any, clump: float) -> float | None:
    """How near a copse clump's seat a record of `key` may come (`village_grove`'s occupancy discs), None for a record the
    copse does not refuse a clump for.

    Research:
        clump clearances - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html:
            a building's half diagonal, half a clump and 2 px
        wellhead clearance - CONVENTION: the well's drawn radius, 1.05 clumps and 1 px, so no clump is drawn over the wellhead
    """
    if key in SEAT_OCCUPIERS and "x" in o and "w" in o and "h" in o:
        return 0.5 * math.hypot(float(o["w"]), float(o["h"])) + clump * 0.5 + 2.0
    if key == "wells" and "x" in o:
        return float(o.get("vr") or o.get("r") or 8.0) + clump * 1.05 + 1.0
    return None


class Reservations:
    """The reserved corridors and wood seats, binned once as they are reserved and asked per candidate."""

    def __init__(self) -> None:
        self.corridors: list[tuple[tuple[float, float], tuple[float, float], float, Any]] = []
        self._cbins: dict[tuple[int, int], list[int]] = {}
        self.seats: list[tuple[float, float]] = []
        self._sbins: dict[tuple[int, int], list[int]] = {}
        self.clump = 0.0
        self.lane_buffer = 0.0

    def __bool__(self) -> bool:
        return bool(self.corridors or self.seats)

    @staticmethod
    def _cells(x0: float, y0: float, x1: float, y1: float) -> Iterator[tuple[int, int]]:
        for gx in range(int(x0 // CELL), int(x1 // CELL) + 1):
            for gy in range(int(y0 // CELL), int(y1 // CELL) + 1):
                yield (gx, gy)

    def reserve_corridor(self, a: Sequence[float], b: Sequence[float], half: float, owner: Any = None) -> None:
        """Reserve the strip `half` either side of a-b, for the household at `owner` (its center) or none (the exit strip,
        the field's corridor)."""
        n = len(self.corridors)
        pa, pb = (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))
        self.corridors.append((pa, pb, float(half), owner))
        for cell in self._cells(min(pa[0], pb[0]) - half, min(pa[1], pb[1]) - half, max(pa[0], pb[0]) + half, max(pa[1], pb[1]) + half):
            self._cbins.setdefault(cell, []).append(n)

    def reserve_seats(self, seats: Sequence[Sequence[float]], clump: float, lane_buffer: float) -> None:
        """Reserve the copse seats, with the clump they are planted at and the copse's lane buffer."""
        self.clump, self.lane_buffer = float(clump), float(lane_buffer)
        for p in seats:
            n = len(self.seats)
            self.seats.append((float(p[0]), float(p[1])))
            self._sbins.setdefault((int(float(p[0]) // CELL), int(float(p[1]) // CELL)), []).append(n)

    def _seats_near(self, x0: float, y0: float, x1: float, y1: float) -> Iterator[tuple[float, float]]:
        for cell in self._cells(x0, y0, x1, y1):
            for n in self._sbins.get(cell, ()):
                yield self.seats[n]

    def _corridors_near(self, x0: float, y0: float, x1: float, y1: float) -> Iterator[tuple[tuple[float, float], tuple[float, float], float, Any]]:
        seen: set[int] = set()
        for cell in self._cells(x0, y0, x1, y1):
            for n in self._cbins.get(cell, ()):
                if n not in seen:
                    seen.add(n)
                    yield self.corridors[n]

    def conflicts(self, key: str, o: Any, extents: Sequence[tuple[str, Poly, Any, Any]]) -> list[tuple[str, str, float, float]]:
        """Every reservation recording `o` under `key` (drawn as `extents`) would cover: (key, "access corridor" or "wood
        seat", x, y).

        Research:
            access corridor - research/questions/0081-village-lanes.drawing.html: a household's strip to the lanes kept clear, but its own parts
            wood seats - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: a reserved copse seat kept off occupied ground and a lane's buffer
        """
        if not self:
            return []
        out: list[tuple[str, str, float, float]] = []
        for k, poly, own_id, parent in extents:
            if OVERLAP_CLASS.get(k) not in CORRIDOR_KEEPERS or not self.corridors:
                continue
            xs, ys = [q[0] for q in poly], [q[1] for q in poly]
            for a, b, half, owner in self._corridors_near(min(xs), min(ys), max(xs), max(ys)):
                if owner is not None and (_mx_same(owner, own_id) or _mx_same(owner, parent)):
                    continue  # the household's own parts: its door stands in its yard
                if poly_seg_gap(poly, a, b) < half:
                    out.append((k, "access corridor", round((a[0] + b[0]) / 2), round((a[1] + b[1]) / 2)))
                    break
        if not self.seats:
            return out
        r = seat_radius(key, o, self.clump) if isinstance(o, dict) else None
        if r is not None:
            x, y = float(o["x"]), float(o["y"])
            out += [(key, "wood seat", round(sx), round(sy)) for sx, sy in self._seats_near(x - r, y - r, x + r, y + r) if (sx - x) ** 2 + (sy - y) ** 2 < r * r][:1]
        elif key == "lanes" and isinstance(o, dict):
            pts = o.get("pts") or []
            gap = float(o.get("w") or 6.0) / 2.0 + self.lane_buffer
            for a, b in zip(pts, pts[1:], strict=False):
                hit = next(
                    (
                        (sx, sy)
                        for sx, sy in self._seats_near(min(a[0], b[0]) - gap, min(a[1], b[1]) - gap, max(a[0], b[0]) + gap, max(a[1], b[1]) + gap)
                        if seg_dist(sx, sy, (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) < gap
                    ),
                    None,
                )
                if hit is not None:
                    out.append((key, "wood seat", round(hit[0]), round(hit[1])))
                    break
        return out

    def corridors_mark(self) -> int:
        """How many corridors stand reserved - a mark `release_corridors_to` drops back to."""
        return len(self.corridors)

    def release_corridors_to(self, mark: int) -> None:
        """Release every corridor reserved since `mark` (`corridors_mark`): a reservation held only while one placer runs."""
        self.corridors = self.corridors[:mark]
        self._cbins = {cell: kept for cell, ns in self._cbins.items() if (kept := [n for n in ns if n < mark])}

    def release_corridors(self) -> None:
        """The web has drawn every way the corridors were held for (`settle_the_web`): the reservation ends with it."""
        self.corridors, self._cbins = [], {}

    def release_seats(self) -> None:
        """The copse has planted the seats (`stage_windbreak`): they stand as its clumps now, and the reservation ends."""
        self.seats, self._sbins = [], {}

    def release_seats_along(self, pts: Sequence[Sequence[float]], width: float) -> list[tuple[float, float]]:
        """Give up every seat a way along `pts`, `width` wide, comes within the lane buffer of (the connector's last resort,
        `track.connector_through`); returns them."""
        gap = width / 2.0 + self.lane_buffer
        gone = [(sx, sy) for sx, sy in self.seats if any(seg_dist(sx, sy, (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) < gap for a, b in zip(pts, pts[1:], strict=False))]
        if gone:
            keep = [p for p in self.seats if p not in set(gone)]
            self.seats, self._sbins = [], {}
            self.reserve_seats(keep, self.clump, self.lane_buffer)
        return gone

    def box_covers(self, x0: float, y0: float, x1: float, y1: float, seat_pad: float) -> bool:
        """Would a box (x0, y0, x1, y1) - a title's pocket - cover a reservation: a wood seat within `seat_pad` of it (the
        copse refuses a clump inside the pocket grown by its radius), or a corridor's line through it?"""
        if any(x0 - seat_pad < sx < x1 + seat_pad and y0 - seat_pad < sy < y1 + seat_pad for sx, sy in self._seats_near(x0 - seat_pad, y0 - seat_pad, x1 + seat_pad, y1 + seat_pad)):
            return True
        box = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        return any(poly_seg_gap(box, a, b) < half for a, b, half, _o in self._corridors_near(x0, y0, x1, y1))

    def seat_walls(self, sides: int = 12, reach: float | None = None) -> list[list[tuple[float, float]]]:
        """Each seat's lane keep-out as a polygon, circumscribing a circle of `reach` (the copse's lane buffer by default) -
        the walls a router threads a way between, so the run it finds is one the seats admit."""
        r = self.lane_buffer if reach is None else reach
        return [
            [(sx + r * math.cos(2 * math.pi * k / sides) / math.cos(math.pi / sides), sy + r * math.sin(2 * math.pi * k / sides) / math.cos(math.pi / sides)) for k in range(sides)]
            for sx, sy in self.seats
        ]
