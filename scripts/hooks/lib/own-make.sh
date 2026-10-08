#!/usr/bin/env bash
# own-make.sh <target words...> - exit 0 while a `make <target>` runs in THIS working tree, 1 otherwise.
#
# What a waiter means by `pgrep -f "make done"`, scoped to the session that asks. pgrep searches the whole
# host, and several sessions gate at once (each clone runs its own `make done`), so a host-wide match on
# another clone's run holds a waiter open after its own run has finished. The real one, 2026-09-28: a waiter on
# a detached gate in diagram-shrines looped on `pgrep -f "[m]ake done"` for six hours after that gate had failed
# in two minutes, held by diagram-kashikawa's gates. `no-poll-hooks.sh` rewrites such a match to this helper.
#
# A process belongs to this tree when its working directory is inside the git toplevel of the directory the
# helper runs in (a waiter runs where its session works). The pattern here is built from the arguments, so this
# helper's own command line (`own-make.sh done`) never matches it.
set -uo pipefail
[ $# -ge 1 ] || { echo "usage: own-make.sh <make target>" >&2; exit 2; }
top=$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)
target="$*"
# GUARD_EDIT_OK: 2026-09-30 (GM: "Yes, please go ahead") - ONLY A MAKE PROCESS COUNTS. The waiting shell that LAUNCHED
# the run carries "make <target>" in its own command line (`setsid nohup make map ... & until ! own-make.sh map ...`),
# its working directory is this tree, and so it counted itself as the run and waited four hours past a map roll that
# had finished (diagram-readability, 2026-09-30). A process counts only when its first argument is make itself.
for pid in $(pgrep -f "[m]ake ${target}" 2>/dev/null); do
  argv0=$(tr '\0' '\n' < "/proc/$pid/cmdline" 2>/dev/null | head -1) || continue
  case "${argv0##*/}" in make | "make "* | gmake | "gmake "*) ;; *) continue ;; esac
  cwd=$(readlink "/proc/$pid/cwd" 2>/dev/null) || continue
  case "$cwd/" in "$top"/*) exit 0 ;; esac
done
exit 1
