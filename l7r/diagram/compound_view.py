"""The one view of a composed draft's captions (feature 340): the draft read as the hand-sheet placer reads a hand sheet, so
`compound.py` seats each caption by the hand-sheet placer's classification of the drawn sheet, its reading of the declared
subject and its measure of the caption's width - one view for the draft and the hand sheets (plan D3, D4). Split out of
`compound.py`, which it serves, to keep that file at human scale."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass

from .labels import ObstacleIndex, Subject, hand_sheet

Request = tuple[str, Subject, float, bool, str, str]
"""A caption request: its text, the composer's subject, size, italic, fill and kind (the shape `compound.py` uses)."""


View = Callable[[int, Subject], ObstacleIndex]
"""Caption i's drawn sheet as the hand-sheet placer sees it (feature 340): the index `labels.hand_sheet.classify` gives for one
of its subjects, its kind and its face - the shapes it declares never an obstacle to it (plan D4)."""


@dataclass
class OneView:
    """How every caption of a draft is seated by the hand-sheet placer's one view (feature 340, plan D3): each caption's
    ordered subjects (`hand_sheet.subjects` over its declared parts), its width (`hand_sheet.char_w_of`) and the sheet's
    classification (`view`)."""

    view: View
    subjects: list[list[Subject]]
    widths: list[float]


def one_view(sheet: str, requests: list[Request], declared: list[str]) -> OneView:
    """The one view of a draft (feature 340, plan D3): the drawn sheet - every feature drawn, no caption yet written - read as
    the hand-sheet placer reads a hand sheet; each caption's subjects from the shapes its declaration names, in the
    hand-sheet placer's order; its width from its face; and the sheet's classification for each caption and subject,
    computed once (the repair and the foot's growth ask again). A shape the caption declares never makes its seat unfree
    (plan D4): `classify`'s obstacle for it is dropped, flagged inner or not (a caption tried beside one mat is not judged
    against the other mats it names) - its partitions, a court's buildings, any shape it does not name still block. The hand-sheet placer's own legibility rules for the subject stay: a name in dark ink takes no dark fill
    it names, and none lies across its own drawn outline."""
    shapes, view = hand_sheet.read_sheet(sheet)
    named = frozenset(r[5] for r in requests)
    cache: dict[tuple[int, str, tuple[tuple[float, float], ...]], ObstacleIndex] = {}
    owned: list[frozenset[int]] = []

    def classified(i: int, sub: Subject) -> ObstacleIndex:
        key = (i, sub.kind, tuple(sub.poly))
        if key not in cache:
            kind, dark = requests[i][5], hand_sheet._luma(requests[i][4]) <= hand_sheet.LIGHT  # a name in dark ink takes no dark fill
            base = hand_sheet.classify(shapes, view, subject=list(sub.poly), area=sub.kind == "area", kind=kind, dark_inside=dark, named=named)
            mine = {tuple(shapes[k].poly) for k in owned[i]}
            kept = [o for o in base.obstacles if not (o.weight != hand_sheet.WEIGHT_DARK and tuple(o.poly) in mine)]
            cache[key] = base if len(kept) == len(base.obstacles) else ObstacleIndex(kept, list(base.ways))
        return cache[key]

    subjects: list[list[Subject]] = []
    widths: list[float] = []
    for (text, subject, size, italic, _fill, _kind), names in zip(requests, declared, strict=True):
        want = set(names.split())
        own = [k for k, s in enumerate(shapes) if s.tag != "text" and not s.leader and s.ids & want]
        owned.append(frozenset(own))
        subjects.append(hand_sheet.subjects([shapes[k] for k in own], size) if own else [subject])
        widths.append(hand_sheet.char_w_of(ET.Element("text", {"font-style": "italic"} if italic else {"font-weight": "bold"}), text, size))
    return OneView(classified, subjects, widths)
