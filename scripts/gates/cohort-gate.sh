#!/usr/bin/env bash
# cohort-gate.sh - the LANDING COHORT gate: engine work lands only with a 48-seed cohort rolled on the engine being landed, no
# seed of it regressed against main, and a fresh block rolled whose failure rate is printed, never refused on (feature 386).
#
# GUARD_EDIT_OK: feature 386 - a NEW push gate, the GM 2026-10-17 approving the recommendation "Run 48 seeds when a feature or
# batch lands ... it's what would have caught 17/21/40/45 the same day" and "a block of fresh seeds that rotates each run,
# recorded as a failure rate rather than a pass/fail". `scripts/gates/cohort_gate.py check` decides it (plan D2-D5); the
# regression reading is scripts/measure/cohort_known.py's own. Run by sync-with-main.sh on the GATED route only: a DIRECT
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
  python3 - "$BL" "COHORT_OK: $COHORT_OK" <<'PYBL' || true
import json, pathlib, secrets, subprocess, sys, time
bl, why = pathlib.Path(sys.argv[1]), sys.argv[2]
head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
(bl / f"{stamp}-{secrets.token_hex(3)}.json").write_text(
    json.dumps({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "target": "cohort-gate", "commit": head, "why": why}, indent=2) + "\n",
    encoding="utf-8",
)
PYBL
  printf 'cohort-gate: BYPASSED (COHORT_OK) - %s\n  recorded in dev/bypass-log/ - `make audit` lists it\n' "$COHORT_OK"
  exit 0
fi

OUT="$(PYTHONDONTWRITEBYTECODE=1 python3 "$CO_HERE/cohort_gate.py" check 2>&1)"; rc=$?
[ -n "$OUT" ] && printf '%s\n' "$OUT" | grep -v 'REFUSED' | sed 's/^/  /'
[ "$rc" -eq 0 ] && exit 0

guard_log cohort-gate blocked "$(printf '%s' "$OUT" | grep 'REFUSED' | head -c 400)" cohort
printf '\n\033[1mCOHORT GATE: engine work lands with its landing cohort - 48 seeds on this engine, none regressed, and a fresh block.\033[0m\n' >&2
printf '%s\n' "$OUT" | grep 'REFUSED' | sed 's/^cohort-gate: REFUSED /  /' >&2
printf '\nRun `make cohort-landing` (about 2 min each roll uncached, seconds when served): it rolls seeds 1-48 and the pinned rows,\n' >&2
printf 'then the fresh block, rolls main'"'"'s baseline in a detached worktree when a failing seed has none, and says what this gate will.\n' >&2
printf 'A seed NEWLY FAILING or WORSENED is a regression (constitution XIII): fix it, or take the round arbiter'"'"'s waiver\n' >&2
printf '(`make arbiter-ask`). COHORT_OK="<why>" discharges every refusal, to dev/bypass-log/.\n\n' >&2
exit 1
