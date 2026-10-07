# Tasks: the implementation brought to the research, easiest first (feature 328)

**Input**: plan.md (Phase 1, Phase 2, D1-D4). Only the CURRENT wave's rows are task boxes (spec FR-006); the rest of the
ranking is data in `ranking.json` / `ranking.md`, and the next wave is appended here as an amendment once this one lands.

## Occasions

- none: wave 1 changes `Research:` claim lines only (tier E0) - nothing a map draws or where it is placed moves.

## Phase 1 - the audit

- [ ] T01 the findings snapshot: `findings.json` = every finding of `make claims-report` at `a52ff1bcd` (565) (FR-001)
      research: rendering
      verify:
- [ ] T02 the nine ranking batches, one Opus agent each, read-only, from `ranking-brief.md`; every finding tiered E0-E4 with its fix, files and dependencies (FR-002, FR-003)
      research: rendering
      verify:
- [ ] T03 the merge: `ranking.json` in tier order (by module within a tier, dependencies after what they wait on), `ranking.md` generated; E0 rows outside the bounded E0 re-tiered; `tests/test_328_ranking.py` green (FR-001, SC-001)
      research: rendering
      verify:
- [ ] T04 the second reader: 30 rows sampled across tiers re-tiered blind by a fresh Opus reader; a batch disagreeing by more than one tier on more than 5 rows is re-run (plan D4)
      research: rendering
      verify:

## Phase 2 - wave 1 (tier E0: the claim alone)

- [ ] T05 every E0 row's claim corrected to what the implementation already matches, module by module; `make claims-owed` lists them; each re-checked by `impl-drift` from `make claims-bundle` and recorded with `make claims-checked`; every one IN-STEP (FR-004, FR-005, SC-002)
      research: rendering
      verify:
- [ ] T06 the wave's close: `make claims-report` shows the E0 rows gone and no new finding; `make done` green; `ranking.json` rows marked wave 1; landed (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify:
