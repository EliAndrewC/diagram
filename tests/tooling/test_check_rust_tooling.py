"""`make rust-tooling` - no Python-only check without its row in `dev/rust-tooling.md` (feature 443 T07, FR-011, SC-007).

The check fails on a scratch reader of each kind with no row - one using `ast.parse`, `tokenize`, `inspect`, `symtable`, the
builtin `compile(`, one that only globs `*.py`, one with a `.py` suffix test, a shell `-name '*.py'`, and a Makefile recipe running
ruff - and passes on the real tree, which it reads to find `scripts/gates/check-file-scale.py` (the round arbiter's note).
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

from tests._scripts import script

REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("check_rust_tooling", script("check-rust-tooling.py"))
assert _spec is not None and _spec.loader is not None
crt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(crt)

ROW = "| check | today | rust | fate | keys |\n|---|---|---|---|---|\n"


def _repo(tmp: Path, files: dict[str, str], inventory: str = "") -> Path:
    for rel, text in {"dev/rust-tooling.md": ROW + inventory, **files}.items():
        (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp / rel).write_text(text)
    subprocess.run(["git", "init", "-q", str(tmp)], check=True)
    subprocess.run(["git", "-C", str(tmp), "add", "-A"], check=True)
    return tmp


def test_the_real_tree_has_a_row_for_every_reader_and_finds_the_file_cap() -> None:
    files = subprocess.run(["git", "-C", str(REPO), "ls-files"], capture_output=True, text=True, check=True).stdout.split()
    assert "scripts/gates/check-file-scale.py" in crt.readers(REPO, files)
    assert crt.problems(REPO) == []
    assert crt.main(["--root", str(REPO)]) == 0


@pytest.mark.parametrize(
    ("name", "text"),
    [
        ("scripts/a.py", "import ast\n\nast.parse('x')\n"),
        ("scripts/b.py", "import tokenize\n"),
        ("scripts/c.py", "from inspect import getsource\n"),
        ("scripts/d.py", "import symtable\n"),
        ("scripts/e.py", "code = compile(src, 'x', 'exec')\n"),
        ("scripts/f.py", "from pathlib import Path\n\nfor p in Path('.').rglob(\"*.py\"):\n    pass\n"),
        ("scripts/g.py", "ok = [p for p in names if p.endswith('.py')]\n"),
        ("scripts/h.py", "ok = p.suffix == \".py\"\n"),
        ("scripts/i.sh", "find . -name '*.py'\n"),
    ],
)
def test_a_reader_of_each_kind_with_no_row_fails_and_a_row_clears_it(tmp_path: Path, name: str, text: str) -> None:
    root = _repo(tmp_path, {name: text})
    assert crt.problems(root) == [f"{name}: reads Python's syntax tree or .py files, and no row of dev/rust-tooling.md names it"]
    (root / "dev" / "rust-tooling.md").write_text(ROW + f"| x | y | z | unchanged | `{name.rsplit('/', 1)[0]}/*` |\n")
    assert crt.problems(root) == [], "a glob key names it"


def test_a_dotted_compile_and_a_mention_in_specs_are_not_readers(tmp_path: Path) -> None:
    root = _repo(tmp_path, {"scripts/a.py": "import re\n\nR = re.compile('x')\n", "specs/1/x.py": "import ast\n"})
    assert crt.problems(root) == []


def test_a_make_recipe_running_a_python_only_tool_needs_its_row(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _repo(tmp_path, {"Makefile": "lint:   ## lint\n\truff check .\nother:\n\techo hi\nX := 1\n"})
    assert crt.problems(root) == ["make lint: its recipe runs a Python-only tool, and no row of dev/rust-tooling.md names it"]
    assert crt.main(["--root", str(root)]) == 1 and "add a row to dev/rust-tooling.md" in capsys.readouterr().err
    (root / "dev" / "rust-tooling.md").write_text(ROW + "| lint | ruff | clippy | one for one | `make lint` |\n")
    assert crt.problems(root) == []


def test_no_inventory_names_nothing(tmp_path: Path) -> None:
    root = _repo(tmp_path, {"scripts/a.py": "import ast\n"})
    (root / "dev" / "rust-tooling.md").unlink()
    assert len(crt.problems(root)) == 1
