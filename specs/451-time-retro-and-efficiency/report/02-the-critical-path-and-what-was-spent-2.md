## The critical path and what was spent beside it (`make where-time`'s columns, feature 451 T11)

| task | agents | agent minutes | k tokens in | k tokens out | k advisor in | k advisor out | refused landings | plan re-rounds | by kind (count) |
|---|---|---|---|---|---|---|---|---|---|
| T02 | 4 | 37 | 14554.3 | 79.2 | 274.1 | 31.3 | 0 | 0 | impl-drift 2, general-purpose 1, spec-fidelity 1 |
| T23 | 2 | 22 | 10104.1 | 67.8 | 301.1 | 41.5 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T03 | 4 | 29 | 10666.1 | 68.7 | 388.1 | 38.9 | 0 | 2 | spec-fidelity 3, general-purpose 1 |
| T26 | 3 | 33 | 25374.4 | 126.2 | 400.8 | 24.2 | 0 | 0 | general-purpose 1, spec-fidelity 1, claims-triage 1 |
| T25 | 3 | 33 | 17903.3 | 94.4 | 378.3 | 38.3 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T04 | 3 | 30 | 19659.9 | 86.5 | 346.0 | 23.6 | 0 | 0 | spec-fidelity 2, general-purpose 1 |
| T05 | 3 | 32 | 19722.4 | 94.6 | 385.7 | 38.3 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T06 | 5 | 43 | 22480.7 | 131.3 | 535.9 | 50.1 | 1 | 1 | spec-fidelity 3, general-purpose 1, spec-fidelity-verify 1 |
| T18 | 5 | 15 | 3734.1 | 49.9 | 95.3 | 16.3 | 0 | 0 | spec-fidelity 4, general-purpose 1 |
| T14 | 5 | 41 | 21703.3 | 119.0 | 461.5 | 37.6 | 0 | 1 | spec-fidelity 4, general-purpose 1 |
| T12 | 5 | 32 | 28183.2 | 111.3 | 399.4 | 44.6 | 0 | 1 | spec-fidelity 4, general-purpose 1 |
| T13 | 4 | 32 | 17375.3 | 108.1 | 314.2 | 34.0 | 0 | 1 | general-purpose 2, spec-fidelity 2 |
| T20 | 5 | 54 | 21027.5 | 118.7 | 488.4 | 43.9 | 0 | 1 | spec-fidelity 3, general-purpose 2 |
| T21 | 4 | 82 | 24073.6 | 111.0 | 625.1 | 53.3 | 0 | 1 | general-purpose 2, spec-fidelity 2 |
| T39 | 3 | 9 | 7756.7 | 33.6 | 114.9 | 7.9 | 0 | 0 | spec-fidelity 2, general-purpose 1 |
| T31 | 5 | 76 | 35239.6 | 196.5 | 845.5 | 66.0 | 0 | 1 | general-purpose 3, spec-fidelity 2 |
| T34 | 2 | 14 | 8998.9 | 54.6 | 267.0 | 21.1 | 1 | 0 | general-purpose 1, spec-fidelity 1 |
| T43 | 5 | 36 | 35368.4 | 122.5 | 468.3 | 31.9 | 1 | 1 | spec-fidelity 3, general-purpose 2 |
| T38 | 5 | 61 | 53590.9 | 205.3 | 433.9 | 40.5 | 0 | 0 | general-purpose 3, spec-fidelity 2 |
| T44 | 4 | 31 | 20605.7 | 105.5 | 178.7 | 28.3 | 0 | 2 | spec-fidelity 3, general-purpose 1 |
| T45 | 4 | 39 | 13203.3 | 66.2 | 169.3 | 24.9 | 0 | 1 | spec-fidelity 3, general-purpose 1 |
| T33 | 7 | 100 | 92401.8 | 348.5 | 1162.3 | 122.6 | 1 | 1 | general-purpose 4, spec-fidelity 2, round-arbiter 1 |
| T08 | 5 | 52 | 34962.6 | 197.0 | 705.6 | 58.8 | 0 | 0 | general-purpose 2, spec-fidelity 2, spec-fidelity-verify 1 |
| T09 | 3 | 38 | 29327.2 | 128.4 | 341.8 | 38.7 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T55 | 5 | 74 | 42934.6 | 225.2 | 807.8 | 70.5 | 0 | 1 | general-purpose 3, spec-fidelity 2 |
| T57 | 4 | 49 | 38265.1 | 177.9 | 727.3 | 58.4 | 0 | 1 | general-purpose 2, spec-fidelity 2 |
| T62 | 4 | 31 | 16960.7 | 82.3 | 317.3 | 25.1 | 0 | 0 | spec-fidelity 3, general-purpose 1 |
| T58 | 6 | 69 | 50419.7 | 232.2 | 781.5 | 86.1 | 0 | 0 | general-purpose 2, claims-triage 1, spec-fidelity 1, round-arbiter 1, impl-drift 1 |
| T11 | 5 | 58 | 36934.2 | 176.7 | 918.3 | 83.5 | 0 | 1 | general-purpose 3, spec-fidelity 2 |
| T65 | 3 | 30 | 18678.4 | 125.3 | 307.9 | 27.5 | 0 | 0 | spec-fidelity 2, general-purpose 1 |
| T56 | 2 | 19 | 14729.1 | 71.6 | 94.1 | 15.0 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T61 | 3 | 46 | 35143.1 | 206.5 | 378.6 | 37.3 | 0 | 0 | general-purpose 2, spec-fidelity 1 |
| T54 | 3 | 43 | 34159.3 | 154.9 | 569.1 | 44.0 | 0 | 0 | general-purpose 2, spec-fidelity 1 |
| T72 | 2 | 14 | 5811.1 | 52.4 | 220.0 | 20.5 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T74 | 3 | 32 | 25093.1 | 119.8 | 397.5 | 40.8 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T76 | 2 | 19 | 11605.3 | 60.4 | 286.4 | 27.8 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T79 | 7 | 186 | 123953.6 | 653.0 | 1000.0 | 111.8 | 0 | 1 | general-purpose 4, spec-fidelity 2, round-arbiter 1 |
| T84 | 5 | 57 | 53195.5 | 229.9 | 559.8 | 63.4 | 2 | 0 | general-purpose 3, spec-fidelity 2 |
| T88 | 4 | 62 | 52331.1 | 249.6 | 507.0 | 46.8 | 2 | 1 | general-purpose 2, spec-fidelity 2 |
| T97 | 3 | 64 | 47054.9 | 230.2 | 772.0 | 78.7 | 1 | 0 | general-purpose 2, spec-fidelity 1 |
| T101 | 3 | 46 | 32854.8 | 194.3 | 389.1 | 41.9 | 1 | 0 | general-purpose 2, spec-fidelity 1 |
| T102 | 3 | 40 | 38304.4 | 153.2 | 154.3 | 28.8 | 1 | 1 | spec-fidelity 2, general-purpose 1 |
| T103 | 3 | 74 | 38007.0 | 177.5 | 425.7 | 57.1 | 0 | 0 | general-purpose 2, spec-fidelity 1 |
| T99 | 4 | 67 | 53372.0 | 225.7 | 855.2 | 68.9 | 0 | 1 | general-purpose 2, spec-fidelity 2 |
| T96 | 4 | 93 | 88292.4 | 324.0 | 759.9 | 65.6 | 0 | 0 | general-purpose 3, spec-fidelity 1 |
| T92 | 2 | 39 | 39572.3 | 129.4 | 182.0 | 28.7 | 2 | 0 | general-purpose 1, spec-fidelity 1 |
| T108 | 3 | 41 | 30305.6 | 132.8 | 374.9 | 41.2 | 1 | 1 | spec-fidelity 2, general-purpose 1 |
| T49 | 2 | 32 | 16325.5 | 84.1 | 205.8 | 28.9 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T113 | 5 | 64 | 53031.7 | 219.4 | 245.2 | 43.1 | 0 | 2 | spec-fidelity 3, general-purpose 2 |
| T111 | 2 | 27 | 15032.1 | 96.8 | 372.7 | 32.9 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T106 | 2 | 37 | 37912.8 | 147.7 | 361.2 | 29.1 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T112 | 3 | 38 | 57014.4 | 134.6 | 117.9 | 15.9 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T114 | 3 | 40 | 27688.9 | 151.9 | 190.5 | 23.2 | 0 | 0 | general-purpose 2, spec-fidelity 1 |
| T51 | 3 | 40 | 28404.7 | 160.4 | 688.7 | 50.1 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T110 | 6 | 121 | 61551.3 | 323.3 | 560.2 | 84.4 | 0 | 3 | spec-fidelity 4, general-purpose 2 |
| T80 | 3 | 50 | 22484.5 | 123.2 | 311.8 | 26.2 | 1 | 1 | spec-fidelity 2, general-purpose 1 |
| T83 | 6 | 186 | 106648.6 | 442.5 | 1116.5 | 130.6 | 1 | 2 | general-purpose 3, spec-fidelity 3 |
| T87 | 8 | 156 | 99709.2 | 434.5 | 919.5 | 118.7 | 1 | 4 | spec-fidelity 5, general-purpose 3 |
| T123 | 4 | 73 | 64957.2 | 214.7 | 471.1 | 78.4 | 0 | 1 | general-purpose 2, spec-fidelity 2 |
| T105 | 3 | 41 | 29587.1 | 137.8 | 359.4 | 39.5 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T118 | 5 | 122 | 72489.2 | 332.0 | 769.6 | 72.6 | 0 | 1 | general-purpose 3, spec-fidelity 2 |
| T89 | 5 | 105 | 73240.6 | 287.8 | 459.3 | 53.0 | 0 | 2 | spec-fidelity 3, general-purpose 2 |
| T129 | 3 | 56 | 49929.1 | 188.5 | 634.3 | 57.3 | 0 | 0 | general-purpose 2, spec-fidelity 1 |
| T115 | 3 | 57 | 29218.9 | 136.9 | 387.2 | 36.1 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T91 | 4 | 96 | 36022.6 | 236.7 | 164.1 | 35.3 | 1 | 1 | general-purpose 2, spec-fidelity 2 |
| T94 | 3 | 49 | 27286.6 | 86.8 | 192.5 | 32.2 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T142 | 2 | 85 | 20056.1 | 76.3 | 81.5 | 11.5 | 1 | 0 | general-purpose 1, spec-fidelity 1 |
| T141 | 5 | 42 | 48613.9 | 143.6 | 172.1 | 22.6 | 0 | 2 | spec-fidelity 3, general-purpose 2 |
| T147 | 6 | 23 | 12544.8 | 71.1 | 143.0 | 28.5 | 0 | 0 | modal-depiction 2, general-purpose 1, modal-form 1, modal-research 1, spec-fidelity 1 |
| T151 | 5 | 30 | 9928.5 | 63.7 | 181.8 | 21.1 | 0 | 1 | spec-fidelity 3, general-purpose 1, escalation-check 1 |
| T153 | 50 | 139 | 70684.9 | 532.3 | 1380.5 | 172.2 | 1 | 2 | modal-research 12, modal-form 11, spec-fidelity 6, modal-depiction 6, impl-drift 6, modal-triage 3, general-purpose 2, claims-triage 2, quote-check 1, record-format 1 |
| T157 | 2 | 15 | 9678.2 | 51.2 | 139.2 | 15.7 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T158 | 4 | 69 | 44801.3 | 211.4 | 222.1 | 23.4 | 0 | 2 | general-purpose 2, spec-fidelity 2 |
| T98 | 79 | 203 | 67623.5 | 716.8 | 2408.6 | 303.7 | 0 | 1 | impl-drift 16, modal-depiction 9, modal-research 8, modal-form 8, glyph-check 6, size-audit 6, building-review 5, record-format 4, modal-triage 4, round-arbiter 4, quote-check 3, spec-fidelity 2, claims-triage 2, general-purpose 1, research-pass 1 |
| T156 | 2 | 9 | 7454.9 | 40.7 | 0.0 | 0.0 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T154 | 13 | 122 | 38343.1 | 215.2 | 930.9 | 85.0 | 1 | 0 | research-pass 6, spec-fidelity 3, impl-drift 2, general-purpose 1, claims-triage 1 |
| T155 | 31 | 130 | 35460.9 | 293.2 | 1192.9 | 149.1 | 1 | 0 | modal-form 5, spec-fidelity 5, impl-drift 4, round-arbiter 4, modal-research 4, modal-depiction 3, general-purpose 1, claims-triage 1, record-format 1, source-applicability 1, modal-triage 1, escalation-check 1 |
| T160 | 19 | 95 | 46997.8 | 313.2 | 1138.0 | 168.4 | 4 | 2 | building-review 5, glyph-check 3, round-arbiter 3, spec-fidelity 3, size-audit 2, general-purpose 1, claims-triage 1, impl-drift 1 |
| T161 | 0 | 0 | - | - | - | - | 4 | 0 |  |
| T164 | 3 | 52 | 40318.1 | 166.0 | 264.7 | 30.6 | 1 | 0 | general-purpose 2, spec-fidelity 1 |
| T90 | 2 | 6 | 5067.1 | 25.9 | 0.0 | 0.0 | 1 | 0 | general-purpose 1, spec-fidelity 1 |
| T167 | 3 | 24 | 26994.2 | 79.4 | 179.5 | 14.4 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T169 | 4 | 50 | 36390.0 | 181.0 | 686.3 | 73.2 | 0 | 1 | general-purpose 2, spec-fidelity 2 |
| T168 | 2 | 7 | 3862.1 | 24.8 | 0.0 | 0.0 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T171 | 6 | 79 | 55872.3 | 256.4 | 600.7 | 58.0 | 0 | 1 | general-purpose 2, spec-fidelity 2, round-arbiter 2 |
| T170 | 18 | 196 | 203490.9 | 732.7 | 1665.9 | 173.8 | 4 | 2 | general-purpose 14, spec-fidelity 3, escalation-check 1 |
| T176 | 2 | 2 | 200.5 | 10.3 | 0.0 | 0.0 | 4 | 0 | spec-fidelity 1, escalation-check 1 |
| T175 | 3 | 19 | 17254.2 | 77.3 | 319.8 | 21.1 | 4 | 1 | spec-fidelity 2, general-purpose 1 |
| T180 | 2 | 15 | 14757.3 | 67.7 | 0.0 | 0.0 | 4 | 0 | general-purpose 1, spec-fidelity 1 |
| T100 | 2 | 16 | 11597.9 | 63.5 | 148.8 | 16.1 | 4 | 0 | general-purpose 1, spec-fidelity 1 |
| T177 | 35 | 88 | 98681.8 | 423.1 | 474.2 | 71.0 | 2 | 1 | message-check 27, general-purpose 3, round-arbiter 3, spec-fidelity 2 |
| T179 | 5 | 61 | 77455.8 | 291.8 | 421.1 | 54.8 | 1 | 1 | general-purpose 3, spec-fidelity 2 |
| T182 | 2 | 2 | 180.7 | 9.1 | 0.0 | 0.0 | 1 | 1 | spec-fidelity 2 |
| T174 | 8 | 61 | 49082.2 | 186.8 | 464.6 | 77.8 | 1 | 1 | message-check 4, general-purpose 2, spec-fidelity 2 |
| T165 | 2 | 28 | 26543.9 | 83.4 | 205.3 | 15.5 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T172 | 2 | 1 | 114.4 | 4.3 | 0.0 | 0.0 | 0 | 0 | escalation-check 1, round-arbiter 1 |
| T183 | 13 | 74 | 60530.9 | 275.2 | 435.8 | 49.4 | 0 | 1 | general-purpose 3, fork 3, spec-fidelity 2, escalation-check 2, claude-code-guide 1, message-check 1, round-arbiter 1 |
| T184 | 37 | 90 | 60684.6 | 337.5 | 521.6 | 65.5 | 2 | 3 | record-format 9, quote-check 7, general-purpose 4, spec-fidelity 4, modal-triage 3, translation-check 3, round-arbiter 2, modal-research 2, intro-check 1, source-reader 1, source-applicability 1 |
| T188 | 4 | 39 | 34362.0 | 147.4 | 200.9 | 38.7 | 0 | 2 | spec-fidelity 3, general-purpose 1 |
| T190 | 9 | 28 | 10439.7 | 128.4 | 327.6 | 23.7 | 0 | 0 | general-purpose 9 |
| T185 | 8 | 60 | 49085.2 | 212.0 | 462.2 | 52.0 | 0 | 1 | general-purpose 3, spec-fidelity 2, modal-form 2, modal-research 1 |
| T186 | 32 | 39 | 13762.4 | 159.4 | 425.5 | 47.6 | 0 | 2 | general-purpose 27, spec-fidelity 3, escalation-check 2 |
| T187 | 4 | 31 | 35460.8 | 127.7 | 116.0 | 16.8 | 2 | 1 | spec-fidelity 2, general-purpose 1, claims-triage 1 |
| T191 | 4 | 26 | 19855.0 | 102.4 | 123.6 | 12.9 | 1 | 0 | general-purpose 1, spec-fidelity 1, modal-form 1, modal-research 1 |
| T193 | 7 | 60 | 59264.3 | 251.6 | 369.4 | 52.7 | 3 | 2 | spec-fidelity 3, general-purpose 2, message-check 2 |
| T194 | 3 | 31 | 49199.6 | 119.6 | 304.5 | 17.1 | 1 | 0 | general-purpose 2, spec-fidelity 1 |
| T196 | 3 | 26 | 17471.6 | 80.1 | 110.8 | 13.8 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T195 | 4 | 45 | 35868.6 | 141.8 | 126.6 | 17.1 | 3 | 1 | general-purpose 2, spec-fidelity 2 |
| T192 | 8 | 322 | 61681.8 | 239.8 | 529.3 | 47.9 | 0 | 2 | general-purpose 4, spec-fidelity 3, escalation-check 1 |
| T197 | 3 | 6 | 400.7 | 17.3 | 51.8 | 12.8 | 3 | 1 | spec-fidelity 2, round-arbiter 1 |
| T198 | 7 | 69 | 55835.6 | 209.4 | 599.9 | 81.1 | 2 | 3 | spec-fidelity 4, general-purpose 2, impl-drift 1 |
| T199 | 1 | 1 | 64.5 | 2.5 | 0.0 | 0.0 | 2 | 0 | escalation-check 1 |
| T200 | 0 | 0 | - | - | - | - | 2 | 0 |  |
| T202 | 2 | 4 | 192.6 | 16.5 | 27.3 | 4.2 | 0 | 1 | spec-fidelity 2 |
| T204 | 2 | 16 | 9679.7 | 47.1 | 90.1 | 13.3 | 1 | 0 | general-purpose 1, spec-fidelity 1 |
| T201 | 5 | 43 | 34669.3 | 136.3 | 139.9 | 15.7 | 0 | 0 | general-purpose 2, claude-code-guide 1, message-check 1, spec-fidelity 1 |
| T207 | 3 | 37 | 17307.1 | 62.2 | 125.2 | 9.9 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T214 | 2 | 21 | 9918.7 | 52.6 | 121.1 | 13.2 | 1 | 0 | general-purpose 1, spec-fidelity 1 |
| T209 | 2 | 30 | 20201.0 | 78.5 | 155.0 | 20.2 | 1 | 0 | general-purpose 1, spec-fidelity 1 |
| T213 | 3 | 3 | 1537.1 | 19.2 | 0.0 | 0.0 | 1 | 1 | spec-fidelity 2, general-purpose 1 |
| T212 | 5 | 3 | 274.3 | 12.6 | 26.1 | 6.8 | 1 | 0 | impl-drift 3, spec-fidelity 1, escalation-check 1 |
| T215 | 3 | 20 | 13787.7 | 62.6 | 298.6 | 37.9 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T216 | 11 | 35 | 16608.1 | 146.4 | 624.5 | 38.5 | 0 | 0 | general-purpose 3, message-check 3, Explore 2, spec-fidelity 1, Plan 1, claude 1 |
| T217 | 8 | 15 | 8693.6 | 70.0 | 121.2 | 13.3 | 0 | 1 | message-check 4, spec-fidelity 2, general-purpose 1, escalation-check 1 |
| T221 | 2 | 1 | 126.1 | 7.5 | 0.0 | 0.0 | 5 | 0 | escalation-check 1, spec-fidelity 1 |
| T219 | 6 | 53 | 46623.8 | 209.1 | 562.9 | 45.2 | 5 | 1 | general-purpose 2, spec-fidelity 2, impl-drift 2 |
| T218 | 1 | 1 | 107.5 | 6.0 | 0.0 | 0.0 | 5 | 0 | spec-fidelity 1 |
| T220 | 11 | 34 | 10368.4 | 137.3 | 608.8 | 66.1 | 5 | 1 | general-purpose 6, spec-fidelity 2, impl-drift 2, escalation-check 1 |
| T222 | 2 | 1 | 274.5 | 6.2 | 0.0 | 0.0 | 5 | 0 | general-purpose 1, spec-fidelity 1 |
| T223 | 21 | 56 | 26968.0 | 202.0 | 706.9 | 84.9 | 4 | 0 | impl-drift 5, general-purpose 3, spec-fidelity 3, modal-research 2, round-arbiter 2, modal-form 2, modal-depiction 2, claims-triage 1, modal-triage 1 |
| T224 | 5 | 12 | 5060.0 | 48.9 | 93.8 | 13.5 | 2 | 0 | general-purpose 1, spec-fidelity 1, claims-triage 1, impl-drift 1, round-arbiter 1 |
| T225 | 53 | 108 | 23594.4 | 369.7 | 1197.2 | 152.2 | 1 | 0 | source-reader 14, record-format 9, quote-check 7, impl-drift 5, translation-check 4, round-arbiter 3, general-purpose 2, source-applicability 2, modal-depiction 2, spec-fidelity 1, escalation-check 1, modal-triage 1, modal-research 1, modal-form 1 |
| T236 | 15 | 43 | 40332.6 | 173.4 | 502.9 | 49.8 | 0 | 1 | general-purpose 7, spec-fidelity 2, impl-drift 2, quote-check 2, record-format 2 |
| T230 | 3 | 12 | 8740.0 | 48.8 | 256.6 | 15.3 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T238 | 2 | 5 | 5034.0 | 28.1 | 0.0 | 0.0 | 1 | 0 | general-purpose 1, spec-fidelity 1 |
| T240 | 8 | 25 | 28359.3 | 89.7 | 185.4 | 25.9 | 0 | 1 | message-check 5, spec-fidelity 2, general-purpose 1 |
| T237 | 7 | 21 | 15346.3 | 83.8 | 149.3 | 27.2 | 0 | 1 | message-check 3, spec-fidelity 2, general-purpose 1, modal-triage 1 |
| T241 | 2 | 13 | 15818.8 | 51.6 | 203.8 | 17.7 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T226 | 8 | 31 | 29124.9 | 125.5 | 148.2 | 20.4 | 0 | 0 | modal-form 4, general-purpose 2, spec-fidelity 1, modal-research 1 |
| T243 | 20 | 155 | 105302.2 | 539.5 | 1010.1 | 130.9 | 0 | 6 | spec-fidelity 7, general-purpose 6, escalation-check 4, round-arbiter 3 |
| T244 | 4 | 23 | 29314.2 | 80.9 | 359.8 | 30.8 | 0 | 0 | message-check 2, general-purpose 1, spec-fidelity 1 |
| T228 | 3 | 45 | 15115.0 | 58.2 | 258.0 | 17.5 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T234 | 2 | 45 | 40808.6 | 98.2 | 96.3 | 7.4 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T235 | 5 | 42 | 21561.0 | 113.2 | 473.9 | 60.5 | 1 | 2 | spec-fidelity 3, general-purpose 1, round-arbiter 1 |
| T242 | 3 | 18 | 13481.9 | 65.2 | 132.3 | 16.5 | 0 | 0 | general-purpose 1, message-check 1, spec-fidelity 1 |
| T245 | 3 | 40 | 27809.2 | 126.6 | 203.8 | 29.3 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T231 | 3 | 27 | 16126.6 | 70.1 | 161.9 | 21.9 | 0 | 0 | general-purpose 1, spec-fidelity 1, escalation-check 1 |
| T229 | 3 | 40 | 21003.8 | 71.1 | 248.0 | 15.3 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T227 | 2 | 44 | 24281.4 | 83.2 | 115.7 | 14.8 | 1 | 0 | general-purpose 1, spec-fidelity 1 |
| T232 | 11 | 80 | 38978.9 | 178.4 | 577.5 | 40.9 | 0 | 1 | modal-depiction 3, general-purpose 2, modal-research 2, spec-fidelity 2, modal-form 1, round-arbiter 1 |
| T247 | 2 | 12 | 4705.6 | 35.8 | 100.0 | 8.8 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T246 | 3 | 43 | 36436.7 | 139.8 | 222.2 | 30.1 | 0 | 0 | general-purpose 2, spec-fidelity 1 |
| T233 | 3 | 28 | 16661.5 | 84.9 | 402.8 | 26.2 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T249 | 2 | 33 | 13011.9 | 53.4 | 102.4 | 10.6 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T248 | 3 | 34 | 13231.5 | 86.2 | 133.5 | 25.5 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T252 | 2 | 11 | 4282.3 | 29.2 | 206.7 | 16.6 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T253 | 6 | 52 | 76049.5 | 160.7 | 210.6 | 57.2 | 0 | 2 | spec-fidelity 3, general-purpose 2, escalation-check 1 |
| T256 | 2 | 25 | 22152.5 | 79.3 | 69.9 | 7.4 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T254 | 5 | 66 | 47066.7 | 196.6 | 319.6 | 37.4 | 0 | 1 | general-purpose 2, spec-fidelity 2, round-arbiter 1 |
| T259 | 8 | 69 | 48382.5 | 243.7 | 493.3 | 84.0 | 0 | 2 | spec-fidelity 3, general-purpose 2, escalation-check 2, round-arbiter 1 |
| T258 | 3 | 32 | 9974.8 | 78.8 | 124.5 | 13.8 | 2 | 0 | spec-fidelity 2, general-purpose 1 |
| T261 | 2 | 42 | 38451.8 | 93.9 | 523.2 | 33.8 | 2 | 0 | general-purpose 2 |
| T262 | 2 | 27 | 5511.6 | 41.3 | 122.1 | 15.2 | 2 | 0 | general-purpose 1, spec-fidelity 1 |
| T263 | 3 | 31 | 5311.9 | 50.3 | 267.4 | 51.9 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T251 | 30 | 201 | 29799.4 | 285.5 | 1125.3 | 114.1 | 0 | 2 | quote-check 7, record-format 7, general-purpose 4, source-reader 4, spec-fidelity 3, escalation-check 1, impl-drift 1, source-applicability 1, research-pass 1, round-arbiter 1 |
| T250 | 37 | 148 | 34741.2 | 456.3 | 1600.1 | 182.2 | 0 | 2 | general-purpose 10, source-applicability 9, source-reader 5, record-format 4, quote-check 3, spec-fidelity 2, translation-check 2, round-arbiter 2 |
| T267 | 2 | 13 | 4295.4 | 28.3 | 83.8 | 5.7 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T265 | 23 | 62 | 38719.3 | 197.3 | 526.9 | 46.9 | 0 | 2 | record-format 6, quote-check 5, spec-fidelity 3, impl-drift 3, general-purpose 2, source-reader 2, escalation-check 1, round-arbiter 1 |
| T268 | 4 | 16 | 6083.0 | 42.8 | 228.9 | 16.9 | 0 | 1 | spec-fidelity 2, general-purpose 1, escalation-check 1 |
| T272 | 4 | 14 | 4742.9 | 31.7 | 81.4 | 5.9 | 1 | 1 | spec-fidelity 2, general-purpose 1, message-check 1 |
| T271 | 2 | 16 | 4334.4 | 32.7 | 273.1 | 22.9 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T269 | 2 | 20 | 6825.6 | 46.2 | 308.7 | 23.3 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T270 | 2 | 15 | 4250.8 | 29.6 | 106.6 | 11.7 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T292 | 7 | 88 | 54815.4 | 307.0 | 1128.5 | 104.0 | 2 | 2 | general-purpose 4, spec-fidelity 3 |
| T285 | 11 | 57 | 27847.5 | 207.5 | 305.4 | 59.1 | 1 | 5 | spec-fidelity 5, message-check 3, general-purpose 2, escalation-check 1 |
| T281 | 4 | 24 | 14659.5 | 90.1 | 135.8 | 16.5 | 3 | 0 | spec-fidelity 2, general-purpose 1, message-check 1 |
| T284 | 4 | 34 | 17869.3 | 121.0 | 447.2 | 45.7 | 1 | 0 | spec-fidelity 2, general-purpose 1, message-check 1 |
| T295 | 5 | 54 | 19581.0 | 131.0 | 525.7 | 58.0 | 1 | 0 | general-purpose 2, spec-fidelity 2, round-arbiter 1 |
| T305 | 5 | 53 | 21227.6 | 198.9 | 753.3 | 68.9 | 0 | 0 | general-purpose 3, spec-fidelity 2 |
| T303 | 2 | 10 | 3256.9 | 35.2 | 118.0 | 8.8 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T289 | 6 | 88 | 72787.5 | 267.0 | 1098.9 | 64.7 | 1 | 1 | general-purpose 4, spec-fidelity 2 |
| T159 | 5 | 40 | 25658.4 | 85.1 | 406.6 | 41.4 | 0 | 1 | spec-fidelity 2, impl-drift 2, general-purpose 1 |
| T104 | 3 | 77 | 16948.5 | 100.3 | 354.5 | 44.3 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T298 | 4 | 53 | 27791.9 | 184.8 | 454.9 | 45.7 | 1 | 1 | general-purpose 2, spec-fidelity 2 |
| T316 | 6 | 60 | 26162.3 | 162.5 | 614.5 | 56.1 | 0 | 0 | general-purpose 2, spec-fidelity 2, message-check 2 |
| T308 | 5 | 50 | 25912.1 | 186.6 | 845.5 | 76.0 | 0 | 2 | spec-fidelity 3, general-purpose 2 |
| T299 | 4 | 28 | 12904.7 | 90.6 | 412.4 | 42.1 | 3 | 1 | spec-fidelity 2, general-purpose 1, message-check 1 |
| T282 | 0 | 0 | - | - | - | - | 3 | 0 |  |
| T293 | 4 | 42 | 14619.3 | 146.9 | 572.8 | 45.6 | 1 | 0 | general-purpose 3, spec-fidelity 1 |
| T315 | 4 | 72 | 21561.4 | 155.2 | 460.6 | 47.6 | 0 | 3 | spec-fidelity 3, general-purpose 1 |
| T274 | 7 | 61 | 26270.3 | 183.2 | 576.3 | 66.9 | 0 | 1 | general-purpose 3, spec-fidelity 2, message-check 2 |
| T334 | 3 | 45 | 23827.3 | 171.5 | 836.6 | 62.3 | 1 | 0 | general-purpose 2, spec-fidelity 1 |
| T339 | 2 | 18 | 7388.6 | 50.0 | 262.6 | 16.5 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T336 | 3 | 48 | 30984.1 | 154.5 | 620.2 | 54.8 | 0 | 0 | general-purpose 2, spec-fidelity 1 |
| T340 | 2 | 21 | 4547.4 | 39.4 | 203.0 | 17.5 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T347 | 4 | 87 | 21760.5 | 197.9 | 1065.8 | 99.0 | 0 | 0 | general-purpose 3, spec-fidelity 1 |
| T370 | 2 | 16 | 5700.2 | 58.9 | 32.8 | 8.7 | 1 | 0 | general-purpose 1, spec-fidelity 1 |
| T372 | 0 | 0 | - | - | - | - | 1 | 0 |  |
| T359 | 5 | 75 | 34192.6 | 209.7 | 958.0 | 69.7 | 0 | 1 | general-purpose 3, spec-fidelity 2 |
| T324 | 3 | 39 | 12119.0 | 105.9 | 443.8 | 48.2 | 0 | 1 | spec-fidelity 2, general-purpose 1 |
| T325 | 3 | 53 | 24616.9 | 131.3 | 391.9 | 37.5 | 1 | 1 | spec-fidelity 2, general-purpose 1 |
| T383 | 18 | 63 | 13344.0 | 209.4 | 732.6 | 97.7 | 1 | 0 | building-review 6, impl-drift 5, round-arbiter 5, general-purpose 1, spec-fidelity 1 |
| T332 | 2 | 13 | 3719.4 | 34.8 | 122.1 | 16.0 | 1 | 0 | general-purpose 1, spec-fidelity 1 |
| T385 | 1 | 14 | 5605.3 | 64.6 | 470.6 | 15.9 | 1 | 0 | general-purpose 1 |
| T344 | 0 | 0 | - | - | - | - | 1 | 0 |  |
| T346 | 2 | 30 | 12224.6 | 77.8 | 336.8 | 26.5 | 1 | 0 | general-purpose 1, spec-fidelity 1 |
| T382 | 0 | 0 | - | - | - | - | 1 | 0 |  |
| T394 | 5 | 45 | 17772.4 | 163.2 | 763.6 | 55.3 | 5 | 0 | general-purpose 3, spec-fidelity 2 |
| T391 | 3 | 29 | 8519.7 | 73.6 | 197.1 | 28.3 | 4 | 1 | spec-fidelity 2, general-purpose 1 |
| T399 | 6 | 17 | 9339.5 | 66.1 | 171.3 | 12.3 | 2 | 0 | spec-fidelity 3, general-purpose 1, round-arbiter 1, spec-fidelity-verify 1 |
| T139 | 4 | 17 | 5334.2 | 38.1 | 227.0 | 18.9 | 1 | 0 | general-purpose 1, spec-fidelity 1, escalation-check 1, message-check 1 |
| T355 | 5 | 40 | 11692.9 | 87.5 | 400.6 | 29.2 | 0 | 0 | spec-fidelity 2, general-purpose 1, message-check 1, escalation-check 1 |
| T410 | 2 | 21 | 12417.8 | 68.2 | 341.1 | 28.7 | 0 | 0 | general-purpose 1, spec-fidelity 1 |
| T314 | 4 | 19 | 7716.2 | 48.2 | 250.3 | 27.0 | 1 | 0 | spec-fidelity 2, general-purpose 1, message-check 1 |
| T367 | 3 | 21 | 11774.3 | 75.2 | 158.1 | 20.1 | 2 | 0 | general-purpose 1, spec-fidelity 1, round-arbiter 1 |
| T414 | 4 | 13 | 4901.8 | 44.1 | 84.7 | 6.4 | 2 | 0 | spec-fidelity 2, general-purpose 1, message-check 1 |
| T411 | 0 | 0 | - | - | - | - | 2 | 0 |  |
| T419 | 2 | 24 | 14172.9 | 68.1 | 152.5 | 17.8 | 15 | 0 | general-purpose 1, spec-fidelity 1 |
| T352 | 0 | 0 | - | - | - | - | 15 | 0 |  |
| T403 | 2 | 12 | 6585.7 | 30.0 | 0.0 | 0.0 | 15 | 0 | general-purpose 1, spec-fidelity 1 |
| T424 | 9 | 16 | 4603.3 | 45.3 | 91.5 | 12.9 | 15 | 0 | message-check 5, spec-fidelity 3, general-purpose 1 |
| T417 | 4 | 68 | 48051.4 | 164.9 | 572.1 | 36.7 | 15 | 0 | general-purpose 2, spec-fidelity 2 |
| T404 | 0 | 0 | - | - | - | - | 15 | 0 |  |
| T409 | 2 | 23 | 11018.3 | 55.0 | 134.5 | 8.0 | 13 | 0 | general-purpose 1, spec-fidelity 1 |
| T313 | 9 | 132 | 74942.2 | 401.0 | 1202.3 | 109.3 | 13 | 2 | general-purpose 4, spec-fidelity 4, round-arbiter 1 |
| T413 | 5 | 28 | 15653.9 | 81.3 | 204.2 | 26.4 | 13 | 0 | spec-fidelity 4, general-purpose 1 |
| T406 | 0 | 0 | - | - | - | - | 13 | 0 |  |
| T427 | 1 | 41 | 16798.9 | 60.3 | 283.5 | 18.7 | 12 | 0 | general-purpose 1 |
| T428 | 1 | 1 | 77.9 | 2.5 | 0.0 | 0.0 | 12 | 0 | spec-fidelity 1 |
| T369 | 3 | 32 | 13191.2 | 61.1 | 353.8 | 36.2 | 12 | 0 | spec-fidelity 2, general-purpose 1 |
| T364 | 4 | 41 | 16120.4 | 90.6 | 227.7 | 30.4 | 12 | 1 | spec-fidelity 3, general-purpose 1 |
| T365 | 2 | 39 | 16656.2 | 116.2 | 393.5 | 31.8 | 12 | 0 | general-purpose 2 |
| T373 | 1 | 50 | 15186.3 | 93.3 | 366.7 | 22.3 | 12 | 0 | general-purpose 1 |
| T341 | 1 | 3 | 136.8 | 9.0 | 36.9 | 8.0 | 12 | 0 | spec-fidelity 1 |
| T420 | 3 | 33 | 23029.1 | 110.2 | 396.6 | 37.9 | 12 | 0 | general-purpose 2, spec-fidelity 1 |
| T312 | 3 | 69 | 41808.8 | 144.5 | 369.7 | 26.3 | 11 | 0 | general-purpose 2, spec-fidelity 1 |
| T425 | 28 | 75 | 32527.0 | 273.2 | 955.0 | 65.8 | 11 | 0 | spec-fidelity 10, message-check 7, general-purpose 5, round-arbiter 4, escalation-check 2 |
| all | 1878 | 15320 | 8907233.4 | 44992.8 | 129686.7 | 13278.0 | 115 | 175 | |

the critical path: 11574 min of wall clock; beside it, the agents' own minutes summed: 15320 min over 1878 agents, 8907233.4k tokens in and 44992.8k out (0 with no count), the advisor's own 129686.7k in and 13278.0k out beside them (0 with no count); rework: 115 refused landings, 175 plan re-rounds (feature 451 T10, D7)

booked by: carried 11113 min, the mark 399 min, named 61 min (feature 385 T89: the task a call names, else the last named, else the mark)

the waits between turns on work, by what held them: a background shell 1533 min, an agent 3507 min, a monitor alone 35 min, none 408 min (feature 451 T09)

| task | runs | minutes | tests | compile | waiting on a build slot | hook suites | map generation | gate | land | review | docs | spec-kit step | other | in the background |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| - | 291 | 5.1 | 1.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 4.0 | 0.0 |
| T27 | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T28 | 109 | 10.7 | 6.4 | 0.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.7 | 0.0 | 0.0 | 2.8 | 1.8 |
| T24 | 44 | 13.5 | 2.4 | 1.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 10.1 | 10.0 |
| T15 | 152 | 44.5 | 19.3 | 11.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 13.3 | 26.6 |
| T29 | 4 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| T30 | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T16 | 127 | 25.4 | 11.6 | 5.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.0 | 8.4 | 5.5 |
| T17 | 107 | 12.1 | 2.9 | 3.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.0 | 5.0 | 7.0 |
| T19 | 154 | 21.5 | 8.2 | 1.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.1 | 11.4 | 13.1 |
| T32 | 185 | 74.2 | 11.3 | 4.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 58.3 | 57.2 |
| T37 | 53 | 1.3 | 0.8 | 0.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 |
| T35 | 40 | 3.2 | 1.6 | 0.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.3 | 1.2 |
| T40 | 134 | 74.8 | 14.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 60.2 | 57.3 |
| T41 | 61 | 6.4 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 5.9 | 0.5 |
| T42 | 167 | 41.5 | 10.2 | 2.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.1 | 28.7 | 29.1 |
| T46 | 177 | 12.6 | 6.4 | 2.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9 | 0.0 | 0.0 | 2.7 | 5.9 |
| T48 | 114 | 104.1 | 57.4 | 0.8 | 0.0 | 0.0 | 0.0 | 0.5 | 0.3 | 2.0 | 0.0 | 0.0 | 43.1 | 100.2 |
| T47 | 175 | 29.7 | 9.9 | 2.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9 | 0.0 | 0.0 | 16.7 | 24.5 |
| T07 | 71 | 20.4 | 6.4 | 5.3 | 0.0 | 0.0 | 0.0 | 1.6 | 0.3 | 0.2 | 0.0 | 0.0 | 6.6 | 19.3 |
| T36 | 114 | 0.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 0.4 | 0.0 |
| T53 | 104 | 11.9 | 8.5 | 1.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.0 | 1.6 | 0.7 |
| T10 | 186 | 28.3 | 10.0 | 4.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 1.3 | 0.0 | 12.8 | 27.8 |
| T66 | 87 | 9.8 | 5.0 | 1.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.0 | 3.1 | 9.4 |
| T59 | 119 | 14.4 | 5.0 | 2.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 6.7 | 13.7 |
| T64 | 101 | 15.2 | 4.1 | 2.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.0 | 8.6 | 13.1 |
| T63 | 110 | 7.9 | 3.1 | 1.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.0 | 3.3 | 6.9 |
| T68 | 105 | 12.2 | 5.3 | 1.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 5.5 | 10.9 |
| T69 | 118 | 23.2 | 4.2 | 4.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 1.0 | 0.0 | 13.7 | 19.7 |
| T70 | 83 | 21.8 | 9.4 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 12.0 | 19.5 |
| T60 | 60 | 3.7 | 2.6 | 0.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.2 | 3.4 |
| T67 | 356 | 35.2 | 14.0 | 2.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 18.8 | 27.7 |
| T75 | 4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T71 | 132 | 17.4 | 1.5 | 1.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 14.5 | 11.3 |
| T73 | 117 | 29.2 | 2.5 | 1.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 25.5 | 25.3 |
| T77 | 100 | 37.8 | 9.5 | 2.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.0 | 25.2 | 32.7 |
| T50 | 155 | 58.2 | 17.8 | 1.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 38.7 | 55.2 |
| T78 | 173 | 88.7 | 25.9 | 6.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.0 | 55.8 | 78.1 |
| T85 | 129 | 8.4 | 4.7 | 0.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 3.1 | 6.9 |
| T86 | 182 | 8.8 | 6.0 | 1.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 1.2 | 5.3 |
| T93 | 121 | 32.7 | 8.0 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 24.1 | 29.8 |
| T81 | 130 | 37.8 | 15.4 | 2.2 | 0.0 | 0.0 | 0.0 | 1.5 | 0.4 | 0.2 | 0.0 | 0.0 | 18.1 | 22.5 |
| T82 | 84 | 7.2 | 3.9 | 1.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 1.8 | 6.7 |
| T95 | 56 | 6.0 | 2.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 2.9 | 5.8 |
| T330 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T210 | 122 | 19.8 | 4.4 | 4.4 | 0.0 | 0.7 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 10.1 | 10.8 |
| T439 | 42 | 1.9 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.8 | 0.0 | 0.0 | 1.0 | 0.0 |
| T294 | 63 | 4.1 | 1.5 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.7 | 0.0 | 0.0 | 1.4 | 0.0 |
| T309 | 55 | 18.2 | 2.6 | 4.0 | 0.0 | 4.7 | 0.0 | 1.1 | 1.4 | 2.1 | 0.0 | 0.0 | 2.3 | 10.6 |
| T300 | 95 | 15.3 | 4.5 | 0.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.8 | 0.0 | 0.1 | 8.2 | 0.0 |
| T301 | 48 | 6.7 | 0.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.1 | 5.8 | 4.8 |
| T381 | 28 | 1.7 | 0.2 | 0.3 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.6 | 0.1 | 0.0 | 0.5 | 0.0 |
| T307 | 173 | 11.4 | 3.1 | 2.8 | 0.3 | 0.0 | 0.0 | 0.0 | 0.0 | 1.4 | 0.0 | 0.1 | 3.9 | 0.0 |
| T342 | 60 | 5.6 | 2.1 | 1.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 2.2 | 0.0 |
| T297 | 32 | 1.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 1.6 | 0.0 |
| T392 | 77 | 33.8 | 24.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.6 | 0.0 | 3.2 | 5.1 | 19.9 |
| T275 | 92 | 6.4 | 1.0 | 0.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.6 | 0.0 | 0.2 | 3.8 | 2.1 |
| T426 | 71 | 9.5 | 1.2 | 2.4 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.8 | 0.0 | 0.0 | 4.9 | 0.0 |
| T311 | 62 | 6.6 | 1.2 | 1.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.6 | 0.0 | 0.0 | 2.0 | 0.0 |
| T304 | 142 | 114.6 | 4.5 | 4.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.7 | 0.0 | 0.8 | 104.2 | 101.6 |
| T288 | 41 | 6.0 | 1.1 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.7 | 0.0 | 0.0 | 2.1 | 0.5 |
| T296 | 57 | 13.0 | 1.4 | 2.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.5 | 0.0 | 0.0 | 7.3 | 10.7 |
| T143 | 72 | 5.0 | 1.2 | 0.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 0.1 | 2.1 | 0.7 |
| T286 | 116 | 13.3 | 1.4 | 2.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 3.4 | 0.0 | 0.4 | 6.0 | 0.0 |
| T306 | 101 | 18.6 | 5.9 | 1.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 2.0 | 0.0 | 0.2 | 9.3 | 0.0 |
| T408 | 26 | 1.1 | 0.2 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.7 | 0.0 | 0.0 | 0.1 | 0.0 |
| T397 | 62 | 3.0 | 0.9 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.8 | 0.0 | 0.1 | 0.6 | 0.3 |
| T445 | 77 | 9.1 | 1.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.2 | 0.0 | 2.0 | 4.1 | 3.8 |
| T448 | 105 | 28.4 | 2.0 | 4.7 | 0.3 | 0.0 | 0.0 | 0.0 | 0.0 | 1.2 | 0.0 | 0.4 | 19.8 | 8.9 |
| T446 | 87 | 21.0 | 2.2 | 3.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 | 14.0 | 9.0 |
| T434 | 45 | 4.3 | 1.4 | 1.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.2 | 0.0 | 0.0 | 0.4 | 0.0 |
| T449 | 71 | 8.8 | 1.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 2.4 | 1.8 | 0.0 | 2.9 | 0.0 |
| T443 | 96 | 17.8 | 8.3 | 4.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.3 | 4.1 | 3.9 |
| T435 | 66 | 6.3 | 1.8 | 1.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.1 | 0.1 | 0.0 | 1.8 | 1.9 |
| T433 | 50 | 8.2 | 1.9 | 1.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.5 | 3.9 | 0.4 |
| T457 | 89 | 88.1 | 0.7 | 0.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.1 | 86.2 | 76.2 |
| T458 | 65 | 10.9 | 4.2 | 2.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.0 | 4.1 | 4.2 |
| T455 | 93 | 54.7 | 0.8 | 0.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 52.8 | 52.1 |
| T464 | 70 | 7.8 | 1.4 | 1.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 4.8 | 0.3 |
| T462 | 67 | 7.7 | 0.8 | 1.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 5.2 | 3.8 |
| T441 | 65 | 4.9 | 0.9 | 1.2 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 2.5 | 0.0 |
| T442 | 65 | 5.7 | 1.0 | 1.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.0 | 2.5 | 0.0 |
| T437 | 57 | 5.3 | 0.9 | 1.9 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 0.0 | 1.9 | 2.1 |
| T466 | 56 | 13.8 | 0.5 | 1.2 | 0.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9 | 0.0 | 0.0 | 10.8 | 1.2 |
| T444 | 58 | 15.5 | 3.4 | 3.4 | 1.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.8 | 0.0 | 0.0 | 6.7 | 2.3 |
| T459 | 5 | 0.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.6 | 0.0 | 0.0 | 0.0 | 0.0 |
| T452 | 44 | 11.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.6 | 0.0 | 0.0 | 10.7 | 4.0 |
| T463 | 71 | 24.1 | 5.2 | 5.6 | 0.0 | 1.0 | 0.3 | 3.3 | 3.2 | 0.6 | 0.0 | 0.4 | 4.4 | 16.9 |
| T465 | 122 | 21.8 | 2.8 | 3.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.7 | 0.0 | 0.3 | 14.7 | 0.0 |
| T384 | 49 | 8.4 | 0.5 | 0.5 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 1.1 | 0.0 | 0.0 | 6.1 | 1.5 |
| T451 | 3 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| T412 | 47 | 9.5 | 1.6 | 1.5 | 0.0 | 0.7 | 0.2 | 0.6 | 1.0 | 0.5 | 0.0 | 0.1 | 3.4 | 2.8 |
| T430 | 33 | 6.9 | 0.6 | 0.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.4 | 0.0 | 0.0 | 4.1 | 0.0 |
| T431 | 59 | 15.5 | 4.8 | 5.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.1 | 0.0 | 0.1 | 3.6 | 5.9 |
| T477 | 49 | 4.5 | 1.0 | 1.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.7 | 0.9 | 0.0 |
| T478 | 56 | 13.4 | 2.1 | 3.0 | 0.0 | 2.4 | 0.2 | 2.3 | 1.3 | 0.8 | 0.0 | 0.0 | 1.2 | 9.1 |
| T475 | 17 | 0.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 0.0 | 0.1 | 0.0 |
| T353 | 85 | 18.5 | 1.5 | 2.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9 | 0.0 | 0.0 | 13.6 | 7.1 |
| T310 | 66 | 5.9 | 0.8 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.6 | 0.0 | 0.0 | 3.6 | 0.0 |
| T360 | 1 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| T387 | 86 | 9.2 | 2.3 | 2.6 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.1 | 4.0 | 0.0 |
| T386 | 49 | 6.4 | 0.3 | 1.0 | 0.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 4.6 | 2.3 |
| T483 | 51 | 6.3 | 0.4 | 1.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.0 | 4.3 | 1.4 |
| T388 | 87 | 11.9 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.2 | 11.0 | 8.6 |
| T485 | 45 | 2.4 | 0.7 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.5 | 0.8 | 0.0 |
| T487 | 99 | 4.8 | 1.4 | 1.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.2 | 1.2 | 0.0 |
| T489 | 76 | 9.5 | 2.9 | 3.7 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.2 | 2.0 | 0.0 |
| T495 | 79 | 6.1 | 0.6 | 1.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.6 | 0.0 | 0.0 | 3.0 | 3.3 |
| T499 | 25 | 1.9 | 0.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.7 | 0.0 | 0.0 | 0.5 | 0.0 |
| T501 | 79 | 5.9 | 1.1 | 1.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.7 | 0.3 | 0.1 | 2.1 | 0.0 |
| T497 | 65 | 8.4 | 1.4 | 1.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 5.0 | 0.5 |
| T490 | 87 | 18.6 | 3.9 | 5.4 | 0.0 | 0.0 | 0.2 | 3.0 | 2.4 | 0.4 | 0.0 | 0.5 | 2.8 | 10.1 |
| T496 | 53 | 9.4 | 0.8 | 2.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 6.1 | 4.7 |
| T500 | 61 | 15.9 | 2.6 | 3.5 | 0.0 | 2.0 | 0.2 | 2.2 | 1.5 | 0.3 | 0.0 | 0.3 | 3.3 | 12.4 |
| T470 | 98 | 9.1 | 3.9 | 1.7 | 0.1 | 0.0 | 0.1 | 0.2 | 0.8 | 0.5 | 0.0 | 0.0 | 1.8 | 2.0 |
| T504 | 65 | 5.1 | 0.2 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.0 | 4.0 | 2.6 |
| T505 | 90 | 9.2 | 1.0 | 1.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.4 | 0.0 | 0.2 | 5.9 | 3.1 |
| T507 | 65 | 3.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.3 | 2.8 | 1.0 |
| T508 | 98 | 12.5 | 1.7 | 3.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 0.2 | 6.3 | 0.3 |
| T510 | 71 | 4.7 | 0.7 | 1.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 1.3 | 0.1 | 0.7 | 1.6 |
| T512 | 203 | 34.1 | 2.5 | 6.7 | 0.0 | 1.0 | 0.1 | 0.4 | 0.6 | 0.6 | 9.8 | 0.1 | 12.4 | 17.4 |
| T515 | 116 | 15.8 | 1.3 | 1.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9 | 0.0 | 0.1 | 11.9 | 4.9 |
| T520 | 126 | 48.6 | 0.8 | 3.8 | 0.0 | 0.0 | 0.1 | 0.2 | 0.8 | 0.2 | 0.0 | 0.2 | 42.6 | 42.7 |
| T521 | 51 | 10.9 | 0.9 | 4.1 | 0.0 | 0.0 | 0.1 | 0.4 | 1.2 | 0.5 | 3.1 | 0.0 | 0.6 | 5.3 |
| T522 | 116 | 10.6 | 1.3 | 2.4 | 0.0 | 0.0 | 0.2 | 0.4 | 0.8 | 0.6 | 3.6 | 0.1 | 1.2 | 2.5 |
| T530 | 66 | 9.3 | 2.2 | 3.1 | 0.0 | 0.6 | 0.1 | 0.2 | 1.5 | 0.6 | 0.0 | 0.0 | 0.9 | 3.0 |
| T531 | 105 | 13.2 | 2.4 | 4.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 1.2 | 0.0 | 4.2 | 0.0 |
| T526 | 39 | 2.6 | 0.7 | 1.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 0.4 | 0.0 |
| T523 | 94 | 7.9 | 0.6 | 2.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.2 | 0.2 | 0.0 | 3.8 | 1.9 |
| T517 | 50 | 6.4 | 0.7 | 1.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.2 | 4.1 | 0.0 |
| T535 | 24 | 2.5 | 1.5 | 0.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 0.4 | 0.0 |
| T513 | 113 | 22.2 | 0.8 | 4.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 8.7 | 0.0 | 8.3 | 14.2 |
| T537 | 264 | 32.8 | 7.6 | 11.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 2.5 | 10.9 | 12.9 |
| T358 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T379 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T371 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T211 | 3 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T012 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T257 | 12 | 0.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.0 | 0.0 | 0.0 |
| T255 | 5 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| T454 | 33 | 4.8 | 1.4 | 0.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.7 | 0.0 | 0.0 | 1.0 | 0.3 |
| T436 | 2 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| T460 | 53 | 3.4 | 0.6 | 1.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.2 | 0.0 | 1.3 | 1.0 |
| T450 | 5 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T440 | 10 | 0.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.0 | 0.1 | 0.0 |
| T438 | 77 | 14.5 | 6.4 | 1.6 | 2.8 | 0.0 | 0.0 | 0.0 | 0.0 | 1.6 | 0.0 | 0.7 | 1.4 | 3.9 |
| T453 | 76 | 15.1 | 2.1 | 4.1 | 0.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9 | 0.0 | 0.0 | 7.4 | 8.8 |
| T467 | 93 | 11.3 | 3.5 | 4.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9 | 0.0 | 0.0 | 2.9 | 0.0 |
| T469 | 46 | 5.8 | 2.1 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.0 | 2.5 | 0.9 |
| T472 | 9 | 0.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.2 | 0.0 |
| T479 | 97 | 13.1 | 2.2 | 4.2 | 0.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.1 | 5.8 | 7.6 |
| T473 | 7 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 |
| T482 | 61 | 6.4 | 0.7 | 1.9 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.8 | 0.0 | 0.0 | 2.9 | 3.0 |
| T481 | 6 | 0.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.0 | 0.1 | 0.0 |
| T480 | 6 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.1 | 0.0 |
| T447 | 7 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| T491 | 82 | 6.0 | 1.5 | 2.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.0 | 2.2 | 0.3 |
| T488 | 13 | 0.9 | 0.1 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.7 | 0.0 | 0.0 | 0.1 | 0.0 |
| T492 | 9 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| T494 | 4 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| T363 | 14 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.1 | 0.0 |
| T506 | 9 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| T519 | 63 | 3.7 | 0.4 | 0.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.0 | 2.2 | 0.0 |
| T528 | 71 | 6.3 | 2.0 | 1.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 1.2 | 0.0 | 1.2 | 0.0 |
| T536 | 161 | 139.6 | 0.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.0 | 138.9 | 84.7 |
| T532 | 4 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| T356 | 1 | 1.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T393 | 1 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 |
| T474 | 1 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| T468 | 2 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 |
| T432 | 2 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| T456 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T493 | 2 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| T01 | 1 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 |
| T02 | 121 | 13.9 | 6.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 7.4 | 0.0 |
| T23 | 85 | 3.5 | 2.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 1.1 | 0.0 |
| T03 | 74 | 9.6 | 8.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.7 | 0.0 |
| T26 | 110 | 8.4 | 7.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9 | 0.0 |
| T25 | 105 | 9.8 | 8.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9 | 0.0 | 0.0 | 0.5 | 0.0 |
| T04 | 106 | 12.5 | 11.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.0 | 0.1 | 0.5 | 0.3 |
| T05 | 113 | 10.7 | 6.8 | 2.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.6 | 0.0 | 0.0 | 1.0 | 0.3 |
| T06 | 123 | 12.6 | 4.4 | 3.9 | 0.0 | 0.0 | 0.0 | 0.8 | 0.0 | 2.7 | 0.0 | 0.4 | 0.6 | 1.3 |
| T18 | 68 | 45.9 | 3.2 | 3.3 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 0.5 | 2.7 | 0.1 | 35.7 | 39.3 |
| T14 | 133 | 57.9 | 11.9 | 11.3 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 0.5 | 0.0 | 0.6 | 32.6 | 42.9 |
| T12 | 168 | 21.3 | 5.2 | 3.3 | 0.0 | 0.0 | 0.0 | 0.9 | 0.3 | 0.3 | 0.0 | 0.2 | 11.1 | 17.6 |
| T13 | 123 | 32.6 | 10.0 | 5.9 | 0.0 | 0.0 | 0.0 | 0.4 | 0.3 | 0.1 | 0.0 | 0.2 | 15.6 | 26.4 |
| T20 | 151 | 63.4 | 21.0 | 0.2 | 0.0 | 0.0 | 0.0 | 0.4 | 0.3 | 0.1 | 0.0 | 0.1 | 41.3 | 51.1 |
| T21 | 177 | 173.8 | 30.9 | 0.1 | 0.0 | 0.0 | 0.0 | 0.3 | 0.3 | 0.1 | 0.0 | 0.2 | 142.0 | 154.3 |
| T39 | 69 | 2.5 | 0.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.3 | 0.0 | 0.0 | 0.1 | 1.2 | 1.1 |
| T31 | 256 | 60.2 | 10.3 | 12.6 | 0.0 | 0.0 | 0.0 | 0.6 | 0.3 | 0.2 | 0.0 | 0.6 | 35.6 | 43.7 |
| T34 | 71 | 11.4 | 5.1 | 2.9 | 0.0 | 0.0 | 0.0 | 1.1 | 1.2 | 0.5 | 0.0 | 0.0 | 0.8 | 9.5 |
| T43 | 225 | 50.6 | 7.1 | 6.4 | 0.0 | 0.0 | 0.0 | 0.9 | 0.4 | 0.1 | 0.0 | 0.5 | 35.1 | 43.4 |
| T38 | 321 | 51.1 | 10.3 | 11.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.3 | 0.0 | 0.0 | 0.1 | 28.9 | 39.1 |
| T44 | 123 | 64.0 | 12.2 | 9.6 | 0.0 | 0.0 | 0.0 | 1.2 | 0.3 | 0.3 | 0.0 | 0.6 | 39.8 | 59.8 |
| T45 | 105 | 111.8 | 14.4 | 6.7 | 0.0 | 0.0 | 0.0 | 0.2 | 0.3 | 0.0 | 0.0 | 0.0 | 90.2 | 98.0 |
| T33 | 459 | 120.1 | 16.6 | 9.9 | 0.0 | 0.0 | 0.0 | 0.1 | 0.1 | 0.1 | 0.0 | 0.2 | 93.1 | 112.8 |
| T08 | 235 | 10.7 | 2.9 | 5.5 | 0.0 | 0.0 | 0.0 | 0.3 | 0.3 | 0.1 | 0.1 | 0.5 | 1.0 | 4.8 |
| T09 | 184 | 26.7 | 6.9 | 9.2 | 0.0 | 0.0 | 0.0 | 1.2 | 0.4 | 0.3 | 0.6 | 0.2 | 8.0 | 21.9 |
| T55 | 274 | 35.6 | 12.9 | 10.0 | 0.0 | 0.0 | 0.0 | 1.3 | 0.4 | 0.1 | 0.0 | 0.2 | 10.7 | 15.1 |
| T57 | 215 | 28.6 | 12.9 | 7.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.4 | 7.0 | 25.4 |
| T62 | 117 | 23.0 | 12.5 | 2.5 | 0.0 | 0.0 | 0.0 | 0.3 | 0.3 | 0.2 | 0.0 | 0.0 | 7.0 | 20.2 |
| T58 | 335 | 96.1 | 32.6 | 19.4 | 0.0 | 0.0 | 0.0 | 1.1 | 0.3 | 0.2 | 0.0 | 0.5 | 42.0 | 86.5 |
| T11 | 263 | 96.7 | 14.0 | 0.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 8.9 | 0.1 | 72.6 | 90.3 |
| T65 | 119 | 26.9 | 6.4 | 9.6 | 0.0 | 0.0 | 0.0 | 0.6 | 0.3 | 0.2 | 0.0 | 0.0 | 9.7 | 25.1 |
| T56 | 93 | 15.8 | 4.9 | 1.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.3 | 0.3 | 0.0 | 0.0 | 9.1 | 13.4 |
| T61 | 213 | 10.4 | 3.5 | 2.3 | 0.0 | 0.0 | 0.0 | 0.3 | 0.3 | 0.2 | 0.0 | 0.0 | 3.7 | 9.1 |
| T54 | 180 | 23.1 | 4.0 | 2.5 | 0.0 | 0.0 | 0.0 | 0.2 | 0.3 | 0.0 | 0.0 | 0.1 | 15.9 | 18.9 |
| T72 | 64 | 3.0 | 1.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.3 | 0.1 | 0.0 | 0.0 | 0.7 | 2.3 |
| T74 | 122 | 12.1 | 6.9 | 3.2 | 0.0 | 0.0 | 0.0 | 0.2 | 0.3 | 0.1 | 0.2 | 0.0 | 1.0 | 10.9 |
| T76 | 102 | 21.0 | 8.9 | 1.9 | 0.0 | 0.0 | 0.0 | 0.2 | 0.3 | 0.5 | 1.8 | 0.1 | 7.3 | 18.6 |
| T79 | 627 | 197.8 | 20.1 | 12.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.6 | 0.4 | 164.3 | 167.4 |
| T84 | 310 | 56.1 | 5.1 | 4.6 | 0.0 | 0.0 | 0.0 | 0.4 | 0.7 | 0.1 | 0.0 | 0.0 | 45.2 | 53.4 |
| T88 | 270 | 42.3 | 12.3 | 3.7 | 0.0 | 0.0 | 0.0 | 22.8 | 0.0 | 0.0 | 0.0 | 0.1 | 3.4 | 37.1 |
| T97 | 227 | 20.9 | 7.9 | 2.6 | 0.0 | 0.0 | 0.0 | 3.6 | 1.0 | 0.4 | 0.0 | 0.0 | 5.4 | 15.5 |
| T101 | 184 | 23.0 | 5.2 | 3.9 | 0.0 | 0.0 | 0.0 | 1.8 | 0.6 | 0.2 | 0.0 | 0.1 | 11.3 | 21.1 |
| T102 | 162 | 40.4 | 17.7 | 1.9 | 0.0 | 0.0 | 0.0 | 15.9 | 3.3 | 0.3 | 0.0 | 0.0 | 1.3 | 38.8 |
| T103 | 211 | 141.4 | 5.9 | 1.6 | 0.0 | 0.0 | 0.0 | 8.0 | 2.1 | 0.2 | 0.0 | 0.0 | 123.7 | 130.5 |
| T99 | 228 | 63.7 | 0.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9 | 0.4 | 2.0 | 0.0 | 0.0 | 59.9 | 58.2 |
| T96 | 386 | 144.8 | 37.6 | 9.4 | 0.0 | 0.0 | 0.0 | 8.9 | 1.1 | 0.1 | 0.0 | 0.3 | 87.4 | 136.3 |
| T92 | 175 | 31.7 | 9.7 | 8.4 | 0.0 | 0.0 | 0.0 | 7.6 | 1.6 | 0.1 | 0.0 | 0.0 | 4.3 | 27.7 |
| T108 | 151 | 32.9 | 12.1 | 2.8 | 0.0 | 0.0 | 0.0 | 5.6 | 0.6 | 0.1 | 0.0 | 0.2 | 11.6 | 31.3 |
| T49 | 135 | 23.0 | 3.2 | 2.7 | 0.0 | 0.0 | 0.0 | 0.8 | 1.1 | 0.1 | 0.0 | 0.1 | 15.0 | 17.5 |
| T113 | 250 | 56.8 | 15.8 | 3.6 | 0.0 | 0.0 | 0.0 | 4.0 | 0.5 | 0.1 | 0.0 | 0.0 | 32.7 | 53.9 |
| T111 | 88 | 18.1 | 11.4 | 1.2 | 0.0 | 0.0 | 0.0 | 0.4 | 0.3 | 0.0 | 0.0 | 0.1 | 4.7 | 17.1 |
| T106 | 181 | 33.0 | 9.7 | 4.0 | 0.0 | 0.0 | 0.0 | 6.1 | 0.6 | 0.1 | 0.0 | 0.0 | 12.4 | 31.5 |
| T112 | 253 | 65.1 | 8.1 | 2.2 | 0.0 | 0.0 | 0.0 | 2.5 | 0.6 | 0.1 | 0.0 | 0.0 | 51.6 | 63.4 |
| T114 | 156 | 9.7 | 2.5 | 0.9 | 0.0 | 0.0 | 0.0 | 0.7 | 0.4 | 0.1 | 0.0 | 0.0 | 5.1 | 3.1 |
| T51 | 145 | 6.2 | 0.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 | 4.4 | 4.4 |
| T110 | 292 | 173.3 | 41.9 | 5.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 3.0 | 0.0 | 0.2 | 122.9 | 136.8 |
| T80 | 139 | 80.6 | 24.8 | 8.2 | 0.0 | 0.0 | 0.0 | 18.8 | 2.0 | 0.2 | 0.0 | 0.5 | 26.1 | 65.1 |
| T83 | 505 | 389.7 | 30.5 | 5.2 | 0.0 | 0.0 | 0.0 | 8.0 | 1.7 | 0.4 | 0.0 | 0.4 | 343.4 | 336.8 |
| T87 | 521 | 250.6 | 35.9 | 5.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 0.3 | 208.1 | 209.1 |
| T122 | 4 | 0.6 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 0.0 |
| T123 | 309 | 127.8 | 16.4 | 11.8 | 0.0 | 0.0 | 0.0 | 12.5 | 2.5 | 0.2 | 0.0 | 0.0 | 84.5 | 118.5 |
| T105 | 154 | 18.1 | 3.0 | 4.2 | 0.0 | 0.0 | 0.0 | 2.6 | 0.4 | 0.1 | 0.0 | 0.0 | 7.7 | 10.2 |
| T118 | 384 | 138.7 | 21.2 | 10.6 | 0.0 | 0.0 | 0.0 | 11.0 | 3.7 | 1.2 | 0.0 | 8.6 | 82.5 | 95.9 |
| T89 | 346 | 217.1 | 61.0 | 2.5 | 0.0 | 0.0 | 0.0 | 8.4 | 1.3 | 0.6 | 0.0 | 0.5 | 142.7 | 196.7 |
| T129 | 259 | 124.6 | 12.2 | 1.5 | 0.0 | 0.0 | 0.0 | 12.0 | 1.4 | 1.0 | 0.0 | 0.0 | 96.4 | 118.9 |
| T115 | 149 | 74.9 | 1.9 | 1.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.1 | 71.6 | 64.7 |
| T91 | 209 | 239.3 | 62.0 | 2.1 | 0.0 | 0.0 | 0.0 | 27.5 | 5.3 | 4.5 | 0.0 | 0.6 | 137.2 | 200.1 |
| T94 | 153 | 217.6 | 40.7 | 5.1 | 0.0 | 0.0 | 0.0 | 8.8 | 3.6 | 6.3 | 0.0 | 0.3 | 152.8 | 196.6 |
| T142 | 139 | 153.8 | 27.8 | 10.9 | 0.0 | 0.0 | 0.0 | 3.0 | 5.9 | 0.3 | 0.0 | 4.5 | 101.4 | 100.2 |
| T141 | 364 | 133.4 | 96.9 | 8.5 | 0.0 | 0.0 | 0.0 | 0.0 | 1.3 | 0.9 | 2.0 | 0.6 | 23.3 | 125.0 |
| T147 | 86 | 8.2 | 2.8 | 0.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 4.6 | 3.6 |
| T151 | 101 | 31.5 | 2.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.1 | 29.0 | 24.0 |
| T153 | 235 | 74.1 | 8.4 | 8.0 | 0.0 | 2.1 | 0.2 | 0.9 | 3.0 | 41.0 | 3.0 | 0.0 | 7.5 | 14.7 |
| T157 | 62 | 7.3 | 1.6 | 4.1 | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.4 | 4.8 |
| T158 | 201 | 36.0 | 11.6 | 12.5 | 0.0 | 4.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.6 | 0.0 | 7.0 | 11.4 |
| T98 | 382 | 50.0 | 0.2 | 0.3 | 0.0 | 0.4 | 0.4 | 0.2 | 0.7 | 27.7 | 1.0 | 0.0 | 19.1 | 4.3 |
| T156 | 53 | 48.4 | 3.9 | 13.8 | 0.0 | 2.8 | 0.1 | 0.4 | 2.5 | 0.2 | 0.0 | 0.0 | 24.6 | 23.0 |
| T154 | 335 | 139.1 | 5.7 | 26.1 | 0.0 | 0.0 | 0.1 | 0.3 | 1.3 | 0.0 | 0.1 | 0.0 | 105.5 | 85.3 |
| T155 | 166 | 112.3 | 6.3 | 29.8 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.3 | 0.0 | 0.0 | 75.5 | 75.7 |
| T160 | 380 | 30.4 | 4.6 | 3.1 | 0.0 | 0.8 | 0.0 | 0.3 | 0.9 | 0.8 | 0.0 | 0.1 | 19.9 | 26.7 |
| T164 | 229 | 29.3 | 3.1 | 6.3 | 0.0 | 2.2 | 0.4 | 7.0 | 0.0 | 0.1 | 0.1 | 0.0 | 10.1 | 20.3 |
| T90 | 65 | 14.0 | 4.1 | 5.3 | 0.0 | 0.2 | 0.1 | 0.3 | 2.3 | 0.2 | 0.0 | 0.0 | 1.4 | 9.1 |
| T167 | 110 | 35.4 | 3.0 | 2.1 | 0.0 | 0.9 | 0.0 | 0.0 | 0.3 | 0.1 | 0.0 | 0.0 | 29.0 | 33.5 |
| T169 | 173 | 5.0 | 0.9 | 0.9 | 0.0 | 0.4 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 2.8 | 2.7 |
| T168 | 44 | 13.3 | 1.4 | 5.4 | 0.0 | 1.6 | 0.1 | 2.4 | 1.4 | 0.3 | 0.4 | 0.0 | 0.4 | 10.3 |
| T171 | 272 | 45.5 | 17.7 | 5.9 | 0.0 | 3.2 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 18.6 | 40.1 |
| T170 | 1057 | 103.8 | 15.9 | 25.9 | 0.0 | 11.6 | 0.2 | 0.4 | 2.8 | 2.5 | 0.0 | 0.3 | 44.1 | 88.4 |
| T176 | 15 | 0.3 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.1 | 0.0 |
| T175 | 111 | 14.4 | 2.9 | 2.5 | 0.0 | 3.4 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.0 | 5.2 | 12.5 |
| T180 | 89 | 11.0 | 4.1 | 3.5 | 0.0 | 1.2 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.0 | 1.8 | 8.9 |
| T100 | 98 | 4.0 | 0.6 | 0.1 | 0.0 | 0.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 2.8 | 2.4 |
| T177 | 455 | 40.4 | 7.4 | 11.0 | 0.0 | 6.6 | 0.0 | 0.0 | 1.4 | 0.8 | 0.0 | 0.0 | 13.3 | 31.8 |
| T179 | 357 | 43.8 | 6.5 | 12.8 | 0.0 | 1.7 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 22.5 | 40.5 |
| T182 | 8 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T174 | 262 | 52.0 | 12.6 | 7.1 | 0.0 | 4.0 | 0.1 | 0.4 | 1.9 | 0.4 | 0.0 | 0.0 | 25.3 | 44.2 |
| T165 | 162 | 17.9 | 6.5 | 0.5 | 0.0 | 1.3 | 0.0 | 0.1 | 0.7 | 0.5 | 0.0 | 0.0 | 8.2 | 7.3 |
| T172 | 5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T183 | 311 | 97.4 | 8.0 | 14.5 | 0.0 | 4.1 | 0.1 | 1.8 | 1.3 | 0.3 | 0.0 | 0.0 | 67.2 | 26.0 |
| T184 | 438 | 142.9 | 11.1 | 4.1 | 0.0 | 1.7 | 0.1 | 0.3 | 1.8 | 11.8 | 1.7 | 0.0 | 110.3 | 116.8 |
| T188 | 165 | 19.2 | 3.9 | 8.0 | 0.0 | 2.4 | 0.1 | 0.4 | 1.1 | 0.3 | 0.0 | 0.0 | 2.9 | 15.3 |
| T190 | 66 | 0.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 |
| T185 | 279 | 34.2 | 3.6 | 3.6 | 0.0 | 1.3 | 0.2 | 0.4 | 2.0 | 0.6 | 14.6 | 0.1 | 7.9 | 13.1 |
| T186 | 156 | 2.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.0 | 2.2 | 0.0 |
| T187 | 194 | 59.9 | 5.9 | 7.2 | 0.0 | 2.0 | 0.1 | 0.5 | 1.8 | 41.5 | 0.0 | 0.0 | 0.8 | 16.4 |
| T191 | 108 | 17.0 | 0.5 | 1.5 | 0.0 | 0.6 | 0.0 | 0.0 | 0.0 | 12.3 | 0.0 | 0.0 | 2.0 | 1.5 |
| T193 | 282 | 39.9 | 21.3 | 6.8 | 0.0 | 2.3 | 0.1 | 0.5 | 2.1 | 0.3 | 0.0 | 0.0 | 6.5 | 36.1 |
| T194 | 342 | 22.8 | 3.0 | 4.2 | 0.0 | 2.2 | 0.1 | 0.4 | 1.1 | 0.0 | 0.0 | 0.0 | 11.7 | 18.6 |
| T196 | 116 | 18.3 | 9.5 | 6.3 | 0.0 | 1.6 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.0 | 0.6 | 9.8 |
| T195 | 207 | 31.5 | 9.9 | 10.0 | 0.0 | 2.2 | 0.2 | 0.5 | 2.8 | 1.5 | 0.0 | 0.2 | 4.2 | 18.9 |
| T192 | 452 | 420.9 | 22.0 | 4.6 | 0.0 | 2.9 | 0.0 | 0.3 | 0.7 | 2.7 | 0.1 | 1.3 | 386.3 | 183.1 |
| T197 | 15 | 0.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 0.6 | 0.0 |
| T198 | 294 | 39.0 | 9.3 | 8.4 | 0.0 | 2.4 | 0.0 | 0.0 | 0.0 | 0.9 | 11.5 | 0.1 | 6.4 | 14.0 |
| T199 | 3 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 |
| T202 | 226 | 3.5 | 1.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9 | 0.0 | 0.0 | 1.4 | 0.0 |
| T204 | 77 | 10.1 | 2.8 | 1.2 | 0.0 | 2.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.1 | 3.8 | 5.7 |
| T201 | 178 | 315.4 | 5.7 | 2.7 | 0.0 | 4.9 | 0.1 | 0.2 | 0.9 | 0.1 | 186.5 | 0.0 | 114.2 | 117.8 |
| T207 | 168 | 85.2 | 7.9 | 6.6 | 0.0 | 1.5 | 0.1 | 1.4 | 0.7 | 0.2 | 42.4 | 0.0 | 24.3 | 26.3 |
| T214 | 70 | 11.2 | 3.1 | 4.5 | 0.0 | 1.9 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.0 | 1.4 | 4.5 |
| T209 | 102 | 15.4 | 3.8 | 2.9 | 0.0 | 0.4 | 0.0 | 0.1 | 1.3 | 0.3 | 0.0 | 0.0 | 6.6 | 10.4 |
| T213 | 27 | 0.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.2 | 0.1 | 0.0 |
| T212 | 22 | 0.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.5 | 0.0 |
| T215 | 106 | 7.2 | 0.7 | 2.2 | 0.0 | 0.4 | 0.1 | 0.1 | 0.6 | 0.1 | 0.0 | 0.0 | 3.0 | 3.9 |
| T216 | 83 | 9.2 | 1.9 | 1.4 | 0.0 | 1.6 | 0.1 | 0.5 | 0.4 | 0.1 | 0.0 | 0.0 | 3.3 | 7.1 |
| T217 | 88 | 7.0 | 2.2 | 1.0 | 0.0 | 2.2 | 0.1 | 0.1 | 0.4 | 0.2 | 0.0 | 0.2 | 0.5 | 4.8 |
| T221 | 48 | 2.8 | 1.2 | 0.6 | 0.0 | 0.8 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.1 | 1.4 |
| T219 | 145 | 12.3 | 5.1 | 4.4 | 0.0 | 1.5 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 0.0 | 0.9 | 3.6 |
| T218 | 39 | 13.0 | 1.4 | 2.6 | 0.0 | 0.5 | 0.2 | 3.1 | 5.0 | 0.1 | 0.0 | 0.0 | 0.0 | 12.8 |
| T220 | 59 | 3.3 | 1.1 | 0.2 | 0.0 | 0.4 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.1 | 1.2 | 1.7 |
| T222 | 6 | 0.3 | 0.1 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 |
| T223 | 190 | 9.2 | 2.7 | 1.2 | 0.0 | 0.8 | 0.0 | 0.0 | 0.0 | 3.2 | 0.0 | 0.0 | 1.3 | 1.6 |
| T224 | 61 | 6.2 | 1.6 | 1.9 | 0.0 | 1.1 | 0.0 | 0.0 | 0.0 | 0.8 | 0.0 | 0.0 | 0.7 | 3.6 |
| T225 | 235 | 139.7 | 6.0 | 2.4 | 0.0 | 0.5 | 0.0 | 0.0 | 0.0 | 45.6 | 22.7 | 0.5 | 62.0 | 59.8 |
| T236 | 202 | 13.1 | 3.1 | 5.0 | 0.0 | 1.2 | 0.2 | 0.3 | 0.6 | 1.0 | 0.0 | 0.0 | 1.6 | 5.6 |
| T230 | 68 | 4.3 | 0.9 | 0.3 | 0.0 | 0.9 | 0.0 | 0.0 | 0.7 | 0.5 | 0.0 | 0.0 | 1.0 | 2.6 |
| T238 | 55 | 8.5 | 1.5 | 3.8 | 0.0 | 0.3 | 0.7 | 0.5 | 0.4 | 0.4 | 0.0 | 0.0 | 0.9 | 6.9 |
| T240 | 130 | 20.1 | 6.7 | 6.6 | 0.0 | 3.0 | 0.1 | 0.2 | 0.6 | 0.9 | 0.0 | 0.1 | 1.9 | 14.0 |
| T237 | 95 | 7.4 | 1.5 | 0.9 | 0.0 | 1.6 | 0.1 | 0.2 | 0.6 | 0.5 | 0.4 | 0.0 | 1.5 | 3.7 |
| T241 | 94 | 4.7 | 0.9 | 0.6 | 0.0 | 1.0 | 0.1 | 0.2 | 0.6 | 0.5 | 0.0 | 0.0 | 0.7 | 3.1 |
| T226 | 169 | 14.3 | 2.2 | 4.3 | 0.0 | 1.9 | 0.2 | 0.3 | 0.7 | 1.7 | 0.0 | 0.0 | 3.0 | 6.4 |
| T243 | 609 | 82.6 | 19.1 | 24.7 | 0.0 | 5.2 | 0.1 | 0.2 | 0.7 | 3.0 | 16.8 | 0.2 | 12.6 | 31.4 |
| T244 | 123 | 14.5 | 4.4 | 3.3 | 0.0 | 3.3 | 0.1 | 0.3 | 0.6 | 0.9 | 0.0 | 0.0 | 1.5 | 10.3 |
| T228 | 118 | 64.1 | 13.4 | 11.1 | 0.0 | 4.9 | 0.1 | 1.6 | 1.1 | 0.9 | 0.0 | 2.1 | 28.8 | 46.7 |
| T234 | 228 | 62.8 | 6.6 | 11.9 | 0.0 | 4.9 | 0.0 | 0.0 | 0.0 | 1.6 | 0.0 | 2.4 | 35.4 | 43.5 |
| T235 | 112 | 57.8 | 35.3 | 9.5 | 0.0 | 6.4 | 0.2 | 0.3 | 0.8 | 0.5 | 0.0 | 0.0 | 4.8 | 50.6 |
| T242 | 78 | 32.9 | 4.1 | 19.7 | 0.0 | 4.5 | 0.0 | 0.3 | 0.8 | 0.6 | 0.0 | 2.1 | 0.9 | 29.6 |
| T245 | 99 | 45.2 | 24.2 | 3.2 | 0.0 | 6.7 | 0.4 | 0.9 | 1.4 | 1.1 | 0.1 | 2.7 | 4.6 | 34.2 |
| T231 | 127 | 44.9 | 4.3 | 29.5 | 0.0 | 0.3 | 0.1 | 0.6 | 1.3 | 1.2 | 0.0 | 0.3 | 7.2 | 32.5 |
| T229 | 125 | 118.2 | 58.0 | 17.8 | 0.0 | 8.4 | 0.1 | 1.7 | 1.5 | 2.3 | 0.3 | 1.4 | 26.6 | 110.7 |
| T227 | 129 | 91.0 | 15.1 | 23.9 | 0.0 | 7.3 | 0.2 | 2.0 | 2.8 | 3.0 | 0.0 | 2.7 | 33.9 | 67.8 |
| T232 | 215 | 82.7 | 21.8 | 22.6 | 0.0 | 4.0 | 0.1 | 0.4 | 1.4 | 2.3 | 0.6 | 2.8 | 26.6 | 62.4 |
| T247 | 35 | 23.4 | 16.3 | 0.0 | 0.0 | 2.7 | 0.0 | 0.1 | 1.4 | 0.3 | 0.0 | 0.0 | 2.6 | 20.4 |
| T246 | 160 | 76.2 | 7.8 | 17.4 | 0.0 | 6.1 | 0.1 | 4.0 | 1.2 | 0.6 | 0.0 | 0.1 | 38.9 | 68.9 |
| T233 | 89 | 26.9 | 9.3 | 11.5 | 0.0 | 3.5 | 0.1 | 0.3 | 0.8 | 0.4 | 0.0 | 0.0 | 1.1 | 21.8 |
| T249 | 85 | 45.8 | 10.0 | 8.4 | 0.0 | 2.5 | 0.2 | 0.5 | 1.3 | 0.5 | 0.0 | 0.0 | 22.4 | 36.9 |
| T248 | 85 | 33.8 | 9.6 | 11.4 | 0.0 | 4.5 | 0.2 | 1.4 | 1.6 | 0.6 | 0.0 | 0.1 | 4.3 | 21.0 |
| T252 | 48 | 4.8 | 0.6 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.8 | 0.1 | 0.0 | 0.0 | 2.9 | 1.7 |
| T253 | 386 | 12.8 | 1.3 | 1.3 | 0.0 | 1.6 | 0.1 | 0.2 | 0.9 | 0.6 | 0.0 | 0.2 | 6.6 | 5.6 |
| T256 | 117 | 28.1 | 11.1 | 8.9 | 0.0 | 4.0 | 0.1 | 1.4 | 1.2 | 0.4 | 0.0 | 0.0 | 1.0 | 21.0 |
| T254 | 259 | 54.5 | 23.6 | 11.3 | 0.0 | 6.0 | 0.2 | 1.9 | 3.2 | 0.7 | 0.0 | 0.2 | 7.4 | 33.2 |
| T259 | 273 | 13.8 | 2.3 | 3.9 | 0.0 | 1.9 | 0.1 | 0.2 | 0.9 | 1.3 | 0.0 | 0.2 | 2.9 | 6.0 |
| T258 | 84 | 47.5 | 5.9 | 13.3 | 0.0 | 4.1 | 0.0 | 0.1 | 4.6 | 6.2 | 0.0 | 1.1 | 12.0 | 41.5 |
| T261 | 29 | 8.9 | 0.8 | 1.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 6.7 | 3.0 |
| T262 | 103 | 123.2 | 8.5 | 9.7 | 0.0 | 5.7 | 0.2 | 0.3 | 2.7 | 22.9 | 14.6 | 4.8 | 53.7 | 76.0 |
| T263 | 67 | 36.0 | 7.5 | 14.6 | 0.0 | 4.9 | 0.2 | 0.2 | 1.2 | 0.2 | 0.0 | 1.3 | 5.8 | 25.3 |
| T251 | 251 | 183.1 | 13.8 | 14.0 | 0.0 | 1.1 | 0.0 | 0.1 | 1.1 | 46.0 | 27.2 | 0.2 | 79.7 | 92.6 |
| T250 | 411 | 264.2 | 19.5 | 9.5 | 0.0 | 0.0 | 1.0 | 1.6 | 1.5 | 13.0 | 4.2 | 0.0 | 214.0 | 160.1 |
| T267 | 45 | 50.8 | 13.6 | 21.7 | 0.0 | 6.0 | 0.2 | 0.2 | 1.3 | 1.6 | 0.0 | 0.3 | 6.1 | 41.7 |
| T265 | 155 | 175.9 | 10.9 | 22.0 | 0.0 | 1.9 | 0.2 | 0.2 | 1.3 | 26.6 | 12.4 | 0.5 | 100.0 | 101.1 |
| T268 | 63 | 93.0 | 12.6 | 19.1 | 0.0 | 4.9 | 0.2 | 1.8 | 1.4 | 0.8 | 0.0 | 0.9 | 51.3 | 88.0 |
| T272 | 48 | 78.7 | 7.8 | 19.0 | 0.0 | 4.1 | 0.1 | 0.3 | 2.5 | 1.0 | 0.0 | 0.2 | 43.7 | 76.1 |
| T271 | 37 | 44.0 | 11.5 | 19.0 | 0.0 | 7.7 | 0.2 | 0.4 | 1.6 | 1.5 | 0.0 | 0.1 | 2.0 | 39.1 |
| T269 | 46 | 46.0 | 13.2 | 23.9 | 0.0 | 2.9 | 0.1 | 0.3 | 1.2 | 1.0 | 1.8 | 0.4 | 1.3 | 41.0 |
| T270 | 52 | 44.9 | 32.0 | 2.1 | 0.0 | 4.8 | 0.1 | 0.7 | 1.8 | 0.9 | 0.0 | 0.0 | 2.4 | 40.8 |
| T292 | 88 | 15.8 | 3.4 | 4.7 | 0.0 | 2.0 | 0.2 | 0.4 | 2.8 | 0.7 | 0.0 | 0.1 | 1.5 | 9.1 |
| T285 | 211 | 91.7 | 9.1 | 8.0 | 0.0 | 5.1 | 0.3 | 2.8 | 1.3 | 0.9 | 1.2 | 0.7 | 62.2 | 74.1 |
| T281 | 79 | 26.6 | 5.5 | 6.4 | 0.0 | 6.2 | 0.3 | 1.0 | 4.8 | 0.4 | 0.0 | 0.0 | 2.0 | 23.3 |
| T284 | 93 | 14.0 | 4.0 | 3.5 | 0.1 | 4.0 | 0.0 | 0.0 | 0.0 | 1.1 | 0.0 | 0.9 | 0.4 | 7.5 |
| T295 | 142 | 46.4 | 17.9 | 14.4 | 0.0 | 6.5 | 0.3 | 1.8 | 1.9 | 0.7 | 0.0 | 0.5 | 2.2 | 23.9 |
| T305 | 144 | 150.0 | 3.1 | 1.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 2.3 | 0.9 | 142.1 | 137.3 |
| T303 | 29 | 6.2 | 0.6 | 0.6 | 0.0 | 0.7 | 0.1 | 0.3 | 1.6 | 0.5 | 0.0 | 0.0 | 1.7 | 3.9 |
| T289 | 88 | 21.5 | 3.8 | 2.5 | 0.0 | 1.6 | 0.0 | 0.7 | 3.9 | 0.3 | 0.0 | 1.2 | 7.4 | 8.7 |
| T159 | 133 | 56.1 | 20.5 | 3.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.2 | 0.0 | 0.0 | 30.4 | 47.6 |
| T104 | 120 | 196.0 | 3.2 | 7.2 | 0.4 | 3.8 | 0.4 | 1.7 | 6.0 | 3.5 | 0.0 | 0.0 | 170.0 | 156.3 |
| T298 | 166 | 32.6 | 4.4 | 8.5 | 0.8 | 1.3 | 0.3 | 2.0 | 2.7 | 0.3 | 2.4 | 0.3 | 9.5 | 17.6 |
| T316 | 143 | 58.7 | 25.8 | 2.3 | 0.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9 | 0.0 | 1.4 | 27.9 | 42.5 |
| T308 | 202 | 9.3 | 1.5 | 2.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9 | 1.1 | 0.2 | 3.2 | 1.5 |
| T299 | 96 | 76.0 | 3.7 | 2.8 | 0.0 | 0.9 | 0.3 | 0.7 | 4.5 | 0.3 | 0.0 | 0.2 | 62.6 | 68.1 |
| T293 | 97 | 11.5 | 2.6 | 2.6 | 0.0 | 0.6 | 0.1 | 0.1 | 0.9 | 0.3 | 1.5 | 0.3 | 2.5 | 2.8 |
| T315 | 124 | 38.2 | 5.4 | 3.3 | 1.9 | 0.0 | 0.1 | 0.4 | 2.1 | 0.5 | 0.2 | 0.3 | 24.0 | 11.0 |
| T274 | 120 | 22.4 | 8.3 | 5.6 | 0.1 | 0.6 | 0.1 | 0.3 | 1.5 | 0.2 | 0.3 | 0.4 | 4.9 | 14.1 |
| T334 | 135 | 35.3 | 14.1 | 6.8 | 0.0 | 1.6 | 0.3 | 2.9 | 3.5 | 0.3 | 0.3 | 0.1 | 5.3 | 27.7 |
| T339 | 42 | 13.9 | 9.1 | 3.1 | 1.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 0.3 | 10.1 |
| T336 | 173 | 127.4 | 9.7 | 1.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.1 | 116.2 | 122.9 |
| T340 | 57 | 14.3 | 2.1 | 0.9 | 0.0 | 0.0 | 0.1 | 0.3 | 1.6 | 0.5 | 0.0 | 0.0 | 8.8 | 2.8 |
| T347 | 142 | 50.5 | 7.8 | 8.8 | 5.4 | 0.0 | 0.1 | 0.3 | 1.7 | 0.6 | 1.7 | 0.7 | 23.3 | 24.2 |
| T370 | 42 | 13.3 | 1.6 | 3.2 | 0.0 | 0.9 | 0.2 | 1.7 | 1.6 | 0.5 | 0.0 | 0.0 | 3.4 | 8.4 |
| T372 | 9 | 5.7 | 2.6 | 2.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 |
| T359 | 188 | 42.5 | 8.9 | 12.6 | 0.4 | 1.2 | 0.2 | 1.0 | 3.7 | 2.5 | 5.8 | 0.1 | 6.1 | 15.1 |
| T324 | 72 | 16.7 | 2.2 | 5.0 | 0.7 | 0.0 | 0.1 | 0.4 | 2.3 | 1.2 | 0.0 | 0.0 | 4.8 | 4.5 |
| T325 | 135 | 53.1 | 6.0 | 4.3 | 0.0 | 0.0 | 0.1 | 3.0 | 3.0 | 0.6 | 0.8 | 0.1 | 35.3 | 33.4 |
| T383 | 56 | 10.5 | 2.4 | 2.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.5 | 0.0 | 0.0 | 4.3 | 0.9 |
| T332 | 35 | 14.7 | 2.1 | 2.9 | 0.0 | 0.0 | 0.4 | 1.6 | 5.6 | 1.0 | 0.0 | 0.5 | 0.7 | 10.7 |
| T385 | 33 | 0.9 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 |
| T346 | 79 | 33.9 | 1.5 | 2.5 | 0.0 | 0.0 | 0.3 | 0.6 | 4.0 | 0.7 | 0.0 | 0.2 | 24.2 | 24.9 |
| T382 | 28 | 2.1 | 0.7 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.8 | 0.0 |
| T394 | 100 | 13.5 | 2.9 | 2.4 | 0.0 | 0.4 | 0.1 | 0.1 | 3.9 | 0.9 | 0.8 | 0.5 | 1.5 | 5.8 |
| T391 | 68 | 14.1 | 5.1 | 3.2 | 0.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.2 | 0.0 | 4.8 | 0.0 |
| T399 | 45 | 8.9 | 0.7 | 0.2 | 0.0 | 0.6 | 0.2 | 0.4 | 4.7 | 1.5 | 0.0 | 0.0 | 0.6 | 6.6 |
| T139 | 58 | 15.3 | 1.6 | 1.8 | 0.0 | 1.0 | 0.1 | 0.2 | 2.6 | 0.5 | 0.0 | 0.3 | 7.1 | 8.0 |
| T355 | 86 | 31.1 | 3.9 | 1.9 | 0.0 | 0.0 | 0.1 | 0.3 | 1.8 | 0.6 | 0.0 | 0.1 | 22.4 | 15.2 |
| T410 | 30 | 7.8 | 1.5 | 1.3 | 0.0 | 0.5 | 0.1 | 0.3 | 2.0 | 1.3 | 0.0 | 0.0 | 0.7 | 4.5 |
| T314 | 75 | 55.4 | 1.8 | 2.8 | 0.0 | 2.4 | 0.4 | 1.4 | 5.5 | 0.6 | 0.0 | 0.1 | 40.3 | 50.5 |
| T367 | 74 | 7.4 | 1.5 | 0.9 | 0.0 | 0.7 | 0.1 | 0.3 | 2.1 | 0.6 | 0.0 | 0.0 | 1.1 | 4.3 |
| T414 | 80 | 17.0 | 3.1 | 2.5 | 0.0 | 0.5 | 0.1 | 0.3 | 5.8 | 1.4 | 1.0 | 0.0 | 2.4 | 6.8 |
| T419 | 95 | 198.0 | 7.4 | 30.8 | 1.5 | 4.7 | 0.9 | 9.5 | 135.6 | 0.4 | 0.1 | 0.0 | 6.9 | 191.3 |
| T403 | 49 | 5.8 | 0.2 | 0.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 0.0 | 4.3 | 0.0 |
| T424 | 67 | 29.4 | 5.9 | 9.6 | 1.1 | 1.5 | 0.1 | 2.0 | 3.6 | 2.3 | 0.0 | 0.0 | 3.3 | 12.7 |
| T417 | 92 | 14.6 | 9.4 | 0.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.8 | 0.0 | 0.2 | 2.6 | 0.0 |
| T409 | 53 | 10.3 | 3.2 | 2.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.1 | 0.0 | 0.0 | 3.3 | 0.0 |
| T313 | 339 | 51.8 | 10.0 | 12.9 | 0.6 | 0.0 | 0.0 | 0.0 | 0.0 | 4.2 | 0.7 | 1.0 | 22.5 | 13.1 |
| T413 | 133 | 12.3 | 4.9 | 1.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 0.1 | 4.4 | 0.0 |
| T427 | 90 | 25.8 | 10.3 | 6.4 | 0.7 | 0.0 | 0.0 | 0.0 | 0.0 | 1.2 | 0.0 | 1.5 | 5.7 | 3.3 |
| T369 | 77 | 12.3 | 7.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 0.4 | 3.9 | 0.0 |
| T364 | 85 | 20.3 | 7.3 | 4.4 | 2.8 | 0.0 | 0.0 | 0.0 | 0.0 | 2.0 | 0.0 | 0.1 | 3.6 | 2.7 |
| T365 | 103 | 14.0 | 1.0 | 1.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9 | 0.0 | 0.3 | 10.0 | 4.4 |
| T373 | 85 | 61.0 | 0.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.3 | 60.1 | 37.2 |
| T420 | 78 | 5.1 | 0.3 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.7 | 0.0 | 0.4 | 3.6 | 0.0 |
| T312 | 632 | 198.0 | 29.9 | 46.6 | 0.8 | 4.7 | 2.2 | 18.4 | 36.8 | 3.4 | 2.3 | 3.4 | 49.6 | 118.7 |
| T425 | 232 | 10.2 | 3.2 | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.1 | 1.1 | 0.0 | 2.8 | 0.1 |
| T333 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T239 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| T345 | 10 | 2.7 | 1.4 | 0.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.2 | 0.1 | 0.0 |
| T402 | 2 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 |
| T398 | 1 | 1.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.1 | 0.0 | 0.0 | 0.0 | 0.0 | 1.1 |
| T486 | 2 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| T498 | 2 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 |
| all | 49163 | 14135.5 | 2623.0 | 1635.3 | 28.4 | 310.1 | 21.9 | 343.0 | 434.0 | 520.9 | 437.8 | 91.6 | 7689.5 | 9832.5 |

runs: 49163 Bash calls of every session and agent (3148 in the background, 1 open at the window's end), booked by their `make` target through the guard's table (feature 451 T08); machine minutes, which overlap, never the wall clock; 869 refused before running; phases tied to no run: 841 (71.1 min); waits on a scratch slot directory (451 T426): 4 (3.7 min), booked to no category - a measurement's own scripted holds (`L7R_BUILD_SLOT_DIR` away from the default), their seconds their run's own, never `waiting on a build slot`

