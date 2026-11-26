# Trial: do sized briefs keep builders under their context cap?

**Form**: trial

**Created**: 2026-11-26

**Status**: Running

**Affects**: tooling

**Approved**: the GM, 2026-11-26, "since it sounds like we want to do some follow-up measurements in a day or two, or maybe next week, after we have more data about how well this is going, then is there already a feature filed for that? Because if not, then we should file that, and then that is another feature that we can talk about before we resume our port, along with the other one that we filed to take similar measurements after we've been running for enough time to gather this kind of data."

**Input**: `request.md` (the GM's words, verbatim).

<!-- THE TRIAL FORM (feature 438; docs/spec-kit-and-reviews.md, "The trial form"). A question a measurement answers, asked
before any decision to build. Measure first; this brief is reviewed ONCE, by spec-fidelity, when the evidence below is fixed
and the status turns Done - pushes before that go through without a verdict. While it runs it lands no engine code: a spike is
committed, measured and reverted, so its pushes change no engine code on net; a push that does change l7r/ owes the verdict. A
spike that wins lands as any engine change does; its push then owes this brief's verdict. -->

## The question

Since 2026-11-25 a builder's brief is sized (one task, at most three jobs; `scripts/container/builder-brief.md`,
`docs/process-decisions.md`, "The builders' context cap stays at 300k, builders stay, and briefs are sized"), tightened on
2026-11-26 (a new guard or command is a builder of its own; a several-job brief names its order and stop). Does the share of
builders that reach the 300k cap and hand off stay under the falsifier's one in five, and do the two additions of 2026-11-26
hold? Before sizing it was 28% (27 of 97 builders); on 2026-11-26, read by hand from the builders' final context sizes, one of
about fifteen (7%). The GM wants it looked at again with more data, and talked about before the port resumes.

## The measurement

Not before 2026-11-28, and again a week on if the count of builders is small (the GM: "in a day or two, or maybe next week,
after we have more data"), over the builders dispatched since 2026-11-25:

- the handoff rate by the M1 method: `dev/measurements/2026-11-25/talk-measures/m1.py` and `m1b.py` (each general-purpose
  builder's brief sized by its jobs and files; a handoff is a refusal at the cap, a handoff file written, or context at 290k or
  more), split before and after the 2026-11-26 tightening;
- the rate by brief size (1-2, 3, 4+ jobs) and for briefs that held a new guard or a new command;
- what a handoff cost where it happened: the successor's minutes and tokens to its first edit (`make where-time`);
- the count of builders in each group, stated first: a group under about ten is reported as too thin, not compared.

## The rule

It reports which reading the data supports, for the GM's discussion before the port resumes: (a) the sizing holds - the
handoff rate under one in five (the audit entry's threshold) with the tightened briefs no worse; (b) it does not - the rate at
or above one in five, with the kind of brief that still hands off named, when the task's own size or the cap is looked at
again; (c) too thin - fewer than about ten builders in a group, with the date it is read again. The one-in-five threshold is
the audit entry's; the group size of ten is this trial's GUESS knob.

## The evidence

[Filled as measured: `research/<name>.md` per measurement, each dated with its command and its output in a fenced block beside
the figure - the one review checks a figure against its recorded output and re-runs only what has none (`make trial-review`).]

- THE VERDICT: [the branch of the rule taken] - because [the measurement that took it, with its figure and command].
  [A branch the rule names but the trial did not take, and why - so the review checks the verdict against the rule.]

## The time

As feature 437 reported it: `make feature-report F=457`'s split - the session's work, its waits and the agents' own time,
from the event log - and a per-step breakdown (each step's start, end, time, and whether it was work or a wait), with the
total from the GM's request to the end.

## Review history

<!-- the one review is recorded here when it returns: "- <date>, the one review (spec-fidelity, MODE 2, on the brief with its
evidence fixed): <verdict>." - a line written before it would read as a round already taken -->
