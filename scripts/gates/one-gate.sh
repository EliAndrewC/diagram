#!/usr/bin/env bash
# one-gate.sh - exit 1, saying why, while a `make done` already runs in THIS working tree; 0 otherwise.
#
# `make verify` starts the gate detached and returns, so a second `make verify` in the same turn started a second gate
# beside the first. Killing the duplicate removed the first one's invocation token, and every roll the first then made
# was refused as not invoked through make - a whole gate of errors (feature 328 batch 7, 2026-10-09). One gate per tree.
set -uo pipefail
own="$(dirname "${BASH_SOURCE[0]}")/../hooks/lib/own-make.sh"
if "$own" --no-print-directory done || "$own" done; then
  printf '\n\033[1mA GATE IS ALREADY RUNNING IN THIS TREE\033[0m - not starting another. Wait on its log: until grep -qE "verification-state|GATE FAILED" .git/verify-gate.log; do sleep 20; done\n'
  exit 1
fi
exit 0
