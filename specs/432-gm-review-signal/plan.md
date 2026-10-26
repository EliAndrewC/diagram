# Implementation Plan: the GM-review queue holds only what is his (feature 432)

**Spec**: `spec.md` | **Request**: `request.md` | **Audit**: `audit/`

## Summary

One source for what reaches the GM - a QUESTION record, owed escalation-check until judged, then kept (his decision) or cut -
written by the arbiter only from `for_gm` and from a declined fix; every other ruling and every fix made stays in
`arbiter.jsonl`. The held list reads those records alone. E measures the claims triage and the pop-up cascade before
changing either. F clears the backlog with his words and carries the three that are his as kept questions.

## Measured before planning (2026-10-26)

- **What the arbiter has recorded** (observed 2026-10-26, method: every `specs/*/arbiter.jsonl` row with a `ruling`): 344
  rulings (166 round, 77 hour, 66 ask, 35 others); 25 carry `for_gm`, all on hour triggers (only the hour's ruling may
  carry one today, `hm_arbiter.record`). Under FR-001 those 25 and the 7 declined fixes are the rows that would have
  reached the door, against 465 open rows queued.
- **The held list** (observed 2026-10-26, method: `scripts/gm_review.py` `held()` and `specs/328-match-the-research/audit/
  overrides.json`): `held()` lists an override whose `flag` opens "Held"; the residence row carries a `held` key and a
  `flag` opening "deviation-tempting", so it is not listed. One override row's flag opens "Held behind" (the tubs row,
  waiting on another row).
- **Claims after a triage** (observed 2026-10-26, method: the impl-drift rows of `dev/review-ledger.md` since 2026-10-10,
  each "impl-drift: N claims - IN-STEP a, ..."): 284 passes over 3,471 claims, 2,664 IN-STEP (77%). The ledger does not say
  which passes a triage fed, so T05 measures that before deciding.

## Constitution Check

Tooling only (no engine path): `scripts/`, `tests/`, the Makefile, `.claude/agents/`, docs and the constitution's text. Lands
by the DIRECT route; no map moves. Every guard keeps its test companion (XVIII).

## T01 - the question record and one source for held decisions (FR-002 record, FR-004)

### T01 Approach (checklist part A)

1. **The goal, in the world.** The GM's list of decisions comes from one place, so nothing ruled his can be dropped by a field
   name again, and nothing hand-edited can list itself.
2. **The constraints.** `gm-review.jsonl` stays the per-feature file; old rows read as before.
3. **Where each comes from.** O: spec FR-002, FR-004; the audit (374#60 dropped by `held()`).
4. **Do they describe the world here?** Yes, measured above.
5. **The order.** First: T02 and T03 write and enforce these records.
6. **The exits.** Red: the failing seeds recorded and the task set down, a claim that it cannot be placed correctly ruled through `make arbiter-ask` (D11, D35).
7. **The search smell.** None.
8. **The budget.** 45 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** Tests: a question row owed, kept, cut; the decisions list reads kept questions only; an override with a
   `held` key or "Held" flag and no question is not listed; "Held behind" still lists as waiting.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1** A question is a `gm-review.jsonl` row of kind `question`: `{kind, id, question, source (the trigger or fix), status:
  owed | kept | cut, reason, utc}`; `make gm-escalated F=<n> ROW=<n> VERDICT=KEEP|CUT REASON="..."` records escalation-check's
  verdict. `make gm-review` shows kept questions as "needs your decision", owed ones under "owed escalation-check (the
  session's)", and nothing else as a decision. Rendering: none.
- **D2** `held()` keeps only the "waiting on other work" reading of override flags ("Held behind ..."); an override's own
  "Held" flag or `held` key is no longer a decision. Rendering: none.

## T02 - what the arbiter queues (FR-001, FR-003)

### T02 Approach (checklist part A)

1. **The goal, in the world.** A ruling or a fix made never reaches the GM; a question he must answer reaches him only
   through the door.
2. **The constraints.** `arbiter.jsonl` unchanged; the hour's "continue with nothing" rule kept; the fix bookkeeping (open,
   done, declined) unchanged.
3. **Where each comes from.** O: spec FR-001, FR-003.
4. **Do they describe the world here?** Yes: `hm_arbiter.record` queues every non-trivial ruling, `settle_fix` every fix.
5. **The order.** After T01.
6. **The exits.** Red: the failing seeds recorded and the task set down, a claim that it cannot be placed correctly ruled through `make arbiter-ask` (D11, D35).
7. **The search smell.** None.
8. **The budget.** 45 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** Tests: an accept, a continue, a change-route and a fix done write no GM row; a ruling with `for_gm` on
   any trigger writes one owed question; a declined fix writes one owed question; a ruling whose `why`/`what` hands the GM a
   decision without `for_gm` is refused naming `for_gm`. SC-001's replay over the recorded rulings in `research.md`.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D3** `for_gm` is accepted on every trigger kind, and the arbiter-bundle text and the round arbiter's contract say it is
  the one way to put anything to the GM, and only what passes escalation-check's tests. Rendering: none.
- **D4** The refusal pattern for C is words handing the GM a decision in `why` or `what`: "the GM's (to decide|call|question|
  decision)", "for the GM to", "held for the GM", "the GM (must|should) decide", "GM's choice" (case-insensitive), with no
  `for_gm`; tested on the audit's rows that said it (335#2, 374#60) and on 20 rulings that do not. Rendering: none.

## T03 - the door enforced (FR-002 enforcement)

### T03 Approach (checklist part A)

1. **The goal, in the world.** A question cannot sit unjudged, and a kept one is told to the GM the turn it is kept.
2. **The constraints.** A refusal names the command that clears it; the turn's end is refused at most once per message.
3. **Where each comes from.** O: spec FR-002.
4. **Do they describe the world here?** Yes: the push gates and `escalation-hooks.sh` (feature 429 T02) are the two places.
5. **The order.** After T01 and T02.
6. **The exits.** Red: the failing seeds recorded and the task set down, a claim that it cannot be placed correctly ruled through `make arbiter-ask` (D11, D35).
7. **The search smell.** None.
8. **The budget.** 45 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** Tests: a landing of a feature with an owed question refused naming `make gm-escalated`; a kept question
   recorded since the GM's last message and not named (by its row id) in the final message refuses the turn's end once.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D5** The landing refusal lives in the push gates (`scripts/gates/push_gates.py`) over the active feature's records; the
  Stop check in `escalation-hooks.sh` reads kept questions whose `utc` is after the session's last GM message. Rendering: none.

## T04 - E(b): pop-ups that share a paragraph (FR-005 b)

### T04 Approach (checklist part A)

1. **The goal, in the world.** One wording edit to a passage several pop-ups share costs one round of checks, not one a
   pop-up.
2. **The constraints.** No check skipped on a pop-up whose own text changed (FR-005's no-defect rule).
3. **Where each comes from.** O: the audit's 374#81 (about 85 checks on about six pop-ups).
4. **Do they describe the world here?** To be measured: replay 374's bamboo and shelter batch through `make record-owed` and
   count what each edit owed, and why.
5. **The order.** After T03; measured before any change.
6. **The exits.** Red: the failing seeds recorded and the task set down, a claim that it cannot be placed correctly ruled through `make arbiter-ask` (D11, D35).
7. **The search smell.** None.
8. **The budget.** 90 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** `research.md` R2: the batch's owed checks before and after, with every pop-up whose own text changed
   still owed.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T04 Decisions

- **D6** Measure first; the change is chosen from what the replay shows owed each check (a shared paragraph, a sibling's
  re-owe, or a rule of the checks) and recorded as a decision before it is made. Rendering: none.

## T05 - E(a): claims after a page edit (FR-005 a)

### T05 Approach (checklist part A)

1. **The goal, in the world.** A small page edit owes impl-drift only on the claims the edited passage bears on.
2. **The constraints.** A claim whose cited passage changed stays owed; no narrowing lets through a drift today's checks catch.
3. **Where each comes from.** O: the audit's 385#0 (217 claims triaged, 58 impl-drift checks for two bullets on 0081).
4. **Do they describe the world here?** In part: since feature 318 a claim is owed impl-drift only when a block it rests on
   changed, the rest a triage (`scripts/record/claims_triage.py`). To be measured: on recent triages, how many claims the
   triage named TOUCHES, and what impl-drift then found on them.
5. **The order.** After T04.
6. **The exits.** Red: the failing seeds recorded and the task set down, a claim that it cannot be placed correctly ruled through `make arbiter-ask` (D11, D35).
7. **The search smell.** None.
8. **The budget.** 90 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** `research.md` R3: the 0081 edit's claims owed by today's rules and by the change, with every DRIFTED
   claim the old route found still owed.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T05 Decisions

- **D7** Measure first (the triage's TOUCHES and impl-drift's yield on them); if the triage is already the per-passage scoping
  the GM asked for, the change is to the triage's own threshold for TOUCHES, recorded with its yield. Rendering: none.

## T06 - F: the backlog cleared, three carried (FR-006)

### T06 Approach (checklist part A)

1. **The goal, in the world.** `make gm-review` shows exactly the GM's three decisions, and the features held open only by
   their GM-review box close.
2. **The constraints.** His words on every row cleared; nothing deleted.
3. **Where each comes from.** O: the GM's answer, `request.md`.
4. **Do they describe the world here?** Yes: 465 open rows, `audit/judged.jsonl`.
5. **The order.** After T01-T03 (the three need the question record).
6. **The exits.** Red: the failing seeds recorded and the task set down, a claim that it cannot be placed correctly ruled through `make arbiter-ask` (D11, D35).
7. **The search smell.** None.
8. **The budget.** 30 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** SC-005: `make gm-review` lists three decisions and no other open row; `make speckit-todo` before and
   after.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T06 Decisions

- **D8** Every open row is marked reviewed with `make gm-reviewed F=<n> WORDS="<his answer>"`, feature by feature; the three
  are written as kept questions in their own features (374, 385, 397), each with the audit's escalation-check reason.
  Rendering: none.

## T07 - the texts that say what reaches the GM, and the close (FR-007)

### T07 Approach (checklist part A)

1. **The goal, in the world.** No document tells a session or the GM that every ruling reaches him.
2. **The constraints.** The constitution's text changes with the amendment rule it carries.
3. **Where each comes from.** O: spec FR-007's search.
4. **Do they describe the world here?** Yes, the search's hits.
5. **The order.** Last.
6. **The exits.** Red: the failing seeds recorded and the task set down, a claim that it cannot be placed correctly ruled through `make arbiter-ask` (D11, D35).
7. **The search smell.** None.
8. **The budget.** 30 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** Each hit of the search changed or recorded as needing none; `make feature-report F=432 WRITE=1`.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T07 Decisions

- **D9** The texts change with the code of the task that makes each true (T01-T03), and T07 sweeps the rest. Rendering: none.
