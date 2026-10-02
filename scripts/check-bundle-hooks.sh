#!/bin/bash
# check-bundle-hooks.sh - a record check reads a BUNDLE, not the repository (feature 250).
# GUARD_EDIT_OK: feature 250 - a NEW guard, part of the token work the GM asked for on 2026-09-26.
#
# THE FAILURE. The moment a defined agent reads a file under the repository, the harness attaches every
# `CLAUDE.md` above that file to its context - about 28,400 tokens for a file under `research/`. Measured
# on feature 250's slice (research R1): all nine check runs, 55-65% of each one's context, five to twelve
# times what the check read of the record. `omitClaudeMd` (feature 256) drops only the copy given at
# LAUNCH. A check handed copies outside the repository attached nothing; peak 47,700 -> 14,500.
#
# WHAT IT DOES. A dispatch of `quote-check`, `record-format`, `source-applicability`, `source-reader`, `entry-drift` or `record-style`
# whose prompt names a file under the repository and no bundle is REFUSED, and the refusal carries the
# `make check-bundle` command for the question the prompt names, read off its path. It cannot BUILD the
# bundle itself: the bundle fetches every quoted page, and a hook that takes a minute is worse than a
# refusal. A prompt that names a bundle's `MANIFEST.md` passes, as does one that names no repository file
# at all (a reader handed only URLs).
#
# ESCAPE: `CHECK_BUNDLE_OK="<reason>"` in the prompt, with a reason of two words or more - for a check
# that genuinely needs a file the bundle does not carry and cannot be given with EXTRA=.
#
# Modes:
#   pretool (PreToolUse, Agent)   refuse / pass, recorded
set -uo pipefail

MODE=${1:-}
CB_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$CB_HERE/_guardlog.sh"

#: the checks whose contract reads a bundle (`.claude/agents/<name>.md`, "Read the BUNDLE")
# GUARD_EDIT_OK: feature 292 - record-style and translation-check are new bundle-reading checks; added to the list, nothing is loosened.
# GUARD_EDIT_OK: feature 303 - the questions are research/questions/NNNN-<slug>.html; the compliant command is read off
# that path as `make check-bundle Q=NNNN`. A change of layout; nothing loosened.
# GUARD_EDIT_OK: feature 311 - intro-check is a new bundle-reading check; added, nothing loosened.
CHECKS="quote-check record-format source-applicability source-reader entry-drift record-style translation-check intro-check"

pretool() {
  local verdict kind detail reason
  INPUT="$(cat)"
  verdict="$(printf '%s' "$INPUT" | CHECKS="$CHECKS" python3 -c '
import json, os, re, sys
try:
    p = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if p.get("tool_name") != "Agent":
    sys.exit(0)
ti = p.get("tool_input") or {}
atype, prompt = str(ti.get("subagent_type") or ""), str(ti.get("prompt") or "")
if atype not in os.environ["CHECKS"].split():
    sys.exit(0)
esc = re.search(r"CHECK_BUNDLE_OK=\"([^\"]*)\"", prompt)
if esc:
    print("\x1fescape\x1f" + esc.group(1)); sys.exit(0)
if "MANIFEST.md" in prompt:
    # GUARD_EDIT_OK: feature 311 - a NEW refusal: a check the bundle does not owe is not dispatched (the GM, 2026-10-02:
    # a formatting tweak must not re-run every check). The MANIFEST names what may be dispatched on it (`owed-checks:`,
    # written by `make check-bundle` from `_record_owed.py`); record-style is owed by a declared sweep, never a delta.
    nok = re.search(r"CHECK_NOT_OWED_OK=\"([^\"]*)\"", prompt)
    if nok:
        print("\x1fnotowed\x1f" + nok.group(1)); sys.exit(0)
    if atype != "record-style":
        for mp in re.findall(r"(/[^\s`\"<>)]*MANIFEST\.md)", prompt):
            try:
                text = open(mp, encoding="utf-8").read()
            except OSError:
                continue
            owed = re.search(r"^owed-checks: *(.*)$", text, re.M)
            if owed is None or atype not in owed.group(1).split():
                print("\x1fnotowed-refuse\x1f" + atype + "\x1e" + mp + "\x1e" + (owed.group(1).strip() if owed else "(none - a bundle from before feature 311: build it again)") or "nothing"); sys.exit(0)
    print("\x1fbundle\x1f" + atype); sys.exit(0)
paths = re.findall(r"(?:/diagram(?:/\.clones/[\w.-]+)?/)?\.claude/skills/diagram/research/[^\s`\"<>)]+", prompt)
if not paths:
    print("\x1fnone\x1f" + atype); sys.exit(0)
cmds = []
for path in paths:
    # GUARD_EDIT_OK: feature 303 - a question is research/questions/NNNN-<slug>.html now; a change of layout
    m = re.search(r"research/questions/(\d{4})-[^/]*\.html$", path)
    k = re.search(r"research/sources/010-works-cited/\d+-([a-z0-9-]+)\.html$", path)
    if k:
        # D19 (plan review): a source-reader hunts the passage behind a NEW claim, so it gets the whole page in parts;
        # the excerpt around already-quoted passages is for source-applicability (no apostrophe: this is single-quoted)
        cmds.append(f"make check-bundle KEY={k.group(1)}" + (" WHOLE=1" if atype == "source-reader" else ""))
    elif m:
        # GUARD_EDIT_OK: feature 303 - the compliant command names the question by its number (Q=), nothing loosened
        cmds.append(f"make check-bundle Q={m.group(1)}" + (f" FOR={atype}" if atype in ("record-style", "translation-check") else ""))
cmds = list(dict.fromkeys(cmds)) or ["make check-bundle Q=<question number>   (or KEY=<registry key>)"]
print("\x1frefuse\x1f" + atype + "\x1e" + "\x1e".join(cmds))
' 2>/dev/null)" || exit 0
  IFS=$'\x1f' read -r _ kind detail <<<"$verdict"
  case "$kind" in
    "" ) exit 0 ;;
    none )   guard_log check-bundle permitted "$detail names no repository file" no-repo-path; exit 0 ;;
    bundle ) guard_log check-bundle permitted "$detail reads a bundle" bundle-named; exit 0 ;;
    notowed )
      # GUARD_EDIT_OK: feature 311 - the escape for the not-owed refusal, held to the same reason floor as every escape
      if printf '%s' "$detail" | "$CB_HERE/_hm_escape.py" reason-ok >/dev/null 2>&1; then
        guard_log check-bundle escaped "$detail" check-not-owed-ok
        exit 0
      fi
      guard_log check-bundle blocked "CHECK_NOT_OWED_OK=\"$detail\"" CHECK_NOT_OWED_OK-no-reason
      printf 'BLOCKED: CHECK_NOT_OWED_OK needs a REASON - two words and eight characters - so the audit says why.\n' >&2
      exit 2 ;;
    notowed-refuse )
      local natype=${detail%%$'\x1e'*} rest=${detail#*$'\x1e'}
      local mp=${rest%%$'\x1e'*} owedlist=${rest#*$'\x1e'}
      guard_log check-bundle blocked "$natype not owed on $mp" not-owed
      {
        printf '\n\033[1mBLOCKED: `%s` is not owed on this bundle.\033[0m\n\n' "$natype"
        printf 'Its MANIFEST (%s) owes: %s\n' "$mp" "$owedlist"
        printf 'A check is owed only where the words it reads changed (`make record-owed` lists every unit, feature 311) -\n'
        printf 're-running it on words it already passed is the waste the GM named. Dispatch only what is owed;\n'
        printf 'a check the GM asked for, or a backfill: CHECK_NOT_OWED_OK="<why>" in the prompt.\n'
        printf '(scripts/check-bundle-hooks.sh; feature 311)\n'
      } >&2
      exit 2 ;;
    escape )
      reason="$detail"
      if printf '%s' "$reason" | "$CB_HERE/_hm_escape.py" reason-ok >/dev/null 2>&1; then
        guard_log check-bundle escaped "$reason" check-bundle-ok
        exit 0
      fi
      guard_log check-bundle blocked "CHECK_BUNDLE_OK=\"$reason\"" CHECK_BUNDLE_OK-no-reason
      printf 'BLOCKED: CHECK_BUNDLE_OK needs a REASON - two words and eight characters - so the audit says why.\n' >&2
      exit 2 ;;
    refuse )
      local atype=${detail%%$'\x1e'*} cmds=${detail#*$'\x1e'}
      guard_log check-bundle blocked "$atype dispatched into the repository" repo-path
      {
        printf '\n\033[1mBLOCKED: this `%s` dispatch points the agent at files IN the repository.\033[0m\n\n' "$atype"
        printf 'Reading one attaches every CLAUDE.md above it - about 28,000 tokens, 55-65%% of a check'"'"'s context\n'
        printf 'on the measured runs (feature 250, research R1). Copy what it reads out first:\n\n'
        printf '%s\n' "${cmds//$'\x1e'/$'\n'}" | sed 's/^/    /'
        printf '\nthen re-send the dispatch naming the MANIFEST.md it prints (and nothing under /diagram).\n'
        printf 'A file the bundle lacks: EXTRA="<path> ..." on the same command. A check that truly cannot be\n'
        printf 'bundled: CHECK_BUNDLE_OK="<why>" in the prompt.\n'
        printf '(scripts/check-bundle-hooks.sh; feature 250)\n'
      } >&2
      exit 2 ;;
  esac
  exit 0
}

case "$MODE" in
  pretool) pretool ;;
  *) echo "check-bundle-hooks: unknown mode '$MODE' (want: pretool)" >&2; exit 1 ;;
esac
