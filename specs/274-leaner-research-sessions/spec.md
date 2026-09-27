# Feature Specification: Leaner research sessions

**Feature Branch**: `274-leaner-research-sessions` (no branch - `main`, per CLAUDE.md)

**Created**: 2026-09-27

**Status**: Draft

**Input**: the GM's request, verbatim in [`request.md`](request.md): implement all three of the session's suggestions from the
token measurement in [`research.md`](research.md), land them, and then tell the other research sessions so they use them
at once. A change to the research process is always a feature (the GM, 2026-09-27); this is that feature.

## What the measurement found (research.md R1)

282 page sessions since feature 250 landed held 250's cost per thing checked (median 1.02 M), but the largest context
doubled (246 K against 102-171 K), because write sessions grew long: a write session's cost follows its turn count (r =
0.92), and groups are twice R11's size. Coordination files were re-read whole about 1,400 times (about 60 M). Every turn
of a headless session carries the clone's root CLAUDE.md (about 5.2 K tokens), most of which a research session never uses.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A large research group is written in short sessions (Priority: P1)

A feature queues a group of nine questions. Every write brief declares its load in one line,
`<!-- write-load: questions=N -->`, counting each question to write or rework (an item spanning six existing sections is
six). The page-session launcher refuses a write brief declaring more than four, naming the split (`<g>a-write.md`,
`<g>b-write.md`, each with its own handoff), and refuses a write brief that declares nothing. While the session writes,
`make reserve` counts the registry keys it has reserved; the eleventh is refused, and the session writes the items it
has not reached into a continuation brief and stops, which the runner queues next.

**Independent Test**: the launcher refuses a write brief declaring 5 questions and one declaring none, and runs one
declaring 4. `make reserve` refuses a page session's 11th registry key. The runner queues a continuation brief a session
leaves.

### User Story 2 - A session reads only its own coordination lines (Priority: P1)

A check session needs its two questions' lines from the group handoff, a write session checks the claims file for its
pages, and each appends a line to its checks report. Each uses `make lines` and `make append`, and none reads the
file whole.

**Independent Test**: `make lines FILE=<f> KEY=<re>` prints only the matching lines, with their numbers and a count
of the lines it left out; `make append FILE=<f> LINE=<text>` adds one line without printing the file.

### User Story 3 - A headless session carries a slim instructions file (Priority: P1)

A page session starts without the clone's root CLAUDE.md. In its place it gets a short file holding exactly the rules
a research session acts on: house style, the research rules, the clone and commit rules, and the agent rules. The
research record's own CLAUDE.md still auto-loads.

**Independent Test**: the runner's launch flags exclude the clone's root CLAUDE.md and append the slim file. A probe
session's first turn is measured before and after.

## Edge Cases

- **What a write brief is.** A brief is a write brief if its file name contains `write`, or if it has a `## Your items`
  heading. The load line is required of every write brief; a brief generator writes it, and a hand-written brief
  carries it too.
- **Briefs that are not a new group's writing** say so in the same line: `kind=assertions` (feature 250's `brief.py`
  briefs, which footnote assertions inside existing questions rather than write questions) or `kind=handover` (a
  group handed to another feature). Only those two kinds are exempt, and the exemption is tested.
- **An item spanning several sections** counts each section it asks the session to write or rework. The declared count
  is the generator's responsibility, and a generator counts sections, not lines.
- **Keys are not known before writing**, so they are capped during the session, not at launch. The runner exports the
  session's id (`L7R_PAGE_SESSION`) and a continuation path (`L7R_CONTINUE`). `make reserve` records the session on
  each reservation and refuses a registry key past the tenth in one page session, telling it to finish the question in
  hand, write the unreached items to `$L7R_CONTINUE` as a brief of the same shape, commit and stop. When a session
  ends, the runner queues a brief found at that path next. Glossary terms are not capped.
- **A deliberate larger load**: the escape is `WRITE_CAP_OK='<reason>'` at launch or `KEY_CAP_OK='<reason>'` on
  `make reserve`, each logged with its reason, as the guard doctrine asks.
- **A queue already running** keeps the briefs it holds. The change applies to briefs launched after it lands, and
  the other sessions are told (FR-005), so they can regenerate groups they have not started.
- **The slim file drifts from CLAUDE.md**: a test pins, by named phrase, every house-style and research rule in the
  root CLAUDE.md that a research session acts on. A rule added to CLAUDE.md later fails the test until it is carried
  over or explicitly marked as not for page sessions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (suggestion 1)**: A write session MUST take at most four questions AND at most ten new registry keys.
  `scripts/page-session.sh` MUST refuse a write brief declaring more than four questions, or declaring none (only the
  `assertions` and `handover` kinds are exempt), naming the split and the escape. `make reserve` MUST refuse a page
  session's eleventh registry key with the continuation instructions, and the runner MUST queue a continuation brief a
  session leaves. The research CLAUDE.md and `docs/research-record-rules.md` MUST state both limits with the
  measurement behind them (research.md R1). 269's generator MUST declare honest counts and split its unstarted groups.
- **FR-002 (suggestion 2)**: `make lines FILE=<f> KEY=<regex>` MUST print only a coordination file's matching lines
  (numbered, with a count of the rest), and `make append FILE=<f> LINE=<text>` MUST append one line without printing
  the file. The research CLAUDE.md MUST say a session reads a claims file, a handoff or a checks report ONLY this way.
  269's brief generator MUST use them for its unstarted groups.
- **FR-003 (suggestion 3)**: A headless page session MUST start without the clone's root CLAUDE.md, carrying instead a
  slim file (`container-scripts/page-session-rules.md`) with the rules a research session acts on. A test MUST hold the
  slim file to the root CLAUDE.md's research-relevant rules, so neither drifts silently.
- **FR-004**: Each change MUST be measured. FR-003 is measured before landing: a probe session's first-turn tokens under
  the old and new flags (research.md R2). FR-001 and FR-002 can only be measured on groups that run after landing, so
  that measurement is recorded as owed in `.claude/skills/diagram/future-work/cross-cutting.md`, with the method (research.md R1's scripts in
  `measure/`) and the figures to beat.
- **FR-005**: Once this is on main, every session doing research (Diagram research [271], Diagram shrines [273],
  Diagram buildings [267], and any other with a research claim) MUST be told what changed and how to use it at once.

### Key Entities

- **Write brief**: a page session's brief for writing, with its `## Your items` list.
- **Coordination file**: the claims file, a group's handoff, a checks report.
- **Slim rules file**: `container-scripts/page-session-rules.md`.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001): tested: the launcher refuses a write brief declaring 5 questions or none, exempts only the two
  kinds, and runs one declaring 4; `make reserve` refuses a page session's 11th registry key; the runner queues a
  continuation brief.
- **SC-002** (FR-002): `make lines` and `make append` are tested, and the research CLAUDE.md and 269's briefs name them.
- **SC-003** (FR-003): the runner's flags exclude the root CLAUDE.md and append the slim file (tested), and the probe
  shows the first-turn floor fall.
- **SC-004** (FR-004): research.md R2 records the probe, and `.claude/skills/diagram/future-work/cross-cutting.md` holds the owed post-landing
  measurement with its method and baseline.
- **SC-005** (FR-005): each research session was sent the change after the landing commit reached main.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

None: nothing a map draws or states changes. This is process tooling.

## Review history

- Round 1 (spec-fidelity, 2026-09-27): CHANGES REQUIRED, three findings. (1) The ten-key half of suggestion 1 was
  dropped: now capped during the session by `make reserve`, with a continuation brief. (2) Counting item lines missed
  both costliest groups (272 S, 269 V2): the unit is now the declared question count, counted per section. (3) A brief
  without the heading escaped the cap: now refused, with only two declared kinds exempt. The future-work path was corrected.
