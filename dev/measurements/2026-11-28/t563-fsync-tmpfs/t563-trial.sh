#!/usr/bin/env bash
# t563 trial: one run of the four fixture-heavy test binaries (shared, guard, lane, task) under one SETTING:
#   default - the tests' TMPDIR a fresh directory on the disk (/tmp/l7r-tmp), git's own fsync
#   A       - the same, git told core.fsync=none through GIT_CONFIG_COUNT/KEY/VALUE (as the runners would set beside TMPDIR)
#   B       - TMPDIR a tmpfs mounted in a user+mount namespace, the tests run as uid 1000 in a nested user namespace
#   AB      - both
# The binaries get side.rs's environment (PATH with cargo's bin first, RUSTC_BOOTSTRAP, CARGO_TARGET_DIR, CARGO, CARGO_MANIFEST_DIR,
# CARGO_PKG_NAME). Appends one row per binary to OUT: setting, binary, seconds, exit, load, io-pressure some avg10, jbd2 forced
# commits over the run, and (B) the tmpfs's peak use in KiB sampled at the binary's end.
# Usage: t563-trial.sh <setting> <out.tsv> <bin-list-file>
set -u
SET=${1:?}; OUT=${2:?}; BINS=${3:?}
J=/proc/fs/jbd2/nvme0n1p3-8/info
req() { sed -n 's/.*(\([0-9]*\) requested).*/\1/p' $J; }
psi() { sed -n 's/^some avg10=\([0-9.]*\).*/\1/p' /proc/pressure/io; }
mkdir -p /tmp/l7r-tmp
TMP=$(mktemp -d /tmp/l7r-tmp/t563-trial.XXXXXX)
export PATH="$HOME/.cargo/bin:$PATH" RUSTC_BOOTSTRAP=1 CARGO="$HOME/.cargo/bin/cargo" \
  CARGO_TARGET_DIR="$HOME/.cache/l7r-cargo-target/diagram-backlog-t271"
case $SET in A|AB) export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsync GIT_CONFIG_VALUE_0=none ;; esac
while read -r name exe dir pkg; do
  [ -n "$name" ] || continue
  sub=$TMP/$name; mkdir -p "$sub"
  l=$(cut -d' ' -f1 /proc/loadavg); p=$(psi); q0=$(req); t0=$(date +%s.%N)
  used=-
  case $SET in
    B|AB)
      used=$(unshare -Urm sh -c 'mount -t tmpfs -o size=256m,mode=1777 tmpfs "$1" || exit 99; cd "$3" &&
        unshare --map-user=1000 --map-group=1000 -U env TMPDIR="$1" CARGO_MANIFEST_DIR="$3" CARGO_PKG_NAME="$4" "$2" -q > "$5" 2>&1
        rc=$?; df -k --output=used "$1" | tail -1 | tr -d " "; exit $rc' sh "$sub" "$exe" "$dir" "$pkg" "$TMP/$name.log")
      code=$? ;;
    *)
      ( cd "$dir" && TMPDIR=$sub CARGO_MANIFEST_DIR=$dir CARGO_PKG_NAME=$pkg "$exe" -q ) > "$TMP/$name.log" 2>&1
      code=$? ;;
  esac
  t1=$(date +%s.%N); q1=$(req)
  printf '%s\t%s\t%.2f\t%s\t%s\t%s\t%s\t%s\n' "$SET" "$name" "$(echo "$t1-$t0" | bc)" "$code" "$l" "$p" $((q1-q0)) "$used" >> "$OUT"
  [ $code = 0 ] || cp "$TMP/$name.log" "$OUT.$SET.$name.$$.fail.log"
done < "$BINS"
rm -rf -- "$TMP"
