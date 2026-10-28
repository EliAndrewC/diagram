#!/usr/bin/env python3
"""The decider for `budget-change-hooks.sh` (feature 443 T03, plan D6): a budget is raised, or the program's whole-roll budget set,
only with the GM's own words.

WHY (the GM's approval of the design, 2026-10-28, `specs/443-work-budget-tooling/request.md`): a work budget that a session could
raise on its own would be a figure to defend, not a goal. `make budget-change` and `make budget-program` carry `WORDS="<the GM's
words>"`; a make target cannot read the transcript, a hook can, so the words are checked here, exactly as an `**Approved**:` line
is (`hm_approval.problem` against `hm_approval.gm_messages`): three words or more, verbatim in a message the GM wrote in this
session. There is no escape: the GM's words are the way through.

    hm_budget.py judge < <hook payload>   -> the problem (`no-words`, `short`, `not-found`), nothing on a pass
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hm_approval import gm_messages, problem  # noqa: E402
from hm_make import targets  # noqa: E402

GUARDED = frozenset({"budget-change", "budget-program"})
_WORDS = re.compile(r"""(?<![\w-])WORDS=(?:"([^"]*)"|'([^']*)'|(\S+))""")


def judge(cmd: str, transcript: str) -> str:
    """'' when `cmd` invokes no guarded target or its WORDS are the GM's; else why not."""
    if not targets(cmd) & GUARDED:
        return ""
    m = _WORDS.search(cmd)
    words = next((g for g in m.groups() if g is not None), "") if m else ""
    if not words.strip():
        return "no-words"
    return problem(f'**Approved**: the GM, 2000-01-01, "{words}"', gm_messages(transcript))


def main(argv: list[str]) -> int:
    if argv[:1] != ["judge"]:
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0
    print(judge(str((payload.get("tool_input") or {}).get("command") or ""), payload.get("transcript_path") or ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
