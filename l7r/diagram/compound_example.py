"""The built-in county-magistracy example's PROGRAM (feature 374 wave 125 split it from `compound.py`, which passed the
1,000-line bar when the example's outer court was recomposed): the feet-first declaration the placer in `compound.py`
lays out - its envelope, the reserved court spine and the buildings, each with the research its size and wall rest on.
`compound.county_magistracy_program` is this function, re-exported; the pool generator and the tests call it there."""

from __future__ import annotations

import random
import zlib

from .buildings.types import load_types
from .compound_model import FIRE_GAP_FT, BuildingSpec, CompoundProgram, CourtZone, Envelope
from .compound_parts import SHRINE_TREE_CLEAR_FT, SHRINE_TREE_CROWN_FT

# The built-in example's pool tier: the type that declares the example as its generated exception
# (feature 254) - the folder is the declaration's to name, not this module's.
_EXAMPLE_TIER: str = next(t.tier for t in load_types() if "county-magistracy-example" in t.generated_exceptions)


#: The two entry forms of a servants' range (research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html, a knob
#: set per compound), and this draft's roll of it, keyed as Ochiba's sheet keys its own (feature 374 batch 4).
SERVANTS_FORMS: tuple[str, str] = ("common room under one door", "a door to each dwelling")
SERVANTS_FORM: str = random.Random(zlib.crc32(b"county-magistracy-example:servants' quarters form")).choice(SERVANTS_FORMS)


#: The granary's two forms (research/questions/0098-storehouses-for-the-tax-rice.drawing.html: "A granary takes one of two forms, a knob"), the kind
#: each draws as, and this draft's roll.
#: The forms in the record's order ("Either a timber storehouse raised on posts, the takakura, or an earth-walled kura"), the
#: key the knob's name: the roll is fixed by the record's wording, never chosen after the result (T20's plan review).
GRANARY_FORMS: tuple[str, str] = ("raised timber storehouse", "earth-walled kura")
GRANARY_KIND: dict[str, str] = {"earth-walled kura": "kura", "raised timber storehouse": "takakura"}
GRANARY_FORM: str = random.Random(zlib.crc32(b"county-magistracy-example:granary form")).choice(GRANARY_FORMS)


#: The main gate's two forms in the record's order ("a one-bay gate or a gate range (nagaya-mon), a knob chosen for each
#: plan", research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.drawing.html), each form's drawn opening (a
#: one-bay gate ~6-8.5 ft, a nagaya-mon's two ken), and this draft's roll. The gatekeepers' place follows from the form: a
#: one-bay gate has no range to hold a guardroom, so they sit in a gatehouse of their own (T20's plan review).
GATE_FORMS: tuple[str, str] = ("one-bay gate", "gate range")
#: The one-bay gate's frontage and its pillar (feature 374 wave 132): research/questions/0093-the-main-gate-and-its-gatekeepers-
#: nagaya-mon.html measures a yakuimon's 間口 (frontage) at 1.8-2.6 m, read as the span between its pillar centers (a bay is
#: counted between post centers), so the real passage is the frontage less ONE pillar; no yakuimon pillar was found measured, so
#: ~1 ft is a GUESS. This draft takes an 8 ft frontage. The drawn ~2 ft posts are a convention outside the real passage.
YAKUIMON_FRONTAGE_FT: float = 8.0
"""Research: one-bay gate frontage - research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.drawing.html: a one-bay gate is drawn about 6 to 8.5 ft wide, the frontage of the three registered examples taken between pillar centers; this draft takes 8 ft."""
YAKUIMON_PILLAR_FT: float = 1.0
"""Research: one-bay gate pillar - GUESS research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.drawing.html: the passage is the frontage less one pillar of about 1 ft, a guess because no page measures a one-bay gate's pillar."""
GATE_W_FT: dict[str, float] = {"one-bay gate": YAKUIMON_FRONTAGE_FT - YAKUIMON_PILLAR_FT, "gate range": 12.0}
GATE_FORM: str = random.Random(zlib.crc32(b"county-magistracy-example:main gate form")).choice(GATE_FORMS)


#: 0109's four sites for a vegetable garden, in the record's order (research/questions/0109-vegetable-gardens-at-a-samurai-
#: residence-saien.drawing.html: "A garden's site is a knob among four"), and what rules each out on this draft - the sun
#: or the room, measured on the draft (feature 374 wave 129) - None where it is open; the roll is among the open ones.
GARDEN_SITES: tuple[str, ...] = ("west of the residence", "south, beside the formal garden", "in the rear service ground", "on a parcel of its own")
GARDEN_SITE_RULED_OUT: dict[str, str | None] = {
    "west of the residence": None,  # the kitchen yard: 9.5 h of sun (garden_sun), room for the plot
    "south, beside the formal garden": "no room: 8 ft between the formal garden (to y 82) and the divider (y 90)",
    "in the rear service ground": "no room and no sun: a 9-12 ft band behind the house, the storehouses on it, in the house's shadow",
    "on a parcel of its own": None,  # outside the walls: the plan draws the field nowhere, its notes say where it is
}
GARDEN_SITE: str = random.Random(zlib.crc32(b"county-magistracy-example:vegetable garden site")).choice([site for site in GARDEN_SITES if GARDEN_SITE_RULED_OUT[site] is None])
#: The plot's size: the low form of 0109's size knob, the Takei house's soup-greens plot of ~100 sq m (~1,076 sq ft), drawn
#: 36 x 30 ft (1,080 sq ft). The field form, over about half the grounds (~27,000 of 54,000 sq ft), cannot stand in an
#: inner court of 24,300 sq ft before anything is built in it, so the room rules it out (T21's plan review).
GARDEN_PLOT_FT: tuple[float, float] = (36.0, 30.0)
"""Research: vegetable garden plot - research/questions/0109-vegetable-gardens-at-a-samurai-residence-saien.drawing.html: the low form of the garden size knob is a soup-greens plot of about 100 sq m (~1,076 sq ft), drawn 36 x 30 ft (1,080 sq ft)."""


def garden_zones(site: str) -> tuple[CourtZone, ...]:
    """The vegetable garden as the site rolled draws it: the plot in the kitchen yard west of the house with the yard's
    working ground beside the kitchen named, or - on a parcel of its own - no plot inside the walls, the yard whole.

    Research:
        its unstated figures - GUESS: searched, the record silent (feature 417 T38 pass N13, 2026-10-25) - 14 (whole kitchen yard when the plot is off-site); 25 (whole kitchen yard when the plot is off-site); 66 (whole kitchen yard when the plot is off-site); 62 (whole kitchen yard when the plot is off-site); 54 (service yard's bounds by the kitchen); 26 (service yard's bounds by the kitchen)
        its figures guessed on 0109 - GUESS research/questions/0109-vegetable-gardens-at-a-samurai-residence-saien.drawing.html: 40 (plot's corner in the kitchen yard (site cited, place in it ours))
    """
    if site == "west of the residence":
        return (CourtZone("vegetable garden", 14.0, 40.0, *GARDEN_PLOT_FT), CourtZone("service yard", 54.0, 25.0, 26.0, 62.0))
    return (CourtZone("service yard", 14.0, 25.0, 66.0, 62.0),)


def servants_row(form: str) -> BuildingSpec:
    """The county draft's servants' row on the street (south) wall, 60 x 15 ft (a GUESS), in the entry form rolled: four
    dwellings of 15 ft each with its door, or one common room behind one door (0097's two forms). 60 ft since feature 374
    wave 128 (it was 76): the 40 ft gatehouse beside the gate takes the wall's room, and the stable keeps its seat west of it.

    Research:
        its figures of ours - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 60 (common-room form's size); 15 (common-room form's size); 0.375 (door at each 15 ft dwelling's middle); 0.625 (door at each 15 ft dwelling's middle); 0.875 (door at each 15 ft dwelling's middle); 30 (walls of four 15 ft dwellings (claim stale: five)); 45 (walls of four 15 ft dwellings (claim stale: five))
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N13, 2026-10-25) - 6 (placement order)
        its unstated figures - GUESS: searched, the record silent (feature 417 T38 pass N13, 2026-10-25) - 0.17 (west door moved off its middle for the privy)
    """
    if form == SERVANTS_FORMS[1]:
        return BuildingSpec(
            "servants' row",
            "service",
            60.0,
            15.0,
            "outer",
            "S",
            6,
            feature="servants' quarters",
            extra_doors=("N", "N", "N"),
            door_fracs=(0.17, 0.375, 0.625, 0.875),  # the west door off its middle: there its approach met the servants' privy
            bays=(15.0, 30.0, 45.0),
        )
    return BuildingSpec("servants' row", "service", 60.0, 15.0, "outer", "S", 6, feature="servants' quarters", door_fracs=(0.5,))


def county_magistracy_program() -> CompoundProgram:
    """A generic county magistracy declared entirely in feet (the placer composes it).

    Building masses are sized to land in the ~30-42% jin'ya coverage band (real jin'ya
    consolidate into a few large masses); the spine (garden -> oshirasu -> forecourt, plus
    the practice ground beside the barracks) sits clear of the wall rows so the placer never
    has to overlap it.

    Research:
        tax archive size - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: a 24 x 18 ft kura (432 sq ft), under the ~450 sq ft records-store ceiling, its shape a GUESS
        barracks size - research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html: a 23 x 70 ft range along the east wall, 23 ft deep, long and narrow, never squat; its length a GUESS within ~145 ft
        envelope - GUESS research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: a 270 x 200 ft walled compound, the divider at 90 ft, its buildings in the ~30-42% coverage band; the size a GUESS
        gates - research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.drawing.html: the main gate's form rolled from the record's two (GATE_FORM: a one-bay gate, an 8 ft frontage in the yakuimon's ~6-8.5 ft, read as its pillar-center span); the west kitchen postern and the south service gate 6 ft each, narrower, a GUESS
        one-bay gate passage - GUESS research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.drawing.html: the frontage less one ~1 ft pillar, 7 ft; no yakuimon pillar was found measured
        garden before the house - GUESS research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.drawing.html: the garden on the sunny south before the reception and the guest house; its 124 x 46 ft a GUESS
        vegetable garden site - research/questions/0109-vegetable-gardens-at-a-samurai-residence-saien.drawing.html: the site rolled among 0109's four, those the sun or the room rule out on this draft struck first (GARDEN_SITE: west of the residence)
        vegetable garden size - research/questions/0109-vegetable-gardens-at-a-samurai-residence-saien.html: the soup-greens plot of ~1,076 sq ft (36 x 30 ft), the field form ruled out by the room
        service yard - GUESS: the kitchen yard's working ground beside the kitchen, named as Ochiba's sheet names its own; no page records a kitchen yard's use, and its bounds are a drawing convention
        rear yard - research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.drawing.html: open working ground behind the house with the storehouses beyond it, as the Higuchi house kept; its bounds a drawing convention
        hearing court - GUESS research/questions/0099-the-hearing-court-shirasu.drawing.html: before the dais, centered on the office hall and no longer than it, 80 x 26 ft; no roofed court's size was found
        forecourt - GUESS research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.drawing.html: open ground just inside the main gate, east of the gatehouse; its 55 x 31 ft a GUESS
        practice ground - research/questions/0165-martial-training-grounds-and-dojo.drawing.html: a swept patch beside the barracks, 33 x 42 ft
        outer yard - CONVENTION: named open ground between the hearing court and the practice ground, its bounds a drawing convention
        cart yard - GUESS research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: the loading ground before the service gate, carts, the stable's muck and the prisoners' way out, 37 x 20 ft, the apron's ~15-20 ft
        residence form and size - research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.drawing.html, research/questions/0102-verandas-and-storm-shutters-engawa-and-amado.drawing.html: one block in two rows, the reception at the east end, a 4 ft veranda on the garden face, 10 ft off the north wall; 56 x 24 ft, with the kitchen and the bath ~50 tsubo, the Yokota house's 49
        residence room sizes - GUESS: the maids' room, the inner rooms, the family's and the lord's quarters and the reception at 10 x 10, 26 x 10, 18 x 10, 18 x 10 and 20 x 20 ft
        storehouses - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html, research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.drawing.html: two household storehouses behind the house, unequal as the Yokota pair - 16 x 19 ft and the common 12 x 18 ft (two by three ken); the count and the sizes GUESSES
        kitchen ell - research/questions/0107-kitchens-daidokoro.drawing.html, research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.html, research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.drawing.html: a 20 x 18 ft kitchen joined to the house's west end as an ell, its door west; its size a GUESS
        shrine - research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html: one modest shrine, 18 x 14 ft, on the inner court's east wall; its size a GUESS
        guest house - GUESS research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.drawing.html: a detached 40 x 42 ft guest house (42 since feature 374 wave 134 holds the coverage band); a guest house apart was not found at a samurai house
        shrine tree ground - research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html: the shrine's corner holds the ground for the tree beside it, the next building on its wall flowing below the crown
        shrine tree ground's size - GUESS: the 20 ft crown and 2 ft clear either side, less the fire-gap the next building keeps (tree_ft); no source sizes a household god's tree
        kitchen off the north wall - research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.drawing.html: the kitchen ell stands 10 ft off the north wall as the house does, the rear alley of ~6-10 ft running on behind it
        guest house seat - GUESS research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.drawing.html: on the inner court's east wall facing the garden beside the reception rooms, below the shrine's corner and its tree
        office hall - research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.html, research/questions/0099-the-hearing-court-shirasu.drawing.html: a 113 x 38 ft hall backing the divider, its rooms behind a 30 x 10 ft dais on the south face over the hearing court; the room sizes GUESSES
        tax archive place - GUESS research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: the archive on the divider beside the granary, the court's stores together
        staff long-house - research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html, research/questions/0106-the-chief-retainers-house-karo-yashiki.drawing.html: 24 x 82 ft on the west wall, the karo's 14 ft bay and four 17 ft bays side by side, a door to each on the long face
        granary - research/questions/0098-storehouses-for-the-tax-rice.drawing.html: the granary's form rolled from the record's two (GRANARY_FORM: the earth-walled kura, drawn without posts), 50 x 27 ft in the ~43-50 x 25-27 ft band (its size a GUESS there), on the east wall
        cell place and size - research/questions/0096-holding-cells-agariya-and-roya.drawing.html: a 12 x 10 ft remand cell on the south wall just east of the service gate
        gatehouse - research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.drawing.html: the gatekeepers in a gatehouse of their own beside the one-bay gate (a one-bay gate holds no guardroom), 40 x 12 ft as the page draws one - its length a GUESS, 2 ken deep measured
        stables - research/questions/0108-stables-umaya.drawing.html: 18 x 24 ft, three bays long, the stalls, the passage and the grooms' room in its depth
        stable door - research/questions/0108-stables-umaya.html: its door at an end into the passage, a gable-entered stable as the Shomei's three-bay stable - the west end, the gatehouse standing a foot off the east
        residence inner entrance - GUESS research/questions/0107-kitchens-daidokoro.drawing.html: the house's inner entrance on its rear (north) face at the kitchen (west) end, clear of the family privy at the corner
        gatehouse door - GUESS: searched, the record silent (feature 417 T36 pass P7, 2026-10-25); the gatehouse's door on the gate passage, where the gatekeepers watch
        office hall doors - GUESS research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.drawing.html: the office takes the formal entrance where it shares a compound with the residence, facing open ground; its doors on its east face by the middle gate and on its west face, the faces a GUESS
        servants' row - research/questions/0115-servants-in-a-samurai-household-where-they-sleep-and-how-they-were-hired-hokonin.drawing.html, research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html: a range on the south (street) wall, the menservants'; its entry form the compound's knob, rolled (this draft's roll: a door to each dwelling, five of ~15.2 ft); its 76 x 15 ft and the five dwellings GUESSES, the 15 ft depth 0115's
        postern places - GUESS: the kitchen postern 50 ft down the west wall on the kitchen yard, the service gate 221 ft along the south wall at the cart yard's south end; where a compound's lesser gates stood is not recorded
        stables seat - research/questions/0115-servants-in-a-samurai-household-where-they-sleep-and-how-they-were-hired-hokonin.html: the stables on the street (south) wall beside the servants' row, as a long-house gate's passage had servants' quarters and a stable beside it
        cell door - GUESS: searched, the record silent (feature 417 T36 pass P7, 2026-10-25); toward the cell's west end, so its approach leaves the barracks' south dwelling the ground for its own door
        maids' room - GUESS research/questions/0115-servants-in-a-samurai-household-where-they-sleep-and-how-they-were-hired-hokonin.drawing.html: the maids and kitchen hands under the main roof at the kitchen end, as the Aizu chief retainer's house kept the rooms of the maids and servants in the house; which servants slept there, and its 10 x 10 ft, GUESSES
        barracks dwellings - research/questions/0097-staff-rowhouses-and-barracks-nagaya.html: the barracks divided into four dwellings of 17.5 ft, a door each on its court face; four a GUESS in the 12-18 ft bays
        its figures guessed on 0091 - GUESS research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.drawing.html: 102 (garden's corner at the house's garden face (the veranda line)); 35.5 (garden's corner at the house's garden face (the veranda line)); 46.5 (garden depth to y 82 (claim says 46)); 22 (rear yard depth)
        its figures guessed on 0099 - GUESS research/questions/0099-the-hearing-court-shirasu.drawing.html: 50.5 (hearing court centered on the hall, at its south face (90 + 38 + 2.5 stand-off))
        its unstated figures - GUESS: searched, the record silent (feature 417 T38 pass N13, 2026-10-25) - 131 (yard from the hearing court's east end); 130.5 (yard from the hearing court's east end); 57.5 (yard from the hearing court's east end); 0.3 (cell door toward its west end); 0.8 (last door moved off its middle for the cell)
        its figures guessed on 0104 - GUESS research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.drawing.html: 130 (forecourt's corner inside the gate, east of the gatehouse); 166 (forecourt's corner inside the gate, east of the gatehouse); 0.7 (end-face doors on the front room)
        its figures from 0165 - research/questions/0165-martial-training-grounds-and-dojo.drawing.html: 190 (practice ground beside the barracks ("beside its guards' quarters")); 126 (practice ground beside the barracks ("beside its guards' quarters"))
        its figures guessed on 0116 - GUESS research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: 188 (cart yard's corner before the service gate); 177 (cart yard's corner before the service gate)
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N13, 2026-10-25) - 13 (placement order); 11 (placement order); 5 (placement order)
        its figures guessed on 0107 - GUESS research/questions/0107-kitchens-daidokoro.drawing.html: 0.35 (residence rear door at the kitchen end); 0.4 (residence rear door at the kitchen end)
        its figures of ours - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 0.085 (door at each bay's middle (one door each, cited)); 0.274 (door at each bay's middle (one door each, cited)); 0.482 (door at each bay's middle (one door each, cited)); 0.689 (door at each bay's middle (one door each, cited)); 0.896 (door at each bay's middle (one door each, cited)); 0.125 (barracks doors at bay middles); 0.375 (barracks doors at bay middles); 0.625 (barracks doors at bay middles); 35 (walls of four 17.5 ft dwellings); 52.5 (walls of four 17.5 ft dwellings)
        its figures from 0097 - research/questions/0097-staff-rowhouses-and-barracks-nagaya.html: 48 (walls between the 14 ft and 17 ft bays); 65 (walls between the 14 ft and 17 ft bays)
        its figures guessed on 0113 - GUESS research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.html: 72 (official study's width and place ("room sizes GUESSES")); 41 (official study's width and place ("room sizes GUESSES"))
    """
    # The main gate is a one-bay yakuimon with an 8 ft frontage and a 7 ft passage - R26's knob, the one-bay form (6-8.5 ft, research
    # 0093); it was a 13 ft opening, the carriage gate the vocabulary once drew. The postern in the west wall,
    # centered 50 ft down it, opens on the kitchen yard between the bath and the karo's house (docs/building-programs.md:
    # the kitchen postern keeps deliveries and night-soil off the hearing court); its 6 ft passage is a GUESS. The
    # middle gate keeps the Envelope's 6 ft (narrower than the main gate). The outer court's SERVICE GATE (pass 4,
    # building-review round 3; docs/building-programs.md "Walled enclosure": a busy outer court warrants a small service
    # gate so muck, night-soil and prisoner transfers skip the formal gate) stands in the south wall by the cell, at
    # the head of the cart yard; its 6 ft passage is a GUESS, narrower than the main gate. Centered 221 ft along the
    # wall, where the cart yard reaches it and the cell stands just east (feature 374 batch 4, building-review E1: at
    # 244 ft the cell and the re-proportioned barracks sealed it, and `postern_approach` holds it now).
    env = Envelope(w_ft=270.0, h_ft=200.0, divider_ft=90.0, gate_w_ft=GATE_W_FT[GATE_FORM], posterns=(("W", 50.0, 6.0), ("S", 221.0, 6.0)))
    spine = (
        # THE GARDEN LIES BEFORE THE HOUSE (research 0091 'Samurai residences and their rooms (buke yashiki)' and
        # rendering 'How our maps lay out samurai residences and their rooms (buke yashiki)': the garden faces the reception rooms). Pass 7 (building-review round 6: ~62 x 66 ft of bare inner court east of a garden sized to
        # the house alone) runs it on to the guest house, x 104-226, so the one garden faces the reception and the guest
        # house both - guests were received in the garden-facing rooms (research 0091); the servants' row it once
        # faced is on the kitchen yard since pass 6. From the house's veranda (y 35.5) 46.5 ft deep to y 82, an 8 ft walk
        # along the divider. Its size is a GUESS.
        CourtZone("garden", 102.0, 35.5, 124.0, 46.5),  # feature 374 wave 113: from the kitchen ell's east face (the house's west end), the house 7 ft west
        # The vegetable ground at the site rolled among those the sun and the room leave (GARDEN_SITE, research 0109), at
        # the soup-greens plot's attested size (feature 374 wave 129: it was a 64 x 48 ft field squeezed into the kitchen
        # yard, a size nobody attests); the kitchen yard's working ground beside the kitchen named the service yard, as
        # Ochiba's sheet names its own (pass 7's bare yard, building-review round 6, answered by naming it).
        *garden_zones(GARDEN_SITE),
        # The rear yard (feature 374 wave 124): open working ground on the north wall between the household's storehouses
        # and the kitchen, where the servants' range stood - the Higuchi house's rear, the ground behind the main house
        # with its storehouse beyond (research buildings 230), as the hand sheets name it; it holds the kitchen and the house
        # where the garden is drawn for them. Its bounds are a drawing convention.
        CourtZone("rear yard", 38.0, 3.0, 37.0, 22.0),
        # The hearing court is centered on the office hall (x 33-146 as placed since feature 374 wave 125: the 24 ft staff
        # long-house and a fire-gap west of it) and no longer than it - R22, research 0099: under the office hall's roof or its
        # own, before the dais. 80 ft leaves each end of the hall's south face out from under the roof, where its tub
        # stands; 26 ft deep (32 until feature 374 batch 5, 36 until pass 5) keeps a way of about 6.4 ft past the stable well before
        # the stables to the west of the outer court (building-review E1: at 32 ft the well left ~2.3 ft each side, the
        # only way west). It was 132 x 39 ft, longer than the hall and 34 ft off its center. Its size is a GUESS - no
        # roofed court's size was found.
        CourtZone(
            "oshirasu", 50.5, 131.0, 80.0, 26.0
        ),  # y 131 and x 50.5 since feature 374 wave 134 (the hall 2.5 ft off the divider's centerline, it was 1.5, and 1 ft east, centered on it again); y 130 since pass 6: the office hall is 38 ft deep; x 49.5 since feature 374 wave 125, centered again on the hall the 24 ft staff long-house let slide west
        # just inside the main gate (131-139), east of the gatehouse that stands beside it, and 55 ft wide (it was 36)
        # to take the ground east of the gate the hearing court gave up when it shrank to the hall's length; a
        # marshalling apron's width is a GUESS
        CourtZone("forecourt", 130.0, 166.0, 55.0, 31.0),
        # Practice ground beside where the watch lodges (the E-wall barracks, 24 ft deep and 67 long since feature 374 wave 125,
        # lands at x 244, y 130 under the current masses): 33 x 42 ft = 1,386 sqft, inside the 1,200-2,000
        # sqft full-platoon band at ~90-135 sqft per drilling samurai (docs/buildings.md
        # "Practice ground" + the dojo-is-a-city-institution grounding), west of the E column,
        # the barracks 21 ft east of the patch's edge at x 223 (it stands at x 244 since feature 374 wave 125), its doors
        # opening on the way between - which is what "beside the watch's lodging" means - so the wall rows still flow past
        # it without overflow. Pass 4 widened it to 45 ft; pass 5
        # gave the 12 ft back to the barracks.
        CourtZone("practice ground", 190.0, 126.0, 33.0, 42.0),
        # The outer court's open ground between the hearing court and the practice ground (pass 4, building-review round
        # 3: ~50 x 40 ft unnamed): the way from the forecourt to the middle gate and the hall's east door, named, not
        # fenced (UNFENCED_ZONES). Its bounds are a drawing convention.
        # It starts where the hearing court, centered on the hall, ends - a yard drawn over the court painted out its east
        # end (building-review E1, feature 372 wave 105).
        CourtZone("yard", 130.5, 131.0, 57.5, 33.0),  # y 131 since pass 6: the office hall is 38 ft deep; x 130.5 since feature 374 wave 134, from the re-centered hearing court's east end
        # The cart yard before the service gate (pass 4: the ~71 x 30 ft of bare ground in the SE outer court) - the
        # carts, the stable muck and the prisoners' way out; the kind the hand sheets draw (a DEVIATION from canon on
        # H and U, forms.md). Its size is a GUESS.
        CourtZone(
            "cart yard", 188.0, 177.0, 37.0, 20.0
        ),  # 37 wide (feature 374 wave 125): the service gate opens at its south end, the cell just east of it  # its north edge 172 (pass 5) leaves the garrison privy its seat by the barracks
    )
    b = BuildingSpec
    buildings = (
        # inner (residence) court - buildings ring N/E/W walls + back the divider
        # The residence (research 0091 'Samurai residences and their rooms (buke yashiki)', rendering 'How our
        # maps lay out the residence'): one block under one roof (R02's ordinary form), MASSED IN TWO ROWS front
        # and back (forms.md R02; the Kuchiba house's rooms "stand in two rows, front and back").
        # Its rooms take the palace order's lesser form - the reception at the east END, the full depth, nearest the
        # middle gate; the master's rooms beside it on the garden row; the family's beyond, with the inner rooms behind
        # (R03). The veranda runs along the garden face alone, 4 ft (R01's first form, research rendering/buildings
        # 'How our maps draw verandas and storm shutters (engawa and amado)': 3-6 ft). Its inner entrance opens on its rear (north) face at the
        # kitchen end, onto the rear alley the kitchen's way joins (feature 374 wave 113: the kitchen ell abuts the west face) (research/questions/0107-kitchens-daidokoro.drawing.html 'How our maps draw kitchens (daidokoro)').
        # It stands 10 ft off the north wall: the rear band narrowed to a cart/servant alley (research 0091),
        # the family privy flush to the wall in it.
        # THE HOUSE'S SIZE is research 0091's: the Yokota house of a 150-koku district magistrate (gun-bugyo, the
        # county post itself) had a main house of about 49 tsubo, ~1,740 sq ft. Pass 6 takes that house, not the 67-tsubo
        # house of a 500-1,000 koku retainer: the district magistrate is this posting's own rank. The residence 56 x 24 ft
        # (1,344 sq ft with its veranda), the kitchen 20 x 18 (360) and the bath 10 x 8 (80) make ~1,784 sq ft, ~50
        # tsubo. The room sizes are GUESSES.
        b(
            "residence",
            "lord",
            56.0,
            24.0,
            "inner",
            "N",
            order=10,
            feature="residence",
            rooms=(
                # the maids' room at the kitchen (west) end, under the main roof (feature 374 batch 4, plan R4-1: research
                # 0115, the Aizu chief retainer's house kept "the rooms of the maids and servants" in the house; which
                # servants slept there, and its 10 x 10 ft, are GUESSES)
                ("servants' quarters", 0.0, 0.0, 10.0, 10.0),
                ("inner rooms", 10.0, 0.0, 26.0, 10.0),
                ("family quarters", 0.0, 10.0, 18.0, 10.0),
                ("lord's quarters", 18.0, 10.0, 18.0, 10.0),
                ("reception room", 36.0, 0.0, 20.0, 20.0),
            ),
            engawa_ft=4.0,
            door_face="N",
            # at the kitchen (west) end of the rear face, as 0107's drawing page seats the inner entrance, just east of the
            # family privy at the corner (feature 374 wave 127; it stood mid-face at 0.4); the kitchen ell takes the west face
            door_fracs=(0.3, 0.35, 0.4),
            inset_ft=8.5,  # the house 10 ft off the north wall's face (11.5 ft off its centerline): the alley at the top of 0091's ~6-10 ft
        ),
        # THE SERVANTS LODGE ON THE STREET FRONT (feature 374 wave 124): a large household's servants are drawn in a range
        # on its street edge, never a rowhouse behind the house (0115's drawing page,
        # research/questions/0115-servants-in-a-samurai-household-where-they-sleep-and-how-they-were-hired-hokonin.drawing.html),
        # so their range stands on the outer court's south wall, the street's, below; it stood in the NW corner of the
        # inner court (pass 6), 72 x 22 ft. THE NW CORNER IS THE HOUSEHOLD'S STORES now: two storehouses (dozo), 12 x 18 ft,
        # the common two by three ken, as the Matsushiro retainer's house kept two (research buildings 230: the Higuchi
        # house's storehouse beyond the ground behind the main house; the hand sheets' two since feature 283) - the rear
        # strip keeps its stores (docs/buildings.md). Their number and size are GUESSES; they carry the coverage the
        # servants' range took to the street, keeping the jin'ya band (0116) without shrinking the envelope.
        # the pair unequal, as the Yokota house's two (feature 374 wave 128: ~15.7 x 18.7 and ~9.5 x 12.5 ft, the national
        # register; glyph-check F4/F5): the west one at the larger's 16 x 19 ft, the east at the common 12 x 18 ft
        b("storehouse (W)", "kura", 16.0, 19.0, "inner", "N", order=13, feature="storehouse"),
        b("storehouse (E)", "kura", 12.0, 18.0, "inner", "N", order=12, feature="storehouse"),
        # The kitchen stands between the rear yard and the house, an ELL abutting the residence's west end (feature 374
        # wave 113, `joins`: research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.html, a kitchen projecting
        # from one side of a one-block house, no corridor), its yard - the bath, the well, its one door, the postern - to the south
        # and west. 20 x 18 ft, part of the house's 49 tsubo (above); the kitchen's own size is a GUESS (research 380:
        # "How much of either house was kitchen is not given").
        # Its one outside door opens WEST, onto the rear yard, which runs south to the kitchen yard (pass 7,
        # building-review round 6: on its yard face it opened into a ~5 ft pocket between the bath, the well and the house).
        # It stands 10 ft off the north wall, as the house does (pass 8, building-review round 7): the house's rear alley
        # then runs on behind the kitchen to the rear yard, and down it to the kitchen yard
        # and the postern - the night-soil carter's service route to the house's privies. Flush to the wall, the
        # kitchen closed the alley's west end, and the privies were ~400 ft round from any service edge.
        b("kitchen", "service", 20.0, 18.0, "inner", "N", order=11, feature="kitchen", door_face="W", door_fracs=(0.5, 0.3, 0.7), inset_ft=8.5, joins="residence"),
        # A MODEST shrine, 18 x 14 ft (pass 4, building-review round 3: it was 36 x 30 ft, the hall-shrine ceiling, which
        # is Ochiba's particular - docs/building-programs.md: the shrine is universal equipment, its scale the per-manor
        # particular; docs/buildings.md "Modest shrine"). The size is a GUESS inside the shrine band (40-1,150 sq ft).
        # its corner holds the ground for its tree (0218's drawing page: "in a corner of its grounds beside a tree"): the
        # crown and its clearance either side past its south end, less the fire-gap the next building keeps anyway - the
        # guest quarters flowing below it, the crown 2 ft clear of both (wave 130)
        b("shrine", "shrine", 18.0, 14.0, "inner", "E", order=4, feature="compound shrine", tree_ft=SHRINE_TREE_CROWN_FT + 2 * SHRINE_TREE_CLEAR_FT - FIRE_GAP_FT),
        # A detached guest house is a GUESS (R10, research 0091: guests were received in the main house, and a
        # guest house apart at a samurai house was not found); kept as the example's draft of the item.
        b(
            "guest house", "lord", 40.0, 42.0, "inner", "E", order=3, feature="guest quarters"
        ),  # 40 x 40 since feature 374 wave 128, holding the jin'ya band when the granary came down to 0098's (38 x 38 until then; 33 x 32 until feature 374 wave 126; 33 x 30 before pass 6)
        # outer (administrative) court - office hall backs the divider (oshirasu in front)
        # The clerks' room is a ROOM of the office hall, at its west end on the rear (divider) side, 30 x 20 ft - the
        # footprint the freestanding clerks' building had (feature 267 R20, research buildings "The office hall and its
        # clerks (goyakusho)": the clerks worked in rooms of the office; no page gives them a workroom building). Its size
        # is a guess.
        # Its DAIS BAND (pass 4, building-review round 3): the magistrate's dais, 30 x 10 ft centered on its south face over
        # the hearing court (docs/buildings.md "Office hall (with dais band)", the size Ochiba draws; a GUESS). Its door opens
        # on its east face, by the middle gate - the south face is the court's.
        b(
            "office hall",
            "lord",
            113.0,
            38.0,
            "outer",
            "divider",
            order=10,
            feature="office hall",
            rooms=(("clerks' room", 0.0, 0.0, 30.0, 20.0), ("day office", 30.0, 0.0, 42.0, 20.0), ("official study", 72.0, 0.0, 41.0, 20.0)),
            dais=(30.0, 10.0),
            door_face="E",
            # its doors open on the FRONT room (0.8 of the end faces), east by the middle gate and west to the archive
            # and the retainers (pass 6, building-review round 5: the front room and the west end had none)
            extra_doors=("W",),
            door_fracs=(0.8, 0.7),
        ),
        # 24 x 18 ft, under 0100's ~450 sq ft records-store ceiling (feature 372 wave 105; it was 34 x 34, pass 6's mass)
        # Feature 374 wave 125: on the divider east of the office hall, beside the granary - the court's two stores together
        # (it stood in the west wall's corner, where the staff long-house, now 24 ft deep, needs the wall's whole length);
        # 18 x 24 ft, turned so its 24 ft runs off the divider.
        b("tax archive", "kura", 18.0, 24.0, "outer", "divider", order=6, feature="tax archive"),
        # 50 ft long (it was 60): the hearing court, centered on the hall, starts at x 75.5 (feature 372 wave 105),
        # and the retainers' east face must keep a 7 ft run in front of it for its tub and door
        # The staff long-house (pass 6): the senior retainers' quarters, with the KARO'S BAY at its north end,
        # 14 ft of it with its own door. Feature 374 wave 125: 24 x 82 ft, its bays SIDE BY SIDE along the west wall, a door
        # to each on the long (east) face - 0097's drawing page: a rowhouse is a long, narrow building no more than about
        # 24 ft deep, never a square or squat block, its dwellings in a row along its length
        # (research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html); it was 50 x 36 ft, the karo's bay
        # stacked across its depth and both doors on its short end. Its length fills the wall to the corner, a GUESS - R11's attested form (research 0106: at an intendancy the staff lived
        # inside the compound in small houses or long-houses; a chief retainer's house inside the lord's own compound was
        # not found, and "a small house of their own rather than a bay of the staff long-house is a GUESS"). The karo's
        # house of its own in the inner court (pass 5) is gone. The sizes are GUESSES.
        b(
            "senior retainers' quarters",
            "service",
            24.0,
            82.0,
            "outer",
            "W",
            order=4,
            feature="retainers' quarters",
            rooms=(("karo's house", 0.0, 0.0, 24.0, 14.0),),
            extra_doors=("E", "E", "E", "E"),
            door_fracs=(0.085, 0.274, 0.482, 0.689, 0.896),  # the karo's 14 ft bay and four 17 ft bays, a door at each bay's middle (0097: bays ~12-18 ft, each a dwelling with its door)
            bays=(14.0, 31.0, 48.0, 65.0),  # the walls between them (feature 374 batch 4, building-review N1)
        ),
        # 60 x 30 ft (it was 52 x 28), the top of the granary band (30-60 x 14-36): pass 5 returned the ~2,000 sq ft the
        # house gave up (research 0091) to the compound's working stores and lodgings, holding coverage in the
        # jin'ya band (30-42%, 0116's drawing page) without shrinking the envelope (docs/buildings.md). A GUESS in the band.
        # Feature 374 wave 128: the granary's form is 0098's knob, rolled (GRANARY_FORM: this draft's roll is the earth-walled
        # kura, drawn without posts as 0098 draws one), at 0098's ~43-50 x 25-27 ft (a GUESS in that band; it was 60 x 30 ft).
        b("granary", GRANARY_KIND[GRANARY_FORM], 50.0, 27.0, "outer", "E", order=6, feature="granary"),
        # 45 ft long (it was 33): the platoon lodged on the grounds (staff housing option (a)) is ~10-20 men, and the
        # watch's range should out-foot the stable by a margin (docs/buildings.md "Barracks": ~27-53 ft); pass 5. A GUESS.
        # Feature 374 wave 125: 24 x 67 ft (it was 45 x 34), long and narrow along the east wall - 0097's drawing page: the
        # barracks is drawn 12 to 24 ft deep, never a square or squat block (above); about the same floor as before.
        # 24 x 70 ft since feature 374 wave 128 (it was 67), the east wall's whole free run: the floor the granary gave up to
        # 0098's band returned here, the length a GUESS inside 0097's up to ~145 ft. Divided into four dwellings of 17.5 ft, a
        # door to each on its court face (feature 374 batch 4, building-review
        # E2: research/questions/0097-staff-rowhouses-and-barracks-nagaya.html, "The barracks is divided into dwellings,
        # each an earth-floored entry and a raised floor", bays ~12-18 ft); four of 17.5 ft a GUESS in that band.
        b(
            "barracks",
            "service",
            23.0,  # 23 ft deep since feature 374 wave 134: a foot more clear of the east wall's face, and the cell at the south-east corner
            70.0,
            "outer",
            "E",
            order=4,
            feature="barracks",
            extra_doors=("W", "W", "W"),
            door_fracs=(0.125, 0.375, 0.625, 0.8),  # the last off its dwelling's middle: the cell stands at the face's south end
            bays=(17.5, 35.0, 52.5),
        ),
        # 12 x 10 ft: the small end of the single cells read (Osaka's 6 mats, ~12 x 9 ft, to Tenmacho's 18); a county
        # remand cell belongs there, its size a guess in the span (feature 267 R24, research 'How our maps draw holding cells (agariya and rōya)'). It was
        # 18 x 16 ft.
        # Feature 374 wave 125: on the south wall just east of the service gate (it stood on the east wall, below the
        # barracks the new depth lengthened), where docs/buildings.md sets it: beside the service gate, so prisoner
        # transfers never cross the hearing court.
        # its door toward its west end, so its approach leaves the barracks' south dwelling its door (feature 374 batch 4)
        b("cell", "cell", 12.0, 10.0, "outer", "S", order=1, feature="cell", door_fracs=(0.3, 0.5)),
        # The gatehouse stands BESIDE the gate, a building of its own (R19's Takayama form, research buildings 420),
        # 18 x 12 ft - the one measured freestanding guardroom (Kita-in's 3 x 2 ken). It was 42 x 15 ft in the SW
        # corner, 83 ft from the gate; ~40 ft is the gate range's scale. Left as found by feature 372 wave 105: 0093 now draws
        # a gatehouse of its own ~40 ft (the hand sheets since wave 101), but at 40 ft the stables find no seat on this
        # south wall - the draft's own row (`docs/building-programs.md` walled enclosure).
        # Its door opens on the gate passage (east), where the gatekeepers watch - not on the court.
        # Feature 374 wave 128: the main gate's form is 0093's knob, rolled (GATE_FORM: this draft's roll is the one-bay gate),
        # and a one-bay gate has no range to hold a guardroom, so its gatekeepers sit in a gatehouse of their own - drawn
        # ~40 x 12 ft as 0093's drawing page draws one (its length a GUESS; 2 ken deep, measured). The servants' row gives
        # it room on the south wall (above).
        b("gatehouse", "dark", 40.0, 12.0, "outer", "S", order=8, feature="gatehouse", beside_gate=True, door_face="E"),
        # Feature 374 wave 126: 18 x 24 ft (it was 42 x 24), 0108's warrior's stable - three bays long of one-ken stalls on
        # the wall side, the earth passage running its length and the grooms' room across it toward the court
        # (`compound_parts._stable_parts`; research/questions/0108-stables-umaya.drawing.html); its door at the east end into
        # the passage, a gable-entered stable. The depths are GUESSES. Still under the barracks as docs/buildings.md asks.
        b("stables", "service", 18.0, 24.0, "outer", "S", order=5, feature="stables", door_face="W", door_fracs=(0.5,)),  # its west gable since wave 128: the gatehouse stands a foot off its east end
        # The grooms' and bearers' row (pass 5, building-review round 4: the bare SW ground by the stables while the
        # grooms lodged in the inner court): a servants' nagaya in the SW corner beside the stables it serves
        # (research: the domestic servants - cooks, grooms, cleaners - lived in a nagaya; a second row by the stables is
        # a GUESS), 44 x 18 ft. It takes the corner (order above the stables') so the stables' privy keeps its end face.
        # Feature 374 wave 124: the household's servants lodge here too - one servants' range on the street front, its
        # south face the wall, the grooms' and the household's (0115's drawing page, above): 76 x 15 ft (it was the grooms'
        # alone, 44 x 18 ft) - the 15 ft depth is 0115's GUESS for a retainer's range, its length a GUESS.
        # Its entry form is 0097's knob, rolled per compound as Ochiba's sheet rolls it (feature 374 batch 4: the filed
        # `servants' row entry form` row; research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html, "a knob set
        # per compound"): this draft's roll is a door to each dwelling, five of ~15.2 ft (inside 0097's 12-18 ft bays). Its
        # lodgers are the menservants, whose work is the gate and the outer court (the grooms keep the stable's grooms' room,
        # research 0108); the maids and the kitchen hands sleep under the main roof at the kitchen end (the residence's maids'
        # room; plan R4-1, research 0115's Aizu house, that the maids slept there a GUESS).
        servants_row(SERVANTS_FORM),
    )
    return CompoundProgram("County Magistracy (example)", env, spine, buildings, tier=_EXAMPLE_TIER, seed_name="county-magistracy-example")
