# Research: feature 212 - guards that do the right thing

Every task here is `research: procedure`; nothing decides how a place was built or lived in. All
numbers were measured on 2026-09-07 in this container.

## R1 - the record the GM asked us to read, and where it actually is

The GM: *"I believe that we are already logging or at least Claude Code is already logging. All of
the times that any of our hooks reject a command including what the command was."* Both are true,
and neither alone is enough:

- `~/.claude/guard-log/` (features 162/168/204) holds 2,788 entries from 2026-08-30 to
  2026-09-07. Before feature 204 landed (2026-09-07 18:00Z) an entry cut the command at 200
  characters, which is shorter than most of the commands this feature needs to judge.
- Claude Code's own transcripts hold every refusal in full: a `tool_result` marked `is_error`
  whose text begins `PreToolUse:<tool> hook error: [<script> pretool]:`, paired to its `tool_use`
  by id. That is the source feature 204 used, and the one used here. The scan is
  `specs/212-guards-that-do-the-right-thing/census.py`.

**1,143 refusals in 610 transcripts (42 sessions and their subagents), 2026-08-25 to 2026-09-07.**
By guard, with what each refusal was FOR and what this feature decides (R2 has the reasoning):

| guard | branch (the rule slug it records) | refusals | what they were | decision |
|---|---|---|---|---|
| batching | serial-recon | 629 (279 Bash, 350 Read) | three single-call read-only turns in the last six | STAYS - the fix is to make fewer, bigger turns, which no rewrite of one command can do; it warns one turn early since 164 |
| main-tree | write-in-mirror | 178 | writes judged by where the shell stood | DONE by feature 204 (rewrite into the clone) |
| make-only | guard-write | 41 | a guard file (the Makefile, a hook) written by a python heredoc or `sed -i` | STAYS - the compliant form is the Edit tool carrying a `GUARD_EDIT_OK` REASON, and the reason is the missing thing; a hook cannot supply it. 21 of the 41 had the token in a heredoc COMMENT, which feature 169 ruled a mention |
| make-only | engine-entry-point | 29 | `python3 -m l7r.diagram.<module>` | REWRITE when a make target wraps the module (FR-002): 4 of the 29 in the record (`ci status`, `ci engine-key`, `switches`, `hamletgen`). 12 were `tools.scatter_audit`, which no target wraps (STAYS, the refusal lists the wrapped modules); 5 `tools.crop_map`, since retired; 8 were heredoc mentions before feature 169 |
| make-only | bare-pytest | 20 | pytest run directly | REWRITE the targeted run (FR-001): 11 of the 20 (one file, a directory, a node id, `-k`, output flags, a pipeline tail). STAYS for `-m`/`--deselect` (1), `--co`/`--collect-only` (3, one of them also a `-p` plugin load), no test path (2, a scratch fixture and a `--co` over a bare directory name), a python heredoc quoting a test (1); 2 were heredoc mentions feature 169 fixed |
| make-only | inline-override | 4 | `REF_OK=`/`GATE_OK=` supplied on the command line | STAYS - the prompt it skips exists to be answered by a person; 3 of the 4 were a suite driving the Makefile to prove the refusal |
| make-only | foreign-makefile | 3 | `make -f <other>` | STAYS - a foreign makefile is the documented route past every guard; all 3 were experiments on a scratch makefile, which `make -C <scratch>` runs legally |
| guard-file | no-marker | 73 | a guard file edited with no `GUARD_EDIT_OK` (31 the Makefile in one clone) | STAYS - a reason only the session has; it teaches at Read time since 164 |
| guard-file | GUARD_EDIT_OK-no-reason | 4 | the token with no reason | STAYS - feature 170's rule |
| no-poll | busy-wait-loop | 32 | a loop containing a sleep | FIX the qualifier (FR-004a): 7 backgrounded log-watching waits were refused by a `|` inside the quoted regex, a `$S/` path, a `2>/dev/null`, or `[ -s f ] && grep`. REWRITE the foreground form (FR-004b): 0 in the record - the one foreground log wait carried a `$(seq 40)` bound and stays refused for the substitution; the rewrite is the path for the next one. STAYS for the 11 loops on a process, a pid list or a network call; 26 rows were not loops at all once heredocs and quotes are blanked (mentions before 164, and the pgrep branch 164 converted) |
| no-poll | self-matching pgrep | 12 | `pgrep -f <literal>` | DONE (164, the bracket rewrite) |
| gate | quick+done | 34 | both targets in one command | DONE (162, combined) |
| gate | k-subset-before-gate | 2 | `make done` after a `-k`-only run | STAYS - the block is the point and it blocks once; the compliant command (the whole file first) could be prepended, but with 2 firings in two weeks the machinery is not worth its false-positive risk |
| gate | (Edit) | 3 | the guard's own file edited | STAYS - a `guard-file` case, counted here by the reporting hook |
| pair | gate-without-review | 21 (11 real) | 8 `make maps`, 3 detached `make done`; 10 mentions and suite-driving commands | REWRITE the exact plain `make done` (164, kept); RECORD AND PERMIT every other shape (FR-003) |
| pair | review-without-gate | 3 | a settlement-review dispatched with no gate beside it | STAYS - the review would judge a map the suite has not checked; the fix is to start the gate, which is a paid run the hook must not start unasked |
| pair | (Agent, spec-fidelity mention) | 2 | a spec-fidelity prompt quoting "settlement-review" | DONE 2026-08-29 (the agent TYPE decides) |
| clone-sync | stale-head | 13 | a clean clone one commit behind main, every time mid-turn | RUN `sync-in` in the hook and let the edit proceed (FR-005) |
| clone-sync | name-routing, live-claim | 3 | an edit in another session's clone; a clone occupied by a live session | STAYS - the fix is a rename or a different clone, a decision for the GM |
| measure | second/third measurement | 12 | an expensive measurement repeated with nothing changed | STAYS - the block is the point (162) |
| readme | readme-is-the-gm-s | 9 | a README written by a session | STAYS - the GM's to write (XVII) |
| discard | discard | 6 | a checkout over uncommitted work | STAYS - destructive; the guard cannot know which version is wanted |
| house-style | (Write) | 6 | British spellings and dashes | DONE (164) - all six predate it |
| source-block | gm-source-block | 3 | the GM's writing edited | STAYS |
| no-branch | branch-creation | 1 | a branch created | STAYS - a procedure, not a substitution |

## R2 - what each conversion is, and why it is exact

**The bare pytest (20 refusals; 18 of them still `bare-pytest` to today's classifier, two were heredoc mentions feature 169 fixed).** Eleven are what the GM described - a targeted run of one file, a
directory or a node id, sometimes with `-k`, always with output-only flags and nearly always with
`2>&1 | tail -N` or `| sed -n` after it. Feature 164's rewrite converted NONE of them, because it
declined any command with a pipeline after the pytest segment. The pipeline is not part of the
pytest invocation; it consumes the output of whatever runs, so `make test-file FILE=x 2>&1 | tail
-8` is the same command with the same tail. The other seven are `--collect-only`, `-m`/`--deselect`,
a `-p` plugin load, a `--co` collection, no test path at all, or a pytest inside a scratch fixture - shapes that change WHICH
tests run or HOW they are measured, and those stay refused, now with the token that stopped the
rewrite named in the refusal.

`-k` was the shape the GM named (*"even a specific test case"*). `make test-file` had no way to
carry it; it gains `K=<expr>`, and the target is what `gate-hooks` already treats a `-k` run as - a
SUBSET, which must be followed by a whole-file run before the gate. So the gate guard learns the
two subset spellings of the make target (`K=` and a `::` node id), or the rewrite would have turned
a tracked subset into an untracked one.

Dropped flags: the ones the target already supplies (`-q`, `-n`, `--dist`, `--no-cov`), output-only
ones (`-v`, `--tb`, `--color`, `--no-header`, `-x`, which only stops early), `-p no:cacheprovider`,
and `-p no:randomly` - pytest-randomly is not installed here (the requirements files do not name it),
so `-p no:randomly` is a no-op and dropping it changes nothing.

**The engine entry point (29 refusals).** Twelve were `tools.scatter_audit`, which no make target
wraps (it stays refused - the refusal names the target list). Eight predate feature 169 and were
heredoc mentions, not runs. The rest were `ci status`, `ci engine-key <ref>`, `switches` and
`hamletgen` - each of which IS a make target's recipe: `$(RUN).ci status`, `$(RUN).ci engine-key
$(or $(REF),HEAD)`, `$(SWITCH) show`, `$(RUN).hamletgen $(ARGS)`. The compliant command is
DERIVED from the Makefile at hook time rather than kept in a table: a target whose recipe is one
`$(RUN).<module> ...` line, with `$(ARGS)` taking the rest, `$(or $(VAR),default)` taking one word
and `$(if $(VAR),--flag,)` taking an optional flag. A module with no such target, or a recipe with
more than one line, or arguments the recipe cannot carry, keeps the refusal - a derived table cannot
name a target that does not exist.

**The gate without a review (11 real refusals of 26).** Feature 164 rewrote a plain `make done`
into `make verify`. It fired once. Every real refusal since was a shape `verify` cannot take: `make
maps` (eight times), a `make done` detached under `setsid nohup ... > log &` (three), `make done
FULL=1`. `make verify` does three things - records the engine key as the pairing's gate key, prints
the maps whose manifest changed with "DISPATCH NOW, in the same turn", and starts the gate. The
hook can do the first two itself for ANY gate invocation and let the command run unchanged as the
third, which is exactly what `verify` did with a fixed shape. The enforcement is the same as it was
under the rewrite: the Stop hook refuses a turn that ends with the gate green and no review
dispatched, once per content. What changes is that no shape of the gate is refused for lacking the
review that the session is about to be told to dispatch.

**The file-watching wait (32 loop refusals, 8 of them the real thing).** Feature 165's ruling
permits ONE wait: a backgrounded loop whose condition reads a file. The record holds eight real
uses of exactly that shape - `until grep -qE "gate green|GATE FAILED|EXIT=" /tmp/161-done2.log; do
sleep 5; done` and its siblings - and the qualifier refused SEVEN of them. It reads the condition
raw, so the `|` inside the quoted regex reads as a pipeline, a `2>/dev/null` reads as an output
redirection, and `[ -s f ] && grep -qE x f` matches none of its three forms. That is a guard firing
on correct work, the failure this project's own rule about guards names as the worst kind, and it
is fixed here as a defect (Principle XIV), in five stated steps: the substitution test runs on
the raw condition first (a `"$(curl ...)"` inside quotes still executes, so it still disqualifies);
inside each quoted operand the shell characters `|<>;&` are dropped and the rest kept, so a regex
loses its bar and a quoted path stays a path; a `2>/dev/null` is removed (it writes nothing, and
the grep form needs the path last); the pipeline and redirection tests run on the result; and the
condition is split on `&&`/`||` with EVERY part required to be one of the three forms, the grep
form's path allowed a `$VAR` prefix as the record writes it. The last step is tighter than before,
which searched the whole condition for one form and so let `[ -f x ] && curl` through.
The boundary is otherwise the one the GM
drew. A foreground use of the same shape is backgrounded and told (none in the record qualifies - the one foreground log wait carries a `$(seq 40)` bound - so this is the path for the next one), since the permitted form
is the same command with `run_in_background` set - the harness's single-completion-notification
shape, with the trailing `tail` running inside it. A loop that waits on a process or a network call
stays refused, backgrounded or not.

**The stale clone (13 refusals).** Every one happened MID-TURN: the prompt hook had synced the clone
at the turn's start, main moved while the session worked (another session landed), and the next Edit
found a clean clone one commit behind. The refusal names one command, `sync-in`, which on a clean
clone is a fast-forward (1.4 s measured). The hook runs it under a 25 s bound; if the clone is then
no longer behind, the Edit proceeds with a line saying main was merged in; if the merge fails or
runs long, the refusal stands as before. An Edit whose file the merge changed fails on the
harness's own staleness check and the session re-reads - which is the correct outcome, not a risk.
Feature 164 classed clone-sync as "a procedure, not a substitution"; for this one rule the procedure
is a single idempotent command, which is the case the class does not cover.

**Sources:** this repository's transcripts and guard log; no claim here is about the world outside
this repository.

## R3 - the corpus, as a fixture

The commands behind R1 are `scripts/fixtures/guard-refusals-2026-09.json` - every make-only, pair,
no-poll and clone-sync refusal with its command, its guard, and the verdict this feature expects of
it. `tests/tooling/test_guard_corpus.py` replays it through the decision functions and fails when
a verdict moves, which is what keeps a later change to `_hm_make.py` or `_hm_shape.py` from quietly
un-converting a shape.

## R4 - a recipe comment that ran (the GM's request relayed 2026-09-07)

The skill Makefile carries 110 recipe comments in the `: "..."` form. Inside that double-quoted
shell string a backtick or a `$(` (a Makefile's `$$(`) is a command substitution, and the record
holds three incidents of exactly that: feature 185 (the phase loop ran lint on every gate; the fix
was single quotes and a comment saying so), feature 188 (`make tick` ran `_ENGINE_DIRS` out of an
interpolated note; the fix moved the note into the environment and left a comment), and feature 207
(a comment in `test-full` naming `make test-full` in backticks recursed 914 levels to the container's
2,048-process limit; the fix was a reworded line and a note). Three notes, three recurrences of one
hazard, which is the GM's point. The only place that sees every Makefile write BEFORE it can execute
is the edit-time guard - a gate-phase check runs only inside a target that includes the phase, and
the 207 recursion fired from a bare `make test-full` - so the refusal is there (FR-010), with the
gate scan as the backstop for a merge or a sweep. The `\$$(MAKE)` mention at line 155 is escaped
and passes, which is the worked example of the escape the detector honors.

**Sources:** this repository's Makefile and git history; no claim here is about the world outside it.
