# Trial: the web's lattice search, and the named searches' ceilings

**Form**: trial

**Created**: 2026-10-27

**Status**: Done - stopped at the measurement: the search's ceiling is 2.7% of the roll, under the 4% floor; no named search's reaches it

**Affects**: performance, hamlet

**Approved**: the GM, 2026-10-27, "I think you should make all 5 of those tooling improvements and then run another search trial on one of the 5 untried searches."

**Input**: `request.md` (the GM's words, verbatim).

<!-- THE TRIAL FORM (feature 438; docs/spec-kit-and-reviews.md, "The trial form"). A question a measurement answers, asked
before any decision to build. Measure first; this brief is reviewed ONCE, by spec-fidelity, when the evidence below is fixed
and the status turns Done - pushes before that go through without a verdict. While it runs it lands no engine code: a spike is
committed, measured and reverted, so its pushes change no engine code on net; a push that does change l7r/ owes the verdict. A
spike that wins lands as any engine change does; its push then owes this brief's verdict. -->

## The question

Can the web's router (`route.lattice_search`, the largest of the five searches trial 439 named by its time) be made to ask
fewer, larger questions - and is any of the five worth a spike at all? Trial 439 found a search judged by its own stage misleads
(its spike cut its stage and slowed the roll), so each is judged here first by what the whole roll could gain.

## The measurement

[The commands, in the order run, each with what it shows:]

- where the time is: `make perf-share [MODULE=<path>] [STAGES=<a,b>]`
- the change against its parent, quick form: `make perf-ab A=<parent>` (seed 25 at 40 households), read against its floor
  (`make perf-ab AA=1`, once per form)
- the calls of the stage it changes: `make perf-fanout STAGES=<stage>`

## The rule

First the ceiling: what the roll would save were the search free (its cumulative time, unprofiled, over the roll). Where the
ceiling is under the quick form's floor (4%), no change to it can be seen in the quick A/B - the trial says so and stops at the
measurement. Where it is over, the batched form is spiked and measured with `make perf-ab` quick against the floor, and is
promoted where it saves time beyond it; otherwise set down. (This rule was written after the first profile reading - the
ceiling question trial 439 learned to ask first.)

## The evidence

- `research/ceilings.md` (measured 2026-10-27, seed 25 at 40 households): the lattice search is 0.428 s of the web's 1.90 s
  under cProfile (22%) - its loop, its memo dictionaries and its two per-cell tests; unprofiled, 0.187 s, 2.7% of the roll. The
  other four named searches' ceilings are 2.8%, 1.6%, 1.2% and 1.0%.
- The batched form (every cell's verdict asked at once) is feature 278's withdrawn design, and an array form of the fabric
  index's test does not exist; A* toward the goal is feature 284's withdrawn change.

- THE VERDICT: STOPPED AT THE MEASUREMENT, the rule's first branch - because the search's ceiling, 2.7% of the roll
  (`research/ceilings.md`), is under the quick form's 4% floor: even its deletion could not be seen. The second branch (the
  spike) was not taken; and no other named search's ceiling reaches the floor either (the highest, 2.8%).

## The time

`report-trial.md` - `make feature-report`'s split and the per-step breakdown, with feature 440's (the tooling it used).

## Review history

- 2026-10-27, the one review (spec-fidelity, MODE 2, on the brief with its evidence fixed): FAITHFUL - every profiled figure
  re-derived from the kept profiles; re-timed under load (the roll 8.04 s) the ceilings still sit under the floor (2.6%, 2.8%).
