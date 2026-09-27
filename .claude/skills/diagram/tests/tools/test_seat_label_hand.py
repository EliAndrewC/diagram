"""`seat_label` on the hand sheets it had to seat for real (feature 267): a group naming several things, the ground
drawn after a caption, a face's width, and the hand's own seat where the standard finds none free.

Kept apart from `test_seat_label.py`, which tests the tool's surface; these are the cases the three magistracy sheets
found."""

from __future__ import annotations

from dataclasses import replace

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


def test_a_kept_caption_is_neither_reported_nor_rewritten() -> None:
    """A name wider than its room, in a room walled on every side: nothing is free, so the standard's least-cost seat
    is written once - and from then on the caption's own seat costs no more, is kept, and the sheet is left as it is.
    Without this the fallback's seat moved on every pass (feature 267)."""
    src = _sheet(
        '  <g data-kind="store"><rect x="100" y="100" width="30" height="14" fill="#C8A878"/><text x="115" y="110" text-anchor="middle" font-size="9">store of the long name</text></g>\n',
        '  <g stroke="#000" stroke-width="30" fill="none" data-kind="compound wall"><line x1="60" y1="80" x2="170" y2="80"/>'
        '<line x1="60" y1="134" x2="170" y2="134"/><line x1="60" y1="80" x2="60" y2="134"/><line x1="170" y1="80" x2="170" y2="134"/></g>\n',
    )
    _findings, placed = sl.seat(src)
    assert placed[0][1].cost > 0, "nothing free"
    once = sl._rewrite_once(src)
    findings, placed = sl.seat(once)
    assert [p.position for _c, p in placed] == [sl.HAND] and findings == []
    assert sl.rewrite(once) == once


def test_each_caption_avoids_the_ones_seated_before_it() -> None:
    """The two privy names, seated in turn: the second is placed against the first's block too."""
    _findings, placed = sl.seat(_sheet(PRIVIES))
    (_a, first), (_b, second) = placed
    fx0, fy0, fx1, fy1 = sl.bbox(list(first.block))
    sx0, sy0, sx1, sy1 = sl.bbox(list(second.block))
    assert fx1 <= sx0 or sx1 <= fx0 or fy1 <= sy0 or sy1 <= fy0
