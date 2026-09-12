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
parse, printing the parser's own message. A syntax error costs a full model round trip to discover at run
time and milliseconds to discover here.

**FR-005** A `git commit -m` whose message contains a double quote or a newline MUST be REWRITTEN to the
`-F -` heredoc form, per the guards-that-correct ladder - the hook can produce the compliant command
exactly, so it does rather than refusing. A single-line message with no quotes is left alone.

**FR-006** A `Co-Authored-By:` trailer that is not the attribution this project expects MUST be refused,
naming the expected line. The failure it prevents is in the record: a placeholder address reached a commit
from a shell fallback branch that was never meant to run, and history here is never rewritten.

### C. House style where the writes actually go (R3)

**FR-007** `scripts/house-style-hooks.sh` sees only `Edit` and `Write`, so every file written through a
Bash heredoc bypasses it. A Bash command whose payload carries a British spelling or a forbidden dash
OUTSIDE a quoted span MUST raise `additionalContext` naming the words - free, at exit 0, teaching before
anything is refused. It MUST NOT rewrite the command: the text sits inside a heredoc inside a script, and
a wrong rewrite costs more than the warning saves.

**FR-008** A test in `make quick` MUST scan the working tree for British spellings and forbidden dashes
outside quoted spans and fail naming file and line. The hook teaches; this is what actually holds the
line, and `quick` is where it belongs because the GM asked for it there and because it runs in seconds.

**FR-009** The tension underneath MUST be written down where the next session meets it: the root
`CLAUDE.md` says edit with `Edit`; a session run under an instruction preferring Bash loses that guard.
Both documents stay as they are - the point is that the guard no longer depends on which one won.

### D. `spec-lint` (R1)

**FR-010** `scripts/spec-lint.py` MUST check a `specs/NNN-*/` directory and fail naming the file and line:

  1. **A self-graded verdict.** The `**Status**:` line may not claim FAITHFUL or ACCEPTED unless the
     "Review history" records a round whose verdict is FAITHFUL. (The motivating case: this session wrote
     "Status: ACCEPTED" into two specs on its own authority and the push gate caught it, costing two
     rounds.)
  2. **An orphaned requirement.** Every `**FR-NNN**` is referenced by at least one success criterion,
     decision or task; every `**SC-NNN**` references at least one FR.
  3. **A withdrawn figure still standing.** A `research.md` may mark a superseded measurement
     `WITHDRAWN: <text>`; that text may then appear nowhere in the feature's own files except in the line
     that withdraws it and in the Review history that records the withdrawal.
  4. **A stale task list.** Every `FR-NNN`/`SC-NNN` a `tasks.md` cites exists in the spec.
  5. **House style**, as FR-008 does for the tree.

**FR-011** It MUST run in the gate and at push time beside `check-file-scale.py`, over every `specs/`
directory the delta touches, with a `--selftest` first as its siblings have.

### E. The re-review, narrowed (R1)

**FR-012** A re-review is dispatched against **named items**, never against a whole spec. The
`spec-fidelity` agent file MUST document a VERIFY mode: given a list of items claimed applied, confirm
each, scan only for contradictions the fixes themselves introduced, and return a verdict - not a fresh
reading of the whole document.

**FR-013** `.specify/templates/tasks-template.md` MUST carry the re-review task SHAPE, because the GM
ruled that doctrine alone will not hold it: *"it would not be enough to simply mention in our spec hit
constitution that you should not do that. We would need the checklists in the tasks to be very explicit
about the fact that that is how this works."* A review task names the round, the items and the mode.

**FR-014** The FULL reading is still owed at two moments and the template MUST say so: the FIRST review of
a spec, and the first review after an amendment that changes the design rather than the text. Narrowing a
round that should have been whole is the failure this must not cause.

## Success criteria

**SC-001** `_patch.py` applied to three edits where the second anchor misses lands the first and third and
reports the second; the file on disk carries both surviving edits.
**SC-002** A command with an unbalanced quote is refused with the parser's message; a valid command with
heredocs, backticks inside quoted strings and `$(...)` is not.
**SC-003** `git commit -m` with an inner double quote is rewritten to the heredoc form and the rewritten
command is valid `bash -n`; a plain single-line `-m` is untouched.
**SC-004** A wrong `Co-Authored-By` is refused; the expected one passes.
**SC-005** A Bash heredoc writing `centre` raises the warning naming the word; one writing it inside a
quoted span does not.
**SC-006** The `make quick` test fails on a British spelling introduced anywhere in the tree and passes on
the tree as it stands.
**SC-007** `spec-lint` fails each of its five rules on a constructed fixture and passes on every
`specs/` directory in the repository as it stands - or names the ones it does not, which is then a finding
rather than a failure of this feature.
**SC-008** Every check proven to FIRE by removing the mechanism and watching a test go red.
**SC-009** `make hooks-test`, `make quick`, `make done` and `make page-check` green.

## Decisions recorded

**D1 - a red-tree commit guard is DECLINED.** It was the sixth candidate. Mid-task commits on a red state
are legitimate here and explicitly protected ("mid-task work is sacred"), so a guard would fire on correct
work - this project's stated bar for not building one. What the record actually needs is that nothing
PUSHES on red, which `gate-stamp.py` already enforces.

**D2 - house style WARNS at the hook and FAILS at the gate.** A rewrite would have to reach inside a
heredoc inside a script to edit prose, and a wrong rewrite costs a session its command. The ladder's own
answer: teach where it is free, enforce where it is cheap.

**D3 - `bash -n` refuses rather than warns.** A command that cannot parse cannot do anything useful, so
there is no correct work to fire on, and the refusal is the cheapest possible form of the failure.

**D4 - `-m` is REWRITTEN, not refused.** The compliant command is exactly derivable from the one typed,
which is the condition the guards-that-correct ladder sets for rewriting.

## Out of scope

- The research record and the verification agents that read it. The GM: *"the research record was valuable,
  and I don't see anything there that I want to change either."* `quote-check`, `record-format`,
  `source-applicability` and `entry-drift` accounted for 27% of agent time and found five reader-facing
  falsehoods; nothing here touches them.
- Reducing the NUMBER of review rounds by lowering the bar. This feature removes rounds by making their
  cheap findings impossible, never by asking the reviewer for less.

## Review history

(to be filled by the `spec-fidelity` rounds)
