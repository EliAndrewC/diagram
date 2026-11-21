#!/usr/bin/env bash
# Tests for scripts/gates/closing-checks.sh (`make closing-checks`, feature 451 T55): make static, make hooks-test and make quick at
# once, one combined result - each verdict, its seconds and its log, the tail of a red one, red if any is red; a TERM stops all three;
# each run under its own directory, so two runs in one clone read their own verdicts and logs, the old ones pruned (451 T72).
# Run: tests/hooks/test-closing-checks.sh   (exit 0 = all green)
#
# The make is a stub (CLOSING_MAKE): each target sleeps - or, where its fixture dir holds <target>.hold, waits for that dir's
# release file - notes when it started and ended (tagged with its run's STUB_TAG), and exits as its fixture says.
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
t=$2; d=$STUB_DIR; ev=${STUB_EVENTS:-$d/events}; tag=${STUB_TAG:+ $STUB_TAG}
echo "start $t$tag $(date +%s%N)" >> "$ev"
echo "output of $t${STUB_TAG:+ ($STUB_TAG)}"
if [ -e "$d/$t.hold" ]; then
  for _ in $(seq 1 600); do [ -e "$d/release" ] && break; sleep 0.05; done
else
  sleep "${STUB_SLEEP:-0.5}"
fi
echo "end of $t${STUB_TAG:+ ($STUB_TAG)}"
echo "end $t$tag $(date +%s%N)" >> "$ev"
rc=$(cat "$d/$t.rc" 2>/dev/null || echo 0)
[ "$rc" = 0 ] || echo "the failure of $t"
exit "$rc"
EOF
chmod +x "$T/make"
printf '#!/usr/bin/env bash\necho "$*" >> "%s/records"\n' "$T" > "$T/gate"; chmod +x "$T/gate"
export CLOSING_MAKE="$T/make" STUB_DIR="$T" CLOSING_CHECKS_DIR="$T/logs" CLOSING_GATE="$T/gate"
run() { : > "$T/events"; OUT=$("$SCRIPT" 2>&1); RC=$?; }
# the run directory a run's table names (its static row's log), and a wait on a line of the events file
run_dir() { local l; l=$(grep -Eo "$T/logs/[^ ]*/static\.log" "$1" | head -1); printf '%s' "${l%/static.log}"; }
wait_for() { for _ in $(seq 1 400); do grep -q "$1" "$T/events" 2>/dev/null && return 0; sleep 0.05; done; return 1; }

echo "1. all three green: one combined result, side by side"
rm -f "$T"/*.rc; run
[ "$RC" -eq 0 ] && ok "exit 0" || no "exit $RC" "$OUT"
for c in static hooks-test quick; do
  printf '%s' "$OUT" | grep -Eq "^  $c +GREEN .*$T/logs/[0-9]{8}T[0-9]{6}Z-[0-9]+/$c.log" && ok "$c: GREEN with its log, in the run's own directory" || no "$c's row" "$OUT"
  grep -q "output of $c" "$T/logs/latest/$c.log" && ok "$c's output is in its log, latest naming the run" || no "$c's log"
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

echo "4. two overlapping runs in one clone (451 T72): each reads its own verdicts and its own logs"
# T69's builder's case, 2026-11-21: a run whose quick ended red, then a second run started, ran green and ended while the first's
# static still ran; the first read the second's quick verdict as its own. Here run A's quick and hooks-test are red, its hooks-test and
# static held; run B, all green, starts once A's quick has ended, its static held; A's hooks-test ends after B's.
rm -rf "$T/logs" "$T/A" "$T/B"; mkdir -p "$T/A" "$T/B"; : > "$T/events"
echo 1 > "$T/A/quick.rc"; echo 1 > "$T/A/hooks-test.rc"; touch "$T/A/static.hold" "$T/A/hooks-test.hold" "$T/B/static.hold"
STUB_DIR="$T/A" STUB_TAG=A STUB_EVENTS="$T/events" STUB_SLEEP=0.1 "$SCRIPT" > "$T/A.out" 2>&1 & pa=$!
wait_for '^end quick A ' && sleep 0.2 || no "run A's quick never ended" "$(cat "$T/events")"
STUB_DIR="$T/B" STUB_TAG=B STUB_EVENTS="$T/events" STUB_SLEEP=0.3 "$SCRIPT" > "$T/B.out" 2>&1 & pb=$!
{ wait_for '^end quick B ' && wait_for '^end hooks-test B '; } || no "run B's quick and hooks-test never ended" "$(cat "$T/events")"
sleep 0.2; touch "$T/A/release"; wait "$pa"; ra=$?
touch "$T/B/release"; wait "$pb"; rb=$?
A=$(cat "$T/A.out"); B=$(cat "$T/B.out")
[ "$ra" -eq 1 ] && printf '%s' "$A" | grep -q '2 of 3 red' && ok "run A: RED, its two red checks counted" || no "run A's verdict (exit $ra)" "$A"
printf '%s' "$A" | grep -Eq '^  quick +RED \(exit 1\)' && printf '%s' "$A" | grep -Eq '^  hooks-test +RED \(exit 1\)' && printf '%s' "$A" | grep -Eq '^  static +GREEN' \
  && ok "run A: its own quick, hooks-test and static verdicts" || no "run A read another run's verdict" "$A"
[ "$rb" -eq 0 ] && printf '%s' "$B" | grep -q 'closing-checks: GREEN' && ok "run B: GREEN" || no "run B's verdict (exit $rb)" "$B"
printf '%s' "$B" | grep -Eq '^  hooks-test +GREEN' && printf '%s' "$B" | grep -Eq '^  quick +GREEN' && ok "run B: its own hooks-test and quick verdicts" || no "run B read another run's verdict" "$B"
da=$(run_dir "$T/A.out"); db=$(run_dir "$T/B.out")
[ -n "$da" ] && [ -n "$db" ] && [ "$da" != "$db" ] && ok "each run has its own directory" || no "one directory for both" "A: $da B: $db"
own=1
for c in static hooks-test quick; do
  grep -q "output of $c (A)" "$da/$c.log" 2>/dev/null && ! grep -q '(B)' "$da/$c.log" && grep -q "output of $c (B)" "$db/$c.log" 2>/dev/null && ! grep -q '(A)' "$db/$c.log" || own=0
done
[ "$own" = 1 ] && ok "each run's logs hold its own lines alone" || no "a log holds the other run's lines" "$(head -50 "$da"/*.log "$db"/*.log 2>&1)"
[ "$(readlink "$T/logs/latest")" = "${db##*/}" ] && ok "latest names the run started last" || no "latest" "$(ls -l "$T/logs" 2>&1)"
rm -f "$T/A/release" "$T/B/release"

echo "5. old runs pruned by age (CLOSING_CHECKS_KEEP_MIN), a fresh one kept"
rm -rf "$T/logs"; mkdir -p "$T/logs/20261101T000000Z-11" "$T/logs/20261121T000000Z-12"
: > "$T/logs/static.log"; : > "$T/logs/static.exit"; : > "$T/logs/notes.txt"
touch -d '2 days ago' "$T/logs/20261101T000000Z-11" "$T/logs/static.log" "$T/logs/static.exit" "$T/logs/notes.txt"
rm -f "$T"/*.rc; run
[ "$RC" -eq 0 ] && ok "exit 0" || no "exit $RC" "$OUT"
[ ! -e "$T/logs/20261101T000000Z-11" ] && ok "an aged run directory pruned" || no "an aged run directory kept" "$(ls -la "$T/logs")"
[ -d "$T/logs/20261121T000000Z-12" ] && ok "a fresh run directory kept" || no "a fresh run directory pruned" "$(ls -la "$T/logs")"
[ ! -e "$T/logs/static.log" ] && [ ! -e "$T/logs/static.exit" ] && ok "the old layout's aged log and exit file pruned" || no "the old layout's files kept" "$(ls -la "$T/logs")"
[ -e "$T/logs/notes.txt" ] && ok "a file not a run's left alone" || no "a file not a run's pruned"
[ -d "$(run_dir <(printf '%s' "$OUT"))" ] && [ "$T/logs/$(readlink "$T/logs/latest")" = "$(run_dir <(printf '%s' "$OUT"))" ] && ok "this run's directory kept, latest naming it" || no "this run's directory" "$(ls -la "$T/logs")"
CLOSING_CHECKS_KEEP_MIN=0 run
[ ! -e "$T/logs/20261121T000000Z-12" ] && [ -d "$(run_dir <(printf '%s' "$OUT"))" ] && ok "CLOSING_CHECKS_KEEP_MIN=0: every other run's directory pruned, its own kept" || no "the knob" "$(ls -la "$T/logs")"

echo
echo "closing-checks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
