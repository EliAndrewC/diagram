"""A household's parts are the household's (feature 287, plan M5; homes H17, H45, H06).

ONE LOT PER HOUSEHOLD, KEYED ON SEAT ORDER. The size of a farmhouse and whether it keeps a kura or a beast were each a
positional roll (`_hjit` of the seat), so they aliased along a row: a row of seats at one pitch drew one kura in 12
against the record's three in ten ("the kura roll under-delivers 2.2x", future-work/farming-communities.md). A share
is a COUNT here instead - a quota by ordinal: household `k`, taken in a seed-shuffled order, carries a part exactly when
`floor((j + 1) * p + 0.5) > floor(j * p + 0.5)` for its place `j` in that order, so `n` seated households carry exactly
`round(n * p)` whatever `n` is. The size is a stratified ladder over the researched factor range, rung `k` to household
`k`, so the footprints spread by construction (H17).

The lot is the household's before its seat is sought, so a household refused at one seat keeps its lot at the next:
nothing about a part depends on where the house lands.
"""

from __future__ import annotations

import math
import random
from collections.abc import Mapping
from typing import Any

from ..farm_fixtures import KURA_PARTS as KURA_PARTS
from ..farm_fixtures import kura_rect as kura_rect

#: The nucleated farmhouse's length and depth factors over its 46 x 28 ft base (`_try_place_bundle`): a minka grew by
#: adding bays along the ridge, so the length varies a lot and the depth a little (the ranges are the placer's own).
LENGTH_FACTORS = (0.85, 1.35)
DEPTH_FACTORS = (0.90, 1.10)

#: The share of plain farmhouses that carry a kura storehouse annex: ONE FARM IN EIGHT (feature 280 M20,
#: research/homesteads/720 - a calibration on the one premodern count read, Kakimochi's 2 storehouses in 16 households,
#: both powerful). The 0.2993 it was drawn at came from Sugiura's 1972 survey, modern. The headman keeps one always (his by
#: the GM's ruling of 2026-07-21, `Settlement._try_place_bundle`), outside the lots.
KURA_SHARE = 0.125

#: No drawn farmhouse runs longer than this against its width (homes H08): the minka norm is about 1.3-2.5:1, and a
#: footprint past 2.7:1 reads as a shed. The ladder's corner (1.35 x 46 over 0.90 x 28) is 2.46.
FARMHOUSE_MAX_ASPECT = 2.7


def quota_member(j: int, p: float) -> bool:
    """Does the `j`-th member of a quota ordering carry a part of share `p`? The Bresenham step: exactly `round(n * p)` of
    the first `n` members do, for every `n`."""
    return math.floor((j + 1) * p + 0.5) > math.floor(j * p + 0.5)


def _order(seed: int, salt: str, n: int) -> list[int]:
    """A seed-shuffled place for each of `n` households (the order the quota walks), by (seed, salt) alone."""
    order = list(range(n))
    random.Random(f"{seed}:{salt}").shuffle(order)
    return order


def quota_carriers(seed: int, salt: str, n: int, p: float) -> list[bool]:
    """Which of `n` households (by seat ordinal) carry a part of share `p`: exactly `round(n * p)` of them."""
    return [quota_member(j, p) for j in _order(seed, salt, n)]


#: The fixture kinds whose quota goes to the larger houses first (feature 280 M21, research/homesteads/720: "the storehouse
#: and the sheds go to the larger houses first" - the wood shed, a building of its own on about four farmsteads in ten). The
#: storehouse itself is dealt the same way (`HouseholdLots.kura`, feature 293).
LARGER_FIRST = frozenset({"woodpile"})


def larger_first(seed: int, salt: str, sizes: list[tuple[float, float]], p: float) -> list[bool]:
    """Which households (by seat ordinal) carry a part of share `p` that goes to the larger houses first: exactly as many
    as `quota_carriers` gives (round(n x p)), taken largest footprint first (the size ladder's length x depth factors), the
    seed-shuffled order breaking ties."""
    n = len(sizes)
    count = sum(quota_carriers(seed, salt, n, p))
    order = _order(seed, salt, n)
    ranked = sorted(range(n), key=lambda k: (-sizes[k][0] * sizes[k][1], order[k]))
    keep = set(ranked[:count])
    return [k in keep for k in range(n)]


def size_ladder(seed: int, n: int) -> list[tuple[float, float]]:
    """`n` (length, depth) factor pairs, one rung per household by seat ordinal (homes H17): the lengths evenly spaced over
    `LENGTH_FACTORS`, the depths over `DEPTH_FACTORS`, each ladder in its own seed-shuffled order."""
    if n <= 0:
        return []

    def rungs(lo: float, hi: float) -> list[float]:
        return [lo + (hi - lo) * (i + 0.5) / n for i in range(n)]

    lengths, depths = rungs(*LENGTH_FACTORS), rungs(*DEPTH_FACTORS)
    lo, do = _order(seed, "size_length", n), _order(seed, "size_depth", n)
    return [(lengths[lo[k]], depths[do[k]]) for k in range(n)]


def house_aspect_bound() -> float:
    """The longest-to-widest a ladder rung can draw: the longest length over the shallowest depth."""
    return (46.0 * LENGTH_FACTORS[1]) / (28.0 * DEPTH_FACTORS[0])


assert house_aspect_bound() <= FARMHOUSE_MAX_ASPECT, "the size ladder can draw a farmhouse past the minka norm (homes H08)"


class HouseholdLots:
    """The lots of one settlement's `n` declared households: `lot(k)` is household `k`'s size factors, whether it keeps a
    kura and whether it keeps a beast (the byre form's keeper share, `byre_share`; 0 where the settlement's byres are not
    the households' own). Built once per seating (`stage_homesteads` sets it on the settlement); the `k`-th house seated
    takes lot `k`."""

    __slots__ = ("byre", "fixtures", "kura", "n", "sizes")

    def __init__(self, seed: int, n: int, byre_share: float = 0.0, fixture_shares: Mapping[str, float] | None = None) -> None:
        self.n = n
        self.sizes = size_ladder(seed, n)
        # THE STOREHOUSE GOES TO THE LARGER HOUSES FIRST (feature 293, research/questions/0040-farm-storehouses-kura.html): the count is the quota's,
        # dealt down the size ladder by the main house's footprint - the carriers are exactly the largest houses. The record's
        # one village put its two with its 2nd- and 3rd-largest houses and its largest had none, so the strict cut is a
        # DELIBERATE DEVIATION (the weighted draw was priced and not taken); a tie goes by the seed-shuffled order, a GUESS the
        # record is silent on, and the ladder's distinct rungs make one all but impossible. It was the shuffled quota
        # (`quota_carriers`), and Sawada's one storehouse stood against its 18th-largest house of 19.
        self.kura = larger_first(seed, "kura", self.sizes, KURA_SHARE)
        self.byre = quota_carriers(seed, "byre", n, byre_share)
        # THE FARMSTEAD FIXTURES, a quota per kind (feature 287, homes H32): exactly round(n x share) households keep each -
        # the wood shed on the LARGER houses first (`larger_first`, feature 280 M21), every other kind by the shuffled order
        self.fixtures = {k: larger_first(seed, f"fixture_{k}", self.sizes, p) if k in LARGER_FIRST else quota_carriers(seed, f"fixture_{k}", n, p) for k, p in (fixture_shares or {}).items()}

    def fixtures_of(self, k: int) -> tuple[str, ...]:
        """The fixture kinds household `k` keeps, in the settlement's order of kinds."""
        return tuple(kind for kind, carriers in self.fixtures.items() if 0 <= k < self.n and carriers[k])

    def lot(self, k: int) -> tuple[float, float, bool, bool] | None:
        """Household `k`'s (length factor, depth factor, keeps a kura, keeps a beast); None past the declared count."""
        if not 0 <= k < self.n:
            return None
        lf, df = self.sizes[k]
        return lf, df, self.kura[k], self.byre[k]


#: How far a household may live from water, in feet: `settlement_dwellings_watered`'s ~760 real ft to the nearest well,
#: channel, pond or stream (homes H11) - the figure `place_wells` has always served.
WATER_REACH_FT = 760.0


def needs_pocket(s: Any, x: float, y: float) -> bool:
    """Does a household seated at (x, y) carry a WELL POCKET (feature 287, homes H10 and H11)? The first household
    always does - so a settlement always has a well - and every later one exactly when no pocket stands within
    `WATER_REACH_FT` of it and no surface water serves it (`surface_water_dist`, the watered rule's own measure): so every
    household is within reach of a well or open water by construction, and two pockets stand at least that far apart."""
    pockets = getattr(s, "_pockets", None)
    if pockets is None:
        return False
    if not pockets:
        return True
    from ..land.wet import surface_water_dist  # the leaf stays free of the land package at import

    reach = s.px(WATER_REACH_FT)
    return all(math.hypot(x - px, y - py) > reach for px, py in pockets) and surface_water_dist(s.M, x, y) > reach


def watered(s: Any, x: float, y: float, well: bool) -> bool:
    """THE ONE PREDICATE of a household's water (feature 287, homes wave 5; `test_every_household_can_reach_water`): a
    household whose house stands at (x, y) reaches water - it carries its own well pocket (`well`), or a pocket already laid
    or surface water stands within `WATER_REACH_FT` (`needs_pocket` asks no more of it). Asked of the house where it is
    PLACED: the pocket was decided at the point the seat was sought from, and the placer may move the house off it (the
    envelope's computed move, the dispersed slides), so a candidate carried out of every pocket's reach is refused."""
    return well or not needs_pocket(s, x, y)


def household_parts(s: Any, x: float, y: float, kind: str, role: Any) -> tuple[tuple[float, float, bool, bool] | None, str | None, bool]:
    """What the household about to be seated at (x, y) carries (plan M5): its lot (the k-th plain household takes lot
    k), the byre form its bundle reserves a stall for (a keeper on a household form), whether it carries a well pocket, and
    its farmstead fixtures (the lot's kinds). Set on the settlement for the seat search (`_household_byre`,
    `_household_well`, `_household_fixtures`, and `_household_watered`, which holds its candidates to `watered`), where
    `_bundle_layout` lays the parts inside the envelope; `seat_parts_done` takes them down."""
    lots = getattr(s, "_lots", None)
    k = sum(1 for h in s.M["houses"] if h.get("kind") == "plain")
    lot = lots.lot(k) if lots is not None and kind == "plain" and role is None else None
    form = getattr(s, "_byre_form", None) if lot is not None and lot[3] else None
    well = kind == "plain" and needs_pocket(s, x, y)
    s._household_byre, s._household_well = form, well
    s._household_watered = kind == "plain"  # the placer holds a household's candidates to `watered`
    s._household_fixtures = lots.fixtures_of(k) if lots is not None and lot is not None else ()
    return lot, form, well


def seat_parts_done(s: Any) -> None:
    s._household_byre, s._household_well, s._household_fixtures, s._household_watered = None, False, (), False


def record_parts(s: Any, rec: dict[str, Any], geom: Any, form: str | None) -> None:
    """The reserved parts a seated household's record carries: its stall (`byre`: where it is drawn, its turn, its box),
    its well pocket (`well_pocket`, the wellhead's center), which the seating also remembers (`_pockets`), its farmstead
    fixtures (`fixtures`: each laid in the bundle), and its share of the wood floor (`wood_share`: the copse seats it
    reserved, their crowns' radius and the ground they cover in sq ft)."""
    cx, cy = rec["x"], rec["y"]
    if form and geom.get("byre") is not None:  # the reserved stall, drawn where it was reserved (`draft_byres`)
        bx, by = geom["byre"][0], geom["byre"][1]
        th = math.radians(rec["rot"])
        west = (bx - cx) * math.cos(th) + (by - cy) * math.sin(th) < 0  # the flank it stands on, in the house's frame
        turn = (90.0 if west else -90.0) if form == "courtyard" else 90.0  # `byre_part`'s turn: its long side along the wall
        rec["byre"] = {"x": bx, "y": by, "rot": rec["rot"] + turn, "box": list(geom["boxes"]["byre"])}
    if geom.get("well") is not None:
        rec["well_pocket"] = [geom["well"][0], geom["well"][1]]
        if getattr(s, "_pockets", None) is not None:  # remembered only while a seating runs (a grove farm's bundle lays its own)
            s._pockets.append((geom["well"][0], geom["well"][1]))
    boxes = (geom.get("boxes") or {}).get("fixtures") or {}
    if geom.get("fixtures"):  # the fixtures laid in the bundle (homes H32), drawn where they were laid (`farmstead_fixtures`)
        rec["fixtures"] = [{"kind": k, "x": r[0], "y": r[1], "w": r[2], "h": r[3], "box": list(boxes[k])} for k, r in geom["fixtures"].items()]
        # ...with the size each was laid at (`fixture_ft`: the privy's and the bath room's are rolled per household, feature
        # 280) and the wall the bath room took, so the drawing draws the laid footprint and records its seat
        notes = geom.get("fixture_notes") or {}
        for f in rec["fixtures"]:
            if f["kind"] in (notes.get("ft") or {}):
                f["ft"] = list(notes["ft"][f["kind"]])
            if f["kind"] == "bath" and notes.get("bath_seat"):
                f["seat"] = notes["bath_seat"]
    seats = geom.pop("wood", None)
    wood = getattr(s, "_wood", None)
    if seats is not None and wood is not None:  # its share of the wood floor (woods W25, plan D9), reserved and on the record
        covered = wood.commit(geom, seats)
        rec["wood_share"] = {"seats": [[x, y] for x, y in seats], "r": wood.cr, "ft2": round(covered / s.px(1.0) ** 2)}


#: The laid fixtures drawn as a record of their own, and so held until drawn (`hamletgen/homesteads/holds.py`): the farmstead
#: fixtures and the retirement house. A persimmon is recorded by its crown's radius alone, which the matrix reads no extent
#: from; a bath's corridor is drawn with its bath.
HELD_KINDS = frozenset({"privy", "manure", "bath", "coop", "woodpile", "shrine", "retirement"})


def held_part_records(hx: float, hy: float, well: Any, fixtures: Any, vr: float) -> list[tuple[str, dict[str, Any]]]:
    """(key, record) for each part a household's seating laid that stands HELD until it is drawn: the well pocket as its
    wellhead (`well`, its center, or None) and each fixture of `HELD_KINDS` as its seat's box (`fixtures`: (kind, box)
    pairs, the box (cx, cy, w, h) as drawn). The ONE form both the hold (`hold_laid_parts`) and the seat's question
    (`bundle_admitted`) use, so the part asked of the registry is the part held there."""
    out: list[tuple[str, dict[str, Any]]] = []
    if well is not None:
        out.append(("wells", {"x": round(float(well[0]), 1), "y": round(float(well[1]), 1), "r": 8, "vr": vr}))
    of = [round(float(hx), 1), round(float(hy), 1)]
    for kind, bx in fixtures:
        if kind not in HELD_KINDS or not bx:
            continue
        key = "retirement_houses" if kind == "retirement" else "farm_fixtures"
        out.append((key, {"x": float(bx[0]), "y": float(bx[1]), "w": float(bx[2]), "h": float(bx[3]), "of": of}))
    return out


#: The key each built or worked part of a bundle is recorded under when it is drawn (`houses.py`, `yards.py`, `gardens.py`,
#: `byres.py`): the part asked of the registry at seat time under the key the matrix will judge it by.
BUNDLE_PART_KEYS = (("house", "houses"), ("yard", "threshing_yards"), ("shed", "farm_sheds"), ("byre", "byres"))


def bundle_records(geom: Mapping[str, Any], vr: float) -> list[tuple[str, dict[str, Any]]]:
    """(key, record) for EVERY part a homestead bundle lays (feature 287, water W53): the house, its yard, its kura, its
    byre and each garden bed as the turned rect it will be drawn as (`rot` the bundle's turn), and the parts held until
    drawn as they are held (`held_part_records`)."""
    hx, hy = float(geom["house"][0]), float(geom["house"][1])
    rot = float(geom.get("turn") or 0.0)
    of = [round(hx, 1), round(hy, 1)]

    def rect(r: Any, parent: bool) -> dict[str, Any]:
        rec = {"x": round(float(r[0]), 1), "y": round(float(r[1]), 1), "w": float(r[2]), "h": float(r[3]), "rot": rot}
        return {**rec, "of": of} if parent else rec

    out = [(key, rect(geom[part], key != "houses")) for part, key in BUNDLE_PART_KEYS if geom.get(part) is not None]
    out += [("gardens", rect(g, True)) for g in geom.get("gardens") or ()]
    boxes = (geom.get("boxes") or {}).get("fixtures") or {}
    return out + held_part_records(hx, hy, geom.get("well"), [(k, boxes.get(k)) for k in (geom.get("fixtures") or {})], vr)


def bundle_admitted(s: Any, geom: Mapping[str, Any]) -> bool:
    """THE BUNDLE ASKS THE REGISTRY FIRST (feature 287, water W53 and plan M8): does the overlap matrix admit every part this
    bundle lays on what already stands - the field's ditches and channels, the streams, the lanes, the houses and parts
    already recorded, and the ground the seating reserved? A layout it refuses is refused and the placer tries the next.
    Under feature 284's probes Inashiro laid a privy on a field ditch at (2960, 1780) that no fit rule of the seat asked
    about, and the hold raised `OverlapRefused` at the seating's end (research R9, failure 4)."""
    vr = float(s._well_vr())
    return all(s.admits(k, rec) for k, rec in bundle_records(geom, vr))
