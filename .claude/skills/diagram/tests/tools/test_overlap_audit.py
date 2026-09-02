"""Every family of the overlap audit fires on an offender and stays silent on a clean map (feature 151, US2).

The `unmeasured` case matters as much as the others: a family that reports `0` when it could not look is
the failure this tool exists to remove - twelve hand-written scripts across features 150's T50-T55, two of
which measured the wrong thing and reported a clean map.
"""

from __future__ import annotations

from l7r.diagram.tools import overlap_audit as oa


def _ring(x0: float, y0: float, x1: float, y1: float, n: int = 8) -> list[list[float]]:
    return (
        [[x0 + (x1 - x0) * i / n, y0] for i in range(n)]
        + [[x1, y0 + (y1 - y0) * i / n] for i in range(n)]
        + [[x1 - (x1 - x0) * i / n, y1] for i in range(n)]
        + [[x0, y1 - (y1 - y0) * i / n] for i in range(n)]
    )


def test_a_footprint_in_the_water_and_on_the_marsh_is_named() -> None:
    wet = {
        "houses": [{"x": 500.0, "y": 500.0, "w": 40.0, "h": 30.0}],
        "streams": [{"poly": [[400.0, 500.0], [600.0, 500.0]], "w": 9.0}],
        "marshes": [{"poly": _ring(450.0, 450.0, 550.0, 550.0), "role": "toe"}],
    }
    res = oa.audit(wet, None, ("footprints-water", "footprints-marsh"))
    assert res["footprints-water"]["status"] == "FAIL" and res["footprints-water"]["hits"][0][0] == "houses"
    assert res["footprints-marsh"]["status"] == "FAIL"

    dry = {**wet, "houses": [{"x": 900.0, "y": 900.0, "w": 40.0, "h": 30.0}]}
    res2 = oa.audit(dry, None, ("footprints-water", "footprints-marsh"))
    assert res2["footprints-water"]["status"] == "ok" and res2["footprints-marsh"]["status"] == "ok"


def test_a_channel_through_a_parcel_is_a_crossing_and_a_mouth_is_not() -> None:
    """The distinction the reference hamlet forced: the source hairline ENDS inside the crop by design
    (`channel_field_anchored` wants its mouth >= 10 px in), and every comb map in the pool has one. Only a
    run that goes in one side and out the other is the T55 defect."""
    ring = _ring(100.0, 100.0, 400.0, 700.0)
    through = {"fields": [{"plot_rings": [ring]}], "channels": [{"poly": [[200.0, 40.0], [205.0, 900.0]], "w": 3.0}]}
    assert oa.audit(through, None, ("parcels-channels",))["parcels-channels"]["status"] == "FAIL"

    mouth = {"fields": [{"plot_rings": [ring]}], "channels": [{"poly": [[200.0, 40.0], [205.0, 300.0]], "w": 3.0}]}  # stops inside
    assert oa.audit(mouth, None, ("parcels-channels",))["parcels-channels"]["status"] == "ok"

    alongside = {"fields": [{"plot_rings": [ring]}], "channels": [{"poly": [[100.0, 40.0], [100.0, 900.0]], "w": 3.0}]}  # along the edge
    assert oa.audit(alongside, None, ("parcels-channels",))["parcels-channels"]["status"] == "ok"


def test_ink_over_a_mound_and_over_water_is_named_by_the_marks_own_reach() -> None:
    """A tint circle centered a foot outside a rim still paints its whole body over the water (feature 150
    T54's own defect), and a reed blade is a LINE that leans - read as a disc round its base it reports ink
    the map does not carry."""
    M = {
        "dikes": [{"outline": _ring(600.0, 200.0, 640.0, 800.0)}],
        "pond": [200.0, 200.0, 60.0, 40.0],
        "channels": [{"poly": [[0.0, 900.0], [1000.0, 900.0]], "w": 4.0}],
    }
    over = '<circle cx="590.0" cy="500.0" r="28.0" fill="#9FBBAE"/>'  # 10 px outside the band, 28 px of body
    assert oa.audit(M, over, ("ink-mounds",))["ink-mounds"]["status"] == "FAIL"
    clear = '<circle cx="500.0" cy="500.0" r="28.0" fill="#9FBBAE"/>'
    assert oa.audit(M, clear, ("ink-mounds",))["ink-mounds"]["status"] == "ok"

    leaning_away = '<g stroke="#6E9377" stroke-width="0.8"><line x1="900.0" y1="906.0" x2="900.0" y2="899.0"/></g>'
    assert oa.audit(M, leaning_away, ("ink-water",))["ink-water"]["status"] == "FAIL", "the tip crosses the bed"
    leaning_off = '<g stroke="#6E9377" stroke-width="0.8"><line x1="900.0" y1="912.0" x2="900.0" y2="905.0"/></g>'
    assert oa.audit(M, leaning_off, ("ink-water",))["ink-water"]["status"] == "ok", "a blade that stops short is not ink on water"


def test_a_family_this_map_cannot_answer_is_unmeasured_not_zero() -> None:
    bare = {"houses": [{"x": 10.0, "y": 10.0, "w": 4.0, "h": 4.0}]}
    res = oa.audit(bare, None)
    assert res["footprints-water"]["status"] == "unmeasured"
    assert res["ink-mounds"]["status"] == "unmeasured"
    assert res["parcels-channels"]["status"] == "unmeasured"


# ---- feature 174: the remaining branches and the CLI --------------------------------------------
def test_a_record_with_no_geometry_at_all_contributes_no_points() -> None:
    """The extractor sweeps whatever the manifest holds; a record carrying neither a polygon nor an
    x/y is not a shape and must not be read as one at the origin."""
    assert oa._pts({"label": "a note"}) == []


def test_a_channel_that_FEEDS_a_field_is_excluded_when_intake_bands_are_not_wanted() -> None:
    """`parcels-channels` asks whether a plot ring is crossed by a channel - but the channel that
    FEEDS the field is supposed to reach it. Counting the intake would report every irrigated field
    as a defect, which is the wolf-crying that gets an audit switched off."""
    M = {"channels": [{"pts": [[0, 0], [100, 0]], "w": 4, "to": {"kind": "field"}}, {"pts": [[0, 50], [100, 50]], "w": 4}]}
    assert len(oa._bands(M, intake=True)) == 2
    assert len(oa._bands(M, intake=False)) == 1, "the field's own intake is not a crossing"


def test_a_channel_that_only_reaches_a_rings_EDGE_is_a_mouth_not_a_crossing() -> None:
    """A run that touches an END of the channel is where it enters or leaves - drawing an outfall
    into a paddy is the design, not a defect. Only a run with channel on BOTH sides is a crossing."""
    ring = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    through = [([(-50.0, 50.0), (150.0, 50.0)], 3.0)]
    assert oa._crossed_by(ring, through) is not None, "in one side and out the other"
    mouth = [([(50.0, 50.0), (150.0, 50.0)], 3.0)]
    assert oa._crossed_by(ring, mouth) is None, "it starts inside: a mouth"
    outside = [([(0.0, 500.0), (100.0, 500.0)], 3.0)]
    assert oa._crossed_by(ring, outside) is None, "and one that never enters is nothing at all"


def test_ink_in_the_POND_is_reported_as_pond_and_ink_on_a_channel_as_channel() -> None:
    """The two water sources are named separately in the hit, because they are fixed differently -
    a scatter dot in the pond is a keep-out failure, one on a channel is a corridor failure."""
    M = {"pond": [100.0, 100.0, 40.0, 30.0], "channels": [{"pts": [[0, 400], [500, 400]], "w": 6}]}
    svg = '<circle cx="100" cy="100" r="3" fill="#9FBBAE"/><circle cx="250" cy="400" r="3" fill="#9FBBAE"/>'
    res = oa.audit(M, svg, families=("ink-water",))
    where = {h[2] for h in res["ink-water"]["hits"]}
    assert res["ink-water"]["status"] == "FAIL"
    assert where == {"pond", "channel"}, f"both sources named: {res['ink-water']['hits']}"


def test_a_family_whose_INPUTS_the_map_does_not_carry_is_unmeasured_not_ok() -> None:
    """The distinction the whole report rests on: "this map has no channels" must not read as "this
    map's channels are clean". A check that never runs looks exactly like a check that passes."""
    res = oa.audit({}, None, families=oa.FAMILIES)
    assert {r["status"] for r in res.values()} == {"unmeasured"}


def test_main_reads_the_svg_beside_the_manifest_and_says_so_when_there_is_none(tmp_path, capsys) -> None:
    """The ink families cannot be read without the SVG, and a reader must not take their silence for
    a pass - so their absence is stated in as many words."""
    import json

    man = tmp_path / "m.json"
    man.write_text(json.dumps({"pond": [100.0, 100.0, 40.0, 30.0]}))
    assert oa.main([str(man)]) == 0
    out = capsys.readouterr().out
    assert "no SVG beside the manifest" in out and "unmeasured" in out

    (tmp_path / "m.svg").write_text('<circle cx="100" cy="100" r="3" fill="#9FBBAE"/>')
    assert oa.main([str(man)]) == 1, "with the SVG the dot in the pond is found, and the rc says so"
    assert "FAIL" in capsys.readouterr().out


def test_main_takes_a_subset_of_families(tmp_path, capsys) -> None:
    import json

    man = tmp_path / "m.json"
    man.write_text(json.dumps({}))
    assert oa.main([str(man), "--families", "ink-water"]) == 0
    out = capsys.readouterr().out
    assert "ink-water" in out and "footprints-water" not in out


def test_a_reed_BLADE_is_judged_on_both_ends_of_the_segment_it_is_drawn_as(tmp_path) -> None:
    """A blade is a line, not a dot: a disc round its base would miss one leaning out over the water
    and would flag one merely rooted near it. Both ends are tested, and the pond is named."""
    M = {"pond": [100.0, 100.0, 40.0, 30.0]}
    svg = '<g stroke="#6E9377" stroke-width="0.8"><line x1="300" y1="300" x2="100" y2="100"/></g>'
    res = oa.audit(M, svg, families=("ink-water",))
    assert res["ink-water"]["status"] == "FAIL"
    assert res["ink-water"]["hits"][0][0] == "reed blade" and res["ink-water"]["hits"][0][2] == "pond"


def test_main_prints_ok_for_a_family_that_was_measured_and_found_clean(tmp_path, capsys) -> None:
    """The third status. `unmeasured` and `FAIL` both have their own line; a family that really ran
    and really passed has to say so, or a clean map is indistinguishable from an unread one."""
    import json

    man = tmp_path / "m.json"
    man.write_text(json.dumps({"pond": [100.0, 100.0, 10.0, 10.0]}))
    (tmp_path / "m.svg").write_text('<circle cx="900" cy="900" r="3" fill="#9FBBAE"/>')
    assert oa.main([str(man), "--families", "ink-water"]) == 0
    assert "ok" in capsys.readouterr().out
