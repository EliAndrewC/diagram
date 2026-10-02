"""Every refusal the registry's fragments can raise (feature 258, spec FR-014, FR-020, SC-006; the registry is the one
page of fragments left after feature 303 flattened the questions), and the reading of a question page's notes.

The assembly never picks one of two possibilities and never drops what it does not recognize: a skipped fragment is a
lost entry of the record, and it would be lost silently. Each case asserts what the MESSAGE names - the file, and the
thing - because a refusal a session cannot act on costs the same round trip as no refusal.
"""

from __future__ import annotations

import pathlib

import pytest

from l7r.diagram.interactive.record import assemble, split, store
from l7r.diagram.interactive.record import fragments as frag
from l7r.diagram.interactive.record.store import RecordError
from tests import _flat_record as fr

PAGE = (
    '<!DOCTYPE html>\n<html lang="en">\n<head><title>T</title></head>\n<body>\n<main>\n'
    '<h1 id="t">T</h1>\n<p>front</p>\n<hr>\n\n'
    '<h2 id="first">First</h2>\n<p>one</p>\n\n'
    '<h2 id="second">Second</h2>\n<p>two</p>\n'
    "</main>\n</body>\n</html>\n"
)


@pytest.fixture
def record(tmp_path: pathlib.Path) -> pathlib.Path:
    return fr.write(tmp_path)


def test_the_registry_reads_back_as_one_page(record: pathlib.Path) -> None:
    """The happy path first, so the refusals below are refusals and not a broken fixture."""
    page = store.read_fragments(store.REGISTRY, str(record))
    assert [s.id for s in page.sections] == ["works-cited"] and [e.id for e in page.sections[0].entries] == ["alpha", "beta"]
    html = store.registry_html(str(record))
    assert html.startswith("<!DOCTYPE html>") and html.index("alpha") < html.index("beta") and html.endswith("</html>\n")
    assert store.entry_level(store.REGISTRY) == 3 and store.entry_level("x.html") is None


def test_two_fragments_claiming_one_prefix_are_refused_rather_than_ordered(record: pathlib.Path) -> None:
    (record / "sources" / "010-another.html").write_text('<h2 id="another">A</h2>\n', encoding="utf-8")
    with pytest.raises(RecordError) as refusal:
        store.registry_html(str(record))
    assert "010-another.html" in str(refusal.value) and "010-works-cited.html" in str(refusal.value) and "will not choose between them" in str(refusal.value)


def test_a_file_that_is_not_a_fragment_name_is_refused_rather_than_skipped(record: pathlib.Path) -> None:
    (record / "sources" / "notes-to-self.html").write_text("<p>stray</p>\n", encoding="utf-8")
    with pytest.raises(RecordError) as refusal:
        store.registry_html(str(record))
    assert "notes-to-self.html" in str(refusal.value) and frag.FRONT in str(refusal.value), "the message names what IS legal there"


@pytest.mark.parametrize("missing", [frag.FRONT, frag.TAIL])
def test_a_page_without_its_front_or_its_closing_is_refused(record: pathlib.Path, missing: str) -> None:
    (record / "sources" / missing).unlink()
    with pytest.raises(RecordError) as refusal:
        store.registry_html(str(record))
    assert missing in str(refusal.value) and "will not invent them" in str(refusal.value)


def test_a_record_with_no_registry_is_refused_by_name(tmp_path: pathlib.Path) -> None:
    with pytest.raises(RecordError, match="sources/: no fragment directory"):
        store.read_fragments(store.REGISTRY, str(tmp_path))
    (tmp_path / "ways").mkdir()
    with pytest.raises(RecordError, match="towns/: no fragment directory for towns.html"):
        store.read_fragments("towns.html", str(tmp_path))


def test_a_registry_entry_whose_filename_and_heading_disagree_is_refused(record: pathlib.Path) -> None:
    """The one case where a fragment's NAME carries meaning a reader relies on: a source's key."""
    entry = record / "sources" / "010-works-cited" / "0010-alpha.html"
    entry.rename(entry.with_name("0010-alpha-2.html"))
    with pytest.raises(RecordError) as refusal:
        store.registry_html(str(record))
    assert "alpha-2" in str(refusal.value) and "`alpha`" in str(refusal.value)


def test_a_heading_with_no_id_is_refused_rather_than_given_a_made_up_name() -> None:
    page = '<!DOCTYPE html>\n<h1 id="t">T</h1>\n<h2>Nameless</h2>\n<p>x</p>\n</main>\n</body>\n</html>\n'
    with pytest.raises(ValueError, match="a heading with no id"):
        split(page)


def test_an_exhausted_gap_is_refused_rather_than_collided() -> None:
    assert frag.free_prefix(10, 20) == "015"
    with pytest.raises(ValueError, match="re-space the directory"):
        frag.free_prefix(10, 11)


def test_the_assembly_adds_nothing_of_its_own() -> None:
    """FR-006, FR-013: concatenation, and the fragments hold the record's bytes as they are."""
    page = split(PAGE)
    assert assemble(page) == PAGE
    assert page.front.endswith("<hr>\n\n")
    assert page.tail == "\n</main>\n</body>\n</html>\n", "the newline before the closing run is the tail's"
    assert "".join(s.text for s in page.sections) == PAGE[len(page.front) : -len(page.tail)]


def test_a_question_page_s_notes_are_its_own_and_a_page_without_any_has_none(record: pathlib.Path) -> None:
    assert list(store.page_notes("0001-lanes.html", str(record))) == ["alpha"]
    assert list(store.page_notes("0001-lanes.drawing.html", str(record))) == ["beta"], "the drawing page has its own"
    assert store.page_notes("0003-rows.html", str(record)) == {}
    (record / "questions" / "0003-rows.notes.html").write_text('<li data-note="k">a</li>\n<li data-note="k">b</li>\n', encoding="utf-8")
    with pytest.raises(RecordError, match="`k` is defined twice in one file"):
        store.page_notes("0003-rows.html", str(record))


def test_a_broken_record_loads_as_a_record_error(record: pathlib.Path) -> None:
    (record / "tags.json").unlink()
    with pytest.raises(RecordError, match="tags.json: missing"):
        store.load(str(record))


def test_the_small_refusals_of_the_layout() -> None:
    """What only a direct call can reach: a name with no prefix asked for its position, a page with no section, a page
    that does not close the way the record closes, a reference whose key is not a key."""
    from l7r.diagram.interactive.record.notes import NoteError, allocate

    with pytest.raises(ValueError, match="must be named <prefix>-<id>.html"):
        frag.position_of("_front.html")
    page = split('<!DOCTYPE html>\n<h1 id="t">T</h1>\n<p>only a front</p>\n</main>\n</body>\n</html>\n')
    assert page.sections == () and page.front.endswith("<p>only a front</p>")
    with pytest.raises(ValueError, match="has not been shown its shape"):
        split('<!DOCTYPE html>\n<h2 id="x">X</h2>\n<p>no closing run</p>\n')
    with pytest.raises(NoteError, match="`Bad Key` is not a note key"):
        allocate('<sup class="fn" data-note="Bad Key"></sup>', {}, "w")
    assert frag.page_dir("SOURCES.html") == "sources" and frag.page_dir("ways.html") == "ways"
