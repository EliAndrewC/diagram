"""The soak suite is DECLARED, DESELECTED and NON-VACUOUS (GM 2026-09-05).

`tests/soak/` is the tier above the gate - the same code over many seeds and larger, more realistic
maps - and it is deliberately empty. These pin the three properties that make an empty directory a
structure rather than a promise nobody keeps:

  * it is not collected by any ordinary run, so it can never slow the gate down by accident;
  * `make soak` REFUSES on an empty suite, so turning remote on cannot buy a vacuously green build;
  * the deselection lives in ONE place, and that place still keeps pytest's own defaults.

The membership rule those serve is in `tests/soak/CLAUDE.md`: a test belongs there if removing it
does not change coverage. That rule is enforced by the 100% floor rather than by review - a soak
test that reached a line nothing else reaches would fail the floor by name.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]

# pytest REPLACES this list rather than extending it, so dropping the defaults would make every run
# recurse into .git, build/, dist/ and node_modules. Read from `_pytest.main`, not from memory.
PYTEST_DEFAULTS = {"*.egg", ".*", "_darcs", "build", "CVS", "dist", "node_modules", "venv", "{arch}"}


def _ini() -> dict[str, object]:
    with open(SKILL / "pyproject.toml", "rb") as fh:
        return dict(tomllib.load(fh)["tool"]["pytest"]["ini_options"])


def test_the_soak_directory_exists_and_is_documented() -> None:
    doc = SKILL / "tests" / "soak" / "CLAUDE.md"
    assert doc.is_file(), "the soak suite is structure; its doc is what makes it that rather than an empty folder"
    text = doc.read_text(encoding="utf-8")
    assert "removing it does not change coverage" in text, "the membership rule must be stated where a reader meets it"


def test_the_soak_suite_is_deselected_in_exactly_one_place() -> None:
    ini = _ini()
    assert "soak" in ini.get("norecursedirs", []), "norecursedirs is the single deselection point"
    # An --ignore repeated across the Makefile's six pytest invocations is the stale-literal shape
    # this repository has been bitten by, so assert nobody has added one.
    mk = (SKILL / "Makefile").read_text(encoding="utf-8")
    assert "--ignore=tests/soak" not in mk, "deselect in pyproject only - six copies of a path literal go stale silently"


def test_the_pytest_defaults_survive_the_override() -> None:
    missing = PYTEST_DEFAULTS - set(_ini().get("norecursedirs", []))
    assert not missing, f"setting norecursedirs REPLACES pytest's list; these defaults were dropped: {sorted(missing)}"


def test_an_ordinary_collection_does_not_descend_into_the_soak() -> None:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "--co", "-q", "--no-cov", "-p", "no:cacheprovider"],
        cwd=SKILL,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert "tests/soak" not in r.stdout, "a broad run must not collect the soak suite"


def test_make_soak_refuses_rather_than_reporting_a_vacuous_green() -> None:
    """The property that stops this becoming a no-op: zero tests must not read as success."""
    r = subprocess.run(["make", "soak"], cwd=SKILL, capture_output=True, text=True, timeout=600)
    if list((SKILL / "tests" / "soak").glob("*.py")):
        return  # once the suite has content this target runs it; the refusal is only for the empty case
    assert r.returncode != 0, "an empty soak must FAIL - a green build that ran nothing is evidence of nothing"
    assert "EMPTY" in r.stdout, "the refusal must say why"
    assert "CLAUDE.md" in r.stdout, "and point at the doc that carries the membership rule"
