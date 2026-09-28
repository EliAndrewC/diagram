"""compound_model.py - the compound PROGRAM's vocabulary: its units, its palettes, the feet-first program types and
the placed result (split out of `compound.py`, feature 267, when the draft's gates, doors and roji took it past the
1,000-line bar). `compound.py` places and emits; `compound_parts.py` seats the point features and the parts of the
house. Every name here is re-exported by `compound.py`, the module the pool generators import.
"""

from __future__ import annotations

from dataclasses import dataclass, field

FTPX: float = 3.0  # 3 px = 1 ft (emit-time only)
FIRE_GAP_FT: float = 7.0  # default gap between hugging buildings (a real fire-gap)
WALL_MARGIN_FT: float = 3.0  # a building's inset from the very corner / wall stroke
# A wall is a built object with real thickness, drawn to scale and CENTERED on the boundary it
# marks - so half of it stands inside the interior, and ground the wall occupies is not ground a
# building can stand on. A hugging building therefore abuts the wall's INNER FACE (inset by half
# the wall's thickness), never the raw boundary. Placing at the boundary drew every wall-ranging
# building 1.5 ft inside the masonry, and since the wall is painted last it ate their outlines
# (GM caught the hand-authored version of this on Ochiba, 2026-07-24; the check that now guards
# it is pack_audit.structures_on_walls, and buildings.md "Walls and gates" carries the rule).
WALL_INK_FT: float = 3.0  # compound wall: 9 px at 3 px = 1 ft
DIVIDER_INK_FT: float = 2.0  # internal court divider: 6 px
OUTLINE_CLEAR_FT: float = 0.5  # a hair beyond the ink, so the wall does not swallow the BUILDING'S
# own outline stroke (a rect drawn exactly flush loses its edge under the wall and reads as merging
# into it). 0.5 ft matches the gap the hand-authored Ochiba leaves between its servants' quarters
# and the north wall - the house style this rule was reverse-engineered from.

# palette keys -> (fill, stroke) reused from the Mode A vocabulary (SKILL.md)
KINDS: dict[str, tuple[str, str]] = {
    "lord": ("#DDB87A", "#5A3F1E"),
    "service": ("#C9A57A", "#6B4F2A"),
    "plain": ("#E8D2A8", "#6B4F2A"),
    "kura": ("#F2EFE4", "#4A3318"),
    "shrine": ("#C9876C", "#6B2A18"),
    "cell": ("#B89868", "#5C4318"),
    "dark": ("#8C6F3E", "#4A3318"),
}
COURT_FILL: dict[str, str] = {
    "forecourt": "url(#court-earth)",
    "oshirasu": "url(#oshirasu-sand)",
    "garden": "url(#garden-stipple)",
    "yard": "url(#court-earth)",
    "cart yard": "url(#court-earth)",
    "vegetable garden": "url(#garden-stipple)",  # the hand sheets' fill for it, a planted open ground to the audit (pass 7)
    "inner yard": "url(#court-earth)",
    "practice ground": "url(#keiko-earth)",  # swept keiko earth (buildings.md "Practice ground")
}
# A court that is ROOFED is drawn with a building's solid outline (stroke, width) and posts along its open side
# (feature 267 R22, research buildings 450 'Was the hearing court open white sand, or roofed?': a magistracy's court
# was roofed or an indoor gravel floor - the open-air white court is the period-drama image). Every other zone keeps
# the thin open-ground edge.
ROOFED_ZONES: dict[str, tuple[str, float]] = {"oshirasu": ("#5A3F1E", 2.0)}
# The posts' spacing along the roofed court's open (south) side: one bay of two ken (~12 ft) between posts. A GUESS -
# no roofed court's measurements were found (buildings.md "Hearing court"); two ken is a common bay for an open
# post-and-beam front. Each post is drawn 1 ft square, at true size.
ROOF_POST_BAY_FT: float = 12.0
ROOF_POST_FT: float = 1.0
# The covered corridor joining the kitchen to the residence (feature 267, research buildings 360/370: the kitchen is
# part of the HOUSE, joined as an ell or by a short covered corridor, never a freestanding cookhouse; buildings.md
# "Kitchen + pantries"). Its width, one ken (~6 ft), is a GUESS; it is drawn only across a gap no wider than a
# fire-gap - a longer run would be a gallery, not the short corridor the research describes.
CORRIDOR_W_FT: float = 6.0
# The bath (feature 267 R09, research buildings 320: a room of the residence or a small addition to it on its
# service side, by the kitchen and its well - no bath as a building of its own was found). 10 x 8 ft (pass 6: the whole
# house is held to research buildings 380's 49-tsubo house, ~1,740 sq ft; it was 15 x 12, then 12 x 10) - below the
# doctrine's 12-15 ft guess, a GUESS.
BATH_W_FT, BATH_H_FT = 10.0, 8.0
# The gates' posts (feature 267 R26, research buildings 480 'How wide was the main gate?'). Each post is drawn over the
# cut end of the wall it closes, so the wall's opening IS the passage the audit measures between the posts
# (`pack_audit.main_gate_passage_ft`). 4 x 14 px (1.33 x 4.67 ft) is a MAP DRAWING CONVENTION: the post block stands
# for the gate's pillar with the wall end it caps, drawn proud of the 3 ft wall so it reads as a post, not a true-size
# pillar (a yakuimon's pillars are about 1 ft).
GATE_POST_W_FT, GATE_POST_D_FT = 4.0 / 3.0, 14.0 / 3.0
# The middle gate's (nakamon's) posts on the 2 ft divider: 4 x 10 px, the same convention at the divider's scale.
NAKAMON_POST_D_FT = 10.0 / 3.0
# An informal door on each lodging block (feature 267, buildings/programs.md: no sealed boxes): a small dark rect set
# flush inside the building's face, as the hand sheets draw one (`floating_doors` holds it to the wall). 6 ft along the
# face is a MAP DRAWING CONVENTION (research buildings 620 'How wide was a real doorway, and how wide are the drawn
# doors?': an ordinary door is about half a ken, ~3 ft; drawn doors run two to three times that to read at 3 px/ft);
# 1.33 ft deep is the ink the hand sheets give one.
DOOR_W_FT, DOOR_D_FT = 6.0, 4.0 / 3.0
# The kinds given a door. The kitchen's is its one outside door, the service entrance on its earth floor (research
# buildings 370); the residence's is the household's inner entrance, apart from the kitchen's (370 again) - the guest's
# way is the middle gate and the roji to the reception's veranda (R07, research buildings 300), so the residence
# carries no genkan. The stables, the kura and the shrine carry theirs too (pass 5, building-review round 4: a building
# with no drawn door reads as sealed). `BuildingSpec.door_face` sets the face a door goes on; the court face otherwise.
DOOR_KINDS: frozenset[str] = frozenset(
    {
        "office hall",
        "stables",
        "granary",
        "tax archive",
        "compound shrine",
        "residence",
        "kitchen",
        "karo's house",
        "guest quarters",
        "retainers' quarters",
        "barracks",
        "servants' quarters",
        "gatehouse",
    }
)
# The fracs along a face a door is tried at, the middle first: a tub or a well holds a face's ends or middle.
DOOR_FRACS: tuple[float, ...] = (0.5, 0.3, 0.7, 0.2, 0.8, 0.1, 0.9)
# The stepping stones of the roji from the middle gate to the reception's veranda (R07): one stone every 4.5 ft, each
# ~2 x 1.33 ft, and the shoe stone (kutsunugi-ishi) at the veranda 4 x 1.67 ft - the spacing and sizes a GUESS, drawn
# as Hayakawa draws its roji.
STONE_STEP_FT: float = 4.5
# A privy (latrine) is drawn 5 ft square, a one-seat outhouse (the size the drafts have always drawn; a GUESS). One stands
# no nearer a well than LATRINE_WELL_FT: 15 ft is a GUESS - no separation distance was read; the hand sheets' reviews
# moved a stable-yard privy ~27 ft off its well (Ubame, 2026-07-25), and the draft's stood 5 ft from its well.
PRIVY_FT: float = 5.0
LATRINE_WELL_FT: float = 15.0


@dataclass(frozen=True)
class Envelope:
    """The walled interior, in feet. Inner (residence) court is north (y small); outer
    (administrative) court is south (y large), with the main gate on the south wall."""

    w_ft: float
    h_ft: float
    divider_ft: float  # y of the inner/outer court divider
    gate_w_ft: float = 13.0  # main-gate PASSAGE width (on the south wall, centered; the posts stand on the cut wall ends)
    # The middle gate (nakamon) in the divider: its passage, narrower than the main gate (buildings/programs.md "Two-court
    # zoning": a household door, ~6-8 ft; the audit's `two_court_zoning` requires one). 6 ft is Ochiba's; 0 draws none.
    middle_gate_w_ft: float = 6.0
    # The lesser gates in the compound wall: (wall "N"|"S"|"E"|"W", its center along that wall in ft, its passage in ft)
    # each - the kitchen postern that keeps deliveries and night-soil off the hearing court, and the outer court's
    # service gate for muck and prisoners (buildings/programs.md "Walled enclosure").
    posterns: tuple[tuple[str, float, float], ...] = ()


@dataclass(frozen=True)
class CourtZone:
    """A reserved OPEN court in the spine (buildings never overlap it)."""

    name: str
    x_ft: float
    y_ft: float
    w_ft: float
    h_ft: float

    @property
    def x2(self) -> float:
        return self.x_ft + self.w_ft

    @property
    def y2(self) -> float:
        return self.y_ft + self.h_ft


@dataclass(frozen=True)
class BuildingSpec:
    """A building sized in feet with a placement tag."""

    name: str
    kind: str
    w_ft: float
    h_ft: float
    court: str  # "outer" | "inner"
    wall: str  # "N" | "S" | "E" | "W" | "divider"
    order: int = 0  # higher places first (largest/most-important win a contested corner)
    rank: int = 1  # 1 = hug the wall; 2 = sit as a second rank BEHIND the rank-1 row
    # The Mode A KIND the building is (feature 262): the `data-kind` the emitter writes on it, a key of the
    # registry in `interactive/compound/`, so the draft's interactive page knows what it drew. `emit_svg`
    # refuses a building without one, naming it - a draft with an unkinded building would be a page with
    # ink nobody ruled on.
    feature: str = ""
    # ROOMS OF THE BUILDING (feature 267): (kind, x_off, y_off, w_ft, h_ft) floors drawn INSIDE it, offset from its NW
    # corner, the way the hand sheets draw a room (feature 264): the building's fill, one same-color floor per room
    # tagged with the room's kind, then the building's outline on top - so the page files the room as a part of the
    # building. A room is never placed; it takes ground its building already holds. Positioned rather than run in one
    # row since pass 4, so a house can be massed in two rows front and back (the one-room-deep bar was the review's).
    rooms: tuple[tuple[str, float, float, float, float], ...] = ()
    # The magistrate's DAIS (w_ft, d_ft): a band flush inside the court face, centered on the building - the office
    # hall's front band overlooking the hearing court (buildings/programs.md "The office hall is the compound's working
    # heart"; buildings.md "Office hall (with dais band)"). (0, 0): none.
    dais: tuple[float, float] = (0.0, 0.0)
    # Stand this many feet further off its wall than the wall's ink requires: the residence's rear alley (research
    # buildings 230 'The shady rear is the service strip': the north band narrowed to a ~6-10 ft cart/servant alley).
    inset_ft: float = 0.0
    # A VERANDA (engawa) along the building's court face, this deep, drawn inside its footprint as a part of it
    # (feature 267 R01: the veranda runs along the garden face; 3-6 ft). 0: none.
    engawa_ft: float = 0.0
    # Stand BESIDE the main gate - flush west of its post on the south wall - rather than slide from the corner: the
    # freestanding gatehouse by the gate, Takayama's form (feature 267 R19, research buildings 420).
    beside_gate: bool = False
    # The face its door goes on ("N"|"S"|"E"|"W"), when not the court face: the residence's inner entrance opens on the
    # kitchen side, off the garden its veranda faces (research buildings 370).
    door_face: str = ""
    # More doors, on these faces (pass 6: the office hall's front room and its west end had none), and the fracs along
    # a face a door is tried at when not DOOR_FRACS
    extra_doors: tuple[str, ...] = ()
    door_fracs: tuple[float, ...] = ()


@dataclass(frozen=True)
class CompoundProgram:
    title: str
    envelope: Envelope
    spine: tuple[CourtZone, ...] = ()
    buildings: tuple[BuildingSpec, ...] = ()


@dataclass(frozen=True)
class Placed:
    """A building assigned a feet position (top-left)."""

    spec: BuildingSpec
    x_ft: float
    y_ft: float

    @property
    def x2(self) -> float:
        return self.x_ft + self.spec.w_ft

    @property
    def y2(self) -> float:
        return self.y_ft + self.spec.h_ft


@dataclass
class PlaceResult:
    placed: list[Placed] = field(default_factory=list)
    overflow: list[BuildingSpec] = field(default_factory=list)  # did not fit the ring


def _gate_interval(env: Envelope) -> tuple[float, float]:
    half = env.gate_w_ft / 2
    return (env.w_ft / 2 - half, env.w_ft / 2 + half)


def _kind_attr(kind: str) -> str:
    return f' data-kind="{kind}"' if kind else ""
