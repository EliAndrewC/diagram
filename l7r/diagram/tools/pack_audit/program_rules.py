"""The program rules feature 294 moved out of the building-review's sweep into the registry (plan B16-B20): what the
review used to read off every sheet by eye, asked of the sheet's own tags.

- `lodging_entrances` (B16): every block someone sleeps in reaches the ground by a door on its outer wall, and each
  dwelling of a divided row by its own (feature 449 T177).
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

#: The kinds someone sleeps in (docs/building-programs.md, the residence and lodging rows; the checklist's "every lodging
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
"""Research: block join distance - NONE: two blocks within 1 px are one building, which is integer-emit rounding."""


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


#: The row kinds a partition divides into dwellings, each entered by a door of its own (feature 449 T177: 0097's rowhouse dwellings,
#: 0106's long-house). A residence's rooms and an undivided block - 0097's common room behind one door - keep the building's rule.
ROW_KINDS: frozenset[str] = frozenset({"barracks", "retainers' quarters", "servants' quarters"})
"""Research: the row-form lodgings - research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html, research/questions/0106-the-chief-retainers-house-karo-yashiki.drawing.html: a barracks and a retainers' long-house are divided into dwellings, each with a door of its own (0097, 0106), and a servants' quarters takes one of 0097's two forms, a row of dwellings each with its door or a common room behind one door, so these three kinds are the ones a dwelling wall can divide."""
#: The one row kind 0097 lets stand undivided, a common room behind one door: the servants' quarters (feature 449 T187).
COMMON_ROOM_KIND: str = "servants' quarters"
"""Research: the common room is the servants' - research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html: a compound's servants' quarters takes one of two forms, a common room entered by one door or a row of dwellings each with a door of its own, where the barracks is divided into dwellings, so a barracks or a retainers' long-house undivided is refused."""


def dwellings(block: Mark, ms: tuple[Mark, ...], tol: float = JOIN_PX) -> list[tuple[float, float]]:
    """The spans (px, along its long axis) of the dwellings a row block is divided into: the block cut at every dwelling wall - a
    SOLID line of its own kind inside it that runs its full depth, within `tol`. A dashed line is a sliding partition, which 0097
    lets a common room's bays have behind one door, and cuts no dwelling (feature 449 T182, its claims round)."""
    along_x = block.w >= block.h
    lo, hi = (block.x, block.x2) if along_x else (block.y, block.y2)
    cuts: set[float] = set()
    for m in ms:
        if m.tag != "line" or block.kind is None or not m.belongs_to(block.kind) or m.paint.get("stroke-dasharray", "none") not in ("", "none"):
            continue
        if along_x and m.w <= tol and lo < m.x < hi and m.y <= block.y + tol and m.y2 >= block.y2 - tol:
            cuts.add(m.x)
        elif not along_x and m.h <= tol and lo < m.y < hi and m.x <= block.x + tol and m.x2 >= block.x2 - tol:
            cuts.add(m.y)
    edges = [lo, *sorted(cuts), hi]
    return list(zip(edges, edges[1:], strict=False))


def lodging_entrances(svg: str, plan: ParsedPlan, tol: float = DOOR_FLUSH_TOL_PX) -> list[str]:
    """Every building holding a lodging kind has at least one entrance on its OUTER wall: an entrance glyph within `tol`
    of one of its blocks and not wholly inside any of them (DOOR_FLUSH_TOL_PX, the floating-door check's flush reach); and
    every dwelling of a divided row block has one of its own, an outer-wall entrance whose middle lies along that dwelling
    (feature 449 T177: one door anywhere on a joined block passed every dwelling in it).

    Research:
        a lodging entered from the ground - research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html, research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.drawing.html, research/questions/0106-the-chief-retainers-house-karo-yashiki.drawing.html: each barracks dwelling has its earth-floored entry and a servants' quarters is entered by its door or by a door to each dwelling (0097); the residence is entered by its genkan where it stands alone and the household by its own kitchen door (0104); the retainers' long-house, where the karo lodges, gives each dwelling a door of its own on the court (0106).
        a door to each dwelling of a row - research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html, research/questions/0106-the-chief-retainers-house-karo-yashiki.drawing.html: a barracks, a retainers' long-house and a servants' quarters in the row form are divided into dwellings, each with a door of its own, and a row of bays walled off from one another behind one shared door is never drawn, so each dwelling a solid wall divides off is held to its own door; a servants' quarters undivided, or divided only by dashed sliding partitions, is 0097's common room behind one door, the one row kind 0097 lets stand undivided.
        every other lodging entered from the ground - UNRESEARCHED: the guest quarters, a shrine's hall and dwelling and the monk's rooms each reach the ground by a door or genkan on their own outer wall, not only through a building they do not join; no page asks how these were entered.
        the karo's own house entered from the ground - GUESS research/questions/0106-the-chief-retainers-house-karo-yashiki.drawing.html: the karo's small house of their own on the hand-drawn plans, a guess the page records, reaches the ground by a door on its own outer wall, as the long-house gives the karo's quarters a door of their own on the court.
    """
    doors = entrances(svg, plan)
    ms = marks(svg)
    out: list[str] = []
    for comp in components(structure_marks(svg)):
        kinds = sorted({k for b in comp for k in (b.kind or "", *b.lineage) if k in LODGING})
        if not kinds:
            continue
        outer = [d for d in doors if any(gap(d, b) <= tol for b in comp) and not any(_inside(d, b, tol) for b in comp)]
        if not outer:
            x, y = min(b.x for b in comp), min(b.y for b in comp)
            out.append(f"the {' / '.join(kinds)} block at svg({x:.0f},{y:.0f}) has no door or genkan on its outer wall - a lodging is entered from the ground")
            continue
        for b in comp:
            if b.kind not in ROW_KINDS:
                continue
            spans = dwellings(b, ms)
            along_x = b.w >= b.h
            mine = [d for d in outer if gap(d, b) <= tol]
            bare = sum(1 for lo, hi in spans if not any(lo <= ((d.x + d.x2) / 2 if along_x else (d.y + d.y2) / 2) <= hi for d in mine))
            if len(spans) == 1 and b.kind != COMMON_ROOM_KIND:
                out.append(
                    f"the {b.kind} at svg({b.x:.0f},{b.y:.0f}) is undivided - a {b.kind} is divided into dwellings, each with a door of its own; only a servants' quarters is drawn as one common room behind one door"
                )
            if len(spans) > 1 and bare:
                out.append(
                    f"the {b.kind} at svg({b.x:.0f},{b.y:.0f}) has {bare} of its {len(spans)} dwellings with no door of its own on its outer wall - each dwelling of a row is entered by its own door"
                )
    return out


# --- B17 privies_by_zone ----------------------------------------------------------------------------------------------

PRIVY_FILL = "#7E726A"  # the palette's latrine / utility fill (SKILL.md, Palette)
"""Research: a privy drawn gray - CONVENTION: a privy is known on the sheet by the palette's gray, #7E726A, the map drawing convention research/questions/0101-privies-setchin.drawing.html records; no source gives a privy's color."""
COURT_KINDS: tuple[str, ...] = ("inner court", "outer court")
#: A privy within this of a residence block is attached to the house (0.5 ft: flush, with integer-emit rounding).
ATTACHED_PX: float = 0.5 * FTPX
#: At least this many privies on a county manor: the low end of docs/building-programs.md's "one per functional zone, about
#: three or four" (research 0101 'Privies (setchin)'). The record itself calls that count "this project's guess
#: rather than a finding", so the 3 is a GUESS (plan D11).
PRIVY_MIN: int = 3
"""Research: least privies on a county manor - GUESS research/questions/0101-privies-setchin.drawing.html: at least 3 privies, the low end of the project's three or four per compound; the page records the count as the project's guess."""


#: The residence's own privies: the guests' and the family's (0101's drawing page).
RESIDENCE_PRIVIES: int = 2
"""Research: the residence's two privies - research/questions/0101-privies-setchin.drawing.html: a samurai residence has two privies, the guests' and the family's."""


def privies_by_zone(svg: str, minimum: int = PRIVY_MIN) -> list[str]:
    """(a) a privy is the residence's own - tagged a part of it, or attached to one of its blocks (research 0101:
    the privy built into the samurai house); (b) every court the sheet tags has a privy; (c) at least `minimum` in all.

    Research:
        the residence's own privy - research/questions/0101-privies-setchin.drawing.html: a samurai residence's privies are built into the house, so a privy is tagged a part of the residence or attached to one of its blocks.
        a privy in each court zone - GUESS research/questions/0101-privies-setchin.drawing.html: each inner and outer court zone the sheet tags holds a privy, the page's about one privy to each part of the compound, which it records as the project's guess; a court zone is the part of the compound its rects draw, buildings and all, not the open courtyard the page keeps every privy out of.
        the residence's two privies - research/questions/0101-privies-setchin.drawing.html: the house has two privies, the guests' and the family's, so a residence with fewer of its own is refused.
        a sheet-wide floor on the privies - GUESS research/questions/0101-privies-setchin.drawing.html: at least the claimed `minimum` privies on the sheet, the low end of the page's about three or four at a county magistrate's compound, which it records as the project's guess.
    """
    ms = marks(svg)
    privies = [m for m in ms if m.tag == "rect" and m.belongs_to("latrine") and m.fill == PRIVY_FILL]
    house = [m for m in structure_marks(svg) if m.belongs_to("residence") and not m.belongs_to("latrine")]
    out: list[str] = []
    owned = [p for p in privies if "residence" in p.lineage or any(gap(p, b) <= ATTACHED_PX for b in house)]
    if house and not owned:
        out.append("no privy is the residence's own - the family's privy is built into the house (tag it data-part-of=\"residence\" and attach it to a block)")
    elif house and len(owned) < RESIDENCE_PRIVIES:
        # FEATURE 449 T182: one of the house's two privies passed the check, where 0101 gives the house the guests' and the family's
        out.append(f"{len(owned)} privy is the residence's own - the house has {RESIDENCE_PRIVIES}, the guests' and the family's (attach the other to a block)")
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
#: the buildings docs/building-programs.md names for the tubs ("at the fire-prone wooden buildings, weighted to the kitchen",
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
"""Research: which wooden buildings carry a tub - GUESS research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: the office hall, the residence, the barracks, the gatehouse, the compound shrine, the stables, the servants' row, the kitchen and a shrine's hall and dwelling are the major wooden buildings that each carry a tub, and the guest quarters, the karo's house and the retainers' quarters are not; the page puts a tub at each major wooden building and records that no page ranks the buildings for fire water, the ranking the project's reasoning."""
#: The kitchen's tubs: "weighted to the kitchen (2)" (docs/building-programs.md; the record's reasoning, not a page's words).
KITCHEN_TUBS: int = 2
"""Research: kitchen tub count - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: the kitchen gets two fire-water tubs, one at each major wooden building and two at the kitchen, whose fire burns all day."""


def _ft_box(m: Mark) -> tuple[float, float, float, float]:
    return (m.x / FTPX, m.y / FTPX, m.x2 / FTPX, m.y2 / FTPX)


def fire_water_distribution(svg: str, plan: ParsedPlan) -> list[str]:
    """A tub by the eaves of every listed wooden building the sheet draws (the engine's `tub_by_its_eaves`, the one
    predicate `fire_water_adrift` holds), two at the kitchen, and no tub served by a plaster kura alone (buildings/
    programs.md: "none at the plaster kura").

    Research:
        a tub at each wooden building - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: one fire-water tub at each major wooden building, two at the kitchen, and none at an earth-walled storehouse (dozo), built not to burn, so a tub served by a plaster kura alone is refused.
    """
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
#: - the house out-measures its kitchen, its document storehouse and storehouse, and its shrine: docs/building-programs.md
#:   (the residence row) calls that "this project's own reading of the compound"; research 0116 reads only
#:   Takayama's order (office > residence > rowhouse > storehouses) - the tax archive pair rests on its 450 sq ft book
#:   storehouse against a 6,400 sq ft residence (READ), the rest is the record's own reading (GUESS);
#: - the stables and the cell under the barracks: no page read ranks them (GUESS);
#: - the sanctuary under the hall: docs/building-programs.md, "the sanctuary is the smallest building of the shrine proper".
HIERARCHY: tuple[tuple[str, str], ...] = (
    ("kitchen", "residence"),
    ("tax archive", "residence"),
    ("storehouse", "residence"),
    ("compound shrine", "residence"),
    ("stables", "barracks"),
    ("cell", "barracks"),
    ("sanctuary", "hall and dwelling"),
)
"""Research:
    the storehouses under the residence - research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: the tax archive and the other small storehouses stand well below the staff rowhouse, which stands below the residence, the order of the one office measured, at Takayama.
    the kitchen and the shrine under the residence - GUESS research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: no kitchen or shrine hall out-sizes the residence, the largest domestic building; the page records the order among them as the project's reading, a guess.
    the stables under the barracks - GUESS research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: the stable stays smaller than the barracks; the page records its place in the order as a guess.
    the cell under the barracks - GUESS: a cell stays smaller than the barracks; no page ranks them, and the pages' sizes agree, a cell of about 12 by 10 ft, a guess on research/questions/0096-holding-cells-agariya-and-roya.drawing.html, against a long rowhouse 12 to 24 ft deep on research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html.
    the sanctuary under the hall and dwelling - research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html: a sanctuary one to three bays of about 6 ft wide stays smaller than the one-roof hall and dwelling of 2,100 to 3,600 sq ft."""


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
    box.

    Research:
        the sheet's furniture - CONVENTION: the sheet's largest text is a bold title above the compound, and it draws no compass rose (north is always up) and no key box; research/questions/0241-the-map-sheet-its-title-legend-frame-and-margins.drawing.html records the no-compass and no-key conventions for a settlement sheet, and the title's place is the building plans' own; nothing about a building.
    """
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


# --- veranda_depths (feature 374 wave 112) ----------------------------------------------------------------------------

#: A veranda's depth in feet: half a ken to one ken, the widths of Katsura's verandas (research/questions/0102-verandas-and-
#: storm-shutters-engawa-and-amado.drawing.html 'How wide is a drawn veranda?'), ACCURATE; free to change from face to face.
VERANDA_FT: tuple[float, float] = (3.0, 6.0)
"""Research: veranda depth band - research/questions/0102-verandas-and-storm-shutters-engawa-and-amado.drawing.html: a drawn veranda is 3 to 6 ft deep, half a ken to one ken, the widths of Katsura's verandas."""
#: Half a pixel either side: a strip is drawn on whole or half pixels at 3 px to the foot.
VERANDA_TOL_PX: float = 0.5
"""Research: veranda depth tolerance - NONE: half a pixel either side, since strips are drawn on whole or half pixels."""


def veranda_depths(svg: str, band: tuple[float, float] = VERANDA_FT) -> list[str]:
    """Every veranda strip (a rect tagged `engawa`, or inside a group so tagged) is 3-6 ft deep across its short side."""
    out: list[str] = []
    lo, hi = band[0] * FTPX - VERANDA_TOL_PX, band[1] * FTPX + VERANDA_TOL_PX
    for m in marks(svg):
        if m.tag == "rect" and m.kind == "engawa" and not lo <= min(m.w, m.h) <= hi:
            out.append(f"the veranda at svg({m.x:.0f},{m.y:.0f}) is {min(m.w, m.h) / FTPX:.1f} ft deep - the band is {band[0]:.0f}-{band[1]:.0f} ft")
    return out
