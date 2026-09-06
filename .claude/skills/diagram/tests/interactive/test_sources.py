"""`interactive/sources.py` - reading a research entry's headings and the keys those sections cite.

Both cases here are defects that SHIPPED and were invisible in the artifact: the page still rendered a
plausible list of sources, just not the right one. Caught by the settlement-review's acceptance
re-check, 2026-08-29."""

import glob
import os
import pathlib
import re

from l7r.diagram.interactive.sources import RESEARCH_DIR, RESEARCH_URL, _sections, research_questions, research_sources, section_sources


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


# ---- feature 190: every source in a research finding is a link ------------------------------------------------
# The classifier below is THE rule (spec FR-001/FR-005, D5): the one-off sweep that converted the record imported
# it from here, so the rule has one body. It reads the CITATION LINE - the first paragraph of an entry - never the
# *Used for:* notes, which can say SUMMARY-ONLY about a different claim drawn from a read document.

_HEADING = re.compile(r"^### `([a-z0-9][a-z0-9-]*)`$", re.M)
_URL = re.compile(r"https?://[^\s)\]>]+")
_LINKED = re.compile(r"\[`([a-z0-9][a-z0-9-]*)`\]\(([^)]*)\)")
_BARE = re.compile(r"(?<!\[)`([a-z0-9][a-z0-9-]*)`(?!\]\()")


def citation_lines(sources_md: str) -> dict[str, str]:
    """key -> the entry's citation line (its first paragraph)."""
    parts = _HEADING.split(sources_md)
    return {parts[i]: parts[i + 1].strip().split("\n\n")[0] for i in range(1, len(parts), 2)}


def not_read(cite: str) -> bool:
    """The record says the document was NOT read: SUMMARY-ONLY, `URL: none`, or the URL recorded as
    unfetched with no READ beside it (feature 143's re-sourcing pass recorded addresses it did not fetch).
    Where a line says both (`artic-pigsty-latrine`: the text READ through the museum's API, the page
    itself unfetched) the READ governs - the GM's qualifier is "which we were able to read"."""
    if "SUMMARY-ONLY" in cite or "URL: none" in cite:
        return True
    return bool(re.search(r"unfetched|not fetched", cite)) and "READ" not in cite


def link_target(key: str, cite: str, rel: str) -> str:
    """Where a citation of `key` links: the document's URL (the FIRST on the citation line, D2) when it was
    read, else the registry entry that says it was not (`rel` is '' from research/, '../' from cities/)."""
    m = _URL.search(cite)
    if not_read(cite) or m is None:
        return f"{rel}SOURCES.md#{key}"
    return m.group(0).rstrip(".,;:")


def research_files() -> list[str]:
    files = glob.glob(os.path.join(RESEARCH_DIR, "*.md")) + glob.glob(os.path.join(RESEARCH_DIR, "cities", "*.md"))
    return sorted(f for f in files if os.path.basename(f) not in ("SOURCES.md", "README.md", "CLAUDE.md"))


def test_the_registry_has_one_entry_per_key() -> None:
    """D6: two keys had two `### ` headings each, which gives one GitHub anchor two bodies and a citation two
    citation lines to choose from. Merged by feature 190; this keeps it so."""
    heads = _HEADING.findall(pathlib.Path(RESEARCH_DIR, "SOURCES.md").read_text(encoding="utf-8"))
    dupes = sorted({h for h in heads if heads.count(h) > 1})
    assert not dupes, dupes


def test_every_registry_key_cited_in_a_research_file_is_a_link_to_the_right_target() -> None:
    """Feature 190 (GM 2026-09-06: "I want all of our references to be links ... Any reference to an external
    document which we were able to read in order to do our research should be a link to that external
    document"). Every backticked registry key in every research file - in a Sources paragraph or in a
    finding's prose - is inside a markdown link, and the link goes where the classifier says. A new entry
    written with a bare key fails here; so does a link to the registry for a document that was read."""
    cites = citation_lines(pathlib.Path(RESEARCH_DIR, "SOURCES.md").read_text(encoding="utf-8"))
    assert len(cites) > 300, "the registry parsed"
    bare, wrong = [], []
    checked = 0
    for path in research_files():
        rel = "../" if os.sep + "cities" + os.sep in path else ""
        text = pathlib.Path(path).read_text(encoding="utf-8")
        name = os.path.relpath(path, RESEARCH_DIR)
        for m in _BARE.finditer(text):
            if m.group(1) in cites:
                bare.append(f"{name}: `{m.group(1)}`")
        for m in _LINKED.finditer(text):
            key, target = m.groups()
            if key in cites:
                checked += 1
                want = link_target(key, cites[key], rel)
                if target != want:
                    wrong.append(f"{name}: `{key}` -> {target} (want {want})")
    assert checked > 400, "the record's citations were found (non-vacuity)"
    assert not bare, "bare keys (write them as [`key`](url)):\n" + "\n".join(bare)
    assert not wrong, "mis-targeted keys:\n" + "\n".join(wrong)


def test_the_classifier_reads_the_citation_line_and_the_read_marker_governs() -> None:
    assert not_read("Paper X (https://a.b/c; SUMMARY-ONLY 2026-08-28)")
    assert not_read("The GM's notes (URL: none - unpublished)")
    assert not_read("Site Y (https://a.b/c; unfetched 2026-08-28)"), "an unfetched URL with no READ is not read"
    assert not not_read("Site Y - text READ via the API (https://a.b/c; unfetched 2026-08-28)"), "READ governs"
    assert not not_read("Paper Z (READ 2026-08-27) (https://a.b/c)")
    assert link_target("k", "Paper Z (READ) (https://a.b/c). More (https://d.e/f)", "") == "https://a.b/c", "the FIRST URL"
    assert link_target("k", "Paper X (https://a.b/c; SUMMARY-ONLY)", "../") == "../SOURCES.md#k"
    assert link_target("k", "Nothing with a URL at all", "") == "SOURCES.md#k"
