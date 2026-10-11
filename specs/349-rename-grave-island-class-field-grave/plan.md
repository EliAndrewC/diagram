# Implementation Plan: Rename the `grave island` class to `field grave`

**Branch**: none (main, in the session clone) | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

## Summary

A key rename across the class's users, carried by the snapshot's renaming table; the two hamlets that draw a field grave
regenerated; no drawing changes.

## Decisions

- **D1 - the key and the class.** `water_and_ways.py`: `class FieldGrave(Kind): key = 'field grave'`; the engine's two
  drawers (`_plot_grave_island`, `_plot_corner_grave` in `settlement/fields/features.py`) tag their ink `field grave`.
- **D2 - the reader-facing data.** `place.json`'s collision key; `siblings.json`'s two pairs (the key, and "the grave island"
  in their text reworded to "the field grave", standing "on an island in a plot or in its corner"); the modal file moves
  to `assets/modals/hamlet/field-grave.md` (its stem is the key's slug) with `Name: field grave`, nothing else changed.
- **D3 - the snapshot.** `SINCE_189["grave island"] = ("field grave",)` in `tests/interactive/test_classes_docstrings.py`, as
  bathhouse -> bath room; the frozen snapshot is not edited (FR-004).
- **D4 - the maps.** Kashikawa and Mizuguchi regenerated (`make map`); Kashikawa's `ink_classes` and its notes' Features key
  (`- **field grave**:`) follow. Mizuguchi's notes mention "a grave island" only in its dated history, which stays.
- **D5 - the island form keeps its name** (FR-003): `grave_form=island`, its choice modal, `_plot_grave_island` and the
  glossary's term "grave island" (a word the prose uses for the form) are unchanged.
- **D6 - checks.** The claims the renamed units carry are re-checked by `impl-drift`; `modal-form` checks the renamed modal;
  the research and depiction checks are not re-run (spec, Decisions Recorded); the glyph-check `review_owed` names on
  Kashikawa is a class key new to the map over an unchanged glyph, answered with `PAIR_OK` / `REVIEW_GATE_OK` and its reason.

## Project Structure

```text
l7r/diagram/interactive/classes/water_and_ways.py, settlement/fields/features.py     D1
l7r/diagram/interactive/assets/{place,siblings}.json, modals/hamlet/field-grave.md   D2
tests/interactive/test_classes_docstrings.py, test_classes.py, test_place.py          D3
pool/hamlets/kashikawa/kashikawa.{json,notes.md}                                      D4
```
