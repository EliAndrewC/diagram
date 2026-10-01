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
