# Feature Specification: Guards That Correct Instead of Refusing

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=164-guards-that-correct`)

**Created**: 2026-08-30

**Status**: Draft - awaiting `spec-fidelity`

**Input**: [`request.md`](request.md), verbatim and unedited. That file is the authority for this
specification.

## The feature, in one sentence

Every refusal in this repository is audited against what it has actually cost, and the ones that can
be answered rather than refused are converted: four guards REWRITE the command into the one they were
already naming in their message, two teach for free BEFORE the block they would otherwise spend a
round trip on, two measured false positives stop firing - and the refusals that must stay refusals
are listed with the reason each one cannot be converted, so the question is settled rather than
reopened by the next session that asks it.

## Why this exists (the GM's words - `request.md` is the authority)

- *"What other commands fail with an error which could instead use this approach?"*
- *"are there places where a makefile command is refusing to do something but a tool could do a
  rewrite or return additional context or whatever?"*
- *"We have a lot of hooks and makefile checks which prevent inefficient tool usage, so are there
  more of them which could use this approach you've implemented?"*

The cost model is feature 162's, in the GM's own earlier words: *"bouncing back a command forces
another pass through the LLM engine, which also takes time."* The audit found **280 firings** across
eleven guards in six days - 280 round trips.

## What was measured before anything was specified

[`research.md`](research.md) carries the full table. The four numbers that drive this spec:

| | |
|---|---|
| total firings, 11 guards, 2026-08-24 to 2026-08-30 | **280** |
| `batching`, the loudest | **127** |
| `guard-file`, of which 28 were followed by the SAME edit again carrying the marker | **29** |
| `discard`, every one of them escaped in the next call | **5 of 5** |

And three harness capabilities, each PROVED against the installed version before being specified: a
Bash payload carries `run_in_background`; an Edit's `new_string` can be rewritten; a READ can carry
`additionalContext`.

## Scope, stated exactly

**IN scope**: `scripts/make-only-hooks.sh`, `no-poll-hooks.sh`, `pair-hooks.sh`,
`house-style-hooks.sh`, `guard-file-hooks.sh`, `batching-hooks.sh`, **`measure-hooks.sh`** (its
matcher only - FR-002), their companion suites, and the firing log those conversions record into.

**OUT of scope**: what any guard PROTECTS. No rule is relaxed by this feature: every command refused
today is either corrected into the compliant form or still refused. The diagram engine, and anything
about maps, are out of scope.

**The Makefile's own refusals are out of scope too, and `research.md` R6 enumerates all ten
one by one** rather than asserting a class - `spec-fidelity` round 1 was right that the first
draft's "prompts for a person to answer" is false of several. What the enumeration actually found,
stated as it found it:

- **seven** ask for a DECISION a substitution cannot supply: a written `REASON=`, an authorization
  typed at a terminal, a procedure to run first.
- **two** are not refusals a rewrite could apply to at all - `quick` over its budget REPORTS a run
  that already happened, and a gate failure is a test result.
- **one IS convertible**: `review-gate` refusing the number claim. It is out of scope here because
  `research.md` R4 records it as the GM's decision between three priced options, not because it
  cannot convert. That one row is the answer to the GM's own "is there a makefile command refusing
  something a tool could rewrite" - and the answer is yes, once, and here it is.

## Requirements

### FR-001 - `make-only` rewrites a bare pytest into the make target it already names

A command whose only fault is running one test FILE through bare pytest is rewritten to
`make test-file FILE=<path>` and allowed - that target being the one this project added for exactly
that question, *"re-run the file I just changed"*.

The rewrite applies ONLY when the shape is exactly rebuildable: one test path, and no flag the
target cannot honor (a `-k` filter, a coverage flag, a plugin flag, a second path). Anything else is
refused exactly as today.

**What is preserved, stated precisely.** `spec-fidelity` round 1 caught the first draft justifying
this with two claims that are false against the files it named. The invariant this guard exists for
is that **every test invocation goes through a make target** (feature 127), and the rewritten command
satisfies it exactly. It is NOT that the rewrite sets the coverage floors up: that target runs
`--no-cov`, exactly as the bare pytest would, and the floors are held by the gate targets, which
neither command runs. Two corrections are therefore owed inside this feature - the guard's
bare-pytest message gives coverage as its reason, which is not the true one, and it names only the
gate targets, never the one-file target, which has been missing from that message since 127.

### FR-002 - `no-poll` corrects instead of complaining, and stops firing on a mention

Two changes, and one thing deliberately NOT changed:

- A **mention is not an invocation**: this guard still matches substrings, so it refused the command
  that was writing this very specification, because the text quotes the shape the guard is about.
  That is the eighth false positive of this exact shape in the repository's history; the answer
  already exists - `_hookmatch.py`, which anchors a match to a command position and blanks heredoc
  bodies and quoted strings first - and CLAUDE.md's standing rule for guards is *"match INVOCATIONS
  not mentions"*. `no-poll` uses it. **So does `measure-hooks`**, whose own substring test fired on
  this feature's spec text while it was being written, spending a budget slot on prose; its stated
  reason for remaining a substring test (*"a real command parse is not worth the false-negative
  risk"*) predates `_hookmatch.py` and is stale now that the parse exists and is proven.
- A correction rather than a complaint: a `pgrep -f` or `pkill -f` carrying a literal pattern is
  rewritten to the bracket form the refusal already recommends in prose.

**NOT changed here, and the reason matters.** The guard also refuses a `sleep` loop when
`run_in_background` is TRUE - the harness's own documented shape for a single completion
notification, and the only way to wait on a run detached with `setsid --fork`. It fired on exactly
that twice on 2026-08-30, and the first draft of this spec permitted it. That is a change to **what
the guard forbids**, not a rewrite and not added context, so by this feature's own standard - the one
FR-008 applies to `discard` - a session does not make it on its own judgment. It goes to the GM with
its measurement in `research.md` R5; `POLL_OK` remains the answer meanwhile.

### FR-003 - `pair` rewrites the gate into the paired command

`make done` with a review owed and none pending becomes **`make verify`** - the command feature 151
created for exactly this case - carrying the line that tells the session to dispatch the
`settlement-review` in the same turn. The pairing rule is unchanged: what was refused now happens
correctly instead of not happening at all.

### FR-004 - `house-style` corrects the text instead of refusing the edit

An em-dash or en-dash becomes a hyphen, and a British spelling on the project's own list becomes its
American form, IN the edit payload, with one line saying what was corrected. Every word on the guard's own detection list has exactly one American form in
`CLAUDE.md`'s table, INCLUDING the British verb spelling of "practice", which the first draft carved
out as a judgment call: the project's rule gives one spelling for both the noun and the verb, so the
substitution is as mechanical as the rest (`spec-fidelity` round 2). An edit still violating house
style after the corrections is refused exactly as today.

**THE GM'S OWN WRITING IS NEVER CORRECTED, and today's exemption does not cover it**
(`spec-fidelity` round 1). The hook exempts by path - `/host-l7r-repo`, `l7r.md`, `gm-request.md` -
and strips SOURCE blocks from the body. But this repository records the GM's verbatim words in
`specs/NNN-*/request.md`, the file that is the authority for every spec including this one, and that
name is not on the list. Under a refusal that is survivable: a person sees the block and decides.
Under a silent correction it would mean **mechanically altering the GM's own words**, which Principle
V forbids outright. So the exemption is extended to a `request.md` under `specs/` BEFORE any
correction is applied, and any file recording the GM speaking stays on the refusal path rather than
the correction path.

### FR-005 - `guard-file` teaches when the file is OPENED, not when the edit is refused

Reading a guard file returns the one line saying an edit here needs `GUARD_EDIT_OK` with a reason.
The refusal stays as the backstop; what changes is that the session learns before it writes the edit
- which is what 28 of the 29 recorded firings had to be told the expensive way.

### FR-006 - `batching` warns one turn before it blocks

At one turn below its threshold the batching guard attaches its playbook as free context instead of
waiting to spend a round trip on it. The block, its rolling window, its backoff and its escape are
unchanged.

### FR-007 - every conversion is recorded

Each converted guard logs what it did (`rewrote`, `reminded`, `blocked`) through feature 162's
`guard_log`, so the next audit of this question is a query rather than a replay of transcripts. No
guard's own test suite may write into the real log (feature 162 T16).

### FR-008 - the refusals that must stay refusals are listed, with the reason

`repo-safety`, `source-block`, `readme`, `discard`, `clone-sync`, `no-branch`, `measure` and
`gate`'s `-k` subset rule keep their refusals, and `research.md` R3 records why for each: the action is
destructive or irreversible, or the refusal is itself the content, or a substitution cannot know
which of two outcomes was wanted. This list is part of the deliverable - an unlisted guard would
otherwise be re-examined from scratch by the next session asking the GM's question.

`measure` needs one line of its own, because "not converted" is not the whole truth about it: its
BLOCK stays exactly as feature 162 left it - that block is the point - but its MATCHER moves to
`_hookmatch.py` under FR-002, so it stops counting a mention as an invocation. The stale limitation
comment in that file (*"a real command parse is not worth the false-negative risk"*) is replaced
rather than left contradicting the code, since the parse now exists and is proven.

**One finding is escalated rather than fixed**: `discard` was escaped in **5 of 5** firings. Either
it fires on a shape it should not, or five sessions each knowingly discarded uncommitted work. A
guard about data loss is not retuned on a session's own judgment, so it goes to the GM.

## Success Criteria

- **SC-001**: a bare pytest run of one test file runs as `make test-file FILE=<that file>`; the same command carrying a `-k` filter is still refused.
- **SC-002**: an edit to a `specs/*/request.md` - the GM's verbatim words - is never mechanically corrected; it is refused if it violates house style, exactly as today.
- **SC-003**: a `pgrep -f` with a literal pattern runs as the bracket form.
- **SC-004**: `make done` with a review owed runs as `make verify`, and the session is told to dispatch the review in the same turn.
- **SC-005**: an edit containing an em-dash or a listed British spelling is applied with the American, hyphenated text; the GM's SOURCE blocks are untouched.
- **SC-006**: reading a guard file returns the `GUARD_EDIT_OK` line; reading an ordinary file returns nothing.
- **SC-007**: the batching guard emits its playbook one turn before it would block.
- **SC-008**: no guard refuses or counts a command that merely MENTIONS the shape it guards - proved for `no-poll` with the command that wrote this file, and for `measure-hooks` with a command whose text names a gate target.
- **SC-009**: every companion suite is green, each new assertion is proved to FIRE by removing the code it guards, and no suite writes fixture events into the real firing log.

## Decisions Recorded

| decision | class | where |
|---|---|---|
| convert four guards to rewrites | measured (280 firings; each is a round trip) | FR-001..FR-004, `research.md` R1/R3 |
| teach at READ time for guard files | measured (28 of 29 firings were the same edit again) | FR-005, R2 |
| warn one turn before the batching block | measured (127 firings, the loudest guard) | FR-006, R1 |
| a backgrounded busy-wait is NOT permitted here | it changes what the guard forbids, so it goes to the GM like `discard` | FR-002, `research.md` R5 |
| the GM's verbatim `request.md` is never mechanically corrected | Principle V; today's exemption does not cover that filename | FR-004 |
| the Makefile's refusals are enumerated, not dismissed as a class | `spec-fidelity` round 1 | Scope, `research.md` R6 |
| a mention is not an invocation, for `no-poll` too | measured false positive, on this feature's own spec | FR-002, R3 |
| eight guards stay refusals | recorded limitation, with the reason for each | FR-008, R3 |
| `discard`'s 5-of-5 escape rate goes to the GM | escalation, not a fix | FR-008 |
