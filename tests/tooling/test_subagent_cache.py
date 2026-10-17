"""`scripts/measure/subagent_cache.py` - what subagents write to the prompt cache fresh (feature 383 amendment 6, FR-036)."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("subagent_cache", REPO / "scripts/measure/subagent_cache.py")
assert spec and spec.loader
ca = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ca
spec.loader.exec_module(ca)

GUIDE = "\n".join(f"Rule {i}: a modal says what the map draws and why, in the voice its reader expects." for i in range(30))


def _run(root: pathlib.Path, session: str, agent: str, kind: str, start: str, calls: list[tuple[int, int, int]], manifest: str = "") -> None:
    d = root / session / "subagents"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"agent-{agent}.meta.json").write_text(json.dumps({"agentType": kind}), encoding="utf-8")
    lines = [{"type": "user", "timestamp": start, "message": {"role": "user", "content": "go"}}]
    for i, (read, write, out) in enumerate(calls):
        content = [{"type": "tool_use", "id": f"r{i}", "name": "Read", "input": {"file_path": "/tmp/b/MANIFEST.md"}}] if i == 0 and manifest else []
        usage = {"input_tokens": 2, "cache_read_input_tokens": read, "cache_creation_input_tokens": write, "output_tokens": out}
        lines.append({"type": "assistant", "requestId": f"q{i}", "timestamp": start, "message": {"id": f"m{i}", "usage": usage, "content": content}})
        lines.append({"type": "assistant", "requestId": f"q{i}", "timestamp": start, "message": {"id": f"m{i}", "usage": usage, "content": []}})  # a streamed repeat
        if i == 0 and manifest:
            lines.append({"type": "user", "timestamp": start, "message": {"content": [{"type": "tool_result", "tool_use_id": "r0", "content": manifest}]}})
    (d / f"agent-{agent}.jsonl").write_text("\n".join(json.dumps(x) for x in lines) + "\nnot json\n", encoding="utf-8")


@pytest.fixture
def root(tmp_path: pathlib.Path) -> pathlib.Path:
    _run(tmp_path, "s1", "a", "modal-form", "2026-10-17T10:00:00Z", [(0, 9000, 100), (9000, 4000, 200)], GUIDE + "\nunit one, its own text that no other bundle carries at all")
    _run(tmp_path, "s1", "b", "modal-form", "2026-10-17T10:02:00Z", [(6000, 2500, 100)], GUIDE + "\nunit two, its own text that no other bundle carries at all")
    _run(tmp_path, "s1", "c", "modal-form", "2026-10-17T11:00:00Z", [(0, 9000, 100)])  # an hour later: not back to back
    _run(tmp_path, "s2", "d", "general-purpose", "2026-10-17T10:01:00Z", [(4000, 29000, 50)])
    _run(tmp_path, "s2", "e", "general-purpose", "2026-10-09T10:01:00Z", [(4000, 29000, 50)])  # before --since
    (tmp_path / "s3" / "subagents").mkdir(parents=True)
    (tmp_path / "s3" / "subagents" / "agent-x.jsonl").write_text("{}\n", encoding="utf-8")  # no meta: not a run
    return tmp_path


def test_a_run_counts_each_request_once_and_keeps_its_first_manifest(root: pathlib.Path) -> None:
    rs = ca.runs(root, "2026-10-10")
    assert [r["kind"] for r in rs] == ["modal-form", "general-purpose", "modal-form", "modal-form"]
    first = rs[0]
    assert len(first["calls"]) == 2, "a streamed repeat of one request is one call"
    assert first["manifest"].startswith("Rule 0")


def test_back_to_back_is_the_same_type_and_session_inside_the_cache_window(root: pathlib.Path) -> None:
    pairs = ca.back_to_back(ca.runs(root, "2026-10-10"))
    assert [r["start"] for r in pairs["modal-form"]] == ["2026-10-17T10:02:00Z"] and "general-purpose" not in pairs


def test_shared_text_counts_long_lines_both_hold_and_drops_the_read_tools_line_numbers() -> None:
    a = "     1\t" + "x" * 50 + "\n     2\tshort\n" + "y" * 45
    b = "x" * 50 + "\nshort\n" + "z" * 45
    assert ca.shared_text(a, b) == 50
    assert ca.repeated([a]) == 0 and ca.repeated([a, b, a]) == 50, "a line in fewer than 80% of them is not repeated"


def test_the_report_names_each_types_fresh_write_its_repetition_and_the_spend(root: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert ca.main(["--since", "2026-10-10", "--root", str(root)]) == 0
    out = capsys.readouterr().out
    row = next(line for line in out.splitlines() if line.startswith("modal-form"))
    assert row.split()[1:5] == ["3", "1", "6000", "2500"], row
    assert int(row.split()[5]) >= len(GUIDE) - 200, "the guidelines every bundle carries are reported as repeated"
    assert "base-input units" in out and "a write 1.25x" in out
    assert ca.main(["--since", "2027-01-01", "--root", str(root)]) == 0 and "no subagent runs" in capsys.readouterr().out


def test_spend_weighs_writes_reads_and_output_at_the_five_minute_tier() -> None:
    s = ca.spend([{"calls": [{"cache_creation_input_tokens": 100, "cache_read_input_tokens": 1000, "input_tokens": 10, "output_tokens": 20}]}])
    assert s["units"] == 100 * 1.25 + 1000 * 0.1 + 10 + 20 * 5


def test_the_contract_part_drops_the_sections_built_from_the_units_own_inputs() -> None:
    page = "## `entry/0038-x.html` - origin `research/questions/0038-x.html`\n" + "a page both units cite, line by line, long enough\n"
    rules = "## `guidelines.txt` - origin `dev/modals.md`\n" + "a rule every bundle of this check carries, long enough\n"
    claims = "## `claims.md` - origin `dev/claims-index.json`\n" + "a claim both units' pages carry, long enough to count\n"
    a, b = "# head\n" + page + rules + claims, "# head\n" + page + rules + claims
    assert ca.contract_shared(a, b) == len("a rule every bundle of this check carries, long enough")
    assert "a page both units cite" not in ca.contract_part(a) and "## `guidelines.txt`" in ca.contract_part(a)
