# Phase checklist - seat (feature 444)

Copy to `specs/444-work-budget-program/phases/<stage>.md` and tick each box, in order, as its step is done; each box carries
the evidence beside it (a path, a ledger row, a figure with its run). `make land` refuses a `phase: <stage>` task of feature 444
while this file is absent, short of any of the eight boxes, or holds one unticked (feature 443 FR-010). The steps are section 3 of
the design the GM approved on 2026-10-28 (`specs/443-work-budget-tooling/request.md`).

- [x] 1. **Contract.** What the phase reads from the manifest and what it writes; the research claims that govern it (from the
  claims index); the cohort properties it must keep.
  Evidence: `phases/seat_greenfield.derivation.md` ## Contract (reads, writes, keeps, bounds; revised 2026-11-04 for the hem after the seat, T28); the claims governing it - 0031, 0035, 0058, 0072, 0081 and the GM's ruling of 2026-08-28 - held at the Rust that decides each (`rust/phases/src/seat/`; impl-drift rounds of 2026-11-04, IN-STEP, recorded in `dev/claims-index.json`); the cohort properties: every seed of the Rust stage gate through the seat
- [x] 2. **Minimal algorithm.** Pseudocode and its operation count, factor by factor (S7), written from the contract alone,
  before the current code's numbers are read, in the derivation template (`.specify/templates/derivation.md`: each factor's
  scope, value, reason and worst case, and the cheaper algorithms considered), copied to `phases/<stage>.derivation.md`.
  Evidence: `phases/seat_greenfield.derivation.md` (greenfield, FR-015), revised under FR-022 rule 2 with `## Work the first derivation missed`: the candidates' refusals, the score's terms, the ladder, the dry way out, the fords and the crossing cost, the watercourses gathered, the indexes, the wet toe, the grown walls
- [x] 3. **Budget review, MODE BUDGET.** The `work-budget` agent's SOUND on the derivation (`make work-budget-bundle MODE=budget`);
  the budget and exponent pinned (`make budget-set`).
  Evidence: SOUND twice blind on the revision (`seat_greenfield.verdict-10.txt` and `-11.txt`, ask:444-seat-round-7): 28,082 / 40,741 / 60,754 at 20 / 40 / 80, exponent 0.56. NOT PINNED: the raise is past ten times the first figure (191 at 40), so it waits for the GM's words (`phases/gm-overages.md`); `dev/work-budget.json` holds the first budget meanwhile
- [x] 4. **Today's measurement.** `make work-budget` for the stage - its ratio to budget and its exponent; the hot chains from
  `make perf-fanout`.
  Evidence: `make work-budget` 2026-11-04 (`dev/work-budget.md`): 27,190 / 36,606 / 52,709 at 20 / 40 / 80, exponent 0.48, under the re-derived figure at every size (191.7x the first); `make perf-fanout STAGES=seat` (`dev/perf-log/20261104T151232Z-fanout-adhoc.txt`)
- [x] 5. **Rebuild.** Behind the manifest seam (`STAGES` in `driver.py`): the same input, the same output, no repair passes (S4);
  the old implementation deleted in the same landing, with no fallback path. The old Python owes no coverage on the way out (feature
  448, the GM 2026-11-02: "We can relax that for the engine code at this pooint since that's going away"): `dev/coverage-exempt.json` names it, so no test is added only to cover a line of it; the landing's
  `make coverage-exempt PRUNE=1` drops its entries once the stage is accepted, and the stage's thin door keeps the floor.
  Evidence: `rust/phases/src/seat/` (margins, exit, fords, index) behind `hamletgen/seat_stage.py` (STAGES unchanged); the old Python seat search (`seat_cluster`, `margin_candidates`, `back_fouled`, `belt_off_canvas`, `below_drain`, `nearest_within`, `track.stage_seat`) deleted with their tests (T27 D6); no fallback path; no repair pass
- [ ] 6. **Acceptance.** Basic operations at most the budget at 40 and 80 households - or at most twice it on the MODE AUDIT's
  LEEWAY, and work the derivation missed re-derived and raised (`make budget-set RAISE=1`), never squeezed (feature 444 FR-022) - and
  the exponent at most the budget's, with no leeway; every seed of
  the Rust stage gate passing where the Rust stages complete (`make rust-gate`, feature 444 FR-019; the whole-pipeline cohort a
  rate, refusing nothing); the phase's claims round IN-STEP, with no open claim finding in a file the landing changes (feature 444 FR-021, refused at `make land`); the reviews
  its occasions owe; `make perf-ab`'s time recorded, as a record and not a gate.
  Evidence: OPEN, held for the GM: the counted operations stand under the re-derived 40,741 / 60,754 but over the pinned first budget, and the raise is his to give (`phases/gm-overages.md`); otherwise met - `make rust-gate` 0 failing, the claims rounds IN-STEP on every file the delta changes (2026-11-04), no review owed (`make verify`: no occasion in the delta), `make perf-ab A=origin/main` seed 25 at 40: the seat 0.03 s to under 0.01
- [ ] 7. **Audit review, MODE AUDIT.** The `work-budget` agent's WITHIN, or LEEWAY, on the landed code (`make work-budget-bundle MODE=audit`).
  Evidence: pending: the MODE AUDIT of the landed code (round 2, after `seat.audit-1.txt`'s UNCOUNTED)
- [ ] 8. **Standing record updated.** `dev/work-budget.md`, for this phase and for the whole roll; the stage accepted.
  Evidence: pending the GM's ruling on the raise: then `make budget-change` and the stage's acceptance
