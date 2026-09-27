# Feature 271 - research

## R1. The audit (FR-001), 2026-09-27

**How big the sweep was.** The census (`measure/census.py`) found:
- 357 kinds (manifest categories, by tier) drawn on the maps: the scripted pool, the 18 hand-drawn legacy maps
  (hamlets, villages, towns and provincial cities) and Shiro Daika in `wip/`;
- 138 map and sheet modals;
- 338 research questions, 54 of them with no quoted evidence at all.

Four domain audits turned these into 620 questions a map needs. Each one says what a thing is, how big it is, how
many there are, where it stands and how it differs by tier and by region. The questions cover tiers not yet
scripted, and each is marked COVERED, THIN or NONE against the record:

| audit | rows | covered | thin | none |
|---|---|---|---|---|
| farming (hamlet, village) | 155 | 74 | 50 | 31 |
| towns | 132 | 31 | 66 | 35 |
| cities and capitals | 175 | 89 | 63 | 23 |
| buildings and religion | 158 | 69 | 64 | 25 |

Rows already owned elsewhere were left with their owners:
- 267: magistracy and compound buildings (R01-R53);
- 268 and 270: shrines, the country shrine hall's size and precincts;
- 269: the farming pages' B01-B46, city defenses, government, fabric, hinterland and sizing;
- 272: temples and shrines beyond the country shrine, and the religious tier table.

The rest were deduplicated across the four domains and packed into 33 write groups, 172 rows, in `inventory.md`.

**Where the GM's examples are:**

| the GM's example | row | group | state (2026-09-27) |
|---|---|---|---|
| how much larger is the village headman's house | A74 D95 | V7 (homesteads 520-580) | written, in its checks |
| the real size of a country shrine where a country monk lives | - | feature 270 (Diagram shrines) | 270's, from religion-and-death 120's bands |
| inns | B67 B68 C110 D135 | T3 (towns 320-370) | written and checked |
| dojos | C141 D143 | G2 (buildings 760-810) | queued after G1 |
| governor's mansions | C27 D125, C28 D126 | K2 (cities/government 200-270) | todo |
| smiths | A149 B48 C129 | U4 (urban-features 430-490) | todo |
| tanneries | B58 C126, C127 | covered by feature 265 (urban-features 060-068); the direction out of town (B59 C127) is in U1, now in its checks | in progress |
| gate markets | B11, C175 | T4 (towns 380-430); the city side is 269's hinterland 040 | written and checked |

The State table in `inventory.md` is where each group stands; it is updated at each hourly wake.
