"""Town, city and capital segments moved out of `segments_05a_field_cover_and_cremation.py` by feature 145.

The GM ruled on 2026-08-28 that the hamlet path owes 100% coverage and the other tiers owe none while
nothing exercises them - and the floor is MODULE level, so a city segment sharing a file with a hamlet
segment put its whole body under the hamlet floor. Execution order is by the segment's numeric key
(`registry._ordered_names`), never by file, so moving one costs nothing and needs no placement row."""

from typing import Any

from .common_01_geometry import point_in_poly
from .common_03_capacity import _UNBOUND, _kept


def _seg_0286_000__cems(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0286.000 (cems) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital'):
        cems = M.get("cemeteries", [])
    return _kept(locals(), ('cems',))


def _seg_0286_007__wall(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0286.007 (wall) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital'):
        wall = M.get("wall")
    return _kept(locals(), ('wall',))


def _seg_0286_008___inside(*, px: Any = _UNBOUND, py: Any = _UNBOUND, scale: Any = _UNBOUND, wall: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0286.008 (_inside) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital'):

        def _inside(px: float, py: float) -> bool:
            return bool(wall) and point_in_poly(px, py, wall)

    return _kept(locals(), ('_inside',))


def _seg_0286_018__pond(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0286.018 (pond) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital'):
        pond = M.get("pond")
    return _kept(locals(), ('pond',))
