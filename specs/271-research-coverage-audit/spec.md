# Feature 271 - an audit of open research questions, and the backfill

**Status:** Draft, 2026-09-27. The GM's words are `request.md`.

## What this feature is

An audit of every open research question the maps raise, and as much backfill of those questions as one long
unattended session can do. It covers the maps already made, the hand-drawn ones included, and the settlement tiers
not yet scripted (village, town, city, capital). The GM expects the existing research to be spotty. Some of it
predates the current conventions: a quoted passage behind every claim, and checks by subagents. The work is shared
with the "Diagram supplemental" session (feature 269) and the other research sessions (267, 268), and must not
duplicate theirs.

## Requirements

**FR-001 - the audit.** An inventory of the research the maps need, one row per question. Rows come from four
places:
- (a) every KIND of thing drawn on any map already made: the scripted pool, the legacy hand-drawn pool, the
  building-plan magistracies and `wip/`;
- (b) every modal whose `Entry:` names no research question, or names one that says nothing about the thing;
- (c) every research question whose findings are thin: no quoted, footnoted evidence, or written before the
  citation conventions;
- (d) the questions a map of a tier not yet scripted will need, for example how much larger the village headman's
  house is than the others, the real size of a country shrine where a country monk lives, and in towns and cities
  the inns, dojos, governor's mansions, smiths, tanneries and gate markets.

Each row carries:
- the thing and the question;
- the tier or tiers it serves;
- its status now: NONE, THIN or COVERED;
- its owner: this feature, another session's feature, or nobody yet.

The inventory is `specs/271-research-coverage-audit/inventory.md`.

**FR-002 - no duplicated work.** Before any row is researched, it is checked against
`/diagram/.clones/RESEARCH-CLAIMS.md` and the other sessions' inventories. A row another session owns is left to it.
This feature's claim is added there before the work starts. The "Diagram supplemental" session is told what this
feature takes.

**FR-003 - the backfill.** The rows this feature owns are researched and written into the record by the landed
research process: page briefs, sessions in parallel queues, reserved prefixes, check bundles, `quote-check`,
`record-format` and `source-applicability`, one re-check round, and every owed modal answered. They are worked in
this order:
1. things already drawn on a map;
2. then the next tier to be scripted (the village);
3. then towns;
4. then cities and capitals.

A claim whose only evidence cannot be read is labeled as the record's guess or estimate, with an absence note. It
is never left bare.

**FR-004 - the download list.** Every source found that a person can likely get but a bot cannot fetch is added at
the END of `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`, in the GM's format, with both links.

**FR-005 - it resumes by itself.** The work restarts with no human action, whichever window runs out, and picks up
at the first row not yet done:
- **Context:** when this session's context fills, it is compacted and continues. The inventory's state column, the
  commits made as each batch finishes, and a memory note say where the work stands.
- **Usage limit:** when the five-hour usage window stops a page session, the runner waits for the reset and resumes
  that same session (`--resume <sid>`), never moving on to the next brief. `scripts/_page_session_runner.py` does this
  as brought into this clone from 269 (diagram-buildings `4d13ad4f`, byte-identical, with its tests) before the first
  271 page session is queued. The orchestrating session carries an
  hourly scheduled wake (`CronCreate`). Each wake reads the inventory and the queues, restarts a queue that stopped,
  and continues the next rows.
- **The other sessions:** 269's hourly check counts 271's claimed work and nudges this session if it goes idle
  with rows unfinished.

## Success criteria

- **SC-001** (FR-001) - `inventory.md` lists every kind drawn on every map in the four sources, and a set of
  next-tier questions for village, town, city and capital, each row with a status and an owner.
- **SC-002** (FR-002) - no row this feature researched is claimed by another session in `RESEARCH-CLAIMS.md`.
- **SC-003** (FR-003) - every row this feature researched is COVERED with quoted, checked evidence, or labeled with
  an absence note. The record checks (`make page-check`, `make done`) are green at the push.
- **SC-004** (FR-004) - the download list grows only at its end, both links on each entry.
- **SC-005** (FR-005) - the hourly wake is scheduled while rows remain. The state column and the commit history show
  where each restart resumed, and any session a usage limit stopped was resumed, not skipped.

## Decisions Recorded

- The backfill runs as far as it can, in FR-003's order, across restarts, and not only for the hours the GM is away.
  Rows not reached stay in the inventory with their status and owner.

## Review history

- **Round 1 (2026-09-27), `spec-fidelity`: CHANGES REQUIRED**, two items. FR-001 to FR-004 carry the request: the
  audit across every map already made (the hand-drawn ones included) and the tiers not yet scripted, with the GM's
  own examples; the check against the other sessions' claims before each row; the backfill under the current
  citation and check conventions; the download list at the end of `TO-DOWNLOAD.md`. FR-003's order is a sequence,
  not a narrowing. (1) FR-005 and SC-005 drop "automatically restart". The request says "if you run out of the
  five-hour context window ... that you automatically restart and pick up the research where you left off". FR-005
  says only that "a session that restarts after its context is compacted" picks up at the first row not done. Nothing
  makes the restart happen, and the "five-hour window" is read as context compaction alone. The GM uses the same words
  for the usage-limit window (269's `request.md`: "run out of my five-hour session window, or run out of tokens within
  that window ... automatically resume when the five-hour window ends"). FR-005 should require the work to resume by
  itself, with no human action, both when the five-hour usage window ends the session and when its context runs out,
  and resume at the first row not done. SC-005 should check that the restart is armed and that a stopped session did
  resume. (2) Decisions Recorded: "The backfill is sized by the time the GM gave (about six hours unattended), not by
  the inventory" sets a stop the GM did not set. The six hours are how long the GM will be away. The request says
  "Fill in as much of it as you are able to" and asks for the work to restart itself past a window. The decision
  should say that the backfill runs as far as it can in FR-003's order, across restarts, and that rows not reached
  stay in the inventory with their status and owner.
- **Round 2 (2026-09-27), `spec-fidelity-verify`: CHANGES REQUIRED**, one item. Round 1's item (2) is RESOLVED: the
  decision now runs the backfill as far as it can, in FR-003's order, across restarts. Item (1) is PARTLY RESOLVED.
  FR-005 and SC-005 now require the work to resume with no human action through both the context and the usage
  window, and SC-005 checks the wake is armed and no stopped session was skipped. But FR-005's usage-limit bullet
  rests on a mechanism that is not there: `scripts/_page_session_runner.py` on main (and in this clone, origin/main
  fetched 2026-09-27) waits for nothing and resumes nothing. It logs `ended <sid> rc=<n>` and starts the next brief,
  so a page session the limit ends is skipped. The wait-for-reset and `--resume` logic exists only in the
  diagram-supplemental clone (269's plan D3, "diagram-buildings' 4d13ad4f"), not on main. FR-005 should say that the
  runner 271's page sessions use MUST wait for the reset and resume the same session, and that this is brought into
  this clone (or landed on main) before the first page session is queued, not that it is "already on main".
- **Round 3 (2026-09-27), `spec-fidelity-verify`: FAITHFUL.** Round 2's item is RESOLVED. FR-005's usage-limit
  bullet now states the requirement (the runner waits for the reset and resumes the same session with `--resume
  <sid>`, never moving to the next brief, brought into this clone before the first 271 page session is queued)
  rather than claiming it is already on main. The mechanism is in this clone: `scripts/_page_session_runner.py` and
  `tests/tooling/test_page_session.py` hash identical to diagram-buildings `4d13ad4f` (sha256 compared 2026-09-27),
  the run loop retries a failed session up to `RETRIES = 14` times through `wait_for()` and `resume_command()` before
  logging `ended`, and `make test-file FILE=tests/tooling/test_page_session.py` ran 7 passed on the reviewer's own
  run. Passages read: FR-005, SC-005, Decisions Recorded, the Review history, and the runner's run loop.
