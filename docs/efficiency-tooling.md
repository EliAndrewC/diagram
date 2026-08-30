# The efficiency tooling, in one picture

Everything this repository does, at the tool level, to stop a session paying five minutes for an
answer worth four seconds. Written 2026-08-30 at the GM's request, because the machinery was spread
across `CLAUDE.md`'s guard table, [`iteration-loop.md`](iteration-loop.md) and
[`dev/loop.md`](../.claude/skills/diagram/dev/loop.md) and had never been laid out as one thing.

**The project goal it serves** (GM 2026-08-25, constitution v2.3.0): *"iterations are expensive in
terms of wall clock time. And if me asking for a simple change results in half an hour of work being
done when it should have only taken five minutes, then that limits the number of changes that I can
make in a single day."* A transcript profile put **78% of wall time in model turn latency**, not tool
execution - so the number of sequential turns is the cost, not the speed of any one command.

## 0. The cost ladder everything else protects

| target | what it runs | measured 2026-08-30 |
|---|---|---|
| `make quick` | lint, types, and every test that does not roll a map | **4.1 s** warm / 25.3 s cold |
| `make reference` | one seed of the reference hamlet, and nothing else | **29 s**, or ~0 on a roll-cache hit |
| `make done` | lint/format/types, THEN reference, then hooks + the suite (feature 168: the static phases run first, so a break ruff cannot fix is reported before a map is rolled) | **median 156 s** over the last 20 green runs |
| `make done FULL=1` | + every pool map + the seeds 41-44 ratchet | minutes; prompts, and cancels by default |

Re-measure any time: `make audit` prints every recorded run with its elapsed seconds, and
`scripts/_gatecost.py done` prints the current median. **No guard message or Makefile prompt states a
duration from memory any more** (feature 162) - they ask the run log or say nothing, because a number
typed into a string in August is wrong in September and nothing tells anybody.

## 1. The expensive thing skips itself

The cheapest run is the one that does not happen. Four short-circuits, each keyed on CONTENT rather
than on time:

| mechanism | what it skips | what re-opens it |
|---|---|---|
| `ci verified-done` | the WHOLE gate, in ~0 s | any change to engine `.py` (compared as its docstring-stripped AST) or to pool gens/manifests. Docs, tests, the Makefile, config and `scripts/` never re-open it - **nor do comments, docstrings or formatting inside engine Python** |
| `gate-stamp --fresh hooks` | the `hooks-test` phase | a change to any guard script. The phase itself runs its suites in PARALLEL since feature 172 - measured on identical content, every suite forced stale: **194 s serial, 63 s parallel** |
| per-suite freshness | any of the 21 guard suites | **its DERIVED dependency set** (feature 172): its own guard and test, plus every shared helper reachable from them TRANSITIVELY, read from code rather than prose. A `_gatecost.py` change re-runs 5 suites where it used to re-run all 21, and a make/rewrite change 6 - measured on real incremental runs; three of those five are the whole-tree suites, which re-run for any script change and always will. The escape family still reaches 17, because every guard reaches its escape - and that is what the parallelism is for |
| `ci tooling-fresh` | `tests/tooling` inside `make quick` | a change to the tooling those tests drive |

Measured: **48 of 314 recorded `make done` runs short-circuited entirely**, at 0 s each.

## 2. Run less of what is left

| mechanism | effect |
|---|---|
| **pytest-testmon** (`make quick`) | runs only the tests whose executed code changed. Nothing changed means nothing runs |
| **the roll cache** (`pipeline/rollcache.py`) | a map roll is served from `.gencache` when nothing the roll executes changed - this is what turns the reference settlement from 29 s into a HIT |
| **the scope lock** (`switches.py`) | with scope locked to the reference settlement, NO invocation rolls another map - no flag, variable or environment override. Map-rolling tests are deferred and owed at unlock |
| **tier selection / tree ignores** | `quick` skips the town and city trees, `tests/gate` and `tests/full` |
| **coverage floors deferred to FULL** | a deselected test takes its coverage with it, so a floor the reference scope cannot meet is not enforced there |
| **`EXHAUSTIVE`** | sweeps run a documented subset by default and their full form only at the gate |

## 3. The command is refused, corrected, or answered before it runs

Twelve `PreToolUse` guards; six of them are about efficiency. **Since features 164 and 165 the rule is
that a refusal is the LAST resort**, because a refusal costs a model round trip - the exact thing it
is trying to save. The ladder: REWRITE where the guard already knows the compliant command; TEACH FOR
FREE where a block cannot be avoided but the lesson can arrive earlier; refuse only where the action
is destructive or the refusal is itself the content.

| guard | the degenerate case it exists for | what it does now |
|---|---|---|
| **`measure-hooks`** | *"rerunning five minutes of tests after many small quick changes"* | counts expensive runs (`make test-full`, `done FULL=1`) since the last thing that made the numbers stale - an **engine edit** or a **commit**. A *test* edit deliberately does NOT reset it. Blocks the **second**; the **first** carries the batching reminder for free. Escape `MEASURE_OK` |
| **`gate-hooks`** | a `-k` subset selecting the tests you were thinking about, right before the gate | refuses the gate ONCE after a subset-only run. `quick` + `done` in one command are **combined**, not refused. Escape `GATE_OK` |
| **`batching-hooks`** | many single-call turns - the dominant cost | a rolling window: 3 of the last 6 turns each a single quick read-only call blocks the next recon-shaped one. **Warns one turn early**, free. The bar re-arms higher after each firing and decays back |
| **`make-only-hooks`** | reaching an expensive path around `make`, where the cheap question cannot be asked first | refuses a bare interpreter or pytest and NAMES the target; **rewrites** a one-file bare pytest into `make test-file FILE=...` |
| **`no-poll-hooks`** | burning wall clock watching a job the harness will notify you about | refuses a busy-wait; **corrects** a self-matching `pgrep` to the bracket form; **permits** a backgrounded loop whose condition reads a FILE (the `setsid --fork` shape). Escape `POLL_OK` |
| **`pair-hooks`** | the independent review running AFTER the gate, adding its whole runtime to the wall clock | **rewrites** a lone `make done` into `make verify`. Escape `PAIR_OK` |

**Every guard's ESCAPE is an invocation too, since feature 169.** Every token matched in a COMMAND goes through
`_hookmatch.py escape <TOKEN>`; before that they were bare substring tests, so a grep for a token or a
commit message quoting it escaped the guard - and, in `measure` and `gate`, also reset the state that
decides whether the NEXT expensive command is refused. `main-tree-hooks` joined the roster in the same
feature: a bare `cd` into the mirror root followed by a write or a commit, which none of the three
existing main-write guards could see because none of them sees a `git commit`.

The other six (`discard`, `guard-file`, `repo-safety`, `source-block`, `readme`, `clone-sync`,
`no-branch`) are protective rather than economic and stay refusals by design; the reason for each is
in `specs/164-guards-that-correct/research.md` R3.

## 4. The Makefile's own refusals

Different in kind: each asks for a DECISION, which no substitution can supply.

| refusal | what it wants |
|---|---|
| **the reference settlement gates everything expensive** | `test`, `done` and `maps` roll Inashiro FIRST and stop there if it is red. Escape `REF_OK`, which demands a written reason |
| **`make maps` picks its own scope** | after a failed run, the reference map alone; after a clean one, the whole tier. There is deliberately no second command |
| **`FULL=1` prompts and defaults to CANCEL** | a written justification, logged with the date, target and commit |
| **`QUICK_BUDGET` (60 s)** | `quick` fails if it exceeds its budget and points at `make durations` |
| **the switches** (`ci-off`, `scope-lock`) | a `REASON=`, committed |
| **the CodeBuild dispatcher** | five conditions before any paid run: an engine delta, a complete feature, a green local check, no existing verified record, and the spend breaker up |

`research.md` R6 of feature 164 enumerates all ten and finds exactly one convertible - the number
claim, fixed in feature 165.

## 5. Take the cost off the critical path

- **Background the final gate and never poll it**; act on the completion notification. Detach a long
  run with `setsid --fork` (plain `setsid` does not fork when it is not a process-group leader, so
  the run stays a child of the tool call and dies with it).
- **`make verify`** starts the gate in the background AND prints the review to dispatch in the same
  turn, so the two overlap instead of queueing.
- **Idle tests**: after 60-120 minutes of idle time (staggered per session, restarted on a laptop
  resume), the clone runs the whole gate detached and the verdict opens the next prompt. Once per
  idle, never on unchanged content, aborted the moment a prompt arrives.

## 6. The records that make all of this auditable

Without these, "is this guard worth what it costs" is an impression. With them it is a query.

| record | answers |
|---|---|
| `dev/run-log/` | every gate run with its elapsed seconds, scope, result and commit - so a target that quietly gets slower shows up in history rather than in someone's memory |
| `~/.claude/guard-log/` + `make audit` | every block, rewrite, reminder, permit and escape, per guard **and per RULE**, with the **escape rate**. A guard escaped more often than obeyed is costing a round trip to prevent nothing - that is what retired the quick+done refusal (62% escaped). Since feature 168 EVERY acting branch of every guard records, and the rule slug says which of a guard's rules is carrying the cost - "no-poll fired 32 times" cannot. It is HOST-WIDE and gitignored-by-absence rather than in a clone, because a hook fires for commands that name no working tree at all; the cost, stated rather than hidden, is that a container rebuild loses it |
| `dev/bypass-log/` | every override with the reason someone will read |
| `make durations`, `make check-census` | where the suite's time goes; which checks re-measure a placer's guarantee |
| the perf bookends | a seed >5% slower must be diagnosed; a total >10% blocks as a regression |

## 7. The caches, and what invalidates them

Two derived caches make the difference between a warm clone and a cold one. **Both are gitignored and
per-clone**, so a fresh clone starts cold:

| cache | where | size | what it holds |
|---|---|---|---|
| testmon | `.testmondata` | 1.5 MB | per test, the source files it executed, keyed by CONTENT hash |
| the roll cache | `.gencache/` | 15.7 MB, 470 files | finished map rolls, keyed by the subject and the rolled code |

**What invalidates testmon** (measured, not assumed): every one of its 3,331 file rows carries a
content hash (`fsha`) and **zero carry an mtime**, so a fresh checkout's new timestamps invalidate
nothing. Every path is repo-relative - **0 of 3,331 absolute** - and no file outside the repository is
tracked. It is additionally keyed to an `environment` row: the Python version and the exact installed
package list, so an interpreter or dependency change correctly invalidates the whole database.

**The one gap, which predates any of this**: testmon tracks executed PYTHON, not data. A test whose
behavior depends on a fixture or a manifest re-runs only when its code changes. The gate covers it,
because the gate never selects.

**Could the cache be shipped so no clone is ever cold?** Technically yes - it is content-addressed and
position-independent, which is exactly the property that makes a copy valid. Two things stop it being
an obvious win, and both are recorded here so the question is not re-derived from scratch:

1. **The vehicle cannot be a commit.** A 1.5 MB binary SQLite file that changes on every test run is
   the worst possible shape for this repository's concurrency model: several clones push per day, and
   a shared binary blob conflicts on every concurrent push. That is the same pathology the run log
   and bypass log avoid by being one file per entry.
2. **The natural producer is forbidden from producing it.** Main is never a workspace - the ONE thing
   a session runs there is render-sync - so main cannot build a testmon database or a roll cache by
   testing. A copy would have to come from a sibling clone at the same commit, or from the idle
   runner, or from CodeBuild.

**And the payoff is small**: 25.3 s - 4.1 s = **~21 s, once per clone**, against roughly one or two
new clones a day. The roll cache is the larger prize of the two and would be the one to price first
if this is ever taken up.

## 8. What all of this is worth, and how to tell

The honest summary: the short-circuits (layer 1) and the selection (layer 2) do the heavy lifting -
48 gate runs skipped entirely, and a `quick` that answers in four seconds. The guards (layer 3) are
cheaper than they look ONLY because they now correct and teach rather than refuse; when they were all
exit-code-2 they cost 280 round trips in six days.

The test of any future addition here is the one the GM set: **does it cost less than what it saves?**
A guard that fires on correct work fails that test twice over, because it also teaches a session to
reach for the escape as a matter of routine - which is why every escape lands its reason in a log
somebody reads.
