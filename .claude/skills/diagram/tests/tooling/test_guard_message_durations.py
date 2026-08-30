"""No guard MESSAGE states how long a command takes (feature 161, GM 2026-08-30).

*"Also I think those numbers for `make quick` are wrong and outdated, though the attempt to get a
savings is still worthwhile."* They were, and worse than outdated: `gate-hooks.sh` said the gate cost
"~70 s with scope locked" while the scope had been UNLOCKED since 2026-08-27 and the gate was costing
a median of 111 s. A number typed into a shell string in August is wrong in September and nothing
tells anybody, because the number lives in a guard and the truth lives in `dev/run-log/`.

So a guard message may not carry one. It asks `scripts/_gatecost.py`, which reads the recorded runs,
or it says nothing at all - silence is the designed outcome, not a failure, because a message with no
number is honest and a message with a stale one is not.

WHAT THIS JUDGES, precisely: text a session actually SEES - heredoc bodies and the arguments of
`echo`, `printf` and the hooks' own `block` helper. A comment recording history ("measured
2026-08-26: 3 times in one task") is not a message and is not judged; the record of what something
once cost is exactly what this project asks sessions to write down.

Data-file test: it re-runs under testmon only when this file changes, and always at the gate.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
SCRIPTS = REPO / "scripts"

# a duration: `~70 s`, `4.5 min`, `~45s`, `3.9-minute`, `2.5-4 minutes`
_DURATION = re.compile(r"~?\d+(?:[.,]\d+)?(?:\s*-\s*\d+(?:[.,]\d+)?)?[-\s]*(?:s\b|sec|min|hour)", re.I)
# what the duration would be describing: a command a session could run
_COMMAND = re.compile(r"\bmake\s+[a-z][\w-]*|\bpytest\b")
_HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?\n(.*?)\n\s*\1\b", re.S)
# ONE LINE AT A TIME, deliberately: an earlier version allowed a quoted string to run across
# newlines, and a `printf '%s' "$INPUT" | ...` swallowed the twenty lines of COMMENT that followed it,
# so the check reported a comment as a message. A guard that fires on correct work is the failure this
# repository keeps paying for, and a check about guard messages may not commit it.
_SAID = re.compile(r"(?:^|[\s;(])(?:echo|printf|block)\s+([^\n]*)", re.M)


def emitted(text: str) -> list[str]:
    """Every chunk of a shell script that a session can actually read."""
    out = [body for _name, body in _HEREDOC.findall(text)]
    out += [m.group(1) for m in _SAID.finditer(text)]
    return out


def offenders(text: str) -> list[str]:
    """Emitted lines that state a duration for a runnable command."""
    bad = []
    for chunk in emitted(text):
        for line in chunk.splitlines():
            if _DURATION.search(line) and _COMMAND.search(line):
                bad.append(line.strip())
    return bad


def test_no_guard_message_states_a_duration() -> None:
    found = {path.name: bad for path in sorted(SCRIPTS.glob("*.sh")) if not path.name.startswith("test-") for bad in [offenders(path.read_text())] if bad}
    assert not found, "a guard message states how long a command takes; ask scripts/_gatecost.py or say nothing:\n" + "\n".join(f"  {name}: {lines}" for name, lines in found.items())


def test_the_check_would_catch_the_string_it_was_written_for() -> None:
    """Proof that it FIRES - the exact wording this feature removed from gate-hooks.sh."""
    was = 'echo "BLOCKED: `make quick` is a subset of `make done` (~70 s with scope locked)"'
    assert offenders(was), "the check no longer catches the message that motivated it"
