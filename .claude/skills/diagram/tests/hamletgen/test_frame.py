"""Unit tests for the crossings, the notice board, and the map frame (`hamletgen/frame.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

from l7r.diagram import hamletgen as hg


def test_the_confluence_reserves_its_own_room_in_the_view() -> None:
    """Feature 230, settlement-review passes 6 and 7. Where the drain meets the passing brook, that junction is a
    FEATURE - the thing the third sink exists to show - and the crop ignores watercourses because they are runners that
    trail off the edge, so one was drawn 7.4 ft outside the sheet with none of its trunk in view. The junction reserves
    itself as content, the way the title pocket does - in `frame_extras`, which the view is decided by (feature 287)."""
    from l7r.diagram.hamletgen.hinterland.frame import frame_extras, frame_for
    from l7r.diagram.hamletgen.sink import BROOK_JOIN_TRUNK
    from l7r.diagram.settlement import Settlement

    from ._builders import a_plan

    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["houses"] = [{"x": 600.0, "y": 600.0, "w": 40.0, "h": 30.0, "rot": 0}]
    plan.title_pocket, plan.title_pocket_outside = (590.0, 590.0, 610.0, 610.0), False  # an inside pocket reserves nothing
    plan.confluence = (1200.0, 900.0)
    got = frame_extras(s, plan)
    assert got, "the junction is reserved as content"
    x0, y0, x1, y1 = got[0]
    assert x0 < 1200.0 < x1 and y0 < 900.0 < y1, "and the reservation is centered on the junction"
    assert (x1 - x0) >= BROOK_JOIN_TRUNK, "with a trunk's length of room around it"
    vx, vy, vw, vh = frame_for(s, plan)
    assert vx + vw >= x1 and vy + vh >= y1, "the view decided takes the junction in"
    plan.title_pocket_outside = True
    assert frame_extras(s, plan)[0] == plan.title_pocket, "an OUTSIDE pocket is content too"


def test_stage_frame_takes_exactly_the_view_decided_and_records_a_drift() -> None:
    """Feature 287, M6: the view is decided ONCE, at the end of `stage_hinterland`, and `stage_frame` sets exactly that view
    - never a second computation of it. The violating case: a frame-setting feature placed after the decision (here a
    house far off the cluster) would have moved a recomputed crop; the view stays the decided one, and the difference is
    recorded as `meta.view_drift` so the pool test can hold that no stage after the decision sets the frame."""
    from l7r.diagram.hamletgen import frame as fr
    from l7r.diagram.hamletgen.hinterland.frame import frame_for
    from l7r.diagram.settlement import Settlement

    from ._builders import a_plan

    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.meta(name=plan.spec.name, scale="hamlet", ftpx=1, down_deg=90)
    s.M["houses"] = [{"x": 600.0, "y": 600.0, "w": 40.0, "h": 30.0, "rot": 0}, {"x": 800.0, "y": 700.0, "w": 40.0, "h": 30.0, "rot": 0}]
    plan.title_pocket, plan.title_pocket_outside = (620.0, 620.0, 700.0, 680.0), False
    plan.view = frame_for(s, plan)
    fr.stage_frame(s, plan)
    assert tuple(s.M["meta"]["view"]) == plan.view, "the crop takes the decided view"
    assert "view_drift" not in s.M["meta"], "nothing moved the frame after the decision"

    t = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    t.meta(name=plan.spec.name, scale="hamlet", ftpx=1, down_deg=90)
    t.M["houses"] = [dict(h) for h in s.M["houses"]]
    decided = frame_for(t, plan)
    plan.view = decided
    t.M["houses"].append({"x": 1100.0, "y": 700.0, "w": 40.0, "h": 30.0, "rot": 0})  # placed AFTER the decision
    fr.stage_frame(t, plan)
    assert tuple(t.M["meta"]["view"]) == decided, "the decided view, not a recomputed one"
    assert t.M["meta"]["view_drift"][2] > 0 and t.M["meta"]["view_drift"][0] == 0, "the drift says the right edge would have moved"


def test_the_brook_beside_the_field_is_reserved_and_the_reach_leaving_the_map_is_not() -> None:
    """`brook_beside_the_field`, settlement-review pass 10. The frame reserves the brook's stations abreast of the field
    so the box `brook_skirt` holds them in can be as wide as the skirt, while the exit legs still trail off the sheet."""
    from l7r.diagram.hamletgen.consts import BROOK_FRAME_MARGIN
    from l7r.diagram.hamletgen.hinterland import brook_beside_the_field

    class _M:
        M = {
            "fields": [{"outline": [(100.0, 100.0), (500.0, 100.0), (500.0, 600.0), (100.0, 600.0)]}],
            "dry_plots": [{"poly": [(500.0, 100.0), (560.0, 100.0), (560.0, 160.0), (500.0, 160.0)]}],
            "streams": [{"w": 6.0, "poly": [(60.0, 60.0), (60.0, 300.0), (560.0 + BROOK_FRAME_MARGIN - 1.0, 400.0), (60.0, 2000.0)]}],
        }

    got = brook_beside_the_field(_M())  # type: ignore[arg-type]
    assert len(got) == 3, "the three stations abreast of the field and its hem, not the one leaving the map"
    assert got[0] == (57.0, 57.0, 63.0, 63.0), "a box of the brook's own width round each"

    class _Empty:
        M = {"fields": [], "dry_plots": [], "streams": _M.M["streams"]}

    assert brook_beside_the_field(_Empty()) == [], "no field, nothing to be beside"  # type: ignore[arg-type]

    class _Rounded:  # a rounded brook (feature 261): the reservation reads the course as first drawn, not the added vertices
        M = {**_M.M, "streams": [{"w": 6.0, "poly": [(60.0, 60.0), (60.0, 250.0), (70.0, 290.0), (60.0, 2000.0)], "stations": _M.M["streams"][0]["poly"]}]}

    assert brook_beside_the_field(_Rounded()) == got  # type: ignore[arg-type]


def test_stage_notice_is_the_one_siter() -> None:
    """Feature 287, labels L2: the board is sited once, by `place_kosatsuba`, which applies every board rule inside the
    view; the re-seat that followed it here - a second siter restating those rules with four recorded drifts - is
    deleted, so the stage asks the siter and nothing else."""
    calls: list[str] = []

    class _S:
        def place_kosatsuba(self) -> None:
            calls.append("sited")

    hg.stage_notice(_S(), None)  # type: ignore[arg-type]
    assert calls == ["sited"]
