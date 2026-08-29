"""The feature-class vocabulary of the interactive map, and what each class tells its reader.

Feature 134 (GM 2026-08-27): a player mousing over the HTML map highlights every feature OF A KIND,
and a click opens a modal that says what the kind is, why it stands where it does, whether that is
historically ACCURATE, a deliberate DEVIATION or a GUESS (constitution XII), and which research
entries it rests on. This module is the ONE place the vocabulary lives: the engine tags ink with a
class KEY (`Settlement.add(..., cls=...)`), the page reads the entry for every key present on the
map, and nothing hamlet-specific is written anywhere - the explanations are per KIND, not per map.

The vocabulary is the spec's FR-007 table (`specs/134-interactive-html-map/spec.md`), verbatim:
those rows are the GM's judgment calls, listed so any can be overruled BY NAME. The distinguishing
text is keyed by SIBLING PAIR and is SYMMETRIC (if A names B, B names A - the fidelity review's
round-1 finding), and the page includes a sibling paragraph only when BOTH classes are on the map,
so a hamlet with no woodland commons never claims the windbreak differs from one.

Every explanation is written FROM a `research/` entry and carries that entry's label; where the
record is silent the entry says GUESS in so many words. `research/README.md`: "an entry that
presents reasoning as a finding is the one failure".

`NOT_HIGHLIGHTED` is the pseudo-class for ink the GM has ruled OUT of highlighting (FR-002:
"judgment calls to make about what things get highlighted and which things do not"). It is a
ruling, not an omission: the census in `page.py` reports only ink that carries NO class at all, so
a `"-"` tag keeps the frame off the report while a forgotten tag still fails the gate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Label = Literal["accurate", "deviation", "guess"]

#: The labels the PAGE announces. `accurate` is not among them, and that is the whole of feature 156's
#: first change (GM 2026-08-29): *"I would like to not explicitly say that things are historically
#: accurate when they are because I want the presumption to be that things are always historically
#: accurate unless stated otherwise. In other words, we should call out liberties that we have taken."*
#: A claim made about nearly every feature on the map carries no information; a liberty does. The
#: three-way classification itself is UNCHANGED and still recorded on every class (constitution XII) -
#: only its presentation changed, and it still reaches the page as `data-label`.
ANNOUNCED: frozenset[Label] = frozenset({"deviation", "guess"})

#: The pseudo-class of ink ruled out of highlighting. Recorded, never wrapped, never reported.
NOT_HIGHLIGHTED = "-"

#: The reserved pseudo-class of the TITLE PLACARD (feature 156). Not a row of `CLASSES` - it is not a
#: kind of feature and has no research entry of its own - but a key the census and the page both know,
#: so the placard is highlightable, clickable, and never reported as ink nobody ruled on. Its modal is
#: built per map by `place.py` from the manifest, the setting's canon and the map's own notes file.
PLACE = "place"

#: Each ruling that put a kind of ink on the not-highlighted list: (what, who, when, why).
NOT_HIGHLIGHTED_RULINGS: tuple[tuple[str, str, str, str], ...] = (
    ("the background sheet", "the spec (FR-002)", "2026-08-27", "not a feature of the place"),
    ("the scale bar and its captions", "the spec (FR-002)", "2026-08-27", "map furniture, not a feature"),
)

#: A ruling that was OVERTURNED, kept beside the list rather than deleted from it - the record should
#: show that a decision was made and then remade, not quietly lose one: (what, who, when, why).
NOT_HIGHLIGHTED_OVERTURNED: tuple[tuple[str, str, str, str], ...] = (
    (
        "the title placard and its text",
        "the GM",
        "2026-08-29",
        'ruled map furniture on 2026-08-27 (feature 134 FR-002) and overturned by the GM in feature 156: "I would like to be able to click on the title card for a settlement and then pull up an explanation of the type of settlement that this is." The placard now carries the reserved class `place`; the scale bar beside it keeps its ruling, having nothing to say.',
    ),
)


@dataclass(frozen=True)
class FeatureClass:
    """One highlightable KIND of thing on the map, and what its modal says."""

    key: str  # the tag the engine writes; also the CSS token (`f-<key>` after slugging)
    name: str  # the class's display name - FR-007's row name, verbatim
    covers: str  # which manifest features it draws - documentation for the next reader
    what: str  # what the thing IS
    why: str  # why it stands where it does on the map
    label: Label  # constitution XII: accurate | deviation | guess
    label_note: str  # the one line that justifies the label (a deviation says what deviates; a guess says what is silent)
    sources: tuple[str, ...]  # `research/SOURCES.md` keys, or ("not recorded",)
    entry: str  # the research/ entry (file + heading) the text was written FROM
    # THE LIBERTY HALF of `label_note`, and only that (feature 156, GM 2026-08-29). An `accurate`
    # class's note usually says two things at once - which parts are READ, and which parts are a
    # drawing convention, a derived number or a sub-guess. The first half is the accuracy claim in
    # other words and the page no longer prints it; the second is exactly what the GM asked to have
    # called out, so it survives, shown AFTER the what and the why instead of ahead of them. Always a
    # verbatim substring of `label_note` (a registry test proves it, so the two cannot drift), and
    # empty both for a class whose note discloses no liberty at all and for every `deviation` or
    # `guess`, whose lead sentence already carries theirs.
    caveat: str = ""
    siblings: dict[str, str] = field(default_factory=dict)  # sibling key -> how THIS class differs from it


_LABEL_WORDS: dict[Label, str] = {
    "accurate": "historically accurate",
    "deviation": "a deliberate deviation",
    "guess": "a guess",
}


def label_phrase(label: Label) -> str:
    """The words the modal uses for a label - constitution XII's three, in the GM's own phrasing."""
    return _LABEL_WORDS[label]


def lead_sentence(label: Label, note: str) -> str:
    """The sentence a modal OPENS with, or "" when there is nothing to announce.

    Only a liberty is announced (`ANNOUNCED`). An `accurate` class returns "" and its modal leads
    with what the feature IS - the presumption of accuracy the GM asked for, which is enforced HERE,
    at the one place the sentence is built, rather than by asking every caller to remember it."""
    if label not in ANNOUNCED:
        return ""
    return "This is " + _LABEL_WORDS[label] + (" - " + note if note else ".")


def _c(**kw: object) -> FeatureClass:
    return FeatureClass(**kw)  # type: ignore[arg-type]


# The sibling texts, written once per PAIR and installed in both directions below. Each is how the
# FIRST-named class differs from the second. SINCE 2026-08-28 THE PAGE DOES NOT SHOW THEM: the GM
# asked for the linkage as "Not to be confused with the X" LINKS (hover lights X, click opens X's
# modal) so each modal's text stays its own; the texts remain here as the record of what
# distinguishes each pair, to be folded into the classes' own explanations as those lengthen.
#: One text for all four rolled crop-dike values - the distinction from the perimeter dike is identical
#: whichever crop the knob rolled, and four copies is four chances for a later edit to fix one and leave
#: three (settlement-review, 2026-08-29). The walk figures are measured on Kuwabata: the crop dike loops
#: run a median 815 ft (3.1 min at 260 ft/min), the perimeter dike 4,591 ft along its CREST
#: (18 min) - the walkable top of the bank, which is the thing you would walk. The first
#: version of this line said half an hour, on the manifest's `outline`: that is the band POLYGON, outer
#: face plus inner face returned, 1.99x the crest, so it counted the same walk twice
#: (settlement-review round 2).
_CROP_VS_PERIMETER = "The crop dike is the wall AROUND one pond - six to ten meters of dredged mud, planted, and part of the loop that feeds the fish. The perimeter dike is the polder's own embankment, the one that holds the river off the whole settlement. You can walk a crop dike round in about three minutes; the polder's takes the better part of twenty, and it is the reason the hamlet is dry."

#: The near-homonym the GM's own list did not name, and the pair a reader is likeliest to confuse on a
#: dike-pond map: both are "sluice", both are boards in a cut (settlement-review, 2026-08-29).
_POND_VS_POLDER_SLUICE = "Both are boards in a cut, and the difference is which wall they sit in. A pond sluice is a gate in a fish pond's own dike, worked by the household that farms that pond - it moves water between pond and channel. A sluice gate is set in the POLDER dike, and it is what lets water in or out of the settlement as a whole; nobody opens one on their own account."

_PAIRS: dict[tuple[str, str], str] = {
    (
        "pond sluice",
        "sluice gate",
    ): _POND_VS_POLDER_SLUICE,
    (
        "field ditch",
        "pond sluice",
    ): "A field ditch carries water through the CROP - it is the paddy fabric's own plumbing, cut between the plots and crossed by a plank. A pond sluice is a gate in a dike: a cut closed with boards that lets one fish pond take water in at its high side and let it out at its low side. The ditch moves water along; the sluice decides whether it moves at all.",
    (
        "mulberry dike",
        "perimeter dike",
    ): _CROP_VS_PERIMETER,
    (
        "sugarcane dike",
        "perimeter dike",
    ): _CROP_VS_PERIMETER,
    (
        "banana dike",
        "perimeter dike",
    ): _CROP_VS_PERIMETER,
    (
        "fruit dike",
        "perimeter dike",
    ): _CROP_VS_PERIMETER,
    (
        "farmhouse",
        "storage shed",
    ): "The farmhouse is the dwelling; a storage shed is a roofed outbuilding for grain, straw, tools and fuel - Sugiura's 1972 survey counted 4.4 outbuildings per household, and the sheds drawn here stand for that inventory, not for a second house.",
    (
        "farmhouse",
        "byre",
    ): "A farmhouse shelters the household; a byre shelters its draft animal. In the temperate lowland this map draws the two are separate buildings - the attached stable wing (magariya) is a cold-country form and is not drawn.",
    (
        "storage shed",
        "byre",
    ): "A storage shed holds things; a byre holds an ox or a water buffalo. The GM's own line: a storage shed attached to a farmhouse is different from the animal sheds where the animals are kept - so the two never highlight together.",
    (
        "byre",
        "hen coop",
    ): "The byre is for the one draft animal a household could keep; the hen coop is a small ground-level roost for a few chickens - the Qimin Yaoshu says to build the roost as an enclosure on the ground with a perch inside, because birds left to the trees sicken.",
    (
        "threshing yard",
        "garden",
    ): "The threshing yard is bare, swept, tamped earth - a work floor for drying and threshing the harvest; the kitchen garden is tilled soil in planted rows. Both want sun, which is why neither is put in a neighbor's shadow.",
    ("garden", "millet"): "The dooryard garden grows the household's vegetables beside the house; the millet plot is a field crop on the dry hem above the paddy, worked in rows.",
    ("garden", "buckwheat"): "The dooryard garden grows the household's vegetables beside the house; the buckwheat plot is a field crop on the dry hem above the paddy, worked in rows.",
    ("garden", "barley"): "The dooryard garden grows the household's vegetables beside the house; the barley plot is a field crop on the dry hem above the paddy, worked in rows.",
    (
        "privy",
        "manure heap",
    ): "The privy is the one-room outhouse; the manure heap is where its night soil and the byre's litter are composted before going onto the fields. They stand together because they were one cluster - in Han China the latrine sat over the pigsty and drained to the cesspool.",
    (
        "persimmon",
        "copse",
    ): "The persimmon is one household's dooryard tree, planted beside the house for its fruit and its summer shade; the copse is village greenery standing in the open ground among the houses.",
    (
        "homestead bamboo",
        "shared bamboo grove",
    ): "This stand belongs to one household - the damp north or west strip of its plot, cut for the household's own baskets, poles and fences. A shared grove is a take-yabu held by the hamlet at the field margin and cut like a coppice, under the village's rules on who may cut and when.",
    (
        "windbreak",
        "copse",
    ): "The windbreak is a planted shelter belt - the fengshui back grove - kept on the windward, high side of the cluster to break the winter monsoon, cedar-backed and dense. A copse is looser fruit-tree and broadleaf greenery in the gaps among the houses, with no sheltering purpose; the households used it for shade and fruit, not as a wall against the wind.",
    (
        "windbreak",
        "woodland commons",
    ): "The windbreak belongs to the settlement as shelter and was kept standing - a village would not cut its own wind wall. The woodland commons was cut: an iriai wood coppiced on a 10-30 year cycle for firewood, forage and leaf litter, under customary rules on who might cut, when, and how much.",
    (
        "copse",
        "woodland commons",
    ): "The copse is greenery among the houses, used for shade and fruit; the woodland commons is a managed coppice on the slope above the paddy, cut on a cycle for fuel and fertilizer under the village's own rules.",
    (
        "scrub and rough grazing",
        "marsh",
    ): "Scrub is dry ground - cut-over fuel and fodder land with grass and the odd scraggly pine, grazed and cut; marsh is the undrained wet ground that wet rice was reclaimed from and that stays reed wetland where reclamation stopped.",
    ("marsh", "pond"): "Marsh is reed wetland on undrained low ground; the pond is an engineered tameike - open water behind an earthen dike, sitting above the fields it waters.",
    (
        "paddy",
        "wet paddy",
    ): "Both are flooded rice basins and both grow the same crop; what differs is the ground under them. An ordinary paddy sits where the water can be let out again, so it dries between crops and can take a winter crop. A wet paddy - shitsuden - is on ground that will not drain, so it stands waterlogged out of season too, works harder, and yields less.",
    ("paddy", "millet"): "A paddy is a basin flooded under a shallow sheet of water for wet rice; millet is a dry crop on the higher, well-drained hem the water cannot command.",
    ("paddy", "buckwheat"): "A paddy is a basin flooded under a shallow sheet of water for wet rice; buckwheat is a dry crop on the higher, well-drained hem the water cannot command.",
    ("paddy", "barley"): "A paddy is a basin flooded under a shallow sheet of water for wet rice; barley is a dry crop on the higher, well-drained hem the water cannot command.",
    ("paddy", "fallow"): "A paddy is in crop and under water; a fallow patch is ground resting out of crop for the season.",
    (
        "bund",
        "bund beans",
    ): "The bund is the earthwork - the puddled-mud ridge between two basins, re-plastered every spring so each paddy holds its water. The beans are the crop planted along its top (azemame): the bund is soil, the beans are what grows on it, so each highlights on its own.",
    (
        "millet",
        "buckwheat",
    ): "Millet is a summer grain; buckwheat is a short-season crop sown late and taken in autumn, tolerant of poor soil. Both sit on the dry hem; the furrows run the same way, the crop differs.",
    ("millet", "barley"): "Millet is a summer grain; barley is the winter grain of the dry hem, sown in autumn and taken before the rice is transplanted. Both sit on the dry hem; the crop differs.",
    ("buckwheat", "barley"): "Buckwheat is a short-season late crop for thin soil; barley is the winter grain, sown in autumn and taken in early summer. Both sit on the dry hem; the crop differs.",
    ("millet", "fallow"): "The millet plot is in crop; a fallow patch rests out of crop for the season.",
    ("buckwheat", "fallow"): "The buckwheat plot is in crop; a fallow patch rests out of crop for the season.",
    ("barley", "fallow"): "The barley plot is in crop; a fallow patch rests out of crop for the season.",
    (
        "stream",
        "field ditch",
    ): "The stream is a natural brook - about two meters across in reality, the widest water on a hamlet map short of the pond. A field ditch is dug: a hairline in reality (about a third of a meter, one three-hundredth of the paddy it waters), drawn at true size.",
    ("stream", "pond"): "The stream is running water off the high ground; the pond is standing water held behind a dike, fed by the stream and let out through one outlet.",
    (
        "pond",
        "field pond",
    ): "The pond is the tameike - the reservoir behind a dike at the field's foot, the hamlet's water store. A field pond is a small open-water pocket sunk into one low paddy, the one obstacle that genuinely belongs in the wet middle of a flooded field.",
    ("paddy", "field pond"): "The paddy is the flooded rice basin; the field pond is a small pocket of open water sunk into one low plot, reed-fringed, drawn where the ground pools.",
    (
        "field ditch",
        "pond",
    ): "The ditches distribute the water; the pond stores it. One outlet leaves the pond and branches into the head race and the laterals - the smallest ditches were often counted as part of the paddy they serve.",
    (
        "soy",
        "millet",
    ): "Soybean and millet are both summer crops of the dry hem; the bean fixes its own nitrogen and was as often grown along the bunds (azemame) as in a plot of its own. Both sit on the dry hem; the crop differs.",
    ("soy", "buckwheat"): "Soybean is a summer crop that fixes its own nitrogen; buckwheat is the short-season late crop for thin soil. Both sit on the dry hem; the crop differs.",
    ("soy", "barley"): "Soybean is the summer crop; barley the winter grain of the same hem, sown in autumn and taken before the rice is transplanted. The crop differs, the ground is the same.",
    ("soy", "paddy"): "A paddy is a basin flooded under a shallow sheet of water for wet rice; soybean is a dry crop on the higher, well-drained hem the water cannot command.",
    ("soy", "fallow"): "The soybean plot is in crop; a fallow patch rests out of crop for the season.",
    ("soy", "garden"): "The dooryard garden grows the household's vegetables beside the house; the soybean plot is a field crop on the dry hem above the paddy, worked in rows.",
    (
        "soy",
        "bund beans",
    ): "The same plant in two places: a soybean PLOT is a field crop of its own on the dry hem; the bund beans are soybeans planted along the tops of the paddy bunds, taking a second crop from ground that would otherwise grow weeds.",
    (
        "grave island",
        "paddy",
    ): "The paddy is the flooded basin; the grave island is a small raised earthen mound with a few stone markers standing in it, the paddy tiling around. Graves in the wet middle are the north-China and Japanese look; in the rice south the dead went to the slope - so this one is drawn rarely, on purpose.",
    (
        "field rock",
        "paddy",
    ): "The paddy is the flooded basin; the rock is a bedrock outcrop the field could not clear, a cluster of boulders the plots wrap around - a terrace feature, absent on alluvial ground.",
    ("grave island", "field rock"): "The grave island is made ground - a mound raised for the dead; the rock is ground that was never made - bedrock the terrace risers had to wrap around.",
}


_DEFS: tuple[FeatureClass, ...] = (
    _c(
        key="farmhouse",
        name="farmhouse",
        covers="`houses` - the dwelling of each household",
        what="The dwelling of one farming household: a thatched minka, its ridge on the long axis, standing on the slightly raised ground the homesteads share, its work yard and garden beside it and, where a farm stands alone, its own yashikirin sheltering it.",
        why="A house in a nucleated hamlet is reached by a lane and stands close to the paddy - up against it, but never on the bund. The lanes between farmsteads are trodden by the households already living there.",
        label="accurate",
        label_note="Placement and form follow the read record; the setback from the paddy is DERIVED - no source states it in feet - so it is set at the near end of what the read bounds allow, close enough that the household works its own ground.",
        caveat="the setback from the paddy is DERIVED - no source states it in feet - so it is set at the near end of what the read bounds allow, close enough that the household works its own ground.",
        sources=("sugiura-1973-fuzoku",),
        entry="research/homesteads.md - 'What stood on a farmstead', 'How close does a farmhouse stand to the paddy', 'Is every farmhouse reached by a lane'",
    ),
    _c(
        key="storage shed",
        name="storage shed",
        covers="`houses[].shed` (the lean-to against a farmhouse) and `farm_sheds` (the detached sheds of the same household)",
        what="A roofed outbuilding for storage - grain, straw, tools, fuel. Some stand as a lean-to against the farmhouse, some free in the yard; storage either way.",
        why="A July 1972 survey of 87 households in three Miyagi hamlets counted 4.4 outbuildings per household - firewood shed, straw shed, barn, work shed, storehouse - so a farmstead with only its house would be the anomaly. The count drawn here is a band below that snow-country figure, because the temperate lowland hamlet this map draws kept fewer.",
        label="accurate",
        label_note="Presence and prevalence read (Sugiura 1973); the drawn count per household is deliberately set below the source's Tohoku figure, which is a colder and better-stocked district than this one.",
        caveat="the drawn count per household is deliberately set below the source's Tohoku figure, which is a colder and better-stocked district than this one.",
        sources=("sugiura-1973-fuzoku",),
        entry="research/homesteads.md - 'What stood on a farmstead - the inventory, with numbers'",
    ),
    _c(
        key="byre",
        name="byre",
        covers="`byres` - the draft-animal sheds",
        what="An open-fronted shed for a household's ox or water buffalo - a roof carried on posts over a shaded stall, standing among the homesteads.",
        why="Most farmsteads kept a draft animal or two, and the vernacular put the animal far closer to the house and the well than a European barn would. Where a byre is shared it stands in a courtyard between the homesteads it serves.",
        label="accurate",
        label_note="The separate byre is the temperate reading of the record; the attached stable wing (magariya) is a cold-country form and is deliberately not drawn.",
        caveat="the attached stable wing (magariya) is a cold-country form and is deliberately not drawn.",
        sources=("cambridge-animals-china",),
        entry="research/homesteads.md - 'May a byre stand beside a wellhead?', 'What stood on a farmstead'",
    ),
    _c(
        key="threshing yard",
        name="threshing yard",
        covers="`threshing_yards`",
        what="A small tamped-earth work floor beside each farmhouse - swept bare, with a straw drying mat and a little rack for hanging sheaves. Households measured it in straw mats: 40 to 60 of them, two mats to the tsubo, so an ordinary yard is 20 to 30 tsubo and a few run past 50.",
        why="Threshing and drying were done per household, in the yard, and the yard needs sun: a thatched roof pitched at 45 degrees puts a minka's ridge at 20-22 feet, so no yard is placed in the shadow band south of a neighbor's wall. Its SIZE follows the crop the household must dry, which is why every yard on this map is different: each is rolled from a right-skewed spread about 18 tsubo (59.5 sq m), correlated with the household - a large farm overwhelmingly has a large yard, and the occasional mismatch is a fact about that farmstead.",
        label="accurate",
        label_note="The size band and the spread's shape are read - Kitamoto's mat counts, and the lognormal that fits Kamikanai's 1771 house histogram; the wet-rice CENTER is interpolated from the crop (rice is field-dried on racks first, so a paddy household needs less floor than the barley district the mat counts come from), and the sun corridor is derived from the read roof pitch.",
        caveat="the wet-rice CENTER is interpolated from the crop (rice is field-dried on racks first, so a paddy household needs less floor than the barley district the mat counts come from), and the sun corridor is derived from the read roof pitch.",
        sources=("not recorded",),
        entry="research/homesteads.md - 'How big was the work yard, and how did the sizes spread'; 'The threshing yard's sun, and how far a farmhouse shades'",
    ),
    _c(
        key="garden",
        name="garden",
        covers="`gardens`",
        what="The household's kitchen garden: a tilled bed in planted rows of greens, beside the house.",
        why="A dooryard garden fed the household and, like the yard, wants light - beds are kept out of a neighbor's shadow to the south and clear of the windbreak's afternoon shade to the west.",
        label="accurate",
        label_note="Presence and the sun rule are read; the record fixes the bed's AREA and that it is hand-worked and irregular, but gives no proportion or row count, so those are drawn to read as a worked kitchen bed at this scale.",
        caveat="the record fixes the bed's AREA and that it is hand-worked and irregular, but gives no proportion or row count, so those are drawn to read as a worked kitchen bed at this scale.",
        sources=("not recorded",),
        entry="research/homesteads.md - 'The garden's sun, and how far the windbreak shades'; 'The threshing yard's sun, and how far a farmhouse shades' (the garden rule is derived from it)",
    ),
    _c(
        key="privy",
        name="privy",
        covers="`farm_fixtures[kind=privy]`",
        what="The household privy - on a farm, the urinal and the privy were one small building standing apart from the main house.",
        why="Near-universal: the Nipponica entry calls the detached privy the norm, and the 1972 survey counted one on 87 of 100 households. Its seat is rolled from three attested positions - by the back door, at the gate, or by the shed.",
        label="accurate",
        label_note="Presence and the three seats are read (kotobank, sinyoken); the 6 x 6 ft footprint is a GUESS - the one sizing page is dead.",
        caveat="the 6 x 6 ft footprint is a GUESS - the one sizing page is dead.",
        sources=("kotobank-benjo", "sinyoken-madori", "sugiura-1973-fuzoku"),
        entry="research/homesteads.md - 'The farmstead's fixtures'",
    ),
    _c(
        key="woodpile",
        name="woodpile",
        covers="`farm_fixtures[kind=woodpile]`",
        what="The household's fuel: split logs stacked head-high against a wall, out of the rain.",
        why="Firewood and charcoal were the fuel, and a shed for them stood on three farms in four; the open stack under the eaves is the cheaper and older form, and the one drawn.",
        label="guess",
        label_note="The firewood SHED is read (Boso-no-Mura); where the open STACK stood relative to the house was found nowhere - the back wall or the shed's outer wall is a guess, and the stack's height is modern practice.",
        sources=("boso-no-mura-kigoya", "326woods-stack", "sugiura-1973-fuzoku"),
        entry="research/homesteads.md - 'The farmstead's fixtures'",
    ),
    _c(
        key="manure heap",
        name="manure heap",
        covers="`farm_fixtures[kind=manure]`",
        what="The muck heap: night soil and byre litter composting before they go onto the fields.",
        why="Night soil was fermented in buried jars or plastered pits and spread as fertilizer; the heap is drawn beyond the privy because the two were one cluster - in Han China the latrine stood over the pigsty and drained to the cesspool.",
        label="guess",
        label_note="The practice is read (jawiki, the Art Institute's Han model); the heap's PLACE on the farm and its size are guesses - the pages describe the pit, not where it stood.",
        sources=("jawiki-koedame", "artic-pigsty-latrine"),
        entry="research/homesteads.md - 'The farmstead's fixtures'",
    ),
    _c(
        key="bathhouse",
        name="bathhouse",
        covers="`farm_fixtures[kind=bath]`",
        what="A small bath shed - the iron goemon-buro tub under its own roof.",
        why="The cauldron bath was widely used in self-sufficient farm villages; the 1972 survey found a bath shed on about three farms in ten and a bath inside the house on half, so only the shed share is drawn and the rest bathe indoors, unseen.",
        label="guess",
        label_note="Use is read (Mizumaki museum); where the shed stood was found nowhere - the back wall or a flank is a guess, and so is the 6 x 6 ft size.",
        sources=("mizumaki-goemonburo", "sugiura-1973-fuzoku"),
        entry="research/homesteads.md - 'The farmstead's fixtures'",
    ),
    _c(
        key="hen coop",
        name="hen coop",
        covers="`farm_fixtures[kind=coop]`",
        what="A small square roost for a few chickens, on the flank of the yard.",
        why="Farmers kept a pig and some chickens in the yard along with a draft animal; the Qimin Yaoshu says to build the roost as a ground enclosure with a perch, because birds left to the trees sicken.",
        label="guess",
        label_note="The coop's existence and ground form are read (Cambridge, the Qimin Yaoshu, the Zhengzhou coop); the household proportion, the 5 x 5 ft size and the seat are guesses bounded by 'most regions'.",
        sources=("cambridge-animals-china", "qimin-yaoshu-yangji", "pitt-zhengzhou-coop"),
        entry="research/homesteads.md - 'The farmstead's fixtures'",
    ),
    _c(
        key="household shrine",
        name="household shrine",
        covers="`farm_fixtures[kind=shrine]` - the hokora",
        what="A household's own small shrine - a stone or wooden hokora in a corner of the plot, drawn vermilion with a torii before its door.",
        why="In some regions every house had one, in others only certain old families; the GM ruled for the old-families pattern here - rare, and notable when it appears - so the count is capped at about three households in a hundred. It stands in the plot's northwest, northeast or southwest corner, all three attested.",
        label="deviation",
        label_note="Presence, rarity and corner are read; the glyph is drawn at 6 x 6 ft against a measured stone shrine of about 1.3 ft - a deliberate deviation for legibility.",
        sources=("tokushima-yashikigami", "jawiki-yashikigami", "kameyama-yashikigami", "sugiura-1973-fuzoku"),
        entry="research/homesteads.md - 'The farmstead's fixtures'",
    ),
    _c(
        key="persimmon",
        name="persimmon",
        covers="`persimmons` - the dooryard persimmon tree",
        what="The household's persimmon tree beside the house, drawn a yellower green than the groves with four fruit dots - the map's convention for naming the tree, not a season.",
        why="A persimmon stood in every dooryard: the Edo agronomist Miyazaki Yasusada urged planting them around the homestead, and the tree shades the house in summer, so it stands beside it.",
        label="guess",
        label_note="Presence and the beside-the-house placement are read (toyoko, uekipedia); WHICH side and the 18 ft crown are guesses - the crown width was found nowhere.",
        sources=("toyoko-kaki", "uekipedia-kaki"),
        entry="research/homesteads.md - 'The farmstead's fixtures'",
    ),
    _c(
        key="homestead bamboo",
        name="homestead bamboo",
        covers="`bamboo_stands[role=homestead]`",
        what="A household's own bamboo stand on the damp north or west strip of its plot - a clonal thicket with a hard edge, drawn as paired culm strokes with a leafy fork.",
        why="Below the frost line bamboo was a matter of course in a lowland paddy hamlet - baskets, poles, fences, fans, food wrappings - and the shady, always-damp service side of the yashiki was where it stood. A cold upland hamlet may have none; whether a hamlet has bamboo is rolled per settlement.",
        label="deviation",
        label_note="Presence and place are read; a culm is inches across and cannot be drawn at one foot per pixel, so the stand's extent is to scale and the marks inside it are symbolic - the convention Japan's own topographic legend uses.",
        sources=("not recorded",),
        entry="research/vegetation.md - 'Bamboo: how common, where it stood, and how to show it'",
    ),
    _c(
        key="shared bamboo grove",
        name="shared bamboo grove",
        covers="`bamboo_stands` with any role other than homestead - the take-yabu at the field margin",
        what="A bamboo thicket held by the hamlet at the field margin, cut like a coppice.",
        why="The record gives bamboo two places: the household's own strip, and the take-yabu as a stand of its own at the village edge, harvested under the village's rules. The two forms are two knobs, not a choice.",
        label="deviation",
        label_note="Presence is read; the stand-level glyph is a deviation for legibility, exactly as for the homestead stand.",
        sources=("not recorded",),
        entry="research/vegetation.md - 'Bamboo: how common, where it stood, and how to show it'",
    ),
    _c(
        key="windbreak",
        # the GM, 2026-08-29: the modal should "actually say 'Windbreak forest' instead of just
        # 'windbreak'". The NAME is what the heading renders (`cap(d.name)`); the KEY is what the ink
        # carries and what `all_ink_is_ruled_on` reads, so it does not move.
        name="windbreak forest",
        covers="`village_groves[role=windbreak]`",
        what="The village shelter belt - the fengshui back grove: a dense, cedar-backed stand of real crowns on the windward, high side of the cluster, embracing it.",
        why="A nucleated village shelters behind one village-scale grove against the winter monsoon. Surveys of southern-China village fengshui forests find about two groves per village at closed-canopy density, the typical back grove one to two hectares - large relative to the cluster, and drawn so. It is kept off the west side of the gardens so the beds keep their afternoon sun.",
        label="accurate",
        label_note="Scale, density and placement follow the surveyed figures (forests-2020); the belt's shape follows the terrain and the cluster.",
        sources=("forests-2020",),
        entry="research/vegetation.md - 'The fengshui forest - real scale, and why ours is honest'; research/homesteads.md - 'The garden's sun, and how far the windbreak shades'",
    ),
    _c(
        key="copse",
        name="copse",
        covers="`village_groves[role=copse]`",
        what="A stand of fruit-tree and broadleaf greenery in the open ground among the houses - shade and fruit, not shelter.",
        why="The leafy greenery scattered through the gaps of a nucleated cluster is the third of the village's grove roles, after the back belt and the water-mouth grove; it threads between the dwellings and never stands on a roof, a yard or a crop.",
        label="accurate",
        label_note="The role is attested with the fengshui-grove system; how much ground one takes is nowhere given, so a copse is drawn to whatever gaps the houses, yards and crop leave it.",
        caveat="how much ground one takes is nowhere given, so a copse is drawn to whatever gaps the houses, yards and crop leave it.",
        sources=("forests-2020",),
        entry="research/vegetation.md - 'The fengshui forest'; settlements/vegetation.md 'Village windbreak' (the three roles)",
    ),
    _c(
        key="woodland commons",
        name="woodland commons",
        covers="`commons[role=woodland]` - the coppice patches",
        what="A managed coppice wood on the slope above the paddy: spaced crowns with an open canopy, the floor raked clear of leaf litter.",
        why="The village woods were iriai commons - customary common land held by the village and governed by its own rules on who might cut, when, and how much - coppiced on a 10-30 year cycle for firewood, forage and the leaf litter that fertilized the paddies. A cut wood lets sun reach the floor, so herbs grow there, not brush; the wood sits on the slope break above the fields, one part of the satoyama the community worked as a whole.",
        label="accurate",
        label_note="The commons regime and the raked floor are read (the Yamaguni study, the satoyama entries); a lot's boundary was NOT laid out as a surveyed square, so the patches are irregular.",
        caveat="a lot's boundary was NOT laid out as a surveyed square, so the patches are irregular.",
        sources=("not recorded",),
        entry="research/vegetation.md - 'How is a coppice lot bounded?', 'Does scrub stand under a village wood?', 'Forest density and crown size'",
    ),
    _c(
        key="scrub and rough grazing",
        name="scrub and rough grazing",
        covers="`commons[role=grazing]`",
        what="The cut-over fuel and fodder land around the settlement: grass with a few scraggly pines, grazed and cut.",
        why="Everything the paddy and the homesteads do not take is the hamlet's rough ground, and it is worked: scrub stands six feet off every field edge (one scythe swath - land hunger keeps the margin to that), off open water and off the cut banks of the channels.",
        label="accurate",
        label_note="The margins are read; nothing describes how the clumps sit within them, so the scatter is drawn to read as rough grazing rather than as any surveyed pattern.",
        caveat="nothing describes how the clumps sit within them, so the scatter is drawn to read as rough grazing rather than as any surveyed pattern.",
        sources=("not recorded",),
        entry="research/vegetation.md - 'The crop margin', 'Scrub stays off open water', 'The cut bank'",
    ),
    _c(
        key="marsh",
        name="marsh",
        covers="`marshes` - every marsh patch, whatever its role",
        what="Reed wetland on the undrained low ground - the wet toe below the fields and the fringe of the pond.",
        why=(
            "Wet rice is reclaimed FROM marsh: where reclamation stops, or the ground is too wet to manage, it stays reed wetland, "
            "and an abandoned paddy reverts to it. The toe marsh is as wide as the fan it drains, and its margin grades reed, then "
            "sedge and grass, then dry ground. A RESERVOIR'S SHORE IS REEDED BECAUSE THE POND IS WORKED, not in spite of it: the "
            "obvious guess is that a maintained tameike - its bank repaired, its silt dredged, its water drawn down each season - "
            "would have a margin kept clear, and the record contradicts that. A Kagawa Prefecture study found a statistically "
            "significant POSITIVE correlation between the number of emergent-plant species (the reed and cattail belt) and the "
            "practice of dredging silt and cutting algae, and it is the ponds whose water use has STOPPED that lose the fringe. "
            "The reeds are a sign of a pond in use. The EMBANKMENT is the other half of the same finding and is different ground: "
            "it is mown and burned and may not be cultivated, to keep the bank strong, and what grows on it is dry-grassland herbs. "
            "So reeds stand in the shallows and stop at the foot of the bank - which is why you will not see the wet haze on a dike "
            "or a pond's raised rim."
        ),
        label="accurate",
        label_note="The reclaimed-from-marsh finding, the margin gradient, and the reeded-shore finding are all read; the embankment is mown in the record as it is bare on the map.",
        sources=("aas-rice-technology", "mineta-2007-tameike", "tameike-jawiki", "kagawa-tameike-structure", "maff-tameike-shizen", "nies-tameike", "inamino-tameike-museum"),
        entry="research/water.md - 'Marsh - wet rice is reclaimed FROM wetland', 'The wet toe is as wide as the FAN', \"A reservoir's shore is reeded, and its EMBANKMENT is mown\"; research/vegetation.md - 'The marsh margin'",
    ),
    _c(
        key="paddy",
        name="paddy",
        covers="the wet plots of every `fields[kind=paddy]` - the flooded basins",
        what="A rice basin under a shallow sheet of water behind its bunds - an inch or so for most of the season - one plot of the hamlet's comb field. The sheet is not constant: at midsummer the field is drained on purpose until the mud cracks underfoot, and it is drained again before the harvest.",
        why="Pre-modern paddies were fitted to land and water by piecemeal reclamation and inheritance, so the plots are odd-sized and odd-shaped, meeting at T-junctions; the tidy rectangular grid is a Meiji land-consolidation artifact. A flooded paddy makes its own nitrogen, which is why the same basins were cropped year after year.",
        label="accurate",
        label_note="Plot form and the irregular patchwork are read; plot sizes are calibrated from the record. the field is shown flooded, which is one moment of a cycle that runs from flooded to cracked and back; the depths behind that choice are modern extension figures, and no pre-modern record of either the depths or the drying stages was found.",
        caveat="the field is shown flooded, which is one moment of a cycle that runs from flooded to cracked and back; the depths behind that choice are modern extension figures, and no pre-modern record of either the depths or the drying stages was found.",
        sources=("maff-suitou-mizu", "zennoh-mizukanri"),
        entry="research/fields.md - 'Paddy plots - irregular patchwork', 'Nitrogen - a flooded paddy makes its own', 'Plot sizes', 'How deep the water actually stands'",
    ),
    _c(
        key="wet paddy",
        name="wet paddy (shitsuden)",
        covers="the plots of a `fields[kind=paddy]` drawn with open water showing - the wettest ground the field has",
        what="Shitsuden, the wet paddy: a rice basin on ground too poorly drained to dry out, which stays waterlogged even in the season when no rice is growing. Its opposite is the kanden, the dry paddy, which empties to a dry field when the water is let out. The difference is the ground, not the crop - the same rice grows in both - which is why it lasts all year and is worth marking on a map.",
        why="It lies at the foot of the field, on the drain. Water falls basin to basin down a gravity system, and in a traditional paddy no line can be drawn between irrigating and draining, so the plots at the bottom take what the plots above shed and never come dry. That makes it the ground nobody wanted: the mud is deep, the soil runs colder and shorter of oxygen than a kanden, no winter crop of wheat or barley can follow the rice, and lodging and disease leave the yield unreliable. From Meiji the state drained wet paddy into dry as a national undertaking, and more than two thirds of the country's fields were converted - the measure of how much of it there was to convert, and the reason a map of these centuries should carry some.",
        label="accurate",
        label_note="The shitsuden and kanden categories, the wetness that defines them and the penalties they carry come from the dictionaries, quoted in the entry. Which plots wear the tint is a drawing convention rather than a survey: on a comb field a share of the wet rank carries it rather than all of it, and seating the wettest ground at the drain foot is inferred from how water falls through the system, not stated by the record.",
        caveat="Which plots wear the tint is a drawing convention rather than a survey: on a comb field a share of the wet rank carries it rather than all of it, and seating the wettest ground at the drain foot is inferred from how water falls through the system, not stated by the record.",
        sources=("kotobank-shitsuden", "kotobank-kanden", "kotobank-yatsuda", "kotobank-fukada", "fao-rice-water"),
        entry="research/fields.md - 'The wettest plots are their own kind of ground - shitsuden, and why they read blue'",
    ),
    _c(
        key="bund",
        name="bund",
        covers="the stroke of every paddy plot and the piled junctions between them",
        what="The aze: a puddled-mud ridge one to two feet wide and about a foot high between two basins, re-plastered every spring so each paddy holds its water; the walking bunds ran two to five feet. Where bunds cross, the earth is piled into a lumpy node - the most-worked point in a field.",
        why="A bund is the wall BETWEEN two basins and is built once, so the fabric is one connected network meeting at T-junctions - never two parallel ridges with idle ground between. Farmers walked the bunds to reach the plots; the footplanks over the ditches serve that walking.",
        label="accurate",
        label_note="Construction, width and the shared-wall finding are read; the drawn stroke is at true size.",
        sources=("aze-standard",),
        entry="research/fields.md - 'Bunds are SHARED, and the fabric is continuous', 'A bund runs on, or it turns for a reason'; research/water.md - 'The bund runs along the channel bank'",
    ),
    _c(
        key="bund beans",
        name="bund beans",
        covers="the bead run along the bunds (`bund_beans`)",
        what="Soybeans planted along the tops of the paddy bunds - azemame - drawn as dark green beads.",
        why="A bund's top is soil that would otherwise grow weeds; planting it with beans took a second crop from the same ground without touching the paddy. A share of the bunds is planted, rolled per map.",
        label="deviation",
        label_note="The practice is attested; the bead color is a deliberate deviation - real soybean foliage is lighter, and the deep pine green was chosen so the beads read against the pale rice.",
        sources=("not recorded",),
        entry="research/fields.md - 'Paddy plots - irregular patchwork'; 'Bunds are SHARED, and the fabric is continuous'; waterfields/palette.py BEAN_GREEN (the color decision)",
    ),
    _c(
        key="millet",
        name="millet",
        covers="`dry_plots[crop=millet]` and their furrows",
        what="A dry-field (hatake) plot under millet, worked in ridged rows.",
        why="Wet-rice villages sort by a topographic catena: the paddy holds the flat valley bottom, dry crops take the higher, well-drained ground the water cannot command - the hem above the paddy and the raised ground the homesteads sit on - and coppice crowns the hills above.",
        label="accurate",
        label_note="Placement on the catena is read; the crop MIX on any one map (how much millet against buckwheat and barley) is rolled from the seed and is a GUESS at the proportions.",
        caveat="the crop MIX on any one map (how much millet against buckwheat and barley) is rolled from the seed and is a GUESS at the proportions.",
        sources=("not recorded",),
        entry="research/fields.md - 'Where dry (hatake) crops go - the topographic catena', 'Why ruled rows waited for Meiji'",
    ),
    _c(
        key="buckwheat",
        name="buckwheat",
        covers="`dry_plots[crop=buckwheat]` and their furrows",
        what="A dry-field plot under buckwheat - the short-season crop for thin soil, sown late and taken in autumn - worked in ridged rows.",
        why="Dry crops take the higher, well-drained hem above the paddy, where the water cannot command the ground.",
        label="accurate",
        label_note="Placement on the catena is read; the crop mix per map is rolled from the seed and is a GUESS at the proportions.",
        caveat="the crop mix per map is rolled from the seed and is a GUESS at the proportions.",
        sources=("not recorded",),
        entry="research/fields.md - 'Where dry (hatake) crops go - the topographic catena'",
    ),
    _c(
        key="barley",
        name="barley",
        covers="`dry_plots[crop=barley]` and their furrows",
        what="A dry-field plot under barley - the winter grain, sown in autumn and taken in early summer - worked in ridged rows.",
        why="Dry crops take the higher, well-drained hem above the paddy, where the water cannot command the ground.",
        label="accurate",
        label_note="Placement on the catena is read; the crop mix per map is rolled from the seed and is a GUESS at the proportions.",
        caveat="the crop mix per map is rolled from the seed and is a GUESS at the proportions.",
        sources=("not recorded",),
        entry="research/fields.md - 'Where dry (hatake) crops go - the topographic catena'",
    ),
    _c(
        key="soy",
        name="soy",
        covers="`dry_plots[crop=soy]` and their furrows",
        what="A dry-field plot under soybean (daizu) grown as a field crop of its own, worked in ridged rows - drawn a soybean green against the tan and ochre grains.",
        why="Dry crops take the higher, well-drained hem above the paddy, where the water cannot command the ground; the bean fixes its own nitrogen, which is why it also went along the bunds.",
        label="accurate",
        label_note="Placement on the catena is read; the crop mix per map is rolled from the seed and is a GUESS at the proportions.",
        caveat="the crop mix per map is rolled from the seed and is a GUESS at the proportions.",
        sources=("not recorded",),
        entry="research/fields.md - 'Where dry (hatake) crops go - the topographic catena'",
    ),
    _c(
        key="fallow",
        name="fallow",
        covers="`fallow_patches`",
        what="Ground resting out of crop for the season.",
        why="Some dry ground rested between crops; how much, and where in the rotation, the record consulted here does not say.",
        label="guess",
        label_note="The record is thin on fallow in this tier's fields; the patch is drawn where the field builder leaves ground unplanted, and that is a guess.",
        sources=("not recorded",),
        entry="research/fields.md (no dedicated entry - recorded as silent)",
    ),
    _c(
        key="stream",
        name="stream",
        covers="`streams` - the brook",
        what="A natural brook off the high ground, feeding the head of the field and, below it, carrying the drain away.",
        why="A village creek runs about two meters wide in reality, six times a field ditch; every watercourse on the map declares which way it flows, because downstream is a real constraint on what may stand beside it.",
        label="deviation",
        label_note="The stream's type and place are read; its DRAWN width is rank, not discharge - the GM's ruling - so junctions do not conserve width.",
        sources=("gb50288", "toro-site"),
        entry="research/water.md - 'Water-width ladder - the real-world tiers', 'Drawn width is RANK, not discharge'",
    ),
    _c(
        key="field ditch",
        name="field ditch",
        covers="`field_ditches` and `channels` - the intake, head race, branches and drain",
        what="The dug irrigation net: the intake from the stream, the head race along the high margin, the laterals running down-slope between the plots, and the drain along the low line.",
        why="The comb layout - supply along the high margins, delivery ditches perpendicular down-slope, one drain on the lowest line - is the Edo Kishu-school layout and codified Chinese canal doctrine alike. Mains taper as branches tap them; the net is SPARSE because a village digs the minimum, and a ditch beside every paddy is a Meiji anachronism. The net is drawn at true size: a field ditch is about a third of a meter, a hairline.",
        label="accurate",
        label_note="Topology, taper and true-size width are read (Tabayashi, the Minuma-dai record, GB 50288).",
        sources=("tabayashi-1986", "jsidre-minumadai", "gb50288", "nougyoudoboku-matsutan"),
        entry="research/water.md - 'The comb net is drawn at TRUE SIZE', 'Where the drawn net STOPS', 'The head-race forks'; research/fields.md - 'Water-first v2'",
    ),
    _c(
        key="pond",
        name="pond",
        covers="`pond` - the tameike",
        what="An irrigation reservoir - a valley-head tameike behind an earthen dike, sitting above the fields it waters.",
        why="A tameike is built by dividing off a valley mouth with a dike, at an elevation above the paddies it serves, with ONE outlet: an inclined intake feeding a bottom conduit through the dam. The spillway is for floods, never for distribution. On this map the pond is the field's drainage sink, at its low foot.",
        label="accurate",
        label_note="Form, siting and the single outlet are read (Tabayashi 1986, the Kagawa tameike documents).",
        sources=("tabayashi-1986", "kagawa-tameike"),
        entry="research/fields.md - 'Water-first v2 - pond, distribution and the three layout modes'",
    ),
    _c(
        key="field pond",
        name="field pond",
        covers="`field_ponds` - the in-field pond sunk into one low paddy",
        what="A small pocket of open water inside one low paddy plot, reed-fringed - a low pocket where the ground pools, or a header pond within the field.",
        why="Flat, flooded valley-bottom paddy is the archetype that hosts non-rice obstacles LEAST - graves and knolls go to the slope, rock outcrops belong to terraces - and a small open-water pond is the one thing that genuinely belongs in the wet middle. It is drawn sunk into a single low plot, never across a bund.",
        label="accurate",
        label_note="The kind of obstacle a flooded paddy hosts is read (corroborated in both traditions); no source counts how often, so the rate is chosen - often enough that a reader meets the feature, rare enough that it does not litter the field.",
        caveat="no source counts how often, so the rate is chosen - often enough that a reader meets the feature, rare enough that it does not litter the field.",
        sources=("not recorded",),
        entry="research/fields.md - 'In-field features - flat flooded paddy hosts obstacles least'",
    ),
    _c(
        key="field rock",
        name="field rock",
        covers="`field_rocks` - a bedrock outcrop inside a plot",
        what="A cluster of gray boulders inside a field plot - a bedrock outcrop the terrace risers wrap around, too big to clear.",
        why="Rock outcrops are a TERRACE feature, bedrock the risers wrap around, and are absent on alluvial valley, polder and delta ground; where the archetype allows one it stands off-center in its plot so it reads as a natural obstacle.",
        label="accurate",
        label_note="Which archetypes host an outcrop is read (corroborated); no source counts how many, so a terraced field gets one to three - enough that the reader meets the obstacle the terrace was cut around, few enough that the field still reads as worked ground.",
        caveat="no source counts how many, so a terraced field gets one to three - enough that the reader meets the obstacle the terrace was cut around, few enough that the field still reads as worked ground.",
        sources=("not recorded",),
        entry="research/fields.md - 'In-field features - flat flooded paddy hosts obstacles least'",
    ),
    _c(
        key="grave island",
        name="grave island",
        covers="`field_graves` - the rare in-field grave mound",
        what="A small raised earthen mound with two or three stone markers standing inside a paddy plot, the flat paddy tiling around it.",
        why="Graves among the paddy are a north-China dry-plain signature, corroborated in Japan - NOT the rice-south default, where feng-shui puts the dead on the slope with a backing hill and a downslope water view. The GM approved both looks, so the island is drawn rarely (about three valley, terrace or ribbon maps in ten) as a deliberate departure.",
        label="deviation",
        label_note="A calibrated liberty, disclosed: the in-field grave is drawn where the rice-south record would put the dead on the slope, at a rate the GM approved.",
        sources=("not recorded",),
        entry="research/fields.md - 'In-field features - flat flooded paddy hosts obstacles least' (the CALIBRATED LIBERTY paragraph, GM 2026-07-20)",
    ),
    # WHY THE CLASS IS A *VILLAGE* LANE AND NOT A HAMLET LANE - the GM, 2026-08-29: "I have been
    # referring to hamlet lanes as village lanes specifically for this reason because they are presumed
    # to lead into the main village when not otherwise stated." The rule is in the `why` where a reader
    # needs it; the naming rationale is project process and stays here (settlement-review, 2026-08-29).
    _c(
        key="village lane",
        name="village lane",
        covers="`lanes` - every lane on the map: the web, the internal skeleton, the connector to the off-map road and the field spur",
        what="A trodden earth track - packed dirt with soft worn shoulders, a single narrow way, no paving and no center line.",
        why="Every house in a nucleated village is reached by the interconnected lanes and alleys - that is what compactness is for - and the narrow lateral lanes are colonized as semi-private space by the houses beside them, which is why they are narrow and irregular. A lane bends like a line feet wear: as few turns as the plots allow, none sharp, never back on itself. The connector to the off-map road predates the settlement; the lanes between the farmsteads were trodden by the households already living there. And the lane leads somewhere: unless this map's notes say otherwise, a village lane runs to the main village of the district the settlement belongs to.",
        label="accurate",
        label_note="Access and form are read; the drawn WIDTHS (3, 5 and 6 ft) are a GUESS - no source gives a figure for an ordinary hamlet lane - laddered from a footpath to a wheelbarrow's width, with the connector kept under the 9 ft of the one cart road the record does measure.",
        caveat="the drawn WIDTHS (3, 5 and 6 ft) are a GUESS - no source gives a figure for an ordinary hamlet lane - laddered from a footpath to a wheelbarrow's width, with the connector kept under the 9 ft of the one cart road the record does measure.",
        sources=("not recorded",),
        entry="research/homesteads.md - 'Is every farmhouse reached by a lane, and in what FORM?', 'How does a village lane bend?'; research/SOURCES.md re-sourcing queue (lane width)",
    ),
    _c(
        key="footbridge",
        name="footbridge",
        covers="`bridges[foot]` - every plank and deck over water",
        what="A plank laid over a ditch, or a small timber deck where a lane crosses the stream.",
        why="Farmers reach the plots by walking the bunds, and the long laterals cut across that walking; a plank every so often keeps the field passable. Where a way crosses water, one deck - never two at the same point.",
        label="guess",
        label_note="That ditches were planked is reasoned, not read: the record consulted says nothing about a plank over a two-foot ditch, so the plank and its spacing are a guess.",
        sources=("not recorded",),
        entry="research/water.md - 'What drawing at TRUE SIZE left open' (channel_footbridges)",
    ),
    _c(
        key="well",
        name="well",
        covers="`wells` - the wellheads",
        what="A communal wellhead: a stone curb and the dark water of the shaft, under a small roof.",
        why="A pre-modern rice village of about seventy households ran one to three communal wells, two typical - drinking water came mostly from surface water, settled and boiled, and a well was expensive durable capital dug by subscription only as surface quality forced. Shared wells outnumbered private ones.",
        label="deviation",
        label_note="Count and sharing are read (the Sphere/UNICEF figures, jawiki); the wellhead is DRAWN larger than true size so it can be seen at map scale.",
        sources=("sphere-unicef",),
        entry="research/urban-features.md - 'Wells - the research, and the deliberate liberty', 'Communal wells and the samurai exception'; research/homesteads.md - 'Does a DISPERSED hamlet's outlying farm have its own well?'",
    ),
    _c(
        key="notice board",
        name="notice board",
        covers="`kosatsuba`, with its label",
        what="The kosatsuba - the official edict board: a small roofed frame posting the standing law, rate tables and ban lists, its face turned square to the way it fronts.",
        why="Every Edo town AND village kept one, and its siting was a traffic decision: it is the state talking at all who pass, so the board stands where the settlement's one lane carries everyone. The circulars reached the farmers through exactly this board, read aloud where needed - one reader per settlement makes it work. The record names SEVERAL such places rather than one, so which of them a settlement uses is rolled from its own seed: the center where villagers assembled, the entrance where the track arrives, or the frontage of the village official's gate. Two more the record attests - a bridgehead, and the shrine precinct - are real at town and city scale and are deliberately not offered at a hamlet, whose crossings are 10 ft ditch planks and whose only shrine is a household hokora in someone's dooryard.",
        label="accurate",
        label_note="Presence and siting are both read. The placement is chosen from the attested set the map can actually site, never from one preferred reading; at hamlet grain the glyph is drawn at its true 12 x 5 ft.",
        sources=("fuchu-kosatsuba", "ogose-kosatsuba", "kosatsu-jawiki", "adachi-kosatsu"),
        entry="research/urban-features.md - 'The notice board (kosatsuba) - siting is a TRAFFIC decision'",
    ),
    # ---- the dike-pond hamlet (feature 150, Kuwabata - the first scripted mulberry_dike_fishpond) ----
    FeatureClass(
        key="fish pond",
        name="fish pond",
        covers="the dug water of every `dikeponds[]` parcel - the pond inset inside its mulberry dike",
        what="A stocked carp pond dug out of a former paddy parcel, two to three meters deep, its water held back by the planted dike piled from its own spoil - one cell of the mulberry-dike fish-pond system (桑基魚塘).",
        why="A dike-pond is dug where the ground was low and flood-prone: the digging drains the hollow and the spoil raises the dike, so the landscape was made cell by cell by the households that farmed it, over centuries. Each pond is fed and drained through a sluice in its dike, plumbed inlet-high and outlet-low, and is drained two or three times a year to dredge the mud onto the dikes. The ponds here are 0.4 to 0.6 hectare oblongs, the size the surveys of the traditional landscape record.",
        label="accurate",
        label_note="The form and the loop are read; the pond SIZES are from 20th-century surveys of the traditional landscape, not Ming or Qing documents, and the whole-block conversion drawn here is the rare end state of a normally scattered system.",
        caveat="the pond SIZES are from 20th-century surveys of the traditional landscape, not Ming or Qing documents, and the whole-block conversion drawn here is the rare end state of a normally scattered system.",
        sources=("isis-dykepond", "ruddle-zhong-1988", "fao-ac241e", "gmrb-2024-sangji"),
        entry="research/archetypes.md - 'The three overlay values', 'The 6:4 water-to-dike ratio, and coppiced mulberry', 'A dike-pond is fed and drained through sluice gates'",
    ),
    FeatureClass(
        key="mulberry dike",
        name="mulberry dike",
        covers="the bank ring of every `dikeponds[]` parcel and the coppiced crowns planted along it",
        what="The raised earthen dike around a fish pond, six to ten meters wide, piled from the pond's own dredged mud and planted with coppiced mulberry - low bushes stripped for leaf several times a year to feed silkworms.",
        why="The dike is the silk side of the loop: mulberry leaf feeds the silkworms, the silkworm waste feeds the fish, the dredged pond mud re-fertilizes the dike. The prescription was six parts water to four parts dike (three-to-seven to four-to-six in the gazetteers) because too much water starves the worms and too much dike starves the fish. A bare dike of heaped mud gullies and slumps, so every dike was planted; in sericulture districts that planting was mulberry.",
        label="accurate",
        label_note="The ratio, the dike width and the planting are read; the coppice density the crowns are drawn at (one bush per ten to twenty square feet) was not re-found and stays on the re-sourcing queue.",
        caveat="the coppice density the crowns are drawn at (one bush per ten to twenty square feet) was not re-found and stays on the re-sourcing queue.",
        sources=("gd-gazetteer-sangji", "fao-ac241e", "isis-dykepond", "ruddle-zhong-1988"),
        entry="research/archetypes.md - 'The 6:4 water-to-dike ratio, and coppiced mulberry', 'Why dikes were planted at all'",
    ),
    FeatureClass(
        key="pond sluice",
        name="pond sluice",
        covers="the short channel stubs of `dikepond_sluices` - where each pond's dike is cut to the canal",
        what="A protected opening in a pond's dike, closed with wooden boards to set the water level and pulled to drain the pond at harvest - the gate through which a dike-pond exchanges water with the canal network.",
        why="A dike-pond is not a sealed basin: the whole system runs in series from a high intake to a low outfall, each pond taking water in at its high side and letting it out at its low side. The stub drawn here is the cut in the dike; the boards themselves are a few inches wide and are not drawn at this scale.",
        label="accurate",
        label_note="The sluice's form is read from the FAO pond-construction manual; its position on each pond is the engine's inlet-high, outlet-low rule from the record, not a surveyed plan.",
        caveat="its position on each pond is the engine's inlet-high, outlet-low rule from the record, not a surveyed plan.",
        sources=("fao-x6708e", "cssn-sangyuanwei"),
        entry="research/archetypes.md - 'A dike-pond is fed and drained through sluice gates'",
    ),
    FeatureClass(
        key="sugarcane dike",
        name="sugarcane dike",
        covers="the bank ring of every `dikeponds[]` parcel on a hamlet whose `meta.dike_crop` is sugarcane, and its cane rows",
        what="The raised dike around a fish pond planted with sugar cane in close rows - the 蔗基魚塘 type of the dike-pond system, where the cane's bagasse feeds the pigs whose manure feeds the fish.",
        why="The dike-pond types succeeded one another across the delta: mulberry, then fruit, cane and vegetables as markets changed, and by the late 1980s cane dikes covered more of the district than mulberry. One hamlet is one type, so a cane hamlet rolls cane on every dike.",
        label="accurate",
        label_note="The type and the loop are read; the row pitch is a drawing calibration from the plant's habit, not a Ming or Qing figure.",
        caveat="the row pitch is a drawing calibration from the plant's habit, not a Ming or Qing figure.",
        sources=("gd-gazetteer-sangji", "isis-dykepond", "ruddle-zhong-1988", "dili360-2005-sangji"),
        entry="research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'",
    ),
    FeatureClass(
        key="banana dike",
        name="banana dike",
        covers="the bank ring of every `dikeponds[]` parcel on a hamlet whose `meta.dike_crop` is banana, and its clumps",
        what="The raised dike around a fish pond planted with banana stools - the 蕉基魚塘 type, the 'banana groves and sea of cane' the geographers remembered of the old delta.",
        why="Banana took the dikes where the silk market fell away; a type of the same system, drawn as a hamlet's whole planting because the types succeeded one another rather than mixing on a dike.",
        label="accurate",
        label_note="The type is read; the clump pitch and crown size are a drawing calibration from the plant's habit, not a surveyed figure.",
        caveat="the clump pitch and crown size are a drawing calibration from the plant's habit, not a surveyed figure.",
        sources=("gd-gazetteer-sangji", "dili360-2005-sangji"),
        entry="research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'",
    ),
    FeatureClass(
        key="fruit dike",
        name="fruit dike",
        covers="the bank ring of every `dikeponds[]` parcel on a hamlet whose `meta.dike_crop` is fruit, and its trees",
        what="The raised dike around a fish pond planted with fruit trees - lychee, longan, citrus - the 果基魚塘 type, the delta's older form before mulberry took the dikes.",
        why="The fruit dike is the type the delta's own accounts put first, before mulberry displaced it; the standard trees stand on the band's crest at an orchard's spacing.",
        label="accurate",
        label_note="The type is read; the tree spacing is an orchard convention, not a measured dike.",
        caveat="the tree spacing is an orchard convention, not a measured dike.",
        sources=("gd-gazetteer-sangji", "dili360-2005-sangji"),
        entry="research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'",
    ),
    FeatureClass(
        key="vegetable ground",
        name="vegetable ground",
        covers="an unconverted parcel of a wholly converted dike-pond block, on a hamlet whose `meta.leftover` is vegetables",
        what="A parcel of tilled vegetable ground in rows among the fish ponds - the one piece of the block that was neither dug into a pond nor left in rice.",
        why="A converted district grew no rice, and Fei's silk village grew its vegetables on whatever ground the mulberry left; so the residual parcel of a converted block reads as vegetable ground as honestly as paddy. Three attested states, so each hamlet rolls one.",
        label="accurate",
        label_note="The absence of rice and the vegetable ground are read; nothing says WHICH parcels carried them, so they take whatever the crop dikes and the ponds leave over.",
        caveat="nothing says WHICH parcels carried them, so they take whatever the crop dikes and the ponds leave over.",
        sources=("fei-1939", "gd-gazetteer-sangji"),
        entry="research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'",
    ),
    FeatureClass(
        key="pig sty",
        name="pig sty",
        covers="every `pig_sties[]` record - a shed with its railed pen on a pond dike",
        what="A simple pig shed built on the dike of a fish pond, its pen railed at the water's edge so the pigs' manure runs straight into the pond.",
        why="The dike-pond loop fed its fish with more than silkworm waste: pigs, chickens and ducks were reared on the dikes to manure the ponds, and a cane hamlet fed its pigs on bagasse. The shed stands on the pond nearest the houses.",
        label="guess",
        label_note="GUESS: the practice is read (the 1980s survey and the FAO/NACA manual), but nothing read gives how many households kept a sty in Ming or Qing; the per-hamlet share band is the generator's.",
        sources=("fao-ac264e", "isis-dykepond", "ruddle-zhong-1988"),
        entry="research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'",
    ),
    FeatureClass(
        key="duck pen",
        name="duck pen",
        covers="every `duck_pens[]` record - a fenced dry run on the dike and a fenced wet run in the pond's corner",
        what="A duck pen on a fish pond: a fenced run on the dike with the duck house in it, and a fenced corner of the water where the birds swim - their droppings feed the fish.",
        why="Fish-cum-duck ponds fence part of the dike as a dry run and part of the water as a wet run; ducks were among the stock the dike-pond loop kept to manure its ponds.",
        label="guess",
        label_note="GUESS: the form is read from the modern manual; its premodern prevalence is not, and the share band is the generator's - the weakest-evidenced item of the audit, drawn because the GM chose it.",
        sources=("fao-ac264e", "isis-dykepond"),
        entry="research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'",
    ),
    FeatureClass(
        key="fry pond",
        name="fry pond",
        covers="the dug water of a `dikeponds[]` parcel recorded `kind: fry` - the block's smallest parcels",
        what="A small nursery pond where carp fry are reared before they are stocked into the grow-out ponds - the hamlet's own hatchery corner of the dike-pond block.",
        why="Fry were a trade of their own in the delta: Jiujiang township on the Xijiang rose on it from the Ming, and the polder proverb has the men trading fry while the women feed the worms. A hamlet stocking its ponds each year keeps a few small ponds for the fry; the smallest parcels of the block are read as those.",
        label="guess",
        label_note="GUESS: the fry trade and the nursery stage are read, but nothing read gives how many fry ponds a hamlet kept or which parcels - the one-in-ten share and the choice of the smallest parcels are the generator's.",
        sources=("miles-2003", "cssn-sangyuanwei", "isis-dykepond"),
        entry="research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'",
    ),
    FeatureClass(
        key="manure pit",
        name="manure pit",
        covers="a `farm_fixtures[]` record of kind `manure` with `form: pit` - the alternative to the heap",
        what="An earthenware jar sunk to its mouth in the ground behind the house, in which the household's night soil is kept until it goes to the fields - the manure store in its Lake Tai form.",
        why="The most important fertilizer on a rice-and-silk farm was human manure, and Fei's village kept it in pits of earthenware half buried behind the buildings, so many that the public road along the stream was lined with them. Where Tohoku farms heaped theirs by the stable, the silk villages potted theirs: two attested forms, so each hamlet rolls one.",
        label="accurate",
        label_note="The form and its place behind the house are read (Fei 1939); the drawn 3.5 ft mouth is a size the record does not give.",
        caveat="the drawn 3.5 ft mouth is a size the record does not give.",
        sources=("fei-1939", "sugiura-1973-fuzoku"),
        entry="research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'",
    ),
    FeatureClass(
        key="sluice gate",
        name="sluice gate",
        covers="the board bar of every `sluice_gates[]` record - the gate in each cut of the perimeter dike",
        what="The wooden boards set in the cut of a polder dike where the water comes in or goes out: dropped, they hold the block's water; lifted, they let it flow.",
        why="A polder is enclosed against the flood outside, so its dike is cut only where a gate controls the water - at the inlet high on the block and the outfall low on it. The gate is a protected opening closed with wooden boards to set the level, and it is why the dike can be complete and the block still fed and drained.",
        label="accurate",
        label_note="The form is read from the FAO pond-construction manual; the 6 x 3 ft bar is drawn at the size of a board set, a glyph the record does not measure.",
        caveat="the 6 x 3 ft bar is drawn at the size of a board set, a glyph the record does not measure.",
        sources=("fao-x6708e", "cssn-sangyuanwei", "shen-kuo"),
        entry="research/archetypes.md - 'A dike-pond is fed and drained through sluice gates', 'Polder siting - full enclosure, fluctuating water, and where the village sits'",
    ),
    FeatureClass(
        key="perimeter dike",
        name="perimeter dike",
        covers="the earthwork band of `dikes[]` - the polder's enclosing dike, gapped at its sluices",
        what="The hand-piled earthen embankment that encloses a polder block, following the natural water edge in gentle curves and non-square bends, planted with willow and mulberry to bind it, and cut only where a gated sluice lets water in at the high corner and out at the low one.",
        why="A polder is wetland enclosed by dikes so it can be drained; its floor sits at or below the flood stage outside, so the enclosure is complete - any gap re-floods the block. The dike was dredged pond mud heaped and packed, breached and repaired for centuries, so it reads as a mottled vegetated band of varying width rather than a ruled line; the dead-straight rectangle is a post-1949 industrial shape.",
        label="accurate",
        label_note="Full enclosure, the organic outline and the planting are read; the drawn width band (14-40 ft) is a drawing calibration inside the attested 6-10 m dike widths.",
        caveat="the drawn width band (14-40 ft) is a drawing calibration inside the attested 6-10 m dike widths.",
        sources=("shen-kuo", "isis-dykepond", "ruddle-zhong-1988"),
        entry="research/archetypes.md - 'Polder siting - full enclosure, fluctuating water, and where the village sits', 'Why dikes were planted at all'",
    ),
)


def _install_siblings(defs: tuple[FeatureClass, ...]) -> dict[str, FeatureClass]:
    by_key = {d.key: d for d in defs}
    for (a, b), text in _PAIRS.items():
        if a not in by_key or b not in by_key:
            raise KeyError(f"sibling pair names an unknown class: {(a, b)}")
        by_key[a].siblings[b] = text
        by_key[b].siblings[a] = text
    return by_key


#: Every feature class, by key. Insertion order is the spec's FR-007 order.
CLASSES: dict[str, FeatureClass] = _install_siblings(_DEFS)


def slug(key: str) -> str:
    """The CSS token for a class key: `storage shed` -> `storage-shed`."""
    return key.replace(" ", "-")
