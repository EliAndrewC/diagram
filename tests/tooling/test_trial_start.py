"""`scripts/trial-start.py` - `make trial` (feature 438): the trial brief written from its template into a claimed directory."""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

from tests._scripts import script

_spec = importlib.util.spec_from_file_location("trial_start", script("trial-start.py"))
assert _spec and _spec.loader
ts = importlib.util.module_from_spec(_spec)
sys.modules["trial_start"] = ts
_spec.loader.exec_module(ts)


def test_the_brief_is_the_template_with_its_date_and_number_and_a_request_stub(tmp_path: pathlib.Path) -> None:
    d = tmp_path / "specs" / "439-fewer-seats"
    d.mkdir(parents=True)
    ts.brief(d, "2026-10-27")
    spec = (d / "spec.md").read_text(encoding="utf-8")
    assert "**Form**: trial" in spec and "**Created**: 2026-10-27" in spec and "make feature-report F=439" in spec
    for section in ("## The question", "## The measurement", "## The rule", "## The evidence", "## The time", "## Review history"):
        assert section in spec
    assert "[DATE]" not in spec and "[N]" not in spec
    assert "Feature 439" in (d / "request.md").read_text(encoding="utf-8")
    (d / "request.md").write_text("kept", encoding="utf-8")
    ts.brief(d, "2026-10-28")
    assert (d / "request.md").read_text(encoding="utf-8") == "kept", "a request already written is not overwritten"


def test_main_claims_then_writes_and_refuses_without_a_slug(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    assert ts.main([]) == 2
    (tmp_path / "specs" / "439-x").mkdir(parents=True)
    monkeypatch.setattr(ts, "ROOT", tmp_path)
    monkeypatch.setattr(ts.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout="439-x\n", stderr="export SPECIFY_FEATURE=439-x\n"))
    assert ts.main(["x"]) == 0 and (tmp_path / "specs" / "439-x" / "spec.md").is_file()
    monkeypatch.setattr(ts.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 3, stdout="", stderr="REFUSED"))
    assert ts.main(["y"]) == 3


def test_the_gms_words_ride_on_the_approval_line_and_the_verdict_names_its_branch(tmp_path: pathlib.Path) -> None:
    """Feature 440 T02 and T05: APPROVED= fills the approval line; the evidence asks for the branch taken and its measurement."""
    d = tmp_path / "specs" / "441-x"
    d.mkdir(parents=True)
    ts.brief(d, "2026-10-27", approved='Then do "it"')
    spec = (d / "spec.md").read_text(encoding="utf-8")
    assert "**Approved**: the GM, 2026-10-27, \"Then do 'it'\"" in spec
    assert "THE VERDICT: [the branch of the rule taken]" in spec and "the measurement that took it" in spec
