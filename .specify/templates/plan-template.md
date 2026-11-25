# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]

**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]

**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]

**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]

**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]

**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]

**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

**Single-artifact target** (REQUIRED for any generator change, constitution VI): [the ONE named
artifact this is proven on before any sweep - e.g. `pool/hamlets/inashiro.gen.py`. State its
rebuild time. Iterate on it alone (`make map MAP=<map>`) and widen to the pool only once it is clean (`make cohort` for a hamlet cohort,
`make rust-test CRATE=rust/mode_a` for the pool sheets). If the feature adds a knob, name one artifact per knob
VALUE.]

**Every step is two steps.** Each phase below must separate "working on the reference settlement"
from "working across the pool". The second is its own task with its own verification - if a phase
lists only the first, it is not finished being planned.

## Performance bookends (REQUIRED for any diagram-generator change, constitution VI)

A change made for speed may move maps - ALWAYS (the GM, 2026-10-18: *"anytime we are trying to make things faster, it's
always okay for maps to change, so long as the changes don't violate our research findings"*). Hold it to the rules and the
research claims (the cohort, the gate, impl-drift) rather than to identical output; an equivalence test is needed only where an
answer is kept on purpose. So may any port or change (constitution XIII, the GM 2026-11-18): its outputs may differ so long as
everything works - its tests pass, it does its job for its callers, its research claims hold; a drawn output must pass its checks,
and a ported check must still do its job (its red fixtures still fail, the sheets it passed still pass), never matching bytes.

| | counted work | notes |
|---|---|---|
| before | `make work-budget` (a Mode A stage: `make budget-sheets`) | taken on UNMODIFIED code, before the first edit |
| after | the same command | taken before the push |

A stage's counted operations rising past its budget is diagnosed here, in writing, with the number - fixed, or accepted with a
reason (the work budget's rules, feature 443). A timing is recorded as evidence, never a gate (feature 427 T03).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Each gate must be marked PASS, N/A (with one-line justification), or DEFERRED
(with a Complexity Tracking entry). DEFERRED gates require explicit GM
approval before /speckit-tasks may run.

- **I. Accessibility-First Viewports**: NOT APPLICABLE in this repository
  (constitution 2.0.0) - it governs gm-assistant's webapp. Write "N/A - no
  UI in this repository". If a feature ever does add a browser page here,
  that is the signal to reinstate the gm-assistant entry, not to skip it.

- **II. Bold, Intentional Design**: NOT APPLICABLE in this repository, same
  reason. Map style is governed by the skill's design doctrine
  (`SKILL.md`, `settlements/`, `buildings/`) and reviewed under VI.

- **III. Pool Data Conventions**: If the feature adds or modifies generated
  content of a recurring kind, the plan MUST specify the markdown-with-YAML
  file format, the per-category directory layout under
  `/.claude/skills/<skill>/pool/`, the frontmatter schema (including
  category slug and `clan` tag), and MUST forbid baking specific cities
  (`Kyuden X`, `Shiro X`, `Shinden X`) into frontmatter or prose.

- **IV. One Canonical Home for GM Source**: If the feature adds or moves
  SOURCE blocks, the plan MUST identify the single canonical home for each
  block and list any references-by-path that other files will use.

- **V. Protecting the GM's Writing (NON-NEGOTIABLE)**: The plan MUST NOT
  include any task that modifies content inside SOURCE markers - there is no
  sync exception in this repository; SOURCE blocks are frozen excerpts.

- **VI. Verify Before Reporting Done**: The plan MUST list the verification
  steps each task will run before being marked complete - `make done` for
  code, the review checks a map's delta owes (`make verify` names them - feature 294's occasions),
  spot-check of delegated work. Every generator step is TWO steps (reference
  settlement, `make map MAP=<map>`, then pool - `make cohort`), both as tasks.

- **VII. De-Localized Generation by Default**: If the feature generates pool
  content, the plan MUST default to generic / reusable framing (clan-level
  designators, family-level named entities) and MUST NOT lock content to
  specific cities or campaign-tied figures without explicit GM scoping.

- **VIII. Direct Voice Over Framing Distance**: If the feature writes in-world
  content, the plan MUST commit to direct-voice phrasing and MUST exclude
  meta-narrational framings ("the temple holds that…," "tradition says
  that…," "skeptics report…").

- **IX. Setting Integration**: The plan MUST cross-reference the relevant
  reference directories (`/setting/`, `/cosmology/`, `/campaigns/`) and
  MUST NOT invent setting details that contradict GM source notes. New
  named figures MUST NOT collide with the campaign-names cache.

- **X. Code Discipline (NON-NEGOTIABLE)**: If the feature ships code, the
  plan MUST commit to: the lint and the format check passing
  (`make static`'s `rust lint` and `rust format --check` since feature 449
  T158 deleted the Python with ruff; constitution v2.37.0), the strict type check passing on production modules (the Rust compiler; constitution v2.38.0), red-green TDD
  for new non-trivial behavior (test exists and fails before
  implementation lands), the coverage floor passing - **100% over the
  WHOLE engine, no opt-in** (`make static`'s `rust cover`, every crate; Principle
  X clause 5 as the GM globalized it on 2026-09-02: a new module owes 100%
  the day it lands, and the measured surface is derived rather than
  rostered) - but for the engine code the Rust port replaces, the files
  `dev/coverage-exempt.json` names, whose unrun lines are reported and not
  held (feature 448, the GM 2026-11-02: "We can relax that for the engine code at this pooint since that's going away, so long as we maintain it for our other Python code not currently slated to be removed (tools, automated checks for hand-drawn maps, etc)."), external boundaries
  tested via saved fixtures (not transport-layer mocks), pinned
  dependencies (`rust/Cargo.toml`'s workspace, `rust/Cargo.lock` tracked),
  no swallowed exceptions and no `print` in production paths (the Python's),
  behavior-named tests, one test over variant inputs, and configuration over
  hardcoding (no hardcoded magic). An overlap or proximity check the
  feature adds within a map - a candidate tested against features already
  on the map - is performed in its efficient form (clause 15, GM
  2026-09-08): the plan MUST say which index answers it (a grid, a ring
  index, an outline of the blocked ground, built once) and MUST NOT walk
  every item on the map per candidate. Functions stay at human scale
  (clause 12): no function past 100 lines, clippy's `too_many_lines` (the
  root `clippy.toml`, refused by `rust lint` at the gate and the push;
  ruff's `PLR0915` statement count until T158) - a plan whose
  implementation would grow one past it says how it is split, or why the
  body must remain one (`#[expect(clippy::too_many_lines, reason = "<why>")]`
  on the function), measured in lines. Files
  stay at human scale too (clause 13, test files included): a plan
  whose implementation
  would grow any source or test file past ~1,000 raw lines MUST say so and
  either plan the package-of-subfiles split (directory-module +
  CLAUDE.md index) or justify the file remaining whole. And when the
  oversized file is ROSTER-shaped - re-export lists, `__all__`
  duplicates, registry rows a machine could regenerate from the code
  they point at - the plan MUST apply clause 14 (derive, don't maintain
  or split): census the consumed surface, move the roster's safety
  property into a guard test proven to fire, then derive the surface;
  `specs/027-init-star-imports/` is the exemplar.

- **XII. Historical Grounding Bookends (NON-NEGOTIABLE)**: Does the feature
  change what a generator ASSERTS ABOUT THE WORLD (any `/diagram` settlement
  or compound change; any generator that draws or states how a place was
  farmed, built, or lived in)? If yes, the plan MUST commit to BOTH bookends:
  - **Opening (Phase 0, in `research.md`)**: for each element added or
    changed, state what the historical reality was (China-first, Japan
    corroborating) in checkable detail, state explicitly whether the proposed
    design matches it, and name WHAT DETERMINES the element in reality
    (topography / season / tenure / economy). A design that does not match is
    changed or dropped HERE, not implemented and revisited. Grounding that
    led to REJECTING a design MUST be recorded too.
- [ ] **XII, decisions for the reader (GM 2026-08-26)**: every rendering decision this plan
      makes is classified accurate / deviation / convention / guess / unresearched with its reason,
      lands in `research/` + the operative doc + a pointer at the point of change, and is listed in
      the spec's "Decisions Recorded" table. A guess is labeled a guess; one not yet searched is
      labeled UNRESEARCHED, on the backlog (`make research-backlog`, constitution v2.39.0).
  - **Closing (final phase, before "done")**: re-examine the RENDERED
    ARTIFACT (the PNG - not the code, not the intent) and confirm each element
    still matches the Phase 0 findings. This is separate from the automated
    gate: `check_village` proves internal consistency, never historical truth.
    A map can pass every check and still depict something that never existed
    (see the `rape` overlay failure in the constitution's Principle XII).

- **XIII. No Known Regressions (NON-NEGOTIABLE)**: Does the feature touch
  shared code with an existing test bed (a cohort, a pool sweep, a regression
  corpus)? If yes, the plan MUST commit to:
  - **A MEASURED baseline, taken before any judging** - on unmodified code, in
    a detached worktree (`git worktree add --detach`), never a stash. Name the
    command and the number in the plan.
  - **Zero NEW failures at merge.** Pre-existing failures do not BLOCK this
    feature's merge (though see Principle XIV - one you actually find is still
    yours to fix); anything that passed before and fails after is a regression
    and BLOCKS the merge. Smallness, "only a cohort seed", having documented it,
    net-positive arithmetic, and a "rotated" residue are explicitly not
    excuses. Exits: fix, revert, or an explicit GM waiver.
  - **A differing output is not a regression** (v2.35.0): name what the
    plan holds a port or change to - its tests, its callers' reads, its
    research claims, its checks passing (a ported check still doing its job) - never its bytes.
  - Where a re-roll destroys per-seed comparison, the pass RATE must not drop
    AND each newly-failing check must be individually diagnosed in the plan's
    closing notes.

- **XIV. Fix Defects Where You Find Them**: a defect (v2.36.0) is a wrong
  outcome - a map that reads wrong, a research finding contradicted, a check
  that passes bad work or refuses good work, a tool that crashes, hangs or
  answers wrongly - never a difference from what was expected, from the
  Python or from a convention's wording. Before any fix, name what a reader
  of the map would see differently; a claim the code does not literally
  match where the behavior is fine is fixed by restating the claim. A
  found-and-left item is filed only with its visible effect or the research
  finding it breaks.

- **XIX. Placed Right, Never Repaired**: Does the feature
  place, move or remove anything on a map? If yes, the plan MUST name, for
  each rule the placement keeps, the ONE predicate its placer asks of every
  candidate before placing - and MUST NOT add a pass that moves, cuts, thins
  or drops what was placed, a finished-map check inside the generator's run,
  or a second copy of a rule. Where no candidate is admitted, the plan gives
  more room; it never relaxes the rule or refuses the map.

Document each gate's status in a short bulleted Constitution Check section
in the plan output before proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
