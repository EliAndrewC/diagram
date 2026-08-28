"""Town, city and capital segments moved out of `segments_02c_walls_gates_and_housing.py` by feature 145.

The GM ruled on 2026-08-28 that the hamlet path owes 100% coverage and the other tiers owe none while
nothing exercises them - and the floor is MODULE level, so a city segment sharing a file with a hamlet
segment put its whole body under the hamlet floor. Execution order is by the segment's numeric key
(`registry._ordered_names`), never by file, so moving one costs nothing and needs no placement row."""

from typing import Any

from .common_03_capacity import (
    _UNBOUND,
    _kept,
)


def _seg_0133_006__ADJ(*, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0133.006 (ADJ) - body verbatim from _seg_0133__outside_fields_farmhouse_density (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city', 'capital'):
        ADJ = 165
    return _kept(locals(), ('ADJ',))
