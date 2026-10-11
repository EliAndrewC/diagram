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
