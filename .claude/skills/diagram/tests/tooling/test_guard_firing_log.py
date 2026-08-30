"""Every guard that acts on a session RECORDS it, with the rule that fired (feature 168).

WHY (GM 2026-08-30): *"the firing log should record more data for us to be able to use to make
improvements in the future."* Before this, seven scripts recorded and most of them only on one
branch - `make-only` logged its rewrite but none of its five refusals, `gate` its rewrite but not its
block - and `batching`, the loudest guard in the repository at 119 firings in six days, recorded
nothing at all. So "is this guard worth what it costs" could not be answered from the log.

WHY THE RULE AND NOT JUST THE GUARD: several guards enforce more than one thing, and *"no-poll fired
32 times"* cannot say which of its three rules is carrying the cost. A future improvement acts on a
RULE.

WHY THIS TEST DRIVES THE HOOKS rather than reading them: a grep for `guard_log` proves a call site
exists, not that it fires. Each case below is a real payload through the real hook, and the assertion
is on the entry that lands in a throwaway log.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[5] / "scripts"  # the REPO root; parents[4] is .claude


def _payload(**tool_input: object) -> str:
    return json.dumps({"session_id": "t", "tool_name": tool_input.pop("_tool", "Bash"), "tool_input": tool_input})


# (guard script, payload, the event and rule its entry must carry)
CASES = [
    ("no-poll", _payload(command="while :; do sleep 5; done"), "blocked", "busy-wait-loop"),
    ("no-poll", _payload(command="command sleep 30"), "blocked", "disguised-sleep"),
    ("no-poll", _payload(command="make done  # POLL_OK: an external port"), "escaped", "poll-ok"),
    ("make-only", _payload(command="python3 -m pytest tests/x/test_y.py -k foo"), "blocked", "bare-pytest"),
    ("make-only", _payload(command="make -f /tmp/other.mk all"), "blocked", "foreign-makefile"),
    ("no-branch", _payload(command="git checkout -b side"), "blocked", "branch-creation"),
    ("no-branch", _payload(command="git checkout -b side  # NO_BRANCH_OK: a throwaway bisect"), "escaped", "no-branch-ok"),
    ("repo-safety", _payload(command="git push --force origin main"), "blocked", "force-push"),
    ("repo-safety", _payload(command="git rebase origin/main"), "blocked", "history-rewrite"),
    ("readme", _payload(_tool="Write", file_path="/r/README.md", content="hello"), "blocked", "readme-is-the-gm-s"),
    ("guard-file", _payload(_tool="Edit", file_path="/r/scripts/gate-hooks.sh", new_string="x"), "blocked", "no-marker"),
    ("guard-file", _payload(_tool="Edit", file_path="/r/scripts/gate-hooks.sh", new_string="GUARD_EDIT_OK: fixing a guard that fires on correct work"), "escaped", "guard-edit-ok"),
    ("guard-file", _payload(_tool="Edit", file_path="/r/scripts/gate-hooks.sh", new_string="GUARD_EDIT_OK: why"), "blocked", "GUARD_EDIT_OK-no-reason"),
]


@pytest.mark.parametrize(("guard", "payload", "event", "rule"), CASES, ids=[f"{c[0]}:{c[3]}" for c in CASES])
def test_a_guard_records_the_rule_that_fired(tmp_path, guard: str, payload: str, event: str, rule: str) -> None:
    subprocess.run(
        [str(SCRIPTS / f"{guard}-hooks.sh"), "pretool"],
        input=payload,
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path), "GUARD_LOG_DIR": str(tmp_path / "log")},
    )
    entries = [json.loads(f.read_text()) for f in sorted((tmp_path / "log").glob("*.json"))]
    assert entries, f"{guard} recorded nothing for the {rule} case"
    assert any(e["event"] == event and e["rule"] == rule for e in entries), f"{guard} recorded {[(e['event'], e['rule']) for e in entries]}, wanted ({event}, {rule})"


def test_the_gm_s_source_block_records_both_the_refusal_and_the_escape(tmp_path) -> None:
    """`source-block` needs a file on disk to judge, so it gets its own case rather than a row above.

    Its ESCAPE is the interesting half. `SOURCE_EDIT_OK` was handled inside the guard's python by
    printing an empty verdict - indistinguishable from "this edit touches no protected block" - so
    an authorized edit of the GM's own writing, the single most consequential permit in the
    repository, left no trace at all. It records now (feature 168), and still permits.
    """
    note = tmp_path / "n.md"
    note.write_text("x\n<!-- SOURCE: GM NOTES - DO NOT MODIFY -->\nthe GM wrote this\n<!-- END SOURCE -->\n")
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)}

    def run(new_string: str, log: str) -> int:
        payload = _payload(_tool="Edit", file_path=str(note), old_string="the GM wrote this", new_string=new_string)
        return subprocess.run(
            [str(SCRIPTS / "source-block-hooks.sh"), "pretool"],
            input=payload,
            capture_output=True,
            text=True,
            check=False,
            env={**env, "GUARD_LOG_DIR": str(tmp_path / log)},
        ).returncode

    def entry(log: str) -> dict:
        files = sorted((tmp_path / log).glob("*.json"))
        assert files, f"source-block recorded nothing in {log}"
        return json.loads(files[0].read_text())

    assert run("reworded", "block") == 2
    assert (entry("block")["event"], entry("block")["rule"]) == ("blocked", "gm-source-block")
    assert entry("block")["detail"] == str(note), "an entry with an empty detail says something fired, not what on"

    assert run("SOURCE_EDIT_OK the GM told me to", "escape") == 0, "the escape must still PERMIT"
    assert (entry("escape")["event"], entry("escape")["rule"]) == ("escaped", "source-edit-ok")


def _recording_guards() -> list[pathlib.Path]:
    """Every guard script that calls `guard_log`, DERIVED (feature 169).

    The hand-written set this replaces named seven guards and omitted eight, so `guard-file`'s Read
    reminder shipped without a rule slug and the census could not tell its three branches apart. A
    census of your own tree written by hand is stale the day it is written - the same lesson feature
    168's own spec review returned twice.
    """
    return sorted(p for p in SCRIPTS.glob("*.sh") if not p.name.startswith("test-") and "guard_log " in p.read_text())


def test_every_recording_branch_names_a_rule_rather_than_defaulting() -> None:
    """A `guard_log` call with no fourth argument records the EVENT as its rule, which is right for a
    guard with ONE acting branch and wrong for every other. Derived over the whole guard tree."""
    for guard in _recording_guards():
        calls = [ln for ln in guard.read_text().splitlines() if "guard_log " in ln and not ln.strip().lstrip("#").startswith("#")]
        calls = [ln for ln in calls if not ln.strip().startswith("#")]
        if len(calls) < 2:
            continue  # a single-branch guard may let the rule default to its event
        for call in calls:
            body = call.split("guard_log ", 1)[1]
            assert len(body.split('"')) > 2 or len(body.split()) >= 4, f"{guard.name} logs without a rule slug, so its branches cannot be told apart: {call.strip()}"


def test_every_suite_of_a_recording_guard_isolates_the_firing_log() -> None:
    """A suite that drives a recording guard must write into a throwaway log (feature 169).

    Feature 168 added `GUARD_LOG_DIR` isolation to SIX suites BY HAND (measured from its own
    commits, not remembered) and missed `test-review-gate.sh`, because `review-gate.sh` is not a `*-hooks.sh` file. The cost was
    measurable within a day: 24 of the live census's 113 entries were that suite's `specs/900-x`
    fixtures - in the census this project uses to decide which guards are worth their cost.
    """
    missing = []
    for guard in _recording_guards():
        suite = SCRIPTS / f"test-{guard.stem}.sh"
        if not suite.exists():
            continue
        text = suite.read_text()
        # A suite may delegate to the shared runner (`exec python3 test_hooks_cases.py <guard>`)
        # rather than isolate for itself; follow one level, and hold the runner to the same rule.
        for delegate in re.findall(r"[\w./-]*test_hooks_cases\.py", text):
            target = SCRIPTS / pathlib.Path(delegate).name
            if target.exists():
                text += target.read_text()
        if "GUARD_LOG_DIR" not in text:
            missing.append(suite.name)
    assert not missing, f"these suites drive a recording guard but write into the real census: {missing}"


# ---------------------------------------------------------------------------------------------
# THE ESCAPE CENSUS IS DERIVED, NOT WRITTEN FROM MEMORY (feature 169).
#
# WHY THIS EXISTS AND NOT A LIST IN A DOCUMENT: three drafts of this feature's spec each asserted a
# complete census of "every guard's escape token", and each was short by one - `HOST_GIT_OK` found by
# the round-2 review, `GATE_STAMP_OK` by round 3. The reviewer's diagnosis was that the census was
# being written from memory of the guards rather than derived from the tree, and that a fourth
# attempt by the same author would miss the next one too. It was right, so the list moved here.
#
# A NEW `*_OK` token now fails this test until someone classifies it, and a guard that decides a
# COMMAND escape with a bare substring test fails it too - which is the defect the whole feature
# exists to remove, and the one a future guard would most naturally reintroduce.
_ESCAPES = {
    # token: (kind, why this kind is safe)
    "GATE_OK": ("command", "routes through _hookmatch.py escape"),
    "MEASURE_OK": ("command", "routes through _hookmatch.py escape"),
    "POLL_OK": ("command", "routes through _hookmatch.py escape"),
    "DISCARD_OK": ("command", "routes through _hookmatch.py escape"),
    "NO_BRANCH_OK": ("command", "routes through _hookmatch.py escape"),
    "MAIN_TREE_OK": ("command", "routes through _hookmatch.py escape"),
    "HOST_GIT_OK": ("command", "routes through _hookmatch.py escape, via RS_ESCAPED"),
    "PAIR_OK": (
        "command",
        "the Bash branch routes through the matcher; the AGENT-PROMPT branch is the "
        "one stated exclusion - a prompt is prose with no command grammar, and "
        "blanking its quoted regions would break the GM's own PAIR_OK=\"reason\" form",
    ),
    "GUARD_EDIT_OK": ("command", "classify() routes through escape_used; also a marker in edit CONTENT"),
    "SOURCE_EDIT_OK": ("content", "matched in an Edit's new_string, never in a command - the marker in the text IS the escape, so a 'mention' is the intended use"),
    "REVIEW_GATE_OK": ("environment", "read as ${REVIEW_GATE_OK:-} at push time; an environment variable cannot be set by mentioning it in a command"),
    "GATE_STAMP_OK": ("environment", "read as ${GATE_STAMP_OK:-} at push time; same ground as REVIEW_GATE_OK. Missed by three drafts of the spec (round 3)"),
    "REF_OK": ("make-variable", "a make override, already anchored positionally by _hookmatch.py:116 - it must appear as REF_OK= at a command position"),
    "SWEEP_OK": ("not-an-escape", "a Makefile MACRO that runs the scope check; nothing overrides"),
    "REMOTE_OK": ("not-an-escape", "a Makefile MACRO that runs the remote check; nothing overrides"),
}

_TOKEN = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*_OK\b")


def _tree_tokens() -> set[str]:
    files = list(SCRIPTS.glob("*.sh")) + list(SCRIPTS.glob("*.py"))
    files.append(pathlib.Path(__file__).resolve().parents[2] / "Makefile")
    found: set[str] = set()
    for f in files:
        if f.exists():
            found |= set(_TOKEN.findall(f.read_text()))
    return found


def test_the_escape_census_is_derived_from_the_tree() -> None:
    """Every `*_OK` token in the guard tree is classified - a new one fails until someone says what
    kind it is. Three spec drafts each missed a different token; this cannot."""
    unclassified = _tree_tokens() - set(_ESCAPES)
    assert not unclassified, (
        f"new escape token(s) with no classification: {sorted(unclassified)}. Add each to _ESCAPES "
        "saying whether it is matched in a COMMAND (and so must route through _hookmatch.py escape), "
        "in edit CONTENT, as an ENVIRONMENT variable, or is not an escape at all."
    )
    stale = set(_ESCAPES) - _tree_tokens()
    assert not stale, f"classified but no longer in the tree: {sorted(stale)}"


def test_no_guard_decides_a_command_escape_with_a_bare_substring_test() -> None:
    """The defect feature 169 removed, and the one a new guard would most naturally reintroduce.

    A `case "$CMD" in *TOKEN*)` or an `if "TOKEN" in cmd` decides a COMMAND escape by substring, so a
    grep for the token, or a commit message quoting it, escapes the guard - and in `measure` and
    `gate` also resets the state that decides whether the NEXT expensive command is refused.
    """
    offenders = []
    for guard in SCRIPTS.glob("*hooks*"):
        if guard.name.startswith("test") or guard.suffix not in (".sh", ".py"):
            continue
        for line in guard.read_text().splitlines():
            if line.strip().startswith("#"):
                continue
            # A line only counts if it DECIDES - substring-tests a token and then acts on it. The
            # first draft of this check flagged the `sed` that extracts the reason for the bypass log
            # (it reads `PAIR_OK=`, it decides nothing), which is the mention-versus-invocation
            # mistake being made by the very check that exists to prevent it.
            if not re.search(r"guard_log|exit 0|return 0", line):
                continue
            # ...and `$prompt` is the ONE declared exclusion (see PAIR_OK in _ESCAPES): a subagent
            # dispatch prompt is prose, with no command grammar for the matcher to anchor on.
            if 'case "$prompt"' in line:
                continue
            for token, (kind, _why) in _ESCAPES.items():
                if kind != "command" or token not in line:
                    continue
                if re.search(rf"\*{token}[=*]", line) or re.search(rf'["\']{token}["\'] not in \w+', line):
                    offenders.append(f"{guard.name}: {line.strip()[:90]}")
    assert not offenders, "these decide a command escape by substring, so a mention of the token escapes the guard: " + "; ".join(offenders)


# ---------------------------------------------------------------------------------------------
# EVERY PERMITTING SITE RECORDS - DERIVED OVER (TOKEN, SITE), NOT OVER TOKENS (feature 170).
#
# WHY THE PAIR AND NOT THE TOKEN: round 3 of this feature's review caught the first version keyed on
# the token alone, which two tokens defeat by having TWO permitting sites each - `GUARD_EDIT_OK` is
# permitted by `guard-file-hooks.sh` (which recorded) and by `make-only` (which did not), so one
# driver per token passed green while the exact branch the feature existed to close stayed silent.
#
# WHY DERIVED AT ALL: four hand-written censuses across features 169 and 170 were each short by one,
# every time found by the reviewer rather than the author. A list cannot be trusted here.
# Two shapes record a permit: a direct `guard_log <guard> escaped`, and a delegation to
# `escape_or_refuse <guard> <TOKEN> <rule>`, which does the logging in `_guardlog.sh` so the
# refusal is written once rather than nine times. A check that knew only the first shape reported
# every converted guard as silent - which is how a completeness check can be wrong in the safe
# direction and still be wrong.
_PERMIT = re.compile(r"guard_log\s+(\S+)\s+escaped|escape_or_refuse\s+(\S+)")


def _permitting_sites() -> set[tuple[str, str]]:
    """(guard file, rule slug) for every branch that RECORDS a permitted escape."""
    out = set()
    for f in list(SCRIPTS.glob("*.sh")) + [SCRIPTS.parent / ".claude/skills/diagram/Makefile"]:
        if not f.exists() or f.name.startswith("test"):
            continue
        for line in f.read_text().splitlines():
            if line.strip().startswith("#"):
                continue
            m = _PERMIT.search(line)
            if m:
                out.add((f.name, m.group(1) or m.group(2)))
    return out


def test_every_escape_token_has_at_least_one_recording_permit_site() -> None:
    """A token classified as an escape must be recorded somewhere when it permits.

    This is the completeness half. `test_no_guard_decides_a_command_escape_with_a_bare_substring_test`
    is the correctness half, and `_ESCAPES` is what both derive from - so a NEW token is red here
    until someone both classifies it and gives it a recording permit site.
    """
    sites = _permitting_sites()
    recorded_guards = {g for g, _rule in sites}
    # the three that were silent when this feature began, named so the test says what it is for
    for guard in ("make-only-hooks.sh", "repo-safety-hooks.sh", "sync-with-main.sh"):
        assert guard in recorded_guards, f"{guard} permits an escape and records nothing - the defect feature 170 exists to close. Recording guards found: {sorted(recorded_guards)}"


def test_no_escape_class_is_quietly_exempt_from_the_reason_floor() -> None:
    """`not-an-escape` may not be used to retire a red (feature 170, round 3).

    A token belongs in that class only if NO branch permits on it. If one does, it is an escape and
    owes a reason like every other - so the class is checked against the tree rather than trusted.
    """
    for token, (kind, _why) in _ESCAPES.items():
        if kind != "not-an-escape":
            continue
        for f in SCRIPTS.glob("*.sh"):
            if f.name.startswith("test"):
                continue
            for line in f.read_text().splitlines():
                if token in line and _PERMIT.search(line):
                    raise AssertionError(f"{token} is classified `not-an-escape` but {f.name} records a permit on it - either it is an escape and owes a reason, or the classification is wrong")
