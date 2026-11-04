# The homesteads port, piece by piece (feature 444 T30)

Load this file when: you continue porting the homesteads stage to Rust - what is ported, what is left, and where each piece's
Python lives. The stage's map is `homesteads.map.md`; the plan's decisions are `plan.md` T30 (D1-D5, CLEAR on 2026-11-04).

The Rust lives in `rust/phases/src/homesteads/`, behind `#![cfg_attr(not(test), expect(dead_code))]` in `homesteads.rs` until the stage
is whole: nothing calls it but its tests, so it lands with T27-T29 without changing a map, and is wired into `STAGES` (a thin
`homesteads/stages.py` door) only when every piece below is in. Each piece keeps its Python's research claims at its constants.

## Ported (2026-11-04)

| piece | Rust | Python it replaces |
|---|---|---|
| the free ground's raster, a rectangle at nine points | `ground.rs` (`Ground`) | `homesteads/boundary.py` `FreeGround`, `SiteCorridors` |
| the reach, labeled once | `ground.rs` (`Ground::reach`, `Reach`) | `homesteads/region.py` `SeatRegion` (the flood) |
| the positional hash, the yard, the garden and its beds | `layout.rs` | `houses.py` `_hjit`, `homestead_parts/yards.py` `_yard_area_ft2`/`_yard_dims`, `rolling/bundle.py` `_garden_beds` |
| the storehouse annex, the byre | `layout.rs` (`kura`, `byre`) | `farm_fixtures.py` `kura_rect`, `shrines_wells/byres.py` `byre_part` |
| the farmhouse's turn | `bearing.rs` | `rolling/bearing.py` (`MarginBearing`, `house_rot`, `turned_box`) |
| the fixtures | `fixtures.rs` | `homestead_parts/fixture_seats.py` (`lay_fixtures` and every kind's seats) |
| the bundle and its envelope | `bundle.rs` | `rolling/bundle.py` `_bundle_geom`, `_bundle_layout` (nucleated), `_rake_parts`, `_bundle_envelope` |
| the households' lots | `lots.rs` | `rolling/lot.py` (`size_ladder`, `quota_carriers`, `larger_first`, `HouseholdLots`) |
| the fit rules: the south sun both ways, the eave gap on turned roofs, one bank, free ground, the yard's opening | `fit.rs` (`Standing`, `sun_ok`, `too_near`, `across_a_stream`, `on_free_ground`, `opens`) | `rolling/fit.py` `_sun_corridor_ok`, `_gardens_sun_ok`, `_house_too_near_a_neighbor`, `_parts_across_stream`, `_rect_hits`/`_rect_on_water` (by the raster), `SeatRegion.opens` |
| the placer and the growth: the first house nearest the seat, the rest grown ring by ring; each offer's sides, the one computed move, the least-shaded side | `place.rs` (`grow`, `Seating::offer`, `Keep`) | `rolling/place.py` `_place_bundle_nucleated`, `homesteads/growth.py` `grow_the_margin`, `capacity.py` `free_seats`/`offer_seats` (the nucleated path; the passage share's tight seats still owed) |
| the wood share, judged at its lattice square on the map's lattice, each household's keep-outs barring the others' | `wood.rs` (`Shares`, `keepouts`), asked last of every layout by `place.rs` | `homestead_parts/wood_share.py` (`WoodShares.share`, `seat_barred`, `covers_a_seat`, `copse_keepouts`) |
| the track out's sweep: the gateway pulled clear of the crop, 41 bearings nearest the ideal first, ranked wet, steadings, then crop and water, the least-bad dry bearing kept, else the dry exit | `track.rs` (`connector`, `Checker`, `fabric_hits`, `grown`, `past_the_frame`, `pull_clear`) | `ways/track.py` `connector_track`, `past_the_frame`, `wet_grown_by_the_lane`; `ways/checks.py` `PathChecker`, `shallow_crossing`, `crossing_lands_on_crop`; `ways/fabric.py` `fabric_hits_boxed`, `_crosses_fabric`; `clearance.py` `pairs_within`; `sitegen/geom.py` `pull_clear`, `crosses_poly` |
| Python's string-seeded `random.Random` | `pyrand.rs` (`from_text`, `shuffled`, `sha512`) | - (pinned against CPython's own draws) |

## Left, in the order they are needed

1. The fit rules still owed (the rest ported in `fit.rs`): the wood seat covered, the persimmon's sun conflict, the house's wall on the bund, the registry's admission beyond the raster, the house unreachable - the fit rules a layout is asked (`rolling/fit.py` `_parts_fit` and its rules, 309-431 and 433-930): the wood seat covered, the
   south sun of the yard and beds (`_sun_corridor_ok`, `_yard_sun_conflict`, `_gardens_sun_ok`, `_persimmon_sun_conflict`), the yard
   opening onto the reach (`SeatRegion.opens`), the house's wall on the bund (`houses.py` `_wall_on_the_bund`), the parts across a
   stream, the parts and fixtures off the field (`_rect_hits`), the beds off the water (`_rect_on_water`), the registry's admission
   of each part (`rolling/lot.py` `bundle_admitted` - the overlap matrix the standing registry reads: port the pairs a homestead's
   parts meet at seating time), the house on a tread, too near a neighbor, unreachable.
2. (ported: the placer.) 3. The growth's passage share and its tight seats (the rest ported) - the growth (`homesteads/growth.py` `grow_the_margin`, `footprint`, `seat_toward`, `settled_seat`, `keeps_its_distance`,
   `keeps_every_gap`; the first house by `capacity.py` `free_seats`), the passage share and tight seats.
4. (ported: the wood share.)
5. The track out, the sweep ported (`track.rs`): still owed the dry exit (`ways/dry_exit.py`, reusing `seat/exit.rs`), `connector_through` (`route_around`, the thread through the fabric in `thread.py`), the gateway (`cluster_edge.py` `_cluster_gateway`) and the choice (`ways/track.py` `choose_track_out`, via `homesteads/household_ways.py` `chose_the_track`, `near_the_cluster`).
6. The households' ways (`rolling/gap_ways.py` `lay_the_ways`: the lane layers, the flood, each door's exits, the taut run, the lane
   law's rules each leg asks - `fixtures_clear`, `parts_clear`, `lawful_leg`, `tree_admits` - and `access.reserve`); the lane law's
   rules into `rust/phases/src/law/` (D1).
7. The dispersed hamlet's front row and ranks (`homesteads/stages.py` `_seat_households_as`, `capacity.py`) and the row village
   (`homesteads/rows.py`) - D4; a grove farm's layout (`rolling/dispersed.py`).
8. The door: `homesteads/stages.py` gathers the inputs, calls the Rust, writes the records (`houses.py` `try_place`'s record,
   `rolling/lot.py` `record_parts`), draws the farmsteads (`Settlement.farmsteads`) and reserves the seating; the counters (D5); the
   Python above deleted (D4); `make rust-gate` through the stage; the tests moved.

## Size of what is left (measured 2026-11-04, `wc -l`)

The track out (`ways/track.py` 549, `thread.py` 268, `gateway.py` 71, `dry_exit.py` 212, `clearance.py` 395, `route.py` 423,
`cluster_edge.py` 79), the households' ways (`rolling/gap_ways.py` 591, `access.py` 823, `passage.py` 329, `route.py` 305), the lane law
the ways ask (`ways/law/` and `law_water.py`, 1,431), the dispersed and row forms (`homesteads/rows.py` 690, `capacity.py`, the front
row in `stages.py`, `rolling/dispersed.py`) and the door: about 7,000 lines of Python. The seat's way-out walk
(`rust/phases/src/seat/exit.rs`) is the dry exit's form already in Rust, for the track's fallback to reuse.
