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

A feature queues a group of nine questions. The page-session launcher refuses a write brief listing more than four,
naming the split (`<g>a-write.md`, `<g>b-write.md`, each with its own handoff). The group runs as three short write
sessions, each peaking near R11's context, not one long one.

**Independent Test**: `make page-session BRIEF=<a write brief with 5 item lines>` refuses and prints the split; the
same brief with 4 runs.

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

- **A write brief whose items are not one line each.** The launcher counts item lines under the brief's `## Your items`
  heading, which is the unit every generator emits (one line per question or item). A brief with no such heading is not
  counted: feature 250's `brief.py` briefs list FR-002 assertions inside existing questions, not new questions. The rule
  is stated in questions in the docs, and generators emit one line per question.
- **An item that edits several existing sections** (e.g. one thin-section item across six sections) counts as one line
  but is several questions. The docs say to count questions, and a generator should list one line per section it asks
  a session to rework.
- **A deliberate larger brief**: the escape is `WRITE_CAP_OK='<reason>'`, and the reason is logged. That fits the
  guard doctrine for a refusal that only the session can decide.
- **A queue already running** keeps the briefs it holds. The change applies to briefs launched after it lands, and
  the other sessions are told (FR-005).
- **The slim file drifts from CLAUDE.md**: a test pins that every house-style and research rule heading in the root
  CLAUDE.md that a research session acts on is in the slim file, by named phrase. A rule added to CLAUDE.md later
  fails the test until it is carried over or explicitly marked as not for page sessions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (suggestion 1)**: A write session MUST take at most four questions. `scripts/page-session.sh` MUST refuse a
  brief whose `## Your items` section lists more than four item lines, naming the split and the escape. The research
  CLAUDE.md and `docs/research-record-rules.md` MUST state the cap with the measurement behind it (research.md R1).
- **FR-002 (suggestion 2)**: `make lines FILE=<f> KEY=<regex>` MUST print only a coordination file's matching lines
  (numbered, with a count of the rest), and `make append FILE=<f> LINE=<text>` MUST append one line without printing
  the file. The research CLAUDE.md MUST say a session reads a claims file, a handoff or a checks report ONLY this way.
  269's brief generator MUST use them for its unstarted groups.
- **FR-003 (suggestion 3)**: A headless page session MUST start without the clone's root CLAUDE.md, carrying instead a
  slim file (`container-scripts/page-session-rules.md`) with the rules a research session acts on. A test MUST hold the
  slim file to the root CLAUDE.md's research-relevant rules, so neither drifts silently.
- **FR-004**: Each change MUST be measured. FR-003 is measured before landing: a probe session's first-turn tokens under
  the old and new flags (research.md R2). FR-001 and FR-002 can only be measured on groups that run after landing, so
  that measurement is recorded as owed in `future-work/cross-cutting.md`, with the method (research.md R1's scripts in
  `measure/`) and the figures to beat.
- **FR-005**: Once this is on main, every session doing research (Diagram research [271], Diagram shrines [273],
  Diagram buildings [267], and any other with a research claim) MUST be told what changed and how to use it at once.

### Key Entities

- **Write brief**: a page session's brief for writing, with its `## Your items` list.
- **Coordination file**: the claims file, a group's handoff, a checks report.
- **Slim rules file**: `container-scripts/page-session-rules.md`.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001): the launcher refuses a 5-item write brief and runs a 4-item one (tested).
- **SC-002** (FR-002): `make lines` and `make append` are tested, and the research CLAUDE.md and 269's briefs name them.
- **SC-003** (FR-003): the runner's flags exclude the root CLAUDE.md and append the slim file (tested), and the probe
  shows the first-turn floor fall.
- **SC-004** (FR-004): research.md R2 records the probe, and `future-work/cross-cutting.md` holds the owed post-landing
  measurement with its method and baseline.
- **SC-005** (FR-005): each research session was sent the change after the landing commit reached main.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

None: nothing a map draws or states changes. This is process tooling.

## Review history

- (none yet)
