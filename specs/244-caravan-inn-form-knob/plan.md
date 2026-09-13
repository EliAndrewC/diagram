# Plan - feature 244, the caravan inn's form is a knob

Spec: [`spec.md`](spec.md) (FAITHFUL, round 2). Research: [`research.md`](research.md).

## Constitution check

- **Engine code has a spec-kit feature** - this is it; `_knobs.py` and `lodging.py` are engine, so the
  delta routes GATED and lands on a green `make done`.
- **Two supportable answers become a knob** (XII) - the whole feature; the knob is rolled per settlement
  from the seed, never chosen.
- **100% coverage, the day it lands** (X.5) - the new branches in `inn()` and the registration are
  reached by the tests in phase 1.
- **No known regressions** (XIII) - no live pool map draws an inn, so no manifest moves; the frozen
  legacy renders are never regenerated; the gate's pool phase is the measurement.
- **Record the why at the point of change** - the registration comment, the docstring and the research
  page, per spec FR-001, FR-005, FR-003/FR-004.
- **Files at human scale** - `lodging.py` and `_knobs.py` stay far under 1,000 lines.
- **Overlap checks in their efficient form** (X.15) - none added; the glyph places exactly as before.

## Phases

**Phase 1 - the knob and the glyph** (`research: physical`; the research pass is 238 R2/R2a and 244 R1).
Register `caravan_inn_form` beside `byre_form`, with its why-comment. `inn(form=None)`: a passed form
is validated against the knob's value space and used; none resolves the knob. Draw the `hatago` second
story as an eave band and an upper row of the lattice windows - the shape the glyph carried before
2026-09-12, now the correct drawing of its own analogue rather than a mistake on the other. Write the
form to `M["meta"]["caravan_inn_form"]` and the building record. Tests in
`tests/settlement/test_civic_grounds.py`: each form pinned and its SVG asserted, the record and meta,
the refusal, two unpinned seeds resolving differently; and the knob's row in `tests/settlement/test_knobs.py`
if that file enumerates knobs.

**Phase 2 - the record.** `research/towns.html`, the caravan-inn section: the ruling replaces the
open-question sentence and the Evidence comment's line; both forms stated accurate to their analogues;
the umayado leg at the strength R1 bears, footnoted fn-30 from a new registry key `kotobank-umayado`
(Seisenban Nihon Kokugo Daijiten, s.v. 馬宿, at kotobank; both write-ups); the form rule as a
`<p class="spec">`. `make citations`. The docstring per FR-005.

**Phase 3 - the checks.** `source-applicability` on `kotobank-umayado` BEFORE its passage is relied on
in the section (spec FR-006; the physical task's fifth box); `quote-check` and `record-format` on the
changed section; `scripts/_entry_owed.py`.

**Phase 4 - the gate and the push.** `make done`; `sync-with-main.sh done`. This delta also carries
242's accepted amendment, which could not land alone.

## Decisions this plan makes that the spec left open

- **The `hatago` drawing reuses the pre-2026-09-12 upper-story shape.** The spec asks only that a second
  story "reads as one at map scale"; the eave band plus upper windows is the shape the glyph already had
  and that no reader mistook for anything else. Nothing narrower than the spec.
- **`test_knobs.py` is checked for an enumeration** rather than assumed to have one; if it enumerates
  registered knobs by name, the new knob gets its row there, else phase 1's tests are the whole of it.
