# parts.sh - run a guard suite's cases in parallel parts. Sourced, never run (feature 383 amendment 4, plan D28; the runner
# sync-with-main's suite carried since feature 375 amendment 4, FR-022).
#
# A suite defines its cases as functions, each building its own fixture (no case reads a variable another sets), lists them
# in CASES, may weigh them in an associative array WEIGHT (seconds, measured; a case without one counts 10), and calls
#   run_parts <parts>
# The cases are dealt longest first onto the lightest part; each part is a subshell with its own $T, HOME and guard log, and
# calls `part_env` first when the suite defines one (a suite's own per-run files - a captured-stderr file, say - made fresh
# there). Every check still runs and is counted into PASS and FAIL; a part that ends before a case reports fails the suite and
# names the case. PARTS_CASES="case_a case_b" runs only those cases - to time one case where it lives; run_parts 1 runs them
# one after another, in this shell.
# GUARD_EDIT_OK: feature 383 amendment 4 - adding an operation: the parallel runner, shared by every split guard suite.

run_parts() {
  local parts=${1:-4} k c w best p f
  # PARTS_MAX caps the parts: `make hooks-test` runs up to HOOKS_JOBS suites at once, and eight suites of eight parts each hit
  # the containers' shared 10 GB memory cap on the first run (2026-10-17: memguard killed another session's process, and a
  # timed sync-with-main check failed under the load). tests/hooks/hookrun.sh sets it; a suite run alone takes its own count.
  [ -n "${PARTS_MAX:-}" ] && [ "$parts" -gt "$PARTS_MAX" ] && parts=$PARTS_MAX
  [ -n "${PARTS_CASES:-}" ] && read -r -a CASES <<< "$PARTS_CASES"
  if [ "$parts" -le 1 ]; then
    for c in "${CASES[@]}"; do "$c"; done
    return 0
  fi
  local W; W=$(mktemp -d)
  local -a LOAD PART
  for ((k = 0; k < parts; k++)); do LOAD[k]=0; PART[k]=""; done
  while read -r w c; do
    best=0; for ((k = 1; k < parts; k++)); do [ "${LOAD[k]}" -lt "${LOAD[best]}" ] && best=$k; done
    LOAD[best]=$((LOAD[best] + w)); PART[best]="${PART[best]} $c"
  done < <(for c in "${CASES[@]}"; do echo "${WEIGHT[$c]:-10} $c"; done | sort -rn)
  for ((k = 0; k < parts; k++)); do
    [ -n "${PART[k]}" ] || continue
    ( T=$(mktemp -d); export GUARD_LOG_DIR="$T/guard-log" HOME=$T; PASS=0; FAIL=0
      declare -F part_env >/dev/null && part_env
      for c in ${PART[k]}; do "$c"; echo "@@reported $c"; done
      echo "$PASS $FAIL" > "$W/$k.counts"; rm -rf "$T" ) > "$W/$k.log" 2>&1 &
  done
  wait
  for ((k = 0; k < parts; k++)); do
    [ -n "${PART[k]}" ] || continue
    grep -v '^@@reported ' "$W/$k.log"
    if [ -f "$W/$k.counts" ]; then read -r p f < "$W/$k.counts"; PASS=$((PASS + p)); FAIL=$((FAIL + f))
    else
      for c in ${PART[k]}; do grep -qx "@@reported $c" "$W/$k.log" || { echo "FAIL  $c never reported - its part ended before it finished"; FAIL=$((FAIL + 1)); }; done
    fi
  done
  rm -rf "$W"
}
