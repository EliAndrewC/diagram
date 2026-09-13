#!/usr/bin/env bash
# Tests for house-style-hooks.sh. Run: scripts/test-house-style-hooks.sh   (exit 0 = all green)
#
# TWO DIRECTIONS, always (the project's standing rule for a guard): it must FIRE on the case it
# exists to catch, and STAY QUIET on correct work. The second half is the one that matters most -
# every guard in this repo that fired on legitimate work taught a session to reach for the escape,
# which is the habit these guards exist to break.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$HERE/test_hooks_cases.py" "house-style"
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
cp -r "$HERE" "$TMP/scripts"
printf 'raise ImportError("broken on purpose")\n' > "$TMP/scripts/_hm_house.py"
OUT=$(printf '%s' '{"tool_name":"Bash","tool_input":{"command":"echo \"the centre of it\" >> docs/a.md"}}' \
      | GUARD_LOG_DIR="$TMP/log" "$TMP/scripts/house-style-hooks.sh" pretool 2>"$TMP/err")
STUB=1
case "$OUT" in
  *hookSpecificOutput*) echo "  ok     the guard still acts with the helper unimportable"; STUB=0 ;;
  *) echo "  FAIL   the guard went silent: $(head -c 160 "$TMP/err")" ;;
esac
exit $(( TABLE != 0 || STUB != 0 ))
