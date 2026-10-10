# Feature 376: The claims sign-up sheet through tooling, and looking at what we have before searching the web

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-10 (filed); repurposed 2026-10-10
**Status**: In progress - spec FAITHFUL (round 2), plan under review

**Affects**: research process, tooling

**Approved**: the GM, 2026-10-10, "So yeah, go ahead and do both of those as part of 376."

**Input**: `request.md` (the GM, 2026-10-10)

## Why

This feature was filed to lower a research group's fixed cost. Its own measurement (`research.md` R1) found the
premise backward: after feature 274 the fixed part per group fell and the cost per thing checked rose, in more reading
and more web searching per item. Of its two levers the GM kept the small, cheap one, the claims lookup. The GM also
asked for the thing they first took the lookup to be: making sure a session looks at what the project already has before
searching the web.

The GM's principle for the first part (request.md): *"any time we have a process that requires editing a potentially
large file, then we should use tooling to edit the file ... the same sensibility that is why we have a make target for
doing a task tick"*.

**The claims file today.** Parallel research sessions share `/diagram/.clones/RESEARCH-CLAIMS.md`, a sign-up sheet: a
session adds a line saying which questions it is working on, and checks that no other session holds them. It has grown
to 1,138 lines (170 KB) (observed 2026-10-10; method: `wc` on the file). A session checks it with `make lines
FILE=<claims> KEY=<page name>`, which returns every line naming the page: a median of 4,147 characters, up to 20,553;
across the research groups after 274 these reads carried about 16 M tokens (observed 2026-10-10; method: every
`make lines` call on the claims file in those groups' transcripts, its result's length and the tokens it carried, as
347's `measure/coord.py` counts them). Status changes are appended as new lines, so the sheet only grows.

## User Scenarios & Testing

### User Story 1 - A session claims its questions with one command (Priority: P1)

A session about to work on questions 0060 and 0246 runs one command. It answers whether another session holds either
one right now, and, if none does, records the claim. Later the session marks them done with the same command. It never
opens, reads or appends to the sheet by hand.

**Independent Test**: in a scratch sheet, two sessions claim overlapping questions: the second is refused, naming only
the overlapping claim. The first marks its questions done, and the second's claim then succeeds.

**Acceptance Scenarios**:
1. **Given** no live claim on 0060, **When** a session claims `0060 0246`, **Then** its line is recorded and the command
   prints one line.
2. **Given** another session's live claim on 0246, **When** a session claims `0060 0246`, **Then** nothing is recorded
   and the command prints only that claim.
3. **Given** a session's claim on 0060, **When** it marks 0060 done, **Then** a query on 0060 shows no live claim.
4. **Given** a query on questions nobody holds, **Then** it prints one line saying so, whatever the sheet's size.

### User Story 2 - The sheet cannot be edited by hand (Priority: P1)

A session that tries to write the sheet with `Edit`, `Write`, a shell redirect or `make append` is refused, and the
refusal names the command to use. A read by the old routes (`cat`, `Read`, `make lines`) is refused the same way.

### User Story 3 - The project knows whether sessions look locally before searching (Priority: P1)

The session measures, over every session transcript since the source archive landed (feature 309, 2026-10-02), how
often a session searched the web without first asking the record, the archive or the GM's canon, and how often a web
fetch or search retrieved something the archive or the record already held. Each gap it finds gets a tooling fix,
chosen in the plan from that measurement.

### Edge Cases

- **The sheet's old lines** are free text naming pages (`homesteads 060`) or numbers (`0060`). A query matches a
  question by its number and by the page and number the old record used, and an old line counts as live unless a later
  line for the same owner and item says it is done.
- **Two sessions claim at the same moment**: the claim is made under a lock, so one of them is refused.
- **A session ends without marking its claim done**: its claim stays live. The refusal names the holder, its feature and
  the date, so a session can see a stale claim, and the command can release one claim by name with a reason.
- **The measurement finds nothing to fix**: the fix list is empty, and the finding is recorded.

## Requirements

### Functional Requirements

- **FR-001 - Claim, query and release through one tool.**
  - `make research-claim Q="<questions>" FEATURE=<n> [STATUS=<text>]` records a claim. It refuses, under a lock,
    when another owner holds a live claim on any of the questions, and prints only those claims.
  - `make research-claims Q="<questions>"` prints only the live claims touching them.
  - `STATUS=done` releases the claim.
  - The owner is the session's clone name, so a session cannot claim as another.
  - Output is a few lines whatever the sheet's size.
- **FR-002 - The sheet is written and read only through FR-001.** A session's `Edit`, `Write`, shell write or
  `make append`, and the old read routes (`cat`, `Read`, `make lines`) on the claims file, are refused. The refusal names the
  FR-001 command.
- **FR-003 - The briefs and rules use it.** `scripts/container/page-session-rules.md`, the brief template and the docs
  say `make research-claim` / `research-claims` where they said `make lines` / `make append` on the claims file.
- **FR-004 - The principle in the guidelines.** CLAUDE.md states the GM's rule as the GM gave it: any time a process
  requires editing a potentially large file, it uses tooling (here, a make target) to edit the file, never opening
  and editing it by hand - as `make tick` does for `tasks.md`.
- **FR-005 - Measure local-first searching.** Over every session transcript since 2026-10-02 that searched or fetched
  from the web, the session measures:
  - how often the first web call came with no prior look at the record, the archive (`make archive-find`) or the canon
    (`make canon`);
  - how many fetched URLs the archive already held;
  - how many searches were for a subject the record already answers, judged by the search terms against the record's
    question headings.

  It is recorded in `research.md` R2 with its method.
- **FR-006 - Fix what FR-005 finds.** Each gap R2 measures gets a tooling fix in this feature, chosen in the plan, with
  a test that fails on the gap. The one exception is constitution XIV's: a gap whose fix would be a complete overhaul or
  a giant architectural change (not merely long work) is deferred, and `research.md` R2 records its measurement, its
  mechanism and an implementation sketch; the final message puts it to the GM. It is not filed (feature 377).
- **FR-007 - Tested.** FR-001 and FR-002 have tests covering the scenarios above (a refused overlap, a release, a lock,
  an old free-text line matched, each refused write and read).

## Success Criteria

- **SC-001** (FR-001, FR-007): in a test sheet of the real sheet's size, a claim and a query print at most five lines;
  an overlapping claim is refused naming only the holder; a released claim no longer refuses.
- **SC-002** (FR-002, FR-003, FR-007): every hand route to the sheet named in FR-002 is refused with the FR-001 command;
  `page-session-rules.md` no longer tells a session to use `make lines` or `make append` on it.
- **SC-003** (FR-004): CLAUDE.md states the GM's rule for a potentially large file, in the GM's terms.
- **SC-004** (FR-005, FR-006): `research.md` R2 holds the three measurements, and each gap it names has a fix with a test,
  or - for an overhaul only - its measurement, mechanism and implementation sketch in R2, put to the GM.

## What it does not cover

- **One check pass over several groups** (the other lever R1 priced, about 4%): the GM judged it not worth its
  complexity.
- **Other large files sessions edit by hand**: FR-004 states the rule. Converting another file is proposed to the GM,
  as 377 requires, not built here.

## Decisions Recorded

- **D1 - The claims file stays where it is**, outside every repository, at `/diagram/.clones/RESEARCH-CLAIMS.md`,
  because every clone's sessions share it. The tool reads and appends it under a lock.

## Review history
- spec-fidelity, Mode 2, round 1 (2026-10-10): CHANGES REQUIRED. Applied: FR-006 and SC-004 defer only constitution
  XIV's overhaul, with its measurement, mechanism and sketch in R2; FR-004 and SC-003 state the GM's rule in the GM's
  terms ("potentially large", any file); the Why section's figures are labeled. Ruled faithful: FR-002's read refusal,
  the other large files proposed rather than converted, and the approval line.

- spec-fidelity-verify, Mode 3, round 2 (2026-10-10): **FAITHFUL**. Every round 1 item resolved; nothing to change.
