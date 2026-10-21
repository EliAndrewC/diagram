"""`scripts/record/found.py` (feature 405 T29): a found.jsonl row is closed as FILED (a task id) or SETTLED (a reason)."""

from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

from tests._scripts import script

_s = importlib.util.spec_from_file_location("found", script("found.py"))
assert _s and _s.loader
found = importlib.util.module_from_spec(_s)
_s.loader.exec_module(found)


def _rows(d: pathlib.Path, n: int) -> pathlib.Path:
    (d / "found.jsonl").write_text("".join(json.dumps({"check": "impl-drift", "file": f"f{i}.py", "finding": f"x{i}", "status": "open"}) + "\n" for i in range(n)))
    return d / "found.jsonl"


def test_a_row_is_filed_or_settled_and_the_rest_stay_open(tmp_path: pathlib.Path, capsys) -> None:  # noqa: ANN001
    """385's 63 rows all read open, filed or not (405 T28): a closed row says how."""
    path = _rows(tmp_path, 4)
    assert found.main(["close", "--feature", str(tmp_path), "--rows", "1,3", "--task", "T61"]) == 0
    assert found.main(["close", "--feature", str(tmp_path), "--rows", "2", "--task", "385 T12"]) == 0, "another feature's task"
    assert found.main(["close", "--feature", str(tmp_path), "--rows", "1", "--why", "no longer holds: the cited text is gone"]) == 2, "closed once"
    assert found.main(["close", "--feature", str(tmp_path), "--rows", "4", "--why", "decided not to file this one"]) == 2, "settled only where it no longer holds"
    assert found.main(["close", "--feature", str(tmp_path), "--rows", "4", "--task", "x"]) == 2
    assert found.main(["close", "--feature", str(tmp_path), "--rows", "4", "--task", "374 T5"]) == 2, "385 and 405 only"
    rows = [json.loads(x) for x in path.read_text().splitlines()]
    assert [r["status"] for r in rows] == ["filed", "filed", "filed", "open"] and rows[1]["task"] == "385 T12"
    capsys.readouterr()
    assert found.main(["list", "--feature", str(tmp_path)]) == 0 and "1 open of 4" in capsys.readouterr().out
    assert found.main(["close", "--feature", str(tmp_path), "--rows", "4", "--why", "no longer holds: the cited text is gone"]) == 0
    assert json.loads(path.read_text().splitlines()[3])["why"] == "no longer holds: the cited text is gone"
    with pytest.raises(ValueError, match="no row 9"):
        found.close(rows, [9], task="T1")


def test_a_close_naming_no_rows_is_refused_with_the_rows_argument() -> None:
    with pytest.raises(ValueError, match=r"ROWS=3,7"):
        found.close([{"status": "open"}], [], task="T61")
