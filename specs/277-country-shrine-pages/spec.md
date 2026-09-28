# Feature 277 - country shrine sheets as interactive pages, from the same source as their PNG

**Feature Branch**: `277-country-shrine-pages` (no branch; `export SPECIFY_FEATURE=277-country-shrine-pages`)

**Created**: 2026-09-28

**Status**: specified; awaiting spec-fidelity

**Input**: the GM's request of 2026-09-28, verbatim in [`request.md`](request.md).

## Summary

The GM asked for the magistracy process applied to country shrine maps: one canonical source describing the map's
features, with both the PNG and the interactive HTML page downstream of it, so nothing is defined twice. A country
shrine sheet's tracked SVG is that source, as a magistracy sheet's is: every drawn element names its kind
(`data-kind`), the kinds' write-ups live once in the shared registry, and the sheet's generator renders the PNG and
writes the page from the same file, failing when any ink names no kind or a kind has no write-up.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A country shrine sheet has an interactive page (Priority: P1)

A reader opens `hoshigaoka-shrine.html` beside its PNG, hovers a feature and sees every feature of its kind light, and
clicks one for its write-up - what it is, why it stands there, whether it is accurate, a deviation, a drawing
convention or a guess, and the research questions behind it - exactly as on a magistracy page.

**Acceptance Scenarios**:

1. **Given** the country shrine's generator, **When** it runs, **Then** it writes the PNG and the HTML page from the
   one tracked SVG, and fails if any ink carries no kind or any kind has no write-up.
2. **Given** the page, **When** a kind is hovered or clicked, **Then** its kind lights and its write-up opens.

### User Story 2 - The process holds for every country shrine sheet (Priority: P1)

A new country shrine sheet added to the pool is held to the same rule without anyone remembering it: a test fails on a
sheet with untagged ink or an unregistered kind, and on a registered kind no shrine or magistracy sheet draws.

### Edge Cases

- A kind both a magistracy and a country shrine draw (a well, a latrine, a torii, the grove) is written once and serves
  both; where the country shrine's reads differently, the page's own notes carry the difference, not a second kind.
- The background and pure framing ink carry the ruled-out tag (`-`), as on the magistracy sheets.
- A write-up is written FROM the research record (religion-and-death 090-128, 540 where it applies); a kind the record
  does not cover says it is silent, as the magistracy kinds do.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every element of every country shrine sheet in the pool MUST carry a `data-kind` naming a registered kind,
  or `-`.
- **FR-002**: Every kind a country shrine sheet draws MUST have a write-up in the shared Mode A registry, in the
  magistracy kinds' form (`What:` / `Why:` / `Note:` / `Caveat:`, label, sources, `Entry:` into the research).
- **FR-003**: Each country shrine sheet's generator MUST render its PNG and write its HTML page from the same tracked
  SVG (`write_sheet_page`), and MUST fail on untagged ink or an unregistered kind.
- **FR-004**: The pool's tests MUST hold every country shrine sheet complete (FR-001, FR-002) and the registry closed
  over the sheets it serves, as they do for the magistracies.
- **FR-005**: The drawn sheet and its PNG MUST NOT change in appearance: this feature adds tags, write-ups and a page,
  not ink.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-003): `hoshigaoka-shrine.gen.py` writes the page with a clean census (no untagged ink, no
  unknown kind).
- **SC-002** (FR-002): every kind on the page has a complete write-up that resolves to a research section or says it is
  silent.
- **SC-003** (FR-004): the tests fail on a shrine sheet with an untagged element or an unregistered kind (proved on a
  seeded fault).
- **SC-004** (FR-005): the PNG before and after differs by no pixel.

## Assumptions

- "Country shrine maps" are the pool's `country-shrines/` sheets (today one, Hoshigaoka's); the village map that shows
  the shrine as a glyph is a Mode B map with its own page and is not in scope.
