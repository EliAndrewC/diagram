# Tasks: the implementation brought to the research, easiest first (feature 328)

**Input**: plan.md (Phase 1, Phase 2, D1-D4). Only the CURRENT wave's rows are task boxes (spec FR-006); the rest of the
ranking is data in `ranking.json` / `ranking.md`, and the next wave is appended here as an amendment once this one lands.

## Occasions

- none: wave 1 changes `Research:` claim lines only (tier E0) - nothing a map draws or where it is placed moves.

## Phase 1 - the audit

- [x] T01 the findings snapshot: `findings.json` = every finding of `make claims-report` at `a52ff1bcd` (565) (FR-001)
      research: rendering
      verify: DONE. findings.json: 565 findings (DRIFTED 439, MISLABELED 50, UNCLAIMED 36, NEEDS-RESEARCH 20, CANNOT-TELL 20) from dev/claims-index.json at a52ff1bcd
- [x] T02 the nine ranking batches, one Opus agent each, read-only, from `ranking-brief.md`; every finding tiered E0-E4 with its fix, files and dependencies (FR-002, FR-003)
      research: rendering
      verify: DONE. nine Opus batches (47-76 rows) returned 565 rows, each once (merge.py checked missing/extra = 0); 26 flagged deviation-tempting
- [x] T03 the merge: `ranking.json` in tier order (by module within a tier, dependencies after what they wait on), `ranking.md` generated; E0 rows outside the bounded E0 re-tiered; `tests/test_328_ranking.py` green (FR-001, SC-001)
      research: rendering
      verify: DONE. ranking.json 565 rows: E0 60, E1 162, E2 169, E3 136, E4 38; 30 flagged deviation-tempting. The 30 E0 rows tiered on the unbounded wording re-checked bounded (audit/e0review-out.jsonl): 23 stay E0 with a quoted e0_basis, 7 re-tiered; the shops-face-the-street row moved to E3 (its basis was a recorded DEVIATION, FR-004). Reproducible: python3 audit/merge.py audit . ; tests/test_328_ranking.py 2 passed
- [x] T04 the second reader: 30 rows sampled across tiers re-tiered blind by a fresh Opus reader; a batch disagreeing by more than one tier on more than 5 rows is re-run (plan D4)
      research: rendering
      verify: DONE. 30 rows (6 per tier, seed 328) re-tiered blind: 25/30 exact; 4 off by more than one tier (batches 8, 8, 5, 9) - no batch over 5, so none re-run (plan D4); for the 2 where the second reader ranked higher, the higher taken (audit/overrides.json)

## Phase 2 - wave 1 (tier E0: the claim alone)

- [x] T05 every E0 row's claim corrected to what the implementation already matches, module by module; `make claims-owed` lists them; each re-checked by `impl-drift` from `make claims-bundle` and recorded with `make claims-checked`; every one IN-STEP (FR-004, FR-005, SC-002)
      research: rendering
      verify: DONE. 56 of 57 E0 rows closed IN-STEP by impl-drift (audit/waves.json, from the claims index); 3 rows moved down when the re-check found a code mismatch (the rank step, the merchant kura, the universal shrine sheet - audit/overrides.json); three rounds of claim corrections (113 + 46 + 12 + 1 claims re-checked, bundles 1-8); 15 found rows added (audit/found-wave1.jsonl). Findings 565 -> 523.
- [ ] T06 the wave's close: `make claims-report` shows the E0 rows gone and no new finding; `make done` green; `ranking.json` rows marked wave 1; landed (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify:
