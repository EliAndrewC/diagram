"""Feature 308, plan D1-D2 (FR-003, FR-004, FR-007): a nucleated cluster grown from its first house."""

from __future__ import annotations

import math
from types import SimpleNamespace
from typing import Any

import pytest

from l7r.diagram.hamletgen.consts import SUN_CORRIDOR_FT
from l7r.diagram.hamletgen.homesteads import growth
from l7r.diagram.hamletgen.homesteads.growth import GROW_LEVELS, box_reach, footprint, grow_gap, grow_the_margin, seat_toward


def test_a_box_reaches_from_its_house_to_each_side() -> None:
    assert box_reach((10.0, 10.0), (12.0, 15.0, 20.0, 30.0)) == (8.0, 12.0, 10.0, 20.0)


def test_the_least_distance_parts_the_two_footprints_on_the_nearer_axis() -> None:
    standing, new = (10.0, 20.0, 30.0, 40.0), (5.0, 6.0, 7.0, 8.0)
    assert seat_toward((0.0, 0.0), standing, new, 0.0, 2.0) == pytest.approx((27.0, 0.0)), "east: its east reach and the new west"
    assert seat_toward((0.0, 0.0), standing, new, math.pi, 2.0) == pytest.approx((-18.0, 0.0)), "west"
    assert seat_toward((0.0, 0.0), standing, new, math.pi / 2, 2.0) == pytest.approx((0.0, 49.0)), "south: the sun's reach and the new north"
    assert seat_toward((0.0, 0.0), standing, new, -math.pi / 2, 2.0) == pytest.approx((0.0, -40.0)), "north"
    q = seat_toward((0.0, 0.0), standing, new, math.pi / 4, 0.0)
    assert q == pytest.approx((25.0, 25.0)), "diagonal: the boxes part when the east axis does (25 / cos 45 along it)"


def _s() -> Any:
    return SimpleNamespace(px=lambda ft: ft)  # one foot a pixel


def test_a_footprint_holds_the_envelope_the_wood_and_the_sun_its_yard_and_beds_are_owed() -> None:
    rec = {
        "x": 0.0,
        "y": 0.0,
        "geom": {"bbox": (0.0, 10.0, 60.0, 60.0), "boxes": {"yard": (0.0, 20.0, 20.0, 10.0), "gardens": [(25.0, 30.0, 10.0, 10.0)]}},
        "wood_share": {"seats": [[0.0, -50.0], [-40.0, 0.0]]},
    }
    w, e, n, so = footprint(_s(), rec)
    assert (w, e, n) == (52.0, 30.0, 62.0), "the envelope, widened west and north by the wood seats and a clump"
    assert so == 35.0 + SUN_CORRIDOR_FT + 2.0, "south: the farther south edge (the bed's, 35) plus the sun corridor and 2 ft"
    bare = {"x": 0.0, "y": 0.0, "geom": {"bbox": (0.0, 0.0, 10.0, 10.0)}}
    assert footprint(_s(), bare) == (5.0, 5.0, 5.0, 5.0), "no yard, no beds, no wood: the envelope alone"


def test_the_gap_between_footprints_is_a_lanes_threading_gap_and_the_parting() -> None:
    """FR-011 (feature 318): `MIN_WEB_GAP` (a lane 7 ft off each garden fence and its 4 ft tread) and the 2 ft parting."""
    from l7r.diagram.hamletgen.consts import MIN_WEB_GAP

    assert grow_gap(_s()) == MIN_WEB_GAP + 2.0 == 20.0


class _Ground:
    """A stand-in settlement: a placer that seats any homestead at least `room` from every other and inside `ring`."""

    def __init__(self, room: float, ring: float = 1e9, first: bool = True) -> None:
        self.room, self.ring = room, ring
        self.M: dict[str, Any] = {"houses": []}
        self._seat_search: dict[str, int] = {"candidates": 0}
        self._seat_region = None
        self.first = first
        self.asked: list[tuple[float, float]] = []
        self._canvas_box = (-1000.0, -1000.0, 1000.0, 1000.0)  # the canvas the growth widens to (`growth.on_the_canvas`)

    def px(self, ft: float) -> float:
        return ft

    def _hjit(self, x: float, y: float, salt: float) -> float:
        return 0.5

    def _bundle_envelope(self, x: float, y: float, w: float, h: float, shed: bool = False) -> tuple[float, float, float, float]:
        return (x, y, 40.0, 40.0)

    def _house_box(self, x: float, y: float, w: float, h: float) -> tuple[float, float, float, float]:
        return (x, y, w, h)

    def _house_box_refused(self, box: tuple[float, float, float, float]) -> bool:
        return False

    def try_place(self, x: float, y: float, _kind: str) -> bool:
        self.asked.append((x, y))
        if math.hypot(x, y) > self.ring or any(math.hypot(x - h["x"], y - h["y"]) < self.room for h in self.M["houses"]):
            return False
        self.M["houses"].append({"x": x, "y": y, "geom": {"bbox": (x, y, 40.0, 40.0), "boxes": {}}})
        return True


def _plan(n: int) -> Any:
    return SimpleNamespace(spec=SimpleNamespace(households=n), seat={"cx": 0.0, "cy": 0.0})


def test_the_cluster_grows_from_its_first_house_nearest_the_seat_first(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(growth, "free_seats", lambda s, c, step=None: [(0.0, 0.0), (500.0, 0.0)])
    s = _Ground(room=40.0)
    assert grow_the_margin(s, _plan(6), 0, (46.0, 28.0)) == 6  # type: ignore[arg-type]
    assert s.asked[0] == (0.0, 0.0), "the first house on the free ground nearest the seat"
    near = [math.hypot(h["x"], h["y"]) for h in s.M["houses"][1:]]
    assert max(near) < 100.0, "every next house a footprint away from one standing, not across the margin"
    assert s._seat_search["grow_took"] == 6 and s._seat_search["grow_level"] == 0 and s._seat_search["grow_offered"] >= 6


def test_a_margin_whose_seats_run_dry_widens_then_is_reported_short(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(growth, "free_seats", lambda s, c, step=None: [(0.0, 0.0)])
    s = _Ground(room=40.0, ring=120.0)  # the ground ends 120 from the seat
    got = grow_the_margin(s, _plan(200), 0, (46.0, 28.0))  # type: ignore[arg-type]
    assert 1 < got < 200, "seated what the ground holds, then short"
    assert s._seat_search["grow_level"] > len(GROW_LEVELS) - 1, "widened past the table until the canvas offered no new seat"
    assert all(math.hypot(x, y) <= 1000.0 * math.sqrt(2.0) for x, y in s.asked), "never offered a seat off the canvas"


def test_past_the_table_the_growth_widens_one_ring_at_a_time() -> None:
    """`growth.grow_level` (feature 318): the table's levels as they stand, then 16 directions on one ring half the least
    distance further each level - no radius stops the growth."""
    assert [growth.grow_level(k) for k in range(len(GROW_LEVELS))] == list(GROW_LEVELS)
    last = GROW_LEVELS[-1][1][-1]
    assert growth.grow_level(len(GROW_LEVELS)) == (16, (last + 0.5,)) and growth.grow_level(len(GROW_LEVELS) + 2) == (16, (last + 1.5,))


def test_the_growth_tries_the_nearest_ring_first_and_the_field_breaks_ties_within_a_ring() -> None:
    """SC-002a (feature 318, Amendments 2 and 3): seats are ordered by their ring of distance from the seat center (`TIE_RING_FT`
    wide), the nearer the field first only WITHIN a ring - a seat in a farther ring is never tried first for being nearer the
    field; and the growth's breadth is main's."""
    s = _Ground(room=40.0)
    s._site_chains = [[((-1000.0, 300.0), (1000.0, 300.0), (0.0, -1.0))]]
    ring = s.px(growth.TIE_RING_FT)
    near_field_far_ring = growth.grow_key(s, (0.0, ring * 2.5), (0.0, 0.0))
    far_field_near_ring = growth.grow_key(s, (0.0, -ring * 0.5), (0.0, 0.0))
    assert far_field_near_ring < near_field_far_ring, "the nearer ring first, however near the field the farther lies"
    a, b = growth.grow_key(s, (0.0, ring * 0.6), (0.0, 0.0)), growth.grow_key(s, (0.0, -ring * 0.4), (0.0, 0.0))
    assert a[0] == b[0] and a < b, "within one ring the nearer the field first, though farther from the seat"
    assert growth.GROW_LEVELS == ((8, (1.0,)), (12, (1.0, 1.5)), (16, (1.25, 1.75, 2.0))), "main's breadth"
    assert growth.field_distance(_Ground(room=40.0), (0.0, 0.0)) == 0.0, "no field installed: no order of its own"


def test_a_pop_the_tie_break_reordered_is_counted() -> None:
    """`growth.tie_reordered` (SC-002a's count): a seat popped ahead of one in its own ring nearer the seat center is counted; one
    whose ring holds none nearer, or only seats in another ring, is not."""
    popped = (1, 5.0, 30.0, 0)
    assert growth.tie_reordered([(1, 9.0, 25.0, 1)], popped), "the same ring, nearer the seat: the field reordered them"
    assert not growth.tie_reordered([(1, 9.0, 35.0, 1), (2, 1.0, 10.0, 2)], popped), "nothing nearer in its own ring"


def test_a_box_keeps_the_threading_gap_from_every_standing_footprint_but_its_tight_neighbor() -> None:
    """`growth.keeps_every_gap` (FR-011, pairwise): a box nearer than the gap to any standing footprint is refused - but the one
    it is a tight seat against is held only to the parting."""
    rec_a, rec_b = {"x": 0.0}, {"x": 100.0}
    standing = [((0.0, 0.0), (10.0, 10.0, 10.0, 10.0), rec_a), ((100.0, 0.0), (10.0, 10.0, 10.0, 10.0), rec_b)]
    box = (30.0, 0.0, 20.0, 20.0)  # its west edge 10 px from a's east edge, 50 from b's
    assert not growth.keeps_every_gap(box, standing, 20.0), "10 px from a: under the gap"
    assert growth.keeps_every_gap(box, standing, 20.0, tight=rec_a), "a tight seat against a, by more than the parting"
    assert growth.keeps_every_gap((50.0, 0.0, 20.0, 20.0), standing, 20.0), "30 px from each"
    assert not growth.keeps_every_gap((0.0, 30.0, 20.0, 20.0), standing, 20.0), "10 px south of a: the gap on the other axis too"


def test_a_margin_with_no_free_ground_or_nothing_owed_seats_no_one(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(growth, "free_seats", lambda s, c, step=None: [])
    s = _Ground(room=40.0)
    assert grow_the_margin(s, _plan(5), 0, (46.0, 28.0)) == 0 and s._seat_search["grow_took"] == 0  # type: ignore[arg-type]
    assert grow_the_margin(_Ground(room=40.0), _plan(0), 0, (46.0, 28.0)) == 0  # type: ignore[arg-type]


def test_the_first_seat_asks_the_seat_region(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(growth, "free_seats", lambda s, c, step=None: [(900.0, 0.0), (0.0, 0.0)])
    s = _Ground(room=40.0)
    s._seat_region = SimpleNamespace(offer=lambda seats: [q[0] < 500.0 for q in seats])  # type: ignore[assignment]
    grow_the_margin(s, _plan(1), 0, (46.0, 28.0))  # type: ignore[arg-type]
    assert s.asked == [(0.0, 0.0)], "the seat the region refuses is never offered"


def test_a_seat_is_moved_out_until_its_own_envelope_rolled_there_clears_and_dropped_when_it_never_does() -> None:
    from l7r.diagram.hamletgen.homesteads.growth import SETTLE_TRIES, settled_seat

    standing, guess = (10.0, 10.0, 10.0, 10.0), (5.0, 5.0, 5.0, 5.0)
    assert settled_seat((0.0, 0.0), standing, guess, 0.0, 0.0, 1.0, lambda q: guess) == pytest.approx((15.0, 0.0)), "its roll fits the guess"
    big = (9.0, 5.0, 5.0, 5.0)  # rolled where it stands, it reaches 9 west
    assert settled_seat((0.0, 0.0), standing, guess, 0.0, 0.0, 1.0, lambda q: big) == pytest.approx((19.0, 0.0)), "moved out by the four"
    calls: list[int] = []

    def grows(q: tuple[float, float]) -> tuple[float, float, float, float]:
        calls.append(1)
        return (q[0], 5.0, 5.0, 5.0)  # always reaching past where it was placed

    assert settled_seat((0.0, 0.0), standing, guess, 0.0, 0.0, 1.0, grows) is None and len(calls) == SETTLE_TRIES


def test_a_seat_the_ground_refuses_is_dropped_before_its_household_is_laid_out() -> None:
    """Feature 314: the settle asks `refused` of every seat before it rolls the household there, and a refused seat is dropped
    without the roll."""
    from l7r.diagram.hamletgen.homesteads.growth import settled_seat

    standing, guess = (10.0, 10.0, 10.0, 10.0), (5.0, 5.0, 5.0, 5.0)
    rolled: list[tuple[float, float]] = []
    roll = lambda q: rolled.append(q) or guess  # noqa: E731
    assert settled_seat((0.0, 0.0), standing, guess, 0.0, 0.0, 1.0, roll, lambda q: True) is None and rolled == [], "never laid out"
    assert settled_seat((0.0, 0.0), standing, guess, 0.0, 0.0, 1.0, roll, lambda q: False) == pytest.approx((15.0, 0.0)) and rolled


def test_the_seats_own_questions_are_the_placers_asked_of_the_house_alone() -> None:
    """Feature 314: the house's own box against the canvas, the corridors and the placed homesteads, and the
    refused-ground grid under it - each refuses the seat; a seat none refuses is laid out."""
    from l7r.diagram.hamletgen.homesteads.growth import seat_refused

    s = _Ground(room=40.0)
    assert seat_refused(s, (0.0, 0.0), (46.0, 28.0)) is False, "nothing refuses it"  # type: ignore[arg-type]
    s._free_ground = SimpleNamespace(rect_refused=lambda box: box[2] == 46.0)  # type: ignore[attr-defined]
    assert seat_refused(s, (0.0, 0.0), (46.0, 28.0)) is True, "a refused cell under the house's box"  # type: ignore[arg-type]
    s._free_ground = None  # type: ignore[attr-defined]
    s._house_box_refused = lambda box: True  # type: ignore[method-assign]
    assert seat_refused(s, (0.0, 0.0), (46.0, 28.0)) is True, "the canvas, a corridor or two homesteads under the house"  # type: ignore[arg-type]
    far = _Ground(room=40.0)
    far._site_chains = [[((0.0, 0.0), (10.0, 0.0), (0.0, 1.0))]]  # type: ignore[attr-defined]
    assert seat_refused(far, (0.0, 5000.0), (46.0, 28.0)) is False, "no distance from the field refuses a seat (feature 318)"  # type: ignore[arg-type]


def test_the_next_house_is_its_lots_rung_or_the_largest() -> None:
    from l7r.diagram.hamletgen.homesteads.growth import next_house

    s = _Ground(room=40.0)
    assert next_house(s, (99.0, 98.0)) == (99.0, 98.0), "no lots: the largest"  # type: ignore[arg-type]
    s._lots = SimpleNamespace(lot=lambda k: (1.5, 1.0, False, False) if k == 1 else None)  # type: ignore[attr-defined]
    s.M["houses"] = [{"kind": "plain"}, {"kind": "abandoned"}]
    assert next_house(s, (99.0, 98.0)) == pytest.approx((69.0, 28.0)), "the second plain household's rung"  # type: ignore[arg-type]
    s.M["houses"].append({"kind": "plain"})
    assert next_house(s, (99.0, 98.0)) == (99.0, 98.0), "past the declared lots: the largest"  # type: ignore[arg-type]


def test_the_next_households_reach_is_rolled_with_its_own_lot_and_its_parts_taken_down_after() -> None:
    from l7r.diagram.hamletgen.homesteads.growth import household_reach

    asked: list[tuple[float, float, bool, tuple]] = []

    class Lots:
        def lot(self, k: int) -> tuple[float, float, bool, bool]:
            return (1.2, 1.1, True, False)

        def fixtures_of(self, k: int) -> tuple[str, ...]:
            return ("privy",)

    s = _Ground(room=40.0)
    s._lots = Lots()  # type: ignore[attr-defined]

    def envelope(x: float, y: float, w: float, h: float, shed: bool = False) -> tuple[float, float, float, float]:
        asked.append((w, h, shed, tuple(getattr(s, "_household_fixtures", ()) or ())))
        return (x, y, 40.0, 60.0)

    s._bundle_envelope = envelope  # type: ignore[method-assign]
    assert household_reach(s, (10.0, 20.0), (99.0, 99.0)) == (20.0, 20.0, 30.0, 30.0)  # type: ignore[arg-type]
    assert asked == [(46 * 1.2, 28 * 1.1, True, ("privy",))], "its own house from the size ladder, its kura, its fixtures set"
    assert s._household_fixtures == () and s._household_well is False, "...and taken down after"
    s2 = _Ground(room=40.0)
    s2._bundle_envelope = lambda x, y, w, h, shed=False: asked.append((w, h, shed, ())) or (x, y, 10.0, 10.0)  # type: ignore[method-assign]
    household_reach(s2, (0.0, 0.0), (99.0, 98.0))  # type: ignore[arg-type]
    assert asked[-1] == (99.0, 98.0, True, ()), "no lots: the largest house, the kura reserved"


def test_every_settled_seat_clears_the_standing_footprint_by_the_gap_with_its_own_envelope_there() -> None:
    """FR-004's "never closer", as a property: in every direction and ring, with an envelope that changes from seat to seat
    (as a household's rolled yard and parts do), the seat settled on clears the standing footprint by the gap - its own
    envelope, rolled where it stands, and the standing one part on one axis by at least `gap`."""
    from l7r.diagram.hamletgen.homesteads.growth import settled_seat

    standing = (30.0, 40.0, 50.0, 90.0)
    gap = 16.0

    def reach_at(q: tuple[float, float]) -> tuple[float, float, float, float]:
        k = (int(abs(q[0])) * 7 + int(abs(q[1])) * 13) % 17
        return (20.0 + k, 25.0 + (k * 3) % 11, 18.0 + (k * 5) % 13, 30.0 + (k * 2) % 9)

    seen = 0
    for i in range(48):
        ang = math.radians(7.5 * i)
        for scale in (1.0, 1.12, 1.5, 2.0):
            q = settled_seat((0.0, 0.0), standing, (20.0, 25.0, 18.0, 30.0), ang, gap, scale, reach_at)
            if q is None:
                continue
            seen += 1
            w, e, n, s = reach_at(q)
            apart_x = max(q[0] - w - standing[1], -standing[0] - (q[0] + e))
            apart_y = max(q[1] - n - standing[3], -standing[2] - (q[1] + s))
            assert max(apart_x, apart_y) >= gap - 1e-6, (ang, scale, q)
    assert seen > 100, "the property held over the seats it settled, and most settled"


def test_a_moved_box_keeps_the_growths_distance_from_its_source_or_is_refused() -> None:
    from l7r.diagram.hamletgen.homesteads.growth import keeps_its_distance

    standing = (10.0, 10.0, 10.0, 30.0)  # reaching 10 west, east, north and 30 south of (0, 0)
    assert keeps_its_distance((36.0, 0.0, 20.0, 20.0), (0.0, 0.0), standing, 16.0), "16 px east of its east edge"
    assert not keeps_its_distance((35.0, 0.0, 20.0, 20.0), (0.0, 0.0), standing, 16.0), "15: moved too near"
    assert keeps_its_distance((0.0, 56.0, 20.0, 20.0), (0.0, 0.0), standing, 16.0), "south, past the sun's reach"
    assert keeps_its_distance((-36.0, 0.0, 20.0, 20.0), (0.0, 0.0), standing, 16.0) and keeps_its_distance((0.0, -36.0, 20.0, 20.0), (0.0, 0.0), standing, 16.0)


class _Tight(_Ground):
    """The stand-in placer, each seated household reached by a corridor and given a yard, recording the tight seat's word."""

    def __init__(self, room: float) -> None:
        super().__init__(room)
        self.told: list[Any] = []

    def _bundle_envelope(self, x: float, y: float, w: float, h: float, shed: bool = False) -> tuple[float, float, float, float]:
        return (x, y, 120.0, 120.0)  # a homestead's envelope at the engine's scale: a tight seat stands past half a pitch

    def try_place(self, x: float, y: float, _kind: str) -> bool:
        told = getattr(self, "_tight_of", None)
        self.told.append(told)
        ok = super().try_place(x, y, _kind)
        if ok:
            self.M["houses"][-1]["geom"].update(access=((x, y), (x, y - 50.0)), boxes={"yard": (x, y + 10.0, 20.0, 10.0)})
            if told is not None:
                self._passage_left -= 1  # type: ignore[attr-defined]  # a passage spends the share, as the placer's record does
        return ok


def test_while_the_share_has_room_each_reached_house_offers_tight_seats_against_its_land(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 317, plan D2: a tight seat parts the two footprints by `TIGHT_GAP_PX` alone, and the household offered it is told
    its neighbor, the neighbor's land, its own allotted reach and the parting; none is offered with the share spent."""
    monkeypatch.setattr(growth, "free_seats", lambda s, c, step=None: [(0.0, 0.0)])
    s = _Tight(room=30.0)
    s._passage_left = 1  # type: ignore[attr-defined]
    grow_the_margin(s, _plan(3), 0, (46.0, 28.0))  # type: ignore[arg-type]
    told = [t for t in s.told if t is not None]
    assert told, "tight seats offered"
    t = told[0]
    nb = t["rec"]  # the standing house whose yard-side seat was offered first
    assert any(nb is h for h in s.M["houses"])
    assert t["gap"] == growth.TIGHT_GAP_PX and t["land"] == growth.land_box((nb["x"], nb["y"]), footprint(s, nb))
    assert t["own"] == (60.0, 60.0, 60.0, 60.0), "its own land: the reach the seat was parted by"
    assert getattr(s, "_tight_of", None) is None, "...and forgotten after"
    assert sum(t is not None for t in s.told) == 1, "the share of one spent, the tight seats still queued are passed over"
    spent = _Tight(room=30.0)
    spent._passage_left = 0  # type: ignore[attr-defined]
    grow_the_margin(spent, _plan(3), 0, (46.0, 28.0))  # type: ignore[arg-type]
    assert all(t is None for t in spent.told), "the share spent: no tight seat"


def test_a_house_no_passage_may_cross_to_offers_no_tight_seat(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(growth, "free_seats", lambda s, c, step=None: [(0.0, 0.0)])
    s = _Ground(room=30.0)  # seats households with no corridor and no yard
    s._passage_left = 1  # type: ignore[attr-defined]
    asked: list[Any] = []
    real = s.try_place
    s.try_place = lambda x, y, k: asked.append(getattr(s, "_tight_of", None)) or real(x, y, k)  # type: ignore[method-assign]
    grow_the_margin(s, _plan(3), 0, (46.0, 28.0))  # type: ignore[arg-type]
    assert asked and all(t is None for t in asked)


def test_the_seat_s_allotted_reach_is_the_one_it_was_parted_by() -> None:
    from l7r.diagram.hamletgen.homesteads.growth import settled_seat

    standing, guess, big = (10.0, 10.0, 10.0, 10.0), (5.0, 5.0, 5.0, 5.0), (9.0, 9.0, 9.0, 9.0)
    rolls = iter([big, (8.0, 8.0, 8.0, 8.0)])
    lot: list[Any] = []
    assert settled_seat((0.0, 0.0), standing, guess, 0.0, 0.0, 1.0, lambda q: next(rolls), None, lot) is not None
    assert lot == [big], "moved out to the union, and parted by it - not by the smaller reach rolled at the last seat"
    assert growth.land_box((0.0, 0.0), (10.0, 20.0, 5.0, 15.0)) == (5.0, 5.0, 30.0, 20.0)


def test_a_tight_seat_stands_on_its_neighbor_s_yard_side() -> None:
    """Feature 317 (`TIGHT_BEARING_DEG`): on the side of the house its yard lies on, as the drawing page places such a
    household - within 90 degrees of the bearing to the yard, never past the perpendicular or behind the house."""
    center, yard = (0.0, 0.0), (0.0, 10.0)  # the yard to the south (screen axes)
    assert growth.yard_side(center, yard, math.pi / 2), "toward the yard"
    off = math.radians(80.0)
    assert growth.yard_side(center, yard, math.pi / 2 - off) and growth.yard_side(center, yard, math.pi / 2 + off), "80 degrees off: the yard's side"
    off = math.radians(100.0)
    assert not growth.yard_side(center, yard, math.pi / 2 - off) and not growth.yard_side(center, yard, math.pi / 2 + off), "100 degrees off: past it"
    assert not growth.yard_side(center, yard, -math.pi / 2), "behind the house"


def test_the_tight_seats_offered_stand_on_the_yard_s_side(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(growth, "free_seats", lambda s, c, step=None: [(0.0, 0.0)])
    s = _Tight(room=30.0)
    s._passage_left = 1  # type: ignore[attr-defined]
    seats: list[tuple[float, float]] = []
    real = s.try_place
    s.try_place = lambda x, y, k: (seats.append((x, y)) if getattr(s, "_tight_of", None) is not None else None) or real(x, y, k)  # type: ignore[method-assign]
    grow_the_margin(s, _plan(3), 0, (46.0, 28.0))  # type: ignore[arg-type]
    assert seats and all(y > -1e-6 for _x, y in seats), "the first house's yard lies south: no tight seat north of it"


def test_the_built_share_is_the_homesteads_over_their_outline() -> None:
    """FR-007 (feature 318): four 100 x 100 homesteads at the corners of a 300 x 300 square cover 40,000 of the 90,000 their
    corners' hull holds; under three homesteads there is no outline."""
    homes = [{"geom": {"bbox": (x, y, 100.0, 100.0)}} for x, y in ((50.0, 50.0), (250.0, 50.0), (50.0, 250.0), (250.0, 250.0))]
    assert growth.built_share(homes) == round(40000.0 / 90000.0, 3)
    assert growth.built_share(homes[:2]) == 0.0 and growth.built_share([{"geom": {}}] * 3) == 0.0
    flat = [{"geom": {"bbox": (x, 0.0, 0.0, 0.0)}} for x in (0.0, 1.0, 2.0)]
    assert growth.built_share(flat) == 0.0, "a degenerate outline reports nothing"


def test_a_constructed_site_too_small_for_everyone_is_refused_naming_the_shortfall(monkeypatch: pytest.MonkeyPatch) -> None:
    """SC-003 (feature 318, FR-005): ground that holds only what fits within 120 px of the seat, asked for 200 households -
    the growth seats what the ground holds, widening until the canvas offers nothing new, and the seating is refused naming
    how many stood; every house it seated still stands."""
    from l7r.diagram.hamletgen.homesteads import stages
    from l7r.diagram.hamletgen.homesteads.capacity import SiteRefused

    monkeypatch.setattr(growth, "free_seats", lambda s, c, step=None: [(0.0, 0.0)])
    s = _Ground(room=40.0, ring=120.0)
    plan = SimpleNamespace(spec=SimpleNamespace(households=200, name="Tiny", seed=5), seat={"cx": 0.0, "cy": 0.0, "ladder": []}, field_archetype="hill")
    monkeypatch.setattr(stages, "seating_mark", lambda s_: ())
    monkeypatch.setattr(stages, "_seat_households", lambda s_, p_: (grow_the_margin(s_, p_, 0, (46.0, 28.0)), 0))
    with pytest.raises(SiteRefused, match=r"Tiny \(seed 5\): seated \d+ of 200 households on margin 1; no house is taken back") as got:
        stages.seat_every_household(s, plan)  # type: ignore[arg-type]
    stood = int(str(got.value).split("seated ")[1].split(" of")[0])
    assert 1 < stood == len(s.M["houses"]), "the shortfall named, and every house seated still standing"


def test_the_direction_jitter_scales_with_the_step_so_neighbors_never_cross() -> None:
    """`grow_jitter` (feature 318): 12 degrees either way at eight directions, 6 at sixteen - always under half the step."""
    assert growth.grow_jitter(8) == growth.GROW_JITTER_DEG and growth.grow_jitter(16) == growth.GROW_JITTER_DEG / 2.0
    assert all(2.0 * growth.grow_jitter(n) < 360.0 / n for n in (8, 12, 16))


def test_a_tight_seat_queued_while_the_share_had_room_is_passed_over_once_it_is_spent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 320: a tight seat is queued only while the passage share has room, but the share may be spent before the seat
    is popped - by any household seated in between. Popped then, it is no seat: no way stands while houses are seated to be
    near, so the household is never told a neighbor."""
    monkeypatch.setattr(growth, "free_seats", lambda s, c, step=None: [(0.0, 0.0)])

    class _Spends(_Tight):
        def try_place(self, x: float, y: float, _kind: str) -> bool:
            ok = super().try_place(x, y, _kind)
            if ok and len(self.M["houses"]) == 2:
                self._passage_left = 0  # type: ignore[attr-defined]  # the share spent by the second house, seated loose
            return ok

    s = _Spends(room=30.0)
    s._passage_left = 1  # type: ignore[attr-defined]
    grow_the_margin(s, _plan(6), 0, (46.0, 28.0))  # type: ignore[arg-type]
    assert len(s.M["houses"]) > 2 and all(t is None for t in s.told), "the tight seats queued by the first house were passed over"
