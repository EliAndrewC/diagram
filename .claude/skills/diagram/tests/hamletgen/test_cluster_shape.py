#!/usr/bin/env python3
"""The rolled `cluster_shape` must bind, and must not be declared where it did not.

Background: over 48 cohort seeds and all four pool hamlets, `cluster_shape` was rolled, printed in
every cohort-audit header, and HONORED ON ONE (seed 34). It fed only the cloud seeding pass, which
runs for households the front rows do not seat - and the rows seat everyone on 47 of 48 seeds. Round,
elongated and crescent all drew the same 3:1 band."""

import math

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.homesteads import cluster_aspect

# THE TWIN LOST ITS OTHER HALF (feature 166). Two tests here used to pin the GATE's copy of
# `CLUSTER_DRAWN_ASPECT` against the generator's - one comparing the source text, one comparing the
# answers on the same point sets - because the gate could not import the generator and so restated the
# table. With the battery retired there is ONE table, in `hamletgen.consts`, and a duplicate that
# cannot exist needs no pin. What survives is everything that was about the MEASURE rather than about
# the duplication: rotation invariance, the diagonal string, the degenerate cluster, and the ordering
# of the bands - which is the half that was always load-bearing.


def test_every_rollable_shape_has_a_band_a_row_span_and_a_drawn_range() -> None:
    """A shape that can be ROLLED but has no entry falls back to the crescent default, which is how a
    knob silently stops binding for one of its values - the exact defect this feature fixed."""
    for shape in set(hg.consts.CLUSTER_SHAPES):
        assert shape in hg.consts.CLUSTER_BAND_ASPECT, f"{shape} can be rolled but has no band aspect"
        assert shape in hg.consts.CLUSTER_ROW_SPAN, f"{shape} can be rolled but has no row span"
        assert shape in hg.consts.CLUSTER_DRAWN_ASPECT, f"{shape} can be rolled but has no drawn range"


def test_the_drawn_ranges_admit_the_band_they_are_meant_to_describe() -> None:
    """Ordering sanity, in the observable's own units: round must not reach as long as elongated's
    floor, or the two words describe the same picture and the knob buys no variance at all."""
    rnd = hg.consts.CLUSTER_DRAWN_ASPECT["round"]
    lng = hg.consts.CLUSTER_DRAWN_ASPECT["elongated"]
    assert rnd[0] >= 1.0, "an aspect ratio below 1.0 is not a shape, it is a swapped axis"
    assert rnd[1] < lng[0], "round's ceiling must sit below elongated's floor or the shapes are indistinguishable"
    for shape, (lo, hi) in hg.consts.CLUSTER_DRAWN_ASPECT.items():
        assert lo < hi, f"{shape} has an empty drawn range"


def test_the_drawn_aspect_does_not_care_which_way_the_field_margin_points() -> None:
    """Rotation invariance, asserted rather than assumed - it is the property the whole fix is for."""
    xs = [0.0, 100.0, 200.0, 300.0, 150.0]
    ys = [0.0, 10.0, -10.0, 0.0, 40.0]
    flat = hg.homesteads.cluster_aspect(xs, ys)
    for deg in (17.0, 45.0, 63.0, 90.0, 134.0):
        th = math.radians(deg)
        rx = [x * math.cos(th) - y * math.sin(th) for x, y in zip(xs, ys, strict=True)]
        ry = [x * math.sin(th) + y * math.cos(th) for x, y in zip(xs, ys, strict=True)]
        turned = hg.homesteads.cluster_aspect(rx, ry)
        assert abs(turned - flat) < 0.02 * flat, f"aspect changed from {flat:.2f} to {turned:.2f} when the cloud was turned {deg} deg"


def test_a_perfectly_diagonal_string_is_not_recorded_as_round() -> None:
    """The defect itself, pinned. If this reads near 1.0, the page-axis bbox measure has been restored."""
    diag = [0.0, 70.7, 141.4, 212.1, 282.8]
    assert hg.homesteads.cluster_aspect(diag, list(diag)) > 10.0, "a diagonal string must measure as extremely elongated"


def test_a_cluster_of_fewer_than_two_houses_has_no_aspect() -> None:
    """The degenerate guard. One house has no axis and no proportion, so the only
    honest answer is 1.0 - and a covariance over a single point is a divide-by-nothing waiting to
    happen.

    Held because no map in the corpus has fewer than two houses, so this branch never executes during
    a pool or cohort run and its coverage would depend entirely on a generator being re-run. That is
    the same cache-dependent, tested-by-luck state four other branches were in before today."""
    for xs, ys in (([], []), ([100.0], [200.0])):
        assert cluster_aspect(xs, ys) == 1.0, f"the measure gave a proportion for {len(xs)} house(s)"
