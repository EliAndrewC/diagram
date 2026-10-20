# Tasks - feature 406: every tool measured by what it does

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md).

- [ ] T01 The usage-log helper and the tool registry: one helper every silent tool records through, and one registry of what records (FR-002) [lands-open]
      research: rendering
- [ ] T02 A make target's outcome recorded: the event log records a failed tool call beside a succeeded one, and the runs it cannot see record through the helper (FR-003) [lands-open]
      research: rendering
- [ ] T03 The silent tools record: every refusing check, the two silent hooks and the automatic steps call the helper, each in the registry (FR-002) [lands-open]
      research: rendering
- [ ] T04 `make tool-yield`: every wired hook, refusing check, make target, review check and logged step, with its uses, interventions, likely misfires, too new or no outcome record (FR-001) [lands-open]
      research: rendering
- [ ] T05 The rule: `make hooks-test` refuses a hook or check that records nothing without naming its record, and a helper call or registry entry the other lacks (FR-004) [lands-open]
      research: rendering
- [ ] T06 `make fix-yield` on the new numbers: each arbiter fix by the tools its change touched, since it was made; the step-back reads it (FR-005) [lands-open]
      research: rendering
- [ ] T07 The 22 fixes judged: each a recorded judgment citing its numbers, for the GM's review (FR-005, SC-003) [lands-open]
      research: rendering
- [ ] T08 The close: the feature report and its retro rows [lands-open]
      research: rendering

- [ ] GM review (make gm-reviewed F=406) [lands-open]
