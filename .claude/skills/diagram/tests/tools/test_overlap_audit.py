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
