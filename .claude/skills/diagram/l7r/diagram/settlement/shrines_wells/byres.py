"""The draft-animal byre (ox / water-buffalo shed) standing among the homesteads.

Split from settlement/shrines_wells.py by feature 116 - see settlement/shrines_wells/CLAUDE.md for the index.
"""

import math
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from .._geom import (
    Pt,
    edge_dist,
    point_in_poly,
)
from .._geom.water_index import crosses_a_stream
from .._knobs import knob_rng

if TYPE_CHECKING:
    from ..core import Settlement


_BORROW_REACH = 120.0  # a neighbor this close can walk over and borrow the team (see draft_byres)

# HOW MANY HOUSEHOLDS KEEP A BEAST, on the two household forms (269 B16, research/homesteads/460): "from the early
# eighteenth century only about half the farm households of Bizen kept an ox or a horse at all - the same share as in
# Mimasaka - and fewer as time went on". A degree along a continuum, so a band rolled per settlement: its top is the
# half the record reads, its bottom the "fewer" after it (how many fewer no page gives - 0.35 is calibrated liberty).
# The commons form keeps the caller's `fraction`: a shared shed serves several households, so its count is not this.
BYRE_KEEPER_SHARE = (0.35, 0.50)
HOUSEHOLD_FORMS = ("courtyard", "yard_shed")
# THE OUTER STABLE'S SEAT (269 B16): "the outer stable standing on its own" (kotobank-umaya) - no page gives how far
# from the house, so one ken off the wall, and a second ken out when that is taken, is a GUESS; it keeps the shed
# distinct from the inner stable's arm, which stands a 3 ft drip line off the same wall.
YARD_SHED_GAP_FT = (6.0, 12.0)

# HOW FAR A COURTYARD-FORM BYRE MAY STAND FROM THE HOUSE IT BELONGS TO. In that form the shed is the
# homestead's own stable wing, not common property, so it gets its owner's yard and no more: the
# spiral is allowed 18 px past the first seat that clears the wall, where the shared form gets 70.
# Exported because `byres_stand_in_their_declared_form` measures the same span - the placer and its
# check read ONE source, which is the standing rule here.
COURTYARD_REACH = 18.0


def courtyard_annex_span(hw: float, hh: float, bh: float) -> float:
    """The farthest a courtyard-form byre's CENTER may stand from its owner farmhouse's center.

    `max(hw, hh) / 2` is the house's own half-extent on its longest side (the spiral is circular, so
    it must clear the worst case), `bh * 0.55` steps just past the byre's own half-depth, and
    `COURTYARD_REACH` is the search budget past that. A byre farther out than this is not an annex of
    anybody's homestead, whatever the manifest declares."""
    return max(hw, hh) / 2 + bh * 0.55 + COURTYARD_REACH


def byre_keeper_share(seed: int) -> float:
    """The share of households that keep a beast on a household form, rolled once per settlement within
    `BYRE_KEEPER_SHARE` - one roll read by the seat's lots (feature 287, homes H06) and by `draft_byres`."""
    lo, hi = BYRE_KEEPER_SHARE
    return round(lo + knob_rng(seed, "byre_share").random() * (hi - lo), 3)


def household_byre_form(s: Any) -> tuple[str | None, float]:
    """`(form, keeper share)` for a seating that lays each keeper's byre in its bundle (feature 287, homes H06): the
    settlement's `byre_form` where it is a household form on a nucleated seating, else `(None, 0.0)` - the shared shed
    on the commons (`detached_commons`) is no household's part and keeps its own pass."""
    if not getattr(s, "_nucleated", False):
        return None, 0.0
    form = s.resolve("byre_form")
    return (form, byre_keeper_share(s.seed)) if form in HOUSEHOLD_FORMS else (None, 0.0)


#: The byre's footprint in feet (a stall for one or two beasts and their fodder, ~15 sq m): the glyph's own size.
BYRE_FT = (16.12, 10.92)

#: THE SHARED SHED'S COUNT AND SPACING (`detached_commons`, a labeled GUESS): about one shed to four or five households,
#: sheds at least 60 px apart - the figures `stage_appurtenances` has always asked `draft_byres` for.
COMMONS_BYRE_FRACTION = 0.22
COMMONS_BYRE_GAP = 60.0
#: How far the seat band is widened, round by round, when its core holds no free pocket (homes H06).
_POCKET_WIDENING = (0.8, 1.0, 1.5, 2.0)


def commons_byre_target(households: int, fraction: float = COMMONS_BYRE_FRACTION) -> int:
    """How many shared sheds a settlement of `households` asks for: one at least (`draft_byres`'s own count)."""
    return max(1, round(households * fraction))


def byre_part(hw: float, hh: float, bw: float, bh: float, garden_side: str, form: str, gap: float) -> tuple[float, float, float, float, float]:
    """A household's byre as a PART of its homestead bundle (feature 287, homes H06): `(dx, dy, w, h, turn)` - its
    center off the house's center and its footprint, both in the house's unturned frame, and the turn the stall is drawn
    at relative to the house. On the flank AWAY from the garden (the garden takes its side of the house first): the
    inner stable's arm (`courtyard`) abuts that wall a 3 ft drip line off, reaching toward the court as
    `_courtyard_byre_seat` sets it; the outer stable (`yard_shed`) stands a ken (`YARD_SHED_GAP_FT[0]`, `gap`) off it. Its
    long side runs along the wall either way, so its footprint is `bh` across the frame and `bw` along it."""
    sx = -1.0 if garden_side in ("E", "SE") else 1.0
    if form == "courtyard":
        return sx * (hw / 2.0 + bh / 2.0 + 3.0), max(0.0, hh / 2.0 - bw / 2.0), bh, bw, (90.0 if sx < 0 else -90.0)
    return sx * (hw / 2.0 + gap + bh / 2.0), 0.0, bh, bw, 90.0


#: How far a shared shed's pocket keeps off the access tree's strips beyond their half-width, in feet: half a bundle pitch
#: (`BUNDLE_PITCH`, 100 ft) - every household's corridor comes to the exit strip, so the ground either side of it is
#: its approach, not a shed's (feature 287 M8). A map drawing convention.
POCKET_TREE_CLEAR_FT = 50.0


class DraftByresMixin:
    def reserve_commons_byres(self: Settlement, seat: Mapping[str, Any], households: int) -> list[Pt]:  # type: ignore[misc]
        """THE SHARED SHEDS' POCKETS, reserved in the seat band BEFORE any house (feature 287, homes H06): on a settlement
        whose byre form is `detached_commons`, `commons_byre_target` pockets of a shed's ground (its box plus 3 px round)
        are laid in the band the houses will fill, so the houses pack round them and `draft_byres` draws each shed where
        its pocket stands - the count asked is the count drawn, never a spiral that finds the courtyards full. Spread as
        the drawing spread them (farthest from the pockets already laid), first nearest the band's middle; offered over
        the band's core first, then the band widened round by round (`_POCKET_WIDENING`). Records `_byre_pockets` and
        returns them; fewer than asked only where the band has no free ground, which the caller refuses."""
        bw, bh = round(self.px(BYRE_FT[0]), 1), round(self.px(BYRE_FT[1]), 1)
        target = commons_byre_target(households)
        cx, cy = float(seat["cx"]), float(seat["cy"])
        ax, ay = seat["along"]
        ox, oy = seat["out"]
        lat, dep = float(seat["lat"]), float(seat["dep"])
        pockets: list[Pt] = []
        for widen in _POCKET_WIDENING:
            nu, nv = max(1, int(lat * widen / bw)), max(1, int(2.0 * dep * widen / bh))
            cands = [
                (cx + ax * lat * widen * (i / nu - 0.5) + ox * dep * widen * (2.0 * j / nv - 1.0), cy + ay * lat * widen * (i / nu - 0.5) + oy * dep * widen * (2.0 * j / nv - 1.0))
                for i in range(nu + 1)
                for j in range(nv + 1)
            ]
            cands = [q for q in cands if self._commons_pocket_clear(q[0], q[1], bw, bh, pockets)]
            while cands and len(pockets) < target:
                q = (
                    min(cands, key=lambda c: (math.hypot(c[0] - cx, c[1] - cy), c))
                    if not pockets
                    else max(cands, key=lambda c: (min(math.hypot(c[0] - p[0], c[1] - p[1]) for p in pockets), -c[0], -c[1]))
                )
                pockets.append(q)
                self.placed.append((q[0], q[1], bw + 6.0, bh + 6.0))
                cands = [c for c in cands if self._commons_pocket_clear(c[0], c[1], bw, bh, pockets)]
            if len(pockets) >= target:
                break
        self._byre_pockets = pockets
        return pockets

    def _commons_pocket_clear(self: Settlement, x: float, y: float, bw: float, bh: float, pockets: list[Pt]) -> bool:  # type: ignore[misc]
        """May a shared shed's pocket stand at (x, y)? The fit test at its box plus 3 px round, off the paddy by a stall's
        depth, and `COMMONS_BYRE_GAP` from every pocket laid."""
        if any(math.hypot(x - p[0], y - p[1]) <= COMMONS_BYRE_GAP for p in pockets):
            return False
        if any(point_in_poly(x, y, ff) or edge_dist(x, y, ff) < bh for ff in self.field_polys):
            return False
        # ...nor on or beside the exit strip or the field's corridor the seating reserved first (feature 287 M8: the registry
        # refuses a shed on an access corridor, and the web draws its way along one). Held off them by half a bundle pitch
        # besides: every household's corridor comes to the strip, and a shed standing against it walls that side of it off -
        # the toy hamlet's one pocket, laid beside the strip's root, left no house on its far side a way in
        tree = getattr(self, "_access", None)
        clear = self.px(POCKET_TREE_CLEAR_FT)
        if tree is not None and tree.covers_box((x, y, bw + 6 + 2 * clear, bh + 6 + 2 * clear)):
            return False
        # ...and the registry of what stands admits the shed as `draft_byres` will record it (feature 287, water W53)
        return bool(self._fits(x, y, bw + 6, bh + 6)) and self.admits("byres", {"x": round(x, 1), "y": round(y, 1), "w": bw, "h": bh, "rot": 0})

    def _courtyard_byre_seat(self: Settlement, h: Mapping[str, Any], bw: float, bh: float) -> tuple[float, float, float, float, float] | None:  # type: ignore[misc]
        """A courtyard-form byre's seat: the magariya's short arm, ABUTTING a free side wall of its owner.

        WHY THIS EXISTS AT ALL - all four settlement-reviews, 2026-08-18, same day the knob shipped.
        The first cut of the courtyard form changed the FORM in the manifest and left the PLACEMENT
        IDIOM alone: it ran the shared shed's first-fit spiral with a shorter leash. Measured, that
        put Sawada's three byres 8.9 / 8.9 / 23.0 ft off their owners' BACK corners at `rot: 0`
        against houses raked -0.1 to -3.6 deg, on the opposite side of the house from that
        household's work yard - and the 23.0 ft one is indistinguishable from Kashikawa's detached
        22.7 ft and Inashiro's 22.8 ft. The two forms' distance ranges OVERLAPPED. That is a degree,
        not a form, and constitution Principle XII says liberty covers a degree while a knob must be
        a form; the knob was buying nothing it was added to buy. It also under-seated badly, because
        a first-fit spiral in a yard the appurtenances already fill mostly finds nothing: over 24
        cohort seeds the courtyard form seated 8 of 16 asked byres against detached's 18 of 18, and
        on Mizuguchi it seated NONE, silently deleting three byres from a shipped map.
        (`byres_meet_their_target` now catches that class.)

        THE SHEET ALREADY HAD THE RIGHT VOCABULARY and the byre was not using it. The attached kura
        (`houses.house`, `_farm_shed_rect`) is drawn INSIDE the house's own transform group, shares
        its rake exactly, abuts its wall, and records an `of` back-reference. Both named precedents
        want that: the Nambu magariya's *umaya* is one L-shaped structure joined to the dwelling
        through the doma, and the sanheyuan's *xiangfang* are connected ranges bounding the court.
        So the arm is seated in the owner's LOCAL frame, on a side wall, rotated with the house, and
        offset along that wall toward the yard so house-plus-arm make the L that frames the working
        court. Side walls because the kura takes the back wall on a nucleated cluster and the yard
        and garden take the sunny front.

        Returns `(x, y, rot, aabb_w, aabb_h)` or None if neither wall is free - the caller then falls
        back to the shared form's spiral rather than dropping the byre, because a byre in the wrong
        place still beats a hamlet that plows without one."""
        hw, hh, rot = float(h["w"]), float(h["h"]), float(h.get("rot", 0.0) or 0.0)
        th = math.radians(rot)
        # WHICH WAY THE HOMESTEAD FACES, derived rather than assumed: the sign of the local-y offset
        # to this house's own work yard. Deriving it from the yard means the arm keeps framing the
        # court when a later change moves the yard, which pinning a compass side would not.
        _yards = self.M.get("threshing_yards") or []
        sy = 1.0
        if _yards:
            yx, yy = min(((float(y["x"]), float(y["y"])) for y in _yards), key=lambda p: math.hypot(p[0] - h["x"], p[1] - h["y"]))
            sy = 1.0 if (-(yx - h["x"]) * math.sin(th) + (yy - h["y"]) * math.cos(th)) >= 0 else -1.0
        for lyc in (sy * max(0.0, hh / 2.0 - bw / 2.0), 0.0):  # reach toward the court first, then sit centered on the wall
            for sx in (-1.0, 1.0):
                # ABUTTING, NOT OVERLAPPING - a 3 ft drip line rather than the kura's shared wall.
                # The first cut overlapped by 1.5 px to read as literally joined, the way the kura
                # is drawn inside the house's own transform, and that cost `no_structure_overlaps`
                # exactly one failing pair per byre. The kura gets away with it because it is drawn
                # as part of the house rather than as a structure in its own right; a byre is a
                # first-class overlap struct and has to keep its own footprint. At 1 ft/px a 3 ft
                # gap is 3 px - the two roofs still read as one L-shaped building, and the gap is
                # the eaves drip between them, which is what the space between a magariya's arms
                # actually is.
                lx = sx * (hw / 2.0 + bh / 2.0 + 3.0)
                cx = h["x"] + lx * math.cos(th) - lyc * math.sin(th)
                cy = h["y"] + lx * math.sin(th) + lyc * math.cos(th)
                brot = rot + (90.0 if sx < 0 else -90.0)  # long axis along the wall; the stall mouth opens OUTWARD, away from the house
                _c, _s = abs(math.cos(math.radians(brot))), abs(math.sin(math.radians(brot)))
                aw, ah = bw * _c + bh * _s, bw * _s + bh * _c
                if self._byre_clear_of_all_but(cx, cy, aw, ah, h):
                    return cx, cy, brot, aw, ah
        return None

    def _yard_shed_seat(self: Settlement, h: Mapping[str, Any], bw: float, bh: float) -> tuple[float, float, float, float, float] | None:  # type: ignore[misc]
        """The OUTER stable's seat (269 B16): a shed standing on its own in its owner's homestead, a ken off the back
        wall or a flank (a second ken out when those are taken), raked with the house - its long side along the wall it
        faces. Which wall is tried first turns with the homestead's own hash, so the sheds of one hamlet do not all
        stand at the same bearing. Returns `(x, y, rot, aabb_w, aabb_h)` or None."""
        hw, hh, rot = float(h["w"]), float(h["h"]), float(h.get("rot", 0.0) or 0.0)
        hx, hy = float(h["x"]), float(h["y"])
        th = math.radians(rot)
        seats: list[tuple[float, float, float]] = []  # (lx, ly, turn) in the house frame
        for gap in (self.px(g) for g in YARD_SHED_GAP_FT):
            seats += [(fx * hw, -(hh / 2 + gap + bh / 2), 0.0) for fx in (0.0, -0.3, 0.3)]
            seats += [(sx * (hw / 2 + gap + bh / 2), fy * hh, 90.0) for fy in (0.0, -0.25) for sx in (-1.0, 1.0)]
        k = int(self._hjit(hx, hy, 131.0) * 5) % 5  # the first ring's five seats, turned
        seats = seats[k:5] + seats[:k] + seats[5:]
        for lx, ly, turn in seats:
            cx, cy = hx + lx * math.cos(th) - ly * math.sin(th), hy + lx * math.sin(th) + ly * math.cos(th)
            brot = rot + turn
            _c, _s = abs(math.cos(math.radians(brot))), abs(math.sin(math.radians(brot)))
            aw, ah = bw * _c + bh * _s, bw * _s + bh * _c
            if self._byre_clear_of_all_but(cx, cy, aw, ah, h):
                return cx, cy, brot, aw, ah
        return None

    def _byre_clear_of_all_but(self: Settlement, cx: float, cy: float, aw: float, ah: float, h: Mapping[str, Any]) -> bool:  # type: ignore[misc]
        """Collision test for an ATTACHED annex: clear of everything placed EXCEPT its own farmhouse.

        `_fits` cannot answer this - it inflates the box and tests it against every placed footprint
        including the owner, so an abutting seat is refused by construction, which is precisely why
        the first cut had to stand the byre off in the open.

        THE OWNER IS A BUNDLE, NOT A POINT, and getting that wrong is why the first version of this
        method never returned a seat. `_garden_fits` exempts the owner by matching `px == hx and
        py == hy`, so I mirrored it - but the garden runs DURING `farmsteads()`, when the house is
        its own entry in `placed`, while byres run after, when `placed` holds one merged HOMESTEAD
        BUNDLE per farm (house + yard + garden, e.g. 100 x 52 px centered off the house). Measured:
        zero entries at the house center, and the owner's own bundle refusing every wall seat. So
        the owner is identified by CONTAINMENT - the placed rect the house center falls inside - and
        the arm is allowed inside that bundle, which is what being an annex means.

        Inside the bundle it must still keep off the things it shares the yard with, so the
        appurtenance records are tested individually: its own house is exempt (the arm joins that
        wall), everything else is not. Those tests are AABB rather than the center-distance circles
        `_garden_fits` uses, because a circle round a 100 x 52 bundle reserves ground the bundle does
        not occupy, and this engine's standing rule is that gap verdicts read footprints."""
        hx, hy = float(h["x"]), float(h["y"])
        if self._in_blocked(cx, cy) or self._near_corridor(cx, cy):
            return False
        # ON ITS HOUSE'S BANK (feature 287, homes H01): a household's beast is stabled on the bank its house stands on -
        # the one same-bank predicate the homestead's parts and the fixtures read
        if crosses_a_stream((hx, hy), (cx, cy), self.M.get("streams", [])):
            return False
        r = math.hypot(aw, ah) / 2
        for poly in self.field_polys:  # a byre stands on dry ground, off the paddies
            if point_in_poly(cx, cy, poly) or edge_dist(cx, cy, poly) < r:
                return False
        # ASKED OF THE INDEX (269 B16, dev/performance.md "Three more shapes"): the placed footprints near this seat come
        # from `_fits`'s own reach grid, which boxes each by its half-diagonal plus 4 - a superset of every box that can
        # meet this one within the 2 px below, so the verdict is the scan's. The owner's bundle is found the same way.
        for px, py, pw, ph, *_ in self._reach_index(self.placed, "placed_reach").near(cx, cy, math.hypot(aw, ah) / 2 + 2):
            if abs(hx - px) <= pw / 2 + 0.5 and abs(hy - py) <= ph / 2 + 0.5:
                continue  # the owner's own homestead bundle - the arm belongs INSIDE it
            if abs(cx - px) < (aw + pw) / 2 + 2 and abs(cy - py) < (ah + ph) / 2 + 2:
                return False
        for _key in ("houses", "threshing_yards", "gardens", "farm_sheds", "byres", "farm_fixtures"):
            for _o in self.M.get(_key) or []:
                if _key == "houses" and abs(float(_o["x"]) - hx) < 0.05 and abs(float(_o["y"]) - hy) < 0.05:
                    continue  # its OWN wall: the arm joins the house, it does not clear it
                if abs(cx - float(_o["x"])) < (aw + float(_o["w"])) / 2 + 2 and abs(cy - float(_o["y"])) < (ah + float(_o["h"])) / 2 + 2:
                    return False
        # ...AND NO ROOF UNDER A YARD PERSIMMON'S CROWN (feature 287, homes H32: the fixtures are drawn before the annexes now)
        return not any(abs(cx - float(p["x"])) < aw / 2 + float(p["r"]) + 1 and abs(cy - float(p["y"])) < ah / 2 + float(p["r"]) + 1 for p in self.M.get("persimmons") or [])

    def _draw_byre(self: Settlement, cx: float, cy: float, w: float, h: float, rot: float = 0) -> None:  # type: ignore[misc]
        """A small OPEN-FRONTED draft-animal shed (ox / water-buffalo byre): a plank-and-thatch roof with a
        dark stall mouth along the front, distinct from the solid gray kura storehouse and from a dwelling."""
        g = [f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.1f})">']
        g.append(f'<rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="1.6" fill="#B0905E" stroke="#59431F" stroke-width="1.1"/>')  # thatch/plank roof
        # THE STALL MOUTH IS SHADE, NOT A BOARD (settlement-review x2, 2026-08-18 round 2). At
        # `#33291C` this bay was the darkest fill of its size anywhere on a hamlet sheet and filled
        # ~30% of a 16 x 11 ft glyph, so at fit zoom a byre read as an oversized notice board - and
        # there are several byres to one board, so the board's caption disambiguates the board while
        # nothing disambiguates a byre. Lifted to a mid-tone shade and given two POSTS, which is what
        # actually distinguishes an open-fronted shed from a plank: the eye reads a roof carried on
        # supports rather than a solid dark rectangle, and the byre stops outranking the farmhouses
        # it belongs to.
        g.append(f'<rect x="{-w / 2 + 2:.1f}" y="{h * 0.02:.1f}" width="{w - 4:.1f}" height="{h * 0.4:.1f}" rx="1" fill="#4E4030"/>')  # the shaded open stall mouth
        for _pf in (0.30, 0.70):  # the two posts carrying the open front
            _pxq = -w / 2 + 2 + (w - 4) * _pf
            g.append(f'<line x1="{_pxq:.1f}" y1="{h * 0.02:.1f}" x2="{_pxq:.1f}" y2="{h * 0.42:.1f}" stroke="#8A7350" stroke-width="0.9"/>')
        g.append(f'<line x1="{-w / 2 + 2:.1f}" y1="{-h * 0.08:.1f}" x2="{w / 2 - 2:.1f}" y2="{-h * 0.08:.1f}" stroke="#59431F" stroke-width="0.8" opacity="0.6"/>')  # roof ridge
        g.append('</g>')
        self.add(''.join(g), cls="byre")

    def draft_byres(self: Settlement, fraction: float = 0.2, gap: float = 64) -> list[Pt]:  # type: ignore[misc]
        """DRAFT-ANIMAL BYRES (ox / water-buffalo sheds) among the homesteads, in the form the `byre_form` knob rolled.

        The two household forms (269 B16, research/homesteads/460): the beast lived with the household that owned it
        or had it on loan, and about half the households kept one (`BYRE_KEEPER_SHARE`, rolled per settlement; `fraction`
        is then unused) - the INNER stable drawn as the arm against the farmhouse (`courtyard`), or the OUTER stable,
        a shed of its own in the yard (`yard_shed`). The rare `detached_commons` form is the older reading, a labeled
        GUESS: a minority of shared sheds (`fraction` of the households) spread among the homesteads, each spiralled out
        from its owner's house to the nearest clear gap past its reserved footprint (via `_fits`), `gap` px apart.
        HOUSE-DRIVEN on every form: the wealthier homesteads in turn; a homestead boxed in on all sides is skipped
        and the next one asked. Call AFTER farmsteads() (homesteads fixed) and BEFORE the grove (which then skips the
        byres). Records M['byres']."""
        bs = self.bscale
        # SIZE: a shared byre houses ~1-2 draft animals (an ox / water-buffalo stall is ~2x3 m) plus fodder ->
        # ~16 x 11 ft ~ 15 m2, well under the ~120 m2 farmhouse. To-scale tiers carry it in FEET (drawn at ftpx);
        # legacy tiers scale it with the urban glyph grain (bscale).
        if self._toscale():
            bw, bh = round(self.px(16.12), 1), round(self.px(10.92), 1)
        else:
            bw, bh = round(15.5 * bs, 1), round(10.5 * bs, 1)
        # WHICH OF THE TWO ATTESTED FORMS THIS SETTLEMENT USES (knob `byre_form`, 2026-08-18).
        # `courtyard` = the stable wing of its owner's own homestead (magariya / sanheyuan); the shed
        # follows the WEALTH, so the owners are taken straight down the wealth ranking with no spread
        # objective, the search is held to the owner's own yard, and two byres may stand near each
        # other because their houses do. `detached_commons` = the shared shed on the ground between
        # homesteads, unchanged and still the default: spread by minimax, separated by `gap`, allowed
        # 70 px of spiral. The reasoning for having a knob at all is at the registration in
        # `_knobs.py`; the DECLARATION is written to meta so the gate can hold the drawing to it,
        # because a form nobody records is a form nothing can check.
        form = self.resolve("byre_form")
        self.M["meta"]["byre_form"] = form
        # THE BEAST LIVES WITH ITS HOUSEHOLD (269 B16, research/homesteads/460): on both household forms the byre is its
        # owner's, taken down the wealth ranking and seated in the owner's own homestead, and it records its owner (`of`).
        # `detached_commons` - the shared shed below - is the rare labeled GUESS the record has not found.
        _courtyard = form in HOUSEHOLD_FORMS
        _reach = COURTYARD_REACH if _courtyard else 70.0
        _sep = 0.0 if _courtyard else gap
        houses = [h for h in self.M.get("houses", []) if h.get("kind") == "plain"]
        # THE WEALTH KEY WAS A NO-OP, AND THE REAL SORT WAS LONGITUDE (settlement-review x2, Kashikawa
        # and Sawada, 2026-08-18 round 2 - found independently on two maps). This read
        # `key=(-wealth, x, y)` and called it "buffalo owners = the wealthier", but EVERY plain house
        # in a scripted hamlet records `wealth: 1.0`, so the first term is constant and the ranking
        # collapses to smallest x - the cluster's WEST EDGE. Measured: Sawada's four oxen went to the
        # four westernmost houses, 230 ft of an 810 ft cluster with the whole SE lobe oxless, and by
        # the only wealth signal a reader can actually see - footprint - those owners rank 4th, 6th,
        # 17th and 18th of 19, with the three largest houses on the map owning no ox. Kashikawa's
        # first byre went to a west-edge outlier with ZERO households inside borrowing distance, and
        # the borrower floor added earlier that day could not reach it because the first byre never
        # enters the branch the floor lives in.
        #
        # FOOTPRINT IS THE WEALTH SIGNAL THE SHEET ACTUALLY CARRIES. `wealth` and house size were
        # decoupled at some point - the sizes here vary 1,040-1,688 sq ft while `wealth` stays 1.0 -
        # so the ranking was reading the dead one. Area is what a reader judges wealth by, and it is
        # what `farmhouse_sizes_vary` already makes meaningful. `wealth` stays first so a tier that
        # DOES set it still wins; area breaks the tie it leaves behind; position only breaks an exact
        # tie between two identical houses.
        # THE STALLS THE SEATING RESERVED (feature 287, homes H06): where the households were seated with their lots, each
        # keeper's byre is a part of its homestead, laid inside the envelope that admitted it - so every one is drawn,
        # where it was reserved, and the count is the lots' quota (round(n x the keeper share)) by construction. Nothing is
        # sought here, so no full courtyard can lose a beast.
        if _courtyard and getattr(self, "_byre_form", None) == form:
            fraction = byre_keeper_share(self.seed)
            self.M["meta"]["byre_share"] = fraction
            seated: list[Pt] = []
            for h in houses:
                b = h.get("byre")
                if not b:
                    continue
                self._draw_byre(float(b["x"]), float(b["y"]), bw, bh, float(b["rot"]))
                self.placed.append(tuple(b["box"]))
                self.M["byres"].append({"x": round(b["x"], 1), "y": round(b["y"], 1), "w": bw, "h": bh, "rot": round(b["rot"], 1), "of": [round(h["x"], 1), round(h["y"], 1)]})
                seated.append((float(b["x"]), float(b["y"])))
            self.M["meta"]["byre_target"] = len(seated)
            return seated
        # THE SHARED SHEDS' POCKETS THE SEATING RESERVED (feature 287, homes H06): each shed drawn in its pocket, which the
        # houses packed round, so the count asked is the count drawn
        pockets = getattr(self, "_byre_pockets", None)
        if not _courtyard and pockets:
            for x, y in pockets:
                self._draw_byre(x, y, bw, bh)
                self.M["byres"].append({"x": round(x, 1), "y": round(y, 1), "w": bw, "h": bh, "rot": 0})
            self.M["meta"]["byre_target"] = len(pockets)
            return list(pockets)
        ranked = sorted(houses, key=lambda h: (-h.get("wealth", 1.0), -(float(h["w"]) * float(h["h"])), h["x"], h["y"]))
        if _courtyard:  # about half the households kept a beast, and fewer later (BYRE_KEEPER_SHARE)
            fraction = byre_keeper_share(self.seed)  # the one roll the seating's lots read too (feature 287)
            self.M["meta"]["byre_share"] = fraction
        target = max(1, round(len(houses) * fraction))
        self.M["meta"]["byre_target"] = target  # the ASK, recorded so a silent shortfall is visible (byres_meet_their_target)
        out: list[Pt] = []
        # SPREAD THE BYRES ACROSS THE SETTLEMENT, do not drain toward one end (settlement-review on
        # Kashikawa and Sawada, 2026-08-17). Walking the wealth ranking in order and taking the first
        # clear gap sends every byre to whichever flank still has open verge: measured along each
        # cluster's own principal axis, all four byres occupied the SW 143 ft of a 993 ft settlement
        # on Kashikawa (14%), 160 of 810 ft on Sawada (20%), and every map put them in one half.
        # These are SHARED sheds - the whole point is that a household too poor for its own team
        # borrows or hires one (`research/homesteads/`) - so a byre quarter at one end defeats
        # the sharing the feature exists to depict, leaving most households several hundred feet from
        # the nearest.
        #
        # The fix is the MINIMAX idiom the well siting already uses: after the first, take the
        # wealthiest candidate that stands FURTHEST from every byre already placed. Deterministic (no
        # RNG - the key is a distance, then wealth, then position), and it only changes WHICH owners
        # get one, never how many or how the spiral seats them.
        _pool = list(ranked)

        def _borrowers(q: Mapping[str, Any]) -> int:
            """Households close enough to walk over and borrow this homestead's team."""
            return sum(1 for o in houses if o is not q and math.hypot(o["x"] - q["x"], o["y"] - q["y"]) <= _BORROW_REACH)

        while len(out) < target and _pool:
            if not out and not _courtyard:
                # THE FIRST SHARED BYRE NEEDS THE BORROWER FLOOR TOO (settlement-review, Kashikawa
                # 2026-08-18 round 2). The floor below lives inside `if out and ...`, so the FIRST
                # byre took `_pool[0]` unconditionally - and the floor had been written for exactly
                # that byre. Measured on the shipped sheet: Kashikawa's byre 0 stood 53 ft from one
                # farmhouse and 239 ft from the next, ONE household inside 200 ft against the other
                # three sheds' 3, 5 and 5, unmoved by the fix meant to cure it. Same shape on
                # Inashiro (2 within 200 ft) and Akagahara (1). A shared shed nobody can reach is
                # the private-stable read, on a map that declares the shared form.
                h = next((q for q in _pool if _borrowers(q)), _pool[0])
            elif out and not _courtyard:
                # SPREAD, THEN SHARE. Farthest-point alone minimizes the worst walk, which is the
                # right coverage objective - but with every house at wealth 1.0 the tie-break
                # collapses to pure distance, so it picks the most ISOLATED homestead and the shed
                # reads as that household's private one. That is the inverse of the doctrine: a byre
                # is shared precisely so a household owning no team can borrow from a neighbor
                # (research/homesteads/), and the neighbor has to be there to borrow from.
                # So: take the spread score, then among the candidates within a quarter of the best
                # prefer the one with the most households in borrowing distance.
                _best = max(min(math.hypot(q["x"] - bx, q["y"] - by) for bx, by in out) for q in _pool)

                # A BORROWER IS A FLOOR, NOT ONLY A TIE-BREAK (settlement-review, Kashikawa
                # 2026-08-18). Preferring the best-connected owner AMONG the near-best spread was
                # already the fix for "spread alone picks the most isolated homestead" - but it can
                # only choose between the candidates the spread tier offers, and when every one of
                # them is isolated it still seats a shared shed where nobody can share it. Measured:
                # Kashikawa's first byre stands 53 ft from one farmhouse and 239 ft from the next,
                # with ONE household inside 200 ft while the other three sheds serve 3, 5 and 5. On a
                # map that rolled `detached_commons` that byre reads as a private stable, which is
                # the other form - so it also makes the knob illegible.
                #
                # So the spread tier WIDENS until it contains an owner somebody can actually borrow
                # from. Relaxing the tier costs a little coverage spread; seating a communal shed
                # out of everyone's reach costs the feature its whole meaning.
                _near = [q for q in _pool if min(math.hypot(q["x"] - bx, q["y"] - by) for bx, by in out) >= _best * 0.75]
                for _tier in (0.5, 0.25, 0.0):
                    if any(_borrowers(q) for q in _near):
                        break
                    _near = [q for q in _pool if min(math.hypot(q["x"] - bx, q["y"] - by) for bx, by in out) >= _best * _tier]
                h = max(_near, key=lambda q: (sum(1 for o in houses if o is not q and math.hypot(o["x"] - q["x"], o["y"] - q["y"]) <= _BORROW_REACH), q.get("wealth", 1.0), -q["x"], -q["y"]))
            else:
                h = _pool[0]
            _pool.remove(h)
            if _courtyard:  # the inner stable's arm on its owner's wall, else the outer stable's shed in its yard
                _seat = self._courtyard_byre_seat(h, bw, bh) if form == "courtyard" else None
                _seat = _seat or self._yard_shed_seat(h, bw, bh)
                if _seat is not None:
                    _cx, _cy, _brot, _aw, _ah = _seat
                    self._draw_byre(_cx, _cy, bw, bh, _brot)
                    self.placed.append((_cx, _cy, _aw, _ah))
                    self.M["byres"].append({"x": round(_cx, 1), "y": round(_cy, 1), "w": bw, "h": bh, "rot": round(_brot, 1), "of": [round(h["x"], 1), round(h["y"], 1)]})
                    out.append((_cx, _cy))
                    continue
            # The courtyard form starts its spiral at the owner's OWN half-extent (the same span
            # `courtyard_annex_span` states, and the same one the gate measures), the shared form at
            # the house's diagonal - a shed on the commons should clear the homestead entirely.
            rr0 = (courtyard_annex_span(h["w"], h["h"], bh) - COURTYARD_REACH) if _courtyard else (math.hypot(h["w"], h["h"]) / 2 + bh)
            rr = rr0
            done = False
            while rr < rr0 + _reach and not done:
                for a in range(0, 360, 30):
                    cx = h["x"] + rr * math.cos(math.radians(a))
                    cy = h["y"] + rr * math.sin(math.radians(a))
                    if (
                        self._fits(cx, cy, bw + 6, bh + 6)
                        and not any(point_in_poly(cx, cy, ff) or edge_dist(cx, cy, ff) < bh for ff in self.field_polys)
                        and all((bx - cx) ** 2 + (by - cy) ** 2 > _sep * _sep for bx, by in out)
                        and not (_courtyard and crosses_a_stream((float(h["x"]), float(h["y"])), (cx, cy), self.M.get("streams", [])))  # a household's byre on its house's bank (H01)
                    ):
                        self._draw_byre(cx, cy, bw, bh)
                        self.placed.append((cx, cy, bw, bh))
                        _rec: dict[str, Any] = {"x": round(cx, 1), "y": round(cy, 1), "w": bw, "h": bh, "rot": 0}
                        if _courtyard:  # a household's byre names its household, wherever the fallback put it (269 B16)
                            _rec["of"] = [round(h["x"], 1), round(h["y"], 1)]
                        self.M["byres"].append(_rec)
                        out.append((cx, cy))
                        done = True
                        break
                rr += 16
        return out
