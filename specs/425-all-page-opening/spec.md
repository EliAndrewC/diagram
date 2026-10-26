# Feature 425: the single-page record opens the same way as the home page

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-26

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-26, "yess all.html should indeed get the same opening"

**Input**: `request.md` (the GM's words, verbatim).

## Why

Feature 424 gave the record's home page an opening on what the research is for - the maps and the money pages, each linked -
kept in `research/contents.json`'s `opening`. The single-page record (`all.html`, `record/site.py` `_single`) still opens with
"Every question the maps were researched from, every note behind them and every source they cite, on one page", which names only
the maps.

## User Scenarios & Testing

1. A reader opening `all.html` reads, under its title, the same opening the home page carries (from the same `opening` text), then
   the line that points to the record a page per question.

**Acceptance**:
1. `all.html` carries the opening, read from `contents.json`'s `opening` - one text for both pages, so they cannot drift.
2. The maps-only sentence is gone; the pointer to the per-question pages ("the contents") stays, after the opening.

## Requirements

- **FR-001**: `_single` writes `contents.load_opening` under its title, before the page's pointer to the contents; the pointer's
  sentence no longer says the record is the maps' alone.
- **FR-002**: A record test pins that `all.html` carries both links and that they come before the pointer to `index.html`.

## Success Criteria

- **SC-001** (FR-001, FR-002): the built `all.html` opens with the opening; the test passes; `make done` is green at the landing.
