# Tasks: Cut the Cost of the Hamlet-Tier Test Suite (feature 158)

Every task here is `research: rendering`: this feature changes how the SUITE is run, never a claim
about how a place was built, farmed or lived in. The one judgment that looks physical - "does the
placer still guarantee this?" - is answered by READING the placer, which is code, not record.

## Phase A - the audit

- [ ] A01 baseline all three tiers, measured and recorded (`make quick ALL=1`, `make test`, `make test-full`), plus the per-test duration profile of the gate tree and the full tree
      research: rendering
- [ ] A02 re-run `make check-census` on today's engine and write this feature's ledger (`ledger.md` / `ledger.json`)
      research: rendering
- [ ] A03 classify every `pool/regressions/` fixture: tier, and whether a generator alive today can produce it
      research: rendering

## Phase B - retire the checks the placer already guarantees

- [ ] B01 the HAND PASS over every mechanical retire-candidate: read the placer and record whether it GUARANTEES the fact or does its best and falls back
      research: rendering
- [ ] B02 retire what survives the reading - segment function, check-name fixture entry, unit tests, scripted negative fixtures
      research: rendering
- [ ] B03 record each retirement's disposition (what carries the invariant now) per FR-005
      research: rendering

## Phase C - the corpus

- [ ] C01 delete every frozen fixture that is a hand-authored legacy-tier map
      research: rendering
- [ ] C02 delete every fixture whose only `fires` are checks this feature retired
      research: rendering
- [ ] C03 replace the proof of any KEPT check that lost its only fixture with a scripted negative fixture
      research: rendering

## Phase D - the cheapening

- [ ] D01 coverage measurement mode: `COVERAGE_CORE=sysmon`, with the coverage totals proved identical before and after
      research: rendering
- [ ] D02 `test_the_fit_gives_a_saturated_best_aspect_the_full_search_it_was_denied` (39 s): shrink the subject, keep the branch and both assertions
      research: rendering
- [ ] D03 `test_a_saturated_aspect_stops_after_the_probe_instead_of_bisecting_a_fan_it_cannot_grow` (5-8 s): the same
      research: rendering
- [ ] D04 the 1-5 s tail (the linear-hamlet homestead test, the three `village_grove` tests, the belt-vertex test): smaller subjects, each with the break demonstrated
      research: rendering
- [ ] D05 whatever the re-profiled durations turn up once D01-D04 land
      research: rendering

## Phase E - close

- [ ] E01 re-measure all three tiers; write the before/after table into the ledger
      research: rendering
- [ ] E02 `make done` green; every pool manifest byte-identical; the three coverage floors at or above their pre-feature values
      research: rendering
- [ ] E03 the bypass-log audit for this feature, and the run-log entry
      research: rendering
- [ ] E04 push to main (the GM reviews after the fact - there is no acceptance task here, by the GM's own sequencing)
      research: rendering
