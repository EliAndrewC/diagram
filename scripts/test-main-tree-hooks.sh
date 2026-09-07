#!/usr/bin/env bash
# test-main-tree-hooks.sh - prove main-tree-hooks.sh MOVES a write that would land in the mirror to the
# session's clone, REFUSES one that names the mirror, and leaves everything else alone.
# (GUARD_EDIT_OK: feature 204 - the verdict changed shape; the 2026-08-30 incidents are rewrites now, and
# the suite replays the 173-command corpus the rework was measured on.)
#
# THREE DIRECTIONS. (1) The rewrites: every shape feature 169/170 refused because the write would have
# landed in main THROUGH THE SHELL - both real incidents, a write while standing in main, a cd deeper
# into main - is rewritten into the clone and the rewritten command is itself clean. (2) The refusals
# that remain: a write that NAMES main, an unresolvable or missing clone, a shape that cannot be
# rebuilt. (3) The correct work the old guard refused: the corpus, replayed, with ZERO refusals.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/main-tree-hooks.sh"
PASS=0; FAIL=0
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
export GUARD_LOG_DIR="$T/guard-log"
# The resolver's sessions-json fallback reads $HOME; the suite must never resolve a REAL session.
export HOME="$T/home"; mkdir -p "$HOME"

# A fake mirror with a clone under it, so the guard's own derivation (toplevel, minus /.clones/<name>)
# is exercised rather than stubbed - and the CLAIM MAP clone-sync writes at a session's first edit,
# naming session "t" -> the worker clone, which is what `clone-sync-hooks.sh resolve` reads first.
MAIN=$T/diagram
git init -q "$MAIN"; git -C "$MAIN" config user.email t@t; git -C "$MAIN" config user.name t
echo a > "$MAIN/f"; mkdir -p "$MAIN/specs"; git -C "$MAIN" add f; git -C "$MAIN" commit -qm a
mkdir -p "$MAIN/.clones/.session-clones"; git clone -q "$MAIN" "$MAIN/.clones/worker"
WORKER=$MAIN/.clones/worker
printf '%s' "$WORKER" > "$MAIN/.clones/.session-clones/t"
printf '%s' "$MAIN/.clones/ghost" > "$MAIN/.clones/.session-clones/ghost"   # a claimed clone that was never created

SID=t
run() { # run <cwd> <command> -> RC, and OUT (stdout+stderr: the hook JSON on a rewrite, the refusal on a block)
  OUT=$(cd "$1" && printf '{"session_id":"%s","cwd":"%s","tool_name":"Bash","transcript_path":"%s/none.jsonl","tool_input":{"command":%s}}' \
        "$SID" "$1" "$T" "$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$2")" | "$HOOK" pretool 2>&1); RC=$?
}
check() { if [ "$2" = "$3" ]; then printf 'ok    %s (rc=%s)\n' "$1" "$3"; PASS=$((PASS+1));
          else printf 'FAIL  %s (expected rc=%s, got rc=%s)\n      out: %s\n' "$1" "$2" "$3" "$OUT"; FAIL=$((FAIL+1)); fi; }
rewritten() { # rewritten <label> <substring the rewritten command must carry>
  local got; got=$(printf '%s' "$OUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["hookSpecificOutput"]["updatedInput"]["command"])' 2>/dev/null)
  case "$got" in *"$2"*) printf 'ok    %s\n' "$1"; PASS=$((PASS+1));;
    *) printf 'FAIL  %s\n      rewritten to: %s\n      out: %s\n' "$1" "$got" "$OUT"; FAIL=$((FAIL+1));; esac
  REWRITTEN=$got
}
untouched() { # untouched <label> - allowed, and NOT rewritten
  case "$OUT" in *updatedInput*) printf 'FAIL  %s - rewrote a command it should have left alone: %s\n' "$1" "$OUT"; FAIL=$((FAIL+1));;
    *) printf 'ok    %s\n' "$1"; PASS=$((PASS+1));; esac
}
says() { case "$OUT" in *"$2"*) printf 'ok    %s\n' "$1"; PASS=$((PASS+1));; *) printf 'FAIL  %s - text lacks: %s\n      out: %s\n' "$1" "$2" "$OUT"; FAIL=$((FAIL+1));; esac; }

echo "--- 1. a write that would land in the mirror THROUGH THE SHELL is moved to the clone ---"
# THE TWO REAL INCIDENTS OF 2026-08-30, in the shape they actually took - refused by 169, rewritten now.
run "$WORKER" "cd $MAIN && git add -A && git commit -m 'work'"
check "the 166 incident: cd into the mirror, then add and commit -> rewritten (rc 0)" 0 "$RC"
rewritten "  ...the cd now names the clone" "cd $WORKER && git add -A && git commit -m 'work'"
says "  ...and the context says the command cd'd into the mirror" "cd'd into $MAIN"
run "$WORKER" "cd $MAIN; echo x > specs/163/request.md"
check "the 163 incident: cd into the mirror, then a redirect into a file -> rewritten" 0 "$RC"
rewritten "  ...the cd now names the clone, the rest untouched" "cd $WORKER; echo x > specs/163/request.md"
run "$WORKER" "cd $MAIN && sed -i 's/a/b/' f";       check "cd into the mirror, then sed -i -> rewritten" 0 "$RC"
run "$WORKER" "cd $MAIN && make done";               check "cd into the mirror, then make -> rewritten" 0 "$RC"
rewritten "  ...to make in the clone" "cd $WORKER && make done"
run "$WORKER" "( cd $MAIN && echo x > f )";          check "the subshell form into the mirror -> rewritten" 0 "$RC"
rewritten "  ...inside the subshell" "( cd $WORKER && echo x > f )"
run "$WORKER" "cd $MAIN/specs && echo x > f";        check "cd DEEPER into the mirror -> rewritten" 0 "$RC"
rewritten "  ...to the same subdirectory of the clone" "cd $WORKER/specs && echo x > f"

# THE SHAPE THAT ACTUALLY HAPPENED 146 TIMES: the shell already standing in the mirror, no cd at all.
run "$MAIN" "git add -A && git commit -m work"
check "STANDING in the mirror, a commit -> rewritten" 0 "$RC"
rewritten "  ...with cd <clone> prepended" "cd $WORKER && git add -A && git commit -m work"
says "  ...and the context names the real cause: the shell was standing in the mirror" "shell was standing in $MAIN"
says "  ...and gives the read route" "git -C $MAIN <read>"
run "$MAIN" "echo x > notes.md";                     check "standing in the mirror, a relative redirect -> rewritten" 0 "$RC"
run "$MAIN/specs" "echo x > f";                      check "standing in a SUBDIRECTORY of the mirror -> rewritten" 0 "$RC"
rewritten "  ...to the same subdirectory of the clone" "cd $WORKER/specs && echo x > f"
run "$MAIN" "python3 -c 'print(1)'";                 check "standing in the mirror, python3 -c (spec D5: still a write) -> rewritten, free" 0 "$RC"
run "$MAIN" "cd \$UNSET && git commit -am x";        check "standing in the mirror, cd through an UNSET variable (D6: unknown resolves toward main) -> rewritten" 0 "$RC"
run "$MAIN" "grep -rn MAIN_TREE_OK scripts/ && git commit -am x"
check "the escape token merely GREPPED for -> not an escape; rewritten like any other" 0 "$RC"
rewritten "  ...into the clone" "cd $WORKER && grep -rn MAIN_TREE_OK"

# THE REWRITE IS CLEAN: fed back through the guard from the same cwd, it is allowed untouched.
run "$MAIN" "git add -A && git commit -m work"; rewritten "  (rewrite to re-judge)" "cd $WORKER"
run "$MAIN" "$REWRITTEN";                            check "the rewritten command, re-judged from the mirror -> allowed" 0 "$RC"
untouched "  ...and not rewritten again"

echo "--- 2. what is still refused, and the refusal names the ACTUAL cause ---"
run "$WORKER" "git -C $MAIN commit -am x";           check "a write that NAMES the mirror (git -C) -> refused" 2 "$RC"
says "  ...as 'names a path inside the mirror'" "names a path inside the mirror"
run "$WORKER" "echo x > $MAIN/notes.md";             check "a redirect that names the mirror -> refused" 2 "$RC"
run "$MAIN" "sed -i 's/a/b/' $MAIN/f";               check "sed -i on a path inside the mirror -> refused" 2 "$RC"
run "$WORKER" "cd $MAIN && git commit -am x  # MAIN_TREE_OK"
check "an escape with NO reason -> refused (feature 170)" 2 "$RC"
SID=nobody
run "$MAIN" "git commit -am x";                      check "standing in the mirror, a session whose clone cannot be resolved -> refused" 2 "$RC"
says "  ...saying so" "cannot be resolved"
SID=ghost
run "$MAIN" "git commit -am x";                      check "a claimed clone that does not exist -> refused" 2 "$RC"
says "  ...with the command that creates it" "git clone $MAIN $MAIN/.clones/ghost"
SID=t
run "$MAIN" "f() { echo hi; }; git commit -am x";    check "a command opening with a function definition (cd && would be a syntax error) -> refused" 2 "$RC"
says "  ...as a shape that could not be rewritten" "could not be rewritten"
case "$OUT" in *"git -C $MAIN"*) printf 'ok    every refusal still gives the git -C read route\n'; PASS=$((PASS+1));;
  *) printf 'FAIL  the refusal does not give the route\n'; FAIL=$((FAIL+1));; esac

echo "--- 3. correct work is untouched (the half that decides whether this guard survives) ---"
run "$WORKER" "cd $MAIN && git log --oneline -5";    check "a READ in the mirror after a cd -> allowed" 0 "$RC"; untouched "  ...untouched"
run "$WORKER" "cd $MAIN && git status --short";      check "git status in the mirror -> allowed" 0 "$RC"
run "$WORKER" "git -C $MAIN log --oneline -1";       check "git -C read, no cd at all -> allowed" 0 "$RC"
run "$WORKER" "cd $WORKER && git commit -am work";   check "a commit in a CLONE under the mirror -> allowed" 0 "$RC"; untouched "  ...untouched"
run "$WORKER" "( cd $WORKER && make quick )";        check "the documented subshell form in a clone -> allowed" 0 "$RC"
run "$WORKER" "git commit -am work";                 check "an ordinary commit with no cd -> allowed" 0 "$RC"
run "$WORKER" "cd \$UNSET && git commit -am x";      check "cd through an unset variable FROM A CLONE -> allowed (D6 only pulls toward main)" 0 "$RC"
run "$MAIN" "( cd $WORKER && git commit -am work )"; check "STANDING IN MAIN, the subshell form into a clone -> allowed" 0 "$RC"
run "$MAIN" "( cd $WORKER && echo x > f )";          check "standing in main, subshell into a clone, then a redirect -> allowed" 0 "$RC"
run "$MAIN" "cd $WORKER && git commit -am work";     check "standing in main, but cd INTO A CLONE first -> allowed" 0 "$RC"
run "$MAIN" "cd /tmp && echo x > f";                 check "standing in main, cd right out of the tree -> allowed" 0 "$RC"
run "$MAIN" "git log --oneline -5";                  check "a READ while standing in the mirror -> allowed" 0 "$RC"
run "$MAIN" "git status --short";                    check "git status while standing in the mirror -> allowed" 0 "$RC"
run "$MAIN" "grep -h X /tmp/f 2>/dev/null";          check "a read with 2>/dev/null while standing in main -> allowed" 0 "$RC"
run "$MAIN" "git log --oneline 2>&1 | head -3";      check "a read with 2>&1 -> allowed" 0 "$RC"
# THE 146: the shell in the mirror, the write somewhere else. Every one of these was refused by 170.
run "$MAIN" "git log > /tmp/out";                    check "standing in main, a redirect to /tmp -> allowed (the write lands in /tmp)" 0 "$RC"; untouched "  ...untouched"
run "$MAIN" "$(printf "cat > /tmp/x.py <<'PY'\nprint(1)\nPY")"
check "standing in main, a heredoc into /tmp -> allowed" 0 "$RC"
run "$MAIN" "C=$WORKER; git -C \$C rm -q f";        check "standing in main, git -C through a variable assigned in the command -> allowed" 0 "$RC"
run "$MAIN" "R=$WORKER; cd \$R && git add -A && git commit -q -m x"
check "standing in main, cd through a variable naming a clone -> allowed" 0 "$RC"; untouched "  ...untouched"
run "$MAIN" "S=/tmp; ( cd \$S && cat > m.py <<'PY'
import x
PY
)";                                                  check "standing in main, subshell through a variable into /tmp with a heredoc -> allowed" 0 "$RC"
run "$MAIN" "SP=/tmp/claude-1000/-diagram/abc/scratchpad; cat > \$SP/phases.py <<'PY'
import boto3
PY";                                                 check "the commonest corpus shape (a scratchpad path that CONTAINS '-diagram') -> allowed" 0 "$RC"
run "$MAIN" "cp $MAIN/f /tmp/";                      check "copying FROM the mirror is a read -> allowed" 0 "$RC"
run "$MAIN" "mkdir -p /tmp/x/y && touch /tmp/x/y/z"; check "mkdir and touch under /tmp -> allowed" 0 "$RC"
run "$MAIN" "$(printf "python3 - <<'PY'\nprint(1)\nPY")"
check "a python heredoc while standing in main (not in the write list, as before) -> allowed" 0 "$RC"
run "$MAIN" "curl -s https://example.org -o /tmp/page.html"; check "curl -o into /tmp -> allowed" 0 "$RC"

echo "--- 4. a MENTION is not an invocation; the escape is ---"
run "$WORKER" "git commit -m 'never cd $MAIN && git commit - name the tree instead'"
check "the pattern quoted inside a commit message -> allowed" 0 "$RC"; untouched "  ...untouched"
run "$WORKER" "$(printf 'python3 - <<PY\ntext = "cd %s && git commit"\nPY' "$MAIN")"
check "the pattern inside a heredoc body -> allowed" 0 "$RC"
run "$WORKER" "cd $MAIN && git commit -am x  # MAIN_TREE_OK: render-sync, by hand, GM asked"
check "a real escape -> allowed, and NOT rewritten (the session said what it meant)" 0 "$RC"; untouched "  ...untouched"
run "$MAIN" "git commit -am x  # MAIN_TREE_OK: render-sync by hand"
check "standing in the mirror, escaped WITH a reason -> allowed" 0 "$RC"; untouched "  ...untouched"

echo "--- 5. THE CORPUS: every command the old guard refused, replayed with its recorded cwd ---"
# /diagram in the recorded cwd and commands becomes the fake mirror; session "t" resolves to the
# worker clone. The expected split is stated in the fixture and asserted exactly - a change in the
# judge that moves a single command between allow and rewrite fails here and says which.
REPLAY=$(python3 - "$HERE/fixtures/main-tree-refusals-2026-09.json" "$HOOK" "$MAIN" "$T" <<'PY'
import json, os, re, subprocess, sys, collections
fixture, hook, main, t = sys.argv[1:5]
data = json.load(open(fixture))
want = data["expected"]
# /diagram as a path ROOT only: `l7r/diagram/x.py` and `.claude/skills/diagram` are relative paths that
# merely CONTAIN it (the first cut substituted those too and turned three reads into named writes).
sub = lambda s: re.sub(r"(?<![\w./-])/diagram(?=/|[\s\"';&|):]|$)", main, s)
got = collections.Counter(); wrong = []
for i, row in enumerate(data["rows"]):
    cwd, cmd = sub(row["cwd"]), sub(row["command"])
    os.makedirs(cwd, exist_ok=True)  # the recorded cwd must EXIST: the resolver derives the mirror from it through git
    payload = json.dumps({"session_id": "t", "cwd": cwd, "tool_name": "Bash", "transcript_path": t + "/none.jsonl", "tool_input": {"command": cmd}})
    p = subprocess.run([hook, "pretool"], input=payload, capture_output=True, text=True, cwd=main)
    v = "refused" if p.returncode == 2 else ("rewrote" if "updatedInput" in p.stdout else "allowed") if p.returncode == 0 else f"rc{p.returncode}"
    got[v] += 1
    if v != row["verdict"]:
        wrong.append(f"row {i} ({row['ts']}): expected {row['verdict']}, got {v}: {cmd[:100]!r}")
print(json.dumps({"got": got, "want": want, "wrong": wrong[:8], "n_wrong": len(wrong), "rows": len(data["rows"])}))
PY
)
python3 -c '
import json, sys
r = json.loads(sys.argv[1])
ok = r["got"].get("refused", 0) == 0 and r["got"] == r["want"] and r["n_wrong"] == 0
print(("ok    " if ok else "FAIL  ") + f"the corpus: {r[chr(114)+chr(111)+chr(119)+chr(115)]} commands -> {dict(r[chr(103)+chr(111)+chr(116)])} (expected {r[chr(119)+chr(97)+chr(110)+chr(116)]})")
for w in r["wrong"]: print("      " + w)
sys.exit(0 if ok else 1)' "$REPLAY" && PASS=$((PASS+1)) || FAIL=$((FAIL+1))

echo "--- 6. it records, with a rule slug and the fields an audit needs (features 168 and 204) ---"
rules=$(python3 -c "
import json,glob,os,collections
rows=[json.load(open(f)) for f in glob.glob(os.path.join('$GUARD_LOG_DIR','*.json'))]
print(dict(collections.Counter((r['event'], r.get('rule')) for r in rows)))
named=[r for r in rows if r.get('rule')=='named-main']
print('FIELDS', named[0]['session'], named[0]['session_name'], named[0]['cwd']=='$WORKER', named[0]['tool'], len(named[0]['command'])>0, named[0]['context']['verdict'])" 2>/dev/null)
for want in "'rewrote', 'moved-to-clone'" "'blocked', 'named-main'" "'blocked', 'clone-unresolved'" "'blocked', 'clone-missing'" "'blocked', 'shape'" "'escaped', 'main-tree-ok'" "'blocked', 'MAIN_TREE_OK-no-reason'"; do
  case "$rules" in *"($want)"*) printf 'ok    records (%s)\n' "$want"; PASS=$((PASS+1));;
    *) printf 'FAIL  did not record (%s): %s\n' "$want" "$rules"; FAIL=$((FAIL+1));; esac
done
case "$rules" in *"FIELDS t worker True Bash True refuse"*) printf 'ok    an entry carries session, session_name (from the claim map), cwd, tool, command and the verdict\n'; PASS=$((PASS+1));;
  *) printf 'FAIL  the entry fields: %s\n' "$rules"; FAIL=$((FAIL+1));; esac

echo "-----"
printf 'test-main-tree-hooks: passed %s, failed %s\n' "$PASS" "$FAIL"
[ "$FAIL" = 0 ] || exit 1
