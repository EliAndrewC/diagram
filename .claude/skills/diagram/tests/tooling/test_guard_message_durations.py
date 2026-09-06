"""No guard MESSAGE states how long a command takes (feature 162, GM 2026-08-30).

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

import ast
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


# ---------------------------------------------------------------------------------------------
# THE PYTHON HALF (feature 191). The make-only guard has TWO halves - `scripts/make-only-hooks.sh`
# and `l7r/diagram/_invocation.py` - and until now this file scanned only `scripts/`. That is why
# the shell ladder stayed clean while the Python one accumulated three stale facts: a retired
# target (`make reference`), two durations, and the vocabulary of the retired scope lock. The rule
# was censused over the surface where it was first written rather than over every place the
# mechanism lives, which is the same failure that produced the defect it was meant to catch.
ENGINE = REPO / ".claude/skills/diagram/l7r/diagram"

_OUTPUT_ATTRS = {"stdout", "stderr"}


def _is_output_call(node: ast.AST) -> bool:
    """`print(...)`, or `sys.stdout/sys.stderr.write(...)` - what a session actually reads."""
    if not isinstance(node, ast.Call):
        return False
    fn = node.func
    if isinstance(fn, ast.Name) and fn.id == "print":
        return True
    return (
        isinstance(fn, ast.Attribute)
        and fn.attr == "write"
        and isinstance(fn.value, ast.Attribute)
        and fn.value.attr in _OUTPUT_ATTRS
    )


def printed_text(source: str) -> list[str]:
    """Every string a session can READ from this module.

    Two kinds, and the second is the point of FR-006. A plain literal in an output call is a
    message. A DOCSTRING is a message only when its `__doc__` is itself handed to an output call -
    `print(_Ladder.__doc__)`. That distinction is load-bearing rather than fastidious: this very
    module's own docstring records the history *"the fast path already existed - `make reference`
    answers in ~60 s"*, which matches both patterns below. It is a RECORD, not a message, and a
    guard that cannot tell one from the other fires on protected history and gets switched off.
    """
    tree = ast.parse(source)
    docs = {
        node.name: ast.get_docstring(node) or ""
        for node in ast.walk(tree)
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }
    out: list[str] = []
    for call in (n for n in ast.walk(tree) if _is_output_call(n)):
        for arg in call.args:
            for part in ast.walk(arg):
                if isinstance(part, ast.Constant) and isinstance(part.value, str):
                    out.append(part.value)
                elif (
                    isinstance(part, ast.Attribute)
                    and part.attr == "__doc__"
                    and isinstance(part.value, ast.Name)
                    and part.value.id in docs
                ):
                    out.append(docs[part.value.id])
    return out


def py_offenders(source: str) -> list[str]:
    return [
        line.strip()
        for chunk in printed_text(source)
        for line in chunk.splitlines()
        if _DURATION.search(line) and _COMMAND.search(line)
    ]


def _python_guard_files() -> list[Path]:
    """DERIVED, never a roster (constitution X clause 14): every engine `.py` that can print.

    The search space is stated because getting it wrong is this project's recurring failure - an
    earlier draft of this requirement derived the set from `_invocation.OPERATIONS`, which is
    hand-enumerated by its own docstring and does not contain `_invocation` itself, so it would
    have missed the one file the rule exists for.
    """
    return [p for p in sorted(ENGINE.rglob("*.py")) if printed_text(p.read_text(encoding="utf-8"))]


def test_no_python_guard_message_states_a_duration() -> None:
    found = {p.name: bad for p in _python_guard_files() for bad in [py_offenders(p.read_text(encoding="utf-8"))] if bad}
    assert not found, "a printed message states how long a command takes; ask scripts/_gatecost.py or say nothing:\n" + "\n".join(f"  {name}: {lines}" for name, lines in found.items())


def test_the_python_check_fires_on_a_planted_duration_in_a_PRINTED_docstring() -> None:
    """SC-003, first half - proven by planting, per the add-a-guard rule."""
    planted = 'class _L:\n    """\n    make quick   ~33 s   lint and types\n"""\n\n\nimport sys\nsys.stderr.write(_L.__doc__)\n'
    assert py_offenders(planted), "a duration in a PRINTED docstring must be caught - that is where feature 191 put the text"


def test_the_python_check_does_NOT_fire_on_a_docstring_that_is_only_a_RECORD() -> None:
    """SC-003, second half. `_invocation.py`'s MODULE docstring contains both a duration and a
    command (`make reference` answers in ~60 s) and is protected history. A file-granular rule
    would turn the gate red on it and the tempting fix would be to edit the record."""
    record = '"""WHY THIS EXISTS. The fast path already existed - `make reference` answers in ~60 s."""\nprint("nothing to see")\n'
    assert not py_offenders(record), "a docstring nothing prints is a RECORD, not a message, and must not fire"
    live = (ENGINE / "_invocation.py").read_text(encoding="utf-8")
    assert "answers in ~60 s" in live, "the historical note this test guards has moved - update the test, do not edit the record"
    assert not py_offenders(live), "the module docstring is a record and must not be judged as a message"


def test_every_target_named_in_the_refusal_ladder_resolves() -> None:
    """FR-008. A refusal that names a command which does not exist is the defect this feature fixes;
    `make reference` sat in this ladder for hours after that rung was retired. Only the STATIC
    ladder is checked - `assert_via_make`'s interpolated `{target}` is passed a free-form ROUTE by
    `ci/__main__.py` ("ci-status (free) | make ci-check | ..."), which is prose, not one target."""
    makefile = (REPO / ".claude/skills/diagram/Makefile").read_text(encoding="utf-8")
    rules = set(re.findall(r"^([a-z][\w-]*):(?!=)", makefile, re.M))
    ladder = "\n".join(printed_text((ENGINE / "_invocation.py").read_text(encoding="utf-8")))
    # A LADDER ROW, not any mention of the word "make". The first cut used `\bmake\s+(\w+)` and
    # fired on this very message's own prose - "goes through a make target, so the expensive ones
    # can ask" - reporting `target` as a missing make target. A guard that fires on correct work is
    # the failure this repository keeps paying for; a row is indented and followed by its gloss.
    named = {m.group(1) for m in re.finditer(r"^\s+make\s+([a-z][\w-]*)\s", ladder, re.M)}
    assert named, "the ladder names no targets at all - the extractor is not seeing it"
    assert named <= rules, f"the refusal ladder names targets that do not exist: {sorted(named - rules)}"
