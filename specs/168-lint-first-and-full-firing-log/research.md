# Feature 168 - research and measurements

Everything here was measured in this tree on 2026-08-30. Where a number contradicts an earlier
document, this file is the later measurement and the earlier prose is the one to fix.

## R1 - what the lint-first reorder is actually worth (FR-001)

The GM asked for it *"on general principle ... but I don't think that it will yield an efficiency
improvement"*, and the record agrees with them, which is why this is written down rather than
claimed:

- Both static phases AUTOCORRECT (`ruff format` then `ruff check --fix`), so the common failure -
  formatting, an unused import, an import order - is fixed by the phase rather than reported by it.
  What survives to fail the phase is a syntax error, an unfixable rule, or a type error.
- **8 of 317 recorded gate runs** failed on `lint`, `format` or `typecheck` WITHOUT also failing the
  test suite. Those eight are the only runs where the order could have saved anything at all.
- The saving on one of those eight, measured by planting an unfixable syntax error and timing the
  gate to its first red: **2 s instead of ~31 s** (the reference roll is what stood in front of it).

So the reorder is right - the cheapest check runs first, and a session that broke something ruff
cannot fix hears about it in seconds - and it is worth about 29 s on 2.5% of gate runs. **Do not
later credit it with a saving it does not deliver.** That sentence is also in the Makefile at the
point of change, because a document nobody re-reads does not hold.

## R2 - the in-scope set is DERIVED, and a hand-list went stale inside one session

`spec-fidelity` round 1 rejected the first draft of `spec.md` for asserting "two guards out of
twelve record" and naming ten that do not. That census was true when this session started and false
by the time it was written: **this session's own feature 164** had added recording to five more
guards in the meantime. Round 2 then found `agent-stall`, `idle-tests` and `review-gate` missing from
the corrected list, because `review-gate.sh` does not match `*-hooks.sh` and the other two were not
thought of as guards.

The rule this produced, and the reason FR-002 states a criterion rather than a table: **a census of
your own tree, written by hand, is stale by the time it is reviewed.** The implementation derived the
set from `scripts/*-hooks.sh` plus `review-gate.sh` and asked each script whether every acting branch
records.

`idle-tests` was ruled OUT of class with the reason stated (FR-002): it is a RUNNER, not a guard on a
session's command - nothing it does costs a session a round trip, which is the cost this log exists
to measure, and it already keeps `dev/idle-log/`.

## R3 - the escape is the branch that matters, and one of them recorded nothing at all

Before this feature, `MEASURE_OK` was the only escape token whose use was recorded. That matters
because the escape RATE is the number this project has actually acted on: feature 162 retired a
refusal that was being escaped in 62% of its firings, and that decision was only possible because
`measure-hooks.sh` recorded escapes.

Audited here, one token at a time: `GATE_OK`, `PAIR_OK`, `DISCARD_OK`, `NO_BRANCH_OK`,
`REVIEW_GATE_OK`, `GUARD_EDIT_OK`, `POLL_OK` and `MEASURE_OK` now each produce an `escaped` entry.

**`SOURCE_EDIT_OK` was the one that could not simply be added.** Its escape lived INSIDE the guard's
python, which printed an empty verdict - a value the shell could not tell apart from "this edit
touches no protected block at all". So an authorized edit of the GM's own writing, the single most
consequential permit in the repository, left no trace anywhere. The python now announces the escape
(`ESCAPED`) and the shell records it and permits. The exit code and what a session may do are
unchanged; `tests/tooling/test_guard_firing_log.py` asserts both halves.

## R4 - a defect found while auditing: three guards recorded an EMPTY detail

`readme`, `source-block` and `guard-file`'s Read reminder all guard the **Edit / Write / Read** tools,
whose payload carries `file_path` and NO `command`. All three called `guard_cmd`, which read
`tool_input.command` only - so every one of their entries recorded that something fired and not what
it fired on.

Fixed in `_guardlog.sh` (Principle XIV, fix defects where you find them): `guard_cmd` falls back to
`file_path`. One body, because the two are the same question - what did the session try to do. The
new test asserts a non-empty detail on the `source-block` block, so the defect cannot come back
unnoticed.

## R5 - the fixture-leakage rule, and the count that proves it

A census polluted by its own tests answers nothing, and that had already happened once (24 entries
from a suite run). Every companion suite of a newly-recording guard now isolates `GUARD_LOG_DIR` for
the whole file. Measured after the change, running the suites of every guard that records:

    real log before: 91 entries      real log after: 91 entries

`test-agent-stall-hooks.sh` hangs its log off the `TMP` directory it already traps, rather than
adding a second trap - a file with two EXIT traps keeps only the last one, which is exactly the kind
of silent fixture defect this session recorded six of in `specs/167-portable-roll-cache/` R6.

## R6 - the path that broke the new test, again

`tests/tooling/test_guard_firing_log.py` first ran 13 red on `FileNotFoundError:
.../.claude/scripts/no-poll-hooks.sh`. From `tests/tooling/`, `parents[4]` is `.claude`; the
repository root is `parents[5]`. This is the SAME off-by-one this session made once already in
feature 167's fixtures. The fix carries the count in a comment at the point of change.

The failure mode is worth naming: the test did not silently pass while proving nothing - it went red
loudly, because it asserts on an artifact the hook must WRITE. A fixture that asserts on a file's
existence cannot be fooled by a wrong path; one that asserts on the absence of a failure can.

## R7 - a guard that sent every session at a command that could not help

Found while implementing this feature, and fixed in it (Principle XIV). It is not about the firing
log; it is about a refusal whose ADVICE was wrong, which is the same failure class feature 164 was
built to attack.

**What happened.** `/diagram` (the mirror) only ever fast-forwards from GitHub, so its HEAD is
normally main's tip - and `clone-sync-hooks.sh` compares every clean clone against it. Twice on
2026-08-30 a session let a bare `cd /diagram` leak into its next command (the exact trap
`CLAUDE.md` documents under "NAME THE TREE IN THE COMMAND", and deliberately leaves unenforced) and
COMMITTED into the mirror. From that moment:

- the mirror's HEAD was a commit GitHub main did not have, and no clone had the object;
- every clean clone was refused on the stale-base check and told to run `sync-in`;
- `sync-in` fetched GitHub, found nothing new, **reported success**, and changed nothing;
- so the session was blocked from every edit with no route forward, and the only advice it had been
  given amounted to building ON the stray commit - the one thing the mirror rule forbids.

Measured from the second occurrence: two sessions, ~20 minutes, and it took reading `origin/main`
against the mirror's HEAD by hand to work out what had happened.

**The fix.** Before believing the mirror, ask whether its HEAD is on `origin/main`. If it is not,
say so: name the stray commit, say plainly that `sync-in` will not fix it, say that main is an
integration point and no session may build on it, and give the recovery - into the OWNING session's
clone, because the mirror's working tree may be the only copy of that work. A genuinely stale clone
is unaffected; that refusal is untouched below the new branch.

**Proof it fires.** Better than a synthetic one: the real incident produced the OLD message
verbatim, twenty minutes before the fix, and that message is exactly what the new test now forbids
for this scenario. The suite builds a bare "GitHub", a mirror cloned from it and a clone of the
mirror, and asserts four things - the clean case is allowed, the stray commit blocks, the refusal
names the stray commit and says `sync-in` cannot fix it, and a genuinely stale clone against a clean
mirror still gets the ordinary `sync-in` refusal.

**Two fixture defects on the way there, both of the kind that report success while proving nothing**
(the same family as `specs/167-portable-roll-cache/` R6):

1. `git init --bare` leaves HEAD on `master`, so cloning it produced a mirror with **no
   `origin/main` at all** - the new branch could never have fired, and the test would have "passed"
   against the fallback if it had asserted only on the exit code. It asserts on the MESSAGE, so it
   went red. `symbolic-ref HEAD refs/heads/main` on the bare repo fixes it.
2. `FMAIN4` was already in use by an unrelated fixture 45 lines above, so `git clone` failed with
   *"destination path already exists"* and my scenario silently ran against **someone else's
   repository**. Renamed to `FSTRAY`/`main-stray`. Nothing about this was visible in the exit codes;
   the message assertion is what exposed it.

The rule both of those teach, and it is the one this session keeps re-learning: **assert on the
artifact the code must PRODUCE, not on the absence of a failure.** A test that asserts an exit code
passes for the wrong reason; a test that asserts the text cannot.
