"""The map-notes reader (feature 156).

The GM's requirement is a NEGATIVE one - *"resilient against that formatting not being present ...
default to simply not pulling anything in if the parsing fails"* - so most of this file is malformed
input, and the assertion is always the same: a usable result, and no exception. Every function under
test takes a plain string and returns a plain dict, which is the whole reason `section` and
`bullets` are module-level rather than inner functions (the closure rule, GM 2026-08-28).
"""

from __future__ import annotations

import os

import pytest

from l7r.diagram.interactive.notes import EMPTY, MapNotes, bullets, normalize_key, parse_map_notes, read_map_notes, section

GOOD = """# Design notes: Somewhere

Prose the parser must never touch, including a stray - **decoy**: not in a section.

## Map notes

<!-- a comment inside the block -->

### Place

- **district**: Hoshigaoka
- **district direction**: east
- **imperial road**: directly south

### Features

- **village lane**: The connector runs south to the road; the district's main village,
  Hoshigaoka, lies east along it.
- **windbreak**: Unusually deep here.

## Something else

- **ignored**: after the block
"""


def test_the_good_case_reads_both_halves() -> None:
    notes = parse_map_notes(GOOD)
    assert notes.place == {"district": "Hoshigaoka", "district direction": "east", "imperial road": "directly south"}
    assert notes.features["windbreak"] == "Unusually deep here."
    assert notes  # truthy when it carries anything


def test_a_wrapped_value_is_joined_into_one_line() -> None:
    lane = parse_map_notes(GOOD).features["village lane"]
    assert lane == "The connector runs south to the road; the district's main village, Hoshigaoka, lies east along it."
    assert "\n" not in lane


def test_prose_outside_the_block_is_never_parsed() -> None:
    notes = parse_map_notes(GOOD)
    assert "decoy" not in notes.place and "decoy" not in notes.features


def test_a_following_section_closes_the_block() -> None:
    assert "ignored" not in parse_map_notes(GOOD).place


# --- the resilience contract: every one of these yields a usable result and raises nothing ---


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("", id="empty file"),
        pytest.param("# Design notes\n\nJust prose.\n", id="no block at all"),
        pytest.param("## Map notes\n", id="block present but empty"),
        pytest.param("## Map notes\n\n### Place\n", id="subsection present but empty"),
        pytest.param("## Map notes\n\n### Place\n\n- district: Hoshigaoka\n", id="bullet with no bold key"),
        pytest.param("## Map notes\n\n### Place\n\n- **district** Hoshigaoka\n", id="bullet with no colon"),
        pytest.param("## Map notes\n\n### Place\n\n- **district**:\n", id="empty value"),
        pytest.param("## Map notes\n\n### Place\n\n- **dist", id="truncated mid-bullet"),
        pytest.param("## Map notes\n\n### Place\n\n  - **district**: Nested\n", id="nested list is not an entry"),
        pytest.param("## MAP NOTES\n\n### place\n\n- **district**:  \n", id="whitespace-only value"),
        pytest.param("###### Map notes\n### Place\n- **district**: x\n", id="a deeper heading closes on a shallower one"),
    ],
)
def test_malformed_input_yields_nothing_and_never_raises(text: str) -> None:
    """Not one of these shapes may produce a fact. A half-read key is worse than no key at all -
    the page would state it to a reader as if it had been authored."""
    notes = parse_map_notes(text)
    assert isinstance(notes, MapNotes)
    assert notes.place == {} and notes.features == {}


def test_a_block_with_nothing_usable_is_the_shared_empty() -> None:
    assert parse_map_notes("## Map notes\n\n### Place\n\nno bullets here\n") is EMPTY
    assert not EMPTY


def test_the_heading_is_found_at_any_level_and_any_case() -> None:
    for hashes in ("#", "##", "###", "####"):
        text = f"{hashes} MAP NOTES\n\n{hashes}# Place\n\n- **district**: Kawakami\n"
        assert parse_map_notes(text).place == {"district": "Kawakami"}


def test_a_duplicate_key_keeps_the_first() -> None:
    got = bullets("- **district**: First\n- **district**: Second\n")
    assert got == {"district": "First"}


def test_a_comment_or_a_table_does_not_continue_an_entry() -> None:
    got = bullets("- **district**: Hoshigaoka\n  <!-- note -->\n  | a | b |\n")
    assert got == {"district": "Hoshigaoka"}


def test_prose_between_entries_ends_the_one_above_it() -> None:
    got = bullets("- **a**: one\n\nSome prose at column zero.\n\n- **b**: two\n")
    assert got == {"a": "one", "b": "two"}


def test_markup_characters_survive_as_text() -> None:
    got = bullets("- **also**: the <smith> & the ford\n")
    assert got == {"also": "the <smith> & the ford"}


@pytest.mark.parametrize(
    ("raw", "want"),
    [("District", "district"), ("  district   direction ", "district direction"), ("`village lane`", "village lane"), ("**windbreak**", "windbreak")],
)
def test_normalize_key(raw: str, want: str) -> None:
    assert normalize_key(raw) == want


def test_section_returns_empty_when_the_heading_is_absent() -> None:
    assert section("# A\n\nbody\n", "map notes") == ""


def test_section_keeps_deeper_headings_in_the_body() -> None:
    body = section("## Map notes\n\n### Place\n\n- **a**: b\n", "map notes")
    assert "### Place" in body


# --- the file layer ---


def test_read_map_notes_on_a_real_file(tmp_path: object) -> None:
    path = os.path.join(str(tmp_path), "somewhere.notes.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(GOOD)
    assert read_map_notes(path).place["district"] == "Hoshigaoka"


def test_read_map_notes_on_a_missing_file_is_empty() -> None:
    assert read_map_notes("/nonexistent/nowhere.notes.md") is EMPTY


def test_read_map_notes_on_a_directory_is_empty(tmp_path: object) -> None:
    assert read_map_notes(str(tmp_path)) is EMPTY


def test_read_map_notes_survives_undecodable_bytes(tmp_path: object) -> None:
    path = os.path.join(str(tmp_path), "bad.notes.md")
    with open(path, "wb") as fh:
        fh.write(b"## Map notes\n\n### Place\n\n- **district**: Ho\xff\xfeshigaoka\n")
    assert read_map_notes(path).place["district"].startswith("Ho")
