# Feature 212 - Guards That Do The Right Thing

**Status**: **APPROVED** 2026-09-07 - `spec-fidelity` round 3 returned FAITHFUL. Round 1 required hook context on FR-002, the `make verify` rewrite kept for the plain gate with the serialization of a foreground gate stated (D7), and the audit per refusal branch; round 2 required FR-004's normalization stated in full with the substitution test on the raw condition. The GM's request is [`request.md`](request.md)
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
- The bare-pytest refusal fired 20 times; 8 were a targeted run of the kind the GM described, and
  feature 164's rewrite converted none of them, because each carried `2>&1 | tail` after the
  pytest segment.
- The gate-without-review refusal fired on 11 real gate invocations; feature 164's rewrite to
  `make verify` fired once, because `make maps` and a detached `make done` are not shapes `verify`
  takes.
- The engine-entry-point refusal fired 29 times; the Makefile wraps four of the modules run.
- The busy-wait refusal fired on eight real log-watching waits of the shape the GM permitted in
  feature 165: seven of them BACKGROUNDED and refused anyway by the qualifier's raw reading of the
  condition, one issued in the foreground.
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

The rest of the command (pipelines, chains, prefix) is kept as in FR-001. On a rewrite the guard
returns `additionalContext` naming the module that was rewritten, the make target it became with
its variable assignments, and that an engine entry point is invoked through its make target in
future (`make help` lists them). Acceptance: `python3 -m l7r.diagram.ci engine-key worktree`
becomes `make engine-key REF=worktree` and the context names both; `python3 -m l7r.diagram.ci
status` becomes `make ci-status`; `python3 -m l7r.diagram.tools.scatter_audit pool/hamlets/x` is
refused.

### FR-003 - the gate runs, the pairing is recorded, the session is told to dispatch

When a Bash command invokes the gate (`make done`, `make maps`, any flags, variables, `FULL=1`,
`nohup`/`setsid`/`timeout` prefixes, a redirect or `&` after it) and no settlement-review is
pending in the session and none is recorded for this engine content, the guard no longer refuses.

- **The exact shape `make verify` reproduces** - a `make done` with no other goal, variable, flag,
  prefix or redirect - is REWRITTEN to `make verify` as feature 164 already does: `verify` starts
  the gate detached and returns at once, so the DISPATCH NOW line reaches the session while the
  gate runs and the two overlap (feature 151's property, kept).
- **Every other shape** is RECORDED AND PERMITTED. The guard records the engine key as the pairing's
  `gate_key` (what `make verify` does), lets the command run UNCHANGED, and returns
  `additionalContext` carrying what `make verify` prints: the engine key, the maps whose manifest
  changed in the last commit (or "the delta" when none), **DISPATCH NOW, in the same turn:
  settlement-review over <maps>**, and the `PAIR_OK="<why>"` form for a one-sided case. When the
  command is DETACHED or backgrounded (`nohup`, `setsid`, a trailing `&`, `run_in_background`) it
  returns at once and the review overlaps the gate exactly as under `verify`. When it is a
  FOREGROUND run (`make maps 2>&1 | tail -30`) the context reaches the session only when the
  command returns, and the context SAYS so: the review will start after this gate, adding its
  runtime to the wall clock; to overlap them, detach the gate (`setsid nohup ... > log 2>&1 &`, the
  form `make maps` needs - `run_in_background` reaps it) or use `make verify`. D7 records this.

The Stop hook is unchanged: a turn that ends with the gate green on this content and no review
dispatched, recorded or waived is refused once. The settlement-review-without-gate refusal is
unchanged. `make verify` stays as a target. Acceptance: `scripts/test-pair-hooks.sh` proves a
plain `make done` is still rewritten to `make verify`; a `make maps SCOPE=all`, a `setsid nohup
make done > log 2>&1 &` and a `make done FULL=1` each run unchanged with the context and the
recorded key, the detached one told it overlaps and the foreground one told it serializes; the
Stop refusal still fires afterward when nothing was dispatched.

### FR-004 - the file-watching wait qualifies as written, and a foreground one is backgrounded

Two parts. The first is a defect fixed where it was found (Principle XIV): of the eight real
backgrounded log-watching waits in the record, `file_watching_wait` refused SEVEN, every one the
shape the GM permitted in feature 165 - `until grep -qE "gate green|GATE FAILED" $S/done.log;
do sleep 5; done` - because it reads the loop condition RAW: a `|` inside the quoted regex counts
as a pipeline, `2>/dev/null` counts as an output redirection, and `[ -s f ] && grep -q x f` is not
one of its three forms. The condition is normalized in exactly these steps, in this order, and
no other:

1. the command-substitution test (`$(`, a backtick) runs on the RAW condition first, so a
   substitution inside a double-quoted operand still disqualifies - `"$(curl ...)"` executes;
2. inside each quoted operand the characters `|`, `<`, `>`, `;` and `&` are dropped and the rest
   of the quoted text is KEPT (a regex loses its alternation bar; a quoted path stays a path);
3. a `2>/dev/null` is REMOVED from the condition (stderr discarded writes no file, and the grep
   form needs the path operand to be the last thing);
4. the pipeline and output-redirection tests run on the result;
5. the condition is split on `&&`/`||`, and EVERY part must be one of the three forms; the grep
   form's path operand may carry a shell-variable prefix (`$S/done.log`, `${LOG}`), which is how
   the record writes it.

Nothing wider: `> file`, `$(...)` anywhere, a real pipeline, a `curl`, a `pgrep`, a process test
all still fail it, so the "permit whenever backgrounded" rule the GM declined stays declined - and
step 5 is TIGHTER than today, where `[ -f x ] && curl -sf https://h` qualified because the whole
condition was searched for one form.

The second: when the busy-wait branch would refuse a FOREGROUND loop that satisfies the (fixed)
`file_watching_wait` with `run_in_background` forced true, the guard instead returns the tool input
with `run_in_background: true` and an `additionalContext` saying the wait was backgrounded, that
its output arrives as a completion notification, that the turn is free meanwhile, and that a
pattern which may never appear needs a bound. Every other busy-wait shape keeps the refusal.

Acceptance: `scripts/test-no-poll-hooks.sh` proves the seven corpus shapes are permitted when
backgrounded (a `|` inside the quoted pattern, a `$S/done.log` operand, `2>/dev/null`, `[ -s f ]
&& grep`); the foreground `until grep -q x /tmp/a.log; do sleep 5; done; tail /tmp/a.log` is
backgrounded; and `until curl -sf https://h/x; do sleep 5; done`, `until pgrep -f make; do sleep
5; done`, `until grep -q x f > /tmp/out; do sleep 5; done`, `until grep -q "$(curl -s
https://h/x)" /tmp/f; do sleep 5; done` and `until [ -f x ] && curl -sf https://h; do sleep 5;
done` are refused, backgrounded or not.

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

### FR-008 - the audit is written down, refusal branch by refusal branch

`research.md` R1-R2 classify every REFUSAL BRANCH in the record - the unit is the rule slug the
guard records, not the guard, because a guard-level verdict is how feature 164 converted one
make-only branch and left four unexamined. For every branch: what it refused, how many times, and
either the conversion this feature makes or the reason the refusal stays (the fix is a decision or
a reason only the session has; the action is destructive; the block is the point). Named at
minimum: make-only's `guard-write` (41), `inline-override` (4) and `foreign-makefile` (3); gate's
three Edit-time refusals; every no-poll loop shape that stays; clone-sync's name-routing and
live-claim. A branch whose verdict changed from feature 164's classification (pair, clone-sync's
stale-head, no-poll's file wait) says what evidence changed it.

### FR-009 - the documents follow

CLAUDE.md's enforcement table rows for make-only, pair, no-poll and clone-sync; the "A GUARD THAT
CAN PRODUCE THE COMPLIANT COMMAND SHOULD PRODUCE IT" paragraph gains the five; `docs/efficiency-tooling.md`
where it lists the rewrites; each guard's header comment at the point of change; the `make test-file`
help line. Feature 164's research is not edited (it is the record of what was decided then).

### FR-010 - a recipe comment that would run is refused at edit time (added 2026-09-07)

Added mid-feature at the GM's request, relayed by the "Diagram html" session (the words are the
appendix of [`request.md`](request.md)). On 2026-09-07 feature 207 wrote a `: "..."` recipe comment
naming `make test-full` in backticks into the skill Makefile's `test-full` target; inside a
double-quoted shell string a backtick is a command substitution, so the comment RAN `make
test-full`, which reached the comment again, 914 levels deep, until the container hit its
2,048-process limit. Feature 185 had met the same hazard in the same file. Each fix was a reworded
line and a note, and the GM's ruling is that a note is not prevention.

The guard: `guard-file-hooks.sh` refuses an Edit or Write to ANY Makefile (`*/Makefile`, `*.mk`)
whose new text contains a recipe line - a tab, an optional `@`, `: "` - whose double-quoted string
holds an unescaped backtick or an unescaped `$$(` / `$${`. The refusal runs BEFORE the marker
escape and has no escape token of its own: the hazard is a shell fact, not a policy a reason can
argue past. `\`` and `\$$(` are literal to the shell and pass (the Makefile's own `\$$(MAKE)`
mention is the worked example); a single-quoted comment, a `#` make comment, and a recipe COMMAND
(`@echo "$$(date)"`) are not comments and pass. The detector is `_hm_make.py
recipe_comment_hazards`, so the hook and the gate share one definition; the gate-phase backstop is
`tests/tooling/test_makefile_recipe_comments.py`, which scans every Makefile in the tree (for the
routes an edit arrives by that the hook never sees - a merge, a scripted sweep) and proves the
detector fires on each hazard form and passes each safe form. The refusal records
`guard-file blocked recipe-comment-substitution`. Acceptance: `scripts/test-guard-file-hooks.sh`
section 5 (the 207 shape refused with the marker present; the same line without backticks passes;
any Makefile by Write too).

A defect found on the way (Principle XIV): the guard-file hook judged the marker escape BEFORE the
file, on every file, so a spec that merely mentioned the token was refused for a missing reason.
The escape is now judged only for a guard file.

## Decisions Recorded

- **D1 - the pair guard rewrites the one shape `verify` reproduces and permits the rest.** A
  rewrite to `make verify` can carry neither `maps` nor a detached run nor `FULL=1`, and those are
  11 of the 11 real refusals. The bookkeeping `verify` does is two writes and a printf, which the
  hook does itself for any shape. The enforcement point for those shapes moves from before the
  gate to the Stop hook, which is where the 164 rewrite already left it.
- **D7 - a foreground gate shape serializes the review, and says so.** For a detached run the
  review overlaps the gate exactly as under `verify`. For a foreground `make maps ... | tail` the
  hook cannot free the turn without changing where the output goes (`run_in_background` reaps
  `make maps`; a `setsid nohup` rewrite would move the output into a file the session did not
  name), so the review starts when the command returns. That is the serialization feature 151 was
  built to prevent, and this feature accepts it FOR THAT SHAPE ONLY, because the alternative in
  the record was not simultaneity: it was 24 refusals and 98 `PAIR_OK` waivers (80% escaped). The
  context tells the session how to overlap them next time. **To be raised with the GM once the
  implementation works**, as the one place this feature changes what feature 151's ruling delivers.
- **D8 - the file-wait qualifier is fixed as a defect, not widened as a rule.** The three permitted
  forms are unchanged; what changes is that the qualifier now reads them the way the GM's own
  example was written (a regex with `|` in it, a variable in front of the log's path, stderr
  discarded). The substitution test stays on the RAW condition, so nothing quoted can hide one;
  and the every-part rule is tighter than before. Principle XIV: found while auditing, fixed in
  the same feature.
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
