"""tier city tests split out of `tests.settlement.test_knobs` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import settlement
import math

from l7r.diagram.settlement.city.knobs import machi_mouths, moat_swept_tap


@pytest.mark.tiers("city")
def test_wall_tower_spacing_px_scales_with_tier():
    """The per-city defense tier sets the max mural-tower spacing. siege = aimed-lethal bowshot
    (197 ft), >=2 everywhere, so spacing == range; garrison = full war-bow (328 ft), >=2, so the
    wider range; peaceful keeps only >=1 flanking tower within aimed-lethal range, so its spacing
    is DOUBLE (a tower every 2*197 ft - the sparser Xi'an crossfire). At 3 ft/px (city scale):"""
    ppf = 1.0 / 3.0  # px per ft
    assert settlement.wall_tower_spacing_px(ppf, "siege") == 197.0 * ppf
    assert settlement.wall_tower_spacing_px(ppf, "garrison") == 328.0 * ppf
    assert settlement.wall_tower_spacing_px(ppf, "peaceful") == 2 * 197.0 * ppf
    # siege is tighter than garrison; peaceful is the loosest
    assert settlement.wall_tower_spacing_px(ppf, "siege") < settlement.wall_tower_spacing_px(ppf, "garrison")
    assert settlement.wall_tower_spacing_px(ppf, "peaceful") > settlement.wall_tower_spacing_px(ppf, "garrison")


# ---- feature 174: the two city knob functions, tested directly ------------------------------------


def test_machi_mouths_finds_where_a_street_ENTERS_a_ward_and_collapses_a_grazed_corner() -> None:
    """Research 021 item 6: Edo's machi-kido, Qing's zhalan - the ward mouths the kido mesh bars at
    night. THE SINGLE SOURCE for both the placer (`kido_mesh`) and the validator that checks it,
    the same doctrine as `bridge_carried_ways`: one function, so the two cannot disagree.

    Three rules, all asserted: only `machi` districts have mouths, out-wall SUBURB districts are
    skipped (their bar is the city gate itself), and mouths within 40 px collapse to one, because a
    street grazing a district corner is one entry rather than two.
    """
    ward = [(400.0, 400.0), (800.0, 400.0), (800.0, 800.0), (400.0, 800.0)]
    M = {
        "wall": [(200.0, 200.0), (1000.0, 200.0), (1000.0, 1000.0), (200.0, 1000.0)],
        "districts": [{"kind": "machi", "poly": ward}],
        "town_streets": [{"pts": [(0.0, 600.0), (1200.0, 600.0)], "w": 18}],
    }
    mouths = machi_mouths(M)
    assert len(mouths) == 2, f"the street enters and leaves: two mouths, one per side ({mouths})"
    assert {round(m[0]) for m in mouths} == {400, 800}, "at the ward's own edges"

    other_kind = dict(M, districts=[{"kind": "samurai", "poly": ward}])
    assert machi_mouths(other_kind) == [], "only a machi ward has a kido mouth"

    outside = [(1100.0, 400.0), (1400.0, 400.0), (1400.0, 800.0), (1100.0, 800.0)]
    suburb = dict(M, districts=[{"kind": "machi", "poly": outside}])
    assert machi_mouths(suburb) == [], "an out-wall suburb's bar is the city gate itself"


def test_a_moat_offtake_is_SWEPT_DOWNSTREAM_rather_than_tapped_square() -> None:
    """Canal practice: an offtake leaves its parent at an ACUTE angle pointing downstream - the
    studied optimum for water and sediment is 15-45 degrees, explicitly "30 or 45 instead of 90". A
    square tap sheds sediment into its own mouth and, on the page, says nothing about which way the
    water runs.

    Only the MOAT-SIDE end moves: the sluice stays exactly where it is, so the comb field it feeds
    does not shift by a pixel. That is the invariant asserted here - the returned point is on the
    ring and upstream of where the throat would otherwise have left.
    """
    ring = [(200.0, 200.0), (1000.0, 200.0), (1000.0, 1000.0), (200.0, 1000.0)]
    near = (1000.0, 600.0)  # where the throat would leave if it tapped square
    tapped = moat_swept_tap(ring, inlet=(1000.0, 200.0), outlet=(1000.0, 1000.0), other=(200.0, 600.0), near=near)
    assert tapped != near, "the tap moves upstream along the rim"

    # ON THE RING, not on the same EDGE of it - the walk is by ARC LENGTH, so a long enough set-back
    # carries the point around a corner onto the next edge. (Asserting it keeps x=1000 is the same
    # mistake the comment above the function warns about: "a vertex step on these rings is ~140 px".)
    from l7r.diagram.settlement import seg_dist

    on_ring = min(seg_dist(tapped[0], tapped[1], ring[i], ring[(i + 1) % len(ring)]) for i in range(len(ring)))
    assert on_ring < 1.0, f"the tap sits on the moat ring itself ({tapped})"


def test_a_DRAIN_lands_walking_DOWNSTREAM_and_is_CAPPED_however_far_the_caller_allows() -> None:
    """Same geometry, mirrored. An OFFTAKE leaves the ring so its rim end walks UPSTREAM and the
    throat runs with the current; a DRAIN ARRIVES, so its landing walks the other way.

    A landing is additionally held to 90 px of set-back whatever the caller asked for: walk further
    and the culvert's sink end finishes closer to the drain's HEAD than to its tail, which flips the
    outfall attribution `drain_flows_downhill` reads (Nagahara's fnn2 did exactly that). Driven with
    an unreachable `want_deg` so the walk always runs to its limit, which is what makes the limit
    itself visible: the offtake keeps walking as `max_back` is raised and the landing does not."""
    ring = [(200.0, 200.0), (1000.0, 200.0), (1000.0, 1000.0), (200.0, 1000.0)]
    kw = {"inlet": (1000.0, 200.0), "outlet": (1000.0, 1000.0), "other": (1400.0, 900.0), "near": (1000.0, 600.0), "want_deg": -1.0}

    leaving = [moat_swept_tap(ring, max_back=mb, **kw) for mb in (90.0, 220.0, 1000.0)]
    assert len(set(leaving)) == 3, f"an offtake walks further the more set-back it is allowed: {leaving}"

    landing = [moat_swept_tap(ring, max_back=mb, arriving=True, **kw) for mb in (90.0, 220.0, 1000.0)]
    assert len(set(landing)) == 1, f"a landing stops at its own 90 px cap and ignores the rest: {landing}"
    assert landing[0] != leaving[1], "and the two ends do not land on the same point"
