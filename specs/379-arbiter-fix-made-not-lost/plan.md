# Implementation Plan: an arbiter's tooling fix is made, not lost (feature 379)

**Spec**: `spec.md` | **Request**: `request.md` | **Builds on**: feature 375's round arbiter (`scripts/hooks/lib/hm_arbiter.py`,
`.claude/agents/round-arbiter.md`), the GM's review after landing (`scripts/gm_review.py`) and the closing check
(`scripts/gates/close_check.py`).

## Summary

The ruling gains a `tooling_fix` field; `make arbiter-ruled` records it as an OPEN item on the ruling's row in the feature's
`arbiter.jsonl`, and the ruling's GM-review row carries it. Every `make tick` of that feature, and its closing check, refuse
while one is open. Two commands close it - done (what was built and its test) or declined as an overhaul (why) - and each
adds a row to the GM's review. Tooling only: every task `research: rendering`.

## Constitution Check

I-V N/A (no UI, no pool content, no SOURCE blocks). VI N/A (no generator change). XII N/A (no physical decision). XIII: the
tooling tests and `make hooks-test` green before landing. XIV: none found yet. XVI: built as asked; decisions below.

## Decisions

**D1 - The field, and the contract.** The ruling JSON takes an optional `tooling_fix`: one sentence naming the tool and the
change. The arbiter's contract gives one whenever the loop it judged came from a tooling gap - a guard that let a known
hazard through, a command that misled, a bundle that hid what it needed - and says it is MADE by the session, soon, never
filed. A `process-fault` ruling MUST carry one (its fault, named so a tool can be built against it): `record_ruling` refuses
a `process-fault` without it. The contract's "the fault is filed as a tooling row" becomes "the fault is your
`tooling_fix`"; no ruling's text tells anyone to file a tooling row (FR-001).

**D2 - Recorded open, and shown to the GM.** `record_ruling` keeps `tooling_fix` on the ruling's `arbiter.jsonl` row with
`"fix": "open"`, and on its GM-review row. A later `arbiter.jsonl` row `{"fix_of": "<trigger>", "status": "done"|"declined",
"note": ..., "utc": ...}` closes it; the latest wins. `hm_arbiter.open_fixes(feature dir) -> list[(trigger, tooling_fix)]` is
the one rule every hold reads. The `process-fault` row in `found.jsonl` is no longer written: the open item replaces it
(the found row was what nothing enforced, spec review round 1).

**D3 - The hold is the next tick, and the close.** `scripts/tick-task.py` refuses ANY tick of a feature with an open fix,
naming each and both commands. A tick is the session's next step forward, so the fix is made before the work goes on
("before proceeding with the rest of your implementation") without interrupting a step in flight. `close_check.reasons`
refuses too, so neither a closing status line nor the push closes the feature around it (FR-002, FR-004).

**D4 - Done, with its test, on the GM's review.** `make arbiter-fix-done ID=<trigger> NOTE="<what was built>" TEST=<test
file>`: the TEST must be an existing file under `tests/` (a fix without a test is not done - a guard proves it fires); the
NOTE has the escape reason floor (two words, eight characters). It writes the closing row and a GM-review row (`kind:
arbiter-fix-done`, the fix, the note, the test) and ensures the GM-review box (FR-002).

**D5 - Declined as an overhaul, to the GM.** `make arbiter-fix-declined ID=<trigger> REASON="<why it overhauls a process>"`
(the same floor) writes the closing row and a GM-review row (`kind: arbiter-fix-declined`) and ensures the box (feature 375
FR-012). Nothing files a feature; nothing waits on the GM; the GM reviews it after landing and may overturn it into a
feature (FR-003).

**D6 - The motivating case (SC-001).** 378's ruling in the research clone predates the field; its fix - one gate at a time in
a clone - landed separately today (`scripts/gates/gate_lock.py`). The replay test feeds that ruling, with its fix as the
field, through D2-D5: open; tick refused; close_check refuses; done with `tests/tooling/test_gate_lock.py` closes it and
puts it on the GM's review; a second ruling declined puts the reason there.

**D7 - Where it is written down.** CLAUDE.md's `checks-hooks.sh` guard row gains the hold (one clause); the two targets
carry `##` lines for `make docs`. The guard-file edits (Makefile) carry GUARD_EDIT_OK.

## Amendment 1 - a tooling fix lands alone (FR-005, FR-006)

**D8 - A subset landing, not a flag.** The open-task refusal keeps its "there is no flag" (GM 2026-08-25) and is not
touched: the sessions' deltas mix engine or record work with tooling, so an exemption for an all-tooling delta would never
fire. `make land-tooling FILES="<paths>"` (`scripts/land-tooling.sh`) builds a NEW commit on top of the latest main holding
only those files' changes since the clone's merge base with main (`git diff <merge-base> HEAD -- FILES`, applied with plain
`git apply --index`: a failure IS FR-005's "does not apply cleanly"), in a detached worktree at
`.clones/<clone>-tooling` (a detached worktree is no local branch; the project already uses one for baselines), and lands
that commit with `scripts/sync-with-main.sh done` run from the worktree, so every push check runs unchanged. The clone's
own history is untouched; its next merge of main meets identical hunks and is clean (SC-003). The worktree is removed on
every exit. Measured: `.specify/feature.json` is untracked, so the worktree carries no feature pointer and the open-task
check finds no feature in a delta that touches no `specs/`; `sync-with-main.sh` requires only that its root sit under
`.clones/`.

**D9 - FILES is required and named, never inferred.** A file lands whole, and mid-feature a `CLAUDE.md`, a test or the
`Makefile` edit may describe engine work that has not landed; so with no FILES the command lists the tooling paths the
delta changed and exits 2 (the guard producing the compliant command). A path outside FR-005's set - `scripts/`, `tests/`,
`.claude/agents/`, `.claude/skills/`, any `CLAUDE.md`, the `Makefile`, `.claude/settings.json`, `docs/make-targets.html` -
is refused naming it; so is a FILE with uncommitted changes (only committed work lands). A `Makefile` among them
regenerates `docs/make-targets.html` in the worktree. The checks before the push: `make hooks-test`, `make test-file
FILE=tests/tooling`, and `make test-file` on every test file among FILES (a test needing work not yet landed fails there,
not on main), in the worktree, logged, the tail shown on failure.
The commit is the GM's identity with the clone's commit subjects that touched the files, and the co-author line.

**D10 - Done means landed (FR-006).** `settle_fix(..., "done", ...)` fetches main and refuses unless the TEST file's blob
on `origin/main` equals its blob at the clone's HEAD, naming `make land-tooling FILES="<the test> ..."`. The existing test
fixture gains an `origin/main` holding the test, in the same edit (SC-004).

## Amendment 2 - the arbiter before the GM (FR-007 to FR-010)

**D11 - The spec review's sixth round trips the arbiter.** `scripts/hooks/lib/hm_review_round.py` already numbers a spec
review's rounds (the counter back to one when a round returns FAITHFUL, and a new pass for an amendment). Where it computes
the round, before the snapshot moves (so a refused dispatch spends nothing), a round past `SPEC_ROUND_CAP = 5` beyond the
`continue` rulings on this PASS of the review, `round:spec-fidelity|<feature>#<pass>@` (the pass counted beside the
round in `.git/review-round/<feature>/pass`, one more each time a FAITHFUL round is followed by an amendment - so a ruling
on one pass neither lifts nor closes a later pass's cap; plan review round 1), trips that trigger (`hm_arbiter.trip`, kind `round`) and refuses
with `hm_arbiter.refusal`, as `pair-hooks.sh` does for a review check's third round; `ARBITER_OK="<reason>"` in the prompt
is the escape (the hook's own census row). An `accept` or `process-fault` ruling closes the review: the refusal says so.

**D12 - An `accept` or `process-fault` is the spec's verdict at the push.** `review-gate.sh` refuses a spec with no
FAITHFUL verdict; an arbiter's `accept` or `process-fault` on the review's CURRENT pass, `round:spec-fidelity|<feature>#<pass>@N`
in that feature's `arbiter.jsonl` (the pass read from the clone's `.git/review-round/<feature>/pass`), answers it; a
`continue` does not, and a ruling on an earlier pass does not pass an amended spec (the spec stands as
the last round left it, the GM reviewing the ruling after landing). Without it, "accept" would leave the feature unable to
land - the stop the GM asked to remove.

**D13 - One command for any other process stop.** `make arbiter-ask SUBJECT=<short id> WHY="<the question>"` trips
`ask:<subject>` (kind `ask`, the question its detail; the escape floor on WHY) and builds its bundle in the same command,
printing the MANIFEST to dispatch `round-arbiter` on (FR-009's one command). It holds nothing - the session asked because it is stuck - and the ruling lands on the GM's review like any other. The
round arbiter's contract gains what each ruling means for a spec review (continue: one more round; accept: the spec
stands; process-fault: the review loop is the fault, its `tooling_fix`) and for an `ask` (continue: go on as the question
proposed - for a regression, fix it; accept: it stands, waived; process-fault: the process is wrong, its `tooling_fix`). The bundle states, for a
spec review, that its rounds are the spec's Review history (copied beside it), and for an `ask`, the question.

**D14 - The cap and the exits written once, as five and the arbiter.** The spec-review cap reads five rounds, then the
round arbiter, in CLAUDE.md, the constitution's XVI (its "STOP and put it to the GM" and the two stale sentences counting
three), `.claude/agents/spec-fidelity.md` and `spec-fidelity-verify.md`, and `docs/spec-kit-and-reviews.md`;
`review-gate.sh`'s two-round message is the review checks' cap and stays. The regression exit's "explicit GM waiver"
(CLAUDE.md, `docs/spec-kit-and-reviews.md`, the constitution's XIII) becomes the round arbiter's ruling through `make
arbiter-ask`, reviewed by the GM after landing. The stop-and-ask rule (CLAUDE.md, `docs/spec-kit-and-reviews.md`) is split
as FR-009 says - how the process goes to the arbiter first, what to build to the GM - and so are `wakeup-hooks.sh`'s two
"a question for the GM" lines and `escalation-check.md`'s "a question or a decision" for the GM.

**D15 - The GM's-words waiver of a review check's cap is retired (FR-010).** `pair-hooks.sh` drops its `REVIEW_ROUNDS_OK`
branch, so a third round past the cap meets only the arbiter path (the refusal naming `make arbiter-bundle`); its census
entry in `tests/tooling/test_guard_firing_log.py` goes, its suite's waiver cases become a refusal case, and
`docs/reviews.md`'s sentence names the arbiter. The event log's `waiver` flag stays, reading old transcripts.

## Tasks

T01 the field, the record, `open_fixes`, the found row retired (D1, D2); T02 the holds (D3) and the two commands (D4, D5);
T03 the contract; T04 tests red on today's code, the replay (D6), the docs (D7); T05 the gate, the report, landed.
