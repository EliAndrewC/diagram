"""What stands in a farmstead's yard: the privy, the wood shed, the manure heap, the bath room, the coop, the household
shrine and the yard persimmon - rolled per hamlet, kept per household, drawn where the seating laid them.

Split from hamletgen/homesteads.py by feature 173 - see this package's CLAUDE.md for the index. Since feature 287 (homes
H32, plan M5 and D9) the fixtures are PARTS of the homestead: the hamlet's shares and forms are rolled here and handed to
the seating (`fixture_quota`, `fixture_forms`), each household's lot keeps its kinds (`rolling/lot.py`), the bundle lays
them beside the house (`settlement/homestead_parts/fixture_seats.py`), and `farmstead_fixtures` draws them where they
were laid - so every rolled fixture is drawn and none is recorded short. Feature 280 eliminated the modern-only forms:
the bath is a room of the house, the firewood a wood shed of its own (the eaves stack and the kizuma are gone), and the
privy and the bath room take a size rolled per household.

Research: fixture drawing plumbing - NONE: indexes, records and drawing what was laid; the units that decide carry their own claims
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, rot_rect, segments_cross
from l7r.diagram.settlement._geom.water_index import crosses_a_stream
from l7r.diagram.settlement._knobs import knob_rng
from l7r.diagram.settlement.homestead_parts.fixture_seats import (
    BATH_DEPTH_FT as BATH_DEPTH_FT,
)
from l7r.diagram.settlement.homestead_parts.fixture_seats import (
    BATH_LENGTH_FT as BATH_LENGTH_FT,
)
from l7r.diagram.settlement.homestead_parts.fixture_seats import (
    PRIVY_SIZES_FT as PRIVY_SIZES_FT,
)
from l7r.diagram.settlement.homestead_parts.fixture_seats import (
    PRIVY_SUN_MAX_FT as PRIVY_SUN_MAX_FT,
)
from l7r.diagram.settlement.homestead_parts.fixture_seats import (
    PRIVY_SUN_MIN_FT as PRIVY_SUN_MIN_FT,
)
from l7r.diagram.settlement.homestead_parts.fixture_seats import (
    PRIVY_SUNNY_SHARE as PRIVY_SUNNY_SHARE,
)
from l7r.diagram.settlement.homestead_parts.fixture_seats import (
    FixtureForms,
    fixture_size,
    weighted,
)
from l7r.diagram.settlement.homestead_parts.fixture_seats import (
    bath_room_seats as bath_room_seats,
)
from l7r.diagram.settlement.homestead_parts.fixture_seats import (
    privy_sun_reach_ft as privy_sun_reach_ft,
)
from l7r.diagram.settlement.land.wet import marsh_ground

from ..consts import Poly, Pt
from ..plan import SitePlan
from .bamboo import Footing, _strip_blocked
from .holds import release_held
from .retirement import RETIREMENT_FT, RETIREMENT_GAP_FT

# FARMSTEAD FIXTURES (feature 133 T53-T59, GM 2026-08-27; research/questions/0045-chickens-and-chicken-coops.html). Each row: the kind, the per-hamlet PREVALENCE BAND (rolled once per map from the seed -
# two hamlets differ honestly where the record gives a range), and the seats tried in the house's
# local frame (+y = the sunny front where the yard is, -y = the back wall, -x = the kura side). The
# first seat is rolled where the record shows two forms; the rest are fallbacks. Every number is
# labeled in the research entry:
#   privy    READ  an independent outbuilding was "普通" (Nipponica) - near-universal; FOUR attested seats
#                  (research/questions/0047-farm-privies-and-their-night-soil-benjo.html, 269 B10): under the eaves by the stable, a separate outhouse in
#                  the yard, the front yard, inside the barn - rolled per house, the weights per hamlet; its size
#                  one of the Kakimochi table's sixteen (research/questions/0047-farm-privies-and-their-night-soil-benjo.html, feature 280)
#   woodpile READ  a WOOD SHED of its own (research/questions/0043-firewood-stacks-and-sheds-kigoya.html and 720, feature 280 M21): Hasuda 1824 ("many"
#                  houses), Kakimochi 6 of 16 households, commonly 4 x 2 ken - so about four farmsteads in ten, the
#                  larger houses first, 24 x 12 ft. The open stack under the eaves (a present-day page only) and the
#                  kizuma along the windbreak (undated modern pages only) are MODERN-ONLY and are not drawn
#                  (feature 280, 2026-09-29; the GM's ruling of 2026-09-28: "eliminate anything which is only modern")
#   manure   READ  in Han China the latrine stood over the pigsty (AIC) - muck and privy are one
#                  cluster; in Japan the pit stood "near the stable, under the eaves" (SUMMARY-ONLY);
#                  so the heap is seated beyond the privy; the share is a GUESS (Sugiura: a SHED on 0.24).
#                  The PIT form (night soil) has two attested seats (research/questions/0047-farm-privies-and-their-night-soil-benjo.html, 269 B11): beside
#                  the privy, or a field pit at a field edge or roadside - the field share rolled per hamlet
#   bath     READ  a ROOM JOINED TO THE MAIN HOUSE, not a shed (research/homesteads/740, feature 280 M22): the Nikko
#                  house-plan registers put a bath of 1-2 tsubo in 2-3 houses in 10 by 1824 and 1842, beside the main
#                  door or at the far end of the stable wing, and in a few (mostly headmen's) joined to the floored rooms;
#                  a bath as a building of its own is found only in the twentieth century (Sugiura's 0.29 sheds, the
#                  Tohoku reconstructions' 0-80%), so the shed is not drawn. The band is (0.20, 0.30); the seat a knob
#   coop     READ  "farmers in most regions of China managed to keep a pig and some chickens in their
#                  yard" (Animals through Chinese History); a ground-level enclosure (Qimin Yaoshu);
#                  Buck 1921-25 counts chickens on 82% of 2,866 farms, so the band is centered there
#                  (research/questions/0045-chickens-and-chicken-coops.html, 269 B13); its width is calibrated liberty
#   shrine   READ  two patterns - every house, or only certain old families (Tokushima; ja.wikipedia);
#                  the GM chose the rare pattern (T58); Sugiura's shrine column is 0.01 per household over all
#                  houses and empty among the pre-1944 ones (feature 211 re-read the table: the 0.03 once cited
#                  was a neighboring shed column) - the 0.03-0.08 band is the GM's ruling, above the paper's
#                  figure; corner NE (kimon, READ), NW
#                  (17 of 37, SUMMARY-ONLY), SW (Tokushima, READ) - rolled
#   persimmon READ "どこの庭先にも柿の木が植えてある" and Miyazaki Yasusada urged planting them round the
#                  homestead; two sides attested (research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.html, 269 B14): the dooryard in front, at the
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
    "coop": (0.72, 0.92),  # centered on Buck's 82% (research/questions/0045-chickens-and-chicken-coops.html); +/-0.10 is calibrated liberty, a GUESS
    "shrine": (0.03, 0.08),
    "persimmon": (0.80, 0.95),
}
"""Each fixture kind's per-hamlet share band.

Research:
    privy share - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: 0.85-0.95
    wood shed share - research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: 0.35-0.45
    manure heap share - research/questions/0042-manure-heaps-and-compost-kyuhi.drawing.html: 0.40-0.70
    bath room share - research/questions/0044-baths-on-the-farm-furo.drawing.html: 0.20-0.30
    coop share - research/questions/0045-chickens-and-chicken-coops.drawing.html: 0.72-0.92
    household shrine share - research/questions/0219-household-shrines-yashikigami.drawing.html: 0.03-0.08
    persimmon share - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: 0.80-0.95
"""
# THE FOUR ATTESTED PRIVY SEATS (269 B10, research/questions/0047-farm-privies-and-their-night-soil-benjo.html "Farm privies and their night soil (benjo)"): under the eaves by the
# stable beside the entrance (sinyoken), a separate outhouse in the yard (sinyoken), the front yard (Sugiura 1977, northern
# Miyagi, "usually"), and inside the barn (Suzuki 1959, "several farms"). The record says how often each is drawn is a
# GUESS, so these base weights are one, and each hamlet re-weights them (`privy_seat_weights`) - a degree along a
# continuum, rolled from the seed. Where in the yard the separate outhouse stands no page says: behind the house, a step
# off the wall, is a GUESS. A privy inside the barn is a tub under its floor, which a top-down map cannot show; it is
# drawn as the privy glyph against the barn's outer wall - a MAP DRAWING CONVENTION.
_PRIVY_SEATS = (("yard", 0.35), ("front", 0.30), ("stable", 0.20), ("barn", 0.15))
"""Research: four privy seats - research/questions/0047-farm-privies-and-their-night-soil-benjo.html, research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: yard 35, front 30, stable 20, barn 15 in 100"""
_PRIVY_WEIGHT_SPREAD = (0.5, 1.5)  # each base weight scaled by a factor in this range per hamlet, then renormalized (calibrated liberty)
"""Research: privy weights per hamlet - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: each base weight scaled 0.5-1.5"""
# THE NIGHT-SOIL PIT AT THE FIELDS (269 B11, research/questions/0047-farm-privies-and-their-night-soil-benjo.html): Suzuki 1959 found the pit "beside the privy, or in
# a field pit (nodame) away from the house" near the household's fields or the roadside, in 2 of 83 households (Saitama),
# 19 of 53 (Tokyo), 15 of 18 (Miyagi) - so the field share is rolled per hamlet across that span.
PIT_FIELD_SHARE_BAND = (0.02, 0.85)
"""Research: field pit share - research/questions/0047-farm-privies-and-their-night-soil-benjo.html, research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: 0.02-0.85 rolled per hamlet"""
PIT_FIELD_REACH_FT = 160.0  # how far from the house the field or road edge is looked for: the household's NEAREST paddy or road (GUESS)
"""Research: field pit reach - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: the nearest paddy or road within 160 ft"""
_PIT_EDGE_CLEAR_FT = 8.0  # off the paddy's edge: the placer's 6 ft paddy margin plus two (the pit stands on the bund-side ground)
"""Research: pit off the paddy edge - UNRESEARCHED: 8 ft"""
_PIT_CANDIDATES = 8  # the nearest edge points tried, nearest first
# THE BATH ROOM'S THREE SEATS (feature 280 M22, research/homesteads/740): joined to the main house beside its main door, at
# the far end of its stable wing (the house's -x end, where the doma and its stable are), or joined to its floored rooms (the
# +x end) - three attested places, so a KNOB rolled per hamlet between the two common ones; the third, "found in only a few
# houses, most of them headmen's", is the last wall offered (the headman keeps no lot of fixtures, feature 287). The odds are
# a GUESS. The room abuts the wall: joined, not beside (`fixture_seats.bath_room_seats`, `joined_to_house`).
BATH_SEATS = ("main_door", "stable_end")
"""Research: bath room wall - research/questions/0044-baths-on-the-farm-furo.html, research/questions/0044-baths-on-the-farm-furo.drawing.html: the main door or the stable end, rolled per hamlet"""
# THE PERSIMMON'S SIDE (269 B14, research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.html): "the dooryard in front of the house, most often, and behind it" -
# the front the likelier, by how much no page says, so this hamlet's front share is rolled in this band (calibrated liberty).
PERSIMMON_FRONT_BAND = (0.60, 0.85)
"""Research: persimmon in front - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: the front share 0.60-0.85 per hamlet"""


_roll = weighted  # the weighted roll the seat tables read (`fixture_seats.weighted`), under its old name


def privy_seat_weights(seed: int) -> tuple[tuple[str, float], ...]:
    """This hamlet's weights over the four attested privy seats (269 B10): each base weight in `_PRIVY_SEATS` scaled by a
    factor rolled from the seed within `_PRIVY_WEIGHT_SPREAD`, then renormalized - two hamlets differ where the record
    gives the forms but not their frequency.

    Research: privy seat weights - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: rolled once per hamlet, renormalized
    """
    rng = knob_rng(seed, "privy_seats")
    lo, hi = _PRIVY_WEIGHT_SPREAD
    raw = [(k, w * (lo + rng.random() * (hi - lo))) for k, w in _PRIVY_SEATS]
    tot = sum(v for _k, v in raw)
    return tuple((k, round(v / tot, 3)) for k, v in raw)


def fixture_shares(seed: int) -> dict[str, float]:
    """This hamlet's share of households keeping each fixture kind, rolled once inside its band (`FIXTURE_BANDS`).

    Research: shares rolled per hamlet - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html: once per map inside each kind's band
    """
    rng = knob_rng(seed, "farm_fixtures")
    return {k: round(lo + rng.random() * (hi - lo), 3) for k, (lo, hi) in FIXTURE_BANDS.items()}


def fixture_quota(seed: int, households: int, mins: Mapping[str, int]) -> dict[str, float]:
    """The share each kind's household quota is drawn at (feature 287, homes H32): the rolled share, raised where a spec
    floor asks more (`fixtures_min`) - so exactly `max(round(share x n), floor)` of `n` households keep it.

    Research: count to the share - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html, research/questions/0219-household-shrines-yashikigami.drawing.html: exactly the share's count, raised to a spec's floor
    """
    n = max(1, households)
    return {k: max(p, float(mins.get(k, 0)) / n) for k, p in fixture_shares(seed).items()}


def fixture_forms(seed: int, manure_form: str) -> FixtureForms:
    """The hamlet's fixture forms, rolled once from the seed: the privy seats' weights (269 B10), the bath room's wall
    (feature 280 M22), the persimmon's front share (B14) and the manure's form (the plan's knob). The woodpile has one form
    left, the wood shed (feature 280 M21), so it rolls none.

    Research:
        privy seats - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: this hamlet's weights
        bath room wall - research/questions/0044-baths-on-the-farm-furo.drawing.html: one of two walls at even odds
        persimmon side - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: this hamlet's front share
    """
    lo, hi = PERSIMMON_FRONT_BAND
    return FixtureForms(
        privy_weights=privy_seat_weights(seed),
        bath_seat=BATH_SEATS[knob_rng(seed, "bath_seat").randrange(len(BATH_SEATS))],
        persimmon_front=round(lo + knob_rng(seed, "persimmon_front").random() * (hi - lo), 3),
        manure_form=manure_form,
        retirement_ft=RETIREMENT_FT,
        retirement_gaps=RETIREMENT_GAP_FT,
    )


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
    road were recorded as field-edge pits).

    Research: pit at the field or road edge - research/questions/0047-farm-privies-and-their-night-soil-benjo.html, research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: the nearest edge points, on the house's side
    """
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


def farmstead_fixtures(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]], early: bool = False) -> int:
    """Draw every farmstead fixture where the seating laid it (feature 287, homes H32, plan M5 and D9). Returns the count
    drawn by this call.

    THE GM'S DESIGN, NOW THE PIPELINE'S (2026-09-12, on the page this docstring publishes): *"Our entire approach to
    homesteads is to place them and then determine what they have and then move on and place more homesteads. So why would
    we move on to the next homestead that we are placing if we have not placed all of the features on the previous
    homestead?"* The fixtures used to be seated here, at the hinterland stage after the web, in whatever ground was left -
    and a fixture with no seat was recorded short (`meta.farm_fixtures_unseated`: Kuwabata drew 3 of its 15 woodpiles once
    the eaves stack had to stand against a wall). Each household's lot now keeps its kinds, a quota per kind by seat order
    (exactly `max(round(share x n), floor)`), and the bundle lays them beside the house as its parts, inside the envelope
    that admitted the household (`settlement/homestead_parts/fixture_seats.py`). Nothing is sought here, so nothing can fall
    short; the web is laid after, round what already stands.

    TWO CALLS. `early` (from `stage_appurtenances`, after the byres): the hamlet's rolls declared, and every laid fixture
    drawn but the one whose attested form reads ground the web lays later - a night-soil pit at the household's field or
    road (269 B11). The later call (the hinterland stage's) offers it that seat first and draws the laid seat where it has
    none - the record's own alternative, the pit beside the privy. A call with no early call before it makes both.

    Research: field pit, else beside the privy - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: the field seat sought after the web, the laid seat its fallback
    """
    if not houses:
        return 0
    meta = s.M["meta"]
    count = 0
    if "farm_fixtures_target" not in meta:
        count += _draw_laid(s, plan, houses)
    if early:
        return count
    pending = getattr(s, "_fixtures_pending", None) or []
    s._fixtures_pending = []  # type: ignore[attr-defined]
    count += _draw_pending(s, plan, houses, pending)
    record_drawn_forms(s.M)
    return count


def _draw_laid(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]]) -> int:
    """Declare the hamlet's fixture rolls and draw every fixture the seating laid, holding back the flexible form.

    Research: which pits go to the field - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: on a pit hamlet, each house's position hash against the rolled field share
    """
    forms = getattr(s, "_fixture_forms", None) or fixture_forms(s.seed, plan.manure_form)
    meta = s.M["meta"]
    shares = fixture_shares(s.seed)
    meta["farm_fixtures"] = dict(shares)
    meta["privy_seats"] = dict(forms.privy_weights)
    meta["bath_seat"] = forms.bath_seat
    meta["persimmon_front_share"] = forms.persimmon_front
    pit_field_share = 0.0
    if plan.manure_form == "pit":
        _lo, _hi = PIT_FIELD_SHARE_BAND
        pit_field_share = round(_lo + knob_rng(s.seed, "pit_field_share").random() * (_hi - _lo), 3)
        meta["pit_field_share"] = pit_field_share
    mins = {k: int(v) for k, v in plan.fixtures_min.items() if k in FIXTURE_BANDS}
    if mins:
        meta["farm_fixtures_min"] = dict(mins)
    n_h = len(houses)
    # the lots' own count (`quota_carriers`: floor(n x p + 0.5), a half rounded up - not Python's round, which rounds a half
    # to even and so declared 10 privies where the lots, rightly, laid 11)
    meta["farm_fixtures_target"] = {k: max(math.floor(shares[k] * n_h + 0.5), mins.get(k, 0)) for k in FIXTURE_BANDS}
    # ...A ROLLED TREE A HOUSEHOLD COULD NOT KEEP, KEPT BY ONE THAT CAN (feature 315, B10): the roll is honored by what is drawn
    from .persimmon_reseat import reseat_persimmons

    reseat_persimmons(s, houses, int(meta["farm_fixtures_target"].get("persimmon", 0)), forms)  # type: ignore[arg-type]
    pending: list[tuple[Mapping[str, Any], dict[str, Any], dict[str, Any] | None]] = []
    count = 0
    for h in houses:
        laid = {f["kind"]: f for f in h.get("fixtures") or ()}
        hx, hy = float(h["x"]), float(h["y"])
        for kind in ("privy", "manure", "bath", "coop", "woodpile", "shrine", "persimmon"):
            f = laid.get(kind)
            if f is None:
                continue
            if kind == "manure" and pit_field_share > 0.0 and s._hjit(hx, hy, 102.7) < pit_field_share:
                pending.append((h, f, None))
                continue
            draw_laid_fixture(s, h, f, forms)
            count += 1
    s._fixtures_pending = pending  # type: ignore[attr-defined]
    return count


def draw_laid_fixture(s: Settlement, h: Mapping[str, Any], f: Mapping[str, Any], forms: FixtureForms, form: str | None = None) -> None:
    """Draw one fixture where the seating laid it: its glyph raked with its house at the size it was laid at (`ft`, rolled
    per household for the privy and the bath room - feature 280), turned along a flank where it was laid along one, its box
    reserved (`s.placed`, `s.block_polys`) so the bamboo and the scrub keep off it; a bath room records the wall it took."""
    hx, hy, rot = float(h["x"]), float(h["y"]), float(h.get("rot", 0.0))
    kind = str(f["kind"])
    x, y = float(f["x"]), float(f["y"])
    bx = f["box"]
    release_held(s, "farm_fixtures", f)
    if kind == "persimmon":
        s.persimmon(x, y, of=(hx, hy))
        s.placed.append((x, y, s.px(4.0), s.px(4.0)))
        return
    ft = (float(f["ft"][0]), float(f["ft"][1])) if f.get("ft") and form is None else None
    w, d = (s.px(ft[0]), s.px(ft[1])) if ft is not None else fixture_size(kind, forms, s.px)
    spin = 90.0 if abs(float(f["w"]) - d) < 1e-6 and abs(float(f["h"]) - w) < 1e-6 and abs(w - d) > 1e-6 else 0.0  # laid along a flank
    s.farm_fixture(kind, x, y, rot=rot + spin, of=(hx, hy), form=form if form is not None else fixture_form(kind, forms.manure_form), size_ft=ft)
    if kind == "bath" and f.get("seat"):
        s.M["farm_fixtures"][-1]["seat"] = f["seat"]
    s.placed.append((float(bx[0]), float(bx[1]), float(bx[2]), float(bx[3])))
    s.block_polys.append(_ring(bx))


def _ring(b: Sequence[float]) -> list[Pt]:
    x, y, w, h = float(b[0]), float(b[1]), float(b[2]), float(b[3])
    return [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)]


def _draw_pending(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]], pending: Sequence[tuple[Mapping[str, Any], dict[str, Any], Any]]) -> int:
    """The flexible form, now the web is laid: a pit at the household's nearest field or road (269 B11) - clear of every
    drawn footprint, lane, paddy, marsh and the pond, on the house's bank - else the seat laid for it.

    Research:
        a lane between pit and house allowed - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: the pit stands at the field or road, the laid seat where none is clear
        field pit size - UNRESEARCHED: drawn 3.5 ft square
    """
    if not pending:
        return 0
    forms = getattr(s, "_fixture_forms", None) or fixture_forms(s.seed, plan.manure_form)
    px = s.px
    fields = [list(f) for f in s.field_polys]
    marsh = marsh_ground(s.M)
    pond = s.M.get("pond")
    lanes = [([(float(a), float(b)) for a, b in ln["pts"]], float(ln.get("w", 3)) / 2 + px(3.0)) for ln in s.M.get("lanes", []) if len(ln.get("pts") or []) >= 2]
    footing = Footing(s, fields, marsh)
    _dry = [[(float(a), float(b)) for a, b in o.get("poly") or []] for o in s.M.get("dry_plots", [])]
    edges = edge_index(fields + _dry, lanes)
    count = 0
    for h, f, _c in pending:
        hx, hy, rot = float(h["x"]), float(h["y"]), float(h.get("rot", 0.0))
        release_held(s, "farm_fixtures", f)  # its laid seat stood held through the web; the form's own seat is sought now
        # the night-soil pit at the household's field or road (269 B11), a lane between it and the house allowed
        d = px(3.5)
        spot = next(
            (
                (x, y, road)
                for x, y, road in field_edge_seats(edges, hx, hy, px(PIT_FIELD_REACH_FT), px(_PIT_EDGE_CLEAR_FT) + d / 2)
                if _flexible_clear(s, h, (x, y), (d, d), fields, marsh, pond, lanes, footing)
                and not under_a_lane(s.M, (x, y, d, d, rot))
                and s.admits("farm_fixtures", {"x": round(x, 1), "y": round(y, 1), "w": d, "h": d, "rot": rot, "of": [round(hx, 1), round(hy, 1)]})
            ),
            None,
        )
        if spot is not None:
            s.farm_fixture("manure", spot[0], spot[1], rot=rot, of=(hx, hy), form="pit")
            s.M["farm_fixtures"][-1]["seat"] = "roadside" if spot[2] else "field_edge"
            s.placed.append((spot[0], spot[1], d, d))
            s.block_polys.append(_ring((spot[0], spot[1], d, d)))
        else:
            draw_laid_fixture(s, h, f, forms)
        count += 1
    return count


def under_a_lane(M: Mapping[str, Any], fixture: tuple[float, float, float, float, float]) -> bool:
    """Would a fixture drawn at `(x, y, w, h, rot)` stand under a lane's tread - the web's own test of a lane over a fixture
    (`law.over_a_fixture`, the ONE predicate the finished-map rule reads)? The flexible form is seated after the web, so
    the web cannot route round it; a seat under lane ink is refused and the next offered, and the laid seat - which the web
    was routed round - is the fallback (feature 287, ways: 8 pool and cohort maps ended with a woodpile or a heap under a lane)."""
    from ..ways.law import lane_pts, over_a_fixture

    quad = rot_rect(*fixture)
    return any(over_a_fixture(lane_pts(ln), float(ln.get("w") or 3.0), [quad]) is not None for ln in M.get("lanes") or [] if len(ln.get("pts") or ()) >= 2)


def _flexible_clear(s: Settlement, h: Mapping[str, Any], q: Pt, ext: tuple[float, float], fields: Any, marsh: Any, pond: Any, lanes: Any, footing: Footing) -> bool:
    """May the field pit stand at `q`: off every drawn footprint and the ground (`_strip_blocked`), on its house's bank. A
    lane between it and the house is allowed - it stands at the field or the road (the kizuma, which kept to its yard's side
    of every lane, went with feature 280's modern-only forms).

    Research:
        pit on its house's bank - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: no brook between pit and house
        pit off every grove - UNRESEARCHED: clear of every farm's grove band
    """
    hx, hy = float(h["x"]), float(h["y"])
    if _strip_blocked(s, q[0], q[1], ext[0], ext[1], hx, hy, fields, marsh, pond, lanes, footing):
        return False
    # ...nor in any farm's grove band (feature 291 on 287: `grove_rules.fixtures_on_groves`, the same boxes)
    if any(
        abs(q[0] - float(g["x"])) < (ext[0] + float(g["w"])) / 2 and abs(q[1] - float(g["y"])) < (ext[1] + float(g["h"])) / 2
        for g in s.M.get("groves") or ()
        if all(k in g for k in ("x", "y", "w", "h"))
    ):
        return False
    return not across_the_brook(s, (hx, hy), q)


def record_drawn_forms(m: dict[str, Any]) -> None:
    """Beside the rolled bath-seat knob, what the sheet DRAWS: the bath rooms by the wall each took (feature 280: the
    reviews of Kuwabata and Sawada found a declared `main_door` never drawn, so the record says which seat each took)."""
    m["meta"]["bath_seats_drawn"] = dict(sorted(Counter(str(r.get("seat")) for r in m.get("farm_fixtures") or [] if r.get("kind") == "bath").items()))


def fixture_form(kind: str, manure_form: str | None) -> str | None:
    """The attested form a fixture is drawn in: the manure PIT on a pit hamlet (feature 150); None for the plain glyph."""
    if kind == "manure":
        return "pit" if manure_form == "pit" else None
    return None


def across_the_brook(s: Settlement, house: Pt, seat: Pt) -> bool:
    """Would this fixture stand across a stream from the house it serves (feature 261 FR-013)? The same rule, and the
    same guess, as `Settlement._parts_across_stream` for the homestead's own parts: the line from the house to the
    seat crosses no reach of any stream. The body is `crosses_a_stream`, the one predicate the homestead's own parts and
    the finished-map test read too (feature 287, FR-003).

    Research: a farmstead whole on one bank - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the line from house to fixture crosses no reach of a stream
    """
    return crosses_a_stream(house, seat, s.M.get("streams", []))


def across_a_lane(lanes: Sequence[tuple[Poly, float]], house: Pt, seat: Pt) -> bool:
    """Would a lane run between this fixture and the house it serves (settlement-review of Mizuguchi, feature 261)? A
    shrine stands "in a corner of the house plot" and a coop in the yard (research/contents.json#homesteads), and a shared lane
    between the house and the seat puts the seat outside the plot. The same line test as `across_the_brook`, against the
    lanes' centerlines - the predicate the web asks of a run between a house and its own fixtures (homes H32).

    Research: fixtures inside the plot - research/questions/0219-household-shrines-yashikigami.html, research/questions/0045-chickens-and-chicken-coops.html: no shared lane between a house and its fixture
    """
    return any(segments_cross(house, seat, pts[k], pts[k + 1]) for pts, _half in lanes for k in range(len(pts) - 1))
