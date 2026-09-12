# Plan - 228 The crop dike lights as a ring

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **I**: `settlement-review` on the regenerated Kuwabata before it ships (FR-005).
- **VI**: the unit test on the emitted bank path (FR-004), shown failing on the old emit (SC-002).
- **X**: one emit site in `landuse.py`; 100% coverage holds (every dike-pond map rolls it).
- **XII**: rendering, nothing physical; the convention recorded at the point of change.
- **XIII**: the manifest records and the checks are untouched (FR-003); baseline in a detached
  worktree if anything moves.
- **XVI**: spec-fidelity before code.
- **Route**: `landuse.py` is engine code -> GATED (LOCAL-GATED).

## Design

- `settlement/fields/landuse.py` `_landuse_draw_plot`: compute `bd` and `wd` as now (same order, same
  draws), then emit the bank as `<path d="{bd} {wd}" fill-rule="evenodd" ...>` with the why; the pond
  path unchanged.
- `tests/settlement/test_wet_ground.py`: beside the existing bank-is-planted-earth test, assert the
  bank path holds both outlines and the rule and the pond path holds the second alone.
- `settlements/` operative doc ('Polder fourth pass'): the bank is a ring, and why.
- `make map GEN=pool/hamlets/kuwabata/kuwabata.gen.py`; open the page; `make verify` (gate +
  settlement-review together); notes entry; land GATED.
