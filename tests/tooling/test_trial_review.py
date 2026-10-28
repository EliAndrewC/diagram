"""`scripts/trial-review.py` - `make trial-review` (feature 442): a Done trial's brief, request and research bundled for its one
review, the dispatch asking to check each figure against its recorded output."""

from __future__ import annotations

import importlib.util
import pathlib
import sys

from tests._scripts import script

_spec = importlib.util.spec_from_file_location("trial_review", script("trial-review.py"))
assert _spec and _spec.loader
tr = importlib.util.module_from_spec(_spec)
sys.modules["trial_review"] = tr
_spec.loader.exec_module(tr)


def test_the_bundle_holds_the_brief_the_request_the_research_and_the_instruction(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:  # noqa: ANN001
    d = tmp_path / "specs" / "441-x"
    (d / "research").mkdir(parents=True)
    (d / "spec.md").write_text("# Trial: x\n\n**Form**: trial\n\n**Status**: Done - stopped at the measurement\n", encoding="utf-8")
    (d / "request.md").write_text("> words\n", encoding="utf-8")
    (d / "research" / "ceilings.md").write_text("2.7%\n\n```\nlattice_search 3 self 0.171 cum 0.428\n```\n", encoding="utf-8")
    monkeypatch.setattr(tr, "ROOT", tmp_path)
    monkeypatch.setattr(tr, "CHECK_DIR", tmp_path / "check")
    assert tr.main(["441"]) == 0
    out = tmp_path / "check" / "trial-review-441"
    manifest = (out / "MANIFEST.md").read_text(encoding="utf-8")
    assert (out / "spec.md").is_file() and (out / "research" / "ceilings.md").is_file() and "`research/ceilings.md`" in manifest
    assert "CHECK each figure against the output recorded beside it" in manifest and "re-run a command only where" in capsys.readouterr().out
    assert "cum 0.428" in (out / "research" / "ceilings.md").read_text(encoding="utf-8"), "the recorded output rides in the bundle"
    assert tr.main(["441"]) == 0, "a second bundle replaces the first"
    (d / "spec.md").write_text("# Trial: x\n\n**Form**: trial\n\n**Status**: Done - promoted: the spike lands\n", encoding="utf-8")
    assert tr.main(["441"]) == 0
    assert "review it in full" in capsys.readouterr().out and "CHECK each figure" not in (out / "MANIFEST.md").read_text(encoding="utf-8")
    assert tr.measurement_only("**Status**: Running\n") is False and tr.measurement_only("no status\n") is False
    (d / "spec.md").write_text("# Feature Specification: x\n", encoding="utf-8")
    assert tr.main(["441"]) == 2 and tr.main([]) == 2 and tr.main(["999"]) == 2
