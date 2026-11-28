#!/bin/bash
# T278: the gate's coverage build of the gate family (rust/gate/crates/rustc/src/rustc/cover.rs: `cover_env`, `workspace_only`,
# `build`) by hand, into a COPY of a cover-<family> directory, from the tree's root, timed; prints wall seconds, the units compiled
# (compiler-artifact messages with fresh=false, as `phase::compiled` counts them) and the load, and keeps the JSON messages.
# usage: t278-build.sh WORK LABEL [PACKAGE ...]   (default packages: every gate family crate with a library)
set -u
TREE=${TREE:-/diagram/.clones/diagram-backlog-t270}
WORK=$1; LABEL=$2; shift 2
LOGS=${LOGS:-$(dirname "$0")/runs}; mkdir -p "$LOGS"
case "$WORK" in "$HOME/.cache/l7r-cargo-target"*) echo "t278-build: refusing a live cache" >&2; exit 2;; esac
PKGS=("$@")
if [ ${#PKGS[@]} -eq 0 ]; then
  PKGS=(l7r_gate)
  for d in "$TREE"/rust/gate/crates/*/; do [ -f "$d/src/lib.rs" ] && PKGS+=("$(grep -m1 '^name' "$d/Cargo.toml" | cut -d'"' -f2)"); done
fi
MANIFEST=$TREE/rust/gate/crates/arbiter/Cargo.toml
# the wrapper the gate writes (`workspace_only`): the same text at the live directory's own path, so no build key moves
WRAP=$HOME/.cache/l7r-cargo-target/${TREE##*/}/cover-gate/instrument.sh
cd "$TREE" || exit 1
export CARGO_TARGET_DIR=$WORK/target
while IFS= read -r line; do
  k=${line%%=*}; v=${line#*=}; k=${k#export }; v=${v#[\'\"]}; v=${v%[\'\"]}
  export "$k=$v"
done < <("$HOME/.cargo/bin/cargo" llvm-cov show-env --manifest-path "$MANIFEST")
RF=$RUSTFLAGS
for f in "-C instrument-coverage" "--cfg=coverage" "--cfg=trybuild_no_target"; do RF=${RF//$f/}; done
export RUSTFLAGS=$(echo $RF) RUSTC_WORKSPACE_WRAPPER=$WRAP
args=(test --no-run --lib --quiet --message-format=json-render-diagnostics --manifest-path "$MANIFEST")
for p in "${PKGS[@]}"; do args+=(-p "$p"); done
load0=$(cut -d' ' -f1 /proc/loadavg)
s=$(date +%s.%N)
"$HOME/.cargo/bin/cargo" "${args[@]}" >"$LOGS/$LABEL.json" 2>"$LOGS/$LABEL.err"; rc=$?
e=$(date +%s.%N)
python3 -I - "$LOGS/$LABEL.json" "$LABEL" "$rc" "$(echo "$e - $s" | bc)" "$load0" "$(cut -d' ' -f1 /proc/loadavg)" <<'EOF'
import json, sys
path, label, rc, wall, l0, l1 = sys.argv[1:]
built, fresh = [], 0
for line in open(path):
    try: m = json.loads(line)
    except ValueError: continue
    if m.get("reason") == "compiler-artifact":
        if m.get("fresh"): fresh += 1
        else: built.append(m["target"]["name"] + (":test" if m.get("profile", {}).get("test") else ""))
print(f"{label}\trc={rc}\twall={float(wall):.1f}s\tcompiled={len(built)}\tfresh={fresh}\tload={l0}->{l1}\t{' '.join(sorted(built))}")
EOF
