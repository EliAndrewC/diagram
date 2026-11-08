#!/usr/bin/env bash
# guard-cases.sh - run the named case tests of the guard crate (feature 449 T050): the four guards whose cases are structured payloads keep them as crate tests
# (`rust/guard/src/guards/case_tables.rs`), and each of their suites comes here so that `make hooks-test` still answers for it.
# GUARD_EDIT_OK: feature 449 T050 - the shared runner's replacement.
#
# Usage: guard-cases.sh <test name> [<test name>...]
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tree=${here%/tests/hooks}
# A suite may move HOME; the real home, from the password database, pins cargo and its target directory, as `guard-shim.sh` does.
real=$(getent passwd "$(id -u)" | cut -d: -f6)
export RUSTUP_HOME="${RUSTUP_HOME:-$real/.rustup}" CARGO_HOME="${CARGO_HOME:-$real/.cargo}"
export CARGO_TARGET_DIR="${L7R_GUARD_TARGET:-$real/.cache/l7r-cargo-target/${tree##*/}}"
cargo=cargo; [ -x "$real/.cargo/bin/cargo" ] && cargo="$real/.cargo/bin/cargo"
exec "$cargo" test -q --manifest-path "$tree/rust/Cargo.toml" -p l7r_guard --lib -- "$@"
