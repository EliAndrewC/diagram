"""Split from tools/pack_audit.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ...compound_model import NOTICE_BOARD_MAX_FT as NOTICE_BOARD_MAX_FT
from ...compound_model import TUB_DOOR_MAX_FT as TUB_DOOR_MAX_FT
from ...compound_model import TUB_MAX_GAP_FT as TUB_MAX_GAP_FT
from ...compound_parts import board_by_a_gate, tub_by_its_door, tub_by_its_eaves
from .grids import FTPX
from .parse import WALL_KIND, WALL_STROKE, ParsedPlan, Rect

# TUB_MAX_GAP_FT (3.5): a wall-hugging tub sits ~1.7-2 ft from a wall (its own radius + eaves); beyond this it is adrift
# in the court with no roof draining into it. NOTICE_BOARD_MAX_FT (40 since feature 372 wave 104): a notice board must sit within this of a gate
# opening to be read. Both numbers AND both rules are the engine's (feature 287, homes H29b): the compound draft seats its
# tubs and its board by `tub_by_its_eaves` / `board_by_a_gate`, and `fire_water_adrift` / `notice_board_adrift` below
# call the same two predicates, so a generated sheet cannot seat what this audit would flag.
TUB_WELL_MIN_PX: float = 1.0  # a fire-water tub overlapping a well glyph by more than this sits ON it
TUB_BLDG_MIN_PX: float = 0.5  # ...and reaching this far past a building's edge, it is drawn INTO the
OCCLUSION_MIN_PX: float = 3.0  # a later feature must cover at least this much of a foreground item to count
# (privy, door, board, hearth, stilt, mat) - foreground that belongs ABOVE the fills.
PASSAGE_DEPTH_PX: float = 9.0  # the gateway zone reaches 3 ft in front of and behind the wall ink -
# a stone set just inside or just outside the masonry is still in the track a cart drives through
PASSAGE_CLEAR_MIN_PX: float = 0.5  # sub-pixel contact is a flush jamb (a gate post abutting the
# opening edge) plus integer-emit rounding, not an object standing in the passage
OPENING_MAX_PX: float = 80.0  # a wider gap in the wall is a structural break (a wall drawn around a
# building that IS part of it), not a gate - see `wall_openings`
DOOR_FLUSH_TOL_PX: float = 1.5  # a door within this of a building edge reads as ON the wall
DOOR_NEAR_PX: float = 12.0  # a door candidate this close to an edge is TRYING to be in the wall (vs a deep interior marker)
WALL_OVERLAP_MIN_PX: float = 0.5  # sub-pixel contact is a flush abutment + integer-emit rounding,


@dataclass(frozen=True)
class Gap:
    """An empty gap (ft) between two buildings stacked on a shared edge."""

    ft: float
    orient: str
    mx: float
    my: float
    kura: bool


@dataclass(frozen=True)
class TubAdrift:
    """A fire-water tub sitting too far from any building to be gutter-fed."""

    x: float  # tub center, SVG px
    y: float
    gap_ft: float  # distance from tub center to the nearest building


def _point_rect_dist(px: float, py: float, r: Rect) -> float:
    """Euclidean distance from a point to a rectangle (0 if the point is inside)."""
    dx = max(r.x - px, 0.0, px - r.x2)
    dy = max(r.y - py, 0.0, py - r.y2)
    return math.hypot(dx, dy)


def _ft_box(r: Rect) -> tuple[float, float, float, float]:
    """A sheet rect as the engine's feet box (x0, y0, x1, y1) - what the H29b predicates measure."""
    return (r.x / FTPX, r.y / FTPX, r.x2 / FTPX, r.y2 / FTPX)


def fire_water_adrift(plan: ParsedPlan) -> list[TubAdrift]:
    """Fire-water tubs sitting farther than TUB_MAX_GAP_FT from any building - a tub no building's eaves hold by the
    engine's `tub_by_its_eaves`, the one predicate the compound draft seats its tubs by.

    A tensuioke is fed by roof runoff (gutter -> downspout -> tub at the wall base), so every
    tub must sit against a building. Unlike a court's open space (a judgment call), this is a
    hard geometric rule: a tub adrift in the court is fed by nothing. Worst (farthest) first.
    """
    out: list[TubAdrift] = []
    for t in plan.tubs:
        cx, cy = t.x + t.w / 2, t.y + t.h / 2
        if any(tub_by_its_eaves((cx / FTPX, cy / FTPX), _ft_box(b)) for b in plan.buildings):
            continue
        gaps = [_point_rect_dist(cx, cy, b) for b in plan.buildings]
        out.append(TubAdrift(cx, cy, (min(gaps) if gaps else float("inf")) / FTPX))
    out.sort(key=lambda t: t.gap_ft, reverse=True)
    return out


@dataclass(frozen=True)
class TubOffItsDoor:
    """A fire-water tub at its building's eaves but away from every door of it."""

    x: float
    y: float
    door_ft: float  # the center-to-center distance to the nearest door of the buildings it serves


# A door glyph is drawn inside its wall's line or just outside it (Hayakawa's kitchen door stands on the face, 6 px out)
DOOR_ON_WALL_PX = 2.0 * FTPX


def doors_of(plan: ParsedPlan, b: Rect) -> list[tuple[float, float]]:
    """The centers (px) of the doors on building `b`: each rect the sheet tags `door` (its own tags, feature 262 - a
    small dark rect may as well be a hearth) lying within DOOR_ON_WALL_PX of the footprint."""
    m = DOOR_ON_WALL_PX
    return [
        (d.x + d.w / 2, d.y + d.h / 2)
        for d in plan.fills
        if plan.label_kinds.get(d.pos) == "door" and d.x >= b.x - m and d.x2 <= b.x2 + m and d.y >= b.y - m and d.y2 <= b.y2 + m
    ]


def tubs_off_their_doors(plan: ParsedPlan) -> list[TubOffItsDoor]:
    """Fire-water tubs that stand at a building's wall but not at its entrance (feature 372 wave 106): research 0100 keeps
    standing water at a wooden building's entrance, so a tub's center stands within TUB_DOOR_MAX_FT of a door of a
    building whose eaves hold it (`tub_by_its_door`, the predicate the draft seats by). A tub whose buildings draw no door
    is not judged here; one adrift of every building is `fire_water_adrift`'s. Worst (farthest) first."""
    out: list[TubOffItsDoor] = []
    for t in plan.tubs:
        cx, cy = t.x + t.w / 2, t.y + t.h / 2
        hosts = [b for b in plan.buildings if tub_by_its_eaves((cx / FTPX, cy / FTPX), _ft_box(b))]
        doors = [(dx / FTPX, dy / FTPX) for b in hosts for dx, dy in doors_of(plan, b)]
        if not doors or tub_by_its_door((cx / FTPX, cy / FTPX), doors):
            continue
        out.append(TubOffItsDoor(cx, cy, min(math.hypot(cx / FTPX - dx, cy / FTPX - dy) for dx, dy in doors)))
    out.sort(key=lambda t: t.door_ft, reverse=True)
    return out


@dataclass(frozen=True)
class TubInBuilding:
    """A fire-water tub whose glyph reaches into a building instead of standing clear of it."""

    x: float
    y: float
    into_ft: float  # how far the tub's BODY reaches past the footprint edge


def tubs_in_buildings(plan: ParsedPlan, min_px: float = TUB_BLDG_MIN_PX) -> list[TubInBuilding]:
    """Fire-water tubs whose glyph overlaps a building footprint instead of standing clear of it.

    A tensuioke stands in the open at the foot of a downspout, catching what the roof sheds, so
    it belongs OUTSIDE the wall it serves. Drawn into the footprint it is fed by nothing and
    stands where no bucket line can reach it - the two things the tub exists for. This is the
    companion of `fire_water_adrift`: that check pulls a tub IN toward a building, this one keeps
    it OUT of one, and only the narrow band along the outside wall - where a real tub stands -
    satisfies both. Worst (deepest in) first.

    A ROOFED court counts as a footprint (feature 267 pass 3, the building-review's catch: the placer seated the office
    hall's tub inside its roofed hearing court): the tub stands under the roof, where no gutter feeds it.

    The measure is the DRAWN DISC's penetration past the nearest footprint edge, not its center's
    position (GM catch 2026-07-26, Ubame's karo's-house tub). A center test asks "is the tub
    indoors?", but what the GM sees is INK ON INK, and a tub whose center sits a hair outside the
    wall still has a quarter of its body inside the room - the same defect, drawn smaller. Center
    tests are also discontinuous: a tub creeping in registers nothing at all until its center
    crosses, then jumps to a whole radius. Penetration rises smoothly from the first pixel of
    contact, so the check has no blind band where a real overlap scores zero. Disc geometry
    rather than the parsed square bbox because a tub set diagonally off a building CORNER
    overlaps the bbox while its round body stands clear - a bbox test would flag a good tub.
    """
    out: list[TubInBuilding] = []
    for t in plan.tubs:
        cx, cy, rad = t.x + t.w / 2, t.y + t.h / 2, t.w / 2
        into = 0.0
        for b in plan.buildings + plan.roofed_courts:
            gap = _point_rect_dist(cx, cy, b)
            # center outside: the disc reaches (rad - gap) past the edge. Center inside: it reaches
            # its own radius PLUS the center's depth, so the two cases join continuously at gap=0.
            inside = min(cx - b.x, b.x2 - cx, cy - b.y, b.y2 - cy) if gap == 0 else -gap
            into = max(into, rad + inside)
        if into >= min_px:
            out.append(TubInBuilding(cx, cy, into / FTPX))
    out.sort(key=lambda t: t.into_ft, reverse=True)
    return out


@dataclass(frozen=True)
class TubOnWell:
    """A fire-water tub glyph overlapping a well glyph - they smear into one blob."""

    x: float
    y: float


def tubs_on_wells(plan: ParsedPlan, min_px: float = TUB_WELL_MIN_PX) -> list[TubOnWell]:
    """Fire-water tubs sitting ON a well. Both are small point-glyphs; overlapping ones read as
    one object and are functionally wrong (a rain-fed fire tub is not the drawing well). Any real
    overlap is a defect - move the tub to a different eaves corner."""
    out: list[TubOnWell] = []
    for t in plan.tubs:
        if any(_overlap_px(t.x, t.y, t.x2, t.y2, w) >= min_px for w in plan.wells):
            out.append(TubOnWell(t.x + t.w / 2, t.y + t.h / 2))
    return out


@dataclass(frozen=True)
class Occluded:
    """A foreground item painted over by anything drawn later in the SVG (not on the top layer)."""

    kind: str  # "tub" | "well" | "feature"
    x: float
    y: float


def _overlap_px(ax: float, ay: float, ax2: float, ay2: float, b: Rect) -> float:
    """Smaller of the x/y overlaps between a box and rect b (>0 only on a real 2-D overlap)."""
    return min(min(ax2, b.x2) - max(ax, b.x), min(ay2, b.y2) - max(ay, b.y))


def occluded_foreground(plan: ParsedPlan, min_px: float = OCCLUSION_MIN_PX) -> list[Occluded]:
    """Foreground items painted OVER by anything drawn LATER in the SVG - i.e. not on the top
    layer, so they read as buried (a tub's rim, a privy that vanishes).

    Draw-order rule: point glyphs and furniture-scale features belong ABOVE the fills, so any
    later rect or glyph covering one is a defect. Both sides of that test are deliberately broad -
    the occluder side is fill-BLIND (see OCCLUSION_MIN_PX) and the occluded side spans tubs, wells
    and every sub-building rect - because the two defects this check was widened for (2026-07-25)
    each slipped through a narrow enumeration: a note box was not a "building or garden", and a
    privy was not a "label or tub".

    NOT CAPTIONS (feature 286): a caption is placed by the one placer in the render pipeline, which
    writes it after the drawing; whether it is buried is the placer's to get right and its unit
    tests' to hold, not a check's (the GM: "There is no point in having an automated check run
    against an automated process"). What is still drawn by hand is still checked here.
    """
    occluders = plan.fills + plan.glyphs
    out: list[Occluded] = []

    def buried(x: float, y: float, x2: float, y2: float, pos: int) -> bool:
        # A later shape wholly INSIDE the item is its own detailing (a well-mouth circle in its
        # curb, a hearth's fire in its hearth), not something painted over it.
        return any(f.pos > pos and _overlap_px(x, y, x2, y2, f) >= min_px and not (f.x >= x and f.y >= y and f.x2 <= x2 and f.y2 <= y2) for f in occluders)

    for t in plan.tubs:
        if buried(t.x, t.y, t.x2, t.y2, t.pos):
            out.append(Occluded("tub", t.x + t.w / 2, t.y + t.h / 2))
    for w in plan.wells:
        if buried(w.x, w.y, w.x2, w.y2, w.pos):
            out.append(Occluded("well", w.x + w.w / 2, w.y + w.h / 2))
    for f0 in plan.furniture:
        if buried(f0.x, f0.y, f0.x2, f0.y2, f0.pos):
            out.append(Occluded("feature", f0.x + f0.w / 2, f0.y + f0.h / 2))
    return out


@dataclass(frozen=True)
class WallOpening:
    """A gap in the compound wall's INK - the passage a cart actually drives through.

    `span1..span2` is the gap along the wall, `across1..across2` the ink's own thickness; together
    they are the gateway rect that `passage_blockers` keeps clear.
    """

    x: float
    y: float
    ft: float
    horiz: bool = True
    span1: float = 0.0
    span2: float = 0.0
    across1: float = 0.0
    across2: float = 0.0


def wall_openings(plan: ParsedPlan) -> list[WallOpening]:
    """Openings in the compound wall, measured from the INK, widest first.

    Measured from `wall_bands` - which model `stroke-linecap="square"`, a run inking half a stroke
    past each endpoint - and NOT from the line endpoints. That difference IS the check. WHY
    (2026-07-25): all three pool manors were authored by writing each intended opening as the two
    flanking ENDPOINTS, which a 9 px capped wall then narrowed by a full stroke width, so every
    stated 13.3 ft main gate rendered as 10.3 ft of passage. On Ubame that had quietly made the
    goods-cart gate WIDER than the ceremonial main gate - a hierarchy inversion nobody intended.
    Nothing in the audit measured ink, so the error was invisible in the report: it had to be found
    by eye on one map, and it then sat unfixed on the other two until they were hand-checked.
    Reporting ink width makes "ink equals intent" something an author reads off the audit.

    The correct authoring idiom is to pull each flanking endpoint back by half a stroke (4.5 px on
    the 9 px compound wall) so the CAP lands on the intended edge - never to write the endpoints at
    the opening's coordinates and hope the cap is not there.
    """
    out: list[WallOpening] = []
    for horiz in (True, False):
        groups: dict[float, list[Rect]] = {}
        for band in plan.wall_bands:
            if band.fill != WALL_STROKE or (band.w >= band.h) != horiz:
                continue
            groups.setdefault(round(band.y + band.h / 2 if horiz else band.x + band.w / 2, 1), []).append(band)
        for key, segs in groups.items():
            segs.sort(key=lambda s: s.x if horiz else s.y)
            for a, b in zip(segs, segs[1:], strict=False):
                gap = (b.x - a.x2) if horiz else (b.y - a.y2)
                if 0 < gap < OPENING_MAX_PX:
                    mid = (a.x2 + b.x) / 2 if horiz else (a.y2 + b.y) / 2
                    s1, s2 = (a.x2, b.x) if horiz else (a.y2, b.y)
                    t1, t2 = (a.y, a.y2) if horiz else (a.x, a.x2)
                    out.append(WallOpening(mid if horiz else key, key if horiz else mid, gap / FTPX, horiz, s1, s2, t1, t2))
    out.sort(key=lambda o: o.ft, reverse=True)
    return out


@dataclass(frozen=True)
class PassageBlocker:
    """A furniture-scale object standing in a gateway, where the traffic goes."""

    x: float
    y: float
    w_ft: float
    h_ft: float
    opening_ft: float


def passage_blockers(plan: ParsedPlan) -> list[PassageBlocker]:
    """Furniture-scale objects standing in a gate's PASSAGE - the track that carts and people use.

    WHY (GM 2026-07-25): a threshold stone is an ABOVE-GROUND marker set on either side of the road,
    not paving laid flush with it, so nothing may stand between a gateway's jambs. Ochiba's vermillion
    pair had been drawn "centered in the gate threshold" - what the vocabulary used to say - which put
    both stones INSIDE a 13.3 ft passage and left 5.3 ft of clear track between them, so a cart would
    have had to roll over a stone meant to stand proud of the ground. That is the SECOND round of this
    defect: a single large stone squarely across the passage was caught by eye in 2026-07 and "fixed"
    into the pair, which is precisely the history that argues for a check rather than a habit.

    Two exclusions, both deliberate. BUILDINGS do not count: a mass filling a gap in the wall is the
    wall-broken-around-a-structure idiom (Ubame's parley room stands in the border wall exactly that
    way), not a blocked gate. GROUND COVER does not count either - gravel, swept keiko earth and
    garden stipple run through a gateway by design. What has to stay out is the furniture: stones,
    point glyphs, tubs, well curbs, posts set in the track.
    """
    out: list[PassageBlocker] = []
    for o in wall_openings(plan):
        x1, y1, x2, y2 = (o.span1, o.across1 - PASSAGE_DEPTH_PX, o.span2, o.across2 + PASSAGE_DEPTH_PX) if o.horiz else (o.across1 - PASSAGE_DEPTH_PX, o.span1, o.across2 + PASSAGE_DEPTH_PX, o.span2)
        for r in plan.furniture + plan.wells + plan.glyphs + plan.tubs:
            if min(r.x2, x2) - max(r.x, x1) > PASSAGE_CLEAR_MIN_PX and min(r.y2, y2) - max(r.y, y1) > PASSAGE_CLEAR_MIN_PX:
                out.append(PassageBlocker(r.x + r.w / 2, r.y + r.h / 2, r.w / FTPX, r.h / FTPX, o.ft))
    out.sort(key=lambda b: b.w_ft * b.h_ft, reverse=True)
    return out


def _gate_openings(plan: ParsedPlan) -> list[tuple[float, float]]:
    """Midpoints of gaps in the compound wall - the gate/postern openings."""
    return [(o.x, o.y) for o in wall_openings(plan)]


@dataclass(frozen=True)
class MisplacedBoard:
    """A notice board too far from any gate opening to be seen by passers-through."""

    x: float
    y: float
    gap_ft: float


def _main_gate_passage(plan: ParsedPlan) -> list[tuple[float, float]]:
    """The middle of the passage between the `main gate`'s posts. A nagaya-mon's passage runs THROUGH its gate range,
    which stands in a wall break wider than any gap the wall-opening scan counts as a gate (feature 267: the range is
    the wall line, research buildings 420), so a board at that gate read as adrift; the posts say where it is."""
    posts = plan.gate_posts
    if not posts:
        return []
    return [(sum(r.x + r.w / 2 for r in posts) / len(posts), sum(r.y + r.h / 2 for r in posts) / len(posts))]


def main_gate_passage_ft(plan: ParsedPlan) -> float | None:
    """The clear width between the `main gate`'s two posts, in feet - the ceremonial gate's passage, which a wall-gap scan
    cannot see where it runs through a gate range standing in a wider break (feature 267). The posts are the group's two
    SMALLEST rects: a gate drawn through a range tags its passage floor `main gate` too (Hayakawa). None without two."""
    if len(plan.gate_posts) < 2:
        return None
    posts = sorted(sorted(plan.gate_posts, key=lambda r: r.w * r.h)[:2], key=lambda r: (r.x, r.y))
    a, b = posts
    across = b.x - (a.x + a.w) if abs(a.y - b.y) < max(a.h, b.h) else b.y - (a.y + a.h)
    return across / FTPX


def notice_board_adrift(plan: ParsedPlan) -> list[MisplacedBoard]:
    """A notice board (kosatsu) is read where people pass, so it must sit at a gate. Flag any notice
    board farther than max_ft from the nearest wall gate opening.

    THE BOARD, NOT ITS CAPTION (feature 266). This measured the 'notice board' LABEL as a stand-in for the
    board, which held while every caption hung just under its board; once captions are seated by the
    cartographic standard - beside the board at its first free ranked position - the caption can stand a
    board's length off to one side, and a board at the gate read as adrift. The sheet tags the board
    (feature 262), so its own drawn rect is measured - and only that: a caption is placed by the pipeline
    (feature 286), so where it stands says nothing about where the board was drawn, and a sheet that tags
    no board has no board this check can see."""
    ops = _gate_openings(plan) + _main_gate_passage(plan)
    if not ops:
        return []
    out: list[MisplacedBoard] = []
    for r in plan.fills:
        if plan.label_kinds.get(r.pos) != "notice board":
            continue
        if board_by_a_gate(_ft_box(r), [(ox / FTPX, oy / FTPX) for ox, oy in ops]):  # the engine's one predicate (H29b)
            continue
        out.append(MisplacedBoard(r.x + r.w / 2, r.y + r.h / 2, min(_point_rect_dist(ox, oy, r) for ox, oy in ops) / FTPX))
    return out


@dataclass(frozen=True)
class FloatingDoor:
    """A door glyph floating INSIDE a building instead of sitting on (an opening in) its wall."""

    x: float
    y: float
    gap_ft: float  # gap to the nearest wall it should sit on


def floating_doors(plan: ParsedPlan) -> list[FloatingDoor]:
    """A door is an opening in a WALL, so its glyph must sit on a building edge, not adrift in the
    interior. Flag a small dark door-rect fully contained in a building whose nearest edge is close
    (it is clearly meant to be that wall's door) but not flush - leaving white space to the wall."""
    out: list[FloatingDoor] = []
    for d in plan.door_rects:
        for b in plan.buildings:
            gaps = (d.x - b.x, b.x2 - d.x2, d.y - b.y, b.y2 - d.y2)
            if all(g >= 0 for g in gaps):  # fully inside this building
                gap = min(gaps)
                if DOOR_FLUSH_TOL_PX < gap <= DOOR_NEAR_PX:
                    out.append(FloatingDoor(d.x + d.w / 2, d.y + d.h / 2, gap / FTPX))
                break
    return out


@dataclass(frozen=True)
class StructureOnWall:
    """A built footprint drawn across the ink of a wall, i.e. standing inside the masonry."""

    x: float  # structure center, SVG px
    y: float
    w_ft: float  # the structure's size, to identify it in the source
    h_ft: float
    into_ft: float  # how far it reaches into the wall's ink
    wall: str  # "compound wall" | "court divider"


def structures_on_walls(plan: ParsedPlan, min_px: float = WALL_OVERLAP_MIN_PX) -> list[StructureOnWall]:
    """Structures overlapping the ink of a compound wall or a court divider, worst first.

    A wall is a built object with real thickness (drawn at true scale - 3 ft for the compound
    wall, 2 ft for the divider - and centered on the boundary, so half of it lies inside), not a
    boundary line with no substance. Two things go wrong when a structure is drawn across it:
    the plan asserts a building and a wall occupy the same ground, and the render shows it -
    the wall is painted last, so it eats the structure's own outline and the structure reads as
    bleeding through the masonry. The correct relation is ABUT: a jin'ya's buildings back the
    wall with their rear eaves nearly touching it, which the check permits (a flush edge scores
    zero overlap). Where a structure genuinely IS part of the wall - a nagayamon gatehouse, a
    postern - the established idiom is to draw the wall as segments BROKEN around it (already
    used for Ochiba's kitchen postern and both south gates), which states the relationship
    explicitly and leaves no ink to overlap.
    """
    out: list[StructureOnWall] = []
    for s in plan.structures:
        worst: tuple[float, str] | None = None
        for band in plan.wall_bands:
            ov = _overlap_px(s.x, s.y, s.x2, s.y2, band)
            if ov > min_px and (worst is None or ov > worst[0]):
                worst = (ov, WALL_KIND[band.fill])
        if worst is not None:
            out.append(StructureOnWall(s.x + s.w / 2, s.y + s.h / 2, s.w / FTPX, s.h / FTPX, worst[0] / FTPX, worst[1]))
    out.sort(key=lambda r: r.into_ft, reverse=True)
    return out


def _blocked(
    buildings: tuple[Rect, ...],
    i: int,
    j: int,
    lo: float,
    hi: float,
    near: float,
    far: float,
    *,
    vert: bool,
) -> bool:
    for k, r in enumerate(buildings):
        if k in (i, j):
            continue
        if vert and r.x < hi and r.x2 > lo and r.y < far and r.y2 > near:
            return True
        if not vert and r.y < hi and r.y2 > lo and r.x < far and r.x2 > near:
            return True
    return False


def aligned_gaps(plan: ParsedPlan) -> list[Gap]:
    """Empty gaps (5-30 ft) between buildings stacked on a shared edge, largest first."""
    b = plan.buildings
    raw: list[Gap] = []
    for i, a in enumerate(b):
        for j, c in enumerate(b):
            if i == j:
                continue
            ox = min(a.x2, c.x2) - max(a.x, c.x)
            if ox >= 30 and c.y >= a.y2 and 15 <= (c.y - a.y2) <= 90:
                xl, xr = max(a.x, c.x), min(a.x2, c.x2)
                if not _blocked(b, i, j, xl, xr, a.y2, c.y, vert=True):
                    raw.append(
                        Gap(
                            (c.y - a.y2) / FTPX,
                            "V",
                            (xl + xr) / 2,
                            (a.y2 + c.y) / 2,
                            a.is_kura or c.is_kura,
                        )
                    )
            oy = min(a.y2, c.y2) - max(a.y, c.y)
            if oy >= 30 and c.x >= a.x2 and 15 <= (c.x - a.x2) <= 90:
                yl, yr = max(a.y, c.y), min(a.y2, c.y2)
                if not _blocked(b, i, j, a.x2, c.x, yl, yr, vert=False):
                    raw.append(
                        Gap(
                            (c.x - a.x2) / FTPX,
                            "H",
                            (a.x2 + c.x) / 2,
                            (yl + yr) / 2,
                            a.is_kura or c.is_kura,
                        )
                    )
    raw.sort(key=lambda gp: gp.ft, reverse=True)
    out: list[Gap] = []
    for gp in raw:
        if not any(abs(gp.mx - o.mx) < 15 and abs(gp.my - o.my) < 15 for o in out):
            out.append(gp)
    return out


def gap_tag(gap: Gap) -> str:
    """Heuristic label for an aligned gap (a kura keeps a fire-gap; wooden slack tightens)."""
    if gap.kura:
        return "fire-gap OK (kura)" if gap.ft <= 10 else "LOOSE (kura gap >10 ft)"
    return "tight" if gap.ft <= 8 else "LOOSE (wooden >8 ft)"
