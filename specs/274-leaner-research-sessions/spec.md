# Feature Specification: Leaner research sessions

**Feature Branch**: `274-leaner-research-sessions` (no branch - `main`, per CLAUDE.md)

**Created**: 2026-09-27

**Status**: FAITHFUL at round 5; implementing

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

A feature queues a group of nine questions. Before the runner starts any session it counts the questions the brief
ASSIGNS, with one shared, tested helper (`scripts/_brief_load.py`), whatever generator wrote it. The helper reads only
the brief's assignment lists (`## Your items`, `**Your questions:**`, `**Your pairs**`), never a "do not edit"
paragraph or any other section a brief names as someone else's. In those lists it counts each section named
(`page/NNN`, and a backticked `NNN` under that page), expands a range (`090-128`) against the page's actual fragments,
and counts each item id that names no section as one new question. The runner refuses a brief that
counts more than four, naming the split (`<g>a-write.md`, `<g>b-write.md`, each with its own handoff). While a write
session runs, `make reserve` counts the registry keys it reserves; the eleventh is refused, and the session writes the
items it has not reached into a continuation brief and stops, which the runner queues next.

**Independent Test**: the helper counts a 272-S-shaped brief (a range and an id list) and a V2-shaped one above four,
and a one-line item spanning six sections as six; the runner refuses them, and runs a real two-question check brief
(271's `g1-check-a.md`, with its do-not-edit list) and a real owed-modal brief of six sections declared `check`. `make
reserve` refuses a page session's 11th registry key. The runner queues a continuation brief a session leaves.

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

- **Every brief is counted, whatever its generator.** The cap is enforced by the count, not by a declaration, so the
  other features' generators keep working unchanged (the GM asked that the sessions use this at once): their check
  briefs assign two questions and pass, however many sections their do-not-edit paragraphs name; a write brief
  assigning more than four is refused, which is the cap working. The cap is the GM's cap on a WRITE session: a check
  session is not capped. The runner
  counts the briefs listed at launch (a refusal stops the launch before anything starts) and the ones a `then:` step
  prints later (a refusal STOPS the queue with a `STOPPED` line in the run log, rather than being skipped).
- **A brief that is not a group's writing may declare an exempt kind** in one line, `<!-- page-load: kind=<kind> -->`.
  There are four kinds: `check` (a check-and-apply session, which the cap does not cover), `assertions` (feature 250's
  FR-002 briefs, which footnote many assertions inside existing questions), `split` (splitting an over-cap question) and
  `handover` (a group handed to another feature). Feature 250's `brief.py` writes the line on every brief it makes: its
  2a/2b check briefs and owed-modal briefs are `check` (they are sized by bytes and may assign more than four), its
  page briefs are `assertions`, and its split briefs are `split`. A brief that assigns NOTHING countable and declares no
  kind is refused: the count never fails open.
- **Generators may split with the same helper.** 269 updates its own generator in 269, splitting its unstarted groups
  and reading coordination files by line. The other features are told what changed (FR-005).
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
  The page-session runner MUST count every brief's assigned questions with one shared, tested helper, and MUST refuse a
  brief without an exempt kind that counts more than four or none, naming the split and the escape. The helper MUST
  count only what a brief assigns.
  Only four named kinds are exempt (`check`, `assertions`, `split`, `handover`), and feature 250's `brief.py` MUST declare
  the kind on every brief it makes. `make reserve` MUST refuse a page
  session's eleventh registry key with the continuation instructions, and the runner MUST queue a continuation brief a
  session leaves. The research CLAUDE.md and `docs/research-record-rules.md` MUST state both limits and the
  load line, with the measurement behind them (research.md R1).
- **FR-002 (suggestion 2)**: `make lines FILE=<f> KEY=<regex>` MUST print only a coordination file's matching lines
  (numbered, with a count of the rest), and `make append FILE=<f> LINE=<text>` MUST append one line without printing
  the file. The research CLAUDE.md MUST say a session reads a claims file, a handoff or a checks report ONLY this way.
  269 updates its own generator in 269 to use them; that change is 269's, not this feature's.
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

- **Brief**: what a page session starts from; its questions are counted by `scripts/_brief_load.py`, and an
  exempt kind is declared in a `page-load` line.
- **Coordination file**: the claims file, a group's handoff, a checks report.
- **Slim rules file**: `container-scripts/page-session-rules.md`.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001): tested: the helper counts a one-line item spanning six sections as 6, a 272-S-shaped brief (a
  range and an id list) and a V2-shaped brief above four, and a real two-question check brief with a do-not-edit list
  (271's `g1-check-a.md`) as 2; the runner refuses a brief counting over four or counting none without a kind (at
  launch, and one a `then:` step prints, which stops the queue), and runs that check brief, a real owed-modal brief of
  six sections declared `check`, and one brief of each exempt kind; `brief.py` declares a kind on every brief it makes; `make reserve` refuses a page session's 11th registry key; the runner queues a continuation brief.
- **SC-002** (FR-002): `make lines` and `make append` are tested, and the research CLAUDE.md names them.
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
- Round 2 (spec-fidelity-verify, 2026-09-27): CHANGES REQUIRED. Finding 1 resolved; 2 and 3 partly. The declared count
  now has a tested generator behind it (`brief.py`, the one on main; 269's in 269). Every brief, whatever its name,
  carries the load line, only four named kinds are exempt, and a `then:`-planned brief is checked too.
- Round 3 (spec-fidelity-verify, 2026-09-27): CHANGES REQUIRED. `brief.py` makes no write briefs, and a required
  declaration would break the active sessions' generators until each changed. The cap now rests on a count the runner
  makes itself with one tested helper, for any generator. Declarations are only for exempt kinds, and 269's
  generator changes are 269's, stated so in FR-002, SC-002 and the Edge Cases.
- Round 4 (spec-fidelity-verify, 2026-09-27): CHANGES REQUIRED. Round 3's finding 1 was resolved, and finding 2 only partly:
  FR-002 still named 269's generator. Now fixed. The cap is again on WRITE sessions only, with `check` an exempt kind that
  `brief.py` declares; the helper counts only what a brief assigns, never its do-not-edit sections; SC-001 runs real
  briefs (271's `g1-check-a.md`, a six-section owed-modal brief).
- Round 5 (spec-fidelity-verify, 2026-09-27): FAITHFUL. All three findings resolved; FR-001 reworded as the reviewer suggested.
