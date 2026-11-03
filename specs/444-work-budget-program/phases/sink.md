# Phase checklist - sink (feature 444)

Copy to `specs/444-work-budget-program/phases/<stage>.md` and tick each box, in order, as its step is done; each box carries
the evidence beside it (a path, a ledger row, a figure with its run). `make land` refuses a `phase: <stage>` task of feature 444
while this file is absent, short of any of the eight boxes, or holds one unticked (feature 443 FR-010). The steps are section 3 of
the design the GM approved on 2026-10-28 (`specs/443-work-budget-tooling/request.md`).

- [x] 1. **Contract.** What the phase reads from the manifest and what it writes; the research claims that govern it (from the
  claims index); the cohort properties it must keep.
  Evidence: `phases/sink_greenfield.derivation.md` ## Contract (reads, writes, keeps, bounds; revised for amendment 7); the claims governing it, 0060, 0061, 0054, 0067, 0068, held at the Rust that decides each (impl-drift rounds of 2026-11-03, recorded in `dev/claims-index.json`); the cohort properties: every seed of the Rust stage gate through the sink
- [x] 2. **Minimal algorithm.** Pseudocode and its operation count, factor by factor (S7), written from the contract alone,
  before the current code's numbers are read, in the derivation template (`.specify/templates/derivation.md`: each factor's
  scope, value, reason and worst case, and the cheaper algorithms considered), copied to `phases/<stage>.derivation.md`.
  Evidence: `phases/sink_greenfield.derivation.md` (greenfield, FR-015), revised under FR-022 rule 2 with `## Work the first derivation missed`: the ditch to the pond, the reeds' ring and ground, the outline and the brook read without the field's index, the registry filing
- [x] 3. **Budget review, MODE BUDGET.** The `work-budget` agent's SOUND on the derivation (`make work-budget-bundle MODE=budget`);
  the budget and exponent pinned (`make budget-set`).
  Evidence: SOUND on the first greenfield form (verdict-2, pinned 149 at 40); SOUND twice, blind (verdicts 3 and 4, ask:444-sink-round-7), raised to 239/291/380; the reeds' ground re-priced on the MODE AUDIT's finding (ask:444-sink-round-9) - see box 6
- [x] 4. **Today's measurement.** `make work-budget` for the stage - its ratio to budget and its exponent; the hot chains from
  `make perf-fanout`.
  Evidence: before the rebuild, `dev/work-budget/20261103T133422Z-8a72bd036ed1.json`: 173,537 at 40 (1,164.7x the 149), its cost the brook's re-filing (150,314 of seed 4's 167,264); `make perf-fanout STAGES=sink,field` (`dev/perf-log/20261103T153325Z-fanout-adhoc.txt`)
- [x] 5. **Rebuild.** Behind the manifest seam (`STAGES` in `driver.py`): the same input, the same output, no repair passes (S4);
  the old implementation deleted in the same landing, with no fallback path. The old Python owes no coverage on the way out (feature
  448, the GM 2026-11-02: "We can relax that for the engine code at this pooint since that's going away"): `dev/coverage-exempt.json` names it, so no test is added only to cover a line of it; the landing's
  `make coverage-exempt PRUNE=1` drops its entries once the stage is accepted, and the stage's thin door keeps the floor.
  Evidence: `rust/phases/src/sink/` and `rust/phases/src/course.rs` behind `hamletgen/sink_stage.py` (STAGES unchanged); the old `hamletgen/sink.py`, `water/brook_course.py`, `settlement/fields/outfall.py`, `Settlement.round_stream` and every unit only they reached deleted (`make dead-closure`), with their tests; no fallback path; the field's brook drawn where it is laid (D2), the walk after a Rust stage skipped (D3); FR-012 `phases/sink.fr012.md`
- [ ] 6. **Acceptance.** Basic operations at most the budget at 40 and 80 households - or at most twice it on the MODE AUDIT's
  LEEWAY, and work the derivation missed re-derived and raised (`make budget-set RAISE=1`), never squeezed (feature 444 FR-022) - and
  the exponent at most the budget's, with no leeway; every seed of
  the Rust stage gate passing where the Rust stages complete (`make rust-gate`, feature 444 FR-019; the whole-pipeline cohort a
  rate, refusing nothing); the phase's claims round IN-STEP, with no open claim finding in a file the landing changes (feature 444 FR-021, refused at `make land`); the reviews
  its occasions owe; `make perf-ab`'s time recorded, as a record and not a gate.
- [ ] 7. **Audit review, MODE AUDIT.** The `work-budget` agent's WITHIN, or LEEWAY, on the landed code (`make work-budget-bundle MODE=audit`).
- [ ] 8. **Standing record updated.** `dev/work-budget.md`, for this phase and for the whole roll; the stage accepted.
