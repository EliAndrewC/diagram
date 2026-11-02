# waterfields/ - what the field's drawing and checks still read of the old water-first engine

The comb and the polder are laid in Rust since feature 444 T16 (`rust/phases/src/field/`, the `field` stage). T16 deleted the
Python engine they replaced - the comb's carve, partition, settle, tint, furrows and trunks, the polder builder, the ring rules and
the seam re-hold (plan D10: deleted in the landing where nothing outside the field path imports it). What stays is read by the ink,
the overlap and keep-out code and two gate checks. **Load only the file the task calls for.** `import waterfields` exposes the
consumed surface via `__init__.py` (star re-exports plus an aliased block for underscore names; guard:
`tests/waterfields/test_surface.py`) - never add logic to the `__init__`.

| file | look here when |
|---|---|
| `__init__.py` | the re-export mechanism and the engine's doctrine docstring; never logic |
| `frame.py` | the channel TAPER LAW (`taper_w` - width goes as the square root of the discharge), the ditch widths (`DRAIN_FT`) and their pixels (`chan_px`), when a ditch is worth a plank (`worth_planking`), `BANK_MARGIN` and the segment helpers the banks read |
| `banks.py` | a tapered channel cut one piece a segment (`taper_pieces`, the ink's and the keep-outs'), and the bank clearances and bends the drawing reads |
| `palette.py` | the colors (`_RICE_GREEN`, `FLOODED`, `RIPE_GOLD`, `BUND`, `AZE`, `BEAN_GREEN`), `aze_w`, `DRY_CROPS` |
| `twins.py` | TWO WATERCOURSES DO NOT RUN SIDE BY SIDE (feature 294 B4): the predicate the sink and a gate check read |
