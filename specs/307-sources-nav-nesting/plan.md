# Implementation Plan: the sources nested by section and kind; URLs as links; the campaign notes on GitHub

**Branch**: none (main, clone `diagram-organization`) | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)

## Summary

The registry's works, already grouped by section (feature 305), are grouped once more by their primary kind. One
builder method, `Build.shelves`, gives section -> kind -> works, and the sidebar, the sources index, the one-page record
and the home page all draw from it. Bare URLs in citation lines are made links by one function, `sources.linkify`,
called where a citation line is rendered. The 16 canon entries' citation lines are rewritten once to cite GitHub, by a
spec-local script that computes each anchor from the notes' headings.

## Technical Context

- Python 3.12 engine (`l7r/diagram/interactive/`), the site's JS and CSS, registry HTML fragments.
- Testing: pytest through `make test-file` / `make done`; 100% coverage.
- Constraints: two builds byte-identical; no file past 1,000 lines (`site.py` about 440).

## Constitution Check

- I, II, III, IV, V, VII, VIII, IX: N/A. No pool content, no in-world prose, no SOURCE block. The canon entries' citation
  lines are registry text, not the GM's writing; the notes themselves are read only for their headings.
- VI: PASS. Every task names its verification; the closing task runs `make record CHECK=1` and `make done`.
- X: PASS. New behavior is tested (nesting, linkify, canon links, the site-wide no-bare-URL check); ruff, pyrefly, 100%.
- XII: N/A for the world. No map decision.
- XIII: PASS. Feature 305's green gate (126 s, 2026-10-02) on the same base is the baseline; zero new failures.
- XVI: the decisions below are reviewed by `spec-fidelity` (MODE 4).

## Decisions

**D1 - The second level is the primary kind**, in `source-tags.json` order. `Catalog.by_kind` groups; the canon,
untagged, stands under no kind and its section lists its works directly.

**D2 - The sidebar.** The Sources group's sections are the works sections themselves (no "Sources" node), each with key
`sources/<section id>`, its kinds `sources/<section id>/<kind id>`, linking `sources/index.html#<section id>` and
`#<section id>-<kind id>`. A source's own page opens its section and kind. The ids are claimed by the build's id check.

**D3 - The pages.** The sources index: section `h3`, kind `h4` (`works-kind`, its explanation as the tooltip), then the
works. The one-page record: the same, entries at `h5`, its contents nesting sections and kinds. The home page: the
"Sources" heading links the index, with the sections and their kinds nested beneath. The registry pager walks
section -> kind -> registry order.

**D4 - `linkify`** in `sources.py`: a bare `http(s)` URL outside every tag, comment, link, script and style becomes
`<a href=URL target="_blank" rel="noopener">URL</a>`, its sentence punctuation and an unopened parenthesis left outside
(the rule `link_target` already follows). `site_pages.shell` calls it on every page's content, so a URL shown anywhere
on a page is a link (FR-006 as amended); `works_html` and `Build.entry_html` also call it on the citation line, which
is idempotent.

**D5 - The canon rewrite** (`migrate/canon_links.py`, one-time): each quoted section on a canon citation line is found
among its file's headings - by plain text (markdown emphasis dropped), else by a unique prefix - and followed by
`(.../setting/<file>.md#<anchor>)`, the anchor by `sources.github_anchor` over all headings in order (so a repeat takes
`-1`). The "(URL: none ...)" parenthesis becomes the file's URL. A name not found is refused; the run found 36 of 36.
The headings were read from the public files on GitHub.

**D6 - The rule for future entries**: `research/CLAUDE.md` says a canon entry cites GitHub this way, and that a citation
line carries its URL in plain text because the build links it.

## Project Structure

```text
.claude/skills/diagram/l7r/diagram/interactive/{sources,citations}.py, record/{site,site_pages,source_tags}.py
.claude/skills/diagram/research/assets/site.css            the kind heading
.claude/skills/diagram/research/sources/010-works-cited/*  the 16 canon citation lines
.claude/skills/diagram/research/CLAUDE.md                   the rule
.claude/skills/diagram/tests/interactive/test_{record_site,citations}.py
specs/307-sources-nav-nesting/migrate/canon_links.py
```
