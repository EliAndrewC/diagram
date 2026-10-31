"""Feature 294's engine fixes, as unit tests: B1, the pond's feed record traces its drawn inlet stub (`settlement/fields/comb.py`,
`feed_stub`); B10, a layout whose lot found no seat for a part is refused by the nucleated placer (`rolling/fit.py`)."""

from __future__ import annotations

ENVELOPE = [(0.0, 100.0), (200.0, 100.0), (200.0, 300.0), (0.0, 300.0)]


def test_a_layout_whose_lot_found_no_seat_for_a_part_is_refused_by_the_parts_too() -> None:
    """Feature 294 B10: the nucleated placer judges a layout's parts with `_parts_fit`, which refuses an `unlaid` layout as
    `_bundle_side_fits` does - Kuwabata seated three households bare before it did."""
    from l7r.diagram.settlement.rolling.fit import BundleFitMixin

    assert BundleFitMixin._parts_fit(object(), {"unlaid": "a bath room found no place"}) is False  # type: ignore[arg-type]
