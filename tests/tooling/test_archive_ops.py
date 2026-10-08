"""`scripts/record/archive_ops.py` - the inbox, every page read, the lookup and the relayout (feature 309, Amendment 1).

WHAT THESE PROVE. The GM's download directory is processed as an inbox: every entry but the GM's two lists is archived,
the push confirmed, and only then deleted - a failed push deletes nothing, and the table still finds a copy whose file
is gone. The pages a session read are archived once each (a page read again is not captured again), the consulted
backfill takes the page cache's own URLs and the ledger's, and the lookup answers by URL, key and words in the text,
saying so when nothing is held. The relayout moves the first, unsharded captures and rows into the sharded layout. The
ledger's writers hand their URLs to the archiver, never in a test. No test fetches: the remote is a bare repository on disk.
"""

from __future__ import annotations

import importlib.util
import io
import json
import pathlib
import subprocess
import sys

import pytest

from l7r.diagram.interactive.record import archive as rec
from tests import _flat_record as fr
from tests._scripts import script

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, script(name))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = sys.modules[name.lstrip("_")] = mod  # the old name and the one a sibling imports it by (2026-10-08)
    spec.loader.exec_module(mod)
    return mod


ar = _load("_archive")
ops = _load("_archive_ops")
src = ar.src


def _world(tmp: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> tuple[pathlib.Path, ar.Archive, pathlib.Path]:
    root = tmp / "clone"
    (root / ar.MANIFEST).mkdir(parents=True)
    fr.write(root / ar.MANIFEST.parent)
    (root / ar.MANIFEST / rec.GM_COPIES).write_text(json.dumps({"_about": "x", "files": {"a.pdf": {"keys": ["alpha"]}}}), encoding="utf-8")
    bare = tmp / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True)
    inbox = tmp / "academic-sources"
    inbox.mkdir()
    monkeypatch.setattr(ar, "GM_DIR", inbox)
    return root, ar.Archive(tmp / "home", remote=str(bare)), inbox


def test_the_inbox_is_archived_confirmed_and_emptied_but_the_gms_lists_stay(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, store, inbox = _world(tmp_path, monkeypatch)
    (inbox / "a.pdf").write_bytes(b"%PDF the GM's copy")
    (inbox / "new.txt").write_text("a paper nothing cites yet", encoding="utf-8")
    (inbox / "page_files").mkdir()
    (inbox / "page_files" / "i.png").write_bytes(b"png")
    for name in ops.GM_LISTS:
        (inbox / name).write_text("the GM's list", encoding="utf-8")
    placed, waiting = ops.process_inbox(root, store, inbox)
    assert placed == {"a.pdf": "gm-copies/a.pdf"} and waiting == ["new.txt", "page_files"], "a new download waits for its keys"
    assert sorted(p.name for p in inbox.iterdir()) == sorted([*ops.GM_LISTS, "new.txt", "page_files"])
    placed, waiting = ops.process_inbox(root, store, inbox, match={"new.txt": [], "page_files": ["beta"]})
    assert placed == {"new.txt": "gm-copies/new.txt", "page_files": "gm-copies/page_files"} and waiting == []
    assert sorted(p.name for p in inbox.iterdir()) == sorted(ops.GM_LISTS)
    table = ar.gm_table(root)
    assert table["a.pdf"] == {"keys": ["alpha"], "archived": "gm-copies/a.pdf"}
    assert table["new.txt"]["keys"] == [] and table["new.txt"]["archived"] == "gm-copies/new.txt"
    assert table["page_files"]["keys"] == ["beta"]
    assert all(ops.on_github(store, p) for p in ("gm-copies/a.pdf", "gm-copies/new.txt", "gm-copies/page_files"))
    assert ar.place_gm(store, "a.pdf", table["a.pdf"]) == "gm-copies/a.pdf", "found in the archive after its file is gone"


def test_a_failed_push_deletes_nothing_from_the_inbox(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, store, inbox = _world(tmp_path, monkeypatch)
    with store.locked():
        store.ensure()
    store.git("remote", "set-url", "origin", str(tmp_path / "nowhere.git"))
    (inbox / "a.pdf").write_bytes(b"%PDF x")
    with pytest.raises(RuntimeError, match="nothing was deleted"):
        ops.process_inbox(root, store, inbox)
    assert (inbox / "a.pdf").is_file()
    assert ops.process_inbox(root, store, tmp_path / "no-inbox") == ({}, [])


def test_a_page_read_again_is_not_captured_again(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, _store, _inbox = _world(tmp_path, monkeypatch)
    ar.write_row(root, "https://a.org/p", {"url": "https://a.org/p", "outcome": "archived"})
    assert ops.unarchived(root, ["https://www.a.org/p/", "https://b.org/q#x", "https://b.org/q", "not a url"]) == ["https://b.org/q"]


def test_the_consulted_backfill_takes_the_caches_urls_and_the_ledgers(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, _store, _inbox = _world(tmp_path, monkeypatch)
    home = src.home(root)
    src.put(home, "https://Cached.org/Page", "text")
    src.append(home, [src.line(src.context(root), "ledger-only.org/x", "rejected: not about it"), src.line(src.context(root), "cached.org/page", "pending")])
    ar.write_row(root, "https://done.org/y", {"url": "https://done.org/y", "outcome": "archived"})
    src.append(home, [src.line(src.context(root), "done.org/y", "cited:k")])
    assert ops.consulted_urls(root) == ["https://Cached.org/Page", "https://ledger-only.org/x"]


def test_the_lookup_answers_by_url_key_and_words_and_says_when_nothing_is_held(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, store, inbox = _world(tmp_path, monkeypatch)
    (inbox / "a.pdf").write_bytes(b"%PDF x")
    assert ops.process_inbox(root, store, inbox)[0] == {"a.pdf": "gm-copies/a.pdf"}
    with store.locked():
        rel = store.put(f"{ar.capture_base('https://a')}/20261002T000000Z", {"text.txt": b"Forty to sixty MATS of straw."}, "a capture")
    ar.write_row(root, "https://a", {"url": "https://a", "outcome": "archived", "path": rel, "keys": ["alpha"], "gm_copies": ["gm-copies/a.pdf"]})
    out = io.StringIO()
    assert ops.find(root, store, url="https://www.a/", out=out) == 0 and f"local: {store.dir / rel}" in out.getvalue()
    out = io.StringIO()
    assert ops.find(root, store, key="alpha", out=out) == 0
    assert "the GM's copy:" in out.getvalue() and "the GM's copy of alpha" in out.getvalue()
    out = io.StringIO()
    assert ops.find(root, store, terms="sixty mats|straw", out=out) == 0 and "url: https://a" in out.getvalue()
    out = io.StringIO()
    assert ops.find(root, store, terms="sixty mats|rice", out=out) == 1 and "search the web" in out.getvalue()


def test_the_relayout_moves_the_first_captures_and_rows_into_shards(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, store, _inbox = _world(tmp_path, monkeypatch)
    uid = rec.url_id("https://a")
    with store.locked():
        store.ensure()
        store.put(f"alpha/{uid}/20261002T000000Z", {"text.txt": b"t"}, "old layout")
        store.put("alpha/gm-copy", {"a.pdf": b"%PDF"}, "old gm copy")
    flat = root / ar.MANIFEST / f"{uid}.json"
    old = {"url": "https://a", "outcome": "archived", "path": f"alpha/{uid}/20261002T000000Z", "first": f"alpha/{uid}/20261002T000000Z", "gm_copies": ["alpha/gm-copy/a.pdf"]}
    flat.write_text(json.dumps(old), encoding="utf-8")
    assert ops.relayout(root, store) == 1
    row = ar.read_row(root, "https://a")
    assert not flat.exists() and row["path"] == f"{uid[:2]}/{uid}/20261002T000000Z" == row["first"]
    assert row["gm_copies"] == ["gm-copies/a.pdf"] and ar.gm_table(root)["a.pdf"]["archived"] == "gm-copies/a.pdf"
    assert (store.dir / row["path"] / "text.txt").is_file() and (store.dir / "gm-copies" / "a.pdf").is_file()
    assert not (store.dir / "alpha").exists()
    assert ops.relayout(root, store) == 0, "a second relayout finds nothing to move"


def test_the_ledgers_writers_hand_their_urls_to_the_archiver_but_never_in_a_test(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    class Done:
        returncode = 1

    def runner(cmd, **kw):  # noqa: ANN001, ANN003, ANN202
        calls.append(cmd)
        return Done()

    assert src.archive_reads(tmp_path, ["https://a"], runner) == 0, "the suite's seam: L7R_ARCHIVE_READS=0"
    assert calls == []
    monkeypatch.setenv("L7R_ARCHIVE_READS", "1")
    assert src.archive_reads(tmp_path, ["https://a", "https://b"], runner) == 1
    assert calls[0][1].endswith("archive_ops.py") and calls[0][2:] == ["urls", "https://a", "https://b"]
    assert src.archive_reads(tmp_path, [], runner) == 0
