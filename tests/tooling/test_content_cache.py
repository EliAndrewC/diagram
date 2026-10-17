"""Feature 383, phase 1 (SC-002, SC-003, SC-005): a check's work kept by the content it read - and never an answer changed.

WHAT THESE PROVE. A file's content id is git's blob id while the index holds it unchanged, and a hash of its bytes once the
work tree changes it. A fact is served again only for the same content under the same extractor: a changed file and a
changed extractor each extract again. A check's whole answer is replayed only after a PASS and only while every input is
unchanged; a refusal is never kept. Each of the four whole-tree checks says the same with the cache as without it, on a
tree that passes and on one seeded to fail, and finds a fault put into a file after a cached run. The ledger check reads
no transcript once every pass is costed, and answers as before. A revision's record files are read from git once.
"""

from __future__ import annotations

import concurrent.futures
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

from tests._scripts import ROOT, script


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), script(name))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name.replace("-", "_")] = mod
    spec.loader.exec_module(mod)
    return mod


rc = _load("record_cache")


def _git(d: pathlib.Path, *a: str) -> str:
    return subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, check=True).stdout


def _repo(tmp: pathlib.Path, files: dict[str, str]) -> pathlib.Path:
    d = tmp / "repo"
    d.mkdir()
    _git(d, "init", "-q")
    for name, text in files.items():
        (d / name).parent.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(text, encoding="utf-8")
    _git(d, "add", "-A")
    _git(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "seed")
    return d


@pytest.fixture(autouse=True)
def _cache_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("L7R_CACHE_OFF", raising=False)


def test_a_clean_file_is_its_blob_and_a_changed_or_untracked_one_its_bytes(tmp_path: pathlib.Path) -> None:
    d = _repo(tmp_path, {"a.txt": "one\n", "sub/b.txt": "two\n"})
    ids = rc.content_ids(d)
    assert ids["a.txt"] == _git(d, "rev-parse", "HEAD:a.txt").strip()
    (d / "a.txt").write_text("changed\n", encoding="utf-8")
    (d / "sub" / "new.txt").write_text("new\n", encoding="utf-8")
    again = rc.content_ids(d, untracked=True)
    assert again["a.txt"] != ids["a.txt"]
    assert again["a.txt"] == subprocess.run(["git", "-C", str(d), "hash-object", "a.txt"], capture_output=True, text=True).stdout.strip(), (
        "a changed file's id is the blob id git would give it (383 amendment 1: same bytes, same id, in a clone or a worktree)"
    )
    assert again["sub/b.txt"] == ids["sub/b.txt"] and "sub/new.txt" in again
    assert "sub/new.txt" not in rc.content_ids(d), "untracked files only when asked"
    assert set(rc.content_ids(d, ["sub"], untracked=True)) == {"sub/b.txt", "sub/new.txt"}


def test_a_fact_is_extracted_once_per_content_and_again_for_a_changed_file_or_extractor(tmp_path: pathlib.Path) -> None:
    d = _repo(tmp_path, {"a.txt": "one\n", "b.txt": "two\n"})
    code = tmp_path / "extractor.py"
    code.write_text("X = 1\n", encoding="utf-8")
    calls: list[str] = []

    def extract(p: str) -> str:
        calls.append(p)
        return (d / p).read_text(encoding="utf-8").upper()

    assert rc.FileFacts(d, "t", code).facts(["a.txt", "b.txt"], extract) == {"a.txt": "ONE\n", "b.txt": "TWO\n"}
    assert rc.FileFacts(d, "t", code).facts(["a.txt", "b.txt"], extract) == {"a.txt": "ONE\n", "b.txt": "TWO\n"}
    assert calls == ["a.txt", "b.txt"], "the second run extracted nothing"
    (d / "a.txt").write_text("three\n", encoding="utf-8")
    assert rc.FileFacts(d, "t", code).facts(["a.txt", "b.txt"], extract)["a.txt"] == "THREE\n"
    assert calls[2:] == ["a.txt"], "only the changed file is extracted again"
    code.write_text("X = 2\n", encoding="utf-8")
    rc.FileFacts(d, "t", code).facts(["a.txt", "b.txt"], extract)
    assert calls[3:] == ["a.txt", "b.txt"], "a changed extractor extracts everything again"


def test_a_batch_extractor_is_handed_only_the_misses(tmp_path: pathlib.Path) -> None:
    d = _repo(tmp_path, {"a.txt": "1", "b.txt": "2"})
    handed: list[list[str]] = []

    def many(paths: list[str]) -> dict[str, int]:
        handed.append(paths)
        return {p: len(p) for p in paths}

    rc.FileFacts(d, "b", d / "a.txt").facts_batch(["a.txt", "b.txt"], many)
    (d / "b.txt").write_text("22", encoding="utf-8")
    assert rc.FileFacts(d, "b", d / "a.txt").facts_batch(["a.txt", "b.txt"], many) == {"a.txt": 5, "b.txt": 5}
    assert handed == [["a.txt", "b.txt"], ["b.txt"]]


def test_the_switch_turns_the_facts_off(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    d = _repo(tmp_path, {"a.txt": "1"})
    calls: list[str] = []
    rc.FileFacts(d, "s", d / "a.txt").facts(["a.txt"], calls.append)
    monkeypatch.setenv("L7R_CACHE_OFF", "1")
    rc.FileFacts(d, "s", d / "a.txt").facts(["a.txt"], calls.append)
    assert calls == ["a.txt", "a.txt"]


def test_a_pass_is_replayed_until_an_input_changes_and_a_failure_is_never_kept(tmp_path: pathlib.Path) -> None:
    d = _repo(tmp_path, {"in/a.txt": "1", "other.txt": "x"})
    memo = rc.ResultMemo(d, "m", ["in"], argv=["cmd"])
    assert memo.hit() is None
    memo.keep("out\n", "err\n")
    assert rc.ResultMemo(d, "m", ["in"], argv=["cmd"]).hit() == ("out\n", "err\n")
    (d / "other.txt").write_text("y", encoding="utf-8")
    assert rc.ResultMemo(d, "m", ["in"], argv=["cmd"]).hit() is not None, "a file outside the inputs changes nothing"
    assert rc.ResultMemo(d, "m", ["in"], argv=["other"]).hit() is None, "another command is another answer"
    (d / "in" / "b.txt").write_text("new", encoding="utf-8")
    assert rc.ResultMemo(d, "m", ["in"], argv=["cmd"]).hit() is None, "an untracked input is an input"


def test_memo_check_replays_a_pass_and_always_runs_a_failure(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    mc = _load("memo_check")
    d = _repo(tmp_path, {"in/a.txt": "1"})
    count = tmp_path / "count"
    cmd = [
        sys.executable,
        "-c",
        f"import pathlib,sys; p=pathlib.Path({str(count)!r}); p.write_text(p.read_text()+'x' if p.exists() else 'x'); print('ran'); sys.exit(int(pathlib.Path({str(d / 'in' / 'a.txt')!r}).read_text()=='bad'))",
    ]
    assert mc.run(d, "c", ["in"], cmd) == 0 and mc.run(d, "c", ["in"], cmd) == 0
    assert count.read_text() == "x", "the second pass was replayed"
    assert capsys.readouterr().out == "ran\nran\n", "with the same output"
    (d / "in" / "a.txt").write_text("bad", encoding="utf-8")
    assert mc.run(d, "c", ["in"], cmd) == 1 and mc.run(d, "c", ["in"], cmd) == 1
    assert count.read_text() == "xxx", "a failure is computed every time"


# ---- the four whole-tree checks: the same answer with the cache and without it (SC-002) ------------------------------------


def _run(argv: list[str], cwd: pathlib.Path, off: bool) -> tuple[int, str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    env.pop("L7R_CACHE_OFF", None)
    if off:
        env["L7R_CACHE_OFF"] = "1"
    p = subprocess.run([sys.executable, *argv], cwd=cwd, capture_output=True, text=True, check=False, env=env)
    return p.returncode, (p.stdout + p.stderr).replace(str(cwd), "<root>")


def _same_on_and_off(argv: list[str], cwd: pathlib.Path) -> tuple[int, str]:
    # the cache-off run and the first cache-on run share nothing (the off run reads and writes no cache), so they run side by
    # side; the second cache-on run follows the first, as a warm run must (feature 383 amendment 4, plan D29)
    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        off_f, first_f = pool.submit(_run, argv, cwd, True), pool.submit(_run, argv, cwd, False)
        off, first = off_f.result(), first_f.result()
    second = _run(argv, cwd, False)
    assert first == off and second == off, f"the cache changed the answer:\n{off}\n{first}\n{second}"
    return off


def _check_repo(tmp: pathlib.Path, files: dict[str, str]) -> pathlib.Path:
    """A repository carrying the real scripts (the checks import the cache module beside them) and the given files."""
    d = _repo(tmp, files)
    shutil.copytree(ROOT / "scripts", d / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    return d


def test_duplicate_defs_answers_the_same_and_finds_a_fault_put_in_after_a_cached_run(tmp_path: pathlib.Path) -> None:
    d = _check_repo(tmp_path, {"l7r/a.py": "def f():\n    return 1\n", "l7r/b.py": "X = 1\n"})
    argv = ["scripts/gates/check-duplicate-defs.py", "."]
    assert _same_on_and_off(argv, d)[0] == 0
    (d / "l7r" / "b.py").write_text("def g():\n    return 1\n\n\ndef g():\n    return 2\n", encoding="utf-8")
    code, out = _same_on_and_off(argv, d)
    assert code == 1 and "duplicate top-level def 'g'" in out


def test_function_cap_answers_the_same_and_finds_a_fault_put_in_after_a_cached_run(tmp_path: pathlib.Path) -> None:
    d = _check_repo(tmp_path, {"l7r/a.py": "def f():\n    return 1\n"})
    shutil.copy(ROOT / "pyproject.toml", d / "pyproject.toml")
    argv = ["scripts/gates/check-function-cap.py", "."]
    assert _same_on_and_off(argv, d)[0] == 0
    (d / "l7r" / "a.py").write_text("def f():  # noqa: PLR0915\n    return 1\n", encoding="utf-8")
    code, out = _same_on_and_off(argv, d)
    assert code == 1 and "say why the body must remain one" in out


def test_the_conflict_check_answers_the_same_and_finds_a_marker_put_in_after_a_cached_run(tmp_path: pathlib.Path) -> None:
    d = _check_repo(tmp_path, {"a.md": "fine\n"})
    argv = ["scripts/hooks/lib/hm_conflict.py", "--tracked", "."]
    assert _same_on_and_off(argv, d)[0] == 0
    (d / "a.md").write_text("<" * 7 + " ours\nx\n" + "=" * 7 + "\ny\n" + ">" * 7 + " theirs\n", encoding="utf-8")
    code, out = _same_on_and_off(argv, d)
    assert code == 1 and "a.md" in out


def test_the_pointer_check_answers_the_same_and_resolves_a_new_question_each_run(tmp_path: pathlib.Path) -> None:
    files = {
        "research/questions/0001-a.html": "x",
        "research/contents.json": json.dumps({"sections": [{"id": "water"}]}),
        "research/moved-303.json": json.dumps({"files": {}, "pages": {"water": "water"}, "numbers": {"water 120": "0001"}}),
        "docs/x.md": "see research/questions/0002-b.html and research/contents.json#water\n",
    }
    d = _check_repo(tmp_path, files)
    argv = ["scripts/gates/check-research-pointers.py", "."]
    code, out = _same_on_and_off(argv, d)
    assert code == 1 and "0002-b.html` - no such question file" in out
    (d / "research" / "questions" / "0002-b.html").write_text("y", encoding="utf-8")
    _git(d, "add", "-A")
    assert _same_on_and_off(argv, d)[0] == 0, "the cached file now resolves: its questions are asked each run"
    (d / "docs" / "x.md").write_text("water 120\n", encoding="utf-8")
    code, out = _same_on_and_off(argv, d)
    assert code == 1 and "it is now 0001" in out


@pytest.mark.parametrize("argv", [["scripts/gates/check-research-pointers.py", "."], ["scripts/hooks/lib/hm_conflict.py", "--tracked", "."]], ids=["pointers", "conflicts"])
def test_the_whole_repository_s_pointers_and_conflicts_are_the_same_with_the_cache(argv: list[str]) -> None:
    """SC-002 over this repository itself, for the two checks that read every tracked file - one test each, so they run side by
    side (feature 383 amendment 4, plan D29): it was 9.4 s, the longest test a landing ran."""
    _same_on_and_off(argv, ROOT)


# ---- the ledger check (SC-003) ---------------------------------------------------------------------------------------------


def test_the_ledger_check_reads_no_transcript_once_every_pass_is_costed(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    lo = _load("ledger_owed")
    root = tmp_path / "projects"
    t = root / "p" / "s" / "subagents" / "agent-a1.jsonl"
    t.parent.mkdir(parents=True)
    call = {"timestamp": "2026-10-12T00:00:00Z", "requestId": "r", "message": {"role": "assistant", "usage": {"input_tokens": 1000, "output_tokens": 100}}}
    end = {**call, "timestamp": "2026-10-12T00:01:00Z"}
    t.write_text(json.dumps({"message": {"role": "user", "content": "go"}, "timestamp": "2026-10-12T00:00:00Z"}) + "\n" + json.dumps(call) + "\n" + json.dumps(end) + "\n", encoding="utf-8")
    passes = [{"check": "glyph-check", "agent": "a1", "segment": "0", "wall": "1 s", "tokens": "x"}]
    kept = tmp_path / "settled.json"
    first = lo.settled(passes, root, kept)
    reads: list[pathlib.Path] = []
    real = pathlib.Path.read_text
    monkeypatch.setattr(pathlib.Path, "read_text", lambda self, *a, **k: reads.append(self) or real(self, *a, **k))
    globs: list[str] = []
    monkeypatch.setattr(pathlib.Path, "glob", lambda self, pat: globs.append(pat) or iter(()))
    again = lo.settled(passes, root, kept)
    assert again == first and first[0]["wall"] == "60 s"
    assert t not in reads and not globs, "no transcript read, no listing made"
    monkeypatch.undo()
    with t.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**call, "timestamp": "2026-10-12T00:02:00Z", "requestId": "r2"}) + "\n")
    assert lo.settled(passes, root, kept)[0]["wall"] == "120 s", "a transcript that grew is costed again"
    assert lo.settled(passes, root, None)[0]["wall"] == "120 s", "and with no cache the answer is the same"


# ---- check-bundle's base read (SC-005) ---------------------------------------------------------------------------------------


def test_a_revision_s_record_files_are_read_from_git_once(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ro = _load("record_owed")
    d = _repo(tmp_path, {"research/questions/0001-a.html": "<h2 id=a>A</h2>"})
    rev = _git(d, "rev-parse", "HEAD").strip()
    asked: list[list[str]] = []
    real = ro._cat
    monkeypatch.setattr(ro, "_cat", lambda root, objs: asked.append(list(objs)) or real(root, objs))
    ro._REV_FILES.clear()
    first = ro._blobs_at(d, rev, ["research/questions/0001-a.html"])
    ro._REV_FILES.clear()  # a new process: only the disk cache is left
    assert ro._blobs_at(d, rev, ["research/questions/0001-a.html"]) == first == ["<h2 id=a>A</h2>"]
    assert len(asked) == 1
