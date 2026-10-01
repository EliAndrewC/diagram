"""Feature 269 group E7: the village windbreak belt's two forms, conifer-led in rank or mixed broadleaf (B30, research/contents.json#vegetation "Shelter belts on a village's windward side")."""

import math
import re

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._knobs import KNOBS
from l7r.diagram.settlement.homestead_parts.groves import WINDBREAK_BELT_FORMS, belt_centerline, belt_walk, rank_points
from tests.settlement._builders import _nuc_village

CONIFER = 'fill="#496733"'


def _hamlet() -> Settlement:
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="G", scale="hamlet", ftpx=1)
    return s


def test_the_belt_knob_rolls_between_the_two_attested_forms():
    knob = KNOBS["windbreak_belt"]
    assert tuple(knob.value_space) == WINDBREAK_BELT_FORMS == ("conifer_led", "mixed_broadleaf")
    assert {knob.roll(seed, {}) for seed in range(40)} == set(WINDBREAK_BELT_FORMS), "both forms are reachable from a seed"


def _arc(n: int = 40) -> list[tuple[float, float]]:
    """Clump seats on a quarter circle of radius 300 about (0, 0) - a bent belt like Inashiro's crescent, three seats deep."""
    return [(r * math.cos(a), r * math.sin(a)) for k in range(n) for a in [math.pi / 2 * k / (n - 1)] for r in (280.0, 300.0, 320.0)]


def test_the_centerline_follows_a_bent_belt():
    line = belt_centerline(_arc(), 40.0)
    inner = line[1:-1]
    assert len(inner) >= 5
    assert all(abs(math.hypot(x, y) - 300.0) < 25.0 for x, y in inner), "the inner vertices stay on the arc, not on its chord"
    assert len(belt_centerline([(5.0, 5.0)], 40.0)) == 4, "one seat still gives a line, carried on at both ends"
    assert len(belt_centerline([(0.0, 0.0), (50.0, 0.0)], 40.0)) == 4


def test_the_centerline_follows_a_belt_that_turns_back_on_its_axis():
    """Round 2 of the settlement-review: Inashiro's crescent turns back on its principal axis at its tip, and binning along
    that axis averaged across the turn. A U - a half circle, three seats deep - is walked, so every vertex stays on it."""
    seats = [(r * math.cos(a), r * math.sin(a)) for k in range(60) for a in [math.pi * k / 59] for r in (280.0, 300.0, 320.0)]
    inner = belt_centerline(seats, 40.0)[1:-1]
    assert len(inner) >= 15 and all(abs(math.hypot(x, y) - 300.0) < 25.0 for x, y in inner)


def test_the_walk_bridges_a_gap_in_the_belt():
    seats = [(20.0 * k, 0.0) for k in range(5)] + [(200.0 + 20.0 * k, 0.0) for k in range(5)]  # a 120 ft hole in the middle
    walked = belt_walk(seats, 40.0)
    assert walked[4] == 80.0 and walked[5] == 200.0 and walked[9] == 280.0


def test_the_rows_run_along_the_belt_as_drawn():
    """The settlement-review's finding: one straight axis set a bent arm's rows across it. Each row is an offset of the
    centerline, so a row's points keep their distance from the arc's center, and neighbors along a row are `along` apart."""
    line = belt_centerline(_arc(), 40.0)
    pts = rank_points(line, 40.0, 20.0, 26.0)
    radii = sorted({round(math.hypot(x, y) / 26.0) for x, y in pts if 0.3 < math.atan2(y, x) < 1.2})
    assert len(radii) >= 3, "several rows"
    for x, y in pts:
        if 0.3 < math.atan2(y, x) < 1.2:  # away from the carried-on ends
            d = math.hypot(x, y)
            assert min(abs(d - (300.0 + j * 26.0)) for j in range(-2, 3)) < 6.0, "every point sits on a row concentric with the belt"
    row = sorted(((math.atan2(y, x), x, y) for x, y in pts if abs(math.hypot(x, y) - 300.0) < 6.0 and 0.3 < math.atan2(y, x) < 1.2))
    gaps = [math.hypot(b[1] - a[1], b[2] - a[2]) for a, b in zip(row, row[1:], strict=False)]
    assert gaps and all(15.0 < g < 22.0 for g in gaps)


def test_a_conifer_led_clump_draws_only_lesser_crowns():
    s = _hamlet()
    tally: dict[str, int] = {}
    s._draw_grove(400.0, 400.0, 80.0, 80.0, face=(0, -1), mix="conifer_led", tally=tally)
    assert CONIFER not in s.out[-1] and tally.get("broadleaf", 0) > 0 and "conifer" not in tally


def test_a_mixed_broadleaf_clump_draws_no_conifer():
    s = _hamlet()
    tally: dict[str, int] = {}
    s._draw_grove(400.0, 400.0, 80.0, 80.0, face=(0, -1), mix="mixed_broadleaf", tally=tally)
    assert CONIFER not in s.out[-1] and tally.get("broadleaf", 0) > 0 and "conifer" not in tally


@pytest.mark.parametrize("form", WINDBREAK_BELT_FORMS)
def test_the_village_belt_draws_and_declares_its_form(form):
    s = _nuc_village()
    s.pin_knob("windbreak_belt", form)
    s.village_grove([(150, 350), (260, 330), (280, 640), (160, 660)], role="windbreak")
    g = s.M["village_groves"][0]
    assert s.M["meta"]["windbreak_belt"] == form == g["form"]
    assert (g["crowns"].get("conifer", 0) > 0) == (form == "conifer_led")
    assert g["crowns"].get("broadleaf", 0) > 0


def test_the_rows_are_painted_over_every_clump_and_seated_first():
    """The settlement-review's second finding: painted per clump, a later clump's broadleaf lay over an earlier clump's
    conifers. The rows are one group after every clump, and no lesser crown stands centered under a row conifer."""
    s = _nuc_village()
    s.pin_knob("windbreak_belt", "conifer_led")
    s.village_grove([(150, 350), (260, 330), (280, 640), (160, 660)], role="windbreak")
    g = s.M["village_groves"][0]
    belt = [svg for svg, cls in zip(s.out, s.out_cls, strict=True) if cls == "windbreak"]
    last = belt[-1]
    assert CONIFER in last and all(CONIFER not in svg for svg in belt[:-1]), "every conifer is in the one group painted last"
    rows = [(float(x), float(y), float(r)) for x, y, r in re.findall(r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="([\d.]+)"', last)]
    assert len(rows) == g["crowns"]["conifer"] > g["crowns"]["broadleaf"], "the conifer is the commonest crown (the entry's guess)"
    crowns = s.M["tree_crowns"]
    others = [(crowns[i], crowns[i + 1], crowns[i + 2]) for i in range(0, len(crowns), 3)]
    others = [c for c in others if all(abs(c[0] - x) > 0.2 or abs(c[1] - y) > 0.2 for x, y, _ in rows)]
    assert others and all((cx - x) ** 2 + (cy - y) ** 2 >= max(r, cr) ** 2 - 1.0 for x, y, r in rows for cx, cy, cr in others)


def test_row_points_off_the_belt_ground_in_the_marsh_or_on_a_roof_are_refused():
    s = _nuc_village()
    seated = [(200.0 + 20 * k, 400.0) for k in range(6)]
    wet = [[(250.0, 380.0), (300.0, 380.0), (300.0, 420.0), (250.0, 420.0)]]
    s.M["houses"].append({"x": 220.0, "y": 400.0, "w": 12.0, "h": 10.0})
    s.M["tree_crowns"] += [310.0, 400.0, 30.0]  # an earlier stand's broad crown over the belt's east end
    rows, ink = s._belt_ranks(seated, 28.0, wet)
    assert all((x - 310.0) ** 2 + (y - 400.0) ** 2 >= 30.0**2 for x, y, _r in rows), "no row conifer stands under an earlier crown"
    assert rows and ink.startswith("<g>")
    for x, y, r in rows:
        assert 186 - 3 <= x <= 314 + 3 and 386 - 3 <= y <= 414 + 3, "on the clumps' ground"
        assert max(abs(x - 220.0) - 6.0, 0.0) ** 2 + max(abs(y - 400.0) - 5.0, 0.0) ** 2 >= r**2, "no crown on the roof"
    assert all(not (252 <= x <= 298) for x, _y, _r in rows), "the marsh stretch draws no row conifer"


def test_the_copse_is_not_a_belt_form():
    s = _nuc_village()
    s.village_grove([(200, 300), (500, 300), (500, 500), (200, 500)], role="copse", dense=False)
    g = s.M["village_groves"][0]
    assert g["form"] is None and "windbreak_belt" not in s.M["meta"]
