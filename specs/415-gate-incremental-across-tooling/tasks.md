# Tasks - feature 415, the gate stays incremental across tooling changes

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

- [x] T01 The run record says what ran, why, and where the time went: plan mode, reason and selected count; each phase's seconds (D1, D2; FR-002, FR-005)
      research: rendering
      verify: DONE. landed: phases and this run's plan in the gate's run record; runstats tests green (20), the new test red without
- [x] T02 A tooling change no longer runs everything: a planner hash of the gate's configuration, the scripts/ readers selected, the tooling tests reused on an incremental plan (D3, D4; FR-001)
      research: rendering
      verify: DONE. landed: the planner plans full on the gate's configuration, not the tooling hash; scripts/ changes select their readers; ci and reuse tests green, the new tests red without
- [x] T03 The landing waits only on what can refuse it: the cohort's fresh block after the push, cover-changed beside the gate (D5, D6; FR-003, FR-004)
      research: rendering
      verify: DONE. landed: fresh block after the push under a lock; cover-changed beside the gate, stopping it on a refusal; 62 landing/cohort/runstats tests green, the new ones red without
- [x] T04 The gate's fixed and per-test costs and the selection's growth between full runs, measured (D7; FR-007)
      research: rendering
      verify: DONE. landed: research R2: one full and three incremental gate runs measured (67 s fixed + 12.7 ms per selected test, the selection 1,492 -> 2,657 between full runs); make gate-costs and its test
- [x] T05 A landing runs what its change reaches; the baseline refreshed off the landing's path, on T04's numbers (D8; FR-006)
      research: rendering
      verify: DONE. landed: a landing's gate plans with no FULL_FRACTION cutoff (NO_CUTOFF to the planner's call alone); after the push, a landing gate that selected >= 25% of its baseline starts a full refresh in a worktree; cover_changed's coverage data in its own directory; the gate's machinery lands through a gate
- [x] T06 A real engine landing after a tooling change measured end to end against T26's 8.8 minutes (D9; SC-006)
      research: rendering
      verify: DONE. research.md R3: 417 T04's landing (D9's: incremental, scripts/ changed) measured from its log and run record, 5.1 min against R1's 8.8; the full-plan reasons since counted
- [x] T08 A changed hook suite (`tests/hooks/*.sh`) plans the gate FULL ("a non-module file under tests/ changed"), though it is tooling that `hooks-test` runs: both of 405 T138's landing gates on 2026-10-25 planned full for `tests/hooks/test-no-poll-hooks.sh`, merged from main by another session (10,085 tests, pytest 337-348 s) - treat the hooks tree as tooling in the planner, so T06 can be measured (found by 405 T106/T138, 2026-10-25)
      research: rendering
      verify: DONE. landed: fixed by feature 430 T02's planner (7d1ced680): test_a_hook_suite_keeps_the_gate_incremental pins tests/hooks/test-no-poll-hooks.sh planning incremental, red on the planner before 7d1ced680, green now; plan blocks CLEAR
- [ ] T07 Close: report and land
      research: rendering
- [ ] GM review (make gm-reviewed F=415)
