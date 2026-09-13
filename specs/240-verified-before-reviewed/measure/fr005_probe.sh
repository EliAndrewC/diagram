#!/usr/bin/env bash
# SC-004 on a real pool map, both ways: the FR-005 check on Inashiro read where the reviewer reads - the pool
# folder when the dispatch names no snapshot, the snapshot when it names one - then with the generator edited so
# the key moves, and restored. Prints one line per state: the exit code, the wall time, the refusal if any.
# Run from the clone root. The generator edit is a trailing assignment, restored by copy on exit.
set -u
C="$(git rev-parse --show-toplevel)"; G="$C/.claude/skills/diagram/pool/hamlets/inashiro/inashiro.gen.py"
B="$(mktemp)"; P="$(mktemp)"; cp "$G" "$B"; trap 'cp "$B" "$G"; rm -f "$B" "$P"' EXIT
probe() { # label, prompt
  local t0 t1 out rc; printf '%s' "$2" > "$P"; t0=$(date +%s.%N)
  out=$(python3 "$C/scripts/_review_prereq.py" check --clone "$C" --maps inashiro --prompt-file "$P" --gate-green yes); rc=$?
  t1=$(date +%s.%N); printf '%-16s rc=%s %.2f s %s\n' "$1" "$rc" "$(echo "$t1 - $t0" | bc)" "$out"
}
echo "pool folder: $(ls "$(dirname "$G")" | tr '\n' ' ')"
echo "snapshot:    $(ls "$C/.git/review-snapshot/inashiro/clone" 2>/dev/null | tr '\n' ' ')"
probe no-snapshot "review inashiro"
probe named-snapshot "review inashiro from .git/review-snapshot/inashiro/clone/"
printf '\nSTALE_PROBE_240 = 1\n' >> "$G"; probe key-moved "review inashiro from .git/review-snapshot/inashiro/clone/"
cp "$B" "$G"; probe restored "review inashiro from .git/review-snapshot/inashiro/clone/"
