# 432-gm-review-signal - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-26 -->
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

<!-- plan-archive: archived 2026-10-26 -->
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
- **D4** The refusal pattern for C is words handing the GM a decision in `why` or `what` - the regular expressions
  `the GM's (to decide|call|question|decision)`, `for the GM to`, `held for the GM`, `the GM (must|should) decide`,
  `GM's choice` (case-insensitive) - with no `for_gm`; tested on the audit's rows that said it (335#2, 374#60) and on 20 rulings that do not. Rendering: none.

<!-- plan-archive: archived 2026-10-26 -->
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

<!-- plan-archive: archived 2026-10-26 -->
## T06 - F: the backlog cleared, three carried (FR-006)

### T06 Approach (checklist part A)

1. **The goal, in the world.** `make gm-review` shows exactly the GM's three decisions, and the features held open only by
   their GM-review box close.
2. **The constraints.** His words on every row cleared; nothing deleted.
3. **Where each comes from.** O: the GM's answer, `request.md`.
4. **Do they describe the world here?** Yes: 465 open rows (measured 2026-10-26 (`make gm-review`), `audit/judged.jsonl`).
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

