# Found-rows triage, part 3: 444's remaining open rows (341 open; the 298 the earlier triages did not read)

Read-only, clone diagram-backlog at HEAD 35f7dcb5a5 (2026-11-24). Rust and research pages read from `git archive HEAD`; the
Python read at ea5638968e~1, the last commit that still held `l7r/diagram/hamletgen` (2026-11-07; the tag
`python-tests-before-removal` is later and no longer has the engine). No make target run. The pool's `*.driver.svg/json` are
untracked files built from the builder's working tree at 09:50-09:58 today, used only as evidence of what a build draws.
Numbering is the file's line number, as `found_list` prints it (record.rs enumerates before filtering); checked on rows 1, 26, 354.

## Summary

**Rule**: constitution XIV as the earlier triages used it - a wrong map, a check passing bad work or a page telling its reader
something false is a DEFECT; wording whose behavior is fine is a RESTATEMENT; "not in the bundle" is a note on the check.
**The split of the 298** (the other 43 open rows name rust/phases, re-listed from found-triage-older.md, not re-judged): MOOT 89
(wording, comments, units in deleted Python, no outcome) - WORDING-FORMAT 86 (mostly a page not recording a guess the code
states) - NOT NEEDED 65 (fixed or verified at HEAD; 19 bundle notes) - FIXED IN THE PORT 23 - PORT NOTE 17 - CARRIED-FORWARD
RISK 7 - RESTATEMENT 3 - DUPLICATE 3 - DEFECT 2 - RESEARCH QUESTION 2 - owed work with no task 1 (364, a budget re-derivation).
**Confirmed live-code defects new in this batch: none that makes a map read wrong; one minor cluster on the live polder.**
- Rows 140, 167 - CONFIRMED. 0027's page says the dike band is "mottled with patches of earth of different ages" (0018 says the
  same of a pond's bank); rust/phases/src/driver/polder.rs 249 and 288 paint both one flat fill, as the last Python did (the
  pool's Kuwabata of 11-07 has no mottle either). The page describes ink that is not there: restate it or draw it. No task found.
- Python faults in ported stages are gone in the Rust (each read in the ported function): the 7 ft brook, a pocket pond on a
  dike-pond block, the brook's weight at the seat, Sawada's seat refusal (the Python refused it to the end), over-wide bends.
- Wording that survived, no map effect: field/brook.rs 7 cites 0054 for a 22 ft figure the page lacks (21, 234); driver.rs 417
  cites only 0081 for the no-crossing rule (394).
**CARRIED-FORWARD RISK - Python faults in these rows that a port must not copy (7 rows, none in rust/phases):**
- Footbridges and crossings, UNPORTED, 3: row 326 two footplanks side by side where a canal is several ditch records (Inashiro,
  Kashikawa; still failing in the last Python's waiting list); 294/311 a lane's crossing skipped where a footplank stands (as
  reported). Plus 12 port notes: its figures are raw pixels, right only at a foot to the pixel.
- Toe marsh drawing, UNPORTED, 1: row 325 Inashiro's marsh with laid corners and straight runs (still failing in the last Python).
- Lanes (the web), UNPORTED, 1: row 371 two of Mizuguchi's ways side by side; that test stopped failing only when the map moved
  on 11-05, and a second web fault (two lane ends 8 ft apart, unjoined) was still failing at the end.
- Household groves, PARKED (grove_seat.rs), with the unported web, 1: row 380 two bamboo groves under lanes, cohort seed 904.
- Bamboo stands, UNPORTED, 1 (low): row 358 a stand off Kashikawa's sheet; gone when the map moved, the stage never fixed.
- Homesteads, track, appurtenances (PARKED): no other fault in these rows (open 444 T31 is one outside them); the 7 stage-order
  rows are moot there (rust/parked lays fixtures before any way); port notes: file the polder's feeder and outfall as
  keep-clear, keep houses off the pond's reeds. Pond stock, burial, frame (UNPORTED): 0 faults, 3 latent notes (399, 400, 346).
**Record defects: 0 beyond the mottle.** The two big clusters are wording: 0068's "far edge" for the 4.0 ft canal is an undefined
label (9 copies), and 0022's "never a grid of uniform rectangles" sits in its rice-polder section, so 0019's chessboard of ponds
does not contradict it (6 copies). 3 restatements: 220/308 (0053 "on every hamlet map") and 395 (0058 "built on").
**Can close: 180 of 298** (65 not needed, 89 moot, 23 fixed in the port, 3 duplicates: 317 -> 449 T418, 381/382 -> placeholder 380).
**Riddled with defects? These rows say no**: none is a new wrong map from the live Rust stages; the real faults are five
pool or cohort faults of unported Python stages, two still pinned by failing tests when the Python was deleted.
**Could not judge:** nothing was run, so 294/311, 380 and 220/308 are as reported; 303 and 350 rest on today's working-tree build
(the builder's unread edits in it); rust/parked and the Rust polder's drain width (249, 265, 295) were read as source or not at all.

## Table (341 open rows)

`OLDER:` = a rust/phases row copied from found-triage-older.md Table 2, not re-judged. LIVE / PARKED / UNPORTED is the row's
stage in Rust. File paths are under rust/phases/src unless given.

| row | verdict | note |
|---|---|---|
| 1 | OLDER: latent | randbelow(0) shifts by 32; every caller passes a constant or a table length |
| 2 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 3 | OLDER: wording | water_frame.rs line 5 "the bearing and the fall rolled"; three copies |
| 4 | WORDING-FORMAT | three copies; verified: 0031 drawing page does not state the wind-before-fall rule the code keeps |
| 5 | OLDER: wording | water_frame.rs line 5 "the bearing and the fall rolled"; three copies |
| 6 | WORDING-FORMAT | three copies; verified: 0031 drawing page does not state the wind-before-fall rule the code keeps |
| 7 | OLDER: wording | water_frame.rs line 5 "the bearing and the fall rolled"; three copies |
| 8 | WORDING-FORMAT | three copies; verified: 0031 drawing page does not state the wind-before-fall rule the code keeps |
| 9 | WORDING-FORMAT | 0017: the 15% band and the 1.3-acre gross figure are unrecorded; "1 to 2.5 acres" still reads as one band |
| 10 | MOOT [field/polder fit, LIVE] | claim or docstring wording of deleted fit code; 0022 page reads 5.5 mu a module at HEAD |
| 11 | MOOT [field/polder fit, LIVE] | claim or docstring wording of deleted fit code; 0022 page reads 5.5 mu a module at HEAD |
| 12 | MOOT [field/polder fit, LIVE] | claim or docstring wording of deleted fit code; 0022 page reads 5.5 mu a module at HEAD |
| 13 | MOOT [polder, LIVE] | latent: a hamlet polder (16 households) is far under the cap; same cluster as older rows 226/269/299/363 |
| 14 | NOT NEEDED | fixed: the brook is 5.25 ft and 0068 gives the village creek at three and a half times the floor |
| 15 | FIXED IN THE PORT [brook, LIVE] | BROOK_W 5.25 ft, under the 6.0 ft head race (driver.rs 59-60) |
| 16 | NOT NEEDED | fixed: the brook is 5.25 ft and 0068 gives the village creek at three and a half times the floor |
| 17 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 18 | NOT NEEDED [field ink, LIVE] | verified: 0008 page describes the bank, the wet ground inside it and open water; driver/polder.rs 235 draws that |
| 19 | NOT NEEDED | 0006 gives 1.4 ft for a hamlet, which is what is drawn; other tiers are not built |
| 20 | WORDING-FORMAT | 0014 does not record the bead guesses (count, spacing, share, opacity, none on a polder) |
| 21 | WORDING-FORMAT | verified: 0054 drawing page has no 22 ft, 1.6 degrees or ten widths; field/brook.rs 7 and 31 cite it for them |
| 22 | OLDER: wording | a module claim inherited by plumbing units; labels only |
| 23 | WORDING-FORMAT | nine copies, still there: 0068 table names the 4.0 ft canal "along the far edge" while the code calls the 4.5 canal flank the far one (field/channels.rs 38, 189). No page defines "far" as away from the brook, so an ambiguous label, not a false statement; one word in the table settles it |
| 24 | NOT NEEDED | fixed: 0053 now says a delivery leaves nearly square and leans downstream, citing 0054 |
| 27 | WORDING-FORMAT | 0027 does not record the crown sizes or the 30 ft cut as guesses |
| 28 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 29 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 30 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 31 | OLDER: wording | a module claim inherited by plumbing units; labels only |
| 32 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 35 | WORDING-FORMAT | 0005 does not record the bow, the plot_size forms or the half-row fallback as guesses |
| 36 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 37 | OLDER: wording | a module claim inherited by plumbing units; labels only |
| 38 | WORDING-FORMAT | 0018 does not record the corner rounding or the small-parcel fallback as guesses |
| 39 | WORDING-FORMAT | 0017: the 15% band and the 1.3-acre gross figure are unrecorded; "1 to 2.5 acres" still reads as one band |
| 40 | OLDER: wording | a module claim inherited by plumbing units; labels only |
| 41 | NOT NEEDED | the flooded and gold plots are a per-map roll (field/states.rs 148, SEASONAL_IN) |
| 42 | NOT NEEDED | fixed: 0059 says 5.25 ft and has no 300 ft; 0031 and 0069 have no 7 ft brook |
| 43 | FIXED IN THE PORT [brook, LIVE] | BROOK_TAP_RUN is a stated GUESS in feet (driver.rs 42-43) |
| 44 | NOT NEEDED | fixed: 0059 says 5.25 ft and has no 300 ft; 0031 and 0069 have no 7 ft brook |
| 45 | MOOT [field records, LIVE] | fixed in the last Python (field_stage.py 445); the Rust record writes no flooded_plots |
| 46 | FIXED in the last Python [polder keep-clear] | feeder and outfall filed (field_stage.py 485, 490). PORT NOTE: the Rust has no keep-clear registry yet; the homesteads port must file both |
| 47 | NOT NEEDED [weir, LIVE] | 0059 page now records the full closure as a drawing convention at a 5.25 ft brook; driver.rs 228 spans it |
| 48 | NOT NEEDED | fixed: 0059 says 5.25 ft and has no 300 ft; 0031 and 0069 have no 7 ft brook |
| 49 | MOOT [footbridges, UNPORTED] | polder_crossing_caps docstring against its code; wording of deleted code |
| 50 | WORDING-FORMAT | 0084 gives no length for "long", and records neither the collector cap nor the merged deck as guesses |
| 51 | MOOT [footbridges/crossings, UNPORTED] | stale docstring, comment or claim wording in deleted bridges.py; no outcome |
| 52 | MOOT [footbridges/crossings, UNPORTED] | stale docstring, comment or claim wording in deleted bridges.py; no outcome |
| 53 | PORT NOTE [footbridges, UNPORTED] | figures in raw pixels, right only at 1 ft/px (every hamlet); a port holds them in feet |
| 54 | PORT NOTE [footbridges, UNPORTED] | figures in raw pixels, right only at 1 ft/px (every hamlet); a port holds them in feet |
| 55 | MOOT [field ink / old settlement code] | comment, label, unit or dead-code note in deleted Python; the Rust driver draws in feet; DIKE_CROPS rolls only mulberry, fruit, tea (plan.rs 98) |
| 56 | MOOT [field ink / old settlement code] | comment, label, unit or dead-code note in deleted Python; the Rust driver draws in feet; DIKE_CROPS rolls only mulberry, fruit, tea (plan.rs 98) |
| 57 | MOOT [field ink / old settlement code] | comment, label, unit or dead-code note in deleted Python; the Rust driver draws in feet; DIKE_CROPS rolls only mulberry, fruit, tea (plan.rs 98) |
| 58 | MOOT [field ink / old settlement code] | comment, label, unit or dead-code note in deleted Python; the Rust driver draws in feet; DIKE_CROPS rolls only mulberry, fruit, tea (plan.rs 98) |
| 60 | WORDING-FORMAT | 0059: "on one side" beside a center intake, "leave the map or take in the drain", "stops short" - each still open to two readings |
| 64 | WORDING-FORMAT | nine copies, still there: 0068 table names the 4.0 ft canal "along the far edge" while the code calls the 4.5 canal flank the far one (field/channels.rs 38, 189). No page defines "far" as away from the brook, so an ambiguous label, not a false statement; one word in the table settles it |
| 65 | NOT NEEDED | fixed: 0053 now says a delivery leaves nearly square and leans downstream, citing 0054 |
| 66 | WORDING-FORMAT | 0027 does not record the crown sizes or the 30 ft cut as guesses |
| 68 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 69 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 70 | WORDING-FORMAT | 0018 does not record the corner rounding or the small-parcel fallback as guesses |
| 72 | WORDING-FORMAT | 0005 does not record the bow, the plot_size forms or the half-row fallback as guesses |
| 73 | WORDING-FORMAT | six copies, still there: 0022 "never ... a grid of uniform rectangles" stands in its rice-polder parcel section (the 190 ft modules), so it does not contradict 0019 chessboard of ponds; the scope is unstated in the sentence |
| 75 | OLDER: latent, as reported | rest() stops after want x 8 tries; a small rice polder could rest fewer than two |
| 77 | WORDING-FORMAT | 0018 does not record the corner rounding or the small-parcel fallback as guesses |
| 78 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 79 | WORDING-FORMAT | 0017: the 15% band and the 1.3-acre gross figure are unrecorded; "1 to 2.5 acres" still reads as one band |
| 80 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 82 | MOOT | claim wording or a missing claim line in deleted Python |
| 83 | MOOT in rust/parked [homesteads order, PARKED] | the row could not tell; rust/parked seats each homestead fixtures (homesteads/fixtures.rs) before any way is laid (gap_ways.rs), which is the order 0246 wants; unverified, nothing runs |
| 84 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 85 | MOOT | claim wording or a missing claim line in deleted Python |
| 86 | WORDING-FORMAT | 0005 does not record the bow, the plot_size forms or the half-row fallback as guesses |
| 87 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 88 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 89 | WORDING-FORMAT | 0059: "on one side" beside a center intake, "leave the map or take in the drain", "stops short" - each still open to two readings |
| 90 | MOOT [footbridges, UNPORTED] | polder_crossing_caps docstring against its code; wording of deleted code |
| 91 | MOOT [footbridges/crossings, UNPORTED] | stale docstring, comment or claim wording in deleted bridges.py; no outcome |
| 92 | MOOT [footbridges/crossings, UNPORTED] | stale docstring, comment or claim wording in deleted bridges.py; no outcome |
| 93 | WORDING-FORMAT | 0008 does not record the bank width or the two rice_pond guesses |
| 94 | MOOT [field ink / old settlement code] | comment, label, unit or dead-code note in deleted Python; the Rust driver draws in feet; DIKE_CROPS rolls only mulberry, fruit, tea (plan.rs 98) |
| 95 | WORDING-FORMAT | 0014 does not record the bead guesses (count, spacing, share, opacity, none on a polder) |
| 96 | WORDING-FORMAT | 0014 does not record the bead guesses (count, spacing, share, opacity, none on a polder) |
| 97 | WORDING-FORMAT | an unclaimed decision: the brook meander against 0054 two-to-three-width bends; no claim compares them |
| 98 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 102 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 103 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 104 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 105 | WORDING-FORMAT | 0059: "on one side" beside a center intake, "leave the map or take in the drain", "stops short" - each still open to two readings |
| 106 | WORDING-FORMAT | 0027 does not record the crown sizes or the 30 ft cut as guesses |
| 108 | WORDING-FORMAT | 0011 does not give the hem order along the canal, its course on the brook flank, or where a remainder goes |
| 115 | WORDING-FORMAT | 0005 does not record the bow, the plot_size forms or the half-row fallback as guesses |
| 117 | WORDING-FORMAT | six copies, still there: 0022 "never ... a grid of uniform rectangles" stands in its rice-polder parcel section (the 190 ft modules), so it does not contradict 0019 chessboard of ponds; the scope is unstated in the sentence |
| 119 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 120 | WORDING-FORMAT | 0013 is still silent on a wet plot resting; the code records its choice as a GUESS |
| 121 | MOOT [burial, UNPORTED] | claim wording: the burial ground is seated before the lane-side wells; a port states it |
| 122 | MOOT in rust/parked [homesteads order, PARKED] | the row could not tell; rust/parked seats each homestead fixtures (homesteads/fixtures.rs) before any way is laid (gap_ways.rs), which is the order 0246 wants; unverified, nothing runs |
| 123 | MOOT [field ink / old settlement code] | comment, label, unit or dead-code note in deleted Python; the Rust driver draws in feet; DIKE_CROPS rolls only mulberry, fruit, tea (plan.rs 98) |
| 124 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 125 | MOOT [footbridges, UNPORTED] | polder_crossing_caps docstring against its code; wording of deleted code |
| 126 | PORT NOTE [footbridges, UNPORTED] | latent: caps asked before the seat fall through to the foot caps; a port refuses instead |
| 127 | WORDING-FORMAT | 0084 gives no length for "long", and records neither the collector cap nor the merged deck as guesses |
| 128 | MOOT [footbridges/crossings, UNPORTED] | stale docstring, comment or claim wording in deleted bridges.py; no outcome |
| 129 | PORT NOTE [footbridges, UNPORTED] | figures in raw pixels, right only at 1 ft/px (every hamlet); a port holds them in feet |
| 130 | MOOT [footbridges, UNPORTED] | polder_crossing_caps docstring against its code; wording of deleted code |
| 133 | FIXED IN THE PORT [weir, LIVE] | WEIR_KEY_FT carries its GUESS (driver.rs 66-69) |
| 134 | NOT NEEDED | fixed: 0059 records the straight-reach or bend-apex siting, rolled per settlement |
| 135 | WORDING-FORMAT | nine copies, still there: 0068 table names the 4.0 ft canal "along the far edge" while the code calls the 4.5 canal flank the far one (field/channels.rs 38, 189). No page defines "far" as away from the brook, so an ambiguous label, not a false statement; one word in the table settles it |
| 136 | WORDING-FORMAT | 0053: how the second canal tail ends is told two ways |
| 137 | NOT NEEDED | fixed: 0053 now says a delivery leaves nearly square and leans downstream, citing 0054 |
| 140 | DEFECT (minor) [polder dike, LIVE] | CONFIRMED: 0027 says the band is "mottled with patches of earth of different ages" (0018 says the same of the bank); driver/polder.rs 249 and 288 paint both one flat fill (Svg::band, svg.rs 160-174), as the last Python did (ink.dike) - the pool Kuwabata picture of 11-07 has no mottle either; the older village dike code drew it. Restate the page or draw it |
| 143 | WORDING-FORMAT | 0018 does not record the corner rounding or the small-parcel fallback as guesses |
| 144 | WORDING-FORMAT | 0020 does not say where the kept rice stands among the ponds |
| 146 | WORDING-FORMAT | 0005 does not record the bow, the plot_size forms or the half-row fallback as guesses |
| 147 | WORDING-FORMAT | six copies, still there: 0022 "never ... a grid of uniform rectangles" stands in its rice-polder parcel section (the 190 ft modules), so it does not contradict 0019 chessboard of ponds; the scope is unstated in the sentence |
| 148 | WORDING-FORMAT | 0019 records no guess for the feeder course |
| 149 | NOT NEEDED | fixed: 0019 says a village polder gets two, a GUESS |
| 150 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 151 | WORDING-FORMAT | 0018 does not record the corner rounding or the small-parcel fallback as guesses |
| 152 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 153 | MOOT in rust/parked | 0246 against the stage order: rust/parked lays fixtures before ways; unverified |
| 154 | MOOT in rust/parked [homesteads order, PARKED] | the row could not tell; rust/parked seats each homestead fixtures (homesteads/fixtures.rs) before any way is laid (gap_ways.rs), which is the order 0246 wants; unverified, nothing runs |
| 155 | NOT NEEDED | verified: the 0008 table has its headings (kind of field, pond, rock outcrop, grave) |
| 156 | MOOT [footbridges, UNPORTED] | polder_crossing_caps docstring against its code; wording of deleted code |
| 157 | MOOT [footbridges, UNPORTED] | polder_crossing_caps docstring against its code; wording of deleted code |
| 158 | MOOT [footbridges/crossings, UNPORTED] | stale docstring, comment or claim wording in deleted bridges.py; no outcome |
| 159 | MOOT [footbridges, UNPORTED] | polder_crossing_caps docstring against its code; wording of deleted code |
| 160 | PORT NOTE [footbridges, UNPORTED] | a plank spans the ditch head width + 5.5 ft at every seat, not the local width; as reported |
| 161 | PORT NOTE [footbridges, UNPORTED] | figures in raw pixels, right only at 1 ft/px (every hamlet); a port holds them in feet |
| 162 | WORDING-FORMAT | 0068 has no rung for a default channel or a polder toe, and two sentences that hold only for some canals |
| 163 | NOT NEEDED | fixed: 0059 records the straight-reach or bend-apex siting, rolled per settlement |
| 164 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 165 | WORDING-FORMAT | nine copies, still there: 0068 table names the 4.0 ft canal "along the far edge" while the code calls the 4.5 canal flank the far one (field/channels.rs 38, 189). No page defines "far" as away from the brook, so an ambiguous label, not a false statement; one word in the table settles it |
| 166 | NOT NEEDED | fixed: 0053 now says a delivery leaves nearly square and leans downstream, citing 0054 |
| 167 | DEFECT (minor) [polder dike, LIVE] | CONFIRMED: 0027 says the band is "mottled with patches of earth of different ages" (0018 says the same of the bank); driver/polder.rs 249 and 288 paint both one flat fill (Svg::band, svg.rs 160-174), as the last Python did (ink.dike) - the pool Kuwabata picture of 11-07 has no mottle either; the older village dike code drew it. Restate the page or draw it |
| 168 | WORDING-FORMAT | six copies, still there: 0022 "never ... a grid of uniform rectangles" stands in its rice-polder parcel section (the 190 ft modules), so it does not contradict 0019 chessboard of ponds; the scope is unstated in the sentence |
| 170 | NOT NEEDED | 0017 now scopes the rule to a field watered from a pond; the wild pond size is a stated GUESS |
| 171 | MOOT in rust/parked | 0246 against the stage order: rust/parked lays fixtures before ways; unverified |
| 172 | MOOT in rust/parked [homesteads order, PARKED] | the row could not tell; rust/parked seats each homestead fixtures (homesteads/fixtures.rs) before any way is laid (gap_ways.rs), which is the order 0246 wants; unverified, nothing runs |
| 173 | WORDING-FORMAT | 0053 and 0060 on when the drain is laid |
| 174 | FIXED IN THE PORT [polder, LIVE] | verified: no pocket pond on a dike-pond block (field/staged.rs 129) |
| 175 | NOT NEEDED [weir, LIVE] | 0059 page now records the full closure as a drawing convention at a 5.25 ft brook; driver.rs 228 spans it |
| 176 | NOT NEEDED [weir, LIVE] | 0059 page gives each form its thickness, the 5 ft a GUESS |
| 177 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 178 | MOOT [footbridges/crossings, UNPORTED] | stale docstring, comment or claim wording in deleted bridges.py; no outcome |
| 179 | PORT NOTE [footbridges, UNPORTED] | figures in raw pixels, right only at 1 ft/px (every hamlet); a port holds them in feet |
| 180 | WORDING-FORMAT | an unclaimed decision: the brook meander against 0054 two-to-three-width bends; no claim compares them |
| 181 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 183 | NOT NEEDED | fixed: 0053 now says a delivery leaves nearly square and leans downstream, citing 0054 |
| 184 | WORDING-FORMAT | nine copies, still there: 0068 table names the 4.0 ft canal "along the far edge" while the code calls the 4.5 canal flank the far one (field/channels.rs 38, 189). No page defines "far" as away from the brook, so an ambiguous label, not a false statement; one word in the table settles it |
| 185 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 188 | WORDING-FORMAT | 0020 does not say where the kept rice stands among the ponds |
| 189 | WORDING-FORMAT | six copies, still there: 0022 "never ... a grid of uniform rectangles" stands in its rice-polder parcel section (the 190 ft modules), so it does not contradict 0019 chessboard of ponds; the scope is unstated in the sentence |
| 191 | OLDER: latent | two sluices fixed; right for a hamlet |
| 193 | NOT NEEDED | verified: the 0008 table has its headings (kind of field, pond, rock outcrop, grave) |
| 194 | MOOT | claim wording or a missing claim line in deleted Python |
| 195 | MOOT in rust/parked [homesteads order, PARKED] | the row could not tell; rust/parked seats each homestead fixtures (homesteads/fixtures.rs) before any way is laid (gap_ways.rs), which is the order 0246 wants; unverified, nothing runs |
| 196 | FIXED IN THE PORT [polder, LIVE] | verified: no pocket pond on a dike-pond block (field/staged.rs 129) |
| 197 | MOOT [footbridges/crossings, UNPORTED] | stale docstring, comment or claim wording in deleted bridges.py; no outcome |
| 198 | PORT NOTE [footbridges, UNPORTED] | figures in raw pixels, right only at 1 ft/px (every hamlet); a port holds them in feet |
| 199 | MOOT [footbridges, UNPORTED] | polder_crossing_caps docstring against its code; wording of deleted code |
| 201 | WORDING-FORMAT | an unclaimed decision: the brook meander against 0054 two-to-three-width bends; no claim compares them |
| 202 | NOT NEEDED | fixed: 0059 records the straight-reach or bend-apex siting, rolled per settlement |
| 203 | NOT NEEDED | fixed: 0053 now says a delivery leaves nearly square and leans downstream, citing 0054 |
| 204 | WORDING-FORMAT | 0053: how the second canal tail ends is told two ways |
| 205 | WORDING-FORMAT | nine copies, still there: 0068 table names the 4.0 ft canal "along the far edge" while the code calls the 4.5 canal flank the far one (field/channels.rs 38, 189). No page defines "far" as away from the brook, so an ambiguous label, not a false statement; one word in the table settles it |
| 207 | WORDING-FORMAT | six copies, still there: 0022 "never ... a grid of uniform rectangles" stands in its rice-polder parcel section (the 190 ft modules), so it does not contradict 0019 chessboard of ponds; the scope is unstated in the sentence |
| 208 | OLDER: latent, as reported | rest() stops after want x 8 tries; a small rice polder could rest fewer than two |
| 211 | NOT NEEDED [polder, LIVE] | verified: polder::rest never takes a low plot and its claim says so (field/polder.rs 734) |
| 212 | FIXED IN THE PORT [polder, LIVE] | verified: no pocket pond on a dike-pond block (field/staged.rs 129) |
| 213 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 214 | MOOT [footbridges, UNPORTED] | polder_crossing_caps docstring against its code; wording of deleted code |
| 215 | PORT NOTE [footbridges, UNPORTED] | figures in raw pixels, right only at 1 ft/px (every hamlet); a port holds them in feet |
| 216 | WORDING-FORMAT | 0068 has no rung for a default channel or a polder toe, and two sentences that hold only for some canals |
| 217 | NOT NEEDED | fixed: 0053 now says a delivery leaves nearly square and leans downstream, citing 0054 |
| 218 | WORDING-FORMAT | nine copies, still there: 0068 table names the 4.0 ft canal "along the far edge" while the code calls the 4.5 canal flank the far one (field/channels.rs 38, 189). No page defines "far" as away from the brook, so an ambiguous label, not a false statement; one word in the table settles it |
| 219 | NOT NEEDED | fixed: 0068 figures re-measured; a canal reaches the 1.5 ft thread at its last offtake whether or not it runs on (field/channels.rs 192-194), so 0053 and 0068 agree on Inashiro |
| 220 | RESTATEMENT | 0053 says the second canal feeds a delivery "on every hamlet map"; field/channels.rs 191 draws a second canal with none half way. Whether any hamlet rolls that was not measured |
| 221 | WORDING-FORMAT | 0014 does not record the bead guesses (count, spacing, share, opacity, none on a polder) |
| 222 | MOOT [footbridges/crossings, UNPORTED] | stale docstring, comment or claim wording in deleted bridges.py; no outcome |
| 223 | MOOT [footbridges/crossings, UNPORTED] | stale docstring, comment or claim wording in deleted bridges.py; no outcome |
| 224 | WORDING-FORMAT | 0068 has no rung for a default channel or a polder toe, and two sentences that hold only for some canals |
| 226 | OLDER: latent | several fields on one map; no hamlet reaches the cap; village tier (380) |
| 229 | WORDING-FORMAT | 0068 has no rung for a default channel or a polder toe, and two sentences that hold only for some canals |
| 231 | FIXED IN THE PORT [intake, LIVE] | the 35 degrees is a GUESS citing 0054 (driver.rs 36-37) |
| 232 | FIXED IN THE PORT [weir, LIVE] | the reed-woven comment is gone; 0059 says brushwood or bamboo |
| 233 | MOOT [field, LIVE] | BROOK_FAN_TRIM is not in the Rust; the claim went with the Python |
| 234 | WORDING-FORMAT [brook, LIVE] | survived: field/brook.rs line 7 cites 0054 for "a step over 22 ft led in over two"; the page has no such figure. No map effect; same as row 21 |
| 235 | MOOT | claim wording or a missing claim line in deleted Python |
| 236 | OLDER: wording | a module claim inherited by plumbing units; labels only |
| 239 | MOOT [channels, LIVE] | comments and a px floor in deleted waterfields |
| 240 | MOOT [channels, LIVE] | comments and a px floor in deleted waterfields |
| 241 | MOOT [homesteads plots] | plot_texture was gone before the last Python tree and rust/parked rolls no grid or strip plots |
| 242 | MOOT [homesteads plots] | plot_texture was gone before the last Python tree and rust/parked rolls no grid or strip plots |
| 243 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 244 | MOOT [old village paddy code] | water_field was not on the hamlet path (only captions named it); the Rust hem rolls each map crop mix (field/dry.rs 62) |
| 245 | MOOT [old village paddy code] | water_field was not on the hamlet path (only captions named it); the Rust hem rolls each map crop mix (field/dry.rs 62) |
| 246 | MOOT [old village paddy code] | water_field was not on the hamlet path (only captions named it); the Rust hem rolls each map crop mix (field/dry.rs 62) |
| 247 | MOOT [head race, LIVE] | claim wording of deleted plan.py |
| 248 | MOOT [head race, LIVE] | claim wording of deleted plan.py |
| 249 | MOOT [polder drain, LIVE] | the unrecorded full-width drain was deleted polder.py; the Rust polder channels were rebuilt (field/polder.rs 517-596) and the drain width there was not read against 0068 |
| 250 | MOOT [channels, LIVE] | comments and a px floor in deleted waterfields |
| 251 | NOT NEEDED | a pointer to another unit, no finding |
| 252 | MOOT [homesteads plots] | plot_texture was gone before the last Python tree and rust/parked rolls no grid or strip plots |
| 253 | MOOT [homesteads plots] | plot_texture was gone before the last Python tree and rust/parked rolls no grid or strip plots |
| 254 | MOOT [homesteads plots] | plot_texture was gone before the last Python tree and rust/parked rolls no grid or strip plots |
| 255 | MOOT [homesteads plots] | plot_texture was gone before the last Python tree and rust/parked rolls no grid or strip plots |
| 256 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 257 | FIXED IN THE PORT [brook, LIVE] | BROOK_TAP_RUN is a stated GUESS in feet (driver.rs 42-43) |
| 258 | NOT NEEDED [weir, LIVE] | 0059 page now records the full closure as a drawing convention at a 5.25 ft brook; driver.rs 228 spans it |
| 259 | NOT NEEDED [weir, LIVE] | 0059 page gives each form its thickness, the 5 ft a GUESS |
| 261 | MOOT [old village paddy code] | water_field was not on the hamlet path (only captions named it); the Rust hem rolls each map crop mix (field/dry.rs 62) |
| 262 | MOOT [old village paddy code] | water_field was not on the hamlet path (only captions named it); the Rust hem rolls each map crop mix (field/dry.rs 62) |
| 263 | MOOT [channels, LIVE] | comments and a px floor in deleted waterfields |
| 264 | MOOT [channels, LIVE] | comments and a px floor in deleted waterfields |
| 265 | MOOT [polder drain, LIVE] | the unrecorded full-width drain was deleted polder.py; the Rust polder channels were rebuilt (field/polder.rs 517-596) and the drain width there was not read against 0068 |
| 266 | MOOT [channels, LIVE] | comments and a px floor in deleted waterfields |
| 267 | WORDING-FORMAT | 0014 does not record the bead guesses (count, spacing, share, opacity, none on a polder) |
| 268 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 269 | OLDER: latent | several fields on one map; no hamlet reaches the cap; village tier (380) |
| 270 | WORDING-FORMAT | 0011 does not give the hem order along the canal, its course on the brook flank, or where a remainder goes |
| 271 | NOT NEEDED | fixed: 0068 figures re-measured; a canal reaches the 1.5 ft thread at its last offtake whether or not it runs on (field/channels.rs 192-194), so 0053 and 0068 agree on Inashiro |
| 272 | WORDING-FORMAT | 0006: an unrecorded clearance, and a tract rule with no fallback stated |
| 273 | MOOT [footbridges/crossings, UNPORTED] | stale docstring, comment or claim wording in deleted bridges.py; no outcome |
| 274 | PORT NOTE [footbridges, UNPORTED] | figures in raw pixels, right only at 1 ft/px (every hamlet); a port holds them in feet |
| 275 | PORT NOTE [footbridges, UNPORTED] | figures in raw pixels, right only at 1 ft/px (every hamlet); a port holds them in feet |
| 277 | WORDING-FORMAT | nine copies, still there: 0068 table names the 4.0 ft canal "along the far edge" while the code calls the 4.5 canal flank the far one (field/channels.rs 38, 189). No page defines "far" as away from the brook, so an ambiguous label, not a false statement; one word in the table settles it |
| 278 | NOT NEEDED | fixed: 0068 figures re-measured; a canal reaches the 1.5 ft thread at its last offtake whether or not it runs on (field/channels.rs 192-194), so 0053 and 0068 agree on Inashiro |
| 279 | NOT NEEDED | fixed: 0068 figures re-measured; a canal reaches the 1.5 ft thread at its last offtake whether or not it runs on (field/channels.rs 192-194), so 0053 and 0068 agree on Inashiro |
| 280 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 282 | FIXED IN THE PORT [seat, LIVE] | the brook is only the tie-break between margins otherwise level (seat/margins.rs 413-422) |
| 283 | NOT NEEDED | fixed in the port: the brook is a tie-break and seat/margins.rs 422 quotes the page words |
| 284 | FIXED IN THE PORT [weir, LIVE] | the reed-woven comment is gone; 0059 says brushwood or bamboo |
| 285 | FIXED IN THE PORT [brook, LIVE] | the 7 ft brook is gone from code and from 0059 |
| 286 | WORDING-FORMAT | 0059 does not record the 70 ft straight run past the intake; the code holds it as a GUESS |
| 287 | MOOT | claim wording or a missing claim line in deleted Python |
| 288 | FIXED IN THE PORT [polder, LIVE] | verified: no pocket pond on a dike-pond block (field/staged.rs 129) |
| 289 | MOOT [records] | record values the deleted readers used; the Rust record carries none of them |
| 290 | WORDING-FORMAT | a page silent on a figure or case the code decides (0035, 0081, 0071, 0087) |
| 291 | MOOT [footbridges/crossings, UNPORTED] | stale docstring, comment or claim wording in deleted bridges.py; no outcome |
| 292 | FIXED IN THE PORT [brook, LIVE] | the 7 ft brook is gone from code and from 0059 |
| 293 | MOOT [footbridges/crossings, UNPORTED] | stale docstring, comment or claim wording in deleted bridges.py; no outcome |
| 294 | CARRIED-FORWARD RISK [crossings, UNPORTED] | as reported, unverified: the covered-crossing skip does not leave out footplanks, so a lane could cross on a 4 ft board against 0084 |
| 295 | MOOT [polder drain, LIVE] | the unrecorded full-width drain was deleted polder.py; the Rust polder channels were rebuilt (field/polder.rs 517-596) and the drain width there was not read against 0068 |
| 296 | WORDING-FORMAT | 0068 has no rung for a default channel or a polder toe, and two sentences that hold only for some canals |
| 299 | OLDER: latent | several fields on one map; no hamlet reaches the cap; village tier (380) |
| 301 | NOT NEEDED | fixed: 0068 figures re-measured; a canal reaches the 1.5 ft thread at its last offtake whether or not it runs on (field/channels.rs 192-194), so 0053 and 0068 agree on Inashiro |
| 302 | NOT NEEDED [polder, LIVE] | verified: polder::rest never takes a low plot and its claim says so (field/polder.rs 734) |
| 303 | FIXED IN THE PORT [polder, LIVE] | seen on the 11-24 working-tree build of Kuwabata: 16 paddy and 6 wet paddy parcels among the ponds |
| 304 | PORT NOTE [footbridges, UNPORTED] | figures in raw pixels, right only at 1 ft/px (every hamlet); a port holds them in feet |
| 305 | WORDING-FORMAT | 0084 gives no length for "long", and records neither the collector cap nor the merged deck as guesses |
| 306 | WORDING-FORMAT | 0011 does not give the hem order along the canal, its course on the brook flank, or where a remainder goes |
| 307 | WORDING-FORMAT | nine copies, still there: 0068 table names the 4.0 ft canal "along the far edge" while the code calls the 4.5 canal flank the far one (field/channels.rs 38, 189). No page defines "far" as away from the brook, so an ambiguous label, not a false statement; one word in the table settles it |
| 308 | RESTATEMENT | 0053 says the second canal feeds a delivery "on every hamlet map"; field/channels.rs 191 draws a second canal with none half way. Whether any hamlet rolls that was not measured |
| 309 | FIXED IN THE PORT [polder, LIVE] | verified: no pocket pond on a dike-pond block (field/staged.rs 129) |
| 310 | WORDING-FORMAT | 0068 has no rung for a default channel or a polder toe, and two sentences that hold only for some canals |
| 311 | CARRIED-FORWARD RISK [crossings, UNPORTED] | as reported, unverified: the covered-crossing skip does not leave out footplanks, so a lane could cross on a 4 ft board against 0084 |
| 312 | MOOT [footbridges/crossings, UNPORTED] | stale docstring, comment or claim wording in deleted bridges.py; no outcome |
| 313 | WORDING-FORMAT | 0014 does not record the bead guesses (count, spacing, share, opacity, none on a polder) |
| 314 | NOT NEEDED [beans, LIVE] | RUN_BEADS (2, 4) holds the two-bead rule (older triage, row 131 cluster) |
| 315 | NOT NEEDED [beans, LIVE] | RUN_BEADS (2, 4) holds the two-bead rule (older triage, row 131 cluster) |
| 317 | DUPLICATE | open 449 T418 (the cleared middle with a bare winter; T416 done) |
| 318 | WORDING-FORMAT | 0006: an unrecorded clearance, and a tract rule with no fallback stated |
| 319 | OLDER: wording | a module claim inherited by plumbing units; labels only |
| 320 | WORDING-FORMAT | 0008 does not record the bank width or the two rice_pond guesses |
| 322 | WORDING-FORMAT | 0084 gives no length for "long", and records neither the collector cap nor the merged deck as guesses |
| 324 | FIXED IN THE PORT [seat, LIVE] | Sawada refused at the Python seat to the end (_SEAT); the Rust seats it (seat.rs 117, the back to the hill; driver/tests.rs 38 rolls it at HEAD) and the 11-24 working-tree build lays its hem with refusals [] |
| 325 | CARRIED-FORWARD RISK [toe marsh drawing, UNPORTED] | CONFIRMED still failing in the last Python (_MARSH): Inashiro toe marsh with laid corners and straight runs; the Rust computes the toe band for the seat only (driver/toe.rs) and draws none |
| 326 | CARRIED-FORWARD RISK [footbridges, UNPORTED] | CONFIRMED still failing in the last Python (tests/_waiting_ports.py _PLANKS): two footplanks side by side where a canal is written as separate legs - Inashiro, Kashikawa |
| 327 | WORDING-FORMAT | 0011 does not give the hem order along the canal, its course on the brook flank, or where a remainder goes |
| 328 | WORDING-FORMAT | 0005 does not record the bow, the plot_size forms or the half-row fallback as guesses |
| 330 | MOOT [field ink / old settlement code] | comment, label, unit or dead-code note in deleted Python; the Rust driver draws in feet; DIKE_CROPS rolls only mulberry, fruit, tea (plan.rs 98) |
| 331 | MOOT [field ink / old settlement code] | comment, label, unit or dead-code note in deleted Python; the Rust driver draws in feet; DIKE_CROPS rolls only mulberry, fruit, tea (plan.rs 98) |
| 332 | MOOT [field ink / old settlement code] | comment, label, unit or dead-code note in deleted Python; the Rust driver draws in feet; DIKE_CROPS rolls only mulberry, fruit, tea (plan.rs 98) |
| 333 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 334 | FIXED IN THE PORT [brook, LIVE] | BROOK_TAP_RUN is a stated GUESS in feet (driver.rs 42-43) |
| 335 | WORDING-FORMAT | 0059 does not record the 70 ft straight run past the intake; the code holds it as a GUESS |
| 336 | FIXED IN THE PORT [weir, LIVE] | the reed-woven comment is gone; 0059 says brushwood or bamboo |
| 337 | FIXED IN THE PORT [brook, LIVE] | the 7 ft brook is gone from code and from 0059 |
| 338 | FIXED IN THE PORT [bends, LIVE] | read: course.rs arc() (59-90) draws a true arc whose radius is BEND_WIDTHS x the width, capped by the legs - the radius itself, not a cut-back |
| 339 | MOOT [field ink / old settlement code] | comment, label, unit or dead-code note in deleted Python; the Rust driver draws in feet; DIKE_CROPS rolls only mulberry, fruit, tea (plan.rs 98) |
| 340 | NOT NEEDED | a pointer to another unit, no finding |
| 341 | MOOT [field ink / old settlement code] | comment, label, unit or dead-code note in deleted Python; the Rust driver draws in feet; DIKE_CROPS rolls only mulberry, fruit, tea (plan.rs 98) |
| 342 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 343 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 344 | NOT NEEDED | a pointer to another unit, no finding |
| 345 | WORDING-FORMAT | 0005 does not record the bow, the plot_size forms or the half-row fallback as guesses |
| 346 | FIXED IN THE PORT [frame crop] | the driver crops to everything drawn (driver/svg.rs finish); Kuwabata W and S reed strips lie inside the view. The frame stage itself is UNPORTED: a port crops to declared reed ground |
| 347 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 348 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 349 | WORDING-FORMAT | 0014 does not record the bead guesses (count, spacing, share, opacity, none on a polder) |
| 350 | NOT NEEDED | seen on the 11-24 working-tree build of Kuwabata: reed strips on the west flank and the south side |
| 351 | MOOT [records] | record values the deleted readers used; the Rust record carries none of them |
| 352 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 353 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 355 | MOOT [field ink / old settlement code] | comment, label, unit or dead-code note in deleted Python; the Rust driver draws in feet; DIKE_CROPS rolls only mulberry, fruit, tea (plan.rs 98) |
| 356 | NOT NEEDED | the Rust draws a row ditch wherever its gap is open (field/polder.rs 635), so the lattice runs both ways; the lattice width question is open 449 T420 |
| 357 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 358 | CARRIED-FORWARD RISK (low) [bamboo, UNPORTED] | Kashikawa bamboo stand off its sheet: its test left the waiting list on 11-05 when the Rust row village moved the map (3876c3d494), not by a fix to the bamboo stage; a port checks stands against the sheet |
| 359 | WORDING-FORMAT | 0054 records the 35% radius cap, not the tangent cap (course.rs 34) |
| 360 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 361 | WORDING-FORMAT | 0054 records the 35% radius cap, not the tangent cap (course.rs 34) |
| 362 | WORDING-FORMAT [sink, LIVE] | the no-sink-on-a-polder rule has no page; Kuwabata runs no sink stage |
| 363 | OLDER: latent | several fields on one map; no hamlet reaches the cap; village tier (380) |
| 364 | NOT A DEFECT - owed work, no task | the field budget owes a re-derivation pricing the brook as drawn at its next re-pin; no map. No task carries it (444 T24 re-prices the hem, not the brook) |
| 365 | MOOT [records] | record values the deleted readers used; the Rust record carries none of them |
| 366 | PORT NOTE [homesteads, PARKED] | houses against the pond reed ring: the seat already walls the reeds off (driver.rs 417); the homesteads port must too |
| 367 | NOT NEEDED [sink, LIVE] | 0061 page puts the bank beyond the reed fringe; the pond bank stage is unported |
| 368 | MOOT | docstring or claim wording of deleted Python |
| 369 | MOOT | docstring or claim wording of deleted Python |
| 370 | NOT NEEDED | fixed: 0061 rolls a bank form for a pond that ends the runoff |
| 371 | CARRIED-FORWARD RISK [lanes/web, UNPORTED] | Mizuguchi: two ways side by side past a pitch; its test left the waiting list on 11-05 when the map moved (3876c3d494), replaced by a web fault still failing at the end: two lane ends 8 ft apart, unjoined (_KNOTS) |
| 372 | RESEARCH QUESTION | two copies: 0074 calls the undrawn alder-and-willow carr a shortfall and no task carries it; a feature to propose, not a defect |
| 373 | PORT NOTE [lanes/web, UNPORTED] | two copies: a way reaching the sink pond reeds would be reeded over; the Rust way out treats reeds as walls (driver.rs 417) |
| 374 | RESEARCH QUESTION | two copies: 0074 calls the undrawn alder-and-willow carr a shortfall and no task carries it; a feature to propose, not a defect |
| 375 | PORT NOTE [lanes/web, UNPORTED] | two copies: a way reaching the sink pond reeds would be reeded over; the Rust way out treats reeds as walls (driver.rs 417) |
| 376 | NOT NEEDED [sink, LIVE] | 0061 page puts the bank beyond the reed fringe; the pond bank stage is unported |
| 377 | MOOT | docstring or claim wording of deleted Python |
| 378 | NOT NEEDED | bundle note ("not in the bundle"), no finding about a map |
| 379 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 380 | CARRIED-FORWARD RISK [household groves, PARKED; lanes, UNPORTED] | as reported: cohort seed 904 drew two bamboo groves of one farm under lanes; groves are seated in rust/parked homesteads/grove_seat.rs and wood.rs 30 refuses a path over reserved grove seats, but the web that crossed them is unported; unverified |
| 381 | DUPLICATE | the village tier placeholder (feature 380); the row says so |
| 382 | DUPLICATE | the village tier placeholder (feature 380); cluster_anchor was already gone from the last Python |
| 383 | OLDER: wording | a module claim inherited by plumbing units; labels only |
| 384 | NOT NEEDED | fixed in the port: the brook is a tie-break and seat/margins.rs 422 quotes the page words |
| 385 | OLDER: research question | the brook share as an exact-tie break; a reading of 0035 |
| 386 | WORDING-FORMAT | a page silent on a figure or case the code decides (0035, 0081, 0071, 0087) |
| 389 | WORDING-FORMAT | a page silent on a figure or case the code decides (0035, 0081, 0071, 0087) |
| 390 | MOOT [old village paddy code] | water_field was not on the hamlet path (only captions named it); the Rust hem rolls each map crop mix (field/dry.rs 62) |
| 391 | MOOT [old village paddy code] | water_field was not on the hamlet path (only captions named it); the Rust hem rolls each map crop mix (field/dry.rs 62) |
| 392 | MOOT [old village paddy code] | water_field was not on the hamlet path (only captions named it); the Rust hem rolls each map crop mix (field/dry.rs 62) |
| 393 | MOOT [old village paddy code] | water_field was not on the hamlet path (only captions named it); the Rust hem rolls each map crop mix (field/dry.rs 62) |
| 394 | WORDING-FORMAT [seat, LIVE] | survived: driver.rs 417 cites only 0081 for the no-crossing rule; 0035 holds it. No map effect |
| 395 | RESTATEMENT | 0058 says the 90 ft tucked strip is "farmed and built on"; the seat refuses any anchor in the toe band (seat/margins.rs). The page meant wells |
| 396 | OLDER: wording / restatement | claim or comment wording, behavior fine |
| 397 | MOOT | docstring or claim wording of deleted Python |
| 398 | WORDING-FORMAT | a page silent on a figure or case the code decides (0035, 0081, 0071, 0087) |
| 399 | PORT NOTE [pond stock, UNPORTED] | latent: a sty seat near a short edge corner, or set outward on a concave parcel; the last Python turned the normal to the centroid (pondstock.py 69-71) |
| 400 | PORT NOTE [pond stock, UNPORTED] | latent: a sty seat near a short edge corner, or set outward on a concave parcel; the last Python turned the normal to the centroid (pondstock.py 69-71) |
| 401 | MOOT [pond stock, UNPORTED] | unit of a fallback and a gloss; wording |
| 402 | MOOT [pond stock, UNPORTED] | unit of a fallback and a gloss; wording |
