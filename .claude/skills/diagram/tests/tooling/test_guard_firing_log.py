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
    ("guard-file", _payload(_tool="Edit", file_path="/r/scripts/gate-hooks.sh", new_string="GUARD_EDIT_OK: why"), "escaped", "guard-edit-ok"),
]


@pytest.mark.parametrize(("guard", "payload", "event", "rule"), CASES, ids=[f"{c[0]}:{c[3]}" for c in CASES])
def test_a_guard_records_the_rule_that_fired(tmp_path, guard: str, payload: str, event: str, rule: str) -> None:
    subprocess.run(
        [str(SCRIPTS / f"{guard}-hooks.sh"), "pretool"],
        input=payload, capture_output=True, text=True, check=False,
        env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path), "GUARD_LOG_DIR": str(tmp_path / "log")},
    )
    entries = [json.loads(f.read_text()) for f in sorted((tmp_path / "log").glob("*.json"))]
    assert entries, f"{guard} recorded nothing for the {rule} case"
    assert any(e["event"] == event and e["rule"] == rule for e in entries), (
        f"{guard} recorded {[(e['event'], e['rule']) for e in entries]}, wanted ({event}, {rule})"
    )


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
            [str(SCRIPTS / "source-block-hooks.sh"), "pretool"], input=payload, capture_output=True,
            text=True, check=False, env={**env, "GUARD_LOG_DIR": str(tmp_path / log)},
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


def test_every_recording_guard_names_a_rule_rather_than_defaulting() -> None:
    """A `guard_log` call with no fourth argument records the EVENT as its rule, which is right for a
    single-branch guard and wrong for a multi-branch one. This catches a branch added later without
    its slug."""
    multi = {"no-poll", "make-only", "repo-safety", "clone-sync", "pair", "review-gate", "gate"}
    for guard in sorted(multi):
        text = (SCRIPTS / f"{guard}-hooks.sh").read_text() if guard != "review-gate" else (SCRIPTS / "review-gate.sh").read_text()
        calls = [ln for ln in text.splitlines() if "guard_log " in ln and not ln.strip().startswith("#")]
        assert calls, f"{guard} has no guard_log call at all"
        for call in calls:
            body = call.split("guard_log ", 1)[1]
            assert len(body.split('"')) > 2 or len(body.split()) >= 4, (
                f"{guard} logs without a rule slug, so its branches cannot be told apart: {call.strip()}"
            )
