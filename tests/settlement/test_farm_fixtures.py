"""The farmstead fixture glyphs and records (settlement/farm_fixtures.py, feature 133 T53-T59)."""

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.farm_fixtures import FIXTURE_FT, FIXTURE_KINDS, SHRINE_RED


def test_every_fixture_kind_draws_on_top_and_records_its_house():
    s = Settlement(W=600, H=600, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    for i, kind in enumerate(FIXTURE_KINDS):
        s.farm_fixture(kind, 100 + 40 * i, 300, rot=12.0, of=(100 + 40 * i, 330))
    recs = s.M["farm_fixtures"]
    assert [r["kind"] for r in recs] == list(FIXTURE_KINDS)
    assert all(r["of"] == [100 + 40 * i, 330] and r["rot"] == 12.0 for i, r in enumerate(recs))
    assert all((r["w"], r["h"]) == FIXTURE_FT[r["kind"]] for r in recs), "true feet at 1 ft/px - no size inflation"
    assert len(s.top) >= len(FIXTURE_KINDS) and any(SHRINE_RED in t for t in s.top), "the hokora carries the religious red"
    with pytest.raises(ValueError):
        s.farm_fixture("pigsty", 10, 10)


def test_the_manure_pit_form_draws_a_jar_mouth_and_records_its_form():
    # feature 150 A2: the pit is the same KIND (one share, one seat table) in another form and class
    from l7r.diagram.settlement import Settlement

    s = Settlement(W=400, H=400, seed=1)
    s.farm_fixture("manure", 100.0, 100.0, rot=5.0, of=(80.0, 90.0), form="pit")
    rec = s.M["farm_fixtures"][-1]
    assert rec["kind"] == "manure" and rec["form"] == "pit" and abs(rec["w"] - rec["h"]) < 0.01
    assert s.top_cls[-1] == "manure pit" and "<circle" in s.top[-1]
    with pytest.raises(ValueError, match="form"):
        s.farm_fixture("privy", 100.0, 100.0, form="pit")


def test_pond_stock_glyphs_record_and_class_themselves():
    # feature 150 A3: a sty on a pond bank, its own class and record; the duck pen is retired (269 B32), so none draws
    s = Settlement(W=400, H=400, seed=1)
    s.pig_sty(100.0, 100.0, rot=10.0, pond=3)
    assert s.M["pig_sties"][0]["pond"] == 3 and s.top_cls[-1] == "pig sty"
    assert not hasattr(s, "duck_pen") and "duck_pens" not in s.M
    assert s.pond_fixture_fits(300.0, 300.0, 0.0) and not s.pond_fixture_fits(100.0, 100.0, 0.0)


def test_persimmon_is_one_crown_with_fruit_and_joins_the_tree_record():
    s = Settlement(W=600, H=600, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    before = len(s.M["tree_crowns"])
    s.persimmon(200, 200, of=(180, 200))
    assert s.M["persimmons"] == [{"x": 200.0, "y": 200.0, "r": 11.5, "of": [180.0, 200.0]}]  # 269 B14: a ~23 ft crown
    assert len(s.M["tree_crowns"]) == before + 3, "the crown is a tree: structures_clear_of_trees reads it"
    assert s.top[-1].count("#E07B22") == 4, "four fruit dots are the persimmon convention"


def test_the_woodpile_is_a_wood_shed_and_a_rolled_size_draws_at_its_own_feet():
    """Feature 280 M21 (research/questions/0043-firewood-stacks-and-sheds-kigoya.html, 720): the firewood is drawn in its wood shed, 24 x 12 ft, a roof with its band
    of log ends - the open stack and the kizuma, modern-only, have no form left. A privy or bath room drawn at a size the
    placer rolled records that size (research/homesteads/750, 740)."""
    s = Settlement(W=400, H=400, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    s.farm_fixture("woodpile", 100.0, 100.0, rot=0.0, of=(80.0, 90.0))
    rec = s.M["farm_fixtures"][-1]
    assert (rec["w"], rec["h"]) == (24.0, 12.0) and "form" not in rec and s.top_cls[-1] == "wood shed"
    assert "<line" in s.top[-1] and s.top[-1].count("<circle") >= 7, "the shed's ridge and its log ends along 24 ft (one to 3.2 ft)"
    s.farm_fixture("privy", 200.0, 200.0, size_ft=(18.0, 12.0))
    assert (s.M["farm_fixtures"][-1]["w"], s.M["farm_fixtures"][-1]["h"]) == (18.0, 12.0)
    for kind, form in (("coop", "shed"), ("woodpile", "kizuma"), ("woodpile", "shed")):
        with pytest.raises(ValueError, match="form"):
            s.farm_fixture(kind, 100.0, 100.0, form=form)


def test_a_privy_carries_its_jar_so_a_large_one_is_not_read_as_a_wood_shed():
    """Feature 280 (settlement-review of Mizuguchi): at the rolled sizes a plain ridged roof read as the wood shed."""
    s = Settlement(W=400, H=400, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    s.farm_fixture("privy", 100.0, 100.0, size_ft=(24.0, 12.0))
    assert s.top[-1].count("<circle") == 1 and "#3E2A12" in s.top[-1] and s.top_cls[-1] == "privy"


def test_the_north_annex_is_held_inside_the_edo_sheds_band():
    """Feature 293: dealt to the largest houses, the annex drawn as shares of its house ran past 27 ft and past 1.8 to one;
    research/questions/0052-farm-sheds-and-barns-naya.html's band is 18-27 ft and 1.5-1.8 to one. The west annex is the shares alone."""
    from l7r.diagram.settlement.farm_fixtures import kura_rect

    assert kura_rect(46.0, 28.0, "N", 1.0) == pytest.approx((0.0, -0.675 * 28.0, 0.46 * 46.0, 0.45 * 28.0)), "an ordinary minka: inside the band, unchanged"
    for w, h in ((62.0, 28.0), (55.4, 29.9), (40.0, 28.0), (36.0, 30.0), (62.0, 31.0), (70.0, 40.0)):
        _x, y, length, depth = kura_rect(w, h, "N", 1.0)
        assert 18.0 <= length <= 27.0 and 1.5 - 1e-9 <= length / depth <= 1.8 + 1e-9, (w, h)
        assert (y, depth) == pytest.approx((-0.675 * h, 0.45 * h)), "the depth stays the house's share, lapping its back wall"
        assert length <= w, "the length lies within the house's own width"
    assert kura_rect(62.0, 28.0, "N", 1.0)[2] == pytest.approx(1.8 * 12.6), "a long house's annex stops at 1.8 to one"
    assert kura_rect(40.0, 28.0, "N", 1.0)[2] == pytest.approx(1.5 * 12.6), "a short one's reaches 1.5 to one"
    assert kura_rect(80.0, 40.0, "N", 1.0)[2] == pytest.approx(27.0), "and none runs past 27 ft"
    assert kura_rect(23.0, 14.0, "N", 0.5) == pytest.approx((0.0, -0.675 * 14.0, 0.46 * 23.0, 0.45 * 14.0)), "the band is in feet: a village's 2 ft pixel"
    assert kura_rect(31.0, 14.0, "N", 0.5)[2] == pytest.approx(1.8 * 6.3), "a 62 ft house at 2 ft to the pixel stops at 1.8 to one too"
    assert kura_rect(40.0, 20.0, "N", 1.0)[2] == pytest.approx(1.8 * 9.0), "under ~22 ft deep the band cannot be met, and 1.8 to one wins"
    assert kura_rect(62.0, 28.0, "W", 1.0) == pytest.approx((-0.64 * 62.0, 0.0, 0.32 * 62.0, 0.56 * 28.0)), "the west annex keeps its shares"
