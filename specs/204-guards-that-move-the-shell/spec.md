# Feature 204 - Guards That Move The Shell

**Status**: **APPROVED** 2026-09-07 - `spec-fidelity` round 3 returned FAITHFUL. Round 1 required
the session NAME recorded at firing time (not a read-time lookup over pruned transcripts) and a
stated rule that a subagent resolves to its PARENT's clone; round 2 required FR-009 to stop reading
transcripts, which the spec's own OUT list excludes. Specified 2026-09-07. The GM's request is
[`request.md`](request.md) and it is the authority; where this document and that one differ, that
one is right. Measurements are in [`research.md`](research.md).

## The feature, in one sentence

The main-tree guard judges where a write LANDS rather than where the shell stands, moves a write that
would land in the mirror into the session's own clone instead of refusing it (telling the session it
did), and every guard's firing record carries what an after-the-fact audit needs.

## Why this exists (the GM's words)

*"I keep seeing this error pop up ... is it possible for us to intercept the cd command and rewrite
it to change into the correct directory instead based on what session we are currently in? And then
if we did that, we could add tool context, which reminds the session what directories it should be
working in without actually blocking the command and forcing a retry."* And on the record: *"we
probably need our tools which are blocking commands to log the specific commands that they blocked
along with when this happened and the name of the session in which this occurred. and any other
context which is loggable at that time."* Then, on being told a log exists: *"overall, I want to do
whatever will accomplish the thing which we are trying to accomplish rather than simply have you
follow my directions if my directions are a worse way to accomplish our goals."*

## What was measured before specifying (research R1-R3)

- 173 refusals by this guard were recovered, with full commands and cwd, from Claude Code's own
  transcripts. 127 came from subagents. 164 were issued with the shell standing in `/diagram`.
- Replayed through today's guard: 169 refused. **None** of the 169 names a write inside main by an
  absolute path. 146 contain no `cd` at all; the write went to the scratchpad, `/tmp` or a clone.
  **Two** are the shape the guard was built for (`cd /diagram && git commit`).
- All 16 recorded escapes misdiagnosed the cause, because the refusal text names a cause (*"this
  command cds into /diagram"*) that was not the cause.
- The guard log exists (features 162/168), is on a host mount already, and records `session:
  unknown` on 2,049 of 2,371 entries, the command cut at 200 characters, no cwd, and no reasoning.

## Scope, stated exactly

**IN**: the main-tree guard's verdict, rewrite, context and refusal text (FR-001 to FR-007); the
firing-log entry every guard writes (FR-008); a listing command over that log (FR-009); the corpus
as a regression fixture (FR-010); exposing the clone resolver (FR-011); the documents that describe
the guard (FR-012).

**OUT**: any other guard's VERDICT (what `batching`, `no-poll`, `gate` and the rest refuse or
rewrite is untouched - only the entry they record changes); a new log store (D1); reading the
transcripts from the audit (D1); the 2026-08-17 rule that a bare `cd` into main for a READ is
unenforced - it stays unenforced, and this feature touches no read-only command.

## Requirements

### FR-001 - the guard judges where a write LANDS

For each command segment that writes, the guard determines the write's TARGET directory: the
`-C` path of a `git -C <path> <write-verb>`; the path of a redirect (`>`/`>>`); the absolute path
arguments of a file-writing tool (`sed -i`, `tee`, `touch`, `mkdir`, `rm`, `mv`, `cp`, `ln`, `chmod`,
`chown`, `truncate`, `install`, an editor); otherwise the shell's EFFECTIVE directory at that point
in the command (a `git commit` with no `-C`, `make`, `python3 -c`, a relative path). A target is
classed `main` (under the mirror root and not under `.clones/`), `clone`, or `elsewhere`.

**Acceptance**: every one of the 146 no-`cd` corpus commands whose writes are absolute and outside
main is ALLOWED, silently (FR-010 proves it).

### FR-002 - the effective directory follows the command's own `cd`s, variables and subshells

The effective directory starts at the payload's `cwd` and is advanced by each command-position `cd`
(absolute, relative, or `$VAR` where `VAR=value` appears earlier in the same command, resolved
transitively; `~` is `$HOME`). A `cd` inside `( ... )` does not persist past the `)`. A `cd` whose
target cannot be resolved (an unassigned variable, `cd -`, a command substitution) leaves the
directory UNKNOWN, and an unknown directory is treated as main whenever the shell was last known to
be in main - the conservative direction, so the fix cannot turn a refusal into a false allow.

**Acceptance**: the 12 `cd $VAR` corpus commands and the 8 subshell-into-a-clone commands are
allowed; `cd $UNSET && git commit` from main is not allowed silently.

### FR-003 - a write that names main ABSOLUTELY is still refused

`git -C /diagram commit`, `> /diagram/x`, `sed -i ... /diagram/scripts/x` - a command whose write
verb itself names a path inside the mirror is refused exactly as today, with `MAIN_TREE_OK` as the
escape. No rewrite is attempted: the session named the tree, and a guard never guesses at a command
that says what it means (feature 164's rule).

**Acceptance**: the suite's absolute-path refusals stay at rc 2; the corpus contains zero such
commands, and the fixture asserts that count so a future replay that finds one is noticed.

### FR-004 - a write that would land in main THROUGH THE SHELL'S DIRECTORY is moved to the clone

When a write's target is main only because of where the shell stands or where a `cd` in the command
put it, the guard REWRITES the command so that the write lands in the session's clone at the same
relative position: a command-position `cd <main>[/sub]` becomes `cd <clone>[/sub]`; a command that
writes from the standing cwd with no cd before the write gets `cd <clone> && ` prepended (and when
the standing cwd is a subdirectory of main, `cd <clone>/<that sub> && `). The rewritten command is
returned as `updatedInput`, exit 0.

**Acceptance**: the two `cd /diagram && git commit` corpus commands rewrite to the clone; the
2026-08-30 incidents in `test-main-tree-hooks.sh` (`cd $MAIN && git add -A && git commit`,
`cd $MAIN; echo x > specs/163/request.md`, `cd $MAIN/specs && echo x > f`, a commit while standing
in main) now REWRITE rather than refuse, and the rewritten command's cd names the clone.

### FR-005 - shapes the rewriter cannot rebuild exactly keep the refusal

No rewrite, a refusal instead: the session's clone cannot be resolved (FR-011 returns nothing), or
the resolved clone does not exist as a git work tree; the command opens with a function definition
(`name() {`), where a prepended `cd &&` would be a syntax error; a `cd` into main whose text the
rewriter cannot locate in the ORIGINAL command (it matched only in the sanitized copy, e.g. through
a resolved variable). The refusal says which of these it was.

### FR-006 - the session is told what happened, and why

A rewrite carries `additionalContext` stating: the shell was standing in the mirror (or the command
cd'd into it), which is main's tree and never a workspace; the command was rewritten to run in
`<clone>` and the shell stays there for later commands; `git -C /diagram <read>` for reading main;
the pointer `(scripts/main-tree-hooks.sh; feature 204)`. One paragraph, no more.

### FR-007 - the refusal text names the ACTUAL cause

The refusal distinguishes *"your shell is standing in `<cwd>`, inside the mirror"* from *"this
command cds into the mirror"* from *"this command names a path inside the mirror"*, because the
present text names the second in all three cases and every recorded escape misread it.

### FR-008 - every guard's firing record carries what an audit needs

`guard_log` in `_guardlog.sh` writes, for EVERY guard, in addition to today's fields (`utc` is
already the GM's *"when this happened"*): `session` from the payload's `session_id` (falling back
to `$SID`, then `unknown`); **`session_name`, resolved AT FIRING TIME** through the FR-011
resolver - the claim map's clone directory name first (one file read), else the transcript's last
`custom-title` - falling back to the id, then `unknown`, because the transcripts the read-time
lookup would need are pruned (R2) and the GM named the session's NAME explicitly; `cwd`; `tool`
(`tool_name`); `transcript` (`transcript_path`); `command` - the full command or file path, never
truncated (`detail` stays, truncated, for the existing readers); and `context`, an optional fifth
argument holding the guard's own decision inputs as JSON (for main-tree: the standing cwd, the
effective directory, each write target and its class, the verdict, the clone). Entries stay one
file each, host-side, untracked (D1). The `_guardlog.sh` comment about rebuild loss is corrected.

**Acceptance**: `tests/tooling/test_guard_firing_log.py` gains cases for main-tree's `rewrote` and
`blocked` entries and asserts the new fields, `session_name` included, on a real firing whose
claim map names a clone; `make hooks-test` green.

### FR-009 - a listing over the log, by guard

`make guard-log` (skill Makefile) prints the recorded firings: `GUARD=<name>` filters to one guard,
`SINCE=YYYY-MM-DD` to a date, `EVENT=blocked|rewrote|escaped|reminded` to an event; each row shows
the UTC time, the session NAME (the recorded `session_name`, else the recorded id - entries written
before this feature show their id, and the 2,049 that recorded `unknown` stay `unknown`; no
transcript is read, per the OUT list and D1), the cwd, the event and rule, and the first line of
the command; `FULL=1` prints the whole command and the context. A reader, not a report generator.
`make audit`'s census is unchanged.

### FR-010 - the corpus is a regression fixture

The 173 recovered refusals (command, cwd, whether a subagent, timestamp; session ids dropped) are
checked in as `scripts/fixtures/main-tree-refusals-2026-09.json`, and `test-main-tree-hooks.sh`
replays them through the guard with a fake mirror substituted for `/diagram` and a resolvable
clone, asserting: zero REFUSALS remain; the count of rewrites equals the count of commands whose
write lands in main through the shell (the two `cd /diagram` cases plus the standing-in-main
relative writes, a number the fixture states); everything else is allowed silently. **Measured on
2026-09-07**: 109 allowed, 64 rewritten (62 standing, 2 by cd), 0 refused; each row carries its
verdict and the suite fails on a single row moving between classes. Two things the replay had to
get right, recorded because each cost a round: `/diagram` is substituted only as a path ROOT
(`l7r/diagram/page.py` and `.claude/skills/diagram` merely contain it), and each recorded cwd is
created under the fake mirror, because the resolver derives the mirror from the cwd through git.

### FR-011 - the clone resolver is exposed, not copied

`clone-sync-hooks.sh resolve` reads a hook payload on stdin and prints the session's clone path
(claim map first, then `canonical_clone`), or nothing. `main-tree-hooks.sh` calls it, and so does
`guard_log` for the name (FR-008).

**A subagent's command resolves to its PARENT session's clone.** A subagent's hook payload carries
the parent's `session_id` (R6), so the claim map and the sessions json both answer with the parent's
clone, and the subagent's own transcript (which holds no `custom-title`) is never the deciding
source. 127 of the 173 recorded refusals were subagents', and this is the direction where a wrong
answer is destructive - a rewrite into a DIFFERENT session's clone writes one session's work into
another's tree - so the rule is stated here and proved by its own acceptance rather than left to
FR-010's replay, whose resolver is stubbed.

**Acceptance**: the clone-sync suite drives `resolve` with (a) a payload whose id is in the claim
map, (b) one whose id is only in a transcript's `custom-title`, (c) a SUBAGENT-shaped payload - the
parent's id, a `transcript_path` under `<parent>/subagents/` holding no `custom-title` - and gets
the parent's clone, and (d) an unresolvable id, and gets nothing.

### FR-012 - the documents

`CLAUDE.md`'s table row for this guard, the "NAME THE TREE IN THE COMMAND" paragraph's mention of
what is enforced, `docs/efficiency-tooling.md`'s line on the guard, and the guard's own header
comment describe the verdict as it now is; the ledger row in `docs/review-ledger.md` is NOT owed
(this is a guard, not a review agent).

## Decisions recorded

- **D1 - the log stays where it is, enriched; no new store and no transcript reader.** The GM was
  indifferent between a host-side untracked directory and source control. Host-side, untracked:
  `~/.claude/guard-log/` is already a host mount (R1), several clones write it concurrently (a
  tracked directory would conflict on every push - `dev/run-log/README.md`'s reason), and 2,371
  files a week is not history anyone wants in `git log`. The transcripts (R2) are complete but
  pruned and expensive; the guard log is the index and it now carries everything they do plus the
  guard's reasoning.
- **D2 - only a write that lands in main THROUGH THE SHELL is rewritten.** A write that names main
  absolutely is refused (FR-003). The corpus has zero of those, so nothing observable is lost, and
  the rule stays "never guess at a command that says what it means".
- **D3 - a correct command is silent.** A write that lands elsewhere while the shell stands in main
  is allowed with no context line. A guard that speaks on correct work trains sessions to skip
  what it says (the deliberately-unenforced list in `CLAUDE.md`). The shell's next RELATIVE write
  gets the rewrite and the explanation.
- **D4 - the rewrite moves the shell, deliberately.** `cd <clone> &&` is prepended rather than the
  write being redirected in place, so the shell's persisted cwd ends in the clone and the leak the
  guard exists for is cured for the following commands, not just this one.
- **D5 - `python3 -c` remains a write.** It was a false positive on read-only diagnostics, but its
  cost is now zero: from the clone it is allowed; from main it is moved. Narrowing the write list
  would reopen the false-allow direction for no saving.
- **D6 - unknown resolves toward main.** An unresolvable `cd` target while the shell is in main is
  treated as still in main, so the precision fix cannot become a bypass (`cd $(somewhere) && git
  commit`).
- **D7 - verdict logic lives in Python (`scripts/_hm_tree.py`), the shell script stays the
  wrapper.** The bash guard is four regexes with three feature-numbered patches on top; the
  effective-directory walk (FR-002) is a small interpreter and is testable as one.

## Exceptions

None. The GM's literal ask - rewrite the `cd`, add context, log the block - is delivered in full,
and the widening (rewriting the standing-in-main shape too) is the GM's second message applied:
*"do whatever will accomplish the thing"*, where the thing is the refusal they keep seeing, which
the census shows is that shape 146 times out of 173.
