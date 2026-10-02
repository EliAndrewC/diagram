"""`scripts/_downloads.py` - the canonical download list, the GM's marked copy, ingest, sync and add (feature 313).

WHAT THESE PROVE. The import keeps both sources byte for byte (SC-001). A copy driven through sync, a GM tick, a GM text
edit, a session edit and ingest records the marks, holds the text edit for an instruction, keeps the session's edit, and
sync is refused before the ingest and allowed after (SC-002). Two adds from two clones take distinct numbers, and the push
check refuses each violation (SC-003). Contradictory marks, an unknown id, a first sync over a changed file and an ingest
before any sync are each refused, naming what to do. No test touches the GM's real copy: the copy is a file in tmp.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


dl = _load("_downloads")
ops = _load("_archive_ops")

GM = """# Sources to download - the working list

Intro the GM reads.

## Part 1 - the ones worth fetching

### 1. A work

- **[Direct PDF](https://example.org/a.pdf)**
- Blocked by: 403.

### 2. Another work

- **[Page](https://example.org/b)**
- Blocked by: paywalled.

## Part 4 - appended

### 3. A third work

- **[Page](https://example.org/c)**
- Blocked by: TLS.
"""
HR = """# High-risk sources: download first

Why these come first.

## Tier 1 - a footnote rests on it (1)

### H1. A cited work (`alpha`)

- **[The cited page](https://example.org/alpha)**
- Blocked by: 403.
"""


def _git(root: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout


def _clone(root: pathlib.Path) -> pathlib.Path:
    (root / dl.CANON).parent.mkdir(parents=True, exist_ok=True)
    _git(root.parent, "init", "-q", "-b", "main", str(root))
    _git(root, "config", "user.email", "t@example.org")
    _git(root, "config", "user.name", "t")
    return root


def _commit(root: pathlib.Path, msg: str = "x") -> None:
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", msg)


def _world(tmp: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    """A clone with the list imported from GM and HR and committed, and the GM's copy (still the old file)."""
    root = _clone(tmp / "mirror" / ".clones" / "a")
    (root / dl.CANON).write_text(dl.import_list(GM, HR), encoding="utf-8")
    dl.save_state(root, {"imported": {"sha256": dl.sha(GM), "date": "2026-10-02"}})
    _commit(root, "import")
    copy = tmp / "academic-sources" / "TO-DOWNLOAD.md"
    copy.parent.mkdir()
    copy.write_text(GM, encoding="utf-8")
    return root, copy


def _tick(copy: pathlib.Path, eid: str, **marks: object) -> None:
    blocks = dl.parse(copy.read_text(encoding="utf-8"))
    e = dl.by_id(blocks)[eid]
    e.marks = dl.Marks(**marks)  # type: ignore[arg-type]
    copy.write_text(dl.render(blocks), encoding="utf-8")


def _edit(path: pathlib.Path, eid: str, line: str) -> None:
    blocks = dl.parse(path.read_text(encoding="utf-8"))
    dl.by_id(blocks)[eid].body.insert(-1, line)
    path.write_text(dl.render(blocks), encoding="utf-8")


def test_the_import_keeps_both_sources_byte_for_byte_and_gives_every_entry_its_marks() -> None:
    canon = dl.import_list(GM, HR)
    assert dl.unimport(canon) == (GM, HR)
    es = dl.entries(dl.parse(canon))
    assert [e.id for e in es] == ["H1", "1", "2", "3"], "the high-risk section first, then the GM's file in order"
    assert es[0].marks == dl.Marks() and es[0].recorded is None, "every box starts unticked where the GM's file records nothing"
    assert all(e.marks is not None for e in es), "every entry carries its mark lines"
    assert dl.render(dl.parse(canon)) == canon


def test_the_status_table_ticks_only_what_the_gms_file_records() -> None:
    blocks = dl.by_id(dl.parse(dl.import_list(GM, HR)))
    assert blocks["1"].marks == dl.Marks(downloaded=True) and blocks["1"].recorded and "2026-09-13" in blocks["1"].recorded
    assert blocks["3"].marks == dl.Marks(downloaded=True), "entry 3's status-table row says a file was saved"
    assert set(dl.STATUS_2026_09_13) == {str(i) for i in range(1, 17)}, "the table settled Part 1's sixteen and nothing else"
    assert {k for k, m in dl.STATUS_2026_09_13.items() if m.not_found} == {"7", "9", "10", "11"}


def test_the_committed_list_re_derives_the_gms_file_the_import_read() -> None:
    """SC-001 on the repository itself: the list as first committed, unimported, has the fingerprint the import recorded."""
    first = subprocess.run(["git", "-C", str(REPO), "log", "--diff-filter=A", "--format=%H", "--", dl.CANON], capture_output=True, text=True).stdout.split()
    if not first:
        pytest.skip("the list is not committed in this checkout")
    text = subprocess.run(["git", "-C", str(REPO), "show", f"{first[-1]}:{dl.CANON}"], capture_output=True, text=True, check=True).stdout
    state = json.loads(subprocess.run(["git", "-C", str(REPO), "show", f"{first[-1]}:{dl.STATE}"], capture_output=True, text=True, check=True).stdout)
    gm, hr = dl.unimport(text)
    assert dl.sha(gm) == state["imported"]["sha256"]
    assert hr.startswith("# High-risk sources") and "### H1. " in hr


def test_a_round_of_marking_ingest_and_sync(tmp_path: pathlib.Path) -> None:
    """SC-002: sync, tick, GM text edit, session edit, ingest - and sync refused before the ingest, allowed after."""
    root, copy = _world(tmp_path)
    dl.sync(root, copy, "2026-10-03")
    _commit(root, "synced")
    assert copy.read_text(encoding="utf-8") == (root / dl.CANON).read_text(encoding="utf-8")
    _tick(copy, "2", partial=True, paywalled=True)
    _tick(copy, "H1", downloaded=True, elsewhere=True, where="a library", saved="alpha.pdf")
    _edit(copy, "3", "- The GM's note: try the archive.")
    _edit(root / dl.CANON, "1", "- A pointer a session fixed.")
    _commit(root, "session edit")
    with pytest.raises(dl.Refusal, match="not yet ingested"):
        dl.sync(root, copy)
    out = dl.ingest(root, copy, set(), set(), "2026-10-04")
    assert sorted(out.recorded) == ["2", "H1"] and set(out.pending) == {"3"} and out.saved == {"H1": "alpha.pdf"}
    canon = dl.by_id(dl.parse((root / dl.CANON).read_text(encoding="utf-8")))
    assert canon["2"].marks == dl.Marks(partial=True, paywalled=True) and canon["2"].recorded == "- Marks recorded 2026-10-04"
    assert "- A pointer a session fixed." in canon["1"].body, "the session's edit is kept"
    assert "- The GM's note: try the archive." not in canon["3"].body, "a GM text edit waits for KEEP= or DROP="
    assert "ingested" not in dl.load_state(root), "nothing pending is the condition for the copy counting as ingested"
    out = dl.ingest(root, copy, {"3"}, set(), "2026-10-04")
    assert out.kept == ["3"] and out.clean()
    assert "- The GM's note: try the archive." in dl.by_id(dl.parse((root / dl.CANON).read_text(encoding="utf-8")))["3"].body
    _commit(root, "ingested")
    dl.sync(root, copy, "2026-10-05")
    assert copy.read_text(encoding="utf-8") == (root / dl.CANON).read_text(encoding="utf-8")


def test_a_dropped_edit_is_discarded_and_a_conflict_is_named(tmp_path: pathlib.Path) -> None:
    root, copy = _world(tmp_path)
    dl.sync(root, copy)
    _commit(root, "synced")
    _edit(copy, "1", "- the GM's line")
    _edit(copy, "2", "- the GM's other line")
    _edit(root / dl.CANON, "1", "- the session's line")
    out = dl.ingest(root, copy, set(), {"2"}, "2026-10-04")
    assert out.dropped == ["2"] and out.pending["1"].startswith("CONFLICT")


def test_contradictory_marks_and_an_unknown_id_are_named_not_recorded(tmp_path: pathlib.Path) -> None:
    root, copy = _world(tmp_path)
    dl.sync(root, copy)
    _commit(root, "synced")
    _tick(copy, "1", elsewhere=True, where="somewhere")
    _tick(copy, "2", not_found=True, paywalled=True)
    copy.write_text(copy.read_text(encoding="utf-8") + "\n### 99. One the GM added\n\n- x\n", encoding="utf-8")
    out = dl.ingest(root, copy, set(), set())
    assert set(out.refused) == {"1", "2"} and "without downloaded or partial" in out.refused["1"]
    assert out.unknown == ["99"] and not out.recorded and not out.clean()


def test_ingest_before_any_sync_is_refused(tmp_path: pathlib.Path) -> None:
    root, copy = _world(tmp_path)
    with pytest.raises(dl.Refusal, match="make downloads-sync"):
        dl.ingest(root, copy, set(), set())


def test_the_first_sync_refuses_a_file_changed_since_the_import(tmp_path: pathlib.Path) -> None:
    root, copy = _world(tmp_path)
    copy.write_text(GM + "\n### 4. Appended by hand after the import\n\n- x\n", encoding="utf-8")
    with pytest.raises(dl.Refusal, match=r"changed since the import.*4 \(not in the canonical list") as e:
        dl.sync(root, copy)
    assert "make download-add" in str(e.value)


def test_sync_refuses_an_uncommitted_list(tmp_path: pathlib.Path) -> None:
    root, copy = _world(tmp_path)
    _edit(root / dl.CANON, "1", "- not committed")
    with pytest.raises(dl.Refusal, match="uncommitted"):
        dl.sync(root, copy)


def test_a_missing_copy_is_simply_written(tmp_path: pathlib.Path) -> None:
    root, copy = _world(tmp_path)
    copy.unlink()
    dl.sync(root, copy)
    assert copy.is_file()


DRAFT = """### NEW. A paper only the GM can reach

- **[Publisher page](https://example.org/p)**
- Fallback: [Google: a paper](https://www.google.com/search?q=a+paper)
- **Rests on it:** "Wells" (`research/questions/0001-wells.html`).
- Blocked by: paywalled.
"""


def test_two_adds_from_two_clones_take_distinct_numbers_at_the_end(tmp_path: pathlib.Path) -> None:
    a, _copy = _world(tmp_path)
    b = tmp_path / "mirror" / ".clones" / "b"
    _git(tmp_path, "clone", "-q", str(a), str(b))
    for root in (a, b):
        q = root / dl.SKILL / "research" / "questions"
        q.mkdir(parents=True, exist_ok=True)
        (q / "0001-wells.html").write_text("<h2>Wells</h2>", encoding="utf-8")
    assert dl.add(a, DRAFT) == ["4"]
    assert dl.add(b, DRAFT + "\n" + DRAFT) == ["5", "6"], "the other clone's unpushed 4 is seen through the lock's scan"
    assert dl.entries(dl.parse((b / dl.CANON).read_text(encoding="utf-8")))[-1].id == "6"
    ledger = tmp_path / "mirror" / ".specify" / dl.LEDGER
    assert [json.loads(line)["n"] for line in ledger.read_text(encoding="utf-8").splitlines()] == [4, 5, 6]


@pytest.mark.parametrize(
    ("draft", "missing"),
    [
        ("### 7. Numbered by hand\n", "headed `### NEW."),
        (DRAFT.replace("- Fallback", "- Elsewhere"), "Fallback"),
        (DRAFT.replace("- Blocked by: paywalled.", ""), "Blocked by"),
        (DRAFT.replace("research/questions/0001-wells.html", "fields.html"), "a pointer in Rests on it"),
        (DRAFT.replace("0001-wells", "0002-ponds"), "0002-ponds.html - none such"),
        ("", "no `### NEW."),
    ],
)
def test_a_draft_lacking_a_part_is_refused_naming_it(tmp_path: pathlib.Path, draft: str, missing: str) -> None:
    record = tmp_path / "research"
    (record / "questions").mkdir(parents=True)
    (record / "questions" / "0001-wells.html").write_text("x", encoding="utf-8")
    with pytest.raises(dl.Refusal, match=missing.replace("(", r"\(").replace(".", r"\.").replace("`", "`")):
        dl.drafts(draft, record)


def _list(*ids: str, marks: bool = True) -> str:
    out = ["# T", ""]
    for i in ids:
        out += [f"### {i}. Work {i}", *(["", *dl.Marks().lines()] if marks else []), "", f"- body {i}", ""]
    return "\n".join(out)


@pytest.mark.parametrize(
    ("old", "new", "said"),
    [
        (_list("H1", "1", "2"), _list("H1", "1"), "are gone"),
        (_list("H1", "1", "2"), _list("H1", "2", "1"), "reordered"),
        (_list("H1", "1", "3"), _list("H1", "1", "2", "3"), "not appended at the end"),
        (_list("H1", "1", "3"), _list("H1", "1", "3", "2"), "not appended at the end"),
        (_list("H1", "1"), _list("H1", "H2", "1"), "not appended at the end"),
        (_list("H1", "1"), _list("H1", "1", "1"), "appears twice"),
        (_list("H1", "1"), _list("H1", "1") + "### 2. No marks\n\n- b\n", "no mark lines"),
    ],
)
def test_the_push_check_refuses_each_violation(old: str, new: str, said: str) -> None:
    assert any(said in p for p in dl.problems(old, new)), dl.problems(old, new)


def test_the_push_check_passes_an_append_and_a_list_main_lacks(tmp_path: pathlib.Path) -> None:
    assert dl.problems(_list("H1", "1"), _list("H1", "1", "2")) == []
    assert dl.problems(None, _list("H1", "1")) == []
    root, _copy = _world(tmp_path)
    assert dl.check(root, "HEAD") == [] and dl.check(tmp_path, "HEAD") == []
    dl.selftest()


def test_a_saved_as_name_matches_its_file_when_the_file_is_there(tmp_path: pathlib.Path) -> None:
    (tmp_path / "alpha.pdf").write_bytes(b"%PDF")
    assert dl.inbox_matches({"H1": "alpha.pdf", "2": "missing.pdf", "3": "../escape.pdf", "4": ""}, tmp_path) == {"H1": "alpha.pdf"}


def test_marks_parse_with_either_case_and_spacing() -> None:
    lines = ["- Mark: [X] downloaded | [ x ] partial (abstract or excerpt) | [] paywalled | [ ] not found", "- [x] Found elsewhere (only with downloaded or partial) - where: a library", "- Saved as (optional, the file's name): f.pdf"]
    assert dl.parse_marks(lines) == dl.Marks(downloaded=True, partial=True, elsewhere=True, where="a library", saved="f.pdf")
    assert dl.parse_marks(lines[:2]) is None and dl.parse_marks(["x", *lines[1:]]) is None


def test_the_inbox_resolves_an_entry_id_to_that_entrys_keys(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    at = sys.modules.get("_access_tags") or _load("_access_tags")
    world = at.World(["open"], {}, {"alpha": []}, {}, {}, ["download:3"], {"download:H1": {"alpha"}, "download:3": set()})
    monkeypatch.setattr(at, "load", lambda _root: world)
    match, downloads = ops.resolve_matches(tmp_path, ["a.pdf=#H1", "b.pdf=3", "c.pdf=beta,gamma", "junk"])
    assert match == {"a.pdf": ["alpha"], "b.pdf": [], "c.pdf": ["beta", "gamma"]} and downloads == {"a.pdf": "H1", "b.pdf": "3"}
    with pytest.raises(SystemExit, match="no download-list entry 9"):
        ops.resolve_matches(tmp_path, ["d.pdf=#9"])
