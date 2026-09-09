# Research - 220 the field fitted once

## R1 - the profile before (2026-09-09, seed 4, `make perf-profile STAGE=field`)

`stage_field` 5.40 s real (10.85 s under cProfile). `fit_field` -> `_fit_at_aspect` -> **`build_comb`
x4** at 2.68 s profiled each - the search carves the whole comb at every guess. Inside a build:

| function | calls | profiled s | share of a build |
|---|---|---|---|
| `close_seams` | 4 | 7.22 | 67% |
| `_unjog` | 4 | 2.87 | |
| `_trade` | 155 | 2.79 | |
| `_absorb` | 364 | 1.78 | |
| `_carve` | 4 | 2.81 | 26% |
| `_carve_sector` / `_sector_body_rows` | 24 / 20 | 2.47 / 2.28 | |
| `supply_bank_clearance` | 86,259 | 1.68 (1.07 self) | |
| `in_supply` -> `_quad_in_supply` | 2,557 | 1.35 | |
| shapely: `Polygon.__new__` 34,881, `buffer` 38,574, `bounds` 267,604, `intersection` 23,884, `is_valid` 27,757 | | 4.8 of the 7.2 in the seams | |

`net_acres` reads the plot polygons only; `tail_dangles` the plots' extent; `net_bends_acutely` the
channels - none reads what the finish adds.

The commons scatter's own per-glyph work bounded feature 218's hinterland; here the bound is the
search paying the finish three times over.
