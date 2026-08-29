# Tasks: The paddy is not four to six inches deep

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Phase 0 - research

- [x] T1 The `source-reader` pass on the maintained water depth, its staging, and whether
  `tabayashi-1986` supports either.
  research: physical
  - [x] research pass - dispatched 2026-08-29 with the failed host from the previous pass excluded
  - [x] source-reader confirmed - MAFF and Zennoh READ with verbatim quotes (2-3 cm maintained;
    3-4 cm at rooting; 10/20 cm only as cold contingency; 中干し drain to cracking); Tabayashi 1986
    CONTRADICTED as a citation for depth; no pre-modern figure found
  - [x] recorded and cited - `research/fields.md` entry + two `SOURCES.md` keys + the queue closed

## Phase 1 - the correction

- [x] T2 The seven live sites: `classes.py` `paddy.what` and the four sibling texts, the
  `waterfields/seams.py` docstring, and the aze finding in `research/fields.md`.
  research: physical
  - [x] research pass - the 2026-08-29 pass; the record answers it
  - [x] source-reader confirmed - MAFF and Zennoh READ; the old claim CONTRADICTED
  - [x] recorded and cited - `research/fields.md` 'How deep the water actually stands'

- [x] T3 The provenance disclosure: `paddy`'s `label_note` and `caveat`, and `paddy` off the
  no-caveat list in `tests/interactive/test_classes.py`. Drop `tabayashi-1986` from the class's
  depth sourcing; register `maff-suitou-mizu` and `zennoh-mizukanri`.
  research: rendering

- [x] T4 Regenerate the reference hamlet and read the corrected modal on the page.
  research: rendering

- [x] T5 FR-007 (constitution XIV): the same wrong shape without the number, in
  `check_village/segments_04a_margins_lanes_and_wells.py` - found by spec-fidelity outside the scope
  it was given. Comment corrected; the check (no wellhead in a paddy) is untouched and still fires.
  research: physical
  - [x] research pass - the same 2026-08-29 pass covers it; it is the same claim without the number
  - [x] source-reader confirmed - the mid-season drain is READ (MAFF, 中干し to cracking)
  - [x] recorded and cited - the comment now names the drain and points at feature 160

## Phase 2 - verification

- [x] T6 `make done`, and SC-001's grep proving no live text asserts the number.
  research: procedure

- [x] T7 Stop-work: commit, `scripts/sync-with-main.sh done`.
  research: procedure
