# `tools/` - diagnostics, audits and by-hand utilities

Things you RUN when a map comes out wrong or a number needs measuring, and the builders and audits the gate and the
record call. **Nothing in this directory is imported by a generator or by the engine** - that is the membership rule
for the folder, and it is what makes these modules safe to change without thinking about map output. (No engine is
Python any more: the Rust generation cache keys a map on its engine's binary and the files it reports reading,
[`dev/cache.md`](../../../dev/cache.md).)

Run them through their `make` targets at the repository root (named in the table; `docs/make-targets.html` lists each
target's arguments). A tool with no target of its own is run by a test or by another target, never by a bare
interpreter (`rust/guard/src/guards/make_only_hooks.rs` refuses one).

## Which tool answers which question

| You are asking | Reach for |
|---|---|
| Is there too much empty space in this Mode A compound? Does its SVG break a geometric rule? | `make pack-audit` - Rust since feature 449 T175, `rust/mode_a/src/audit/` (its index is `audit.rs`'s module doc: which module holds which check, and where a new one is registered); the Python package deleted by T212 |
| What does each declared Mode A type require, as a table? | `make building-programs` (writes `docs/building-programs.md` between markers) - Rust since feature 449 T168, `rust/mode_a/src/programs.rs` |
| I fixed one hamlet - does the fix generalize across a cohort, and what exactly collides? | `cohort_audit` - `make cohort N=... [SEED=...]` |
| Will the gated push take this engine - 48 seeds on it, none regressed, and the fresh block's rate? | owed only at the port switch's `integrated` (feature 444 FR-023): `make cohort-landing` refuses while nothing writes its record (feature 449 T223); the gate is `l7r-gate cohort check`, `scripts/gates/cohort-gate.sh`, the trend `make cohort-seeds` |
| Check every pool sheet against its tier's checks | the pool sweep, `make rust-test CRATE=rust/mode_a` (`rust/mode_a/src/pool_sweep.rs`; `make maps` and `mapcheck` went with the Python engine) |
| What does the map look like after each placement stage, and why is that stage there? | `placement_stages` - `make placement-stages` |
| I lit one class on the page - which OTHER classes' pixels changed, and by how much of each? | `make page-lit` (`VECTOR=1` zooms past the raster switch, feature 245) - Rust since feature 449 T150, `rust/mode_a/src/diagnostics/page_lit.rs`, its browser half `rust/browser/src/lit.rs` |
| Two renders of this map: how much differs, by how much, where, and on whose ink? | `make picture-diff` - Rust since feature 449 T150, `rust/mode_a/src/diagnostics/picture_diff.rs` (every format the `image` crate reads, held to PIL's reading; see `diagnostics/image.rs`) |
| Which classes does a page draw see-through, and is a broadleaf crown painted over a conifer? | `see_through` (feature 294 B5; the declared table is `settlement/see_through.py`) |
| Does a marsh meet the open ground on a ruled or plumb line, where a reader sees it? | `marsh_edges` (feature 294 B2; the visible free edge from the page's id map) |
| What does a hand-drawn Mode A sheet look like with its captions placed? | `make sheet-render SHEET=<svg> OUT=<png>` - the placer is `labels/hand_sheet.py` |
| A map's canonical counts, in the block its `.notes.md` carries | `make notes-census` - Rust since feature 449 T170, `rust/mode_a/src/census.rs` (the sheets' typed counts, B15b, held by its `census/pool_check.rs`) |
| The engine's and the Mode A procedures' research CLAIMS, read from the source | `l7r-gate claims` (`rust/gate/crates/claims/src/claims.rs`, feature 449 T82) behind `make claims-owed`, `claims-bundle`, `claims-checked`, `claims-report` (feature 316); `claims` here is its `.py` half, CPython's syntax tree, asked through `scripts/bundle_door.py` |
| The record's footnotes counted by kind - what is owed | `make footnote-census` (`l7r-gate record footnote-census`, Rust since feature 449 T148) |
| Assemble or check the glossary from its per-term files | `make glossary` (`l7r-gate record glossary`, Rust since feature 449 T148) |
| Build or check the record's site from its per-entry fragments | `make record` (`l7r-gate record site`, Rust since feature 449 T148) |
| The source vocabulary derived into the `source-applicability` contract | `make source-tags-contract` (feature 305; `l7r-gate record source-tags-contract`, Rust since feature 449 T148) |
| How much work does each stage do, against its budget? | `make work-budget` (a hamlet stage, the Rust driver's counters), `make budget-sheets` (a Mode A stage); the Python snapshot, bands, profile and review records (`make perf`, `perf-report`, `perf-profile`, `perf-review` and the rest) went with the Python engine, their names with feature 449 T223 |
| How long does this loop take, and where does the time go? | `make audit`, `l7r-gate measure gatecost <target>` (`scripts/gates/l7r-gate.sh measure gatecost`); the frozen ledger is `dev/timings.md` |

Each module's own docstring carries the WHY it exists, usually with the incident that produced it. Read that before
extending one. The operational guidance for `why_placed` and `open_seat` is [`dev/diagnostics.md`](../../../dev/diagnostics.md).

## The rule these share: a diagnostic OBSERVES, it never restates

`why_placed` reads its refusal causes off the real `_in_blocked` / `_near_corridor` / `_hard_clear` as they return; it
re-implements no rule, and that is not style. A predecessor that re-derived every rule as its own predicate drifted
**within a single session** - a relaxation made to satisfy one map persisted and put Nagahara's boundary stone in a
field off the highway. A tool that re-derives a rule will eventually disagree with the placer and then tell you the
wrong thing with total confidence. To ask where a feature may go, use `open_seat` and `why_placed`, which read the
placer's own refusals rather than a second opinion about them.

The Mode A audit (`make pack-audit`, Rust) and `scatter_audit` are the exception that proves the rule: Mode A has no manifest and scatter is
draw-time ink, so both parse the rendered SVG. They are the source of truth for their own questions rather than a
restatement of someone else's.

## A tool whose input is a PATH will be broken by a refactor - point it at a directory

`cache_audit` mutates a numeric literal and demands a cached sweep and a fresh sweep agree. Its mutation target was once
a single hand-picked FILE, invalidated twice by package splits - each time the tool crashed on its next mandatory run.
The target is now the set of trees that DRAW a map (`settlement`, `waterfields`, `sitegen`, `hamletgen`), and the site
is chosen from what the audited maps actually EXECUTE, measured by a coverage pass over the gens. To carry to any tool
of the same shape:

- **A directory target cannot be invalidated by a split inside it.**
- **Choose from what runs.** Literals in code the maps never run change no byte, so a trial on one proves nothing while
  printing the same `[OK ]` as a real one.
- **State the membership rule at BOTH ends.** Coverage's own config is not the rule: `--include` is ignored when
  `[tool.coverage.run] source` is set, and a `source` list can omit a tree that draws every paddy.

## Coverage

**Everything here owes 100%, the day it lands** (GM 2026-09-02, constitution Principle X clause 5: *"A new tool
absolutely should silently owe one hundred percent coverage the day it lands ... For tools, for our settlement
generation, for the automated checks on our hand drawn diagrams, for everything."*). The measured surface is DERIVED -
every line of a Rust crate, by its own tests (`make rust-test`; the Python's `pyproject.toml` floor went with the last Python, feature 449 T158) - so the way to not owe coverage on something is to not ship it. A boundary that
genuinely cannot be reached is argued at the point of change, like any other exclusion.

For a tool whose work is a SUBPROCESS or a BROWSER: the pure half is tested directly and the driving half where it can
be driven. The two picture measures are Rust since feature 449 T150 and are tested there: their arithmetic on synthetic
images, the browser half on the browser crate's fake Chromium and its one end-to-end test on the real one.
