#!/usr/bin/env bash
# Tests for scripts/gates/closing-checks.sh (`make closing-checks`, feature 451 T55): make static, make hooks-test and make quick at
# once, one combined result - each verdict, its seconds and its log, the tail of a red one, red if any is red; a TERM stops all three.
# Run: tests/hooks/test-closing-checks.sh   (exit 0 = all green)
#
# The make is a stub (CLOSING_MAKE): each target sleeps, notes when it started and ended, and exits as its fixture says.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$HERE/../../scripts/gates/closing-checks.sh"
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

cat > "$T/make" <<'EOF'
#!/usr/bin/env bash
# the stub make: `make --no-print-directory <target>`
t=$2; d=$STUB_DIR
echo "start $t $(date +%s%N)" >> "$d/events"
echo "output of $t"
sleep "${STUB_SLEEP:-0.5}"
echo "end $t $(date +%s%N)" >> "$d/events"
rc=$(cat "$d/$t.rc" 2>/dev/null || echo 0)
[ "$rc" = 0 ] || echo "the failure of $t"
exit "$rc"
EOF
chmod +x "$T/make"
printf '#!/usr/bin/env bash\necho "$*" >> "%s/records"\n' "$T" > "$T/gate"; chmod +x "$T/gate"
export CLOSING_MAKE="$T/make" STUB_DIR="$T" CLOSING_CHECKS_DIR="$T/logs" CLOSING_GATE="$T/gate"
run() { : > "$T/events"; OUT=$("$SCRIPT" 2>&1); RC=$?; }

echo "1. all three green: one combined result, side by side"
rm -f "$T"/*.rc; run
[ "$RC" -eq 0 ] && ok "exit 0" || no "exit $RC" "$OUT"
for c in static hooks-test quick; do
  printf '%s' "$OUT" | grep -Eq "^  $c +GREEN .*$T/logs/$c.log" && ok "$c: GREEN with its log" || no "$c's row" "$OUT"
  grep -q "output of $c" "$T/logs/$c.log" && ok "$c's output is in its log" || no "$c's log"
done
printf '%s' "$OUT" | grep -q 'closing-checks: GREEN' && ok "the combined verdict" || no "no combined verdict" "$OUT"
[ "$(tail -1 "$T/records" 2>/dev/null)" = "log usage --tool closing-checks --kind check --outcome passed" ] && ok "the run recorded, passed" || no "no usage record" "$(cat "$T/records" 2>/dev/null)"
# side by side: every check started before any ended
last_start=$(grep '^start' "$T/events" | awk '{print $3}' | sort -n | tail -1)
first_end=$(grep '^end' "$T/events" | awk '{print $3}' | sort -n | head -1)
[ "$(grep -c '^start' "$T/events")" -eq 3 ] && [ "$last_start" -lt "$first_end" ] && ok "the three ran at once" || no "they ran one after another" "$(cat "$T/events")"

echo "2. one red: every verdict, the red one's tail, exit 1"
echo 2 > "$T/hooks-test.rc"; run
[ "$RC" -eq 1 ] && ok "exit 1" || no "exit $RC" "$OUT"
printf '%s' "$OUT" | grep -Eq '^  hooks-test +RED \(exit 2\)' && ok "hooks-test: RED with its exit" || no "hooks-test's row" "$OUT"
printf '%s' "$OUT" | grep -Eq '^  static +GREEN' && printf '%s' "$OUT" | grep -Eq '^  quick +GREEN' && ok "the others still GREEN" || no "the green rows" "$OUT"
printf '%s' "$OUT" | grep -q 'the failure of hooks-test' && ok "the red one's tail is shown" || no "no tail" "$OUT"
printf '%s' "$OUT" | grep -q 'closing-checks: RED.* 1 of 3 red' && ok "the combined verdict counts it" || no "no red verdict" "$OUT"
[ "$(tail -1 "$T/records")" = "log usage --tool closing-checks --kind check --outcome refused" ] && ok "the run recorded, refused" || no "no refused record" "$(cat "$T/records")"
echo 1 > "$T/static.rc"; echo 1 > "$T/quick.rc"; run
[ "$RC" -eq 1 ] && printf '%s' "$OUT" | grep -q '3 of 3 red' && ok "three red: every one reported" || no "not all reported" "$OUT"
rm -f "$T"/*.rc

echo "3. a TERM stops all three"
: > "$T/events"
STUB_SLEEP=30 "$SCRIPT" > "$T/term.out" 2>&1 & pid=$!
for _ in $(seq 1 50); do [ "$(grep -c '^start' "$T/events" 2>/dev/null)" -eq 3 ] && break; sleep 0.1; done
kill -TERM "$pid"; wait "$pid"; rc=$?
[ "$rc" -eq 130 ] && ok "exit 130 on TERM" || no "exit $rc on TERM"
sleep 0.3
pgrep -f "$T/make" > /dev/null && no "a check outlived the TERM" "$(pgrep -af "$T/make")" || ok "no check outlives it"
grep -q 'stopped' "$T/term.out" && ok "says it stopped" || no "no stop line" "$(cat "$T/term.out")"

echo
echo "closing-checks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
