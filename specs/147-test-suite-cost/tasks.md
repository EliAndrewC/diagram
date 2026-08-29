# Tasks: feature 147 - cut the cost of the test suite

Every task is `research: rendering` - this feature changes what the SUITE costs, never what a map draws or
how a place was built. The GM's acceptance is the final task, by their instruction, and more tasks are
expected after the initial findings.

- [x] T01 the GM's request verbatim; the audit measured BEFORE any change; spec; `spec-fidelity` round 1 (6 changes) and round 2 (FAITHFUL)
- [ ] T02 the audit's numbers recorded in `research.md`, every one labeled WARM or COLD and with the command that produced it, so the next efficiency pass starts from measurements (FR-010)
- [ ] T03 FR-007: the prior performance rounds enumerated (135, 138, 140, 141, 146, and whatever else the record shows), each technique they produced, and whether it applies here - plus the direct answer to *"have we even attempted to take an optimization pass on that particular set of tests"*
- [ ] T04 FR-002/FR-003, technique (i) CACHING: the 31 scripted fixtures share one roll per distinct spec instead of 31, without hiding execution from the coverage floors. The single biggest measured waste
- [ ] T05 FR-006(iii), SEED COUNTS: census every test that rolls more than one seed - how many it rolls, how many the coverage floor and the property actually need - and cut what is redundant, recording the argument (FR-005)
- [ ] T06 FR-006(ii), SMALLER INPUTS: the determinism ratchet rolls a large hamlet twice by design; the pool round-trip and the fan-out each roll a real map. Each examined for a smaller input that still proves the same property
- [ ] T07 FR-004: the five named tests (cohort 155 s, determinism 105 s, pool round-trip 32 s, fan-out 22 s, re-roll 18 s) each cut, reduced, or KEPT with a written statement of what its time buys
- [ ] T08 re-measure all six baselines the same way they were taken (gate warm, gate rolls-forced, sweep warm, sweep cold, cheap loop, the rolls group) and record before/after (SC-001, SC-001b, SC-003)
- [ ] T09 FR-009: the docs corrected where they carry a cold figure as if warm, and every new timing labeled
- [ ] T10 the GM's acceptance of the resulting state
