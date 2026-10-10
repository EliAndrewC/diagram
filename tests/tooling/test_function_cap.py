"""The function-length cap: 100 statements, ruff's count, held at the gate (feature 370).

The GM, 2026-10-10: *"Please go with 100. And we can document why 100 is the number that we went with, like that it
is the second most common value on GitHub from our initial survey"* (`specs/370-function-length-gate/research.md`
R1), and *"I do like the idea of just doing that in our linter"*. These run the project's own ruff configuration on
fixture files, so they prove the SETTING, not a copy of it.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

from tests._scripts import script

REPO = Path(__file__).resolve().parents[2]
CAP = 100
#: the one line `make static` and the push run over the trees the lint fence leaves out (plan D2)
OUT_OF_FENCE = "ruff check --select PLR0915,PGH004 scripts pool tests/hooks"

_spec = importlib.util.spec_from_file_location("check_file_scale", script("check-file-scale.py"))
assert _spec is not None and _spec.loader is not None
cfs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfs)


def _function(n: int, suppress: str = "") -> str:
    """A module holding one function of exactly `n` statements (ruff counts the body's statements)."""
    return f"def f() -> None:{suppress}\n" + "".join(f"    x{i} = {i}\n" for i in range(n))


def _ruff(path: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--no-cache", "--config", str(REPO / "pyproject.toml"), *extra, str(path)],
        capture_output=True,
        text=True,
        check=False,
        cwd=REPO,
    )


@pytest.mark.parametrize(("n", "fails"), [(CAP, False), (CAP + 1, True)])
def test_the_project_config_fails_a_function_past_100_statements(tmp_path: Path, n: int, fails: bool) -> None:
    """SC-001: 101 statements fails, 100 passes, under the configuration the gate runs."""
    f = tmp_path / "one.py"
    f.write_text(_function(n))
    r = _ruff(f)
    assert ("PLR0915" in r.stdout) is fails, r.stdout
    if fails:
        assert f"({CAP + 1} > {CAP})" in r.stdout


def test_a_blanket_noqa_is_refused_so_it_cannot_silence_the_cap(tmp_path: Path) -> None:
    """FR-004: a bare `# noqa` would suppress the cap with no rule named and no reason (PGH004)."""
    f = tmp_path / "bare.py"
    f.write_text(_function(CAP + 1, "  # noqa"))
    r = _ruff(f)
    assert "PGH004" in r.stdout, r.stdout


def test_the_out_of_fence_line_holds_the_cap_over_scripts_pool_and_hook_tests(tmp_path: Path) -> None:
    """FR-002: the trees `extend-exclude` fences out are named explicitly, so ruff lints them for these two rules."""
    for where in ("Makefile", "scripts/sync-with-main.sh"):
        assert OUT_OF_FENCE in (REPO / where).read_text(), f"{where} lost the out-of-fence line"
    d = tmp_path / "scripts"
    d.mkdir()
    (d / "long.py").write_text(_function(CAP + 1))
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--no-cache", "--config", str(REPO / "pyproject.toml"), "--select", "PLR0915,PGH004", str(d)],
        capture_output=True,
        text=True,
        check=False,
        cwd=REPO,
    )
    assert r.returncode == 1 and "PLR0915" in r.stdout, r.stdout


def test_the_setting_says_why_100() -> None:
    """FR-005 / SC-005: the GM's reason stands beside the number."""
    text = (REPO / "pyproject.toml").read_text()
    assert "max-statements = 100" in text
    assert "131 of 1,209" in text and "second most common" in text


@pytest.mark.parametrize(
    ("line", "refused"),
    [
        ("def f():  # noqa: PLR0915", True),
        ("def f():  # noqa: PLR0915 - long", True),
        ("def f():  # noqa: PLR0915 - one ordered pass whose steps share every local", False),
        ("def f():  # noqa: E501, PLR0915 too short", False),
        ("def f():  # noqa: E501", False),
    ],
)
def test_a_cap_suppression_must_say_why_the_body_stays_one(tmp_path: Path, line: str, refused: bool) -> None:
    """FR-004 / SC-004: fewer than three words after the code is refused, with the clause-12 message."""
    (tmp_path / "m.py").write_text(line + "\n    pass\n")
    found = cfs.reasonless_suppressions(str(tmp_path))
    assert bool(found) is refused, found
    r = subprocess.run([sys.executable, str(script("check-file-scale.py")), str(tmp_path)], capture_output=True, text=True, check=False)
    assert (r.returncode == 1) is refused
    if refused:
        assert "m.py:1" in r.stderr and "why the body must remain one" in r.stderr and "or split it" in r.stderr
