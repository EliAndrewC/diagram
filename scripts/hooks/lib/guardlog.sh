#!/usr/bin/env bash
# guardlog.sh - what a guard did, recorded so the next tuning starts from a total (feature 162).
#
# WHY (GM 2026-08-30): *"I notice I've been seeing a lot of this in the output of my claude code
# sessions over time ... Given how expensive that is, should we make it so we start blocking at 2 in
# a row instead of 3 in a row?"* Answering that took a replay of 715 MB of session transcripts,
# because no guard in this repository records anything when it fires. `dev/review-ledger.md` exists
# so that "is it pulling its weight" is a TOTAL for the review subagents; this is the same thing for
# the two guards feature 162 touches.
#
#   guard_log <guard> <blocked|escaped|rewrote|reminded> <detail>
#
# ONE FILE PER ENTRY, never an appended shared file - the reason is `dev/run-log/README.md`'s: several
# clones work at once and a shared append conflicts on every push. HOST-WIDE (~/.claude/guard-log/)
# rather than in a clone, because a hook fires for commands that name no working tree at all and
# main's tree is never written by a session. The cost, stated rather than hidden: the log is not
# versioned. (It DOES survive a container rebuild - `/home/agent/.claude` is a host mount, checked
# against `mount` on 2026-09-07, feature 204; this comment used to say the opposite.)
# (GUARD_EDIT_OK: feature 204 - the record gains the fields an audit needs; nothing a guard DECIDES changes.)
#
# It must never take a guard down with it: every failure here is swallowed.

# guard_log <guard> <event> <detail> [rule]
#
# THE RULE IS THE FOURTH FIELD (feature 168, GM 2026-08-30: *"the firing log should record more data
# for us to be able to use to make improvements in the future"*). Several guards enforce more than one
# thing, and "no-poll fired 32 times" cannot say which of its three rules is carrying the cost - the
# unit a future improvement acts on is a RULE, not a script. Absent, it records as the event.
#
# AN ESCAPE IS A BRANCH, and the one that matters most: the escape RATE is what this project has
# actually acted on (feature 162 retired a refusal that was being escaped 62% of the time), and before
# this feature it was computable for exactly one guard.
#
# (`escape_or_refuse`, the escape decided in shell, and `guard_cmd`, its parse of the command for the log, were removed with
# `hm_escape.py` - feature 449 T129: no script called either once every guard was ported to Rust. The rule is the guard's
# `shared::escape` (`escape_or_refuse` there), and the shell's one question of it, the reason floor, is `l7r-gate escape reason-ok`.)

# guard_log <guard> <event> <detail> [rule] [context-json]
#
# EVERY ENTRY CARRIES WHAT AN AUDIT NEEDS (feature 204, GM 2026-09-07: *"log the specific commands
# that they blocked along with when this happened and the name of the session in which this occurred.
# and any other context which is loggable at that time"*). The census that motivated it: 2,049 of
# 2,371 entries said `session: unknown`, because this read a shell variable ONE guard set instead of
# the payload's own `session_id`; the command was cut at 200 characters; nothing recorded the cwd, the
# tool, or what the guard was thinking. `utc` was already "when". `detail` stays, truncated, for the
# existing readers; `command` is the whole thing; `context` is the guard's own decision inputs, when
# it passes them. THE NAME IS RESOLVED NOW, NOT AT READ TIME: the transcripts a later lookup would
# need are pruned after 30 days, and the name is the GM's stated requirement - so it costs the claim
# map's one file read on every firing (do not "optimize" this away; a name not recorded at firing
# time cannot be recovered), and the transcript scan only for a session that has never claimed a
# clone. The name is the CLONE's directory name - the project's identity for a session - not the
# verbatim /rename title. The payload ($INPUT) reaches the writer on stdin: an environment variable
# has a size limit a heredoc-carrying command can exceed.
#
# THE ENTRY IS THE GUARD'S RUST (feature 449 T143, the round arbiter's `ask:449-phase4-slices` Q12): `l7r-gate log guard`, over the
# guard's one writer (`rust/guard/shared/src/log.rs`) and its one resolver of the session's clone (`shared/src/session.rs`), where this ran
# two Python starts (`clone-resolve.sh resolve`, deleted, and the writer) on every firing. The gate's binary, not the guard's: every
# caller but one has just run `l7r-gate.sh escape reason-ok`, and a suite's fixture tree stands `l7r-gate.sh` in as a link to the real
# one. `L7R_GATE_STALE_OK` and `L7R_GATE_NO_BUILD`: the one hook-time caller, `l7r-guard.sh`'s no-binary path, must never wait on a
# build, so the binary there is runs, stale or not; with none, that one caller writes its entry by `lib/failed-open-log.sh`, the one
# entry written without a binary (the plan review of T143). The directory, the session the caller's
# shell names (`SID`) and the tree the session's mirror falls back to are handed over here, as the Python read them from this shell.
guard_log() {
  _guard_log_write "$@" >/dev/null 2>&1 || true
  return 0
}

# _guard_log_write <guard> <event> <detail> [rule] [context-json] - the entry, its exit the writer's: 0 written, else not (no gate binary
# here, an unwritable log). Only `l7r-guard.sh`'s no-binary path reads it, to write its one entry without a binary when this did not.
_guard_log_write() {
  local here=${BASH_SOURCE[0]%/*}
  case "${BASH_SOURCE[0]}" in */*) ;; *) here=. ;; esac  # sourced by a bare name, from its own directory
  case "$here" in /*) ;; *) here="$(cd "$here" && pwd)" ;; esac
  printf '%s' "${INPUT:-}" | GUARD_LOG_DIR="${GUARD_LOG_DIR:-$HOME/.claude/guard-log}" L7R_GUARD_TREE="${here%/scripts/hooks/lib}" \
    L7R_GATE_STALE_OK=1 L7R_GATE_NO_BUILD=1 "$here/../../gates/l7r-gate.sh" log guard "$1" "$2" "$3" "${SID:-unknown}" "${4:-}" "${5:-}"
}
