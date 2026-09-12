# Feature 236 - catch mistakes early and cheaply

**Created**: 2026-09-12
**Status**: Draft
**Input**: the GM's request, verbatim, in `request.md`

## Summary

A 201-minute session delivered two features and spent **91 of those minutes on 20 `spec-fidelity`
rounds** (`research.md` R1). At least eight of the twenty returned findings a mechanical check could have
caught for nothing. Alongside them the session lost 15-20 minutes to its own rework and called that an
embarrassment needing no tooling. The GM declined that reading:

> Mistakes are inevitable, and good systems catch mistakes early and cheaply. And if a system is set up
> such that mistakes are very expensive, particularly mistakes which it is easy to make and which are made
> frequently, then the system design is poor. ... anytime someone says, "oops, that's embarrassing. I'll
> just do better in the future", then a good engineer says, hold on. This might be a system designs
> problem masquerading as a personal failing.

Classified that way (`research.md` R2), five of six failures are mechanically catchable, and one of them
is a guard hole this project has already found and closed once for a different guard (R3). This feature
closes them and cuts the review rounds that the rest of the cost sits in.

**The research record is explicitly out of scope** - the GM: *"I agree that the research record was
valuable, and I don't see anything there that I want to change either."*

## Functional requirements

### A. The edit helper (R2 item 1)

**FR-001** A shared `scripts/_patch.py` MUST apply a list of (anchor, replacement) edits to a file so that
**each edit is its own write**: an anchor that matches zero or more than one time is REPORTED and SKIPPED,
and every other edit in the batch still lands. It MUST print one line per edit saying which.

**FR-002** Anchors MUST match whitespace-insensitively (a run of whitespace in the anchor matches any run
in the file), because the single commonest miss in the record is an anchor that spans a line wrap.

**FR-003** It MUST be the documented way to script a multi-file or multi-edit change, named in the root
`CLAUDE.md` beside the existing "Edit files with `Edit`" rule, which it does not replace: `Edit` stays the
default and this is for the sweep that genuinely must be scripted.

### B. Shell syntax, before the round trip (R2 items 2 and 3)

**FR-004** A `PreToolUse` hook MUST run `bash -n` over every Bash command and REFUSE one that fails to
parse, printing the parser's own message. It MUST check the same text the Bash tool executes.

**FR-005** A `git commit -m` whose message contains a double quote or a newline MUST be handled in one of
two ways, never a third: **REWRITTEN** to the `-F -` heredoc form when the matcher can rebuild the message
exactly, and **REFUSED** with the compliant form named when it cannot. The ladder's own proviso governs -
*"Never guess: a shape the matcher cannot rebuild exactly keeps the refusal"* - and the motivating case in
`research.md` R2 row 3 is on the refusal side, because a command whose quoting has ALREADY broken does not
carry the message its author meant. A single-line message with no quotes is left alone.

**FR-006** A `Co-Authored-By:` trailer whose address is not `noreply@anthropic.com` MUST be refused,
naming the expected form. It MUST match by SHAPE and not pin the display name, which carries the model
and changes: a guard pinning today's literal would refuse correct commits the day the attribution moves,
which is this repository's own recorded lesson that a stale literal agrees with itself. The failure it
prevents is in the record - a placeholder address reached a commit from a shell fallback branch, and
history here is never rewritten.

### C. House style where the writes actually go (R3, R4)

**FR-007** `scripts/house-style-hooks.sh` sees only `Edit` and `Write`, so every file written through a
Bash heredoc bypasses it. A Bash command whose payload carries a British spelling or a forbidden dash MUST
raise `additionalContext` naming the words - free, at exit 0, teaching before anything is refused. It MUST
NOT rewrite the command.

**FR-007a** "Outside a quoted span" means the HOUSE-STYLE sense - a prose quotation (`「」`, curly or
straight quotes, `<q>`, `<blockquote>`) or a backtick span naming a token - and explicitly NOT shell
quoting: under a `<<'PY'` heredoc the entire payload is shell-quoted, so reading it that way would make
the exemption swallow the rule. Search-command segments MUST be dropped as `_hookmatch.py` already drops
them, or `git grep -n "centre"` warns on correct work.

**FR-008** A check in `make quick` MUST scan the **DELTA** - the lines this working tree adds or changes
against the merge base - and fail naming file and line. NOT the whole tree: `research.md` R4 measures 146
pre-existing hits, so a tree-wide check would fail on landing and commit this feature to a sweep the GM
did not ask for. The delta is also the only scope that would have caught the failures that motivate it,
every one of which was new text.

**FR-008a** It MUST carry the full exemption set of the hook it mirrors - the GM's writing, `SOURCE`
blocks, verbatim `specs/*/request.md`, backtick spans, prose quotations, and the files that must quote the
rule - and MUST exclude `.clones/`, which a repo-root scan double-collects.

**FR-008b** It MUST be a `make quick` PHASE rather than a pytest test. `make quick` is testmon-selected, so
a tree- or delta-scanning test whose own code never changes would sit unexecuted through exactly the prose
edits it exists to catch. A phase runs every time and costs milliseconds.

**FR-009** The tension underneath MUST be recorded in the root `CLAUDE.md`: it says edit with `Edit`, while
a session run under an instruction preferring Bash loses that guard. Neither document changes - the point
is that the guard no longer depends on which one won.

### D. `spec-lint` (R1)

**FR-010** `scripts/spec-lint.py` MUST check a `specs/NNN-*/` directory and fail naming file and line:

  1. **A self-graded verdict.** The `**Status**:` line may not claim FAITHFUL or ACCEPTED unless the
     "Review history" records a round whose verdict is FAITHFUL **or** records the GM accepting the spec
     in their own words - the GM outranks `spec-fidelity` and a spec they accept has no round to point at.
     (Motivating case: this session wrote "Status: ACCEPTED" into two specs on its own authority and the
     push gate caught it, costing two rounds.)
  2. **An orphaned requirement.** Every `**FR-NNN**` is referenced by at least one success criterion,
     decision or task, and every `**SC-NNN**` names at least one FR id.
  3. **A stale task list.** Every `FR-NNN`/`SC-NNN` a `tasks.md` cites exists in the spec.
  4. **House style**, as FR-008 does for the delta, over the spec's own files.

**FR-010a** Rules 1, 2 and 3 apply ONLY to a spec that has a `tasks.md` - that is, one past the claim
stage. A freshly claimed spec is a Draft with no tasks, no Review history and requirements not yet cited,
and the root `CLAUDE.md` explicitly protects two pushes that carry exactly that: the number claim
(`specs/` directory alone) and the ordinary mid-feature milestone push. A lint that refused those would
fire on correct work at the first opportunity.

**FR-010b** This spec MUST itself pass rule 2 - every SC below names the FR it verifies. A rule whose
author's own document fails it is either wrong or the document is, and the spec must not leave that open.

**FR-011** `spec-lint` MUST run in the gate and at push time beside `check-file-scale.py`, over every
`specs/` directory the delta touches, with a `--selftest` first as its siblings have.

### E. The re-review, narrowed (R1)

**FR-012** A re-review is dispatched against **named items**, never against a whole spec. The
`spec-fidelity` agent file MUST document a VERIFY mode: given a list of items claimed applied, confirm
each, scan for contradictions the fixes themselves introduced, and return a verdict.

**FR-013** `.specify/templates/tasks-template.md` MUST carry the re-review task SHAPE, because the GM ruled
that doctrine alone will not hold it: *"it would not be enough to simply mention in our spec hit
constitution that you should not do that. We would need the checklists in the tasks to be very explicit
about the fact that that is how this works."* A review task names the round, the items and the mode.

**FR-014** A round may be narrowed ONLY when every change since the last round is confined to items that
round named. Anything else is a FULL reading. That covers the three moments the record shows biting:
  1. the FIRST review of a spec;
  2. ANY amendment after acceptance - the root `CLAUDE.md` reset doctrine's own trigger, not a
     design-versus-text distinction, because that distinction would be graded by the party who wants the
     narrow round;
  3. a round whose preceding revision ADDED or rewrote a requirement, since the next reviewer is otherwise
     handed text nobody has read whole - the class that produced feature 234's amendment round 2, whose
     severe finding was a docstring still describing a withdrawn design.

## Success criteria

**SC-001** (FR-001, FR-002) `_patch.py` over three edits whose second anchor misses lands the first and
third, reports the second, and the file carries both surviving edits; an anchor spanning a line wrap
matches.
**SC-002** (FR-004) A command with an unbalanced quote is refused with the parser's message; a valid
command carrying heredocs, backticks inside quoted strings and `$(...)` is not.
**SC-003** (FR-005) A `git commit -m` whose message the matcher can rebuild is rewritten to the heredoc
form and the result passes `bash -n`; one whose quoting has already broken is REFUSED rather than guessed
at; a plain single-line `-m` is untouched.
**SC-004** (FR-006) A trailer addressed anywhere but `noreply@anthropic.com` is refused; today's line
passes, and so does one carrying a different display name.
**SC-005** (FR-007, FR-007a) A Bash heredoc writing `centre` warns naming the word; the same word inside a
prose quotation or a backtick span does not; `git grep -n "centre"` does not.
**SC-006** (FR-008, FR-008a, FR-008b) The phase fails on a British spelling added by the working delta and
passes on this delta; it does not fail on the 146 pre-existing hits R4 ledgers; it runs on a delta that
changes no Python.
**SC-007** (FR-010, FR-010a, FR-011) `spec-lint` fails each of its four rules on a constructed fixture;
passes on a freshly claimed spec with no `tasks.md`; and runs over every `specs/` directory the delta
touches. Its output over ALL existing `specs/` directories is recorded and every pre-existing failure is
ledgered BY NAME in `research.md` - not waved through as "a finding rather than a failure".
**SC-008** (FR-010b) This spec passes rule 2 against itself.
**SC-009** (FR-012, FR-013) The `spec-fidelity` agent file documents VERIFY mode and the tasks template
carries the review-task shape naming round, items and mode.
**SC-010** (FR-014) The template states the three moments a round may not be narrowed, and a task
generated from it for an amendment after acceptance asks for a FULL reading.
**SC-011** (FR-003, FR-009) The root `CLAUDE.md` names `_patch.py` beside the `Edit` rule and records the
Edit-versus-Bash tension.
**SC-012** (all) Every check proven to FIRE by removing the mechanism and watching a test go red.
**SC-013** `make hooks-test`, `make quick`, `make done` and `make page-check` green.

## Decisions recorded

**D1 - a red-tree commit guard is DECLINED.** It was the SEVENTH candidate, offered alongside the six and
recommended for skipping by the session, so the GM's "all 6" does not cover it. Mid-task commits on a red
state are legitimate here and explicitly protected ("mid-task work is sacred"), so a guard would fire on
correct work - this project's stated bar for not building one. What the record needs is that nothing
PUSHES on red, which `gate-stamp.py` already enforces.

**D2 - house style WARNS at the hook and FAILS in `make quick`, over the DELTA.** A rewrite would have to
reach inside a heredoc inside a script to edit prose, and a wrong rewrite costs a session its command. The
delta rather than the tree because the tree carries 146 pre-existing hits (R4), which are LEDGERED under
Principle XIII rather than swept under this feature.

**D3 - `bash -n` refuses rather than warns.** A command that cannot parse cannot do correct work, so there
is nothing correct to fire on, and the refusal is the cheapest form of the failure.

**D4 - `-m` is REWRITTEN where the message is exactly rebuildable and REFUSED where it is not.** An earlier
draft of this decision claimed the compliant command is always "exactly derivable", which is false for its
own motivating case: `git commit -m "...said \"the pond's own center\"..."` is valid bash whose quoting
already broke, so what the author MEANT is not recoverable. Guessing there would cost a session its commit
message, which is worse than the refusal.

**D5 - the `WITHDRAWN:` rule is DROPPED from this feature**, with its measurement, because it would not
have caught its own motivating case (all five surviving places were outside `specs/`) and it fires on
correct work (feature 234's spec narrates the withdrawn figures legitimately in six places). Reaching the
real surface means scanning the whole tree, which is a broadening beyond the `spec-lint` the GM approved.
`research.md` R5 carries the finding for the next session.

## Out of scope

- The research record and the verification agents that read it. The GM: *"the research record was valuable,
  and I don't see anything there that I want to change either."* `quote-check`, `record-format`,
  `source-applicability` and `entry-drift` were 27% of agent time and found five reader-facing falsehoods;
  nothing here touches them.
- The 146 pre-existing British spellings, ledgered in `research.md` R4. A pre-existing failure stays
  ledgered and is not fixed under someone else's feature (Principle XIII); a sweep of them wants the GM.
- Reducing the NUMBER of review rounds by lowering the bar. This feature removes rounds by making their
  cheap findings impossible, never by asking the reviewer for less.

## Review history

**Round 1** (`spec-fidelity`, 2026-09-12): CHANGES REQUIRED, twelve items, all taken. The consequential
ones: the six the GM approved existed only in a transcript and are now in `request.md`; FR-008 would have
failed on landing against 146 measured pre-existing hits, so it is scoped to the DELTA and the rest is
ledgered; the `WITHDRAWN:` rule would not have caught its own motivating case and fired on correct work, so
it is dropped with its measurement (D5); FR-010's orphan rule would have refused THIS spec and the
number-claim push the root `CLAUDE.md` protects, so it applies only past the claim stage and this spec now
passes it; D4's "exactly derivable" was false for its own case, so FR-005 refuses where it cannot rebuild;
FR-006 pinned a literal that changes and now matches by shape; FR-014 graded its own trigger and now uses
the reset doctrine's; SC-007's self-absolving hedge is replaced by a named ledger; and "outside a quoted
span" was undefined in a way that would have let shell quoting swallow the rule.
