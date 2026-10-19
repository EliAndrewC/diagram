# Implementation Plan: Earlier rounds to the record checks

**Branch**: none (main, in the clone) | **Date**: 2026-10-18 | **Spec**: `spec.md`

## Summary

One new read-only module, `scripts/record/earlier_rounds.py`, builds a MANIFEST's `## Earlier rounds (feature 393)` section
from the check state and the arbiter's rulings, reusing `scripts/reviews/arbiter_bundle.py`'s readers (`reply_of`,
`mark_rounds`, `last_edits`, `subject_files`); `check_bundle.py` and `modal_bundle.py` append it to every MANIFEST they write
for a page check; one shared paragraph in the ten receiving agent files says what a round does with it.

## Technical Context

Python 3 tooling under `scripts/`; tests under `tests/tooling/` (the gate and the full run, never quick - they build git trees
in tmp). No engine code (`l7r/`, `pool/`): the landing route is DIRECT. No map changes; no research rendering decision.

## Performance bookends

None taken: no engine code and no roll. A bundle with earlier rounds reads the state file once and each earlier reply once;
a first round reads nothing new (FR-005).

## Constitution Check

- I-IX, XI: N/A - no UI, no pool content, no in-world prose, no kanji.
- X: PASS - ruff and format on the tests; a red-green test per requirement (`tests/tooling/test_earlier_rounds.py`).
- XII: PASS - no rendering decision; the tasks are `research: rendering` (tooling).
- XIII: PASS - SC-002 holds every first-round bundle byte-identical.
- XIV: no defect found in passing.
- XVI: PASS - the literal reading is the spec's "What it is".

## Decisions

- **D1 - one builder, reading through the arbiter bundle's readers (FR-001, FR-004).** `earlier_rounds.section(root, out,
  manifest)` takes the checks from the MANIFEST's `owed-checks:` line (only `hm_checks.PAGE_CHECKS`: no other check has a
  subject in the state) and the subjects from its `unit:` lines (`hm_checks.subjects_of_manifest`), the same reading the
  dispatch guard makes, so the rounds handed over are the ones the round counter counts on. Each round's verdict is
  `event_log.verdict_of`, its findings `mark_rounds` (NEW / REPEATED / REVERSING, another check's EDITs on the subject as
  earlier fixes), its EDITs `last_edits` against `subject_files`. Reusing them keeps the arbiter and a later round reading
  one account of the rounds; a second reader would drift.
- **D2 - the rounds of the ACTIVE feature only.** The state keeps dispatches across features (`hm_checks.main`: a new feature
  resets only the counts), so a round is handed over only when its `t` is at or after the first commit of the active
  feature's `spec.md` (`hm_arbiter.feature_dir`, which honors a page session's own feature). Unknown -> every round kept.
  Why: an earlier feature's round on the same page judged another change, and its findings would read as settled ones.
- **D3 - a returned or answered round only.** A `pending` or `running` dispatch has no verdict yet; it is no earlier round.
- **D4 - note-scoped bundles, ready for the Money session's field.** Where a dispatch records `notes` (the Money session's
  planned round-key fix adds it; a list, [] for the whole page), a note-scoped bundle gets only the rounds that read one of
  its notes or the whole page. Without the field every round on the page is handed over - more than needed, never less.
- **D5 - the replies beside the MANIFEST, a summary in it (FR-005).** Each round's whole reply is copied to
  `earlier/<check>-<subject>-round-<n>.md`; the MANIFEST holds the verdict, the marked findings and the edit marks, and the
  rulings. The bundler's `fresh()` clears `earlier/` with the rest of an old bundle.
- **D6 - the rulings (FR-002).** `hm_arbiter.rulings(root)` filtered to `round:<check>|<subject>@`, in round order, each with
  its `ruling`, `why` and, where present, `what`.
- **D7 - where it is appended.** `check_bundle.with_earlier` wraps the question, key and intro bundles' MANIFEST writes; the
  keys bundle is `source-applicability`'s alone and is left as it is (no subject - spec, Out of scope). `modal_bundle` appends
  it to each pop-up's MANIFEST, and the batched top MANIFEST names the pop-ups whose own MANIFEST carries one.
- **D8 - the contract paragraph (FR-003).** One paragraph, `**Earlier rounds (feature 393).**`, the same words in the ten
  receiving agent files, placed before their second section so it is read before the artifact; a test holds the ten equal.
  Agent files are the cached prefix every dispatch shares (feature 383 R16), so the paragraph costs once per agent type, not
  per dispatch.

## Tasks

T01 the module and the two bundlers (D1-D7); T02 the contract paragraph (D8); T03 tests, gate and landing.
