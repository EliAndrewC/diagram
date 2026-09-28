# Feature 271 - plan

### D1 - The audit is a census, then four domain audits, then one merge (FR-001)

`measure/census.py` counts what the maps and the record already hold, with no judgment:
- every manifest category and sub-kind on every map in `pool/`, `legacy-hand-authored-pool/` and `wip/`, by tier;
- every map and sheet modal with its label and `Entry:`;
- every research question with its number of quoted notes and absence notes.

A question with no quoted note is flagged THIN. Four Opus agents then judge coverage, one per domain: farming,
towns, cities and capitals, buildings and religion. Each reads the census, the record's headings and the deferred
work lists, and adds the questions a map of each tier will need, including tiers not yet scripted. Each marks the
owner of every row against the other sessions' claims. One more agent merges the four: it removes duplicates across
domains, applies the owners confirmed by message, and packs this feature's THIN and NONE rows into write groups by
record page. That merge is `inventory.md`. Its `## State` table is the resume point (FR-005).

### D2 - The backfill uses 269's brief generator, adapted (FR-003)

`briefs/gen.py` is 269's generator (itself 267's and 250's pattern) with four changes:
- it reads the groups from `inventory.md`'s own headings;
- it reserves prefixes with `make reserve`, which is on main since 265;
- it names every other session's sections as off limits;
- each check session adds an owed-modal step. It runs `entry-drift` on each pair `_entry_owed.py` names on its own
  questions, records the verdict in `owed-verdicts.md` and runs the sheet-modal tests. 265 found that owed sessions
  skipping those tests leave broken Caveats.

`briefs/queue.sh <n> <GROUP>...` runs a group's write brief and then its `-checks.sh` in queue clone `<n>`, one group
after another. `scripts/pull-queue.sh <n>` brings a finished queue back. Up to three queues run at once. A group is
claimed in `RESEARCH-CLAIMS.md` and announced to "Diagram supplemental" before it is queued (FR-002).

### D3 - Order, landing and resumption (FR-003, FR-005)

Groups run in the inventory's order: already drawn, then village, then town, then city and capital. A finished
group is pulled back and committed. A batch of groups lands on main after `make page-check`, `make done` and
`owed-check`, so that other sessions build on it.

`tasks.md` carries only the batch being worked. `scripts/sync-with-main.sh` refuses any feature with an open task, so
a batch lands once all its tasks are ticked, and the next batch's tasks are added after that push. Rows the work has
not reached keep `todo` in the State table; they have no task yet.

The runner resumes a page session the usage limit stopped. An hourly `CronCreate` wake (job `13e01f26`) restarts a
stopped queue and continues the next groups.

### D4 - Sources (FR-004)

A write session saves pages with `make source-pages` and reads through `source-reader`. It adds a free source it
cannot fetch at the end of `TO-DOWNLOAD.md` in the GM's format. The orchestrator's closing report counts them.
