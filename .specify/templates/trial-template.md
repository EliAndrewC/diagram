# Trial: [QUESTION, AS A SHORT TITLE]

**Form**: trial

**Created**: [DATE]

**Status**: Running

**Affects**: [tags from .specify/affects.json - e.g. performance, tooling]

**Approved**: the GM, [DATE], "[his words, verbatim]"

**Input**: `request.md` (the GM's words, verbatim).

<!-- THE TRIAL FORM (feature 438; docs/spec-kit-and-reviews.md, "The trial form"). A question a measurement answers, asked
before any decision to build. Measure first; this brief is reviewed ONCE, by spec-fidelity, when the evidence below is fixed
and the status turns Done - pushes before that go through without a verdict. While it runs it lands no engine code: a spike is
committed, measured and reverted, so its pushes change no engine code on net; a push that does change l7r/ owes the verdict. A
spike that wins lands as any engine change does; its push then owes this brief's verdict. -->

## The question

[What the trial answers, in one or two sentences, and why it is asked now.]

## The measurement

[The commands, in the order run, each with what it shows:]

- where the time is: `make perf-share [MODULE=<path>] [STAGES=<a,b>]`
- the change against its parent, quick form: `make perf-ab A=<parent>` (seed 25 at 40 households), read against its floor
  (`make perf-ab AA=1`, once per form)
- the calls of the stage it changes: `make perf-fanout STAGES=<stage>`

## The rule

[This trial's own decision rule: what result decides it, and what follows each way. The worked example, feature 437's:
"the change lands only where the evidence shows time saved beyond the quick form's floor; otherwise it is set down (the
engine change not landed), its evidence recorded".]

## The evidence

[Filled as measured: `research/<name>.md` per measurement, each dated with its command and its output in a fenced block beside
the figure - the one review checks a figure against its recorded output and re-runs only what has none (`make trial-review`).]

- THE VERDICT: [the branch of the rule taken] - because [the measurement that took it, with its figure and command].
  [A branch the rule names but the trial did not take, and why - so the review checks the verdict against the rule.]

## The time

As feature 437 reported it: `make feature-report F=[N]`'s split - the session's work, its waits and the agents' own time,
from the event log - and a per-step breakdown (each step's start, end, time, and whether it was work or a wait), with the
total from the GM's request to the end.

## Review history

<!-- the one review is recorded here when it returns: "- <date>, the one review (spec-fidelity, MODE 2, on the brief with its
evidence fixed): <verdict>." - a line written before it would read as a round already taken -->
