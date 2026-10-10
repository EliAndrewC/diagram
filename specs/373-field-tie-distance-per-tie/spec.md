# Feature Specification: the field tie's distance asked only of the tied seats

**Created**: 2026-10-10

**Status**: Filed - found by feature 328's landing pair (its perf-audit, round 4, 2026-10-10); not requested by the GM, so
filed rather than carried in feature 372. Rewriting this into a full spec, a plan and tasks is the work of whoever picks it
up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

**Affects**: hamlet, performance

`capacity.field_distances` (wave 20's seat-order tie toward the field, 81a14d318, vectorized 07ca65758) computes a ring
distance for every free grid point, but the seating uses it only to break ties within one grid pitch. At 40 households, seed
47, it is 0.166 s of the homesteads stage (`free_seats` 0.31 s at main, 0.51 s after it); stubbed, the stage returns to
main's time (feature 328's `measurements.json`, `landing-pair-40hh-field-tie`). Sketch: compute the distance only for the
candidates tied within the pitch; the roll must not change (a pool reroll diffed against HEAD's manifests shows it).
