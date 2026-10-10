#!/usr/bin/env bash
# event-log-hooks.sh - one line per hook event into the feature's event log (feature 375, FR-008, plan D7).
# (GUARD_EDIT_OK: a NEW hook - it records, it never refuses.)
#
# WHY. The GM, 2026-10-10: a table of where a feature's time went - tests, thinking, implementing, waiting on reviews -
# should come from "hooks built into our tooling which will save off timestamps", so that `make feature-report` answers in
# seconds what took a hand reading of a transcript for feature 372. The line and its fields are
# `scripts/measure/event_log.py`'s; this wrapper only hands it the payload.
#
# WIRED on PreToolUse, PostToolUse, SubagentStart, SubagentStop, UserPromptSubmit and Stop, with no matcher, so every
# tool call is seen. It ALWAYS exits 0 and prints nothing: a hook on every call must not be able to stop one, and its
# output would be read as a hook's message.
EL_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -S "$EL_HERE/../measure/event_log.py" hook >/dev/null 2>&1
exit 0
