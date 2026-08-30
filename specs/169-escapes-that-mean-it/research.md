# Feature 169 - research and measurements

Everything here was measured in this tree on 2026-08-30.

## R0 - what "these fixes" refers to

The GM asked what other tooling improvements the session had become aware of. The answer named five
findings, each produced by driving the real guard with a real payload; the GM replied *"Yes please
make these fixes as their own feature"*. The five are listed in [`request.md`](request.md), which is
the authority. Two of them (the `sync-in` false success and the mirror-`cd` guard) had been offered
for the GM's own decision rather than recommended, and the reply answers the message as a whole -
adjudicated by `spec-fidelity`, which said it would have flagged a spec that built only three.

## R1 - the escape branches were the last substring tests in the repository

Every BLOCKING decision here has been anchored since 2026-08-25 - `_hookmatch.py`'s own docstrings
carry the six pieces of correct work a bare substring test refused in one day - but every guard still
decided its own ESCAPE with `case "$CMD" in *TOKEN*)`. Measured:

| driven with | guard | before | after |
|---|---|---|---|
| `grep -rn MEASURE_OK scripts/` | `measure` | one `escaped` entry, state cleared | nothing |
| `grep -rn GATE_OK ...` | `gate` | `escaped`, state file removed | nothing |
| a grep for the token | `no-poll`, `discard`, `no-branch` | one `escaped` entry each | nothing |
| a real escape (`# TOKEN: reason`) | all five | escapes | escapes, unchanged |

**All six recorded `measure escaped` entries in the live log were mentions**: four heredoc bodies and
commit messages, and two word lists from an audit that was itself enumerating the tokens. `make audit`
reported `measure escape rate 100%` for a guard nobody had escaped - in the statistic this project
acts on (feature 162 retired a refusal escaped in 62% of its firings).

**The half that makes it a correctness fix, not a reporting one**: `measure` clears its
repeat-measurement counter on that branch and `gate` removes its state file. So a session that
grepped for `MEASURE_OK` - to find out how the escape works - thereby switched the guard off for its
next expensive command.

## R2 - a check that fed raw text to a JSON entry point, and "passed"

The first run of the ten-case matcher check reported every mention correctly rejected. It was
worthless: the CLI reads its command from a JSON payload, the check piped raw text, so `payload` was
empty and EVERY case returned nothing - including the five that had to return `yes`. The mentions
"passed" because the answer was empty for the wrong reason.

It was caught only because the check asserted BOTH directions. Had it asserted only that mentions are
rejected, it would have passed forever against a function that never ran. Same lesson as feature
168's R8, one layer up: assert on the artifact the code must PRODUCE.

## R3 - `HOST_GIT_OK`, and why blanking quotes was not enough

**Found by the round-2 spec review, not by the session** - it noticed that its own audit command
would have disarmed the guard it was auditing. `repo-safety-hooks.sh` matched its escape against the
RAW command while the sanitized copy it builds fourteen lines earlier - heredocs and quoted strings
blanked, with a comment saying this is *"the mention-versus-invocation rule this repo has now learned
six times over"* - sat unused. That escape guards git writes against `/host-l7r-repo`, the GM's own
repository.

The first fix - point it at the sanitized copy - was measured and **did not work**:

    grep -rn HOST_GIT_OK scripts/ && git -C /host-l7r-repo commit -am x     -> still permitted

because the token is a BARE word there, not a quoted one. Blanking quotes only catches the token
inside a string. The working fix routes the decision through `_hookmatch.py escape`, which also drops
search-command segments - which is the argument for having the rule in one place rather than written
a twelfth time. Verified in five directions afterwards, including that the file's two no-escape rules
(force-push, history-rewrite) are untouched.

## R4 - the derived checks found two more things immediately

Replacing the two hand-lists with checks derived over the guard tree paid within a minute:

1. **`no-poll`'s escape was silently broken by my own edit** - the branch sits at line 60 and uses
   `$NP_HERE`, but I wrote `$HERE`, which is not defined until line 72. The path was empty, the
   matcher never ran, and the escape stopped working entirely. A test that only checked mentions
   would have called that a success.
2. **Three suites isolate the log through the shared runner** (`test_hooks_cases.py`) rather than for
   themselves, so the naive check reported them as polluting. The check follows one level of
   delegation and holds the runner to the same rule.

The hand-list this replaced is the same failure feature 168's spec review caught twice: a census of
your own tree, written by hand, is stale by the time it is read.

## R5 - `--ff-only` does not catch a mirror that is merely AHEAD

`CLAUDE.md` has always said a hand commit in `/diagram` *"stops the next sync-in (mirror cannot
fast-forward)"*. It does not. `git pull --ff-only` fails on DIVERGENCE; a mirror carrying one stray
commit on top of GitHub main's tip has nothing to pull, satisfies `--ff-only`, and prints
`Already up to date`. So on 2026-08-30, twice, every subsequent `sync-in` reported
`clone synced with GitHub main` while the mirror held a commit GitHub did not have and every clean
clone in the container was refused as stale.

The added check is containment - the mirror's HEAD must be an ancestor of its `origin/main` - and it
reports rather than repairs, because the mirror's working tree may be the only copy of that work and
whose work it is cannot be known from another session.

## R6 - what FR-006 is, and what it is NOT

Recorded because the first draft of this spec got it wrong and the GM was shown that wrong claim.

`CLAUDE.md`'s "NAME THE TREE IN THE COMMAND" rule (2026-08-17) is about a **read-only diagnostic that
reports the wrong tree** - *"worse than an error because it looks like an answer"* - and the GM priced
a hook for it and declined, because every candidate fired on nearly every correct command. Its stated
reopening condition names that read-only case.

`main-tree-hooks.sh` **does not meet that condition**: it excludes read-only commands by construction
and cannot see a section header, which is where the mislabeling lives. **The 2026-08-17 rule remains
deliberately unenforced.**

What it does guard is the WRITE half, which nothing catches. Writing in main is supposedly caught
three ways - `webapp/mainguard.py`, the Makefile's `guard`, `settlement._assert_not_main_tree` - and
none of the three sees a `git commit`; all are in-process or `make`-time. Both incidents of
2026-08-30 went straight through. It is also neither declined candidate: candidate (a) demanded
`git -C` on every git call, candidate (b) needed one command to name both a non-clone path and
`.clones/`. This needs no second path and demands `git -C` of nothing.

**The GM's approval of this item rested on the false claim**, so the correction is owed to them in
the close-out report, plainly enough that they can withdraw it. That obligation is SC-007 - the only
requirement in this feature that no test can tick.

## R7 - the guard's own risk, and the half of the suite that manages it

This guard's danger is not missing a write; it is refusing correct work. A session reads main
constantly, and every clone lives UNDER the mirror root, so a pattern one character greedier would
refuse all editing everywhere. Six of the suite's seventeen cases exist for that: a read after a `cd`,
`git status`, a `git -C` read, a commit in a clone under the mirror, the documented subshell form,
and an ordinary commit with no `cd`. Two more prove a MENTION of the pattern - in a commit message,
in a heredoc - is not an invocation, which is this feature's own rule applied to itself.

Proved to fire by neutering the block in a copy and watching the case that must fail pass.

## R8 - the same slip, twice, and what it says about testing an escape

An escape branch converted to the shared matcher reads its stdin from a variable, and TWICE in this
feature I named the wrong one:

- `no-poll-hooks.sh` uses `$NP_HERE` for its own directory (`$HERE` is not defined until twelve lines
  later). The path was empty, the matcher never ran, and **the escape stopped working entirely**.
- `pair-hooks.sh` names its stdin `payload`, not `INPUT`. The waiver branch never fired, and four of
  its own cases went red at the gate.

Both were caught, and neither by inspection. The first was caught because the new suite asserts that a
REAL escape still escapes, not merely that a mention does not; a check written the obvious way -
"prove the mention no longer escapes" - passes against a branch that has been disabled altogether,
which is the worse failure of the two, since the escape is what lets a guard be repaired through the
channel it guards. The second was caught by `hooks-test`.

After the second, the class was closed rather than the instance: every converted guard was audited for
whether its escape line names the same variable the file assigns from `cat`. All six agree.

**The rule this earns**: an escape is tested in BOTH directions, always. `tests/tooling/test_guard_firing_log.py`
and each guard's own suite now do that for every token.

## R9 - the live census still shows the defect, and that is the correct reading

Checked after the gate went green: 63 entries landed in the live log during this feature's own
implementation window, including 8 `gate gate-ok` and 4 `measure escaped` - for a session that never
once escaped either guard. They are mentions: commit messages and spec text naming the tokens.

That is not a failure of the fix. `.claude/settings.json` points every hook at **main's copy**
(`/diagram/scripts/*.sh`), so the live guards are still the substring versions while this work sits in
a clone. The census will stop recording phantom escapes for every session in the container at the
moment this lands, and not before - which is also the cleanest available confirmation that the defect
was real and is being fixed at the right layer.

## R10 - the census was written from memory three times; now it is derived

Three drafts of FR-001 each claimed a complete list of "every guard's escape token". Each was short
by one, and each was caught by the reviewer rather than by the author:

| round | missed | what it guards |
|---|---|---|
| 1 -> 2 | `HOST_GIT_OK` | git writes against `/host-l7r-repo`, the GM's own repository |
| 2 -> 3 | `GATE_STAMP_OK` | the push-time rule that nothing lands which a green gate did not see |

Round 3 declined to review a fourth draft and escalated, with the diagnosis that matters more than
either token: the census *"is being written from memory of the guards rather than derived from the
tree"*, so a fourth attempt would miss the next one too.

**The remedy is mechanical, and it is the same one this feature already applied twice** (FR-003's
suite-isolation check and FR-004's slug check both replaced hand-lists that had each missed a guard
within a day). `tests/tooling/test_guard_firing_log.py` now enumerates every `*_OK` token in
`scripts/` and the skill Makefile and fails on any that is not classified as `command`, `content`,
`environment`, `make-variable` or `not-an-escape`. A second check fails the build if any guard decides
a COMMAND escape by substring again - the exact shape every guard carried before this feature, and the
one a new guard would most naturally reintroduce.

Both were proved to fire: removing `GATE_STAMP_OK` from the classification turns the census check red
naming that token, and the substring check flagged two real lines on its first run against live code
(one a true positive - the declared prose exclusion - and one a FALSE positive, a `sed` that extracts
the bypass reason and decides nothing, which is the mention-versus-invocation mistake being made by
the very check that exists to prevent it; the check now requires the line to ACT).

The four unconverted tokens are unconverted by CONSTRUCTION, not by exemption: `SOURCE_EDIT_OK` is a
marker inside edit content, `REVIEW_GATE_OK` and `GATE_STAMP_OK` are environment variables that a
mention cannot set, and `REF_OK` is a make override already anchored positionally. The single real
exclusion is `pair`'s agent-prompt branch, adjudicated legitimate by the round-3 review.

## R11 - a flaky gate test, fixed at its cause (Principle XIV)

`make hooks-test` went red on `test-idle-tests-hooks.sh` case 5, "the suspend was counted", while the
same suite passed 30/30 standalone. Measured before touching anything: my delta contains no
idle-tests file, and standalone the suite passed - so not a regression. Left alone it would have cost
a gate cycle every second or third run, for this feature and every future one.

**The mechanism.** `wait_awake` takes a clock baseline (`last=$(now)`) and only then sleeps on its
first tick; a suspend is detected as drift between two readings. The test simulated a suspend with one
`tick_clock 500` after a fixed `sleep 1.5`. That is a bet that the timer has reached its baseline but
not its next reading - and a fixed sleep cannot guarantee either end. The previous fix for this same
flake had simply raised the sleep from 0.6 s to 1.5 s, with a comment saying load was the cause.

**One hypothesis measured and REJECTED before fixing anything.** The clock is a file, and both the
0.1 s ticker and the jump do a read-modify-write on it, so a lost update looked like the obvious
culprit. Reproduced in isolation, 40 runs: **0 lost**. Had I "fixed" that, I would have changed
working code and left the flake.

**The fix**: jump repeatedly (8 x 500 s over ~1.2 s) instead of once. At least one lands inside the
window; extra ones only restart the wait, which the record check already tolerates. Measured after:
five consecutive clean runs where the failure rate had been roughly one in two.

The general form, which is why this is written down: **a test that waits a fixed time and then asserts
on a race is not slow, it is wrong.** Wait for the condition, or make the stimulus unmissable.
