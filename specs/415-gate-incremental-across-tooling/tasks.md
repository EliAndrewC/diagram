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
- [x] T04 The gate's fixed and per-test costs and the merged baseline's drift, measured on real landings (D7; FR-007)
      research: rendering
      verify: DONE. landed: research R2: one full and three incremental gate runs measured (67 s fixed + 12.7 ms per selected test, the selection 1,492 -> 2,657 between full runs); make gate-costs and its test
- [ ] T05 A landing runs what its change reaches; the baseline refreshed off the landing's path, on T04's numbers (D8; FR-006)
      research: rendering
- [ ] T06 A real engine landing after a tooling change measured end to end against T26's 8.8 minutes (D9; SC-006)
      research: rendering
- [ ] T07 Close: report and land
      research: rendering
- [ ] GM review (make gm-reviewed F=415)
