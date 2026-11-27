#!/bin/bash
# featsets.sh [edges]: for each workspace member's manifest, the features cargo resolves for every l7r crate in its
# test build (edges normal,dev by default); prints each crate with more than one feature set and the roots under each.
TREE=${TREE:-$(git rev-parse --show-toplevel)}; E=${1:-normal,dev}
cd "$TREE" || exit 1
for m in rust/phases rust/guard rust/guard/shared rust/gate rust/gate/crates/* rust/browser rust/embed rust/mode_a; do
  [ -f $m/Cargo.toml ] || continue
  $HOME/.cargo/bin/cargo tree --offline -e $E --prefix none -f "{p} [{f}]" --manifest-path $m/Cargo.toml 2>/dev/null \
   | grep '^l7r' | sed 's/ v[0-9.]* ([^)]*)//; s/ (\*)//' | sort -u | sed "s|\$| ROOT=${m#rust/}|"
done | python3 -I -c '
import sys,collections
d=collections.defaultdict(lambda: collections.defaultdict(list)); roots=set()
for l in sys.stdin:
    a,r=l.rstrip().rsplit(" ROOT=",1); n,f=a.split(" ",1); d[n][f].append(r); roots.add(r)
multi=0
for n in sorted(d):
    if len(d[n])>1:
        multi+=1
        print(n)
        for f,rs in sorted(d[n].items()): print("   ",f,len(rs),"roots:"," ".join(rs) if len(rs)<8 else " ".join(rs[:8])+" ...")
print(f"roots={len(roots)} crates={len(d)} crates-with-more-than-one-feature-set={multi}")
'
