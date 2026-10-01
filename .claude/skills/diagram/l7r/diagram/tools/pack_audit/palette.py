"""A kind is painted in its palette role (feature 294, plan B22): the building a sheet tags `stables` is filled with the
service buildings' color, a kura with the sealed storehouse's, and so on.

THE TABLE IS A MAP DRAWING CONVENTION (plan D11): `SKILL.md`'s Palette table names a role per element; its machine form
is `compound_model.KINDS` (role -> fill), and nothing mapped a KIND to its role until this table. A kind the palette
names is taken from it; a kind it does not name is assigned the role every sheet that draws it already paints it in,
and is labeled GUESS beside its row. A kind not in the table is not checked (a garden, a court, a pond - ground, not a
built role).

THE MAIN FILL. A kind's color is the fill of its largest rect that is NOT a room - a rect wholly inside a structure of
another kind (the clerks' room drawn inside the office hall in the hall's own fill, `parse.rooms_folded`'s reasoning) is
the building it stands in, and is not judged. A kind whose every rect is a room is skipped.
"""

from __future__ import annotations

from ...compound_model import KINDS
from .parse import STRUCTURE_FILLS
from .tagged import Mark, marks

LORD, SERVICE, PLAIN, KURA, SHRINE, CELL, DARK = (KINDS[k][0] for k in ("lord", "service", "plain", "kura", "shrine", "cell", "dark"))
GRANARY_SLATS = "url(#granary-slats)"
PRIVY = "#7E726A"  # SKILL.md: Latrines / utility
WELL = "#9C8C70"  # SKILL.md: Well stone curb

#: kind -> the fills it may be painted in. Rows with no comment are the SKILL.md palette's own words.
ROLES: dict[str, frozenset[str]] = {
    "residence": frozenset({LORD}),
    "lord's quarters": frozenset({LORD}),
    "family quarters": frozenset({LORD}),
    "office hall": frozenset({LORD}),  # GUESS: the palette names "residence, audience pavilion"; every sheet's office hall is the lord's
    "guest quarters": frozenset({LORD}),  # GUESS: the lord's own rooms (a room of the residence on the hand sheets)
    "karo's house": frozenset({LORD}),  # GUESS: the house elder's house, painted as the lord's on every sheet
    "hall and dwelling": frozenset({LORD}),  # GUESS: the shrine's hall-and-dwelling in the lord's-building color
    "kitchen": frozenset({SERVICE}),
    "stables": frozenset({SERVICE}),
    "barracks": frozenset({SERVICE}),
    "servants' quarters": frozenset({SERVICE}),  # GUESS: a service building (the servants' row)
    "retainers' quarters": frozenset({SERVICE}),  # GUESS: a service building (the retainers' row)
    "bath": frozenset({SERVICE}),  # GUESS: a service building (a small addition to the kitchen)
    "gatehouse": frozenset({DARK}),
    "magistrate's dais": frozenset({DARK}),
    "clerks' room": frozenset({PLAIN}),
    "tally office": frozenset({PLAIN}),
    "tax archive": frozenset({KURA}),
    "storehouse": frozenset({KURA}),  # GUESS: a sealed kura, as the tax archive
    # the granary has TWO attested forms (buildings/programs.md; Ochiba notes R18): the raised slatted granary, and the
    # earthen kura - a knob, so both fills are its role
    "granary": frozenset({GRANARY_SLATS, KURA}),
    "cell": frozenset({CELL}),
    "compound shrine": frozenset({SHRINE}),
    "sanctuary": frozenset({SHRINE}),
    "latrine": frozenset({PRIVY}),
    "well": frozenset({WELL}),
}


def _room(r: Mark, structures: list[Mark]) -> bool:
    """`r` stands wholly inside a built structure of another kind: a room, not a building (the ground it stands on - a
    court, a garden - is no structure, so a building on it is not its room)."""
    return any(s is not r and s.kind != r.kind and s.x <= r.x and s.y <= r.y and r.x2 <= s.x2 and r.y2 <= s.y2 for s in structures)


def main_fill(kind: str, svg: str) -> Mark | None:
    """The kind's largest filled rect that is not a room, or None where it draws none."""
    rects = [m for m in marks(svg) if m.tag == "rect" and m.fill not in ("", "none") and m.w > 0 and m.h > 0]
    structures = [m for m in rects if m.fill in STRUCTURE_FILLS]
    own = [r for r in rects if r.kind == kind and not _room(r, structures)]
    return max(own, key=lambda r: r.w * r.h) if own else None


def palette_roles(svg: str, roles: dict[str, frozenset[str]] = ROLES) -> list[str]:
    """Every tabled kind's main fill is one of its role's fills."""
    out: list[str] = []
    for kind, allowed in roles.items():
        r = main_fill(kind, svg)
        if r is not None and r.fill not in allowed:
            out.append(f"the {kind} at svg({r.x:.0f},{r.y:.0f}) is painted {r.fill} - its palette role is {' or '.join(sorted(allowed))}")
    return out
