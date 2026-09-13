"""`scripts/_hookbench.py`, proven to fire (feature 239 B: FR-004 to FR-007).

The bench replays real commands through a guard's DECISION in process, and diffs verdicts against a
ref. Each case below is a rule a later session could break without noticing: the codepoint prefilter,
the refusal of an unimportable guard, the four-way classification, the diff in both directions.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[5]
_spec = importlib.util.spec_from_file_location("_hookbench", REPO / "scripts" / "_hookbench.py")
assert _spec and _spec.loader
bench = importlib.util.module_from_spec(_spec)
# the British forms are SPLIT so the house-style hook cannot correct these cases as they are written -
# it did, the first time, and three of them then tested the American spelling they were meant to avoid
BRIT_CENTER, BRIT_COLOR = "cent" + "re", "col" + "our"
sys.modules["_hookbench"] = bench
_spec.loader.exec_module(bench)


def test_a_verdict_is_classified_four_ways() -> None:
    assert bench.classify("") == "silent"
    assert bench.classify('{"hookSpecificOutput": {"updatedInput": {"command": "x"}}}') == "corrected"
    assert bench.classify('{"hookSpecificOutput": {"additionalContext": "told"}}') == "reported"
    assert bench.classify(f"{BRIT_COLOR} | {BRIT_CENTER}") == "blocked"
    assert bench.classify("", blocked=True) == "blocked"


def test_a_guard_with_no_importable_decision_is_refused_by_name() -> None:
    """FR-007: never a silent fallback to spawning, which would hide the cost the bench exists to remove."""
    with pytest.raises(SystemExit) as caught:
        bench.decision("no-poll")
    assert "no importable decision" in str(caught.value) and "FR-001" in str(caught.value)


def test_the_house_style_decision_is_called_in_process() -> None:
    """FR-005: the decision answers without a process per command - and answers correctly."""
    got = bench.verdicts_in_process(
        "house-style",
        [
            f"echo 'the {BRIT_CENTER} of it' >> docs/a.md",  # prose the command writes: corrected
            f"sed -i 's/{BRIT_CENTER}/center/g' docs/a.md",  # the fix shape: reported, left as typed
            f"grep -n {BRIT_CENTER} docs/a.md",  # a search: silent
        ],
    )
    assert got == ["corrected", "reported", "silent"], got


def test_the_prefilter_matches_a_real_dash_and_not_a_spaced_hyphen() -> None:
    """FR-004: written literally, the dashes were corrected to hyphens by the hook as the file was saved."""
    pattern = bench.word_pattern()
    assert pattern.search("a " + chr(0x2014) + " b") and pattern.search(f"the {BRIT_CENTER}")
    assert not pattern.search("a - b")


def test_the_window_is_frozen_from_transcripts(tmp_path: pathlib.Path) -> None:
    """FR-004: every unique Bash command carrying a word or a dash, deduplicated, dated in its name."""
    proj = tmp_path / "projects" / "-x"
    proj.mkdir(parents=True)

    def use(c: str) -> str:
        return json.dumps({"message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": c}}]}})

    (proj / "s.jsonl").write_text("\n".join([use(f"echo the {BRIT_CENTER}"), use(f"echo the {BRIT_CENTER}"), use("ls -la"), use("echo a " + chr(0x2013) + " b")]) + "\n")
    out = bench.refresh(14, out_dir=tmp_path, projects=tmp_path / "projects")
    got = json.loads(out.read_text())
    assert out.name.startswith("command-window-") and got["commands"] == [f"echo the {BRIT_CENTER}", "echo a " + chr(0x2013) + " b"]


def test_the_diff_reports_both_directions() -> None:
    """FR-006: a verdict that moved either way is named - the exemption's drafts moved them both ways."""
    changed = bench.diff(["a", "b", "c"], ["silent", "corrected", "silent"], ["corrected", "silent", "silent"])
    assert changed == [("silent", "corrected", "a"), ("corrected", "silent", "b")]
