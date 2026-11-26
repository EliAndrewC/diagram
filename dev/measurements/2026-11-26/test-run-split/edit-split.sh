#!/bin/sh
# 451 T315: a one-line edit's test run as a builder has it (no FRESH), crate by crate, with the process list sampled through it
# (ps-sample.py): the wall, the Phase lines, and from the samples the seconds each rustc and the linker (`cc`, which runs rust-lld) lived.
# A constant with a new value is appended to the crate's lib.rs, twice (e1, e2); the file is put back whatever happens.
# usage: edit-split.sh <out dir> <crate dir> <a word of the tree's paths>      (from the tree's root)
out="$1"; crate="$2"; word="$3"; here="$(dirname "$0")"; lib="$crate/src/lib.rs"; tag="$(echo "$crate" | tr / _)"
trap 'git checkout -- "$lib"' EXIT INT TERM
for step in e1 e2; do
  # a value no earlier run had: the kept result is keyed by content, so the same edit twice runs nothing the second time
  git checkout -- "$lib"; printf '\npub const T315_PROBE: u64 = %s;\n' "$(date +%s%N)" >> "$lib"
  NOFRESH=1 python3 "$here/ps-sample.py" "$word" -- "$here/gate-run.sh" "$crate" "$out" "split-$step" > "$out/$tag-split-$step.ps" 2>&1
  grep "^rust/" "$out/$tag-split-$step.ps" | sed 's/libtest.*//'
  awk '/bin\/rustc --crate-name/ { n=$5; for (i=6;i<=NF;i++) if ($i=="--test") n=n"(test)"; printf "    rustc %s %.2f s;", n, $2-$1+0.05 }
       / cc -m64| cc / && /rcgu/ { printf "    linker %.2f s;", $2-$1+0.05 }
       /cargo build --profile tool/ { printf "    tool build %.2f s (%s);", $2-$1+0.05, $NF }
       /rustdoc/ { printf "    rustdoc %.2f s;", $2-$1+0.05 } END { print "" }' "$out/$tag-split-$step.ps"
done
