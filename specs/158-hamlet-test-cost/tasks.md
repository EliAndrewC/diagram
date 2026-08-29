# Tasks: Cut the Cost of the Hamlet-Tier Test Suite (feature 158)

Every task here is `research: rendering`: this feature changes how the SUITE is run, never a claim
about how a place was built, farmed or lived in. The one judgment that looks physical - "does the
placer still guarantee this?" - is answered by READING the placer, which is code, not record.

The audit's own record is [`ledger.md`](ledger.md); the measurements are [`research.md`](research.md).

## Phase A - the audit

- [x] A01 baseline all three tiers, measured and recorded, plus the per-test duration profile of the gate tree and the full tree - `research.md` R1/R2
      research: rendering
- [x] A02 re-run `make check-census` on today's engine and write this feature's ledger (`ledger.json` / `ledger.md`): 154 names, 130 KEEP, 13 RETIRE-CANDIDATE, 10 NO-SCRIPTED-EXECUTOR, 1 VACUOUS
      research: rendering
- [x] A03 classify every `pool/regressions/` fixture - by declared tier AND by the `source` its own `_regression` block names, which is what actually says whether a generator alive today could produce it
      research: rendering

## Phase B - retire the checks the placer already guarantees

- [x] B01 the HAND PASS over every mechanical retire-candidate: read the placer, grep the record. Four candidates survived the reading as KEEPs the census had called candidates (the three kosatsuba checks, whose placer has an explicit "keep the engine's seat rather than none" fallback, and `bridges_span_their_water`, which `hamletgen/ways.py` records catching the scripted placer four times)
      research: rendering
- [x] B02 retire what survived: `bridges_align_with_their_way`, `bridges_seat_on_water`, `bridges_clear_of_houses` - 19 segments, their unit tests, their frozen fixtures, the check-name fixture and the frozen registry rows. Plus six segments that were ALREADY dead (Principle XIV). The cut was proved closed before it was made
      research: rendering
- [x] B03 record each retirement's disposition per FR-005 - `ledger.md` section 2
      research: rendering

## Phase C - the corpus

- [x] C01 delete every frozen fixture that is a hand-authored legacy-tier map - 26 of them; the corpus is 134 -> 104
      research: rendering
- [x] C02 delete every fixture whose only `fires` are checks this feature retired - 4 more
      research: rendering
- [x] C03 replace the proof of any KEPT check that lost its only fixture - `water_channels_obtuse_turns`, `field_ditches_terminate` (pointed at the POLDER: only the polder grid draws lateral ditches) and `paddy_fan_has_floor` now have scripted negative fixtures; and the full-gate coverage SENTINEL, which one of the deleted fixtures was doubling as, is now a real roll
      research: rendering

## Phase D - the cheapening

- [x] D01 coverage measurement mode - `COVERAGE_CORE=sysmon` MEASURED AND REJECTED: slower here than the C tracer (20.1 s against 16.2 s wall) on byte-identical coverage tables, and the premise behind it was a cold-cache artifact. `research.md` R5, `dev/lessons.md`
      research: rendering
- [x] D02 `test_the_fit_gives_a_saturated_best_aspect_the_full_search_it_was_denied`: a coarse plot grid, 1,985 plots -> 257. 39.2 s -> 8.1 s, with `make cov-file` proving the branch is still executed. The obvious lever (shrinking `plan.envelope`) was measured FIRST and rejected - it changes nothing at all
      research: rendering
- [x] D03 `test_a_saturated_aspect_stops_after_the_probe_instead_of_bisecting_a_fan_it_cannot_grow`: the same. 5.1-8.2 s -> 0.85 s
      research: rendering
- [x] D04 the 1-5 s tail: the linear-hamlet homestead test (10 households, the floor of the band), three `village_grove` tests (narrower bands, and the dike-bank one gained a precondition so the skip cannot pass for the wrong reason), the belt-vertex test (a smaller derived canvas) and the comb-hem fixture (a smaller canvas and a shorter fall)
      research: rendering
- [x] D05 what the re-profile turned up: the determinism ratchet rolls Kashikawa TWICE, not three times - the perturbed roll runs first, so the clean one leaves the committed manifest as it should be. 214 s -> ~143 s, the largest single item in the full tier. And `tests/tier_city/test_frozen_pool_gate.py` plus the five frozen-pool coverage carriers are deleted: hand-authored maps carrying a floor that stopped existing under feature 145
      research: rendering

## Phase E - close

- [x] E01 re-measure all three tiers; the before/after table is `ledger.md` section 1
      research: rendering
- [x] E02 `make done` green; every pool manifest byte-identical; the coverage floors judged
      research: rendering
- [x] E03 the bypass-log audit for this feature, and the run-log entry
      research: rendering
- [x] E04 push to main (the GM reviews after the fact - there is no acceptance task here, by the GM's own sequencing)
      research: rendering
