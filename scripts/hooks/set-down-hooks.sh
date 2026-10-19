#!/usr/bin/env bash
# set-down-hooks.sh - a feature is worked until it is set down (feature 385 T70, plan D89/D90). (GUARD_EDIT_OK: a NEW guard.)
#
# stop (Stop): refuse the turn's end while the clone's active feature has an open task, nothing the session started is still
# running, and no `make set-down` is recorded since its task-start. The verdict and its why: lib/hm_setdown.py.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/guardlog.sh
. "$HERE/lib/guardlog.sh"
MODE=${1:-}
[ "$MODE" = stop ] || exit 0
INPUT="$(cat)"
ROOT=${SET_DOWN_ROOT:-$(printf '%s' "$INPUT" | "$HERE/clone-sync-hooks.sh" resolve 2>/dev/null | tail -1)}
if [ -z "$ROOT" ] || [ ! -d "$ROOT" ]; then
  CWD=$(printf '%s' "$INPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("cwd",""))' 2>/dev/null)
  ROOT=$(git -C "${CWD:-.}" rev-parse --show-toplevel 2>/dev/null) || exit 0
fi
V=$(printf '%s' "$INPUT" | python3 "$HERE/lib/hm_setdown.py" "$ROOT" 2>/dev/null)
case "$V" in
  "") exit 0 ;;
  ERROR*) guard_log set-down error "stop" read-error "${V#ERROR }"; exit 0 ;;
  *) printf '%s\n' "$V" >&2; guard_log set-down blocked "stop" not-set-down; exit 2 ;;
esac
