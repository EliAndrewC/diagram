#!/usr/bin/env python3
"""The work-budget check's round cap (the round arbiter's tooling fix on ask:444-T02-field-round-15).

WHY: the round cap counts a page check's rounds by its subjects (`hm_checks.dispatch`), and a `work-budget` bundle names none, so
nothing counted its rounds. After the arbiter's accept on ask:444-T02-field-round-9 ("no round 9 runs") the session ran field's
rounds 9 to 14 on its own judgment - 33 minutes of dispatches and edits - with no guard firing. A stage's rounds are its recorded
MODE BUDGET verdicts, `specs/<feature>/phases/<stage>.verdict-<N>.txt`.

THE RULE, at a `work-budget` dispatch on `/tmp/l7r-check/work-budget-budget-<stage>/`: refused when the newest arbiter ruling naming
the stage is an ACCEPT given after its last verdict (the derivation stands; an edit to a Total or a Bounds figure re-owes a ruling
through `make arbiter-ask`, never a fresh dispatch), or when the stage has `ROUND_CAP` verdicts or more and no arbiter CONTINUE naming
it was given after its last verdict. The escape is the arbiter's own, `ARBITER_OK` with a reason in the prompt.
"""

from __future__ import annotations

import datetime
import re
from pathlib import Path

ROUND_CAP = 2
_STAGE = re.compile(r"/work-budget-budget-([a-z_]+)/MANIFEST\.md")


def _utc(text: str) -> float:
    try:
        return datetime.datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def refusal(feature_dir: Path | None, rulings: dict[str, dict], prompt: str) -> str:
    """'' when a `work-budget` dispatch may go, else why not (the module docstring)."""
    m = _STAGE.search(prompt)
    if not m or feature_dir is None:
        return ""
    stage = m.group(1)
    verdicts = sorted((feature_dir / "phases").glob(f"{stage}.verdict-*.txt"))
    last = max((p.stat().st_mtime for p in verdicts), default=0.0)
    named = re.compile(rf"(?<![a-z_]){re.escape(stage)}(?![a-z_])")
    about = sorted(
        ((_utc(str(r.get("utc", ""))), t, r) for t, r in rulings.items() if named.search(t) or named.search(str(r.get("what", "")))),
        key=lambda x: x[0],
    )
    since = [x for x in about if x[0] > last]
    if since and since[-1][2].get("ruling") == "accept":
        return (
            f"the round arbiter accepted {stage}'s derivation ({since[-1][1]}) after its last verdict - no further work-budget round "
            f"runs on it; an edit to a Total or a Bounds figure re-owes a ruling: make arbiter-ask SUBJECT=<id> WHY=\"<what changed>\""
        )
    if len(verdicts) >= ROUND_CAP and not any(x[2].get("ruling") == "continue" for x in since):
        return (
            f"round {len(verdicts) + 1} of work-budget on {stage} passes its cap of {ROUND_CAP} with no arbiter continue since "
            f"{verdicts[-1].name} - bring it to the round arbiter first: make arbiter-ask SUBJECT=<feature>-{stage}-round-{len(verdicts) + 1} "
            "WHY=\"<the verdicts and what changed>\" FILES=\"<the verdict files>\""
        )
    return ""
