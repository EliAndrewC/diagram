#!/usr/bin/env bash
# cohort-gate.sh - the LANDING COHORT gate: engine work lands only with a 48-seed cohort rolled on the engine being landed, no
# seed of it regressed against main, and a fresh block rolled whose failure rate is printed, never refused on (feature 386).
#
# GUARD_EDIT_OK: feature 386 - a NEW push gate, the GM 2026-10-17 approving the recommendation "Run 48 seeds when a feature or
# batch lands ... it's what would have caught 17/21/40/45 the same day" and "a block of fresh seeds that rotates each run,
# recorded as a failure rate rather than a pass/fail". `l7r-gate cohort check` decides it (plan D2-D5); the
# regression reading is `rust/gate/src/cohort/known.rs`'s own. Run by sync-with-main.sh on the GATED route only: a DIRECT
# delta changes no map. COHORT_OK="<reason>" discharges, to the guard log and dev/bypass-log/.
set -uo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT" || exit 0
CO_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$CO_HERE/../hooks/lib/guardlog.sh"

# A tree with no landing cohort to roll (the guard suites' fixtures: no Makefile, or one without the target) is silent, as
# claims-gate is on a tree with no engine. Keyed on the TARGET, not on l7r/diagram: a fixture holding l7r/diagram wakes every
# push check that imports the engine.
grep -qs '^cohort-landing:' "$ROOT/Makefile" || exit 0

if [ -n "${COHORT_OK:-}" ]; then
  if ! python3 "$CO_HERE/../hooks/lib/hm_escape.py" reason-ok <<<"$COHORT_OK" >/dev/null; then
    guard_log cohort-gate blocked "$COHORT_OK" COHORT_OK-no-reason
    printf 'cohort-gate: COHORT_OK needs a REASON, not just a value - two words and eight characters.\n' >&2
    printf 'It ships with the push: say why this engine lands without its landing cohort, or with the seeds it regressed.\n' >&2
    exit 1
  fi
  guard_log cohort-gate escaped "$COHORT_OK" cohort-ok
  BL="$ROOT/dev/bypass-log/$(date -u +%Y-%m)"
  mkdir -p "$BL" 2>/dev/null || true
  "$CO_HERE/l7r-gate.sh" log gate-bypass cohort-gate "$BL" "COHORT_OK: $COHORT_OK" 2>/dev/null || true
  printf 'cohort-gate: BYPASSED (COHORT_OK) - %s\n  recorded in dev/bypass-log/ - `make audit` lists it\n' "$COHORT_OK"
  exit 0
fi

# GUARD_EDIT_OK: feature 430 T04 (D4) - a delta holding no engine code, or a pass already stored for its exact content, is not
# judged again (`l7r-gate push-gate`); a refusal is never stored
if why="$("$CO_HERE/l7r-gate.sh" push-gate skip cohort 2>/dev/null)"; then printf '  %s\n' "$why"; exit 0; fi
OUT="$("$CO_HERE/l7r-gate.sh" cohort check 2>&1)"; rc=$?
[ -n "$OUT" ] && printf '%s\n' "$OUT" | grep -v 'REFUSED' | sed 's/^/  /'
[ "$rc" -eq 0 ] && { "$CO_HERE/l7r-gate.sh" push-gate pass cohort 2>/dev/null; exit 0; }

guard_log cohort-gate blocked "$(printf '%s' "$OUT" | grep 'REFUSED' | head -c 400)" cohort
printf '\n\033[1mCOHORT GATE: engine work lands with its landing cohort - 48 seeds on this engine, none regressed, and a fresh block.\033[0m\n' >&2
printf '%s\n' "$OUT" | grep 'REFUSED' | sed 's/^cohort-gate: REFUSED /  /' >&2
printf '\nRun `make cohort-landing`: it rolls seeds 1-48, the pinned rows and a 48-seed fresh block (main'"'"'s baseline FIRST when\n' >&2
printf 'main'"'"'s engine has none, in a detached worktree), and says what this gate will.\n' >&2
printf 'A seed NEWLY FAILING or WORSENED is a regression (constitution XIII): fix it, or take the round arbiter'"'"'s waiver\n' >&2
printf '(`make arbiter-ask`). COHORT_OK="<why>" discharges every refusal, to dev/bypass-log/.\n\n' >&2
exit 1
