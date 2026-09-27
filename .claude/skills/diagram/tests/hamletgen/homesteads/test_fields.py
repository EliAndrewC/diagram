"""The homestead field (`hamletgen/homesteads/fields.py`, feature 261) on stub settlements - no roll."""

from __future__ import annotations

from typing import Any

from l7r.diagram.hamletgen.homesteads import fields
from l7r.diagram.hamletgen.homesteads.stages import water_push


class _S:
    """A settlement with one homestead box at the origin and nothing else on the ground unless a test puts it there."""

    def __init__(self, **M: Any) -> None:
        self.M: dict[str, Any] = {"meta": {}, "houses": [{"x": 0.0, "y": 0.0}], **M}
        self.placed: list[Any] = [(0.0, 0.0, 100.0, 80.0), (0.0, 0.0, 10.0, 10.0)]
        self.hard_polys: list[Any] = []
        self.block_polys: list[Any] = []
        self.dry_polys: list[Any] = []
        self.drawn: list[str] = []
        self.blocked: Any = None

    def _envelope_blocked(self, rect: Any) -> Any:
        return self.blocked

    def add(self, svg: str, cls: str | None = None) -> None:
        self.drawn.append(svg)

    def _draw_furrows(self, poly: Any, color: str, theta: float, cls: str | None = None) -> None:
        self.drawn.append("furrows")


class _Plan:
    class spec:  # noqa: N801 - the attribute the stage reads off a SitePlan
        seed = 7

    wind = (0.0, -1.0)  # from the north


def test_the_steading_is_the_largest_box_holding_the_house() -> None:
    """`homestead_box`: of the reserved boxes round the house, the whole steading's - and none when no box holds it."""
    assert fields.homestead_box([(0.0, 0.0, 10.0, 10.0), (0.0, 0.0, 100.0, 80.0), (500.0, 0.0, 400.0, 400.0)], 0.0, 0.0) == (0.0, 0.0, 100.0, 80.0)
    assert fields.homestead_box([(500.0, 0.0, 10.0, 10.0)], 0.0, 0.0) is None


def test_a_plot_lies_against_a_side_never_the_windward_one_and_the_lee_first() -> None:
    """`side_plots`: three candidates for a north wind - the lee (south) side first - each a bund's width off the box,
    as long as the side it lies against (clamped) and `depth` deep."""
    plots = fields.side_plots((0.0, 0.0, 100.0, 80.0), 36.0, (0.0, -1.0))
    normals = [n for n, _ in plots]
    assert (0.0, -1.0) not in normals and normals[0] == (0.0, 1.0) and len(plots) == 3
    south = plots[0][1]
    assert min(p[1] for p in south) == 40.0 + fields.HOMESTEAD_FIELD_GAP_FT and max(p[1] for p in south) - min(p[1] for p in south) == 36.0
    assert max(p[0] for p in south) - min(p[0] for p in south) == 100.0
    east = next(r for n, r in plots if n == (1.0, 0.0))
    assert max(p[1] for p in east) - min(p[1] for p in east) == 80.0  # the side it lies against
    assert (
        max(p[0] for n, r in fields.side_plots((0.0, 0.0, 20.0, 20.0), 36.0, (0.0, -1.0))[:1] for p in r)
        - min(p[0] for n, r in fields.side_plots((0.0, 0.0, 20.0, 20.0), 36.0, (0.0, -1.0))[:1] for p in r)
        == fields.HOMESTEAD_FIELD_LEN_FT[0]
    )  # a short side, clamped up


def test_a_plot_keeps_its_clearance_from_a_line() -> None:
    """`ring_clear_of_lines`: a lane through the ring, one with an end inside it, one passing within its clearance, and
    one well clear - and a line far off is skipped by its box."""
    ring = [(0.0, 0.0), (40.0, 0.0), (40.0, 20.0), (0.0, 20.0)]
    assert not fields.ring_clear_of_lines(ring, [([(-10.0, 10.0), (50.0, 10.0)], 2.0)])
    assert not fields.ring_clear_of_lines(ring, [([(20.0, 10.0), (20.0, 80.0)], 2.0)])
    assert not fields.ring_clear_of_lines(ring, [([(-10.0, 23.0), (50.0, 23.0)], 5.0)])
    assert fields.ring_clear_of_lines(ring, [([(-10.0, 30.0), (50.0, 30.0)], 5.0), ([(500.0, 500.0), (600.0, 500.0)], 5.0)])


def test_a_plot_keeps_clear_of_a_well_or_a_fixture() -> None:
    """`ring_clear_of_items`: an item within its radius of the ring's box refuses it; one beyond does not."""
    ring = [(0.0, 0.0), (40.0, 0.0), (40.0, 20.0), (0.0, 20.0)]
    assert not fields.ring_clear_of_items(ring, [(45.0, 10.0, 8.0)])
    assert fields.ring_clear_of_items(ring, [(60.0, 10.0, 8.0)])


def test_a_plot_fits_only_on_open_dry_ground_on_its_houses_bank() -> None:
    """`homestead_field_fits`: refused where the ground refuses the envelope, on a lane, beside a fixture, in the marsh,
    and across a stream from its house; admitted on open ground."""
    ring = [(-50.0, 44.0), (50.0, 44.0), (50.0, 80.0), (-50.0, 80.0)]
    s = _S()
    assert fields.homestead_field_fits(s, ring, (0.0, 0.0), [], [], [], [])  # type: ignore[arg-type]
    s.blocked = True
    assert not fields.homestead_field_fits(s, ring, (0.0, 0.0), [], [], [], [])  # type: ignore[arg-type]
    s.blocked = None
    assert not fields.homestead_field_fits(s, ring, (0.0, 0.0), [([(-80.0, 60.0), (80.0, 60.0)], 4.0)], [], [], [])  # type: ignore[arg-type]
    assert not fields.homestead_field_fits(s, ring, (0.0, 0.0), [], [], [(0.0, 90.0, 12.0)], [])  # type: ignore[arg-type]
    assert not fields.homestead_field_fits(s, ring, (0.0, 0.0), [], [], [], [[(-100.0, 50.0), (100.0, 50.0), (100.0, 200.0), (-100.0, 200.0)]])  # type: ignore[arg-type]
    assert not fields.homestead_field_fits(s, ring, (0.0, 0.0), [], [[(-200.0, 30.0), (200.0, 30.0)]], [], [])  # type: ignore[arg-type]


def test_each_house_gets_one_plot_where_one_fits_and_the_count_is_recorded() -> None:
    """`stage_homestead_fields`: one plot per house with room, drawn, registered as dry and no-build crop and as a placed
    box, marked `homestead`; a house with no steading box or no clear side gets none."""
    s = _S(
        lanes=[{"pts": [[-500.0, 500.0], [500.0, 500.0]]}, {"pts": [[0.0, 0.0]]}],
        streams=[{"poly": [[-500.0, 900.0], [500.0, 900.0]]}],
        wells=[{"x": 2000.0, "y": 2000.0}],
        farm_fixtures=[{"x": 3000.0, "y": 3000.0}],
        marshes=[{"poly": [[4000.0, 4000.0], [4100.0, 4000.0], [4100.0, 4100.0]]}],
    )
    s.M["houses"].append({"x": 9000.0, "y": 9000.0})  # no steading box: skipped
    fields.stage_homestead_fields(s, _Plan())  # type: ignore[arg-type]
    assert s.M["meta"]["homestead_fields"] == 1
    plot = s.M["dry_plots"][0]
    assert plot["homestead"] and plot["crop"] and len(plot["poly"]) == 4
    assert s.block_polys and s.dry_polys and len(s.placed) == 3 and "furrows" in s.drawn
    s2 = _S()
    s2.blocked = True
    fields.stage_homestead_fields(s2, _Plan())  # type: ignore[arg-type]
    assert s2.M["meta"]["homestead_fields"] == 0 and "dry_plots" not in s2.M


def test_a_front_seat_is_pushed_across_a_brook_by_the_waters_reach() -> None:
    """`water_push` (feature 261): a box whose near side a water course lies across moves along `n` past the course by its
    clearance; a course beside the box but beyond its lateral span, or one far off, moves nothing."""
    brook = [((-100.0, 10.0), (100.0, 10.0), 5.0)]  # across the box, 10 ft past its near edge at 0
    assert water_push(brook, (0.0, 20.0), (0.0, 1.0), 30.0, 0.0, 40.0) == 15.0
    assert water_push([((200.0, -50.0), (200.0, 90.0), 5.0)], (0.0, 20.0), (0.0, 1.0), 30.0, 0.0, 40.0) == 0.0
    assert water_push([((5000.0, 0.0), (5100.0, 0.0), 5.0)], (0.0, 20.0), (0.0, 1.0), 30.0, 0.0, 40.0) == 0.0
