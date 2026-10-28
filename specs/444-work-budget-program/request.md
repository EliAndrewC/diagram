# Request - the work-budget conversion (features 443 and 444)

<!-- SOURCE: GM NOTES -->
## The GM's words, verbatim (dictated), 2026-10-27 and 2026-10-28

2026-10-27: "it sounds like we can probably close out. A few of the features that we were working on. Our open feature for resolving all claims that are still open is still valid, because those claims will still exist even if they exist in the Rust code base instead of the Python code base. But yeah, let's go ahead and see if we can design a checklist-based approach for doing this conversion. And then maybe we'll go ahead and start it off, after I have a chance to take a look at what the specifics are, and you tell me how we are going to go step by step, and crucially ensuring that the act of conversion is, as I said, checklist based and has rigorous standards for ensuring that we are not just faster, but that we are performing an algorithmically sensible number of computations as validated by some kind of adversarial subagent check based on some real standards, such as the ones that you just said about what should be feasible for a homestead versus what we are actually doing. Once I am confident that we will not just end up repeating the mistakes of the past, then I will give you the go-ahead ... not just how we should get there, but how we are going to enforce through our processes that we really do get there and don't just lose sight"

2026-10-28, on compiling the counters out: "is that possible to do in Rust as well, such that whatever overhead we are adding by adding all of these measurements, there is a compiler flag we can set to not take the measurements, so that when we, for instance, compile the version of this that we deploy, that it lacks that overhead?"

2026-10-28, on the safeguards: "I feel like it is very important to get these safeguards in place and to identify in advance as part of this plan exactly which of those existing checks will port over one for one, which of them will be dropped, and which of them have some partial version that we would move to ... we do have a number of makefile targets and tooling that integrates with Python and coding conventions which we enforce mechanically, which I want to make sure are not forgotten or lost. So that should probably become part of this plan."

2026-10-28, the approval: "Thank you. I approve the design. Please proceed."
<!-- END SOURCE -->

## The design he approved (the session's, as he read it on 2026-10-28)

Nothing here is filed or built. It becomes a feature only on the GM's go-ahead.

## Why the past attempts lost sight

Features 226, 227, 297, 304, 306, 314, 417 T55, 427, 437, 439 and 441 each asked one question:
"does this change save time?" Each measured a slice (2-4% of the roll), found the gain small and set
it down. No record ever said what the whole roll *should* cost, so nothing showed that the roll does
100-200x too much work. Today it makes about 26.4M Python calls for 40 households, about 660k calls
per house. A sensible design needs a few thousand basic operations per house.

So the fix is a standing target, not a better slice-picker. Every phase gets a budget derived from
first principles, before anyone looks at the current code. Every landing then reports budget against
actual for the whole roll. A phase is finished when it meets its budget. "The gain was small" is
never a reason to finish one.

## 1. The measure: counted work that survives a port to Rust

Python call counts disappear when code moves to Rust. They also miss work done in C: shapely,
numpy and builtins. The program therefore counts **basic operations**:

- a point or segment test;
- a distance;
- a spatial-index query, with the number of entries it examined;
- a candidate site evaluated;
- a thing placed, and a thing dropped or moved after placing.

The counters live in the shared geometry layer (`settlement/_geom/primitives.py`, `indexes.py`) and
at each phase's candidate loop. They count once per element, even when a vectorized call handles
many elements. A Rust port must keep the same counters, so its numbers stay comparable.

`make work-budget` rolls the reference hamlet (seed 25 and the cohort's pinned seeds) at 10, 20, 40
and 80 households. For each stage it prints:

- the basic operations, total and per thing placed;
- the growth exponent;
- the stage's budget;
- the ratio of measured to budget.

The bottom line gives the whole roll against the program's budget.

**The counters cost nothing in the deployed build.** In Rust each counter is a macro behind a Cargo
feature (`#[cfg(feature = "counters")]`). Development and the gate build with the feature on. The
deployed build leaves it off, and the compiler then removes the counters entirely. While the code is
still Python, the counters sit in `if __debug__:` blocks, which `python -O` drops when it compiles
the code. The gate rolls a seed both ways and requires identical manifests, so a counter can never
change a map. Python calls and times are still
recorded beside these figures, but neither is the target.

## 2. The standards a budget is held to

These standards go in a rubric file the adversarial agent reads. They are the "real standards".

- **S1 Indexed neighbors.** A check on a candidate examines a bounded number of neighbors, through
  an index. The bound is stated and does not grow with the number of households.
- **S2 Derived candidates.** The candidates tried per thing placed are a constant derived from the
  geometry, such as the sites within reach at the rule's spacing. They are never a tuned retry count.
- **S3 No all-pairs.** No pass over a growing set runs inside another loop over a growing set, unless
  the inner set has a stated constant bound.
- **S4 Ask before placing.** This is feature 417's principle. Every rule is asked of a candidate
  before the thing is placed. Nothing is placed and then moved, dropped or repaired. The counters
  report drops and moves, and the budget for them is zero.
- **S5 Count the work where it happens.** Work in C or numpy is counted per element. An uncounted
  inner loop is a finding.
- **S6 Linear growth.** A stage's exponent from 20 to 80 households is at most 1.15, which allows
  n log n. A stage over that limit needs a stated reason, such as a bounded n.
- **S7 Show the arithmetic.** A budget is items × candidates × checks × slack (slack at most 2).
  Each factor names its reason (S1-S3).

The reference point is the homesteads. About 20 candidate seats per house, about 10 indexed
neighbors each and about 10 parts gives about 2,000-4,000 basic operations per house. Today the
stage makes about 180k Python calls per house. Trial 439 found 803 envelopes built for 40 houses,
95% of them thrown away.

## 3. The per-phase checklist

The checklist is a template, `.specify/templates/phase-checklist.md`. Each phase is one task, and
its boxes are ticked in order. `make land` refuses a phase task whose boxes are not all ticked.

1. **Contract.** What the phase reads from the manifest and what it writes. The research claims that
   govern it (from the claims index). The cohort properties it must keep.
2. **Minimal algorithm.** Pseudocode for the algorithm and its operation count, factor by factor
   (S7). It is written from the contract alone, before the current code's numbers are read.
3. **Budget review, MODE BUDGET.** The `work-budget` agent reviews the derivation (section 4). The
   budget and exponent are then pinned in the standing record.
4. **Today's measurement.** `make work-budget` for the stage, giving the ratio to budget and the
   exponent. The hot chains come from `make perf-fanout`.
5. **Rebuild.** The phase is rebuilt behind the manifest seam (`STAGES` in `driver.py`). It reads the
   same input and writes the same output. It has no repair passes (S4). The old implementation is
   deleted in the same landing, with no fallback path.
6. **Acceptance.** All of these are needed:
   - basic operations at most the budget at 40 and 80 households, and exponent at most the budget's;
   - `make cohort-landing` shows no regressed seed, and the fresh block's pass rate is no worse
     (not all seeds pass: that is 417's goal, not this program's);
   - the phase's claims round is IN-STEP;
   - the reviews its occasions owe (`docs/reviews.md`), such as `settlement-review` when a map's form
     changes;
   - `make perf-ab` time recorded, as a record and not a gate.
7. **Audit review, MODE AUDIT.** The `work-budget` agent reviews the landed code against its counters
   (section 4).
8. **Standing record updated.** `dev/work-budget.md`, for this phase and for the whole roll.

## 4. The adversarial check: a new agent, `work-budget` (Opus)

The agent has two modes. Each mode gets its own bundle from `make work-budget-bundle`.

**MODE BUDGET** checks the derivation before the rebuild. The bundle holds the contract, the
pseudocode, the operation count and the rubric. It does **not** hold the current code or its
numbers, so today's waste cannot anchor the target.

The agent asks three questions. Is each factor derived (S1-S3, S7)? Is there a standard, cheaper
algorithm, such as a sweep, a grid, a priority queue or incremental update? Is any factor padded?

The verdict is one of:

- **SOUND**;
- **LOOSE**, naming the factor and a tighter bound;
- **UNDERIVED**, naming the factor with no reason.

**MODE AUDIT** checks the landed code. The bundle holds the rebuilt code, the counters by function
at each size and the pinned budget.

The agent asks four questions. Are the counters within budget? Does a counter cover every inner
loop (S5), with nothing uncounted in C? Is anything placed and then repaired (S4)? Is the growth
linear (S6)?

The verdict is one of:

- **WITHIN**;
- **OVER**, naming the chain;
- **UNCOUNTED**, naming the loop.

**Proving that it bites.** Before the agent's first real use, two fixtures:

- today's homestead seat funnel (803 envelopes, all-pairs `free_end`/`box_gap` in the web) must be
  ruled OVER or LOOSE;
- a textbook grid-index placer must be ruled SOUND or WITHIN.

Its tests hold both rulings, as with every check the project adds.

## 5. Enforcement - how we keep sight of the goal

1. **One program feature, with the phases as its tasks.** It closes only when the whole roll meets
   the program budget, or when the GM changes the budget. The trial form's "set down when the gain is
   small" does not apply. A phase is judged against its budget, never against the time it saves.
2. **The standing record**, `dev/work-budget.md`, generated by `make work-budget`. It shows every
   phase's budget, measured value and status, and the whole-roll total. It is printed at every
   engine landing and listed by `make speckit-todo`. This keeps the distance from the goal in view in
   every session.
3. **A ratchet on converted phases.** Once a phase is accepted, any landing that raises its basic
   operations past its accepted figure, or past its budget, is refused. This extends today's
   call-count guard (feature 427 T03). Unconverted phases keep that guard.
4. **Budgets change only with the GM's words.** The budget table is a guard file. Raising a budget
   needs `make budget-change PHASE= TO= WORDS="<the GM's words>"`, logged like an `**Approved**:`
   line. The round arbiter may rule on process, but it may not accept a phase over budget.
5. **A phase is done when the old code is gone.** No fallback path, no flag. The landing's size delta
   shows the deletion.
6. **The agent re-reads the whole table at each phase landing.** It checks that no unconverted phase
   grew and that the sum still converges. This is cheap: one bundle, one agent.
7. **The language checkpoint after phase 2.** This is a written decision. It compares the basic
   operations per second of the rebuilt Python phases against a Rust spike of the same phase,
   measured on the same counters. Rust adopted, or not, from there.

## 6. Step by step

0. **Close-outs**: 427 and 435 close, as set out at the end.
1. **The instrument.** A tooling feature: the counters, `make work-budget` and today's figures for
   every stage at 10/20/40/80 households. Engine counters only; no map changes.
2. **The agent and its rubric**, proven on the two fixtures.
3. **The whole-program budget.** Derive every stage's budget on paper (about 25 stages), MODE BUDGET
   on each, and their sum, which is the program's target. The GM approves the target. This is the
   step that stops the program from losing sight.
4. **Phase 1, `water_frame`, and phase 2, `field`**, through the checklist.
5. **The language decision**, measured.
6. **The remaining phases, in pipeline order.** Each one reads what the earlier phases wrote, so the
   order keeps each rebuild's input fixed.

## 7. The safeguards when phases move to Rust

**The shape assumed.** Rust holds only the rebuilt phases. They are compiled into one extension
module that Python imports (PyO3, built by maturin). Everything else stays Python:

- the driver and `STAGES`;
- the manifest;
- rendering and the interactive page;
- the pool's `.gen.py` scripts, the tools and the pytest suite.

Each stage stays a thin Python function with its docstring and calls into Rust. That is why most of
the tooling below keeps working unchanged, and why the move can go one phase at a time.

**Rust's habits on file size.** Each Rust file is a module, and splitting a large module into a
directory of smaller files is ordinary practice. A `mod.rs` that re-exports with `pub use` is the
exact analogue of our `__init__.py` re-exports. Both caps carry over:

- **1,000 lines per file**, with the same split rule: submodules of about 650 lines.
- **About 100 lines per function**, through clippy's `too_many_lines` lint. It counts lines where
  ruff counts statements, so the rule is the same but the count differs.

One Rust habit would undo the file cap: unit tests sit at the bottom of the file they test
(`#[cfg(test)] mod tests`). Our rule puts them in their own file, so the cap still measures code.

**Every check, sorted.**

| today (Python) | in the Rust phases | |
|---|---|---|
| ruff lint | clippy, all and pedantic, warnings refused | one for one |
| ruff format | rustfmt | one for one |
| pyrefly (types) | the Rust compiler, which is stricter | dropped, replaced by the compiler |
| function cap (PLR0915, 100 statements) | clippy `too_many_lines` (100 lines) | one for one, counts lines |
| a suppression must say why | `#[expect(lint, reason = "...")]` and clippy's `allow_attributes_without_reason` | one for one |
| file cap (`check-file-scale.py`) | the same script, reading `.rs` | one for one |
| duplicate top-level definitions | the compiler refuses them | dropped, replaced by the compiler |
| 100% line coverage, the floors | `cargo llvm-cov --fail-under-lines 100`, plus the Rust lines pytest reaches through the extension | one for one; an argued exclusion is only partial (`#[coverage(off)]` needs a nightly compiler) |
| `make cover-changed` | llvm-cov per changed `.rs` file | one for one |
| `make roll-audit` (lines only one rolling test reaches) | per-test coverage profiles | partial: possible but slow |
| `quick`'s change-selected tests (testmon) | cargo rebuilds and re-tests only the changed crate; pytest's selection still covers the Python callers | partial |
| `Research:` claims in docstrings, claims gate, bundles, `make tunables` | the same section in `///` doc comments; a new reader (via the `syn` parser) writes the same index | rewritten reader; the process is unchanged |
| placement-stages page (`STAGES` and `Steps:` docstrings) | unchanged for the stages; Rust steps are read through the same doc-comment reader | partial: the steps' reader is new |
| the docstring-blind code id (`codeid`, `gate-stamp`, the cache's engine hash) | a hash of the Rust token stream without comments, and the built extension added to `gencache.engine_files()` | rewritten |
| `cache-audit` (mutate a literal, compare sweeps) | the same audit, mutating `.rs` and rebuilding | one for one, slower |
| `dead-closure` | the compiler's dead-code lint, refused, for private items; the script for the rest | partial |
| perf-profile, perf-fanout, perf-share (cProfile) | the work-budget counters, plus a sampling profiler (`samply`) for time | replaced: Python call chains mean nothing inside Rust |
| perf-ab, cohorts, the gate's map tests, pool-readers, `make map` | unchanged: they roll maps and read manifests | one for one |
| house style (hyphens, American spelling, identifiers) | the hook extended to `.rs` | one for one |
| make-only guard and `_invocation.py` | the hook also refuses a bare `cargo`; the extension refuses use outside make as the engine does now | one for one |
| `docs/make-targets.html`, spec-kit, reviews, research, ledger, arbiter | unchanged | unchanged |

**Nothing forgotten, mechanically.** The step-1 tooling feature adds `dev/rust-tooling.md`, which
holds the table above with one row per check. A `make hooks-test` check lists every hook, gate
script and make target that reads `.py` files or Python's syntax tree. It fails on any one with no
row. A new Python-only check therefore cannot be added without saying what happens to it under
Rust. The first Rust phase cannot land until every "one for one", "partial" and "rewritten" row
has been proven to fire on a Rust fixture, the same "prove it fires" rule every guard meets today.
Steps 1 and 5 grow to match: the inventory comes in step 1, and the language decision in step 5
includes building these ports.

## The one decision for the GM

**Approve the design (sections 1-7)**, or name what to change before step 1 starts. Approving it
also does three pieces of bookkeeping, which the session will carry out:

- **427** (call-volume refactors): T10, the web's pairwise chains, is withdrawn, because the web
  phase's rebuild replaces it. T11, the closing bookend and report, runs, and 427 closes.
- **435** (speed aims at time): its three drawing-page notes (T05, T07, T09) move to 405, the claims
  feature, and 435 closes.
- **417** (all seeds pass) **stays open**. It is still the feature that exists to get every seed
  passing, and 405's hold on it stands. The program does **not** require all seeds to pass. Its
  gate is that the fresh block's pass rate is no worse, as you set for speed work on 2026-10-26.
  When a phase's rebuild does one of 417's "ask before placing" tasks for that phase, the task is
  ticked with the landing as evidence. Its other tasks stay where they are.

## The GM's words, 2026-10-28 (on a repeated error: careful made a checked step)

> So does that mean that our process for step 3 needs to change? Because anytime I hear you say that something went wrong and that you will address this by being careful in the future, then I tend to think that that will not work, unless being careful specifically means that our checklist-based process has been updated to include whatever "careful" means in that context. Now you say that there is a working "rule" for step three, but is that an actual enforced rule, either enforced in our tooling or enforced in our subagent checks or enforced in our procedures in some way? Or do you just mean colloquially that you set a rule for yourself? because the latter is likely to be ineffective.

> That's fine, as long as it happens before the place where it would actually matter, then I don't care which feature it belongs to.
