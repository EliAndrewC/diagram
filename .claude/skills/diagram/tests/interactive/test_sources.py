"""`interactive/sources.py` - reading a research entry's headings and the keys those sections cite.

Both cases here are defects that SHIPPED and were invisible in the artifact: the page still rendered a
plausible list of sources, just not the right one. Caught by the settlement-review's acceptance
re-check, 2026-08-29."""

from l7r.diagram.interactive.sources import RESEARCH_URL, _sections, research_questions, research_sources, section_sources


def test_an_entry_may_name_a_research_file_one_directory_down() -> None:
    """Feature 180, spec FR-012a - a latent defect the spec review noticed, fixed under Principle XIV. The
    file pattern was `research/([a-z-]+\\.md)` and could not match `research/cities/fabric.md`, so such an
    entry resolved to no sources and no questions with nothing said. No class named one on the day it was
    fixed; the question URL is built from the same match, so the silent miss would have become a silent
    broken link when the town and city vocabulary arrives."""
    entry = "research/cities/fabric.md - 'Urban commoners built in continuous street walls'"
    qs = research_questions(entry)
    assert len(qs) == 1 and qs[0]["url"] == RESEARCH_URL + "cities/fabric.md#urban-commoners-built-in-continuous-street-walls", qs
    assert research_sources(entry), "and its sources resolve too"


def test_a_heading_inside_a_code_fence_is_not_a_section() -> None:
    """GitHub does not anchor a heading inside a fenced block, and the numbering of a repeated heading
    counts only real headings - so the README's entry-format example (`## <stable anchor title>` in a
    fence) must be skipped, or every anchor after it in a file that carried one would be off by one."""
    import os

    from l7r.diagram.interactive.sources import RESEARCH_DIR

    headings = [h for h, _b in _sections(os.path.join(RESEARCH_DIR, "README.md"))]
    assert "<stable anchor title>" not in headings and "Citing" in headings


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
