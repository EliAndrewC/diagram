#!/bin/bash
# family.sh OUTDIR PASS...   - T325's re-measurement, T301 part 1's way (cargo-hashes/gate-call.sh): the gate's test build
# (`cargo test --no-run --message-format=json`, -v for --quiet) of each of the 28 gate manifests in turn, one call at a time.
#   PASS warm    : every manifest once, nothing touched (brings the tree's cache up; its figures are first builds)
#   PASS touch   : `touch rust/gate/crates/core/src/lib.rs`, then every manifest once; the summary counts rustc runs against
#                  distinct targets (crate, lib or test, its root source file) - the difference is a target compiled again in another configuration
#   PASS same    : every manifest once more, nothing touched (all Fresh expected)
TREE=${TREE:-$(git rev-parse --show-toplevel)}; HERE=$(cd "$(dirname "$0")" && pwd); CALL=${CALL:-$TREE/dev/measurements/2026-11-26/cargo-hashes/gate-call.sh}
out=$1; shift; mkdir -p "$out"
for pass in "$@"; do
  logs=$out/$pass; mkdir -p "$logs"
  [ "$pass" = touch ] && touch "$TREE/rust/gate/crates/core/src/lib.rs"
  s=$(date +%s.%N); l0=$(cut -d' ' -f1 /proc/loadavg)
  for m in "$TREE"/rust/gate/Cargo.toml "$TREE"/rust/gate/crates/*/Cargo.toml; do
    d=$(dirname "$m"); n=$(basename "$d")
    TREE=$TREE LOGS=$logs "$CALL" "$n" test --no-run --message-format=json -v --manifest-path "$m"
  done > "$out/$pass.txt" 2>&1
  e=$(date +%s.%N)
  python3 -I - "$logs" "$pass" "$(echo "$e - $s" | bc)" "$l0" "$(cut -d' ' -f1 /proc/loadavg)" <<'PY' | tee -a "$out/summary.txt"
import sys,re,glob,collections
logs,label,secs,l0,l1=sys.argv[1:]
runs=collections.Counter(); conf=collections.defaultdict(set); calls=0; rc_bad=0
for f in sorted(glob.glob(logs+"/t301-log-*.txt")):
    calls+=1
    for l in open(f,errors="replace"):
        if not re.match(r"^ *Running `.*--crate-name l7r",l): continue
        n=re.search(r"--crate-name (\S+)",l).group(1)
        kind="test" if " --test " in l else ("bin" if "--crate-type bin" in l else "lib")
        feats=",".join(sorted(re.findall(r'feature=\\?"(\w[\w-]*)',l)))
        src=re.search(r"--edition=\d+ (\S+)",l); src=src.group(1) if src else ""
        runs[(n,kind,src)]+=1; conf[(n,kind,src)].add(feats)
total=sum(runs.values()); targets=len(runs); again={k:v for k,v in runs.items() if v>1}
print(f"{label}: calls={calls} rustc-runs={total} targets={targets} repeats={total-targets} wall={float(secs):.1f}s load={l0}->{l1}")
for (n,k,s),v in sorted(again.items(), key=lambda x:(-x[1],x[0])):
    print(f"    {n} {k} ({s}): {v} times, feature sets {sorted(conf[(n,k,s)])}")
PY
done
