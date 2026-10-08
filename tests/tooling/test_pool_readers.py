"""scripts/gates/pool-readers.py (feature 328 wave 54): the readers are named when the manifests move, and not again once
stamped."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "gates" / "pool-readers.py"


def _run(repo: Path, *args: str) -> str:
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=repo, capture_output=True, text=True, check=True).stdout


def test_readers_named_when_the_manifests_move_and_not_once_stamped(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "pool" / "hamlets" / "a").mkdir(parents=True)
    man = tmp_path / "pool" / "hamlets" / "a" / "a.json"
    man.write_text("{}")
    (tmp_path / "tests" / "hamletgen").mkdir(parents=True)
    (tmp_path / "tests" / "gate").mkdir()
    (tmp_path / "tests" / "hamletgen" / "test_reads.py").write_text('GENS = glob(os.path.join(ROOT, "pool", "hamlets", "*"))\n')
    (tmp_path / "tests" / "hamletgen" / "test_other.py").write_text("x = 1\n")
    (tmp_path / "tests" / "test_census.py").write_text('for tree in ("pool", "legacy-hand-authored-pool"):\n    pass\n')
    (tmp_path / "tests" / "gate" / "test_gate_reads.py").write_text('p = "pool/hamlets/*/*.json"\n')
    assert _run(tmp_path, "changed").split() == ["tests/hamletgen/test_reads.py", "tests/test_census.py"], "no stamp yet: the quick-tree readers only"
    _run(tmp_path, "stamp")
    assert _run(tmp_path, "changed") == "", "stamped and unchanged: nothing"
    man.write_text('{"lanes": []}')
    assert _run(tmp_path, "changed").split() == ["tests/hamletgen/test_reads.py", "tests/test_census.py"], "a manifest moved: the readers again"
