"""Gate segments (justice grounds and land fall; keys 0555_000-0561) - bodies verbatim, registry order preserved."""

from typing import Any

from .common_03_capacity import _UNBOUND, _kept

# A MAP MUST DECLARE ITS LAND FALL (GM 2026-07-25). This closes the hole that let the whole
# problem happen: the drainage-slope block, `downhill_direction_valid` and `marsh_on_low_ground`
# are ALL gated on a fall being declared, and the code's own comment said "maps without the tag
# are exempt (slope unknown)" - so the two provincial cities, which declared none, silently
# skipped every one of those checks for months and nobody could tell from a green gate. Exempt
# is exactly what a map must not be. Either form counts: a map-level `meta(down_deg)`, or a
# per-field fall on every paddy (which is what a settlement ringed by farmland needs, since its
# fans drain several ways at once and no single bearing describes them).


def _seg_0557___lf_paddies(*, M: Any = _UNBOUND, f: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 557 (_lf_paddies, f) - body verbatim from the legacy gate() (feature 022)."""
    _lf_paddies = [f for f in M.get("fields") or [] if f.get("kind") == "paddy"]
    return _kept(locals(), ('_lf_paddies', 'f'))


def _seg_0558__settlement_declares_a_land_fall(
    *, M: Any = _UNBOUND, _lf_missing: Any = _UNBOUND, _lf_paddies: Any = _UNBOUND, check: Any = _UNBOUND, f: Any = _UNBOUND, meta: Any = _UNBOUND
) -> dict[str, Any]:
    """Gate segment 558 (settlement_declares_a_land_fall) - body verbatim from the legacy gate() (feature 022)."""
    if _lf_paddies or M.get("field_ditches"):
        _lf_missing = [f.get("name") for f in _lf_paddies if f.get("down_deg") is None]
        check(
            "settlement_declares_a_land_fall",
            meta.get("down_deg") is not None or (bool(_lf_paddies) and not _lf_missing),
            f"no land fall declared - give the map a meta(down_deg=...) or a per-field fall on every paddy "
            f"(paddies without one: {_lf_missing}). Every drainage-slope rule is gated on this, so a map that "
            f"declares nothing SKIPS them all and still shows a green gate - which is how both provincial "
            f"cities went unvalidated. Water flow (meta water_flow) is a separate declaration and does not substitute",
        )
    return _kept(locals(), ('_lf_missing', 'f'))


# WATER FLOW DIRECTION (GM 2026-07-24; the "why" lives in settlements.md "WATER FLOW").
# Every map declares a DRAINAGE BEARING - where this landscape sends its water - and every
# watercourse declares which way it runs. Before this, direction lived only in gen docstrings,
# so no check could read it and "downstream" was unverifiable; the tannery work is what
# exposed the gap. Angles use the same convention as down_deg (0 = east, 90 = south).
