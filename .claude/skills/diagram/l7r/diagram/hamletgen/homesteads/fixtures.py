"""Split from hamletgen/homesteads.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_dist, segments_cross
from l7r.diagram.settlement._geom import boxed_ring_hit
from l7r.diagram.settlement._knobs import knob_rng
from l7r.diagram.settlement.farm_fixtures import FIXTURE_FT, PERSIMMON_CROWN_FT

from ..consts import Poly, Pt
from ..plan import SitePlan
from .bamboo import Footing, _strip_blocked

# FARMSTEAD FIXTURES (feature 133 T53-T59, GM 2026-08-27; research/homesteads.html "The farmstead's
# fixtures"). Each row: the kind, the per-hamlet PREVALENCE BAND (rolled once per map from the seed -
# two hamlets differ honestly where the record gives a range), and the seats tried in the house's
# local frame (+y = the sunny front where the yard is, -y = the back wall, -x = the kura side). The
# first seat is rolled where the record shows two forms; the rest are fallbacks. Every number is
# labeled in the research entry:
#   privy    READ  an independent outbuilding was "普通" (Nipponica) - near-universal; FOUR attested seats
#                  (research/homesteads/260, 269 B10): under the eaves by the stable, a separate outhouse in
#                  the yard, the front yard, inside the barn - rolled per house, the weights per hamlet
#   woodpile READ  a WOOD SHED of its own (research/homesteads/212 and 720, feature 280 M21): Hasuda 1824 ("many"
#                  houses), Kakimochi 6 of 16 households, commonly 4 x 2 ken - so about four farmsteads in ten, the
#                  larger houses first, 24 x 12 ft. The open stack under the eaves (a present-day page only) and the
#                  kizuma along the windbreak (undated modern pages only) are MODERN-ONLY and are not drawn
#                  (feature 280, 2026-09-29; the GM's ruling of 2026-09-28: "eliminate anything which is only modern")
#   manure   READ  in Han China the latrine stood over the pigsty (AIC) - muck and privy are one
#                  cluster; in Japan the pit stood "near the stable, under the eaves" (SUMMARY-ONLY);
#                  so the heap is seated beyond the privy; the share is a GUESS (Sugiura: a SHED on 0.24).
#                  The PIT form (night soil) has two attested seats (research/homesteads/260, 269 B11): beside
#                  the privy, or a field pit at a field edge or roadside - the field share rolled per hamlet
#   bath     READ  a ROOM JOINED TO THE MAIN HOUSE, not a shed (research/homesteads/740, feature 280 M22): the Nikko
#                  house-plan registers put a bath of 1-2 tsubo in 2-3 houses in 10 by 1824 and 1842, beside the main
#                  door or at the far end of the stable wing, and in a few (mostly headmen's) joined to the floored rooms;
#                  a bath as a building of its own is found only in the twentieth century (Sugiura's 0.29 sheds, the
#                  Tohoku reconstructions' 0-80%), so the shed is not drawn. The band is (0.20, 0.30); the seat a knob
#   coop     READ  "farmers in most regions of China managed to keep a pig and some chickens in their
#                  yard" (Animals through Chinese History); a ground-level enclosure (Qimin Yaoshu);
#                  Buck 1921-25 counts chickens on 82% of 2,866 farms, so the band is centered there
#                  (research/homesteads/215, 269 B13); its width is calibrated liberty
#   shrine   READ  two patterns - every house, or only certain old families (Tokushima; ja.wikipedia);
#                  the GM chose the rare pattern (T58); Sugiura's shrine column is 0.01 per household over all
#                  houses and empty among the pre-1944 ones (feature 211 re-read the table: the 0.03 once cited
#                  was a neighboring shed column) - the 0.03-0.08 band is the GM's ruling, above the paper's
#                  figure; corner NE (kimon, READ), NW
#                  (17 of 37, SUMMARY-ONLY), SW (Tokushima, READ) - rolled
#   persimmon READ "どこの庭先にも柿の木が植えてある" and Miyazaki Yasusada urged planting them round the
#                  homestead; two sides attested (research/homesteads/218, 269 B14): the dooryard in front, at the
#                  work yard's edge (the edge a GUESS), most often, or behind the house - rolled per house against a
#                  per-hamlet front share (`PERSIMMON_FRONT_BAND`); the flank, attested nowhere, is no longer a seat
#
# EVERY SHARE IS SEATED TO ITS COUNT (269 fc:2261): each kind's declared share of this hamlet's households is a COUNT,
# `round(share x houses)` (a spec floor may raise it), drawn on the houses whose positional
# roll is lowest; a house with no room passes its fixture to the next house that lacks one. Presence used to be the
# positional roll against the share, house by house, and the drawn counts missed the declared shares both ways
# (the H1 table: Kashikawa drew 8 heaps for a declared 0.442 of 20, Inashiro 12 heaps for 0.531 of 15).
FIXTURE_BANDS: dict[str, tuple[float, float]] = {
    "privy": (0.85, 0.95),
    "woodpile": (0.35, 0.45),  # a wood shed on about four farmsteads in ten (Kakimochi 6 of 16; research/homesteads/720)
    "manure": (0.40, 0.70),
    "bath": (0.20, 0.30),  # two or three houses in ten, 1824 and 1842 (research/homesteads/740); the old 0-0.80 was the twentieth century's sheds
    "coop": (0.72, 0.92),  # centered on Buck's 82% (research/homesteads/215); +/-0.10 is calibrated liberty, a GUESS
    "shrine": (0.03, 0.08),
    "persimmon": (0.80, 0.95),
}
_FIXTURE_ORDER = ("privy", "manure", "bath", "coop", "woodpile", "shrine", "persimmon")  # the buildings before the stack, which has the most seats
# THE FOUR ATTESTED PRIVY SEATS (269 B10, research/homesteads/260 "Where did the privy stand"): under the eaves by the
# stable beside the entrance (sinyoken), a separate outhouse in the yard (sinyoken), the front yard (Sugiura 1977, northern
# Miyagi, "usually"), and inside the barn (Suzuki 1959, "several farms"). The record says how often each is drawn is a
# GUESS, so these base weights are one, and each hamlet re-weights them (`privy_seat_weights`) - a degree along a
# continuum, rolled from the seed. Where in the yard the separate outhouse stands no page says: behind the house, a step
# off the wall, is a GUESS. A privy inside the barn is a tub under its floor, which a top-down map cannot show; it is
# drawn as the privy glyph against the barn's outer wall - a MAP DRAWING CONVENTION.
_PRIVY_SEATS = (("yard", 0.35), ("front", 0.30), ("stable", 0.20), ("barn", 0.15))
_PRIVY_WEIGHT_SPREAD = (0.5, 1.5)  # each base weight scaled by a factor in this range per hamlet, then renormalized (calibrated liberty)
_PRIVY_YARD_STEP_FT = 6.0  # the yard outhouse stands one ken off the back wall, so it reads as its own building (GUESS)
_PRIVY_FRONT_STEP_FT = 8.0  # the front-yard privy a step out from the front wall, at the yard's side (GUESS)
# THE NIGHT-SOIL PIT AT THE FIELDS (269 B11, research/homesteads/260): Suzuki 1959 found the pit "beside the privy, or in
# a field pit (nodame) away from the house" near the household's fields or the roadside, in 2 of 83 households (Saitama),
# 19 of 53 (Tokyo), 15 of 18 (Miyagi) - so the field share is rolled per hamlet across that span.
PIT_FIELD_SHARE_BAND = (0.02, 0.85)
PIT_FIELD_REACH_FT = 160.0  # how far from the house the field or road edge is looked for: the household's NEAREST paddy or road (GUESS)
_PIT_EDGE_CLEAR_FT = 8.0  # off the paddy's edge: the placer's 6 ft paddy margin plus two (the pit stands on the bund-side ground)
_PIT_CANDIDATES = 8  # the nearest edge points tried, nearest first
# THE BATH ROOM'S THREE SEATS (feature 280 M22, research/homesteads/740): joined to the main house beside its main door, at
# the far end of its stable wing (the house's -x end, where the doma and its stable are), or joined to its floored rooms (the
# +x end) - three attested places, so a KNOB rolled per hamlet between the two common ones; the third, "found in only a few
# houses, most of them headmen's", is the headman's seat. The odds are a GUESS. The room abuts the wall: joined, not beside.
BATH_SEATS = ("main_door", "stable_end")
BATH_DEPTH_FT = 6.0  # a room of 6 by 6 to 6 by 12 ft (1-2 tsubo, research/homesteads/740): one ken out from the wall ...
BATH_LENGTH_FT = (6.0, 12.0)  # ... and one to two ken along it, rolled per house (the spread a calibration on the registers' 1-2 tsubo)
# THE PRIVY'S SIZE (feature 280, research/homesteads/750): each homestead's privy is one of the sixteen of the Kakimochi table
# (Meiji 18, read back to the last years of the shogunate), frontage by depth in feet at 6 ft to the ken - each as likely as
# the next. A calibration against one village's table; the old 6 x 6 ft one-ken module was a GUESS.
PRIVY_SIZES_FT: tuple[tuple[float, float], ...] = (
    (27.0, 15.0),
    (6.0, 5.0),
    (12.0, 6.0),
    (18.0, 12.0),
    (15.0, 12.0),
    (15.0, 9.0),
    (24.0, 12.0),
    (24.0, 12.0),
    (5.0, 5.0),
    (24.0, 12.0),
    (18.0, 12.0),
    (15.0, 9.0),
    (9.0, 6.0),
    (24.0, 12.0),
    (24.0, 12.0),
    (6.0, 6.0),
)
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


def privy_sun_reach_ft(w_ft: float, d_ft: float) -> float:
    """How far from its house's center the sun-side search may seat a privy of `w_ft` x `d_ft`: `PRIVY_SUN_MAX_FT`, plus the
    half-length it has past the one-ken default, so its near edge stands no farther out than a one-ken privy's."""
    return PRIVY_SUN_MAX_FT + max(0.0, (max(w_ft, d_ft) - 6.0) / 2.0)


PRIVY_SUNNY_SHARE = 0.727  # the share of outhouses seated SE-to-S: Wang & Ochiai 2022 measured 72.7% in
# Arakawa village, and the GM (2026-08-29) ruled the figure be used literally rather than rounded. The
# reason the record gives is fermentation, not wind - see the note at the seat roll.
_SHRINE_CORNERS = (("NW", 0.45), ("NE", 0.35), ("SW", 0.20))
# each corner's direction in the world, y down: north is -y
_CORNER_SIGNS = {"NW": (-1.0, -1.0), "NE": (1.0, -1.0), "SW": (-1.0, 1.0)}


def shrine_corner_local(wx: float, wy: float, ca: float, sa: float) -> Pt:
    """A world offset (wx, wy) from the house center in the house's own frame, the inverse of the seat loop's
    `hx + lx * ca - ly * sa, hy + lx * sa + ly * ca`: the household shrine's corner is rolled by compass name."""
    return (wx * ca + wy * sa, -wx * sa + wy * ca)


# THE PERSIMMON'S SIDE (269 B14, research/homesteads/218): "the dooryard in front of the house, most often, and behind it" -
# the front the likelier, by how much no page says, so this hamlet's front share is rolled in this band (calibrated liberty).
PERSIMMON_FRONT_BAND = (0.60, 0.85)
_PERSIMMON_STEPS_FT = (10.0, 20.0)  # the same bearings a step out, and two, when the first ring is taken (feature 261)
_WOODSHED_STEP_FT = 6.0  # the wood shed stands one ken off the wall it serves, a building of its own (GUESS: where on the plot no page says)
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


def privy_seat_weights(seed: int) -> tuple[tuple[str, float], ...]:
    """This hamlet's weights over the four attested privy seats (269 B10): each base weight in `_PRIVY_SEATS` scaled by a
    factor rolled from the seed within `_PRIVY_WEIGHT_SPREAD`, then renormalized - two hamlets differ where the record
    gives the forms but not their frequency."""
    rng = knob_rng(seed, "privy_seats")
    lo, hi = _PRIVY_WEIGHT_SPREAD
    raw = [(k, w * (lo + rng.random() * (hi - lo))) for k, w in _PRIVY_SEATS]
    tot = sum(v for _k, v in raw)
    return tuple((k, round(v / tot, 3)) for k, v in raw)


def edge_index(field_rings: Sequence[Poly], lanes: Sequence[tuple[Poly, float]]) -> tuple[Any, list[tuple[Any, float]]]:
    """The paddy edges and road centerlines a field pit stands beside (269 B11), in ONE spatial index built once per pass:
    an STRtree over the rings and lanes as lines, each with the clearance its pit keeps (0 for a paddy - the caller adds
    its own - or the lane's keep-out half-width). Asked per house, never scanned."""
    from shapely import LineString, STRtree

    items: list[tuple[Any, float]] = [(LineString(list(r) + [r[0]]), 0.0) for r in field_rings if len(r) >= 3]
    items += [(LineString(pts), half) for pts, half in lanes if len(pts) >= 2]
    return STRtree([g for g, _h in items]), items


def field_edge_seats(index: tuple[Any, list[tuple[Any, float]]], hx: float, hy: float, reach: float, clear: float) -> list[tuple[float, float, bool]]:
    """World points for a field pit (269 B11): the nearest point of each paddy edge or road within `reach` of the house,
    stepped TOWARD the house by `clear` (plus a road's own keep-out), so the pit stands on the house's side of its field
    or road; nearest first, at most `_PIT_CANDIDATES`. Each carries whether its edge is a ROAD, so the pit is recorded
    as the seat it took - `roadside` or `field_edge` (settlement-review of Kuwabata at the 269 landing: two pits by the
    road were recorded as field-edge pits)."""
    from shapely import Point

    tree, items = index
    here = Point(hx, hy)
    out: list[tuple[float, tuple[float, float, bool]]] = []
    for i in tree.query(here, predicate="dwithin", distance=reach):
        line, half = items[int(i)]
        q = line.interpolate(line.project(here))
        dx, dy = hx - q.x, hy - q.y
        dist = math.hypot(dx, dy)
        if dist <= clear + half:  # the house itself stands within the pit's clearance - nothing to step out onto
            continue
        k = (clear + half) / dist
        out.append((dist, (q.x + dx * k, q.y + dy * k, half > 0.0)))
    out.sort()
    return [p for _d, p in out[:_PIT_CANDIDATES]]


def farmstead_fixtures(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]]) -> int:
    """Seat and draw the small fixtures of every farmstead. Returns the count placed.

    Seated in `stage_hinterland` (stage 11) after the web, like the household bamboo (T49): a fixture hugs
    its house and is tested against every placed footprint, lane, paddy, marsh and pond (`_strip_blocked`),
    so the web is never re-threaded and nothing is drawn on anything.

    THIS SENTENCE USED TO SAY "after the web and the board", AND THE BOARD IS STAGE 17 - four stages after
    this one (the GM read it on the generated page, 2026-09-12, and it is wrong in the one direction that
    matters: it claims this placer sees a feature it cannot). A docstring the page publishes is read by
    somebody, so it is worth the same accuracy as a comment beside a branch.

    AND THE ORDERING ITSELF IS QUESTIONED, by the GM in the same message: *"this farmstead fixtures
    placement is happening as part of the hinterlands stage, which does not make any sense to me. Our
    entire approach to homesteads is to place them and then determine what they have and then move on and
    place more homesteads. So why would we move on to the next homestead that we are placing if we have not
    placed all of the features on the previous homestead?"* The reason it is here is the lane web: a privy
    that hugs a wall must keep off a tread, and at homestead time no tread exists, so seating the fixtures
    early would mean either re-threading the web around them or drawing them on it. That is a REASON and not
    necessarily the right design - deciding a homestead's whole contents at the homestead, and letting the
    web thread around what is already there, is the other arrangement, and it is the one the rest of this
    package follows. Recorded as an open question rather than answered here, because the measurement that
    settles it is what the web does when the fixtures are already on the ground. Each kind's
    share is rolled once per map inside the band above and declared in meta, and seated as a COUNT (269 fc:2261):
    the houses whose positional roll (`_hjit`) is lowest, a house with no room passing its fixture on. Every seated fixture joins `s.placed`
    and `s.block_polys`, so the bamboo strips and the scrub keep off it."""
    if not houses:
        return 0
    rng = knob_rng(s.seed, "farm_fixtures")
    shares = {k: round(lo + rng.random() * (hi - lo), 3) for k, (lo, hi) in FIXTURE_BANDS.items()}
    s.M["meta"]["farm_fixtures"] = dict(shares)
    privy_weights = privy_seat_weights(s.seed)
    s.M["meta"]["privy_seats"] = dict(privy_weights)
    bath_seat = BATH_SEATS[knob_rng(s.seed, "bath_seat").randrange(len(BATH_SEATS))]  # the headman's is joined to his floored rooms
    s.M["meta"]["bath_seat"] = bath_seat
    pit_field_share = 0.0
    if plan.manure_form == "pit":
        _lo, _hi = PIT_FIELD_SHARE_BAND
        pit_field_share = round(_lo + knob_rng(s.seed, "pit_field_share").random() * (_hi - _lo), 3)
        s.M["meta"]["pit_field_share"] = pit_field_share
    mins = {k: int(v) for k, v in plan.fixtures_min.items() if k in FIXTURE_BANDS}
    if mins:
        s.M["meta"]["farm_fixtures_min"] = dict(mins)
    px = s.px
    g = px(_WALL_GAP_FT)
    fields = [list(f) for f in s.field_polys]
    marsh = [[(float(a), float(b)) for a, b in m["poly"]] for m in s.M.get("marshes", []) if m.get("poly")]
    pond = s.M.get("pond")
    lanes = [([(float(a), float(b)) for a, b in ln["pts"]], float(ln.get("w", 3)) / 2 + px(3.0)) for ln in s.M.get("lanes", []) if len(ln.get("pts") or []) >= 2]
    footing = Footing(s, fields, marsh)  # the static ground, indexed once per pass (feature 218)
    _dry = [[(float(a), float(b)) for a, b in o.get("poly") or []] for o in s.M.get("dry_plots", [])]
    edges = edge_index(fields + _dry, lanes) if pit_field_share > 0 else None  # the field pit's paddy, plot and road edges (269 B11)
    # THE HOMESTEAD BUNDLES ARE PACKING RESERVATIONS, NOT GROUND (feature 261, spec-fidelity of round 6fefdcdf): each is the
    # rectangle `_try_place_bundle` reserves round a whole steading, and its parts - the house, the yard, the gardens - are
    # registered one by one besides. Tested as a solid, a bundle offset by its gardens refused its own house's open flank, and a
    # neighbor's refused ground nothing stood on: Mizuguchi's farmstead at (1277,257) seated no coop and no stack. Skipped only
    # for the yard ring (below): skipped for every seat, the fixtures took the flanks first and the persimmons after them
    # lost their ground - on a trial roll of 2026-09-27, Inashiro drew 6 of its 12 persimmons (plan D19).
    bundles = frozenset(b for b in (homestead_box(s.placed, float(q["x"]), float(q["y"])) for q in houses) if b is not None)
    count = 0
    # THE COUNTS (269 fc:2261; see the note at FIXTURE_BANDS): each kind's share is seated as a count - the shrine's too, so
    # RARE stays rare (a 0.03-0.08 share of a dozen households is none or one); a spec floor may raise any count.
    n_h = len(houses)
    targets = {k: max(round(shares[k] * n_h), mins.get(k, 0)) for k in FIXTURE_BANDS}
    s.M["meta"]["farm_fixtures_target"] = dict(targets)
    chosen = {k: set(sorted(range(n_h), key=lambda i, _k=k: fixture_order_key(s, houses[i], _k))[: targets[k]]) for k in FIXTURE_BANDS}
    have = dict.fromkeys(FIXTURE_BANDS, 0)
    owned: set[tuple[str, int]] = set()
    privy_seat: dict[int, tuple[float, float]] = {}  # a house's privy, so a heap passed to it later still lies beyond it

    _flo, _fhi = PERSIMMON_FRONT_BAND
    persimmon_front = round(_flo + knob_rng(s.seed, "persimmon_front").random() * (_fhi - _flo), 3)
    s.M["meta"]["persimmon_front_share"] = persimmon_front

    # THE PASS THAT MAKES UP THE COUNT (T61's floor, GM 2026-08-27: "a min number of something which may or may not appear";
    # since 269 fc:2261 every count): after the rolled pass, any kind short of its count is offered to the houses that lack
    # it, in positional order, until the count is met or every house has been tried. A shrine with no seat used to pass to
    # the next house with room by a rule of its own (settlement-review of Mizuguchi, feature 261); this is that rule, general.
    _second = sorted(range(n_h), key=lambda i: s._hjit(float(houses[i]["x"]), float(houses[i]["y"]), 108.0))
    for i, force in [(i, False) for i in range(n_h)] + [(i, True) for i in _second]:
        if force and all(have[k] >= targets[k] for k in targets):
            break
        h = houses[i]
        hx, hy, hw, hh = float(h["x"]), float(h["y"]), float(h["w"]), float(h["h"])
        rot = float(h.get("rot", 0.0))
        th = math.radians(rot)
        ca, sa = math.cos(th), math.sin(th)
        shed_side = h.get("shed_side", "W")
        privy_at: tuple[float, float] | None = privy_seat.get(i)

        for kind in _FIXTURE_ORDER:
            if have[kind] >= targets[kind] or (kind, i) in owned or (not force and i not in chosen[kind]):
                continue
            u = s._hjit(hx, hy, _SALT[kind] + 0.5)
            if kind == "persimmon":
                r = px(PERSIMMON_CROWN_FT)
                # a raked house is a circumscribed SQUARE to the canopy keep-out (_canopy_keepouts mirrors
                # structures_clear_of_trees), so the trunk stands a half-diagonal + the crown out from the center
                reach = math.hypot(hw / 2, hh / 2) + r + s.CANOPY_PAD + 1.0
                # THE DOORYARD OR BEHIND THE HOUSE (269 B14, `persimmon_seats`): the side rolled against the hamlet's front
                # share, then the other side, then both a step out and two; the flank, attested nowhere, is not tried. A tree
                # that finds no seat is counted short at the end (feature 261: on Sawada one once vanished without a record).
                tseats = persimmon_seats(yard_local(h, hx, hy, ca, sa), reach, px(4.0) / 2 + 3.0, u < persimmon_front, [px(st) for st in _PERSIMMON_STEPS_FT])
                _planted = False
                for lx, ly in tseats:
                    cx, cy = hx + lx * ca - ly * sa, hy + lx * sa + ly * ca
                    # the TRUNK is tested against drawn footprints, not the plot reservations: a yard tree
                    # stands at a plot's edge, and in a nucleated cluster the reservations tile the ground
                    if _trunk_blocked(s, cx, cy, px(4.0), fields, marsh, pond, lanes, footing) or across_the_brook(s, (hx, hy), (cx, cy)) or across_a_lane(lanes, (hx, hy), (cx, cy)):
                        continue
                    # no tree on a roof: the SAME keep-outs and the same test the grove drawer uses, so
                    # structures_clear_of_trees (which mirrors them) cannot disagree with this seat
                    rects, circles = s._canopy_keepouts((cx - r - 40, cy - r - 40, cx + r + 40, cy + r + 40))
                    if s._crown_covers(cx, cy, r, rects, circles, pad=s.CANOPY_PAD):
                        continue
                    s.persimmon(cx, cy, of=(hx, hy))
                    s.placed.append((cx, cy, px(4.0), px(4.0)))
                    count += 1
                    have[kind] += 1
                    owned.add((kind, i))
                    break
                continue
            _ft = fixture_size_ft(s, kind, hx, hy)
            w, d = px(_ft[0]), px(_ft[1])  # along the wall, out from it
            field_table: list[tuple[float, float, float, float]] = []  # a field pit's seats (269 B11), tried first and never offset
            roadside: dict[int, bool] = {}  # which of them stands by a road rather than a field, keyed by the seat's id

            sun_table: list[tuple[float, float, float, float]] = []  # the privy's sun-side search, when rolled, tried first
            # THE ATTESTED SEATS INSIDE THE STEADING (269 B10; feature 280 M22): the privy's four seats and the bath room, tested past the
            # homestead BUNDLE boxes as the yard ring is. Tested against them - as every recorded seat was - the bundle, whose edges
            # are the house's own walls, refused every seat before or beside the house: measured on the first roll of this
            # change, no privy on the five pool maps took the front or stable seat and no front-yard bath stood in front.
            yard_lead: list[tuple[float, float, float, float]] = []
            bath_names: dict[int, str] = {}
            # candidate seats as (lx, ly, w_local, h_local); the fixture is drawn raked with the house
            if kind == "privy":
                seat = {  # the four attested seats (`_PRIVY_SEATS`); -x is the shed end of the house, where the doma and its stable are
                    "yard": (hw * 0.3, -(hh / 2 + g + px(_PRIVY_YARD_STEP_FT) + d / 2), w, d),
                    "front": (hw * 0.40, hh / 2 + g + px(_PRIVY_FRONT_STEP_FT) + d / 2, w, d),
                    "stable": (-hw * 0.35, hh / 2 + g + d / 2, w, d),
                    "barn": ((hw / 2 + g + d / 2), -hh * 0.25, d, w) if shed_side == "N" else (-(hw / 2 + hw * 0.32 + g + d / 2), -hh * 0.25, d, w),
                    # THE SUN SIDE, which the record documents and this seat table did not have (feature 152
                    # T07). The three seats above are all north or flank: measured on the pool before this
                    # change, every privy on every map sat at bearing 33-73 degrees from its house. The source
                    # the GM ruled on puts 72.7% of them SOUTHEAST to SOUTH, so a seat has to exist there.
                }
                first = _roll(privy_weights, u)
                seats = [seat[first]] + [seat[k] for k, _ in privy_weights if k != first]
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
                # ...THE RADIUS IS TO THE PRIVY'S CENTER, so a privy of a rolled size reaches the same NEAR EDGE as a one-ken
                # one: the reach grows by the half-length it has past 6 ft (settlement-review of Sawada, feature 280: every
                # privy of 18 x 12 ft or more fell through to the north-east seat, 7 of 17, the failure feature 152 fixed)
                for _r_ft in range(int(PRIVY_SUN_MIN_FT), int(privy_sun_reach_ft(w / px(1.0), d / px(1.0))) + 1, 4):
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
                sun_table = _sun if _u_dir < PRIVY_SUNNY_SHARE else []
                yard_lead = list(seats)
                seats = sun_table + seats
            elif kind == "manure":
                # THE FIELD PIT (269 B11): on a pit hamlet, a share of households keep the night soil out at the edge of the
                # nearest paddy or plot, or beside the road, rather than beside the privy. Those seats are tried first; the
                # privy-side ones below stay as the fallback, so a house with no field or road edge in reach keeps its pit.
                if edges is not None and s._hjit(hx, hy, 102.7) < pit_field_share:
                    for _fx, _fy, _road in field_edge_seats(edges, hx, hy, px(PIT_FIELD_REACH_FT), px(_PIT_EDGE_CLEAR_FT) + d / 2):
                        _ddx, _ddy = _fx - hx, _fy - hy
                        field_table.append((_ddx * ca + _ddy * sa, -_ddx * sa + _ddy * ca, w, d))
                        roadside[id(field_table[-1])] = _road
                if privy_at is not None:
                    plx, ply = privy_at
                    out_ = -1.0 if ply < 0 else 1.0
                    # BEYOND THE PRIVY, and with somewhere to go when that one spot is taken (feature 152
                    # T16). Three candidates seated 3 of a declared 8 per map: the heap is placed against
                    # the privy, and where the privy now sits on the sun side the ground just past it is
                    # often the work yard. The researched rule is only that the heap lies BEYOND the privy
                    # (research/homesteads.html) - which these all do; they differ in how far and how wide.
                    # ...AND NOT AT A FIXED OFFSET (feature 152 T17). Every heap sat the SAME distance
                    # beyond its privy - an acceptance review measured 15 of 19 pairs at |dy| 9.4-9.9 ft
                    # with |dx| under 1 ft - so the pair read as one stamp repeated down the row. The
                    # researched rule is only that the heap lies BEYOND the privy; how far beyond is ours,
                    # and real yards vary. Jittered off the homestead's own position so it is stable for a
                    # given farmstead and differs between them.
                    _pout = px(fixture_size_ft(s, "privy", hx, hy)[1]) / 2 + g + d / 2 + px(9.0) * (s._hjit(hx, hy, 102.4) - 0.5)
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
                    #     - the actual researched rule (research/homesteads.html) - fell from 16 of 16 to
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
                # THE WOOD SHED (feature 280 M21): the same walls, a ken further out - a building of its own
                _st = px(_WOODSHED_STEP_FT)
                seats = [(lx + math.copysign(_st, lx) * (abs(lx) > hw / 2), ly + math.copysign(_st, ly) * (abs(lx) <= hw / 2), cw, ch) for lx, ly, cw, ch in seats]
            elif kind == "bath":
                # THE BATH ROOM (feature 280 M22, `bath_room_seats`): joined to the house - against its wall, no gap - at the
                # hamlet's seat, then at the other attested seats; it is never a building standing off in the yard.
                _named = bath_room_seats("floored_rooms" if h.get("role") == "headman" else bath_seat, hw, hh, w, d)
                yard_lead = [q for q, _n in _named]
                bath_names = {id(q): _n for q, _n in zip(yard_lead, (_n for _q, _n in _named), strict=True)}
                seats = []
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
                # THE CORNER IS ROLLED BY COMPASS NAME, so it is laid out in the WORLD and carried into the house frame the
                # seat loop works in (settlement-review of Kashikawa at the 269 landing): laid out in the house frame, a
                # quarter-turned house swung every name 90 degrees - a roll of NE, the kimon corner, drew at world SE.
                ex, ey = abs(hw * ca) + abs(hh * sa), abs(hw * sa) + abs(hh * ca)
                corner = {k: shrine_corner_local(sx * (ex / 2 + off), sy * (ey / 2 + off), ca, sa) for k, (sx, sy) in _CORNER_SIGNS.items()}
                first = _roll(_SHRINE_CORNERS, u)
                seats = [(*corner[first], w, d)] + [(*corner[k], w, d) for k, _ in _SHRINE_CORNERS if k != first]
            # THE SEATS, THEN THE SAME SEATS FURTHER OUT - and a MISS IS RECORDED (settlement-review of
            # Kuwabata, 2026-09-12). This loop used to end without placing and without saying so when every
            # seat was blocked, which is how a map came to draw 6 privies for 16 farmhouses against its own
            # declared 0.851 share: a re-routed tread passed 5 and 8 ft from two steadings' privy seats, each
            # inside the lane keep-out, and both records simply did not appear. Nothing in the tree could see
            # it - the share is declared in `meta` and nothing compares the drawing to it.
            #
            # The outward rungs are STRICTLY ADDITIVE: a fixture that seats at its first choice never reaches
            # them, so no map moves except where a fixture was previously dropped. Three rungs, at the wall
            # gap again each time, which is how `clear_label_seat` and the board's own caption ladder ring
            # outward for the same reason - the crowded ground is exactly where the thing has to stand.
            _rungs = [(0.0, 0.0, seats)] + [(px(8.0) * _k, px(8.0) * _k, seats) for _k in (1, 2, 3)]
            # ...THEN THE REST OF ITS OWN YARD (feature 261, spec-fidelity of round 6fefdcdf): once a seat beyond a lane is refused
            # (`across_a_lane`), a farmstead whose lane runs close behind its back wall had no recorded seat left, and seven
            # coops, woodpiles, baths and heaps went unseated across the pool. The recorded seats keep their order and win
            # wherever they fit; only a fixture that fits none of them is offered the ring round the house's other walls, which is
            # still its own plot (a GUESS, labeled: the record places each fixture at a wall, not at which one when that is taken).
            if kind != "shrine":
                _ring = yard_ring(hw, hh, g, w, d)
                _rungs += [(px(8.0) * _k, px(8.0) * _k, _ring) for _k in (0, 1, 2, 3)]
                # ...and each seat straight out from its own wall (feature 261): the diagonal rungs move a front seat along the
                # wall as far as out, into the lane or the neighbor's bed at a crowded corner, while Mizuguchi's north-row
                # house had open ground straight out past its yard and seated no woodpile.
                _rungs += [(_o, 0.0, _ring) for _o in (px(8.0) * _k for _k in (1, 2, 3, 4))] + [(0.0, _o, _ring) for _o in (px(8.0) * _k for _k in (1, 2, 3, 4))]
            if kind == "bath":  # a room joined to the house has no seat out in the yard: no rung walks it away from the wall
                _rungs = []
            if kind == "woodpile":  # the shed stands a step off its wall: no rung walks it out across the dooryard (settlement-reviews of
                # Inashiro and Kuwabata, feature 280: 25-37 ft out, between farmsteads); a house with no room passes it on
                _rungs = [r for r in _rungs if max(abs(r[0]), abs(r[1])) <= px(8.0)]
            _lead: list[tuple[float, float, Sequence[tuple[float, ...]]]] = [(0.0, 0.0, _t) for _t in (field_table, sun_table, yard_lead) if _t]
            _rungs = _lead + _rungs
            _strict_ids = {id(seats), id(field_table), id(sun_table)}
            _seated = False
            for _ox, _oy, _table in _rungs:
                if _seated:
                    break
                for _seat in _table:
                    lx, ly, cw, ch = _seat[0], _seat[1], _seat[2], _seat[3]
                    lx = lx + (_ox if lx >= 0 else -_ox)
                    ly = ly + (_oy if ly >= 0 else -_oy)
                    cx, cy = hx + lx * ca - ly * sa, hy + lx * sa + ly * ca
                    ext = abs(cw * ca) + abs(ch * sa), abs(cw * sa) + abs(ch * ca)  # the drawn rect's bbox, raked with the house
                    if (
                        _strip_blocked(s, cx, cy, ext[0], ext[1], hx, hy, fields, marsh, pond, lanes, footing, frozenset() if id(_table) in _strict_ids else bundles)
                        or across_the_brook(s, (hx, hy), (cx, cy))
                        # a field pit stands out by its fields or the road, not in the yard, so a lane may run between (269 B11)
                        or (_table is not field_table and across_a_lane(lanes, (hx, hy), (cx, cy)))
                        # a household shrine stands in a corner of ITS OWN plot: a seat nearer another farmhouse reads as the
                        # neighbor's (the 269 landing's round-3 review of Inashiro: 25.9 ft from the next house, 44.3 from its
                        # own, among that yard's coop, heap and privy); the count loop passes it on to a house with room
                        or (kind == "shrine" and nearer_own_house((lx, ly, cw, ch), hx, hy, ca, sa, [(float(q["x"]), float(q["y"])) for q in houses if q is not h])[0] == 1)
                    ):
                        continue
                    spin = 90.0 if (cw, ch) == (d, w) and w != d else 0.0  # a flank seat turns the glyph to lie ALONG the wall (review at T99: stacks stood end-on)
                    s.farm_fixture(kind, cx, cy, rot=rot + spin, of=(hx, hy), form=fixture_form(kind, plan.manure_form), size_ft=_ft)
                    ring = [(cx - ext[0] / 2, cy - ext[1] / 2), (cx + ext[0] / 2, cy - ext[1] / 2), (cx + ext[0] / 2, cy + ext[1] / 2), (cx - ext[0] / 2, cy + ext[1] / 2)]
                    s.placed.append((cx, cy, ext[0], ext[1]))
                    s.block_polys.append(ring)
                    if _table is field_table:
                        s.M["farm_fixtures"][-1]["seat"] = "roadside" if roadside.get(id(_seat)) else "field_edge"
                    elif kind == "bath":
                        s.M["farm_fixtures"][-1]["seat"] = bath_names[id(_seat)]

                    if kind == "privy":
                        privy_at = privy_seat[i] = (lx, ly)
                    count += 1
                    have[kind] += 1
                    owned.add((kind, i))
                    _seated = True
                    break
            # THE SHORTFALL IS RECORDED, so a drawing that departs from its own declared count cannot ship unremarked again:
    # `meta.farm_fixtures_unseated` is what a reader and a check compare against `meta.farm_fixtures_target`. A silent drop
    # is the thing that made the Kuwabata defect invisible (settlement-review, 2026-09-12). Counted once, after every house
    # has been offered the fixture, rather than per refused seat - a refusal passed on and taken is no shortfall.
    short = {k: targets[k] - have[k] for k in targets if have[k] < targets[k]}
    if short:
        s.M["meta"]["farm_fixtures_unseated"] = short
    s.M["meta"]["bath_seats_drawn"] = dict(sorted(Counter(str(r.get("seat")) for r in s.M.get("farm_fixtures", []) if r.get("kind") == "bath").items()))
    return count


def fixture_order_key(s: Settlement, h: Mapping[str, Any], kind: str) -> tuple[float, float]:
    """Which houses take a kind's count first (269 fc:2261): the positional roll, lowest first - except the WOOD SHED, which
    goes to the larger houses first (research/homesteads/720: "the storehouse and the sheds go to the larger houses first"),
    the roll breaking ties among houses of one size."""
    roll = s._hjit(float(h["x"]), float(h["y"]), _SALT[kind])
    if kind == "woodpile":
        return (-float(h["w"]) * float(h["h"]), roll)
    return (0.0, roll)


def fixture_size_ft(s: Settlement, kind: str, hx: float, hy: float) -> tuple[float, float]:
    """A fixture's size in real feet, (along its wall, out from it): the privy one of the Kakimochi table's sixteen and the
    bath room 6 ft out by 6-12 ft along, each rolled off the house's own position (feature 280, research/homesteads/750 and
    740); every other kind its one size in `FIXTURE_FT`."""
    if kind == "privy":
        return PRIVY_SIZES_FT[int(s._hjit(hx, hy, 101.3) * len(PRIVY_SIZES_FT)) % len(PRIVY_SIZES_FT)]
    if kind == "bath":
        lo, hi = BATH_LENGTH_FT
        return (round(lo + (hi - lo) * s._hjit(hx, hy, 104.3)), BATH_DEPTH_FT)
    return FIXTURE_FT[kind]


def bath_room_seats(first: str, hw: float, hh: float, w: float, d: float) -> list[tuple[tuple[float, float, float, float], str]]:
    """The bath room's seats in the house frame (feature 280 M22, research/homesteads/740), `first` tried first then the
    other attested seats: beside the MAIN DOOR (the front wall, either side of the door at its middle), at the far end of
    the STABLE WING (the -x end wall, where the doma and its stable are), or joined to the FLOORED ROOMS (the +x end wall).
    Each abuts its wall - a room of the house, not a building beside it. Each seat carries its name, which the record keeps.
    Beside the main door the front wall comes first, then the end walls' front corners - the work yard lies before the front
    wall, and on Kuwabata no bath room found room there (settlement-review, feature 280: the seat was declared, never drawn)."""
    front, side = hh / 2 + d / 2, hw / 2 + d / 2
    table = {
        "main_door": [(hw * 0.22 + w / 2, front, w, d), (-(hw * 0.22 + w / 2), front, w, d), (side, hh / 2 - w / 2, d, w), (-side, hh / 2 - w / 2, d, w)],
        "stable_end": [(-side, 0.0, d, w), (-side, -hh * 0.25, d, w), (-side, hh * 0.25, d, w)],
        "floored_rooms": [(side, 0.0, d, w), (side, -hh * 0.25, d, w), (side, hh * 0.25, d, w)],
    }
    return [(q, first) for q in table[first]] + [(q, k) for k, v in table.items() if k != first for q in v]


def yard_local(h: Mapping[str, Any], hx: float, hy: float, ca: float, sa: float) -> tuple[float, float, float, float] | None:
    """This steading's threshing yard (`geom.yard`) in its house's own frame, as (center x, center y, width, depth); None
    for a house that recorded no yard."""
    yard = (h.get("geom") or {}).get("yard")
    if not yard:
        return None
    dx, dy = float(yard[0]) - hx, float(yard[1]) - hy
    return (dx * ca + dy * sa, -dx * sa + dy * ca, float(yard[2]), float(yard[3]))


def persimmon_seats(yard: tuple[float, float, float, float] | None, reach: float, trunk: float, front_first: bool, steps: Sequence[float]) -> list[Pt]:
    """A yard persimmon's trunk seats in its house's frame (269 B14, research/homesteads/218): the DOORYARD in front - first
    at the work yard's two side edges, level with its middle and its outer edge (`trunk` clear of it), then the front
    corners and straight out - or BEHIND the house, its back corners and straight out; `front_first` says which side is
    tried first. Then both sides again at each of `steps` further out. `reach` is the trunk's distance from the house center
    that keeps the crown off the roof. The flank is attested nowhere and is not a seat."""
    front = [(sx * reach * 0.75, reach * 0.75) for sx in (1.0, -1.0)] + [(0.0, reach)]
    back = [(sx * reach * 0.75, -reach * 0.75) for sx in (1.0, -1.0)] + [(0.0, -reach)]
    edge: list[Pt] = []
    if yard is not None:
        ylx, yly, yw, yh = yard
        edge = [(ylx + sx * (yw / 2 + trunk), yly + oy) for oy in (0.0, yh / 2) for sx in (1.0, -1.0)]
    ring = front + back if front_first else back + front
    seats = (edge + ring) if front_first else (ring + edge)
    return seats + [(lx * (reach + st) / reach, ly * (reach + st) / reach) for st in steps for lx, ly in ring]


def fixture_form(kind: str, manure_form: str | None) -> str | None:
    """The attested form a fixture is drawn in: the manure PIT on a pit hamlet (feature 150); None for the plain glyph."""
    if kind == "manure":
        return "pit" if manure_form == "pit" else None
    return None


def homestead_box(placed: Sequence[Any], x: float, y: float) -> tuple[float, float, float, float] | None:
    """The largest reserved box (`cx, cy, w, h`) holding the house center - the steading's whole footprint."""
    boxes = [(float(b[0]), float(b[1]), float(b[2]), float(b[3])) for b in placed if abs(x - b[0]) <= b[2] / 2 and abs(y - b[1]) <= b[3] / 2]
    return max(boxes, key=lambda b: b[2] * b[3]) if boxes else None


def across_the_brook(s: Settlement, house: Pt, seat: Pt) -> bool:
    """Would this fixture stand across a stream from the house it serves (feature 261 FR-013)? The same rule, and the
    same guess, as `Settlement._parts_across_stream` for the homestead's own parts: the line from the house to the
    seat crosses no reach of any stream. Mizuguchi drew a privy and a persimmon on the far bank of the brook that runs
    past their house's door."""
    return any(segments_cross(house, seat, poly[k], poly[k + 1]) for f in s.M.get("streams", []) for poly in (f.get("poly") or [],) for k in range(len(poly) - 1))


def yard_ring(hw: float, hh: float, g: float, w: float, d: float) -> list[tuple[float, float, float, float]]:
    """The seats round a house's walls in its own frame (`lx, ly, along x, along y`), a wall gap out: the back wall at
    its middle and ends, each flank at three heights, and the front corners - the last resort of a fixture every
    recorded seat of which is refused (`farmstead_fixtures`). A seat on the back or front wall lies along it (`w, d`),
    a flank seat turned to lie along its flank (`d, w`)."""
    back, front, side = -(hh / 2 + g + d / 2), hh / 2 + g + d / 2, hw / 2 + g + d / 2
    ring = [(0.0, back, w, d), (-hw * 0.35, back, w, d), (hw * 0.35, back, w, d)]
    ring += [(sx * side, fy * hh, d, w) for fy in (-0.3, 0.0, 0.3) for sx in (-1.0, 1.0)]
    return ring + [(-hw * 0.35, front, w, d), (hw * 0.35, front, w, d)]


def across_a_lane(lanes: Sequence[tuple[Poly, float]], house: Pt, seat: Pt) -> bool:
    """Would a lane run between this fixture and the house it serves (settlement-review of Mizuguchi, feature 261)? A
    shrine stands "in a corner of the house plot" and a coop in the yard (research/homesteads.html), and a shared lane
    between the house and the seat puts the seat outside the plot: Mizuguchi drew a household's coop, woodpile and the
    map's one shrine 10-13 ft beyond the lane that carries the west rows past its back wall. The same line test as
    `across_the_brook`, against the lanes' centerlines."""
    return any(segments_cross(house, seat, pts[k], pts[k + 1]) for pts, _half in lanes for k in range(len(pts) - 1))


def _trunk_blocked(
    s: Settlement, cx: float, cy: float, t: float, fields: Sequence[Poly], marsh: Sequence[Poly], pond: Any, lanes: Sequence[tuple[Poly, float]], footing: Footing | None = None
) -> bool:
    """Would a tree trunk (a t x t box) stand on a drawn footprint, a lane, a paddy, the marsh or the pond?"""
    if cx - t < 30 or cy - t < 30 or cx + t > s.W - 30 or cy + t > s.H - 30:
        return True
    ft = footing or Footing(s, fields, marsh)  # (feature 218) see `Footing`
    for key in ("houses", "farm_sheds", "retirement_houses", "gardens", "threshing_yards", "byres", "wells", "kosatsuba", "farm_fixtures", "persimmons", "bamboo_stands"):
        for o in s.M.get(key, []):
            if "x" not in o:
                continue
            ow, oh = float(o.get("w", 2 * float(o.get("r", 8)))), float(o.get("h", 2 * float(o.get("r", 8))))
            if abs(cx - float(o["x"])) < (t + ow) / 2 + 2 and abs(cy - float(o["y"])) < (t + oh) / 2 + 2:
                return True
    corners = [(cx - t / 2, cy - t / 2), (cx + t / 2, cy - t / 2), (cx + t / 2, cy + t / 2), (cx - t / 2, cy + t / 2)]
    if any(boxed_ring_hit(q[0], q[1], ft.rings.near(q[0], q[1]), 6.0) for q in corners):  # a paddy or the marsh, inside or within 6 ft
        return True
    for pts, half in lanes:
        if any(seg_dist(q[0], q[1], pts[k], pts[k + 1]) < half for q in corners for k in range(len(pts) - 1)):
            return True
    if any(boxed_ring_hit(q[0], q[1], ft.dry.near(q[0], q[1])) for q in corners):  # standing IN a dry plot (no margin here, as before)
        return True
    if any(ft.on_water(s, q[0], q[1]) for q in corners):
        return True
    return bool(pond) and ((cx - pond[0]) / (pond[2] + 20.0)) ** 2 + ((cy - pond[1]) / (pond[3] + 20.0)) ** 2 <= 1.0
