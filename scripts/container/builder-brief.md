# The rules behind a code builder's brief

Load this file when: you, the coordinating session, are about to dispatch a builder for a code task; or you are a builder, sent
here by the first lines of your brief.

THE STANDING PART OF A BRIEF IS MADE BY A COMMAND, not pasted from this file (feature 451 T334; the GM 2026-11-26: "is this also
part of our checklist-based process for kicking off and managing builders? ... I just want to make sure that we're putting the
instructions in the right place"):

    make builder-brief T=<task> F=<feature> KIND=fix|measurement|build-half|closing-half [JOBS=<n>] [MEASURES=<n>] [CRATE="<crates>"] [BLOCKS="<feature> T<n>"] [LOAD=1]

It SIZES the brief first - one task or one bundle (`T=a,b`), at most three jobs, a measurement's things measured, a new mechanism never one `fix` - and
refuses with the commands to run instead; then takes the task's tree from the pool (`make builder-tree`'s own step) and prints the
block for that kind: the marker line `BUILDER-BRIEF <feature> <task> KIND= JOBS= TREE=`, the tree and its exports, the kind's STOP
POINT, the first-tier checks, the filing and report lines. Paste it at the head of the brief, then write the task's own text. A
builder's dispatch without that marker, with a marker the pool does not bear out, or a measurement that orders a source edit, is
refused (`rust/guard/src/guards/builder_brief_hooks.rs`; a dispatch that is no builder's takes a prompt line
`BUILDER_BRIEF_OK: <reason>`). Why a command: on 2026-11-26 the session broke the sizing rules below five times with nothing
refusing (T285, T298, T316, T308, each at the 300k cap; T315 at 308k), and its briefs carried no STOP POINT line.

What stays here is what a prompt cannot show: why each rule exists, with its incident. The block is under 2,000 characters on
purpose (`agent-prefix-hooks` refuses a prompt repeating that much of an earlier one), so it points here instead of quoting.

Why builders stop where they do: on 2026-11-24/25 five 449 code builders and the 451 T218-T222 builder hit the 300k context cap
and handed off, each handoff costing a fresh builder 10 to 20 minutes of re-reading. One builder did the fix, the measurement sweep,
the plan section, the plan review AND the claims round. The claims round (agents, replies, re-bundles) is the part that runs it out.

Enforced (451 T237, `rust/guard/src/guards/context_cap_hooks/split.rs`): a builder whose brief holds a line opening
`STOP POINT` is refused a `claims-triage` or `impl-drift` dispatch (an Agent call, or a Workflow naming either), and its
context-cap handoff says it stops there; the command's block carries that line for every kind. A claims-round dispatch's prompt
opens `Run the claims round for feature ...` and is never held. The coordinating session runs the claims round (the claims-triage
agent, make claims-bundle, impl-drift, make claims-checked) as its own dispatch; a DRIFTED fix: claim comes back to a small builder.
Past the 300k cap a builder has a WRAP-UP BAND to 340k (451 T417) in which it may still run its stop point's own steps and write
the handoff file its brief names (451 T352), never new code - so a brief names its handoff file by its full path.

THE FOUR KINDS: `fix` - red-first, then its own plan section and review; `measurement` - changes no source, writes the record,
files the levers it priced, and its report is the next builder's brief; `build-half` - builds and tests a new mechanism and ends at
a handoff file (`<the clone's git dir>/l7r-handoffs/<task>-build.md`) by about 200k; `closing-half` - reads that handoff first, then
the owed tests, the plan section and the review. Every kind that changes source stops at the FIRST TIER's checks (TWO TIERS, below):
the closing half too, whose block told it to run `make crate-checks` for real coverage until 451 T308 brought it into line.

SIZING, before you write the brief (the GM 2026-11-25, pre-approving the talk's item 12; `docs/process-decisions.md`, "The
builders' context cap stays at 300k, builders stay, and briefs are sized"; audited as `dev/audits/builder-brief-sizing.md`):

- ONE task a builder. A BUNDLE - tasks one builder builds in one tree, as T299 and T282 were on 2026-11-26 - is briefed as one
  (`T=a,b`) where `make builder-tree T=a,b` hands a tree out for it: the marker names both, and the guard reads the tree held for
  both. It is sized as one brief: its jobs together are at most three.
- At most THREE jobs in a brief. A measurement or sweep, a build, a found defect's fix and written content each count as one.
- A NEW GUARD (with its suite) or a NEW COMMAND is a builder of its own: it is several jobs' size, whatever it counts as
  (2026-11-26: the pool task, three such jobs, reached the cap at 307k; the landing refusals, two, finished at 296k; fifteen
  other builders that day ended at 122k to 174k).
- A NEW MECHANISM (a command, a guard, a background step that is measured before and after) is TWO builders from the start:
  the first (`KIND=build-half`) measures, builds and tests and writes a handoff; the second (`KIND=closing-half`) writes the
  plan section, takes the review and reports; the command refuses `KIND=fix` for a task whose line names a new command or
  guard. Three of three such tasks under two tiers reached the cap before closing (T285, T298, T316, 2026-11-26).
- A MEASUREMENT is sized by the THINGS MEASURED as well as its jobs: each crate, lever or case timed is one, and a brief measures
  at most six (`MEASURES=`, a GUESS knob: 451 T315's "one job" timed seven crates and priced eight levers and ended at 308k). Past
  that it is two measurement builders, the first's record the second's brief.
- A task that must LOAD the machine runs ALONE in its batch, bounded (`LOAD=1`; 451 T321; feature 460).
- A brief of more than one job NAMES THE ORDER and the stop: "if these will not fit, finish <job> whole, stop, and report
  the rest as not started" - so a builder near its cap stops at a job's boundary and its successor takes up a whole job.
- A task expected to edit more than about three files, or needing a measurement first, is SPLIT into builders that hand results
  along, a measuring agent first: its report (the figures, the paths, the commands) is the next builder's brief.
- A one-turn edit is yours, the coordinating session's, not a builder's.
- Tell a builder: an assertion's failure MESSAGE stays on the assertion's own line or is left out - on a line of its own it is
  never reached while the assertion holds, and the batch gate's coverage refuses it (three gates in a row, 2026-11-26; 451 T343).
- TWO TIERS (a trial from 2026-11-26; `docs/process-decisions.md`, "Two tiers of checking"): a builder's tree runs the FIRST
  tier only - `make builder-checks CRATE="<the crates it changed>"` (tests, lint, format) and a changed guard's own hook suite
  - while ITERATING, `make rust-test CRATE=<dir> ONLY="<module::path> ..."` runs only the changed modules' tests, kept as no
  crate's green, and `make builder-checks` still runs each crate whole at the builder's end (451 T435) - and NOT `make closing-checks`, `make static`, `make hooks-test` or a coverage run; the full gate runs once in the clone
  over the batch (`make land T="<tasks>"`, which carries each task's done commit first, 451 T397; `make carry` is kept for a
  carry by hand or one a landing stopped on), after `scripts/sync-with-main.sh backup` for each. The block's
  CHECKS line says so, for every kind. A BUILDER RUNS NO COVERAGE (the GM's ruling of 2026-11-26, the same record's "REVERSED
  the same night": the goal is tasks through, not gates passed, and a red batch gate holds no builder back): on the session's own
  reading, briefs from 21:40 UTC that day added `make crate-checks` after the first tier, 7 to 111 s on every builder's critical
  path, and that was withdrawn (451 T381). THE ONE EXCEPTION: a builder whose JOB is the coverage repair of a red batch gate
  runs `make crate-checks CRATE="<the crates its brief names>"` - coverage is what it was sent to mend. In the session clone the
  check of a repair is the batch gate itself: the order notice at `make decide` names `make land` for the staged batch there,
  and says nothing while a landing runs (451 T308).
- A builder ENDS at its report and is not kept for follow-up (the GM 2026-11-26): what a successor needs is in its plan
  section, its commit and its report, and a later fix - a gate failure, even a design that proved wrong - goes to a fresh
  agent briefed from those. A message to a builder is for a question it asked before it reported.
- THE BUILDER HANDS IN ITSELF (461 T43, US2: "A refusal a builder can answer is answered by the builder that has the context"): a
  `fix` or `closing-half` builder's last step, once its plan review is CLEAR, is `make builder-done T=<task(s)> F=<feature>
  MSG="<the commit's subject>" [GUARD="<guard-edit reason>"]` - the HAND-IN since 461 T08: it applies the tree (found in the pool's
  registry) onto the clone's HEAD, asks the landing's first pass there, commits it, keeps the commit under
  `refs/l7r/done/<feature>-<task>`, releases the tree and prints the next dispatch and `handed in to the lane`. A conflict no rule
  resolves is left in the tree with its paths named: the builder resolves them, `git add`s those paths - the one hand `git add` in a
  pool tree - and runs it again; a first-pass refusal it answers in its tree (each prints its fixing command) and runs it again; one
  that is the session's (an owed claims round, which a builder never dispatches) it reports verbatim and stops, the tree held. It
  never lands or pushes, touches the tree no more after `handed in`, and reports the outcome, the done ref and the next dispatch the
  command printed. WHY: since T08 the session ran it after the report, so a conflict or a refusal reached the coordinator, who had to
  re-read what the builder already knew (found by T08's builder). Past the context cap the wrap-up band lets `make builder-done`
  through (`context_cap_hooks/band.rs`'s `MAKE`) but no edit: a conflict there goes to the handoff. A `build-half` builder hands
  in once its handoff is written and a `measurement` builder once its record is (461 T44): neither writes a plan section, so their
  hand-in puts off the two asks a stub section fails - the plan gate's of the task and its Approach block's - reading the kind from
  the brief's line of the pool's log, never from the builder; a measurement's hand-in is refused while its work holds nothing under
  `dev/measurements/`, the record standing in for the section. Every other ask stands, and the landing asks both whatever the kind.
  WHY: the tick check's approach refusal refused a stub's Approach block, so from T08 to T44 neither kind could hand in, whoever ran
  it. The block's CHECKS line names the coverage-repair exception in a fix's block alone (a repair is briefed as a fix): with the
  hand-in line, a build half's block with every option given ran past the 2,000-character cap (2,256 in the test, 2026-11-27).
- AT A BUILDER'S END, your steps in this order (451 T394): where the builder has not handed in (a builder stopped short), `make builder-done T=<task(s)> F=<feature> MSG="<the commit's subject>" [GUARD="<guard-edit reason>"]`,
  as above; THEN THE NEXT DISPATCH (`make builder-brief` for the queue's next task no tree holds, the one `make builder-done` printed,
  or `make builder-next`), and only then - in phase 1, until the lane runs it - the landing, `make land F= T=`, which
  carries the commit itself (`make carry FROM=<the tree> COMMIT=<the commit>` by hand, or after a carry stopped), while the next
  builder works. Never a hand `git commit` in a pool tree (nor a hand `git add` but a hand-in's conflict's paths), and never the
  carry before the dispatch: measured 2026-11-27, the three warm trees stood idle 23% of an eight-hour window with the queue never
  short, because the tree waited on the carry, its conflicts, the gate and the landing
  (`dev/measurements/2026-11-27/tree-idle/results.md`). `make builder-trees` lists every done commit not yet carried, each with
  its carry. THE ONE EXCEPTION to dispatch-first: the SAME task's next builder (its closing half) is dispatched AFTER its carry -
  a handout brings the tree to the clone's HEAD, so before the carry it would start without the build half's work: `make builder-tree`
  (and so `make builder-brief`) refuses that handout with the carry to run (451 T398), and a task's second `make builder-done`
  is refused until its first commit is carried. A done commit is also carried by `make carry COMMIT=<sha>` alone (451 T397).
- THE QUEUE IS A FILE, AND THE TOOLING NAMES THE NEXT TASK (451 T313, T395, T297): `specs/<feature>/queue.txt` holds one entry a
  line, in the order to hand out - `<task[,task]> <kind> [jobs=] [measures=] [load=1] crates=<dirs|-> files=<paths|-> [waits=<T<n>,GM,alone>]
  [note=...]` - written by `make queue-add` or a plain edit. `make queue` lists it with each state computed (landed, built, in
  flight, waiting, READY); `make builder-next`, and `make builder-done`'s first step, print the next READY entry (performance work of any queue first, FR-013; an open performance task with no line named before it, with its `make queue-add`) whose crates and
  files overlap no task holding a tree, with its exact `make builder-brief` command and each entry passed over. Paste that command whole: its `ENTRY=<k>` is
  logged beside the take, so the `make builder-done` line names the entry it ends (a successor on the same tree inherits it). An entry is ONE
  dispatch: a mechanism is two lines (its build half, its closing half), a line stays until its task is landed, and a task that
  needs another builder gets another line. A turn that ends with a pool tree free, fewer than `L7R_BUILDERS` (3) held and a READY
  entry is refused (`rust/guard/src/guards/pool_idle_hooks.rs`); where the tree should stay free, a line of the final message STARTS
  `POOL_IDLE_OK: <reason>` (the next entries wait on the GM; the count is held for a measurement) - at the line's start, not after
  a bullet or in backticks.
- A builder's commit reaches the clone by `make carry FROM=<its worktree> [COMMIT=<sha>]` run in the clone (451 T292), never a hand `git cherry-pick`: `make land` refuses a carry-over left unfinished.
- TWO code builders at once, each in a REUSED worktree (its build cache warm); three or four at once only for batches that
  compile nothing (`docs/process-decisions.md`, "Two code builders at once"; `dev/audits/parallel-builder-count.md`).
- The memory sampler starts with a handout: `make builder-tree` starts the clone's sampler where none runs, and the hand-started
  shell loop of 2026-11-26 is retired - `make sampler` says whether it runs, `make sampler-report` reads a batch's window (451 T274).
- A builder that ABSORBS a filed task - builds its work inside its own task's section - writes, in that section, a line of its own
  `Built here: T<n> - <what was built>` (451 T307 part 2), leaves T<n>'s plan stub unfilled and names T<n> in its report's FOR THE
  SESSION; `make decide` holds the line to an open box with an unfilled stub, the plan review rules on it, and the session lands both
  (`make land T="<own task> T<n>"`), which ticks T<n> `built inside` it. Without the line, T<n>'s tick is refused for its stub and
  `make task-withdraw` for its carried code (T393 in T391, T398 in T394, T366 in T359, T395 in T313, T410 in T308).
- A builder FILES what it found, from its own tree (451 T289; the block's `FILE what you find` line, and this file's last paragraph): `make task-add` allots the
  id under the feature's lock from the reservations every worktree of the clone shares (451 T255), and `make carry` keeps both
  sides where two trees each appended a task's box and its plan stub. Measured 2026-11-26: four candidates left unfiled until the
  GM asked, and eight later plan review rounds, 23.0 minutes, rooted in a found-and-left item with no filed id - four reviews
  BLOCKED on it alone (T250, T305, T309, T285's fourth), two beside a real objection (T295, T316), and two sections edited after
  their CLEAR only to write the ids in (T251, T265) - each costing a filing by the session, an edit of the builder's section and
  another round (`dev/measurements/2026-11-26/plan-review-rounds/t308-results.md`). Do not write "do not file
  tasks" into a brief.
- A builder reads its plan sections by `make plan-section T=<task[,task]>` (plan.md, else plan-done.md; a section it names, by `T=<that id>` when needed), never by grep, sed or a Read over plan.md or plan-done.md: those carried 3.68 MB of builders' tool results in two days, and `CITED=1` (every section named, one level) printed 4.6 to 18 times the plain bytes on 2026-11-27, so take it only when most of them are needed (451 T499, T501).
- A builder's tree comes from `make builder-tree T=<task> [F=<feature>]` and nothing else: it prints the tree's path for the brief, `make land` releases it, and a hand `git worktree add` is refused (451 T285).
- A warm handout's pre-warm no longer cuts a build (451 T336): it finishes the crate in flight and yields between crates, so hand trees out with it on (no `L7R_PREWARM=0`); a builder's first run can wait for the rest of one crate (median 2.0 s, longest measured 82.7 s), and a link failure after a killed build (`undefined hidden symbol`) is healed once by `make rust-test` itself.

Why: of 97 builders briefed since 2026-11-24, a brief of 4 or more jobs handed off 52% of the time against 16-22% at 1-3 jobs;
4 or more files edited, 39-45% against 22% at three or fewer; a brief that began with a measurement, 46% against 25%. A one-turn edit by the
coordinator costs about half a small builder's tokens (0.3-0.4M against 0.65M); past 5 minutes or several files it costs about
1.5M, so that work goes to a builder (`dev/measurements/2026-11-25/talk-measures/`, `m1b.txt` and `m2b.txt`). The three-job and three-file
limits are GUESS knobs set where the measured rate steps up.

The block's second line, `Blocks:` (451 T243, the GM 2026-11-25: "a minute should count as blocking. When something else is
waiting on it to be done before it can be started"), is written on the dispatch's event-log line and read by `make task-time`:
the task named is the one this builder's time blocks (`BLOCKS="<feature> T<n>"`); with `none`, the command's default, the
builder's own task. A command takes the same clue as `L7R_BLOCKS=<feature>:T<n>` (or `none`) before its `make`.

A builder FILES what it finds and leaves, itself, from its tree (451 T289): `make task-add F=<feature> TITLE="<title, its paths and
figures>"` prints its id; it writes `Not fixed here: <why>. Filed as T<n>; lands before T<m>.` in its plan section's item and lists
it in the report's CANDIDATES as `filed: T<n>`. Scratch files carry the task id's prefix (`t<n>-`): builders share one scratchpad
(451 T271).

## Re-scoping a builder in flight (for the coordinating session)

A message sent to a builder with `SendMessage` reaches it. None was lost of the 220 located, 2026-11-12 to 11-27. It arrives
at one of two moments, and the result's first words say which. "Resuming agent" means the builder's turn had ended: it was
waiting on a background job, stopped by a usage limit, or done. It gets the message as a user turn within about a second.
"Message queued for delivery ... at its next tool round" means the builder is mid-turn. The message is attached after the
last tool result of its current round: median 6 s, and 1.5 s when the result says a running call was moved to the
background. An advisor call holds it until the call ends, up to about 4.5 minutes (all 10 delays over a minute). On
2026-11-26/27 builders took up 14 of 14: 12 at their next step or at the point the message named, one already doing it, one
already done. So do not resend a queued message: the result itself says, if the builder finishes first, "wait for that
notification before resending". Write a re-scope to survive an advisor call's few minutes: as a stop at the next boundary, or
as branches the builder picks from what it has built ("if job 2 is not yet built, do not start it"), never as "stop what you
are doing now". A withdrawal stops the builder's own edits, but not an agent or job it already launched in the background
(T381's plan review ran on after TaskStop), so name what to stop and expect a late notice from it. A message after the
builder's report resumes a finished builder, which the brief's "ends at its report" rule keeps for a question it asked.
Measured in `dev/measurements/2026-11-27/message-delivery/results.md` (451 T297).
