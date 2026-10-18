# Feature 389: A money section of the research record

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-18

**Status**: Draft

**Affects**: research record, research process

**Approved**: the GM, 2026-10-18, "I do approve of you making a diagram tooling change that adds the issue watch file and a diagram feature for the money research section of the research record."

**Input**: `request.md` (the GM, 2026-10-18)

## Why

The GM wants a money skill in gm-assistant: a coherent way to say what things cost in Rokugan, built on historical
research (request.md). Prices, wages, coinage, credit and land values are research questions of exactly the kind this
record already answers rigorously. The record has the search pass, the archive, verbatim citations and the checking
agents. Copying that machinery into gm-assistant would leave two copies of it to drift apart. So the research is done
HERE, in this record, and the skill cites it. The GM agreed (request.md, second and third messages): *"you would say what
research you need, they would do the research, and then you would be able to pull the research when they're done."*

The record has no home for these questions yet:
- **No section.** No subject tag or contents section covers prices, wages, coinage or credit.
- **No close.** A `research record` feature closes through `make impl-check`, which asks which engine code each changed
  question drives. Money questions drive no code here; their consumer is another repository.
- **No protocol.** The two sessions coordinate through GitHub issues (issue watch, landed on main 2026-10-18), but nothing
  says what a request carries or what an answer returns.

This feature supplies those three, and answers the first questions the existing notes raise
(`/host-l7r-repo/money/digest.md`, the GM's old emails and spreadsheets digested on 2026-10-18).

## User Scenarios & Testing

### User Story 1 - A money question has a home in the record (Priority: P1)

A page session writes a question about the price of farmland, a day wage or a coin's worth. It tags it `money`. The built
record lists it under a "Money and prices" section, with no drawing page, and every existing check runs on it unchanged.

**Why this priority**: without a home, nothing else in this feature can land.

**Independent Test**: build the record with one money question present. It appears in the new section. `make record-owed`
names its checks like any other question's, and no check refuses it for lacking a drawing page.

**Acceptance Scenarios**:

1. **Given** a question tagged `money`, **When** the record is built, **Then** it is listed under "Money and prices" and
   has no drawing page.
2. **Given** that question changed in a `research record` feature, **When** `make impl-check F=<n>` runs, **Then** it
   accepts a `no code implements it` line that names the gm-assistant money skill as the consumer and says what was
   searched.

### User Story 2 - The gm-assistant session asks, a diagram session answers (Priority: P1)

The gm-assistant session opens an issue on `EliAndrewC/diagram` asking for a money question. A diagram session the GM starts
watches it, acknowledges it, and works the pages in page sessions. It answers on the issue with the question files, their
verdicts and the figures the record now supports. The asking side verifies the answer and closes the issue.

**Why this priority**: this is how all later money research reaches the skill.

**Independent Test**: the first seeded question goes through the protocol end to end, and its issue closes with the
fragment files named.

**Acceptance Scenarios**:

1. **Given** an issue that asks for a money question, **When** a diagram session works it, **Then** its answer names each
   question fragment FILE (never a built page), the verdict of each figure (ATTESTED, ATTESTED ONLY FOR, NOT ATTESTED or
   SILENT) and anything left open.
2. **Given** a request whose figure contradicts the GM's canon (`setting/l7r.md` "Money", `setting/budgets.md`), **When**
   it is answered, **Then** the answer reports the history and leaves the canon as it is. The canon wins in the skill;
   the record records what history says.

### User Story 3 - The first questions are answered (Priority: P2)

The four questions the notes left open are written, checked and cited:
- **Q1 - land price against yield.** What farmland sold for, in years of its net yield, in Tokugawa Japan and Qing China.
  The GM has asked this since 2013; Rokugan's "~50 koku, ~20 times the yearly profit" is *"based largely on nothing"*.
- **Q2 - unskilled day wages.** Day wages in rice and coin, city against countryside, Japan in the 18th century and
  China.
- **Q3 - the koku of rice.** The volume and weight of a koku of rice, the historical measure beside the canon's 40
  gallons. The 2017 spreadsheet converts at 151.5 kg (its silver-per-zeni constant 2.257575 = 100 zeni per 151.5 kg at
  1.49 g/kg). That is 40 gallons read as 151 kg, while 40 gallons of uncooked rice weighs nearer 120 kg.
- **Q4 - the Kyoto basket.** Bassino & Ma's Japan Basket A, 1745-54, with its quantities and silver prices, quoted
  verbatim from the paper. This is the basket the PPP conversion re-prices.

**Why this priority**: the skill's first conversion (PPP dollars per koku) rests on Q3 and Q4. Its wages and land rules
rest on Q1 and Q2.

**Independent Test**: each question's fragment exists, carries its verbatim citations, and has passed `quote-check`,
`source-reader` and `source-applicability`.

**Acceptance Scenarios**:

1. **Given** the four questions, **When** the feature closes, **Then** each is checked, and its issue on `EliAndrewC/diagram`
   is answered and closed by the asking side.

### Edge Cases

- **A question also bears on a map** (a market's prices beside its stalls). It takes both tags; a drawing page follows
  only if the maps draw it, under the existing rules.
- **The history disagrees with the canon.** The finding is recorded as found. The skill states the canon and labels the
  difference as a deliberate deviation, never the reverse.
- **A source is the GM's own book** (Goldsmith's *Premodern Financial Systems*, McClain & Wakita's *Osaka*). It goes on
  `research/to-download.md`; the GM's 2013-2017 summaries are leads, never citations.
- **A Japan-first question.** Tokugawa price and wage series are the richest data, so a request may name Japan first. The
  pass contract already follows the prompt.

## Requirements

### Functional Requirements

- **FR-001**: The record MUST have a `money` subject tag ("Money and prices": coinage, prices, wages, credit, land values,
  taxes as money) and a contents section listing the questions that carry it.
- **FR-002**: A question tagged only `money` MUST build and pass every record check without a drawing page.
- **FR-003**: A `research record` feature that changes a money question MUST close `make impl-check` with a `no code
  implements it` line that names the consumer (gm-assistant's money skill) and states what was searched.
- **FR-004**: The request and answer protocol MUST be written where a diagram session reads it before working a money
  issue. It states what a request carries (the question, the figure the skill needs, the canon it must sit beside) and
  what an answer returns (fragment files, verdicts, open items). Closing follows the user-level "Working a GitHub issue"
  rule.
- **FR-005**: Q1-Q4 MUST be written in page sessions, at most four questions a write, and checked by the existing agents
  unchanged.
- **FR-006**: Nothing in this feature changes engine code, a map, or the GM's canon.

### Key Entities

- **Money question**: a research question tagged `money`, with findings, notes and originals and no drawing page.
- **Money request**: a GitHub issue on `EliAndrewC/diagram` from the gm-assistant agent, asking for one or more money
  questions.

## Success Criteria

### Measurable Outcomes

- **SC-001**: The built record lists 4 money questions under their section, and each has 0 open check findings.
- **SC-002**: Each of Q1-Q4 has at least one verbatim, checked citation, or an absence note saying what was searched.
- **SC-003**: Every money request issue opened during the feature is closed by its asker, with the fragment files named.
- **SC-004**: `make impl-check F=389` reports nothing missing.

## Decisions Recorded

This feature draws nothing and states nothing on a map. Its decisions are about the record:

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Money research lives in this record, not in gm-assistant | process decision (the GM, 2026-10-18) | one checked research machinery, no copy to drift | `request.md`; this spec |
| Money questions carry no drawing page | map drawing convention (none drawn) | no map draws a price | the section's description in `research/contents.json` |
| Canon over history in the skill; history recorded as found | process decision (CLAUDE.md: never contradict the GM's notes) | the record reports, the skill rules | FR-004's protocol text |

## Assumptions

- The GM starts the diagram session that works each money issue; this repository does not run sessions by itself.
- The gm-assistant money skill is a separate gm-assistant feature. Only its existence as the consumer matters here.
- Issue watch works on both repositories with the tokens the GM granted on 2026-10-18 (checked: write access answers 422,
  not 403, on both).
