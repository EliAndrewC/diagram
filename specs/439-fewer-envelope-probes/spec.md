# Trial: fewer envelope probes in the growth's seat search

**Form**: trial

**Created**: 2026-10-27

**Status**: Running

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

[Filled as measured: `research/<name>.md` per measurement, each dated with its command. Then the verdict - promote or set
down - and the reason.]

## The time

As feature 437 reported it: `make feature-report F=439`'s split - the session's work, its waits and the agents' own time,
from the event log - and a per-step breakdown (each step's start, end, time, and whether it was work or a wait), with the
total from the GM's request to the end.

## Review history

- 2026-10-27, the one review (spec-fidelity, MODE 2, on the brief with its evidence fixed): [verdict].
