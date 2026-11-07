# `driver/` - a pool hamlet rolled through the Rust stages with no Python (feature 444 T42)

`make hamlet SPEC=pool/hamlets/<name>/<name>.spec.json` runs `src/bin/hamlet.rs`, which calls `driver::roll` and writes
`<name>.driver.svg` and `<name>.driver.json` beside the spec. What each stage is handed, and what the deleted Python drew, is
`specs/444-work-budget-program/t42-brief.md`. `make work-budget` runs `hamlet --budget` built with the counters: the reference
hamlet at 10/20/40/80 households, each stage's operations (`Rolled::by_stage`, `driver::ops`) set against `dev/work-budget.json`
by `scripts/measure/work_budget_rust.py`.

| file | look here when |
|---|---|
| `../driver.rs` | the comb's stages in order (water frame, field, sink, seat, dry hem), a stage's refusal kept in the record |
| `polder.rs` | a polder archetype: the block, its seat and its waterside reeds, and their drawing |
| `plan.rs` | the canvas, the fall and the water frame's 21 knobs, a dike-pond's forms - what `plan_site` resolved |
| `spec.rs` | a spec's fields and its JSON reader |
| `svg.rs` | the SVG writer: the palette, the crop, tapered ditches, furrowed dry plots, the dike's band |
| `toe.rs` | the wet toe below the field and a ring grown by the lane's width, the seat's inputs |
| `record.rs` | the JSON record |
| `check.rs` | the finished map's checks - dry plots off the paddy, the water and each other, the tameike off the paddy, the seat off the field, all on the canvas; `make cohort` fails a seed that breaks one |
