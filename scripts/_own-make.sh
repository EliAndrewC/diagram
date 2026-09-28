#!/usr/bin/env bash
# _own-make.sh <target words...> - exit 0 while a `make <target>` runs in THIS working tree, 1 otherwise.
#
# What a waiter means by `pgrep -f "make done"`, scoped to the session that asks. pgrep searches the whole
# host, and several sessions gate at once (each clone runs its own `make done`), so a host-wide match on
# another clone's run holds a waiter open after its own run has finished. The real one, 2026-09-28: a waiter on
# a detached gate in diagram-shrines looped on `pgrep -f "[m]ake done"` for six hours after that gate had failed
# in two minutes, held by diagram-kashikawa's gates. `no-poll-hooks.sh` rewrites such a match to this helper.
#
# A process belongs to this tree when its working directory is inside the git toplevel of the directory the
# helper runs in (a waiter runs where its session works). The pattern here is built from the arguments, so this
# helper's own command line (`_own-make.sh done`) never matches it.
set -uo pipefail
[ $# -ge 1 ] || { echo "usage: _own-make.sh <make target>" >&2; exit 2; }
top=$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)
target="$*"
for pid in $(pgrep -f "[m]ake ${target}" 2>/dev/null); do
  cwd=$(readlink "/proc/$pid/cwd" 2>/dev/null) || continue
  case "$cwd/" in "$top"/*) exit 0 ;; esac
done
exit 1
