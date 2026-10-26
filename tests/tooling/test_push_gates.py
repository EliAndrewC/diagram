"""`scripts/gates/push_gates.py` (feature 430 T04, D4; the GM 2026-10-26, item 4): a push gate skips a delta holding nothing it
judges, and a delta it passed already; never a refusal, never uncommitted content, never with no merge base."""

import importlib.util
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("push_gates", REPO / "scripts" / "gates" / "push_gates.py")
assert _spec and _spec.loader
pg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pg)


def _constant(path: str, name: str) -> str:
    m = re.search(rf'^{name} = (.+)$', (REPO / path).read_text(encoding="utf-8"), re.M)
    assert m, f"{name} in {path}"
    return m.group(1)


def _covered(gate: str, path: str) -> bool:
    return bool(pg.judged(gate, [path.rstrip("/") + "/x" if not path.endswith((".json", ".md")) else path]))


def test_each_gate_judges_every_path_its_own_constants_name() -> None:
    """The lists are read off the gates' own code; a constant naming a path the list lacks would let a delta through unjudged."""
    for p in re.findall(r'"([^"]+)"', _constant("scripts/record/claims.py", "BASE_PATHS")):
        assert _covered("claims", p) or p == "QUESTIONS", p
    for name in ("INDEX", "DEFERRED", "STORE"):
        assert _covered("claims", re.search(r'"([^"]+)"', _constant("scripts/record/claims.py", name)).group(1)), name
    assert _covered("claims", re.search(r'"([^"]+)"', _constant("scripts/record/claims.py", "QUESTIONS")).group(1))
    assert _covered("claims", "specs/430-x/tasks.md") and _covered("claims", "specs/430-x/gm-review.jsonl"), "a known drift's task row and record"
    for path, name in (
        ("scripts/record/record_units.py", "RECORD"),
        ("scripts/record/entry_owed.py", "CLASSES"),
        ("scripts/record/entry_owed.py", "COMPOUND_KINDS"),
        ("scripts/record/modal_owed.py", "MODALS"),
    ):
        assert _covered("entry", re.search(r'"([^"]+)"', _constant(path, name)).group(1)), name
    for p in ("l7r/diagram/hamletgen/law.py", "pool/hamlets/m/m.json", "pool/hamlets/m/m.gen.py"):
        assert pg.judged("cohort", [p]), p


def _git(repo: Path, *a: str) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", *a], capture_output=True, text=True, check=True).stdout


def _repo(tmp: Path) -> Path:
    origin, work = tmp / "origin.git", tmp / "work"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    _git(tmp, "init", "-q", str(work))
    (work / "scripts").mkdir()
    (work / "scripts" / "g.sh").write_text("gate\n")
    (work / "l7r").mkdir()
    (work / "l7r" / "a.py").write_text("x = 1\n")
    _git(work, "add", "-A")
    _git(work, "commit", "-qm", "base")
    _git(work, "remote", "add", "origin", str(origin))
    _git(work, "push", "-q", "origin", "HEAD:main")
    _git(work, "fetch", "-q", "origin")
    return work


def test_a_records_only_delta_skips_every_gate(tmp_path: Path) -> None:
    """SC-003: a delta of run records holds nothing the claims, record or cohort gate judges - each exits before reading."""
    work = _repo(tmp_path)
    (work / "dev" / "run-log").mkdir(parents=True)
    (work / "dev" / "run-log" / "r.json").write_text("{}")
    _git(work, "add", "-A")
    _git(work, "commit", "-qm", "a record")
    for gate in ("claims", "entry", "cohort"):
        assert "nothing to judge" in pg.skip(work, gate), gate


def test_a_pass_is_served_only_for_the_same_committed_content(tmp_path: Path) -> None:
    work = _repo(tmp_path)
    (work / "l7r" / "a.py").write_text("x = 2\n")
    assert pg.skip(work, "claims") == "", "a judged path changed: the gate runs"
    _git(work, "commit", "-qam", "code")
    assert pg.skip(work, "claims") == ""
    pg.record_pass(work, "claims")
    assert "passed already" in pg.skip(work, "claims"), "the same content: served"
    (work / "l7r" / "a.py").write_text("x = 3\n")
    assert pg.skip(work, "claims") == "", "an uncommitted judged path is never served"
    _git(work, "commit", "-qam", "more code")
    assert pg.skip(work, "claims") == "", "new content: judged again"
    (work / "scripts" / "g.sh").write_text("gate, changed\n")
    _git(work, "commit", "-qam", "the gate's own code")
    pg.record_pass(work, "claims")
    assert "passed already" in pg.skip(work, "claims")


def test_with_no_merge_base_nothing_is_skipped(tmp_path: Path) -> None:
    """A tree with no `origin/main` (the guard suites' fixtures) has no delta to read: every gate judges as it always did."""
    work = tmp_path / "w"
    _git(tmp_path, "init", "-q", str(work))
    (work / "a.txt").write_text("a\n")
    _git(work, "add", "-A")
    _git(work, "commit", "-qm", "only")
    assert pg.skip(work, "claims") == "" and pg.skip(work, "entry") == "" and pg.skip(work, "cohort") == ""
    pg.record_pass(work, "claims")
    assert pg.skip(work, "claims") == ""
