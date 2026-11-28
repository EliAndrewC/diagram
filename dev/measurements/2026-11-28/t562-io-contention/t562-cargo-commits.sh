#!/usr/bin/env bash
# t562 lever C's premise: journal forced commits a second while a cargo build runs (a cold build of rust/phases and rust/guard into a scratch
# target, from a git archive of HEAD) against the same machine's rate in the minute before and after it. Usage: <scratch> <out>
set -u
S=$1; OUT=$2; J=/proc/fs/jbd2/nvme0n1p3-8/info
req() { sed -n 's/.*(\([0-9]*\) requested).*/\1/p' $J; }
rm -rf "$S"; mkdir -p "$S/src"; git -C /diagram/.clones/diagram-backlog-t270 archive HEAD rust | tar -x -C "$S/src"
span() { local q0 t0; q0=$(req); t0=$(date +%s.%N); "$@"; printf '%s\t%.1f\t%s\t%s\n' "$label" "$(echo "$(date +%s.%N)-$t0"|bc)" $(( $(req)-q0 )) "$(cut -d' ' -f1 /proc/loadavg)"; }
{ printf 'span\tseconds\tforced_commits\tload_after\n'
  label=before span python3 -I -c 'import time; time.sleep(60)'
  label=cargo-build span env CARGO_TARGET_DIR="$S/target" cargo build --quiet --manifest-path "$S/src/rust/Cargo.toml" -p l7r_phases -p l7r_guard
  label=after span python3 -I -c 'import time; time.sleep(60)'; } > "$OUT"
rm -rf "$S"
