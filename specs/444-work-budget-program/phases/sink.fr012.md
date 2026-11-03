# FR-012 for T26's port - a roll with the counters compiled out writes the same manifest (measured 2026-11-03)

Method, as T16's (`phases/field.fr012.md`): the crate built twice - with its `counters` feature (`rust_checks.py build`, into
`.rust-ext/`) and without it (`maturin build --release`, no features, into a scratch folder) - and each seed rolled with each
(`make hamlet ARGS="--name Audit-<s> --seed <s> --households <h> --out <path> --no-render"`, the counters-off module loaded
through `L7R_RUST_EXT`), the two manifests compared with `cmp`. The sink (`stage_sink`), the field with its brook drawn
(`stage_field`, T26 D2) and the knobs all run through the extension on these rolls; the seeds cover each branch the sink takes.

```
seed 1 at 17 (a pond): manifests identical
seed 2 at 13 (the drain joining the brook): manifests identical
seed 8 at 11 (the drain joining the brook): manifests identical
seed 3 at 20 (a run off the map): manifests identical
seed 6 at 19 (a run off the map): manifests identical
```

Seed 4 at 16 refused in the seat (`SeatRefused`) on both builds alike, a later Python stage on a moved map (amendment 5); it
writes no manifest to compare.
