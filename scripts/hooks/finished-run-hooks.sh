#!/usr/bin/env bash
# finished-run-hooks.sh <check|seen|live|judge|stale> ... - the path `l7r-gate reviews prereq gate-state` asks (feature 449 T017 decision (b); GUARD_EDIT_OK: 449 T89 ported its caller, a comment only).
#
# The guard is Rust since T017: `rust/guard/src/guards/finished_run_hooks.rs`, run by `scripts/hooks/l7r-guard.sh`. This path answers
# `live <clone>` for a Python tool of phase 3, and holds nothing else, until T051.
case "${1:-}" in
  check|seen|live|judge|stale) exec "${BASH_SOURCE[0]%/*}/l7r-guard.sh" --finished-run "$@" ;;
  *) echo "usage: $0 check <clone>|seen <clone>|live <clone>|judge <clone>|stale [clone]  (the guard itself is rust/guard/src/guards/finished_run_hooks.rs)" >&2; exit 2 ;;
esac
