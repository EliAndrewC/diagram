#!/usr/bin/env python3
"""The semantic index of the research record and the source archive (feature 447, a trial) - beside `make archive-find`.

WHY (the GM, 2026-10-29, `specs/447-semantic-index/request.md`): a text search finds a term and misses the same idea in other
words or another language - "the largest single paddy", 一枚の田, a size in cho - so a question is answered by meaning as well:
each passage of the record's pages and the archive's texts is turned into a vector by BGE-M3, a multilingual model run locally
(the GM: "let's just go ahead and lock in the larger one"), and a question finds the passages nearest it. The model is the
8-bit build (`Xenova/bge-m3`'s `model_int8.onnx`): the full-precision one ran about seven times slower here, and quantizing it
locally took 7.5 GB, past the containers' shared memory cap (measured 2026-10-29); the 8-bit build's similarities matched the
full one's to two places on the same probes.

THE INDEX IS STORED IN THE ARCHIVE (the GM: "Do we check that in to the private GitHub repo where we store our research corpus?
that probably makes sense to me"): `semantic-index/<model>/<shard>.npz` in the archive's working copy, one shard a folder of the
archive (`<id[:2]>`, `gm-copies`) and one a hundred questions of the record, its vectors at half precision. A passage is keyed
by a fingerprint of the model and its text, so an update embeds only the passages that are new or changed and rewrites only
their shards; a change of model is a new folder, a rebuild whole. Nothing leaves the machine: the model runs here.

    semantic_index.py build [--shard S ...] [--limit N]   `make semantic-index`
    semantic_index.py find "<question>" [--k K]           `make semantic-find Q="..."`
"""

from __future__ import annotations

import argparse
import hashlib
import html
import io
import itertools
import os
import pathlib
import re
import sys
from collections.abc import Callable, Iterator, Sequence
from typing import Any

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

MODEL = "Xenova/bge-m3-int8"  # BGE-M3, its 8-bit ONNX build (the docstring says why)
MODEL_DIR = "bge-m3-int8"  # the model's folder under `semantic-index/`: a new model is a new folder
DIM = 1024
INDEX_DIR = "semantic-index"
CACHE = "model-cache"  # the model's files, under the mirror's `.specify/`: host state, kept off the container
PASSAGE_CHARS = 900  # a few hundred words of English; a CJK passage is cut at the same length (the trial measured 900 against 1,800: the same characters a second)
RECORD_SHARD = 100  # questions a record shard holds
BATCH = 8
QUESTIONS = pathlib.Path("research") / "questions"

Embed = Callable[[Sequence[str]], np.ndarray]


def strip_html(text: str) -> str:
    """A record page's visible text: comments and tags dropped, entities read, whitespace collapsed."""
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def passages(text: str, size: int = PASSAGE_CHARS) -> list[tuple[int, int]]:
    """The (start, end) of each passage of `text`: cut at the last space before `size` characters, or at `size` where a run
    has none (Japanese and Chinese), so every passage is at most `size` long and together they cover the text."""
    out: list[tuple[int, int]] = []
    i, n = 0, len(text)
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        end = min(i + size, n)
        if end < n:
            cut = text.rfind(" ", i + size // 2, end)
            end = cut if cut > i else end
        out.append((i, end))
        i = end
    return out


def fingerprint(text: str) -> str:
    return hashlib.sha1(f"{MODEL}\n{text}".encode()).hexdigest()[:20]


def corpus(archive_dir: pathlib.Path, root: pathlib.Path) -> Iterator[tuple[str, str, str]]:
    """(shard, path, text) for every archived text - `path` relative to the archive, shard its first folder - and every page of
    the record but its originals - `path` relative to the repository, its shard `record-<n>` a hundred questions."""
    if archive_dir.is_dir():
        for p in sorted(archive_dir.rglob("*.txt")):
            rel = p.relative_to(archive_dir)
            if rel.parts[0] in (".git", INDEX_DIR) or len(rel.parts) < 2:
                continue
            yield rel.parts[0], str(rel), p.read_text(encoding="utf-8", errors="replace")
    for p in sorted((root / QUESTIONS).glob("*.html")):
        if p.name.endswith(".originals.html"):
            continue
        num = int(p.name.split("-", 1)[0]) if p.name[:4].isdigit() else 0
        yield f"record-{num // RECORD_SHARD:02d}", str(p.relative_to(root)), strip_html(p.read_text(encoding="utf-8", errors="replace"))


def load_shard(path: pathlib.Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


def save_shard(path: pathlib.Path, fps: list[str], vecs: np.ndarray, paths: list[str], spans: list[tuple[int, int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    np.savez(
        buf,
        fps=np.array(fps, dtype="U20"),
        vecs=vecs.astype(np.float16),
        paths=np.array(paths, dtype=str),
        spans=np.array(spans, dtype=np.int64).reshape(-1, 2),
    )
    path.write_bytes(buf.getvalue())


def build(
    archive_dir: pathlib.Path, root: pathlib.Path, embed: Embed, only: set[str] | None = None, limit: int = 0, log: Callable[[str], None] = print
) -> list[str]:
    """Bring every shard up to date: each passage's vector kept where its fingerprint is already in the shard, embedded where it
    is new; a shard written only where its passages changed. `only` names the shards to do, `limit` stops after that many shards
    written (a run killed or stopped resumes where it left off: each shard is written as it is done). Returns the shards written."""
    out_dir = archive_dir / INDEX_DIR / MODEL_DIR
    written: list[str] = []
    # ONE SHARD IN MEMORY AT A TIME: the corpus comes in path order, so a shard's files are contiguous (the archive's by its first
    # folder, the record's by its questions' numbers), and the whole corpus - about 106 million characters - is never held at once
    for shard, group in itertools.groupby(corpus(archive_dir, root), key=lambda row: row[0]):
        if only and shard not in only:
            continue
        items = [(rel, text[s:e], s, e) for _sh, rel, text in group for s, e in passages(text)]
        fps = [fingerprint(t) for _rel, t, _s, _e in items]
        old = load_shard(out_dir / f"{shard}.npz")
        have = {str(f): old["vecs"][i] for i, f in enumerate(old["fps"])} if old is not None else {}
        if old is not None and [str(f) for f in old["fps"]] == fps:
            continue
        todo = [i for i, f in enumerate(fps) if f not in have]
        new = embed([items[i][1] for i in todo]) if todo else np.zeros((0, DIM), np.float32)
        got = dict(zip((fps[i] for i in todo), new, strict=True))
        vecs = np.stack([have[f] if f in have else got[f] for f in fps]).astype(np.float32)
        save_shard(out_dir / f"{shard}.npz", fps, vecs, [r for r, _t, _s, _e in items], [(s, e) for _r, _t, s, e in items])
        written.append(shard)
        log(f"semantic-index: {shard} - {len(items)} passages, {len(todo)} embedded")
        if limit and len(written) >= limit:
            break
    return written


def find(archive_dir: pathlib.Path, root: pathlib.Path, question: str, embed: Embed, k: int = 10) -> list[tuple[float, str, int, int]]:
    """The `k` passages nearest `question`, as (similarity, path, start, end), the nearest first."""
    out_dir = archive_dir / INDEX_DIR / MODEL_DIR
    q = embed([question])[0].astype(np.float32)
    best: list[tuple[float, str, int, int]] = []
    for p in sorted(out_dir.glob("*.npz")):
        z = load_shard(p)
        assert z is not None
        sims = z["vecs"].astype(np.float32) @ q
        for i in np.argsort(-sims)[:k]:
            best.append((float(sims[i]), str(z["paths"][i]), int(z["spans"][i][0]), int(z["spans"][i][1])))
    return sorted(best, reverse=True)[:k]


def preview(archive_dir: pathlib.Path, root: pathlib.Path, rel: str, start: int, end: int, width: int = 240) -> str:
    """The passage's opening words, read again from its file (a record page through `strip_html`, as it was indexed)."""
    if rel.startswith(str(QUESTIONS)):
        text = strip_html((root / rel).read_text(encoding="utf-8", errors="replace"))
    else:
        text = (archive_dir / rel).read_text(encoding="utf-8", errors="replace")
    return re.sub(r"\s+", " ", text[start:end])[:width]


def model_embed(home: pathlib.Path) -> Embed:  # pragma: no cover - the real model, run by `make semantic-index` and the trial
    """BGE-M3's 8-bit build through fastembed, its files under the mirror's `.specify/model-cache/`, on half the cores (the
    containers share the machine and a 10 GB memory cap: a run of the full model at every core was killed, 2026-10-29)."""
    from fastembed import TextEmbedding  # noqa: PLC0415 - only a build or a search needs the model
    from fastembed.common.model_description import ModelSource, PoolingType  # noqa: PLC0415

    if MODEL not in {m["model"] for m in TextEmbedding.list_supported_models()}:
        TextEmbedding.add_custom_model(
            model=MODEL, pooling=PoolingType.CLS, normalization=True, sources=ModelSource(hf="Xenova/bge-m3"), dim=DIM, model_file="onnx/model_int8.onnx"
        )
    model = TextEmbedding(MODEL, cache_dir=str(home / CACHE), threads=max(1, (os.cpu_count() or 2) // 2))

    def embed(texts: Sequence[str]) -> np.ndarray:
        return np.array(list(model.embed(list(texts), batch_size=BATCH)), dtype=np.float32).reshape(-1, DIM)

    return embed


def commit(store: Any, written: list[str], log: Callable[[str], None] = print) -> str:  # noqa: ANN401 - an `archive.Archive`
    """Commit the shards written and push, under the archive's lock: '' on success, else git's complaint."""
    if not written:
        return ""
    with store.locked():
        store.git("add", "--", f"{INDEX_DIR}/{MODEL_DIR}")
        if store.git("diff", "--cached", "--quiet", check=False).returncode == 0:
            return ""
        store.git("commit", "-q", "-m", f"the semantic index ({MODEL}): {len(written)} shard(s) - {', '.join(written[:8])}{' ...' if len(written) > 8 else ''}")
        why = store.push()
    log("semantic-index: committed and pushed" if not why else f"semantic-index: the push failed - {why}")
    return why


def main(argv: list[str] | None = None, embed: Embed | None = None, store: Any = None) -> int:  # noqa: ANN401
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--shard", action="append", default=[])
    b.add_argument("--limit", type=int, default=0)
    f = sub.add_parser("find")
    f.add_argument("question")
    f.add_argument("--k", type=int, default=10)
    args = ap.parse_args(argv)
    import archive as ar  # noqa: PLC0415 - the archive's working copy and lock

    root = ar.src.repo_root()
    home = ar.home_of(root)
    store = store or ar.Archive(home, env=ar.git_env(ar.token(root)))
    embed = embed or model_embed(home)
    if args.cmd == "build":
        written = build(store.dir, root, embed, set(args.shard) or None, args.limit)
        print(f"semantic-index: {len(written)} shard(s) written")
        return 1 if commit(store, written) else 0
    hits = find(store.dir, root, args.question, embed, args.k)
    if not hits:
        print("semantic-find: no index yet - run `make semantic-index`", file=sys.stderr)
        return 1
    for sim, rel, s, e in hits:
        print(f"{sim:.3f}  {rel} [{s}:{e}]\n       {preview(store.dir, root, rel, s, e)}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
