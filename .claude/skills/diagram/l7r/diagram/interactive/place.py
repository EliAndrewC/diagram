"""The place card: what a reader gets for clicking the settlement's own title placard (feature 154).

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

from .notes import MapNotes
from .sources import citations, research_sources

#: `l7r.md`, "The Median Domain": ~5 inhabitants per household, and a hamlet of 10-20 households
#: holds 50-100. The tiers that record a population outright (towns, cities) use theirs instead.
PER_HOUSEHOLD = 5

#: `l7r.md`'s median-domain table, for the one ranking the card is allowed to make - of TIERS.
HAMLETS_PER_DOMAIN, VILLAGES_PER_DOMAIN, HAMLET_SHARE = 1296, 216, "40%"


@dataclass(frozen=True)
class Kind:
    """What one tier IS, in terms a player can use at the table."""

    noun: str
    what: str  # the sentence that follows "<Name> is a <noun>"
    # What to call the dwellings the map draws, or None to say nothing about them. A hamlet's and a
    # village's houses ARE its households - the manifest's count and `meta.households` agree - so the
    # figure means something. A town's and a city's do not: a settlement of 3,000 inhabitants is drawn
    # with a few hundred representative dwellings, and printing "~273 dwellings" beside "population
    # ~3,000" tells a reader something false about the place rather than about the drawing.
    houses_noun: str | None


#: Keyed by `meta.scale`. Written from `l7r.md` (a hamlet "belongs to a village district and is
#: overseen by a village headsman who lives in the main village and not in the hamlet"; "county towns
#: are the lowest level at which samurai live") and from `settlements.md`'s tier rules.
KINDS: dict[str, Kind] = {
    "hamlet": Kind(
        "hamlet",
        "a small outlying farming community belonging to a village district. Like every hamlet it has no headman of its own - its overseer, the district headman, lives in the main village - no shrine, no tax-free plot and no burial ground; its dead go to the district's ground.",
        "farmhouses",
    ),
    "village": Kind(
        "village",
        "the main village of a village district: the seat of the headman who oversees the district's outlying hamlets, with its own shrine, its tax-free plots and the burial ground the whole district uses. Like every village district it is peasant-only - no samurai live here.",
        "farmhouses",
    ),
    "town": Kind(
        "town",
        "a county town: the lowest level of Rokugani society at which samurai live, and the lowest that has resident merchants, which is why the farmers of the surrounding districts come in for market day. The county magistrate holds court here.",
        None,
    ),
    "city": Kind(
        "city",
        "a provincial city: the seat of a province's governor and its ministries, and a market the whole province turns toward.",
        None,
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

#: The `### Place` keys the card understands. Anything else an author writes is ignored rather than
#: guessed at - the block stays a place to record things this module has not learned to use yet.
PLACE_KEYS = ("district", "district direction", "county", "imperial road", "town", "town direction", "also")

#: The research entry the card is written FROM, in the form `sources.py` parses - so the card's
#: references are READ FROM THE RECORD at page-write time, exactly like a class's, rather than being
#: a second list here that could drift from it.
ENTRY = "research/archetypes.md - 'What a settlement IS'"

#: The basis the card owes its reader (spec FR-008a). Two statements rest on setting canon where the
#: historical record does not back them, and the GM's rule is that a liberty is called out.
BASIS = (
    f"A hamlet is the most numerous kind of settlement in a domain - about {HAMLETS_PER_DOMAIN:,} of them "
    f"to {VILLAGES_PER_DOMAIN} villages, holding about {HAMLET_SHARE} of its inhabitants. That is the setting's own "
    "arithmetic rather than a historical finding: the research pass found no source that ranks settlement forms "
    "by frequency, and none for which KIND of hamlet is commonest either, so this map claims neither. "
    "Rokugan is also simpler than history in one respect stated above - that a hamlet never has a headman of its "
    "own is the setting's rule, where the Edo record has branch hamlets that did."
)


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
    if houses and kind.houses_noun:
        parts.append(f"{houses} {kind.houses_noun}")  # no tilde: the reader can count them
    population = meta.get("population") or (PER_HOUSEHOLD * meta["households"] if meta.get("households") else None)
    if population:
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
        out.append(f"An Imperial road runs {place['imperial road']}.")
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
    explanation, which already states the default in general terms, stands alone."""
    district, direction = place.get("district"), place.get("district direction")
    if scale != "hamlet" or not district:
        return ""
    return f"The lanes lead {direction + ' ' if direction else ''}to {district}, the main village of the district this hamlet belongs to."


def place_card(meta: dict[str, Any], houses: int, present: set[str], notes: MapNotes) -> dict[str, Any] | None:
    """The card behind the title placard, or None for a tier the vocabulary does not describe.

    Shaped like a class entry on purpose: the page opens it through the same modal, so there is one
    renderer and one set of behaviors rather than a second dialog to keep in step."""
    kind = KINDS.get(str(meta.get("scale") or ""))
    if kind is None:
        return None
    name = str(meta.get("name") or "This settlement")
    size = size_sentence(kind, meta, houses)
    what = f"{name} is a {kind.noun}: {kind.what}"
    if size:
        what = f"{name} is a {kind.noun} of {size}: {kind.what}"
    why = " ".join(x for x in [crop_sentence(present), *where_sentences(str(meta.get("scale")), notes.place)] if x)
    keys = research_sources(ENTRY)
    return {
        "name": name,
        "what": what,
        "why": why,
        "label": "accurate",
        "lead": "",  # the card never announces accuracy either (spec FR-001)
        "caveat": BASIS if kind.noun == "hamlet" else "",
        "sources": keys,
        "refs": citations(keys),
        "entry": ENTRY,
        "siblings": [],
    }
