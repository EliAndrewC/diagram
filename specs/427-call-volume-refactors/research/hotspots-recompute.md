# Hotspots: recomputing what did not change

**Load this file when:** you work on the wells, homestead seating's reach test, the free-ground components, the field's
fall transform or the crop boxes.

There are two shapes here:

- **re-score everything after each step**, where state could be kept and updated;
- **build a whole thing to answer a small question**.

Counts are Python-level calls, seed 39, at 20 households -> 40 (`fanout-2026-10-26.txt`). Paths are under `l7r/diagram/`.

## R1. Wells: every seat re-ranked against every household, per added well (the cubic term)

- **Chain:** `hamletgen/homesteads/wells.py:759 reach_wells` adds one well per round. Each round calls `seat_wells` (`:393`)
  or `seat_cluster` per form. Each of those calls `pool.sort(key=_key)` (`:654`) over the whole seat pool, and `_key` calls
  `most_served_after` (`:144`), a pure-Python `min` over the wells for every household.
- **Counts:**

| step | @20 | @40 |
|---|---|---|
| `SeatSweep.seats` (`well_seats.py:41`) | 6 | 11 |
| `most_served_after` | 4,071 | 15,594 |
| the lambda at `wells.py:151` | 244k | 2.19M (n^3.2) |

- **Legality, checked per candidate seat:** `settlement/shrines_wells/wells.py:33 well_gap_to_dwellings` 19.6k -> 79k ->
  `_geom/overlap.py:82 point_quad_dist` 104k -> `seg_dist` 235k -> 965k.
- **Also per candidate:** `_worst_after` / `worst_after` (`:166`) and `_extent_added` (`:621`) -> `drawn_r` -> `_well_vr` ->
  `houses._toscale` 53k (n^2.2).
- **Wall time:** 0.35 s at 20 and 4.58 s at 40 (median). It is heavily seed-dependent (`measurements.md`).
- **Direction:**
  - Find and admit the candidate seats once per form.
  - Hold a households-by-seats distance array (numpy) and each household's current nearest-well distance; a new well
    updates it with one `np.minimum`.
  - Score every seat by broadcasting ("worst-served after a well here", "busiest well after a well here"), then admit only
    the winner through the registry.
  - `well_seats.py` already vectorizes part of this (`SeatSweep.dist`, `PairAhead.keeps_ten`), so extend that pattern; do
    not start over.
- **Expected:** removes the n^3 term and the slow tail (worst seed 23.8 s -> about 14 s). It does little for the median or
  for 15-20 households.

## R2. Crop boxes: every windbreak clump against every house, on every call

- **Where:** `settlement/_knobs.py:719 crop_boxes`, the expression at `:827`. It runs
  `any((cx-hx)**2+(cy-hy)**2 <= reach**2 for h in houses)` for every clump of every windbreak grove.
- **Counts:** called 6 -> 21 times; the generator runs 20.6k -> 122k (n^2.6).
- **Direction:**
  - Compute the shelter-of-a-house set once per (houses, groves) state, or with one numpy distance matrix.
  - Ask why the crop is recomputed 21 times. It is called from several stages, so cache it on the manifest version.

## R3. `free_seats`: every grid point against every house

- **Where:** `hamletgen/homesteads/capacity.py:68 free_seats` -> `_near_a_house` (`:52`), an `any(math.hypot(...))` over all
  houses per grid point. It sits behind `boundary.point_taken` (`boundary.py:401`, a set lookup), 41k -> 82k.
- **Direction:** one vectorized distance-to-nearest-house over the grid (numpy, or `shapely.dwithin` on arrays).

## R4. `household_reach`: four whole homesteads laid out to measure one candidate

- **Chain:** `hamletgen/homesteads/growth.py:146 settled_seat` (116 -> 267) -> `reach_at` (`:402`) -> `household_reach` (`:176`,
  253 -> 416) -> `settlement/rolling/bundle.py:73 _bundle_envelope`. That builds `_bundle_geom` for each of the four garden
  sides (`_NUC_SIDES`): 1,344 -> 2,506 builds.
- **What it reaches:** `_bundle_layout` -> `_lay_fixtures` -> `homestead_parts/fixture_seats.py:354 lay_fixtures` (776 -> 1,216,
  about 30 per household) -> `_first` (`:643`) -> `within_reach_of` 44k -> 73k -> `core.px` 116k -> 204k.
- **Note:** `_bundle_geom`'s docstring says the unraked layout is "built once per household and size". The fixture layout
  under it still runs about 30 times per household, so check what the memo actually keys on.
- **Direction:**
  - Cache the four-sided envelope per (household lot, house size) relative to the house center, and move or rotate it to the seat.
  - Lay fixtures only for the configuration actually chosen.

## R5. `free_components`: the free ground relabeled once per house

- **Where:** `hamletgen/homesteads/region.py:302 free_components`, called 20 -> 40 times (once per seated house). Each call is
  a whole-grid run-length union-find, about 19 ms at 40 households.
- **Direction:** after a house is seated, relabel only the window its envelope touched, or keep the union-find live and
  split components locally.
- **Same family:** the one-off `rolling/gap_ways.py:201 flood` (0.38 s profiled, 1 call).

## R6. Field `_falls`: every vertex re-transformed on each lookup

- **Chain:** `waterfields/partition.py:187 grid_lines` (6 -> 8) -> `edge` (`:225`) -> `bound` (`:149`) -> `carve._bnd` ->
  `frame._at_f` (`frame.py:291`) -> `_falls` (`:285`, 4.7k -> 15.6k) -> `_Frame.to_uf` (`:242`), 161k -> 514k.
- **Note:** `_falls`' docstring says the per-carve cache "went with feature 302, and nothing asks it often enough now to want
  the cache". The measurement contradicts that.
- **Direction:** cache the falls per polyline for the length of a `grid_lines` call, or compute them as one numpy dot product.

## R7. Field settle: every added cell judged by the full ring rules

- **Chain:** `waterfields/settle.py:170 Fabric.__init__` calls `add` (`:191`) once per cell (633 -> 1,228). Each `add` calls
  `judge` -> `verdict` -> `waterfields/ring_rules.py:476 ring_violations` (788 -> 1,416) -> `collector_crossings` (`:354`) ->
  the genexpr at `:375` (19.7k -> 67k) -> `_seg_dist` (`:342`, 18k -> 63k).
- **Direction:** test a new cell only against the collectors near it, using the STRtree the fabric already builds (`:182`).

## R8. Field-tie distances computed for every free grid point (folded in from feature 373)

Feature 373, filed 2026-10-10 from feature 328's landing pair and folded in here by the GM on 2026-10-26 (`request.md` 4), said:

- `capacity.field_distances` (wave 20's seat-order tie toward the field, 81a14d318, vectorized 07ca65758) computes a ring
  distance for every free grid point, though the seating uses it only to break ties within one grid pitch;
- at 40 households, seed 47, it was 0.166 s of the homesteads stage (`free_seats` 0.31 s at main, 0.51 s after it);
- stubbed, the stage returned to main's time (feature 328's `measurements.json`, `landing-pair-40hh-field-tie`).

- **Direction (373's sketch):** compute the distance only for the candidates tied within the pitch.
- **Check:** 373 also said "the roll must not change (a pool reroll diffed against HEAD's manifests shows it)". This
  feature's rule is the GM's speed rule (maps may change, research held), but this change should be output-neutral, so
  the diff is a cheap check that it is.
- **Re-measure first:** it did not appear in the 2026-10-26 survey's chains at seed 39, because it is one vectorized call,
  not a multiplier. Time it on seed 47 at 40 households before sizing it.
