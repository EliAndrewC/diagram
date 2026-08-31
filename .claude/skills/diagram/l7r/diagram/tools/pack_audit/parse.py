"""Split from tools/pack_audit.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import re
from dataclasses import dataclass

INTERIOR_FILL = "url(#court-earth)"
BUILDING_FILLS: frozenset[str] = frozenset({"#DDB87A", "#C9A57A", "#E8D2A8", "#F2EFE4", "#C9876C", "#B89868", "#8C6F3E", "#6B4030"})
BUILDING_PATTERNS: frozenset[str] = frozenset({"url(#granary-slats)", "url(#colonnade-hatch)"})
KURA_FILLS: frozenset[str] = frozenset({"#F2EFE4"})  # fireproof plaster kura: a fire-gap IS correct
OPEN_PATTERNS: frozenset[str] = frozenset({"url(#garden-stipple)", "url(#oshirasu-sand)", "url(#keiko-earth)"})
MIN_BLDG_AREA_PX: float = 500.0  # ~55 sqft; below this it is furniture, not a building mass. Lowered
# from 900 (2026-07-21): the glyph-doctrine retirement shrank real buildings to TRUE size - an 11x7 ft
# modest shrine is 693 px2 - and the old floor silently dropped them from coverage/adjacency, emitting
# a false "fire tub adrift" on Hayakawa (the tub sits 1.8 ft off the shrine the tool stopped seeing).

_RECT_RE = re.compile(r'<rect x="([\-\d.]+)" y="([\-\d.]+)" width="([\d.]+)" height="([\d.]+)"[^>]*?fill="([^"]+)"')
_CIRCLE_RE = re.compile(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"')
_ELLIPSE_RE = re.compile(r'<ellipse cx="([\d.]+)" cy="([\d.]+)" rx="([\d.]+)" ry="([\d.]+)"')
DIVIDER_STROKE = "#3F3A30"  # internal court-divider wall; buildings legitimately back it, so it
# counts as a "wall" for perimeter-hugging (a jin'ya's office hall backs the divider).
_DIV_GROUP_RE = re.compile(rf'<g stroke="{re.escape(DIVIDER_STROKE)}"[^>]*>(.*?)</g>', re.DOTALL)
_LINE_RE = re.compile(r'<line x1="([\-\d.]+)" y1="([\-\d.]+)" x2="([\-\d.]+)" y2="([\-\d.]+)"')
FIRE_WATER_FILL = "#8FB0C6"  # tensuioke (rain-water fire tubs). They are GUTTER-FED by roof runoff,
# so each must sit at a building's wall/eaves; a tub standing out in the open court is fed by nothing.
_TUB_GROUP_RE = re.compile(rf'<g fill="{re.escape(FIRE_WATER_FILL)}"[^>]*>(.*?)</g>', re.DOTALL)
# building. A tub is meant to stand ~1.7-2 ft OFF the wall, so unlike a wall-abutting structure it has
# no legitimate flush case - any real contact is a defect and this is a rounding floor, not a
# tolerance. Same 0.5 px floor as WALL_OVERLAP_MIN_PX and for the same reason: emit rounding and
# stroke width put sub-pixel ink over an edge that is geometrically clear.

# --- text labels (for the layer/legibility/proximity checks) ---
_TEXT_RE = re.compile(r"<text\s([^>]*)>(.*?)</text>", re.DOTALL)
_ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')
_INNER_TAG_RE = re.compile(r"<[^>]*>")
CHAR_W_FRAC: float = 0.55  # a serif glyph's advance width as a fraction of font-size (bbox estimate)
CHAR_W_BOLD: float = 0.72  # bold ALL-CAPS band labels (RESIDENCE, HEARING COURT) run widest
CHAR_W_BOLD_MIXED: float = 0.60  # ...but mixed-case bold (building names) is much narrower than caps.
# Measured 2026-07-25 by rendering real pool strings through resvg/DejaVu Serif and reading the ink
# extents: at 0.72 the all-caps band labels land at 0.95-0.99x of true width (right), while
# mixed-case bold came out 1.26-1.27x (way over). That 26% phantom width was enough to make the
# widened occlusion check report a FALSE positive on Ochiba - "Tatsuya's quarters" was estimated to
# run into the residence's connecting corridor when the real ink stops 7 px short of it. 0.60 lands
# mixed-case at 0.96-1.06x: still biased slightly LONG, which is the safe direction for a check that
# is looking for overlaps.
CAPS_RATIO: float = 0.8  # a label with >= this share of upper-case letters is a caps label
WELL_FILL = "#9C8C70"  # well-curb stone
WALL_STROKE = "#2D2A24"  # the compound wall (and gate posts / well-mouths share this dark ink)
_WALL_GROUP_RE = re.compile(rf'<g stroke="{re.escape(WALL_STROKE)}"[^>]*>(.*?)</g>', re.DOTALL)
# Fills dark enough that BLACK label ink laid over them stops being legible (luminance < ~0.30):
DARK_FILLS: frozenset[str] = frozenset({"#2D2A24", "#3A2010", "#3A2418", "#1A1410", "#4A3318", "#5C0A04", "#3A2E1C", "#6B4030", "#5A3F1E", "#5C1A0A"})
MIN_DARK_AREA_PX: float = 150.0  # ignore tiny dark markers (kura door, altar square) - only a real dark BLOCK or wall hurts legibility
# The occlusion check is deliberately fill-BLIND on the occluder side: ANY rect or glyph drawn later
# counts, not just the fills this tool happens to classify as a building or a garden. Enumerating
# occluders by fill is what let two real defects through (2026-07-25) - a note box (an unclassified
# solid fill) painted over the bounty bill, and a NEW pattern (url(#cart-gravel), unknown to
# OPEN_PATTERNS) painted over a privy. A palette grows; "drawn later, covers it" does not.
FURNITURE_MAX_AREA_PX: float = MIN_BLDG_AREA_PX  # a rect below the building floor is furniture
DOOR_MAX_AREA_PX: float = 250.0  # a door glyph is small (a kura door); bigger dark rects are hearths/blocks

# --- structures vs wall ink (a structure may ABUT a wall, never occupy it) ---
# Every roofed/built footprint color, with NO area floor: the motivating defect was a 26x8 px
# ENTRY PORCH laid across Ochiba's court divider (GM caught it, 2026-07-24), and the
# MIN_BLDG_AREA_PX floor that keeps furniture out of the coverage math would have hidden it.
# Porches, sheds and privies are small but they are still built things standing on the ground.
UTILITY_FILLS: frozenset[str] = frozenset({"#7E726A", WELL_FILL})  # privies/sheds + well curbs
STRUCTURE_FILLS: frozenset[str] = BUILDING_FILLS | BUILDING_PATTERNS | UTILITY_FILLS
# Why UTILITY_FILLS had to be added (2026-07-25): the comment above already said privies count, but
# the fill list did not contain the privy color, so all 23 utility rects in the pool went
# unchecked - documented intent and implementation had silently drifted apart.
#
# And why this list stays ENUMERATED, where the occlusion check went deliberately fill-blind: the
# two rules have opposite defaults. NOTHING may legitimately bury a foreground item, so there the
# safe rule is "any later shape counts". But plenty of things legitimately occupy wall ink - gate
# posts flank an opening, threshold and boundary stones mark a crossing, salt wards flank a door -
# so "anything that is not ground" would flag every one of them. A structure is a ROOFED, standing
# thing, and that has to be named rather than inferred.
WALL_KIND: dict[str, str] = {WALL_STROKE: "compound wall", DIVIDER_STROKE: "court divider"}


@dataclass(frozen=True)
class Rect:
    """An axis-aligned rectangle in SVG pixel space."""

    x: float
    y: float
    w: float
    h: float
    fill: str = ""
    pos: int = -1  # byte offset in the source SVG (document/draw order; higher = drawn later, on top)

    @property
    def x2(self) -> float:
        return self.x + self.w

    @property
    def y2(self) -> float:
        return self.y + self.h

    @property
    def area_px(self) -> float:
        return self.w * self.h

    @property
    def is_kura(self) -> bool:
        return self.fill in KURA_FILLS


@dataclass(frozen=True)
class Label:
    """A text label with an ESTIMATED bounding box (px) and its draw-order position."""

    x: float  # bbox top-left
    y: float
    w: float
    h: float
    fill: str
    text: str
    pos: int  # byte offset in the source SVG (draw order)

    @property
    def x2(self) -> float:
        return self.x + self.w

    @property
    def y2(self) -> float:
        return self.y + self.h

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


def _luma(fill: str) -> float:
    """Relative luminance (0=black, 1=white) of a #rrggbb fill; 1.0 for anything non-hex."""
    if not (len(fill) == 7 and fill.startswith("#")):
        return 1.0
    r, g, b = (int(fill[i : i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


@dataclass(frozen=True)
class ParsedPlan:
    """Classified geometry of one compound plan."""

    interior: tuple[Rect, ...]
    buildings: tuple[Rect, ...]
    open_features: tuple[Rect, ...]
    glyphs: tuple[Rect, ...]
    dividers: tuple[Rect, ...] = ()  # internal divider walls, as thin rects
    tubs: tuple[Rect, ...] = ()  # fire-water tubs (bbox of each), to check wall-adjacency
    labels: tuple[Label, ...] = ()  # text labels with estimated bboxes + draw order
    wall_segs: tuple[Rect, ...] = ()  # compound-wall line segments (thin rects), for gate openings
    wells: tuple[Rect, ...] = ()  # well-curb rects, for the 'well' group-label proximity check
    dark_rects: tuple[Rect, ...] = ()  # dark-filled rects, for the black-on-black legibility check
    door_rects: tuple[Rect, ...] = ()  # small dark rects (door glyphs), for the door-on-a-wall check
    wall_bands: tuple[Rect, ...] = ()  # the INKED band of each wall/divider stroke (`fill` = its stroke color)
    structures: tuple[Rect, ...] = ()  # every built footprint, NO area floor (porches/sheds count)
    fills: tuple[Rect, ...] = ()  # every drawn rect (any fill) - the fill-blind occluder set
    furniture: tuple[Rect, ...] = ()  # sub-building rects (privy, door, board, mat): foreground

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        minx = min(r.x for r in self.interior)
        miny = min(r.y for r in self.interior)
        maxx = max(r.x2 for r in self.interior)
        maxy = max(r.y2 for r in self.interior)
        return minx, miny, maxx, maxy


def _bold_char_w(text: str) -> float:
    """Per-character advance for BOLD text: caps labels run wider than mixed-case ones."""
    letters = [c for c in text if c.isalpha()]
    caps = sum(c.isupper() for c in letters) / len(letters) if letters else 0.0
    return CHAR_W_BOLD if caps >= CAPS_RATIO else CHAR_W_BOLD_MIXED


def _parse_labels(text: str) -> list[Label]:
    """Text labels with an estimated bbox (from font-size x string length) + draw-order pos."""
    out: list[Label] = []
    for m in _TEXT_RE.finditer(text):
        attrs = dict(_ATTR_RE.findall(m.group(1)))
        content = _INNER_TAG_RE.sub("", m.group(2)).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").strip()
        if not content or "x" not in attrs or "y" not in attrs:
            continue
        x, y = float(attrs["x"]), float(attrs["y"])
        fs = float(attrs.get("font-size", "13"))
        ls = float(attrs.get("letter-spacing", "0"))
        n = len(content)
        frac = _bold_char_w(content) if attrs.get("font-weight") == "bold" else CHAR_W_FRAC
        w = n * fs * frac + ls * max(n - 1, 0)
        anchor = attrs.get("text-anchor", "start")
        left = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
        out.append(Label(left, y - fs * 0.78, w, fs, attrs.get("fill", "#000000"), content, m.start()))
    return out


_ELEM_RE = re.compile(r"<(/?)(g|line)\b([^>]*?)/?>")


def _wall_bands(text: str) -> list[Rect]:
    """The INKED band of every wall / court-divider stroke, as an axis-aligned rect.

    Handles both authoring forms present in the pool - a `<g stroke=... stroke-width=...>`
    wrapping bare `<line>`s (the hand-authored plans) and stand-alone `<line stroke=...
    stroke-width=.../>` (compound.py's emitter) - by tracking `<g>` attribute inheritance, so a
    plan drawn either way is checked rather than silently skipped.

    Parsed separately from `wall_segs` on purpose: those stay CENTERLINE segments because
    `_gate_openings` measures the gaps BETWEEN them, and widening them by the stroke would shrink
    every measured opening by a stroke width. `fill` carries the stroke color so the report can
    name which barrier was hit. Mode A walls are axis-aligned, so a run is classified by its
    longer axis; a `stroke-linecap="square"` run also inks half a stroke past each endpoint.
    """
    stack: list[dict[str, str]] = []
    out: list[Rect] = []
    for m in _ELEM_RE.finditer(text):
        closing, name, attrs = m.group(1), m.group(2), m.group(3)
        if name == "g":
            if not closing:
                stack.append(dict(_ATTR_RE.findall(attrs)))
            elif stack:
                stack.pop()
            continue
        d: dict[str, str] = {}
        for frame in stack:
            d.update(frame)
        d.update(dict(_ATTR_RE.findall(attrs)))
        stroke = d.get("stroke", "")
        if stroke not in WALL_KIND or "x1" not in d:
            continue
        sw = float(d.get("stroke-width", "1"))
        hw = sw / 2
        cap = hw if d.get("stroke-linecap") == "square" else 0.0
        x1, y1, x2, y2 = (float(d[k]) for k in ("x1", "y1", "x2", "y2"))
        if abs(y2 - y1) <= abs(x2 - x1):  # horizontal run
            out.append(Rect(min(x1, x2) - cap, min(y1, y2) - hw, abs(x2 - x1) + 2 * cap, sw, stroke, m.start()))
        else:
            out.append(Rect(min(x1, x2) - hw, min(y1, y2) - cap, sw, abs(y2 - y1) + 2 * cap, stroke, m.start()))
    return out


def parse_svg(text: str) -> ParsedPlan:
    """Parse an SVG into interior / building / open-feature / point-glyph rects + labels + walls."""
    rects = [Rect(float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5), m.start()) for m in _RECT_RE.finditer(text)]
    interior = tuple(r for r in rects if r.fill == INTERIOR_FILL)
    if not interior:
        raise ValueError("no court-earth interior rect found in the SVG")
    buildings = tuple(r for r in rects if (r.fill in BUILDING_FILLS or r.fill in BUILDING_PATTERNS) and r.area_px >= MIN_BLDG_AREA_PX)
    open_features = tuple(r for r in rects if r.fill in OPEN_PATTERNS)
    glyphs: list[Rect] = []
    for c in _CIRCLE_RE.finditer(text):
        cx, cy, rad = float(c.group(1)), float(c.group(2)), float(c.group(3))
        if rad >= 4.0:
            glyphs.append(Rect(cx - rad, cy - rad, 2 * rad, 2 * rad, "", c.start()))
    for e in _ELLIPSE_RE.finditer(text):
        ex, ey, rx, ry = float(e.group(1)), float(e.group(2)), float(e.group(3)), float(e.group(4))
        glyphs.append(Rect(ex - rx, ey - ry, 2 * rx, 2 * ry, "", e.start()))
    dividers: list[Rect] = []
    for grp in _DIV_GROUP_RE.finditer(text):
        for ln in _LINE_RE.finditer(grp.group(1)):
            x1, y1, x2, y2 = (float(ln.group(i)) for i in range(1, 5))
            dividers.append(Rect(min(x1, x2), min(y1, y2), max(abs(x2 - x1), 2.0), max(abs(y2 - y1), 2.0)))
    tubs: list[Rect] = []
    for grp in _TUB_GROUP_RE.finditer(text):
        for c in _CIRCLE_RE.finditer(grp.group(1)):
            cx, cy, rad = float(c.group(1)), float(c.group(2)), float(c.group(3))
            tubs.append(Rect(cx - rad, cy - rad, 2 * rad, 2 * rad, FIRE_WATER_FILL, grp.start() + c.start()))
    wall_segs: list[Rect] = []
    for grp in _WALL_GROUP_RE.finditer(text):
        for ln in _LINE_RE.finditer(grp.group(1)):
            x1, y1, x2, y2 = (float(ln.group(i)) for i in range(1, 5))
            wall_segs.append(Rect(min(x1, x2), min(y1, y2), max(abs(x2 - x1), 2.0), max(abs(y2 - y1), 2.0)))
    wells = tuple(r for r in rects if r.fill == WELL_FILL)
    fills = tuple(r for r in rects if r.fill != INTERIOR_FILL)
    furniture = tuple(r for r in fills if r.area_px < FURNITURE_MAX_AREA_PX)
    dark_rects = tuple(r for r in rects if r.fill in DARK_FILLS and r.area_px >= MIN_DARK_AREA_PX)
    door_rects = tuple(r for r in rects if r.fill in DARK_FILLS and r.area_px < DOOR_MAX_AREA_PX)
    return ParsedPlan(
        interior,
        buildings,
        open_features,
        tuple(glyphs),
        tuple(dividers),
        tuple(tubs),
        tuple(_parse_labels(text)),
        tuple(wall_segs),
        wells,
        dark_rects,
        door_rects,
        tuple(_wall_bands(text)),
        tuple(r for r in rects if r.fill in STRUCTURE_FILLS),
        fills=fills,
        furniture=furniture,
    )
