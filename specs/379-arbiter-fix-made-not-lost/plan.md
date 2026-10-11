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

## Tasks

T01 the field, the record, `open_fixes`, the found row retired (D1, D2); T02 the holds (D3) and the two commands (D4, D5);
T03 the contract; T04 tests red on today's code, the replay (D6), the docs (D7); T05 the gate, the report, landed.
