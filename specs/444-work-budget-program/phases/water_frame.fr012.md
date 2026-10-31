# FR-012 for T19's port - a roll with the counters compiled out writes the same manifest (measured 2026-10-31)

Method: the crate built twice - with its `counters` feature (`rust_checks.py build`, into `.rust-ext/`) and without it (`maturin build
--release`, no features, into a scratch folder) - and each seed rolled with each (`make hamlet ARGS="--name Inashiro --seed <s>
--households <h> --out <path> --no-render"`, the counters-off module loaded through `L7R_RUST_EXT`), the two manifests compared with
`cmp`. On a probe call (`stage_water_frame(3, "NW", False, False, ["nucleated"], [("settlement_form", 1, False, "all")])`) the
counters-off build hands back a count of 0 and the counters-on build 11 - the 3 identity writes, the 6 bearings and the one-form
knob's 2.

```
seed 25 at 20: manifests identical
seed 39 at 10: manifests identical
seed 47 at 20: manifests identical
```
