# Feature 243 - research

## R1 - the incident the gate exists for (feature 239, 2026-09-13; a judgment over its record)

Feature 239 shipped two narrowings of a rule the GM had accepted. The first was a decision in its plan:
P2 limited spec-lint check 5 to features numbered 239 and later. The second was never written into the
plan: the check's code added a condition, applying only once a `tasks.md` existed. Both shipped with
every task ticked and both pushes made, and the independent `spec-fidelity` MODE 1 check that
constitution XVI requires BEFORE an exception reaches the GM never ran. The escalation filter noticed
its absence while reviewing the closing report; the two checks then ran and ruled both NOT LEGITIMATE -
the first exempted feature 236's amendment, the very case the rule was built for - and removing them
took a second fix, gate and push, and a second filter round (`specs/239-*/plan.md` P2, `tasks.md` T17).

How P2 was framed matters for the design. As first committed
(`git show 95179a93:specs/239-measurable-guards-and-derived-figures/plan.md`) it read: *"P2 - check 5
applies to features numbered 239 and later. The spec says a figure with a unit must carry a key; it does
not say whether that reaches the 238 specs written before the rule existed."* The author presented it as
a question the spec left open, not as a narrowing, so a gate that reviewed only the decisions an author
marks as narrowing would not have seen it.

Nothing in the tooling asks for the check. `scripts/review-gate.sh` refuses a push whose SPEC has no
FAITHFUL verdict, which feature 239 satisfied at the GM's acceptance; a plan is written after that
verdict, and nothing reads it. A gate keyed on `plan.md` reaches the first narrowing and not the second.

## R2 - what existing plans look like (census, 2026-09-13)

Across the 158 spec directories there are 112 `plan.md` files (`ls specs/*/plan.md | wc -l`). Their
decisions take no common form: 21 carry a heading naming decisions
(`grep -l -E '^#+ .*[Dd]ecision' specs/*/plan.md | wc -l`), 30 use the words exception, narrow or
carve-out somewhere (`grep -l -i -E 'exception|narrow|carve-out' specs/*/plan.md | wc -l`), and exactly
one labels its decisions with ids (`**P1 -`), feature 239's own. 43 spec directories have a `tasks.md`
and no `plan.md` (for example 124, 139, 169, 170, 236, 241). This is supporting detail for D1, not its
ground: the ground is R1.

## R3 - the mechanisms a gate can reuse (2026-09-13)

- `scripts/tick-task.py` (`make tick`) is the tooling route by which a task is ticked; it resolves the
  spec directory, reads `tasks.md` and refuses to stderr with exit 2. It is NOT the only route: no hook
  refuses a hand edit that turns `- [ ]` into `- [x]` in a `tasks.md`, so a refusal at tick time alone
  can be walked around, and the push is where a gate holds (spec D4).
- `scripts/review-gate.sh` runs at push from `sync-with-main.sh`, with a `REVIEW_GATE_OK="<reason>"`
  escape that is logged; it judges every feature whose `specs/NNN-*/` directory the delta touches, not
  only those whose `spec.md` changed, and a push is where the GATED and DIRECT routes both pass.
- The record that only a reviewer may write already has a pattern: `make perf-confirm ... AS=perf-audit`
  declines without the declaration, and its limit is disclosed in the root `CLAUDE.md` - nothing
  distinguishes the shells, so the declaration is recorded rather than proven.
