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


def test_a_kept_pass_is_reused_only_while_everything_it_read_is_unchanged() -> None:
    ids = {"scripts/a.py": "1", "tests/tooling/test_a.py": "2"}
    entries = {"scripts": ["a.py"], "": ["scripts", "tests"]}
    kept = {"v": deps.STORE_VERSION, "py": sys.version, "opaque": [], "files": {"scripts/a.py": "1"}, "dirs": {"scripts": '["a.py"]'}}
    assert deps.reusable(kept, ids, entries)
    assert not deps.reusable(kept, {**ids, "scripts/a.py": "9"}, entries), "a file it read changed"
    assert not deps.reusable(kept, ids, {**entries, "scripts": ["a.py", "b.py"]}), "a directory it listed gained an entry"
    assert not deps.reusable({**kept, "opaque": ["git"]}, ids, entries), "it ran git in the repository"
    assert not deps.reusable({**kept, "py": "2.7"}, ids, entries), "another interpreter"
    assert not deps.reusable({**kept, "v": 1}, ids, entries), "a pass kept in an older form"
    assert not deps.reusable({**kept, "files": {"x/.gencache/k": "ignored"}}, ids, entries), "it read a file git ignores"


def test_what_a_child_process_reads_is_known_or_the_file_always_runs() -> None:
    site = str(deps.SITE)
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
    assert deps.opaque_child(("make", ["make", "quick"], ROOT, None), site) == "make"
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
    kept = {"v": deps.STORE_VERSION, "py": sys.version, "opaque": [], "files": {}, "dirs": {}, "git": {q: rules.ask(q, str(a))}}
    assert deps.reusable(kept, {}, {}, {q: rules.ask(q, str(a))})
    assert not deps.reusable(kept, {}, {}, {q: rules.ask(q, str(b))}), "the answer here differs"
