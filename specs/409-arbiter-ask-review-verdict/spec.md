# Feature 409: an arbiter's ruling on an asked review stands as that review's verdict

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-22

**Status**: Draft

**Affects**: tooling

**Approved**: the GM, 2026-10-22, "Yes, please go ahead and file that tooling feature and then go ahead and work the feature start to finish. Thank you."

**Input**: `request.md`

## The gap (measured on feature 408)

The gates already take the round arbiter's `accept` (or `process-fault`) as a review's verdict when the ruling is on a
ROUND trigger: `round:spec-fidelity|<feature>#...` for a spec (feature 379 amendment 2, `hm_arbiter.spec_ruled`, read by
`review-gate.sh`) and `round:spec-fidelity|plan:<feature>#...` for a plan (feature 385 T16, `plan_gate.arbiter_accept`,
run when the ruling is recorded). A session that puts the same question through `make arbiter-ask` - which the record
rules send a third round to before it runs - gets an `ask:<subject>` trigger. Its ruling row names no review, so neither
gate can tell it is a spec's or a plan's verdict, and nothing honors it:

- 408's `ask:408-spec-round3` (accept) did not satisfy `review-gate.sh`; a third spec-fidelity round ran anyway.
- 408's `ask:408-plan-round3` (accept) did not satisfy `plan-gate.sh`: `dev/bypass-log/` holds 6 `plan-gate push` and
  19 `plan-gate tick` escapes for 408 (clone 686ec2) with the reason "round arbiter ruled ACCEPT on ask:408-plan-round3",
  and the page sessions' plan-review-stale guard fired on a plan that had not changed since the ruling.

## User Scenarios & Testing

### User Story 1 - An asked spec or plan review closes on the arbiter's accept (Priority: P1)

**Acceptance Scenarios**:

1. `make arbiter-ask SUBJECT=<s> WHY="..." REVIEW=plan` records the ask as about the active feature's plan review; when the
   round arbiter rules `accept` or `process-fault` on it, the plan's owed and BLOCKED blocks are recorded CLEAR at their
   digest at that moment, declared `round-arbiter` - exactly what a ruling on a plan round trigger does - and `plan-gate.sh`
   and `make tick` pass on that plan with no escape.
2. `REVIEW=spec` records the ask as about the spec review; the ruling row carries the spec's body digest, and
   `review-gate.sh` takes it as the spec's verdict while the spec still reads so - exactly as for a spec round trigger.
3. An ask without `REVIEW=` is about no review, whatever its SUBJECT says. Where the SUBJECT looks like a review's
   (`<n>-spec-...`, `<n>-plan-...`), the ask prints a hint to pass `REVIEW=`; the hint records nothing.
4. A plan or spec edited after the ruling is NOT covered by it: a changed plan block is owed its review as before (`make
   plan-delta`), a changed spec is owed spec-fidelity as before. A `continue` ruling records nothing CLEAR.
5. Every other ask, with no review named or inferred, is recorded and ruled exactly as today.

## Requirements

### Functional Requirements

- **FR-001**: `make arbiter-ask` MUST accept `REVIEW=spec|plan` and record it on the ask's owed entry, and the ask's output
  names the review the ruling will stand for. An ask without `REVIEW=` is about no review. The question the arbiter's bundle
  shows says, for a review ask, that an accept stands as that review's verdict.
- **FR-002**: A ruling recorded on an ask about a review MUST carry `review` in its `arbiter.jsonl` row, and for `spec` the
  spec body digest (`spec_sha`) as a spec round's ruling does.
- **FR-003**: `hm_arbiter.spec_ruled` MUST honor an `accept`/`process-fault` row whose `review` is `spec` and whose
  `spec_sha` matches the spec now, as it honors a spec round trigger's.
- **FR-004**: An `accept`/`process-fault` ruling on an ask whose `review` is `plan` MUST run `plan_gate.arbiter_accept` for
  the active feature, as a plan round trigger's ruling does; `arbiter_accept` MUST take such a trigger.
- **FR-005**: Each behavior has a unit test that fails with the change removed.

## Success Criteria

- **SC-001**: In a fixture feature, an asked plan review ruled `accept` leaves `plan_gate.py push` owing nothing for that
  plan, and an asked spec review ruled `accept` makes `spec_ruled` answer for the unchanged spec and not for an edited one.
- **SC-002**: `make test-file FILE="tests/hooks/test_hm_arbiter.py tests/tooling/test_plan_arbiter_accept.py"` and
  `make hooks-test` pass.

## Assumptions

- No backfill: 408's two `ask:` rulings were made before this and its plan has had blocks added since; 408 is closed and no
  later push re-ticks it. A ruling made before this lands keeps today's behavior.
- The ruling covers the spec or plan as it reads at the ruling, not edits the ruling itself asks for (408's arbiter asked for
  two spec wording fixes after its accept); those owe their ordinary review, which `make plan-delta` keeps to the changed
  blocks.

## Review history

- spec-fidelity round 1 (2026-10-22): CHANGES REQUIRED - the SUBJECT inference was not asked for (an accept on an ask merely
  named like a plan would clear every owed plan block); dropped, a hint kept that records nothing; the escape counts
  reconciled with `dev/bypass-log/`.
