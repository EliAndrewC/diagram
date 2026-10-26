# Feature Specification: the field tie's distance asked only of the tied seats

**Created**: 2026-10-10

**Status**: Superseded by 427 - the GM folded it into feature 427 on 2026-10-26 ("Since feature 373 overlaps this, then I think we should just fold it into this feature", `specs/427-call-volume-refactors/request.md` 4); its finding is R8 of `specs/427-call-volume-refactors/research/hotspots-recompute.md`. Filed 2026-10-10 from feature 328's landing pair (its perf-audit, round 4).

**Affects**: hamlet, performance

`capacity.field_distances` (wave 20's seat-order tie toward the field, 81a14d318, vectorized 07ca65758) computes a ring
distance for every free grid point, but the seating uses it only to break ties within one grid pitch. At 40 households, seed
47, it is 0.166 s of the homesteads stage (`free_seats` 0.31 s at main, 0.51 s after it); stubbed, the stage returns to
main's time (feature 328's `measurements.json`, `landing-pair-40hh-field-tie`). Sketch: compute the distance only for the
candidates tied within the pitch; the roll must not change (a pool reroll diffed against HEAD's manifests shows it).
