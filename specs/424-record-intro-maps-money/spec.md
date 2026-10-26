# Feature 424: the record's home page opens with what the research is for - the maps and the money

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-25

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-25, "We should instead open with an explanation of what this research is for, i.e. our maps and our money stuff."

**Input**: `request.md` (the GM's words, verbatim).

## Why

The built record's home page (`research/site/index.html`, written by `record/site.py` `_home`) opens with its title and then "The
whole record on one page - every question, every note and every source, under one table of contents." A reader arriving there is
not told what the research is for: the toolkit's maps and its money pages.

## User Scenarios & Testing

1. A reader opening the record's home page reads first, under the title, what the research is for: the maps
   (https://l7r-gm-assistant.fly.dev/maps) and the money pages (https://l7r-gm-assistant.fly.dev/money), each a link, before the
   link to the whole record on one page and the table of contents.

**Acceptance**:
1. The opening names both uses and links both URLs exactly as the GM gave them.
2. The whole-record link stays, after the opening, no longer the first thing a reader reads.
3. The opening's words live in the record's own data (`research/contents.json`), not in Python, so a later wording change is a
   record edit, not an engine change (the reason feature 207 moved page prose to JSON).
4. The opening is true to the record: it claims nothing the record does not do (the maps draw from it; the money pages cite it).

## Requirements

- **FR-001**: `research/contents.json` carries the opening as HTML; the home page writes it under the title, before the
  whole-record link.
- **FR-002**: A record test pins that the home page carries both links and that the opening comes before the whole-record link.

## Success Criteria

- **SC-001** (FR-001, FR-002): the built `index.html` shows the opening with both links first; the test passes; `make done` is
  green at the landing.

## Review history

- spec-fidelity round 1 (2026-10-25): FAITHFUL. Aside (not in scope): `all.html` has its own maps-only opening line.
