# FR-012 for T16's port - a roll with the counters compiled out writes the same manifest (measured 2026-10-31)

Method, as T19's (`phases/water_frame.fr012.md`): the crate built twice - with its `counters` feature (`rust_checks.py build`, into
`.rust-ext/`) and without it (`maturin build --release`, no features, cargo on the path, into a scratch folder) - and each seed
rolled with each (`make hamlet ARGS="--name <name> --seed <s> --households <h> [--archetype <a>] --out <path> --no-render"`, the
counters-off module loaded through `L7R_RUST_EXT`), the two manifests compared with `cmp`. The comb (`stage_field`), the polder
(`stage_polder`), the knobs (`roll_knob`) and finish's bead settling (`settle_runs`) all run through the extension on these rolls.

```
seed 39 at 10 (valley paddy): manifests identical
seed 47 at 20 (valley paddy): manifests identical
seed 26 at 20 (valley paddy): manifests identical
seed 4 at 15 (polder_grid): manifests identical
seed 21 at 16 (mulberry_dike_fishpond, Kuwabata's spec): manifests identical
```

Seed 25 at 20 refused in the sink on both builds alike (`SinkRefused`: the drain's constructed route lies where the overlap matrix
forbids it), and seed 4 at 16 on the dike-pond in the web (`WebRefused`), each a later Python stage on a moved map (amendment 5);
neither writes a manifest to compare, so both were replaced by the seeds above.
