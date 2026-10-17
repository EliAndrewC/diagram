"""Feature 383 amendment 1 (SC-010, SC-011): a tooling test file's pass reused only on identical inputs; quote-verbatim's
verdicts kept by their passage and page.

WHAT THESE PROVE. A kept pass is reused while every file it read and every directory it listed is unchanged, and not when one
changed, when it read a file git ignores, when it started another program against the repository, or under another
interpreter. A child process is known when it is a Python process that records itself, and not when it runs isolated, drops
the recording from its environment, or is another program working in the repository; git working on paths it names outside
the repository is known. A module's bytecode read stands for its source. A verdict is served again for the same passage and
page, and judged afresh when either changes.
"""

from __future__ import annotations

import importlib.util
import sys

from tests._scripts import script
from tests.tooling import _test_deps as deps

ROOT = str(deps.ROOT)


def test_a_kept_read_set_holds_only_while_everything_it_read_is_unchanged() -> None:
    ids = {"scripts/a.py": "1", "tests/tooling/test_a.py": "2"}
    entries = {"scripts": ["a.py"], "": ["scripts", "tests"]}
    states = {"f:scripts/a.py": "1", "d:scripts": '["a.py"]'}
    kept = {"opaque": [], "files": ["scripts/a.py"], "dirs": ["scripts"]}
    assert deps.entry_ok(kept, states, ids, entries)
    assert not deps.entry_ok(kept, states, {**ids, "scripts/a.py": "9"}, entries), "a file it read changed"
    assert not deps.entry_ok(kept, states, ids, {**entries, "scripts": ["a.py", "b.py"]}), "a directory it listed gained an entry"
    assert not deps.entry_ok({**kept, "opaque": ["git"]}, states, ids, entries), "it ran git in the repository"
    assert not deps.entry_ok({**kept, "files": ["x/.gencache/k"]}, {**states, "f:x/.gencache/k": "ignored"}, ids, entries), "a file git ignores"
    assert not deps.entry_ok({**kept, "files": ["scripts/b.py"]}, states, ids, entries), "a path the table does not hold"


def test_a_pass_is_reused_per_test_on_its_own_its_file_s_and_the_session_s_reads() -> None:
    """Amendment 5 (plan D32): a test stands on its own reads, its file's and the session's; a file is not collected only when
    every recorded test of it is reused."""
    ids = {"tests/tooling/test_a.py": "f1", "research/sources/p.html": "s1", "scripts/x.py": "x1", "scripts/y.py": "y1"}
    one = lambda p: {"opaque": [], "files": [p], "dirs": []}  # noqa: E731
    kept = {"v": deps.STORE_VERSION, "py": sys.version, "states": {"f:" + k: v for k, v in ids.items()}, "session": one("scripts/y.py"),
            "files": {"tests/tooling/test_a.py": {"nodeids": ["tests/tooling/test_a.py::t1", "tests/tooling/test_a.py::t2"], "entry": one("tests/tooling/test_a.py")}},
            "tests": {"tests/tooling/test_a.py::t1": one("research/sources/p.html"), "tests/tooling/test_a.py::t2": one("scripts/x.py")}}  # fmt: skip
    tests, whole = deps.reusable_tests(kept, ids, {}, {})
    assert tests == {"tests/tooling/test_a.py::t1", "tests/tooling/test_a.py::t2"} and whole == {"tests/tooling/test_a.py": 2}
    tests, whole = deps.reusable_tests(kept, {**ids, "research/sources/p.html": "s2"}, {}, {})
    assert tests == {"tests/tooling/test_a.py::t2"} and whole == {}, "a source page edited: only the test that read it runs"
    assert deps.reusable_tests(kept, {**ids, "tests/tooling/test_a.py": "f2"}, {}, {}) == (set(), {}), "the file edited: all of it"
    assert deps.reusable_tests(kept, {**ids, "scripts/y.py": "y2"}, {}, {}) == (set(), {}), "a session fixture's read: everything"
    assert deps.reusable_tests({**kept, "v": 2}, ids, {}, {}) == (set(), {}), "a pass kept in an older form"
    assert deps.reusable_tests({**kept, "py": "2.7"}, ids, {}, {}) == (set(), {}), "another interpreter"
    assert {"tests/tooling/conftest.py", "tests/conftest.py", "pyproject.toml", "tests/tooling/_test_deps.py"} <= deps.file_inputs("tests/tooling/test_a.py")
    assert "tests/tooling/ci/conftest.py" in deps.file_inputs("tests/tooling/ci/test_b.py"), "every conftest above the file"


def test_what_a_child_process_reads_is_known_or_the_file_always_runs(monkeypatch) -> None:  # noqa: ANN001
    site = str(deps.SITE)
    monkeypatch.delenv(deps.rules.SHIM_ENV, raising=False)  # no C recorder: a non-Python program is unknown
    rec = {"L7R_TEST_DEP_LOG": "/tmp/x.log", "PYTHONPATH": site}
    assert deps.opaque_child(("python3", ["python3", "x.py"], "/tmp", None), site) == "", "a Python child inheriting the recording"
    assert deps.opaque_child(("python3", ["python3", "x.py"], "/tmp", rec), site) == ""
    assert deps.opaque_child(("python3", ["python3", "-I", "x.py"], "/tmp", rec), site) == "python3", "isolated: no recording"
    fresh = {"PATH": "/bin"}
    values = {"L7R_TEST_DEP_LOG": "/tmp/x.log", "L7R_TEST_DEP_FILE": "tests/tooling/test_x.py", "L7R_TEST_DEP_ROOT": ROOT}
    assert deps.rules.adopt("python3", ["python3", "x.py"], fresh, values, site), "a fresh environment is adopted (FR-016)"
    assert site in fresh["PYTHONPATH"] and fresh["L7R_TEST_DEP_LOG"] == "/tmp/x.log", "...in place, before the child starts"
    assert not deps.rules.adopt("python3", ["python3", "-I", "x.py"], {"PATH": "/bin"}, values, site), "isolated ignores it"
    assert not deps.rules.adopt("python3", ["python3", "x.py"], {"PATH": "/bin"}, {}, site), "nothing to adopt with: not recording"
    assert deps.opaque_child(("python3", ["python3", "-E", "x.py"], "/tmp", {"PATH": "/bin"}), site) == "python3", "-E ignores it"
    assert deps.opaque_child(("git", ["git", "status"], ROOT, None), site) == "", "a read-only git question is asked again (FR-015)"
    assert deps.opaque_child(("git", ["git", "commit", "-m", "x"], ROOT, None), site) == "git", "a git command that writes"
    assert deps.opaque_child(("git", ["git", "cat-file", "--batch"], ROOT, None), site) == "git", "one reading its input"
    assert deps.opaque_child(("git", ["git", "log"], ROOT, {"GIT_DIR": "/tmp/x"}), site) == "git", "one steered elsewhere"
    assert deps.opaque_child(("git", ["git", "-C", "/tmp/fixture", "status"], ROOT, None), site) == "", "git -C a fixture"
    assert deps.opaque_child(("git", ["git", "init", "-q", "/tmp/fixture"], ROOT, None), site) == "", "git init names its dir"
    assert deps.opaque_child(("git", ["git", "clone", "-q", "/tmp/a", "/tmp/b"], ROOT, None), site) == "", "a clone from outside"
    assert deps.opaque_child(("git", ["git", "clone", ROOT, "/tmp/b"], "/tmp", None), site) == "git", "a clone of the repository"
    assert deps.opaque_child(("git", ["git", "worktree", "add", "/tmp/base", "HEAD"], ROOT, None), site) == "git", (
        "an outside path named does not make a command run in the repository known (the plan review)"
    )
    assert deps.opaque_child(("git", ["git", "-C", ROOT, "worktree", "list"], "/tmp", None), site) == "git", "git -C the repository"
    assert deps.opaque_child(("make", ["make", "quick"], ROOT, None), site) == "make", "no C recorder: unknown"
    monkeypatch.setenv(deps.rules.SHIM_ENV, "/x/l7r_file_log.so")
    monkeypatch.setenv("LD_PRELOAD", "/x/l7r_file_log.so")
    assert deps.rules.judge(("make", ["make", "quick"], ROOT, None), ROOT, site) == ("c", "make"), "the C recorder in it (D26)"
    given = {"PATH": "/bin"}
    monkeypatch.setenv("L7R_TEST_DEP_LOG", "/tmp/x.log")
    assert deps.rules.judge(("node", ["node", f"{ROOT}/x.js"], "/tmp", given), ROOT, site) == ("c", "node")
    assert given["LD_PRELOAD"].startswith("/x/l7r_file_log.so") and given["UV_USE_IO_URING"] == "0", "put into its own environment"
    assert deps.rules.judge(("git", ["git", "commit", "-m", "x"], ROOT, None), ROOT, site) == ("opaque", "git"), "git is never the C recorder's"
    assert deps.opaque_child(("git", ["git", "-C", ROOT, "rev-parse", "--git-common-dir"], ROOT, None), site) == "", "where, not what"
    assert deps.opaque_child(("git", ["git", "rev-parse", "HEAD"], ROOT, None), site) == "", "a revision is content, asked again"
    assert deps.opaque_child(("sleep", ["sleep", "1"], ROOT, None), site) == ""


def test_a_module_s_bytecode_stands_for_its_source() -> None:
    assert deps._rel_path(f"{ROOT}/scripts/record/__pycache__/record_cache.cpython-314.pyc") == "scripts/record/record_cache.py"
    assert deps._rel_path(f"{ROOT}/CLAUDE.md") == "CLAUDE.md"


def test_a_verdict_is_kept_by_its_passage_and_page_and_judged_afresh_when_either_changes(tmp_path, monkeypatch) -> None:  # noqa: ANN001
    spec = importlib.util.spec_from_file_location("qv_for_reuse", script("quote_verbatim"))
    assert spec and spec.loader
    qv = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(script("record_cache").parent))
    spec.loader.exec_module(qv)
    import record_cache

    monkeypatch.delenv("L7R_CACHE_OFF", raising=False)
    calls: list[tuple[str, str]] = []
    real = qv._verdict
    monkeypatch.setattr(qv, "_verdict", lambda a, b: calls.append((a, b)) or real(a, b))
    qv._VERDICTS = record_cache.ParseCache(tmp_path / "quote-verdicts-x.pickle")
    page = "<p>The well stood by the lane, two to a lane.</p>"
    first = qv.verdict("the well stood by the lane", page)
    assert qv.verdict("the well stood by the lane", page) == first and len(calls) == 1, "served again"
    qv.verdict("the well stood by the pond", page)
    qv.verdict("the well stood by the lane", page.replace("lane,", "road,"))
    assert len(calls) == 3, "a changed passage and a changed page are each judged afresh"
    qv._VERDICTS.save()
    qv._VERDICTS = record_cache.ParseCache(tmp_path / "quote-verdicts-x.pickle")
    qv.verdict("the well stood by the lane", page)
    assert len(calls) == 3, "kept on disk for the next run; a changed module is another file (ParseCache.at, tested there)"
    qv._VERDICTS = None


def test_a_git_question_is_asked_again_and_its_answer_compared(tmp_path) -> None:  # noqa: ANN001
    """FR-015, SC-012: the same question in another checkout of the same content gets the same answer; a changed file changes it."""
    import subprocess  # noqa: PLC0415

    rules = deps.rules

    def git(root, *a):  # noqa: ANN001, ANN202
        subprocess.run(["git", "-C", str(root), *a], check=True, capture_output=True)

    a = tmp_path / "a"
    git(tmp_path, "init", "-q", str(a))
    (a / "x.txt").write_text("one\n")
    git(a, "add", "x.txt")
    git(a, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x")
    b = tmp_path / "b"
    git(tmp_path, "clone", "-q", str(a), str(b))
    q = rules.git_question(["git", "ls-files", "-s", f"{a}/x.txt"], str(a), None, str(a))
    assert "{ROOT}" in q and str(a) not in q, "the checkout's path is written {ROOT}"
    assert rules.ask(q, str(a)) == rules.ask(q, str(b)), "another checkout of the same content answers the same"
    (b / "x.txt").write_text("two\n")
    git(b, "add", "x.txt")
    assert rules.ask(q, str(a)) != rules.ask(q, str(b)), "a changed file changes the answer: the test file runs"
    assert rules.git_question(["git", "commit", "-m", "x"], str(a), None, str(a)) == "", "a command that writes is no question"
    assert rules.ask('["{ROOT}/nowhere", "status"]', str(a)) == "error", "one that cannot be asked"
    kept = {"opaque": [], "files": [], "dirs": [], "git": {q: rules.ask(q, str(a))}}
    assert deps.entry_ok(kept, {}, {}, {}, {q: rules.ask(q, str(a))})
    assert not deps.entry_ok(kept, {}, {}, {}, {q: rules.ask(q, str(b))}), "the answer here differs"


def test_the_c_recorder_is_checked_against_python_s() -> None:
    """Plan D26: a file a Python child opened that the C recorder did not see is a gap; a cache read is not."""
    ok = {"t.py": {"py-file": {f"{ROOT}/a.py"}, "c-file": {f"{ROOT}/a.py", f"{ROOT}/b.sh"}, "c": {"bash"}}}
    assert deps.shim_gaps(ok) == {}
    gap = {"t.py": {"py-file": {f"{ROOT}/a.py", f"{ROOT}/.git/l7r-cache/x.tmp"}, "c-file": {f"{ROOT}/b.sh"}, "c": {"bash"}}}
    assert deps.shim_gaps(gap) == {"t.py": {f"{ROOT}/a.py"}}, "the cache read is not a gap; the missed module is"
    assert deps.shim_gaps({"t.py": {"py-file": {f"{ROOT}/a.py"}}}) == {}, "no C child: nothing to check"


def test_an_entry_kept_against_content_that_moved_is_dropped(tmp_path, monkeypatch) -> None:  # noqa: ANN001
    """Plan D32a: each read's content is kept once; when a run records a path whose content moved, an entry naming it that the
    run did not record again was kept against the old content - it is dropped, never judged against the new."""
    import json as _json  # noqa: PLC0415

    store = tmp_path / "store.json"
    monkeypatch.setattr(deps, "_store", lambda: store)
    ids = {"data/p.html": "old"}
    monkeypatch.setattr(deps, "_ids", lambda: (ids, {}))

    def run(name: str, ran: list[str], reads: dict) -> dict:
        d = tmp_path / name
        d.mkdir()
        (d / "worker-gw0.json").write_text(
            _json.dumps({"reads": reads, "failed": [], "ran": ran, "collected": {"tests/tooling/test_a.py": ["tests/tooling/test_a.py::t1", "tests/tooling/test_a.py::t2"]}})
        )
        deps._keep(d)
        return _json.loads(store.read_text())

    p = str(deps.ROOT / "data/p.html")
    s = str(deps.ROOT / "data/s.json")  # a session fixture's read, kept as a union across runs that never ran it
    ids["data/s.json"] = "s"
    kept = run(
        "one", ["tests/tooling/test_a.py::t1", "tests/tooling/test_a.py::t2"], {"tests/tooling/test_a.py::t1": {"file": [p]}, "tests/tooling/test_a.py::t2": {"file": [p]}, deps.SESSION: {"file": [s]}}
    )
    assert kept["states"]["f:data/p.html"] == "old" and len(kept["tests"]) == 2
    ids["data/p.html"] = "new"  # the page edited; only t1 runs again
    kept = run("two", ["tests/tooling/test_a.py::t1"], {"tests/tooling/test_a.py::t1": {"file": [p]}})
    assert kept["states"]["f:data/p.html"] == "new"
    assert set(kept["tests"]) == {"tests/tooling/test_a.py::t1"}, "t2 saw the old page: dropped, not kept against the new"
    assert kept["session"]["files"] == ["data/s.json"], "the earlier run's session read carried, as the relative path it was kept as"
