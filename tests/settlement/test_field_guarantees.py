"""Feature 287 (water W28-W30, W33, W34, W37, plan D9): what the comb field's drawing guarantees where it decides.

Each test drives the placer - `carve_around_grave`, a grave or pond seat, `draw_comb_field` or its bead drop - on
constructed inputs that include the violating case, and asks the rule's one predicate (`waterfields/ring_rules.py`, or
the rule's own record) of what it made.
"""

import copy
import math

from l7r.diagram.pipeline import rollcache
from l7r.diagram.settlement import Settlement


def _comb() -> dict:
    """One small comb net, built once on disk (as `tests/settlement/test_fields.py` builds its own) and deep-copied per
    caller, because drawing and carving MUTATE the net."""
    from tests.waterfields._builders import lay_comb

    key = "test_field_guarantees-comb:v1"
    return copy.deepcopy(rollcache.obtain(key, lambda: lay_comb(1400, 1400, (700, 200), 1, down_deg=90, field_fall=400, grain=2.0, supply_banks=True))[0])


def _lattice(n: int, side: float = 40.0) -> list[dict]:
    return [{"poly": [(i * side, j * side), ((i + 1) * side, j * side), ((i + 1) * side, (j + 1) * side), (i * side, (j + 1) * side)], "fill": "#A6C398"} for j in range(n) for i in range(n)]


def _area(plots: list[dict]) -> float:
    from shapely.geometry import Polygon
    from shapely.ops import unary_union

    return float(unary_union([Polygon(p["poly"]).buffer(0) for p in plots]).area)


def test_a_plot_drawn_after_the_water_is_painted_under_every_channel(tmp_path) -> None:
    """W38: a settlement that draws a channel and THEN a plot - the stage order that buried a village's ditches - emits the
    plot before the channel, because every plot goes through the paddy layer (`add_paddy`) and `finish` lifts one drawn
    after the water block's anchor to the block's front."""
    s = Settlement(W=600, H=600, seed=1)
    s.meta(name="Pl", scale="hamlet", ftpx=1, down_deg=90)
    s.field_channel([(100.0, 300.0), (500.0, 300.0)], "#6C9CBE", 3.0, 3.0)
    s.add_paddy('<polygon points="80,250 520,250 520,350 80,350" fill="#A6C398" stroke="#8FA87A" stroke-width="2"/>', cls="paddy")
    s.add_paddy('<polygon points="0,0 10,0 10,10" fill="#A6C398"/>', cls="paddy")
    s.finish(str(tmp_path / "p"), render=False)
    svg = (tmp_path / "p.svg").read_text()
    assert 0 <= svg.index("<polygon points=\"80,250") < svg.index('stroke="#6C9CBE"'), "the plot is painted before the channel"
    assert svg.index('<polygon points="0,0') < svg.index('stroke="#6C9CBE"')


def _turn_deg(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    h0, h1 = math.atan2(b[1] - a[1], b[0] - a[0]), math.atan2(c[1] - b[1], c[0] - b[0])
    return abs(math.degrees((h1 - h0 + math.pi) % (2 * math.pi) - math.pi))
