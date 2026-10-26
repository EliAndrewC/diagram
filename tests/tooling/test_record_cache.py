"""Feature 375 amendment 3, FR-020 (SC-013): what the record tooling reads, read once - and never an answer changed by it.

WHAT THESE PROVE. A parse is served again only for the same text under the same code: a changed file, a changed parsing
module and a changed module it imports each miss. A corrupt cache is an empty one, and `L7R_CACHE_OFF=1` turns it off. A
record parsed through the cache equals one parsed without it. A revision's files come from one batch, a missing one is None,
a path outside the batch's directories still reads. The claims are re-read when an engine module or a procedure document
changes, and served from the cache when nothing did.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

from tests._scripts import script


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, script(name))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = sys.modules[name.lstrip("_")] = mod
    spec.loader.exec_module(mod)
    return mod


rc = _load("_record_cache")
ru = _load("_record_units")
claims = _load("_claims")

PAGE = '<h2 id="rooms">Rooms</h2>\n<p class="intro">Why ask.</p>\n<p>A post was built.<sup class="fn" data-note="k"></sup></p>\n'
NOTES = '<li data-note="k">"A post." <a href="https://x"><code>kyakhta-src</code></a></li>\n'


def test_a_parse_is_kept_by_its_text_and_served_again(tmp_path: pathlib.Path, monkeypatch) -> None:
    monkeypatch.delenv("L7R_CACHE_OFF", raising=False)
    calls: list[str] = []
    c = rc.ParseCache(tmp_path / "c" / "record-parse-aaaa.pickle")
    assert c.get("k1", lambda: calls.append("1") or "one") == "one"
    c.save()
    again = rc.ParseCache(tmp_path / "c" / "record-parse-aaaa.pickle")
    assert again.get("k1", lambda: calls.append("2") or "two") == "one" and calls == ["1"], "served from disk"
    assert again.get("k2", lambda: "new") == "new", "a new text is a miss"


def test_another_version_of_the_code_is_another_file_and_the_old_one_goes(tmp_path: pathlib.Path, monkeypatch) -> None:
    monkeypatch.delenv("L7R_CACHE_OFF", raising=False)
    old = rc.ParseCache(tmp_path / "record-parse-aaaa.pickle")
    old.get("k", lambda: "old parse")
    old.save()
    new = rc.ParseCache(tmp_path / "record-parse-bbbb.pickle")
    assert new.get("k", lambda: "new parse") == "new parse", "a parse made by other code is never served"
    new.save()
    assert not (tmp_path / "record-parse-aaaa.pickle").exists()


def test_a_corrupt_cache_is_empty_and_the_switch_turns_it_off(tmp_path: pathlib.Path, monkeypatch) -> None:
    monkeypatch.delenv("L7R_CACHE_OFF", raising=False)
    f = tmp_path / "record-parse-cccc.pickle"
    f.write_bytes(b"not a pickle")
    assert rc.ParseCache(f).get("k", lambda: "made") == "made"
    monkeypatch.setenv("L7R_CACHE_OFF", "1")
    off = rc.ParseCache(tmp_path / "record-parse-dddd.pickle")
    off.get("k", lambda: "x")
    off.save()
    assert not (tmp_path / "record-parse-dddd.pickle").exists()


def test_the_code_key_follows_the_modules_it_imports(tmp_path: pathlib.Path) -> None:
    """The spec review's item: a change to a helper the parser imports must miss, not only a change to the parser."""
    (tmp_path / "parser.py").write_text("import helper\nimport json\n", encoding="utf-8")
    (tmp_path / "helper.py").write_text("from deeper import x\n", encoding="utf-8")
    (tmp_path / "deeper.py").write_text("x = 1\n", encoding="utf-8")
    before = rc.code_sha_of(tmp_path, tmp_path / "parser.py")
    assert {p.name for p in rc.imported_files(tmp_path / "parser.py", tmp_path)} == {"parser.py", "helper.py", "deeper.py"}
    (tmp_path / "deeper.py").write_text("x = 2\n", encoding="utf-8")
    assert rc.code_sha_of(tmp_path, tmp_path / "parser.py") != before, "two imports away, still in the key"


def test_a_record_parsed_through_the_cache_is_the_record_parsed_without_it(tmp_path: pathlib.Path, monkeypatch) -> None:
    monkeypatch.delenv("L7R_CACHE_OFF", raising=False)
    files = {"0094-rooms.html": PAGE, "0094-rooms.notes.html": NOTES}
    plain = ru.Record.of(files, {"kyakhta-src": "<p>A write-up.</p>"})
    cache = rc.ParseCache(tmp_path / "record-parse-eeee.pickle")
    first = ru.Record.of(files, {"kyakhta-src": "<p>A write-up.</p>"}, cache)
    cache.save()
    warm = ru.Record.of(files, {"kyakhta-src": "<p>A write-up.</p>"}, rc.ParseCache(tmp_path / "record-parse-eeee.pickle"))
    assert plain == first == warm
    changed = ru.Record.of({**files, "0094-rooms.html": PAGE.replace("A post", "Two posts")}, {}, rc.ParseCache(tmp_path / "record-parse-eeee.pickle"))
    assert changed.pages["0094"].blocks[1].words.startswith("Two posts"), "a changed file is parsed afresh"


def _git(d: pathlib.Path, *a: str) -> str:
    return subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True, text=True).stdout


def test_a_revision_is_read_in_one_batch_and_any_other_path_still_reads(tmp_path: pathlib.Path) -> None:
    d = tmp_path / "r"
    (d / "a" / "b").mkdir(parents=True)
    (d / "a" / "one.py").write_text("one\n", encoding="utf-8")
    (d / "a" / "b" / "two.md").write_text("two\n", encoding="utf-8")
    (d / "elsewhere.txt").write_text("far\n", encoding="utf-8")
    _git(d.parent, "init", "-q", str(d))
    _git(d, "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
    _git(d, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "c")
    read = rc.RevReader(d, "HEAD", ("a",))
    assert read("a/one.py") == "one\n" and read("a/b/two.md") == "two\n" and read("a/missing.py") is None
    assert read.names("a") == ["a/one.py"] and read.names("a/b") == ["a/b/two.md"]
    assert read("elsewhere.txt") == "far\n" and read("nowhere.txt") is None
    assert rc.cat_blobs(d, ["HEAD:a/one.py", "HEAD:gone"]) == ["one\n", ""]


class _Engine:
    """A stand-in claim reader: counts the times the engine is read."""

    PROCEDURES = {"docs/buildings.md": None}
    __file__ = __file__  # the reader's source, which names the per-module cache (feature 375 amendment 8)

    def __init__(self) -> None:
        self.reads = 0
        self.memos: list[object] = []

    def all_units(self, skill: pathlib.Path, memo: object = None):  # noqa: ANN201
        self.reads += 1
        self.memos.append(memo)
        return iter([("unit", [])])


def test_the_claims_are_kept_until_an_engine_module_or_a_procedure_changes(tmp_path: pathlib.Path, monkeypatch) -> None:
    monkeypatch.delenv("L7R_CACHE_OFF", raising=False)
    skill = tmp_path / "s"
    (skill / "l7r" / "diagram").mkdir(parents=True)
    (skill / "docs").mkdir()
    mod = skill / "l7r" / "diagram" / "m.py"
    mod.write_text("A = 1\n", encoding="utf-8")
    doc = skill / "docs" / "buildings.md"
    doc.write_text("Research: x\n", encoding="utf-8")
    _git(tmp_path, "init", "-q", str(skill))
    eng = _Engine()
    monkeypatch.setattr(claims, "engine", lambda _root: eng)
    assert claims.units_of(skill) == ["unit"] and eng.reads == 1
    assert claims.units_of(skill) == ["unit"] and eng.reads == 1, "nothing changed: served from the cache"
    mod.write_text("A = 2\n", encoding="utf-8")
    claims.units_of(skill)
    assert eng.reads == 2, "an engine module changed"
    doc.write_text("Research: y\n", encoding="utf-8")
    claims.units_of(skill)
    assert eng.reads == 3, "a procedure document changed"
    assert len(list((skill / ".git" / rc.CACHE_DIR).glob("claims-*.pickle"))) == 1, "only the newest key is kept"
    assert all(m is not None for m in eng.memos), "every miss is handed the per-module memo (amendment 8, FR-035)"


def test_claims_owed_reads_the_gates_form_problems_from_the_kept_parse(tmp_path: pathlib.Path, monkeypatch) -> None:
    """Feature 374 batch 4: a GUESS claim naming the findings page failed the gate's coverage test, which `make quick` never
    runs; `claims-owed` now prints the same problems, from the parse it already keeps."""
    monkeypatch.delenv("L7R_CACHE_OFF", raising=False)
    skill = tmp_path / "s"
    (skill / "l7r" / "diagram").mkdir(parents=True)
    (skill / "research" / "questions").mkdir(parents=True)
    (skill / "research" / "questions" / "0001-x.html").write_text("x", encoding="utf-8")
    (skill / "l7r" / "diagram" / "m.py").write_text("A = 1\n", encoding="utf-8")
    _git(tmp_path, "init", "-q", str(skill))

    class _Coverage(_Engine):
        def coverage(self, pairs, questions):  # noqa: ANN001, ANN201
            return [f"{u}: {e}" for u, errors in pairs for e in errors] + sorted(questions)

        def all_units(self, skill: pathlib.Path, memo: object = None):  # noqa: ANN201
            self.reads += 1
            return iter([("unit", ["GUESS names the drawing page"])])

    eng = _Coverage()
    monkeypatch.setattr(claims, "engine", lambda _root: eng)
    assert claims.form_problems(skill) == ["unit: GUESS names the drawing page", "0001-x.html"]
    assert claims.units_of(skill) == ["unit"] and eng.reads == 1, "the form check and the claims share one parse"


def test_an_extractor_s_docstring_or_comment_keeps_its_code_sha(tmp_path: pathlib.Path) -> None:
    """Feature 426's audit: a parse cache's key is the extractor's code by what runs."""
    p = tmp_path / "parser.py"
    p.write_text('def parse(x):\n    """Doc."""\n    return x\n', encoding="utf-8")
    before = rc.code_sha(p)
    p.write_text('def parse(x):\n    """Doc, reworded."""\n    return x  # c\n', encoding="utf-8")
    assert rc.code_sha(p) == before
    p.write_text('def parse(x):\n    return x + 1\n', encoding="utf-8")
    assert rc.code_sha(p) != before
