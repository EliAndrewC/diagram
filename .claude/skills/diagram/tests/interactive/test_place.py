"""The place card (feature 154): what a reader gets for clicking the settlement's title placard.

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
    CROP_SENTENCES,
    CROPS,
    KINDS,
    PER_HOUSEHOLD,
    crop_sentence,
    join,
    lane_default,
    place_card,
    size_sentence,
    where_sentences,
)

HAMLET = {"scale": "hamlet", "name": "Inashiro", "households": 15}
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
    assert size_sentence(KINDS["town"], {"scale": "town", "population": 680}, 42) == "population ~680"


def test_a_town_and_a_city_do_not_state_a_dwelling_count() -> None:
    """The count would be a fact about the DRAWING read as a fact about the place: Tango is 3,000
    inhabitants drawn with 273 representative dwellings, and "~273 dwellings, population ~3,000" tells
    a reader something false. A hamlet's houses ARE its households, so there the figure means what it
    says (found while sweeping the pool's cards, 2026-08-29)."""
    for scale in ("town", "city"):
        assert "dwelling" not in size_sentence(KINDS[scale], {"population": 3000}, 273)
    assert KINDS["hamlet"].houses_noun == "farmhouses" and KINDS["city"].houses_noun is None


def test_a_thousands_separator_on_a_city() -> None:
    assert "population ~3,000" in size_sentence(KINDS["city"], {"population": 3000}, 273)


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
    assert "An Imperial road runs directly south." in got
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
    assert lane_default("hamlet", NOTES.place) == "The lanes lead east to Hoshigaoka, the main village of the district this hamlet belongs to."


def test_the_lane_default_needs_no_direction() -> None:
    assert lane_default("hamlet", {"district": "Kawakami"}).startswith("The lanes lead to Kawakami,")


@pytest.mark.parametrize(("scale", "place"), [("hamlet", {}), ("village", {"district": "Hoshigaoka"}), ("town", {"district": "X"})])
def test_no_default_where_there_is_nothing_to_name(scale: str, place: dict[str, str]) -> None:
    """A village IS the main village, so its lanes lead nowhere else by default; a hamlet with no
    district recorded has no name to give, and the class's own explanation states the rule in general
    terms without it."""
    assert lane_default(scale, place) == ""


# --- the assembled card ---


def test_the_card_on_the_reference_hamlet() -> None:
    card = place_card(HAMLET, 15, PADDY, NOTES)
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
    card = place_card(HAMLET, 15, PADDY, NOTES)
    assert card is not None and card["caveat"] == BASIS
    assert "the setting's own arithmetic rather than a historical finding" in BASIS
    assert "the Edo record has branch hamlets that did" in BASIS


def test_the_card_ranks_tiers_and_never_kinds_of_hamlet() -> None:
    """The GM asked which TYPE of hamlet is commonest; nothing answers it, so nothing is claimed."""
    assert "most numerous kind of settlement" in BASIS
    assert "none for which KIND of hamlet is commonest either" in BASIS
    card = place_card(HAMLET, 15, PADDY, NOTES)
    assert card is not None
    assert "commonest" not in card["what"] and "most common" not in card["what"]


def test_a_map_with_no_notes_at_all_still_describes_itself() -> None:
    """Spec Story 2 AS6, and the normal case for most of the pool."""
    card = place_card(HAMLET, 15, PADDY, EMPTY)
    assert card is not None
    assert "15 farmhouses, population ~75" in card["what"]
    assert card["why"].startswith("The flooded fields grow rice.")
    assert "district of" not in card["why"], "nothing is asserted that nothing authored"


@pytest.mark.parametrize("scale", sorted(KINDS))
def test_every_tier_the_generator_supports_has_a_card(scale: str) -> None:
    card = place_card({"scale": scale, "name": "Somewhere", "households": 20}, 20, PADDY, EMPTY)
    assert card is not None and card["what"].startswith("Somewhere is a ")


def test_an_unknown_tier_gets_no_card_rather_than_a_wrong_one() -> None:
    assert place_card({"scale": "megalopolis"}, 5, PADDY, EMPTY) is None
    assert place_card({}, 5, PADDY, EMPTY) is None


def test_only_a_hamlet_carries_the_hamlet_basis() -> None:
    card = place_card({"scale": "village", "name": "Hoshigaoka", "households": 70}, 70, PADDY, EMPTY)
    assert card is not None and card["caveat"] == ""


def test_an_unnamed_settlement_does_not_produce_a_blank_sentence() -> None:
    card = place_card({"scale": "hamlet"}, 0, set(), EMPTY)
    assert card is not None and card["what"].startswith("This settlement is a hamlet:")


@pytest.mark.parametrize(("items", "want"), [([], ""), (["a"], "a"), (["a", "b"], "a and b"), (["a", "b", "c"], "a, b and c")])
def test_join(items: list[str], want: str) -> None:
    assert join(items) == want
