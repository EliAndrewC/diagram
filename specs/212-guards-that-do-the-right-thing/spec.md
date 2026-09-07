# Feature 212 - Guards That Do The Right Thing

**Status**: DRAFT 2026-09-07, awaiting `spec-fidelity`. The GM's request is [`request.md`](request.md)
and it is the authority; where this document and that one differ, that one is right. The census
behind every number is [`research.md`](research.md).

## The feature, in one sentence

Where a guard refuses a command and its own refusal names the command that should have been run,
the guard runs that command instead and tells the session what it did - for the targeted pytest run,
the gate without a review beside it, the engine entry point a make target wraps, the foreground
file-watching wait, and the edit in a clone that fell behind main mid-turn - and an audit of every
other refusal in the record says, guard by guard, why the rest stay refusals.

## Why this exists (the GM's words)

*"if A Claude code session is using Pytest to run a targeted set of tests, such as targeting a
specific module or even a specific test case, then rather than failing, that does seem like
something where we could modify the command so that instead of running Pytest directly, we
translate it into the make target which should have been run, and then we pass back additional
hook context to the session explaining what we did and instructing the session to do the correct
thing in the future."* And of the gate: *"anytime we are able to say that a command was run
incorrectly and then supply the correct thing to do, then it is at least possible that what we
should do is simply do the correct thing and then inform the session through hook context that we
have done it."* And the audit: *"auditing our other hooks to see whether there are other places
where we are blocking a command from being run when we could instead simply run the correct
command and output hook context explaining what we did ... I do not expect it to be able to work or
be reliable in every case. So I imagine that there will always be some hook commands which simply
fail. Determining this would be the point of the audit, and then part of the feature is acting upon
the results of that audit if there are any other easy wins."*

## What was measured before specifying (research R1-R2)

- 1,143 refusals recovered from the transcripts, 2026-08-25 to 2026-09-07, every one with its
  command. Fourteen guards.
- The bare-pytest refusal fired 20 times; 10 were a targeted run of the kind the GM described, and
  feature 164's rewrite converted none of them, because each carried `2>&1 | tail` after the
  pytest segment.
- The gate-without-review refusal fired on 11 real gate invocations; feature 164's rewrite to
  `make verify` fired once, because `make maps` and a detached `make done` are not shapes `verify`
  takes.
- The engine-entry-point refusal fired 29 times; the Makefile wraps four of the modules run.
- The busy-wait refusal fired on about ten foreground loops that are the file-watching wait the GM
  permitted in feature 165, issued without `run_in_background`.
- The stale-clone refusal fired 13 times, every time mid-turn after main moved under a clone the
  prompt hook had synced at the turn's start.

## Scope, stated exactly

**IN**: the five conversions (FR-001 to FR-005), each recording what it did (FR-006); the `K=`
argument of `make test-file` and the gate guard's view of it (FR-001); the corpus as a regression
fixture (FR-007); the audit of every guard's refusals with a verdict each (FR-008); the documents
that describe the guards (FR-009).

**OUT**: any refusal the audit classes as staying a refusal - batching, guard-file, measure,
readme, discard, source-block, no-branch, repo-safety, the `-k`-subset block, the guard-write,
inline-override and foreign-makefile verdicts of make-only, the remaining busy-wait shapes, and
clone-sync's name-routing and live-claim refusals: their verdicts and messages are untouched;
`make verify` as a target (it stays, unchanged); the guard log's entry shape (feature 204's); any
engine code.

## Requirements

### FR-001 - a targeted pytest run becomes `make test-file`

A pytest invoked at a command position (`pytest`, `python3 -m pytest`, with an env-assignment or
`timeout` prefix, inside `( cd <dir> && ... )` or after `cd <dir>;`) is REWRITTEN to
`make test-file FILE=<paths> [K=<expr>]` when everything on the pytest segment is one of:

- one or more test paths: a `test_*.py` file, a directory, or a node id (`file::name`);
- `-k <expr>` / `-k=<expr>`, quoted or bare, once;
- a flag the target already supplies or that only shapes output: `-q`, `-qq`, `--quiet`, `-x`,
  `--exitfirst`, `--no-cov`, `--no-header`, `-n <workers>`, `--dist <mode>`, `-v`, `-vv`,
  `--tb=<style>`, `--color=<mode>`, `-p no:<plugin>`.

What follows the segment - a redirect (`2>&1`, `> file`), a pipeline (`| tail -8`), a chain (`&&`,
`;`, a newline) and the rest of the command - is kept verbatim after the make command. The
segment's own prefix (`cd`, `(`, env assignments) is kept in front of it.

Anything else on the segment keeps the refusal: `-m`, `--deselect`, `--co`/`--collect-only`,
`--cov*`, `-p <plugin>` (a load, not a `no:`), `--lf`/`--ff`, `-s`, `--pdb`, `-W`, `-o`, a
`--timeout`, a `--durations`, a path that is not a test path, an unknown flag. The refusal NAMES the
token that stopped the rewrite, so the session knows what to change rather than guessing.

`make test-file` gains `K=<expr>`: when set, the recipe adds `-k "$(K)"`. The help line says so.

`gate-hooks` records a subset when the command invokes `test-file` with `K=` or with a `::` node
id in `FILE=`, exactly as it records a bare `pytest ... -k` today, and clears it on a `test-file`
without either. Acceptance: `scripts/test-gate-hooks.sh` proves both directions.

The `additionalContext` says what was rewritten, that everything here goes through make so an
expensive run can ask whether the cheap one would do, and that `make test-file FILE=... K=...` is
the form to use next time. Acceptance: every corpus row labeled `rewrite` converts to exactly the
recorded target command; every row labeled `refuse` is refused with its stopping token named.

### FR-002 - an engine entry point a make target wraps becomes that target

`python3 -m l7r.diagram.<module> <args>` at a command position is REWRITTEN to `make <target>
<VAR=value ...>` when the skill Makefile has exactly one target whose recipe is a single line of the
form `$(RUN).<module> <recipe-args>` (or `@$(RUN)...`, or `$(SWITCH) <word>` for `l7r.diagram.switches`)
and the command's arguments can be laid onto `<recipe-args>` word for word: a literal word matches
itself; `$(ARGS)` takes everything remaining as `ARGS="..."`; `$(or $(VAR),<default>)` takes one
word as `VAR=<word>` (or nothing, when the next word is absent); `$(if $(VAR),<flag>,)` takes
`<flag>` as `VAR=1` when present. The derivation reads the Makefile at hook time; it is never a
table kept by hand. A module with no such target, a recipe with more than one line or a
`$(REF_FIRST)` guard before it, or arguments the recipe cannot carry, keeps the refusal, and the
refusal lists the targets that do wrap engine modules.

The rest of the command (pipelines, chains, prefix) is kept as in FR-001. Acceptance: `python3 -m
l7r.diagram.ci engine-key worktree` becomes `make engine-key REF=worktree`; `python3 -m
l7r.diagram.ci status` becomes `make ci-status`; `python3 -m l7r.diagram.tools.scatter_audit
pool/hamlets/x` is refused.

### FR-003 - the gate runs, the pairing is recorded, the session is told to dispatch

When a Bash command invokes the gate (`make done`, `make maps`, any flags, variables, `FULL=1`,
`nohup`/`setsid`/`timeout` prefixes, a redirect or `&` after it) and no settlement-review is
pending in the session and none is recorded for this engine content, the guard no longer refuses
and no longer rewrites. It:

1. records the engine key as the pairing's `gate_key` (what `make verify` does);
2. lets the command run UNCHANGED;
3. returns `additionalContext` carrying what `make verify` prints: the engine key, the maps whose
   manifest changed in the last commit (or "the delta" when none), **DISPATCH NOW, in the same turn:
   settlement-review over <maps>**, and the `PAIR_OK="<why>"` form for a one-sided case.

The Stop hook is unchanged: a turn that ends with the gate green on this content and no review
dispatched, recorded or waived is refused once. The settlement-review-without-gate refusal is
unchanged. The `make verify` rewrite (`_hm_make.py as_paired`) is retired with its cases; `make
verify` itself stays as a target. Acceptance: `scripts/test-pair-hooks.sh` proves a plain `make
done`, a `make maps SCOPE=all`, a `setsid nohup make done > log 2>&1 &` and a `make done FULL=1`
each run with the context and the recorded key; the Stop refusal still fires afterward when nothing
was dispatched.

### FR-004 - a foreground file-watching wait is backgrounded

When the busy-wait branch of `no-poll` refuses a loop, and that loop would satisfy
`file_watching_wait` if `run_in_background` were true (the same three condition forms, the same
exclusions - nothing else about the boundary moves), the guard instead returns the tool input with
`run_in_background: true` and an `additionalContext` saying the wait was backgrounded, that its
output arrives as a completion notification, that the turn is free meanwhile, and that a pattern
which may never appear needs a bound. Every other busy-wait shape keeps the refusal. Acceptance:
`scripts/test-no-poll-hooks.sh` proves the foreground `until grep -q x /tmp/a.log; do sleep 5;
done; tail /tmp/a.log` is backgrounded, and `until curl -sf https://h/x; do sleep 5; done` and
`until pgrep -f make; do sleep 5; done` are still refused.

### FR-005 - a clean clone that fell behind is synced, then the edit proceeds

When `clone-sync`'s pretool branch finds a clean clone whose HEAD is behind main (and not the
stray-mirror-commit case, which stays a refusal), it runs `scripts/sync-with-main.sh sync-in` in
that clone under a 25 s bound. If the clone is then no longer behind, the edit proceeds with an
`additionalContext` saying main was merged in mid-turn and that a file the merge changed must be
re-read. If the sync fails, times out or leaves the clone behind, the refusal stands with its
message. Acceptance: `scripts/test-clone-sync-hooks.sh` proves a stale clean clone is synced and the
edit allowed, and that a sync that cannot fast-forward (a diverged clone in the fixture) is still
refused.

### FR-006 - every new branch records, with a rule

Each conversion records to the guard log through `guard_log` with a rule slug: `make-only rewrote
targeted-pytest`, `make-only rewrote entry-point`, `pair permitted review-owed`, `no-poll rewrote
backgrounded-file-wait`, `clone-sync permitted synced-in`. `tests/tooling/test_guard_firing_log.py`
gains a case for each. `make audit` needs no change: it already sums by event and rule.

### FR-007 - the corpus is a fixture

`scripts/fixtures/guard-refusals-2026-09.json` holds every make-only, pair, no-poll and clone-sync
refusal from R1 with its command, guard and the verdict this feature expects (`rewrite` with the
expected command, `permit`, or `refuse`). `tests/tooling/test_guard_corpus.py` replays the make-only
and no-poll rows through `_hm_make.py` / `_hm_shape.py` and fails on any verdict that moved. Pair and
clone-sync rows are replayed by their shell suites, which own the state those decisions read.

### FR-008 - the audit is written down, guard by guard

`research.md` R1-R2 classify every guard's refusals in the record: what they were for, how many, and
for each guard either the conversion this feature makes or why the refusal stays (the fix is a
decision or a reason only the session has; the action is destructive; the block is the point). A
guard whose verdict changed from feature 164's classification (pair, clone-sync) says what evidence
changed it.

### FR-009 - the documents follow

CLAUDE.md's enforcement table rows for make-only, pair, no-poll and clone-sync; the "A GUARD THAT
CAN PRODUCE THE COMPLIANT COMMAND SHOULD PRODUCE IT" paragraph gains the five; `docs/efficiency-tooling.md`
where it lists the rewrites; each guard's header comment at the point of change; the `make test-file`
help line. Feature 164's research is not edited (it is the record of what was decided then).

## Decisions Recorded

- **D1 - the pair guard permits rather than rewrites.** A rewrite to `make verify` can carry
  neither `maps` nor a detached run nor `FULL=1`, and those are 11 of the 11 real refusals. The
  bookkeeping `verify` does is two writes and a printf, which the hook does itself for any shape.
  The enforcement point moves from before the gate to the Stop hook, which is where the 164 rewrite
  already left it.
- **D2 - the entry-point table is derived from the Makefile.** A hand table names targets that get
  renamed (feature 193 retired nine) and misses ones that get added; a recipe parse cannot.
- **D3 - `K=` on `make test-file`, not a new target.** One target with an optional filter keeps the
  "which target does the job" question answerable in one line of help, and `gate-hooks` already
  knows the target.
- **D4 - the file-wait boundary does not move.** FR-004 converts only what feature 165 already
  permits; the GM declined the wider "whenever backgrounded" rule and this feature does not reopen it.
- **D5 - the sync in FR-005 is bounded and idempotent.** 25 s under a 30 s hook timeout; a clean
  clone's `sync-in` is a fast-forward; a failure is the old refusal, never a half-merged tree left
  for the session to find.
- **D6 - what stays a refusal.** Named in R1 with the reason each; the two families are "the missing
  thing is a reason or a decision" and "the action is destructive or the block is the point".
