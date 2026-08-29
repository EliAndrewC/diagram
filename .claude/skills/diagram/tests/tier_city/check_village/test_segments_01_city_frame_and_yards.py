"""tier city tests split out of `tests.check_village.test_segments_01_city_frame_and_yards` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import check_village
from tests.check_village._builders import (
    _gate_parts,
    f_only,
)


@pytest.mark.tiers("city")
def test_guard_box_on_the_ward_fence_is_a_defect_though_the_gateway_on_it_is_not():
    # GM 2026-07-27: "ward gates seem to sometimes overlap with neighborhood walls". The GATEWAY
    # stands on the fence - the gate IS the opening. The guard box is a building on the verge and
    # rides no such permission, so a fence drawn through it is a defect.
    thru_gateway = {"meta": {"scale": "city"}, "kido": [_gate_parts()], "wards": [{"name": "samurai", "boundary": [[400, 300], [400, 700]]}]}
    assert not [v for v in check_village.matrix_violations(thru_gateway) if "kido_guard_box" in (v[0], v[1])]
    thru_box = {"meta": {"scale": "city"}, "kido": [_gate_parts()], "wards": [{"name": "samurai", "boundary": [[300, 520], [700, 520]]}]}
    assert [v for v in check_village.matrix_violations(thru_box) if "kido_guard_box" in (v[0], v[1])]
    assert "features_do_not_overlap" in f_only(thru_box, "features_do_not_overlap")
