#!/bin/bash
# T278: each lever's arm on its own fresh copy of the warmed base (t278-build.sh's warmup and control runs): the variants rule at
# KEEP (idle cutoff 12 h) applied to the copy (t278-prune.py, with the control run's live hashes checked first), then three builds:
# the whole family warm, one crate alone warm (`-p l7r_gate_claims`, the selection T301 found resolving other features before T325),
# and the whole family after a one-line edit of `registry` (a constant appended; the file and its mtime restored after, so the tree
# and its live caches are as they were).
# usage: t278-arms.sh BASE KEEP ...
set -u
D=$(cd "$(dirname "$0")" && pwd); TREE=${TREE:-/diagram/.clones/diagram-backlog-t270}
BASE=$1; shift
LOGS=${LOGS:-$D/runs}; export LOGS
SRC=$TREE/rust/gate/crates/registry/src/lib.rs; SAVED=$LOGS/t278-registry-lib.rs.orig
for K in "$@"; do
  W=${BASE%/*}/t278-arm; rm -rf "$W"; cp -a "$BASE" "$W"
  python3 -I "$D/t278-prune.py" "$W" "$K" 12 --live "$LOGS/control.json" --apply | sed "s/^/k$K prune: /"
  bash "$D/t278-build.sh" "$W" "k$K-warm"
  bash "$D/t278-build.sh" "$W" "k$K-claims" l7r_gate_claims
  cp -p "$SRC" "$SAVED"
  printf '\npub const T278_PROBE: u32 = 1;\n' >> "$SRC"
  bash "$D/t278-build.sh" "$W" "k$K-edit"
  cp -p "$SAVED" "$SRC"
  git -C "$TREE" diff --quiet -- "$SRC" || echo "k$K: RESTORE FAILED for $SRC"
  rm -rf "$W"
done
