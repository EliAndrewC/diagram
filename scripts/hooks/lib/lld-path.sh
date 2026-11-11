#!/usr/bin/env bash
# lld-path.sh - sourced by the two build wrappers, `scripts/gates/l7r-gate.sh` and `scripts/hooks/l7r-guard.sh`.
# lld_missing <tree>: true, with the fix on stderr, when <tree>/.cargo/config.toml links through a `gcc-ld` directory this machine lacks
# (feature 449 T96). Every cargo build reads that file, so a toolchain that moved would otherwise fail every link with gcc's
# "cannot find 'ld'", which names nothing to change.
lld_missing() {
  local cfg="$1/.cargo/config.toml" dir
  [ -f "$cfg" ] || return 1
  dir=$(grep -o -- '-B/[^"]*' "$cfg" | head -n 1)
  dir=${dir#-B}
  { [ -z "$dir" ] || [ -x "$dir/ld.lld" ]; } && return 1
  echo "the build links with rust-lld from $dir (.cargo/config.toml), which has no ld.lld: the toolchain moved. Set that -B path to \$(rustc --print sysroot)/lib/rustlib/x86_64-unknown-linux-gnu/bin/gcc-ld" >&2
  return 0
}
