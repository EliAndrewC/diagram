"""Feature 340 (plan D1): the composed draft declares each caption the way a hand sheet does - every caption's `data-names`
lists the `data-id`s of drawn shapes - so `labels.hand_sheet` reads the draft as it reads a hand sheet."""

from __future__ import annotations

import re

from l7r.diagram import compound as c
from l7r.diagram.labels import hand_sheet as hs


def _draft() -> str:
    prog = c.county_magistracy_program()
    return c.emit_svg(prog, c.place(prog))


def test_every_caption_names_drawn_shapes_and_the_hand_sheet_reader_takes_the_draft() -> None:
    svg = _draft()
    ids = set(re.findall(r'data-id="([^"]+)"', svg))
    caps = re.findall(r'<text[^>]*data-kind="(?!-")[^"]+"[^>]*>', svg)
    assert caps, "the draft writes captions"
    for cap in caps:
        names = re.search(r'data-names="([^"]*)"', cap)
        assert names and names.group(1), f"an undeclared caption: {cap[:120]}"
        assert set(names.group(1).split()) <= ids, f"a caption names a shape the draft does not draw: {cap[:120]}"
    shapes, _view = hs.read_sheet(svg)
    assert hs.captions_of(shapes)  # the reader finds the captions and their declared parts without refusing


def test_the_straw_mats_caption_names_every_mat_and_the_tubs_caption_every_tub() -> None:
    svg = _draft()
    mats = re.search(r'<text[^>]*data-kind="kneeling positions"[^>]*data-names="([^"]*)"', svg)
    tubs = re.search(r'<text[^>]*data-kind="fire-water tubs"[^>]*data-names="([^"]*)"', svg)
    assert mats and len(mats.group(1).split()) > 1
    assert tubs and len(tubs.group(1).split()) == len(re.findall(r'data-id="tub-\d+"', svg))


# --- feature 340 plan D3/D4: the one view ---

from l7r.diagram.labels import Obstacle, ObstacleIndex, Subject  # noqa: E402

_SHEET = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400"><rect x="0" y="0" width="400" height="400" fill="#EFE3C2" data-kind="-"/><rect x="100" y="100" width="60" height="40" fill="#C9A57A" stroke="#6B4F2A" stroke-width="2" data-kind="kitchen" data-id="d0"/></svg>'


def _sq(x: float, y: float, w: float, h: float) -> tuple[tuple[float, float], ...]:
    return ((x, y), (x + w, y), (x + w, y + h), (x, y + h))


def test_one_view_reads_subjects_from_the_declaration_and_falls_back_to_the_composers_own() -> None:
    own_sub = Subject("point", _sq(300, 300, 4, 4))
    reqs = [("kitchen", Subject("area", _sq(100, 100, 60, 40)), 8.0, False, "#3A2E1C", "kitchen"), ("well", own_sub, 8.0, True, "#FFFAE6", "well")]
    one = c.one_view(_SHEET, reqs, ["d0", ""])
    assert one.subjects[0][0].kind == "area" and one.subjects[1] == [own_sub]  # a caption naming nothing keeps the composer's subject
    assert one.widths[0] > one.widths[1]  # the bold face measures wider than the italic
    index = one.view(0, one.subjects[0][0])
    assert one.view(0, one.subjects[0][0]) is index
    assert not any(o.poly == ((100.0, 100.0), (160.0, 100.0), (160.0, 140.0), (100.0, 140.0)) for o in index.obstacles)  # its own rect is never inner ink against it  # classified once per subject


def test_under_the_one_view_the_next_subject_is_tried_and_a_stranded_caption_is_reported() -> None:
    blocked = Subject("area", _sq(10, 10, 30, 20))
    free = Subject("area", _sq(200, 200, 120, 60))
    wall = ObstacleIndex([Obstacle(_sq(0, 0, 60, 50), 1000.0)])
    one = c.OneView(lambda i, sub: wall if sub is blocked else ObstacleIndex([]), [[blocked, free]], [0.6])
    seats, stuck = c._seat_all([("garden", blocked, 10.0, True, "#333", "garden")], [], (0.0, 0.0, 400.0, 400.0), one)
    assert stuck is None and 200 <= seats[0].x <= 320  # inside the second subject
    none = c.OneView(lambda i, sub: wall, [[blocked]], [0.6])
    seats, stuck = c._seat_all([("garden", blocked, 10.0, True, "#333", "garden")], [], (0.0, 0.0, 400.0, 400.0), none)
    assert stuck == 0 and seats == []


def test_under_the_one_view_a_stranded_caption_lifts_a_neighbor() -> None:
    from l7r.diagram.labels import Placement

    small = Subject("area", _sq(100, 100, 40, 20))  # the stranded caption's only ground
    big = Subject("area", _sq(200, 200, 150, 120))  # where the neighbor can go instead
    sitting = Placement(120.0, 113.0, 0.0, ("shed",), _sq(98, 98, 44, 24), 0, 0, "inside", 0.0, None)  # the neighbor, on it
    one = c.OneView(lambda i, sub: ObstacleIndex([]), [[big], [small]], [0.6, 0.6])
    reqs = [("shed", big, 10.0, False, "#333", "shed"), ("tub", small, 8.0, False, "#333", "tub")]
    got = c._repair(1, reqs, [], [sitting], (0.0, 0.0, 400.0, 400.0), one, small)
    assert got is not None and 100 <= got.x <= 140  # seated on its own ground, the neighbor moved
    assert c._width(None, 0) == c.CHAR_W_EM
