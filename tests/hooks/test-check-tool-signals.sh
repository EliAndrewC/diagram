#!/bin/bash
# Tests for check-tool-signals.py - no tool lands recording none of its runs (feature 406 T05, FR-004, D164).
# Run: tests/hooks/test-check-tool-signals.sh   (exit 0 = all green)
# GUARD_EDIT_OK: feature 406 - a NEW check's companion suite.
#
# Each case builds a small repository the check reads with --root, so a refusal is proven on the case it names; the last case
# runs it on this repository, which must be clean. CHECK_TOOL_SIGNALS lets a proof of firing run the suite against a mutated copy.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK="${CHECK_TOOL_SIGNALS:-$HERE/../../scripts/gates/check-tool-signals.py}"
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

fixture() { # a clean repository: one wired hook, one gate check, one entry-named script, a registry in step
  rm -rf "$T/r"; mkdir -p "$T/r/.claude" "$T/r/scripts/hooks" "$T/r/scripts/gates" "$T/r/scripts/tools"
  printf '{"hooks":{"PreToolUse":[{"hooks":[{"command":"scripts/hooks/foo-hooks.sh pretool"}]}]}}\n' > "$T/r/.claude/settings.json"
  printf 'done: lint\nlint:\n\t@python3 scripts/tools/lint.py\nquick:\n\t@true\ntick:\n\t@true\n' > "$T/r/Makefile"
  printf '#!/bin/bash\n. guardlog.sh\nguard_log foo blocked x\n' > "$T/r/scripts/hooks/foo-hooks.sh"
  printf 'import usage_log\nif __name__ == "__main__":\n    usage_log.exited("gatey", 0)\n' > "$T/r/scripts/gates/gatey.py"
  printf '# TOOL_RECORD: its run is make lint in the usage log\n' > "$T/r/scripts/tools/lint.py"
  printf '{"tools":{"gatey":{"kind":"check","what":"x"}}}\n' > "$T/r/scripts/tool-registry.json"
}
run() { python3 "$CHECK" --root "$T/r" > "$T/out" 2>&1; echo $? > "$T/rc"; }
rc() { cat "$T/rc"; }

echo "1. a clean repository passes"
fixture; run
[ "$(rc)" -eq 0 ] && ok "every tool records, the registry in step" || no "a clean fixture was refused" "$(cat "$T/out")"

echo "2. a wired hook that records nothing"
fixture; printf '#!/bin/bash\nexit 0\n' > "$T/r/scripts/hooks/foo-hooks.sh"; run
[ "$(rc)" -eq 1 ] && grep -q 'scripts/hooks/foo-hooks.sh: records none of its runs' "$T/out" && ok "refused, naming the hook" || no "the silent hook passed" "$(cat "$T/out")"
grep -q 'TOOL_RECORD' "$T/out" && ok "...and the message names the fix" || no "no fix named"

echo "3. a gate check that records nothing"
fixture; printf 'if __name__ == "__main__":\n    raise SystemExit(0)\n' > "$T/r/scripts/gates/silent.py"; run
[ "$(rc)" -eq 1 ] && grep -q 'scripts/gates/silent.py: records none' "$T/out" && ok "refused, naming the check" || no "the silent check passed" "$(cat "$T/out")"

echo "4. a script an entry point names is held to it too (no target-body exemption)"
fixture; printf 'print(1)\n' > "$T/r/scripts/tools/lint.py"; run
[ "$(rc)" -eq 1 ] && grep -q 'scripts/tools/lint.py: records none' "$T/out" && ok "refused, naming the recipe's script" || no "the recipe's script passed" "$(cat "$T/out")"

echo "5. a script no entry point reaches is not a check"
fixture; printf 'print(1)\n' > "$T/r/scripts/tools/other.py"; run
[ "$(rc)" -eq 0 ] && ok "an unreached helper is left alone" || no "an unreached helper was refused" "$(cat "$T/out")"

echo "6. a usage-log call the registry lacks"
fixture; printf 'import usage_log\nusage_log.record(root, "stray", "step", "changed")\n' > "$T/r/scripts/tools/step.py"; run
[ "$(rc)" -eq 1 ] && grep -q 'records `stray`, which scripts/tool-registry.json lacks' "$T/out" && ok "refused, naming the call" || no "an unregistered call passed" "$(cat "$T/out")"

echo "7. a shell call by --tool the registry lacks"
fixture; printf 'python3 usage_log.py record --tool shelly --kind step --outcome changed\n' > "$T/r/scripts/tools/s.sh"; run
[ "$(rc)" -eq 1 ] && grep -q 'records `shelly`' "$T/out" && ok "refused, naming the shell call" || no "an unregistered shell call passed" "$(cat "$T/out")"

echo "8. a registry entry nothing records"
fixture; printf '{"tools":{"gatey":{"kind":"check","what":"x"},"ghost":{"kind":"step","what":"y"}}}\n' > "$T/r/scripts/tool-registry.json"; run
[ "$(rc)" -eq 1 ] && grep -q '`ghost` is registered but no code records it' "$T/out" && ok "refused, naming the entry" || no "an unused entry passed" "$(cat "$T/out")"

echo "9. this repository is clean"
if python3 "$CHECK" > "$T/out" 2>&1; then ok "every tool here records its runs"; else no "this repository has unrecorded tools" "$(cat "$T/out")"; fi

echo; echo "check-tool-signals: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
