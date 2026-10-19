"""tier city tests split out of `tests.settlement.test_knobs` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

from l7r.diagram.settlement.city.knobs import machi_mouths

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
