#!/usr/bin/env bash
# SC-004 on a real pool map, both ways: the FR-005 check on Inashiro as it stands, with its generator edited
# (the key moves), and restored. Prints one line per state: the exit code, the wall time, the refusal if any.
# Run from the clone root after its renders are present. The edit is a trailing assignment, restored by copy.
set -u
C="$(git rev-parse --show-toplevel)"; G="$C/.claude/skills/diagram/pool/hamlets/inashiro/inashiro.gen.py"
B="$(mktemp)"; cp "$G" "$B"; trap 'cp "$B" "$G"; rm -f "$B"' EXIT
probe() {
  local t0 t1 out rc; t0=$(date +%s.%N)
  out=$(python3 "$C/scripts/_review_prereq.py" check --clone "$C" --maps inashiro --prompt-file /dev/null --gate-green yes); rc=$?
  t1=$(date +%s.%N); printf '%-10s rc=%s %.2f s %s\n' "$1" "$rc" "$(echo "$t1 - $t0" | bc)" "$out"
}
probe current
printf '\nSTALE_PROBE_240 = 1\n' >> "$G"; probe edited
cp "$B" "$G"; probe restored
