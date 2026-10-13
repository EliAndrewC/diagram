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
    kept = {"py": sys.version, "opaque": [], "files": {"scripts/a.py": "1"}, "dirs": {"scripts": '["a.py"]'}}
    assert deps.reusable(kept, ids, entries)
    assert not deps.reusable(kept, {**ids, "scripts/a.py": "9"}, entries), "a file it read changed"
    assert not deps.reusable(kept, ids, {**entries, "scripts": ["a.py", "b.py"]}), "a directory it listed gained an entry"
    assert not deps.reusable({**kept, "opaque": ["git"]}, ids, entries), "it ran git in the repository"
    assert not deps.reusable({**kept, "py": "2.7"}, ids, entries), "another interpreter"
    assert not deps.reusable({**kept, "files": {"x/.gencache/k": "ignored"}}, ids, entries), "it read a file git ignores"


def test_what_a_child_process_reads_is_known_or_the_file_always_runs() -> None:
    site = str(deps.SITE)
    rec = {"L7R_TEST_DEP_LOG": "/tmp/x.log", "PYTHONPATH": site}
    assert deps.opaque_child(("python3", ["python3", "x.py"], "/tmp", None), site) == "", "a Python child inheriting the recording"
    assert deps.opaque_child(("python3", ["python3", "x.py"], "/tmp", rec), site) == ""
    assert deps.opaque_child(("python3", ["python3", "-I", "x.py"], "/tmp", rec), site) == "python3", "isolated: no recording"
    assert deps.opaque_child(("python3", ["python3", "x.py"], "/tmp", {"PATH": "/bin"}), site) == "python3", "recording dropped"
    assert deps.opaque_child(("git", ["git", "status"], ROOT, None), site) == "git", "git in the repository"
    assert deps.opaque_child(("git", ["git", "-C", "/tmp/fixture", "status"], ROOT, None), site) == "", "git -C a fixture"
    assert deps.opaque_child(("git", ["git", "init", "-q", "/tmp/fixture"], ROOT, None), site) == "", "git on paths it names"
    assert deps.opaque_child(("git", ["git", "-C", ROOT, "log"], "/tmp", None), site) == "git", "git -C the repository"
    assert deps.opaque_child(("make", ["make", "quick"], ROOT, None), site) == "make"


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
