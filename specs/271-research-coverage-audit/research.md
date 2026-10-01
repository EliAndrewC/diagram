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
| how much larger is the village headman's house | A74 D95 | V7 (0034, 0050) | written, in its checks |
| the real size of a country shrine where a country monk lives | - | feature 270 (Diagram shrines) | 270's, from 0222's bands |
| inns | B67 B68 C110 D135 | T3 (0185, 0186, 0188) | written and checked |
| dojos | C141 D143 | G2 (0095, 0153, 0154, 0184) | queued after G1 |
| governor's mansions | C27 D125, C28 D126 | K2 (0167, 0168, 0169) | todo |
| smiths | A149 B48 C129 | U4 (0051, 0205, 0206) | todo |
| tanneries | B58 C126, C127 | covered by feature 265 (0193); the direction out of town (B59 C127) is in U1, now in its checks | in progress |
| gate markets | B11, C175 | T4 (0127, 0128, 0129); the city side is 269's hinterland 040 | written and checked |

The State table in `inventory.md` is where each group stands; it is updated at each hourly wake.

## R2. The work resumed by itself (FR-005), 2026-09-27

Two stops have happened so far, and the work resumed from each without the GM:
- **The dispatching session's process ended (about 12:00 UTC), killing all five queue runners mid-way through
  their write sessions.** Each session's work sat uncommitted in its queue clone. The runner gained a
  `resume:<sid>:<brief>` item, and every queue was relaunched with its interrupted session RESUMED, not restarted.
  Nothing was redone and nothing was lost (`t1`, `v1`, `v3`, `t3`, `v6`; the runs are logged in
  `/home/agent/.claude/jobs/d2f6f26d/tmp/resume-q*.log`).
- **The five-hour usage window ran out at 13:37 UTC.** Each queue logged `failed <sid> rc=1 - waiting <n> min, then
  resuming it`. At the reset (16:41 UTC) all five resumed the same sessions and went on (the `run-*.log` of
  queues 1-5).

This session's own context is compacted when it fills, and it continues from `inventory.md`'s State table and the
memory note `project-research-coverage-271`. An hourly scheduled wake (`CronCreate` job `13e01f26`) checks the
queues and continues the next groups. Neither covers a crash of the whole container: the terminals crashing again
would need the GM to resume this conversation.

## R3. What the backfill closed (FR-002 to FR-004), 2026-09-28

Every one of the audit's 33 groups (172 rows) is closed. 29 landed in three batches: batch 1 (`010034db`), batch 2
(`2c0cefa78`) and batch 3 (this landing). The other four (R2, R3, R4, D63) were done by Diagram shrines, feature
272, and their outcomes are in `inventory.md`.

- **What changed in the record.** 169 questions were written or rewritten. 101 of them are new: urban-features 31,
  cities/government 12, buildings 11, ways 6, towns 6, cities/defenses 6, cities/capitals 6, water 5,
  cities/fabric 5, archetypes 5, cities/river-cities 4, religion-and-death 2, fields 2. Each has quoted footnotes
  and passed quote-check, record-format and source-applicability. 73 of the new questions end in a
  `The rule the map follows` specification for tiers that no generator draws yet.
- **What is still silent.** 80 of the new questions carry at least one absence note. Each note names what was
  searched, and the claim it covers is labeled GUESS where it reaches a rule. Most of these are shares and
  frequencies: how many hamlets, how many households, how large a typical example was. Pages describe a form far
  more often than they count it.
- **What waits on the GM.** Free sources that bots cannot fetch were appended to
  `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` as they were found, each with both links. The list now runs to
  No. 277; this feature's queues added entries alongside features 269 and 272. Reading the copies the GM downloads is
  its own feature (GM 2026-09-28), not part of this one; reading a downloaded copy re-opens
  the absence note it would answer.
- **Owed follow-up.** Religion-and-death 400 points at 540 (feature 273's question, where a hamlet's dead lie).
  The link is live now that 273 has landed.
