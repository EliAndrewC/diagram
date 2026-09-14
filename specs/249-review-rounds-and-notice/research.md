# Research - 249 review rounds read the diff, and the notice speaks on any single call

## R1 - what the two rounds cost, and why (one-shot, 2026-09-14, from this session's transcript)

Measured from the session transcript's timestamps and the two subagents' usage lines, one pass, on
the feature 242 amendment of 2026-09-14. The whole change took 700 s from prompt to report. Round 1
of `spec-fidelity` ran 229 s, 13 tool uses, 165k tokens; round 2 ran 160 s, 9 tool uses, 110k tokens;
together 363 s, over half the change. Both rounds read `spec.md`, `request.md` and `tasks.md` end to
end. The agent's contract already said a round after the first reads only the changed passages
(MODE 3, *"only rereviewing the new stuff"*, feature 236 item 6) and that a reviewer not told which
passages changed should ASK rather than re-read. Neither round asked. The cause is the dispatch: round 1
was handed the whole spec and a commit to diff itself; round 2 was handed the whole amendment diff
against the accepted spec plus whole-spec questions ("every FR has an SC"). The rule was right and the
prompt asked for more than the rule, which is what the GM's *"instructions are not reliably followed"*
names, and why the fix is a rewrite of the dispatch by the tooling rather than a fourth copy of the
sentence.

## R2 - why the batching notice did not fire (one-shot, 2026-09-14, from the guard log and the state file)

The batching guard records a turn as serial when it made ONE call that finished under the cheap bound,
whatever the command's shape. The notice and the block both add a shape test on the INCOMING call
(no fold, no heredoc, no runner). In the measured sequence the window reached one below the bar while
the arriving call was a folded command with a semicolon, so the notice stayed silent; the next call was a
bare `sed` at the bar and was blocked with no notice before it. The session's state file at the time
read five serial marks in six. A notice is `additionalContext` on an allowed call and costs no round
trip, so there is no reason for it to carry the shape test the block needs.

## R3 - where the previous round's verdict can be read back (measured 2026-09-14)

A subagent's transcript persists at `~/.claude/projects/<proj>/<session>/subagents/agent-<id>.jsonl`
(the path `agent-stall-hooks.sh` already derives from the payload's `transcript_path`). Its FIRST
record is the dispatch prompt as a plain string, and its LAST record is the agent's final assistant
message, whose text blocks carry the verdict. Checked on this session's two `spec-fidelity`
transcripts: both first records open with the session's prompt naming `specs/242-...`, and both last
records carry `FAITHFUL` or `CHANGES REQUIRED`. So the previous round's verdict is recoverable verbatim
by the hook: the newest transcript whose prompt names the feature directory and whose last text carries
one of the two verdict words. When none matches - a fresh container, a `/clear` that minted a new
session id - the spec's own Review history is the fallback, marked as the session's summary rather than
the reviewer's words.

## R4 - why the diff base is a snapshot rather than a commit

A round's application and the Review history entry that records it may share one commit (feature 242's
round 1 did), may be uncommitted at dispatch, or may be spread over several. A snapshot of the feature
directory taken at every dispatch is the one base that is right in all three cases: the next round's
diff is exactly what changed since the reviewer last looked. It lives under the clone's `.git/`, beside
`pair-hooks.sh`'s `review-snapshot/`, so it is never committed and never crosses sessions.
