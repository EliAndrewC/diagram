# The stages' items - what each stage writes, counted from the reference roll's manifest

Load this file when: you write a stage's derivation (its `items` row) or check one.

Measured 2026-10-28 (`make hamlet ARGS="--name Inashiro --seed 25 --households <h> --down-deg 90 --sink pond --form nucleated
--out <scratch> --no-render"`, the reference spec of `perf_snapshot.REFERENCE`, then the length of each manifest list). These are
the size of each stage's OUTPUT - its contract's "Writes" - never its work: no operation or call count is read here (feature 444
D1). The hamlet band is 10 to 20 households (`HamletSpec`), so 40 and 80 - the scaling legs `make work-budget` rolls beyond the
band - are extended from 10 and 20 by each item's own scaling, stated in the derivation that uses it.

| manifest key | at 10 | at 20 | the stage that writes it |
|---|---|---|---|
| houses | 10 | 20 | homesteads |
| gardens | 12 | 23 | appurtenances |
| threshing_yards | 10 | 20 | appurtenances |
| byres | 4 | 7 | appurtenances |
| farm_sheds | 1 | 3 | appurtenances |
| wells | 2 | 2 | appurtenances, lane_wells |
| retirement_houses | 5 | 11 | homesteads |
| access_corridors | 22 | 51 | homesteads |
| farm_fixtures | 38 | 78 | hinterland |
| persimmons | 9 | 17 | hinterland |
| fields[0].plots (the comb's plots, cells of 1,488 sq ft) | 376 | 853 | field |
| fields[0].outline (points) | 67 | 78 | field |
| streams[0].poly (the brook's points; its length) | 212 (5,404 ft) | 237 (7,362 ft) | field |
| wet_plots + dry_plots + flooded_plots (the plots labeled or drawn apart) | 71 | 129 | field |
| field_ditches (their segments: 2 to 22 each; the longest segment) | 9 (79 segments; 222 ft) | 12 (120 segments; 183 ft) | field |
| drawn_channels | 10 | 13 | field |
| comb_floors.inashiro-paddies | 67 | 78 | field |
| weirs, streams, fields, field_ponds | 1 each | 1 each | field |
| pond | 1 pond (4 points) | 1 pond | sink |
| lanes | 12 | 23 | web |
| bridges | 6 | 9 | crossings |
| washing_places | 1 | 3 | washing |
| tree_crowns | 1,167 | 2,151 | hinterland, woodland, windbreak, pond_bank |
| scrub_pines | 252 | 591 | hinterland |
| bamboo_stands | 3 | 6 | bamboo |
| commons | 5 | 5 | woodland |
| village_groves | 2 | 2 | windbreak |
| marshes | 2 | 2 | hinterland |
| kosatsuba | 1 | 1 | notice |
| labels | 1 | 1 | labels |
| way_out_track, way_out_gate | 2 points each | 2 points each | track |

**Corrected 2026-10-28**: the brook's and the ditches' rows first counted each record's dict keys (`poly`, `role`, ...), not its points; recounted from their `poly` lists the same day. The field and sink derivations written before the correction rest on the wrong figures and are being rewritten.
