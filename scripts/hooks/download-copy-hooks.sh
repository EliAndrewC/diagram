#!/usr/bin/env bash
# download-copy-hooks.sh - a PreToolUse hook that stops a session writing the GM's copy of the download list (feature 313).
#
# WHY (the GM, 2026-10-02, specs/313-download-list/request.md): the GM's working file "should be an actual copy and not
# the canonical source"; the GM marks it as they work, says "ingest", and later "sync". Until feature 313 every session
# appended to /host-l7r-repo/academic-sources/TO-DOWNLOAD.md by hand, by a rule nothing held. Now the canonical list is
# research/to-download.md: a session adds there (`make download-add`), and the copy is written by `make downloads-sync`
# alone - which refuses while the copy holds marks not yet ingested, so a GM's tick is never overwritten. A session's own
# write to the copy would bypass exactly that, so it is refused here. The make targets pass: they run a script, which a
# PreToolUse hook does not see, and they carry their own refusals.
#
# Matched as an INVOCATION, never a mention (docs/guards.md): reading, grepping or diffing the copy is fine.
# ESCAPE: DOWNLOAD_COPY_OK with a reason, recorded - for a repair the GM asks for in so many words.
# GUARD_EDIT_OK: feature 313 - a NEW guard.
set -uo pipefail

MODE="${1:-pretool}"
[ "$MODE" = pretool ] || exit 0
INPUT=$(cat)
DC_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$DC_HERE/lib/guardlog.sh"
case "$INPUT" in *TO-DOWNLOAD*) ;; *) exit 0 ;; esac
if escape_or_refuse download-copy DOWNLOAD_COPY_OK gm-authorized "$DC_HERE"; then exit 0; fi

HIT=$(printf '%s' "$INPUT" | python3 -c '
import json, re, sys
try:
    d = json.load(sys.stdin)
except Exception:
    print(""); raise SystemExit
inp = d.get("tool_input", {}) or {}
copy = r"(?:/host-l7r-repo/)?academic-sources/TO-DOWNLOAD\.md"
if d.get("tool_name", "") in ("Write", "Edit", "NotebookEdit"):
    p = inp.get("file_path", "")
    print(p if re.search(r"(^|/)academic-sources/TO-DOWNLOAD\.md$", p) else "")
    raise SystemExit
cmd = inp.get("command", "") or ""
# The name adjacent to a writing operator: a redirect, tee, sed -i, cp or mv onto it, or a Python write to it.
pat = rf"(?:>>?\s*|sed\s+-i\b[^;|&]*?|tee\s+(?:-a\s+)?|(?:cp|mv|install)\s+(?:-\S+\s+)*\S+\s+)[\x27\x22]?[\w./-]*{copy}"
m = re.search(pat, cmd) or re.search(rf"{copy}[\x27\x22]\s*\)?\s*\)?\s*\.(?:write_text|write_bytes)", cmd) or re.search(rf"open\(\s*[\x27\x22][\w./-]*{copy}[\x27\x22]\s*,\s*[\x27\x22][wa]", cmd)
print(m.group(0) if m else "")
')

[ -z "$HIT" ] && exit 0

cat >&2 <<'TAIL'
BLOCKED: writing the GM's copy of the download list.

/host-l7r-repo/academic-sources/TO-DOWNLOAD.md is the GM's working copy: they tick its boxes as they work. The
canonical list is research/to-download.md (feature 313).

  - a source only the GM can fetch:   make download-add FILE=<draft.md>   (entries headed "### NEW. <the work>",
                                       appended at the end)
  - the GM said "ingest":             make downloads-ingest
  - the GM said "sync":               make downloads-sync   (refused while the copy holds marks not ingested)

The one escape is a repair the GM asks for in their own words: DOWNLOAD_COPY_OK with a reason that quotes it.
(scripts/hooks/download-copy-hooks.sh; feature 313)
TAIL
guard_log download-copy blocked "$(guard_cmd)" the-gm-s-copy
exit 2
