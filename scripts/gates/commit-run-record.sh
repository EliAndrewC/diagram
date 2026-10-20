#!/usr/bin/env bash
# TOOL_RECORD: it writes the run record itself - dev/run-log/ is where its runs are seen (feature 406 T03, D162)
# commit-run-record.sh <result> [pointer] - a run commits its OWN record (feature 375 amendment 7, FR-033; FR-029 for the cohort).
#
# WHY. Every `make done` writes a record under dev/run-log/, a tracked file, and `sync-with-main.sh done` refuses an
# uncommitted tree - so every landing after a gate cost a commit by hand and a second try (twice on 2026-10-12 alone).
# `sync-with-main.sh` says "the procedure never writes your commit for you", and this keeps that: the record is the RUN's
# output, not the session's work, and only that one file is committed. The writer names it in <git dir>/<pointer> -
# `last-run-record` (the Makefile's LOGRUN, the default) or `last-cohort-record` (cohort_audit.write_record) - so no other
# file is swept in: dev/run-log/ also holds l7r/diagram/ci/runlog.py's entries, which are not this run's (the plan review).
# `git commit --only -- <path>` leaves anything the session has staged staged and uncommitted. The path may be in another
# work tree (a cohort's "before" leg in a detached worktree writes into its clone): it is committed there.
#
# Skipped inside a CodeBuild build (its checkout merges and pushes; a commit there is no session's) and outside a git work
# tree. Best-effort: a failure to commit costs the old manual commit, never the run's verdict - it always exits 0.
set -uo pipefail
result="${1:-recorded}"
pointer="${2:-last-run-record}"
[ -n "${CODEBUILD_BUILD_ID:-}" ] && exit 0
gitdir=$(git rev-parse --absolute-git-dir 2>/dev/null) || exit 0
[ -f "$gitdir/$pointer" ] || exit 0
path=$(cat "$gitdir/$pointer")
rm -f "$gitdir/$pointer"
[ -f "$path" ] || exit 0
root=$(git -C "$(dirname "$path")" rev-parse --show-toplevel 2>/dev/null) || exit 0
[ -n "$(git -C "$root" status --porcelain -- "$path")" ] || exit 0
case "$pointer" in last-cohort-record) what="the cohort's record" ;; *) what="the gate's run record" ;; esac
git -C "$root" add -- "$path" 2>/dev/null || exit 0
git -C "$root" commit -q --only -m "$what ($result)" -- "$path" >/dev/null 2>&1 \
  && printf 'record committed (%s): %s\n' "$result" "${path#"$root"/}" \
  || git -C "$root" reset -q -- "$path" 2>/dev/null
exit 0
