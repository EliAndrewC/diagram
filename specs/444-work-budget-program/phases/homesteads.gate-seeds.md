# The homesteads' fresh-seed refusals at the Rust gate - measured 2026-11-05

Each `make rust-gate` rolls a fresh block of 48 seeds that rotates with the engine. Three blocks in a row each failed one seed at
the homesteads (SiteRefused), beside the seat's 901280 (the 444#9 class, carried on the failing list).

| gate record | seed | households | the Rust stages | main's Python (worktree at origin/main, `make hamlet`) | found | now |
|---|---|---|---|---|---|---|
| `dev/rust-gate/20261105T155554Z.json` | 901303 | 15 | seated 14 of 15 on margin 1 (the grow) | 15 of 15 (the grow, 109 offers) | the wood share's lattice (the map's one lattice against Python's anchored on each house): house 0's footprint 87.9 ft west against 58.6, every later seat parted that much farther | 15 of 15 (commit "the wood share as Python reserves it") |
| `dev/rust-gate/20261105T171105Z.json` | 290494 | 19 | seated 14 of 19 on margin 1 (the row, one side, dry edge) | 19 of 19 (the row) | the first street's slack (a row's length, the departure seed 729966 needed) laid it 5,000 ft and centered it east, three frames seatable | 19 of 19 (commit "a row short of its households seated again on Python's street") |
| `dev/rust-gate/20261105T175757Z.json` | 778251 | 17 | seated 12 of 17 on margin 1 | REFUSED at the seat (SeatRefused: "no field margin turns its back to the NW wind clear of the dry hem, the toe and the canvas edge - the site has no seat (plan D3)") | the Rust seat seats a margin Python's seat refuses; no Python homesteads ran on it | open |

## The probe the round arbiter ruled (ask:444-T30-fresh-seed-refusals), 2026-11-05

The old Python seat (detached worktree at e16522808) on seed 778251, 17 households: REFUSED (SeatRefused). Instrumented, its three
margins nearest the Rust seat's anchor (2840.5, 2233.2; the Rust's first three frames, seat for seat the same margin points) are
each refused by `back_fouled` - the share of the back under DRY PLOTS: 1.000, 0.952 and 0.333 against the 0.30 bar, with 97 dry
plots on the map when the seat is chosen. The Rust seat on the same seed is handed 0 dry plots: since T28 (`STAGES`:
`stage_hem` after `stage_seat`, "so the houses stand between the paddy and the dry fields" - the research pass of 2026-11-04 in
`seat.refusals.md`, form (b) ATTESTED) no dry plot stands when the seat is chosen. At e16522808 the field laid the plots before
the seat. So the Python seat's refusal is the dry plots T28 moved after it, not a Rust seat that diverged from Python's: the
Rust seat's margin 1 stands under the stage order T28 set, and the homesteads seat 12 of 17 on it.

How each was traced: the Python stage instrumented in a scratch worktree of origin/main (never committed), the Rust stage by a
temporary probe (never committed), offer by offer from the first house.
