# How we work, and why: the process decisions with their reasoning and numbers

**Load this file when:** you are about to change how work is organized - running builders, landings, claims rounds or page
sessions in parallel; clones against worktrees; starting work before a plan review is final; the tooling's run time;
long-running against small features; what must be a spec-kit feature - or the GM asks why we work the way we do, or
reopens one of these questions.

The GM, 2026-11-25: *"we also want to make sure that these decisions are stored somewhere that the next time we talk about
them, then it will be obvious to that new other session where it is that they can go in order to [look] up this reasoning
and measurement and such."*

Each decision is recorded here once it is made: the question, the GM's words deciding it, the measurements it rested on
(each dated, with its method and the command that reproduces it), the alternatives weighed, and what followed - a task
filed, a rule changed (where), or nothing and why. A later session that reopens a question starts from its entry and
re-measures with the same command before arguing for a change.

## Open: the talk before the port resumes (449 T437)

Eleven questions, raised by the GM on 2026-11-25, are listed with their context and the measurements each needs in
`specs/449-rust-codebase/port-talk-agenda.md`. The figures come from `make task-time` (the task time breakdown, 451
T243) and `make where-time`. When the talk decides an item, its entry moves here, and the agenda keeps one line pointing
at it.

## Decided

### What counts as blocking time (decided 2026-11-25)

**Question.** The task time breakdown (451 T243) reports each kind of work twice: its minutes, and its BLOCKING minutes.
What makes a minute blocking?

**Decided** - the GM, 2026-11-25: *"a minute should count as blocking. When something else is waiting on it to be done before
it can be started. because that is a different standard than whether or not a different unrelated piece of work is able to be
done at the same time ... if we need to decide which of two implementations to perform, and then in order to do that, we must
perform research in order to know what is even correct, such that that research must complete prior to us beginning our
implementation work, then that research is blocking. And that research would be blocking even if there was a different
unrelated task happening in a different subagent at the same time."*

**Reasoning.** Two readings were tried and rejected the same day: a session's own idle waits summed (it booked a headless page
session's turns as blocking - 949 min, half the working time - and could exceed the clock), and the project's wall clock with
nothing working anywhere (it hides research a decision truly waits on whenever unrelated work runs elsewhere). Blocking is a
DEPENDENCY: work blocks a task when that task's next step waits on its result. Research run beside other work to clarify
wording or labels blocks nothing; research a choice of implementation waits on blocks that task.

**How it is measured.** The tooling cannot know the dependency from a make target, so the data carries a clue where the
session knows it: a `Blocks: <feature> T<n>` or `Blocks: none` line in a dispatch (builder, page-session brief, research pass,
review agent) and an `L7R_BLOCKS` variable on a make run; where none is given, stated defaults decide (a builder's foreground
command blocks its task; a background run only from when its task waits on it; a page session or research pass blocks
nothing unless its brief names a task). Accuracy of about 90% is enough - the GM: *"it doesn't have to be 100% exact ...
what we're looking for here is just a broad understanding of where our time goes when we are implementing tasks."*

**What followed.** 451 T243 builds it (`make task-time`); the builder brief and the page-session briefs carry the `Blocks:`
line. **Falsifier:** a sample of tasks read by hand where the booked blocking disagrees with what actually waited more than
about one time in ten - then the clues or the defaults are wrong.

