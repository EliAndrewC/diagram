"""FR-029: `perf-gate` pairs bookends only within one machine class - FIRES on laptop-vs-build,
STAYS QUIET on two build snapshots from the same image (T064, T065)."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest

from l7r.diagram.tools import perf_snapshot as ps


def _snap(tmp: Any, label: str, seconds: dict[int, float], utc: str, **ident: str) -> None:
    rows = [{"seed": s, "seconds": v} for s, v in seconds.items()]
    body = {"utc": utc, "label": label, "commit": "abc1234", "rows": rows, "total_seconds": sum(seconds.values()), "median_seconds": 1.0, "worst_seconds": max(seconds.values()), **ident}
    (tmp / f"{utc}-{label}.json").write_text(json.dumps(body), encoding="utf-8")


@pytest.fixture
def logdir(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Any:
    monkeypatch.setattr(ps, "LOG_DIR", str(tmp_path))
    os.makedirs(tmp_path, exist_ok=True)
    return tmp_path


def test_a_laptop_start_and_a_build_end_REFUSE_to_pair(logdir: Any, capsys: pytest.CaptureFixture[str]) -> None:
    _snap(logdir, "130-start", {1: 100.0}, "20260825T000000Z")  # pre-130 shape: no identity = laptop
    _snap(logdir, "130-end", {1: 50.0}, "20260825T010000Z", host="codebuild:BUILD_GENERAL1_XLARGE", image="ecr/x:latest")
    assert ps.report("130-start") == 1
    out = capsys.readouterr().out
    assert "REFUSED" in out and "is a local snapshot" in out and "codebuild:BUILD_GENERAL1_XLARGE" in out


def test_two_build_snapshots_on_one_image_pair(logdir: Any, capsys: pytest.CaptureFixture[str]) -> None:
    _snap(logdir, "131-start", {1: 100.0}, "20260825T000000Z", host="codebuild:BUILD_GENERAL1_XLARGE", image="ecr/x:latest")
    _snap(logdir, "131-end", {1: 102.0}, "20260825T010000Z", host="codebuild:BUILD_GENERAL1_XLARGE", image="ecr/x:latest")
    assert ps.report("131-start") == 0
    out = capsys.readouterr().out
    assert "REFUSED" not in out and "codebuild:BUILD_GENERAL1_XLARGE" in out, "the machine is named on every row"


def test_identity_is_a_class_not_a_hostname(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CODEBUILD_BUILD_ID", raising=False)
    lap = ps.machine_identity()
    assert (lap["host"], lap["image"]) == ("laptop", "laptop") and lap["hostname"]
    monkeypatch.setenv("CODEBUILD_BUILD_ID", "gm-assistant-check:1")
    monkeypatch.setenv("COMPUTE_TYPE", "BUILD_GENERAL1_XLARGE")
    monkeypatch.setenv("CODEBUILD_BUILD_IMAGE", "ecr/x:latest")
    build = ps.machine_identity()
    assert build["host"] == "codebuild:BUILD_GENERAL1_XLARGE" and build["image"] == "ecr/x:latest"
    assert ps.identity_of({}) == ("local", "laptop", "laptop")
    assert build["environment"] == "codebuild" and lap["environment"] == "local", "the environment is recorded, never inferred (FR-013)"
