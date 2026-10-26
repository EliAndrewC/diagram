# Research - feature 432

## R3 - the price of clearing triage-owed claims mechanically (T05, FR-005 a, D7)

- **Finding** (`m:triage-price`): over every commit that changed `dev/claims-index.json` from 2026-10-04 to 2026-10-26, a claim
  whose code stood and whose cited page moved was re-judged 6,419 times. In 5,304 the blocks it rests on stood (the TRIAGE
  route): 5,297 kept their verdict, and 7 became a finding - 4 DRIFTED, 3 MISLABELED, on 6 claims (a polder claim twice):
  `ways/bund.py::RUN_ON_REACH_FT`, `ways/geom.py::_trim_to_service`, `ways/settle.py::settle_street_ends`,
  `ways/sweeps.py::_sweep_dangling_ends`, `homesteads/wells.py::shared_row_wells`, `water/polder.py::polder_crossing_caps`.
  In 1,115 a rested-on block moved (the route D7 keeps): 66 became a finding.
- **So** the mechanical clearing would have let 7 findings in 5,304 through (0.13%) - about one finding in 760 triage-route
  re-checks, each a claim whose cited page gained a passage that bore on it without the passage it rests on changing - and
  saved the triage of all 5,304 (one agent per page edit, the 0081 edit's 217 claims among them).
- **Method**: `python3 specs/432-gm-review-signal/measure/triage_price.py` - each commit against its first parent, a claim's
  `code`, `pages` and `rests` compared; the triage route is `pages` changed with `rests` the same.
