"""A hand-drawn sheet's captions placed by the one placer (features 266, 286): read, declare, place, write, render."""

from __future__ import annotations

import math
import re

import pytest

from l7r.diagram.labels import Placement, Subject
from l7r.diagram.labels import hand_sheet as sl

HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">\n'
BACK = '  <rect x="0" y="0" width="400" height="300" fill="#EFE3C2" data-kind="-"/>\n'


def _sheet(*body: str) -> str:
    return HEAD + BACK + "".join(body) + "</svg>\n"


BOARD = '  <g data-kind="notice board">\n    <rect x="190" y="140" width="20" height="8"/>\n    <text font-size="9" font-style="italic" fill="#5C4830">notice board</text>\n  </g>\n'


def test_transforms_compose() -> None:
    assert sl.parse_transform(None) == sl.IDENTITY
    m = sl.parse_transform("translate(10,20) scale(2) rotate(90 5 5) matrix(1 0 0 1 3 4)")
    x, y = sl._apply(m, (0.0, 0.0))
    assert (round(x, 6), round(y, 6)) == (10.0 + 2 * (10 - 4), 20.0 + 2 * 3)
    assert sl.parse_transform("translate(7)")[4] == 7.0 and sl.parse_transform("scale(2 3)")[3] == 3.0
    assert round(sl._angle(sl.parse_transform("rotate(30)")), 6) == 30.0


def test_a_path_is_read_as_its_vertices() -> None:
    assert sl._path_points("M 10 10 L 20 10 H 30 V 40 l 5 5 h 1 v 1 C 1 1 2 2 50 50 Z") == [
        (10.0, 10.0),
        (20.0, 10.0),
        (30.0, 10.0),
        (30.0, 40.0),
        (35.0, 45.0),
        (36.0, 45.0),
        (36.0, 46.0),
        (50.0, 50.0),
    ]


def test_every_drawn_element_is_read_in_sheet_coordinates() -> None:
    src = _sheet(
        '  <g transform="translate(5,0)" stroke="#000" stroke-width="40" data-kind="road"><path d="M 0 250 L 400 250" fill="none"/></g>\n',
        '  <circle cx="50" cy="50" r="5" data-kind="well"/>\n',
        '  <ellipse cx="80" cy="50" rx="6" ry="3" data-kind="pond"/>\n',
        '  <polygon points="100,100 120,100 110,120" data-kind="shrine"/>\n',
        '  <polyline points="0,10 50,10" fill="none" stroke="#000" stroke-width="2" data-kind="fence"/>\n',
        '  <line x1="0" y1="20" x2="10" y2="20" stroke="#000" stroke-width="6" data-kind="court divider"/>\n',
        '  <path d="M 300 20 L 320 20 L 320 40 Z" fill="#000" data-kind="altar"/>\n',
        '  <text x="10" y="290" font-size="10" data-kind="-">title <tspan>ignored</tspan></text>\n',
        '  <text x="390" y="290" font-size="10" text-anchor="end" data-kind="-"><tspan>two</tspan><tspan dy="11">lines</tspan></text>\n',
        '  <rect x="1" y="1" width="0" height="0" data-kind="-"/><line x1="1" y1="1" x2="1" y2="1"/><polygon points="1,1"/>\n',
    )
    shapes, view = sl.read_sheet(src)
    assert view == (0.0, 0.0, 400.0, 300.0)
    road = next(s for s in shapes if s.kind == "road")
    assert road.line and road.half == 20.0 and road.poly[0] == (5.0, 250.0), "a stroked road is a band, turned with its group"
    assert next(s for s in shapes if s.kind == "fence").line
    assert not next(s for s in shapes if s.kind == "altar").line, "a filled path is an outline"
    two = [s for s in shapes if s.tag == "text" and s.lines == ["two", "lines"]]
    assert two and two[0].center[0] < 390.0, "an end-anchored text's block stands left of its anchor"


def test_the_sheet_is_classified_by_its_tags() -> None:
    src = _sheet(
        '  <rect x="10" y="10" width="100" height="100" data-kind="outer court"/>\n',
        '  <rect x="200" y="10" width="60" height="20" data-kind="-"/>\n',
        '  <rect x="10" y="200" width="30" height="20" data-kind="river"/>\n',
        '  <line x1="0" y1="150" x2="400" y2="150" stroke="#000" stroke-width="10" data-kind="road"/>\n',
        '  <line x1="0" y1="180" x2="400" y2="180" stroke="#000" stroke-width="6" data-kind="court divider"/>\n',
        '  <line x1="0" y1="190" x2="4" y2="190" stroke="#000" data-kind="door" data-leader="1"/>\n',
        '  <text x="300" y="250" font-size="9" data-kind="garden">garden</text>\n',
    )
    shapes, view = sl.read_sheet(src)
    idx = sl.classify(shapes, view)
    weights = sorted(o.weight for o in idx.obstacles)
    assert weights == [500.0, 1000.0, 2000.0, 10000.0], "the river fill, the scale-bar-like `-` rect, the divider band in black ink (dark weighs double), the text (weighs ten) - feature 267"
    assert len(idx.ways) == 1 and idx.ways[0].half_width == 5.0


def test_a_caption_names_its_group_or_its_declared_ids() -> None:
    """Feature 286 (plan D1): a group's one caption names the group's drawn shapes; a caption among several, or tagged
    on its own, names the `data-id`s its `data-names` lists (an id on a group marks everything in it). Where it stands
    is never read."""
    src = _sheet(
        BOARD,
        '  <g data-kind="latrine"><rect x="300" y="40" width="20" height="10" data-id="east"/><rect x="40" y="40" width="20" height="10" data-id="west"/>'
        '<text font-size="8" data-names="east">latrine</text><text font-size="8" data-names="west">latrine</text></g>\n',
        '  <g data-id="wells"><circle cx="100" cy="250" r="4" data-kind="well"/><circle cx="120" cy="250" r="4" data-kind="well"/></g>\n',
        '  <text font-size="8" data-kind="well" data-names="wells">wells</text>\n',
    )
    shapes, _view = sl.read_sheet(src)
    caps = sl.captions_of(shapes)
    assert [shapes[c[0]].text for c in caps] == ["notice board", "latrine", "latrine", "wells"]
    board = sl.declared_parts(shapes[caps[0][0]], shapes, alone=True)
    assert [sl.bbox(s.poly) for s in board] == [(190.0, 140.0, 210.0, 148.0)]
    west = sl.declared_parts(shapes[caps[2][0]], shapes, alone=False)
    assert [sl.bbox(s.poly) for s in west] == [(40.0, 40.0, 60.0, 50.0)], "one of several like parts, by its id"
    assert len(sl.declared_parts(shapes[caps[3][0]], shapes, alone=True)) == 2, "an id on a group names all of it"


def test_a_caption_that_names_nothing_is_refused() -> None:
    """A caption is never dropped (feature 266): one whose declaration names nothing drawn stops the render with the fix."""
    for body, why in (
        ('  <text font-size="8" data-kind="well">well</text>\n', "names nothing"),
        ('  <circle cx="1" cy="1" r="1" data-kind="well"/><text font-size="8" data-kind="well" data-names="nope">well</text>\n', "mark no drawn shape"),
        ('  <g data-kind="well"><text font-size="8">a</text><text font-size="8">b</text><circle cx="1" cy="1" r="1"/></g>\n', "names nothing"),
        ('  <g data-kind="well"><text font-size="8">only words</text></g>\n', "names nothing"),
    ):
        with pytest.raises(ValueError, match=why):
            sl.seat(_sheet(body))
    with pytest.raises(ValueError, match="no caption comes before it"):
        sl.captions_of(sl.read_sheet(_sheet('  <text font-size="8" data-kind="well" data-cont="1">x</text>\n'))[0])


def test_a_continued_line_joins_the_caption_before_it() -> None:
    src = _sheet(
        '  <g data-kind="granary"><rect x="100" y="100" width="130" height="78"/><text font-size="13">granary</text><text font-size="9" data-cont="1">staging store</text></g>\n',
        '  <text font-size="9" data-kind="-">title</text>\n',
    )
    shapes, _view = sl.read_sheet(src)
    caps = sl.captions_of(shapes)
    assert [[shapes[i].text for i in c] for c in caps] == [["granary", "staging store"]], "the title is the sheet's own drawing"


def test_a_subject_is_tried_inside_then_beside() -> None:
    """Feature 286 (plan D2): an area's name inside it first, the standard's seat, then beside it; a stepped building
    by each block, largest first; a scatter of glyphs beside only; an elongated area named along it."""

    def r(x: float, y: float, w: float, h: float, tag: str = "rect") -> sl.Shape:
        return sl.Shape(tag, "k", [(x, y), (x + w, y), (x + w, y + h), (x, y + h)])

    one = sl.subjects([r(0, 0, 100, 40)])
    assert [s.kind for s in one] == ["area", "point"] and one[0].angle == 0.0
    assert sl.subjects([r(0, 0, 10, 100)])[0].angle == 90.0, "a tall band is named along its length"
    full = sl.subjects([r(0, 0, 100, 40), r(100, 0, 100, 40)])
    assert [(s.kind, sl.bbox(list(s.poly))) for s in full] == [("area", (0.0, 0.0, 200.0, 40.0)), ("point", (0.0, 0.0, 200.0, 40.0))]
    west, east = r(0, 0, 100, 40), r(110, 30, 80, 40)
    stepped = sl.subjects([west, east])
    assert [s.kind for s in stepped] == ["area", "area", "point", "point"] and stepped[0].poly == tuple(west.poly), "each block, largest first"
    garden = sl.Shape("path", "k", [(0.0, 0.0), (100.0, 0.0), (100.0, 30.0), (30.0, 30.0), (30.0, 100.0), (0.0, 100.0)])
    held = sl.subjects([garden, r(10, 10, 5, 5)])
    assert [s.kind for s in held] == ["area", "point"] and held[0].poly == tuple(garden.poly), "an outline holding its lantern is the area"
    pines = sl.subjects([r(0, 0, 10, 10, "circle"), r(40, 40, 10, 10, "circle")])
    assert [s.kind for s in pines] == ["point", "point", "point"], "three pines have no inside: beside the group, then beside each"
    assert sl.bbox(list(pines[1].poly)) == (0.0, 0.0, 10.0, 10.0)
    tubs = sl.subjects([r(0, 0, 10, 10, "circle"), r(400, 300, 10, 10, "circle")], 8.0)
    assert [sl.bbox(list(s.poly)) for s in tubs] == [(0.0, 0.0, 10.0, 10.0), (400.0, 300.0, 410.0, 310.0)], "spread past the reach: beside a tub only"
    line = sl.Shape("line", "k", [(0.0, 0.0), (50.0, 0.0)], half=1.0, line=True)
    assert [s.kind for s in sl.subjects([line])] == ["point"]
    ring = sl.Shape("polygon", "k", [(0.0, 0.0), (60.0, 0.0), (60.0, 60.0), (30.0, 80.0), (0.0, 60.0)])
    assert sl.subjects([ring])[1].angle == 0.0, "a five-sided outline stands level"


def test_a_caption_of_several_texts_wraps_by_the_standard() -> None:
    shapes, _view = sl.read_sheet(
        _sheet('  <g data-kind="tally"><rect x="0" y="0" width="80" height="56"/><text font-size="11">tally office</text><text font-size="9" data-cont="1">barge manifests &amp; seals</text></g>\n')
    )
    caps = [s for s in shapes if s.tag == "text"]
    ways = sl.wraps(caps)
    assert ways[0] == [["tally office"], ["barge manifests & seals"]] and ways[1] == [["tally", "office"], ["barge manifests", "& seals"]]
    assert len(ways) == 3
    fixed = sl.Shape("text", "k", [], lines=["INNER", "COURT"], size=13.0)
    assert sl.wraps([fixed, caps[1]])[1][0] == ["INNER", "COURT"], "a text the sheet breaks keeps its breaks"
    assert sl.fits_inside(caps, [s for s in shapes if s.tag == "rect" and s.kind == "tally"]) is False
    assert sl.fits_inside(caps[:1], [sl.Shape("rect", "k", [(0.0, 0.0), (300.0, 0.0), (300.0, 100.0), (0.0, 100.0)])])


def test_placement_is_a_function_of_the_drawing_alone() -> None:
    """SC-001: a caption's coordinates, anchor and turn on the sheet change nothing - the placer decides."""
    walls = "".join(f'  <rect x="{x}" y="{y}" width="30" height="30" data-kind="house"/>\n' for x in range(100, 300, 30) for y in range(80, 220, 30) if not (180 <= x <= 210 and y <= 150))
    src = _sheet(walls, BOARD)
    moved = src.replace('<text font-size="9"', '<text x="7" y="290" text-anchor="end" transform="rotate(30)" font-size="9"')
    assert moved != src and sl.placed(moved) == sl.placed(src)
    out = sl.placed(src)
    assert 'data-leader="1"' in out, "hemmed in, the caption stands out further and a leader ties it back"
    assert sl.placed(_sheet(BOARD)).count("<text") == 1 and 'data-leader="1"' not in sl.placed(_sheet(BOARD))


def test_each_caption_avoids_every_one_placed() -> None:
    boards = BOARD + '  <g data-kind="notice board">\n    <rect x="215" y="140" width="20" height="8"/>\n    <text font-size="9">bounty board</text>\n  </g>\n'
    placed = sl.seat(_sheet(boards))
    (_a, first, _pa), (_b, second, _pb) = placed
    fx0, fy0, fx1, fy1 = sl.bbox(list(first.block))
    sx0, sy0, sx1, sy1 = sl.bbox(list(second.block))
    assert fx1 <= sx0 or sx1 <= fx0 or fy1 <= sy0 or sy1 <= fy0


def test_a_stranded_caption_is_freed_by_lifting_a_neighbor() -> None:
    """The repair pass (feature 286): a caption left covering ink is tried with each near neighbor lifted, and the pair
    is kept where the two together cover less - Ochiba's stables had taken the garrison latrine's one free seat. A far
    caption is never lifted."""

    def at(x: float, cost: float) -> sl.Seated:
        return (Placement(x, 0.0, 0.0, ("a",), ((x, 0.0), (x + 10, 0.0), (x + 10, 5.0), (x, 5.0)), 0, 0, "right", cost, None), [["a"]])

    boxes = {"A": (0.0, 0.0, 10.0, 5.0), "B": (30.0, 0.0, 40.0, 5.0), "C": (500.0, 0.0, 510.0, 5.0)}
    sizes = dict.fromkeys(boxes, 9.0)
    done = {"A": at(0, 1000.0), "C": at(500, 0.0), "B": at(30, 0.0)}
    calls: list[tuple[str, bool, int]] = []

    def one(k: str, rest: list[Placement], quick: bool = False) -> sl.Seated:
        calls.append((k, quick, len(rest)))
        return at(20, 0.0) if k == "A" else at(40, 0.0)

    sl.repair(done, boxes, sizes, one)
    assert done["A"][0].cost == 0.0 and done["B"][0].x == 40, "A freed; B re-placed no worse"
    assert calls == [("A", True, 1), ("B", False, 2)], "only the near neighbor is lifted, the lift tries the standard's seats"
    worse = {"A": at(0, 1000.0), "B": at(30, 0.0)}
    sl.repair(worse, boxes, sizes, lambda k, rest, quick=False: at(20, 0.0) if k == "A" else at(40, 50.0))
    assert worse["A"][0].cost == 0.0 and worse["B"][0].cost == 50.0, "a little worse for the neighbor, much better for the pair"
    even = {"A": at(0, 1000.0), "B": at(30, 0.0)}
    sl.repair(even, boxes, sizes, lambda k, rest, quick=False: at(20, 0.0) if k == "A" else at(40, 1000.0))
    assert even["A"][0].cost == 1000.0, "a swap that only moves the ink is not a repair"
    stuck = {"A": at(0, 1000.0), "B": at(30, 0.0)}
    sl.repair(stuck, boxes, sizes, lambda k, rest, quick=False: at(20, 1000.0))
    assert stuck["A"][0].x == 0, "no freer seat, nothing moves"


def test_start_tags_are_the_elements_in_document_order() -> None:
    src = '<svg><!-- <rect/> --><?pi x?><g><rect/></g><text>a</text></svg>'
    assert [src[a:b] for a, b in sl.start_tags(src)] == ["<svg>", "<g>", "<rect/>", "<text>"]


def test_a_translated_caption_is_written_in_its_group_and_keeps_its_tag() -> None:
    src = _sheet('  <g transform="translate(50,0)"><rect x="100" y="100" width="20" height="8" data-kind="well" data-id="w"/><text font-size="9" data-kind="well" data-names="w">well</text></g>\n')
    out = sl.placed(src)
    text = re.search(r"<text[^>]*>well</text>", out)
    assert text is not None and 'data-kind="well"' in text.group(0)
    x = float(re.search(r' x="([^"]*)"', text.group(0)).group(1))  # type: ignore[union-attr]
    assert 90 <= x <= 140, "in the group's frame, not the sheet's (the rect stands at 150-170 on the sheet)"


def test_render_writes_the_picture(tmp_path, capsys) -> None:
    f = tmp_path / "s.svg"
    f.write_text(_sheet(BOARD), encoding="utf-8")
    out = tmp_path / "s.png"
    assert sl.main([str(f), str(out)]) == 0 and out.stat().st_size > 0
    assert "sheet-render" in capsys.readouterr().out
    assert sorted(p.name for p in tmp_path.iterdir()) == ["s.png", "s.svg"], "the temporary sheet is removed"


def test_the_seats_agree_with_the_placer() -> None:
    """The sheet asks the same placer the engines do: a level board's name, too long to stand inside it, takes the
    placer's own seat beside it."""
    from l7r.diagram.labels import ObstacleIndex, place

    p = place("notice board", 9.0, Subject("point", ((190.0, 140.0), (210.0, 140.0), (210.0, 148.0), (190.0, 148.0))), ObstacleIndex())
    placed = sl.seat(_sheet(BOARD))
    assert math.dist((placed[0][1].x, placed[0][1].y), (p.x, p.y)) < 1e-6


def test_an_empty_sheet_has_no_captions_and_a_bad_number_reads_as_its_default() -> None:
    assert sl.seat("<svg xmlns='http://www.w3.org/2000/svg'/>") == []
    import xml.etree.ElementTree as ET

    assert sl._f(ET.fromstring('<rect width="9px"/>'), "width", 3.0) == 3.0
