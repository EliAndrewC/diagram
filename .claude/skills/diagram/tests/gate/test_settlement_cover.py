"""The ground cover a rolled hamlet must produce (feature 166): what is left of it after feature 287.

Feature 166 carried six rules here that the retired battery re-measured on every finished map. Feature 287 moved five into
their placers, each with a unit test on the violating case, and retired their finished-map tests with the woodland
fixture only they read (specs/287-placer-guarantees/research.md R8): the woodland commons stocked, on dry ground and
mostly inside the picture (`hamletgen/hinterland/parcels.py:open_ground_patches`, `land/cover.py:commons`), the dooryard
copse clear of the belt and no canopy over open water (`homestead_parts/stands.py:village_grove`).

KEPT, because no placer guarantees it yet: `village_groves_visibly_stocked`. The copse is held to its stocking
(`stands.py`, `stocked_copse`), but the windbreak's and the water mouth's records keep the requested polygon's size with
no placer deciding their density, and `settlement/core.py:_partition_grove_clumps` (called by `set_view`) moves the
off-page clumps out of a grove without re-recording its size.
"""

from __future__ import annotations

import pytest

from tests import rolls
from tests.gate import _pool

SPEC = rolls.REFERENCE  # the pool's brief (feature 215)

MIN_CLUMP_DENSITY = 1.5
"""Clumps per 100k square pixels. Below this the grove is a declared outline with almost nothing in it."""


@pytest.fixture(scope="module")
def rolled():
    return _pool.rolled_map(SPEC)


def test_every_recorded_grove_holds_trees(rolled) -> None:
    """`village_groves_visibly_stocked`. The same failure as the woodland rule, one feature over: a grove
    that DECLARES an outline and draws almost nothing in it leaves the dooryards it should have greened
    bare while every other grove rule reads green."""
    _plan, M = rolled
    groves = [g for g in (M.get("village_groves") or []) if float(g.get("w") or 0) * float(g.get("h") or 0) > 0]
    assert groves, "the roll recorded no grove, so this rule would judge nothing"
    bare = []
    for g in groves:
        area = float(g["w"]) * float(g["h"])
        n = len(g.get("clumps") or [])
        dens = n * 1e5 / area
        if dens < MIN_CLUMP_DENSITY:
            bare.append(f"{g.get('role') or 'grove'} {float(g['w']):.0f}x{float(g['h']):.0f}px holds {n} clump(s) ({dens:.2f}/100k)")
    assert not bare, f"{len(bare)} recorded grove(s) hold almost no trees: {bare[:3]}"
