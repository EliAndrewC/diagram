"""Gate segments (work yards and matrix; keys 0052-0096) - bodies verbatim, registry order preserved."""

from typing import Any

from .common_01_geometry import (
    _MATRIX_OUTSTANDING,
    _MX_NOT_GEOMETRY,
    OVERLAP_CLASS,
)
from .common_02_overlap_policy import matrix_violations
from .common_03_capacity import (
    _UNBOUND,
    _kept,
)

# `_fr_gap` is gone: it was feature 016's own exact footprint-gap helper, written before
# `edge_gap` existed and doing the same job by the same method. Two correct helpers for one
# question is how the three WRONG conventions got started, so the call sites now use edge_gap
# and take records rather than pre-built corner lists (GM, 2026-07-27). The only behavioral
# difference is that an overlap now reads 0.0 instead of -1.0, which every call site - all of
# them `< some_positive_gap` - treats identically.


# ===== THE OVERLAP MATRIX (feature 017) - one general rule in place of per-pair whack-a-mole.
# Every geometric key has a class; a class-by-class policy forbids by default; conditional
# permissions (an annex on its own parent, a canal serving its own hem) live in
# matrix_violations. Adding a feature = one line in OVERLAP_CLASS and it is protected against
# everything, which is the entire point (GM 2026-07-26).


def _seg_0058___mx_name(*, meta: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 58 (_mx_name) - body verbatim from the legacy gate() (feature 022)."""
    _mx_name = str(meta.get("name") or "")
    return _kept(locals(), ('_mx_name',))


def _seg_0059___mx_known(*, _mx_name: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 59 (_mx_known) - body verbatim from the legacy gate() (feature 022)."""
    _mx_known = _MATRIX_OUTSTANDING.get(_mx_name, {})
    return _kept(locals(), ('_mx_known',))


def _seg_0060___mx_seen() -> dict[str, Any]:
    """Gate segment 60 (_mx_seen) - body verbatim from the legacy gate() (feature 022)."""
    _mx_seen: dict[tuple[str, str], list[tuple[str, str, float, float]]] = {}
    return _kept(locals(), ('_mx_seen',))


def _seg_0061___mx_key(*, M: Any = _UNBOUND, _mx_key: Any = _UNBOUND, _mx_seen: Any = _UNBOUND, _v: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 61 (_mx_key, _mx_seen, _v) - body verbatim from the legacy gate() (feature 022)."""
    for _v in matrix_violations(M):
        _mx_key: tuple[str, str] = (min(_v[0], _v[1]), max(_v[0], _v[1]))  # type: ignore[no-redef]
        _mx_seen.setdefault(_mx_key, []).append(_v)
    return _kept(locals(), ('_mx_key', '_mx_seen', '_v'))


def _seg_0062___mx_bad(*, _mx_known: Any = _UNBOUND, _mx_seen: Any = _UNBOUND, pair: Any = _UNBOUND, v: Any = _UNBOUND, vs: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 62 (_mx_bad, pair, v, vs) - body verbatim from the legacy gate() (feature 022)."""
    _mx_bad = [v for pair, vs in _mx_seen.items() for v in vs[_mx_known.get(pair, 0) :]]
    return _kept(locals(), ('_mx_bad', 'pair', 'v', 'vs'))


def _seg_0063__features_do_not_overlap(*, _mx_bad: Any = _UNBOUND, a: Any = _UNBOUND, b: Any = _UNBOUND, check: Any = _UNBOUND, x: Any = _UNBOUND, y: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 63 (features_do_not_overlap) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "features_do_not_overlap",
        not _mx_bad,
        f"overlapping feature(s) whose classes forbid it: {[(a, b, x, y) for a, b, x, y in _mx_bad[:4]]} - the overlap MATRIX decides every pair from one classification (OVERLAP_CLASS + the policy above), so this is not a missing per-pair rule. Either the drawing is wrong, or the pair genuinely may overlap and needs a permission WITH ITS REASON in _MATRIX_PERMISSIVE / _MATRIX_SAME_KEY_OK / _MATRIX_ALLOWED_PAIRS / _MATRIX_ALLOWED_KEYS",
    )
    return _kept(locals(), ('a', 'b', 'x', 'y'))


# ...and the ratchet on the ratchet. An _MATRIX_OUTSTANDING line is WORK OWED, so once the defect
# it records is fixed the line does not merely rot - it goes on TOLERATING that many real
# overlaps of that pair on that map for ever, which is exactly the hole a debt register is
# supposed to close. (Minami's five outstanding pairs were fixed by the 016 session while the
# entry recording them stayed behind, so the map could have silently regressed on any of them.)
# Same rule, and same reason, as waivers_are_live.


def _seg_0064___mx_stale(*, _mx_known: Any = _UNBOUND, _mx_seen: Any = _UNBOUND, allow: Any = _UNBOUND, pair: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 64 (_mx_stale, allow, pair) - body verbatim from the legacy gate() (feature 022)."""
    _mx_stale = sorted(pair for pair, allow in _mx_known.items() if len(_mx_seen.get(pair, [])) < allow)
    return _kept(locals(), ('_mx_stale', 'allow', 'pair'))


def _seg_0065__matrix_debts_still_owed(*, _mx_name: Any = _UNBOUND, _mx_stale: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 65 (matrix_debts_still_owed) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "matrix_debts_still_owed",
        not _mx_stale,
        f"_MATRIX_OUTSTANDING still records {_mx_stale} for {_mx_name!r}, but the map no longer draws that many - the debt is PAID. Delete the line: left there it tolerates that many real overlaps of the pair for ever, which is the opposite of what a debt register is for",
    )
    return _kept(locals(), ())


# the ratchet: a drawn geometric key nobody classified
# DERIVED from the manifest, not from a hand list - a ratchet that enumerates its own keys is
# the same defect this feature exists to abolish, and it showed: the hand-listed version passed
# an unseen river city silently while TEN of its keys (bridges, jetties, kido, sluice_gates,
# wall_towers, water_gates, docks, inspection_stations, gate_structs, stable_yards) had no class
# at all. A key counts as drawn geometry when its records carry a position or an outline.


def _seg_0066___mx_unclassified(*, M: Any = _UNBOUND, c: Any = _UNBOUND, k: Any = _UNBOUND, v: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 66 (_mx_unclassified, c, k, v) - body verbatim from the legacy gate() (feature 022)."""
    _mx_unclassified = sorted(
        {
            k
            for k, v in M.items()
            if k not in OVERLAP_CLASS
            and k not in _MX_NOT_GEOMETRY
            and isinstance(v, list)
            and v
            and (
                (isinstance(v[0], dict) and ("x" in v[0] or "poly" in v[0] or "pts" in v[0]))
                # ...OR a bare POLYLINE / point list - how the wall, moat, ring road and torii are
                # stored. The first cut inspected only DICT records and so passed five unclassified
                # keys in silence: a ratchet that enumerates one record shape has the same blindness
                # this feature exists to abolish.
                or (isinstance(v[0], (list, tuple)) and len(v[0]) >= 2 and all(isinstance(c, (int, float)) for c in v[0][:2]))
            )
        }
    )
    return _kept(locals(), ('_mx_unclassified', 'c', 'k', 'v'))


def _seg_0067__every_feature_classified_for_matrix(*, _mx_unclassified: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 67 (every_feature_classified_for_matrix) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "every_feature_classified_for_matrix",
        not _mx_unclassified,
        f"drawn feature key(s) {_mx_unclassified} have no entry in OVERLAP_CLASS - give each one a class (SOLID / GROUND / WATER / WAY / ANNEX, or a permissive class WITH its reason) and it is governed against every other feature at once",
    )
    return _kept(locals(), ())


# ===== A COMPOUND'S OWN WALL KEEPS OFF THE WAYS (found by the settlement-review agent, 2026-07-26).
# `manors` sits in _OVERLAP_TARGETS - the registry of things OTHER features must avoid - and never
# in _OVERLAP_STRUCTS, so the whole no_structure_on_* battery reads a manor as a hazard and nothing
# reads it as a candidate. The compound's own wall was therefore ungoverned against the roadbed,
# and a trunk road duly ran 18 px inside a magistracy's south wall, 80 ft from its own gate, with
# the gate fully green. A wall standing in a public carriageway is the same defect as a house
# standing in one; it just had nobody watching for it.


# ===== NOTHING IS BUILT ON THE FAR SIDE OF A DRAWN BORDER (found by the settlement-review agent,
# 2026-07-26). A border is deliberately overlap-EXEMPT - a frontier magistracy stands its wall ON
# the line by design - but "the wall may sit on the line" is not "the settlement may build across
# it." Water and roads cross a jurisdiction freely; buildings, yards and gardens do not, because
# the ground on the far side belongs to somebody else. Ubame's own notes promised its cover was
# "kept west of the border" while three kitchen gardens and two commons reached 43 px past it.
# The test is on the CENTER, which is what keeps the deliberate case legal: the magistracy's
# center is on its own side and only its wall touches the line.


# ===== THE CHARCOAL DISTRICT'S TRADE WORKS (feature 016; full grounding in
# settlements/urban-features.md "CHARCOAL YARDS" and "REFINING FORGES", research in
# research/urban-features.md).
#
# The SEPARATION LADDER these two join, and why each rung sits where it does. Every figure is
# placed against the ones this project already uses rather than invented, because the whole
# value of a magic number is that a later reader can see what it was reasoned against:
#
#     ~6 ft   farrier from a stall range   sparks from an ATTENDED open forge onto hay
#      30 ft  charcoal yard from anything  a stack that self-heats UNATTENDED
#      60 ft  refining forge from homes    a live worked fire under forced blast, + noise/smoke
#      60 ft  kiln from anything           a days-long ATTENDED firing (see "THE KILN WORKS")
#     120 ft  crematory / tanning yard     putrefaction and smoke carried on the air
#
# NOTE THE SCOPING ASYMMETRY, which is deliberate. The two PRESENCE checks are gated on an
# opt-in meta knob (only a fuel or iron county should own one of these). The three SITING checks
# are gated on the FEATURE's presence instead, so a yard or forge drawn on ANY map - declared or
# not - is still fully validated. That is the mitigation for this file's standing hazard: "a
# check that never RUNS looks exactly like a check that passes."


# THE FIRE GAP. Charcoal self-heats: fresh charcoal absorbs oxygen fast enough to raise its own
# temperature to ignition, worst of all as tightly-packed fines, which is why the documented
# handling rule stands new stock in the open away from conditioned stock for at least 24 hours.
# The hazard is therefore an UNATTENDED ignition inside a large fuel mass - which is why 30 ft
# sits an order above the attended-forge figure and well below the nuisance figures: it is about
# one flame-height clear of a fully-involved 10-12 ft stack, the usual rule of thumb for radiant
# ignition of adjacent timber. It is emphatically NOT the 120 ft nuisance figure - that defends
# against smell carried on air, and borrowing it here would push the yard off the cart route
# that is its entire reason for existing.


# THE COOLING APRON is part of the record's contract, not decoration: a yard that put arriving
# loads straight under cover with the conditioned stock is the yard that burns down. A yard
# drawn without one is recording a layout nobody would build.


# ===== THE KILN WORKS (GM 2026-07-27; grounding in settlements/urban-features.md "KILN WORKS",
# research record in research/urban-features.md). The GM's two questions - "would whoever works
# the kiln also live next to it?" and "why is it specifically a tile kiln?" - turned a lone
# mound glyph into a works. The short answers the checks below enforce:
#
#   - THE WORKERS LIVE AT THE KILN. A firing runs for DAYS, stoked in shifts round the clock,
#     and the works stands at its CLAY rather than at its customers, so digging, weathering,
#     throwing, drying and firing all happen at one spot. China first: Song/Ming kiln districts
#     were worked by registered kiln households living at their kilns (Jingdezhen is a city
#     grown around them); Japan corroborates with Seto, Tokoname, Imado, Awataguchi.
#   - THE HOUSING IS NOT BANISHED WITH THE WORK. Fire law puts the kiln outside the wall
#     (city_kiln_outside_walls) to keep the risk out of the dense blocks; it says nothing
#     against the households whose trade it is. They keep the ordinary fire gap, no more.
#
# THE 60 FT RUNG on the separation ladder above is deliberate rather than new. A firing is a
# very large fire, but an ATTENDED one - somebody is stoking it, which is the whole reason it
# runs in shifts - so it sits with the refining forge (a live worked fire) and not with the
# unattended charcoal stack at 30 ft or the nuisance figures at 120 ft, where a smell carried
# on air is the hazard. Duration here does the work the forced blast does there.
#
# SCOPED ON THE FEATURE, NOT THE SCALE, like the charcoal-district siting checks and for the
# same reason: a kiln drawn on any map is validated, whatever it declares.


# TROUGH RECTS DRAW ON OPEN GROUND - the cluster's drawn BOX must not clip any structure (GM
# 2026-07-23, after Tango's caravan cluster hugged its well on a near-vertical ray and the
# bottom trough clipped the well-house roof corner: the old fixed offset only guaranteed
# HORIZONTAL clearance - the stack is taller than it is wide - and only the cluster CENTER was
# point-checked, so the rects themselves could land on footprints). Placement records the
# drawn extent as `troughs_box`; it is tested against every solid footprint (the yard's own
# keep kinds + houses, rotation-exact via SAT) and every wellhead roof square (vr). A yard
# with troughs but no recorded box fails - the extent is part of the record's contract.


# HITCHING RAILS + DUNG HEAPS keep off the ROADS and the WALL (GM 2026-07-24). The road-side
# rail's whole PURPOSE is keeping tethered stock off the through-road, so a rail whose drawn
# extent (posts included) reaches the roadbed defeats itself and bars the public way; a dung
# heap on the tread fouls it, and either against the rampart sits in the wall's patrol
# clearance. The old placement tested only each glyph's CENTER point, so an 18px rail could
# lay its tip on a road or against the wall; s._stable_yard now probes the full extent AND
# records the furniture ('rails' / 'dung_heaps' on each M['stable_yards'] entry) so this
# check can hold the drawn geometry to it.
