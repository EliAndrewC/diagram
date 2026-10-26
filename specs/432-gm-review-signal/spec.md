# Feature 432: the GM-review queue holds only what is his

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-26

**Status**: Draft

**Affects**: tooling, review process

**Approved**: the GM, 2026-10-26, "Please file A through F as one feature. after we have cleared the backlog, then there will still be the three GM review items that are genuinely mine open, which is exactly what we want. And then I will handle them on my own time as appropriate. Thank you."

**Input**: `request.md` (the GM's request for the audit, the audit's summary and the A-F proposal as put to him, and his
answer, verbatim); `audit/` (the rubric, the report and every row's verdict).

## Why

The GM, 2026-10-26: *"right now I've basically concluded that I should just ignore it because it is almost purely a
distraction, which is bad, because that probably means that there are a few important things buried in there that I really
should look at, but our system is kind of training me to not even bother"*.

The audit (observed 2026-10-26, method: nine agents, one rubric, every open row; `audit/judged.jsonl`) read the 465 open rows
of 36 features: 443 are not his. Feature 375 (FR-012) queues every round-arbiter ruling and every fix the arbiter orders,
and the arbiter fires on tripwires (round caps 231, hourly step-backs 98, a session's asks 93, red gates 33), so the queue
is the arbiter's log, and `make gm-review` itself says "nothing waits on them". The 22 rows that might be his came by two
paths nothing surfaced: a question written into a step-back's `for_gm` field, or a ruling whose text said "the GM's to
decide". One of the three still live, the magistracy residence size (374#60), was ruled held for him on 2026-10-12 and never
reached the held list: its override row carries a `held` key, and `gm_review.held()` reads only a `flag` opening "Held".

The audit also found the check work behind many rows multiplying from small edits: two bullets added to page 0081 put 217
claims into one triage and 58 impl-drift checks (385#0); about 85 pop-up checks ran on about six bamboo and shelter pop-ups,
each wording edit re-owing its siblings (374#81). No later change scoped either.

## User Scenarios & Testing

### Story 1 - the queue holds only his decisions (A, B, C; P1)

The GM opens `make gm-review` and sees only what needs his decision. A round-cap ruling, a continue, a tooling fix landed
with its test, a routine step-back and a red-gate fix are recorded in the arbiter's own log and never reach him. A ruling or
step-back that wants him writes the question in `for_gm`; it reaches him only after `escalation-check` keeps it, and the
session names it in that turn's final message.

1. **Given** a round-cap `accept` with no `for_gm`, **when** it is recorded, **then** `arbiter.jsonl` has it and
   `gm-review.jsonl` does not.
2. **Given** a ruling carrying `for_gm`, **when** it is recorded, **then** a question row is written as owed
   `escalation-check`, and `make gm-review` lists it to the session, not under the GM's decisions.
3. **Given** escalation-check's KEEP on it, **when** the session records the verdict, **then** the question is held for the
   GM and the session's final message that turn must name it; on CUT it is closed with the reason.
4. **Given** a ruling whose `why` or `what` hands a decision to the GM with no `for_gm`, **when** it is recorded, **then**
   it is refused, naming `for_gm`.

### Story 2 - a held row is never dropped (D; P1)

1. **Given** a question ruled held for the GM, **when** `make gm-review` runs, **then** it is listed among his decisions, from
   one source (the kept questions), so no field name can drop it; an override row edited by hand does not list itself.

### Story 3 - a small edit owes small checks (E; P2)

1. **Given** the 0081 two-bullet edit replayed, **when** the claims it owes are counted, **then** claims citing a passage the
   edit did not change are cleared without a triage, and those citing the changed passage are still owed.
2. **Given** the bamboo and shelter pop-up batch replayed, **when** the checks it owes are counted, **then** a paragraph the
   pop-ups share is checked once, not once a pop-up.

### Story 4 - the backlog cleared, three left (F; P1)

1. **Given** the 465 open rows, **when** the backlog is cleared with the GM's words, **then** every row is reviewed except the
   three that are his (374#60, 385#40, 397#10), `make gm-review` lists exactly those three as needing his decision, and the
   features held open only by their GM-review box close.

## Requirements

- **FR-001 (A)**: `make arbiter-ruled` writes every ruling to the feature's `arbiter.jsonl`, and a row of the GM's review only
  for a question in `for_gm` (FR-002), on every trigger kind, not only the hourly one. `make arbiter-fix-done` writes no
  row of the GM's review. A declined fix (`arbiter-fix-declined`) wants his decision, so it too is written as a question owed
  `escalation-check` (FR-002's path), not straight to him. A finding accepted with a reason (`make accept`) and a known drift
  (feature 430) are rows he may read, not decisions, and are not changed by this feature.
- **FR-002 (B)**: a `for_gm` question is written as a question owed `escalation-check`. `make gm-review` lists owed questions
  to the session apart from the GM's decisions. One command records escalation-check's verdict on a question: KEEP holds
  it for the GM, CUT closes it with the reason, both kept in the record. A feature with an owed question cannot land until
  it is judged. A question kept in a session is named in that session's next final message to the GM; the turn's end is
  refused once while it is not.
- **FR-003 (C)**: `make arbiter-ruled` refuses a ruling whose `why` or `what` hands a decision to the GM (his call, his
  question, his to decide, held for him) without a `for_gm`; the round arbiter's contract says so.
- **FR-004 (D)**: the GM's list of decisions reads one source, FR-002's kept questions. An override row of 328's ranking
  (`audit/overrides.json`, edited by hand, never through escalation-check) no longer lists itself as his decision, whether by
  a `flag` opening "Held" or a `held` key; a row waiting on other work ("Held behind ...") is still listed as waiting. The
  residence row, ruled held on 2026-10-12 and dropped because its `held` key was never read, gets a kept question (FR-006).
- **FR-005 (E)**: measured first on the two replays, then fixed:
  - (a) a page edit owes a claims triage only for claims whose cited passage changed; a claim citing only passages the edit
    left unchanged is cleared mechanically, recorded as such;
  - (b) a paragraph several pop-ups share, edited once, owes its checks once for the pop-ups that share it.
  - No change may let a defect through that today's checks catch: each narrowing is proven on the replays against what
    today's rules owe, or stated and priced.
- **FR-006 (F)**: every open row is marked reviewed with the GM's words of 2026-10-26. The three that are his - 374#60 (the
  magistracy residence size), 385#40 (the dispersed-hamlet feature never filed) and 397#10 (translation-check as a wave job)
  - are each carried on as one kept question (the audit's escalation-check kept all three), so each appears once, as one of
  his three decisions.
- **FR-007**: each change names its cure in its own output and carries a test that fails without it. Every text that says what
  reaches the GM says the new rule; found by `grep -rln "GM's review\|gm-review\|GM review" --exclude-dir=specs
  --exclude-dir=tests --exclude-dir=.git --exclude-dir=.clones .` (2026-10-26), the hits that describe it: the constitution
  (`.specify/memory/constitution.md`, "the GM reviews the ruling after landing"), `CLAUDE.md`, `docs/spec-kit-and-reviews.md`,
  `docs/guards.md`, the round arbiter's, escalation-check's and spec-fidelity's contracts, `scripts/gm_review.py`'s and
  `scripts/hooks/lib/hm_arbiter.py`'s docstrings, and the step-back bundle's text (`scripts/reviews/stepback_bundle.py`); the
  plan reads every other hit and records why it needs no change.

## Success Criteria

- **SC-001** (FR-001): replayed over every ruling and fix recorded in `specs/*/arbiter.jsonl`, the new rule writes a row of
  the GM's review only for the rulings carrying `for_gm` (the audit's count: 22 of the 465 open rows came that way or by a
  ruling's own words), and none for a round-cap ruling, a fix made or a routine step-back.
- **SC-002** (FR-002, FR-003): the tests show a `for_gm` question owed, kept, cut and named; a ruling handing the GM a
  decision without `for_gm` refused.
- **SC-003** (FR-004): `make gm-review` lists the residence question among the GM's decisions, and an override row with a
  `held` key or a "Held" flag and no kept question is not listed as one.
- **SC-004** (FR-005): on the two replays, the claims triaged and the pop-up checks owed fall, with every claim whose cited
  passage changed still owed (the counts before and after in `research.md`).
- **SC-005** (FR-006): after the clearing, `make gm-review` lists exactly three decisions for the GM and no other open row, and
  `make speckit-todo` no longer lists a feature whose only open box was its GM review.

## Assumptions

- The arbiter's log (`arbiter.jsonl`) and the hourly step-back stay as they are; only what reaches the GM changes.
- Whether a question is the GM's is escalation-check's to judge (its contract's tests), as for every other question.
