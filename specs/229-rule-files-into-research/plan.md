# Implementation Plan: 229 - the rule files retire into the research pages

**Spec**: [`spec.md`](spec.md). **Request**: [`request.md`](request.md). **Inventory**: [`audit/`](audit/).
**Writer rulebook**: [`migration-rules.md`](migration-rules.md).

## Summary

Thirteen rule files (`settlements.md`, eleven `settlements/*.md`, five `settlements/cities/*.md`; ~670 KB) are
retired. Their decision records and unencoded specifications land on the research pages (fifteen existing, four
new), physical claims that move go through the research pass, every pointer in the tree is re-pointed to a
research anchor, the record's tests hold the new state, and the pages are checked by the record's two agents.
No map changes; no engine behavior changes (comment-only edits and one docstring `Entry:` tag).

## Technical Context

- **Language / tooling**: hand-authored HTML under `research/`; Python tests under `tests/interactive/`;
  `make citations` / `make glossary` derive the assets; `make page-check` is the page gate; `make done` the full
  gate (its engine key does not move - comments and docstrings are stripped from it; the browser key does).
- **Landing route**: derived by `sync-with-main.sh` from the delta. Engine `.py` files change in comments only,
  which `ci/delta.py` classes as not engine code; the `Entry:` docstring tag is page content. Expected DIRECT with
  a green `make page-check` and a green `make done`.
- **Concurrency**: one Opus writer per target page (fourteen writers), each editing only its page and its
  citations page; the session makes every cross-page edit (engine comments, tests, docs, SOURCES.html, glossary)
  centrally. `source-reader`, `quote-check`, `record-format` and `source-applicability` run in the background
  as the constitution and `research/CLAUDE.md` require; the stall watchdog is armed.

## Performance bookends

N/A - no diagram-generator code changes (comment-only edits; `ci/delta.py` compares the docstring-stripped AST).
`make done`'s `perf-gate` will report band 0.

## Constitution Check

- **I, II**: N/A - no UI in this repository (the research pages are the record, not a UI; their one browser
  test is the synthetic-page behavior suite, unchanged).
- **III, VII, VIII**: N/A - no pool content generated.
- **IV, V**: PASS - no SOURCE blocks exist in any rule file (checked); nothing inside SOURCE markers is touched.
- **VI**: PASS - verification per task: `make page-check` after every batch of page edits; `make test-file` on
  each test touched; `make done` once at the end; each page's `quote-check` + `record-format` verdicts recorded
  in `tasks.md`; new registry keys through `source-applicability`; the four new pages opened in a browser from
  disk once; delegated work spot-checked (each writer's report checked against its page: the anchors exist, the
  `class="spec"` count matches, no `FN-PENDING` survives at the end).
- **IX**: PASS - setting canon in the rule files (population, castes, clan patrons, the canal exception) moves
  labeled `setting-canon`; nothing new is invented.
- **X**: PASS - Python changes are tests only (`test_record.py` gains the retired-file rule and its
  self-test; `test_docs_match_the_mechanism.py`'s list; docstring edits). `ruff`, `pyrefly`, the 100% floor hold
  (a new test function is executed by the gate). No file approaches 1,000 lines. No overlap check is added.
- **XII**: PASS, both bookends. Opening: `research.md` holds the inventory - every decision item mapped to its
  anchor with its label; every physical claim that moves without a footnote listed with the source the rule file
  named and its `source-reader` verdict; every new key's applicability verdict. Closing: the pages themselves are
  the artifact; `quote-check` and `record-format` re-examine every changed entry. No rendered map changes, so no
  PNG re-examination is owed.
- **XIII**: PASS - baseline is the current green gate on main (`make done` green 6 h before this feature began,
  per the run log) and a `make page-check` run on the unmodified clone before the first page edit; zero new
  failures at merge. No roll, no cohort.
- **XIV**: the audit's incidental defects are fixed in this work - the broken md->html anchors (moot once the
  md is deleted), the stale engine docstring figures the audit found (`urban_fixtures.py:74` "county tier
  ~60-80 ft"), `inashiro.notes.md`'s dead `research/homesteads.md` link, the eight `pack_audit.py` paths.
- **XVI**: spec reviewed by `spec-fidelity` against `request.md` (round 1: six changes; round 2 pending at the
  time of this plan; the plan is not the review's input).
- **XVII**: `research/README.md` is not edited; the correction is offered to the GM.

## Phases

### Phase 0 - the inventory (`research.md`)

R1 the contradiction list (FR-001), each with the truth it resolves to and where. R2 the decision map (every
audit D item -> anchor), filled by the writers' reports. R3 the specification map (every unencoded rule -> anchor,
or dropped with reason). R4 the physical-claims table (claim, source named, `source-reader` verdict, footnote or
absence note). R5 new registry keys and their applicability verdicts. R6 the engine pointers re-pointed. R7 the
dropped stale content, by rule file, with reasons.

### Phase 1 - FR-001 on the pages that already exist

The session edits: `research/water.html` (head-race 6.0 ft, the sentence at the width ladder);
`research/urban-features.html` (the drum tower's decision figures 36 ft / 30 ft); `research/cities/river-cities.html`
(receives the junction hydrology in Phase 2; noted here). The other FR-001 items are applied by the writers as
they move content (the rulebook says so) and the writers report them. `make page-check` after.

### Phase 2 - the writers, one per target page (background, parallel)

| Target page | From | Notes |
|---|---|---|
| `homesteads.html` | `homesteads.md` | 12 D items; 5-6 "why" items; the name-informed siting question |
| `fields.html` | `fields.md` | 12 D items; the two rejected fillers |
| `archetypes.html` | `archetypes.md` | 8 D items; FR-001's Shunde and density labels |
| `vegetation.html` | `vegetation.md` | 9 D items incl. the four prose sections; the belt's three roles heading (for `greenery.py`); bamboo 14 ft |
| `water.html` | `water.md` + the swept-bend entry from `presentation.md` | 15 D items; drainage-bearing doctrine |
| NEW `ways.html` | `ways.md` | 5 D items; three physical findings; canal canon |
| NEW `presentation.html` | `presentation.md` | 11 D items; the page says it is conventions; the thirteen town/city label and crop rules as specs |
| `religion-and-death.html` | `religion-and-death.md` | 11 D items (district catchment first); ~30 numbers as specs |
| `towns.html` | `towns.md` | 8 D items; the town's census, zoning, wall, streets, institutions as specs |
| `urban-features.html` | `urban-features.md` | 15 D items; wells, tannery, justice, trades scoping, stable yards, seam as specs |
| `cities/defenses.html` + `cities/government.html` | the two md files | 3 + 3 D items; the page's labels win |
| `cities/fabric.html` | `fabric.md` | 5 D items; the largest spec load; the fire-tower narrative is physical-pending |
| `cities/hinterland.html` + `cities/river-cities.html` | the two md + `cities.md`'s farmland rulings | junction hydrology lands on river-cities |
| NEW `cities/sizing.html` + `cities/capitals.html` | `sizing.md`, `capitals.md`, `cities.md`'s population rule | the density model's constants as specs; the castle doctrine; FR-001's extramural fix |
| NEW `settlements.html` | `settlements.md` + `cities.md`'s tier definition and three intake questions | the tiers, page statements, waivers, the ordinary-first lesson; the houses-per-household fix |

Each writer returns the report the rulebook specifies. The session spot-checks each page (anchors present,
`class="spec"` count, no bare key, no visible forbidden shape) and runs `make page-check`.

### Phase 3 - the research pass on physical claims (background, parallel with Phase 2 where the source is named)

`source-reader` agents, one per host group, given each claim verbatim with its pointer from the rule file:
Knapp on Chinese settlement form; Leopold & Wolman on meander radius; the bridge landing (scour, bearing);
the lane-vehicle sources from the 2026-08-27 pass (registry keys may exist); the district-catchment sources
(Buck; danka; ryobosei); the swept-ground sources; the funerary size memo's five named works; temple-account
economics; the 土地庙 siting; the fire-tower narrative (hinomi-yagura, Meireki, wanghuolou, jin'ya); the junction
hydrology (bedload); the guan-xiang 10-40; the sizing model's Chang-in-Skinner civic share. READ -> footnote
under feature 194's form on the citations page (new keys get their two write-ups in `SOURCES.html` and a
`source-applicability` verdict before their numbers stand); otherwise an ABSENCE note dated 2026-09-12 and the
label follows. Every `FN-PENDING` comment is resolved; `make citations` and `make glossary` run.

### Phase 4 - the tree

Re-point every file the SC-001 grep finds (FR-007), by kind: docs (`SKILL.md`, root and skill `CLAUDE.md`,
`migration-plan.md`, `dev/*.md`, `future-work/*.md`, `hamletgen.md`, `buildings.md`, `programs.md`, the three
audit md files at the skill root, pool and legacy notes, `wip/`), the `settlement-review` agent, engine comments
and docstrings (about sixty files by the grep - comment-only), the `Entry:` tag in `greenery.py`, tests
(docstrings and the two lists). Then delete the thirteen rule files and `settlements/`. Extend
`test_record.py` with the retired-file rule (a `_RETIRED` set; the same resolver; the same exemptions plus
`research/README.md`), with a self-test that the rule fires. `research/CLAUDE.md` gains a short section on the
specification paragraphs and D1/D2. `make page-check`; `make quick`.

### Phase 5 - verification and landing

`quote-check` + `record-format` on every changed and new page (dispatched together, background, one pair per
page; verdicts recorded in `tasks.md`; findings resolved); the four new pages opened in a browser from disk;
`make done` (detached, never polled); commit; `sync-with-main.sh done`. The closing report to the GM carries the
README correction text, the Mode A rulings question (FR-009), and any physical claim left labeled guess.

## Project Structure

```
specs/229-rule-files-into-research/   request.md spec.md plan.md tasks.md research.md migration-rules.md audit/
.claude/skills/diagram/research/      15 pages edited; ways.html presentation.html settlements.html cities/sizing.html added
.claude/skills/diagram/research/citations/   the matching citations pages and derived .js
.claude/skills/diagram/research/SOURCES.html new keys with write-ups (Phase 3)
.claude/skills/diagram/research/CLAUDE.md   the spec-paragraph convention
.claude/skills/diagram/settlements.md, settlements/, settlements/cities/   DELETED
.claude/skills/diagram/l7r/diagram/**       comment edits; interactive/classes/greenery.py docstring tag; interactive/assets/glossary.json
.claude/skills/diagram/tests/interactive/test_record.py   the retired-file rule
.claude/skills/diagram/tests/tooling/test_docs_match_the_mechanism.py   the list
.claude/agents/settlement-review.md       the reading list
CLAUDE.md, SKILL.md, migration-plan.md, dev/*.md, future-work/*.md, pool/**/*.notes.md, legacy-hand-authored-pool/**   pointers
```

## Complexity Tracking

None deferred. The one cost worth naming: fourteen writers plus the read/check agents is a large fan-out; it is
the shape the GM asked for ("one spec kit feature and one sweep") and the same shape feature 202's sweep took.
