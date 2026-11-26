# Trial: do long-running features still cost more per landing than small ones?

**Form**: trial

**Created**: 2026-11-26

**Status**: Running

**Affects**: tooling

**Approved**: the GM, 2026-11-26, "For the question of long-running features against small ones, then please file a spec kit feature to do as you recommend and look back over this after we have at least a day or two of good data, and we might need to wait longer than a day or two depending on whether we do end up with any small features during that time."

**Input**: `request.md` (the GM's words, verbatim).

<!-- THE TRIAL FORM (feature 438; docs/spec-kit-and-reviews.md, "The trial form"). A question a measurement answers, asked
before any decision to build. Measure first; this brief is reviewed ONCE, by spec-fidelity, when the evidence below is fixed
and the status turns Done - pushes before that go through without a verdict. While it runs it lands no engine code: a spike is
committed, measured and reverted, so its pushes change no engine code on net; a push that does change l7r/ owes the verdict. A
spike that wins lands as any engine change does; its push then owes this brief's verdict. -->

## The question

Does a task landed in a long-running feature (449, 451: hundreds of tasks, weeks open) still cost more gate friction and
review than a task landed in a small feature filed and closed, now that the defect behind the friction measured on 2026-11-25
is fixed? It is the talk's item 10 (`specs/449-rust-codebase/port-talk-agenda.md`), and the GM will refer back to it for a
larger structural change to how development is done in this project, to be discussed before the mapping work resumes.

What was measured on 2026-11-25 (`dev/measurements/2026-11-25/talk-measures/ALL-TABLES.txt`, M3): gate escapes per landing
1.85 in feature 449 and 1.13 in 451 against 0.0 across 25 small features; plan reviews per task 0.83 (449) and 1.51 (451).
The cause first reported (unstarted tasks' template stubs) was wrong; what the plan gate truly held was 449's 17 withdrawn
tasks' edited, never-reviewed sections, three ticked tasks' stubs and one renumbered block (451 T261's replay). 451 T262 now
refuses an escape the gate does not owe and 449 T439 reviewed the withdrawn sections, so the measured friction may be gone.

## The measurement

Not before 2026-11-28 (the GM: "after we have at least a day or two of good data, and we might need to wait longer than a day
or two depending on whether we do end up with any small features during that time"), over the landings since 2026-11-26:

- gate escapes per landing, by feature: `make audit` (its plan-gate count by each record's `held` list, 451 T270) and the
  `dev/bypass-log/` records, each landing's feature from its tick commit - long-running features against any small feature
  filed and closed in the window;
- plan reviews and their rounds per task, by feature: `dev/review-ledger.md`'s MODE 4 rows;
- minutes and blocking minutes per landed task, by feature: `make task-time SINCE=<the window>`;
- tokens per landed task, by feature: `make where-time F=<feature> SINCE=<the window>` (agents' tokens in and out);
- the count of small features in the window, stated first: with none, the trial waits and says so instead of comparing
  against the 25 old ones, which predate the fixes on both sides.

## The rule

The trial decides nothing about how features are shaped; it reports, for the GM's structural discussion, which of three
readings the new data supports: (a) the friction is gone - long-running features land at 0.1 escapes a landing or fewer and
within about a quarter of the small features' plan reviews, minutes and tokens per task, so feature size is free to be chosen
on other grounds; (b) the friction remains - long-running features still pay more by those measures, with the gate or review
step that charges it named; (c) not answerable yet - too few small features or landings in the window, with the count that
was seen and the date it is looked at again. The thresholds are this trial's GUESS knobs.

## The evidence

[Filled as measured: `research/<name>.md` per measurement, each dated with its command and its output in a fenced block beside
the figure - the one review checks a figure against its recorded output and re-runs only what has none (`make trial-review`).]

- THE VERDICT: [the branch of the rule taken] - because [the measurement that took it, with its figure and command].
  [A branch the rule names but the trial did not take, and why - so the review checks the verdict against the rule.]

## The time

As feature 437 reported it: `make feature-report F=456`'s split - the session's work, its waits and the agents' own time,
from the event log - and a per-step breakdown (each step's start, end, time, and whether it was work or a wait), with the
total from the GM's request to the end.

## Review history

<!-- the one review is recorded here when it returns: "- <date>, the one review (spec-fidelity, MODE 2, on the brief with its
evidence fixed): <verdict>." - a line written before it would read as a round already taken -->
