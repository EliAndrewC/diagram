"""The hand-sheet placer on the cases the magistracy sheets found (features 267, 283, 286): the ground drawn after a
caption, a face's width, ink inside what a caption names, a wall a leader may not cross, and the order captions are
placed in.

Kept apart from `test_hand_sheet.py`, which tests the module's surface."""

from __future__ import annotations

import pytest

from l7r.diagram.labels import Subject
from l7r.diagram.labels import hand_sheet as sl

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


def test_a_box_within_another() -> None:
    shapes, _view = sl.read_sheet(
        _sheet(
            '  <g data-kind="genkan"><rect x="10" y="10" width="10" height="10"/><rect x="22" y="10" width="10" height="10"/><rect x="34" y="10" width="10" height="10"/><rect x="200" y="10" width="10" height="10"/></g>\n'
        )
    )
    rects = [s for s in shapes if s.kind == "genkan"]
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


def _weights(src: str, text: str, area: bool = False) -> dict[tuple[int, int, int, int], tuple[float, bool]]:
    shapes, view = sl.read_sheet(src)
    i, cap = _text(shapes, text)
    sub = sl.subjects(sl.declared_parts(cap, shapes, alone=True))[-1]
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
        '  <rect x="200" y="200" width="150" height="80" data-kind="inner court" data-id="court" fill="#D9C28E"/>\n'
        '  <rect x="210" y="210" width="40" height="30" data-kind="garden" fill="#BFD0A0" stroke="#7A8C5C" stroke-width="1"/>\n'
        '  <text x="300" y="260" font-size="9" data-kind="inner court" data-names="court">court</text>\n',
    )
    w = _weights(src, "store")
    assert w[(160, 100, 160, 160)] == (sl.WEIGHT_OBSTACLE, True), "the store's own partition weighs in full (round 4)"
    assert w[(107, 107, 113, 113)] == (sl.WEIGHT_OBSTACLE, True), "a dark post weighs in full"
    assert w[(190, 140, 210, 150)] == (sl.WEIGHT_TEXT, True), "a mat painted after the name hides it"
    court = _weights(src, "court")
    assert court[(210, 210, 250, 240)] == (sl.WEIGHT_INNER, True), "a garden in the court is ground, but not the court's"
    later = src.replace('  <text x="300" y="260" font-size="9" data-kind="inner court" data-names="court">court</text>\n', "").replace(
        "</svg>", '  <rect x="320" y="250" width="20" height="20" data-kind="vegetable garden" fill="#BFD0A0"/>\n</svg>'
    )
    later = later.replace(
        'data-kind="inner court" data-id="court" fill="#D9C28E"/>\n',
        'data-kind="inner court" data-id="court" fill="#D9C28E"/>\n  <text x="300" y="260" font-size="9" data-kind="inner court" data-names="court">court</text>\n',
    )
    assert _weights(later, "court")[(320, 250, 340, 270)] == (sl.WEIGHT_TEXT, True), "a garden painted after the name hides it (feature 283)"


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
    assert 'fill="#3A2E1C"' in sl.placed(off) and "#FFFAE6" not in sl.placed(off)
    on = _sheet('  <g data-kind="hall"><rect x="100" y="100" width="200" height="80" fill="#5C1A0A"/><text x="150" y="130" font-size="8" fill="#FFFAE6">hall</text></g>\n')
    assert "#FFFAE6" in sl.placed(on), "still on its dark roof, it keeps its light ink"
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
        '  <g data-kind="guest house"><rect x="100" y="100" width="90" height="100" fill="#E0B878"/><text x="145" y="140" font-size="12" font-weight="bold">guest house</text><text x="145" y="152" font-size="8" font-style="italic" data-cont="1">(in the annex added by)</text></g>\n'
    )
    shapes, _view = sl.read_sheet(src)
    caps = [s for s in shapes if s.tag == "text"]
    head_w = sl.char_w_of(caps[0].element, caps[0].text, caps[0].size)
    lines = sl._as_head(caps, head_w, [c.lines for c in caps])
    assert lines[0] == "guest house" and len(lines[1]) < len("(in the annex added by)") * 8 / 12 + 1
    (_caps, p, per) = sl.seat(src)[0]
    x0, _y0, x1, _y1 = sl.bbox(list(p.block))
    name = max(sl.block_half([ln], 12, head_w)[0] for ln in per[0])
    note = max(sl.block_half([ln], 8, sl.char_w_of(caps[1].element, ln, 8))[0] for ln in per[1])
    assert x1 - x0 == pytest.approx(2 * max(name, note), rel=0.1), "as wide as its widest line, as placed, at that line's own size"
    assert x1 - x0 < 2 * max(sl.block_half([ln], 12, head_w)[0] for ln in per[1]), "not the note measured at the name's face"


def test_ink_marked_as_texture_weighs_light() -> None:
    """A wing's shutter marks are its surface, not its parts: marked `data-texture`, they weigh light and a name may lie
    on them, where unmarked they pushed Ubame's shuttered wing name across its wall (round 5)."""
    wing = (
        '  <g data-kind="wing"><rect x="100" y="100" width="90" height="70" fill="#C9B489"/>'
        '<g stroke="#8C7448" stroke-width="1.2"{mark}><line x1="120" y1="104" x2="120" y2="166"/></g>'
        '<text x="145" y="138" font-size="9">wing</text></g>\n'
    )
    marked = _weights(_sheet(wing.format(mark=' data-texture="1"')), "wing")
    plain = _weights(_sheet(wing.format(mark="")), "wing")
    assert marked[(119, 104, 121, 166)] == (sl.WEIGHT_INNER, True)
    assert plain[(119, 104, 121, 166)] == (sl.WEIGHT_OBSTACLE, True)


def test_a_caption_keeps_off_a_leader_placed_before_it() -> None:
    """A caption seated with a leader lends the next ones its leader as well as its block: Ubame's INNER COURT lay
    across the leader tying RESIDENCE to the house (round 6)."""
    walls = "".join(f'  <rect x="{x}" y="{y}" width="30" height="30" data-kind="house"/>\n' for x in range(100, 300, 30) for y in range(80, 220, 30) if not (180 <= x <= 210 and y <= 150))
    board = '  <g data-kind="notice board">\n    <rect x="190" y="140" width="20" height="8"/>\n    <text x="200" y="200" text-anchor="middle" font-size="9">notice board</text>\n  </g>\n'
    later = '  <g data-kind="well"><rect x="330" y="140" width="8" height="8"/><text x="334" y="160" font-size="9">well</text></g>\n'
    placed = sl.seat(_sheet(walls, board, later))
    (_b, first, _pb), (_w, second, _pw) = placed
    assert first.leader is not None, "hemmed in, the board's name stands out with a leader"
    band = sl._band(first.leader[0], first.leader[1], 1.0)
    bx0, by0, bx1, by1 = sl.bbox(band)
    sx0, sy0, sx1, sy1 = sl.bbox(list(second.block))
    assert sx1 <= bx0 or bx1 <= sx0 or sy1 <= by0 or by1 <= sy0


def test_a_bed_in_rows_is_no_seat_for_another_name() -> None:
    """Feature 283: a worked bed's furrows run through a name's letters, so neither a court nesting it nor a neighbor
    may set its name there; the bed's own name lies on it."""
    src = _sheet(
        '  <rect x="200" y="200" width="150" height="80" data-kind="inner court" data-id="court" fill="#D9C28E"/>\n'
        '  <rect x="210" y="210" width="40" height="30" data-kind="vegetable garden" fill="url(#vegetable-rows)"/>\n'
        '  <text x="300" y="260" font-size="9" data-kind="inner court" data-names="court">court</text>\n'
        '  <rect x="400" y="210" width="40" height="30" data-kind="vegetable garden" fill="url(#vegetable-rows)"/>\n'
        '  <rect x="450" y="210" width="20" height="20" data-kind="well" data-id="well" fill="#9C8C70"/>\n'
        '  <text x="480" y="225" font-size="9" data-kind="well" data-names="well">well</text>\n',
    )
    assert _weights(src, "court")[(210, 210, 250, 240)] == (sl.WEIGHT_OBSTACLE, True), "nested, but in rows"
    assert _weights(src, "well")[(400, 210, 440, 240)][0] == sl.WEIGHT_OBSTACLE, "a neighbor's bed is no free ground"


def test_a_leader_ends_on_the_ink_it_names() -> None:
    """Feature 283: a leader set against a group's box ended in the box's empty corner (a moored barge, three pines);
    it is carried on to the nearest drawn part. A leader already on the ink, or with nothing drawn, is left alone."""
    from dataclasses import replace as _replace

    pine = sl.Shape("circle", "garden pines", [(100, 100), (110, 100), (110, 110), (100, 110)])
    rope = sl.Shape("line", "garden pines", [(120, 90), (140, 90)], half=0.5, line=True)
    p = sl.place("x", 9.0, sl.Subject("point", ((100, 100), (110, 100), (110, 110), (100, 110))), sl.ObstacleIndex())
    p = _replace(p, leader=((60.0, 105.0), (95.0, 105.0)))
    moved = sl.leader_to_ink(p, [pine, rope])
    assert moved.leader is not None and 99.0 <= moved.leader[1][0] <= 100.0, "carried on to the pine's edge"
    on = _replace(p, leader=((60.0, 105.0), (100.5, 105.0)))
    assert sl.leader_to_ink(on, [pine]) == on, "already on the ink"
    assert sl.leader_to_ink(p, []) == p and sl.leader_to_ink(_replace(p, leader=None), [pine]).leader is None


def test_a_dark_ink_name_goes_beside_its_own_dark_fill() -> None:
    """Feature 286 (plan D2): a well's shaft, a tub, a dark roof takes no name in the sheet's dark ink - inside first
    would have set it there - while a name in light ink, chosen for the dark roof, may sit on it."""
    src = _sheet('  <g data-kind="shaft"><rect x="100" y="100" width="80" height="40" fill="#2D2A24"/><text font-size="8">shaft</text></g>\n')
    shapes, view = sl.read_sheet(src)
    i, cap = _text(shapes, "shaft")
    box = [(100.0, 100.0), (180.0, 100.0), (180.0, 140.0), (100.0, 140.0)]
    dark = sl.classify(shapes, view, {i}, subject=box, area=True, dark_inside=True)
    assert [(o.weight, o.inner) for o in dark.obstacles] == [(sl.WEIGHT_DARK, True)]
    assert sl.classify(shapes, view, {i}, subject=box, area=True).obstacles == [], "a light name may lie on it"
    (_c, p, _per) = sl.seat(src)[0]
    assert p.position != "inside", "the dark-ink name stands beside"


def test_a_leader_does_not_cross_a_wall_unless_it_names_the_wall() -> None:
    """Feature 286: with no hand seat to fall back on, the bath's name was led across the court divider from ground on
    the far side. A wall is a leader's obstacle - the Fox border's names excepted, which name the east wall itself."""
    wall = sl.Shape("line", "compound wall", [(0.0, 50.0), (200.0, 50.0)], half=4.5, line=True, dark=True)
    thin = sl.Shape("line", "partition", [(0.0, 80.0), (200.0, 80.0)], half=0.5, line=True, dark=True)
    sub = Subject("point", ((90.0, 90.0), (110.0, 90.0), (110.0, 100.0), (90.0, 100.0)))
    lead = sl.leader_blockers([wall, thin], set(), [], sub)
    assert [o.weight for o in lead.obstacles] == [sl.WEIGHT_DARK], "the wall, not the partition"
    assert sl.leader_blockers([wall, thin], set(), [], sub, [wall]).obstacles == [], "a wall the caption names"

    def building(x: float, y: float, kind: str) -> sl.Shape:
        return sl.Shape("rect", kind, [(x, y), (x + 60, y), (x + 60, y + 40), (x, y + 40)], filled=True)

    kitchen, court, room_range = building(200, 200, "kitchen"), building(300, 200, "outer court"), building(80, 80, "range")
    lead = sl.leader_blockers([kitchen, court, room_range], set(), [], sub)
    assert [sl.bbox(o.poly) for o in lead.obstacles] == [(200.0, 200.0, 260.0, 240.0)], "a building it would cross; not ground, not the range holding its room"


def test_a_glyph_in_a_named_ground_is_named_after_the_ground() -> None:
    """Feature 286: placed first, a practice ground's weapon rack took the ground's inside and the ground's name went
    into the empty building beside it. The ground is named first; the glyph finds its seat after."""
    src = _sheet(
        '  <g data-kind="practice ground"><rect x="100" y="100" width="90" height="40" fill="#D9C28E"/><text font-size="9">practice ground</text></g>\n',
        '  <g data-kind="weapon rack"><rect x="140" y="118" width="10" height="4" fill="#5C4830"/><text font-size="7">rack</text></g>\n',
    )
    placed = sl.seat(src)
    ground = next(p for c, p, _ in placed if c[0].text == "practice ground")
    assert ground.position == "inside" and ground.cost == 0.0
