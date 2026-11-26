#!/bin/bash
# t301-run.sh LABEL <cargo args...>   - the gate's cargo call by hand, -v in place of --quiet, from the tree's root
TREE=${TREE:-$(git rev-parse --show-toplevel)}; T=$HOME/.cache/l7r-cargo-target/${TREE##*/}
label=$1; shift; log=${LOGS:-/tmp}/t301-log-$label.txt
cd "$TREE" || exit 1
s=$(date +%s.%N)
CARGO_TARGET_DIR=${TGT:-$T} $HOME/.cargo/bin/cargo "$@" >"$log.out" 2>"$log"; rc=$?
e=$(date +%s.%N)
run=$(grep -c '^ *Running `.*--crate-name l7r' "$log"); fresh=$(grep -c '^ *Fresh l7r' "$log"); dirty=$(grep -c '^ *Dirty l7r' "$log")
printf '%-34s rc=%s %6.1fs  rustc-runs(l7r)=%s  Fresh(l7r pkgs)=%s  Dirty=%s  load=%s\n' "$label" $rc $(echo "$e - $s" | bc) $run $fresh $dirty "$(cut -d' ' -f1 /proc/loadavg)"
grep '^ *Dirty l7r' "$log" | sed "s|$TREE/||; s/^ */    /"
grep -o '^ *Running `.*--crate-name l7r[a-z_0-9]*.*' "$log" | python3 -I -c '
import sys,re,collections
c=collections.Counter()
for l in sys.stdin:
    n=re.search(r"--crate-name (\S+)",l).group(1); f=",".join(re.findall(r"feature=\\?\"(\w[\w-]*)",l)); 
    kind="test" if " --test " in l else ("bin" if "--crate-type bin" in l else "lib"); mode="check" if "--emit=dep-info,metadata " in l or "clippy-driver" in l else "build"
    c[(n,kind,mode,f)]+=1
per=collections.Counter()
for (n,k,m,f),v in c.items(): per[(n,k)]+=v
for (n,k,m,f),v in sorted(c.items()): print(f"      {n} {k} {m} [{f}]" + (f"   <- {per[(n,k)]} builds of this target in this one call" if per[(n,k)]>1 else ""))
'
