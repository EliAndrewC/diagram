#!/bin/bash
# probe.sh - feature 274 R2 (plan D9): a page session's first-turn input under the OLD flags and the NEW.
#
# Two headless sessions of one turn each, run from this clone as the page-session runner runs them, each asked for one
# word. OLD is the launch as it was before 274: the standing authorization appended, only the MIRROR's root CLAUDE.md
# excluded. NEW is `floor_flags` as it is now: the clone's own root CLAUDE.md excluded too, the slim rules file
# appended after the authorization. Prints each session's first-turn input (uncached + cache write + cache read).
set -uo pipefail
ROOT=$(git rev-parse --show-toplevel)
OUT=${1:-/tmp/274-probe}; mkdir -p "$OUT"
ASK="Reply with the single word OK and nothing else. Do not use any tool."
python3 - "$ROOT" "$OUT" <<'PY'
import json, os, subprocess, sys, uuid
root, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(root, "scripts"))
import _page_session_runner as ps
mirror = root.split("/.clones/")[0]
old = ["--disable-slash-commands", "--strict-mcp-config", "--tools", ps.TOOLS,
       "--settings", json.dumps({"claudeMdExcludes": [f"{mirror}/CLAUDE.md"]}),
       "--append-system-prompt", open(os.path.join(root, ps.PROMPT_FILES[0])).read()]
new = ps.floor_flags(root)
ask = "Reply with the single word OK and nothing else. Do not use any tool."
env = ps.headless_env(os.environ, ps.dispatcher(root))
for label, flags in (("old", old), ("new", new)):
    sid = str(uuid.uuid4())
    cmd = ["claude", "-p", ask, "-n", os.path.basename(root), "--session-id", sid, "--permission-mode", "bypassPermissions", *flags, "--output-format", "json"]
    got = subprocess.run(cmd, cwd=root, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False)
    open(os.path.join(out, f"{label}.json"), "w").write(got.stdout)
    try:
        u = json.loads(got.stdout)["usage"]
    except (ValueError, KeyError):
        print(f"{label}: no usage - rc={got.returncode} {got.stdout[:300]} {got.stderr[:300]}")
        continue
    first = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
    print(f"{label}: session {sid} first-turn input {first} (uncached {u.get('input_tokens')}, cache write {u.get('cache_creation_input_tokens')}, cache read {u.get('cache_read_input_tokens')}), output {u.get('output_tokens')}")
PY
