"""The place card: what a reader gets for clicking the settlement's own title placard (feature 156).

The GM, 2026-08-29: *"I would like to be able to click on the title card for a settlement and then
pull up an explanation of the type of settlement that this is. And I don't just mean saying that
Inashiro is a hamlet ... Basically, if someone clicks on the title card, I want to have a brief
'what is this place' overview."*

Everything the card states comes from one of three places, and never from a per-map special case in
this module (spec FR-014):

  MEASURED   the map's own manifest and its own ink - the farmhouse count, the crops actually drawn
  CANON      the GM's campaign notes, `/host-l7r-repo/setting/l7r.md`, for what a tier IS and how many
             inhabitants a household holds
  AUTHORED   the map's `<name>.notes.md` "Map notes" block, for what no drawing can know - which
             village district this hamlet belongs to, and in which direction

WHAT THE CARD IS NOT ALLOWED TO SAY, and why it is worth knowing (spec `research.md`, and the
`source-reader` pass of 2026-08-29 that produced it):

  * It does NOT rank kinds of hamlet. The GM asked "if this is the most common type of hamlet that
    exists or whatever" - and nothing answers it. No fetchable historical source ranks settlement
    forms by frequency, and `l7r.md` ranks TIERS rather than kinds of hamlet. So the card states the
    tier fact, which the setting does give, and says nothing about which sort of hamlet is usual.
  * It does NOT claim wet-rice dominance. The research pass came back NOT-FOUND, and `kokudaka`'s
    rice-denominated assessment is a FISCAL convention covering dry field too - citing it would be
    citing a source for something adjacent to what it says. The card says this hamlet farms rice
    because the map draws rice.
  * Where it rests on canon that the historical record contradicts or is silent on, it SAYS SO, in
    the caveat (spec FR-008a). That is the GM's own liberty rule - *"we should call out liberties
    that we have taken when we have chosen to deviate from historical accuracy"* - applied to this
    surface. A hamlet having no headman of its own is the case: it is Rokugan's rule, and the Edo
    record has branch hamlets that did have one.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..dwellings import DWELLING_KINDS, HOUSEHOLD
from .notes import MapNotes
from .sources import citations, research_sources

#: `l7r.md`, "The Median Domain": ~5 inhabitants per household, and a hamlet of 10-20 households
#: holds 50-100. The tiers that record a population outright (towns, cities) use theirs instead.
#: TAKEN FROM THE LEAF, not restated: the gate's capacity maths uses the same five, and the whole
#: point of `dwellings.py` was to stop this module keeping its own copy of what that package knows
#: (settlement-review round 5 - the move had left the constant behind).
PER_HOUSEHOLD = HOUSEHOLD

#: `l7r.md`'s median-domain table, for the one ranking the card is allowed to make - of TIERS. They are
#: INTERPOLATED into the hamlet's text below rather than typed into it: writing them out left these
#: three with no consumer and the same numbers in two places, which nothing would have caught (ruff
#: does not flag an unused module constant) - settlement-review round 7, 2026-08-29.
HAMLETS_PER_DOMAIN, VILLAGES_PER_DOMAIN, HAMLET_SHARE = 1296, 216, "40%"


@dataclass(frozen=True)
class Kind:
    """What one tier IS, in terms a player can use at the table."""

    noun: str
    # The sentence that follows "<Name> is a <noun>". MIND THE WORDS THE CLASS VOCABULARY ALSO USES:
    # the hamlet's line said "no shrine" on a page whose own `household shrine` class describes a
    # hokora with a torii, and "no burial ground" on maps that draw a `grave island`. Both were true
    # and both read as contradictions, because the card and the classes were using one word for two
    # things (settlement-review, 2026-08-29 - live on the reference map, not merely predicted).
    what: str
    # What to call the dwellings the map draws. EVERY tier states a count, and it is always exact,
    # because every one of them is enumerated and rendered (GM 2026-08-29: "towns and cities should
    # state and list the number of non farmhouse dwellings ... this is something which is enumerated
    # and known and which is actually exact and rendered"). What differs is WHICH dwellings are
    # countable: a hamlet's and a village's are farmhouses and are all of them, while a town's and a
    # city's farmhouses are only a sample of a countryside deliberately not drawn whole, so those
    # tiers count their NON-farm dwellings and say nothing about farmhouses at all.
    houses_noun: str
    # Whether the count excludes dwellings standing in a drawn agricultural district.
    excludes_farms: bool
    # What the population figure MEANS at this tier, which is a matter of Imperial census convention
    # rather than of arithmetic, and differs between a town and a city (GM 2026-08-29). Empty where
    # the population is simply five to a drawn household and needs no explaining.
    population_note: str


#: Keyed by `meta.scale`. Written from `l7r.md` (a hamlet "belongs to a village district and is
#: overseen by a village headsman who lives in the main village and not in the hamlet"; "county towns
#: are the lowest level at which samurai live") and from `settlements.md`'s tier rules.
KINDS: dict[str, Kind] = {
    "hamlet": Kind(
        "hamlet",
        "a small outlying farming community belonging to a village district. It has no headsman of its own - the village headsman who oversees it lives in the main village - and no shrine and no burial ground; its dead go to the district's ground. "
        f"A hamlet is the commonest kind of settlement there is: a domain holds {HAMLETS_PER_DOMAIN:,} of them to {VILLAGES_PER_DOMAIN} villages, and {HAMLET_SHARE} of its inhabitants live in one.",
        "farmhouses",
        False,
        "",
    ),
    "village": Kind(
        "village",
        "the head of its village district, and the seat of the village headsman who oversees the outlying hamlets - with its own shrine, its tax-free plots and the burial ground the whole district uses. Like every village district it is peasant-only; no samurai live here.",
        "farmhouses",
        False,
        "",
    ),
    "town": Kind(
        "town",
        "the seat of a county magistrate, and the lowest level of Rokugani society at which samurai live - the lowest, too, that has resident merchants, which is why the farmers of the surrounding districts come in for market day.",
        "dwellings",
        True,
        "That figure counts the settlement as drawn - its townsfolk and the farming households on the sheet around them, about five to each. The county the town heads is larger again, and the Imperial convention counts the whole of its farming population as part of the town; this map does not yet state that larger number.",
    ),
    "city": Kind(
        "city",
        "the seat of a province's governor and its ministries, and a market the whole province turns toward.",
        "dwellings",
        True,
        "That figure is the households drawn inside the city itself, about five to a dwelling - including the few farmhouses that stand within the wall. It does NOT take in the farming countryside: the farms out on this sheet belong to village districts and counties, which the Imperial census counts separately from the city. (By convention the city's figure also takes in the samurai country estates around it, only some of which are drawn; this map does not yet state that larger number either.)",
    ),
}

#: Which classes are a CROP, and how the card groups them. Read from the classes PRESENT on the map
#: (spec FR-010, FR-014), never from a per-map list - which is what lets the dike-pond hamlet, whose
#: fields are mulberry, sugarcane, banana and fish and which draws no dry plot at all, describe
#: itself correctly with no code of its own.
CROPS: dict[str, tuple[str, str]] = {
    "paddy": ("wet", "rice"),
    "millet": ("dry", "millet"),
    "buckwheat": ("dry", "buckwheat"),
    "barley": ("dry", "barley"),
    "soy": ("dry", "soy"),
    "vegetable ground": ("dry", "vegetables"),
    "mulberry dike": ("dike", "mulberry, for silkworms"),
    "sugarcane dike": ("dike", "sugarcane"),
    "banana dike": ("dike", "bananas"),
    "fruit dike": ("dike", "fruit trees"),
    "fish pond": ("water", "fish"),
}

#: How each group is introduced. A group with nothing present is skipped, so a map that grows only
#: dike crops never says "the flooded fields grow" of fields it does not have.
_CROP_LEAD: dict[str, str] = {
    "wet": "The flooded fields grow",
    "dry": "The dry ground carries",
    "dike": "The pond dikes are planted with",
    "water": "The ponds are stocked with",
}

#: A crop whose mention is a whole SENTENCE rather than an item in a list. Bund beans are the case
#: and the reason the split exists: they are neither the wet field nor the dry ground but the wall
#: between them, and listing them under either says something false about where they grow.
CROP_SENTENCES: dict[str, str] = {
    "bund beans": "Soybeans are sown along the tops of the paddy bunds, a second crop off ground that would otherwise grow weeds.",
}

#: Where the card and the class vocabulary use ONE WORD FOR TWO THINGS, and the sentence that keeps a
#: reader from meeting a contradiction. Appended only when that class is actually drawn on this map -
#: the same rule the crop sentence follows, and the reason it must not live inside `Kind.what`, which
#: cannot see what is present (settlement-review, 2026-08-29: the card told every hamlet about a grave
#: mound, and Mizuguchi draws none). The wording follows the CLASS's own, not the card's: the hokora
#: stands in a corner of the plot, which is where `household shrine` puts it and where Sawada's sits,
#: 46 ft from its house.
COLLISIONS: dict[str, str] = {
    "household shrine": "(The little hokora in a corner of a farmstead plot is one household's own, and is a different thing from a village shrine.)",
    "grave island": "(The mound out among the plots is a field grave, not a burial ground.)",
}

#: The `### Place` keys the card understands. Anything else an author writes is ignored rather than
#: guessed at - the block stays a place to record things this module has not learned to use yet.
PLACE_KEYS = ("district", "district direction", "county", "imperial road", "town", "town direction", "also")

#: The research entry the card is written FROM, in the form `sources.py` parses - so the card's
#: references are READ FROM THE RECORD at page-write time, exactly like a class's, rather than being
#: a second list here that could drift from it.
ENTRY = "research/archetypes.md - 'What a settlement IS'"

#: The basis the card owes its reader (spec FR-008a). Two statements above rest on setting canon where
#: the historical record does not back them, and the GM's rule is that a liberty is called out. It is
#: the FINE PRINT and it reads as fine print: the facts themselves belong in the body, where the reader
#: meets them (settlement-review, 2026-08-29 - the basis block had grown longer than the card).
BASIS = (
    "the counts above are Rokugan's own arithmetic rather than a historical finding, and so is the rule that a "
    "hamlet keeps no headman - the Edo record has branch hamlets that kept their own officials and stood on a par "
    "with the parent village."
)

#: What introduces the basis on the card. NOT "On the drawing:", which is what a class's caveat gets:
#: this paragraph is about where the card's claims COME FROM, not about how anything was drawn, and a
#: renderer that decides the lead-in for both cannot tell them apart (settlement-review, 2026-08-29).
BASIS_LEAD = "What this rests on: "


def join(items: list[str]) -> str:
    """`a`, `a and b`, `a, b and c` - the serial comma is not the house style here."""
    if len(items) <= 1:
        return items[0] if items else ""
    return ", ".join(items[:-1]) + " and " + items[-1]


def crop_sentence(present: set[str]) -> str:
    """What this map grows, from the crop classes actually on it. Empty when it grows nothing the
    vocabulary knows - a map with no crops says nothing about crops rather than saying none."""
    groups: dict[str, list[str]] = {}
    for key, (group, display) in CROPS.items():
        if key in present:
            groups.setdefault(group, []).append(display)
    parts = [f"{_CROP_LEAD[g]} {join(groups[g])}." for g in ("wet", "dry", "dike", "water") if g in groups]
    parts += [text for key, text in CROP_SENTENCES.items() if key in present]
    return " ".join(parts)


def size_sentence(kind: Kind, meta: dict[str, Any], houses: int) -> str:
    """The farmhouse count, EXACT, and the population, tilde-marked.

    ONLY THE POPULATION CARRIES THE TILDE (GM 2026-08-29): *"You should not use a ~ for the number of
    farmhouses, because that actually IS an exact map feature - the number of farmhouses listed should
    be whatever is actually displayed on the map itself for hamlets and villages."* The count comes
    from the manifest's own `houses`, so it is not an estimate of anything - it is a statement about
    the sheet in front of the reader, who could sit and count them. The population is an inference
    from it (five to a household) and reads *"population ~75"*, the GM's own phrasing.

    The population comes from the tier's own record where it has one - a town and a city carry
    `meta.population`, because their inhabitants are not a multiple of anybody's farmhouses - and
    otherwise from `l7r.md`'s five to a household. Either may be missing, and then it is not said."""
    parts = []
    if houses:
        parts.append(f"{houses} {kind.houses_noun}")  # no tilde: the reader can count them
    households = meta.get("households")
    population = meta.get("population") or (PER_HOUSEHOLD * households if households else None)
    if population:
        # SAY THE HOUSEHOLDS WHERE THE ARITHMETIC WOULD NOT WORK (settlement-review, 2026-08-29).
        # `settlements.md` permits ~0.7 houses per household at village scale, and Hikari no Sato uses
        # it - 66 drawn against 70 households - so a card reading "66 farmhouses, population ~350"
        # invites a reader to divide and get 5.3. Named only when the two differ, which is rare.
        if households and houses and households != houses and not kind.excludes_farms:
            parts.append(f"about {households} households, population ~{int(population):,}")
        else:
            parts.append(f"population ~{int(population):,}")
    # COMMA, NOT "and" - the GM's own phrasing is a bare apposition: "population ~75".
    return ", ".join(parts)


def where_sentences(scale: str, place: dict[str, str]) -> list[str]:
    """Where this place sits, from what its notes record - and nothing when they record nothing.

    A DISTRICT MEANS A DIFFERENT THING PER TIER, which is why the scale is passed in: a hamlet
    BELONGS to its district, a village IS the head of one. `l7r.md`'s Place Names section (the GM's
    own writing) is what makes the two the same name - *"a village and its district"* - so naming the
    district also names the village a hamlet's lanes lead to."""
    out: list[str] = []
    district, direction = place.get("district"), place.get("district direction")
    if district and scale == "village":
        out.append(f"It is the main village of the {district} district, which takes its name.")
    elif district:
        out.append(f"It belongs to the village district of {district}" + (f", which lies {direction}." if direction else "."))
    if place.get("imperial road"):
        # "runs south" is the road's COURSE; the GM's fact is its POSITION - it lies south of the
        # settlement (settlement-review, 2026-08-29). The notes keep the bearing; the template says
        # what the bearing is of.
        out.append(f"An Imperial road passes {place['imperial road']} of here.")
    if place.get("county"):
        out.append(f"The district is part of {place['county']} county.")
    if place.get("town"):
        out.append(f"The town of {place['town']} lies {place['town direction']}." if place.get("town direction") else f"The town of {place['town']} is the county seat.")
    if place.get("also"):
        out.append(place["also"] if place["also"].endswith(".") else place["also"] + ".")
    return out


#: The class whose destination the GM singled out, and the one class that gets a default annotation.
LANE = "village lane"


def lane_default(scale: str, place: dict[str, str]) -> str:
    """Where this map's lanes lead, when its notes do not say (spec FR-021).

    The GM: *"in our reference hamlet of Inashiro, we can note that the village lane leads towards
    the central village. This should be the default that a village lane leads to when not otherwise
    specified."* A district's name IS its main village's name - `l7r.md`'s Place Names, the GM's own
    writing: *"a village and its district"* - so recording the district is enough to name the place at
    the other end of the track. With no district recorded there is nothing to name and the class's own
    explanation, which already states the default in general terms, stands alone.

    IT NAMES NO DIRECTION, and that is a correction rather than a simplification (settlement-review,
    2026-08-29). The direction a district LIES in is not the direction its track LEAVES in: on
    Akagahara and Ikegami the connector runs SOUTH, to the Imperial road the GM put there, while
    Hoshigaoka lies east and north-east along it. Composing the sentence from `district direction`
    made both of those pages contradict their own ink. A route off the edge of the sheet is not
    something the map knows, so the default states only the destination - and a map that DOES know its
    route says so in its own `### Features` entry, which always wins.

    It names the CONNECTOR too, not "the lanes": the class lights every lane on the sheet, and eight
    of Inashiro's nine are three-foot stragglers between the farmsteads that lead nowhere at all."""
    district = place.get("district")
    if scale != "hamlet" or not district:
        return ""
    return f"The connector track leads out of the hamlet toward {district}, the main village of the district it belongs to; the lanes between the farmsteads feed it."


def dwellings_shown(manifest: dict[str, Any], kind: Kind) -> int:
    """How many dwellings this map DRAWS that the tier is willing to count.

    A hamlet and a village count `houses`: every one is a household of the settlement, and the sheet
    holds all of them. A town and a city count something else entirely (GM 2026-08-29): they *"are
    surrounded by significant farm fields and farmer populations, which are deliberately not all
    rendered on the map. Therefore, that number should not be included."*

    **`houses` IS THE FARM RING at those tiers**, and getting that wrong is the whole trap. The first
    cut of this function counted `houses` and subtracted the few standing inside a drawn
    `agricultural_district` - which looked like it worked (Tango 273 -> 260) while counting nothing but
    farmhouses, exactly the number the GM said to leave out (settlement-review, 2026-08-29). A town's
    and a city's non-farm dwellings live in `buildings`, under `DWELLING_KINDS` - the same set the
    capacity checks use, so there is one definition of "a dwelling" in the engine rather than two.

    The arithmetic confirms which list the tiers mean: Minami's 520 non-farm dwellings x 5 to a
    household is its declared 2,600 exactly, and Nagahara's 600 x 5 is its 3,000 - farmers excluded,
    which is the city convention the GM described. (A town's declared figure counts the drawn
    farmhouses too; see `KINDS["town"].population_note` and the open question recorded with it.)"""
    if not kind.excludes_farms:
        return len(manifest.get("houses") or [])
    return sum(1 for b in (manifest.get("buildings") or []) if b.get("kind") in DWELLING_KINDS)


def place_card(meta: dict[str, Any], present: set[str], notes: MapNotes, manifest: dict[str, Any]) -> dict[str, Any] | None:
    """The card behind the title placard, or None for a tier the vocabulary does not describe.

    Shaped like a class entry on purpose: the page opens it through the same modal, so there is one
    renderer and one set of behaviors rather than a second dialog to keep in step."""
    kind = KINDS.get(str(meta.get("scale") or ""))
    if kind is None:
        return None
    name = str(meta.get("name") or "This settlement")
    size = size_sentence(kind, meta, dwellings_shown(manifest, kind))
    what = f"{name} is a {kind.noun}: {kind.what}"
    if size:
        what = f"{name} is a {kind.noun} of {size}: {kind.what}"
    what = " ".join([what, *(text for key, text in COLLISIONS.items() if key in present)])
    # WHERE IT IS COMES BEFORE WHAT IT GROWS (settlement-review round 6, 2026-08-29). A player wants
    # the place located before they want its crops, and with the crops first the district sentence
    # opened on an "It" whose nearest nouns were "weeds" and "ground".
    why = " ".join(x for x in [*where_sentences(str(meta.get("scale")), notes.place), crop_sentence(present), kind.population_note] if x)
    keys = research_sources(ENTRY)
    return {
        "name": name,
        "what": what,
        "why": why,
        "label": "accurate",
        "lead": "",  # the card never announces accuracy either (spec FR-001)
        "caveat": BASIS_LEAD + BASIS if kind.noun == "hamlet" else "",
        "sources": keys,
        "refs": citations(keys),
        "entry": ENTRY,
        "siblings": [],
    }
