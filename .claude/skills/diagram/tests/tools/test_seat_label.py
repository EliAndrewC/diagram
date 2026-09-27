"""`make seat-label`: the one placer on a hand-drawn sheet (feature 266, FR-013, SC-006) - read, check, write, judge."""

from __future__ import annotations

import math

from l7r.diagram.labels import Subject
from l7r.diagram.tools import seat_label as sl

HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">\n'
BACK = '  <rect x="0" y="0" width="400" height="300" fill="#EFE3C2" data-kind="-"/>\n'


def _sheet(*body: str) -> str:
    return HEAD + BACK + "".join(body) + "</svg>\n"


BOARD = '  <g data-kind="notice board">\n    <rect x="190" y="140" width="20" height="8"/>\n    <text x="200" y="200" text-anchor="middle" font-size="9" font-style="italic" fill="#5C4830">notice board</text>\n  </g>\n'


def test_transforms_compose() -> None:
    assert sl.parse_transform(None) == sl.IDENTITY
    m = sl.parse_transform("translate(10,20) scale(2) rotate(90 5 5) matrix(1 0 0 1 3 4)")
    x, y = sl._apply(m, (0.0, 0.0))
    assert (round(x, 6), round(y, 6)) == (10.0 + 2 * (10 - 4), 20.0 + 2 * 3)
    assert sl.parse_transform("translate(7)")[4] == 7.0 and sl.parse_transform("scale(2 3)")[3] == 3.0
    assert round(sl._angle(sl.parse_transform("rotate(30)")), 6) == 30.0


def test_a_path_is_read_as_its_vertices() -> None:
    assert sl._path_points("M 10 10 L 20 10 H 30 V 40 l 5 5 h 1 v 1 C 1 1 2 2 50 50 Z") == [(10.0, 10.0), (20.0, 10.0), (30.0, 10.0), (30.0, 40.0), (35.0, 45.0), (36.0, 45.0), (36.0, 46.0), (50.0, 50.0)]


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
    assert weights == [500.0, 1000.0, 1000.0, 1000.0], "the river fill, the scale-bar-like `-` rect, the divider band, the text"
    assert len(idx.ways) == 1 and idx.ways[0].half_width == 5.0


def test_a_captions_subject_is_its_own_group() -> None:
    src = _sheet(BOARD, '  <g data-kind="notice board"><rect x="300" y="40" width="20" height="8"/><text x="310" y="70" font-size="9">bounty board</text><text x="310" y="80" font-size="8">a bill</text></g>\n')
    shapes, _view = sl.read_sheet(src)
    caps = sl.captions_of(shapes, None)
    assert len(caps) == 2 and len(caps[1]) == 2, "two boards, the second a caption of two texts"
    sub = sl.subject_of(shapes[caps[0][0]], shapes)
    assert sub is not None and sub.kind == "point" and sl.bbox(sub.poly) == (190.0, 140.0, 210.0, 148.0)


def test_a_caption_tagged_on_its_own_names_the_nearest_shape_of_its_kind() -> None:
    src = _sheet('  <rect x="50" y="50" width="100" height="60" data-kind="kitchen"/>\n', '  <text x="100" y="85" font-size="10" data-kind="kitchen">kitchen</text>\n', '  <text x="5" y="5" font-size="10" data-kind="nothing">x</text>\n')
    shapes, _view = sl.read_sheet(src)
    kitchen = next(s for s in shapes if s.tag == "text" and s.text == "kitchen")
    sub = sl.subject_of(kitchen, shapes)
    assert sub is not None and sub.kind == "area", "a name already inside its building is an area caption"
    stray = next(s for s in shapes if s.tag == "text" and s.text == "x")
    assert sl.subject_of(stray, shapes) is None, "a kind with nothing drawn has nothing to name"
    title = next(s for s in shapes if s.kind == "-" and s.tag == "rect")
    assert sl.subject_of(sl.Shape("text", "-", title.poly, text="t", center=(1.0, 1.0)), shapes) is None


def test_a_many_shape_subject_is_their_box() -> None:
    src = _sheet('  <g data-kind="well"><circle cx="100" cy="100" r="4"/><circle cx="120" cy="100" r="4"/><text x="110" y="130" font-size="8">well</text></g>\n')
    shapes, _view = sl.read_sheet(src)
    sub = sl.subject_of(next(s for s in shapes if s.tag == "text"), shapes)
    assert sub is not None and sl.bbox(sub.poly) == (96.0, 96.0, 124.0, 104.0)


def test_check_then_write_then_check_again() -> None:
    src = _sheet(BOARD)
    findings, placed = sl.seat(src)
    assert [f.what for f in findings] == ["off its standard seat"] and len(placed) == 1
    fixed = sl.rewrite(src)
    assert sl.seat(fixed)[0] == [], "written to its standard seat, the caption checks clean"
    assert sl.seat(fixed, {"well"}) == ([], []), "a kind filter that matches nothing checks nothing"


def test_leaders_are_written_moved_and_removed() -> None:
    walls = "".join(f'  <rect x="{x}" y="{y}" width="30" height="30" data-kind="house"/>\n' for x in range(100, 300, 30) for y in range(80, 220, 30) if not (180 <= x <= 210 and 130 <= y <= 150))
    src = _sheet(walls, BOARD)
    fixed = sl.rewrite(src)
    assert 'data-leader="1"' in fixed, "hemmed in, the caption stands out further and a leader ties it back"
    assert sl.seat(fixed)[0] == []
    moved = fixed.replace('data-leader="1"', 'data-leader="1" transform="translate(9,9)"')
    assert [f.what for f in sl.seat(moved)[0]] == ["a missing or misplaced leader"]
    seated = sl.rewrite(_sheet(BOARD))
    stray = seated.replace("</g>", '<line x1="1" y1="1" x2="5" y2="5" stroke="#000" data-leader="1"/></g>')
    assert [f.what for f in sl.seat(stray)[0]] == ["a stray leader"], "a caption at its adjacent seat carries no leader"
    assert 'data-leader="1"' not in sl.rewrite(stray), "and writing takes it off"
    lone = _sheet('  <rect x="190" y="140" width="20" height="8" data-kind="notice board"/>\n', walls, '  <text x="200" y="200" font-size="9" data-kind="notice board">notice board</text>\n')
    assert 'data-leader="1"' in sl.rewrite(lone)


def test_element_source_finds_the_text_or_nothing() -> None:
    import xml.etree.ElementTree as ET

    el = ET.fromstring('<text x="1" y="2">a</text>')
    assert sl._element_source('<svg><text x="1" y="2">a</text></svg>', el) == '<text x="1" y="2">a</text>'
    assert sl._element_source("<svg></svg>", el) == ""


def test_the_ledger_rule() -> None:
    """Shown red three ways: a changed sheet loses its exemptions, a new off-seat caption is caught, an untagged caption
    in a changed sheet is refused. An unchanged sheet keeps them."""
    src = _sheet(BOARD)
    entry = sl.ledger_entry(src)
    assert entry["exempt"] == [["notice board", "notice board", "off its standard seat"]]
    assert sl.judge(src, entry) == [], "unchanged and recorded: excused"
    changed = src.replace("</svg>", '<rect x="1" y="1" width="2" height="2" data-kind="x"/></svg>')
    assert sl.judge(changed, entry), "changed: every caption held to the standard"
    assert sl.judge(src, None), "new: every caption held to the standard"
    untagged = sl.rewrite(src).replace("</svg>", '<text x="300" y="20" font-size="9">loose words</text></svg>')
    assert any("untagged" in w for w in sl.judge(untagged, None))
    assert sl.judge(sl.rewrite(src), None) == [], "a new sheet at its standard seats passes"


def test_main_checks_and_writes(tmp_path, capsys) -> None:
    f = tmp_path / "s.svg"
    f.write_text(_sheet(BOARD), encoding="utf-8")
    assert sl.main([str(f)]) == 1 and "not at the standard seat" in capsys.readouterr().out
    assert sl.main([str(f), "--kind", "notice board", "--write"]) == 0
    assert sl.main([str(f)]) == 0


def test_the_seats_agree_with_the_placer() -> None:
    """The tool asks the same placer the engines do: its standard seat for a level board is the placer's own."""
    from l7r.diagram.labels import ObstacleIndex, place

    p = place("notice board", 9.0, Subject("point", ((190.0, 140.0), (210.0, 140.0), (210.0, 148.0), (190.0, 148.0))), ObstacleIndex())
    _f, placed = sl.seat(_sheet(BOARD))
    assert math.dist((placed[0][1].x, placed[0][1].y), (p.x, p.y)) < 1e-6


def test_an_empty_sheet_has_no_captions_and_a_bad_number_reads_as_its_default() -> None:
    assert sl.seat("<svg xmlns='http://www.w3.org/2000/svg'/>") == ([], [])
    import xml.etree.ElementTree as ET

    assert sl._f(ET.fromstring('<rect width="9px"/>'), "width", 3.0) == 3.0
    assert sl._drop_group_leader("<svg/>", []) == "<svg/>", "no caption was rewritten, so no leader to drop"
