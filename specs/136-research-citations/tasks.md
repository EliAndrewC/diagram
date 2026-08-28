# Tasks: Every Research Finding Cites Its Sources (136)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [ledger.md](ledger.md); authority [gm-request.md](gm-request.md)

Every task below is `research: physical` (each is about how a place was built, farmed or lived in) and carries the three boxes; a batch task is ticked only when every ledger row it owns is closed (`re-sourced` / `supplemented` / `no-source` / `contradicted`) and its `source-reader` verdicts are on record. No task touches an engine path, a pool artifact or an operative rule's text (FR-006).

## Phase 1 - Setup

- [x] T01 [US1] **The inventory ledger** - `specs/136-research-citations/ledger.md`: 117 research-tree candidate rows (73 `not recorded` + 44 with no sources line), the standalone research documents, the inline-grounding rows (top-level `settlements.md` and pool notes included), 12 spec-research rows, the engine-comment findings, the `SOURCES.md` queue, an empty contradictions section. Taken 2026-08-28 by an entry parser over `research/**/*.md` plus a grep of the other homes; the batch tasks refine it.
      research: procedure
## Phase 2 - The passes (US2 + US3), one research file per task

_Method per batch is plan.md "Method, per batch": (1) diff the operative doc's inline grounding against the tree and add ledger-B rows; (2) search pass, China-first, Japan corroborating, primary/scholarly first, never Grokipedia; (3) one background `source-reader` dispatch with every claim verbatim; (4) write keys, sources lines, supplements, corrected classes, contradictions; (5) ledger + queue; (6) quick run, commit, push attempt._

- [ ] T02 [US2][US3] **`research/archetypes.md`** - 9 open rows; grounds `settlements/archetypes.md`; inline grounding in that operative doc inventoried first (ledger C).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T03 [US2][US3] **`research/buildings.md`** - 9 open rows; grounds `buildings.md + buildings/programs.md (Mode A)`; inline grounding in that operative doc inventoried first (ledger C).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T04 [US2][US3] **`research/cities/capitals.md`** - 20 open rows; grounds `settlements/capitals.md`; inline grounding in that operative doc inventoried first (ledger C).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T05 [US2][US3] **`research/cities/defenses.md`** - 2 open rows; grounds `settlements/cities/defenses.md`; inline grounding in that operative doc inventoried first (ledger C).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T06 [US2][US3] **`research/cities/fabric.md`** - 2 open rows; grounds `settlements/cities/fabric.md`; inline grounding in that operative doc inventoried first (ledger C).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T07 [US2][US3] **`research/cities/government.md`** - 1 open rows; grounds `settlements/cities/government.md`; inline grounding in that operative doc inventoried first (ledger C).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T08 [US2][US3] **`research/cities/hinterland.md`** - 1 open rows; grounds `settlements/cities/hinterland.md`; inline grounding in that operative doc inventoried first (ledger C).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T09 [US2][US3] **`research/cities/river-cities.md`** - 2 open rows; grounds `settlements/cities/river-cities.md`; inline grounding in that operative doc inventoried first (ledger C).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T10 [US2][US3] **`research/fields.md`** - 6 open rows; grounds `settlements/fields.md`; inline grounding in that operative doc inventoried first (ledger C).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T11 [US2][US3] **`research/homesteads.md`** - 9 open rows; grounds `settlements/homesteads.md`; inline grounding in that operative doc inventoried first (ledger C).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T12 [US2][US3] **`research/religion-and-death.md`** - 5 open rows; grounds `settlements/religion-and-death.md`; inline grounding in that operative doc inventoried first (ledger C).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T13 [US2][US3] **`research/towns.md`** - 5 open rows; grounds `settlements/towns.md`; inline grounding in that operative doc inventoried first (ledger C).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T14 [US2][US3] **`research/urban-features.md`** - 15 open rows; grounds `settlements/urban-features.md`; inline grounding in that operative doc inventoried first (ledger C).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T15 [US2][US3] **`research/vegetation.md`** - 8 open rows; grounds `settlements/vegetation.md`; inline grounding in that operative doc inventoried first (ledger C).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T16 [US2][US3] **`research/water.md`** - 9 open rows; grounds `settlements/water.md`; inline grounding in that operative doc inventoried first (ledger C).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited

- [ ] T17 [US2] **Historical spec research files** (ledger D, 12 files) - each historical finding cited in the research-tree entry it grounds (pointer from the spec file), or given its own `**Sources:**` line; technical research left alone.
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited

- [ ] T18 [US2] **`SOURCES.md` queue and README** (ledger F) - every queue row struck or documented unresolvable with what was searched (FR-009, SC-005); README's stale "72 of the 83" sentence replaced with the final count.
      research: procedure

## Phase 3 - Close

- [ ] T19 [US2] **Standalone research documents and engine comments** (ledger B and E) - `flophouse-research.md`, `town-deep-audit.md`, `town-checks-audit.md`, `pending-enclosed-fan-floor.md`: each historical finding cited in place or pointed at a cited tree entry; every finding stated in an `l7r/**/*.py` comment recorded and cited in the tree, the code untouched (FR-006).
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T20 [US3] **The GM's contradiction review** - the report to the GM (ledger G: each contradicted finding, what the record said, what the sources say, rule + checks + maps affected, fix-now / future-work), or the explicit statement that there were none; plus the proposed sources-registration check listed as future work for the GM to accept or decline (FR-010). **Closed by the GM**, who decides each row; a fix-now decision becomes its own feature or task - never a change made inside this one.
      research: procedure
