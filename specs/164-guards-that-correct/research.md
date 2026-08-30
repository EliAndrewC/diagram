# Research: which refusals could correct instead

Same method as feature 162, run over every guard rather than two:
`specs/162-guard-block-economics/measure/replay.py` finds each hook refusal in this project's
transcripts by the script path the harness prints, and reads the next tool call in the same
transcript. 280 firings, 2026-08-24 to 2026-08-30, 29 transcripts.

## R1 - what every guard has actually cost

| guard | firings | what happened in the very next call |
|---|---|---|
| `batching` | **127** | did something else 117, escaped 6, nothing 4 |
| `gate` | 36 | **escaped 24**, something else 11, nothing 1 |
| `no-poll` | 32 | something else 18, **escaped 13** |
| `guard-file` | 29 | something else 28 (each one the same edit again, with the marker), escaped 1 |
| `make-only` | 25 | something else 18, escaped 7 |
| `pair` | 13 | **escaped 7**, nothing 3, something else 3 |
| `measure` | 7 | escaped 4, something else 3 |
| `discard` | 5 | **escaped 5 - every single firing** |
| `house-style` | 3 | something else 3 (the same edit again, hand-corrected) |
| `clone-sync` | 2 | something else 2 |
| `readme` | 1 | escaped 1 |

Every firing is one model round trip, which the GM prices in their own words: *"bouncing back a
command forces another pass through the LLM engine, which also takes time."* 280 firings is 280 of
them. `gate`'s 36 are mostly the quick+done refusal that feature 162 retired.

## R2 - what the harness allows, PROVED before anything was specified

Feature 162 established that a `PreToolUse` hook may return `updatedInput` (rewrite the command) and
`additionalContext` (speak to the model), both at exit 0, both free. Three further questions decide
what can be converted here, and all three were verified against the installed harness (2.1.251) with
a throwaway settings file and a `claude -p` run, not read off documentation:

| question | answer |
|---|---|
| does a Bash payload carry `run_in_background`? | **yes** - `{"command", "description", "run_in_background"}` |
| can an EDIT's `new_string` be rewritten? | **yes** - the probe rewrote `colour` -> `color` and the file on disk carried the correction |
| can a READ carry `additionalContext`? | **yes** - the model quoted it back verbatim |

That third one is the interesting one: a guard can teach when a file is OPENED, which is before the
edit that would have been refused.

## R3 - the classification

**REWRITE** (the guard already knows the right command - it names it in the refusal):

- `make-only`: a bare `pytest <one file>` becomes `make test-file FILE=<file>`. The guard's whole
  message is "run this instead", and for this shape the substitution is exact.
- `no-poll`: `pgrep -f <literal>` becomes `pgrep -f '[<l]iteral'` - the bracket trick the refusal
  already recommends in prose.
- `pair`: `make done` with a review owed becomes `make verify`, which is the paired command the guard
  exists to enforce, plus the line telling the session to dispatch the review in the same turn.
- `house-style`: an em-dash becomes a hyphen and a listed British spelling becomes the American one,
  in the edit payload. Mechanical, unambiguous, and it is exactly what the session does by hand.

**TEACH, FREE, BEFORE THE BLOCK** (the block cannot be avoided but the lesson can arrive earlier):

- `guard-file`: 29 firings, 28 of them followed by the same edit again carrying the marker. The
  lesson can ride on the READ of a guard file, so the marker is in the first edit.
- `batching`: 127 firings. A reminder at one turn below the threshold costs nothing.

**A MEASURED FALSE POSITIVE, worth its own line**: `no-poll` blocks an `until ...; do sleep; done`
loop even when `run_in_background` is TRUE - which is the harness's own documented pattern for a
single completion notification, and the only way to wait on a run detached with `setsid --fork`
(feature 162's `dev/lessons.md` entry). It fired on exactly that twice on 2026-08-30.

**MUST STAY A REFUSAL**, and the reason is the same in each case - the action is destructive,
irreversible, or the refusal IS the content:

- `repo-safety` (force push, history rewrite): no escape exists on purpose.
- `source-block` (the GM's writing): only the GM may change it.
- `readme` (a README is the GM's to write): the same.
- `discard` (a checkout that would destroy uncommitted work): a rewrite cannot know which of two
  versions is wanted. **But its escape rate is 5 of 5** - every firing in the record was overridden
  in the next call, which is a question for the GM rather than a fix: either the guard is firing on
  a shape it should not, or five sessions each knowingly discarded work.
- `clone-sync`, `no-branch`: the correct action is a procedure, not a command substitution.
- `measure` (feature 162), `gate`'s `-k` subset rule: the block is the point, and 162 already moved
  measure's teaching to the first run.

**Sources:** this repository's transcripts, `dev/run-log/`, and the harness probes recorded above.
No external source is cited; no claim here is about the world outside this repository.

## R4 - the number claim cannot land, because the review gate refuses it

Found by this feature's predecessor, at a cost: `specs/162` began life as `specs/161`.

`CLAUDE.md`'s numbering protocol says the number is claimed by pushing the new `specs/NNN-slug/`
**the moment `spec.md` is written** - *"the locked pull+push makes the claim atomic"* - and the
feature-in-progress guard explicitly permits that one push while every task is still open. But
`scripts/review-gate.sh` refuses any push whose delta touches a `spec.md` carrying no FAITHFUL
verdict, and a spec written one minute ago has not been reviewed yet. So the claim cannot be made
when the protocol says to make it.

Measured consequence, 2026-08-30: feature 162's claim was refused on those grounds, another session
claimed 161 in the interval, and the work had to be renumbered - 67 files swept, 51 of them wrongly
(the sweep rewrote the OTHER feature's references and had to be reverted file by file).

The two rules are each correct and they contradict each other. The resolution is the GM's to make,
so it is recorded here rather than fixed:

- **Option A** - `review-gate` permits a push whose delta is EXACTLY one new `specs/NNN-slug/`
  directory with no other file, which is the same carve-out the feature-in-progress guard already
  makes for the claim. Cheap, and the reviewed-before-implementation property is untouched, because
  no implementation can be in a specs-only delta.
- **Option B** - the numbering protocol stops claiming before review, and a session takes the next
  free number at PUSH time instead. Removes the race differently, but every artifact written during
  the feature carries a number that may change under it, which is what the sweep above cost.
- **Option C** - leave it. The collision is rare and the renumber is mechanical.

**It is not rare.** It happened TWICE in one session: this feature was written as 163, and while its
spec sat in review a second session claimed `specs/163-checks-into-the-placer`, so it is 164. Two
collisions in one day, both caused by a claim that could not be pushed when the protocol said to
push it.

**Sources:** `CLAUDE.md` (the numbering protocol and the guard table), `scripts/review-gate.sh`,
`scripts/sync-with-main.sh`, and this session's own transcript.

## R5 - a question for the GM: a backgrounded wait is refused as a busy-wait

`no-poll-hooks.sh` refuses any loop containing `sleep`. That is right for a FOREGROUND loop, which
burns wall clock at model-turn cost. It also fires when the command is run with
`run_in_background: true`, and there the reasoning does not hold: the harness's own guidance names
`until <condition>; do sleep; done` in a background job as the correct shape for a single completion
notification, and it is the only way to wait on a run detached with `setsid --fork` - which feature
162's `dev/lessons.md` entry establishes as the way to detach a long `make` run at all.

Measured: it fired on exactly that twice on 2026-08-30, in this session, while backgrounding a gate.
Both times `POLL_OK` cleared it and the wait was correct.

**Not fixed here, deliberately.** Permitting it is a change to what the guard FORBIDS, not a rewrite
and not added context, so it is outside the approach the GM asked about - and this feature's own
standard (FR-008, and the `discard` escalation) is that a session does not retune a guard's rule on
its own judgment. The options:

- **A** - permit a sleep loop when `run_in_background` is true. One line, and the hook can see the
  flag (proved in R2). Risk: a session could set the flag purely to get past the guard, which is the
  tier-2 workaround shape this project has been bitten by before.
- **B** - leave it, and keep using `POLL_OK` with a note. Costs a round trip only when a session
  forgets, which is what happened twice today.
- **C** - narrow it: permit the loop when it is backgrounded AND its condition names a file, which
  is the detached-run shape, and keep refusing every other backgrounded loop.

**Sources:** this session's transcript; `scripts/no-poll-hooks.sh`; the harness's own tool guidance.

## R6 - the Makefile's own refusals, one by one

The GM's question names *"makefile checks"* explicitly, so they are enumerated rather than dismissed
as a class (`spec-fidelity` round 1 was right that "prompts for a person" is false of several).

| refusal | what it asks for | convertible? |
|---|---|---|
| `scope-lock` / `scope-unlock` / `ci-off` / `ci-on` without `REASON=` | a written reason someone will read | **no** - the reason IS the content; a substitution cannot supply it |
| `switches.py`: remote OFF refusing a dispatch | a decision to spend money, already made and recorded | **no** - the compliant alternative is "do not run it", which is not a command |
| `switches.py`: scope LOCKED refusing a sweep | the same, for wall clock | **no** - and the refusal already names `make reference`, the cheap question |
| `bypass-audit` (a FULL run) | an authorization typed at a terminal | **no** - by design; a hook answering it would be the tier-2 override with extra steps |
| `ci-image` | the same, for money | **no** - same reason |
| `perf-gate` with no opening bookend | a procedure to run first (a detached worktree, two commands) | **no** - it prints the exact commands; a rewrite would have to run them, which is not a substitution |
| `quick` over `QUICK_BUDGET` | attention: something slow ran that should not have | **no** - the run already happened; there is nothing to rewrite, and it already names `make durations` |
| `make done` gate failure | fixes | **no** - it is a test result, not a refusal |
| the main-tree write guard | work moved into a clone | **no** - a procedure, not a command |
| `review-gate` refusing the number claim | nothing - it is a false positive on a claim-only push | **YES**, and it is R4's question for the GM |

So, of the ten: **seven** ask for a DECISION - a written reason, an authorization, a procedure - and
a decision is the one thing a rewrite cannot supply. **Two** are not refusals a rewrite could apply
to at all: the budget check REPORTS a run that already finished, and a gate failure is a test result.
**One** is convertible, and it is already recorded as a question for the GM rather than a change.

**Sources:** `.claude/skills/diagram/Makefile`, `l7r/diagram/switches.py`, `scripts/review-gate.sh`.

## R7 - a mention is not an invocation, and three guards still cannot tell

The class this repository has been bitten by eight times before, met three more times WHILE writing
this feature - each one costing a round trip, each on a document whose subject is the guard that
fired:

| guard | what it fired on | cost |
|---|---|---|
| `no-poll` | the command writing `spec.md`, whose text quotes the shape the guard forbids | one round trip |
| `measure-hooks` | a command whose prose names a gate target; it spent a budget slot on text | one budget slot |
| `house-style` | `plan.md` NAMING the one British word the correction table deliberately excludes | one round trip |

`gate-hooks` stopped making this mistake on 2026-08-29 by asking `_hookmatch.py`, which anchors a
match to a command position. Two of the three above are the same fix. The third is different in kind
and worth stating: `house-style` reads PROSE, not commands, so command-position anchoring does not
apply - what distinguishes a word being USED from a word being NAMED there is the backtick code span
this repository's own prose already uses for exactly that purpose.

Its exemption list has the same gap from the other side: it exempts the files that must quote the
RULE (`CLAUDE.md`, the constitution, the style doc, the hook and its test) but not a spec or plan
DISCUSSING it, which is the document this feature had to write.

**Sources:** this session's transcript; `scripts/_hookmatch.py`; `scripts/house-style-hooks.sh`.
