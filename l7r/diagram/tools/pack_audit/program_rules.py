"""The program rules feature 294 moved out of the building-review's sweep into the registry (plan B16-B20): what the
review used to read off every sheet by eye, asked of the sheet's own tags.

- `lodging_entrances` (B16): every block someone sleeps in reaches the ground by a door on its outer wall.
- `privies_by_zone` (B17): the residence's privy is the house's own; a privy in every court; at least three.
- `fire_water_distribution` (B18): a tub at every fire-prone wooden building, two at the kitchen, none at a kura alone.
- `size_hierarchy` (B19): the compound's ranking of footprints - the house out-measures its kitchen, and so on.
- `sheet_furniture` (B20): a title block, and no compass rose or key box.

Each is a pure function of the sheet's text (and, where a parsed figure already exists, its `ParsedPlan`), returning
finding strings; `registry.py` gives each its tiers, its red fixture and its fix sentence.
"""

from __future__ import annotations

import re

from ...compound_parts import tub_by_its_eaves
from .checks import DOOR_FLUSH_TOL_PX
from .grids import FTPX
from .labels import footprint
from .parse import KURA_FILLS, STRUCTURE_FILLS, ParsedPlan
from .tagged import Mark, gap, marks

# --- B16 lodging_entrances --------------------------------------------------------------------------------------------

#: The kinds someone sleeps in (docs/buildings/programs.md, the residence and lodging rows; the checklist's "every lodging
#: block ... has a drawn entrance" - a composition rule from the building-review sweep, no number in it). A room of the
#: residence (lord's, family, guest quarters) is part of the residence's block and reaches the ground by the block's door.
LODGING: frozenset[str] = frozenset(
    {
        "residence",
        "family quarters",
        "lord's quarters",
        "guest quarters",
        "servants' quarters",
        "retainers' quarters",
        "barracks",
        "karo's house",
        "hall and dwelling",
        "the monk's rooms",
    }
)
#: The kinds that ARE an entrance: a door glyph, a formal entrance.
ENTRANCE_KINDS: frozenset[str] = frozenset({"door", "genkan"})
#: Two blocks within this of each other are one building (a wing, a corridor, a porch): a MAP DRAWING CONVENTION - the
#: sheets join a building's blocks flush, and a pixel is integer-emit rounding (the `WALL_OVERLAP_MIN_PX` reasoning).
JOIN_PX: float = 1.0


def structure_marks(svg: str) -> list[Mark]:
    """Every built footprint the sheet draws (a rect in a structure fill, `parse.STRUCTURE_FILLS`), entrances excluded."""
    return [m for m in marks(svg) if m.tag == "rect" and m.fill in STRUCTURE_FILLS and m.w > 0 and m.h > 0 and m.kind not in ENTRANCE_KINDS]


def components(blocks: list[Mark], join_px: float = JOIN_PX) -> list[list[Mark]]:
    """The blocks grouped into buildings: blocks within `join_px` of each other, transitively (a union-find)."""
    parent = list(range(len(blocks)))

    def root(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, a in enumerate(blocks):
        for j in range(i + 1, len(blocks)):
            if gap(a, blocks[j]) <= join_px:
                parent[root(i)] = root(j)
    out: dict[int, list[Mark]] = {}
    for i, b in enumerate(blocks):
        out.setdefault(root(i), []).append(b)
    return list(out.values())


def _inside(d: Mark, b: Mark, tol: float) -> bool:
    return d.x >= b.x + tol and d.x2 <= b.x2 - tol and d.y >= b.y + tol and d.y2 <= b.y2 - tol


def entrances(svg: str, plan: ParsedPlan) -> list[Mark]:
    """Every entrance glyph: a mark tagged door or genkan, and every small dark door rect the parser finds untagged."""
    out = [m for m in marks(svg) if m.tag == "rect" and m.kind in ENTRANCE_KINDS]
    seen = {m.pos for m in out}
    for r in plan.door_rects:
        if r.pos not in seen:
            out.append(Mark("rect", None, (), r.x, r.y, r.w, r.h, r.pos, {"fill": r.fill}))
    return out


def lodging_entrances(svg: str, plan: ParsedPlan, tol: float = DOOR_FLUSH_TOL_PX) -> list[str]:
    """Every building holding a lodging kind has at least one entrance on its OUTER wall: an entrance glyph within `tol`
    of one of its blocks and not wholly inside any of them (DOOR_FLUSH_TOL_PX, the floating-door check's flush reach)."""
    doors = entrances(svg, plan)
    out: list[str] = []
    for comp in components(structure_marks(svg)):
        kinds = sorted({k for b in comp for k in (b.kind or "", *b.lineage) if k in LODGING})
        if not kinds:
            continue
        if any(any(gap(d, b) <= tol for b in comp) and not any(_inside(d, b, tol) for b in comp) for d in doors):
            continue
        x, y = min(b.x for b in comp), min(b.y for b in comp)
        out.append(f"the {' / '.join(kinds)} block at svg({x:.0f},{y:.0f}) has no door or genkan on its outer wall - a lodging is entered from the ground")
    return out


# --- B17 privies_by_zone ----------------------------------------------------------------------------------------------

PRIVY_FILL = "#7E726A"  # the palette's latrine / utility fill (SKILL.md, Palette)
COURT_KINDS: tuple[str, ...] = ("inner court", "outer court")
#: A privy within this of a residence block is attached to the house (0.5 ft: flush, with integer-emit rounding).
ATTACHED_PX: float = 0.5 * FTPX
#: At least this many privies on a county manor: the low end of docs/buildings/programs.md's "one per functional zone, about
#: three or four" (research 0101 'Privies (setchin)'). The record itself calls that count "this project's guess
#: rather than a finding", so the 3 is a GUESS (plan D11).
PRIVY_MIN: int = 3


def privies_by_zone(svg: str, minimum: int = PRIVY_MIN) -> list[str]:
    """(a) a privy is the residence's own - tagged a part of it, or attached to one of its blocks (research 0101:
    the privy built into the samurai house); (b) every court the sheet tags has a privy; (c) at least `minimum` in all."""
    ms = marks(svg)
    privies = [m for m in ms if m.tag == "rect" and m.belongs_to("latrine") and m.fill == PRIVY_FILL]
    house = [m for m in structure_marks(svg) if m.belongs_to("residence") and not m.belongs_to("latrine")]
    out: list[str] = []
    if house and not any("residence" in p.lineage or any(gap(p, b) <= ATTACHED_PX for b in house) for p in privies):
        out.append("no privy is the residence's own - the family's privy is built into the house (tag it data-part-of=\"residence\" and attach it to a block)")
    # a ZONE is a court kind, however many precinct rects draw it (Hayakawa's inner court runs on into its river annex)
    for kind in COURT_KINDS:
        ground = [m for m in ms if m.ident == "precinct" and m.kind == kind]
        if ground and not any(c.x <= p.x + p.w / 2 <= c.x2 and c.y <= p.y + p.h / 2 <= c.y2 for c in ground for p in privies):
            out.append(f"the {kind} at svg({ground[0].x:.0f},{ground[0].y:.0f}) has no privy - one stands in each functional zone")
    if len(privies) < minimum:
        out.append(f"{len(privies)} privies on the sheet - a county manor has at least {minimum} (one per functional zone, about three or four)")
    return out


# --- B18 fire_water_distribution --------------------------------------------------------------------------------------

#: The fire-prone wooden buildings a tub must stand by - DECIDED AND RECORDED HERE (feature 294, the scout's note on B18):
#: the buildings docs/buildings/programs.md names for the tubs ("at the fire-prone wooden buildings, weighted to the kitchen",
#: and for the shrine "a tub at the hall's corners") and the generator seats one at (`compound_parts._point_features`):
#: the office hall, the residence, the barracks, the gatehouse, the compound shrine, the stables, the servants' row, the
#: kitchen; the shrine's hall-and-dwelling. Guest quarters, the karo's house and the retainers' quarters are NOT on the
#: list: the record names them nowhere for a tub (research 0100 reads only the townspeople's habit and a town
#: order, "not a rule for every building"), and holding them to one would fail Ochiba (karo's house 0, retainers' 0) and
#: Ubame (guest 0) on a rule no source gives. "A tub at every wooden building, as a rule" is the record's reading (GUESS).
TUB_KINDS: tuple[str, ...] = (
    "office hall",
    "residence",
    "barracks",
    "gatehouse",
    "compound shrine",
    "stables",
    "servants' quarters",
    "kitchen",
    "hall and dwelling",
)
#: The kitchen's tubs: "weighted to the kitchen (2)" (docs/buildings/programs.md; the record's reasoning, not a page's words).
KITCHEN_TUBS: int = 2


def _ft_box(m: Mark) -> tuple[float, float, float, float]:
    return (m.x / FTPX, m.y / FTPX, m.x2 / FTPX, m.y2 / FTPX)


def fire_water_distribution(svg: str, plan: ParsedPlan) -> list[str]:
    """A tub by the eaves of every listed wooden building the sheet draws (the engine's `tub_by_its_eaves`, the one
    predicate `fire_water_adrift` holds), two at the kitchen, and no tub served by a plaster kura alone (buildings/
    programs.md: "none at the plaster kura")."""
    blocks = structure_marks(svg)
    wooden = [b for b in blocks if b.fill not in KURA_FILLS]
    kura = [b for b in blocks if b.fill in KURA_FILLS]
    centers = [((t.x + t.w / 2) / FTPX, (t.y + t.h / 2) / FTPX) for t in plan.tubs]
    out: list[str] = []
    for kind in TUB_KINDS:
        own = [b for b in wooden if b.kind == kind or (kind in b.lineage and b.kind not in TUB_KINDS)]
        if not own:
            continue
        n = sum(1 for c in centers if any(tub_by_its_eaves(c, _ft_box(b)) for b in own))
        want = KITCHEN_TUBS if kind == "kitchen" else 1
        if n < want:
            out.append(f"the {kind} at svg({own[0].x:.0f},{own[0].y:.0f}) has {n} fire-water tub(s) by its eaves - it needs {want}")
    for c in centers:
        if any(tub_by_its_eaves(c, _ft_box(k)) for k in kura) and not any(tub_by_its_eaves(c, _ft_box(b)) for b in wooden):
            out.append(f"a fire-water tub at svg({c[0] * FTPX:.0f},{c[1] * FTPX:.0f}) stands by a plaster kura alone - a kura carries no tub")
    return out


# --- B19 size_hierarchy -----------------------------------------------------------------------------------------------

#: (smaller, larger): the compound's size HIERARCHY, the pair list of the building-review checklist. Each pair's class:
#: - the house out-measures its kitchen, its document storehouse and storehouse, and its shrine: docs/buildings/programs.md
#:   (the residence row) calls that "this project's own reading of the compound"; research 0116 reads only
#:   Takayama's order (office > residence > rowhouse > storehouses) - the tax archive pair rests on its 450 sq ft book
#:   storehouse against a 6,400 sq ft residence (READ), the rest is the record's own reading (GUESS);
#: - the stables and the cell under the barracks: no page read ranks them (GUESS);
#: - the sanctuary under the hall: docs/buildings/programs.md, "the sanctuary is the smallest building of the shrine proper".
HIERARCHY: tuple[tuple[str, str], ...] = (
    ("kitchen", "residence"),
    ("tax archive", "residence"),
    ("storehouse", "residence"),
    ("compound shrine", "residence"),
    ("stables", "barracks"),
    ("cell", "barracks"),
    ("sanctuary", "hall and dwelling"),
)


def size_hierarchy(plan: ParsedPlan, pairs: tuple[tuple[str, str], ...] = HIERARCHY) -> list[str]:
    """Each pair's footprints (`labels.footprint`, the largest structure tagged with the kind) rank as the list says; a
    pair is skipped where the sheet draws either kind as no structure."""
    out: list[str] = []
    for small, big in pairs:
        a, b = footprint(plan, small), footprint(plan, big)
        if a is None or b is None:
            continue
        sa, sb = a.area_px / FTPX**2, b.area_px / FTPX**2
        if sa >= sb:
            out.append(f"the {small} ({sa:.0f} sq ft) is not smaller than the {big} ({sb:.0f} sq ft) - the compound ranks its buildings")
    return out


# --- B20 sheet_furniture ----------------------------------------------------------------------------------------------

_COMPASS_TEXT = re.compile(r"^\s*(?:N|North)\s*$", re.I)
_KEY_TEXT = re.compile(r"^\s*(?:Key|Legend)\s*:?\s*$", re.I)
_FURNITURE_ATTR = re.compile(r'\s(?:id|data-kind)="([^"]*(?:compass|rose|legend)[^"]*)"', re.I)


def sheet_furniture(svg: str) -> list[str]:
    """SKILL.md 'Title block' and 'Orientation' (map drawing conventions): a title - the sheet's largest bold text,
    placed, its baseline above the precinct's top edge (its SIZE varies by sheet and is not held: 30 on the hand
    manors, 18 on the shrine, 20 on the drafts); no compass rose (north-at-top is invariant, GM 2026-07); no key
    box."""
    ms = marks(svg)
    texts = [m for m in ms if m.tag == "text" and m.placed and m.text]
    top = min((m.y for m in ms if m.ident == "precinct"), default=None)
    out: list[str] = []
    biggest = max((m.font_size for m in texts), default=0.0)
    if not any(m.paint.get("font-weight") == "bold" and m.font_size == biggest and (top is None or m.y <= top) for m in texts):
        out.append("no title block - the sheet's largest text, bold, centered just above the compound")
    for m in ms:
        if m.tag == "text" and _COMPASS_TEXT.match(m.text):
            out.append(f"a compass mark ('{m.text}') at svg({m.x:.0f},{m.y:.0f}) - north is always up; the sheet draws no compass rose")
        elif m.tag == "text" and _KEY_TEXT.match(m.text):
            out.append(f"a key box ('{m.text}') at svg({m.x:.0f},{m.y:.0f}) - the sheet labels its features in place, with no key")
    # an id or a kind on ANY element, a group's included (an authored rose is a group of strokes): attributes, never comments
    for name in _FURNITURE_ATTR.findall(svg):
        out.append(f"an element marked '{name}' - the sheet draws no compass rose and no key box")
    return out
