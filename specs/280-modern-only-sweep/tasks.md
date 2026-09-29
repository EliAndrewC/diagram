# Tasks - feature 280, the modern-only sweep

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D8). Inventory: [`inventory.md`](inventory.md) (M01-M130, 41 groups). Queue: [`queue.txt`](queue.txt). Briefs and handoffs: [`briefs/`](briefs/).

## Phase 1 - audit and queue

- [x] T01 The audit: seven Opus agents over every record page, the kinds and knobs, and the pool, legacy and magistracy maps; consolidated into `inventory.md` (D1, FR-001, FR-002)
      research: procedure
      verify: DONE. seven Opus audits over every page, kind, knob and map (outputs /tmp/l7r-check/280-audit/out-1..7), consolidated into inventory.md: 130 items, 611 sections accounted for
- [x] T02 The research queue: `briefs/gen.py`, the 41 write briefs (each at most four questions by `scripts/_brief_load.py`), the `<g>-checks.sh` steps, `sync.sh`, `wait269.sh`, `queue.txt` (D2, D3, FR-004)
      research: procedure
      verify: DONE. 41 write briefs, each 2-4 questions by scripts/_brief_load.py; check generator dry-run on a dummy handoff (check-a 2, check-b 1, kind=check); queue.txt and queue-269.txt; plan review CLEAR round 2

## Phase 2 - the research (one write session, then its check sessions, per group; queue order; D2, D3)

- [x] T03 W2 water: the separated net and where it runs (M32-M34; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. group W2 written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); outcomes M32-M34 are rows of outcomes.md
- [x] T04 W1 water: channel widths (M28-M31; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T05 F1 fields: the comb's layout and the drain's head (M01-M02; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T06 F3 fields: the plot-layout knobs and the rice-hill mottle (M06-M08; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T07 F2 fields: the dry plots and the flower field (M03-M05; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T08 H2 homesteads: the yard, the byre, the shed and the sty (M16-M19; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T09 H1 homesteads: the grove and the windbreak's measure (M13-M15; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T10 Y1 ways: bridge landings and the plank (M82-M83; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T11 U1 urban-features: wells and troughs (M96-M98; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T12 R2 religion-and-death: burial grounds and cremation grounds (M68-M71; holds: 272 (done))
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T13 R1 religion-and-death: the shrine's arches, fence, collar and salt (M64-M67; holds: 272 (done), 267 (done))
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T14 B1 buildings: the kitchen, the house and the privy (M109-M112; holds: 267 (done))
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T15 B2 buildings: the garden, the gate board, the striking bundle and the door leaf (M113-M116; holds: 267 (done))
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T16 A2 archetypes: polder parcels, pond layout, planting and sluices (M54-M57; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T17 A1 archetypes: the lotus overlay (M51-M53; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T18 T3 towns: the hayfield and the edge wood (M90-M92; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T19 T1 towns: the caravan inn, its stable and the flophouse (M84-M86; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T20 T2 towns: the built core and its reach (M87-M89; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T21 U4 urban-features: the flophouse quarter and the farrier (M107-M108; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T22 U2 urban-features: brewery, pawnshop and smithy (M99-M102; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T23 U3 urban-features: the boom, the charcoal yard, the bales and the huller (M103-M106; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T24 C1 cities/capitals: the funerary ground's clearance, the castle's area and the sluice's calendar (M120-M122; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T25 C2 cities/river-cities: offtake angles, private landings and the boatmen's shrine (M123-M125; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T26 C3 cities/government and cities/fabric: the generous samurai lot and the storehouse cap (M126-M127; holds: none)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T27 R3 religion-and-death: temple precincts and clergy homes (M72-M73; holds: 272 (done))
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T28 B3 buildings: the Chinese drill hall, the carters' inn and the barracks' bunk rooms (M117-M119; holds: none (M119's kind was written by 267, done))
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T29 F4 fields: the bund, the water, the collector and the pond (M09-M12; holds: 269) - the first 269-held group: after `wait269.sh`; if 269 has not landed in 24 hours the queue stops and `queue-269.txt` starts it later (plan D3)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T30 W3 water: the canal berm and the weir (M35-M36; holds: 269)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T31 W4 water: pond margins and wet ground (M37-M39; holds: 269)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T32 H3 homesteads: outbuildings by the 1972 count (M20-M21; holds: 269)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T33 H4 homesteads: the bath shed and the privy (M22-M23; holds: 269)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T34 H5 homesteads: shares and sizes from twentieth-century counts (M24-M27; holds: 269)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T35 V1 vegetation: the belts and groves' extent (M40-M43; holds: 269)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T36 V3 vegetation: kept-cut margins and bamboo (M47-M50; holds: 269)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T37 V2 vegetation: crown size and stocking (M44-M46; holds: 269)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T38 A3 archetypes: the water-to-dike ratio and the fry ponds (M58-M60; holds: 269)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T39 A4 archetypes: pigs and manure on the dikes (M61-M63; holds: 269)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T40 R4 religion-and-death: burial-ground size, water and distance (M74-M77; holds: 269)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T41 T4 towns: the farm belt and the paddy plot (M93-M95; holds: 269)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T42 C5 cities/fabric, cities/hinterland and cities/defenses: the open reserve, farming inside the wall, and moat width (M128-M130; holds: 269)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md
- [x] T43 R5 religion-and-death: shrine precincts, gifts and the basin (M78-M81; holds: 279, 272 (done)) - runs last; 279's sections are researched and their text handed over (OWED-TO 279) while 279's line is open (plan D3)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. the group written and checked in its page sessions (source-reader, quote-check, record-format, source-applicability applied per its handoff); its outcomes are rows of outcomes.md

## Phase 3 - the eliminations (after the research; 269's modules after 269 lands; D4-D6)

- [x] T44 Gather every handoff's `M<nn>` lines into `outcomes.md`, and confirm each of M01-M130 has an outcome line or an exclusion naming its owner before phase 3 starts; apply each `OWED-TO` text through a `briefs/extra/` brief once its hold clears, or send it to the owner; the spec's Decisions Recorded gets one line per outcome (FR-003, SC-002, plan D3)
      research: procedure
      verify: DONE. outcomes.md: 130 rows, M01-M130 each with an outcome; no exclusion (269 and 279 landed); every OWED-TO text applied (fd8dc79cd); Decisions Recorded one line per elimination
- [x] T45 Report to the GM through `escalation-check`: each GM ruling a MODERN-ONLY outcome reverses, each form ruled in knowingly (held until the GM rules), and the `undated-custom` set (spec D1) (D5, FR-006, SC-004)
      research: procedure
      verify: DONE. escalation-check judged the GM report four times (2026-09-29): 4 items need the GM (M50, M52/M53, M64); the rest informational, in the final message
- [x] T46 Eliminate the MODERN-ONLY forms and calibrate the MIXED degrees in modules OUTSIDE 269's `briefs/engine/groups.md`: knob options removed, generators stop drawing the form, detached-worktree baseline first (D4, FR-005)
      research: rendering
      verify: DONE. 43 eliminations in the engine, the kinds and the sheets (outcomes.md); baseline in a detached worktree /tmp/base280; the gate's regressions fixed (Kashikawa hook, Sawada network, the 282 oracle)
- [x] T47 The same in 269's modules, once 269 has landed (D4, FR-010)
      research: rendering
      verify: DONE. 269 landed before phase 2; its modules (burial, bamboo, the dike-pond, the bearing) were changed in the same pass as T46
- [x] T48 The kinds follow: retired, or their `Entry:`, label and prose rewritten; `entry-drift` IN-STEP on a bundle for each (FR-009, SC-005)
      research: rendering
      verify: DONE. entry-drift on 44 owed pairs (7 agents): 20 DRIFTED rewritten from their sections, 24 IN-STEP; bathhouse/woodpile renamed bath room/wood shed; PondSluice retired
- [x] T49 The frozen legacy maps: each MODERN-ONLY form they draw written against the map in `migration-plan.md`, owed at conversion; the list to the GM through `escalation-check` (D6, FR-007)
      research: procedure
      verify: DONE. the 17 legacy-only items by map in future-work/farming-communities.md, towns.md and cities.md, pointed at from migration-plan.md; the list goes to the GM in T45's escalation-check
- [x] T50 Regenerate each motivating pool map; `settlement-review` / `building-review` one map per agent, a ledger row each; the magistracy sheets edited by hand where a Mode A form goes, with `building-review` (SC-003)
      research: rendering
      verify: DONE. five hamlets regenerated; settlement-review six rounds, PASS x5 at key 098165c0 on a green gate; building-review of the Hoshigaoka and Ubame sheets, fixes applied; ledger rows in docs/review-ledger.md
- [ ] T51 `make done` green, the landing (`scripts/sync-with-main.sh done`), the claims line closed (SC-006)
      research: procedure
