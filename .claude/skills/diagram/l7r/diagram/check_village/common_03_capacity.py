"""Shared gate helpers (capacity): empty_street_runs, DEFAULT_MANIFEST, DWELLING_KINDS, BUSINESS_KINDS, HOUSEHOLD, COMMONER_KINDS, EXTRAMURAL_COMMONER_MAX, lane_near_misses, ... - bodies verbatim from check_village.py (feature 024 package split; SCC-packed, see split_package.py)."""

from typing import Any

from .common_01_geometry import Manifest

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


# ---- SOFT ADVISORY: crop-limiting relocatable singleton ------------------------------------------------
# The crop-hard feature kinds that DRIVE crop_to_content's frame (the village/hamlet subset of
# settlement._CROP_HARD; the fields' vis_bbox + the pond are added specially, exactly as the crop does).
_CROP_DRIVERS = ("houses", "gardens", "threshing_yards", "village_groves", "groves", "dry_plots", "manors", "religious", "shrines", "farm_sheds", "wells", "cemeteries", "torii")

# discrete placed features a single move could freely RELOCATE (NOT the contiguous house/field/grove fabric).
# The outlying irrigation POND is the archetype; the rest are included so the detector is general and filtered
# by the conditions (terrain-anchor, threshold, empty-landing), not hard-coded away.
_RELOCATABLE = ("pond", "cemeteries", "religious", "shrines", "manors")


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
