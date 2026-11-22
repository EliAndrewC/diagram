# Implementation check - feature 374 (feature 378)

`make impl-check F=374` names three questions this feature changed: 0190 is cited by a checked claim
(`rust/mode_a/src/audit/sun.rs::NOTICE_BOARD_FT`, IN-STEP); 0033 and 0075 by none. This file records why (written
2026-11-22, when 449's batch landing touched this feature's `measurements.json` and the push asked its implementation check).

- 0033: no code implements it - the row village's findings (the street laid first, farm spacing, one side or both, the
  leeward farms' bamboo to the south) were decided by the Python hamlet engine, deleted by feature 449 T158, and by its Rust
  port's `homesteads` (`rows.rs`, `row_seat.rs`, `level.rs`), `track` and `appurtenances` (`wells.rs`) stages, which cite
  0033 but are parked under `rust/parked/` (feature 444 amendment 11): nothing compiles, tests or claims them until the GM
  resumes the stage. Searched: `grep -rn "0033" rust/ --include=*.rs` (only `rust/parked/` and a claims-grammar test) and
  `make impl-check F=374`.
- 0075: no code implements it - a farm's bamboo strip (waves 149 and 153) is seated by the parked `homesteads` stage;
  the live `rust/phases` only rolls the `bamboo` knob's stream (`water_frame.rs`, `driver/plan.rs`), placing nothing.
  Searched: `grep -rn "0075\|bamboo" rust/ --include=*.rs`.
