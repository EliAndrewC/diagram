"""Feature 286's one-time migration: a hand sheet's captions from hand-SEATED to DECLARED, naming what the old reading
of where each caption stood took it to name."""

from __future__ import annotations

import re

from l7r.diagram.labels import hand_sheet as sl
from l7r.diagram.tools import caption_decl as cd

HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">\n'
BACK = '  <rect x="0" y="0" width="400" height="300" fill="#EFE3C2" data-kind="-"/>\n'


def _sheet(*body: str) -> str:
    return HEAD + BACK + "".join(body) + "</svg>\n"


PRIVIES = (
    '  <g data-kind="latrine">\n'
    '    <rect x="300" y="100" width="18" height="14"/>\n    <text x="330" y="112" font-size="7.5">latrine</text>\n'
    '    <rect x="40" y="100" width="18" height="14"/>\n    <text x="30" y="125" font-size="7.5">latrine</text>\n'
    "  </g>\n"
)


def _text(shapes: list[sl.Shape], text: str, n: int = 0) -> sl.Shape:
    return [s for s in shapes if s.tag == "text" and s.text == text][n]


def test_the_old_reading_gave_each_privy_its_own() -> None:
    """Ubame's residence privies: one group, a rect at each end, a name by each - each named the privy it stood by."""
    shapes, _view = sl.read_sheet(_sheet(PRIVIES))
    east = cd.read_parts(_text(shapes, "latrine", 0), shapes)
    west = cd.read_parts(_text(shapes, "latrine", 1), shapes)
    assert [sl.bbox(s.poly) for s in east] == [(300.0, 100.0, 318.0, 114.0)]
    assert [sl.bbox(s.poly) for s in west] == [(40.0, 100.0, 58.0, 114.0)]


def test_the_old_reading_of_a_caption_tagged_on_its_own() -> None:
    src = _sheet(
        '  <rect x="50" y="50" width="100" height="60" data-kind="kitchen"/>\n',
        '  <text x="100" y="85" font-size="10" data-kind="kitchen">kitchen</text>\n',
        '  <g data-kind="pines"><circle cx="300" cy="100" r="4"/><circle cx="310" cy="100" r="4"/><circle cx="380" cy="250" r="4"/></g>\n',
        '  <text x="305" y="120" font-size="8" data-kind="pines">pines</text>\n',
        '  <text x="5" y="5" font-size="10" data-kind="nothing">x</text>\n',
        '  <g data-kind="room"><rect x="200" y="200" width="40" height="30"/><rect x="250" y="200" width="40" height="30"/>'
        '<text x="220" y="215" font-size="8">a</text><text x="270" y="215" font-size="8">b</text></g>\n',
    )
    shapes, _view = sl.read_sheet(src)
    assert [sl.bbox(s.poly) for s in cd.read_parts(_text(shapes, "kitchen"), shapes)] == [(50.0, 50.0, 150.0, 110.0)], "the rect it lies in"
    assert len(cd.read_parts(_text(shapes, "pines"), shapes)) == 2, "the nearest cluster, the far pine left out"
    assert cd.read_parts(_text(shapes, "x"), shapes) == [], "nothing drawn of its kind"
    assert [sl.bbox(s.poly) for s in cd.read_parts(_text(shapes, "b"), shapes)] == [(250.0, 200.0, 290.0, 230.0)], "the room it lies in"


def test_texts_that_stood_one_under_another_were_one_caption() -> None:
    src = _sheet(
        '  <g data-kind="board"><rect x="10" y="10" width="20" height="8"/><text x="20" y="40" font-size="9">bounty board</text><text x="20" y="50" font-size="8">a bill</text><text x="200" y="40" font-size="8">apart</text></g>\n'
    )
    shapes, _view = sl.read_sheet(src)
    caps = cd.stacked_captions(shapes)
    assert [[shapes[i].text for i in c] for c in caps] == [["bounty board", "a bill"], ["apart"]]


def test_declare_writes_what_the_old_reading_found_and_strips_every_seat() -> None:
    src = _sheet(
        PRIVIES,
        '  <g data-kind="granary"><rect x="100" y="200" width="130" height="78"/><text x="165" y="230" text-anchor="middle" font-size="13">granary</text>'
        '<text x="165" y="243" text-anchor="middle" font-size="9">staging store</text>\n    <line x1="1" y1="1" x2="5" y2="5" data-leader="1"/></g>\n',
        '  <rect x="250" y="20" width="40" height="30" data-kind="shed" data-id="shed-1"/>\n',
        '  <text x="270" y="40" font-size="8" data-kind="shed" transform="rotate(30)"><tspan x="270" dy="0">shed</tspan><tspan x="270" dy="9">of tools</tspan></text>\n',
        '  <text x="5" y="290" font-size="8" data-kind="ghost">ghost</text>\n',
    )
    out, left = cd.declare(src)
    assert left == ["ghost"], "nothing drawn for it: left for its author"
    texts = re.findall(r"<text[^>]*>.*?</text>", out)
    assert texts[0] == '<text font-size="7.5" data-names="latrine-1">latrine</text>' and texts[1] == '<text font-size="7.5" data-names="latrine-2">latrine</text>'
    assert texts[2] == '<text font-size="13">granary</text>' and texts[3] == '<text font-size="9" data-cont="1">staging store</text>', "alone in its group, a caption needs no names"
    assert texts[4] == '<text font-size="8" data-kind="shed" data-names="shed-1"><tspan>shed</tspan><tspan>of tools</tspan></text>', "an existing data-id is reused"
    assert 'data-leader="1"' not in out and '<rect data-id="latrine-1" x="300"' in out
    placed = sl.placed(out.replace(texts[5], ""))
    assert placed.count("<text") == 5, "the declared sheet places"
