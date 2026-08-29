"""The place card (feature 156): what a reader gets for clicking the settlement's title placard.

Every function under test takes plain dicts and sets and returns a string, so nothing here builds a
settlement. The two properties worth stating up front, because most of the file is one or the other:

  NOTHING IS HARDCODED PER MAP (spec FR-014). The crops come from the classes present, the counts
  from the manifest, the geography from the notes - so the dike-pond hamlet, which grows no rice and
  draws no dry plot, describes itself correctly with no code of its own.

  NOTHING UNSUPPORTED IS SAID (spec FR-008, and the `source-reader` pass in `research.md`). The card
  ranks TIERS, which the setting's own arithmetic supports, and never kinds of hamlet, which nothing
  does - and where it rests on canon the record does not back, it says so.
"""

from __future__ import annotations

import pytest

from l7r.diagram.interactive.classes import CLASSES
from l7r.diagram.interactive.notes import EMPTY, MapNotes
from l7r.diagram.interactive.place import (
    BASIS,
    BASIS_LEAD,
    COLLISIONS,
    CROP_SENTENCES,
    CROPS,
    KINDS,
    PER_HOUSEHOLD,
    PLACE_KEYS,
    crop_sentence,
    dwellings_shown,
    join,
    lane_default,
    place_card,
    size_sentence,
    where_sentences,
)

HAMLET = {"scale": "hamlet", "name": "Inashiro", "households": 15}
M15 = {"houses": [{"x": 0.0, "y": 0.0}] * 15}  # a manifest with 15 drawn dwellings and no agricultural district
PADDY = {"paddy", "millet", "soy"}
NOTES = MapNotes(
    place={"district": "Hoshigaoka", "district direction": "east", "imperial road": "directly south", "county": "Hayakawa", "town": "Hayakawa", "town direction": "further south"},
    features={},
)


# --- the crop table is derived from the map, and is real ---


@pytest.mark.parametrize("key", sorted(CROPS) + sorted(CROP_SENTENCES))
def test_every_crop_key_is_a_real_class(key: str) -> None:
    """A typo here would silently name a crop no map can draw, or drop one every map draws."""
    assert key in CLASSES


def test_the_card_names_only_the_crops_the_map_draws() -> None:
    text = crop_sentence(PADDY)
    assert "rice" in text and "millet" in text and "soy" in text
    assert "buckwheat" not in text and "mulberry" not in text and "sugarcane" not in text


def test_a_dike_pond_map_describes_itself_with_no_code_of_its_own() -> None:
    """Kuwabata's shape: mulberry, sugarcane and fish, no paddy and no dry plot at all. It must not
    claim flooded fields it does not have (spec Edge Cases)."""
    text = crop_sentence({"mulberry dike", "sugarcane dike", "fish pond"})
    assert "mulberry" in text and "sugarcane" in text and "fish" in text
    assert "flooded fields" not in text and "dry ground" not in text


def test_a_map_that_grows_nothing_says_nothing_about_crops() -> None:
    assert crop_sentence({"farmhouse", "well"}) == ""


def test_bund_beans_are_a_sentence_of_their_own_not_an_item_in_a_list() -> None:
    """They grow on the WALL between the wet and the dry, so listing them under either says something
    false about where they are."""
    text = crop_sentence({"paddy", "bund beans"})
    assert "The flooded fields grow rice." in text
    assert "along the tops of the paddy bunds" in text
    assert "rice and soybeans" not in text


# --- the figures, tilde-marked ---


def test_only_the_population_carries_a_tilde() -> None:
    """The GM, 2026-08-29: "You should not use a ~ for the number of farmhouses, because that actually
    IS an exact map feature - the number of farmhouses listed should be whatever is actually displayed
    on the map itself for hamlets and villages." The count is a statement about the sheet, which the
    reader could check by counting; the population is an inference from it."""
    got = size_sentence(KINDS["hamlet"], HAMLET, 15)
    assert got == "15 farmhouses, population ~75"
    assert not got.startswith("~")
    assert str(PER_HOUSEHOLD * 15) == "75"


def test_a_recorded_population_beats_the_household_multiple() -> None:
    """A town's inhabitants are not a multiple of anybody's farmhouses, and its tier records its own."""
    assert size_sentence(KINDS["town"], {"scale": "town", "population": 680}, 42) == "42 dwellings, population ~680"


def test_a_town_and_a_city_count_dwellings_and_never_farmhouses() -> None:
    """The GM, 2026-08-29: "towns and cities should state and list the number of non farmhouse
    dwellings ... this is something which is enumerated and known and which is actually exact and
    rendered." What they must NOT count is the farm housing, because the countryside around them is
    deliberately not drawn whole."""
    assert KINDS["hamlet"].houses_noun == "farmhouses" and not KINDS["hamlet"].excludes_farms
    for scale in ("town", "city"):
        assert KINDS[scale].houses_noun == "dwellings" and KINDS[scale].excludes_farms
        assert "farmhouse" not in size_sentence(KINDS[scale], {"population": 3000}, 260)


def test_each_tier_explains_what_its_population_figure_COUNTS() -> None:
    """A matter of Imperial census convention, not arithmetic, and the two upper tiers differ (GM
    2026-08-29). A hamlet's and a village's need no explaining - they are five to a drawn household.

    THE TOWN NOTE SAYS WHAT ITS FIGURE IS, not what the convention wants it to be. Every town in the
    pool declares the DEPICTED slice - Ubame's 590 is (36 farmhouses + 82 dwellings) x 5 exactly - and
    `settlements.md` has said so since before this feature, so a card claiming the figure took in the
    county's farmers would contradict its own manifest. The GM's convention needs the gens to
    re-declare `population`; until they do, the card states the smaller true thing and names the
    larger one as not yet given (settlement-review, 2026-08-29)."""
    assert "counts the settlement as drawn" in KINDS["town"].population_note
    assert "does not yet state that larger number" in KINDS["town"].population_note
    # THE CITY NOTE SAYS WHAT ITS FIGURE IS. It used to claim the figure "takes in the samurai country
    # estates", which all three cities' arithmetic denies - Minami's 520 dwellings x 5 IS its declared
    # 2,600, with no headroom for an undrawn household, and each city draws three estates that
    # contribute nothing. The estate convention is the GM's and is recorded as owed, not asserted
    # (settlement-review round 4, 2026-08-29).
    assert "households drawn inside the city itself" in KINDS["city"].population_note
    assert "farmhouses that stand within the wall" in KINDS["city"].population_note, "Tango's declared 3,000 is (583 + 17 in-wall farmhouses) x 5"
    assert "does not yet state that larger number either" in KINDS["city"].population_note
    assert "counts separately" in KINDS["city"].population_note
    assert KINDS["hamlet"].population_note == "" and KINDS["village"].population_note == ""


@pytest.mark.parametrize("key", sorted(COLLISIONS))
def test_every_collision_clause_names_a_real_class(key: str) -> None:
    assert key in CLASSES


def test_a_collision_clause_appears_only_where_its_class_is_drawn() -> None:
    """The card and the vocabulary use one word for two things - "shrine", "burial ground" - so the
    card disambiguates; but only on a map that draws the other thing. Mizuguchi draws neither, and was
    being told about both (settlement-review, 2026-08-29)."""
    bare = place_card(HAMLET, PADDY, EMPTY, M15)
    with_shrine = place_card(HAMLET, PADDY | {"household shrine"}, EMPTY, M15)
    assert bare is not None and with_shrine is not None
    assert "hokora" not in bare["what"], "a map with no household shrine hears nothing about one"
    assert "hokora in a corner of a farmstead plot" in with_shrine["what"], "and it stands where its own class puts it"
    assert "hamlet" not in COLLISIONS["household shrine"], "the clause is appended at EVERY tier, so it must not talk about hamlets"
    assert "field grave" not in with_shrine["what"], "this map draws no grave island"


def test_an_upper_tier_counts_buildings_and_a_lower_one_counts_houses() -> None:
    """`houses` IS THE FARM RING at town and city scale, and this is the trap the first cut fell into:
    it counted `houses` and looked right (Tango 273 -> 260) while counting nothing but the farmhouses
    the GM said to leave out (settlement-review, 2026-08-29). A town's and a city's dwellings are
    `buildings` under `DWELLING_KINDS` - the same set the capacity checks use."""
    manifest = {
        "houses": [{"x": 1.0, "y": 1.0}] * 40,  # the farm ring
        "buildings": [{"kind": "merchant"}, {"kind": "laborer"}, {"kind": "samurai"}, {"kind": "granary"}, {"kind": "gate"}],
    }
    assert dwellings_shown(manifest, KINDS["city"]) == 3, "three dwellings; the granary and the gate house nobody"
    assert dwellings_shown(manifest, KINDS["town"]) == 3
    assert dwellings_shown(manifest, KINDS["hamlet"]) == 40, "a hamlet counts every house it draws"


def test_the_upper_tiers_arithmetic_is_the_check_on_which_list_is_right() -> None:
    """Minami declares 2,600 and draws 520 non-farm dwellings - five to a household, exactly, with its
    148 farmhouses excluded. That is the city convention the GM described, and it is what proves the
    count reads `buildings` rather than `houses`."""
    manifest = {"houses": [{}] * 148, "buildings": [{"kind": "merchant"}] * 520}
    assert dwellings_shown(manifest, KINDS["city"]) * PER_HOUSEHOLD == 2600


def test_dwellings_shown_survives_a_manifest_with_nothing_in_it() -> None:
    assert dwellings_shown({}, KINDS["city"]) == 0
    assert dwellings_shown({}, KINDS["hamlet"]) == 0


def test_a_thousands_separator_on_a_city() -> None:
    assert "population ~3,000" in size_sentence(KINDS["city"], {"population": 3000}, 260)


@pytest.mark.parametrize(
    ("meta", "houses", "want"),
    [({}, 0, ""), ({}, 15, "15 farmhouses"), ({"households": 15}, 0, "population ~75")],
)
def test_each_figure_is_omitted_cleanly_when_it_is_not_known(meta: dict[str, object], houses: int, want: str) -> None:
    assert size_sentence(KINDS["hamlet"], meta, houses) == want


# --- where it is: authored, and omitted when unauthored ---


def test_where_sentences_read_every_authored_fact() -> None:
    got = " ".join(where_sentences("hamlet", NOTES.place))
    assert "village district of Hoshigaoka, which lies east" in got
    assert "An Imperial road passes directly south of here." in got, "the road LIES south; it does not head south"
    assert "part of Hayakawa county" in got
    assert "The town of Hayakawa lies further south." in got


def test_a_village_heads_its_district_rather_than_belonging_to_one() -> None:
    """`l7r.md`, the GM's own Place Names block: "a village and its district" share a name."""
    got = where_sentences("village", {"district": "Hoshigaoka"})
    assert got == ["It is the main village of the Hoshigaoka district, which takes its name."]


def test_nothing_authored_means_nothing_said() -> None:
    assert where_sentences("hamlet", {}) == []


def test_a_district_with_no_direction_is_still_named() -> None:
    assert where_sentences("hamlet", {"district": "Kawakami"}) == ["It belongs to the village district of Kawakami."]


def test_a_town_with_no_direction_falls_back_to_its_role() -> None:
    assert where_sentences("hamlet", {"town": "Hayakawa"}) == ["The town of Hayakawa is the county seat."]


@pytest.mark.parametrize("also", ["the magistrate's hunting lodge stands north-west", "a ford lies west."])
def test_the_free_also_line_is_punctuated_once(also: str) -> None:
    got = where_sentences("hamlet", {"also": also})
    assert got[0].endswith(".") and not got[0].endswith("..")


# --- the lane's default destination (spec FR-021) ---


def test_the_lane_leads_to_the_district_the_notes_name() -> None:
    assert (
        lane_default("hamlet", NOTES.place)
        == "The connector track leads out of the hamlet toward Hoshigaoka, the main village of the district it belongs to; the lanes between the farmsteads feed it."
    )


def test_the_lane_default_states_no_direction_even_when_the_notes_record_one() -> None:
    """The direction a district LIES in is not the direction its track LEAVES in (settlement-review,
    2026-08-29): Akagahara's and Ikegami's connectors run SOUTH to the Imperial road while Hoshigaoka
    lies east and north-east along it, so composing the sentence from `district direction` made both
    pages contradict their own ink. A route off the sheet is not something the map knows."""
    with_dir = lane_default("hamlet", NOTES.place)
    without = lane_default("hamlet", {"district": "Hoshigaoka"})
    assert with_dir == without, "the recorded direction changes nothing"
    for word in ("east", "north", "south", "west"):
        assert word not in with_dir


@pytest.mark.parametrize(("scale", "place"), [("hamlet", {}), ("village", {"district": "Hoshigaoka"}), ("town", {"district": "X"})])
def test_no_default_where_there_is_nothing_to_name(scale: str, place: dict[str, str]) -> None:
    """A village IS the main village, so its lanes lead nowhere else by default; a hamlet with no
    district recorded has no name to give, and the class's own explanation states the rule in general
    terms without it."""
    assert lane_default(scale, place) == ""


# --- the assembled card ---


def test_the_card_on_the_reference_hamlet() -> None:
    card = place_card(HAMLET, PADDY, NOTES, M15)
    assert card is not None
    assert card["name"] == "Inashiro"
    assert card["what"].startswith("Inashiro is a hamlet of 15 farmhouses, population ~75:")
    assert "no headman of its own" in card["what"]
    assert "The flooded fields grow rice." in card["why"]
    assert "village district of Hoshigaoka, which lies east" in card["why"]
    assert card["lead"] == "", "the card does not announce accuracy either (spec FR-001)"


def test_the_card_states_the_basis_for_what_it_takes_from_canon() -> None:
    """Spec FR-008a - the GM's liberty rule applied to this surface. Without it the card would print
    a self-declared deliberate deviation under a page-wide presumption of accuracy."""
    card = place_card(HAMLET, PADDY, NOTES, M15)
    assert card is not None and card["caveat"] == BASIS_LEAD + BASIS
    assert card["caveat"].startswith("What this rests on: "), "NOT 'On the drawing:' - this is sourcing, not drawing"
    assert "Rokugan's own arithmetic" in BASIS
    assert "the Edo record has branch hamlets that kept their own officials" in BASIS


def test_the_card_ranks_tiers_and_never_kinds_of_hamlet() -> None:
    """The GM asked which TYPE of hamlet is commonest; nothing answers it, so nothing is claimed.
    The TIER ranking the setting does support sits in the BODY, where a reader meets it, not in the
    fine print (settlement-review, 2026-08-29: it was the one fact the GM asked about by name and it
    had been buried in the quietest text on the card)."""
    card = place_card(HAMLET, PADDY, NOTES, M15)
    assert card is not None
    assert "the commonest kind of settlement there is" in card["what"], "the tier ranking is body text"
    assert "1,296" in card["what"] and "40%" in card["what"]
    # ...and the ranking is of TIERS. No kind of hamlet is ranked anywhere on the card.
    assert "none says which KIND of hamlet is commonest" in BASIS
    assert "kind of hamlet" not in card["what"]


def test_a_map_with_no_notes_at_all_still_describes_itself() -> None:
    """Spec Story 2 AS6, and the normal case for most of the pool."""
    card = place_card(HAMLET, PADDY, EMPTY, M15)
    assert card is not None
    assert "15 farmhouses, population ~75" in card["what"]
    assert card["why"].startswith("The flooded fields grow rice.")
    assert "district of" not in card["why"], "nothing is asserted that nothing authored"


def test_no_tier_restates_its_own_noun_after_the_colon() -> None:
    """ "Ubame is a town of 82 dwellings, population ~590: a county town: the lowest level ..." - the
    noun twice and the colon twice (settlement-review round 4). The card supplies "is a <noun>"; the
    tier text continues that sentence rather than restarting it."""
    for scale, kind in KINDS.items():
        assert ":" not in kind.what.split(".")[0], f"{scale}: the tier text opens with a second colon"


@pytest.mark.parametrize("scale", sorted(KINDS))
def test_every_tier_the_generator_supports_has_a_card(scale: str) -> None:
    card = place_card({"scale": scale, "name": "Somewhere", "households": 20, "population": 100}, PADDY, EMPTY, {"houses": [{"x": 0.0, "y": 0.0}] * 20})
    assert card is not None and card["what"].startswith("Somewhere is a ")


def test_an_unknown_tier_gets_no_card_rather_than_a_wrong_one() -> None:
    assert place_card({"scale": "megalopolis"}, PADDY, EMPTY, M15) is None
    assert place_card({}, PADDY, EMPTY, M15) is None


def test_only_a_hamlet_carries_the_hamlet_basis() -> None:
    card = place_card({"scale": "village", "name": "Hoshigaoka", "households": 70}, PADDY, EMPTY, {"houses": [{"x": 0.0, "y": 0.0}] * 70})
    assert card is not None and card["caveat"] == ""


def test_an_unnamed_settlement_does_not_produce_a_blank_sentence() -> None:
    card = place_card({"scale": "hamlet"}, set(), EMPTY, {})
    assert card is not None and card["what"].startswith("This settlement is a hamlet:")


@pytest.mark.parametrize(("items", "want"), [([], ""), (["a"], "a"), (["a", "b"], "a and b"), (["a", "b", "c"], "a, b and c")])
def test_join(items: list[str], want: str) -> None:
    assert join(items) == want


def test_place_keys_names_exactly_what_the_card_reads() -> None:
    """`interactive/CLAUDE.md` tells authors that `PLACE_KEYS` is the list the card understands, and
    `where_sentences` reads its keys literally - so the roster is DERIVED, not maintained, and the
    doctrine (clause 14) says bind it with a guard rather than trust it (settlement-review nitpick,
    2026-08-29). Feeding one key at a time is the census: a key that produces nothing is not read.
    """
    reads = {k for k in PLACE_KEYS if where_sentences("hamlet", {k: "X"}) or where_sentences("village", {k: "X"})}
    # `district direction`, `town direction` and the county only ever qualify another key, so they
    # produce nothing alone - they are read, and this is how they show it.
    qualifiers = {"district direction", "town direction"}
    for k in qualifiers:
        assert where_sentences("hamlet", {"district": "D", "town": "T", k: "X"}) != where_sentences("hamlet", {"district": "D", "town": "T"}), f"{k} is not read"
    assert reads | qualifiers == set(PLACE_KEYS), f"PLACE_KEYS and the card disagree: {set(PLACE_KEYS) ^ (reads | qualifiers)}"
