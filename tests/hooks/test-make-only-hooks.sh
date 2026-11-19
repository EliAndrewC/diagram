#!/usr/bin/env bash
# Tests for the make-only guard (rust/guard, replayed through its link). Feeds PreToolUse events and asserts which commands are blocked.
# Run: tests/hooks/test-make-only-hooks.sh   (exit 0 = all green)
#
# TWO DIRECTIONS, ALWAYS (feature 127, FR-015 + FR-016). Section 1 proves the hook FIRES on every
# row of the threat model. Section 2 proves it STAYS QUIET on ordinary work - and that half is not a
# formality. A guard that fires on correct work teaches a session that the override is part of the
# normal routine, which is precisely how the documented-override workaround became habitual in the
# feature that motivated this one. A false positive here is a worse outcome than a false negative.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/make-only-hooks.sh"
# GUARD_EDIT_OK: feature 164 - this guard RECORDS its firings now (feature 162's log), so the suite
# must write its fixtures to a throwaway directory. Without it the suite pollutes `make audit`, whose
# whole purpose is to price a guard from real firings: 24 fixture entries appeared there the first
# time these conversions ran their suites.
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
# GUARD_EDIT_OK: 2026-09-26 - stderr is captured in a file of THIS run's own, not a fixed /tmp path that every
# concurrent hooks-test (one per session's gate) rewrote under the others (it failed the batching suite's greps).
HOOK_ERR=$(mktemp)
# the hook's answer, in a file of this run removed on exit: it was a fixed /tmp/mo.out, outside the suite's TMPDIR and so its leak
# check, left behind by every run (feature 449 T160)
MO_OUT=$(mktemp)
trap 'rm -rf "$GUARD_LOG_ROOT" "$HOOK_ERR" "$MO_OUT"' EXIT

PASS=0; FAIL=0

ev() { jq -nc '{"session_id":"m1","tool_name":"Bash","tool_input":{"command":$ARGS.positional[0]}}' --args -- "$1"; }
run() { ev "$1" | "$HOOK" pretool >"$MO_OUT" 2>"$HOOK_ERR"; echo $?; }

check() { # label expected(ok|blocked) command
  local rc; rc=$(run "$3")
  if { [ "$2" = ok ] && [ "$rc" -eq 0 ]; } || { [ "$2" = blocked ] && [ "$rc" -ne 0 ]; }; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else
    echo "  FAIL    $1 (expected $2, rc=$rc)"; FAIL=$((FAIL+1))
  fi
}

names_a_target() { # the refusal must say what to run instead (FR-006)
  local rc; rc=$(run "$2")
  if [ "$rc" -ne 0 ] && grep -q "Run this instead" "$HOOK_ERR" && grep -q "make " "$HOOK_ERR"; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else
    echo "  FAIL    $1 (refusal did not name a make target)"; FAIL=$((FAIL+1))
  fi
}

echo "1. IT FIRES - every row of the threat model (FR-015)"
check "tier 1: a cohort run bare"              blocked "python3 -m l7r.diagram.tools.cohort_audit --count 48"
check "tier 1: the generator run bare"         blocked "python3 -m l7r.diagram.hamletgen --batch 24"
check "tier 1: a pool sweep run bare"          blocked "python3 -m l7r.diagram.pipeline.regen pool/hamlets/inashiro/inashiro.gen.py"
check "tier 1: regen by script path"           blocked "python3 l7r/diagram/pipeline/regen.py pool/hamlets/x/x.gen.py"
check "tier 1: a bare cargo test (feature 444)" blocked "cargo test --manifest-path rust/phases/Cargo.toml"   # GUARD_EDIT_OK: feature 444 T17 - the bare-cargo rule's cases
check "tier 1: a bare cargo clippy, by path"   blocked "~/.cargo/bin/cargo clippy --all-targets"
check "make rust-test is the compliant form"   ok "make rust-test"
check "a word cargo in prose is a mention"     ok "git commit -m 'cargo test now goes through make'"
check "tier 2: the documented override"        blocked "make done FULL=1 REF_WHY=pre-push verification"
check "tier 2: the reference-gate override"    blocked "REF_OK=1 make maps"
check "tier 2: the -k gate override"           blocked "GATE_OK=1 make done"
# feature 385 T91 (plan D112): a landing of tooling is linted before it runs
LT="$(mktemp -d)"; printf 'x  =  1\n' > "$LT/bad.py"; printf 'x = 1\n' > "$LT/good.py"
lint_case() { printf '{"tool_name":"Bash","cwd":"%s","tool_input":{"command":"%s"}}' "$LT" "$2" | "$HOOK" pretool >/dev/null 2>"$HOOK_ERR"; [ "$?" "$1" 0 ]; }
if lint_case -ne 'make land-tooling FILES=bad.py'; then echo "  ok      a landing whose file fails the lint is refused before it runs"; PASS=$((PASS+1)); else echo "  FAIL    landing lint (bad)"; FAIL=$((FAIL+1)); fi
if lint_case -ne 'make arbiter-fix-done ID=x NOTE=y TEST=t LAND=bad.py'; then echo "  ok      ...and arbiter-fix-done LAND= too"; PASS=$((PASS+1)); else echo "  FAIL    landing lint (arbiter)"; FAIL=$((FAIL+1)); fi
if lint_case -eq 'make land-tooling FILES=good.py'; then echo "  ok      ...a clean file passes"; PASS=$((PASS+1)); else echo "  FAIL    landing lint (good)"; FAIL=$((FAIL+1)); fi
rm -rf "$LT"
# feature 385 T61 (plan D80): make keeps the last of two assignments of one variable, silently
check "one variable set twice on a make call"   blocked "make quote-verbatim Q=0018 Q=0027"
check "...the quoted list passes"               ok      'make quote-verbatim Q="0018 0027"'
check "...two variables pass"                   ok      "make record-owed Q=0018 IN=ways"
check "...one each on two calls passes"         ok      "make quote-verbatim Q=0018 && make quote-verbatim Q=0027"
check "...a mention in a message passes"        ok      "git log --grep 'make x Q=1 Q=2'"
rc=$(run "make quote-verbatim Q=0018 Q=0027")
if grep -q 'sets Q twice' "$HOOK_ERR" && grep -q 'Q=\"<a> <b>\"' "$HOOK_ERR"; then echo "  ok      ...the refusal names the variable and the quoted list"; PASS=$((PASS+1))
else echo "  FAIL    ...the refusal names the variable and the quoted list"; FAIL=$((FAIL+1)); fi
check "tier 4: a forged makefile"              blocked "make -f /tmp/evil.mk probe"
check "tier 4: --file spelling"                blocked "make --file /tmp/evil.mk probe"
check "tier 4: --makefile spelling"            blocked "make --makefile=/tmp/evil.mk probe"

echo
echo "2. IT STAYS QUIET - ordinary work must never be blocked (FR-016)"
check "the cheap check"                        ok "make quick"
check "the gate"                               ok "make done"
check "the full gate, no inline override"      ok "make done FULL=1"
check "a map sweep"                            ok "make maps"
check "the linters"                            ok "python3 -m ruff check . && pyrefly check"
check "git"                                    ok "git -C /gm-assistant/.clones/x status --porcelain"
check "the stop-work procedure"                   ok "./scripts/sync-with-main.sh done"
check "reading a source file"                  ok "grep -n 'def stage_ways' l7r/diagram/hamletgen/ways.py"
check "a hook's own test"                      ok "tests/hooks/test-make-only-hooks.sh"
check "an unrelated python one-liner"          ok "python3 -c 'print(1)'"
# A `|` or `;` INSIDE A QUOTED STRING is not a command separator (2026-08-25: a pip-freeze grep
# for the lockfile pins was blocked as a bare pytest run - the mention-versus-invocation defect).
check "a quoted regex naming pytest"           ok "pip freeze | grep -iE '^(numpy|pytest|ruff)=='"
check "a quoted message naming pytest"         ok "git commit -m 'gate: ruff clean; pytest green'"
check "a heredoc naming pytest"                ok "cat > requirements-dev.in <<'EOF'
pytest
pytest-cov
EOF"

# GUARD_EDIT_OK: feature 449 T213 - PYTEST IS NO LONGER THE GUARD'S: its targets left with it, so a run has nothing to be routed to
# and the bare-pytest branch went (and with it T214's defect, a pytest MENTION in a quoted `python3 -c` program refused as a run)
check "a bare pytest"                          ok      "python3 -m pytest -n auto"
check "a pipe into pytest"                     ok      'cat x | pytest -q'
check "a pytest word in a quoted -c program"   ok      "python3 -I -c 'print(\"pytest\")'"
check "grep -c with pytest in its pattern"     ok      'grep -c "a|pytest" notes.txt'
# GUARD_EDIT_OK: feature 449 T028 - FR-005: a replacement's binary goes through make too
names_a_target "the guards' binary run directly" "$HOME/.cache/l7r-cargo-target/x/release/l7r-guard --only a PreToolUse"
names_a_target "the hamlet binary run directly"  "target/release/hamlet pool/hamlets/x/x.spec.json"
names_a_target "the gate's binary run directly"  "$HOME/.cache/l7r-cargo-target/x/release/l7r-gate --version"
names_a_target "...from the tools' profile (T95)" "$HOME/.cache/l7r-cargo-target/x/tool/l7r-gate --version"
check "the gate's wrapper is not the binary"    ok      "scripts/gates/l7r-gate.sh --version"
check "the guards' wrapper is not the binary"  ok      "scripts/hooks/l7r-guard.sh --version"
check "make hamlet is the compliant form"      ok      "make hamlet SPEC=pool/hamlets/x/x.spec.json"

echo
echo "2b. TIER 5 VIA BASH - a guard file written by shell rather than the Edit tool"
check "heredoc python writing the Makefile"   blocked "python3 - <<PY
import pathlib; pathlib.Path('Makefile').write_text(x)
PY"
# feature 385 T121 (D143): T117's shape - a name bound to a plain string, written through open() - added a Makefile target unseen
check "open() writing the Makefile by name"   blocked "python3 - <<'EOF'
p=\"Makefile\"
t=open(p).read()
open(p,\"w\").write(t)
EOF"
check "open() writing a hook by literal"      blocked "python3 -c 'open(\"scripts/hooks/gate-hooks.sh\", \"a\").write(\"x\")'"
check "open() only reading the Makefile"      ok      "python3 - <<'EOF'
p=\"Makefile\"
print(open(p).read().count(\"tick\"), open(p, \"r\").read()[:10])
EOF"
check "sed -i on a hook script"               blocked "sed -i 's/foo/bar/' scripts/hooks/gate-hooks.sh"
check "redirect over settings.json"           blocked "cat > .claude/settings.json"
check "append to a hook script"               blocked "echo x >> scripts/hooks/no-poll-hooks.sh"
check "the escape, with a reason"             ok      "sed -i 's/a/b/' scripts/hooks/gate-hooks.sh  # GUARD_EDIT_OK: it fired on correct work"
# GUARD_EDIT_OK: the round arbiter's tooling fix on hour:383@4 - a marker counts as a trailing comment, never inside the
# text written (a whole-file rewrite carries the file's old markers), and the refusal says so
check "an append marked as a trailing comment"  ok      "printf 'x' >> Makefile  # GUARD_EDIT_OK: a measurement probe line"
check "an append marked in the text it writes"  blocked "printf '# GUARD_EDIT_OK: a measurement probe line' >> Makefile"
if grep -q "a marker INSIDE the text written does not count" "$HOOK_ERR"; then echo "  ok      ...and the refusal names the trailing-comment form"; PASS=$((PASS+1)); else echo "  FAIL    ...the refusal does not name the trailing-comment form"; FAIL=$((FAIL+1)); fi  # GUARD_EDIT_OK: hour:383@4
check "...and the bare append"                  blocked "printf 'x' >> Makefile"
check "READING a guard file is not writing"   ok      "grep -n done Makefile"
# GUARD_EDIT_OK: feature 375 - a hook's SUITE is not a guard (guard-file-hooks.sh exempts it on the Edit route)
check "a suite written by python is not a guard" ok   "python3 - <<PY
import pathlib; pathlib.Path('tests/hooks/test-pair-hooks.sh').write_text(x)
PY"
check "sed -i on a suite is not a guard write" ok     "sed -i 's/a/b/' tests/hooks/test-gate-hooks.sh"
check "...but its guard still is"             blocked "sed -i 's/a/b/' scripts/hooks/test-hooks.sh"
# GUARD_EDIT_OK: feature 217 - the roster of rolled hamlets is a guard on the shell route too
check "heredoc appending a roll row to the roster" blocked "cat >> tests/rolls.py <<EOF
Roll(SPEC, 'x', 'y')
EOF"
check "python writing the roster"                blocked "python3 - <<PY
import pathlib; pathlib.Path('tests/rolls.py').write_text(x)
PY"
check "writing the roster's TEST is ordinary"    ok      "cat >> tests/test_rolls.py <<EOF
x = 1
EOF"
check "READING the roster is not writing"        ok      "grep -n Roll tests/rolls.py"
# feature 449 T227 - a write is resolved through the command's own cd against THE guard list (guard_file_hooks::held), so the forms
# a pattern over the text missed are refused: cp, mv, install, perl -i, sed with -i not first, a cd into the file's directory, dev/*.json
check "T220's form: python3 - rewriting a hook by a bound name" blocked "cd /x && python3 - <<'EOF'
p='scripts/hooks/a-hooks.sh'; s=open(p).read()
open(p,'w').write(s)
EOF"
check "cp over the roster"                       blocked "cp /tmp/x tests/rolls.py"
check "a cd, then a heredoc into the switches"   blocked "cd dev && cat > switches.json <<'EOF'
{}
EOF"
check "perl -pi over the Makefile"               blocked "perl -pi -e 's/a/b/' Makefile"
check "sed -E -i over settings.json"             blocked "sed -E -i 's/a/b/' .claude/settings.json"
check "a cd into the suites is still a suite"    ok      "cd tests/hooks && cat > test-a-hooks.sh <<'EOF'
x
EOF"
check "review-gate.sh is no guard file"          ok      "cat > scripts/gates/review-gate.sh <<'EOF'
x
EOF"
# GUARD_EDIT_OK: feature 169 - two live false positives, both matched against the RAW command.
# The first REFUSED A COMMAND THAT WROTE NOTHING: an arrow in printed prose reads as a redirect.
check "an arrow in prose is not a redirect"   ok      "printf '5 mirror cd+write -> scripts/hooks/main-tree-hooks.sh (new)\n'"
check "a hook named in a commit message"      ok      "git commit -m 'edit scripts/hooks/gate-hooks.sh later'"
check "a stderr redirect is not a write"      ok      "make done 2> /tmp/log"
check "a heredoc DISCUSSING a hook"           ok      "cat <<'EOF' > /tmp/notes
see scripts/hooks/gate-hooks.sh
EOF"
check "writing a NON-guard file"              ok      "python3 - <<PY
import pathlib; pathlib.Path('notes.md').write_text(x)
PY"

# GUARD_EDIT_OK: feature 449 T029 - the constitution XIV fix: a scratch file whose text names a guard is not a guard write (found 2026-11-07)
check "a scratch file whose text names a guard"  ok      "cat >> /tmp/probe.py <<'EOF'
(root / 'scripts' / 'x-hooks.sh').write_text('echo guard')
EOF"
check "...but python running that text is a write" blocked "python3 - <<'EOF'
(root / 'scripts' / 'x-hooks.sh').write_text('echo guard')
EOF"
check "...and a heredoc into a guard file still is" blocked "cat >> Makefile <<'EOF'
x
EOF"
check "...and a body piped to python is run"       blocked "cat <<'EOF' | python3
open('Makefile', 'w').write('x')
EOF"
check "...and a body stored and run by the command is run" blocked "cat > /tmp/probe.py <<'EOF'
open('Makefile', 'w').write('x')
EOF
python3 /tmp/probe.py"
check "...and one chained on the heredoc's own line" blocked "cat > /tmp/probe.py <<'EOF' && python3 /tmp/probe.py
open('Makefile', 'w').write('x')
EOF"
check "...and one run through a glob after it"      blocked "cat > /tmp/g_1.py <<'EOF'
open('Makefile', 'w').write('x')
EOF
python3 /tmp/g_*.py"
check "...and an unquoted delimiter, whose body the shell runs" blocked "cat > /tmp/probe <<EOF
\$(python3 -c \"open('Makefile', 'w').write('x')\")
EOF"
check "...and a process substitution as cat's target" blocked "cat > >(bash) <<'EOF'
open('Makefile', 'w').write('x')
EOF"
check "...and a process substitution as tee's file"   blocked "tee >(bash) >/dev/null <<'EOF'
open('Makefile', 'w').write('x')
EOF"
check "...and an assignment that changes what cat runs" blocked "PATH=/tmp/d; cat > /tmp/f <<'EOF'
open('Makefile', 'w').write('x')
EOF"
check "...and a loader variable before it"            blocked "LD_PRELOAD=/tmp/x.so; cat > /tmp/f <<'EOF'
open('Makefile', 'w').write('x')
EOF"
check "a scratch file stored after an assignment"   ok      "S=/tmp/a; cat >> \$S/probe.py <<'EOF'
(root / 'scripts' / 'x-hooks.sh').write_text('echo guard')
EOF"

echo
echo "3. THE REFUSAL IS USEFUL (FR-006) - it must name the target, not just say no"
names_a_target "a blocked cohort names a target"  "python3 -m l7r.diagram.tools.cohort_audit"
names_a_target "a forged makefile names a target" "make -f /tmp/evil.mk x"

# GUARD_EDIT_OK: feature 449 T213 - section 4 (a targeted pytest run rewritten into `make test-file`, feature 212) left with pytest;
# its two helpers stay for the entry-point rewrites below
rewritten() { # label, command, the exact rewritten command
  ev "$2" | "$HOOK" pretool >"$MO_OUT" 2>"$HOOK_ERR"; local rc=$?
  local got; got=$(jq -r '.hookSpecificOutput.updatedInput.command // empty' < "$MO_OUT" 2>/dev/null)
  if [ "$rc" -eq 0 ] && [ "$got" = "$3" ]; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else
    echo "  FAIL    $1 (rc=$rc, got '${got:-<nothing>}', wanted '$3')"; FAIL=$((FAIL+1))
  fi
}
refused_because() { # label, command, the text the refusal must carry
  ev "$2" | "$HOOK" pretool >"$MO_OUT" 2>"$HOOK_ERR"; local rc=$?
  if [ "$rc" -ne 0 ] && grep -qF -- "$3" "$HOOK_ERR"; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else
    echo "  FAIL    $1 (rc=$rc; refusal did not name '$3')"; FAIL=$((FAIL+1))
  fi
}
echo
echo "5. AN ENGINE ENTRY POINT A MAKE TARGET WRAPS IS REWRITTEN INTO IT (feature 212)"
# the render sync stands in for `building_programs`, ported to Rust and deleted by feature 449 T168, and for the pool index, whose
# recipe runs the Rust pool walk since feature 449 T220 (GUARD_EDIT_OK: the stand-in moved, nothing loosened); the CHECK=1 form (a
# recipe's `$(if $(X),--flag,)`) no longer has a one-line Python recipe in the Makefile, and stays tested in make_only_hooks/tests.rs's fixture
rewritten "render sync -> make render-sync" "python3 -m l7r.diagram.pipeline.render_cache 2>&1 | grep -i complete" "make render-sync 2>&1 | grep -i complete"
refused_because "the Rust pool index wraps the Python one no more" "python3 -m l7r.diagram.pipeline.pool_index" "no make target wraps"
rewritten "a recipe's literal argument" "python3 -m l7r.diagram.switches show" "make switches"
refused_because "a ported module is wrapped no more" "python3 -m l7r.diagram.tools.building_programs --check" "no make target wraps"
# the compound draft stands in for `pack_audit`, whose recipe runs the Rust since feature 449 T175 (its `__main__.py` deleted)
refused_because "the ported audit is wrapped no more" "python3 -m l7r.diagram.tools.pack_audit wip/x.svg" "no make target wraps"
# the render sync stands in for the compound draft, whose recipe runs the Rust generator since feature 449 T152 (`compound.py` deleted)
rewritten "a \$(ARGS) recipe takes the rest" "python3 -m l7r.diagram.pipeline.render_cache wip/x.svg" 'make render-sync ARGS="wip/x.svg"'
refused_because "a module nothing wraps lists what is" "python3 -m l7r.diagram.tools.scatter_audit pool/hamlets/x" "no make target wraps"
refused_because "...and the list names a wrapped module" "python3 -m l7r.diagram.tools.scatter_audit pool/hamlets/x" "make render-sync"
refused_because "arguments the recipe cannot carry" "python3 -m l7r.diagram.switches --nonsense" "cannot carry"
refused_because "a multi-line recipe (REF_FIRST) does not wrap" "python3 -m l7r.diagram.hamletgen --seed 4" "no make target wraps"
ev "python3 -m l7r.diagram.pipeline.render_cache" | "$HOOK" pretool 2>/dev/null | grep -q "make render-sync" \
  && { echo "  ok      the context names the module and the target"; PASS=$((PASS+1)); } \
  || { echo "  FAIL    the entry-point rewrite's context is silent"; FAIL=$((FAIL+1)); }

echo
echo "6. FREE TEXT REACHES A RECIPE'S TOOL UNCHANGED, THE SHELL NEVER READING IT (feature 449 T186)"
# `make claims-bundle UNITS="...the required item is \`well\`"` ran `well`: the recipe put $(UNITS) inside a double-quoted shell
# word. The real Makefile (MAKEFILE_UNDER_TEST= runs this section on another copy, which is how its red was shown) is driven in a
# throwaway repository whose gate is a stub that writes the arguments and environment it was handed, one a line.
MK=${MAKEFILE_UNDER_TEST:-$HERE/../../Makefile}
FX="$GUARD_LOG_ROOT/make-fixture"; mkdir -p "$FX/scripts/gates" "$FX/dev"; cp "$MK" "$FX/Makefile"; echo '{}' > "$FX/dev/switches.json"
cat > "$FX/scripts/gates/l7r-gate.sh" <<'STUB'
#!/usr/bin/env bash
case "${1:-} ${2:-}" in "log "*|"switches show"|"switches idle"|"switches state") exit 0 ;; "switches set") printf '%s\n' "$@" > dev/switches.json ;; esac
{ printf '%s\n' "$@"; printf 'TICK_NOTE=%s\n' "${TICK_NOTE-}"; } > "$(git rev-parse --show-toplevel)/.argv"
STUB
chmod +x "$FX/scripts/gates/l7r-gate.sh"
mkdir -p "$FX/http:/a.example"; touch "$FX/http:/a.example/p1"  # what http://a.example/p? and p* would glob to, were globbing on
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
git -C "$FX" init -q && git -C "$FX" add -A && git -C "$FX" commit -qm fixture
# a backtick and a $( that would each create a file if the shell read them, a $ make or the shell would expand, both quotes
V='a`touch ran1`b $(touch ran2) $HOME $$x ${y} "dq" '"'"'sq'"'"' \z'
arrives() { # label expected-lines (consecutive, one argument a line) target VAR=value...
  local label=$1 want=$2; shift 2
  rm -f "$FX/.argv" "$FX/ran1" "$FX/ran2"
  ( cd "$FX" && make --no-print-directory "$@" ) >/dev/null 2>&1
  if [ -f "$FX/.argv" ] && [[ $'\n'"$(cat "$FX/.argv")"$'\n' == *$'\n'"$want"$'\n'* ]] && [ ! -e "$FX/ran1" ] && [ ! -e "$FX/ran2" ]; then
    echo "  ok      $label"; PASS=$((PASS+1))
  else echo "  FAIL    $label: the value did not arrive unchanged$([ -e "$FX/ran1" ] || [ -e "$FX/ran2" ] && echo ', and the shell RAN part of it') - the recipe must read it as \"\$\$NAME\", the name in FREE_TEXT"; FAIL=$((FAIL+1)); fi
}
arrives "a flag's value: make claims-bundle UNITS=" "$V" claims-bundle UNITS="$V"
arrives "an environment variable the gate reads: make tick NOTE= (TICK_NOTE)" "TICK_NOTE=$V" tick F=449 T=T1 NOTE="$V"
arrives "a required argument's check and two values: make check-closed SUBJECT= REASON=" "$V" check-closed SUBJECT="$V" REASON="$V"
arrives "through a sub-make: make claims-clean REASON= (the switch's --why)" "$V" claims-clean REASON="$V"
[ "$(git -C "$FX" log -1 --format=%s)" = "chore: claims clean - $V" ] && [ ! -e "$FX/ran1" ] \
  && { echo "  ok      ...and inside a longer word: the switch's commit message"; PASS=$((PASS+1)); } \
  || { echo "  FAIL    the switch's commit message is not \"chore: claims clean - <the reason>\""; FAIL=$((FAIL+1)); }
# A list is split by the shell, one argument a word, with globbing off: the first URL would glob to http:/a.example/p1. A word
# holds no space, so its backtick and $( create their file by a bare redirection.
U1='http://a.example/p?'; U2='http://a.example/`>ran1`*?q=$z&r=$(>ran2)'
arrives "a list of URLs, split unglobbed: make source-pages URLS=" "$U1"$'\n'"$U2"$'\n'"--question" source-pages OUT=out URLS="$U1 $U2" Q=0001
M1='a$b.pdf=k1'; M2='c`>ran1`d*.pdf=k2,k3'
arrives "a list made into flags: make archive-inbox MATCH= (--match per word)" "--match"$'\n'"$M1"$'\n'"--match"$'\n'"$M2" archive-inbox MATCH="$M1 $M2"
# Every target, not only these: no recipe names a FREE_TEXT variable as $(NAME) outside an $(if ...) test, where make alone reads it.
hits=$(awk '
  /^FREE_TEXT[ \t]*:?=/ { inlist = 1; sub(/^FREE_TEXT[ \t]*:?=/, "") }
  inlist { n = split($0, w, /[ \t\\]+/); for (i = 1; i <= n; i++) if (w[i] != "") { free[w[i]] = 1; nfree++ }; if ($0 !~ /\\$/) inlist = 0; next }
  !/^\t/ && !/^[A-Z_][A-Z0-9_]*[ \t]*[:?+]?=/ { next }
  { s = $0; depth = 0
    for (i = 1; i <= length(s); i++) { c = substr(s, i, 1)
      if (c == "$" && substr(s, i + 1, 1) == "$") { i++; continue }
      if (c == "$" && substr(s, i + 1, 1) == "(") {
        if (match(substr(s, i + 2), /^[A-Z_][A-Z0-9_]*\)/)) {
          name = substr(s, i + 2, RLENGTH - 1); ok = 0; for (d = 1; d <= depth; d++) if (cond[d]) ok = 1
          if ((name in free) && !ok) print NR ": $(" name ")"
          i += RLENGTH + 1; continue }
        depth++; cond[depth] = (substr(s, i + 2, 3) == "if "); i++; continue }
      if (c == "(") { depth++; cond[depth] = 0; continue }
      if (c == ")" && depth > 0) { depth--; continue }
      if (c == "," && depth > 0 && cond[depth]) cond[depth] = 0 } }
  END { if (nfree < 8) print "no FREE_TEXT list of the free-text variables at the top of the Makefile" }' "$MK")
[ -z "$hits" ] && { echo "  ok      no recipe hands a FREE_TEXT variable to the shell as \$(NAME)"; PASS=$((PASS+1)); } \
  || { echo "  FAIL    a free-text variable reaches the shell through make - write it \"\$\$NAME\" (a list: set -f, then \$\$NAME unquoted or a loop over it; FREE_TEXT exports it):"; printf '%s\n' "$hits" | sed 's/^/          Makefile:/'; FAIL=$((FAIL+1)); }

echo
echo "7. WHAT A RECIPE RUNS EXISTS (feature 449 T218)"
# `make scatter-bases` ran scripts/reviews/scatter_bases.py, deleted in ea5638968; `make done FULL=1` ran `make perf-gate`, which no
# rule bears - and a .PHONY name with no rule answers "Nothing to be done" with exit 0, a phase that passes having run nothing;
# `make map` with no GEN rolled pool/hamlets/inashiro/inashiro.gen.py, gone since the hamlets became spec.json (feature 444).
# A recipe line naming a script the tree lacks (comments, `: "..."` notes and `##` help are prose, not run):
gone=$(awk '/^\t/ && !/^\t[ \t]*(#|@?:[ \t])/' "$MK" | grep -oE 'scripts/[A-Za-z0-9_/.-]+\.(py|sh)' | sort -u \
  | while read -r p; do [ -e "$HERE/../../$p" ] || echo "$p"; done)
[ -z "$gone" ] && { echo "  ok      no recipe runs a script the tree lacks"; PASS=$((PASS+1)); } \
  || { echo "  FAIL    a recipe runs a script the tree lacks - delete the target, or point it at what does the job now:"; printf '          %s\n' $gone; FAIL=$((FAIL+1)); }
# Every phase `make done` runs (its `for phase in` lists, the FULL and PORT ones included) has a rule:
lists=$(grep -E 'for phase in ' "$MK" | sed -E 's/.*for phase in (.*); do.*/\1/')
phases=$( { printf '%s\n' "$lists" | tr ' ' '\n' | grep -E '^[a-z][a-z0-9-]+$'; printf '%s\n' "$lists" | grep -oE ',[a-z][a-z0-9-]+,\)' | tr -d ',)'; } | sort -u)
ruleless=$(for t in $phases; do grep -qE "^$t[ ]*:([^=]|\$)" "$MK" || echo "$t"; done)
[ -n "$phases" ] && [ -z "$ruleless" ] && { echo "  ok      every phase make done runs has a rule ($(echo $phases))"; PASS=$((PASS+1)); } \
  || { echo "  FAIL    make done runs a phase no rule bears (a .PHONY name with no rule passes having run nothing) - remove the call, or point it at the target that does the job: ${ruleless:-no phase list found}"; FAIL=$((FAIL+1)); }
# Every .PHONY name has a rule (feature 449 T223): `make perf-review`, which sync-with-main.sh ran on every push, and `make
# cohort-landing`, which `make land` ran at the port switch's `integrated`, had lost theirs with the Python engine and answered
# "Nothing to be done" with exit 0 - each caller passing having checked nothing. A rule line is `name ...:` whose right side, its `##`
# help cut, holds no `=` (`done: export X := ...` is a target-specific variable, no rule). Read from the text, never by running make:
# a $(MAKE) line runs even under -n.
phony=$(awk '/^\.PHONY[ \t]*:/ { on = 1; sub(/^\.PHONY[ \t]*:/, "") }
  on { more = ($0 ~ /\\$/); n = split($0, w, /[ \t\\]+/); for (i = 1; i <= n; i++) if (w[i] != "") print w[i]; if (!more) on = 0 }' "$MK" | sort -u)
rules=$(awk '!/^[\t#.]/ && /^[^=]*[^:=]:([^=]|$)/ { s = $0; sub(/[ \t]*##.*/, "", s); i = index(s, ":")
  if (substr(s, i + 1) ~ /=/) next; n = split(substr(s, 1, i - 1), w, /[ \t]+/); for (j = 1; j <= n; j++) if (w[j] != "") print w[j] }' "$MK" | sort -u)
ruleless=$(comm -23 <(printf '%s\n' $phony) <(printf '%s\n' $rules) | tr '\n' ' ')
[ -n "$phony" ] && [ -z "$ruleless" ] && { echo "  ok      every .PHONY name has a rule ($(printf '%s\n' $phony | wc -l | tr -d ' ') names)"; PASS=$((PASS+1)); } \
  || { echo "  FAIL    a .PHONY name has no rule, so make answers 'Nothing to be done' with exit 0 and its caller passes having run nothing - give it the rule that does its job now, or remove the name from .PHONY with every call to it: ${ruleless:-no .PHONY list found}"; FAIL=$((FAIL+1)); }
# Every `make <name>` a guard or gate message tells the reader to run, and every one in an agent's instructions, names a rule (feature
# 449 T225). T223 removed the Python engine's targets, and their names lived on in tips: `make maps` in the pair guard, `make perf` in
# the measure guard's reminder, `make perf-fanout` in the work-budget bundle's refusal, `make rust-gate` in the cohort's note - each a
# message sending a session to a command that answers "No rule to make target". Read from the text, as the checks above: the Rust
# sources of rust/guard and rust/gate (a `tests.rs`, a `tests/` directory, a `#[cfg(test)]` tail and a `//` comment are not messages)
# and .claude/agents/*.md (a line that says the command is retired or gone, and a DORMANT agent whose banner says so of every
# command it names, are records). A glob (`make claims-*`) and English (`make sure`) are not names.
dead_make_names() {   # dead_make_names ROOT: "file:line: make NAME" for each name ROOT's Makefile has no rule for
  local r=$1 rl
  rl=$(awk '!/^[\t#.]/ && /^[^=]*[^:=]:([^=]|$)/ { s = $0; sub(/[ \t]*##.*/, "", s); i = index(s, ":")
    if (substr(s, i + 1) ~ /=/) next; n = split(substr(s, 1, i - 1), w, /[ \t]+/); for (j = 1; j <= n; j++) if (w[j] != "") print w[j] }' "$r/Makefile" | sort -u)
  {
    ( cd "$r" && find rust/guard/src rust/gate/crates -name '*.rs' ! -name tests.rs ! -path '*/tests/*' ! -path '*/target/*' | sort ) | while read -r f; do
      awk -v F="$f" '/^[ \t]*#\[cfg\(test\)\]/ { exit } /^[ \t]*\/\// { next } { print F ":" NR ": " $0 }' "$r/$f"
    done
    ( cd "$r" && ls .claude/agents/*.md ) | while read -r f; do
      head -3 "$r/$f" | grep -qE '^description: DORMANT' && continue
      grep -nEiv '(left with|retired|gone|deleted|dormant|removed|went with|no longer|has no rule|does not exist)' "$r/$f" | sed "s|^|$f:|"
    done
  } | grep -oE "^[^:]+:[0-9]+:|([\`\"']|run:? |then |try )make( +(-[A-Za-z-]+|[A-Z_]+=[^ ]*))* +[a-z][a-z0-9-]*([^a-z0-9*<-]|$)" \
    | awk '/^[^ ]+:[0-9]+:$/ { loc = $0; next } { n = split($0, w, " "); t = w[n]; sub(/[^a-z0-9-]+$/, "", t); print loc " make " t }' \
    | grep -vE ' make (the|other|target|sure|it|this|that|them|each|one|any|no|up)$' \
    | while read -r loc m t; do grep -qxF -- "$t" <<<"$rl" || echo "$loc make $t"; done
}
dead=$(dead_make_names "$HERE/../..")
[ -z "$dead" ] && { echo "  ok      every make NAME a guard or gate message or an agent file tells the reader to run has a rule"; PASS=$((PASS+1)); } \
  || { echo "  FAIL    a message names a make target with no rule - re-point it at the command that does the job now, or remove the instruction (a line saying it was retired is a record, and passes):"; printf '          %s\n' "$dead"; FAIL=$((FAIL+1)); }
# ...and it fires: a scratch tree whose Makefile has one rule and whose sources name a dead target in a message, a doc comment, a test
# module and an agent line (only the message and the agent line count), beside a live one and a retired one
S="$GUARD_LOG_ROOT/dead-names"; mkdir -p "$S/rust/guard/src" "$S/rust/gate/crates/x/src" "$S/.claude/agents"
printf 'live: ## a rule\n\t@true\n' > "$S/Makefile"
printf '%s\n' 'const A: &str = "run `make dead-one` now";' '/// a doc comment naming `make dead-two`' 'const B: &str = "use `make live`";' \
  '#[cfg(test)]' 'const T: &str = "`make dead-three`";' > "$S/rust/guard/src/a.rs"
printf '%s\n' 'const C: &str = "make sure and `make claims-*`";' > "$S/rust/gate/crates/x/src/b.rs"
printf '%s\n' 'Run `make dead-four` first.' '`make dead-five` left with the Python engine.' > "$S/.claude/agents/a.md"
got=$(dead_make_names "$S" | sed 's/^[^ ]* //' | tr '\n' ' ')
[ "$got" = "make dead-one make dead-four " ] && { echo "  ok      the check fires on a message and an agent line, and passes a comment, a test tail, a retired line, a glob and English"; PASS=$((PASS+1)); } \
  || { echo "  FAIL    the dead-name check answered '$got' on its scratch tree (want: make dead-one make dead-four)"; FAIL=$((FAIL+1)); }
# `make map` with no GEN is refused, naming the forms it takes, before anything runs:
out=$( cd "$FX" && make --no-print-directory map 2>&1 ); rc=$?
[ "$rc" = 2 ] && [[ $out == *"GEN=pool/<tier>/<map>/<map>.gen.py"* ]] && [[ $out == *"make hamlet SPEC="* ]] \
  && { echo "  ok      make map with no GEN is refused, naming the .gen.py form and make hamlet for a hamlet"; PASS=$((PASS+1)); } \
  || { echo "  FAIL    make map with no GEN (exit $rc) did not refuse naming its forms: $(printf '%s' "$out" | head -3)"; FAIL=$((FAIL+1)); }

echo
echo "passed $PASS, failed $FAIL"
[ "$FAIL" -eq 0 ]
