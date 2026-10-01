# Implementation Plan: rethinking the settlement review

**Feature**: 294 | **Date**: 2026-10-01 | **Spec**: [`spec.md`](spec.md) (FAITHFUL at round 3) | **Request**: [`request.md`](request.md)
**Research**: [`research.md`](research.md) (R0 census, R1 audit, R2 rulings, R3 rules) and [`rules-recon.md`](rules-recon.md)
(the engineering scout behind R3, with its measurements).

## Summary

Three moves (spec Summary): what geometry decides goes to a placer or a gate test and leaves every review (A, B); what needs
judgment is split into checks owed only on their occasion, decided by a script from the delta and the feature's declared
occasions (C, D, E); the reviews that remain are cut to their audited residue, capped at two rounds, refused before launch when
they cannot be reviewed, and measured by the ledger itself (F, G). The documents and guards then say so (H), and a cheaper tier
is tried per check once the contracts are small (I).

## Technical Context

**Language**: Python 3.12 (engine, scripts, tests), bash (guards). **Testing**: pytest through `make`; guard companions through
`make hooks-test`. **Constraints**: 100% coverage over the engine; the 1,000-line file bar; guard-file edits carry
`GUARD_EDIT_OK`; no hand edit of a hand-drawn sheet without the GM (memory: no hand-map edits in generator work).
**Single-artifact target**: Inashiro (`pool/hamlets/inashiro/inashiro.gen.py`) for every Mode B engine fix, then the pool;
`county-magistracy-example` for every Mode A engine fix, then the sheets. **Scale**: 5 scripted hamlets, 4 hand-drawn and 2
generated Mode A sheets, 18 legacy maps.

## Performance bookends (constitution VI)

The engine fixes (B4, B6, B8, B10) change the generator. `make perf LABEL=294-start` is taken on unmodified code before the
first engine edit and `make perf LABEL=294-end` before the push; `make perf-report AGAINST=294-start` diagnoses any seed more
than 5% slower.

| | label | total | median | worst | notes |
|---|---|---|---|---|---|
| before | `294-start` | | | | before the first engine edit |
| after | `294-end` | | | | before the push |

## Constitution Check

- I, II: N/A - no UI in this repository. III, IV, V, VII, VIII: N/A - no pool content of a recurring kind, no SOURCE blocks, no
  in-world prose. IX: N/A - no setting content.
- VI Verify before done: every task names its verification; engine tasks run reference map then pool (`make map`, then the
  gate's pool phase). The review agents are themselves the subject here; this feature's own map changes are verified under
  the NEW occasion rules it builds (D10).
- X Python: red-green per rule (each rule proved red on its recorded case or a seeded fault first, spec US2); ruff, pyrefly,
  100% coverage; the overlap tests read indexes built once (B: `shapely.STRtree` over the records each test compares).
- XII Research: every threshold below is labeled - research page, existing constant, or GUESS - in R3 and at its point of
  change. No new historical claim is made; where a finding class turns out to be decided by research (the privy's wind,
  R2.3) it is CUT, not ruled.
- XIII No regressions: baseline in `/tmp/base294` (detached worktree) before the first engine edit; a new rule that fails the
  pool is a defect FOUND, fixed in this feature (XIV), never ledgered as pre-existing.
- XVI Literal: the spec's lists are carried whole; every narrowing is in the Decisions table for the plan review.

## Design

### A. The record (FR-001, FR-013)

- **A1** `research.md` R1 is the audit; R2 rules on its six contradictions; R3 is the rule table. Each audit row's verdict is
  final once this plan's review is CLEAR.
- **A2** The census as a script: `scripts/_review_census.py` (`make review-census`) tallies the ledger by agent, check and
  class. Rows before this feature carry no class, so their classification is recorded ONCE as data -
  `docs/review-ledger-r0.json`, one entry per ledger row (row date + subject prefix as its key; counts per class, author-missed
  count, NOT-REVIEWABLE flag) - written by an Opus agent from the rows and checked by the script against R0's totals (SC-006:
  within R0's own error). Rows from this feature on carry their class in the row (G2) and need no side file.

### B. Geometry becomes rules (FR-003, FR-004, the audit's MOVED rows)

Every rule: a test that goes RED on its recorded case (the unfixed artifact from git history where it still exists, else a
seeded fault in a fixture), then green on the pool. Where the pool fails, the engine is fixed (XIV) and the map regenerated -
never the rule loosened. Thresholds labeled per R3.

Mode B (gate tests in `tests/gate/`, template `test_covers_298.py`; a placer guarantee where a placer decides):

- **B1** record against ink (FR-003 class 1): each `channels` record within 3 ft (GUESS) of drawn water ink, gates and weirs
  within 2 ft of water, no house on a `marshes` polygon. Kuwabata's 101 ft supply run is measured first (culvert ink or a
  defect).
- **B2** ruled edges on non-brook shapes (class 2): the brook's own rules (`straightest_run` share 0.4, the 1.6 deg axis rule,
  research W03/W04) applied to the VISIBLE edge of the marsh, grove and clearing classes, read from the page's class id map
  (`interactive/raster.id_map`, no browser).
- **B3** wood shed seating (class 3): nearer its own house than any other building and turned with it (research homesteads
  212/720; "own house nearest" GUESS) - placer assert in `homesteads/fixtures.py` plus a gate test.
- **B4** parallel twin watercourses (class 4): no two courses - comb branches INCLUDED - run parallel (within 15 deg) 12-32 ft
  apart for more than 60 ft (GUESS). The recorded case (ledger 2026-08-28, "twin branch canals ~25 ft apart") is two comb
  branches, and so are the four maps that fail today. A research pass on the spacing of a comb's branch canals runs first
  (constitution XII; the scout found no norm in `research/water`): if it FINDS an attested branch spacing, B4's test
  ENFORCES it with the citation - siblings at the attested spacing pass, a closer pair or a non-sibling pair fails - and the
  placer lays branches at it; otherwise the placer is fixed so branches are not laid side by side. The class goes back through
  the audit only if the research shows the spacing to be a matter of judgment.
- **B5** see-through marks (class 5): every mark drawn below 0.95 opacity belongs to a class on a declared list, each with its
  reason (drawing convention); seeded red with the mound at 0.9. The sheen half is CUT (`test_finish_287`). **B5b** broadleaf
  over conifer (the recorded case: feature 269 B30, broadleaf inked over earlier clumps' conifers): the crown records carry
  their species (the renderer knows it when it inks a crown), and a gate test refuses a broadleaf crown drawn after a conifer
  crown it overlaps (drawing convention: the conifer, the taller and darker mark, reads on top); proved red on the recorded
  case, the renderer's crown order fixed.
- **B6** page hit regions (class 7): each class wins at least 0.8 (GUESS) of its own ink in the id map, apart from overlaps
  `page.py` declares. Fails today (Kuwabata's mulberry dike takes 78% of the bund; the storage shed loses 18-20% to the
  farmhouse) - fixed in the page's hit order.
- **B7** lane tread to wall (class 8): at least 4 ft (GUESS; the recorded case is 3.85 ft; the research's ~3 ft eaves strip is a
  town figure) - the tread rule in `houses.py` and a gate test.
- **B8** side-by-side footbridges (class 11): no two decks within 60 ft (GUESS) - gate test.
- **B9** drawn against rolled (class 12): every rolled/drawn pair in `meta` drawn within 15% (GUESS) of the ROLLED VALUE - gate
  test. Fails today on Sawada's homestead wood (drawn at 60% of its roll): the placer is fixed, unless the research record
  shows the roll is a ceiling, in which case that finding is recorded and the test is drawn <= rolled and >= the floor.
- **B10** declared forms drawn (audit MOVED 1): every rolled fixture target drawn and every rolled minimum met. Fails today
  (Kuwabata privy 11/14, bath 2/5, household shrine 0 against a minimum of 1) - fixed in the fixture placer.
- **B11** house bearings (class 13): all houses within research homesteads/240 and 780's band (+-33.75 deg of the common
  bearing), no more than 2 at one limit - gate test.
- **B12** the brook in view (class 14): the brook crosses the view as one piece (drawing convention) - gate test. The "share
  off the frame" form is meaningless on a padded canvas (R3).
- **B13** lane law on the shipped maps (class 10): the needle (`NEEDLE_DEG`) and hairpin rules are placer guarantees already;
  a gate test over the shipped lanes proves it there.
- **B14** notes counts (FR-004): a map's current counts are stated in its census block, which the existing test checks against
  the manifest; outside the census block and the dated history entries (the Review log, the journal), a typed count of a
  manifest kind is refused unless it agrees with the manifest. The 55 disagreements the scout found are triaged in the same
  task: stale -> corrected, history -> moved under a dated entry.
- **B15** every pool and legacy map folder has a non-empty `.notes.md` (audit MOVED 2) - gate test.
- **B15b** a Mode A sheet's notes counts (audit B11, ~15 findings): the typed counts of a `data-kind` in a sheet's notes agree
  with the sheet's `data-kind` census, by B14's rule (outside dated history entries) - test over the sheets.
- **B15c** sized marks the size table misses (audit Z5): `make size-table` (`tools/pack_audit`) enumerates paths, circles and
  glyph marks as well as rects, and a test refuses a sheet with a tagged kind the table does not list.

Mode A (registry checks in `tools/pack_audit/registry.py`, each with its red fixture `tests/fixtures/<sheet>-<defect>-red.svg`
and its tier entry in `buildings/types.json`):

- **B16** `lodging_entrances` (door on every lodging block's outer wall); **B17** `privies_by_zone` (a latrine attached to the
  residence, one per court, at least 3 - research buildings/220, 310; the count GUESS) - fails on the generated
  `ochiba-roundtrip-test`, fixed in `compound.py`; **B18** `fire_water_distribution` (research buildings/170); **B19**
  `size_hierarchy` (research buildings/180); **B20** `sheet_furniture` (title present, no compass rose, no key box - SKILL.md);
  **B21** `roads_leave_the_frame` (a road end meets the frame, a gate, a door, a torii or another road); **B22** `palette_roles`
  (fill in the kind's allowed set; the table a drawing convention); **B23** `gate_feeds_its_road` (road no wider than its gate
  opening plus 1 ft - research buildings/480, feature 267); **B24** `mapmatch` gate side and width, roads read under every key,
  and an `**On map**` line required where a map records the sheet's subject (US5's home for plan-sheet agreement).
- **Hand-drawn sheets.** Where B21, B23 or B24 fails a hand-drawn sheet (Ochiba's 13.3 ft road into an 8 ft gate; Ubame's
  missing `**On map**`; Hoshigaoka's footpath 24 ft short), the fix is a hand edit, which the GM approves first (D8). The
  questions go to the GM in ONE message, through `escalation-check`, as soon as the failures are measured; the rest of the work
  proceeds meanwhile.

R2.3: FR-003 class 9 (privy and wind) is CUT - research homesteads/220 searched for a wind rule and found none; the seat is a
researched roll. Class 6 (reed gaps) is CUT by feature 298's tile (`test_covers_298.py`).

### C. The checks after this feature (FR-002, FR-007, FR-008)

| check (agent) | occasion | carries (audit rows) |
|---|---|---|
| `glyph-check` (new) | an element new to a map or sheet, whatever its mark; a glyph redrawn; an element's placement rule substantially changed | C1, B29, C2a residual, C2c, C2e, C5, C6a, C6b funerary, C7, C9c |
| `fix-check` (new) | a feature closing a defect the GM reported by eye | S17, S7 adequacy, X1 (did the fix fire) |
| `settlement-review` (cut) | a map new to the pool; a new settlement form; a new tier | C8 twin, C6d economy, "reads as a place"; C2b/C2d on a new tier |
| `building-review` (cut) | a sheet new to the pool; a sheet's layout revised; a new building program | B12, B13 siting, B17 + Z10-Z13 (merged), B20, B23, B30 |
| `size-audit` (cut) | a sized kind new to a sheet; a new building program | Z6 anchors (a band then enforced), Z10 voids |

Every contract keeps the PROCESS rows the audit keeps (scale, measure independently, every finding names its norm, never ask
the GM what history answers, no edits, the verdict record) in a shared short form. Every struck subject (C3, C4a-f, C6b
outcast, C6c, C9b, B6, B9, B21, B22, B24, B28 wording) is deleted, and its home recorded in R1. The tier-only obligations
(outcast and status zoning, the border rule, the Imperial-road caption) are written into the migration plan's town/city rows.
Page prose (X3, BX) is the record checks' (`entry-drift` owns a modal against its research section); no map review carries it
(R2.6). New agent files carry `omitClaudeMd: true` and their tier row in `test_agent_models.py` (Opus high until I), and are
pre-authorized in `container-scripts/append-system-prompt.md`.

### D. "Is it owed": occasions (FR-005, US3, US4)

- **D1** `scripts/_review_owed.py` is rewritten to answer OCCASIONS. An owed unit is `<check>:<subject>` (`glyph-check:privy`,
  `settlement-review:<map>`, `building-review:<sheet>`, `size-audit:<kind>`, `fix-check:<map>`), with the one map or sheet it
  is reviewed on. Detected from the delta against the merge base:
  - a pool manifest new to the tree -> `settlement-review:<map>`, plus `glyph-check` for each ink class new to the pool legend;
  - an ink class in a map's `ink_classes` that its base manifest lacks -> `glyph-check:<class>`, reviewed on the first such map;
  - a Mode A sheet new to the tree -> `building-review:<sheet>`; a `data-kind` new to a sheet -> `glyph-check:<kind>` and
    `size-audit:<kind>`.
  Declared, from an `## Occasions` section of each active feature's `tasks.md` (one line each): `glyph-redrawn: <class>`,
  `placement-changed: <class>`, `new-form: <map>`, `new-tier: <tier>`, `layout-revised: <sheet>`, `new-program: <type>`,
  `gm-fix: <map> - <the complaint>`, or `none: <why>`.
- **D2** A delta that touches drawing or placement code (`l7r/**/*.py` outside tests, a pool `gen.py`, a tracked sheet SVG) with
  NO `## Occasions` section in any active feature is refused at push by `review-gate.sh` and named by `make verify`: the
  substantial-versus-minor call is the feature's to declare, and an undeclared one is the silent case the GM's tannery example
  forbids.
- **D3** "A manifest moved" is gone as a trigger; the rendering-only waiver (feature 248) goes with it - a rendering feature that
  redraws a glyph owes the glyph check, and one that redraws nothing owes nothing anyway.
- **D4** `make verify` prints the owed units and writes one prompt file per unit (`.git/review-snapshot/<unit>/dispatch.md`,
  the unit's subject, occasion and the one map or sheet to look at); no what-moved report is built (FR-006: no check needs one
  - the glyph check is told the element and the map, which is its input).

### E. The guards (FR-005, FR-007, FR-009)

- **E1** `pair-hooks.sh`: the review branch covers the five agent types; one unit per dispatch; a dispatch is refused unless
  the gate is GREEN for this engine key (not merely running - US6: a red gate is found before launch, never mid-run); the stop
  branch holds the turn while an owed unit has no dispatch, run or record. `_review_prereq.py`, `_review_snapshot.py` and
  `make review-verdict` (`UNIT=`) generalize from map to unit.
- **E2** Rounds: `.git/review-rounds.json` counts dispatches per (feature, unit); a third is refused unless
  `REVIEW_ROUNDS_OK="<the GM's words>"` (logged).
- **E3** `review-gate.sh`: a push ships when every owed unit has a PASS or NEEDS-WORK record at the pushed engine key; a moved
  map that owes nothing ships; the notes-touch fallback goes; D2's refusal is added.
- **E4** Every guard edit carries `GUARD_EDIT_OK` and its companion cases in `test-pair-hooks.sh`, `test-review-gate.sh`, run by
  `make hooks-test`, each proved by deleting the branch and watching a case go red.

### F. Replays (SC-001, SC-002, SC-005)

`scripts/test-review-owed.sh` (or a pytest over `_review_owed.py` in temporary repositories): an engine change moving all five
manifests with `none:` declared owes zero units; one new ink class owes one `glyph-check`; a declared redraw and a declared
re-placement (the tannery, seeded) each owe one; a new element reusing an existing glyph (a new class key drawn with an existing
mark) owes one; a red gate refuses a dispatch (the 280 and 293 cases replayed by their shape: gate red at dispatch, record
missing).

### G. The ledger measures itself (FR-010)

- **G1** `scripts/_review_cost.py` (`make review-cost AGENT=<id>`) reads a finished agent's transcript under the session's
  `subagents/` directory and prints its wall time and tokens (input, cache read, output) as the ledger's cost cells.
- **G2** The ledger gains a new table for rows from this feature on: `date | check | subject | verdict | finding | class |
  author missed? | acted on | wall | tokens`. `scripts/_ledger_lint.py` refuses a new-table row with an empty or unknown check,
  class or cost; it runs in a new guard `ledger-hooks.sh` on a `git commit` that stages `docs/review-ledger.md` (spec: refused at
  commit), with its companion test.
- **G3** `make review-census` (A2) prints R0's table and the per-check totals, the new table included.

### H. The documents (FR-011, US9)

The root `CLAUDE.md` (review bullet; the pair-hooks row of the guard table; a ledger-hooks row), `dev/reviews.md`,
`docs/spec-kit-and-reviews.md`, `docs/guards.md`, the constitution's lines that make the review per-map, the plan template's VI
line, `SKILL.md`'s review mentions, and the memory note on the 2026-08-29 ruling. `make stale-terms F=294` over the retired
trigger's phrases ("layout moved", "manifest moved", "every map whose") finds none left.

### I. The cheaper tier (FR-012, US8)

After C: per check, against SEEDED cases with known findings (glyph-check: the manure heap read as a bush and the rack as a
woodpile, from their commits; building-review: a recorded circulation finding; settlement-review: a seeded twin - a pool map's
layout submitted as a new map - and a map whose notes declare a trade it does not draw; size-audit: a recorded anchor finding;
fix-check: the canopy record of feature 240), Sonnet at the check's effort, three runs a leg against an Opus leg, through
`specs/251-*/measure/seeded.py`. A check moves tier only where every Sonnet run finds the seeded finding; if Opus itself
misses it, that is recorded and the check stays on Opus. Small slices (memory: conserve tokens in validation runs).

## Order of work

1. A1 record (this plan) -> plan review. 2. Baseline worktree and `294-start` bookend. 3. D + E + F (the trigger and the
guards, with replays) - first, because every later engine task is verified under them. 4. C (the contracts). 5. B (the rules,
Mode B then Mode A; engine fixes on the reference artifact, then the pool). 6. G, A2. 7. H. 8. I. 9. `make done`, the owed
checks this feature's own delta declares, `294-end`, land.

## Decisions (for the plan review)

The plan review of 2026-10-01 (round 1) ruled five of these NOT LEGITIMATE as first written (B4's comb exemption, class 12
against the roll's range, broadleaf over conifer sent to the glyph check, the tier experiment skipping settlement-review, and
the audit's B11/Z5 rows left with no home); each is rewritten above. Its LEGITIMATE narrowings (D5, D6a, D6b, D7 class 14,
D15) go to the GM once the implementation works.

| id | decision | class |
|---|---|---|
| D1 | Owed units are `<check>:<subject>`; elements new to a map are detected from `ink_classes` / `data-kind`, the rest declared in `tasks.md` | within (FR-005, FR-007) |
| D2 | A delta touching drawing/placement code with no `## Occasions` section is refused at push | within (US4: "the script refuses a delta ... with no declaration") |
| D3 | The rendering-only waiver of feature 248 is retired with the manifest trigger | within (US4: rendering features are not exempt) |
| D4 | A dispatch needs a GREEN gate, not a running one - the overlap of gate and review (feature 151) is given up | within (US6: NOT-REVIEWABLE never costs a run) |
| D5 | FR-003 class 9 (privy and wind) CUT: research homesteads/220 found no wind rule; the seat is a researched roll | narrowing (FR-003 class 9 not ruled) - the spec's escape "a class the research shows to be ..." names judgment, not research |
| D6 | FR-003 class 6 (reed gaps) CUT by feature 298's tile; class 5's sheen half CUT (`test_finish_287`); broadleaf over conifer RULED (B5b) | narrowing (parts of classes 5 and 6 not ruled) |
| D7 | Class 12 ruled against the rolled value (B9); class 14 ruled as the brook crossing the view as one piece (the "share off the frame" form is meaningless on a padded canvas) | class 14: narrowing (the class's recorded wording changed) |
| D8 | A new Mode A rule failing a HAND-DRAWN sheet waits on the GM's approval of the hand edit, asked once, in one message | within (standing GM rule; the rule itself is not loosened) |
| D9 | Page prose (place card, modals) belongs to `entry-drift`, not a map review | within (the audit's X3/BX: out of every map-review contract) |
| D10 | This feature's own delta is reviewed under the occasions it builds: it declares its occasions in `tasks.md` | within |
| D11 | Thresholds labeled GUESS: B1 3 ft / 2 ft, B4 60 ft and 15 deg, B6 0.8, B7 4 ft, B8 60 ft, B17's count of 3, B22's table | within (each recorded at its point of change) |
| D12 | The tier experiment runs on every check against seeded cases (settlement-review's: a seeded twin, a declared trade not drawn) | within (US8) |
| D13 | Old ledger rows are classified once into `docs/review-ledger-r0.json` by an Opus agent; new rows carry their class | within (FR-013) |
| D15 | Counts in dated history entries (the Review log, the journal) are not checked by B14: they are history, and only a current claim moved under a date would abuse it | narrowing (FR-004 "every count") |
| D16 | B4 covers comb branches; research on a comb's branch spacing first | within (FR-003 class 4) |
| D17 | B15b and B15c rule the audit's B11 and Z5 rows (MOVED) | within |
| D18 | A hand-drawn Mode B map (the legacy tree) owes no review, detected or declared; a Mode A sheet keeps its review wherever it lives (`_review_owed.exempt`). Ubame's sheet opts out of the town map's match (the map is hand-drawn, its match owed at conversion); Ochiba's road narrowed to its 8 ft gate | within (the GM's ruling, 2026-10-01, request.md) |
| D19 | B21: a road or footpath walked to a well or the precinct clearing has arrived (`DESTINATION_KINDS`; the rule's grounds are an approach stopping short of the frame). B15c: a kind tagged on captions alone has no drawn extent and owes no size row (the hand sheets' ancestral alcove) | within (each rule's own grounds, escalation-check 2026-10-01) |
| D20 | T34: `settlement-review` and `fix-check` move to Sonnet (Opus and 3/3 Sonnet found the seed); `glyph-check` stays on Opus (Opus missed its seed, recorded), `building-review` (0/3) and `size-audit` (2/3) stay | within (US8's rule) |
| D14 | `building-review` keeps Mode A layout, program and coherence in one agent with per-occasion sections; `size-audit` keeps anchors; their duplicate dead-space sweeps merge into `building-review` | within (US4 allows a shared agent with a per-check contract) |
