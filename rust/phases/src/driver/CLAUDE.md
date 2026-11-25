# `driver/` - a pool hamlet rolled through the Rust stages with no Python (feature 444 T42)

`make hamlet SPEC=pool/hamlets/<name>/<name>.spec.json` runs `src/bin/hamlet.rs`, which calls `driver::roll` and writes
`<name>.driver.svg` and `<name>.driver.json` beside the spec. What each stage is handed, and what the deleted Python drew, is
`specs/444-work-budget-program/t42-brief.md`. `make work-budget` runs `hamlet --budget` built with the counters: the reference
hamlet at 10/20/40/80 households, each stage's operations (`Rolled::by_stage`, `driver::ops`) set against `dev/work-budget.json`
by `l7r-gate measure work-budget`.

| file | look here when |
|---|---|
| `../driver.rs` | the comb's stages in order (water frame, field, sink, seat, dry hem), a roll a stage refused handed back as an error, no map (`whole`) |
| `polder.rs` | a polder archetype: the block, its seat and its waterside reeds, and their drawing |
| `polder/tests.rs` | the polder's tests: the sluices, the strips off the cuts, the seat's ring, ground and landward shore, the bank bands |
| `plan.rs` | the canvas, the fall and the water frame's 21 knobs, a dike-pond's forms - what `plan_site` resolved |
| `spec.rs` | a spec's fields and its JSON reader |
| `svg.rs` | the SVG writer: the palette, the crop, tapered ditches, furrowed dry plots, the dike's band; the ink census, each mark counted under the registry kind `Svg::kind` names (449 T230) |
| `toe.rs` | the wet toe below the field and a ring grown by the lane's width, the seat's inputs |
| `record.rs` | the JSON record, its `ink_classes` the census the review owed lookup reads as a hamlet's legend (449 T230) |
| `check.rs` | the finished map's checks - dry plots off the paddy, the water, the settlement's ground, the reeds and each other, each held to a plot's size (449 T433-T435), the tameike's water off the paddy, the houses' band off the field or the polder, a polder's reed strips off its block, each asked by its whole area (449 T435), a polder's settlement off its dike and ring canal with a dry way out past its reeds, all on the canvas; `make cohort` fails a seed that breaks one |
| `check/tests.rs` | the checks' tests: each check's red cases built by hand, a plot, pond, band or strip lapping past the slack or within it (449 T433-T435) |
| `tests.rs` | the rolls end to end: a comb and the polders, the record, every mark a registry kind |
