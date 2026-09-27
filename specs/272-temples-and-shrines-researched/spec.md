# Feature 272 - temples and shrines researched: the shrine gaps closed, and town monasteries and city temples ahead of their diagrams

**Feature Branch**: `272-temples-and-shrines-researched` (no branch; `export SPECIFY_FEATURE=272-temples-and-shrines-researched`)

**Created**: 2026-09-27

**Status**: specified; spec-fidelity round 1 CHANGES REQUIRED (4 items) - applied, round 2 next

**Input**: the GM's goal of 2026-09-27 and the coordination with the other sessions, in [`request.md`](request.md).

## Summary

The GM asked whether the shrine research is done and set a goal: close every research gap on shrines of the kind
feature 268 drew, with the public sources a session can reach; write down every source a human could fetch for
free that blocks a bot; and, where no other session covers it, research ahead of their diagrams the town
monastery, the city temple complex and the small city temple or shrine of a temple neighborhood - coordinating
through "Diagram supplemental". The research is recorded in the record the other maps use (`religion-and-death`),
checked as every entry is. A finding that contradicts the drawn country shrine (features 268 and 270, landed) is
applied to that sheet and map in this feature (the GM, 2026-09-12: research-driven map changes need no ask); a finding
about the town and city forms, which have no diagram yet, is written down for the feature that will draw them.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The country shrine's open questions are closed or honestly open (Priority: P1)

Every absence note and every labeled guess in the country-shrine questions (religion-and-death 090-128) gets a
second search with other tools and other queries; where a readable source answers, the claim is cited; where only
a human could fetch it (a bot-blocked page, a paywall-free scan behind a captcha), the source goes on the GM's
download list; where nothing answers, the absence note says what was searched twice.

**Acceptance Scenarios**:

1. **Given** an absence note in 090-128, **When** the second pass runs, **Then** it is either a citation or an
   absence note naming both searches, and any source a human could fetch is on `TO-DOWNLOAD.md`.
2. **Given** audit rows D50 (a small kuri's size) and D51 (a village shrine-temple's bell), **When** researched,
   **Then** each is answered in the record or recorded as silent after the search.

### User Story 2 - Town monasteries and town and city shrines (Priority: P1)

A reader finds, on `religion-and-death`, how many monasteries a county town keeps and who lives in one; how big a
town monastery's precinct and hall are, whether walled, and what stands in it; how big a town's own shrine and a
city's principal shrine (and China's city-god temple) are and where they stand; and who lives inside a city
temple's walls (audit group R2: B96 D66, B97 B98 D65, B101 C152, C147 D70).

### User Story 3 - The village temple and wayside shrines (Priority: P2)

A reader finds whether a village kept a parish temple of its own and how many villages shared one, what its
precinct held, and how many wayside shrines (jizō, dōsojin, a street Inari) a village or a town's streets carried
and where (audit group R3: A138 D64, A139, A140 D61 B103, and A144 as far as 269's burial group leaves it open).

### User Story 4 - The city temple and temple plans (Priority: P2)

A reader finds a city temple's monk count, the shops at its gate, its graveyard's sharing (audit group B37, handed
over by 269), what a temple precinct holds as a plan (gate, hall, bell tower, lecture hall, kuri, cloister,
cemetery) at what sizes in Japan and China, whether a city temple keeps a bell tower and a pagoda, and whether a
county seat or a city carries the Chinese state cult's buildings (audit group R4: B91 D78, C144, D75, D76 D77).

### User Story 5 - The city temple complex and the temple neighborhood (Priority: P1)

A reader finds how big a city temple complex's precinct and main hall are and how it is laid out, and what the small
temple and the small shrine of a temple neighborhood are: their sizes, what stands in them, how many to a block, and
how they pack along the street - the GM's "smaller city temples or smaller city shrines that would appear in a temple
neighborhood". (Audit row B97 pointed the city temple's size at 269's B37, which carries no size; this feature owns
both.)

### Edge Cases

- The GM's canon governs the setting: every village district has a country monk, every county town at least one
  preceptor in a town monastery per Order, every provincial city a provincial abbot in a subordinate temple, every
  domain capital a sovereign temple per Order (setting/l7r.md). The research reports the history against it and
  never overrides it.
- Burial (the graveyard's size, siting, sharing with a temple) is 269's group R1; this feature cites it.
- A finding that contradicts the Hoshigaoka country-shrine sheet or its village map is applied here (a task of this
  feature); nothing else here changes a map, a sheet or the engine, and a finding about an undrawn town or city form
  is written down for the feature that will draw it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every absence note and labeled guess in religion-and-death 010-128 and in the shrine and temple parts
  of 210 MUST get a second search (other
  tools and queries than the first, recorded in an HTML comment) and end as a citation, a download-list entry, or an
  absence note naming both searches. Sections another feature owns (burial and swept ground, 130-206, 269's group
  R1) are cited, not searched.
- **FR-002**: The audit rows handed over (R2, R3, R4, B37, A133, A135, D49-D56) MUST each be answered on
  `religion-and-death` in the ranges reserved for them (450-590 new; 310-330 new for B37; edits to 010, 020, 040, 050,
  070, 210, to 100-128 for A133, A135 and D49-D56, and to 204 after 269's R1 lands), or recorded as silent after the
  search. A144 (village cremation) takes only what 269's burial group R1 leaves open.
- **FR-006**: New questions in 450-590 MUST answer the city temple complex's precinct and main-hall size and layout,
  and the small temple and small shrine of a temple neighborhood - sizes, contents, how many to a block, how they pack
  along the street.
- **FR-003**: Every source only a human can fetch for free MUST be appended to the END of
  `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` in the GM's format (a heading, the believed link, a Google-search
  link, what rests on it, what blocked the fetch).
- **FR-004**: Every new or changed entry MUST pass the record's checks: `source-reader`, `quote-check`,
  `record-format`, `source-applicability` (before any source's numbers are used), and `entry-drift` on every modal
  whose entry moved.
- **FR-005**: The work MUST stay inside its claims in `/diagram/.clones/RESEARCH-CLAIMS.md`, report its handoffs to
  "Diagram supplemental" and to 271's owner, and mark 271's State table and 269's inventory when a group lands.

### Key Entities

- The record page `religion-and-death` (fragments), its citations page, the source registry and the glossary; the
  GM's download list; the claims file and the two inventories.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001): no absence note in 010-128 (outside 130-206) without a second, recorded search.
- **SC-005** (FR-006): the city temple complex and the temple-neighborhood temple and shrine each answered by a
  question with its sizes, or recorded silent.
- **SC-002** (FR-002): each handed-over row answered or recorded silent, by question.
- **SC-003** (FR-003): every human-fetchable source named in the work on the download list.
- **SC-004** (spec-wide; FR-004, FR-005): the record's tests green, every check's findings applied, the work
  pushed and the inventories marked.

## Assumptions

- "These kinds of shrines" means the village and country shrine feature 268 drew and the town and city temples and
  shrines the GM named; the city temple complex's DIAGRAM is not built here - only its research.

## Review history

- Round 1 (spec-fidelity, MODE 2, 2026-09-27): CHANGES REQUIRED - (1) the temple-neighborhood temple and shrine and the
  city temple complex's size were named but not required: User Story 5 and FR-006 added; (2) FR-001's second search
  widened to 010-128 and 210's shrine and temple parts, 130-206 cited as 269 R1's; (3) "changes no map" replaced - a
  finding against the drawn country shrine is applied here; (4) FR-002 names the edits to 100-128 for A133, A135,
  D49-D56, and A144's limit.
