"""The semantic index (feature 447): passages cut, an update embedding only what changed, the nearest passages found, the shards
committed to the archive - with a stand-in for the model, so no test loads it."""

from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys
from collections.abc import Sequence

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "record"))
import semantic_index as si  # noqa: E402

pytestmark = pytest.mark.tooling


class Fake:
    """A stand-in embedder: a passage's vector from its words, so passages sharing words are near; it counts what it embeds."""

    def __init__(self) -> None:
        self.seen: list[str] = []

    def __call__(self, texts: Sequence[str]) -> np.ndarray:
        self.seen += list(texts)
        out = np.zeros((len(texts), si.DIM), np.float32)
        for i, t in enumerate(texts):
            for w in t.lower().split():
                out[i, int(hashlib.md5(w.encode()).hexdigest(), 16) % si.DIM] += 1.0
            n = np.linalg.norm(out[i])
            out[i] /= n or 1.0
        return out


def _corpus(tmp: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    archive, root = tmp / "archive", tmp / "repo"
    (archive / "ab" / "x1").mkdir(parents=True)
    (archive / "ab" / "x1" / "text.txt").write_text("the paddy field lay below the intake " * 40)
    (archive / "gm-copies").mkdir()
    (archive / "gm-copies" / "book.pdf.txt").write_text("a temple roof of cypress bark and its eaves")
    (archive / ".git").mkdir()
    (archive / ".git" / "x.txt").write_text("never read")
    (archive / "top.txt").write_text("a file at the archive's root is no capture")
    q = root / si.QUESTIONS
    q.mkdir(parents=True)
    (q / "0017-farmland.html").write_text("<h2>How much farmland</h2><!-- a comment --><p>a village works its rice in tracts &amp; fields</p>")
    (q / "0017-farmland.originals.html").write_text("<p>never indexed</p>")
    (q / "index.html").write_text("<p>a page with no number</p>")
    return archive, root


def test_passages_cover_the_text_and_cut_at_spaces_or_at_the_size() -> None:
    text = "word " * 500
    spans = si.passages(text, 100)
    assert all(e - s <= 100 for s, e in spans) and spans[0][0] == 0 and spans[-1][1] == len(text)
    assert all(text[e] == " " for _s, e in spans[:-1]), "an English passage ends at a space"
    cjk = "田" * 250
    assert si.passages(cjk, 100) == [(0, 100), (100, 200), (200, 250)], "a run with no space is cut at the size"
    assert si.passages("   ") == []
    assert si.strip_html("<p>a &amp; b</p><!-- x -->  c") == "a & b c"


def test_a_build_embeds_each_passage_once_and_an_update_only_what_changed(tmp_path: pathlib.Path) -> None:
    archive, root = _corpus(tmp_path)
    fake = Fake()
    written = si.build(archive, root, fake, log=lambda _s: None)
    assert written == ["ab", "gm-copies", "record-00"], "one shard a folder, and the record's hundred questions"
    first = len(fake.seen)
    assert si.build(archive, root, fake, log=lambda _s: None) == [] and len(fake.seen) == first, "nothing changed, nothing embedded"
    (archive / "gm-copies" / "book.pdf.txt").write_text("a temple roof of cypress bark and its eaves, and a new line")
    assert si.build(archive, root, fake, log=lambda _s: None) == ["gm-copies"]
    assert len(fake.seen) == first + 1, "only the changed passage is embedded"
    z = si.load_shard(archive / si.INDEX_DIR / si.MODEL_DIR / "gm-copies.npz")
    assert z is not None and z["vecs"].dtype == np.float16 and z["vecs"].shape[1] == si.DIM
    assert si.load_shard(tmp_path / "none.npz") is None


def test_a_build_takes_only_the_shards_named_and_stops_at_its_limit(tmp_path: pathlib.Path) -> None:
    archive, root = _corpus(tmp_path)
    assert si.build(archive, root, Fake(), only={"gm-copies"}, log=lambda _s: None) == ["gm-copies"]
    assert si.build(archive, root, Fake(), limit=1, log=lambda _s: None) == ["ab"]


def test_find_returns_the_nearest_passages_and_their_opening_words(tmp_path: pathlib.Path) -> None:
    archive, root = _corpus(tmp_path)
    fake = Fake()
    si.build(archive, root, fake, log=lambda _s: None)
    hits = si.find(archive, root, "temple roof bark", fake, k=2)
    assert hits[0][1] == "gm-copies/book.pdf.txt" and hits[0][0] > hits[1][0]
    assert si.preview(archive, root, hits[0][1], hits[0][2], hits[0][3]).startswith("a temple roof")
    rec = next(h for h in si.find(archive, root, "village rice tracts", fake, k=5) if h[1].startswith("research"))
    assert "rice in tracts & fields" in si.preview(archive, root, rec[1], rec[2], rec[3])


class Store:
    """An archive working copy in a temporary git repository, pushing to a bare one."""

    def __init__(self, tmp: pathlib.Path) -> None:
        import archive as ar  # noqa: PLC0415

        bare = tmp / "remote.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True)
        self.inner = ar.Archive(tmp / "home", remote=str(bare))
        self.inner.ensure()
        self.dir = self.inner.dir

    def __getattr__(self, name: str):  # noqa: ANN204 - the Archive's own methods
        return getattr(self.inner, name)


def test_the_shards_are_committed_and_pushed_to_the_archive(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    store = Store(tmp_path)
    (store.dir / "seed.txt").write_text("x")
    store.git("add", "seed.txt")
    store.git("commit", "-q", "-m", "seed")
    root = tmp_path / "repo"
    (root / si.QUESTIONS).mkdir(parents=True)
    (store.dir / "ab" / "x").mkdir(parents=True)
    (store.dir / "ab" / "x" / "text.txt").write_text("rice paddy acres")
    assert si.commit(store, []) == ""
    written = si.build(store.dir, root, Fake(), log=lambda _s: None)
    assert si.commit(store, written, log=lambda _s: None) == ""
    assert "semantic index" in store.git("log", "-1", "--format=%s").stdout
    assert store.git("ls-remote", "origin", "main").stdout.strip(), "pushed"
    assert si.commit(store, written, log=lambda _s: None) == "", "nothing new staged: no commit"


def test_main_builds_then_finds_and_says_when_there_is_no_index(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    import archive as ar  # noqa: PLC0415

    store = Store(tmp_path)
    root = tmp_path / "repo"
    (root / si.QUESTIONS).mkdir(parents=True)
    monkeypatch.setattr(ar.src, "repo_root", lambda: root)
    monkeypatch.setattr(ar, "home_of", lambda _r: tmp_path / "home")
    assert si.main(["find", "anything"], embed=Fake(), store=store) == 1
    assert "no index yet" in capsys.readouterr().err
    (store.dir / "ab" / "x").mkdir(parents=True)
    (store.dir / "ab" / "x" / "text.txt").write_text("the paddy field lay below the intake")
    assert si.main(["build"], embed=Fake(), store=store) == 0
    assert si.main(["find", "paddy intake", "--k", "1"], embed=Fake(), store=store) == 0
    out = capsys.readouterr().out
    assert "1 shard(s) written" in out and "ab/x/text.txt" in out and "the paddy field" in out
