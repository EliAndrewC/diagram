"""The overlap taxonomy's matrix policy: which classes, keys and siblings may share ground, and why (split from `overlap/taxonomy.py`
at 1,000 lines - feature 444).

Research: the policy's plumbing - NONE: each table is claimed at its own docstring
"""

import math
from typing import Any

from .kinds import OVERLAP_CLASS

_MATRIX_PERMISSIVE = {
    # the GM's own example, and the distinction the whole design turns on
    "COVER": "permissive ground cover - grazing, pasture and scrub describe what the ground IS, not an object occupying it, so a house or a field built on it is the normal case (never a well: 0196 draws no well out on open common ground, and _OVERLAP_LINEAR keeps wells off it) and the cover simply stops there (contrast GROUND, which is worked as a surface and is ruined by anything standing in it)",
    "OVERLAY": "a declarative zoning overlay (a QUARTER) CONTAINS features by definition - it describes what a district is for, not an object standing in it",
    # Deliberately out of scope rather than unclassified: canopy-vs-structure is already governed
    # precisely by the keep-clear/canopy contract (Settlement._CANOPY_STRUCT_KEYS + the ratchet added
    # in feature 016), which tests recorded CROWNS and knows which grounds a bough may legitimately
    # overhang. Re-deciding that here would duplicate proven machinery and risk two verdicts on one
    # question. Vegetation records are also envelopes (a `forest` is a stand outline, a grove a belt
    # outline) whose ink lives in `tree_crowns` - see the drawn-extent rule in matrix_extents.
    "VEGETATION": "canopy overlap is governed by the canopy keep-out contract, which tests recorded crowns; the matrix does not re-decide it",
    "RING_ROAD": "the intramural patrol strip is governed precisely by ring_road_kept_clear, which knows its real bed width; the matrix does not re-decide it",
    "RECORD": "bookkeeping geometry or an in-field flourish drawn ON its own paddy by design - not ground the matrix reasons about",
    "PADDY_RECONSTRUCTED": "a paddy plot's extent is reconstructed from recorded spans rather than stored, so it is an approximation - the precise paddy checks (harvest_yards_clear_of_paddies, structures_clear_of_dry_plots, streams_avoid_fields, tanning_yard_clear_of_fields) test real geometry and remain authoritative",
}
"""The permissive classes.

Research:
    no well on common ground - research/questions/0196-communal-wells-ido.drawing.html: no well drawn out on open common ground as the normal case, though _OVERLAP_LINEAR keeps structures off commons, pastures and marshes
    house or field on cover - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); built on, the cover stopping there
    deferred classes - NONE: vegetation, the ring road, records and paddy are decided by their own rules
"""

# WHAT EACH FIXTURE IS MOUNTED ON (GM 2026-07-26). FIXTURE used to be a PERMISSIVE class, which had
# two compounding effects: `matrix_extents` skips permissive classes entirely, so all ten fixture keys
# were never extracted and therefore invisible to every matrix check in BOTH directions; and
# `matrix_policy` returned a permission whenever either side was a fixture, so anything could sit on
# one. In Minami that hid 56 solid built objects - 4 bridges, 4 ward gates, 24 wall towers, 10 gate
# structures, 6 sluice gates, 3 jetties, 2 inspection stations, 1 dock - and it is how the map came to
# carry TWO overlapping bridges over the same crossing, a guard station on the ward fence and an oil
# press across a ward gate, all with a green gate.
#
# "The overlap is the whole point" is true only OF THE THING THE FIXTURE IS BUILT ON. A bridge is
# built on water and on the way it carries; it is not built on another bridge, and a ward gate is not
# built on an oil press. So each fixture names its mounts - CLASSES or specific KEYS - and may overlap
# nothing else, including another fixture of its own kind. Entries are deliberately MINIMAL: a
# genuine adjacency the sweep surfaces should be added here with its reason, not pre-permitted.
_FIXTURE_MOUNTS: dict[str, frozenset[str]] = {
    "bridges": frozenset(
        {"WATER", "WAY", "wall", "water_gates"}
    ),  # spans the water to carry the way over it - and a bridge on a moated approach lands ON the rampart at its water gate, which is the crossing the wall is pierced for. `water_gates` was added 2026-07-27 with Nagahara's ring-road canal deck: the ring runs a fixed inset inside the rampart, so where a cargo canal enters through a shuimen the ring necessarily crosses it a few paces INSIDE the arch (Nagahara 39 real ft), and the gate structure's own apron and the deck share that ground - the Suzhou pattern, where the wall road crosses each canal on a bridge at the water gate. Shortening the deck does not separate them (checked: even a bare-abutment span still lands inside the gate footprint), which is what says this is an adjacency rather than a drawing error
    "docks": frozenset({"WATER", "WAY"}),  # a landing stands at the waterline, reached from the quay
    "jetties": frozenset({"WATER"}),  # planked mooring fingers run out OVER the river
    "log_booms": frozenset({"WATER"}),  # a cabled log pen floats ON the river it holds timber in
    "sluice_gates": frozenset({"WATER"}),  # the intake/outfall board IS the water-to-water junction
    "weirs": frozenset({"WATER"}),  # a weir is a bar built ACROSS a stream - the water is what it stands in
    "washing_places": frozenset({"WATER"}),  # a footing of steps down the bank stands at the waterline (0065)
    "water_gates": frozenset(
        {"WATER", "wall"}
    ),  # the shuimen arch stands over its canal AND on the city wall - the wall IS a matrix feature now (classified SOLID for feature 017), so the mount it always had must be stated
    "kido": frozenset({"WAY", "wards"}),  # a ward gate sits ON the ward fence where a lane passes through
    "gate_structs": frozenset({"WAY", "wall"}),  # the guard station and tower ARE the city gate complex, standing on the wall and the road - both mounts now stated, since `wall` is classified
    "inspection_stations": frozenset({"WAY", "gate_structs"}),  # an inspection post is part of the gate complex it stands in
    # A tower stands ON the rampart. That mount is now EXPLICIT: `wall` was unclassified when these
    # entries were written ("which the matrix does not model"), and classifying it SOLID turned every
    # tower, gate complex, water gate and moat bridge in the pool into a violation of a rule they had
    # always satisfied. The lesson is that a mount list written against an unclassified neighbor is
    # silently incomplete - it records only the mounts the matrix could see at the time. The moat and its irrigation taps run at the
    # rampart's foot by construction (Tango's moat-fed channel passes under the tower line), and the
    # tower is elevated above them, so water is a legitimate mount; anything SOLID against a tower is
    # still a defect.
    "wall_towers": frozenset({"WATER", "wall"}),
}
"""What each fixture stands on.

Research:
    bridge - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: on water and the way it carries, and on the rampart at a water gate, the deck sharing ground with the gate where the ring road crosses a canal a few paces inside the arch
    dock and jetty - research/questions/0176-wharves-and-landings-piers-quays-and-stepped-landings-kashi-gangi.drawing.html: at and over the water, a dock reached from the quay
    log boom - research/questions/0210-timber-yards-and-log-booms-kiba.drawing.html: on the river
    sluice and water gate - research/questions/0179-water-gates-and-sluices-shuimen.drawing.html: a board on its channel, an arch over its canal on the wall
    weir - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: across the brook
    washing place - research/questions/0065-washing-places-at-the-waters-edge.drawing.html: a footing of steps down the bank to the water
    ward gate - research/questions/0160-city-wards-and-the-gates-that-shut-them-at-night-machi-kido.drawing.html: on the ward fence where a way passes
    gate complex and inspection post - research/questions/0147-city-and-town-gates-the-opening-the-gate-tower-and-the-crossing-of-the-moat-chengmen.drawing.html: on the wall and the road at the gate
    wall tower - research/questions/0148-towers-along-the-city-wall-mamian.drawing.html: on the rampart
    wall tower over water - GUESS: a wall tower may stand over the moat and its irrigation taps at the rampart's foot (no page on towers or moats says whether water passed under one)
    only the mounts listed - CONVENTION: each fixture - dock, jetty, log boom, sluice, weir, water gate, kido, gate complex, inspection post, bridge, wall tower - stands on the classes and keys listed for it and on nothing else, not even another fixture of its own kind
"""

_MATRIX_SAME_CLASS_OK = {
    "WATER": "watercourses meet at confluences",
    "WAY": "ways meet at junctions",
    # two annexes of the SAME parent (a farmhouse's yard, garden, shed and grove arms) abut one
    # another as a matter of course; the parent-scope test below is what keeps them honest, since an
    # annex touching a DIFFERENT household's annex is still a defect
    "ANNEX": None,
}
"""Same-class permissions.

Research:
    watercourses meet - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: at confluences
    ways meet - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: at junctions, one network
    annexes of one household - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html, research/questions/0040-farm-storehouses-kura.drawing.html: abut one another
"""

# same-KEY permissions: records of one kind that legitimately touch each other
_MATRIX_SAME_KEY_OK = {
    "wall": "consecutive rampart segments meet at every corner - the wall is one continuous work, drawn as a chain of strokes",
    "torii": "the arches of one approach avenue are a series along the sando, spaced by design",
    "wards": "consecutive segments of ONE fence share their corner - the extractor strokes a polyline into one quad per segment, so neighbors always meet. Two DIFFERENT wards' fences crossing is a real defect and is caught by city_ward_fence_clear_of_structures' own ward-x-ward test",
    "dry_plots": "adjacent hatake plots in one quilt abut and share their headlands, exactly as paddy plots share bunds",
    "fields": "paddy plots in one fan abut and share their bunds - and a plot's extent is reconstructed from recorded spans, not a stored polygon, so the reconstruction slightly overstates an irregular plot",
}
"""Same-key permissions.

Research:
    one continuous work - NONE: rampart and fence segments meet at their corners
    arches in a row - research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html: along the approach
    dry plots abut - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: neighbors share their edges
    paddies share bunds - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: one shared bund
"""

_MATRIX_ALLOWED_PAIRS: dict[frozenset[str], str] = {
    frozenset({"WATER", "WAY"}): "a way crosses water at a bridge; unbridged crossings are gated separately by roads_bridge_watercourses",
    frozenset(
        {"WAY", "BARRIER"}
    ): "a way PIERCES a ward fence - that is what a kido is for. The rule that matters is not whether a street crosses the fence but whether every crossing has a gate, and that is held by city_samurai_ward_sealed + city_kido_on_ward_fence, which fire on an ungated crossing",
}
"""Class-pair permissions.

Research:
    way over water - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: on a bridge
    way through a ward fence - research/questions/0160-city-wards-and-the-gates-that-shut-them-at-night-machi-kido.drawing.html: at its gate
"""

# per-KEY-PAIR permissions for genuine one-offs the class policy is too coarse to express
_MATRIX_ALLOWED_KEYS: dict[frozenset[str], str] = {
    frozenset(
        {"quays", "jetties"}
    ): "a jetty SPRINGS FROM the quay face - the faced bank is the working surface the stage projects out of, so they meet by construction (research/contents.json#river-cities: the pier exists for REACH where the bank shelves too gently, and it starts at the revetment)",
    **{
        frozenset(
            {"wall", w}
        ): "a way or a watercourse passes THROUGH the rampart at its gate or water gate - that opening is the point of a gate, and no_structure_on_wall still governs anything BUILT on the rampart"
        for w in ("road", "roads", "town_streets", "alleys", "lanes", "canals", "channels", "streams")
    },
    frozenset({"wall", "moat"}): "the moat LIES AGAINST the rampart's foot - it is dug along the wall it defends, so their outlines meet",
    frozenset(
        {"castles", "castle_towers"}
    ): "a yagura STANDS ON the rampart it defends - a corner tower projecting from the enceinte IS the form of the thing, exactly as a mural tower sits on the city wall. The castle's works may still not be built on by anything else: both keys stay SOLID against every other feature, and the ways are held off by the same matrix that caught the Imperial road running through this castle in the first place",
    **{frozenset({"torii", w}): "a torii STANDS OVER its approach - an arch spanning the sando is the whole form of the thing" for w in ("road", "roads", "town_streets", "alleys", "lanes")},
    frozenset({"religious", "shrines"}): "shrine_hall records one hall under BOTH keys - these are the same object, not two",
    frozenset(
        {"wards", "wall"}
    ): "a ward fence ENDS at the rampart - city_ward_fence_meets_wall demands exactly that, so commoners cannot walk around it. The same adjacency was already stated for {wards, wall_towers}; it needed stating for the wall ITSELF once `wall` was classified SOLID. (The route is held by city_ward_fence_meets_wall + city_samurai_ward_sealed, so this cannot excuse a fence running along INSIDE the rampart.)",
    frozenset(
        {"wards", "wall_towers"}
    ): "a ward fence ENDS at the rampart - that is exactly what city_ward_fence_meets_wall demands, so commoners cannot walk around it - and a wall tower stands ON the rampart. A fence end butting into a tower's footprint IS the fence reaching solid wall. (Its route is held by city_ward_fence_meets_wall and city_samurai_ward_sealed, so this cannot excuse a fence wandering through a tower mid-span.)",
    frozenset(
        {"gate_structs", "wall_towers"}
    ): "a city gate's own TOWER is recorded under both keys - identical x/y/w/h/rot, the same object rather than two (verified on Minami: tower(1323,902) w17h10 appears in each list). The same duplicate-record case as religious x shrines",
    frozenset(
        {"castles", "bridges"}
    ): "a deck carries the approach avenue over the castle's OWN moat - the moat ring is part of the castles record, so the deck that the shared crossing source (feature 020) DEMANDS there necessarily overlaps it. The deck lies on the water, not the works; the ways themselves are still held off the castle by the matrix that caught the Imperial road running through it",
    frozenset(
        {"castle_towers", "bridges"}
    ): "the ote-mon's moat deck lands at the gate tower's foot - a castle bridge ENDS at its gate, so the deck's landing margin may kiss the tower footprint, exactly as a city gate's bridge lands in its gate complex",
    frozenset({"buildings", "merchant_estates"}): "a merchant estate is a walled COURT drawn around an inner building that is itself a checked struct",
    frozenset(
        {"wall", "flower_fields"}
    ): "an ornamental bed laid FLUSH against the inside of the town wall - s.flower_field's `flat_west` flag exists for exactly that (it straightens the edge so it can run against the rampart), so the bed's straight face meeting the wall's drawn stroke is the feature working, not a defect. Anything BUILT on the rampart is still governed by no_structure_on_wall; this permits planting, which occupies no rampart",
}
"""Key-pair permissions.

Research:
    pier from the quay - research/questions/0176-wharves-and-landings-piers-quays-and-stepped-landings-kashi-gangi.drawing.html: springs from the faced bank
    ways and water through the rampart - research/questions/0147-city-and-town-gates-the-opening-the-gate-tower-and-the-crossing-of-the-moat-chengmen.drawing.html, research/questions/0179-water-gates-and-sluices-shuimen.drawing.html: at a gate or a water gate
    moat against the rampart - research/questions/0151-city-moats-how-wide-and-deep-and-whether-they-ring-the-wall-hori-chenghe.html: the moat stood about thirty paces out (Wujing Zongyao), 7 to 10 m at Qufu - the moat is allowed against the rampart's foot, a departure the code keeps until feature 417 T35; wall x moat permitted, the moat lying against the rampart's foot
    castle towers on the rampart - research/questions/0139-the-castle-in-a-capital-where-it-sits-how-big-it-is-and-its-gates-shiro.drawing.html: a corner tower stands on the works
    arch over its approach - research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html: spans the sando
    one object under two keys - NONE: a hall as religious and shrines, a gate tower twice
    ward fence meets the wall - research/questions/0160-city-wards-and-the-gates-that-shut-them-at-night-machi-kido.drawing.html: ends at the rampart
    castle moat bridge - research/questions/0139-the-castle-in-a-capital-where-it-sits-how-big-it-is-and-its-gates-shiro.drawing.html: a deck over the castle's own moat to its gate
    castle bridge at its gate tower - research/questions/0139-the-castle-in-a-capital-where-it-sits-how-big-it-is-and-its-gates-shiro.drawing.html: the moat deck lands at the gate it leads to
    merchant estate court - research/questions/0155-rich-merchants-walled-houses-and-their-fireproof-storehouses-kura.drawing.html: a walled court round its house
    flower bed against the town wall - research/questions/0149-the-street-along-the-inside-of-a-city-wall-shunchengjie.html: walled Chinese cities ran a street along the inside of the rampart, a patrol road by the Ming at Tongzhou - a bed is allowed flush against the rampart, a departure the code keeps until feature 417 T35; a bed laid flush inside the rampart
"""

# A record naming its PARENT may overlap that parent and nothing else - strictly stronger than the
# blanket per-pair exemptions this replaces, because an annex on somebody ELSE's building stays a defect.
# manifest lists that carry coordinates but are NOT drawn ground the matrix reasons about
# Manifest lists carrying coordinates that are NOT drawn ground. `gates` is a list of GAP POSITIONS
# in the wall (the furniture in the gap is `gate_structs`); `wall_tower_keepclears` is a reservation,
# not ink; `forest_edge` is an envelope whose ink is `tree_crowns` and is classified RECORD above.
_MX_NOT_GEOMETRY = frozenset(
    {
        "labels",
        "tree_crowns",
        "scrub_pines",
        "bamboo_marks",
        "planted_trees",
        "pond_bank_trees",
        "wet_plots",
        "flooded_plots",
        "bund_junctions",
        "footbridges",
        "knobs",
        "clearings",
        "gates",
        "wall_tower_keepclears",
    }
)

_MATRIX_PARENT_FIELD = {
    "gardens": "of",
    "threshing_yards": "of",
    "farm_sheds": "of",
    "farm_fixtures": "of",
    "persimmons": "of",
    "byres": "of",
    "retirement_houses": "of",
    "storehouses": "of",
    "field_ditches": "field",  # a field's own irrigation, drawn ON it by design
    "fallow_patches": "field",  # a resting basin is one of its field's paddy plots (`rest_basin`)
    "channels": "field",  # the hairline feed from a field's source names the field it feeds (`_comb_source_channel`)
}
"""Records that name a parent.

Research:
    annexes name their house - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html, research/questions/0040-farm-storehouses-kura.drawing.html: may lie on it
    a field's own ditches and feed - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: drawn on the field they serve
    a resting plot in its field - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: one of the field's own plots
"""

# SIBLINGS OF ONE PARENT that may share ground, by key pair (feature 287, water W53). A resting basin (`fallow_patches`) is
# one of its field's paddy plots with grass where the rice would be, inside its own bunds, and the field's own ditches run
# along and between its plots by design - a ditch drawn ON its own paddy is what `field_ditches` is (the parent row above).
# The basin was classed GROUND, and ground is ruined by water standing in it, so the field's own lateral kissing its own
# resting basin's bund was refused as though a stranger's ditch had been cut through a dry crop: cohort seed 55 raised
# `OverlapRefused` for exactly that pair at (3058, 2342). Another field's ditch across a basin is still forbidden.
_MATRIX_SAME_PARENT_OK: dict[frozenset[str], str] = {
    frozenset(
        {"field_ditches", "fallow_patches"}
    ): "a field's own ditch runs along its own resting basin - the basin is one of the field's paddy plots, and a ditch is drawn ON its own paddy by design",
    # ...and the feed that traces the head race from the source to the fork lies along the same course as that ditch, so
    # it meets the same basin wherever the race does
    frozenset({"channels", "fallow_patches"}): "a field's own feed from its source traces its head race to the fork, along its own resting basin as the race does",
    # ...and two of its resting basins side by side share the bund between them, as any two of its plots do (the Rust stage gate's
    # seed 802010 raised `OverlapRefused` for a basin beside its field's other at (2279, 2539)); another field's basin still may not
    frozenset({"fallow_patches"}): "two of a field's resting basins side by side share the bund between them, as any two of its paddy plots do",
}
"""Research:
    ditch along its resting plot - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: a field's own ditch and feed may meet its resting plot
    resting plots side by side - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: two to four whole plots of one field rested, each inside its own bunds, so two neighbors share one
"""


def matrix_policy(ka: str, kb: str) -> str | None:
    """The reason this pair may overlap, or None if FORBIDDEN. Unclassified keys abstain here and
    are reported by the ratchet check instead. ANNEX x ANNEX resolves to None here on purpose: the
    permission is conditional on a SHARED PARENT, which only the caller can test."""
    ca, cb = OVERLAP_CLASS.get(ka), OVERLAP_CLASS.get(kb)
    if ca is None or cb is None:
        return "unclassified"
    # A FIXTURE may overlap ONLY what it declares itself mounted on (_FIXTURE_MOUNTS), by class or by
    # key - never anything else, and never another fixture unless that key is named. This replaces a
    # blanket permissive class that made ten keys invisible; see that registry's comment.
    pk_first = _MATRIX_ALLOWED_KEYS.get(frozenset({ka, kb}))
    if pk_first:
        return pk_first
    if "FIXTURE" in (ca, cb):
        for fk, ok, oc in ((ka, kb, cb), (kb, ka, ca)):
            if OVERLAP_CLASS.get(fk) != "FIXTURE":
                continue
            mounts = _FIXTURE_MOUNTS.get(fk, frozenset())
            if ok in mounts or oc in mounts:
                return f"{fk} is mounted on {ok} by design"
        return None
    for cls, why in _MATRIX_PERMISSIVE.items():
        if cls in (ca, cb):
            return why
    if ka == kb and ka in _MATRIX_SAME_KEY_OK:
        return _MATRIX_SAME_KEY_OK[ka]
    if ca == cb:
        return _MATRIX_SAME_CLASS_OK.get(ca)
    return _MATRIX_ALLOWED_PAIRS.get(frozenset({ca, cb}))


def _mx_same(a: Any, b: Any) -> bool:
    """Does a parent reference point at this record? Tolerant, because a parent is stored as a
    rounded coordinate pair and the child's own id is rounded independently.

    Research:
        its salts, guards and sentinels - NONE: they decide nothing about the place - 1.5 (same-point tolerance)
    """
    if a is None or b is None:
        return False
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)) and len(a) == 2 and len(b) == 2:
        return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1])) <= 1.5
    return bool(a == b)


# THE OUTSTANDING LIST (2026-07-26). Real defects the matrix found on its first pool-wide run,
# itemized BY MAP AND COORDINATE so the gate can be green while they are worked down. This is
# deliberately NOT a blanket grandfather list: every class PAIR is classified (that was the point of
# the feature), these are individual map defects, and because each entry names a position a NEW
# defect of the same kind is still caught. Every line here is work owed, not a permission.
_MATRIX_OUTSTANDING: dict[str, dict[tuple[str, str], int]] = {
    # Keyed by (map, PAIR) with a COUNT - not by coordinate, which proved brittle to regeneration.
    # Every line is WORK OWED, not a permission.
    #
    # 2026-07-26 final: the matrix found 11 defects across 6 maps on its first pool run, and ALL
    # ELEVEN are now fixed. What is left belongs to another session.
    #
    # (Minami's five were recorded here while it was another session's work in progress; all five are
    # fixed and the entry is gone. A line left here after its defect is fixed does not just rot - it
    # TOLERATES that many real defects on that map for ever after, which is why the guard below now
    # fails on one.)
}
