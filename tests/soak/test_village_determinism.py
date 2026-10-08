"""THE VILLAGE ROLL'S DETERMINISM, in the tier ABOVE the gate (feature 221, GM 2026-09-09: "Ask `make roll-audit`
whether they still carry lines nothing else reaches; if not, feature 216's doctrine moves them to the soak tier").

The audit's answer for this test was ONE line - `settlement/_geom/water_index.py`'s grid-path refusal in
`WaterIndex.clear` - for two 6.7 s village rolls, the longest tests in the gate. That line is a unit test now
(`tests/settlement/test_geom.py`), and what is left here is a real-map behavior no coverage line requires: the same
seed rolls the same combination byte for byte, a different seed a different one, and a rolled map is populated with
no hand-placed coordinates. Nothing ordinary collects this tree (`norecursedirs`); `make soak` runs it.
"""

from __future__ import annotations

import pytest

from l7r.diagram.settlement import Settlement


@pytest.mark.rolls_map
def test_roll_village_is_deterministic_and_seed_varies_the_combination():
    # US2 (SC-004): the same seed rolls the SAME combination (byte-identical), a different seed rolls a
    # DIFFERENT one, and a rolled map is populated with no hand-placed coordinates.
    def roll(seed):
        s = Settlement(W=2000, H=2600, seed=seed)
        s.meta(name="R", scale="hamlet", ftpx=1, toscale=True, households=18, field_footbridges=True)
        return s, s.roll_village("R", households=18, down_deg=90, water_kind="pond", field_fall=1260)

    s7a, k7a = roll(7)
    _s7b, k7b = roll(7)
    assert k7a == k7b  # same seed -> identical roll
    _s8, k8 = roll(8)
    combo = ("cluster_position", "cluster_shape", "lane_skeleton", "water_source_position")
    assert tuple(k7a[c] for c in combo) != tuple(k8[c] for c in combo)  # different seeds -> different combination
    assert 15 <= len(s7a.M["houses"]) <= 19 and s7a.M["fields"] and s7a.view  # a populated, framed map
