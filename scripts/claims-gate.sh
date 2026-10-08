#!/usr/bin/env bash
# claims-gate.sh - the CLAIMS GATE: no research claim of the engine or the Mode A procedures lands owed a check, and no
# finding the delta introduced lands at all (feature 316).
#
# GUARD_EDIT_OK: feature 316 - a NEW push gate. The GM, 2026-10-02, accepting the session's rule: an owed row blocks; a
# drifted row the change introduces blocks; a pre-existing drifted row is a warning, as feature 296 was treated (*"it is
# okay for this to not block landing something on main but that it gives us a warning"*). `scripts/_claims.py gate` decides
# it (spec FR-010, plan D7): OWED is a claim with no index row or whose code or cited research moved since its row; a
# FINDING (DRIFTED, NEEDS-RESEARCH, MISLABELED, UNCLAIMED, CANNOT-TELL) is INTRODUCED when the merge base held its unit
# IN-STEP, or held no row and the delta changed its code or its question's findings; a finding at both ends is
# PRE-EXISTING whatever changed, and only printed.
#
# WHY IT REFUSES RATHER THAN REPORTS: the project's standing rule (feature 234, the GM): *"If it is unenforced, then it is
# not a doctrine."* It checks that a check was RECORDED at the content being pushed, never that it was good - the judgment
# is `impl-drift`'s. CLAIMS_OK="<reason>" discharges, to the guard log and dev/bypass-log/.
set -uo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT" || exit 0
CG_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$CG_HERE/_guardlog.sh"

# A fixture tree with no engine in it has no claims to hold: silent, as entry-gate is on a tree with no record.
[ -d "$ROOT/l7r/diagram/hamletgen" ] || exit 0

if [ -n "${CLAIMS_OK:-}" ]; then
  if ! python3 "$CG_HERE/_hm_escape.py" reason-ok <<<"$CLAIMS_OK" >/dev/null; then
    guard_log claims-gate blocked "$CLAIMS_OK" CLAIMS_OK-no-reason
    printf 'claims-gate: CLAIMS_OK needs a REASON, not just a value - two words and eight characters.\n' >&2
    printf 'It ships with the push: say which claims are owed or newly found and why they may land unchecked.\n' >&2
    exit 1
  fi
  guard_log claims-gate escaped "$CLAIMS_OK" claims-ok
  BL="$ROOT/dev/bypass-log/$(date -u +%Y-%m)"
  mkdir -p "$BL" 2>/dev/null || true
  python3 - "$BL" "CLAIMS_OK: $CLAIMS_OK" <<'PYBL' || true
import json, pathlib, secrets, subprocess, sys, time
bl, why = pathlib.Path(sys.argv[1]), sys.argv[2]
head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
(bl / f"{stamp}-{secrets.token_hex(3)}.json").write_text(
    json.dumps({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "target": "claims-gate", "commit": head, "why": why}, indent=2) + "\n",
    encoding="utf-8",
)
PYBL
  printf 'claims-gate: BYPASSED (CLAIMS_OK) - %s\n  recorded in dev/bypass-log/ - `make audit` lists it\n' "$CLAIMS_OK"
  exit 0
fi

OUT="$(PYTHONDONTWRITEBYTECODE=1 python3 "$CG_HERE/_claims.py" --root "$ROOT" gate 2>&1)"; rc=$?
[ -n "$OUT" ] && printf '%s\n' "$OUT" | grep -v 'REFUSED' | sed 's/^/  /'
[ "$rc" -eq 0 ] && exit 0

guard_log claims-gate blocked "$(printf '%s' "$OUT" | grep 'REFUSED' | head -c 400)" claims
printf '\n\033[1mCLAIMS GATE: research claims owed a check, or a finding this delta introduced.\033[0m\n' >&2
printf '%s\n' "$OUT" | grep 'REFUSED' | sed 's/^claims-gate: REFUSED /  /' | head -40 >&2
n="$(printf '%s\n' "$OUT" | grep -c 'REFUSED')"
[ "$n" -gt 40 ] && printf '  ... and %s more (`make claims-owed`)\n' "$((n - 40))" >&2
printf '\nAn OWED claim: `make claims-bundle MODULE=<file>` (or OWED=1), dispatch `impl-drift` on the MANIFEST it prints, save\n' >&2
printf 'its reply to a file, then `make claims-checked BUNDLE=<dir> REPLY=<file>`. An INTRODUCED finding: fix the code or the\n' >&2
printf 'claim and re-check it. CLAIMS_OK="<why>" discharges every refusal, to dev/bypass-log/.\n\n' >&2
exit 1
