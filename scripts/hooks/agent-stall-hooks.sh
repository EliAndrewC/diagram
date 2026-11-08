#!/usr/bin/env bash
# agent-stall-hooks.sh <check|watch|pending|ack> ... - the path a session runs by hand (feature 449 T015 decision (b)).
#
# The guard is Rust since T015: `rust/guard/src/guards/agent_stall_hooks.rs`, run by `scripts/hooks/l7r-guard.sh`. Its report and
# engine-freeze's refusal print the exact command `scripts/hooks/agent-stall-hooks.sh ack <dir> <id>`, and a Monitor runs `watch`, so
# this path stays, holding nothing else, until T051.
case "${1:-}" in
  check|watch|pending|ack) exec "${BASH_SOURCE[0]%/*}/l7r-guard.sh" --agent-stall "$@" ;;
  *) echo "usage: $0 check <dir>|watch <dir>|pending <dir>|ack <dir> <id>  (the guard itself is rust/guard/src/guards/agent_stall_hooks.rs)" >&2; exit 2 ;;
esac
