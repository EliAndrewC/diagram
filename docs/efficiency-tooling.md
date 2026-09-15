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
| `make _reference` (internal; the public rung was retired 2026-09-06) | one seed of the reference hamlet, and nothing else | **29 s**, or ~0 on a roll-cache hit |
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
| `ci verified-done` | the WHOLE gate, in ~0 s | any change to engine `.py` (compared as its docstring-stripped AST) or to pool gens/manifests. **Not the page's CONTENT since feature 207** - the glossary, the sibling texts, the place card, the page's phrases (`interactive/assets/*.json`), the registry's `Name:`/`Covers:`/`Label:`/`Sources:`/`Entry:` docstring tags, the placement-stages notes and the pool index's text and stylesheet are data files, outside the engine key and the roll-cache key; an edit owes `make page-check` like a stylesheet edit. Docs, tests, the Makefile, config and `scripts/` never re-open it - **nor do comments, docstrings or formatting inside engine Python**. **`l7r/diagram/ci/` DOES re-open it since feature 178**: the coverage floor measures it (`source = ["l7r"]`), and a surface that owes 100% must not be able to skip the gate that enforces it - feature 177 met exactly that, `make done` answering "already verified" on a delta that rewrote four ci modules. The exclusion list is now DERIVED from the coverage configuration rather than kept by hand, so this follows `source` automatically. It does NOT re-open the paid route |
| `gate-stamp --fresh hooks` | the `hooks-test` phase | a change to any guard script. The phase itself runs its suites in PARALLEL since feature 172 - measured on identical content, every suite forced stale: **194 s serial, 63 s parallel** |
| per-suite freshness | any of the 21 guard suites | **its DERIVED dependency set** (feature 172): its own guard and test, plus every shared helper reachable from them TRANSITIVELY, read from code rather than prose. A `_gatecost.py` change re-runs 5 suites where it used to re-run all 21, and a make/rewrite change 6 - measured on real incremental runs; three of those five are the whole-tree suites, which re-run for any script change and always will. The escape family still reaches 17, because every guard reaches its escape - and that is what the parallelism is for |
| `ci tooling-fresh` | `tests/tooling` inside `make quick` | a change to the tooling those tests drive |

Measured: **48 of 314 recorded `make done` runs short-circuited entirely**, at 0 s each.

## 2. Run less of what is left

| mechanism | effect |
|---|---|
| **pytest-testmon** (`make quick`) | runs only the tests whose executed code changed. Nothing changed means nothing runs |
| **the roll cache** (`pipeline/rollcache.py`) | a map roll is served from `.gencache` when nothing the roll executes changed - this is what turns the reference settlement from 29 s into a HIT |
| ~~the scope lock~~ (RETIRED, feature 185) | it deferred multi-map rolls while the gate was slow; feature 174 made the gate run everything, so there was nothing left to defer. Was: no invocation rolls another map - no flag, variable or environment override. Map-rolling tests are deferred and owed at unlock |
| **tier selection / tree ignores** | `quick` skips the town and city trees, `tests/gate` and `tests/full` |
| ~~**coverage floors deferred to FULL**~~ **RETIRED by feature 174** (GM 2026-08-31) | it was true that a deselected test takes its coverage with it - which is why closing the deferral meant making `done`'s test phase `test-full` on both branches rather than floor-ing a partial suite. A plain `make done` now enforces all three floors over the whole engine |
| **the INCREMENTAL GATE** (feature 207, GM 2026-09-07) | a plain `make done` that does run re-runs only the tests a change can reach and still judges 100% over the whole engine: the last FULL green run's coverage is kept PER TEST and PER FIXTURE (coverage contexts, `--cov-context=test` + `l7r/diagram/ci/selection.py`), the planner (`ci/incremental.py`) selects every test whose own contexts or fixture closure executed a changed file (raw bytes, so a moved line re-measures), every test in a changed module and every new one, and the merge drops those tests' old contexts plus every changed file before the floors read the union. Falls back to a FULL run - which is what records the baseline - on: no baseline, a non-Python engine file, a non-module change under `tests/`, the tooling hash, an import-time line, or more than 60% selected. `INCREMENTAL=0` forces a full run. Measured on landing (specs/207 R8): a tools edit 32 s, a polder edit 219 s, a core-placer edit 595 s (every map re-rolls), a full run 664 s, against the old 589 s. The fast coverage core stays: Python 3.14's sys.monitoring core drops a line's event after its first hit and so loses contexts, and the plugin re-arms its events at every context switch (`selection.switch`) - the per-context lines then equal the C tracer's, which was pinned first and cost a full run 2.4x; measured, and a test proves both |
| **`EXHAUSTIVE`** | sweeps run a documented subset by default and their full form only at the gate |

## 3. The command is refused, corrected, or answered before it runs

Thirteen `PreToolUse` guards; seven of them are about efficiency. **Since features 164 and 165 the rule is
that a refusal is the LAST resort**, because a refusal costs a model round trip - the exact thing it
is trying to save. The ladder: REWRITE where the guard already knows the compliant command; TEACH FOR
FREE where a block cannot be avoided but the lesson can arrive earlier; refuse only where the action
is destructive or the refusal is itself the content.

| guard | the degenerate case it exists for | what it does now |
|---|---|---|
| **`measure-hooks`** | *"rerunning five minutes of tests after many small quick changes"* | counts expensive runs (`make test-full`, `done FULL=1`) since the last thing that made the numbers stale - an **engine edit** or a **commit**. A *test* edit deliberately does NOT reset it. Blocks the **second**; the **first** carries the batching reminder for free. Escape `MEASURE_OK` |
| **`gate-hooks`** | a `-k` subset selecting the tests you were thinking about, right before the gate | refuses the gate ONCE after a subset-only run. `quick` + `done` in one command are **combined**, not refused. Escape `GATE_OK` |
| **`batching-hooks`** | many single-call turns - the dominant cost | a rolling window: 3 of the last 6 turns each a single quick read-only call blocks the next recon-shaped one. **Warns one turn early**, free - and since feature 249 the notice speaks on ANY single-call turn at one below the bar, a folded or backgrounded command included, because the window counts round trips whatever their shape and a notice that carried the block's shape test stayed silent on exactly the folded recon the playbook asks for. The bar re-arms higher after each firing and decays back |
| **`make-only-hooks`** | reaching an expensive path around `make`, where the cheap question cannot be asked first | refuses a bare interpreter or pytest and NAMES the target; **rewrites** a TARGETED bare pytest (files, a directory, a node id, `-k` -> `K=`, output flags dropped, the pipeline after it kept) into `make test-file FILE=... [K=...]` and an engine entry point a one-line `$(RUN).<module>` recipe wraps into that target, the table derived from the Makefile at hook time (feature 212); a refusal names the token that stopped the rewrite |
| **`no-poll-hooks`** | burning wall clock watching a job the harness will notify you about | refuses a busy-wait; **corrects** a self-matching `pgrep` to the bracket form; **permits** a backgrounded loop whose condition reads a FILE (the `setsid --fork` shape). Escape `POLL_OK` - which permits the WAIT and nothing else: an escaped command's self-matching `pgrep` is still bracketed (GM 2026-09-08, after an escaped waiter looped for hours on a finished gate) |
| **`pair-hooks`** | the independent review running AFTER the gate, adding its whole runtime to the wall clock - and running AT ALL when nothing about a settlement's layout moved (feature 231) | **rewrites** a lone `make done` into `make verify`; every other gate shape (`make maps`, a detached gate, `FULL=1`) is **recorded and permitted** with the DISPATCH NOW context - a detached run overlaps the review, a foreground run is told the review will follow it and how to overlap next time (feature 212, D7). Since feature 231 it first asks `scripts/_review_owed.py` whether any pool manifest moved against main: no map, no review - the gate runs as typed and the waiver is recorded; a map, and the snapshot is taken into `<clone>/.git/review-snapshot/` and named in the dispatch. Escape `PAIR_OK` |

| **`shell-check-hooks`** (feature 236) | a command that cannot work being sent anyway: the failure costs the command, a model turn reading it, and a second attempt | refuses BEFORE the command runs, with the parser's own message, on four rules that each record separately - it does not PARSE (`bash -O extglob -n`, the options the tool's own shell can enable, because plain `bash -n` refuses work the tool runs); a backtick span bash would EXECUTE, which no parse can see because it is valid syntax; a `git commit -m` with a double quote, a newline or a second `-m`, naming `git commit -F - <<'EOF'`; and a co-author trailer addressed to anything but ours. Measured on 238 real commands: 2 parse refusals, both of which had also failed at run time, 0 false positives. Escape `SHELL_CHECK_OK` |

| **`review-round-hooks`** (feature 249, GM 2026-09-14) | a `spec-fidelity` round after the first re-reading the whole spec - two rounds of one small amendment read every file end to end and were over half of an eleven-minute change, with the contract already saying "only rereviewing the new stuff" | **rewrites** a spec-review dispatch (MODE 2/3; a plan review or an exception check passes untouched) for a feature it has seen before: the previous round's verdict verbatim from the session's own subagent transcript and the diff of the feature directory since that dispatch are PREPENDED to the session's prompt with the MODE 3 instruction, so the reviewer reads those and grep hits only, whatever the session wrote. The first dispatch snapshots silently. Escape `REVIEW_ROUND_OK="<reason>"` for a deliberate full re-read |

**Two static checks joined the CHEAP phases in the same feature**, on the same reasoning one rung
down: `scripts/check-house-style-delta.py` is a `make quick` phase (a British spelling in the delta or
in an untracked file, which is where they were arriving once the corrector only saw `Edit`), and
`scripts/spec-lint.py` runs in `static` and at push (a measured figure with no research pointer, a
withdrawn figure still standing, an orphaned `FR-`/`SC-`, a stale task list). Both are cents against
the thing they save: twenty `spec-fidelity` rounds over two features cost 91 minutes, and at least
eight of those findings were mechanical.

**Every guard's ESCAPE is an invocation too, since feature 169.** Every token matched in a COMMAND goes through
`_hookmatch.py escape <TOKEN>`; before that they were bare substring tests, so a grep for a token or a
commit message quoting it escaped the guard - and, in `measure` and `gate`, also reset the state that
decides whether the NEXT expensive command is refused. `main-tree-hooks` joined the roster in the same
feature: a bare `cd` into the mirror root followed by a write or a commit, which none of the three
existing main-write guards could see because none of them sees a `git commit`. **Feature 204
(2026-09-07) turned it from a refusal into a REWRITE**: it judges where a write LANDS (`_hm_tree.py`,
the command's own cds, variables and subshells walked from the payload's cwd) and moves one that would
land in main to the session's clone with `additionalContext`, because its own firing log showed 173
refusals in a week of which 2 were the shape it was built for. The same feature made EVERY guard's
firing record carry the session name (resolved at firing time), the cwd, the tool and the full command,
and added `make guard-log` to list them.

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
| **the switches** (`ci-off` / `ci-on`) | a `REASON=`, committed |
| **the CodeBuild dispatcher** | five conditions before any paid run: an engine delta, a complete feature, a green local check, no existing verified record, and the spend breaker up |

`research.md` R6 of feature 164 enumerates all ten and finds exactly one convertible - the number
claim, fixed in feature 165.

## 5. Take the cost off the critical path

- **Background the final gate and never poll it**; act on the completion notification. Detach a long
  run with `setsid --fork` (plain `setsid` does not fork when it is not a process-group leader, so
  the run stays a child of the tool call and dies with it).
- **`make verify`** decides whether a settlement-review is owed (a pool manifest moved against main),
  snapshots the changed maps for it, starts the gate in the background AND prints the review to dispatch
  in the same turn, so the two overlap instead of queueing.
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

## 9. The verification and iteration rules, as ruled

*Moved out of CLAUDE.md on 2026-09-15. CLAUDE.md keeps each in a line; this is the record with the
GM's words, the features and the measurements.*

- **Python changes**: `ruff check` + `ruff format --check` + `pyrefly check` (the mypy-strict rule set, feature 142), and the coverage floor - `coverage report --fail-under=100` over the whole engine, run by a plain `make done` (feature 174). It is NOT a pytest flag: `pytest-cov` is never given one and `[tool.coverage.report]` deliberately omits `fail_under`, so the floor runs LAST and a run's own failures are reported before the coverage table.
- **100% COVERAGE IS OWED BY EVERYTHING, THE DAY IT LANDS.** *"A new tool absolutely should silently owe one hundred percent coverage the day it lands."* Enforced **in the standard manner** - a floor on the gate (`coverage report --fail-under=100` in the skill Makefile) with the measured surface DERIVED (`source = ["l7r"]`) - never by a ratchet and never by a roster somebody maintains. **Do NOT put `fail_under` in `[tool.coverage.report]`**: `pytest-cov` reads it there, so it would fire on every partial run (`make test-file`, `make quick`) and would break the deliberate ordering the floor depends on - it runs LAST, after a run's own failures are reported. The GM's *"for example ... and such"* names the shape, not the file.
- **AN INNER FUNCTION THAT IS HARD TO TEST GETS LIFTED OUT (GM 2026-08-28, feature 146).** *"If something is only available as an inner function in a closure, then you can move it out into its own function to make it more unit testable. That is a common unit testing paradigm ... you can generally have your unit tests be much simpler if you're just calling functions that take simple inputs and outputs without needing to create a lot of very complicated setup."* The failure this replaces is real and was in this repository's own commits: a session that met a closure it could not reach wrote *"dropped (nested closure)"* and moved on, leaving the branch untested. **Dropping the test is not one of the options.** Lift the closure to module level with its captured values as parameters, have the inner one delegate so there is ONE body, and test the lifted function with plain dicts and tuples - `web_pieces`, `web_rejoinable` and `fan_rival` are the worked examples, each of which previously needed a whole settlement, a fabric list and a water list to ask a yes/no question. The exception is narrow and must be stated where it is taken: an inner function that genuinely simplifies the implementation AND whose extraction would cost measured performance. *"There usually is not"* such a benefit.
- **AN OVERLAP CHECK WITHIN A MAP IS PERFORMED IN ITS EFFICIENT FORM (GM 2026-09-08, feature 218, constitution Principle X clause 15).** *"We will need to take care to make sure we do not have every item on the map checking for overlap with every other item, or anything silly like that."* Any test of a candidate against the features already on the map - a tree against the crops, a scatter mark against the treads and the water, a parcel against the houses - builds the geometry that does not change during the scan into an index ONCE (`settlement/_geom/indexes.py`: a bounding-box prefilter, a `PointGrid`, a `RingIndex`, a `KeepoutGrid` holding every keep-out of one scatter) and asks the index per candidate; the index prunes, the exact test decides, so nothing is coarsened and the maps do not move. The failure this names was measured the day the rule was written: the windbreak tested each of 37,490 candidate clumps against every edge of every crop polygon (7.2 million segment distances, 77% of a 7.3 s stage) beside an `Indexed` registry the farmhouse placer already queried, and the marsh scatter rebuilt its whole watercourse list per point; both stages went to under 2 s with byte-identical maps. It governs new code and code a profile shows costing time (`make map PROFILE=1`, then `make perf-profile`); a plan that adds an overlap check says how it is indexed. Not mechanically enforced and no subagent reviews it today, by the GM's ruling; the future review of overlap-checking code is recorded in `specs/218-efficient-overlap-checks/spec.md` D4.
- **Edit files with `Edit`, not with heredoc'd Python that rewrites them.** This costs no extra round trips - several `Edit` calls batch into ONE turn exactly like one folded bash command does - and it removes a hazard the patch script carries by construction: Python-inside-a-heredoc that itself contains quoted Python has to be hand-escaped, and when it breaks it breaks as a `SyntaxError` in the PATCHER, so the anchor never even gets tested and a full model turn goes on rewriting the quoting. Measured 2026-08-16 (fan-toe pond fix): three failed patch scripts, ~4-5 min, ~10% of the task, every one a quoting slip rather than a wrong anchor. Keep heredocs for analysis, asserts, and glue that contains no quoted code - and when an edit genuinely must be scripted (a mechanical sweep over many files), **use `scripts/_patch.py` rather than hand-rolling the loop again** (feature 236): each (anchor, replacement) is its own write, so a stale anchor is REPORTED and skipped while every other edit in the batch still lands, and anchors match whitespace-insensitively because four of the six anchor misses in the record spanned a line wrap. The ad-hoc form - accumulate every edit, write once at the end - discarded the substantive edits beside one cosmetic miss three times in a single day, and reported success each time.
- **Foreground-regenerate ONLY the motivating map - never a pre-gate pool sweep.** The gate verifies the pool itself, and render-sync regenerates main's renders from main's own tip, so a clone-side `pipeline/regen.py pool/*/*/*.gen.py` before `make done` is pure waste (38s measured 2026-08-16; evidence in [`docs/iteration-loop.md`](docs/iteration-loop.md)).
- **EVERYTHING RUNS THROUGH `make`, and it is enforced rather than requested** (feature 127). A bare
  interpreter reaching an engine entry point, a bare pytest, a make driven by a foreign makefile, or
  an inline override supplied to skip a prompt is refused BEFORE it runs by
  `scripts/make-only-hooks.sh`; the engine refuses in-process calls too. In the diagram skill the
  ladder, cheapest first, is `make quick`, `make done` (NOT the quick one),
  `make done FULL=1` (prompts, cancels by default, logs a reason). **What each costs is asked of the
  recorded runs, never written down here** (feature 162, GM 2026-08-30: *"I think those numbers for
  `make quick` are wrong and outdated"* - they were: the guard message said the gate cost ~70 s with
  the scope locked, while the scope had been unlocked for three days and the run log's median was
  111 s). `make audit` prints the history; `scripts/_gatecost.py <target>` prints the median a guard
  message would quote. Every refusal names the target that
  does the job, because a guard that blocks a legitimate question without giving the route is a guard
  that gets worked around.
- **`make quick` selects by CHANGE** (pytest-testmon, GM 2026-08-26): it runs only the tests whose executed code changed since the last run - nothing changed means "no tests ran" in ~3 s, a one-line engine edit runs its ~10 tests in ~7 s. `make quick ALL=1` runs every quick test; the gate never selects. A test that reads a DATA file (a fixture, a manifest) re-runs only when its code changes - the gate covers that.
- **`make quick` is the UNIT suite; `make done` is the INTEGRATION suite (GM 2026-08-26, constitution "quick runs the unit form; the gate runs the integration form").** A test with a quick form runs it in quick and its full form at the gate (`tests/_scope.py`: `full_or`, `subset`; the gate always sets `EXHAUSTIVE`). Tests that RUN the tooling (`make` in a fixture, git repos, coverage subprocesses) carry `tooling` and run in quick only when the tooling changed since the last green gate. The bad-map corpus replays at the gate, not in quick.
- **`make quick` while iterating, `make done` ONCE at the end**
- **`make done` reports ALL failures together.** Fix everything it lists, then re-run once. On a coverage failure it also prints the lines you changed that no test reaches.
- **Background the final gate - and NEVER poll it.** Act on the completion notification. **ENFORCED** by `scripts/no-poll-hooks.sh`, which blocks `pgrep -f`, sleep-loops, and the `command sleep` bypass. (A wait on genuinely EXTERNAL state passes by putting `POLL_OK` in the command with a note saying what it waits for.)
- **Read derived data from the recorded artifact, not by re-running the generator.** Regenerate when you need to change what a generator DRAWS; read its manifest/output when you need to know what it drew.

