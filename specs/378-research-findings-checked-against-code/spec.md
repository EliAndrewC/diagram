# Feature 378: A research feature ends with its findings checked against the code

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-10
**Status**: In progress - spec under review

**Affects**: research process, tooling

**Approved**: the GM, 2026-10-10, "update our general processes. I mean, I don't know if this is a constitution update or exactly how that works, but um, you know, just like generally make sure that in the future research tasks of this type include this as a tracked must be there."

**Input**: `request.md` (the GM, 2026-10-10)

## Why

A research-record feature finds or changes what the record says about how something was built, farmed or lived in. The
code that draws that thing may or may not do what the record now says, and today nothing asks. The project already has the
means to say it:
- **The claim.** A `Research:` claim in a docstring (or a Mode A procedure section) cites the question it rests on.
- **The check.** `impl-drift` compares the two, and the claims index records IN-STEP, DRIFTED, NEEDS-RESEARCH and so on.
- **The report.** `make claims-report` lists every finding.

A research feature simply never has to connect its new findings to that machinery.

The GM (request.md): every feature of this type has *"a task in which we look up whether or not our implementation
conforms"*. Where the code should link the new page, the link is added. Where it does not match, it is *"properly
annotated so that a `make claims-report` will show this item"*. The code itself is not fixed *"unless that was already
explicitly part of the spec kit feature"*. The open features of this type are updated, and the process makes the task *"a
tracked must be there"*.

## User Scenarios & Testing

### User Story 1 - A research feature cannot close until its findings are checked against the code (Priority: P1)

A session finishes a research-record feature that changed questions 0047 and 0060. Before it can close (its last tick, a
`Done` status, the push), the tooling asks of each changed question whether the code that decides what the question
decides cites it in a `Research:` claim, and whether that claim's check is recorded. For a question no code implements
yet, it asks for a line saying so, and why.

**Independent Test**: a fixture feature tagged `research record` whose commits changed one question.
- With no claim citing the question and no line about it, closing is refused, naming the question.
- With a claim citing it that `make claims-owed` lists (new, or re-owed by the rewrite), closing is refused, naming it.
- With the claim checked (IN-STEP or DRIFTED alike), or with a full (b) line carrying its `searched:` part, closing passes.

**Acceptance Scenarios**:
1. **Given** a research-record feature whose commits changed a question's findings, **When** its last task is ticked,
   **Then** the tick is refused until every changed question is cited by a checked claim or recorded as implemented
   nowhere.
2. **Given** a claim the check found DRIFTED, **When** the feature closes, **Then** it closes, and `make claims-report`
   lists the drift. Fixing the code is not part of the feature unless its spec asked for it.
3. **Given** a research-record feature that changed no question, **Then** nothing is owed.

### User Story 2 - One command says what is owed (Priority: P1)

`make impl-check F=<n>` lists the questions the feature changed. For each it shows the claims that cite it (their unit,
their index verdict, or "owed", for any reason `make claims-owed` gives) or the recorded "no code implements it" line, and
it ends with what is still missing.

### User Story 3 - Every research feature carries the task (Priority: P2)

A new research-record feature's `tasks.md` carries an implementation-check task from the template. Each open
research-record feature's spec says the check is owed at its close.

### Edge Cases

- **A changed question that only the map's drawing pages discuss** (`.drawing.html`): the drawing page is the
  implementation's own account, not a finding; only a question's findings page (`NNNN-<id>.html`) is owed.
- **A finding no code yet implements** (a tier not built, a building not drawn): recorded in the feature's
  `implementation-check.md` as `- NNNN: no code implements it - <why>; searched: <what>`. A thing that IS drawn is never
  this case.
- **A claim on code the feature may not edit**: adding a `Research:` line to a docstring is a docstring edit, not a code
  change. It owes the claim's `impl-drift` check, not a gate run of the maps.
- **A feature closed before this lands** is never asked.

## Requirements

### Functional Requirements

- **FR-001 - What is owed.** A feature tagged `research record` (its `**Affects**:` line) owes, for each question whose
  findings page its commits changed or created, one of:
  - (a) at least one `Research:` claim citing that question that the claims index reads (in the hamlet scope or the
    Mode A procedures, or a unit's own claim outside the scope, FR-009), none of which `make claims-owed` lists for any
    reason (new, code changed, research changed, triage). A claim that cited the
    question before the feature rewrote it is re-owed by the rewrite, so it is checked against the NEW finding;
  - (b) only for a question that NO code decides (the thing is not built: a tier, a building, a feature no generator
    draws), a line in its `implementation-check.md`: `- NNNN: no code implements it - <why>; searched: <the units and the
    grep that found none>`. Code that draws or decides the thing is case (a) whatever it does: the claim is added, and
    a mismatch is the DRIFTED verdict the report shows.

  A feature's commits are those whose message opens with its number (`Feature NNN` or `NNN:`); a merge commit is
  attributed to no feature.
- **FR-009 - A claim on code outside the hamlet scope reaches the index.** The claims index reads the modules the hamlet
  generator imports, and the code that decides the magistracy's questions (`compound_model.py`, `compound.py`) is not
  among them. A unit of any engine module that carries a `Research:` claim of its own enters the index, so its
  `impl-drift` verdict is kept and `make claims-report` shows it. The rest of its module is not obliged to carry claims:
  the every-unit coverage rule stays the hamlet scope's.
- **FR-002 - Not the code.** Closing never requires that a claim be IN-STEP. A DRIFTED or NEEDS-RESEARCH verdict closes
  the feature and stands in `make claims-report`. The code is changed only where the feature's own spec asks for it.
- **FR-003 - `make impl-check F=<n>`.** It prints, per owed question, its claims with their verdicts (or "owed", for
  any reason `make claims-owed` gives), or its recorded line, and then what is missing. A (b) line without its `searched:`
  part is missing. It prints nothing else.
- **FR-004 - Held at every close.** The closing check (`scripts/gates/close_check.py`, which the last tick, a closing
  status, `make gm-reviewed` and the push all ask) refuses a research-record feature while FR-003 reports anything
  missing. The refusal names what is missing and the command.
- **FR-005 - The task in the template.** The tasks template carries an implementation-check task for a research-record
  feature: find the code each changed question decides, cite the question in a `Research:` claim, run its `impl-drift`
  check through the existing claims commands, and record a question no code implements.
- **FR-006 - The open features.** Each open research-record feature's spec gains a line saying the implementation check
  is owed at its close (feature 378).
- **FR-007 - The guidelines.** CLAUDE.md's research section and `research/CLAUDE.md` state the rule.
- **FR-008 - Tested.** The closing check and `impl-check` have tests covering User Story 1's three cases, an unchanged
  feature, a drawing-page-only change, and a feature not tagged `research record`.

## Success Criteria

- **SC-001** (FR-001, FR-004, FR-008): a fixture research feature that changed a question cannot close with no claim and
  no line; nor with a claim `make claims-owed` lists; nor with a (b) line that does not say what was searched; and can
  with a checked claim, DRIFTED included, or with a full (b) line.
- **SC-005** (FR-009): a unit outside the hamlet scope carrying its own claim is in the claims index's reading, and its
  module's unclaimed units owe nothing.
- **SC-002** (FR-002): a DRIFTED claim closes the feature and appears in `make claims-report`.
- **SC-003** (FR-003): `make impl-check` on a real closed research feature lists its changed questions and their
  claims.
- **SC-004** (FR-005, FR-006, FR-007): the tasks template, every spec `make speckit-todo AFFECTS="research record"` lists
  open at landing, CLAUDE.md and `research/CLAUDE.md` carry the rule.

## What it does not cover

- **Fixing drifted code**: the GM excluded it unless a feature's own spec asks.
- **Features closed before this lands**: never asked.
- **A finding changed by a feature not tagged `research record`**: the GM named "features of this type". Such a change
  is not asked here.

## Decisions Recorded

- **D1 - The constitution is not amended.** The GM left it open ("I don't know if this is a constitution update"). The
  rule is enforced at every close by tooling and written into CLAUDE.md, which operationalizes Principle XII. A
  constitution clause would add no enforcement the closing check does not give.
- **D2 - "Changed" is read from the feature's commits**, by this repository's message convention, so a session cannot
  owe or escape a question by what it chooses to list. Of the 51 commits since 2026-09-25 that touch a question's page,
  40 open with `Feature NNN` or `NNN:` (observed 2026-10-10; method: `git log` over `research/questions/*.html`, by spec-fidelity
  round 1 of this review); the other 11 are merges and repository-wide moves, which no feature owns, and one direct modal tweak.
- **D3 - The index takes claimed units outside the hamlet scope** (FR-009). It is not widened to every engine module,
  which would owe a claim on every unit of 96 more modules (observed 2026-10-10; method: `engine_modules` less `scope` in
  `l7r/diagram/tools/claims.py`): only units that carry their own claim enter. Three did, with four claims (observed
  2026-10-10; method: `claimed_outside`): `compound.county_magistracy_program`, `compound_model.NOTICE_BOARD_MAX_FT` and
  `site_pages.frame`, now owed their `impl-drift` check.

## Review history
- spec-fidelity, Mode 2, round 1 (2026-10-10): CHANGES REQUIRED. Applied: (a) means not listed by `make claims-owed`
  for any reason, so an existing claim is re-checked against the new finding; (b) is only for a thing no code decides,
  with what was searched; FR-009 and D3 bring a claimed unit outside the hamlet scope into the index (the magistracy's
  code); D2 carries its measurement and leaves merges unattributed; SC-004 names the open features by command.
- spec-fidelity-verify, round 2 (2026-10-10): CHANGES REQUIRED, wording only. Applied: FR-001(a) counts only a claim
  the index reads (a module-docstring claim outside the scope does not); US1 and US2 follow FR-001 and FR-003; D2's
  attribution and D3's figures labeled.

