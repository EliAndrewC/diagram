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
- With a claim citing it but not yet checked, closing is refused, naming the claim as owed its check.
- With the claim checked (IN-STEP or DRIFTED alike), or with a "no code implements it" line, closing passes.

**Acceptance Scenarios**:
1. **Given** a research-record feature whose commits changed a question's findings, **When** its last task is ticked,
   **Then** the tick is refused until every changed question is cited by a checked claim or recorded as implemented
   nowhere.
2. **Given** a claim the check found DRIFTED, **When** the feature closes, **Then** it closes, and `make claims-report`
   lists the drift. Fixing the code is not part of the feature unless its spec asked for it.
3. **Given** a research-record feature that changed no question, **Then** nothing is owed.

### User Story 2 - One command says what is owed (Priority: P1)

`make impl-check F=<n>` lists the questions the feature changed. For each it shows the claims that cite it (their unit,
their index verdict, or "owed its check") or the recorded "no code implements it" reason, and it ends with what is still
missing.

### User Story 3 - Every research feature carries the task (Priority: P2)

A new research-record feature's `tasks.md` carries an implementation-check task from the template. Each open
research-record feature's spec says the check is owed at its close.

### Edge Cases

- **A changed question that only the map's drawing pages discuss** (`.drawing.html`): the drawing page is the
  implementation's own account, not a finding; only a question's findings page (`NNNN-<id>.html`) is owed.
- **A finding no code yet implements** (a tier not built, a building not drawn): recorded in the feature's
  `implementation-check.md` as `- NNNN: no code implements it - <why>`.
- **A claim on code the feature may not edit**: adding a `Research:` line to a docstring is a docstring edit, not a code
  change. It owes the claim's `impl-drift` check, not a gate run of the maps.
- **A feature closed before this lands** is never asked.

## Requirements

### Functional Requirements

- **FR-001 - What is owed.** A feature tagged `research record` (its `**Affects**:` line) owes, for each question whose
  findings page its commits changed or created, one of:
  - (a) at least one `Research:` claim, in the engine's code or the Mode A procedures, citing that question, every one
    of which has a row in the claims index (not owed its `impl-drift` check);
  - (b) a line in its `implementation-check.md`: `- NNNN: no code implements it - <why>`.

  A feature's commits are those whose message opens with its number (`Feature NNN` or `NNN:`), as this repository
  writes them.
- **FR-002 - Not the code.** Closing never requires that a claim be IN-STEP. A DRIFTED or NEEDS-RESEARCH verdict closes
  the feature and stands in `make claims-report`. The code is changed only where the feature's own spec asks for it.
- **FR-003 - `make impl-check F=<n>`.** It prints, per owed question, its claims with their verdicts (or "owed its
  check"), or its recorded reason, and then what is missing. It prints nothing else.
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
  no line; nor with a claim owed its check; and can with a checked claim, DRIFTED included, or with a "no code implements
  it" line.
- **SC-002** (FR-002): a DRIFTED claim closes the feature and appears in `make claims-report`.
- **SC-003** (FR-003): `make impl-check` on a real closed research feature lists its changed questions and their
  claims.
- **SC-004** (FR-005, FR-006, FR-007): the tasks template, the seven open research-record specs, CLAUDE.md and
  `research/CLAUDE.md` carry the rule.

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
  owe or escape a question by what it chooses to list.

## Review history
