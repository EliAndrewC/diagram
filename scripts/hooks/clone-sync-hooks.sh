#!/usr/bin/env bash
# clone-sync-hooks.sh resolve - THIS SESSION'S CLONE, printed for the shell guards that still ask (feature 449 T013 decision (c)).
#
# The guard itself - the prompt's sync with main, and the edit's routing, refusals and fast-forward - is Rust since T013:
# `rust/guard/src/guards/clone_sync_hooks.rs`, run by `scripts/hooks/l7r-guard.sh`. Four shell guards and `lib/guardlog.sh` still call
# `resolve` for the session's clone (the claim map first, then the session's name), so that one mode stays here until T051 deletes them.
#
# DON'T ROUTE THIS THROUGH `l7r-guard.sh`: the wrapper's no-binary path calls `guard_log`, and `guard_log` calls this - a call that
# never returns, each level more processes, until the host's process limit (T013, 2026-11-08, on the wrapper suite's own no-binary
# case). A suite that moves HOME would also start a cargo build from nothing on every firing. This mode needs no binary.
set -euo pipefail

SESSIONS_DIR=${CLONE_SESSIONS_DIR:-${HOME:-/home/agent}/.claude/sessions}  # CLONE_SESSIONS_DIR: test seam only
MODE=${1:-}
INPUT=$(cat 2>/dev/null || true)

# GUARD_EDIT_OK: a performance fix found while working (2026-09-27), no rule changed - THE PAYLOAD IS PARSED
# ONCE. Every `$(field x)` used to start its own python to re-read the same JSON: two per `pretool` (every tool
# call, every session), four per `resolve` (every guard firing, via guardlog.sh). `derive_main` below reads
# `cwd` on every run, so this one python replaces a spawn that was always paid. Each value is exactly what
# `field` printed - a string or '' (non-string, missing, unparsable), with a NUL dropped as bash drops one
# from a command substitution; a path not in the list still takes the old per-call route.
declare -A _FIELD=()
_FIELD_PATHS=(cwd session_id transcript_path tool_name tool_input.command tool_input.file_path)
if [ -n "$INPUT" ]; then
  while IFS= read -r -d '' _k && IFS= read -r -d '' _v; do _FIELD[$_k]=$_v; done < <(printf '%s' "$INPUT" | python3 -c "
import json, sys
paths = sys.argv[1:]
try:
    doc = json.load(sys.stdin)
except Exception:
    doc = None
for p in paths:
    d = doc
    for k in p.split('.'):
        d = d.get(k, {}) if isinstance(d, dict) else {}
    v = d if isinstance(d, str) else ''
    sys.stdout.write(p + '\0' + v.replace('\0', '') + '\0')" "${_FIELD_PATHS[@]}")
else
  for _k in "${_FIELD_PATHS[@]}"; do _FIELD[$_k]=''; done
fi

field() { # field <dotted.path> - pull a string field out of the hook's stdin JSON
  if [[ -v _FIELD[$1] ]]; then printf '%s\n' "${_FIELD[$1]}"; return 0; fi
  printf '%s' "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    for k in '$1'.split('.'):
        d = d.get(k, {}) if isinstance(d, dict) else {}
    print(d if isinstance(d, str) else '')
except Exception:
    print('')"
}

# THE ROOT IS DERIVED FROM THE HOOK'S cwd, NOT HARDCODED (feature 131, 2026-08-25 - GUARD_EDIT_OK:
# the split needs one script that works in both repositories). The harness hands every hook the
# session's cwd; its git top level is either main itself or a clone at <main>/.clones/<name>, and
# main is the part before /.clones/. CLONE_MAIN stays as the test seam; the fallback when there is
# no cwd at all (a hook driven by hand with an empty payload) is the repository THIS script lives
# in - since feature 131 that is /diagram here and /gm-assistant there, so it cannot be a literal
# (GUARD_EDIT_OK: split residue - the literal named the OTHER repository's main).
derive_main() {
  local cwd top
  cwd=$(field cwd)
  top=$(git -C "${cwd:-/nonexistent}" rev-parse --show-toplevel 2>/dev/null || true)
  case "$top" in
    */.clones/*) printf '%s' "${top%%/.clones/*}" ;;
    "")          printf '%s' "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)" ;;
    *)           printf '%s' "$top" ;;
  esac
}
MAIN=${CLONE_MAIN:-$(derive_main)}
MAPDIR=$MAIN/.clones/.session-clones

canonical_clone() { # canonical_clone <sid> [transcript] - print .clones/<kebab-name> for a session,
  # or "" if neither source names it (unresolvable -> caller falls through).
  # TWO SOURCES, transcript FIRST (GM 2026-08-27). /rename appends {"type":"custom-title"} to the
  # session's transcript (the hook input's transcript_path) synchronously, and /clear - which mints
  # a NEW session_id - re-emits it as line 1 of the new transcript before a first prompt can exist;
  # --resume carries it too. ~/.claude/sessions/<pid>.json is the running process's STATUS file,
  # rewritten asynchronously, so a lookup keyed by the post-/clear session_id could find no entry
  # yet and report "no human-given name" although the tab title (written from the same name) was
  # right all along. The sessions json stays as the FALLBACK, and remains the liveness source
  # (sid_is_live) - that is a different question and the PID filename answers it. The LAST
  # custom-title wins (a session renamed twice). An entry with a derived/auto title or blank name
  # is treated as UNNAMED -> the shared default, matching CLAUDE.md's naming rule.
  SID="$1" TP="${2:-}" MAIN="$MAIN" SDIR="$SESSIONS_DIR" python3 -c "
import glob, json, os, re, sys
sid, tp, main, sdir = os.environ['SID'], os.environ['TP'], os.environ['MAIN'], os.environ['SDIR']
if not sid:
    sys.exit(0)
name = source = None; found = False
if tp and os.path.isfile(tp):
    with open(tp, errors='replace') as fh:
        for line in fh:
            if 'custom-title' not in line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get('type') == 'custom-title' and str(r.get('customTitle') or '').strip():
                found, name, source = True, r['customTitle'], 'transcript'
for f in ([] if found else glob.glob(os.path.join(sdir, '*.json'))):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if sid in (d.get('id'), d.get('sessionId'), d.get('session_id')):
        found, name, source = True, d.get('name'), d.get('nameSource'); break
if not found:
    sys.exit(0)                       # unresolvable -> print nothing -> caller falls through
if source == 'derived' or not str(name or '').strip():
    name = os.path.basename(main.rstrip('/'))   # unnamed / auto-derived -> the repository's own (FORBIDDEN) name
    # GUARD_EDIT_OK: adding to a guard - the sentinel was the literal 'gm assistant', a split leftover; main's basename is forbidden here too
kebab = re.sub(r'\s+', '-', re.sub(r'[^a-z0-9\s-]', '', str(name).lower()).strip())
if kebab:
    print(os.path.join(main, '.clones', kebab))"
}

case $MODE in
  resolve)
    sid=$(field session_id)
    [ -n "$sid" ] || exit 0
    if [ -f "$MAPDIR/$sid" ]; then cat "$MAPDIR/$sid"; exit 0; fi
    canonical_clone "$sid" "$(field transcript_path)"
    exit 0
    ;;
  *)
    echo "clone-sync-hooks: the guard modes are Rust (rust/guard/src/guards/clone_sync_hooks.rs); only 'resolve' is left here" >&2
    exit 1
    ;;
esac
