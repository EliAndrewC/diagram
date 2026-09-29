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


def test_a_pond_fixture_will_not_stand_on_its_sluice():
    """feature 233. Nobody builds a shed over the opening they have to reach to lift its boards - the
    rule the engine's dike-top house placer already had ("never build over a sluice notch") and the
    pond-stock placer did not, which is why three of Kuwabata's seven sties were drawn with a feed
    culvert running through them."""
    s = Settlement(W=400, H=400, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    s.M["dikepond_sluices"] = [{"a": [100.0, 100.0], "b": [124.0, 100.0], "kind": "feed"}]
    assert not s.pond_fixture_fits(105.0, 100.0, 0.0), "the stub runs through the shed"
    assert not s.pond_fixture_fits(105.0, 104.0, 0.0), "clear of it, but inside the working margin"
    assert s.pond_fixture_fits(105.0, 120.0, 0.0), "a seat further along the same bank is fine"
    # measured to the SEGMENT, not to an endpoint: a stub is 19-41 ft long on a real map
    assert not s.pond_fixture_fits(124.0, 103.0, 0.0), "over the middle of the stub, far from either anchor"


def test_the_woodpile_forms_draw_at_their_own_size_and_keep_the_woodpile_class():
    """269 B15: the woodshed (a roof with its band of log ends) and the kizuma (a long stack) are forms of the one kind."""
    from l7r.diagram.settlement.farm_fixtures import WOODPILE_FORM_FT

    s = Settlement(W=400, H=400, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    for form in ("shed", "kizuma"):
        s.farm_fixture("woodpile", 100.0, 100.0, rot=0.0, of=(80.0, 90.0), form=form)
        rec = s.M["farm_fixtures"][-1]
        assert rec["form"] == form and (rec["w"], rec["h"]) == WOODPILE_FORM_FT[form] and s.top_cls[-1] == "woodpile"
    assert "<line" in s.top[-2] and s.top[-1].count("<circle") >= 9, "the shed's ridge; the kizuma's end grain along 24 ft"
    with pytest.raises(ValueError, match="form"):
        s.farm_fixture("coop", 100.0, 100.0, form="shed")
