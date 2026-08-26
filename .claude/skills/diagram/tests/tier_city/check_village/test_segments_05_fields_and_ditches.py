"""tier city tests split out of `tests.check_village.test_segments_05_fields_and_ditches` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _city_dead,
    _supply_M,
    f,
    f_only,
)


@pytest.mark.tiers("city")
def test_field_ditches_ground_via_the_moat():
    # a MOATED city's combs ground at the moat both ways: the supply taps it (frm=moat is a SOURCE -
    # it is a fed watercourse, per city_moat_irrigates_fields) and a collector may empty into it
    # (to=moat is a SINK - the moat is the city's storm drain). Added for Tango's comb-field port.
    M = {
        "field_ditches": [{"poly": [[300, 300], [500, 300]], "role": "main", "field": "f"}, {"poly": [[300, 600], [500, 600]], "role": "drain", "field": "f"}],
        "channels": [
            {"poly": [[290, 296], [304, 308]], "frm": {"kind": "moat"}, "to": {"kind": "field", "name": "f"}, "w": 2.5},
            {"poly": [[494, 596], [520, 612]], "frm": {"kind": "drain"}, "to": {"kind": "moat"}, "w": 2.5},
        ],
    }
    assert "field_ditches_reach_source_and_sink" not in f_only(M, "field_ditches_reach_source_and_sink")


@pytest.mark.tiers("city")
def test_field_supply_visibly_sourced_passes_on_a_moat_bank():
    # a comb origin on the moat bed is sourced (the moat-fed city-comb pattern)
    M = _supply_M([450, 110])
    M["streams"] = []
    M["moat"] = [[100, 100], [800, 100], [800, 105]]
    M["moat_width"] = 26
    assert "field_supply_visibly_sourced[x]" not in f(M)


@pytest.mark.tiers("city")
def test_city_graveyard_count_fires_when_too_few():
    assert "city_graveyard_count" in f_only(_city_dead(cems=[(300, 300)]), "city_graveyard_count")


@pytest.mark.tiers("city")
def test_city_graveyard_count_fires_when_too_many():
    assert "city_graveyard_count" in f_only(_city_dead(cems=[(300, 300), (350, 300), (400, 300), (700, 300), (100, 100)]), "city_graveyard_count")


@pytest.mark.tiers("city")
def test_city_graveyard_count_passes_at_three():
    assert "city_graveyard_count" not in f_only(_city_dead(), "city_graveyard_count")
