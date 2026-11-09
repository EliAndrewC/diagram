"""The incremental planner's reason to run everything (feature 415, T02, D3/D4; SC-001)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from l7r.diagram.ci import gate_config, incremental

MAKEFILE = """\
XDIST_WORKERS = 6
COV_SCOPE = --cov $(EXTRA)
EXTRA = -q
UNRELATED = 1
test:            ## [tests] {internal} the pytest phase itself
\tpython3 -m pytest -n $(XDIST_WORKERS) $(COV_SCOPE)

test-full:       ## [tests] the gate's whole test phase
\t@$(MAKE) test COV_FLOORS=1

docs:            ## [project] the make-targets page
\tpython3 scripts/make-docs.py $(UNRELATED)
"""


def _tree(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")


def test_the_config_hash_moves_on_the_machinery_a_lockfile_and_the_test_tables_only(tmp_path: Path) -> None:
    """D3 and spec US1 scenario 3: the gate's machinery, a pinned lockfile and the test configuration move it; a requirements
    `.in`, a script, a help line and a non-test pyproject table do not."""
    _tree(
        tmp_path,
        {
            "l7r/diagram/ci/a.py": "x = 1\n",
            "requirements.txt": "a==1\n",
            "requirements.in": "a\n",
            "scripts/s.py": "1\n",
            "Makefile": MAKEFILE,
            "pyproject.toml": "[project]\nname = 'x'\n[tool.coverage.run]\nsource = ['l7r']\n",
        },
    )
    base = gate_config.config_hash(tmp_path)
    for rel, text in (
        ("requirements.in", "a\nb\n"),
        ("scripts/s.py", "2\n"),
        ("Makefile", MAKEFILE.replace("itself", "itself, reworded")),
        ("pyproject.toml", "[project]\nname = 'y'\n[tool.coverage.run]\nsource = ['l7r']\n"),
    ):
        _tree(tmp_path, {rel: text})
        assert gate_config.config_hash(tmp_path) == base, rel
    for rel, text in (("requirements.txt", "a==2\n"), ("l7r/diagram/ci/a.py", "x = 2\n"), ("pyproject.toml", "[project]\nname = 'y'\n[tool.coverage.run]\nsource = ['l7r', 'z']\n")):
        _tree(tmp_path, {rel: text})
        moved = gate_config.config_hash(tmp_path)
        assert moved != base, rel
        base = moved


READERS = {
    "tests/__init__.py": "",
    "tests/_helper.py": "ROOT = 'x'\nTOOLS = ROOT + '/scripts/x.py'\n",
    "tests/test_direct.py": "def test_x():\n    assert open('scripts/a.py')\n",
    "tests/test_bare.py": "import os\nROOT = '.'\ndef test_x():\n    os.path.join(ROOT, \"scripts\")\n",
    "tests/sub/__init__.py": "",
    "tests/sub/test_via.py": "from tests._helper import TOOLS\n\ndef test_x():\n    assert TOOLS\n",
    "tests/sub/test_rel.py": "from .. import _helper\n\ndef test_x():\n    assert _helper\n",
    "tests/test_none.py": "def test_x():\n    assert 1\n",
    "tests/tooling/test_t.py": "def test_x():\n    assert 1\n",
    "tests/hooks/test_h.py": "def test_x():\n    assert 1\n",
}


def test_the_modules_that_read_scripts_are_found_through_their_helpers_and_a_bare_path(tmp_path: Path) -> None:
    """D4 and SC-001: a module naming `scripts/`, one building it as a bare `"scripts"` path component, and two reaching it
    only through a `tests/` helper they import (absolutely, relatively) are readers; a module that never mentions it is not;
    the tooling trees are selected whole instead."""
    _tree(tmp_path, READERS)
    assert gate_config.scripts_readers(tmp_path) == ["tests/sub/test_rel.py", "tests/sub/test_via.py", "tests/test_bare.py", "tests/test_direct.py"]
    assert gate_config.tooling_modules(tmp_path) == ["tests/hooks/test_h.py", "tests/tooling/test_t.py"]


def _baseline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, before: dict, now: dict) -> None:
    bdir = tmp_path / "gb"
    bdir.mkdir()
    monkeypatch.setattr(incremental, "baseline_dir", lambda root: bdir)
    (bdir / incremental.MANIFEST).write_text(json.dumps(before), encoding="utf-8")
    (bdir / incremental.COVERAGE_DB).write_bytes(b"")
    # ...with forty other baseline tests, so the selection stays under the planner's fraction (T05 is what changes that)
    others = {f"tests/test_other_{n}.py::test_x": [] for n in range(40)}
    (bdir / incremental.TESTS).write_text(json.dumps({**{f"{m}::test_x": [] for m in READERS if "/test_" in m}, **others}), encoding="utf-8")
    monkeypatch.setattr(incremental, "manifest", lambda root: now)


def test_a_scripts_change_plans_incremental_over_what_reads_scripts_and_reuses_the_tooling_tests(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """SC-001: after a baseline, a `scripts/` edit alone plans incremental, selecting the tooling trees and the readers, with
    the tooling tests reused on their recorded reads; nothing else runs."""
    _tree(tmp_path, READERS)
    before = {"engine": {}, "tests": {}, "tooling": "T", "gate_config": "G", "scripts": {"scripts/a.py": "1"}}
    _baseline(tmp_path, monkeypatch, before, {**before, "tooling": "U", "scripts": {"scripts/a.py": "2"}})
    pl = incremental.plan(tmp_path)
    assert pl.mode == "incremental" and pl.reuse_tooling and "scripts/" in pl.reason
    assert set(pl.changed_test_modules) == {"tests/sub/test_rel.py", "tests/sub/test_via.py", "tests/test_bare.py", "tests/test_direct.py", "tests/tooling/test_t.py", "tests/hooks/test_h.py"}
    assert "tests/test_none.py" not in pl.paths


def test_the_gate_configuration_plans_full_and_the_tooling_hash_alone_does_not(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """SC-001: a moved configuration plans full, as does a baseline that predates the key (once); a moved tooling hash with no
    other change plans incremental with nothing to run."""
    before = {"engine": {}, "tests": {}, "tooling": "T", "gate_config": "G", "scripts": {}}
    _baseline(tmp_path, monkeypatch, before, {**before, "gate_config": "H"})
    assert incremental.plan(tmp_path).mode == "full"
    (tmp_path / "gb" / incremental.MANIFEST).write_text(json.dumps({k: v for k, v in before.items() if k != "gate_config"}), encoding="utf-8")
    monkeypatch.setattr(incremental, "manifest", lambda root: before)
    assert incremental.plan(tmp_path).mode == "full", "a baseline without the key counts as moved"
    (tmp_path / "gb" / incremental.MANIFEST).write_text(json.dumps(before), encoding="utf-8")
    monkeypatch.setattr(incremental, "manifest", lambda root: {**before, "tooling": "U"})
    pl = incremental.plan(tmp_path)
    assert pl.mode == "incremental" and not pl.reuse_tooling and "nothing" in pl.reason


def test_an_unparseable_helper_reads_nothing(tmp_path: Path) -> None:
    """A file under `tests/` that does not parse
    imports nothing (and still counts where its own text mentions `scripts`)."""
    _tree(tmp_path, {"tests/__init__.py": "", "tests/_broken.py": "def (:\n", "tests/test_uses.py": "from tests import _broken\n"})
    assert gate_config.scripts_readers(tmp_path) == []


def test_the_config_hash_is_blind_to_a_docstring_or_comment_in_the_machinery(tmp_path: Path) -> None:
    """Feature 426's audit: the machinery's Python is keyed on what runs."""
    conf = tmp_path / "tests" / "conftest.py"
    conf.parent.mkdir(parents=True)
    conf.write_text('def pytest_x():\n    """Doc."""\n    return 1\n', encoding="utf-8")
    before = gate_config.config_hash(tmp_path)
    conf.write_text('def pytest_x():\n    """Doc, reworded."""\n    return 1  # c\n', encoding="utf-8")
    assert gate_config.config_hash(tmp_path) == before
    conf.write_text('def pytest_x():\n    return 2\n', encoding="utf-8")
    assert gate_config.config_hash(tmp_path) != before
