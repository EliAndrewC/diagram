# Research - feature 204 (guards that move the shell)

Every number here was MEASURED on 2026-09-07, by reading the records rather than the code, and the
scripts that produced them are in this session's scratchpad (`refusals.json`, the replay). Nothing
here is about how a place was built or lived in; every task is `research: procedure`.

## R1 - what the guard's own log already records

`scripts/_guardlog.sh` writes one JSON file per firing to `~/.claude/guard-log/` (feature 162,
extended to every guard branch by feature 168). Census on 2026-09-07:

| | |
|---|---|
| entries, all guards | 2,371 |
| entries whose `session` field is `unknown` | 2,049 |
| `main-tree` entries | 187 (171 `blocked`, 16 `escaped`) |
| `main-tree` blocks on 2026-09-06 alone | 122 (138 counting the guard log's later arrivals) |

`session` is `unknown` because `guard_log` reads a shell variable `$SID` that only `measure-hooks.sh`
sets; the payload's own `session_id` is never read. `detail` is the command cut at 200 characters.
No `cwd`, no tool name, no transcript, and nothing about which branch of the guard decided.

**The directory is a host mount** - `mount` lists `/home/agent/.claude` on the host's `nvme0n1p3`
alongside `/diagram` - so it already survives a container rebuild. The comment in `_guardlog.sh`
saying *"a container rebuild loses it"* was true when written and is not now; this feature fixes
the comment.

## R2 - what Claude Code's own transcripts record (the GM's second question)

Every session's transcript (`~/.claude/projects/-diagram/<session_id>.jsonl`, and
`<session_id>/subagents/*.jsonl` for its subagents) holds, for a refused command: the refusal text
(`toolUseResult`, with `toolDenialKind: permission-rule`), `timestamp`, `cwd`, `sessionId`,
`gitBranch`, `isSidechain`, and - one record up, through `parentUuid` - the `tool_use` block with
the FULL command. `/rename` records land there as `{"type":"custom-title"}`, so the session name is
recoverable too. 42 top-level transcripts and 483 subagent transcripts, 2.6 GB.

So the transcripts ARE the complete log, and they answered a question the guard log could not
(R3, subagents). They are not the right long-term index: Claude Code prunes them (30 days by
default; nothing in `settings.json` overrides that), they cost a scan of gigabytes per question,
and they say nothing about WHY a guard decided (which branch, what it matched). The decision (D1):
keep the guard log as the durable, cheap index, make each entry carry what the transcript carries
plus the guard's own reasoning, and point the audit at it. No third log.

## R3 - the corpus: every recorded refusal, with its full command and cwd

Recovered from the transcripts: **173** refusals of this guard, every one with its command.

| | |
|---|---|
| from a SUBAGENT (`isSidechain: true`) | 127 |
| from the main session | 46 |
| shell standing in `/diagram` (the mirror root) | 164 |
| standing in `/diagram/.claude/skills/diagram` (inside main) | 9 |

By the shape of the command:

| shape | count |
|---|---|
| no `cd` at all - the write went to the scratchpad, `/tmp`, or a clone via `git -C $C` / an absolute path | 146 |
| `cd $VAR && ...` where `$VAR` was assigned to a clone or the scratchpad in the same command | 12 |
| `( cd /diagram/.clones/<name> && ... )` - the guard's OWN recommended form | 8 |
| `cd <somewhere else>` (relative, or `/tmp`) | 5 |
| `cd /diagram && <write>` - the shape the guard was built for | 2 |

**Replayed through the guard as it stands today**, each with its recorded cwd: **169 refused, 4
allowed**. Of the 169, **zero** name a write inside main by an absolute path (`git -C /diagram
<write>`, `> /diagram/...`, `sed -i ... /diagram/...`). The two `cd /diagram && git commit` cases
are the guard's true positives, and both are mistakes a session would have wanted moved to its clone.

**Why the 146**: a session's shell starts in `/diagram` (the primary working directory), and a
subagent's shell starts wherever its parent's is. Feature 170 taught the guard to refuse any
write-shaped command while the shell stands in main, without asking where the write LANDS. The
motivating incident was a relative write (`git commit` with no path); the 146 are absolute writes.

**The escapes misdiagnosed the cause every time**: all 16 `MAIN_TREE_OK` reasons say a variant of
*"false positive, scratchpad path substring only, no cd used"*. The real cause - the shell was
standing in the mirror - is not in the refusal text, which says *"this command cds into /diagram"*
even when it did not. A session that cannot see the cause cannot fix it, which is why one session
paid 100+ round trips in a day.

## R4 - the shapes a rewrite must handle, from the corpus

- `cd $R && git add -A && git commit` with `R=/diagram/.clones/x` earlier in the command: the
  variable must be resolved from the command's own assignments, or the cd cannot be classified.
- `S=/tmp/...; ( cd $S && cat > m.py <<'PY' ... )`: a subshell's cd must not leak past its `)`.
- `cat > $SP/phases.py <<'PY'` from cwd `/diagram`: an absolute target elsewhere; nothing to do.
- `python3 - <<'PY'` and `python3 -c`: an interpreter can write anywhere; the target is the shell's
  directory (D6).
- `cd /diagram/.claude/skills/diagram/dev/run-log && grep ... > ...`: a cd DEEPER into main, then a
  write - rewritten to the same subpath under the clone.
- `C=/diagram/.clones/x; git -C $C rm ...`: `git -C <path>` writes at `<path>`, not at the shell.

## R5 - how a rewrite is emitted

`gate-hooks.sh`, `no-poll-hooks.sh`, `make-only-hooks.sh`, `pair-hooks.sh` and `house-style-hooks.sh`
already return `hookSpecificOutput.updatedInput` (the command the session runs) plus
`additionalContext` (a line the model reads) at exit 0. The form is copied, not reinvented; the
feature-164 rule applies: a shape the rewriter cannot rebuild exactly keeps the refusal.

## R6 - resolving "this session's clone"

`clone-sync-hooks.sh` already resolves it two ways: `canonical_clone <sid> <transcript>` (the last
`custom-title` in the transcript, else `~/.claude/sessions/*.json`), and the claim map
`<main>/.clones/.session-clones/<session_id>` -> clone path, written when a session first edits. A
subagent's payload carries its PARENT's `session_id` (measured on a 2026-09-06 subagent transcript:
`sessionId` equals the parent's), so both sources resolve it to the parent's clone. This feature
exposes the resolver as a `clone-sync-hooks.sh resolve` mode rather than copying it.
