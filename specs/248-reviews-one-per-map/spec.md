# Feature 248 - reviews one per map

**Status**: DRAFT - awaiting the spec-fidelity review.
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Research**: [`research.md`](research.md) - the serialized review's cost and the ledger's answer, where the push refusal's time went, what a hook can guarantee, the classification, how a dispatch names its maps.
**Predecessors**: 151 (the paired gate), 231 (a review owed only when a layout moved), 240 (the verdict record, the prerequisite check), 246 (a run still going is not abandoned).

## Summary

Feature 247 spent eleven of its thirty-six minutes on one settlement-review agent serialized over four maps (research R1), and
its push was refused once for a hand-written record of a review the reviewer had already recorded. The
GM's ruling: a costly wrong shape is the tooling's to prevent, not the session's to remember - *"whatever
the tooling is currently doing to kick off reviews should be modified to make the correct thing happen
automatically"* - together with the two changes the breakdown recommended and one more the GM asked for
by name. So: a settlement-review dispatch that asks for more than one map is refused before the agent
starts, with no escape (FR-001); `make verify` and the pair guard hand the session one ready prompt per
owed map (FR-002); a turn may not end while an owed map has no review dispatched or recorded (FR-003);
whether the dispatches ran in parallel is measured and recorded, never refused, because a hook cannot
force it (FR-004); a feature whose every task is a rendering convention owes no settlement-review, by
the classification every task already carries (FR-005); and a changed pool map ships on its reviewer's
verdict record rather than on a notes-file touch (FR-006). What a hook can and cannot guarantee is
stated rather than promised (research R3, D4, D6).

## Functional requirements

- **FR-001 A settlement-review dispatch asks for exactly one map.** The pair guard's Agent branch, before
  the prerequisite check, counts the owed maps the dispatch names (R5: the snapshot directories
  `review-snapshot/<map>` it names; when it names none, the owed maps whose names appear as words). More
  than one is refused with exit 2 before the agent starts, naming the per-map prompt files of FR-002 and
  saying to dispatch them as separate Agent calls in the same message. No escape token: a multi-map review
  is never the right shape. A dispatch naming no owed map at all passes this rule (it is not a review of an
  owed map) and meets the guard's other rules as today.
- **FR-002 The tooling writes the prompts.** Wherever a review is found owed at gate time - `make verify`
  and the pair guard's permit branch - the snapshot script writes one dispatch prompt per owed map at
  `<clone>/.git/review-snapshot/<map>/dispatch.md`, carrying the map, its two snapshot directories and
  every file the clone snapshot lacks, the engine key, and the reviewer's standing instructions (the delta
  scope, the contract's first stage, the verdict record). Both places print the N files and say: N
  settlement-review agents, one per map, all in this same message. The one-line "settlement-review over
  <maps>" instruction is retired.
- **FR-003 A turn does not end with an owed map unreviewed.** At each permitted settlement-review dispatch
  the guard records, in the clone's pairing state, the map the dispatch names, the engine key and the
  time. At turn end, for every owed map: a PASS or NEEDS-WORK verdict at this engine key, a dispatch
  recorded at this key, or a pending review agent whose prompt names the map, counts; a map with none
  is missing, and the turn is refused once per (engine key, missing set), naming the missing maps and
  their prompt files. The existing waivers (`PAIR_OK` on the gate, no layout moved, FR-005) clear it as
  they clear the half-open rule today, and the existing half-open rule stays for the case where no map
  was dispatched at all.
- **FR-004 Parallelism is measured, not forced.** When the last owed map's dispatch is recorded, the guard
  records one entry: `reviews-parallel` when the owed maps' dispatch times span under `PARALLEL_SPAN_S` (sixty seconds, a definition - D4), otherwise
  `reviews-serialized` with the span. `make audit` shows both counts. Nothing is refused on it (R3: by the
  time it can be judged, the agents have run).
- **FR-005 A rendering-only feature owes no settlement-review.** `_review_owed.py` reads the clone's
  active feature - the one `.specify/feature.json` names - and when its `tasks.md` exists, holds at least
  one task, and every task is classified `research: rendering`, reports no map owed, with a reason naming
  the feature and its task count (R4). A feature with any `physical` or `procedure` task, no tasks, no
  `tasks.md`, or no pointer owes a review exactly as today. Because every decision point already asks
  this one script (`make verify`, the pair guard's gate branch and stop branch, and FR-006's push gate),
  the waiver reaches all of them, is printed where the gate starts, and is recorded at turn end with
  its reason as feature 231's waiver is.
- **FR-006 A changed map ships on its verdict record.** `review-gate.sh` passes a changed pool manifest
  when its verdict record holds PASS or NEEDS-WORK at the engine key of the pushed tree, or when FR-005's
  waiver holds for the push, or - only when the map has no verdict record at all (a map reviewed before
  the records existed, the legacy tree) - when its notes file is touched in the same push, as today. A
  NOT-REVIEWABLE record still refuses, as today; a verdict at a stale engine key does not count. The
  refusal names the map and which of the three it lacks.
- **FR-007 The record.** The reviewer's contract says the tooling refuses a multi-map dispatch and hands
  over the per-map prompts; CLAUDE.md's pairing row and the review doctrine say the four rules and the
  waiver; the ledger's row-per-pass rule is unchanged.
- **FR-008 Proved.** `scripts/test-pair-hooks.sh` drives the guard with real payloads: a two-map dispatch
  refused and a one-map dispatch permitted; the stop rule refusing on an owed map with no dispatch,
  quiet when every map is dispatched or recorded, and refused once; the parallel and serialized
  entries. `tests/tooling/test_review_owed.py` proves the classification waiver on fixture task files
  in every form (all rendering; one physical; one procedure; no tasks; no pointer). `scripts/test-review-gate.sh`
  proves each of FR-006's three passes and both refusals. The firing-log census sees every new rule.

## Success criteria

- **SC-001** (FR-001, FR-002): on a clone with two owed maps, a settlement-review dispatch naming both is
  refused before it starts and the refusal names two prompt files that exist; a dispatch of either file's
  prompt is permitted.
- **SC-002** (FR-003, FR-004): the suite's stop case with one of two owed maps dispatched is refused once,
  naming the other; with both dispatched within the span it records `reviews-parallel`, and with the
  second dispatch a fixture-clock minute later, `reviews-serialized`.
- **SC-003** (FR-005): on this clone with feature 247's task file as the active feature, `_review_owed.py`
  reports no map owed with the rendering reason although four manifests differ from main; with feature
  230's, it reports the four.
- **SC-004** (FR-006): the review gate passes feature 247's four manifests on their PASS records at the
  landed engine key with no notes touch, refuses a manifest whose only record is NOT-REVIEWABLE, and
  refuses one with a PASS record at another engine key and no notes touch.
- **SC-005** (FR-007, FR-008): the contract and CLAUDE.md say the rules; `make hooks-test` green; the
  firing-log census and the guard corpus green; lands DIRECT (guard scripts and tooling tests, no engine
  code).

## Decisions recorded

- **D1 - no escape on FR-001.** Every guard here takes a reasoned `_OK` except the ones whose action is
  never right (the force-push and history rules); a review of several maps in one agent is in that
  class - it serializes work that shares nothing and there is no case where that is wanted.
- **D2 - the maps a dispatch names are its snapshot directories first, bare names second** (R5). A
  bare-name rule alone would refuse a one-map prompt that mentions a neighbor for context; a
  snapshot-only rule would let a prompt that names no snapshot review several maps by name. The prompt
  files of FR-002 name one snapshot each, so a session dispatching from them never meets the second rule.
- **D3 - the waiver is rendering-only, literally** (R4). A `procedure` feature that moves a manifest
  changed the layout by a mechanism nobody researched, which is the case the review caught on 226 and
  227; the GM named the glyph-convention case and nothing wider. Widening to procedure is a separate
  ruling, not taken here.
- **D4 - parallelism is recorded, never refused.** A hook cannot launch an agent or force several calls
  into one message; it can refuse the wrong shape and hold the turn open, and it can measure. The
  sixty-second span is a definition, not a measurement: parallel calls land within seconds, a sequential one is at
  least a model turn later.
- **D5 - the notes touch survives only as the fallback for a map with no verdict record.** The
  reviewer's record is the one record (the GM: the redundancy is the cost); the legacy hand-authored
  tree and any map never reviewed since feature 240 have no record to ship on, so the 2026-07-27 form
  stays for them alone. A session cannot substitute a notes touch for a review on a map that has a
  record, stale or not.
- **D6 - a review dispatched under another agent type is not caught, and is recorded as such.** A
  general-purpose agent handed a review prompt passes every Agent-typed guard (the escalation guard has
  the same gap today). Matching prompt content would be a mention test, which this project's guard rules
  forbid; the gap is stated in the contract and the doctrine rather than pretended closed.
- **D7 - the active feature is the pointer, not the delta.** `sync-with-main.sh` derives the in-progress
  feature from open tasks the delta touches OR the pointer; the waiver reads the pointer alone, because a
  delta can touch several features' files (a sweep) and the classification is a property of the work the
  session declares it is doing. A wrong pointer names a feature whose tasks the session is not doing,
  and FR-005's reason prints the feature so the waiver is auditable.

## Out of scope

- The ledger row per pass (`docs/review-ledger.md`), still written by hand.
- `building-review` and `size-audit` (Mode A, no pool map, no snapshot).
- The escalation guard's agent-type gap (D6, shared).
- Widening the waiver to `procedure` tasks (D3).

## Review history

- (none yet)
