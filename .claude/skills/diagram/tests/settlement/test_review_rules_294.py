"""Feature 294's engine fixes, as unit tests: B1, the pond's feed record traces its drawn inlet stub (`settlement/fields/comb.py`,
`feed_stub`); B10, a layout whose lot found no seat for a part is refused by the nucleated placer (`rolling/fit.py`)."""

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


def test_a_layout_whose_lot_found_no_seat_for_a_part_is_refused_by_the_parts_too() -> None:
    """Feature 294 B10: the nucleated placer judges a layout's parts with `_parts_fit`, which refuses an `unlaid` layout as
    `_bundle_side_fits` does - Kuwabata seated three households bare before it did."""
    from l7r.diagram.settlement.rolling.fit import BundleFitMixin

    assert BundleFitMixin._parts_fit(object(), {"unlaid": "a bath room found no place"}) is False  # type: ignore[arg-type]
