# 269's engine groups (T21), after 261 landed (2026-09-28)

Each group owns its modules; no two groups touch the same file. Run one after another by
/diagram/.clones/.tools/run-engine-queue.sh (full CLAUDE.md, not the page runner). Source: outcomes.md section 3.

| group | items | modules |
|---|---|---|
| E1 | B10 privy seats, B11 manure seat, B12 bath band and seat, B13 coop band | hamletgen/homesteads/fixtures.py (privy, manure, bath, coop parts) |
| E2 | B14 persimmon, B15 woodpile form, fc:2261 declared shares, B16 byre | settlement/farm_fixtures.py, fixtures.py (persimmon, woodpile, per-house roll), settlement/shrines_wells/byres.py, _knobs.py byre_form |
| E3 | B17 lane stubs, B18 bearing spread, B18 quarter turn with its yard, B04 field spur | settlement/water_ways/lanes.py, settlement/houses.py, seats, hamletgen/ways/track.py |
| E4 | B01 fallow knob, B06 furrow tracts, B07 dry band on a fan | settlement/fields/paddy.py, waterfields/carve.py, waterfields/comb.py |
| E5 | B21 footbridge forms, B22 weir forms, B22 head race, B23 comments | settlement/city/bridges.py, hamletgen/consts.py weir, hamletgen/water/brook.py, cluster.py/stages.py comments |
| E6 | B26 copse size, B27 parcel scorer and comment, B28 commons canopy, B29 bamboo | homestead_parts/groves.py (copse, bamboo b_th), hinterland/parcels.py, core.py canopy, homesteads/bamboo.py |
| E7 | B30 windbreak belt knob (L; one settlement-review after) | homestead_parts/groves.py (mix only), a new crown treatment |
| E8 | B42 retirement house (L; a new kind and knob) | a new module; the houses registry |
| E9 | B40 alley surface | settlement/town_ways.py |
| K1-K4 | T20: the 43 kinds' Entry/label/prose from outcomes.md section 2, entry-drift on bundles | l7r/diagram/interactive/classes/*, compound_kinds |
