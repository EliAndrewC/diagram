# Trial: fewer envelope probes in the growth's seat search

**Form**: trial

**Created**: 2026-10-27

**Status**: Done - set down by its rule: the spike on the search saved its own stage 11% and cost the roll 17% (`research/spike2.md`)

**Affects**: performance, hamlet

**Approved**: the GM, 2026-10-27, "Then do the search-restructuring trial and break down how long it took in the same way we just did."

**Input**: `request.md` (the GM's words, verbatim).

<!-- THE TRIAL FORM (feature 438; docs/spec-kit-and-reviews.md, "The trial form"). A question a measurement answers, asked
before any decision to build. Measure first; this brief is reviewed ONCE, by spec-fidelity, when the evidence below is fixed
and the status turns Done - pushes before that go through without a verdict. While it runs it lands no engine code: a spike is
committed, measured and reverted, so its pushes change no engine code on net; a push that does change l7r/ owes the verdict. A
spike that wins lands as any engine change does; its push then owes this brief's verdict. -->

## The question

Does the nucleated growth's seat search (`hamletgen/homesteads/growth.py`) build fewer full envelopes when each candidate
seat is screened before its envelope is built - and does that cut the homesteads stage's time? Each envelope
(`household_reach` -> `_bundle_envelope`) lays the household's bundle for all four garden sides, fixtures included; feature
437's profile put 803 of them, 3,212 bundle builds, at about 1.0 s of the stage's 4.5 s under cProfile (seed 25, 40
households). Feature 437 found the shared geometry holds little of the time and named the lever as searches that try fewer
candidates: this asks it of the largest search the profile shows.

## The measurement

[The commands, in the order run, each with what it shows:]

- where the time is: `make perf-share [MODULE=<path>] [STAGES=<a,b>]`
- the change against its parent, quick form: `make perf-ab A=<parent>` (seed 25 at 40 households), read against its floor
  (`make perf-ab AA=1`, once per form)
- the calls of the stage it changes: `make perf-fanout STAGES=<stage>`

## The rule

First, measured: how many envelopes are built per house placed, and how many of their seats the placer then refuses. Where
most are refused, a screen asked before the envelope (the placer's own refusals, as cheap tests) is spiked and measured with
`make perf-ab` quick against its floor. The spike is promoted - landed as a feature of its own - where it saves time beyond
the floor and no map breaks the research; otherwise set down. Where few are refused, the screen cannot pay, and the trial says
so and stops there.

## The evidence

- `research/funnel.md` (measured 2026-10-27, seed 25 at 40 households): the envelope probes take 1.002 s of the homesteads
  stage's 4.47 s under cProfile (22%, `make perf-share`); 803 envelopes are built for 40 houses placed - about 397 re-rolled
  inside the settle loop, 134 for settled seats never offered, the rest for the 272 offered of which the placer refuses 232 (100
  tight seats not landlocked, 72 parts, 57 every side blocked, 3 no yard onto lane ground, 0 by the cheap house-box test).
- The ceiling, measured: cProfile inflates the stage 1.96 times (2.28 s unprofiled at the 435-end bookend), so a perfect screen
  of every wasted envelope and refused placement would save about 0.74 s of 6.93 s - about 10.6%.
- Most seats are refused, so by the rule a screen was spiked. No cheap test predicts the placer's refusals (each is read off
  the laid layouts), so the spike took the other large waste, the settle loop's re-rolls: `research/spike2.md` - each settle
  starting from the widest reach seen. Envelopes 803 -> 394, homesteads -11% under cProfile; the roll +17% (`make perf-ab`
  quick, the floor -4%), because the wider seating more than doubled the web's work (4.93M -> 11.55M calls, `make perf-fanout`).
- THE VERDICT: SET DOWN by the rule (time not saved beyond the floor - it rose), spike 2 reverted. What it shows, limited to
  what was tried: a change to how this one search tries its candidates changed the settlement every later stage works on, so
  a search restructure is measured on the whole roll, never its own stage. Feature 437's other named searches
  (`boundary._samples`, `gap_ways.flood`, `route.lattice_search`, the fixture seats' `_first` and `within_reach_of`) and the
  "fewer, larger questions" form of the lever are untried; this is the first search-restructuring trial, not the last word.

## The time

`report-trial.md` - `make feature-report F=439`'s split and the per-step breakdown, with feature 438's (the tooling it used).

## Review history

- 2026-10-27, the one review (spec-fidelity, MODE 2, on the brief with its evidence fixed): CHANGES REQUIRED - the time breakdown
  missing; the verdict did not follow the rule (most seats refused: the rule called for a spike); the ceiling a guess; the
  conclusion wider than the trial. Applied: spike 2 run and measured, the ceiling measured, the conclusion limited, the time
  reported.
