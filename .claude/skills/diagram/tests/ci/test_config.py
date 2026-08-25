"""The rate is pinned (it is mirrored in the Lambda), and the secrets resolve in the documented order."""

from __future__ import annotations

from pathlib import Path

import pytest

from l7r.diagram.ci import config


def test_the_rate_is_the_lambdas_rate() -> None:
    assert config.RATE_PER_MIN == 0.08 and config.COMPUTE_TYPE == "BUILD_GENERAL1_XLARGE"
    assert config.PARK_TIMEOUT_S == 120


def test_secrets_resolution_order(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    main = tmp_path / "main"
    clone = main / ".clones" / "c"
    clone.mkdir(parents=True)
    monkeypatch.delenv("DIAGRAM_SECRETS", raising=False)
    paths = config.candidate_paths(clone)
    assert paths[0] == clone / "development-secrets.ini" and paths[1] == main / "development-secrets.ini" and paths[-1].as_posix().startswith("/gm-assistant/")
    monkeypatch.setenv("DIAGRAM_SECRETS", str(tmp_path / "env.ini"))
    assert config.candidate_paths(clone)[0] == tmp_path / "env.ini"
    (tmp_path / "env.ini").write_text("[aws]\nregion = eu-west-1\naccess_key_id = AK\nsecret_access_key = SK\nci_bucket = b\necr_image = e\n[github]\ncodebuild_pat = P\n", encoding="utf-8")
    s = config.load_secrets(clone)
    assert (s.region, s.access_key_id, s.ci_bucket, s.github_pat, s.log_group) == ("eu-west-1", "AK", "b", "P", "/aws/codebuild/gm-assistant")
    assert s.path == str(tmp_path / "env.ini")


def test_missing_secrets_names_every_place_looked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DIAGRAM_SECRETS", str(tmp_path / "nope.ini"))
    monkeypatch.setattr(config, "candidate_paths", lambda root: [tmp_path / "nope.ini", tmp_path / "other.ini"])
    with pytest.raises(FileNotFoundError) as e:
        config.load_secrets(tmp_path)
    assert "nope.ini" in str(e.value) and "other.ini" in str(e.value) and "development-secrets.ini.example" in str(e.value)


def test_a_file_with_neither_section_loads_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "x.ini").write_text("[other]\nk = v\n", encoding="utf-8")
    monkeypatch.setenv("DIAGRAM_SECRETS", str(tmp_path / "x.ini"))
    s = config.load_secrets(tmp_path)
    assert s.access_key_id == "" and s.github_pat == "" and s.region == "us-east-1"


def test_the_example_matches_the_repo_file() -> None:
    root = Path(__file__).resolve().parents[5]
    assert (root / "development-secrets.ini.example").read_text(encoding="utf-8") == config.SECRETS_EXAMPLE
