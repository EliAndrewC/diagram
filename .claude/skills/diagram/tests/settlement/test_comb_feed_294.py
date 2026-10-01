"""Feature 294 B1: the pond's feed record traces its drawn inlet stub (`settlement/fields/comb.py`, `feed_stub`)."""

from __future__ import annotations

from l7r.diagram.settlement.fields.comb import feed_stub

ENVELOPE = [(0.0, 100.0), (200.0, 100.0), (200.0, 300.0), (0.0, 300.0)]


def test_the_stub_runs_from_the_last_point_inside_the_crop_to_the_rim() -> None:
    race = [(180.0, 120.0), (20.0, 110.0), (10.0, 104.0), (8.0, 40.0)]  # the ring, its corner inside, then the stub out to the rim
    assert feed_stub(race, ENVELOPE) == [(10.0, 104.0), (8.0, 40.0)]


def test_with_no_envelope_or_no_point_inside_it_the_last_leg() -> None:
    race = [(0.0, 0.0), (5.0, 5.0), (9.0, 9.0)]
    assert feed_stub(race, []) == [(5.0, 5.0), (9.0, 9.0)]
    assert feed_stub(race, ENVELOPE) == [(5.0, 5.0), (9.0, 9.0)]
