# seen.sh - sourced by the guard suites (451 T253): `seen VAR <grep args>` greps the text of the variable named VAR from a here-string.
# GUARD_EDIT_OK: feature 451 T253 - the one definition of the suites' text grep.
#
# NEVER A PIPE (451 T252, T253): under pipefail, `printf '%s' "$OUT" | grep -q X` failed when grep matched early and exited while the
# writer still had text to write - the writer died of SIGPIPE, the pipeline returned 141, a line the printed output showed was reported
# absent, and a negated check passed on a line that is there (1 in 3,000 at real size pinned to one CPU; 50 of 50 on a line followed by
# 1.3 MB, measured 2026-11-25). A here-string has no writer process to kill. A command's text is captured first: `o=$(cmd) && seen o -q X`
# keeps what pipefail asked of the writer, its success. `l7r-gate check pipe-race`, run by every `make hooks-test`, refuses the pipe form.
seen() { local __seen_var=$1; shift; grep "$@" <<< "${!__seen_var}"; }
