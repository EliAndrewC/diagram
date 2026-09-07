# Plan - 203 The placard stays on top

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **VI**: a browser test on the real Kuwabata page asserts the pixels (FR-004); SC-002 shows it fires.
- **X**: one attribute in `finish.py`, one selector change in `page.css`; 100% coverage holds (the
  scale bar is emitted on every hamlet the gate rolls).
- **XIII**: the vector page is untouched; feature 200/201's guards stay in the gate.
- **XVI**: spec-fidelity before code.
- **Route**: `finish.py` is engine code -> GATED (LOCAL-GATED).

## Design

- `settlement/finish.py`: the scale bar's `<g stroke=...>` becomes `<g class="scale" stroke=...>`, with
  the why beside the existing "keeps cls='-'" comment.
- `assets/page.css`: the leaf rule gains `:not(g.f-place *):not(g.scale *)`, with the why.
- `tests/full/interactive/page_browser/test_speed.py`: one test (FR-004); `tests/settlement/` gains
  the marker assertion beside the placard's existing tests.
