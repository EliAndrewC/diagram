"""The registry is written per entry and assembled into the page a reader opens (feature 258; since feature 303 the
questions are one file each, and the registry is the one page still assembled from fragments).

The one property everything else rests on: taking a page apart and putting it back gives the same
bytes. It is asserted over the REAL record rather than a fixture, because a fixture and the record
drift apart and agree with themselves separately while they do it.

Byte-identity alone is not enough, and the registry is why (spec FR-008a, research R1): splitting and
rejoining is lossless wherever you cut, so a splitter that cut inside an HTML comment - `SOURCES.html`
holds an 8,042-byte one with two whole `<h2>` groups in it - would assemble back byte-for-byte while
writing two fragments no reader's page has. So the section COUNT and the heading IDS are asserted too.
"""

from __future__ import annotations

from l7r.diagram.interactive.record import assemble, sections_of, split
from l7r.diagram.interactive.sources import record_text


def test_the_registry_splits_and_assembles_back_to_the_same_bytes() -> None:
    """FR-006, FR-013, SC-003: concatenation with no normalization, over the real registry (assembled in memory since
    feature 301 - nothing assembled is committed, so there is no committed page to compare with)."""
    text = record_text("SOURCES.html")
    assert text and assemble(split(text)) == text


def test_a_heading_inside_a_comment_is_not_a_section() -> None:
    """FR-008a on the registry, the file that has one: four sections (feature 312 added the uncited works), not every
    heading a plain count would find."""
    text = record_text("SOURCES.html")
    ids = [section.id for section in sections_of(text)]
    assert ids == ["works-cited", "attested-instances-anchors-not-works", "setting-canon", "uncited-works"]


def test_a_heading_is_found_wherever_it_stands_on_its_line() -> None:
    """FR-008a's other half, on plain strings: a heading after a space opens a section, one in a
    comment does not, and the comment goes to the fragment it falls inside."""
    page = '<!DOCTYPE html>\n<h1 id="t">T</h1>\n<p>front</p>\n<!-- <h2 id="dead">Dead</h2>\n<p>commented out</p> -->\n <h2 id="live">Live</h2>\n<p>body</p>\n</main>\n</body>\n</html>\n'
    parts = sections_of(page)
    assert [s.id for s in parts] == ["live"]
    assert "commented out" in split(page).front
    assert assemble(split(page)) == page
