# Tasks: feature 147 - cut the cost of the test suite

Every task is `research: rendering` - this feature changes what the SUITE costs, never what a map draws or
how a place was built. The GM's acceptance is the final task, by their instruction, and more tasks are
expected after the initial findings.

- [x] T01 the GM's request verbatim; the audit measured BEFORE any change; spec; `spec-fidelity` round 1 (6 changes) and round 2 (FAITHFUL)
- [x] T02 the audit's numbers recorded in `research.md`, every one labeled WARM or COLD and with the command that produced it, so the next efficiency pass starts from measurements (FR-010)
- [x] T03 FR-007: the prior performance rounds enumerated (135, 138, 140, 141, 146, and whatever else the record shows), each technique they produced, and whether it applies here - plus the direct answer to *"have we even attempted to take an optimization pass on that particular set of tests"*
- [x] T04 FR-002/FR-003, technique (i) CACHING: the 31 scripted fixtures share one roll per distinct spec instead of 31, without hiding execution from the coverage floors. The single biggest measured waste
- [x] T05 FR-006(iii), SEED COUNTS: census every test that rolls more than one seed - how many it rolls, how many the coverage floor and the property actually need - and cut what is redundant, recording the argument (FR-005)
- [x] T06 FR-006(ii), SMALLER INPUTS: the determinism ratchet rolls a large hamlet twice by design; the pool round-trip and the fan-out each roll a real map. Each examined for a smaller input that still proves the same property
- [x] T07 FR-004: the five named tests (cohort 155 s, determinism 105 s, pool round-trip 32 s, fan-out 22 s, re-roll 18 s) each cut, reduced, or KEPT with a written statement of what its time buys
- [x] T08 re-measure all six baselines the same way they were taken (gate warm, gate rolls-forced, sweep warm, sweep cold, cheap loop, the rolls group) and record before/after (SC-001, SC-001b, SC-003)
- [x] T09 FR-009: the docs corrected where they carry a cold figure as if warm, and every new timing labeled
- [x] T10 the GM's acceptance - SUPERSEDED, see T22 at the foot of this file: the GM authorized this landing in their own words, and their acceptance of the whole line of work now sits at the end of feature 148

## The flaky floor, and the GM's ruling (2026-08-29)

The hamlet-path floor's verdict on `hinterland.py` 503-504 is UNSTABLE - the same code gives 100% in one full
run and 99.93% in another. It is not a flaky test: every test passes, and a direct test for those lines
exists and covers them in isolation. What varies is whether that coverage is OBSERVED in the full run, and
the suspect is `--dist worksteal`, which hands tests to workers dynamically so which tests share a process
changes between runs.

The GM's ruling, verbatim: *"I would like to keep the speed up even with the flaky floor. And I think it is
worth pushing the speed up back to main even with the four being somewhat flaky. However, once we have pushed
back to main, I would like to have you work on fixing the flakiness. This gives other sessions the benefit of
the faster tests while also prioritizing fixing something that we know is wrong. With that being said, why
don't we mark the flaky tests as skipped so that other sessions don't end up trying to duplicate your work
and fix them."*

- [x] T20 the speedup pushed to main with the floor parked rather than silently red
- [x] T21 the park marked so no other session re-derives it: a pragma with the full reasoning at the point of
      change in `hinterland.py`, and `tools/hamlet_floor.PARKED`, which prints every parked line on EVERY run
      (announced whether or not it is currently missing - a park that speaks up only when the floor would
      have failed is silent exactly when someone could act on it). `tests/tools/test_hamlet_floor.py` proves
      a parked line passes AND that it excuses only itself, so parking cannot quietly lower the floor
- [x] T22 the flakiness handed to its own feature (148) rather than left open here. WHY THE SPLIT, since it
      changes where the GM's acceptance sits: the GM asked for acceptance as 147's final task, and then - after
      the findings, exactly as they predicted - ruled that the speedup should land FIRST and the flakiness be
      fixed after (*"I think it is worth pushing the speed up back to main even with the four being somewhat
      flaky. However, once we have pushed back to main, I would like to have you work on fixing the
      flakiness"*). A feature in progress lands nothing (constitution, no flag), so those two instructions
      cannot both hold inside one feature: 147 would have to stay open for the fix, and then nothing could be
      pushed. So 147 is the audit, the speedup and the park - complete and landed on the GM's own
      authorization to land it - and 148 carries the fix AND the acceptance of the whole line of work. The GM
      can move the acceptance back by saying so; nothing here is hard to undo
- [x] T10 SUPERSEDED by T22: the GM authorized this landing in their own words rather than at an acceptance
      task, and their acceptance now sits at the end of feature 148
