# Research - feature 298, tiled ground cover

All entries here are measurements of the engine's own output (rendering), not physical research.

## R1. What fills the SVGs (observed 2026-10-01, method: a census of the pool SVGs by stroke color and enclosing group)

| map (observed 2026-10-01, method: the census) | SVG | grass blades (`#A7A860`) | marsh reeds (`#6E9377`) |
|---|---|---|---|
| Kashikawa | 7.3 MB | 59.3% | 6.4% |
| Inashiro | 4.6 MB | 50.2% | 12.4% |
| Sawada | 3.4 MB | 24.5% | 30.0% |
| Kuwabata | 2.9 MB | 16.1% | 10.9% |
| Mizuguchi | 4.4 MB | 49.6% | 18.1% |

The brush dots (`#94A063` circles; observed 2026-10-01, method: the census) are another 8.9% of Kashikawa's. Stripping the blade and reed groups took Kashikawa's SVG 7.3 ->
2.5 MB and its PNG 8.2 -> 5.3 MB, and resvg's render of it 0.62-0.71 s -> 0.54-0.56 s (two runs each). The page (20.5 MB) carries
4.8 MB of the blade and reed groups as vector ink, and a 12.2 MB JPEG picture. Bamboo: ~570 elements on Kashikawa (~1% of its
SVG), ~130 on Mizuguchi, 29 marks on Inashiro, none on Sawada or Kuwabata.

## R2. What the tiles bought (observed 2026-10-01, method: `stagemin.sh` - `make map PROFILE=1` uncached, fastest of three per figure - the base `/tmp/base298` and the clone back to back, base / clone / clone / base, and the files' sizes after each regeneration)

| map (observed 2026-10-01, method: `stagemin.sh`, both runs per side) | regen base -> tiles | ground-cover stage (`stage_hinterland`) | SVG | page | PNG | load |
|---|---|---|---|---|---|---|
| Inashiro | 5.8 / 6.0 -> 5.5 / 5.4 s | 0.83 -> 0.66 s | 4.56 -> 1.16 MB | 11.8 -> 8.7 MB | 4.9 -> 5.2 MB | 1.8-2.2 |
| Kashikawa | 6.9 / 6.8 -> 6.4 / 6.1 s | 0.62 -> 0.38 s | 7.29 -> 1.67 MB | 20.5 -> 15.8 MB | 8.2 -> 9.5 MB | 3.0-5.2 |
| Sawada | 7.8 / 7.9 -> 7.2 / 7.2 s | 0.63 -> 0.46 s | 3.44 -> 1.03 MB | 10.4 -> 8.4 MB | 5.0 -> 6.0 MB | 2.4-3.3 |
| Kuwabata | 4.7 / 4.6 -> 4.5 / 4.4 s | 0.35 -> 0.36 s | 2.94 -> 1.97 MB | 6.9 -> 6.0 MB | 8.0 -> 8.3 MB | 2.6-3.5 |
| Mizuguchi | 5.5 / 5.6 -> 4.8 / 4.9 s | 0.41 -> 0.27 s | 4.39 -> 0.78 MB | 10.7 -> 7.5 MB | 3.5 -> 4.3 MB | 2.1-2.5 |

Read off the table above (observed 2026-10-01, method: `stagemin.sh`): a regeneration is 0.2-0.7 s faster (4-13%), most of it in the ground-cover stage (the throws and their keep-out tests are gone)
and the rest in writing and reading a smaller file. The SVG is a quarter of its size or less on four maps; Kuwabata, the least
grassed, two thirds. The page is 13-30% smaller - most of it is the embedded picture, which the tiles do not shrink. The PNG
is 4-22% LARGER: the tile is denser than the feathered scatter at its edges, and the GM does not weigh the PNG's size. The
generation stages other than the ground cover are unchanged within the noise (Inashiro's stage total 3.66 / 3.81 -> 3.67 /
3.63 s at load 1.8-2.2; the first Inashiro pair, at load 3.7-6.7, read 10.4-11.0 s and is not used).
