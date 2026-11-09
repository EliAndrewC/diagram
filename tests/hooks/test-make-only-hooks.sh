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
trap 'rm -rf "$GUARD_LOG_ROOT" "$HOOK_ERR"' EXIT

PASS=0; FAIL=0

ev() { jq -nc '{"session_id":"m1","tool_name":"Bash","tool_input":{"command":$ARGS.positional[0]}}' --args -- "$1"; }
run() { ev "$1" | "$HOOK" pretool >/tmp/mo.out 2>"$HOOK_ERR"; echo $?; }

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
check "tier 1: bare pytest"                    blocked "python3 -m pytest -n auto"
check "tier 1: bare pytest, plain name"        blocked "pytest tests/hamletgen -q -m \"not slow\""   # GUARD_EDIT_OK: feature 212 - a bare directory now REWRITES (section 4); a marker filter still refuses
check "tier 1: pytest run in-process via -c"   blocked "python3 -c 'import pytest; pytest.main()'"
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
# The word 'pytest' appearing inside a make invocation is the gate doing its job, not a bypass.
check "make running pytest internally"         ok "make test  # runs pytest under the hood"
# A `|` or `;` INSIDE A QUOTED STRING is not a command separator (2026-08-25: a pip-freeze grep
# for the lockfile pins was blocked as a bare pytest run - the mention-versus-invocation defect).
check "a quoted regex naming pytest"           ok "pip freeze | grep -iE '^(numpy|pytest|ruff)=='"
check "a quoted message naming pytest"         ok "git commit -m 'gate: ruff clean; pytest green'"
check "a heredoc naming pytest"                ok "cat > requirements-dev.in <<'EOF'
pytest
pytest-cov
EOF"

# GUARD_EDIT_OK: feature 449 T028 - the constitution XIV fix: a search naming pytest is not a pytest run (found 2026-11-07)
check "grep -c with pytest in its pattern"     ok      'grep -c "a|pytest" notes.txt'
check "rg -c with pytest in its pattern"       ok      "rg -c 'x; pytest' notes.txt"
check "an escaped pipe naming pytest"          ok      'grep a\|pytest notes.txt'
check "...a real pipe into pytest still refuses" blocked 'cat x | pytest -q'
check "...and an escaped pipe outside a search still refuses" blocked 'sh -c foo\|pytest'
# GUARD_EDIT_OK: feature 449 T028 - FR-005: a replacement's binary goes through make too
names_a_target "the guards' binary run directly" "$HOME/.cache/l7r-cargo-target/x/release/l7r-guard --only a PreToolUse"
names_a_target "the hamlet binary run directly"  "target/release/hamlet pool/hamlets/x/x.spec.json"
names_a_target "the gate's binary run directly"  "$HOME/.cache/l7r-cargo-target/x/release/l7r-gate --version"
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
names_a_target "a blocked pytest names a target"  "pytest -q"
names_a_target "a forged makefile names a target" "make -f /tmp/evil.mk x"

# GUARD_EDIT_OK: feature 212 - THE TARGETED RUN IS REWRITTEN, THE REST REFUSED WITH THE TOKEN NAMED.
echo
echo "4. A TARGETED PYTEST RUN IS REWRITTEN INTO make test-file (feature 212)"
rewritten() { # label, command, the exact rewritten command
  ev "$2" | "$HOOK" pretool >/tmp/mo.out 2>"$HOOK_ERR"; local rc=$?
  local got; got=$(jq -r '.hookSpecificOutput.updatedInput.command // empty' < /tmp/mo.out 2>/dev/null)
  if [ "$rc" -eq 0 ] && [ "$got" = "$3" ]; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else
    echo "  FAIL    $1 (rc=$rc, got '${got:-<nothing>}', wanted '$3')"; FAIL=$((FAIL+1))
  fi
}
refused_because() { # label, command, the text the refusal must carry
  ev "$2" | "$HOOK" pretool >/tmp/mo.out 2>"$HOOK_ERR"; local rc=$?
  if [ "$rc" -ne 0 ] && grep -qF -- "$3" "$HOOK_ERR"; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else
    echo "  FAIL    $1 (rc=$rc; refusal did not name '$3')"; FAIL=$((FAIL+1))
  fi
}
rewritten "one file, output flags, a pipeline tail" \
  "python3 -m pytest tests/gate/hamletgen/test_driver.py -x -q --no-header --no-cov -p no:randomly 2>&1 | sed -n '1,60p'" \
  "make test-file FILE=tests/gate/hamletgen/test_driver.py 2>&1 | sed -n '1,60p'"
rewritten "-k becomes K=, inside a subshell with a cd" \
  '( cd $C && python3 -m pytest tests/interactive/test_page.py -k pond_sluice -x -q 2>&1 | sed -n "1,40p" )' \
  '( cd $C && make test-file FILE=tests/interactive/test_page.py K="pond_sluice" 2>&1 | sed -n "1,40p" )'
rewritten "a quoted -k expression with spaces" \
  'python3 -m pytest tests/settlement/test_homestead_parts.py -q -x -p no:cacheprovider --no-cov -k "yard or work_yard" 2>&1 | tail -12' \
  'make test-file FILE=tests/settlement/test_homestead_parts.py K="yard or work_yard" 2>&1 | tail -12'
rewritten "a node id is a path" "python3 -m pytest tests/a/test_b.py::test_c -x" "make test-file FILE=tests/a/test_b.py::test_c"
rewritten "a directory is a path" "pytest tests/tooling -q 2>&1 | tail -3" "make test-file FILE=tests/tooling 2>&1 | tail -3"
rewritten "two files are two paths" "python3 -m pytest tests/a/test_b.py tests/c/test_d.py -n auto -q" 'make test-file FILE="tests/a/test_b.py tests/c/test_d.py"'
rewritten "an env prefix and a chain after it" \
  'FULL=1 python3 -m pytest tests/tooling/test_switches.py -q -n 4 --no-cov 2>&1 | tail -6; echo done' \
  'FULL=1 make test-file FILE=tests/tooling/test_switches.py 2>&1 | tail -6; echo done'
rewritten "a pytest AFTER a heredoc is still found (the body is masked, not the command)" \
  "$(printf 'cat > /tmp/x.py <<EOF\nprint(\"pytest tests/never.py\")\nEOF\npython3 -m pytest tests/x/test_y.py -q')" \
  "$(printf 'cat > /tmp/x.py <<EOF\nprint(\"pytest tests/never.py\")\nEOF\nmake test-file FILE=tests/x/test_y.py')"
refused_because "a marker filter names its token"     'python3 -m pytest tests/x/test_y.py -m "not slow"' '`-m`'
refused_because "a collection names its token"        "python3 -m pytest tests/x/test_y.py --collect-only -q" '`--collect-only`'
refused_because "a coverage flag names its token"     "python3 -m pytest tests/x/test_y.py --cov=l7r" '`--cov=l7r`'
refused_because "a plugin LOAD names its token"       "python3 -m pytest tests/x/test_y.py -p l7r.diagram.ci.selection" 'loads a plugin'
refused_because "an absolute path names its token"    "python3 -m pytest /tmp/base/tests/test_y.py" 'absolute path'
refused_because "an in-process pytest.main is refused" "python3 -c 'import pytest; pytest.main()'" 'no test path'
grep -q "make test-file FILE=tests/gate/hamletgen/test_driver.py" /tmp/mo.out 2>/dev/null; ev "python3 -m pytest tests/gate/hamletgen/test_driver.py -q" | "$HOOK" pretool 2>/dev/null | grep -q "SUBSET" \
  && { echo "  ok      the context teaches the K= form and the subset rule"; PASS=$((PASS+1)); } \
  || { echo "  FAIL    the rewrite's context does not teach the form"; FAIL=$((FAIL+1)); }

echo
echo "5. AN ENGINE ENTRY POINT A MAKE TARGET WRAPS IS REWRITTEN INTO IT (feature 212)"
rewritten "ci status -> make ci-status" "python3 -m l7r.diagram.ci status 2>&1 | grep -i complete" "make ci-status 2>&1 | grep -i complete"
rewritten "ci status --route -> ROUTE=1" "python3 -m l7r.diagram.ci status --route" "make ci-status ROUTE=1"
rewritten "a \$(ARGS) recipe takes the rest" "python3 -m l7r.diagram.tools.pack_audit wip/x.svg" 'make pack-audit ARGS="wip/x.svg"'
refused_because "a module nothing wraps lists what is" "python3 -m l7r.diagram.tools.scatter_audit pool/hamlets/x" "no make target wraps"
refused_because "...and the list names a wrapped module" "python3 -m l7r.diagram.tools.scatter_audit pool/hamlets/x" "make ci-status"
refused_because "arguments the recipe cannot carry" "python3 -m l7r.diagram.ci state" "cannot carry"
refused_because "a multi-line recipe (REF_FIRST) does not wrap" "python3 -m l7r.diagram.hamletgen --seed 4" "no make target wraps"
ev "python3 -m l7r.diagram.ci status" | "$HOOK" pretool 2>/dev/null | grep -q "make ci-status" \
  && { echo "  ok      the context names the module and the target"; PASS=$((PASS+1)); } \
  || { echo "  FAIL    the entry-point rewrite's context is silent"; FAIL=$((FAIL+1)); }

echo
echo "passed $PASS, failed $FAIL"
[ "$FAIL" -eq 0 ]
