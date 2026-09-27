"""`seat_label` on the hand sheets it had to seat for real (feature 267): a group naming several things, the ground
drawn after a caption, a face's width, and the hand's own seat where the standard finds none free.

Kept apart from `test_seat_label.py`, which tests the tool's surface; these are the cases the three magistracy sheets
found."""

from __future__ import annotations

from dataclasses import replace

import pytest

from l7r.diagram.labels import Subject
from l7r.diagram.tools import seat_label as sl

HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">\n'
BACK = '  <rect x="0" y="0" width="400" height="300" fill="#EFE3C2" data-kind="-"/>\n'


def _sheet(*body: str) -> str:
    return HEAD + BACK + "".join(body) + "</svg>\n"


def _text(shapes: list[sl.Shape], text: str, n: int = 0) -> tuple[int, sl.Shape]:
    return [(i, s) for i, s in enumerate(shapes) if s.tag == "text" and s.text == text][n]


PRIVIES = (
    '  <g data-kind="latrine">\n'
    '    <rect x="300" y="100" width="18" height="14"/>\n    <text x="330" y="112" font-size="7.5">latrine</text>\n'
    '    <rect x="40" y="100" width="18" height="14"/>\n    <text x="30" y="125" font-size="7.5">latrine</text>\n'
    "  </g>\n"
)


def test_a_group_of_two_privies_gives_each_name_its_own() -> None:
    """Ubame's residence privies: one group, a rect at each end of the house, a name by each. Each name's subject is the
    privy it stands by, not the span between them - both names were seated beside that span's middle."""
    shapes, _view = sl.read_sheet(_sheet(PRIVIES))
    east = sl.subject_of(_text(shapes, "latrine", 0)[1], shapes)
    west = sl.subject_of(_text(shapes, "latrine", 1)[1], shapes)
    assert east is not None and west is not None
    assert sl.bbox(list(east.poly)) == (300.0, 100.0, 318.0, 114.0)
    assert sl.bbox(list(west.poly)) == (40.0, 100.0, 58.0, 114.0)


def test_a_cluster_is_everything_joined_within_reach() -> None:
    shapes, _view = sl.read_sheet(
        _sheet(
            '  <g data-kind="genkan"><rect x="10" y="10" width="10" height="10"/><rect x="22" y="10" width="10" height="10"/><rect x="34" y="10" width="10" height="10"/><rect x="200" y="10" width="10" height="10"/></g>\n'
        )
    )
    rects = [s for s in shapes if s.kind == "genkan"]
    assert len(sl.cluster_of(rects[0], rects, 3.0)) == 3, "joined link by link, the far one left out"
    assert sl._box_within(rects[0].poly, [(0.0, 0.0), (50.0, 0.0), (50.0, 50.0), (0.0, 50.0)])
    assert not sl._box_within(rects[3].poly, [(0.0, 0.0), (50.0, 0.0), (50.0, 50.0), (0.0, 50.0)])


def test_a_faces_width_follows_its_caps_weight_and_spacing() -> None:
    plain = sl.ET.fromstring('<text font-size="10">x</text>')
    bold = sl.ET.fromstring('<text font-size="10" font-weight="bold" letter-spacing="2">X</text>')
    assert sl.char_w_of(None, "shrine", 10) == sl.CHAR_W_EM
    assert sl.char_w_of(plain, "INARI SHRINE", 10) == sl.CAPS_W_EM
    assert sl.char_w_of(bold, "INARI SHRINE", 10) == sl.CAPS_W_EM + sl.BOLD_W_EM + 0.2


def test_ground_drawn_after_a_caption_covers_it() -> None:
    """A hand sheet keeps each caption where it stands in the document, so ground painted LATER covers it: the Inari
    shrine's name seated on the vegetable garden showed only its last letter. Ground drawn before it is free space."""
    src = _sheet('  <text x="100" y="100" font-size="9" data-kind="well">well</text>\n', '  <rect x="150" y="150" width="60" height="40" fill="#BFD0A0" data-kind="garden"/>\n')
    shapes, view = sl.read_sheet(src)
    i, cap = _text(shapes, "well")
    assert len(sl.classify(shapes, view, {i}).obstacles) == 0, "without an order, ground is free"
    assert len(sl.classify(shapes, view, {i}, after=i, group=cap.group).obstacles) == 1, "painted after it, it covers it"


def test_the_hands_seat_stands_where_the_standard_finds_nothing_free() -> None:
    """Where every candidate costs something, the caption's own seat is a candidate too, and it is kept when it costs
    no more (HAND) - but a free standard seat always wins, and a hand seat costing more loses."""
    src = _sheet('  <g data-kind="well"><rect x="100" y="100" width="10" height="10"/><text x="130" y="108" font-size="9">well</text></g>\n')
    shapes, view = sl.read_sheet(src)
    i, cap = _text(shapes, "well")
    sub = sl.subject_of(cap, shapes)
    assert sub is not None
    index = sl.classify(shapes, view, {i})
    _findings, placed = sl.seat(src)
    (_caps, p) = placed[0]
    assert sl.hand_seat_if_no_better(p, [cap], sub, index) == p if p.cost == 0 else True, "a free seat is taken as it is"
    crowded = replace(p, cost=5000.0)
    kept = sl.hand_seat_if_no_better(crowded, [cap], sub, index)
    assert kept.position == sl.HAND and kept.x == cap.center[0] and kept.leader is None
    cheap = replace(p, cost=0.5)
    blocked = sl.classify(shapes, view, {i})
    blocked.add(sl.Obstacle(tuple(cap.poly), sl.WEIGHT_TEXT))
    assert sl.hand_seat_if_no_better(cheap, [cap], sub, blocked) == cheap, "a hand seat on other ink costs more"


def test_an_area_hand_seat_spilling_out_of_its_area_pays_for_it() -> None:
    src = _sheet('  <g data-kind="cell"><rect x="100" y="100" width="20" height="12"/><text x="110" y="109" font-size="9">a cell far too long</text></g>\n')
    shapes, view = sl.read_sheet(src)
    i, cap = _text(shapes, "a cell far too long")
    area = Subject("area", ((100.0, 100.0), (120.0, 100.0), (120.0, 112.0), (100.0, 112.0)))
    _findings, placed = sl.seat(src)
    p = replace(placed[0][1], cost=sl.WEIGHT_OBSTACLE / 2)
    assert sl.hand_seat_if_no_better(p, [cap], area, sl.classify(shapes, view, {i})) == p


def test_a_least_cost_seat_is_written_once_and_then_stands() -> None:
    """A name wider than its room, in a room walled on every side: nothing is free, so the standard's least-cost seat
    is written once - and from then on it is the standard's choice again (a tie goes to the standard, 266 FR-007), is
    reported nowhere, and the sheet is left as it is. Without the fixed point the fallback's seat moved on every pass."""
    src = _sheet(
        '  <g data-kind="store"><rect x="100" y="100" width="30" height="14" fill="#C8A878"/><text x="115" y="110" text-anchor="middle" font-size="9">store of the long name</text></g>\n',
        '  <g stroke="#000" stroke-width="30" fill="none" data-kind="compound wall"><line x1="60" y1="80" x2="170" y2="80"/>'
        '<line x1="60" y1="134" x2="170" y2="134"/><line x1="60" y1="80" x2="60" y2="134"/><line x1="170" y1="80" x2="170" y2="134"/></g>\n',
    )
    _findings, placed = sl.seat(src)
    assert placed[0][1].cost > 0, "nothing free"
    once = sl._rewrite_once(src)
    findings, placed = sl.seat(once)
    assert [p.position for _c, p in placed] != [sl.HAND] and findings == []
    assert sl.rewrite(once) == once


def test_a_hand_seat_strictly_cheaper_is_kept_and_left_alone() -> None:
    """A well walled in on every side has no free seat beside it; its name, set by hand on open ground a little way off,
    covers nothing - strictly less than the standard's least-cost seat - so it stands, reported nowhere and unwritten."""
    src = _sheet(
        '  <g data-kind="well"><rect x="100" y="100" width="10" height="10"/><text x="300" y="250" font-size="9">well</text></g>\n',
        '  <g stroke="#000" stroke-width="60" fill="none" data-kind="compound wall"><line x1="40" y1="60" x2="170" y2="60"/>'
        '<line x1="40" y1="150" x2="170" y2="150"/><line x1="60" y1="40" x2="60" y2="170"/><line x1="150" y1="40" x2="150" y2="170"/></g>\n',
    )
    findings, placed = sl.seat(src)
    assert [p.position for _c, p in placed] == [sl.HAND] and findings == []
    assert sl.rewrite(src) == src


def test_each_caption_avoids_the_ones_seated_before_it() -> None:
    """The two privy names, seated in turn: the second is placed against the first's block too."""
    _findings, placed = sl.seat(_sheet(PRIVIES))
    (_a, first), (_b, second) = placed
    fx0, fy0, fx1, fy1 = sl.bbox(list(first.block))
    sx0, sy0, sx1, sy1 = sl.bbox(list(second.block))
    assert fx1 <= sx0 or sx1 <= fx0 or fy1 <= sy0 or sy1 <= fy0


def _weights(src: str, text: str, area: bool = False) -> dict[tuple[int, int, int, int], tuple[float, bool]]:
    shapes, view = sl.read_sheet(src)
    i, cap = _text(shapes, text)
    sub = sl.subject_of(cap, shapes)
    assert sub is not None
    index = sl.classify(shapes, view, {i}, after=i, group=cap.group, kind=cap.kind, subject=list(sub.poly), area=area)
    return {tuple(round(v) for v in sl.bbox(list(o.poly))): (o.weight, o.inner) for o in index.obstacles}


def test_ink_inside_what_a_caption_names_is_ink_it_avoids() -> None:
    """The placer's standard waives a subject's own parts; on a hand sheet those are partitions, posts, mats and the
    gardens in a court, and a name set on them could not be read. A garden nested in the court it names weighs light; a
    partition or a dark post in full; a mat painted after it as much as a name (it hides it)."""
    src = _sheet(
        '  <g data-kind="store"><rect x="100" y="100" width="120" height="60" fill="#C8A878"/>'
        '<line x1="160" y1="100" x2="160" y2="160" stroke="#8C6F3E" stroke-width="1"/>'
        '<circle cx="110" cy="110" r="3" fill="#2D2A24"/>'
        '<text x="130" y="135" font-size="9">store</text>'
        '<rect x="190" y="140" width="20" height="10" fill="#E8D2A8" data-kind="straw mats"/></g>\n',
        '  <rect x="200" y="200" width="150" height="80" data-kind="inner court" fill="#D9C28E"/>\n'
        '  <rect x="210" y="210" width="40" height="30" data-kind="garden" fill="#BFD0A0" stroke="#7A8C5C" stroke-width="1"/>\n'
        '  <text x="300" y="260" font-size="9" data-kind="inner court">court</text>\n',
    )
    w = _weights(src, "store")
    assert w[(160, 100, 160, 160)] == (sl.WEIGHT_OBSTACLE, True), "the store's own partition weighs in full (round 4)"
    assert w[(107, 107, 113, 113)] == (sl.WEIGHT_OBSTACLE, True), "a dark post weighs in full"
    assert w[(190, 140, 210, 150)] == (sl.WEIGHT_TEXT, True), "a mat painted after the name hides it"
    court = _weights(src, "court")
    assert court[(210, 210, 250, 240)] == (sl.WEIGHT_INNER, True), "a garden in the court is ground, but not the court's"


def test_a_room_names_itself_inside_the_building_that_holds_it() -> None:
    """An area caption's room lies inside its building's rect, which it cannot help covering: waived for an area caption
    (Hayakawa's guardroom was pushed onto its range's roof edge), kept for a point caption beside a thing."""
    src = _sheet(
        '  <rect x="100" y="100" width="200" height="50" fill="#8C6F3E"/>\n',
        '  <g data-kind="guardroom"><rect x="150" y="100" width="60" height="50" fill="#8C6F3E"/><text x="180" y="128" font-size="8">guardroom</text></g>\n',
    )
    assert (100, 100, 300, 150) not in _weights(src, "guardroom", area=True)
    assert (100, 100, 300, 150) in _weights(src, "guardroom", area=False)


def test_a_grounds_drawn_border_is_ink_but_not_the_one_it_names() -> None:
    src = _sheet(
        '  <rect x="50" y="50" width="100" height="60" fill="#BFD0A0" stroke="#7A8C5C" stroke-width="2" data-kind="vegetable garden"/>\n',
        '  <g data-kind="garden"><rect x="200" y="50" width="100" height="60" fill="#BFD0A0" stroke="#7A8C5C" stroke-width="2"/><text x="250" y="80" font-size="9">garden</text></g>\n',
    )
    w = _weights(src, "garden")
    assert sum(1 for k, (wt, _i) in w.items() if k[0] >= 49 and k[2] <= 151) == 4, "the vegetable garden's four edges"
    assert not any(k[0] >= 199 for k in w), "the garden's own border is its own"


def test_a_light_name_set_down_off_its_dark_roof_takes_the_dark_ink() -> None:
    """Ochiba's shrine names were cream for the dark hall; seated beside it, on court earth, they barely showed."""
    off = _sheet('  <g data-kind="shrine altar"><rect x="100" y="100" width="20" height="12" fill="#5C1A0A"/><text x="300" y="250" font-size="8" fill="#FFFAE6">altar</text></g>\n')
    assert 'fill="#3A2E1C"' in sl.rewrite(off) and "#FFFAE6" not in sl.rewrite(off)
    on = _sheet('  <g data-kind="hall"><rect x="100" y="100" width="200" height="80" fill="#5C1A0A"/><text x="150" y="130" font-size="8" fill="#FFFAE6">hall</text></g>\n')
    assert "#FFFAE6" in sl.rewrite(on), "still on its dark roof, it keeps its light ink"
    assert sl._luma("#fff") == pytest.approx(1.0) and sl._luma("url(#p)") == 0.5


def test_an_area_name_keeps_off_its_own_outline_and_its_buildings() -> None:
    """Inside its area by necessity, an area caption still keeps off the drawn outline of the area and of the building
    holding it: Hayakawa's HEARING COURT and Hajime's quarters were seated against their walls (round 4)."""
    src = _sheet(
        '  <rect x="100" y="100" width="200" height="50" fill="#8C6F3E" stroke="#4A3318" stroke-width="2"/>\n',
        '  <g data-kind="guardroom"><rect x="150" y="100" width="60" height="50" fill="#8C6F3E" stroke="#4A3318" stroke-width="1"/><text x="180" y="128" font-size="8">guardroom</text></g>\n',
    )
    w = _weights(src, "guardroom", area=True)
    assert (100, 100, 300, 150) not in w and sum(1 for k, (wt, inner) in w.items() if inner and wt == sl.WEIGHT_OBSTACLE) == 8, "four edges each"


def test_a_sub_line_is_measured_at_its_own_size() -> None:
    """A guest house's 8 px italic note under its 12 px bold name ran 156 px wide measured at the name's face, and the
    name was seated across the house's wall; each line stands in for its own width."""
    src = _sheet(
        '  <g data-kind="guest house"><rect x="100" y="100" width="90" height="100" fill="#E0B878"/><text x="145" y="140" font-size="12" font-weight="bold">guest house</text><text x="145" y="152" font-size="8" font-style="italic">(in the annex added by)</text></g>\n'
    )
    shapes, _view = sl.read_sheet(src)
    caps = [s for s in shapes if s.tag == "text"]
    head_w = sl.char_w_of(caps[0].element, caps[0].text, caps[0].size)
    lines = sl._as_head(caps, head_w)
    assert lines[0] == "guest house" and len(lines[1]) < len("(in the annex added by)") * 8 / 12 + 1
    (_caps, p) = sl.seat(src)[1][0]
    x0, _y0, x1, _y1 = sl.bbox(list(p.block))
    name, _h = sl.block_half(["guest house"], 12, head_w)
    note, _h = sl.block_half([caps[1].text], 8, sl.char_w_of(caps[1].element, caps[1].text, 8))
    assert x1 - x0 == pytest.approx(2 * max(name, note), rel=0.1), "as wide as its widest line at that line's own size"
    assert x1 - x0 < 2 * sl.block_half([caps[1].text], 12, head_w)[0], "not the note measured at the name's face"
