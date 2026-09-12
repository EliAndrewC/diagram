"""Unit tests for the crossings, the notice board, and the map frame (`hamletgen/frame.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

from l7r.diagram import hamletgen as hg


def test_stage_notice_reseats_a_board_the_frame_would_lose(monkeypatch):
    """The board re-seat branch: place_kosatsuba maximizes traffic along the WHOLE way network, so
    a lane arm running past the cluster can seat the board outside the house cloud - where
    crop_to_content (which frames hard features only) would drop it off the sheet. stage_notice
    must then pop the board AND its caption and re-seat it on a lane verge inside the cloud.
    Exercised directly with a stub settlement: no rolled seed reaches this branch any more (the
    2026-08-16 well/lane re-rolls un-covered it), and hunting seeds is fragile where a direct
    call is exact."""

    class _StubS:
        def __init__(self):
            self.M = {
                "houses": [{"x": x, "y": y} for x in (440.0, 520.0, 600.0) for y in (440.0, 520.0, 600.0)],
                "kosatsuba": [{"x": 900.0, "y": 100.0, "z": 2}],  # its ink is top[2] (feature 133 T48): popping the record blanks it
                "labels": [[0, 0, 0, 0], [880.0, 90.0, 60.0, 12.0, 0.0, "notice board"]],
                "lanes": [
                    {"pts": [(-200.0, 0.0), (200.0, 0.0)], "connector": True},  # skipped: connector
                    {"pts": [(300.0, 520.0), (700.0, 524.0)]},  # verge seats inside AND outside the cloud
                    {"pts": [(560.0, 400.0), (560.0, 700.0)]},  # a way ACROSS the verge lane: a seat nearest to it fronts the wrong way (T48)
                ],
            }
            self.top = ["", "", "the first board's glyph"]
            self.TOPZ = 0
            self.reseated: list[tuple[float, float, float]] = []

        def place_kosatsuba(self):
            return (900.0, 100.0)  # outside the cloud - the frame would lose it

        def discard_queued_label(self, kind):
            # feature 157: the caption is QUEUED, so withdrawing the board withdraws the request rather
            # than hunting a drawn label out of M["labels"]. The stub carries a pre-drawn "notice board"
            # record from the era when it was drawn inline; dropping it here keeps the assertion below
            # measuring the same thing - that the re-seat leaves no orphan caption behind.
            self.M["labels"] = [lb for lb in self.M["labels"] if not (len(lb) > 5 and lb[5] == "notice board")]

        def place_labels(self):
            pass  # the phase itself is exercised where it lives, in tests/settlement/test_structures.py

        def _fits(self, x, y, w, h, corridors=False):
            return x >= 500.0  # some verge candidates refused, so the refusal path runs too

        def fixture_clear_of_water(self, x, y, half):
            # a "stream" across the west half of the verge, so the re-seat's water REFUSAL runs too
            # (the same reason `_fits` above refuses part of the range). The predicate's own behavior
            # is covered where it lives, in settlement/structures/fixtures.py; what this pins is that
            # the re-seat consults it at all - without the call a board lands in the water, which is
            # exactly what cohort seed 13 shipped.
            return x >= 540.0

        def kosatsuba(self, x, y, rot=0.0):
            self.reseated.append((x, y, rot))
            self.M["kosatsuba"].append({"x": x, "y": y})

    s = _StubS()
    asked: list[tuple[float, float, float | None]] = []
    real_bearing = hg.frame._nearest_way_bearing

    def bearing(settlement, x, y):  # type: ignore[no-untyped-def]
        b = real_bearing(settlement, x, y)
        asked.append((x, y, b))
        return b

    monkeypatch.setattr(hg.frame, "_nearest_way_bearing", bearing)
    hg.stage_notice(s, None)  # type: ignore[arg-type]
    assert s.reseated, "the board was not re-seated"
    assert s.top[2] == "", "the popped board's ink in the top layer must be blanked with its record (T48)"
    # THE WAY IT FRONTS IS THE WAY IT IS NEAREST (T48; feature 214 asserts it directly - the cohort seeds that
    # reached the refusal went): a verge seat of the east-west lane that stands nearer the north-south way was
    # asked its nearest bearing and got the crossing way's (about 90 degrees against the lane's 0.6), so it was refused
    across = [(x, y, b) for x, y, b in asked if b is not None and abs(y - 522.0) < 25.0 and abs(x - 560.0) < 8.0]
    assert across and all(abs(abs(b) - 90.0) < 5.0 for _x, _y, b in across), across
    assert not any(abs(bx - 560.0) < 8.0 and abs(by - 522.0) < 25.0 for bx, by, _r in s.reseated), "no board seated where its nearest way runs across it"
    bx, by, _rot = s.reseated[0]
    assert 440.0 <= bx <= 600.0 and 440.0 <= by <= 600.0, f"re-seated outside the cloud: {(bx, by)}"
    assert bx >= 540.0, f"re-seated into the stub's water at {(bx, by)} - the re-seat must consult fixture_clear_of_water"
    s.place_labels()  # feature 157: captions are queued and drawn in the LABEL PHASE, so run it before reading them
    assert not any(len(lb) > 5 and lb[5] == "notice board" for lb in s.M["labels"]), "orphan caption left behind"
    assert len(s.M["kosatsuba"]) == 1, "old board not popped"


def test_the_confluence_reserves_its_own_room_in_the_crop(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Feature 230, settlement-review passes 6 and 7. Where the drain meets the passing brook, that junction is a
    FEATURE - the thing the third sink exists to show - and the crop ignores watercourses because they are
    runners that trail off the edge, so one was drawn 7.4 ft outside the sheet with none of its trunk in view.
    Predicting the frame back in `stage_sink` cannot work: the frame is decided here. The junction reserves
    itself instead, the way the title pocket does."""
    from l7r.diagram.hamletgen import frame as fr

    from ._builders import a_plan

    calls: list[list[tuple[float, float, float, float]]] = []

    class _Crop:
        M = {"meta": {}, "houses": [], "lanes": [], "kosatsuba": []}

        def crop_to_content(self, margin=30, extra=()):  # type: ignore[no-untyped-def]
            calls.append(list(extra))

        def title(self, *_a, **_k):  # type: ignore[no-untyped-def]
            pass

    plan = a_plan()
    plan.title_pocket_outside = False
    plan.confluence = (1200.0, 900.0)
    monkeypatch.setattr(fr, "title_pocket", lambda _s, _p: (0.0, 0.0, 10.0, 10.0))  # the pocket is exercised where it lives
    fr.stage_frame(_Crop(), plan)  # type: ignore[arg-type]
    assert calls and calls[0], "the junction is reserved as content"
    x0, y0, x1, y1 = calls[0][0]
    assert x0 < 1200.0 < x1 and y0 < 900.0 < y1, "and the reservation is centred on the junction"
    assert (x1 - x0) >= fr.BROOK_JOIN_TRUNK, "with a trunk's length of room around it"


def test_a_board_with_no_compliant_verge_still_faces_the_way_a_reader_sees_it_by() -> None:
    """Feature 230. Every verge candidate can be refused by the 15-degree rule - a web straggler laid across
    a main lane's verge leaves no seat that fronts one way alone - and the board still has to go somewhere.
    The fallback takes the best-ranked verge and turns the board to its NEAREST way, which is the bearing the
    gate judges it by; the old fallback re-posted the engine's own seat unturned and shipped a board 72
    degrees side-on to the lane 9.5 ft from it."""

    class _StubS:
        def __init__(self) -> None:
            self.M = {
                "houses": [{"x": x, "y": y} for x in (500.0, 560.0, 620.0) for y in (460.0, 520.0, 580.0)],
                "kosatsuba": [{"x": 900.0, "y": 100.0, "z": 2}],
                "labels": [],
                "lanes": [
                    {"pts": [(554.0, 520.0), (566.0, 520.0)]},  # the only main lane, and a short one
                    {"pts": [(560.0, 400.0), (560.0, 700.0)], "web": True},  # the straggler across its every verge
                ],
            }
            self.top = ["", "", "the first board's glyph"]
            self.TOPZ = 0
            self.reseated: list[tuple[float, float, float]] = []

        def place_kosatsuba(self) -> tuple[float, float]:
            return (900.0, 100.0)  # outside the house cloud, so the frame would lose it

        def discard_queued_label(self, kind: str) -> None:
            pass

        def _fits(self, x: float, y: float, w: float, h: float, corridors: bool = False) -> bool:
            return True

        def fixture_clear_of_water(self, x: float, y: float, half: float) -> bool:
            return True

        def kosatsuba(self, x: float, y: float, rot: float = 0.0) -> None:
            self.reseated.append((x, y, rot))
            self.M["kosatsuba"].append({"x": x, "y": y})

    s = _StubS()
    hg.stage_notice(s, None)  # type: ignore[arg-type]
    assert len(s.reseated) == 1, "the board must still be posted when no verge fronts one way alone"
    bx, by, rot = s.reseated[0]
    assert abs(abs(rot) - 90.0) < 1.0, f"the fallback board is turned to its nearest way, not left on the lane's bearing: {rot}"
    assert hg.frame._nearest_way_bearing(s, bx, by) is not None
    assert abs(by - 520.0) > 1.0, "it still stands on a verge rather than in the tread"
