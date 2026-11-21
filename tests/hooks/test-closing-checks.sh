#!/usr/bin/env bash
# Tests for scripts/gates/closing-checks.sh (`make closing-checks`, feature 451 T55): make static, make hooks-test and make quick at
# once, one combined result - each verdict, its seconds and its log, the tail of a red one, red if any is red; a TERM stops all three;
# each run under its own directory, so two runs in one clone read their own verdicts and logs, the old ones pruned (451 T72);
# with T=, the caller's task's files judged and another task's red reported apart, not counted (451 T86).
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
# the rust checks' caller rule as rustc.rs answers it (451 T86, pinned in the rustc crate's tests): static.red names the half-done file;
# a crate red on it is APART, exit 0, when L7R_RUST_CALLER's listing does not hold it; static.blocked makes the caller's crate red with
# its one error in that file, as a crate that builds on a broken one is. static.cover is a counted cover red (451 T95), a line
# "<path> [<lines>]" each as rustc.rs's cover_ran prints it, the path absolute; "<crate> 0" is a failed coverage run's marker, which names
# its crate, not a file. static.apart is an APART crate's red on that file: its `-->` line and its line no test reaches
top=$(git rev-parse --show-toplevel 2>/dev/null)
if [ "$t" = static ] && [ -e "$d/static.apart" ]; then
  f=$(cat "$d/static.apart")
  printf "rust-checks: APART cover red on %s - another task's: its cover key reads none of this task's files\n   --> %s:3:1\n%s/%s - lines no test reaches: 4\n" \
    "${f%/src/*}" "${f#rust/}" "$top" "$f"
fi
if [ "$t" = static ] && [ -e "$d/static.cover" ]; then
  printf 'rust-checks: cover FAILED on %s\n' "$(head -1 "$d/static.cover" | cut -d' ' -f1 | sed 's#/src/.*##')"
  while read -r f n; do printf '%s/%s - lines no test reaches: %s\n' "$top" "$f" "${n:-3, 7}"; done < "$d/static.cover"
  rc=1
fi
if [ "$t" = static ] && [ -e "$d/static.red" ]; then
  red=$(cat "$d/static.red"); crate=${red%/src/*}
  if [ -e "$d/static.blocked" ]; then
    printf 'rust-checks: lint FAILED on rust/mine\nerror[E0308]: mismatched types\n   --> %s:3:1\n' "${red#rust/}"; exit 1
  elif [ -n "${L7R_RUST_CALLER:-}" ] && ! grep -qx "$red" "$L7R_RUST_CALLER"; then
    printf "rust-checks: APART lint red on %s - another task's: its lint key reads none of this task's files\nerror: half-done\n" "$crate"
  else
    printf 'rust-checks: lint FAILED on %s\nerror: half-done\n' "$crate"; exit 1
  fi
fi
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

echo "6. two tasks' work in one clone (451 T86): the caller's files judged, another task's red apart and not counted"
# A scratch clone: T86 (451) and T84 (451) mid-edit beside each other, and 449's T86. The caller's: its own Edit, a file both edited, a
# Bash write no line names, a file a landed task's old line names, a fallback line's file, a file both tasks' Bash calls wrote (451 T93);
# another task's: T84's crate, 449's T86's file, T84's Bash writes - a call's end and a failed end (`writes`, 451 T93) - while the
# directory one of them names claims none of the files in it; and a landed task's line, newer than the file's last commit but older than
# its own task's landing, which left the file unchanged, claims nothing (451 T93).
C="$T/clone"; E="$C/.git/l7r-events"; rm -rf "$C" "$T/c6"; mkdir -p "$C/rust/mine/src" "$C/rust/other/src" "$C/docs" "$T/c6"
git -C "$C" init -q && git -C "$C" config user.email t@t && git -C "$C" config user.name t
for f in rust/mine/src/lib.rs rust/other/src/lib.rs docs/shared.md docs/landed.md docs/reverted.md; do echo base > "$C/$f"; done
git -C "$C" add -A && git -C "$C" commit -qm base
GIT_COMMITTER_DATE="$(( $(date +%s) + 60 )) +0000" git -C "$C" commit -q --allow-empty -m '451-x: T77 T78 ticked (make land)'
later=$(python3 -c 'import datetime, time; print(datetime.datetime.fromtimestamp(time.time() + 30, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"))')
for f in rust/mine/src/lib.rs rust/other/src/lib.rs docs/shared.md docs/landed.md rust/mine/src/new.rs rust/other/src/extra.rs docs/bash.md \
  docs/sed.md docs/failed.md docs/both.md docs/reverted.md; do echo edit >> "$C/$f"; done
now=$(date -u +%Y-%m-%dT%H:%M:%S.000Z); mkdir -p "$E"
line() { printf '{"t":"%s","ev":"PostToolUse","tool":"Edit","cat":"edit","by":"a1","path":"%s/%s","task":"%s"%s}\n' "$1" "$C" "$2" "$3" "${4:-}"; }
{ line "$now" rust/mine/src/lib.rs T86; line "$now" rust/other/src/lib.rs T84; line "$now" docs/shared.md T84; line "$now" docs/shared.md T86
  line 2020-01-01T00:00:00.000Z docs/landed.md T50; line "$now" docs/bash.md T84 ',"fallback":true'
  printf '{"t":"%s","ev":"PreToolUse","tool":"Edit","cat":"edit","path":"%s/docs/bash.md","task":"T84"}\n' "$now" "$C"
  # a Bash call's end as event_log_hooks writes it (the form `a_bash_calls_post_line_names_the_files_it_wrote` pins), its task appended
  bashline() { printf '{"t":"%s","sid":"s","ev":"%s","tool":"Bash","id":"u","cat":"other tool","writes":[%s],"task":"%s"}\n' "$now" "$1" "$2" "$3"; }
  bashline PostToolUse "\"$C/docs/sed.md\",\"$C/rust/mine\"" T84; bashline PostToolUseFailure "\"$C/docs/failed.md\"" T84
  bashline PostToolUse "\"$C/docs/both.md\"" T84; bashline PostToolUse "\"$C/docs/both.md\"" T86
  printf '{"t":"%s","ev":"PostToolUse","tool":"Bash","cat":"other tool","writes":["%s/docs/reverted.md"],"task":"T77"}\n' "$later" "$C"; } > "$E/451-x.jsonl"
line "$now" rust/other/src/extra.rs T86 > "$E/449-y.jsonl"
printf '{"feature": "449-y", "task": "T86", "utc": "2026-11-01T00:00:00Z"}\n{"feature": "451-x", "task": "T86", "utc": "2026-11-21T00:00:00Z"}\n' > "$C/.git/task-starts.jsonl"
c6() { : > "$T/events"; OUT=$(cd "$C" && STUB_DIR="$T/c6" L7R_EVENTS_DIR="$E" STUB_SLEEP=0.1 "$@" "$SCRIPT" 2>&1); RC=$?; }
echo rust/other/src/lib.rs > "$T/c6/static.red"
c6 env CLOSING_TASK=T86
d6=$(run_dir <(printf '%s' "$OUT"))
[ "$(cat "$d6/caller-files" 2>/dev/null | tr '\n' ' ')" = "docs/bash.md docs/both.md docs/landed.md docs/reverted.md docs/shared.md rust/mine/src/lib.rs rust/mine/src/new.rs " ] \
  && ok "the caller's files: its own edit, a shared file, a Bash write no line names, a landed task's file, a fallback line's (the feature from its task-start), a file both tasks' Bash calls wrote, the files in a directory another's call names, a file a task's line names before that task landed" \
  || no "the caller's files" "$(cat "$d6/caller-files" "$d6/split.txt" 2>&1)"
[ "$(cut -f1 "$d6/others" 2>/dev/null | tr '\n' ' ')" = "docs/failed.md docs/sed.md rust/other/src/extra.rs rust/other/src/lib.rs " ] && grep -q 'T86@449-y' "$d6/others" && grep -q 'T84@451-x' "$d6/others" \
  && ok "another task's: T84's file, its Bash writes (a call's end and a failed end, 451 T93), and 449's T86's" || no "another task's files" "$(cat "$d6/others" 2>&1)"
[ "$RC" -eq 0 ] && printf '%s' "$OUT" | grep -Eq '^  static +GREEN' && printf '%s' "$OUT" | grep -q 'closing-checks: GREEN' \
  && ok "the caller's run is GREEN beside the other's red crate" || no "the caller's verdict (exit $RC)" "$OUT"
printf '%s' "$OUT" | grep -q "another task's red.*reported apart and not counted" && printf '%s' "$OUT" | grep -q '  lint red on rust/other - .*T84@451-x: rust/other/src/lib.rs' \
  && ok "the other's red named apart, with its task and file" || no "no apart section" "$OUT"
printf '%s' "$OUT" | grep -q "judged as T86's: 7 of the clone's 11 uncommitted files (3 its own edits name, 4 no task's edit); another task's, its red reported apart: 4" \
  && ok "the split is printed" || no "the split line" "$OUT"
echo rust/mine/src/lib.rs > "$T/c6/static.red"; c6 env CLOSING_TASK=T86 CLOSING_FEATURE=451
[ "$RC" -eq 1 ] && printf '%s' "$OUT" | grep -Eq '^  static +RED' && ! printf '%s' "$OUT" | grep -q "another task's red" \
  && ok "the caller's own red still fails" || no "the caller's red (exit $RC)" "$OUT"
printf '%s' "$OUT" | grep -q 'then run `make closing-checks T=T86 F=451` once more' \
  && ok "the red names the caller's own rerun, its T= and F=" || no "the rerun line drops T= (a bare one judges the whole clone)" "$OUT"
c6 env CLOSING_TASK=T86 CLOSING_FEATURE=449
d6=$(run_dir <(printf '%s' "$OUT"))
grep -qx rust/other/src/extra.rs "$d6/caller-files" && ! grep -qx rust/mine/src/lib.rs "$d6/caller-files" && [ "$RC" -eq 0 ] \
  && ok "F= names the feature: 449's T86 is another task than 451's" || no "F=449 (exit $RC)" "$(cat "$d6/caller-files" 2>&1; printf '%s' "$OUT")"
echo rust/other/src/lib.rs > "$T/c6/static.red"; touch "$T/c6/static.blocked"; c6 env CLOSING_TASK=T86
[ "$RC" -eq 1 ] && printf '%s' "$OUT" | grep -q "BLOCKED.*every error static printed is in another task's files - rust/other/src/lib.rs (T84@451-x)" \
  && ok "a red of the caller's whose every error is in another task's file: BLOCKED, still red" || no "the blocked red (exit $RC)" "$OUT"
# a coverage red (451 T95): cover's lines no test reaches name files too, read as the errors' are; T81's second closing run, 2026-11-21,
# was red on cover alone, its lines in T88's files, and went untagged
c6cover() { rm -f "$T/c6/static.red" "$T/c6/static.blocked" "$T/c6/static.cover" "$T/c6/static.apart"; for a in "$@"; do eval "$a"; done; c6 env CLOSING_TASK=T86; }
c6cover 'printf "rust/other/src/lib.rs\nrust/other/src/extra.rs 12\n" > "$T/c6/static.cover"'
d6=$(run_dir <(printf '%s' "$OUT"))
[ "$RC" -eq 1 ] && printf '%s' "$OUT" | grep -Eq '^  static +RED' && grep -q "$C/rust/other/src/lib.rs - lines no test reaches: 3, 7" "$d6/static.log" \
  && ok "a coverage red on another task's files alone is still counted red" || no "the coverage red's verdict (exit $RC)" "$OUT"
printf '%s' "$OUT" | grep -q "BLOCKED.*every line no test reaches that static printed is in another task's files - rust/other/src/extra.rs (T86@449-y), rust/other/src/lib.rs (T84@451-x); yours are covered" \
  && ok "two tasks' work, the other's lines uncovered and the caller's covered: BLOCKED, naming each file and task" \
  || no "the coverage red on another's files went untagged" "$OUT"
c6cover 'printf "rust/other/src/lib.rs\nrust/mine/src/lib.rs\n" > "$T/c6/static.cover"' 'echo rust/other/src/lib.rs > "$T/c6/static.red"' 'touch "$T/c6/static.blocked"'
[ "$RC" -eq 1 ] && ! printf '%s' "$OUT" | grep -q BLOCKED \
  && ok "the caller's own line no test reaches, beside another task's error: not BLOCKED, red" || no "a caller's uncovered line tagged BLOCKED (exit $RC)" "$OUT"
c6cover 'echo "rust/mine 0" > "$T/c6/static.cover"' 'echo rust/other/src/lib.rs > "$T/c6/static.red"' 'touch "$T/c6/static.blocked"'
[ "$RC" -eq 1 ] && printf '%s' "$OUT" | grep -q "BLOCKED.*every error static printed is in another task's files - rust/other/src/lib.rs (T84@451-x)" \
  && ok "a failed coverage run's marker names a crate, not a file: its build broken on another's file stays BLOCKED" || no "the failed run's marker (exit $RC)" "$OUT"
c6cover 'echo "rust/mine 0" > "$T/c6/static.cover"' 'echo rust/other/src/lib.rs > "$T/c6/static.apart"'
[ "$RC" -eq 1 ] && ! printf '%s' "$OUT" | grep -q BLOCKED \
  && ok "an APART crate's lines are not the counted red's: a caller's red naming no file beside them is not BLOCKED" || no "an APART crate's lines tagged the caller's red (exit $RC)" "$OUT"
rm -f "$T/c6/static.cover" "$T/c6/static.apart"; echo rust/other/src/lib.rs > "$T/c6/static.red"
rm -f "$T/c6/static.blocked"; c6 env -u CLOSING_TASK
[ "$RC" -eq 1 ] && printf '%s' "$OUT" | grep -q 'no T= - every crate and file in the clone is judged as yours' && printf '%s' "$OUT" | grep -Eq '^  static +RED' \
  && ok "no T=: the whole clone judged as before, the T= form named" || no "no T= (exit $RC)" "$OUT"
rm -rf "$T/c6"

echo
echo "closing-checks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
