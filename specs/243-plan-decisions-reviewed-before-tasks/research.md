# Feature 243 - research

## R1 - the incident the gate exists for (feature 239, 2026-09-13; a judgment over its record)

Feature 239's plan made four decisions the spec left open. Two of them narrowed a rule the GM had
accepted: P2 limited spec-lint check 5 to features numbered 239 and later, and the check's code added a
second condition, applying only once a `tasks.md` existed. Both shipped with every task ticked and both
pushes made, and the independent `spec-fidelity` MODE 1 check that constitution XVI requires BEFORE an
exception reaches the GM never ran. The escalation filter noticed its absence while reviewing the
closing report; the two checks then ran and ruled both decisions NOT LEGITIMATE - the first exempted
feature 236's amendment, the very case the rule was built for - and removing them took a second fix,
gate and push, and a second filter round (`specs/239-*/plan.md` P2, `tasks.md` T17).

Nothing in the tooling asks for that check. `scripts/review-gate.sh` refuses a push whose SPEC has no
FAITHFUL verdict, which feature 239 satisfied at the GM's acceptance; a plan is written after that
verdict, and nothing reads it.

## R2 - what existing plans look like (census, 2026-09-13)

Across the 158 spec directories there are 112 `plan.md` files. Their decisions take no common form: 21
carry a heading naming decisions, 41 use words like exception, narrow or carve-out somewhere in their
prose, and exactly ONE labels its decisions with ids (`**P1 -`), feature 239's own. A gate therefore
cannot find a narrowing decision by its label - and could not trust one if it did, because the failure
it exists to catch is an author not seeing that a decision narrows the spec. The independent reader has
to read the whole plan and find them.

## R3 - the mechanisms a gate can reuse (2026-09-13)

- `scripts/tick-task.py` (`make tick`) is the one route by which a task is ticked, so a refusal there
  stops implementation from being recorded as done.
- `scripts/review-gate.sh` runs at push from `sync-with-main.sh`, with a `REVIEW_GATE_OK="<reason>"`
  escape that is logged; a push is where the GATED and DIRECT routes both pass.
- The record that only a reviewer may write already has a pattern: `make perf-confirm ... AS=perf-audit`
  declines without the declaration, and its limit is disclosed in the root `CLAUDE.md` - nothing
  distinguishes the shells, so the declaration is recorded rather than proven.
