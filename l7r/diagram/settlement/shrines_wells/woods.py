"""Woods drawn as STANDS of individual trees - the floor early, the canopy deferred to crop time.

Split from settlement/shrines_wells.py by feature 116 - see settlement/shrines_wells/CLAUDE.md for the index.

Research: plumbing - NONE
"""

import random
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .._geom import (
    Poly,
    edge_dist,
    point_in_poly,
    seg_dist,
)

if TYPE_CHECKING:
    from ..core import Settlement


def trees_off_the_treads(trees: Sequence[tuple[float, float, float, str]], lanes: Sequence[Any]) -> list[tuple[float, float, float, str]]:
    """The trees of a stand whose TRUNK stands on no lane's tread (feature 287, woods W21: `stands.trunk_on_tread`, the one
    predicate of "no tree is planted in a path") - asked only of the lanes whose box comes within a half-width of the
    stand's, so a wood no lane reaches asks nothing.

    Research: no trunk on a lane's tread - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the Tang Code punished whoever planted or tilled a lane, and 0071 keeps groves off the main road
        its figures from 0081 - research/questions/0081-village-lanes.drawing.html: 6 (lane width when a record has no w)
    """
    from ..homestead_parts.stands import trunk_on_tread  # noqa: PLC0415 - kept beside its one use

    if not trees:
        return []
    x0, x1 = min(t[0] for t in trees), max(t[0] for t in trees)
    y0, y1 = min(t[1] for t in trees), max(t[1] for t in trees)
    near = []
    for ln in lanes:
        pts = ln.get("pts") or []
        h = float(ln.get("w", 6)) / 2.0
        if len(pts) >= 2 and min(p[0] for p in pts) - h <= x1 and max(p[0] for p in pts) + h >= x0 and min(p[1] for p in pts) - h <= y1 and max(p[1] for p in pts) + h >= y0:
            near.append(ln)
    return [t for t in trees if not near or not trunk_on_tread(t[0], t[1], near)]


class TreeStandsMixin:
    def flush_tree_stands(self: Settlement) -> None:  # type: ignore[misc]
        """Draw the canopy of every queued tree stand (see _tree_stand). Runs at CROP time, so each
        crown is tested against the COMPLETE map - every building and wellhead, not just the ones
        that happened to precede the wood - and a crown that would cover one is simply not drawn:
        the stand THINS around the structure instead of retreating from it. Deterministic (each
        stand re-seeds its own RNG, state saved/restored), so deferring ripples nothing. Idempotent;
        unit tests call it directly after forest()/forest_patch()."""
        pending = self._pending_stands
        self._pending_stands: list[tuple[Poly, int, bool, str | None]] = []
        for poly, seed, outliers, cls in pending:
            self._draw_stand(poly, seed, outliers, cls)

    def _draw_stand(self: Settlement, poly: Poly, seed: int, outliers: bool, cls: str | None = None) -> None:  # type: ignore[misc]
        """One queued stand's canopy: the crowns inside `poly` plus (optionally) its fringe outside,
        each filtered so no tree is drawn on a roof or a wellhead.

        Research:
            spacing - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html: CANOPY_SPACING_FT, jittered 42% - 0.42 (position jitter, a share of the step)
            crown size - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html: CANOPY_R_FT, 0.75 to 1.05 of it, emergents 1.05 to 1.4
            emergent share - GUESS: searched, the record silent (feature 417 T36 pass P6, 2026-10-25); 18%
            conifer share - GUESS: searched, the record silent (feature 417 T36 pass P6, 2026-10-25); 34%
            no crown on a roof - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: a clump drawn on a roof hides the building
            no crown on a wellhead - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P6, 2026-10-25)
            no crown on a plot's sun ground - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: _sun_keepouts
            no trunk on a lane - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the Tang Code punished whoever planted or tilled a lane, and 0071 keeps groves off the main road
            fringe crowns drawn outside the stand's outline - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html: a worked wood's shrubs were cut and its edge kept as grass - a fringe of advance growth is drawn outside the stand, a departure the code keeps until feature 417 T34; `_stand_fringe` outliers give the wood a soft edge; the 0080 drawing page is silent on a wood's fringe
            no crown under another's canopy - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html: a crown is never seated under another's canopy
            its unstated figures - GUESS: searched, the record silent (feature 417 T38 pass N8, 2026-10-25) - 0.18 (share of emergent crowns); 0.34 (share of conifers)
        """
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        step = self.px(self.CANOPY_SPACING_FT)
        rad = self.px(self.CANOPY_R_FT)
        st = random.getstate()
        random.seed(seed)
        trees: list[tuple[float, float, float, str]] = []
        yy = min(ys)
        while yy <= max(ys) + step:
            xx = min(xs)
            while xx <= max(xs) + step:
                tx = xx + random.uniform(-step * 0.42, step * 0.42)
                ty = yy + random.uniform(-step * 0.42, step * 0.42)
                big = random.random() < 0.18
                kind = "conifer" if random.random() < 0.34 else "broadleaf"
                if point_in_poly(tx, ty, poly):
                    trees.append((tx, ty, rad * (random.uniform(1.05, 1.4) if big else random.uniform(0.75, 1.05)), kind))
                xx += step
            yy += step
        # no crown is drawn on a roof or a wellhead - and by flush time that means EVERY one of them
        reach = rad * 1.4 + self.CANOPY_PAD  # the largest crown AND the pad `_crown_covers` asks: a box within the pad of a crown was never fetched
        krect, kcirc = self._canopy_keepouts((min(xs) - reach, min(ys) - reach, max(xs) + reach, max(ys) + reach))
        krect += self._sun_keepouts((min(xs) - reach, min(ys) - reach, max(xs) + reach, max(ys) + reach))  # every plot's sun ground (feature 310)
        # ...and no trunk stands on a lane's tread (feature 287, woods W21 - `trunk_on_tread`, the rule's one predicate): the
        # stand is drawn at crop time, after every way, so a lane through the wood is known and the trees keep off it
        trees = trees_off_the_treads(trees, self.M.get("lanes") or [])
        seated = self._crowns_near(
            min(xs) - reach, min(ys) - reach, max(xs) + reach, max(ys) + reach
        )  # no crown's center under another's canopy, this stand's or any earlier one's - see _crown_seat_clear
        self.add(''.join(self._crowns(self._canopy_seats([t for t in trees if not self._crown_covers(t[0], t[1], t[2], krect, kcirc, self.CANOPY_PAD)], seated))), cls=cls)
        if outliers:
            self.add(''.join(self._crowns(self._canopy_seats(self._stand_fringe(poly, step, rad, krect, kcirc), seated))), cls=cls)
        random.setstate(st)

    @staticmethod
    def _crown_seat_clear(x: float, y: float, r: float, crowns: Sequence[tuple[float, float, float]]) -> bool:
        """NO CANOPY TREE STANDS UNDER ANOTHER'S CROWN (GM 2026-08-28, found on the interactive map):
        a crown is refused when its center lies inside an already-seated crown, or an already-seated
        center lies inside it - `d < max(r, r_other)`. Edge overlap (`d` between that and `r + r_other`)
        stays: neighboring canopies do interlace. What this removes is the tree drawn wholly inside
        another's circle - a suppressed understory stem, which the canopy layer this map draws does not
        show. Measured before the rule on Inashiro: 298 of 1,728 crowns entirely inside another
        (17%), 950 with their center more than halfway in; the 13 ft grid's +-42% jitter put two grid
        neighbors 2-3 ft apart and a 6 ft crown vanished under a 12 ft one. research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html; gated by `tree_crowns_not_subsumed`.

        Research: no crown under another's - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html: d >= max(r, r_other)
        """
        return all((x - cx) ** 2 + (y - cy) ** 2 >= max(r, cr) ** 2 for cx, cy, cr in crowns)

    def _crowns_near(self: Settlement, x0: float, y0: float, x1: float, y1: float) -> list[tuple[float, float, float]]:  # type: ignore[misc]
        """Every crown ALREADY RECORDED on the map (M['tree_crowns'], any stand or clump) that reaches into
        the box - the seed for a new stand's seating, so neighboring stands and the belt's overlapping
        clumps see each other's crowns. Checked per stand only, 53 of Inashiro's crowns still sat wholly
        inside a crown of the NEXT clump (measured 2026-08-28).

        Research:
            its figures from 0080 - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html: 1.4 (reach padded by the largest crown)
        """
        tc = self.M.get("tree_crowns") or []
        out: list[tuple[float, float, float]] = []
        pad = 2.0 * self.px(self.CANOPY_R_FT) * 1.4  # the largest crown either side of the box's edge (a 12 ft emergent just outside it was missed at the clump's own 9 px reach: 73 seats, 2026-08-28)
        for i in range(0, len(tc), 3):
            cx, cy, cr = tc[i], tc[i + 1], tc[i + 2]
            if x0 - cr - pad <= cx <= x1 + cr + pad and y0 - cr - pad <= cy <= y1 + cr + pad:
                out.append((cx, cy, cr))
        return out

    def _canopy_seats(self: Settlement, trees: Sequence[tuple[float, float, float, str]], seated: list[tuple[float, float, float]]) -> list[tuple[float, float, float, str]]:  # type: ignore[misc]
        """The trees of `trees` that keep their seat under `_crown_seat_clear`, biggest first (the
        dominants hold the canopy; a smaller crown yields), appended to `seated` as they are kept.

        Research:
            no crown under another - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html
            dominants seat first - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P6, 2026-10-25); biggest crown first, a smaller one yields
        """
        kept: list[tuple[float, float, float, str]] = []
        for t in sorted(trees, key=lambda t: -t[2]):
            if self._crown_seat_clear(t[0], t[1], t[2], seated):
                seated.append((t[0], t[1], t[2]))
                kept.append(t)
        return kept

    def _stand_fringe(self: Settlement, poly: Poly, step: float, rad: float, krect: Any, kcirc: Any) -> list[tuple[float, float, float, str]]:  # type: ignore[misc]
        """The cut-over FRINGE of a wood: scattered advance growth thinning out past the tree line,
        kept off every bit of ground already spoken for. Advance growth comes in THICKETS, not as an
        even sprinkle, so a coarse position-seeded mask (~5 crowns across) decides which stretches of
        the margin have seeded at all and which have been kept clear by grazing and fuel-cutting.
        Each fringe tree becomes a block poly, so a later farmstead cannot land on it.

        Research:
            a fringe of advance growth outside the wood - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html: a worked wood's shrubs were cut and its edge kept as grass - a fringe of advance growth is drawn outside the stand, a departure the code keeps until feature 417 T34
            fringe band and thinning - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P6, 2026-10-25); 2.6 steps deep, thinning with distance
            thickets, not a sprinkle - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P6, 2026-10-25); a mask about five crowns across
            fringe crown size and conifer share - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P6, 2026-10-25); 0.55 to 0.95 of the radius, 30% conifer
            fringe tree spacing - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P6, 2026-10-25); 1.15 x 1.7 steps, jittered 0.55 step
            its unstated figures - GUESS: searched, the record silent (feature 417 T38 pass N8, 2026-10-25) - 0.12 (thicket mask about 5 crowns across: 58% seeded, the rest at 0.12); 0.3 (fringe conifer share); 0.42 (thicket mask about 5 crowns across: 58% seeded, the rest at 0.12); 1.4 (thinning exponent away from the wood's edge); 5 (thicket mask about 5 crowns across: 58% seeded, the rest at 0.12)
            its salts, guards and sentinels - NONE: they decide nothing about the place - 31 (jitter salt (thicket mask))
        """
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        band = step * 2.6
        out: list[tuple[float, float, float, str]] = []
        yy = min(ys) - band
        while yy <= max(ys) + band:
            xx = min(xs) - band
            while xx <= max(xs) + band:
                tx = xx + random.uniform(-step * 0.55, step * 0.55)
                ty = yy + random.uniform(-step * 0.55, step * 0.55)
                keep = random.random()
                kind = "conifer" if random.random() < 0.3 else "broadleaf"
                r = rad * random.uniform(0.55, 0.95)
                xx += step * 1.15
                if point_in_poly(tx, ty, poly):
                    continue
                gap = edge_dist(tx, ty, poly)
                thicket = 1.0 if self._hjit(round(tx / (step * 5)), round(ty / (step * 5)), 31.0) > 0.42 else 0.12
                if gap > band or keep > thicket * (1 - gap / band) ** 1.4:  # thins out with distance from the wood
                    continue
                if self._fringe_blocked(tx, ty, r) or self._crown_covers(tx, ty, r, krect, kcirc, self.CANOPY_PAD):
                    continue
                out.append((tx, ty, r, kind))
            yy += step * 1.7
        return out

    def _crowns(self: Settlement, trees: Sequence[tuple[float, float, float, str]]) -> list[str]:  # type: ignore[misc]
        """SVG for a set of (x, y, r, kind) canopy crowns, drawn back-to-front so the stand layers
        with depth. One circle per tree, a conifer told by its darker fill alone (the inner "apex" disc
        was dropped, GM 2026-09-27: it read as a trunk, which a plan view cannot show) - the same crown
        the grove clumps use, so a wood and a windbreak read as the same kind of thing. Records every
        crown it emits (M['tree_crowns']).

        Research: crown glyph - CONVENTION: one circle, conifer darker
        """
        out: list[str] = []
        self._record_crowns([(t[0], t[1], t[2]) for t in trees])
        for tx, ty, r, kind in sorted(trees, key=lambda t: t[1]):
            col = "#4A6733" if kind == "conifer" else ("#6E8B43" if (int(tx) + int(ty)) % 2 else "#7C9A4E")
            out.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="{r:.1f}" fill="{col}" stroke="#3C5526" stroke-width="0.7"/>')
        return out

    def _fringe_blocked(self: Settlement, tx: float, ty: float, r: float) -> bool:  # type: ignore[misc]
        """Whether a fringe tree at (tx, ty) would land on ground already spoken for - anything
        blocking, a field or dry plot, open water, or a way. The wood's margin grows on waste
        ground, never in the crop or on the road.

        Research: fringe on waste ground only - research/questions/0073-scrub-and-rough-grass-at-the-edges-of-fields-and-channels.html: fields and channels were kept cut, uncut cleared land going to scrub; the masks are ours; off blocks, crops, water and ways
        """
        if any(point_in_poly(tx, ty, b) for b in self.block_polys):
            return True
        if any(point_in_poly(tx, ty, f) or edge_dist(tx, ty, f) < r for f in self.field_polys + self.dry_polys):
            return True
        if self._on_watercourse(tx, ty, pad=r):
            return True
        return any(seg_dist(tx, ty, lp[k], lp[k + 1]) < buf + r for lp, buf in self._corridor_buffers() for k in range(len(lp) - 1))
