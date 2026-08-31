"""Split from hamletgen/homesteads.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist
from l7r.diagram.settlement._knobs import knob_rng
from l7r.diagram.settlement.farm_fixtures import FIXTURE_FT, PERSIMMON_CROWN_FT

from ..consts import Poly, Pt
from ..plan import SitePlan
from .bamboo import _strip_blocked

# FARMSTEAD FIXTURES (feature 133 T53-T59, GM 2026-08-27; research/homesteads.md "The farmstead's
# fixtures"). Each row: the kind, the per-hamlet PREVALENCE BAND (rolled once per map from the seed -
# two hamlets differ honestly where the record gives a range), and the seats tried in the house's
# local frame (+y = the sunny front where the yard is, -y = the back wall, -x = the kura side). The
# first seat is rolled where the record shows two forms; the rest are fallbacks. Every number is
# labeled in the research entry:
#   privy    READ  an independent outbuilding was "普通" (Nipponica) - near-universal; sited at the back
#                  door, by the naya, or at the gate (戸口便所) - three attested seats, so rolled
#   woodpile READ  a woodshed for firewood/charcoal on the reconstructed farmstead (Boso-no-Mura);
#                  Sugiura counts the SHED on 0.76 - a stack under the eaves is the cheaper, older
#                  form; its wall is a GUESS (the back wall or the kura's, out of the rain)
#   manure   READ  in Han China the latrine stood over the pigsty (AIC) - muck and privy are one
#                  cluster; in Japan the pit stood "near the stable, under the eaves" (SUMMARY-ONLY);
#                  so the heap is seated beyond the privy; the share is a GUESS (Sugiura: a SHED on 0.24)
#   bath     READ  the goemon-buro "was used widely in self-sufficient farm villages" (Mizumaki); Sugiura:
#                  a bath SHED on 0.29, IN the house on 0.53 - two forms, so only the shed share is drawn
#   coop     READ  "farmers in most regions of China managed to keep a pig and some chickens in their
#                  yard" (Animals through Chinese History); a ground-level enclosure (Qimin Yaoshu);
#                  the share is a GUESS bounded by "most regions"
#   shrine   READ  two patterns - every house, or only certain old families (Tokushima; ja.wikipedia);
#                  the GM chose the rare pattern (T58); Sugiura 0.03; corner NE (kimon, READ), NW
#                  (17 of 37, SUMMARY-ONLY), SW (Tokushima, READ) - rolled
#   persimmon READ "どこの庭先にも柿の木が植えてある" and Miyazaki Yasusada urged planting them round the
#                  homestead; it shades the house in summer, so it stands beside it (side a GUESS)
FIXTURE_BANDS: dict[str, tuple[float, float]] = {
    "privy": (0.85, 0.95),
    "woodpile": (0.75, 0.95),
    "manure": (0.40, 0.70),
    "bath": (0.20, 0.45),
    "coop": (0.50, 0.80),
    "shrine": (0.03, 0.08),
    "persimmon": (0.80, 0.95),
}
_FIXTURE_ORDER = ("privy", "manure", "bath", "coop", "woodpile", "shrine", "persimmon")  # the buildings before the stack, which has the most seats
_PRIVY_SEATS = (("back", 0.60), ("gate", 0.25), ("naya", 0.15))
PRIVY_SUN_MIN_FT = 18.0  # the sun-side search starts at the house wall and steps out; measured free ground begins 24-32 ft
# 48, NOT 72 (settlement-review 2026-08-29, acceptance). At 72 ft the search walked the privy out past
# its own work yard and, in a cluster where the next farmhouse is 50 ft away, out of its own homestead
# altogether: 15 of 86 privies and manure pits ended up nearer ANOTHER house than the one they serve,
# against 0 of 52 on main - a legibility defect this feature CREATED, and one no check can see, because
# nothing tests which farmstead a fixture belongs to. The comment that used to sit on 72 claimed it
# "stops where a fixture would no longer read as belonging to that homestead"; that was the property it
# was chosen for and it did not hold. Wang & Ochiai gives a DIRECTION, not a distance, so the radius is
# ours to set and it belongs against the house: the three attested seats are all at the wall.
PRIVY_SUN_MAX_FT = 48.0
PRIVY_SUNNY_SHARE = 0.727  # the share of outhouses seated SE-to-S: Wang & Ochiai 2022 measured 72.7% in
# Arakawa village, and the GM (2026-08-29) ruled the figure be used literally rather than rounded. The
# reason the record gives is fermentation, not wind - see the note at the seat roll.
_SHRINE_CORNERS = (("NW", 0.45), ("NE", 0.35), ("SW", 0.20))
_WALL_GAP_FT = 3.5  # the review measured -0.3 ft at 3.0 against the drawn wall; half a foot of true daylight
_SALT = {"privy": 101.0, "manure": 102.0, "woodpile": 103.0, "bath": 104.0, "coop": 105.0, "shrine": 106.0, "persimmon": 107.0}


def nearer_own_house(seat: tuple[float, float, float, float], hx: float, hy: float, ca: float, sa: float, others: Sequence[Pt]) -> tuple[int, float, float]:
    """Sort key preferring a fixture seat that is nearer its OWN farmhouse than any other house's.

    `seat` is (dx, dy, w, d) in the house's own raked frame; `ca`/`sa` are that rake's cosine and sine.
    Returns (0 if the seat belongs unambiguously to this house else 1, distance from it) - so a caller
    that sorts by it keeps its own candidate order within each class and only demotes the seats a
    reader would attribute to the neighbor.

    Lifted out of the privy branch's closure (GM 2026-08-28: an inner function that is hard to test
    gets lifted out) so the manure heap can share ONE body with it, and so the rule can be asked with
    two tuples instead of a whole settlement."""
    _mx, _my = hx + seat[0] * ca - seat[1] * sa, hy + seat[0] * sa + seat[1] * ca
    _dmine = math.hypot(_mx - hx, _my - hy)
    if not others:
        return (0, _dmine, -_dmine)
    _dother = min(math.dist((_mx, _my), _o) for _o in others)
    # The third element is the MARGIN, negative when the seat is unambiguously this house's. Sorting by
    # it does what a flag cannot: where no candidate is unambiguous - which is the common case for a
    # heap that must lie beyond a privy already on the neighbor's side - it still picks the LEAST
    # misattributable of them, instead of leaving the arbitrary first one in place.
    return (0 if _dmine < _dother else 1, _dmine, _dmine - _dother)


def _roll(weights: Sequence[tuple[str, float]], u: float) -> str:
    acc = 0.0
    for name, w in weights:
        acc += w
        if u < acc:
            return name
    return weights[-1][0]


def farmstead_fixtures(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]]) -> int:
    """Seat and draw the small fixtures of every farmstead. Returns the count placed.

    Seated in `stage_hinterland` after the web and the board, like the household bamboo (T49): a
    fixture hugs its house and is tested against every placed footprint, lane, paddy, marsh and pond
    (`_strip_blocked`), so the web is never re-threaded and nothing is drawn on anything. Presence
    per house is positional (`_hjit`) against the hamlet's own share, which is rolled once per map
    inside the band above and declared in meta for the gate. Every seated fixture joins `s.placed`
    and `s.block_polys`, so the bamboo strips and the scrub keep off it."""
    if not houses:
        return 0
    rng = knob_rng(s.seed, "farm_fixtures")
    shares = {k: round(lo + rng.random() * (hi - lo), 3) for k, (lo, hi) in FIXTURE_BANDS.items()}
    s.M["meta"]["farm_fixtures"] = dict(shares)
    mins = {k: int(v) for k, v in plan.fixtures_min.items() if k in FIXTURE_BANDS}
    if mins:
        s.M["meta"]["farm_fixtures_min"] = dict(mins)
    px = s.px
    g = px(_WALL_GAP_FT)
    fields = [list(f) for f in s.field_polys]
    marsh = [[(float(a), float(b)) for a, b in m["poly"]] for m in s.M.get("marshes", []) if m.get("poly")]
    pond = s.M.get("pond")
    lanes = [([(float(a), float(b)) for a, b in ln["pts"]], float(ln.get("w", 3)) / 2 + px(3.0)) for ln in s.M.get("lanes", []) if len(ln.get("pts") or []) >= 2]
    count = 0
    shrines_left = max(1, round(shares["shrine"] * len(houses)), mins.get("shrine", 0))  # RARE means rare: positional luck cannot exceed the share (a spec floor may)
    # THE FLOOR (T61, GM 2026-08-27: "a min number of something which may or may not appear"): after the
    # rolled pass, any kind short of its spec'd minimum is forced onto the houses that lack it, in
    # positional order, until the floor is met or every house has been tried
    forced: set[str] = set()
    for h in list(houses) + [dict(h, _force=True) for h in sorted(houses, key=lambda q: s._hjit(float(q["x"]), float(q["y"]), 108.0))]:
        if h.get("_force"):
            have = {k: 0 for k in FIXTURE_BANDS}
            for rec in s.M.get("farm_fixtures", []):
                have[rec["kind"]] = have.get(rec["kind"], 0) + 1
            have["persimmon"] = len(s.M.get("persimmons", []))
            forced = {k for k, v in mins.items() if have.get(k, 0) < v}
            if not forced:
                break
        hx, hy, hw, hh = float(h["x"]), float(h["y"]), float(h["w"]), float(h["h"])
        rot = float(h.get("rot", 0.0))
        th = math.radians(rot)
        ca, sa = math.cos(th), math.sin(th)
        shed_side = h.get("shed_side", "W")
        privy_at: tuple[float, float] | None = None

        for kind in _FIXTURE_ORDER:
            if h.get("_force"):
                own = (round(hx, 1), round(hy, 1))
                has = any(r["kind"] == kind and tuple(r.get("of", ())) == own for r in s.M.get("farm_fixtures", [])) or (
                    kind == "persimmon" and any(tuple(r.get("of", ())) == own for r in s.M.get("persimmons", []))
                )
                if kind not in forced or has:
                    continue
            elif s._hjit(hx, hy, _SALT[kind]) >= shares[kind]:
                continue
            if kind == "shrine" and shrines_left <= 0:
                continue
            u = s._hjit(hx, hy, _SALT[kind] + 0.5)
            if kind == "persimmon":
                r = px(PERSIMMON_CROWN_FT)
                # a raked house is a circumscribed SQUARE to the canopy keep-out (_canopy_keepouts mirrors
                # structures_clear_of_trees), so the trunk stands a half-diagonal + the crown out from the center
                reach = math.hypot(hw / 2, hh / 2) + r + s.CANOPY_PAD + 1.0
                tseats = [(reach, hh * 0.1), (-reach, hh * 0.1), (reach * 0.75, -reach * 0.75), (-reach * 0.75, -reach * 0.75), (reach * 0.75, reach * 0.75), (-reach * 0.75, reach * 0.75)]
                if u < 0.5:
                    tseats[0], tseats[1] = tseats[1], tseats[0]
                for lx, ly in tseats:
                    cx, cy = hx + lx * ca - ly * sa, hy + lx * sa + ly * ca
                    # the TRUNK is tested against drawn footprints, not the plot reservations: a yard tree
                    # stands at a plot's edge, and in a nucleated cluster the reservations tile the ground
                    if _trunk_blocked(s, cx, cy, px(4.0), fields, marsh, pond, lanes):
                        continue
                    # no tree on a roof: the SAME keep-outs and the same test the grove drawer uses, so
                    # structures_clear_of_trees (which mirrors them) cannot disagree with this seat
                    rects, circles = s._canopy_keepouts((cx - r - 40, cy - r - 40, cx + r + 40, cy + r + 40))
                    if s._crown_covers(cx, cy, r, rects, circles, pad=s.CANOPY_PAD):
                        continue
                    s.persimmon(cx, cy, of=(hx, hy))
                    s.placed.append((cx, cy, px(4.0), px(4.0)))
                    count += 1
                    break
                continue
            w, d = px(FIXTURE_FT[kind][0]), px(FIXTURE_FT[kind][1])  # along the wall, out from it
            # candidate seats as (lx, ly, w_local, h_local); the fixture is drawn raked with the house
            if kind == "privy":
                seat = {
                    "back": (hw * 0.3, -(hh / 2 + g + d / 2), w, d),
                    "gate": (-hw * 0.35, hh / 2 + g + d / 2, w, d),
                    "naya": ((hw / 2 + g + d / 2), -hh * 0.25, d, w) if shed_side == "N" else (-(hw / 2 + hw * 0.32 + g + d / 2), -hh * 0.25, d, w),
                    # THE SUN SIDE, which the record documents and this seat table did not have (feature 152
                    # T07). The three seats above are all north or flank: measured on the pool before this
                    # change, every privy on every map sat at bearing 33-73 degrees from its house. The source
                    # the GM ruled on puts 72.7% of them SOUTHEAST to SOUTH, so a seat has to exist there.
                }
                first = _roll(_PRIVY_SEATS, u)
                seats = [seat[first]] + [seat[k] for k, _ in _PRIVY_SEATS if k != first]
                # THE OUTHOUSE FACES THE SUN, AT THE RATE THE RECORD GIVES (feature 152 T07, GM 2026-08-29:
                # "we should literally use the 72.7% number for the chance of any given outhouse being in the
                # southeast and south directions"). Wang & Ochiai's survey of farmhouses in Arakawa village
                # (JAABE 21:6, 2022) found toilets "tended to be located in southeast and south directions,
                # with a total percentage at 72.7%, as a relatively warm temperature helped quick fermentation
                # of excrements" - night soil was fertilizer, and the sun on that side sped the composting.
                #
                # NOT WIND. A settlement-review found every privy on Sawada standing upwind of its own house
                # and proposed seating them downwind; the research pass sent to settle it CONTRADICTED that -
                # the same paper's wind-siting finding covers storage buildings and retirement houses, not
                # toilets, and the words leeward, downwind, odor and hygiene appear nowhere in it. So the
                # defect the review found was real (the seat was north on every map, because these offsets are
                # in the HOUSE's frame and houses draw at rot 0-4) and its proposed cause was wrong.
                #
                # Direction is the primary rule and the attested seats are the tiebreak: the three seats keep
                # their own weights (`_PRIVY_SEATS`) WITHIN each group, so a map that cannot put a privy to the
                # southeast still seats it where the record says privies go.
                _u_dir = s._hjit(hx, hy, _SALT[kind] + 0.25)
                # THE SUN SIDE IS SEARCHED, NOT GUESSED AT (feature 152 T07 round 2, GM 2026-08-29).
                # The first attempt offered the sector a handful of hand-picked offsets - a couple of
                # bearings at a couple of radii, straight out from the house wall - and they happened to
                # land on the work yard or a garden, so the placer fell through to the old north-east seat
                # and the realized share stuck at 43.8%. I read that plateau as the ground being full and
                # said so; the GM asked the obvious question back - the real farmsteads the 72.7% comes
                # from had threshing yards too, so why can ours not do what they did? Measured in answer,
                # on Sawada: EVERY one of the 19 houses has free sun-side ground, 49 to 151 clear 6x6 ft
                # spots each, the nearest 24-32 ft out - the same radius the privy already uses on its
                # north-east side. The yard blocks a slice of a 90-degree arc, not the side. The plateau
                # was evidence about my offsets, not about the ground.
                #
                # So the sector is walked instead: bearings across SE-to-S, radii outward from the house,
                # NEAREST FIRST (the attested seats are all against the house - back door, gate, naya - so
                # the privy belongs as close as the ground allows), and `_strip_blocked` below takes the
                # first that is clear. Bearings are COMPASS bearings in map space, converted back through
                # the house's own rake, so a raked farmhouse still gets a true southeast seat.
                _sun: list[tuple[float, float, float, float]] = []
                for _r_ft in range(int(PRIVY_SUN_MIN_FT), int(PRIVY_SUN_MAX_FT) + 1, 4):
                    for _b in range(1125, 2026, 75):  # 112.5 to 202.5 degrees, tenths
                        _bd = _b / 10.0
                        _rr = px(float(_r_ft))
                        _dx, _dy = _rr * math.sin(math.radians(_bd)), -_rr * math.cos(math.radians(_bd))
                        _sun.append((_dx * ca + _dy * sa, -_dx * sa + _dy * ca, w, d))
                _sun.sort(key=lambda q: (math.hypot(q[0], q[1]), abs(math.degrees(math.atan2(q[0] * ca - q[1] * sa, -(q[0] * sa + q[1] * ca))) % 360.0 - 157.5)))
                # ...AND A FIXTURE BELONGS TO THE HOMESTEAD IT SERVES. A seat closer to a neighbor's
                # farmhouse than to its own is drawn in that neighbor's yard as far as a reader is
                # concerned, whatever the record says - so the sun list drops any seat that is not
                # strictly nearest its own house. This is the ownership test the 72 ft radius was
                # trusting the geometry to provide, made explicit.
                # A STRICT "must be nearest to its OWN house" filter was tried here and cost too much.
                # It states the defect exactly - a fixture nearer a neighbor's farmhouse reads as theirs -
                # but in a cluster the sun side of one house often IS nearer the next, and filtering on it
                # rejected seats that sit honestly in their own yard: privies fell to 2 of 11 declared on
                # Mizuguchi and the sun share to 49%. The bound that does the work without the collateral
                # is the RADIUS (`PRIVY_SUN_MAX_FT`, cut 72 -> 48): a seat against its own house is in its
                # own yard whoever else is near. Ownership stays as a TIE-BREAK - among seats the ground
                # allows, one that is nearer its own house than any other comes first.
                _others = [(float(_h["x"]), float(_h["y"])) for _h in houses if (float(_h["x"]), float(_h["y"])) != (hx, hy)]
                if _others:

                    def _mine_first(
                        _q: tuple[float, float, float, float], _hx: float = hx, _hy: float = hy, _ca: float = ca, _sa: float = sa, _oth: list[Pt] = _others
                    ) -> tuple[int, float]:  # the loop's values bound as defaults - this closure outlives the iteration
                        _k = nearer_own_house(_q, _hx, _hy, _ca, _sa, _oth)
                        return (_k[0], _k[1])

                    _sun.sort(key=_mine_first)
                seats = (_sun + seats) if _u_dir < PRIVY_SUNNY_SHARE else seats
            elif kind == "manure":
                if privy_at is not None:
                    plx, ply = privy_at
                    out_ = -1.0 if ply < 0 else 1.0
                    # BEYOND THE PRIVY, and with somewhere to go when that one spot is taken (feature 152
                    # T16). Three candidates seated 3 of a declared 8 per map: the heap is placed against
                    # the privy, and where the privy now sits on the sun side the ground just past it is
                    # often the work yard. The researched rule is only that the heap lies BEYOND the privy
                    # (research/homesteads.md) - which these all do; they differ in how far and how wide.
                    # ...AND NOT AT A FIXED OFFSET (feature 152 T17). Every heap sat the SAME distance
                    # beyond its privy - an acceptance review measured 15 of 19 pairs at |dy| 9.4-9.9 ft
                    # with |dx| under 1 ft - so the pair read as one stamp repeated down the row. The
                    # researched rule is only that the heap lies BEYOND the privy; how far beyond is ours,
                    # and real yards vary. Jittered off the homestead's own position so it is stable for a
                    # given farmstead and differs between them.
                    _pout = px(FIXTURE_FT["privy"][1]) / 2 + g + d / 2 + px(9.0) * (s._hjit(hx, hy, 102.4) - 0.5)
                    seats = [
                        (plx, ply + out_ * _pout, w, d),
                        (plx + w * 1.1, ply, w, d),
                        (plx - w * 1.1, ply, w, d),
                        (plx + w * 1.1, ply + out_ * _pout, w, d),
                        (plx - w * 1.1, ply + out_ * _pout, w, d),
                        (plx, ply + out_ * (_pout + px(10.0)), w, d),
                        (plx + w * 1.9, ply, w, d),
                        (plx - w * 1.9, ply, w, d),
                    ]
                    # ...AND THE HEAP IS THIS HOUSE'S HEAP (settlement-review 2026-08-29, acceptance
                    # re-check). One pit on Kuwabata sat 53.7 ft from the farmhouse it serves and 45.4 ft
                    # from another; a reader attributes it to the nearer house and the manifest says
                    # otherwise. Ownership is a TIE-BREAK only, the same as the privy's and for the same
                    # reason: in a cluster the ground beyond one house's privy is often nearer the next.
                    #
                    # TWO STRONGER LEVERS WERE TRIED AND REVERTED, MEASURED ACROSS THE 13-MAP POOL.
                    # (1) A SECTOR SEARCH beyond the privy, the shape that worked for the privy itself
                    #     (radii 2-24 ft past its far edge, swung +/-54 deg): 5 misattributed of 68, against
                    #     4 of 66 with the eight offsets. It seats more heaps, none of them better placed.
                    # (2) Sorting by the ownership MARGIN rather than the flag, so that where no candidate
                    #     is unambiguous the LEAST misattributable wins: 4 of 67, no better - and it pulled
                    #     heaps back toward the house to win the margin, so "the heap lies beyond the privy"
                    #     - the actual researched rule (research/homesteads.md) - fell from 16 of 16 to
                    #     9 of 15. A reader-legibility nicety is not worth a researched rule.
                    # (3) The margin sort applied INSIDE the beyond-the-privy group only - the shape the
                    #     acceptance review named as the one both attempts stepped over, and it is a real
                    #     new mechanism: partitioning on the `out_ * _pout` term means every seat it can
                    #     promote is already beyond the privy, so it cannot break the rule that killed (2).
                    #     Implemented and rolled: 4 of 66 by centers, 6 of 66 by footprints, 14 of 14
                    #     beyond - IDENTICAL to the shipped state on all three. Reverted as complexity
                    #     that buys nothing; the lever is sound and it is the geometry that is fixed.
                    #
                    # THE FIGURE IS 6, NOT 4, AND A READER IS WHY (settlement-review 2026-08-29). The sort
                    # above compares distances to recorded house CENTERS, and a reader compares against the
                    # drawn RECTANGLE. Against footprints the pool carries SIX of 66, and the worst case is
                    # much worse than the point metric renders it: Kashikawa's heap at (2194.1, 2759.2) is
                    # 32.0 ft from its own farmhouse's wall and 8.4 ft from a neighbor's, which the center
                    # metric flatters to 46.7 against 33.0. The count that belongs next to a claim about
                    # what a reader attributes is the footprint one.
                    # What is left is the geometry itself: where a privy sits on the sun side and the
                    # neighbor is that way too, every seat beyond it belongs to that arc. Four heaps in the
                    # pool are nearer a neighbor's house than their own, and the interactive page resolves
                    # ownership on click. Do not re-try either lever without a new mechanism.
                    _oth = [(float(_h["x"]), float(_h["y"])) for _h in houses if (float(_h["x"]), float(_h["y"])) != (hx, hy)]
                    if _oth:
                        seats.sort(key=lambda _q, _hx=hx, _hy=hy, _ca=ca, _sa=sa, _o=_oth: nearer_own_house(_q, _hx, _hy, _ca, _sa, _o)[0])
                else:
                    seats = [(hw * 0.3, -(hh / 2 + g + d / 2), w, d), (hw / 2 + g + d / 2, hh * 0.3, d, w)]
            elif kind == "woodpile":
                # a stack stands against whichever wall is free, out of the way: both ends of the back wall
                # and a second row behind it, the kura's outer wall, either flank at two heights
                back = -(hh / 2 + g + d / 2)
                seats = [(-hw * 0.25, back, w, d), (hw * 0.25, back, w, d), (-hw * 0.25, back - d - g, w, d), (hw * 0.25, back - d - g, w, d)]
                if shed_side != "N":
                    seats.insert(1, (-(hw / 2 + hw * 0.32 + g + d / 2), hh * 0.1, d, w))  # against the kura's outer wall
                else:
                    seats.insert(0, (-(hw * 0.46 / 2 + g + d / 2), -hh * 0.6, d, w))  # beside the back kura
                seats += [(hw / 2 + g + d / 2, hh * 0.1, d, w), (-(hw / 2 + g + d / 2), hh * 0.1, d, w), (hw / 2 + g + d / 2, -hh * 0.3, d, w), (-(hw / 2 + g + d / 2), -hh * 0.3, d, w)]
            elif kind == "bath":
                seats = [
                    (-hw * 0.3, -(hh / 2 + g + d / 2), w, d),
                    (-(hw / 2 + g + d / 2), hh * 0.2, d, w),
                    (hw / 2 + g + d / 2, -hh * 0.3, d, w),
                    (-hw * 0.3, -(hh / 2 + g + d * 1.5 + g), w, d),
                    (hw * 0.3, -(hh / 2 + g + d * 1.5 + g), w, d),
                ]
            elif kind == "coop":
                # ...and the back seat is not DEAD CENTRE on the wall, which is the stamp itself: at
                # x = 0.0 exactly, a coop taking it stands at bearing 0 from its house on every farmstead
                # (houses draw at rot 0-4), so 9 of 12 Kashikawa coops sat within 4 degrees of north. A
                # hen coop stands somewhere along the back wall, not on its midpoint.
                _cjx = hw * 0.34 * (s._hjit(hx, hy, 105.9) - 0.5) * 2.0
                seats = [(hw / 2 + g + d / 2, hh * 0.3, d, w), (_cjx, -(hh / 2 + g + d / 2), w, d), (-(hw / 2 + g + d / 2), -hh * 0.3, d, w)]
                # A COOP IS NOT ALWAYS DUE NORTH (feature 152 T17). Measured on the shipped maps before
                # this: 9 of 12 Kashikawa coops and 7 of 12 Sawada's stood within 4 degrees of north of
                # their house, because the seat list is in the house's frame and houses draw at rot 0-4.
                # The arrangement is right - a coop goes in the rear yard - and the INVARIANCE is not.
                # The list is rotated by the homestead's own hash so which rear seat is tried first
                # differs between farmsteads while every seat stays one the record supports.
                if seats:
                    _sh = int(s._hjit(hx, hy, 105.5) * len(seats)) % len(seats)
                    seats = seats[_sh:] + seats[:_sh]
            else:  # shrine: a plot corner, world frame
                off = px(14.0)
                corner = {"NW": (-(hw / 2 + off), -(hh / 2 + off)), "NE": (hw / 2 + off, -(hh / 2 + off)), "SW": (-(hw / 2 + off), hh / 2 + off)}
                first = _roll(_SHRINE_CORNERS, u)
                seats = [(*corner[first], w, d)] + [(*corner[k], w, d) for k, _ in _SHRINE_CORNERS if k != first]
            for lx, ly, cw, ch in seats:
                cx, cy = hx + lx * ca - ly * sa, hy + lx * sa + ly * ca
                ext = abs(cw * ca) + abs(ch * sa), abs(cw * sa) + abs(ch * ca)  # the raked rect's bbox
                if _strip_blocked(s, cx, cy, ext[0], ext[1], hx, hy, fields, marsh, pond, lanes):
                    continue
                spin = 90.0 if (cw, ch) == (d, w) and w != d else 0.0  # a flank seat turns the glyph to lie ALONG the wall (review at T99: stacks stood end-on)
                s.farm_fixture(kind, cx, cy, rot=rot + spin, of=(hx, hy), form=("pit" if kind == "manure" and plan.manure_form == "pit" else None))  # the rolled manure form (feature 150)
                ring = [(cx - ext[0] / 2, cy - ext[1] / 2), (cx + ext[0] / 2, cy - ext[1] / 2), (cx + ext[0] / 2, cy + ext[1] / 2), (cx - ext[0] / 2, cy + ext[1] / 2)]
                s.placed.append((cx, cy, ext[0], ext[1]))
                s.block_polys.append(ring)
                if kind == "privy":
                    privy_at = (lx, ly)
                elif kind == "shrine":
                    shrines_left -= 1
                count += 1
                break
    return count


def _trunk_blocked(s: Settlement, cx: float, cy: float, t: float, fields: Sequence[Poly], marsh: Sequence[Poly], pond: Any, lanes: Sequence[tuple[Poly, float]]) -> bool:
    """Would a tree trunk (a t x t box) stand on a drawn footprint, a lane, a paddy, the marsh or the pond?"""
    if cx - t < 30 or cy - t < 30 or cx + t > s.W - 30 or cy + t > s.H - 30:
        return True
    for key in ("houses", "farm_sheds", "gardens", "threshing_yards", "byres", "wells", "kosatsuba", "farm_fixtures", "persimmons", "bamboo_stands"):
        for o in s.M.get(key, []):
            if "x" not in o:
                continue
            ow, oh = float(o.get("w", 2 * float(o.get("r", 8)))), float(o.get("h", 2 * float(o.get("r", 8))))
            if abs(cx - float(o["x"])) < (t + ow) / 2 + 2 and abs(cy - float(o["y"])) < (t + oh) / 2 + 2:
                return True
    corners = [(cx - t / 2, cy - t / 2), (cx + t / 2, cy - t / 2), (cx + t / 2, cy + t / 2), (cx - t / 2, cy + t / 2)]
    for poly in list(fields) + list(marsh):
        if len(poly) >= 3 and any(point_in_poly(q[0], q[1], poly) or min(seg_dist(q[0], q[1], poly[k], poly[(k + 1) % len(poly)]) for k in range(len(poly))) < 6.0 for q in corners):
            return True
    for pts, half in lanes:
        if any(seg_dist(q[0], q[1], pts[k], pts[k + 1]) < half for q in corners for k in range(len(pts) - 1)):
            return True
    for o in s.M.get("dry_plots", []):
        poly = [(float(a), float(b)) for a, b in o.get("poly") or []]
        if len(poly) >= 3 and any(point_in_poly(q[0], q[1], poly) for q in corners):
            return True
    if any(s._on_watercourse(q[0], q[1], pad=4.0) for q in corners):
        return True
    return bool(pond) and ((cx - pond[0]) / (pond[2] + 20.0)) ** 2 + ((cy - pond[1]) / (pond[3] + 20.0)) ** 2 <= 1.0
