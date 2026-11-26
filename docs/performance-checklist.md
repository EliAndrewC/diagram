# Performance work - the checklist

Load this file when: you plan, build or review a change whose goal is speed - any performance task, at any tier.

**The tools this checklist first named counted and timed the Python engine and are gone** (`make perf`, `perf-profile`,
`perf-fanout`, `phase-calls`, `perf-ab`; feature 444 T39, the names left the Makefile with feature 449 T223). The questions
stand; the measure for the Rust stages is their counted operations - `make work-budget` (a hamlet stage, 10/20/40/80
households) and `make budget-sheets` (a Mode A stage, per pool sheet) against their budgets (feature 443) - and a timing is
any before-and-after wall time, read with the host's load beside it. The Tools table below says what is live.

## The sensibility (the GM, 2026-10-27; feature 435)

- **Time is the goal of every performance change, and never a gate.** Nothing refuses on a timing - not a push, not a task's
  close. A timing depends on the host's load and on which core runs it (not every core here runs at one speed), and waiting
  for a quiet host to measure costs the time the work is meant to save.
- **Call counts are the deterministic measure.** They do not move with load, so they find where work multiplies (`make
  perf-fanout`, `make phase-calls`), and the call-count tripwire (feature 427) catches work creeping back.
- **Time is evidence, read with judgment.** Compare under similar conditions where it is convenient - before and after
  alternated, best of a few, the spread shown (`make perf-ab`) - and read the totality of what was done. Time falling with
  calls confirms the work. Calls falling while time does not, across several comparisons, is a finding: it changes what you
  try next. It is never a failed check, and a single run proves nothing either way.
- **This checklist keeps the steps; it is not the goal.** Each item is a question a good performance change answers. Answer
  it honestly; never tick it to have ticked it, and never let an item make fewer calls a goal in itself.

## The trap this exists to avoid

Fewer calls is not less time. Feature 417's speed lane cut a 40-household roll's calls 38-44% and its time 0-6%, inside a
run spread of up to 1.2 s (an alternating best-of-3 A/B, measured 2026-10-27): much of it inlined helpers and replaced
`min`, `max`, `abs`, `len`, `hypot` and `dict.get` with inline code. That lowers what a profiler counts and barely touches
the time, and it costs readability. Combining functions to lower the count is pointless.

## The questions (answer each in the task's plan, in a sentence or two)

1. **Where does the time go?** Not only the calls: `make perf-profile SEED=<n> STAGE=<stage> HOUSEHOLDS=<n>` (cumulative
   time) beside `make phase-calls` and `make perf-fanout` (calls and growth). Name the stage and the loop.
2. **Does the change remove work, or only move it?**
   - Removes work: fewer candidates tried, a cheap screen before an expensive test, a result kept instead of computed again, an
     index asked instead of a scan, an early stop, a better algorithm, a loop moved into C (numpy, shapely's array functions).
   - Only moves work: a helper inlined, functions merged, a builtin replaced by inline code, a `.get` replaced by a subscript.
     Never the goal. Do it only where the time evidence shows a gain worth its cost in readability.
3. **What do you expect it to save, and why?** In time, before building: a share of the stage's profiled time, not a count.
4. **How does the work grow with the settlement?** The fanout's growth exponent between sizes (20 -> 40 households now;
   hundreds and thousands of buildings in a walled city later). Work that grows faster than what is placed is what will hurt
   at city scale - say whether this change bends that curve.
5. **What did the before and after show, and under what conditions?** Calls (exact) and time (`make perf-ab`: alternated,
   best of N, the spread of each arm, wall and CPU, the host's load) - stated as evidence, not as a pass. QUICK FIRST
   (feature 436): iterate on the quick form - one seed at one size, `make perf-ab A=<parent>` (seed 25 at 40 households) -
   read against its noise floor (`make perf-ab AA=1`, once per form); then a subset (`SEEDS=`, `HOUSEHOLDS=` lists) or the
   full sweep (`FULL=1`) once before landing. A wider run with no quick one of the same engines is refused.
6. **Did any map move, and does it still keep the research?** Speed work may move maps (the GM, 2026-10-18); hold them to the
   rules and the research claims, never to identical output.
7. **What was decided, and where is it recorded?** (the GM, 2026-11-26: *"the stuff that we have decided not to do ... is
   getting captured somewhere that we are able to look it up later, right? ... we should incorporate this step into that
   checklist-based process"*.) Whichever way it went - adopted, declined, or left for more data - the decision has its entry
   in `docs/process-decisions.md` (the question, the GM's words if he decided it, the measurement with its date and command,
   the alternatives weighed, and its falsifier: what would reopen it) and its `dev/audits/` entry (`kind: adopted` or
   `declined`), written in the same landing as the measurement. An option DECLINED is recorded the same way as one adopted;
   a measurement saved under `dev/measurements/` with no entry naming it is unfinished work (451 T320 has the push refuse it).
   This holds for a tooling or process tweak as for engine speed work.

## Tools

| question | command |
|---|---|
| a hamlet stage's counted operations at 10/20/40/80 households, against its budget | `make work-budget` (`WRITE=1` replaces `dev/work-budget.md`) |
| a Mode A stage's counted operations per pool sheet, against its per-sheet budget | `make budget-sheets PHASE=<stage> COUNTS="<sheet>=<ops> ..."` |
| one hamlet rolled, its wall time printed | `make hamlet SPEC=pool/hamlets/<name>/<name>.spec.json` |
| N seeds through the Rust driver, the time taken | `make cohort N=<n> SEED=<first>` |

(Retired with the Python engine, feature 444 T39: `make phase-calls`, `perf-fanout`, `perf-profile`, `perf-ab` and the
bookends `make perf LABEL=<NNN>-start` / `-end`.)
