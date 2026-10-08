"""A placement written as SVG (feature 266): one caption and leader writer for the Mode A paths."""

from l7r.diagram.labels import ObstacleIndex, Subject, place
from l7r.diagram.labels.geom import rect
from l7r.diagram.labels.svg import caption_svg, leader_svg

BOARD = Subject("point", tuple(rect(100.0, 100.0, 10.0, 4.0)))


def test_a_level_one_line_caption() -> None:
    p = place("well", 8.0, BOARD, ObstacleIndex())
    out = caption_svg(p, 8.0, ' font-style="italic"', "#333", "well")
    assert out.startswith("<text ") and "transform" not in out and 'data-kind="well"' in out and ">well</text>" in out
    assert leader_svg(p, 8.0, "#333") == "", "at the preferred offset: no leader"


def test_a_turned_wrapped_caption_with_a_leader() -> None:
    from l7r.diagram.labels import Obstacle

    tilted = Subject("point", tuple(rect(100.0, 100.0, 10.0, 4.0, 30.0)), angle=30.0)
    walls = ObstacleIndex([Obstacle(tuple(rect(100.0, 100.0, 60.0, 40.0)), 1000.0)])
    p = place("a & b", 8.0, tilted, ObstacleIndex(), lines=["a &", "b"])
    out = caption_svg(p, 8.0, "", "#333")
    assert 'transform="rotate(30.0' in out and "<tspan" in out and "a &amp;" in out and "data-kind" not in out
    far = place("notice board", 8.0, BOARD, walls)
    line = leader_svg(far, 8.0, "#333", "notice board", mark=True)
    assert far.leader is not None and line.startswith("<line ") and 'data-leader="1"' in line and 'data-kind="notice board"' in line
