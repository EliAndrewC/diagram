#!/usr/bin/env python3
"""The combined search of the record and the archive (feature 447 amendment 3) - the meaning search and the text search in one
call, their hits merged by SOURCE, each source printed once.

WHY (the GM, 2026-10-30, `specs/447-semantic-index/request.md`): on feature 444's field-size question each search found sources
the other missed (`specs/447-semantic-index/research/t02-judge.md`), so a research pass runs both - "optimizing for finding things
that are relevant rather than doing something which is cheaper because it misses actual matches" - and finds what is held locally
before it goes to the web. A source is an archive capture (`<xx>/<id>`), a GM copy (`gm-copies/<file>`) or a record page (`record
<NNNN>`); the two searches' rankings are fused by reciprocal rank (each list adds 1/(60 + rank), the usual constant), so a source
both find rises. Under a KEY the sources already printed are remembered (`<archive home>/search-seen/<key>.json`) and a later call
prints only new ones: nothing is read twice.

    research_search.py --q "<question>" [--q "<in another language>" ...] [--terms "a|b" ...] [--key K] [--limit N]
                                                                                            `make research-search`
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import time
from collections.abc import Sequence
from typing import Any

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import semantic_index as si  # noqa: E402

LIMIT = 15  # archive sources a call prints: a knob, so a broad term set no longer prints a hundred files' download histories (FR-A3-2)
RECORD_LIMIT = 5  # record pages a call prints, apart: the record's pages, in English and in its own words, outrank every archive
# source on the meaning search (measured on the field-size question 2026-10-30: the first eight were all record pages)
PER_QUESTION = 30  # sources each meaning search contributes to the fusion
FUSE = 60  # the reciprocal-rank constant: rank 1 scores 1/61, rank 30 scores 1/90
CHUNK = 20000  # passages scored at once, so the whole index is never held at full precision (about 490 MB)
SEEN_DIR = "search-seen"
SEEN_DAYS = 1  # how long a key remembers what it printed: one question's session of searching, then forgotten
SNIPPET = 240
PASSAGES = 2  # passages a source shows by meaning, and measures it shows: one passage was the wrong one in ten drops (t05-why.md)

Hit = tuple[str, str, int, int]  # (source, path, start, end)


def source_of(rel: str) -> str:
    p = pathlib.PurePosixPath(rel)
    if rel.startswith(str(si.QUESTIONS)):
        return f"record {p.name[:4]}"
    return "/".join(p.parts[:2])


def load_index(out_dir: pathlib.Path) -> tuple[np.ndarray, list[str], np.ndarray]:
    """Every shard's vectors, paths and spans, in one array each."""
    vecs, paths, spans = [], [], []
    for p in sorted(out_dir.glob("*.npz")):
        z = si.load_shard(p)
        assert z is not None
        vecs.append(z["vecs"])
        paths += [str(x) for x in z["paths"]]
        spans.append(z["spans"])
    if not vecs:
        return np.zeros((0, si.DIM), np.float16), [], np.zeros((0, 2), np.int64)
    return np.concatenate(vecs), paths, np.concatenate(spans)


def meaning(index: tuple[np.ndarray, list[str], np.ndarray], questions: Sequence[str], embed: si.Embed, per: int = PER_QUESTION) -> list[list[Hit]]:
    """For each question, its nearest sources, nearest first, each with up to PASSAGES of its nearest passages (a source's second
    passage listed after its first, the source's rank its first's)."""
    vecs, paths, spans = index
    if not questions or not paths:
        return [[] for _ in questions]
    q = embed(list(questions)).astype(np.float32)
    sims = np.concatenate([vecs[i : i + CHUNK].astype(np.float32) @ q.T for i in range(0, len(paths), CHUNK)])
    out = []
    for j in range(len(questions)):
        by_src: dict[str, list[Hit]] = {}
        for i in np.argsort(-sims[:, j])[: per * 20]:
            src = source_of(paths[i])
            if src in by_src or len(by_src) < per:
                got = by_src.setdefault(src, [])
                if len(got) < PASSAGES:
                    got.append((src, paths[i], int(spans[i][0]), int(spans[i][1])))
        out.append([h for hits in by_src.values() for h in hits])
    return out


def _files(archive_dir: pathlib.Path, root: pathlib.Path, term: str) -> set[str]:
    """Every indexed file holding `term` (any case), relative to the archive or to the repository."""
    got: set[str] = set()
    for base, rel_to, include in ((archive_dir, archive_dir, "*.txt"), (root / si.QUESTIONS, root, "*.html")):
        if not base.is_dir():
            continue
        r = subprocess.run(
            ["grep", "-rlIiF", f"--include={include}", "--exclude-dir=.git", f"--exclude-dir={si.INDEX_DIR}", "--", term, str(base)],
            capture_output=True, text=True, check=False,
        )
        for f in r.stdout.splitlines():
            rel = pathlib.Path(f).relative_to(rel_to)
            if not rel.name.endswith(".originals.html") and len(rel.parts) >= 2:
                got.add(str(rel))
    return got


def _text_of(archive_dir: pathlib.Path, root: pathlib.Path, rel: str) -> str:
    if rel.startswith(str(si.QUESTIONS)):
        return si.strip_html((root / rel).read_text(encoding="utf-8", errors="replace"))
    return (archive_dir / rel).read_text(encoding="utf-8", errors="replace")


def text(archive_dir: pathlib.Path, root: pathlib.Path, term_sets: Sequence[Sequence[str]]) -> list[list[Hit]]:
    """For each term set, the sources holding every term, the most mentions first, each with the place its first term first
    appears."""
    out = []
    for terms in term_sets:
        files: set[str] | None = None
        for t in terms:
            got = _files(archive_dir, root, t)
            files = got if files is None else files & got
        scored = []
        for rel in sorted(files or ()):
            body = _text_of(archive_dir, root, rel)
            low = body.lower()
            at = low.find(terms[0].lower())
            start = max(0, at - SNIPPET // 2)
            scored.append((-sum(low.count(t.lower()) for t in terms), source_of(rel), rel, start, min(len(body), start + SNIPPET)))
        hits: list[Hit] = []
        seen: set[str] = set()
        for _n, src, rel, s, e in sorted(scored):
            if src not in seen:
                seen.add(src)
                hits.append((src, rel, s, e))
        out.append(hits)
    return out


def fuse(meaning_lists: Sequence[Sequence[Hit]], text_lists: Sequence[Sequence[Hit]]) -> list[dict[str, Any]]:
    """The sources of every list, ranked by reciprocal-rank fusion; each keeps its best passage of each search (`index`, `text`)
    and which searches found it."""
    rows: dict[str, dict[str, Any]] = {}
    for kind, lists in (("index", meaning_lists), ("text", text_lists)):
        for hits in lists:
            ranked: list[str] = []
            for src, rel, s, e in hits:
                row = rows.setdefault(src, {"source": src, "score": 0.0, "by": set(), "passages": {}})
                if src not in ranked:
                    ranked.append(src)
                    row["score"] += 1.0 / (FUSE + len(ranked))
                row["by"].add(kind)
                kept = row["passages"].setdefault(kind, [])
                if len(kept) < (PASSAGES if kind == "index" else 1) and (rel, s, e) not in kept:
                    kept.append((rel, s, e))
    return sorted(rows.values(), key=lambda r: (-r["score"], r["source"]))


# A NUMBER WITH A UNIT OF MEASURE (feature 447 amendment 4): the field-size runs dropped sources whose printed passage was the
# nearest by meaning but held no size - Hattori's sizes, Bray's "twenty yards square" and Huizhou's 0.715-mu parcel stood elsewhere
# in their files (`specs/447-semantic-index/research/t05-why.md`) - so each source also shows the passage where a measure stands
# nearest the question's terms. Number and unit forms are those the archive's cases use (t05-why.md: Hattori and Ofuro write ㎡, Bray
# "twenty yards square", the Huizhou register formal numerals with 分 厘 毫 步); a false hit (歩 "step", 分 "part") costs a line, a miss a source.
_WORDS = "one two three four five six seven eight nine ten eleven twelve fifteen twenty thirty forty fifty sixty hundred half quarter".split()
_NUM = r"(?:\d[\d,.]*|[〇一二三四五六七八九十百千万壱弐参拾廿壹贰貳叁參肆伍陆陸柒捌玖佰仟两兩]+|\b(?:" + "|".join(_WORDS) + r")\b(?: an?)?)"  # Bray: "twenty yards square"
_UNIT = (
    r"(?:反|段|畝|畆|歩|步|坪|町|亩|顷|頃|坵|丘|分|厘|毫|間|尺|丈|㎡|m2|m²|平方メートル|平方米|ヘクタール|公顷|"
    r"hectares?\b|ha\b|acres?\b|square (?:feet|foot|yards?|met(?:er|re)s?)\b|feet\b|foot\b|ft\b|yards?\b|mows?\b|mu\b|"
    r"tan\b|se\b|bu\b|tsubo\b|ch[oō]\b|ken\b|qing\b|qiu\b)"
)
MEASURE = re.compile(_NUM + r"\s*" + _UNIT, re.IGNORECASE)
CLOSE, NEAR = 60, 300  # characters either side of a measure in which the question's terms are counted, first close then near
# (measured 2026-10-30: with only the 300-character count every measure on Hattori's page tied, and its site area "2万㎡" won over
# its plots' "10㎡ほど ... 180㎡"; on the Ofuro page a menu's "第一歩" won over "1区画3-5㎡")


def measure_passages(body: str, terms: Sequence[str], n: int = PASSAGES) -> list[tuple[int, int]]:
    """The (start, end) of the passages around the `n` best measures that do not overlap - best by the most of `terms` within
    CLOSE, then within NEAR, then the most other measures within CLOSE (a run of sizes), the earliest on a tie."""
    low = body.lower()
    found = [m.start() for m in MEASURE.finditer(body)]

    def count(at: int, span: int) -> int:
        window = low[max(0, at - span) : at + span]
        return sum(1 for t in terms if t.lower() in window)

    scored = sorted(((count(at, CLOSE), count(at, NEAR), sum(1 for o in found if o != at and abs(o - at) <= CLOSE)), -at) for at in found)
    out: list[tuple[int, int]] = []
    for _score, neg in reversed(scored):
        start = max(0, -neg - SNIPPET // 2)
        span = (start, min(len(body), start + SNIPPET))
        if not any(s < span[1] and span[0] < e for s, e in out):
            out.append(span)
            if len(out) >= n:
                break
    return out


def seen_path(home: pathlib.Path, key: str) -> pathlib.Path:
    return home / SEEN_DIR / (re.sub(r"[^A-Za-z0-9._-]+", "-", key) + ".json")


def search(
    archive_dir: pathlib.Path, root: pathlib.Path, home: pathlib.Path, questions: Sequence[str], term_sets: Sequence[Sequence[str]],
    embed: si.Embed, key: str = "", limit: int = LIMIT, record_limit: int = RECORD_LIMIT,
) -> tuple[list[dict[str, Any]], int, int]:
    """(the sources to print - the record's pages first, then the archive's, each in its own rank - how many were found in all,
    how many were held back as already shown under `key`)."""
    index = load_index(archive_dir / si.INDEX_DIR / si.MODEL_DIR)
    rows = fuse(meaning(index, questions, embed), text(archive_dir, root, term_sets))
    shown: set[str] = set()
    path = seen_path(home, key) if key else None
    if path and path.is_file() and time.time() - path.stat().st_mtime < SEEN_DAYS * 86400:
        shown = set(json.loads(path.read_text(encoding="utf-8")))
    fresh = [r for r in rows if r["source"] not in shown]
    out = [r for r in fresh if r["source"].startswith("record ")][:record_limit] + [r for r in fresh if not r["source"].startswith("record ")][:limit]
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(sorted(shown | {r["source"] for r in out})), encoding="utf-8")
    return out, len(rows), len(rows) - len(fresh)


def render(archive_dir: pathlib.Path, root: pathlib.Path, rows: Sequence[dict[str, Any]], terms: Sequence[str] = ()) -> list[str]:
    """Each source with its passages: up to PASSAGES nearest by meaning, its text-search hit, and up to PASSAGES measures nearest the
    terms that those do not already show."""
    lines = []
    for n, r in enumerate(rows, 1):
        if n == 1 or r["source"].startswith("record ") != rows[n - 2]["source"].startswith("record "):
            lines.append("-- the record's pages (already answered?) --" if r["source"].startswith("record ") else "-- the archive's sources --")
        lines.append(f"{n:2d}. {r['source']}  [{'+'.join(sorted(r['by']))}]")
        shown: list[tuple[str, int, int]] = []
        for kind in ("index", "text"):
            for rel, s, e in r["passages"].get(kind, []):
                shown.append((rel, s, min(e, s + SNIPPET)))  # what the line shows, not the whole passage
                lines.append(f"    {'meaning' if kind == 'index' else 'text'}: {rel} [{s}:{e}] {_snippet(archive_dir, root, rel, s, e)}")
        rel = shown[0][0]
        for span in measure_passages(_text_of(archive_dir, root, rel), terms):
            if not any(r2 == rel and s < span[1] and span[0] < e for r2, s, e in shown):
                lines.append(f"    measure: {rel} [{span[0]}:{span[1]}] {_snippet(archive_dir, root, rel, *span)}")
    return lines


def _snippet(archive_dir: pathlib.Path, root: pathlib.Path, rel: str, s: int, e: int) -> str:
    return re.sub(r"\s+", " ", _text_of(archive_dir, root, rel)[s:e])[:SNIPPET]


def main(argv: list[str] | None = None, embed: si.Embed | None = None, store: Any = None) -> int:  # noqa: ANN401 - an `archive.Archive`
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--q", action="append", default=[], help="the question, once per language")
    ap.add_argument("--terms", action="append", default=[], help='term sets, "a|b;c": every term of a set required, sets apart')
    ap.add_argument("--key", default="", help="remember what is printed under this key; a later call prints only new sources")
    ap.add_argument("--limit", type=int, default=LIMIT)
    ap.add_argument("--record-limit", type=int, default=RECORD_LIMIT)
    args = ap.parse_args(argv)
    questions = [q for q in args.q if q.strip()]
    term_sets = [[t for t in s.split("|") if t.strip()] for arg in args.terms for s in arg.split(";")]
    term_sets = [s for s in term_sets if s]
    if not questions and not term_sets:
        print("make research-search: Q=, Q_JA=, Q_ZH=, Q_KO= or TERMS= is required", file=sys.stderr)
        return 2
    import archive as ar  # noqa: PLC0415 - the archive's working copy

    root = ar.src.repo_root()
    home = ar.home_of(root)
    store = store or ar.Archive(home)
    if questions and not (store.dir / si.INDEX_DIR / si.MODEL_DIR).is_dir():
        print("research-search: no index yet - run `make semantic-index`", file=sys.stderr)
        return 1
    embed = embed or (si.model_embed(home) if questions else (lambda _t: np.zeros((0, si.DIM), np.float32)))
    rows, found, held = search(store.dir, root, home, questions, term_sets, embed, args.key, args.limit, args.record_limit)
    print(
        f"research-search: {len(questions)} question(s), {len(term_sets)} term set(s) - {len(rows)} of {found} source(s)"
        + (f", {held} already shown under key {args.key!r}" if args.key else "")
        + (f"; {found - held - len(rows)} more not printed - call again under KEY= for the next" if found - held > len(rows) else "")
    )
    terms = [w for s in term_sets for w in s] + [w for q in questions for w in re.findall(r"[A-Za-z]{4,}", q)]
    print("\n".join(render(store.dir, root, rows, terms)))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
