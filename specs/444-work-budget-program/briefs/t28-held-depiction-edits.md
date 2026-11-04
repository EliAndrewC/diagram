# Held - feature 444 T28, the crop pop-ups' Depiction edits that wait for the engine

Load this file when: T28's field change lands (the dry-field hem drawn behind the houses where the settlement stands on the
paddy's high edge).

modal-depiction (2026-11-04, Session C) found each of the four crop pop-ups' Depiction still says the hem lies just above
the supply canal everywhere, which 0006's drawing page no longer says. Today's engine still seats every dry plot from the
canal (`rust/phases/src/field/dry.rs` `hem`), so the tab matches the map as drawn; the check advised the edits land WITH
the engine change, not before. Apply this block to each of `l7r/diagram/interactive/assets/modals/hamlet/barley.md`,
`buckwheat.md`, `millet.md` and `soy.md` in the same commit as the field change, then re-run `make record-owed`:

    <<<
    each squared to the canal behind a bare bank.
    ===
    each squared to the canal behind a bare bank. Where the houses stand on that edge, the hem is drawn behind them instead, so the houses lie between the canal and their dry fields.
    >>>
