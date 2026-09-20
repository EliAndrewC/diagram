"""Every refusal the record's fragments can raise (feature 258, spec FR-014, FR-020, SC-006).

The assembly never picks one of two possibilities and never drops what it does not recognize: a
skipped fragment is a lost entry of the record, and it would be lost silently. Each case below is one
row of `specs/258-*/contracts/fragment-format.md`, and each asserts what the MESSAGE names - the file,
and the thing - because a refusal a session cannot act on costs the same round trip as no refusal.
"""

from __future__ import annotations

import pathlib

import pytest

from l7r.diagram.interactive.record import assemble, split
from l7r.diagram.interactive.record import fragments as frag
from l7r.diagram.interactive.record.store import RecordError, check, read_page, write_fragments

PAGE = (
    '<!DOCTYPE html>\n<html lang="en">\n<head><title>T</title></head>\n<body>\n<main>\n'
    '<h1 id="t">T</h1>\n<p>front</p>\n<hr>\n\n'
    '<h2 id="first">First</h2>\n<p>one</p>\n\n'
    '<h2 id="second">Second</h2>\n<p>two</p>\n'
    "</main>\n</body>\n</html>\n"
)


@pytest.fixture
def record(tmp_path: pathlib.Path) -> pathlib.Path:
    """A record of one page, already split."""
    (tmp_path / "ways.html").write_text(PAGE, encoding="utf-8")
    (tmp_path / "cities").mkdir()
    write_fragments("ways.html", str(tmp_path))
    return tmp_path


def test_a_page_splits_into_the_fragments_its_layout_names(record: pathlib.Path) -> None:
    """The happy path first, so the refusals below are refusals and not a broken fixture."""
    assert sorted(p.name for p in (record / "ways").iterdir()) == [
        "010-first.html", "020-second.html", frag.FRONT, frag.TAIL,
    ]
    assert read_page("ways.html", str(record)) == PAGE
    assert check(str(record)) == []


def test_two_fragments_claiming_one_prefix_are_refused_rather_than_ordered(record: pathlib.Path) -> None:
    (record / "ways" / "010-another.html").write_text('<h2 id="another">A</h2>\n', encoding="utf-8")
    with pytest.raises(RecordError) as refusal:
        read_page("ways.html", str(record))
    assert "010-another.html" in str(refusal.value) and "010-first.html" in str(refusal.value)
    assert "will not choose between them" in str(refusal.value)


def test_a_file_that_is_not_a_fragment_name_is_refused_rather_than_skipped(record: pathlib.Path) -> None:
    (record / "ways" / "notes-to-self.html").write_text("<p>stray</p>\n", encoding="utf-8")
    with pytest.raises(RecordError) as refusal:
        read_page("ways.html", str(record))
    assert "notes-to-self.html" in str(refusal.value)
    assert frag.FRONT in str(refusal.value), "the message names what IS legal there"


@pytest.mark.parametrize("missing", [frag.FRONT, frag.TAIL])
def test_a_page_without_its_front_or_its_closing_is_refused(record: pathlib.Path, missing: str) -> None:
    (record / "ways" / missing).unlink()
    with pytest.raises(RecordError) as refusal:
        read_page("ways.html", str(record))
    assert missing in str(refusal.value) and "will not invent them" in str(refusal.value)


def test_a_page_with_no_fragment_directory_names_the_command_that_makes_one(record: pathlib.Path) -> None:
    (record / "towns.html").write_text(PAGE, encoding="utf-8")
    with pytest.raises(RecordError) as refusal:
        read_page("towns.html", str(record))
    assert "make record SPLIT=towns" in str(refusal.value)


def test_a_registry_entry_whose_filename_and_heading_disagree_is_refused(tmp_path: pathlib.Path) -> None:
    """The one case where a fragment's NAME carries meaning a reader relies on: a source's key."""
    registry = (
        '<!DOCTYPE html>\n<html lang="en">\n<head><title>S</title></head>\n<body>\n<main>\n'
        '<h1 id="s">S</h1>\n\n<h2 id="works-cited">Works cited</h2>\n<p>roster</p>\n'
        '<h3 id="work-fei-1939"><code>fei-1939</code></h3>\n<p>a book</p>\n'
        "</main>\n</body>\n</html>\n"
    )
    (tmp_path / "SOURCES.html").write_text(registry, encoding="utf-8")
    write_fragments("SOURCES.html", str(tmp_path))
    entry = tmp_path / "sources" / "010-works-cited" / "0010-fei-1939.html"
    assert entry.is_file(), "the entry is named by its key, not by its `work-` id"
    entry.rename(entry.with_name("0010-fei-1940.html"))
    with pytest.raises(RecordError) as refusal:
        read_page("SOURCES.html", str(tmp_path))
    assert "fei-1940" in str(refusal.value) and "fei-1939" in str(refusal.value)


def test_a_page_that_does_not_close_the_way_the_record_closes_is_refused(tmp_path: pathlib.Path) -> None:
    (tmp_path / "ways.html").write_text('<!DOCTYPE html>\n<h2 id="x">X</h2>\n<p>no closing run</p>\n',
                                        encoding="utf-8")
    with pytest.raises(ValueError, match="has not been shown its shape"):
        write_fragments("ways.html", str(tmp_path))


def test_a_heading_with_no_id_is_refused_rather_than_given_a_made_up_name() -> None:
    page = '<!DOCTYPE html>\n<h1 id="t">T</h1>\n<h2>Nameless</h2>\n<p>x</p>\n</main>\n</body>\n</html>\n'
    with pytest.raises(ValueError, match="a heading with no id"):
        split(page)


def test_an_exhausted_gap_is_refused_rather_than_collided(record: pathlib.Path) -> None:
    assert frag.free_prefix(10, 20) == "015"
    with pytest.raises(ValueError, match="re-space the directory"):
        frag.free_prefix(10, 11)


def test_a_page_whose_committed_bytes_drift_from_its_fragments_is_reported(record: pathlib.Path) -> None:
    """What the gate and the push run: FR-003, FR-004."""
    (record / "ways.html").write_text(PAGE.replace("<p>one</p>", "<p>edited in the wrong file</p>"),
                                      encoding="utf-8")
    assert check(str(record)) == ["ways.html"]


def test_a_page_that_is_not_split_yet_is_not_reported_as_stale(record: pathlib.Path) -> None:
    """A stage that has not landed is not a failure: stage 3's citations pages are whole until it does."""
    (record / "towns.html").write_text(PAGE, encoding="utf-8")
    assert check(str(record)) == []


def test_the_assembly_adds_nothing_of_its_own(record: pathlib.Path) -> None:
    """FR-006, FR-013: concatenation, and the fragments hold the record's bytes as they are."""
    page = split(PAGE)
    assert assemble(page) == PAGE
    assert page.front.endswith("<hr>\n\n")
    assert page.tail == "\n</main>\n</body>\n</html>\n", "the newline before the closing run is the tail's"
    assert "".join(s.text for s in page.sections) == PAGE[len(page.front): -len(page.tail)]
