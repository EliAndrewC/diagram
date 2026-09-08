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

| guard | refusals | what they were | decision |
|---|---|---|---|
| batching | 629 (279 Bash, 350 Read) | serial recon | STAYS - the fix is to batch, which no rewrite can do; it already warns one turn early (164) |
| main-tree | 178 | writes judged by where the shell stood | DONE by feature 204 (rewrite into the clone) |
| make-only | 97 | 41 guard-file written from a shell; 29 engine entry points; 20 bare pytest; 4 inline overrides; 3 foreign makefiles | pytest: REWRITE the targeted runs (FR-001); entry points: REWRITE the ones the Makefile wraps (FR-002); the other three STAY |
| guard-file | 77 | a guard file edited with no marker (31 the Makefile in one clone) | STAYS - the missing thing is a reason, which only the session has; it teaches at Read time (164) |
| no-poll | 44 | 32 loops with a sleep; 12 self-matching pgrep | pgrep: DONE (164); the loops: REWRITE the foreground file-watching wait into the backgrounded form the GM permitted (FR-004); the rest STAY |
| gate | 39 | 34 `quick`+`done` in one command; 2 `-k` subset before the gate; 3 on Edit | quick+done: DONE (162); the `-k` block STAYS (it blocks once and the re-issue passes) |
| pair | 26 (21 Bash, 5 Agent) | 11 real gate invocations with no review beside them (8 `make maps`, 3 detached `make done`), the rest mentions and test-driving | REWORK: the gate runs, the pairing is recorded, the session is told to dispatch now (FR-003) |
| clone-sync | 16 | 13 edits in a clean clone whose HEAD was behind main; 3 name-routing/claim | stale-head: RUN `sync-in` in the hook and let the edit proceed (FR-005); the other two STAY |
| measure | 12 | a second or third expensive measurement with nothing changed | STAYS - the block is the point (162) |
| readme | 9 | a README written by a session | STAYS - the GM's to write (XVII) |
| discard | 6 | a checkout over uncommitted work | STAYS - destructive; the guard cannot know which version is wanted |
| house-style | 6 | British spellings and dashes in a Write | DONE (164) - all six predate it |
| source-block | 3 | the GM's writing edited | STAYS |
| no-branch | 1 | a branch created | STAYS |

## R2 - what each conversion is, and why it is exact

**The bare pytest (20 refusals).** Ten are what the GM described - a targeted run of one file, a
directory or a node id, sometimes with `-k`, always with output-only flags and nearly always with
`2>&1 | tail -N` or `| sed -n` after it. Feature 164's rewrite converted NONE of them, because it
declined any command with a pipeline after the pytest segment. The pipeline is not part of the
pytest invocation; it consumes the output of whatever runs, so `make test-file FILE=x 2>&1 | tail
-8` is the same command with the same tail. The other ten are `--collect-only`, `-m`/`--deselect`,
a `-p` plugin load, a coverage run, or a pytest inside a scratch fixture - shapes that change WHICH
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

**The foreground file-watching wait (about 10 of 32 loop refusals).** Feature 165's ruling permits
ONE wait: a backgrounded loop whose condition reads a file. The census shows the same loop issued in
the FOREGROUND - `until grep -q "gate green" /tmp/164-done.log; do sleep 10; done; tail -30 ...` -
ten times. The permitted form is the same command with `run_in_background` set, which is the
harness's own single-completion-notification shape; the trailing `tail` runs inside it and its
output arrives in the notification. So a foreground loop that would qualify as a file-watching wait
if it were backgrounded is backgrounded, and told. The boundary does not move: the same three
condition forms, no substitution, pipeline or output redirection inside the condition. A loop that
waits on a process or a network call stays refused.

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
