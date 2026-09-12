# Research - 226 the site boundary, and the seats proposed from it

## R1 - the before (2026-09-12, the per-house profile in dev/performance.md)

| per house | inashiro | kuwabata | sawada |
|---|---|---|---|
| candidate seats proposed (`try_place`) | 3 | 10 | 2 |
| positions tested (`_fits_any_side`) | 419 | 1,686 | 363 |
| rectangles tested (`_rect_blocked`) | 1,090 | 2,755 | 848 |
| chord side tests (`chain_violated`) | 7,778 | 13,075 | 6,424 |
| hard-ground scans (`_hard_clear`) | 1,234 | 2,090 | 1,006 |
| rotated-corner gap tests (`poly_gap`) | 396 | 802 | 283 |

The stage: 1.0 / 2.3 / 2.3 s real (15 / 16 / 19 houses). What a rectangle is tested against: `block_polys`
(every dry hem plot, the pond's box, Kuwabata's pond mosaic), the paddy's chords (5 points), the water courses,
and the hard ground (every dry plot again, every marsh, every ditch segment as a quad - 29 + 114 + 2 on
Inashiro); then the standing houses by rotated-corner gap, the sun corridors, the treads and the bund-wall
corners. 24 of Inashiro's 39 proposed seats failed every one of the spiral's 181 offsets.

## R2 - the after

(filled at T05)
