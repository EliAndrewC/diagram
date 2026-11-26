# Trial: is the second tier's threshold right - a full gate when the pipeline drains?

**Form**: trial

**Created**: 2026-11-26

**Status**: Running

**Affects**: tooling

**Approved**: the GM, 2026-11-26, "your suggestion for the threshold seems sensible for now, but this also seems like something where it's probably worth filing a backlog feature to evaluate how things are going after a day or two, just to make sure that whatever it is that we have picked is working out in practice and that we don't need to make any tweaks. You can also mention the stronger version in that feature as something that we can evaluate to see whether it seems like it would in fact be better, or if it actually just doesn't seem necessary or like it would be helping us."

**Input**: `request.md` (the GM's words, verbatim).

<!-- THE TRIAL FORM (feature 438; docs/spec-kit-and-reviews.md, "The trial form"). A question a measurement answers, asked
before any decision to build. Measure first; this brief is reviewed ONCE, by spec-fidelity, when the evidence below is fixed
and the status turns Done - pushes before that go through without a verdict. While it runs it lands no engine code: a spike is
committed, measured and reverted, so its pushes change no engine code on net; a push that does change l7r/ owes the verdict. A
spike that wins lands as any engine change does; its push then owes this brief's verdict. -->

## The question

Since 2026-11-26 checking has two tiers (451 T308): a builder's tree runs the changed crates' tests, lint and format
(`make builder-checks`), finished work is carried into the session clone and staged, and the full gate (coverage, every hook
suite, the static checks) runs ONCE over the batch before it is pushed to main. The threshold picked that day for the second
tier: the gate runs when the pipeline drains - a batch of builders has reported and been carried in - with the next batch
started beside it; a backup branch (`backup/<session>`, deleted when its work lands on main) is pushed after every carry so
staged work is never only local; always before the session stops; and a ceiling of about six tasks or ninety minutes staged
without a gate (GUESS knobs). Is that threshold working in practice, and would the stronger version - a gate that runs
continuously on a snapshot of the staged commit in a tree of its own and pushes exactly that commit when green, the batch
size setting itself - be better, or is it not needed?

## The measurement

Not before 2026-11-28 (the GM: "after a day or two"), over the batches gated since 2026-11-26:

- per batch: the tasks in it, minutes from the first carry to the green gate, the gate's own seconds, its failures by kind
  (format, lint, coverage, a suite or test, a flake) and what each cost to repair and by whom (the tooling, the session, a
  fresh fixer) - from the landing logs and `make task-time`;
- how often the ceiling fired, and how long staged work stood unpushed (and whether the backup branch held it throughout);
- the second tier's BLOCKING minutes (the GM, 2026-11-26: it "is rarely going to be blocking anything" - no new task waits on
  it): expected near zero; what did wait on a gate, if anything - a carry behind a running gate, a repair, a build slot;
- what waiting cost that the threshold was meant to avoid: a failure hard to attribute to its task, a later task built on a
  defect a gate would have caught, a flake re-running a large batch;
- builder minutes a task and tasks landed a wall hour against round one's (2026-11-26, one tier);
- for the stronger version: the minutes the session or its builders waited on a gate, and the batch size the continuous gate
  would have produced (whatever arrived while a gate ran) against the one the drain produced; with one session, and with
  more than one if any ran.

## The rule

It reports, for the GM, which reading the data supports: (a) the drain threshold holds - gates cheap and well timed, the
ceiling rarely firing, no cost of waiting found - and the continuous gate is not needed with one session; (b) a tweak is due -
which knob (the ceiling's tasks or minutes, gating mid-batch) and the figure that shows it; (c) the continuous gate would help -
the waits or batch sizes that show it, with what it needs built (a gate tree: the landing worktree 451 T302 would otherwise
retire). Too few batches is said as such, with the date it is read again.

## The evidence

[Filled as measured: `research/<name>.md` per measurement, each dated with its command and its output in a fenced block beside
the figure - the one review checks a figure against its recorded output and re-runs only what has none (`make trial-review`).]

- THE VERDICT: [the branch of the rule taken] - because [the measurement that took it, with its figure and command].
  [A branch the rule names but the trial did not take, and why - so the review checks the verdict against the rule.]

## The time

As feature 437 reported it: `make feature-report F=458`'s split - the session's work, its waits and the agents' own time,
from the event log - and a per-step breakdown (each step's start, end, time, and whether it was work or a wait), with the
total from the GM's request to the end.

## Review history

<!-- the one review is recorded here when it returns: "- <date>, the one review (spec-fidelity, MODE 2, on the brief with its
evidence fixed): <verdict>." - a line written before it would read as a round already taken -->
