"""Shared gate helpers (capacity): empty_street_runs, DEFAULT_MANIFEST, DWELLING_KINDS, BUSINESS_KINDS, HOUSEHOLD, COMMONER_KINDS, EXTRAMURAL_COMMONER_MAX, lane_near_misses, ... - bodies verbatim from check_village.py (feature 024 package split; SCC-packed, see split_package.py)."""

import math
from collections.abc import Sequence
from typing import Any

from .common_01_geometry import Manifest, Poly, Pt, seg_closest, seg_dist, segments_cross
from .common_02_overlap_policy import in_ellipse

DEFAULT_MANIFEST: Manifest = {
    "houses": [],
    "fields": [],
    "fallow_patches": [],
    "channels": [],
    "lane": [],
    "taxfree": [],
    "torii": [],
    "shrines": [],
    "manors": [],
    "streams": [],
    "buildings": [],
    "pastures": [],
    "forest_patches": [],
    "religious": [],
    "flower_fields": [],
    "labels": [],
    "town_streets": [],
    "gate_structs": [],
    "pond": None,
    "hill": None,
    "summit": None,
    "shrine": None,
    "forest": None,
    "forest_edge": None,
    "tree_crowns": [],
    "storehouses": [],
    "flophouses": [],
    "road": None,
    "wall": None,
    "gate": None,
    "gates": [],
    "moat": None,
    "governor_mansion": None,
    "ministries": [],
    "inspection_stations": [],
    "theater_stage": None,
    "granary": None,
    "wells": [],
    "threshing_yards": [],
    "gardens": [],
    "groves": [],
    "fire_towers": [],
    "village_groves": [],
    "commons": [],
    "dry_plots": [],
    "marshes": [],
    "title": None,
    "meta": {},
}

# a building's role for the population/frontage maths. A DWELLING houses one ~5-person household;
# a BUSINESS is a commercial frontage (the merchant's house+shop is BOTH - dual-use); everything
# else (civic, government, granary kura, barns, gate furniture) houses no one and fronts nothing.
DWELLING_KINDS = {
    "laborer",
    "laborer_large",
    "servant",
    "burakumin",
    "samurai",
    "samurai_large",
    "merchant",
    "merchant_house",
    "merchant_large",
    "monk_house",  # adept-monk households by the temple precincts (GM 2026-07-24) - real resident families, so they count as housing; they are deliberately ABSENT from the caste bands (clergy are not a lay caste)
}  # samurai_large was missing (a senior samurai house is a dwelling like every other _large variant) - found when Tango's population count kept landing 5 short of its generator's

BUSINESS_KINDS = {"shop", "merchant"}

HOUSEHOLD = 5

# COMMONER dwellings must shelter INSIDE a walled city (feature 006). In imperial-Chinese and
# Japanese practice the ordinary working population (laborers, artisans, most shopkeepers) lived
# intramurally - the wall's whole purpose is to protect them - while only four categories sat
# legitimately outside: elite country estates, farmhouses, the riverside wharf suburb, and the
# gate/approach-road (guan-xiang) market. So a commoner dwelling outside the wall is the true
# anomaly (it defeats the wall and has no economic anchor) and is flagged hard-zero; samurai are
# NOT commoners (their country seats are a legitimate extramural category).
COMMONER_KINDS = {"laborer", "laborer_large", "servant", "burakumin", "merchant", "merchant_house", "merchant_large", "monk_house"}

EXTRAMURAL_COMMONER_MAX = 0  # GM decision (FR-002): hard zero, no allowance the generator can drift into


def lane_near_misses(M: Manifest, maxgap: float = 80.0, eps: float = 4.0, align: float = 0.80, block: float = 18.0) -> list[tuple[int, int, int]]:
    """Endpoints of one lane (street/alley) that HEAD STRAIGHT TOWARD another lane and stop just short
    with a CLEAR path between - two lanes pointing at each other that don't meet, which should simply
    connect. Returns [(x, y, gap), ...], one entry per offending endpoint. Filters out: an endpoint that
    already meets a lane or the (wide) road (a junction/corner, not a dangling end); an end that does not
    point toward the other lane (within ~37 deg); and a gap something genuinely BLOCKS - a building, a
    ward fence, or the city wall - since then stopping short is intentional (the lane routes around it)."""
    lanes = [st["pts"] for st in M.get("town_streets", [])] + [(al["pts"] if isinstance(al, dict) else al) for al in M.get("alleys", [])]
    rd = M.get("road")
    bld = [(b["x"], b["y"]) for b in M.get("buildings", [])] + [(h["x"], h["y"]) for h in M.get("houses", [])]
    fences = [wd["boundary"] for wd in M.get("wards", [])]
    wall = M.get("wall") or []

    def to_lane(p: Pt, pts: Poly) -> tuple[tuple[float, float], float]:
        best, bd = (0.0, 0.0), 1e9
        for k in range(len(pts) - 1):
            cx, cy = seg_closest(p[0], p[1], pts[k], pts[k + 1])
            dd = math.hypot(p[0] - cx, p[1] - cy)
            if dd < bd:
                bd, best = dd, (cx, cy)
        return best, bd

    def blocked(a: Pt, b: Pt) -> bool:
        if any(seg_dist(bx, by, a, b) < block for bx, by in bld):
            return True
        if any(segments_cross(a, b, fb[k], fb[k + 1]) for fb in fences for k in range(len(fb) - 1)):
            return True
        return len(wall) >= 3 and any(segments_cross(a, b, wall[k], wall[(k + 1) % len(wall)]) for k in range(len(wall)))

    hits = []
    for i, pi in enumerate(lanes):
        if len(pi) < 2:
            continue  # a one-vertex way has no direction of travel (degenerate input, 2026-08-10)
        for E, nb in ((pi[0], pi[1]), (pi[-1], pi[-2])):
            if rd and to_lane(E, rd)[1] < 30:  # bed-overlaps the wide road
                continue
            if any(to_lane(E, c)[1] < eps for c in lanes if c is not pi):  # already a junction/corner
                continue
            for j, pj in enumerate(lanes):
                if j == i:
                    continue
                cp, g = to_lane(E, pj)
                if not (eps < g < maxgap):
                    continue
                dl = math.hypot(E[0] - nb[0], E[1] - nb[1]) or 1.0
                if (((E[0] - nb[0]) / dl) * (cp[0] - E[0]) + ((E[1] - nb[1]) / dl) * (cp[1] - E[1])) / g < align:
                    continue  # E is not heading toward pj
                if blocked(E, cp):
                    continue
                hits.append((round(E[0]), round(E[1]), round(g)))
                break
    return hits


def lane_ward_shortfalls(M: Manifest, maxgap: float = 60.0, eps: float = 6.0, align: float = 0.80, block: float = 18.0, gate_dist: float = 34.0) -> list[tuple[int, int, str]]:
    """Lane (street/alley) endpoints that head toward a NEIGHBORHOOD wall (a ward fence) but either
    stop short of it or reach it without a gate. Such a lane should extend to the fence and END AT A
    KIDO GATE (so e.g. laborers can pass through to work in the samurai quarter). Returns
    [(x, y, reason), ...]. The MAIN city wall is NOT a target - a lane may stop short of the outer
    rampart (the city's own boundary); only INTERNAL neighborhood fences pull a lane in to a gate."""
    fences = [wd["boundary"] for wd in M.get("wards", [])]
    if not fences:
        return []
    lanes = [st["pts"] for st in M.get("town_streets", [])] + [(al["pts"] if isinstance(al, dict) else al) for al in M.get("alleys", [])]
    kido = M.get("kido", [])
    wall = M.get("wall") or []
    bld = [(b["x"], b["y"]) for b in M.get("buildings", [])] + [(h["x"], h["y"]) for h in M.get("houses", [])]
    # an INTERIOR anchor (the governor's yamen, else the fences' centroid): a lane endpoint on the same
    # side of the fence as the anchor is INSIDE the ward (an internal government/samurai lane), which
    # needs no entry gate - only the COMMONER lanes approaching from OUTSIDE the fence are pulled in.
    gov = M.get("governor_mansion")
    if gov:
        anchor = (gov["x"], gov["y"])
    else:
        fpts = [p for fb in fences for p in fb]
        anchor = (sum(p[0] for p in fpts) / len(fpts), sum(p[1] for p in fpts) / len(fpts))

    def to_fence(p: Pt, pts: Poly) -> tuple[tuple[float, float], float, tuple[Any, Any]]:
        best, bd, bseg = (0.0, 0.0), 1e9, (pts[0], pts[1])
        for k in range(len(pts) - 1):
            cx, cy = seg_closest(p[0], p[1], pts[k], pts[k + 1])
            dd = math.hypot(p[0] - cx, p[1] - cy)
            if dd < bd:
                bd, best, bseg = dd, (cx, cy), (pts[k], pts[k + 1])
        return best, bd, bseg

    def side(p: Pt, a: Pt, b: Pt) -> float:
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])

    hits = []
    for pi in lanes:
        for E, nb in ((pi[0], pi[1]), (pi[-1], pi[-2])):
            for fb in fences:
                cp, g, seg = to_fence(E, fb)
                if g >= maxgap:
                    continue
                if side(E, *seg) * side(anchor, *seg) > 0:  # E is INSIDE the ward (an internal lane)
                    continue
                dl = math.hypot(E[0] - nb[0], E[1] - nb[1]) or 1.0
                toward = (((E[0] - nb[0]) / dl) * (cp[0] - E[0]) + ((E[1] - nb[1]) / dl) * (cp[1] - E[1])) / max(g, 1e-6)
                if g > eps and toward < align:  # not heading at the fence -> a passer-by, not an entry
                    continue
                if any(seg_dist(bx, by, E, cp) < block for bx, by in bld):
                    continue  # a building blocks the way -> the stop is intentional
                if len(wall) >= 3 and any(segments_cross(E, cp, wall[k], wall[(k + 1) % len(wall)]) for k in range(len(wall))):
                    continue  # the main rampart is between them
                if g > eps:
                    hits.append((round(E[0]), round(E[1]), "stops short of the neighborhood wall - extend it to the fence and end at a kido gate"))
                elif not any(math.hypot(E[0] - gt["x"], E[1] - gt["y"]) < gate_dist for gt in kido):
                    hits.append((round(E[0]), round(E[1]), "meets the neighborhood wall but has no kido gate there"))
                break
    return hits


# ---- SOFT ADVISORY: crop-limiting relocatable singleton ------------------------------------------------
# The crop-hard feature kinds that DRIVE crop_to_content's frame (the village/hamlet subset of
# settlement._CROP_HARD; the fields' vis_bbox + the pond are added specially, exactly as the crop does).
_CROP_DRIVERS = ("houses", "gardens", "threshing_yards", "village_groves", "groves", "dry_plots", "manors", "religious", "shrines", "farm_sheds", "wells", "cemeteries", "torii")

# discrete placed features a single move could freely RELOCATE (NOT the contiguous house/field/grove fabric).
# The outlying irrigation POND is the archetype; the rest are included so the detector is general and filtered
# by the conditions (terrain-anchor, threshold, empty-landing), not hard-coded away.
_RELOCATABLE = ("pond", "cemeteries", "religious", "shrines", "manors")


def _adv_bbox(o: Any) -> tuple[float, float, float, float]:
    """(x0,y0,x1,y1) of a feature: a torii list [x,y,z], a poly dict, a w/h dict, or a well radius dict."""
    if isinstance(o, (list, tuple)):
        # torii arch box: the glyph is TRUE SCALE since 2026-07-21 (16 ft rail = 16px at 1 ft/px, less at
        # coarser scales). This advisory helper has no meta access, so it uses the 1 ft/px worst case.
        return (o[0] - 8, o[1] - 3, o[0] + 8, o[1] + 8)
    if o.get("poly"):
        xs = [p[0] for p in o["poly"]]
        ys = [p[1] for p in o["poly"]]
        return (min(xs), min(ys), max(xs), max(ys))
    if "w" in o and "h" in o:
        return (o["x"] - o["w"] / 2, o["y"] - o["h"] / 2, o["x"] + o["w"] / 2, o["y"] + o["h"] / 2)
    return (o["x"] - o["r"], o["y"] - o["r"], o["x"] + o["r"], o["y"] + o["r"])  # a well


def _pond_bbox(M: Manifest) -> tuple[float, float, float, float]:
    c = M["pond"]
    return (c[0] - c[2], c[1] - c[3], c[0] + c[2], c[1] + c[3])


def _norm_skip(skip: Any) -> frozenset[tuple[str, int]]:
    """Normalize `skip` to a SET of (kind, i) members: None -> {}, else the given iterable of members (so a
    whole GROUP - a shrine + its churchyard + well - can be skipped at once, not just a single feature)."""
    return frozenset(skip) if skip else frozenset()


def _member_bbox(M: Manifest, member: tuple[str, int]) -> tuple[float, float, float, float]:
    """The bbox of one crop-driver member (kind, i) - the pond, a torii list, or a w/h / poly / well dict."""
    k, i = member
    return _pond_bbox(M) if k == "pond" else _adv_bbox(M[k][i])


def _crop_frame_boxes(M: Manifest, skip: Any = None) -> list[tuple[float, ...]]:
    """The bboxes that DRIVE the crop frame (crop-hard kinds + fields' visible extent + pond), minus `skip`
    (a single member OR a set of them - a whole relocatable GROUP)."""
    skip = _norm_skip(skip)
    B: list[tuple[float, ...]] = []
    for k in _CROP_DRIVERS:
        for i, o in enumerate(M.get(k) or []):
            if (k, i) not in skip:
                B.append(_adv_bbox(o))
    for fd in M.get("fields") or []:
        vb = fd.get("vis_bbox")
        B.append(tuple(vb) if vb else _adv_bbox({"poly": fd["outline"]}))
    if M.get("pond") and ("pond", 0) not in skip:
        B.append(_pond_bbox(M))
    return B


def _solid_occupancy(M: Manifest, skip: Any = None) -> list[tuple[float, ...]]:
    """Everything a relocated feature must AVOID: the frame drivers + fields + forest + marsh + hill. The
    COMMONS scrub is deliberately excluded - it is sparse grazing waste a pond/feature can simply replace.
    (Marsh IS included: a shrine/graveyard landing must be DRY.) `skip` may be a single member or a group."""
    B = _crop_frame_boxes(M, skip)
    for k in ("forest", "marshes"):
        for o in M.get(k) or []:
            B.append(_adv_bbox(o))
    if M.get("hill"):
        h = M["hill"]
        B.append((h[0] - h[2], h[1] - h[3], h[0] + h[2], h[1] + h[3]))
    return B


def _bbox_frame(B: Sequence[Sequence[float]], m: float = 30) -> tuple[float, float, float, float]:
    return (min(b[0] for b in B) - m, min(b[1] for b in B) - m, max(b[2] for b in B) + m, max(b[3] for b in B) + m)


def _shrine_group(M: Manifest, i: int) -> set[tuple[str, int]]:
    """The set of members that move AS ONE with the shrine at religious[i]: the shrine itself, the graveyard
    it is responsible for (a cemetery within ~300px), its ablution well (~150px), and its torii (~140px). A
    village shrine and its churchyard are a single sacred precinct - you relocate the whole precinct, not the
    altar alone - so the crop advisory must weigh them together, not one at a time. See settlements.md."""
    sh = M["religious"][i]
    sx, sy = sh["x"], sh["y"]
    members = {("religious", i)}
    # the SAME shrine is mirrored into the geometric `shrines` list (parallel footprint records); the mirror
    # is also a crop-driver, so the group must carry it too or the copy left behind still pins the crop edge.
    for j, s in enumerate(M.get("shrines") or []):
        if abs(s["x"] - sx) <= 1 and abs(s["y"] - sy) <= 1:
            members.add(("shrines", j))
    for j, cm in enumerate(M.get("cemeteries") or []):
        if math.hypot(cm["x"] - sx, cm["y"] - sy) <= 300:
            members.add(("cemeteries", j))
    for j, wl in enumerate(M.get("wells") or []):
        if math.hypot(wl["x"] - sx, wl["y"] - sy) <= 150:
            members.add(("wells", j))
    for j, t in enumerate(M.get("torii") or []):
        if math.hypot(t[0] - sx, t[1] - sy) <= 140:
            members.add(("torii", j))
    return members


def crop_relocatable_singletons(M: Manifest, min_shrink: float = 150, clear: float = 20) -> list[dict[str, Any]]:
    """SOFT ADVISORY (never a gate failure): find a relocatable CANDIDATE that ALONE holds a crop_to_content
    edge out by >= `min_shrink` px, AND for which an EMPTY landing (clear of all SOLID occupancy) exists INSIDE
    the tighter frame - so moving it would let the image crop significantly smaller without disturbing anything
    else. A candidate is either (a) a single freely-relocatable feature (the archetype: an outlying irrigation
    POND), or (b) a GROUP that moves as one unit - a village SHRINE together with its churchyard GRAVEYARD (and
    its ablution well + torii). The group case matters because removing the shrine ALONE leaves the graveyard
    holding the same crop corner (and vice versa), so neither reads as relocatable singly - only weighed
    together does the precinct free the corner. Only applies to a village/hamlet that crops to content
    (`meta.view`). Returns a list of {kind, at, edge, shrink, landing, members}; empty when nothing qualifies.
    See settlements.md 'Crop advisory'."""
    meta = M.get("meta", {})
    if meta.get("scale") not in ("village", "hamlet") or not meta.get("view"):
        return []
    full_boxes = _crop_frame_boxes(M)
    if not full_boxes:
        return []
    full = _bbox_frame(full_boxes)
    hill = M.get("hill")
    out: list[dict[str, Any]] = []
    # a pond WIRED TO THE FIELD's water is hydrologically anchored (like a hill-shrine), NOT relocatable: a
    # SOURCE pond (a channel frm=pond -> to=field) belongs UPHILL of the field, so moving it "into the frame"
    # would drop it below the water-entry (backwards for a gravity feed); a DRAINAGE pond (frm=drain -> to=pond)
    # belongs at the low foot BELOW the field, so it must poke past the low crop corner. Either way its poke is
    # intrinsic - the fix is to NUDGE it flush, not move it. (A standalone/decorative pond with no field wiring
    # stays a candidate.) See settlements.md 'Crop advisory'.
    pond_wired = any(
        (c.get("frm", {}).get("kind") == "pond" and c.get("to", {}).get("kind") == "field") or (c.get("frm", {}).get("kind") == "drain" and c.get("to", {}).get("kind") == "pond")
        for c in M.get("channels", [])
    )
    # cands: each entry is (label, members-frozenset, (ox, oy) primary anchor).
    cands: list[tuple[str, frozenset[tuple[str, int]], tuple[float, float]]] = []
    if M.get("pond") and not pond_wired:
        cands.append(("pond", frozenset({("pond", 0)}), (M["pond"][0], M["pond"][1])))
    for k in _RELOCATABLE:
        if k == "pond":
            continue
        for i, o in enumerate(M.get(k) or []):
            cands.append((k, frozenset({(k, i)}), (o["x"], o["y"])))
    # GROUP candidates: a shrine + its churchyard graveyard (+ well + torii) as one movable precinct. Only a
    # shrine with a real COMPANION (a graveyard/well/torii) is a group - a bare shrine (plus its own `shrines`
    # mirror record, which always pairs) is just the singleton already considered above.
    for i, sh in enumerate(M.get("religious") or []):
        gmem = _shrine_group(M, i)
        if any(m[0] in ("cemeteries", "wells", "torii") for m in gmem):
            cands.append(("shrine+churchyard", frozenset(gmem), (sh["x"], sh["y"])))
    for kind, members, (ox, oy) in cands:
        without = _crop_frame_boxes(M, members)
        if not without:
            continue
        f2 = _bbox_frame(without)
        edges = {"W": f2[0] - full[0], "N": f2[1] - full[1], "E": full[2] - f2[2], "S": full[3] - f2[3]}
        shrink = max(edges.values())
        if shrink < min_shrink:
            continue
        is_pond = ("pond", 0) in members
        if hill and not is_pond and in_ellipse(ox, oy, hill):
            continue  # terrain-anchored (a hill-shrine can't move to flat ground)
        mb = [_member_bbox(M, m) for m in members]  # the group's COMBINED footprint moves as one rigid unit
        w = max(b[2] for b in mb) - min(b[0] for b in mb)
        h = max(b[3] for b in mb) - min(b[1] for b in mb)
        occ = _solid_occupancy(M, members)
        tb = _bbox_frame(without, 0)  # the TIGHTER content bbox - land here and the crop tightens
        landing = None  # (a feature wider/taller than tb never enters the loops -> stays None)
        gy = tb[1] + h / 2
        while gy <= tb[3] - h / 2 and landing is None:
            gx = tb[0] + w / 2
            while gx <= tb[2] - w / 2:
                if not any(gx - w / 2 < b[2] + clear and b[0] < gx + w / 2 + clear and gy - h / 2 < b[3] + clear and b[1] < gy + h / 2 + clear for b in occ):
                    landing = (round(gx), round(gy))
                    break
                gx += 25
            gy += 25
        if landing is None:
            continue
        out.append({"kind": kind, "at": (round(ox), round(oy)), "edge": max(edges, key=lambda e: edges[e]), "shrink": round(shrink), "landing": landing, "members": len(members)})
    return out


# canonical residential DENSITY: dwellings per px^2 of residential-capable ground (interior minus
# overhead) that a well-packed provincial-city quarter delivers. Calibrated on Tango, a GM-accepted
# 3,000-person city: 561 placed dwellings on ~378k px^2 of non-overhead, NON-RESERVE interior
# (449,984 res-capable minus the agri reserve's ~72k of non-field slack) = ~1.49/1000.
# Feature-009 recalibration: the original 0.00127 divided by res-capable ground that still
# CONTAINED Tango's agricultural-reserve slack (only non-agri reserves were deducted), so the
# constant under-read what packed urban ground actually delivers - and a no-reserve city
# (Nagahara at its budget-derived ring) was told to 'enlarge' at a density Tango itself packs.
# Reserve ground of ANY kind is committed to non-housing; it must never dilute the density norm.
RHO_CANONICAL = 0.00149

# --- feature 006: per-quarter density + reserve/civic zoning thresholds --------------------
# These are calibrated against Tango (GM-accepted, must pass) AND the pinned pre-feature broken
# Nagahara (pool/regressions/city_density_broken_nagahara.json, must fail); see settlements.md
# "Quarters and per-quarter density" for the recorded why behind each number.
#
# QUARTER_DENSITY band (dwellings per px^2, averaged over a residential/mixed quarter): a commoner
# warren runs ~4-6x denser than a samurai/official ward (Edo: commoners ~50% of population on
# ~20% of land vs samurai ~50% on ~70%; provincial castle towns 4-6x), so the band spans ~5x from
# a low-density samurai ward floor to a packed-warren ceiling. Below the floor reads as a
# half-built quarter; above the ceiling is implausibly crammed. Floor/ceil are provisional here
# and pinned during calibration (T019).
QUARTER_DENSITY_FLOOR = 0.00030  # ~ a legitimately sparse government/samurai ward (Tango's SE reads 0.36/1000 over its non-civic ground; calibrated on Tango)

QUARTER_DENSITY_CEIL = 0.00230  # ~ a packed commoner warren (Tango's NE laborer wedge reads 2.13/1000); ~7.7x the floor, within the 4-8x historical spread

# a residential quarter must not hide a DEAD ZONE: a contiguous empty region larger than a
# firebreak strip. Block-density medians alone cannot separate a good city from a lopsided one
# (Tango and the broken Nagahara share a 4.6/10k median); the discriminator is empty *sub-regions*
# inside a quarter that should be housing. Fire-breaks are thin; a whole empty block is not.
DEAD_ZONE_MAX = 150.0  # px, longest side of an allowed empty pocket in a residential quarter

# a CIVIC precinct (yamen, temple) is legitimately majority-open (roofed halls ~25-45%, courtyards
# and gardens the rest), so tolerate up to ~70% open - but only when the openness is STRUCTURED
# (the quarter actually holds civic compounds); an open-and-structureless "civic" quarter reads as
# merely empty and is flagged.
CIVIC_OPEN_TOL = 0.70

# RESERVE ground (drill ground + gardens + agricultural district) is capped at ~20% of the walled
# interior. Civic *buildings* alone are only ~3-6% of a Chinese county seat; the big open consumer
# is the drill ground plus deliberately under-built garden/farm remainder. ~20% comfortably fits a
# drill ground + gardens + an agricultural district and is historically conservative; beyond it the
# wall encloses more open ground than a provincial seat justifies (read: shrink the wall).
RESERVE_CAP_FRAC = 0.20

# --- feature 009: budget-first wall sizing (specs/009-city-area-budget) ---------------------
# A walled city's wall is DERIVED from a declared space budget (citybudget.plan_city, recorded
# at meta.budget by the gen script BEFORE the wall is drawn); these tolerances bound how far the
# drawn enclosure may drift from that promise, in EITHER direction. Calibrated on the two pinned
# anchors: shipped Tango's enclosure sits ~+0.2% off its budget (must pass) while the pre-feature
# Nagahara - the GM-rejected "too empty" city every other check called green - sits ~+21% (must
# fail, pool/regressions/city_budget_fires_on_the_too_empty_nagahara.json). OVER at 8% leaves
# >2x separation to the known-bad anchor; UNDER is tighter (5%) because an undersized wall
# breaks packing immediately rather than merely reading as sparse.
BUDGET_TOL_OVER = 0.08

BUDGET_TOL_UNDER = 0.05

# --- to-scale gates/walls + funerary features (GM, 2026-07-19) ------------------------------
# Anchors researched 2026-07-19 (full memo in settlements.md "Historical grounding"):
# GATES: a samurai residence gate (nagayamon/yakuimon) opens ~9-12 real ft; a grand yamen
# gatehouse carriage opening runs to ~24 ft. Openings above that (the old fixed +-34px gap =
# 204 ft at city scale) read as a missing wall. WALLS: dobei/tsuijibei ~1.5-2 ft; the 2px
# cartographic floor at 3 ft/px draws 6 ft, so the band top is 8.
GATE_FT_MIN, GATE_FT_MAX = 6.0, 24.0

WALL_FT_MIN, WALL_FT_MAX = 1.0, 8.0

# CREMATION: a village/town sanmai's cleared working core is 30-80 ft across (Fukui sanmai
# survey: ~7 ft hearth, 10-13 ft sheltered structures + bone platform + attendant hut); a
# provincial city justifies ~80-160 ft; the Yoyogi crematory serving metropolitan Edo was ~900
# tsubo (~180 ft square) - the far ceiling, not a template. Floors keep a token dot from
# passing as a crematory.
CREMATION_FT_MIN, CREMATION_FT_MAX_TOWN, CREMATION_FT_MAX_CITY = 25.0, 90.0, 160.0

# OSSUARY: a muenzuka bone mound is typically 10-30 ft across, 3-8 ft high (cremated,
# consolidated bone takes almost no volume - Kozukappara's 100k+ dead never made a great
# mound); Kyoto's monumental state-built Mimizuka is ~50 ft at the base. Band [8, 32] = the
# true 10-30 ft range plus glyph rounding (tightened 2026-07-21: the old top of 60 existed to
# admit a legibility-sized ~40 ft glyph whose 9px floor actually rendered 54 ft at city scale -
# the size-inflation license is retired; the drawn mound is now ~22 ft with a 4.5px floor).
OSSUARY_FT_MIN, OSSUARY_FT_MAX = 8.0, 32.0

# BURIAL GROUNDS (cremation-then-inter culture, aggressive plot reuse, ~1 generation of active
# plots): ~10-20 sq ft per urn-grave packed incl. circulation. The VILLAGE ground serves the
# WHOLE ~800-person district (the central village ~350 + ~6 hamlets ~75 each, whose dead are
# carried here as urns - hamlets draw no ground; settlements.md 'District catchment', GM
# 2026-07-23): ~800 x ~25-30 deaths/1,000/yr x ~30-yr reuse = ~600-720 active plots ->
# village 0.15-0.30 ac; town (~1,200 own pop) 0.25-0.75, city (~3,000) 0.75-2 split across
# yards. Bands widened a little both ways for glyph rounding; the LADDER must stay monotone
# with population SERVED (district 800 < town 1,200, so the ranges nest fine).
BURIAL_AC_BAND = {"village": (0.12, 0.38), "town": (0.10, 0.80), "city": (0.35, 2.20)}

# --- doors-face-open + rows-max-two-deep (GM, 2026-07-18) -----------------------------------
# The boundary between "an eave/drainage gap" (~3-6 real ft between back-to-back rows - rain
# drip and night-soil access, NOT an entrance) and "walkable entrance ground" (a roji/court at
# >= ~10 real ft). 7 ft sits cleanly between the two bands at every map scale; the checks
# convert it to drawn px via meta.ftpx.
DOOR_CLEAR_FT = 7.0


# ---- WAIVERS: a map may decline a rule, but only in writing (GM 2026-07-27) --------------------
# Every placement rule here is a GENERALIZATION, and a specific place is allowed to have a specific
# history that overrides it - Tango's samurai take the southeast because the Emperor lies that way,
# Hirameki's burakumin stayed outside walls that were thrown up in a hurry when a war turned an
# interior county into a border one. What must NOT happen is that overriding a rule looks like
# passing it. So a map waives a named check by declaring meta(waivers={"check_name": "why"}), the
# gate prints WAIVE rather than PASS, and two meta-checks keep the escape hatch honest:
#   - the reason must be a real explanation (WAIVER_MIN_REASON chars), not "n/a" or "by design";
#   - the waiver must be LIVE - a waiver on a check that now passes, or on a name that no longer
#     exists, is stale and fails. Waivers therefore rot loudly instead of silently accumulating
#     into a map that is exempt from rules nobody remembers it was ever breaking.
# The meta-checks themselves are NOT waivable, or the hatch would swallow its own guard.
WAIVER_MIN_REASON = 60

WAIVER_META_CHECKS = frozenset({"waivers_are_documented", "waivers_are_live"})


def _poly_area(p9: Any) -> float:
    a9 = 0.0
    for i9 in range(len(p9)):
        x19, y19 = p9[i9]
        x29, y29 = p9[(i9 + 1) % len(p9)]
        a9 += x19 * y29 - x29 * y19
    return abs(a9) / 2


class _UnboundType:
    """Poison for a gate-scope name no earlier segment bound (feature 022). Any USE raises, so a
    segment that would have hit NameError in the legacy monolith still fails loudly instead of
    computing with garbage; a segment whose guards keep it away from the name never notices."""

    def _boom(self, *a: object, **k: object) -> Any:  # pragma: no cover - never hit on valid manifests; the raise IS the feature
        raise NameError("gate segment read a name no earlier segment bound (legacy NameError parity)")

    __bool__ = __iter__ = __call__ = __len__ = __contains__ = __getitem__ = _boom  # pragma: no cover
    __add__ = __radd__ = __sub__ = __mul__ = __truediv__ = __lt__ = __le__ = __gt__ = __ge__ = _boom  # pragma: no cover

    def __getattr__(self, name: str) -> Any:  # pragma: no cover - see _boom
        raise NameError("gate segment read a name no earlier segment bound (legacy NameError parity)")


_UNBOUND = _UnboundType()


def _kept(loc: dict[str, Any], names: tuple[str, ...]) -> dict[str, Any]:
    """The names a segment binds, ready to merge into the gate namespace (feature 022)."""
    return {k: v for k, v in loc.items() if k in names and v is not _UNBOUND}
