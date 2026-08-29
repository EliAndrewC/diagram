"""`interactive/sources.py` - reading a research entry's headings and the keys those sections cite.

Both cases here are defects that SHIPPED and were invisible in the artifact: the page still rendered a
plausible list of sources, just not the right one. Caught by the settlement-review's acceptance
re-check, 2026-08-29."""

from l7r.diagram.interactive.sources import research_sources, section_sources


def test_a_double_quoted_research_heading_is_read_like_a_single_quoted_one() -> None:
    """A registry entry quotes a heading 'like this' - and "like this" when the heading itself carries
    an apostrophe, which the single-quote form cannot hold. Both must resolve to the same section.

    The defect this pins shipped: the marsh class names research/water.md's "A reservoir's shore is
    reeded, and its EMBANKMENT is mown", and with only the single-quote form the run of characters
    BETWEEN the two double quotes matched as one giant heading that no section is named, so the entry
    contributed nothing and swallowed the one after it."""
    entry = "research/water.md - \"A reservoir's shore is reeded, and its EMBANKMENT is mown\""
    assert "mineta-2007-tameike" in research_sources(entry)


def test_a_sources_line_that_wraps_keeps_the_keys_after_the_wrap() -> None:
    """`**Sources:**` is a paragraph, not a line. Matching to end-of-line dropped every key past the
    first physical line - invisibly, because the modal still showed a plausible shorter list. Measured
    on the same reeded-shore section: seven keys over two lines, four reaching the page."""
    body = "text\n\n**Sources:** `alpha-one`, `beta-two`,\n`gamma-three` (a note), `delta-four`.\n\nafter\n"
    assert section_sources(body) == ["alpha-one", "beta-two", "gamma-three", "delta-four"]
    assert section_sources("**Sources:** `only-one`\n\n`not-a-source`\n") == ["only-one"]
