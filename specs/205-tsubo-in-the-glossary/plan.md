# Plan - 205 tsubo in the glossary

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **VI**: the existing glossary test covers the entry the moment it lands; one unit test on
  `glossary_for` for the positive and negative case (FR-004); the page regenerated and opened (SC-001).
- **X**: one dict entry in `glossary.py`; 100% coverage holds (data, not branches).
- **XII**: the definition is written from the record, with the pointer (D1); nothing is guessed.
- **XIII**: no other entry, explanation or asset changes (FR-003).
- **XVI**: spec-fidelity before code.
- **Route**: `glossary.py` is engine Python -> GATED (LOCAL-GATED).

## Design

- `interactive/glossary.py`: the `tsubo` entry, placed after `hem` beside the other measures of the
  farmstead's ground, with the record pointer in the entry's neighborhood comment.
- `tests/interactive/test_page.py`: one test beside `test_the_glossary_is_well_formed_and_used` -
  `glossary_for` over an explanation that says "18 tsubo" returns the entry; over one that does not,
  it does not.
