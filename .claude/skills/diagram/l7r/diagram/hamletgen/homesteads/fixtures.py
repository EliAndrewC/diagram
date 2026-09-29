"""What stands in a farmstead's yard: the privy, the woodpile, the manure heap, the bath, the coop, the household shrine
and the yard persimmon - rolled per hamlet, kept per household, drawn where the seating laid them.

Split from hamletgen/homesteads.py by feature 173 - see this package's CLAUDE.md for the index. Since feature 287 (homes
H32, plan M5 and D9) the fixtures are PARTS of the homestead: the hamlet's shares and forms are rolled here and handed to
the seating (`fixture_quota`, `fixture_forms`), each household's lot keeps its kinds (`rolling/lot.py`), the bundle lays
them beside the house (`settlement/homestead_parts/fixture_seats.py`), and `farmstead_fixtures` draws them where they
were laid - so every rolled fixture is drawn and none is recorded short.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, rot_rect, segments_cross
from l7r.diagram.settlement._geom.water_index import crosses_a_stream
from l7r.diagram.settlement._knobs import knob_rng
from l7r.diagram.settlement.farm_fixtures import WOODPILE_FORM_FT
from l7r.diagram.settlement.homestead_parts.fixture_seats import (
    BATH_CORRIDOR_FT as BATH_CORRIDOR_FT,
)
from l7r.diagram.settlement.homestead_parts.fixture_seats import (
    BATH_CORRIDOR_W_FT as BATH_CORRIDOR_W_FT,
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
    against_a_wall as against_a_wall,
)
from l7r.diagram.settlement.homestead_parts.fixture_seats import (
    steading_rects as steading_rects,
)
from l7r.diagram.settlement.land.wet import marsh_ground

from ..consts import Poly, Pt
from ..plan import SitePlan
from .bamboo import Footing, _strip_blocked
from .holds import release_held
from .retirement import RETIREMENT_FT, RETIREMENT_GAP_FT

# FARMSTEAD FIXTURES (feature 133 T53-T59, GM 2026-08-27; research/homesteads.html "The farmstead's
# fixtures"). Each row: the kind, the per-hamlet PREVALENCE BAND (rolled once per map from the seed -
# two hamlets differ honestly where the record gives a range), and the seats tried in the house's
# local frame (+y = the sunny front where the yard is, -y = the back wall, -x = the kura side). The
# first seat is rolled where the record shows two forms; the rest are fallbacks. Every number is
# labeled in the research entry:
#   privy    READ  an independent outbuilding was "普通" (Nipponica) - near-universal; FOUR attested seats
#                  (research/homesteads/260, 269 B10): under the eaves by the stable, a separate outhouse in
#                  the yard, the front yard, inside the barn - rolled per house, the weights per hamlet
#   woodpile READ  three forms (research/homesteads/212, 269 B15): a woodshed (Boso-no-Mura; the Shonai plain),
#                  a KIZUMA stacked along the inside of the windbreak on its windward side (the Isawa plain), and
#                  the open stack against the house wall (the GUESS) - a knob rolled per hamlet (`WOODPILE_FORMS`);
#                  the kizuma only where the homestead has the windbreak at its back, else the eaves stack.
#                  Sugiura counts 0.76 SHEDS per household (a mean count, so an upper bound on the share of
#                  households owning one - feature 211); the stack's wall is a GUESS (the back wall or the kura's)
#   manure   READ  in Han China the latrine stood over the pigsty (AIC) - muck and privy are one
#                  cluster; in Japan the pit stood "near the stable, under the eaves" (SUMMARY-ONLY);
#                  so the heap is seated beyond the privy; the share is a GUESS (Sugiura: a SHED on 0.24).
#                  The PIT form (night soil) has two attested seats (research/homesteads/260, 269 B11): beside
#                  the privy, or a field pit at a field edge or roadside - the field share rolled per hamlet
#   bath     READ  the goemon-buro "was used widely in self-sufficient farm villages" (Mizumaki); Sugiura:
#                  a bath SHED on 0.29, IN the house on 0.53 - two forms, so only the shed share is drawn.
#                  The shed share ran 0-80% by village (Sugiura 1977: Tono 80%, Inawashiro 33%, Shiokawa
#                  none), so the band is (0.0, 0.80); seated in the FRONT YARD or joined to the house by a
#                  CORRIDOR - two forms, a knob (research/homesteads/214, 269 B12)
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
    "woodpile": (0.75, 0.95),
    "manure": (0.40, 0.70),
    "bath": (0.0, 0.80),  # none to four farms in five: Shiokawa 0%, Inawashiro 33%, Tono 80% (research/homesteads/214)
    "coop": (0.72, 0.92),  # centered on Buck's 82% (research/homesteads/215); +/-0.10 is calibrated liberty, a GUESS
    "shrine": (0.03, 0.08),
    "persimmon": (0.80, 0.95),
}
# THE FOUR ATTESTED PRIVY SEATS (269 B10, research/homesteads/260 "Where did the privy stand"): under the eaves by the
# stable beside the entrance (sinyoken), a separate outhouse in the yard (sinyoken), the front yard (Sugiura 1977, northern
# Miyagi, "usually"), and inside the barn (Suzuki 1959, "several farms"). The record says how often each is drawn is a
# GUESS, so these base weights are one, and each hamlet re-weights them (`privy_seat_weights`) - a degree along a
# continuum, rolled from the seed. Where in the yard the separate outhouse stands no page says: behind the house, a step
# off the wall, is a GUESS. A privy inside the barn is a tub under its floor, which a top-down map cannot show; it is
# drawn as the privy glyph against the barn's outer wall - a MAP DRAWING CONVENTION.
_PRIVY_SEATS = (("yard", 0.35), ("front", 0.30), ("stable", 0.20), ("barn", 0.15))
_PRIVY_WEIGHT_SPREAD = (0.5, 1.5)  # each base weight scaled by a factor in this range per hamlet, then renormalized (calibrated liberty)
# THE NIGHT-SOIL PIT AT THE FIELDS (269 B11, research/homesteads/260): Suzuki 1959 found the pit "beside the privy, or in
# a field pit (nodame) away from the house" near the household's fields or the roadside, in 2 of 83 households (Saitama),
# 19 of 53 (Tokyo), 15 of 18 (Miyagi) - so the field share is rolled per hamlet across that span.
PIT_FIELD_SHARE_BAND = (0.02, 0.85)
PIT_FIELD_REACH_FT = 160.0  # how far from the house the field or road edge is looked for: the household's NEAREST paddy or road (GUESS)
_PIT_EDGE_CLEAR_FT = 8.0  # off the paddy's edge: the placer's 6 ft paddy margin plus two (the pit stands on the bund-side ground)
_PIT_CANDIDATES = 8  # the nearest edge points tried, nearest first
# THE BATH SHED'S TWO SEATS (269 B12, research/homesteads/214): the front yard (Sugiura 1977, northern Miyagi) or joined to
# the house by a short corridor (the Meiji housing-improvement interview) - two forms, a KNOB rolled per hamlet at even odds
# (the odds a GUESS). The back wall or a flank is only the fallback, a GUESS.
BATH_SEATS = ("front_yard", "corridor")
# THE PERSIMMON'S SIDE (269 B14, research/homesteads/218): "the dooryard in front of the house, most often, and behind it" -
# the front the likelier, by how much no page says, so this hamlet's front share is rolled in this band (calibrated liberty).
PERSIMMON_FRONT_BAND = (0.60, 0.85)
# THE WOODPILE'S FORM (269 B15, research/homesteads/212): "the woodpile's form is a knob ... the weights are a guess" - so even.
WOODPILE_FORMS = ("shed", "kizuma", "eaves")
# THE KIZUMA NEEDS THE HOMESTEAD'S OWN WINDBREAK: the belt counts as this homestead's when its inner edge is within this
# reach of the house wall and lies to windward - within 67.5 degrees of the wind's bearing, the windward octant and half of
# each neighbor. Both are GUESSES: the Isawa plain's windbreak stood "on its northwest side" of every homestead; a hamlet's one
# belt is only the homestead's where it stands at that yard's back, not across the cluster.
KIZUMA_REACH_FT = 40.0
_KIZUMA_WINDWARD_COS = math.cos(math.radians(67.5))
_KIZUMA_GAP_FT = 1.0  # stepped this far out of the belt's line toward the house, so the stack stands at its edge
_WIND_VEC = {k: (math.sin(math.radians(b)), -math.cos(math.radians(b))) for k, b in (("N", 0), ("NE", 45), ("E", 90), ("SE", 135), ("S", 180), ("SW", 225), ("W", 270), ("NW", 315))}
_WALL_GAP_FT = 3.5  # the review measured -0.3 ft at 3.0 against the drawn wall; half a foot of true daylight


_roll = weighted  # the weighted roll the seat tables read (`fixture_seats.weighted`), under its old name


def privy_seat_weights(seed: int) -> tuple[tuple[str, float], ...]:
    """This hamlet's weights over the four attested privy seats (269 B10): each base weight in `_PRIVY_SEATS` scaled by a
    factor rolled from the seed within `_PRIVY_WEIGHT_SPREAD`, then renormalized - two hamlets differ where the record
    gives the forms but not their frequency."""
    rng = knob_rng(seed, "privy_seats")
    lo, hi = _PRIVY_WEIGHT_SPREAD
    raw = [(k, w * (lo + rng.random() * (hi - lo))) for k, w in _PRIVY_SEATS]
    tot = sum(v for _k, v in raw)
    return tuple((k, round(v / tot, 3)) for k, v in raw)


def fixture_shares(seed: int) -> dict[str, float]:
    """This hamlet's share of households keeping each fixture kind, rolled once inside its band (`FIXTURE_BANDS`)."""
    rng = knob_rng(seed, "farm_fixtures")
    return {k: round(lo + rng.random() * (hi - lo), 3) for k, (lo, hi) in FIXTURE_BANDS.items()}


def fixture_quota(seed: int, households: int, mins: Mapping[str, int]) -> dict[str, float]:
    """The share each kind's household quota is drawn at (feature 287, homes H32): the rolled share, raised where a spec
    floor asks more (`fixtures_min`) - so exactly `max(round(share x n), floor)` of `n` households keep it."""
    n = max(1, households)
    return {k: max(p, float(mins.get(k, 0)) / n) for k, p in fixture_shares(seed).items()}


def fixture_forms(seed: int, manure_form: str) -> FixtureForms:
    """The hamlet's fixture forms, rolled once from the seed: the privy seats' weights (269 B10), the bath's seat (B12),
    the woodpile's form (B15), the persimmon's front share (B14) and the manure's form (the plan's knob)."""
    lo, hi = PERSIMMON_FRONT_BAND
    return FixtureForms(
        privy_weights=privy_seat_weights(seed),
        bath_seat=BATH_SEATS[knob_rng(seed, "bath_seat").randrange(len(BATH_SEATS))],
        woodpile_form=WOODPILE_FORMS[knob_rng(seed, "woodpile_form").randrange(len(WOODPILE_FORMS))],
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
    drawn but the two whose attested form reads ground the web and the belt lay later - a kizuma along the windbreak
    (269 B15) and a night-soil pit at the household's field or road (269 B11). The later call (the hinterland stage's)
    offers those their own form first and draws the laid seat where it has none - the record's own alternative in each
    case, the eaves stack and the pit beside the privy. A call with no early call before it makes both."""
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
    """Declare the hamlet's fixture rolls and draw every fixture the seating laid, holding back the flexible forms."""
    forms = getattr(s, "_fixture_forms", None) or fixture_forms(s.seed, plan.manure_form)
    meta = s.M["meta"]
    shares = fixture_shares(s.seed)
    meta["farm_fixtures"] = dict(shares)
    meta["privy_seats"] = dict(forms.privy_weights)
    meta["bath_seat"] = forms.bath_seat
    meta["woodpile_form"] = forms.woodpile_form
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
    pending: list[tuple[Mapping[str, Any], dict[str, Any], dict[str, Any] | None]] = []
    count = 0
    for h in houses:
        laid = {f["kind"]: f for f in h.get("fixtures") or ()}
        hx, hy = float(h["x"]), float(h["y"])
        for kind in ("privy", "manure", "bath", "coop", "woodpile", "shrine", "persimmon"):
            f = laid.get(kind)
            if f is None:
                continue
            flexible = (kind == "woodpile" and forms.woodpile_form == "kizuma") or (kind == "manure" and pit_field_share > 0.0 and s._hjit(hx, hy, 102.7) < pit_field_share)
            if flexible:
                pending.append((h, f, None))
                continue
            draw_laid_fixture(s, h, f, forms, laid.get("bath_corridor") if kind == "bath" else None)
            count += 1
    s._fixtures_pending = pending  # type: ignore[attr-defined]
    return count


def draw_laid_fixture(s: Settlement, h: Mapping[str, Any], f: Mapping[str, Any], forms: FixtureForms, corridor: Mapping[str, Any] | None = None, form: str | None = None) -> None:
    """Draw one fixture where the seating laid it: its glyph raked with its house, turned along a flank where it was laid
    along one, its box reserved (`s.placed`, `s.block_polys`) so the bamboo and the scrub keep off it; a joined bath's
    corridor with it."""
    hx, hy, rot = float(h["x"]), float(h["y"]), float(h.get("rot", 0.0))
    kind = str(f["kind"])
    x, y = float(f["x"]), float(f["y"])
    bx = f["box"]
    release_held(s, "farm_fixtures", f)
    if kind == "persimmon":
        s.persimmon(x, y, of=(hx, hy))
        s.placed.append((x, y, s.px(4.0), s.px(4.0)))
        return
    w, d = fixture_size(kind, forms, s.px)
    spin = 90.0 if abs(float(f["w"]) - d) < 1e-6 and abs(float(f["h"]) - w) < 1e-6 and abs(w - d) > 1e-6 else 0.0  # laid along a flank
    s.farm_fixture(kind, x, y, rot=rot + spin, of=(hx, hy), form=form if form is not None else fixture_form(kind, forms.manure_form, forms.woodpile_form, False))
    s.placed.append((float(bx[0]), float(bx[1]), float(bx[2]), float(bx[3])))
    s.block_polys.append(_ring(bx))
    if corridor is not None:
        cb = corridor["box"]
        _corridor(s, (float(corridor["x"]), float(corridor["y"]), float(corridor["w"]), float(corridor["h"]), float(cb[2]), float(cb[3])), rot, s.M["farm_fixtures"][-1])


def _ring(b: Sequence[float]) -> list[Pt]:
    x, y, w, h = float(b[0]), float(b[1]), float(b[2]), float(b[3])
    return [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)]


def _draw_pending(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]], pending: Sequence[tuple[Mapping[str, Any], dict[str, Any], Any]]) -> int:
    """The flexible forms, now the web and the belt are laid: a kizuma along the windbreak where it is this homestead's
    (269 B15), a pit at the household's nearest field or road (269 B11) - each clear of every drawn footprint, lane,
    paddy, marsh and the pond, on the house's bank, with no lane between it and the house - else the seat laid for it."""
    if not pending:
        return 0
    forms = getattr(s, "_fixture_forms", None) or fixture_forms(s.seed, plan.manure_form)
    px = s.px
    fields = [list(f) for f in s.field_polys]
    marsh = marsh_ground(s.M)
    pond = s.M.get("pond")
    lanes = [([(float(a), float(b)) for a, b in ln["pts"]], float(ln.get("w", 3)) / 2 + px(3.0)) for ln in s.M.get("lanes", []) if len(ln.get("pts") or []) >= 2]
    footing = Footing(s, fields, marsh)
    belt_line = belt_edge(plan.belt) if forms.woodpile_form == "kizuma" and len(plan.belt) >= 3 else None
    wind = _WIND_VEC.get(s._windward(), _WIND_VEC["NW"])
    _dry = [[(float(a), float(b)) for a, b in o.get("poly") or []] for o in s.M.get("dry_plots", [])]
    edges = edge_index(fields + _dry, lanes) if any(f["kind"] == "manure" for _h, f, _c in pending) else None
    count = 0
    for h, f, _c in pending:
        hx, hy, rot = float(h["x"]), float(h["y"]), float(h.get("rot", 0.0))
        release_held(s, "farm_fixtures", f)  # its laid seat stood held through the web; the form's own seat is sought now
        if f["kind"] == "woodpile":
            kw, kd = px(WOODPILE_FORM_FT["kizuma"][0]), px(WOODPILE_FORM_FT["kizuma"][1])
            reach = math.hypot(float(h["w"]) / 2, float(h["h"]) / 2) + px(KIZUMA_REACH_FT)
            seats = kizuma_seats(belt_line, hx, hy, reach, wind, kw, kd / 2 + px(_KIZUMA_GAP_FT)) if belt_line is not None else []
            spot = next(
                (
                    (x, y, a)
                    for x, y, a in seats
                    if _flexible_clear(s, h, (x, y), _turned_ext(kw, kd, a), fields, marsh, pond, lanes, footing, lane_between=True)
                    and not under_a_lane(s.M, (x, y, kw, kd, a))
                    and s.admits("farm_fixtures", {"x": round(x, 1), "y": round(y, 1), "w": kw, "h": kd, "rot": a, "of": [round(hx, 1), round(hy, 1)]})
                ),
                None,
            )
            if spot is not None:
                s.farm_fixture("woodpile", spot[0], spot[1], rot=spot[2], of=(hx, hy), form="kizuma")
                ext = _turned_ext(kw, kd, spot[2])
                s.placed.append((spot[0], spot[1], ext[0], ext[1]))
                s.block_polys.append(_ring((spot[0], spot[1], ext[0], ext[1])))
            else:
                draw_laid_fixture(s, h, f, forms)
        else:  # the night-soil pit at the household's field or road (269 B11), a lane between it and the house allowed
            d = px(3.5)
            assert edges is not None  # noqa: S101 - built when a pit is pending
            spot2 = next(
                (
                    (x, y, road)
                    for x, y, road in field_edge_seats(edges, hx, hy, px(PIT_FIELD_REACH_FT), px(_PIT_EDGE_CLEAR_FT) + d / 2)
                    if _flexible_clear(s, h, (x, y), (d, d), fields, marsh, pond, lanes, footing, lane_between=False)
                    and not under_a_lane(s.M, (x, y, d, d, rot))
                    and s.admits("farm_fixtures", {"x": round(x, 1), "y": round(y, 1), "w": d, "h": d, "rot": rot, "of": [round(hx, 1), round(hy, 1)]})
                ),
                None,
            )
            if spot2 is not None:
                s.farm_fixture("manure", spot2[0], spot2[1], rot=rot, of=(hx, hy), form="pit")
                s.M["farm_fixtures"][-1]["seat"] = "roadside" if spot2[2] else "field_edge"
                s.placed.append((spot2[0], spot2[1], d, d))
                s.block_polys.append(_ring((spot2[0], spot2[1], d, d)))
            else:
                draw_laid_fixture(s, h, f, forms)
        count += 1
    return count


def under_a_lane(M: Mapping[str, Any], fixture: tuple[float, float, float, float, float]) -> bool:
    """Would a fixture drawn at `(x, y, w, h, rot)` stand under a lane's tread - the web's own test of a lane over a fixture
    (`law.over_a_fixture`, the ONE predicate the finished-map rule reads)? The flexible forms are seated after the web, so
    the web cannot route round them; a seat under lane ink is refused and the next offered, and the laid seat - which the web
    was routed round - is the fallback (feature 287, ways: 8 pool and cohort maps ended with a woodpile or a heap under a lane)."""
    from ..ways.law import lane_pts, over_a_fixture

    quad = rot_rect(*fixture)
    return any(over_a_fixture(lane_pts(ln), float(ln.get("w") or 3.0), [quad]) is not None for ln in M.get("lanes") or [] if len(ln.get("pts") or ()) >= 2)


def _turned_ext(w: float, d: float, bearing: float) -> tuple[float, float]:
    c, sn = abs(math.cos(math.radians(bearing))), abs(math.sin(math.radians(bearing)))
    return w * c + d * sn, w * sn + d * c


def _flexible_clear(s: Settlement, h: Mapping[str, Any], q: Pt, ext: tuple[float, float], fields: Any, marsh: Any, pond: Any, lanes: Any, footing: Footing, lane_between: bool) -> bool:
    """May a flexible form stand at `q`: off every drawn footprint and the ground (`_strip_blocked`), on its house's bank,
    and - for a fixture of the yard - with no lane between it and the house (`across_a_lane`)."""
    hx, hy = float(h["x"]), float(h["y"])
    if _strip_blocked(s, q[0], q[1], ext[0], ext[1], hx, hy, fields, marsh, pond, lanes, footing):
        return False
    if across_the_brook(s, (hx, hy), q):
        return False
    return not (lane_between and across_a_lane(lanes, (hx, hy), q))


def record_drawn_forms(m: dict[str, Any]) -> None:
    """Beside each rolled form knob, what the sheet DRAWS: the woodpiles by form and the baths by seat. A knob names the
    hamlet's form; a homestead with no seat for it falls back (no belt within reach for a kizuma), and the
    settlement-reviews at the 269 landing found Kuwabata declaring kizuma with fifteen eaves stacks drawn and Mizuguchi
    declaring corridor baths with none - a declaration the drawing did not bear out."""
    rows = m.get("farm_fixtures") or []
    piles = [str(r.get("form") or "eaves") for r in rows if r.get("kind") == "woodpile"]
    baths = ["corridor" if r.get("corridor") else "unjoined" for r in rows if r.get("kind") == "bath"]
    m["meta"]["woodpile_forms_drawn"] = {f: piles.count(f) for f in sorted(set(piles))}
    m["meta"]["bath_seats_drawn"] = {f: baths.count(f) for f in sorted(set(baths))}


def woodpile_form_for(knob: str, kizuma_seats_found: bool) -> str:
    """The woodpile form a homestead draws (feature 287, homes H33): the kizuma only where the knob rolled it and the
    windbreak stands within the kizuma reach behind this homestead (research/homesteads/260: the kizuma only with the
    windbreak at the homestead's back), else the eaves stack - the record's own alternative; the woodshed where rolled."""
    if knob == "kizuma":
        return "kizuma" if kizuma_seats_found else "eaves"
    return knob


def fixture_form(kind: str, manure_form: str | None, woodpile_form: str, kizuma: bool) -> str | None:
    """The attested form a fixture is drawn in: the manure PIT on a pit hamlet (feature 150); the WOODSHED on a shed hamlet,
    or the KIZUMA where one was seated along the windbreak (269 B15); None for the plain glyph (the eaves stack included)."""
    if kind == "manure":
        return "pit" if manure_form == "pit" else None
    if kind == "woodpile":
        return "kizuma" if kizuma else ("shed" if woodpile_form == "shed" else None)
    return None


def belt_edge(belt: Sequence[Pt]) -> Any:
    """The windbreak belt's outline as one line (269 B15), built once per pass - the kizuma stands along it."""
    from shapely import LineString

    return LineString([*belt, belt[0]])


def kizuma_seats(line: Any, hx: float, hy: float, reach: float, wind: Pt, length: float, step: float) -> list[tuple[float, float, float]]:
    """World seats `(x, y, bearing in degrees)` for a KIZUMA (269 B15, research/homesteads/212): the firewood "stacked along
    the windbreak" on the homestead's windward side. The belt's edge point nearest the house, and a stack's length along the
    edge either way, each kept only when it is within `reach` of the house center and to windward of it (within 67.5 degrees
    of `wind`, the unit vector toward where the wind comes from); stepped `step` from the edge toward the house, the stack
    lying along the edge. Empty when the belt is not this homestead's windbreak."""
    from shapely import Point

    here = Point(hx, hy)
    if line.distance(here) > reach:
        return []
    t0 = line.project(here)
    out: list[tuple[float, float, float]] = []
    for dt in (0.0, -length * 1.1, length * 1.1):
        q = line.interpolate(t0 + dt)
        vx, vy = q.x - hx, q.y - hy
        dist = math.hypot(vx, vy)
        if dist <= step or dist > reach or (vx * wind[0] + vy * wind[1]) / dist < _KIZUMA_WINDWARD_COS:
            continue
        a, b = line.interpolate(t0 + dt - 1.0), line.interpolate(t0 + dt + 1.0)
        k = step / dist
        out.append((q.x - vx * k, q.y - vy * k, math.degrees(math.atan2(b.y - a.y, b.x - a.x))))
    return out


def _corridor(s: Settlement, walk: tuple[float, float, float, float, float, float], rot: float, rec: dict[str, Any]) -> None:
    """Draw and reserve the covered corridor to a bath shed (269 B12) - a plain roofed strip in the shed's own colors - and
    note it on the shed's record, so a reader of the manifest sees the form that was drawn."""
    wx, wy, cww, cwh, ex, ey = walk
    s.add_top(
        f'<g transform="translate({wx:.1f},{wy:.1f}) rotate({rot:.2f})"><rect x="{-cww / 2:.1f}" y="{-cwh / 2:.1f}" width="{cww:.1f}" height="{cwh:.1f}" fill="#A98C58" stroke="#5A4326" stroke-width="0.8"/></g>',
        cls="bathhouse",
    )
    s.placed.append((wx, wy, ex, ey))
    s.block_polys.append([(wx - ex / 2, wy - ey / 2), (wx + ex / 2, wy - ey / 2), (wx + ex / 2, wy + ey / 2), (wx - ex / 2, wy + ey / 2)])
    rec["corridor"] = {"x": round(wx, 1), "y": round(wy, 1), "w": round(cww, 1), "h": round(cwh, 1), "rot": round(rot, 1)}


def across_the_brook(s: Settlement, house: Pt, seat: Pt) -> bool:
    """Would this fixture stand across a stream from the house it serves (feature 261 FR-013)? The same rule, and the
    same guess, as `Settlement._parts_across_stream` for the homestead's own parts: the line from the house to the
    seat crosses no reach of any stream. The body is `crosses_a_stream`, the one predicate the homestead's own parts and
    the finished-map test read too (feature 287, FR-003)."""
    return crosses_a_stream(house, seat, s.M.get("streams", []))


def across_a_lane(lanes: Sequence[tuple[Poly, float]], house: Pt, seat: Pt) -> bool:
    """Would a lane run between this fixture and the house it serves (settlement-review of Mizuguchi, feature 261)? A
    shrine stands "in a corner of the house plot" and a coop in the yard (research/homesteads.html), and a shared lane
    between the house and the seat puts the seat outside the plot. The same line test as `across_the_brook`, against the
    lanes' centerlines - the predicate the web asks of a run between a house and its own fixtures (homes H32)."""
    return any(segments_cross(house, seat, pts[k], pts[k + 1]) for pts, _half in lanes for k in range(len(pts) - 1))
