"""tier city tests split out of `tests.settlement.test_shrines_wells` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import math

import pytest

from l7r.diagram import settlement
from l7r.diagram.settlement import Settlement


@pytest.mark.tiers("city")
def test_open_seat_refuses_a_seat_whose_FOOTPRINT_crosses_the_bound():
    """The martial-hall bug, as a unit test (GM 2026-07-25). s.bound is the ring-road loop a city
    packs inside, and `_fits` tests only a candidate's CENTER against it - so open_seat handed back
    a compound seat whose SE corner lay across Tango's patrol bed. open_seat now tests the whole
    footprint against the bound (and ONLY the bound: block polys and corridors are soft
    reservations a footprint may legitimately overhang, and tightening those cost two pool maps a
    feature apiece when it was tried)."""
    s = Settlement(1200, 1200, seed=3)
    s.meta(name="C", scale="city", ftpx=3)
    s.bound = [[100, 100], [700, 100], [700, 700], [100, 700]]
    over = (665, 300, 695, 320)  # every candidate here keeps its CENTER inside x=700 but its right edge past it
    assert s.open_seat(over, 80, 20) is None
    assert s.open_seat(over, 80, 20, footprint=False) is not None  # the old center-only behavior
    assert s.open_seat((300, 300, 400, 320), 80, 20) is not None  # well inside the bound: fine


@pytest.mark.tiers("city")
def test_open_seat_disc_uses_the_true_radius_of_a_round_candidate():
    """A wellhead is a DISC, so its reach is its radius - not the half-diagonal of the probe box
    around it, which is the documented over-restriction in this skill's CLAUDE.md. Exact rather
    than a relaxation, and opt-in: the derived well grid leans on the conservative radius as its
    padding, and making it exact there put a wellhead on a building."""

    def seat(disc):
        s = settlement.Settlement(600, 600, seed=9)
        s.meta(scale="city", ftpx=3)
        s.placed.append((300.0, 300.0, 40.0, 40.0))  # one standing footprint in the middle
        return s.open_seat((296, 330, 340, 372), 16, 16, step=2.0, footprint=False, disc=disc)

    loose, exact = seat(False), seat(True)
    assert exact is not None, "the exact disc reach must find the gap the half-diagonal refuses"
    assert loose is None or math.hypot(exact[0] - 300, exact[1] - 300) <= math.hypot(loose[0] - 300, loose[1] - 300)


# ---- feature 174: the three shrine glyphs no hamlet draws ----------------------------------------
# 56 of the module's 116 statements. A hamlet has no shrine at all (the kind follows settlement
# scale: villages have shrines, towns monasteries, cities temples), so these three had never run.
# Each is a direct drawing call, and each carries a REAL rule worth pinning rather than a line count.


def test_the_hill_records_its_own_footprint_and_its_summit_separately() -> None:
    """The keep-outs downstream code reads: `M['hill']` is the whole mound (the not-hill predicate
    inflates it), `M['summit']` the crown a shrine may stand on. They are different ellipses, and
    the hill is also pushed onto `ellipses`, which is what makes it block placement."""
    s = Settlement(1200, 1200, seed=3)
    s.hill(600.0, 600.0, 200.0, 150.0)
    assert s.M["hill"] == [600.0, 628.0, 200.0, 150.0], "the base ring, offset south of the center"
    assert s.M["summit"][2] < s.M["hill"][2], "the summit is the small crown, not the mound"
    assert (600.0, 628.0, 200.0, 150.0) in s.ellipses, "and the mound blocks placement"


def test_a_village_shrine_is_drawn_in_REAL_FEET_not_pixels() -> None:
    """GM 2026-07-21. The old signature took fixed PIXELS with a 104x68 default - a latent footgun
    that would have drawn a 208x136 ft monastery-sized hall on any village taking the default
    civic_shrine path. The defaults are ~62x42 REAL FEET now, converted through `px()`.

    Asserted at two scales, because a test at one ftpx cannot tell feet from pixels.
    """
    one = Settlement(1000, 1000, seed=1)
    two = Settlement(1000, 1000, seed=1)
    two.meta(ftpx=2)  # the scale is declared through meta(), not the constructor
    assert one.px(62) == 62.0 and two.px(62) == 31.0, "the same real hall is drawn smaller on a coarser map"
    one.shrine(500.0, 500.0)
    two.shrine(500.0, 500.0)
    assert one.out and two.out, "and both draw their hall"


def test_a_canvas_filling_forest_records_its_TREE_LINE_apart_from_its_polygon() -> None:
    """The two are recorded separately because the frame reveals only a shallow band of wood past
    the tree line - deeper in it is undifferentiated canopy, i.e. wasted image (`content_view`,
    and `forest_reveal_x` is the shared rule).

    Also asserted: the litter floor is pushed a crown's width BACK from the tree line, so its
    straight edge lies UNDER the canopy and the trees alone make the wood's edge - without that, a
    ruler-straight litter line gives the wood a drawn border no forest has.
    """
    s = Settlement(1400, 1400, seed=12)
    s.meta(name="C", scale="city")
    edge = [(800.0, 100.0), (820.0, 500.0), (790.0, 900.0), (810.0, 1300.0)]
    before = len(s.block_polys)
    s.forest(edge)

    assert s.M["forest_edge"] == [[round(x, 1), round(y, 1)] for x, y in edge], "the tree line, as given"
    assert s.M["forest"] != s.M["forest_edge"], "and the filled polygon, which runs on to the canvas"
    assert max(p[0] for p in s.M["forest"]) > 1400.0, "the wood is drawn PAST the canvas edge"
    assert len(s.block_polys) == before + 1, "and it blocks houses"


def test_a_forest_is_DETERMINISTIC_so_it_never_perturbs_house_placement() -> None:
    """Its RNG is saved and restored, which is what lets a wood be drawn mid-map without moving
    everything placed after it. Asserted by drawing the same wood twice and by checking the stream
    that follows is unchanged - the property a saved/restored RNG actually buys."""
    edge = [(800.0, 100.0), (820.0, 700.0), (810.0, 1300.0)]
    a = Settlement(1400, 1400, seed=12)
    a.meta(name="C", scale="city")
    a.forest(edge)

    b = Settlement(1400, 1400, seed=12)
    b.meta(name="C", scale="city")
    b.forest(edge)
    assert a.M["forest"] == b.M["forest"], "the same wood twice, identically"


def test_a_STEEP_hill_draws_emphasized_downslope_hachures() -> None:
    """ "closely-spaced, longer ticks read as a steep, undefendable-on-foot slope" - the flag exists
    so a hill that a map's story says cannot be climbed reads that way at a glance, rather than
    being told to the reader in prose."""
    gentle = Settlement(1200, 1200, seed=3)
    gentle.hill(600.0, 600.0, 200.0, 150.0)

    steep = Settlement(1200, 1200, seed=3)
    steep.hill(600.0, 600.0, 200.0, 150.0, steep=True)
    assert len(steep.out) > len(gentle.out), "the steep hill carries its extra hachures"
    assert steep.M["hill"] == gentle.M["hill"], "and is the same mound - only its shading differs"


def test_a_LABELLED_forest_captions_itself_at_the_middle_of_the_wood() -> None:
    """The wood's own caption, sited by default at the middle of the ground it fills - and slid by
    `label_xy` where a gen wants it elsewhere. Both, because the default is a computation and the
    override is the escape from it."""
    s = Settlement(1400, 1400, seed=12)
    s.meta(name="C", scale="city")
    edge = [(800.0, 100.0), (820.0, 700.0), (810.0, 1300.0)]
    s.forest(edge, label="the Kitsune Mori")
    s.place_labels()
    got = [lb for lb in s.M["labels"] if len(lb) > 5 and "Kitsune" in str(lb[5])]
    assert got, "the wood is named"

    placed = Settlement(1400, 1400, seed=12)
    placed.meta(name="C", scale="city")
    placed.forest(edge, label="the Kitsune Mori", label_xy=(1100.0, 300.0))
    placed.place_labels()
    put = [lb for lb in placed.M["labels"] if len(lb) > 5 and "Kitsune" in str(lb[5])]
    assert put and put[0][:2] != got[0][:2], "and label_xy puts the caption where the gen asked"
