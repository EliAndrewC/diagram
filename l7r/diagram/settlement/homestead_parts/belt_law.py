"""The windbreak's law, read and repaired where the belt is planted (feature 287, woods W16, W17, W18, W19; plan D8).

THE ONE PREDICATE of each rule lives here, and both the placer (`village_grove`, through `settle_the_belt`) and the
finished-map tests read it, so the two cannot disagree:

- W16, the belt's DEPTH (`BeltReading.depths`): no judged 40 ft stretch across the wind is shallower than 30 ft along it
  (research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.html: a belt under about 30 ft reads as a row of blobs). The body is the one
  `test_every_pool_belt_keeps_its_depth_across_its_windward_face` measured with (`belt_depths`), lifted unchanged but for
  the run break below.
- W17, the belt's CONTINUITY (`BeltReading.holes`): no opening across the wind wider than `_BELT_GAP_FT` between two
  crowns, since a gap funnels the wind (the agroforestry passage at `_BELT_GAP_FT`). Judged ACROSS THE WIND, the axis the
  depth bins use, because an opening the wind can blow through is an opening in that projection.
- W18, the belt's BEARING and SUBTENSE on the page (`stands.belt_bearing_and_subtense`), trimmed on the crowns the page
  shows.
- W19, the belt's REACH: no crown farther from every farmhouse than the band's own designed far face (`belt_reach`,
  recorded by `belt_polygon`). A stretch of the band no house stands before is not planted, so a cluster in two groups
  gets a belt in two runs, and the stretch between them is a RUN BREAK, not a hole: nothing stands behind it for the
  wind to reach.

A stretch the page's edge cuts, a way crossing the belt face to face, and a tip are not judged - the measure's own
exemptions (the frame, not the planting, is what is thin there; a crossing is a declared opening; a belt tapers).

`settle_the_belt` guarantees all four where the belt is planted (plan D8, "the belt is planted where it can be deep and
whole"): each round it asks the page the belt will be framed to, trims the hook on the crowns that page shows, deepens a
thin stretch and closes a hole with seats the placer's own tests admit - across the band's depth there, and up to
`BELT_PUSH_BACK_FT` beyond its far face (the band pushed back for that column, the ladder's own 60 ft) - and where no
seat is admitted, ENDS the belt there, keeping the longer side. No round leaves a violation standing: the last phase only
removes crowns, so it terminates, and it stops only when every predicate passes.

Research: plumbing - NONE
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Any

from ._helpers import _BELT_GAP_FT

Pt = tuple[float, float]
View = tuple[float, float, float, float]

MIN_BELT_DEPTH_FT = (
    30.0  # research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.html: a belt 'shallower than about 30 ft reads as a row of blobs'
)
"""The least depth of a judged stretch.

Research:
    least belt depth - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html:
        no judged stretch under 30 ft along the wind
"""
DEPTH_BIN_FT = 40.0  # the stretch across the wind a depth is read over - about a crown and a half
BELT_PUSH_BACK_FT = 60.0  # how far past the band's far face a thin column may be planted: `belt_polygon`'s own ladder tops out at 60 ft back
"""Research: repair push-back - UNRESEARCHED: a thin stretch planted up to 60 ft past the band's far face"""
SETTLE_ROUNDS = 12  # rounds that may add seats before the removing phase; each round re-reads the page the belt sets
BELT_DESIGN_DEPTH_FT = 110.0  # the band `belt_polygon` draws, 36..146 ft behind the fringe: a belt standing against the page has a crown this near its edge
"""The depth of the band `belt_polygon` draws.

Research:
    belt band depth - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html:
        110 ft, 36 to 146 ft behind the fringe
"""

#: The compass quarter the wind comes from, as the manifest records it (`meta.windward`), toward that quarter. Normalized
#: in `wind_unit`, the one place a quarter becomes a vector for these predicates, so the placer and a test read one number.
COMPASS = {"N": (0.0, -1.0), "NE": (1.0, -1.0), "E": (1.0, 0.0), "SE": (1.0, 1.0), "S": (0.0, 1.0), "SW": (-1.0, 1.0), "W": (-1.0, 0.0), "NW": (-1.0, -1.0)}


def wind_unit(compass: str) -> Pt:
    """The unit vector toward the quarter `compass` names - where the wind comes from."""
    q = COMPASS[compass]
    n = math.hypot(*q)
    return (q[0] / n, q[1] / n)


def way_samples(ways: Sequence[Sequence[Sequence[float]]]) -> list[Pt]:
    """Points every 10 ft along each polyline in `ways` (the lanes' `pts`, the brook's `poly`) - a way or the water
    through the belt parts it, and that opening is not a thin stretch."""
    out: list[Pt] = []
    for pts in ways:
        for (ax, ay), (bx, by) in zip(pts, pts[1:], strict=False):
            n = max(1, int(math.hypot(bx - ax, by - ay) // 10))
            out += [(ax + (bx - ax) * i / n, ay + (by - ay) * i / n) for i in range(n + 1)]
    return out


def on_page(c: Sequence[float], r: float, view: View) -> bool:
    """Is a crown of radius `r` at `c` on the page `view` (x, y, w, h) - not WHOLLY outside it? The rule
    `Settlement._partition_grove_clumps` splits the record by, so a crown the placer reads as on the page is one the
    record keeps in `clumps`."""
    ox, oy, w, h = view
    return c[0] + r > ox and c[0] - r < ox + w and c[1] + r > oy and c[1] - r < oy + h


class BeltReading:
    """The belt read in wind coordinates - u along the wind (toward where it comes from), v across it - with every
    exemption the measure grants decided once. `on` are the crowns on the page, `off` those off it; `ways` polylines;
    `reach` the band's far-face reach (W19), or None where the map records none."""

    def __init__(
        self,
        on: Sequence[Sequence[float]],
        off: Sequence[Sequence[float]],
        r: float,
        houses: Sequence[Any],
        wind: Pt,
        ways: Sequence[Sequence[Sequence[float]]],
        view: Sequence[float] | None,
        reach: float | None = None,
        band: Sequence[Sequence[float]] = (),
    ) -> None:
        """The exemptions the measure grants, decided once.

        Research:
            page edge not judged - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a
                stretch the page cuts, or within the band's depth of it, is exempt
            tips not judged - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html:
                a belt tapers at its ends
        """
        wx, wy = wind
        px, py = -wy, wx
        self.r, self.reach = r, reach
        self.axes = (wx, wy, px, py)
        self.cx = sum(float(h["x"]) for h in houses) / len(houses)
        self.cy = sum(float(h["y"]) for h in houses) / len(houses)
        self.cl = [self.uv(float(c[0]), float(c[1])) for c in [*on, *off]]
        self.houses = [self.uv(float(h["x"]), float(h["y"])) for h in houses]
        self.band = [self.uv(float(q[0]), float(q[1])) for q in band]  # the band's outline (the record's `poly`), for W19's run break
        self.lo = min(v for _u, v in self.cl)
        self.bins: dict[int, list[float]] = {}
        for u, v in self.cl:
            self.bins.setdefault(self.bin(v), []).append(u)
        # A BIN THE PAGE'S EDGE CUTS IS NOT JUDGED: the frame, not the belt, is what is thin there (Inashiro's belt runs off
        # the top of its view, and the canvas squeezes the part a reader never sees).
        page = {self.bin(v) for _u, v in self.cl[len(on) :]}
        # ...and a bin whose crowns stand within the belt's own designed depth of the page's edge: where the view starts at
        # the canvas's edge there are no crowns off the page to count - the canvas clamps the belt - but the frame takes its
        # depth just the same, which the record accepts (the belt's inner face is kept at the frame, its depth clipped).
        x0, y0, w, h = (float(c) for c in (view or (-1e9, -1e9, 2e9, 2e9)))  # no view recorded: no frame
        self.view = (x0, y0, w, h)
        self.framed = view is not None
        self.on_xy = [(float(c[0]), float(c[1])) for c in on]
        page |= {self.bin(v) for c, (_u, v) in zip(on, self.cl, strict=False) if min(c[0] - x0, c[1] - y0, x0 + w - c[0], y0 + h - c[1]) <= 2 * r}
        page |= {b for b in range(max(self.bins) + 1) if self._band_leaves_the_page(b)}
        self.page = page
        # ...and the TIPS: a bin at the end of a run of crowned bins is where a belt tapers - it is deepest in the middle
        # (research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.html) - and one crown there is the taper, not the one-row arm this measures
        self.tips = {b for b in self.bins if not self.bins.get(b - 1) or not self.bins.get(b + 1)}
        self.ways = [self.uv(x, y) for x, y in way_samples(ways)]
        self.parted = self._parted()

    def uv(self, x: float, y: float) -> Pt:
        wx, wy, px, py = self.axes
        return ((x - self.cx) * wx + (y - self.cy) * wy, (x - self.cx) * px + (y - self.cy) * py)

    def xy(self, u: float, v: float) -> Pt:
        wx, wy, px, py = self.axes
        return (self.cx + wx * u + px * v, self.cy + wy * u + py * v)

    def bin(self, v: float) -> int:
        return int((v - self.lo) // DEPTH_BIN_FT)

    def _near(self, b: int) -> list[float]:
        return [w for k in (b - 1, b, b + 1) for w in self.bins.get(k, [])]

    def _band_leaves_the_page(self, b: int) -> bool:
        """Does the belt's band at bin `b` - across the depth its neighbors' crowns span - run off the view? Then the frame,
        not the planting, decides what is drawn there (Mizuguchi's belt, laid along the canvas's west edge)."""
        us = self._near(b)
        if not us:
            return False
        x0, y0, w, h = self.view
        v = self.lo + (b + 0.5) * DEPTH_BIN_FT
        for u in (min(us), (min(us) + max(us)) / 2, max(us)):
            x, y = self.xy(u, v)
            if not (x0 <= x <= x0 + w and y0 <= y <= y0 + h):
                return True
        return False

    def _parted(self) -> set[int]:
        """The bins a way or the brook CROSSES face to face: its samples inside the belt's band at a bin span at least half
        the band's depth there. A lane running ALONG the belt inside its band parts nothing - exempting it hid the very
        defect this measures (Kashikawa's seed-8 windward arm, one row deep beside its main lane).

        Research:
            lane crossing exempt - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a
                way crossing face to face over half the band's depth
        """
        r = self.r
        inside: dict[int, list[float]] = {}
        for u, v in self.ways:
            b = self.bin(v)
            us = self._near(b)
            if us and min(us) + r < u < max(us) - r:  # inside the belt's thickness there, a crown's radius in from each face
                inside.setdefault(b, []).append(u)
        out = set()
        for b, us_in in inside.items():
            band = self._near(b)
            if max(us_in) - min(us_in) >= 0.5 * (max(band) - min(band) - 2 * r):
                out.add(b)
        return out

    def unreached(self, v: float) -> bool:
        """Is the belt's band at `v` across the wind beyond `reach` of every house (W19) - its near face there (the band's
        most leeward vertex within a bin of `v`), or where no band is recorded, the nearest crowned bins' most leeward crown?
        No crown may stand there (`plant_the_belt` plants within the reach), so a stretch no house stands before is a run
        break, not a hole.

        Research:
            run break - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a stretch no
                house stands before is not planted
        """
        if self.reach is None:
            return False
        near = [u for u, bv in self.band if abs(bv - v) <= DEPTH_BIN_FT]
        if not near:
            b = self.bin(v)
            near = [min(self.bins[k]) for k in (max((k for k in self.bins if k < b), default=None), min((k for k in self.bins if k > b), default=None)) if k is not None]
        u = min(near)
        return all(math.hypot(hu - u, hv - v) > self.reach for hu, hv in self.houses)

    def depths(self) -> list[float | None]:
        """THE ONE PREDICATE of W16: the belt's depth ALONG the wind per `DEPTH_BIN_FT` bin ACROSS it, crown edge to crown
        edge (a belt one row deep reads one crown), or None where the bin is not judged - cut by the page, parted by a way,
        a tip, or an empty stretch between two runs that no house stands before (W19's run break).

        Research:
            belt depth judged - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html:
                crown edge to crown edge per 40 ft bin
            frame-held belt judged whole - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html:
                exemptions void where the belt stands off the page's edge
        """
        # ...and an empty bin inside an opening a way crosses face to face (`_crossed`): a way crossing on the diagonal parts
        # the belt over more than the one bin its samples span half the band's depth in, and the opening it makes is the
        # crossing's, which W17 judges (no more than `_BELT_GAP_FT` either side of the way)
        # ...AND A BELT NO BIN JUDGES IS JUDGED WHOLE WHERE IT STANDS OFF THE PAGE (feature 287, woods W16's frame-held half):
        # the exemptions are honest only where the frame is what cuts the belt, so a belt every bin of which is exempt - a
        # stub of two tips, a run a way parts - while some stretch of it stands farther than `BELT_DESIGN_DEPTH_FT` from
        # the page's edge (`off_the_page`) has every crowned bin judged, and `settle_the_belt` deepens or ends it
        out = self._depths(lenient=True)
        if all(d is None for d in out) and self.off_the_page():
            out = self._depths(lenient=False)
        return out

    def off_the_page(self) -> list[int]:
        """The bins whose crown on the page NEAREST the page's edge stands farther than `BELT_DESIGN_DEPTH_FT` from it - a
        stretch that does not stand against the page, so its exemption is not the frame's (the one predicate of
        `test_every_pool_belt_keeps_its_depth_across_its_windward_face`'s frame-held half). None without a recorded view."""
        if not self.framed:
            return []
        x0, y0, w, h = self.view
        near: dict[int, float] = {}
        for (x, y), (_u, v) in zip(self.on_xy, self.cl, strict=False):
            b = self.bin(v)
            near[b] = min(near.get(b, math.inf), min(x - x0, y - y0, x0 + w - x, y0 + h - y))
        return sorted(b for b, d in near.items() if d > BELT_DESIGN_DEPTH_FT)

    def _depths(self, lenient: bool) -> list[float | None]:
        """`depths` with its exemptions (`lenient`), or with only an empty bin's (the crossing's, the run break's)."""
        vs = sorted(v for _u, v in self.cl)
        crossed = {k for a, b in zip(vs, vs[1:], strict=False) if b - a > _BELT_GAP_FT and self._crossed(a, b) for k in range(self.bin(a) + 1, self.bin(b - 1e-6) + 1)}
        out: list[float | None] = []
        for b in range(max(self.bins) + 1):
            us = sorted(self.bins.get(b, []))
            exempt = b in self.parted or b in self.page
            if (lenient and (exempt or b in self.tips)) or (not us and (exempt or b in crossed or self.unreached(self.lo + (b + 0.5) * DEPTH_BIN_FT))):
                out.append(None)
                continue
            out.append((us[-1] - us[0] + 2 * self.r) if us else 0.0)
        return out

    def thin(self) -> list[int]:
        """The judged bins shallower than `MIN_BELT_DEPTH_FT`."""
        return [b for b, d in enumerate(self.depths()) if d is not None and d < MIN_BELT_DEPTH_FT]

    def holes(self) -> list[tuple[float, float]]:
        """THE ONE PREDICATE of W17: every opening (v1, v2) across the wind wider than `_BELT_GAP_FT` between two crowns
        that is a HOLE - not where a way crosses the belt, not where the page cuts it, not a run break (W19).

        Research:
            continuous planting - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: an
                opening over 30 ft across the wind is a hole
        """
        vs = sorted(v for _u, v in self.cl)
        out: list[tuple[float, float]] = []
        for a, b in zip(vs, vs[1:], strict=False):
            if b - a <= _BELT_GAP_FT:
                continue
            if set(range(self.bin(a + 1e-6), self.bin(b - 1e-6) + 1)) & self.page:
                continue
            if self._crossed(a, b):
                continue
            n = max(1, int((b - a) // 10.0))
            if any(self.unreached(a + (b - a) * k / n) for k in range(1, n)):
                continue
            out.append((a, b))
        return out

    def _crossed(self, a: float, b: float) -> bool:
        """Is the opening (a, b) across the wind a CROSSING - a way or the brook through it face to face (its samples inside
        the band there spanning at least half the band's depth, as `_parted` reads a bin), with no more than `_BELT_GAP_FT`
        of opening either side of it? A crossing is a declared opening; the belt resuming each side of it is what the gap
        fill plants, so an opening wider than the crossing explains is still a hole.

        Research:
            planting resumes beside a lane - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html:
                no more than 30 ft of opening either side of the way
        """
        band = [*self._near(self.bin(a)), *self._near(self.bin(b))]
        lo, hi = min(band) + self.r, max(band) - self.r
        cross = [(u, v) for u, v in self.ways if a < v < b and lo < u < hi]
        if not cross or max(u for u, _v in cross) - min(u for u, _v in cross) < 0.5 * (max(band) - min(band) - 2 * self.r):
            return False
        return min(v for _u, v in cross) - a <= _BELT_GAP_FT and b - max(v for _u, v in cross) <= _BELT_GAP_FT


def reading_of(m: Any) -> BeltReading | None:
    """The finished map's belt, read as the placer read it: the manifest's windbreak crowns on and off the page, its
    houses, its lanes and brook, its recorded view and the band's reach (`meta.belt_reach`, W19). None without a belt."""
    g = next((g for g in m.get("village_groves") or [] if g.get("role") == "windbreak"), None)
    if g is None or not (g.get("clumps") or g.get("clumps_offpage")) or not m.get("houses"):
        return None
    ways = [rec.get("pts") or rec.get("poly") or [] for rec in [*m.get("lanes", []), *m.get("streams", [])]]
    meta = m.get("meta") or {}
    return BeltReading(
        g.get("clumps") or [], g.get("clumps_offpage") or [], float(g.get("r", 14.0)), m["houses"], wind_unit(meta["windward"]), ways, meta.get("view"), meta.get("belt_reach"), g.get("poly") or ()
    )


def belt_depths(m: Any) -> list[float | None]:
    """W16 over a finished manifest (`BeltReading.depths`); [] where the map has no belt."""
    rd = reading_of(m)
    return rd.depths() if rd is not None else []


def belt_holes(m: Any) -> list[tuple[float, float]]:
    """W17 over a finished manifest (`BeltReading.holes`); [] where the map has no belt."""
    rd = reading_of(m)
    return rd.holes() if rd is not None else []


def _offers(rd: BeltReading, v_lo: float, v_hi: float, band_uv: Sequence[Pt], step: float = 8.0) -> list[Pt]:
    """The seats (u, v) offered across the stretch [v_lo, v_hi] across the wind: every `step` along the wind from the band's
    near face to `BELT_PUSH_BACK_FT` past its far face there (the band's vertices within a bin of the stretch), at three
    places across the stretch, the band's middle first and outward."""
    near = [u for u, v in band_uv if v_lo - DEPTH_BIN_FT <= v <= v_hi + DEPTH_BIN_FT]
    if not near:
        near = [u for u, _v in rd.cl]
    u0, u1 = min(near), max(near) + BELT_PUSH_BACK_FT
    us = [u0 + step * k for k in range(int((u1 - u0) // step) + 1)]
    mid = (min(near) + max(near)) / 2.0
    us.sort(key=lambda u: abs(u - mid))
    vs = [v_lo + (v_hi - v_lo) * f for f in (0.5, 0.25, 0.75)]
    return [(u, v) for u in us for v in vs]


def _deepen(rd: BeltReading, b: int, band_uv: Sequence[Pt], seat: Callable[[float, float], Pt | None]) -> list[Pt]:
    """Seats that deepen bin `b` to `MIN_BELT_DEPTH_FT`, each admitted by `seat` (the placer's own tests, which answer the
    point at the record's grain or None)."""
    v_lo = rd.lo + b * DEPTH_BIN_FT
    us = list(rd.bins.get(b, []))
    got: list[Pt] = []
    for u, v in _offers(rd, v_lo + 1.0, v_lo + DEPTH_BIN_FT - 1.0, band_uv):
        if us and max(us) - min(us) + 2 * rd.r >= MIN_BELT_DEPTH_FT:
            break
        if us and min(us) - 1.0 <= u <= max(us) + 1.0:
            continue  # a seat inside the depth already there adds none
        q = seat(*rd.xy(u, v))
        if q is not None:
            got.append(q)
            us.append(rd.uv(*q)[0])
    return got


def _close(rd: BeltReading, a: float, b: float, band_uv: Sequence[Pt], seat: Callable[[float, float], Pt | None]) -> list[Pt]:
    """Seats that close the opening (a, b) across the wind to steps of at most `_BELT_GAP_FT`, the widest part first."""
    vs = [a, b]
    got: list[Pt] = []
    tried: set[tuple[float, float]] = set()
    while True:
        vs.sort()
        gaps = [(y - x, x, y) for x, y in zip(vs, vs[1:], strict=False) if y - x > _BELT_GAP_FT and (x, y) not in tried]
        if not gaps:
            return got
        _w, x, y = max(gaps)
        tried.add((x, y))
        for u, v in _offers(rd, x + 6.0, y - 6.0, band_uv):
            q = seat(*rd.xy(u, v))
            if q is not None:
                got.append(q)
                vs.append(rd.uv(*q)[1])
                break


def _cut(rd: BeltReading, seated: list[Pt], v1: float, v2: float) -> list[Pt]:
    """The belt ENDED at the stretch [v1, v2] across the wind: the crowns in it removed, and the side with fewer crowns
    with them - the belt stands where it can be deep and whole (plan D8), and the longer run is the one kept.

    Research:
        belt ended at a flaw - UNRESEARCHED: the side with more crowns kept
    """
    uv = [rd.uv(*c) for c in seated]
    left = sum(1 for _u, v in uv if v < v1)
    right = sum(1 for _u, v in uv if v > v2)
    keep_left = left >= right
    return [c for c, (_u, v) in zip(seated, uv, strict=True) if (v < v1 if keep_left else v > v2)]


def settle_the_belt(
    seated: list[Pt],
    *,
    r: float,
    houses: Sequence[Any],
    wind: Pt,
    ways: Sequence[Sequence[Sequence[float]]],
    page: Callable[[list[Pt]], View],
    band: Sequence[Pt],
    seat: Callable[[float, float], Pt | None],
    reach: float | None = None,
    trim: Callable[[list[Pt]], list[Pt]] | None = None,
) -> list[Pt]:
    """The belt's crowns `seated` made to keep W16-W19 on the page they set (plan D8): each round asks `page` for the view
    the crop will take with these crowns, lets `trim` shorten the hook on the crowns that view shows (W18), then deepens
    every thin stretch and closes every hole with seats `seat` admits (across the band `band` and up to
    `BELT_PUSH_BACK_FT` past its far face), until a round adds nothing. Then, while any stretch is still thin or open, the
    belt is ENDED there (`_cut`), and re-read - removal only, so it terminates, and it returns only a belt every predicate
    passes (or none at all).

    Research:
        deep and whole belt - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: thin
            stretches deepened, holes closed, else the belt ended
    """
    seated = list(seated)
    for phase in ("repair", "end"):
        for _ in range(SETTLE_ROUNDS if phase == "repair" else len(seated) + 1):
            view = page(seated)
            if trim is not None:
                shown = [c for c in seated if on_page(c, r, view)]
                kept = set(trim(shown))
                if len(kept) != len(shown):
                    seated = [c for c in seated if c in kept or not on_page(c, r, view)]
                    continue  # the trimmed belt sets its own page: read it again
            if not seated:
                return seated
            rd = BeltReading([c for c in seated if on_page(c, r, view)], [c for c in seated if not on_page(c, r, view)], r, houses, wind, ways, view, reach, band)
            thin, holes = rd.thin(), rd.holes()
            if not thin and not holes:
                return seated
            if phase == "repair":
                band_uv = [rd.uv(float(q[0]), float(q[1])) for q in band]
                got = [q for b in thin for q in _deepen(rd, b, band_uv, seat)] + [q for a, b in holes for q in _close(rd, a, b, band_uv, seat)]
                if not got:
                    break
                seated += got
            else:
                v1, v2 = (rd.lo + thin[0] * DEPTH_BIN_FT, rd.lo + (thin[0] + 1) * DEPTH_BIN_FT) if thin else holes[0]
                seated = _cut(rd, seated, v1, v2)
    return seated  # pragma: no cover - the ending phase removes a crown a round, so it returns before its bound
