"""The record is written per entry and assembled into the pages a reader opens (feature 258).

The one property everything else rests on: taking a page apart and putting it back gives the same
bytes. It is asserted over the REAL record rather than a fixture, because a fixture and the record
drift apart and agree with themselves separately while they do it.

Byte-identity alone is not enough, and the registry is why (spec FR-008a, research R1): splitting and
rejoining is lossless wherever you cut, so a splitter that cut inside an HTML comment - `SOURCES.html`
holds an 8,042-byte one with two whole `<h2>` groups in it - would assemble back byte-for-byte while
writing two fragments no reader's page has. So the section COUNT and the heading IDS are asserted too.
"""

from __future__ import annotations

import pathlib

import pytest

from l7r.diagram.interactive.record import assemble, sections_of, split
from l7r.diagram.interactive.record.store import check
from l7r.diagram.interactive.sources import RESEARCH_DIR

RECORD = pathlib.Path(RESEARCH_DIR)


def record_pages() -> list[str]:
    """Every hand-authored page of the record, as a path relative to it."""
    top = sorted(p.name for p in RECORD.glob("*.html"))
    cities = sorted(f"cities/{p.name}" for p in (RECORD / "cities").glob("*.html"))
    return top + cities


@pytest.mark.parametrize("page", record_pages())
def test_a_page_splits_and_assembles_back_to_the_same_bytes(page: str) -> None:
    """FR-006, FR-013, SC-003: concatenation with no normalization, over the whole record."""
    text = (RECORD / page).read_text(encoding="utf-8")
    assert assemble(split(text)) == text


def test_every_committed_page_is_what_its_fragments_assemble() -> None:
    """FR-003 at the gate: a page edited instead of its fragments, or a fragment edited and the page
    not rebuilt, fails here. The PUSH runs the same check (`sync-with-main.sh`), because a
    record-only change takes the DIRECT route and never reaches the gate at all.

    A page not split yet is not a failure - `check` passes over it - so a stage that has not landed
    does not turn this red."""
    assert check(str(RECORD)) == [], "a committed page differs from its fragments - run `make record`"


def test_a_heading_inside_a_comment_is_not_a_section() -> None:
    """FR-008a on the registry, the file that has one: three sections, not the five a plain count gives."""
    text = (RECORD / "SOURCES.html").read_text(encoding="utf-8")
    ids = [section.id for section in sections_of(text)]
    assert ids == ["works-cited", "attested-instances-anchors-not-works", "setting-canon"]


def test_a_heading_is_found_wherever_it_stands_on_its_line() -> None:
    """FR-008a's other half, on plain strings: a heading after a space opens a section, one in a
    comment does not, and the comment goes to the fragment it falls inside."""
    page = '<!DOCTYPE html>\n<h1 id="t">T</h1>\n<p>front</p>\n<!-- <h2 id="dead">Dead</h2>\n<p>commented out</p> -->\n <h2 id="live">Live</h2>\n<p>body</p>\n</main>\n</body>\n</html>\n'
    parts = sections_of(page)
    assert [s.id for s in parts] == ["live"]
    assert "commented out" in split(page).front
    assert assemble(split(page)) == page
