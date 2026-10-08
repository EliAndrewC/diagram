def test_s_on_side_falls_back_to_the_nearer_end_of_the_ring_side():
    """The position guess for a lateral's end. When the lateral's column line falls INSIDE a span the
    answer is the interpolation; when it falls past the side entirely - a grid wider than its own ring,
    which a well-formed polder never rolls - the nearer end of the side is the honest answer."""
    from l7r.diagram.waterfields.polder import s_on_side

    side = [(0.0, 0.0), (100.0, 50.0), (200.0, 100.0)]
    assert s_on_side(side, 25.0) == 50.0, "halfway along the first span"
    assert s_on_side(side, 500.0) == 200.0, "past the far end: the far end"
    assert s_on_side(side, -500.0) == 0.0, "past the near end: the near end"
