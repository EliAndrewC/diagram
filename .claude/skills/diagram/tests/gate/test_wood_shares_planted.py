"""Every household's reserved share of the wood floor is planted where it was reserved (feature 287, woods W25; plan D9).

The seating reserves each household's copse seats clear of every keep-out the copse plants by (`wood_share.copse_keepouts`),
and other homesteads and their paths are kept off them, so the copse can plant every one first (`village_grove`'s `seats`).
A seat the planting then refuses is ground held for trees that are never drawn. Feature 310 added the afternoon sun lane west of
every yard and bed to the copse's keep-outs but not to the reservation, and the shipped hamlets lost 16-34 seats each. On
Inashiro a neighbor's path, routed round two of those seats, bulged 27 ft round bare scrub (feature 317, the village lane
glyph check's round 3, F5). Read through the pool's gen cache.
"""

from __future__ import annotations

import json
import math
import os

import pytest

from tests.gate import _pool

#: The shipped hamlets whose seating reserves the wood floor; Kashikawa and Mizuguchi reserve none.
SEATED = ("inashiro", "kuwabata", "sawada")


@pytest.mark.parametrize("name", SEATED)
def test_every_reserved_wood_seat_is_planted_where_it_was_reserved(name: str) -> None:
    """Non-vacuous first: households carry reserved seats and the copse records clumps. Then a copse clump stands on every
    seat, at the record's grain."""
    with open(_pool.obtain(os.path.join(_pool.HERE, f"pool/hamlets/{name}/{name}.gen.py")), encoding="utf-8") as fh:
        M = json.load(fh)
    seats = [(i, (float(q[0]), float(q[1]))) for i, h in enumerate(M["houses"]) for q in (h.get("wood_share") or {}).get("seats") or ()]
    copse = [(float(c[0]), float(c[1])) for g in M.get("village_groves") or () if g.get("role") == "copse" for c in g.get("clumps") or ()]
    assert seats and copse, "non-vacuity: the map reserves seats and plants a copse"
    lost = [(i, q) for i, q in seats if min(math.dist(q, c) for c in copse) > 0.05]
    assert not lost, f"{len(lost)} of {len(seats)} reserved seats unplanted (house, seat): {lost[:4]}"
