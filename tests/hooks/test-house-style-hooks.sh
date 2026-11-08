#!/usr/bin/env bash
# Tests for the house-style guard (rust/guard, replayed through its link). Run: tests/hooks/test-house-style-hooks.sh   (exit 0 = all green)
#
# TWO DIRECTIONS, always (the project's standing rule for a guard): it must FIRE on the case it
# exists to catch, and STAY QUIET on correct work. The second half is the one that matters most -
# every guard in this repo that fired on legitimate work taught a session to reach for the escape,
# which is the habit these guards exist to break.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$HERE/guard-cases.sh" house_style_cases_hold
TABLE=$?

# A HELPER THAT CANNOT BE IMPORTED MUST DEGRADE, NOT SILENCE THE GUARD (feature 236 amendment 2).
# The hook reaches `_hm_house` behind a try/except whose stub stands in when the import fails - and
# the stub was written to a one-argument shape while the call site passed two, so the failure raised
# a TypeError instead. The wrapper turns a crash into exit 0 with no output, so the whole guard was
# off for EVERY command, not just for the exemption the helper decides. The table cannot see this:
# it drives the hook with the helper present.
echo
echo "the import stub: a broken _hm_house degrades, and the guard still acts"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
# GUARD_EDIT_OK: feature 449 T036 decision (e) - the Rust guard imports nothing, so the module broken in a copy cannot reach it; the verdict stands
cp -r "$HERE/../../scripts" "$TMP/scripts"
printf 'raise ImportError("broken on purpose")\n' > "$TMP/scripts/hooks/lib/hm_house.py"
OUT=$(printf '%s' '{"tool_name":"Bash","tool_input":{"command":"echo \"the centre of it\" >> docs/a.md"}}' \
      | GUARD_LOG_DIR="$TMP/log" "$HERE/house-style-hooks.sh" pretool 2>"$TMP/err")
STUB=1
case "$OUT" in
  *hookSpecificOutput*) echo "  ok     the guard still acts with the helper unimportable"; STUB=0 ;;
  *) echo "  FAIL   the guard went silent: $(head -c 160 "$TMP/err")" ;;
esac
exit $(( TABLE != 0 || STUB != 0 ))
