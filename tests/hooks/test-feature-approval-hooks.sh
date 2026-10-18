#!/usr/bin/env bash
# Tests for feature-approval-hooks.sh and its decider lib/hm_approval.py (feature 377).
# Run: tests/hooks/test-feature-approval-hooks.sh   (exit 0 = all green)
#
# Every case drives the REAL hook with a REAL payload over a REAL git tree and a fixture transcript, because a grep
# proves a call site exists and not that it fires.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/../../scripts/hooks/feature-approval-hooks.sh"
PASS=0; FAIL=0
LOGROOT=$(mktemp -d); export GUARD_LOG_DIR="$LOGROOT"
FIX=$(mktemp -d); TR=$(mktemp -d)
trap 'rm -rf "$LOGROOT" "$FIX" "$TR"' EXIT

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

git -C "$FIX" init -q 2>/dev/null
git -C "$FIX" config user.email t@t >/dev/null 2>&1
git -C "$FIX" config user.name t >/dev/null 2>&1
mkdir -p "$FIX/specs/376-older-feature" "$FIX/specs/377-held-feature"
printf '# 376\n\n**Status**: Filed - no approval line, and none owed\n' > "$FIX/specs/376-older-feature/spec.md"
printf '# 377\n\n**Status**: Filed\n' > "$FIX/specs/377-held-feature/spec.md"
printf 'x\n' > "$FIX/README.md"
git -C "$FIX" add -A >/dev/null 2>&1
git -C "$FIX" commit -qm base >/dev/null 2>&1

# a transcript: the GM's typed prompt, a headless session's prompt (sdk), a harness notice (isMeta), and an
# AskUserQuestion with the GM's answer
python3 - "$TR/t.jsonl" <<'PY'
import json, sys
recs = [
    {"type": "user", "isMeta": True, "message": {"role": "user", "content": "<system-reminder> please file feature 380 for the widgets </system-reminder>"}},
    {"type": "user", "origin": {"kind": "human"}, "promptSource": "typed", "entrypoint": "cli",
     "message": {"role": "user", "content": "Yes, please file  a feature for the\nwidget cache ’cause it’s slow."}},
    {"type": "user", "promptSource": "sdk", "entrypoint": "sdk-cli", "message": {"role": "user", "content": "File a feature for the gizmo audit."}},
    {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "q1", "name": "AskUserQuestion", "input": {}}]}},
    {"type": "user", "toolUseResult": {"questions": [], "answers": {"Shall I file feature 381 for the sprocket?": "File it"}},
     "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "q1",
     "content": "Your questions have been answered: \"Shall I file feature 381 for the sprocket?\"=\"File it\""}]}},
    {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "q2", "name": "AskUserQuestion", "input": {}}]}},
    {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "q2",
     "content": "The user doesn't want to proceed with this tool use. Shall I file feature 382 for the flange?"}]}},
    {"type": "attachment", "attachment": {"type": "queued_command", "commandMode": "prompt", "origin": {"kind": "human"},
     "prompt": "Yes, please go ahead and file this as a feature"}},
    {"type": "attachment", "attachment": {"type": "queued_command", "commandMode": "prompt", "origin": {"kind": "peer"},
     "prompt": "Relayed: please file the bracket feature now"}},
    {"type": "attachment", "attachment": {"type": "queued_command", "commandMode": "task-notification",
     "prompt": "<task-notification> file the hinge feature </task-notification>"}},
    {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "other",
     "content": "file a feature for the doohickey right away"}]}},
]
open(sys.argv[1], "w").write("\n".join(json.dumps(r) for r in recs) + "\n")
PY

run() {  # run <command> -> stderr+stdout, rc in RC
  OUT=$(python3 -c 'import json,sys; print(json.dumps({"session_id":"t","tool_name":"Bash","transcript_path":sys.argv[2],"tool_input":{"command":sys.argv[1]}}))' "$1" "$TR/t.jsonl" \
        | ( cd "$FIX" && "$HOOK" pretool 2>&1 )); RC=$?
}
spec() {  # spec <dir> <approval line or empty>
  mkdir -p "$FIX/specs/$1"
  printf '# %s\n\n**Status**: Filed\n\n%s\n' "$1" "$2" > "$FIX/specs/$1/spec.md"
}
clean() { git -C "$FIX" reset -q >/dev/null 2>&1; rm -rf "$FIX/specs/378-"* "$FIX/specs/379-"* "$FIX/specs/381-"* "$FIX/specs/390-"*; }

echo "1. a new feature with no approval line is refused, at add and at commit"
spec 378-widget-cache ""
run "git add -A"
[ "$RC" -eq 2 ] && ok "git add -A of a new 378 with no line is blocked" || no "add not blocked" "(rc=$RC)"
printf '%s' "$OUT" | grep -q "specs/378-widget-cache/spec.md: no approval line" && ok "...naming the file and the failed check" || no "the refusal names neither"
printf '%s' "$OUT" | grep -q '\*\*Approved\*\*: the GM, [0-9-]*, "<the GM' && ok "...and giving the exact line to add" || no "the line's form is missing"
printf '%s' "$OUT" | grep -qi "escape" && printf '%s' "$OUT" | grep -q "There is no escape variable" && ok "...and saying there is no escape" || no "the no-escape sentence is missing"
! printf '%s' "$OUT" | grep -q "before the command" && ok "...with no write-then-land note when the command touches no spec.md" || no "the note fired on a plain add"
# GUARD_EDIT_OK: feature 383, the round arbiter's tooling fix on hour:383@6 - a command that writes the line and lands in one go
run "printf '**Approved**: x\n' >> specs/378-widget-cache/spec.md && git add -A"
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q "before the command" && printf '%s' "$OUT" | grep -q "approval line in its own" && ok "a command that writes the spec.md and adds in one go is told the guard read the file before it ran, and the fix" || no "the write-then-land note is missing" "(rc=$RC)"
git -C "$FIX" add -A >/dev/null 2>&1
run "git commit -m wip"
[ "$RC" -eq 2 ] && ok "git commit of the staged spec is blocked too" || no "commit not blocked" "(rc=$RC)"
run "git -C $FIX commit -qm wip"
[ "$RC" -eq 2 ] && ok "...also as git -C <dir> commit" || no "git -C commit not blocked" "(rc=$RC)"
clean

echo "2. the quote must be the GM's, from this session, and three words or more"
spec 378-widget-cache '**Approved**: the GM, 2026-10-10, "Yes"'
run "git add specs"
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q "under three words" && ok "a one-word quote is refused as too short" || no "a short quote passed" "(rc=$RC)"
spec 378-widget-cache '**Approved**: the GM, 2026-10-10, "please file a feature for the gadget"'
run "git add specs"
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q "in no message the GM wrote" && ok "words the GM never wrote are refused" || no "a foreign quote passed" "(rc=$RC)"
spec 378-widget-cache '**Approved**: the GM, 2026-10-10, "File a feature for the gizmo audit."'
run "git add specs"
[ "$RC" -eq 2 ] && ok "a headless session's prompt (promptSource sdk) is not the GM's" || no "an sdk prompt counted as the GM" "(rc=$RC)"
spec 378-widget-cache '**Approved**: the GM, 2026-10-10, "please file feature 380 for the widgets"'
run "git add specs"
[ "$RC" -eq 2 ] && ok "a harness notice (isMeta) is not the GM's" || no "an isMeta record counted as the GM" "(rc=$RC)"
spec 378-widget-cache '**Approved**: the GM, 2026-10-10, "file a feature for the doohickey right away"'
run "git add specs"
[ "$RC" -eq 2 ] && ok "an ordinary tool result is not the GM's" || no "a tool result counted as the GM" "(rc=$RC)"
spec 378-widget-cache '**Approved**: the GM, 2026-10-10, "please file a feature for the widget cache '"'"'cause it'"'"'s slow"'
run "git add specs"
[ "$RC" -eq 0 ] && ok "the GM's typed words pass, whitespace and curly apostrophes normalized" || no "the GM's own words were refused" "(rc=$RC) $OUT"
git -C "$FIX" add -A >/dev/null 2>&1
run "git commit -m 'file 378'"
[ "$RC" -eq 0 ] && ok "...and the commit passes" || no "the approved commit was refused" "(rc=$RC)"
clean
spec 381-sprocket '**Approved**: the GM, 2026-10-10, ""Shall I file feature 381 for the sprocket?"="File it""'
run "git add -A"
[ "$RC" -eq 0 ] && ok "an AskUserQuestion answer quoted with its question passes" || no "the GM's picked answer was refused" "(rc=$RC) $OUT"
clean
spec 381-sprocket '**Approved**: the GM, 2026-10-10, "Shall I file feature 382 for the flange?"'
run "git add -A"
[ "$RC" -eq 2 ] && ok "a declined question (the harness's note, no answer) approves nothing" || no "a declined question counted" "(rc=$RC)"
spec 381-sprocket '**Approved**: the GM, 2026-10-10, "Yes, please go ahead and file this as a feature"'
run "git add -A"
[ "$RC" -eq 0 ] && ok "a message the GM sent mid-turn (a queued_command, origin human) passes" || no "the GM's mid-turn message was refused" "(rc=$RC) $OUT"
spec 381-sprocket '**Approved**: the GM, 2026-10-10, "please file the bracket feature now"'
run "git add -A"
[ "$RC" -eq 2 ] && ok "a peer session's relayed message is not the GM's" || no "a peer relay counted as the GM" "(rc=$RC)"
spec 381-sprocket '**Approved**: the GM, 2026-10-10, "file the hinge feature"'
run "git add -A"
[ "$RC" -eq 2 ] && ok "a task notification is not the GM's" || no "a task notification counted as the GM" "(rc=$RC)"
clean

echo "3. what is not new, and what is below the line, is not checked"
printf '\nmore text\n' >> "$FIX/specs/377-held-feature/spec.md"
run "git add -A"
[ "$RC" -eq 0 ] && ok "an edit to a feature HEAD already holds passes" || no "an existing feature was refused" "(rc=$RC)"
git -C "$FIX" checkout -q -- specs/377-held-feature/spec.md
git -C "$FIX" mv specs/377-held-feature specs/390-held-feature >/dev/null 2>&1
run "git commit -m renumber"
[ "$RC" -eq 0 ] && ok "a renumber (a staged rename) is not a new feature" || no "a renumber was refused" "(rc=$RC)"
git -C "$FIX" reset -q --hard >/dev/null 2>&1
mkdir -p "$FIX/specs/391-held-feature" && cp "$FIX/specs/377-held-feature/spec.md" "$FIX/specs/391-held-feature/spec.md"
run "git add specs/391-held-feature"
[ "$RC" -eq 2 ] && ok "a COPY beside a same-slug spec still in place is new, and refused" || no "a same-slug copy passed" "(rc=$RC)"
mv "$FIX/specs/377-held-feature" "$FIX/specs/377-gone"; rm -rf "$FIX/specs/377-gone"
run "git add -A"
[ "$RC" -eq 0 ] && ok "a renumber by plain move (the old spec gone, not yet staged as a rename) is not new" || no "an unstaged renumber was refused" "(rc=$RC) $OUT"
git -C "$FIX" reset -q --hard >/dev/null 2>&1; rm -rf "$FIX/specs/391-held-feature"

echo "3a. a MERGE that brings main's feature in is not filing it (feature 370's sync-in merged 377 and was refused)"
_base=$(git -C "$FIX" rev-parse HEAD)
git -C "$FIX" checkout -q --detach >/dev/null 2>&1
mkdir -p "$FIX/specs/395-landed-elsewhere" && printf '# 395\n\n**Status**: Filed - approved in its own session\n' > "$FIX/specs/395-landed-elsewhere/spec.md"
git -C "$FIX" add -A >/dev/null 2>&1 && git -C "$FIX" commit -qm "main's feature" >/dev/null 2>&1
_theirs=$(git -C "$FIX" rev-parse HEAD)
git -C "$FIX" checkout -q "$_base" >/dev/null 2>&1
git -C "$FIX" merge -q --no-ff --no-commit "$_theirs" >/dev/null 2>&1
run "git commit -m merge"
[ "$RC" -eq 0 ] && ok "a spec the merge's other side holds passes" || no "a merged-in feature was refused" "(rc=$RC) $OUT"
git -C "$FIX" merge --abort >/dev/null 2>&1; git -C "$FIX" checkout -q "$_base" >/dev/null 2>&1; rm -rf "$FIX/specs/395-landed-elsewhere"
mkdir -p "$FIX/specs/396-filed-here" && printf '# 396\n\n**Status**: Filed\n' > "$FIX/specs/396-filed-here/spec.md"
run "git add specs/396-filed-here"
[ "$RC" -eq 2 ] && ok "...and a new spec with no merge in progress is still refused" || no "a new spec passed with no merge" "(rc=$RC)"
rm -rf "$FIX/specs/396-filed-here"

echo "3b. a plain commit judges what is STAGED, not the working tree"
spec 378-widget-cache ""
git -C "$FIX" add -A >/dev/null 2>&1
spec 378-widget-cache '**Approved**: the GM, 2026-10-10, "Yes, please go ahead and file this as a feature"'
run "git commit -m staged-without-line"
[ "$RC" -eq 2 ] && ok "the staged copy has no line, so the commit is refused though the working tree has one" || no "a plain commit read the working tree" "(rc=$RC)"
clean
spec 378-add-thing ""
git -C "$FIX" add -A >/dev/null 2>&1
spec 378-add-thing '**Approved**: the GM, 2026-10-10, "Yes, please go ahead and file this as a feature"'
run "git commit -m x specs/378-add-thing/spec.md"
[ "$RC" -eq 2 ] && ok "...even when the path itself holds the word add (the subcommand decides, not the word)" || no "a slug holding 'add' made a plain commit read the working tree" "(rc=$RC)"
clean
mkdir -p "$FIX/specs/301-old-style"; printf '# 301\n' > "$FIX/specs/301-old-style/spec.md"
run "git add -A"
[ "$RC" -eq 0 ] && ok "a new directory numbered below 377 is never checked" || no "a pre-377 feature was refused" "(rc=$RC)"
rm -rf "$FIX/specs/301-old-style"
printf 'y\n' >> "$FIX/README.md"
run "git commit -am readme"
[ "$RC" -eq 0 ] && ok "a commit with no spec in it passes" || no "an unrelated commit was refused" "(rc=$RC)"
git -C "$FIX" checkout -q -- README.md
run "ls specs"
[ "$RC" -eq 0 ] && ok "a command that is no git add/commit passes untouched" || no "ls was refused" "(rc=$RC)"

echo "4. the refusal is recorded"
spec 379-unrecorded ""
run "git add -A"
ls "$LOGROOT"/*.json >/dev/null 2>&1 && grep -q '"guard": "feature-approval"' "$LOGROOT"/*.json && ok "a refusal writes a guard-log entry" || no "no guard-log entry"
clean

echo "5. it fires only because the hook calls the decider"
SANS=$(mktemp); sed 's#BAD=$(printf .*judge .*#BAD=""#' "$HOOK" > "$SANS"; chmod +x "$SANS"
spec 378-widget-cache ""
OUT2=$(python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","transcript_path":sys.argv[2],"tool_input":{"command":sys.argv[1]}}))' "git add -A" "$TR/t.jsonl" | ( cd "$FIX" && "$SANS" pretool 2>&1 )); RC2=$?
[ "$RC2" -eq 0 ] && ok "with the decider's call removed the same command passes - the test sees the guard, not a stub" || no "the stripped hook still blocked" "(rc=$RC2)"
rm -f "$SANS"; clean

echo "6. amendment 1: a feature reopened and LANDED open needs the GM's approval; reopened and closed again does not"
mkdir -p "$FIX/.specify" "$FIX/specs/300-closed-by-status" "$FIX/specs/301-closed-by-tasks" "$FIX/specs/302-still-open"
cp "$HERE/../../.specify/affects.json" "$FIX/.specify/"
printf '# 300\n\n**Status**: Done 2026-10-01 - measured\n' > "$FIX/specs/300-closed-by-status/spec.md"
printf '# 301\n\n**Status**: In progress\n' > "$FIX/specs/301-closed-by-tasks/spec.md"
printf -- '- [x] T01 a thing\n' > "$FIX/specs/301-closed-by-tasks/tasks.md"
printf '# 302\n\n**Status**: Filed - deferred\n' > "$FIX/specs/302-still-open/spec.md"
git -C "$FIX" add -A >/dev/null 2>&1; git -C "$FIX" commit -qm closed >/dev/null 2>&1
git -C "$FIX" update-ref refs/remotes/origin/main HEAD
commit() { git -C "$FIX" add -A >/dev/null 2>&1; git -C "$FIX" commit -qm "$1" >/dev/null 2>&1; }
push() { run "scripts/sync-with-main.sh done"; }
sed -i 's/^\*\*Status\*\*: Done.*/**Status**: Filed - more work found/' "$FIX/specs/300-closed-by-status/spec.md"; commit reopen
push
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q "specs/300-closed-by-status/spec.md: closed before, and this push lands it OPEN" && ok "a status reopen left open is refused at the push, naming the feature" || no "a reopen left open landed" "(rc=$RC) $OUT"
printf '%s' "$OUT" | grep -q "needs no approval: finish the work and close the feature" && ok "...and the refusal names finishing and closing first, no approval needed" || no "the reopen-is-fine sentence is missing"
[ "$(printf '%s' "$OUT" | grep -n "finish the work and close" | cut -d: -f1)" -lt "$(printf '%s' "$OUT" | grep -n "A feature is filed only when" | cut -d: -f1)" ] && ok "...before the approval route" || no "the approval route comes first"
run "cd $FIX && scripts/sync-with-main.sh push"
[ "$RC" -eq 2 ] && ok "...also as cd <clone> && sync-with-main.sh push" || no "the cd form was not read" "(rc=$RC)"
# GUARD_EDIT_OK: 2026-10-10 - a MENTION is no push: a plan reviewer's command writing JSON that named the command was refused
run "printf '%s' '{\"why\": \"lands by scripts/sync-with-main.sh done from the worktree\"}' > /dev/null"
[ "$RC" -eq 0 ] && ok "...but a command that only MENTIONS sync-with-main.sh done is no push" || no "a mention was read as a push" "(rc=$RC) $OUT"
run "FOO=1 /abs/scripts/sync-with-main.sh done"
[ "$RC" -eq 2 ] && ok "...while an env-prefixed absolute-path run still is" || no "the env/absolute form was not read" "(rc=$RC)"
sed -i 's/^\*\*Status\*\*: Filed.*/**Status**: Done 2026-10-10 - the more work done/' "$FIX/specs/300-closed-by-status/spec.md"; commit reclose
push
[ "$RC" -eq 0 ] && ok "reopened, worked and closed again within the push: no approval needed" || no "a reopen closed again was refused" "(rc=$RC) $OUT"
git -C "$FIX" update-ref refs/remotes/origin/main HEAD
printf -- '- [ ] T02 the next thing\n' >> "$FIX/specs/301-closed-by-tasks/tasks.md"; commit "reopen by a task"
push
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q "301-closed-by-tasks" && ok "a feature closed by its ticked tasks, reopened by a new task, is refused too" || no "a task reopen landed" "(rc=$RC)"
printf '\n**Approved**: the GM, 2026-10-10, "please file a feature for the gadget"\n' >> "$FIX/specs/301-closed-by-tasks/spec.md"; commit "foreign approval"
push
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q "quotes words the GM did not write" && ok "...and an added approval in words the GM never wrote does not let it land" || no "a foreign approval let a reopen land" "(rc=$RC)"
printf '\n**Approved**: the GM, 2026-10-10, "Yes, please go ahead and file this as a feature"\n' >> "$FIX/specs/301-closed-by-tasks/spec.md"; commit "the GM's approval"
push
[ "$RC" -eq 0 ] && ok "...but the GM's own words, added in the delta, do" || no "the GM's approval did not let the reopen land" "(rc=$RC) $OUT"
git -C "$FIX" update-ref refs/remotes/origin/main HEAD
printf '\nmore notes\n' >> "$FIX/specs/302-still-open/spec.md"; commit "an open feature edited"
push
[ "$RC" -eq 0 ] && ok "a feature already open at the base is not this check's" || no "an already-open feature was refused" "(rc=$RC)"
git -C "$FIX" update-ref refs/remotes/origin/main HEAD
printf -- '- [ ] T01 hidden work\n' > "$FIX/specs/300-closed-by-status/tasks.md"; commit "a task under Done"
push
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q "300-closed-by-status/spec.md: an unticked task added under a status line that still says closed" && ok "FR-012: an unticked task added under a Done status is refused" || no "hidden open work landed" "(rc=$RC) $OUT"
[ "$(printf '%s' "$OUT" | grep -n "do the work and tick the task" | cut -d: -f1)" -lt "$(printf '%s' "$OUT" | grep -n "A feature is filed only when" | cut -d: -f1)" ] && ok "...its refusal, too, leads with doing the work (tick the task) before the approval route" || no "FR-012's refusal leads with the approval"
printf '\n**Approved**: the GM, 2026-10-10, "please file a feature for the gadget"\n' >> "$FIX/specs/300-closed-by-status/spec.md"; commit "foreign approval under Done"
push
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q "a task added under a closed status; the approval line it adds quotes words" && ok "...and a foreign approval gets FR-012's own wording, not 'reopened'" || no "FR-012's not-found wording is wrong" "(rc=$RC) $OUT"
git -C "$FIX" reset -q --hard HEAD~1
sed -i 's/^- \[ \] T01/- [x] T01/' "$FIX/specs/300-closed-by-status/tasks.md"; commit "ticked"
push
[ "$RC" -eq 0 ] && ok "...and passes once the task is done and ticked" || no "a ticked task under Done was refused" "(rc=$RC)"
git -C "$FIX" update-ref refs/remotes/origin/main HEAD
printf -- '- [ ] T02 a leftover box, open when the feature closed\n' >> "$FIX/specs/300-closed-by-status/tasks.md"; commit "a leftover"
git -C "$FIX" update-ref refs/remotes/origin/main HEAD
sed -i 's/^- \[ \] T02/- [x] T02/' "$FIX/specs/300-closed-by-status/tasks.md"
printf -- '- [ ] T03 new work slipped in\n' >> "$FIX/specs/300-closed-by-status/tasks.md"; commit "tick one, add one"
push
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q "300-closed-by-status" && ok "ticking a leftover box and adding a new one (the count unchanged) is still refused" || no "tick-one-add-one landed hidden work" "(rc=$RC)"
sed -i 's/^- \[ \] T03/- [x] T03/' "$FIX/specs/300-closed-by-status/tasks.md"; commit "T03 done"
git -C "$FIX" update-ref refs/remotes/origin/main HEAD
# GUARD_EDIT_OK: feature 375 amendment 8 - the GM-review box `make accept` writes is tracked by make gm-review, not hidden work
printf -- '- [ ] GM review (make gm-reviewed F=300) [lands-open]\n' >> "$FIX/specs/300-closed-by-status/tasks.md"; commit "a row for the GM"
push
[ "$RC" -eq 0 ] && ok "...but the GM-review box make accept writes lands under Done: make gm-review holds it, not speckit-todo" || no "the GM-review box was refused as hidden work" "(rc=$RC) $OUT"
git -C "$FIX" update-ref refs/remotes/origin/main HEAD
run "make quick"
[ "$RC" -eq 0 ] && ok "a command that is neither a git add/commit nor a push passes untouched" || no "make quick was refused" "(rc=$RC)"

echo
echo "feature-approval: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
