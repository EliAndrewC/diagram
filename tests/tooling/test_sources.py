"""`scripts/record/sources.py` (feature 288): the sources-consulted ledger and the saved-page cache keyed by URL.

WHAT THESE PROVE. One page under its several spellings is one ledger URL and one cache entry; a ledger line carries
the feature, clone, session, question and outcome, and only the five outcome forms are recorded; the lookup finds a
URL's lines and a key's; a filled registry entry marks its URL cited once; a cached page is served without a fetch
until it is older than the age or REFRESH is set, and an imported copy never serves a character-for-character check;
the seed writes one line per URL, feature and session and runs once; the import keeps the newest whole save of each
page and skips an excerpt. NO NETWORK: every fetcher here is a fake.

The ledger and the cache live under `L7R_SOURCES_HOME`, which the tooling conftest points at a scratch directory.
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import multiprocessing
import os
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_sources", REPO / "scripts/record/sources.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


src = _load()
CTX = {"feature": "288", "clone": "c", "session": "s-123456789"}


class _Fake:
    """A `Pages` stand-in that counts its fetches."""

    def __init__(self, state: str = "FETCHED", text: str = "A dike is 3.5 m wide. It is old.") -> None:
        self.calls: list[str] = []
        self.state, self.text = state, text

    def get(self, url: str) -> dict:
        self.calls.append(url)
        return {"state": self.state, "text": self.text} if self.state == "FETCHED" else {"state": self.state, "why": "refused"}


def _home() -> pathlib.Path:
    return pathlib.Path(os.environ["L7R_SOURCES_HOME"])


def _registry(root: pathlib.Path, entries: dict[str, str]) -> None:
    d = root / src.REGISTRY
    d.mkdir(parents=True, exist_ok=True)
    for n, (key, body) in enumerate(entries.items(), 1):
        (d / f"{n * 10:04d}-{key}.html").write_text(body, encoding="utf-8")


# ---- normalization, context, home ----


@pytest.mark.parametrize(
    "spelling",
    ["https://www.example.org/a/b/", "http://example.org/a/b#part", "https://example.org/A/B", "example.org/a/%62"],
)
def test_one_page_under_its_spellings_is_one_url(spelling: str) -> None:
    assert src.norm(spelling) == "example.org/a/b"


def test_a_wikipedia_path_keeps_its_case_and_the_mobile_host_folds() -> None:
    assert src.norm("https://ja.m.wikipedia.org/wiki/Edo_Castle") == "ja.wikipedia.org/wiki/Edo_Castle"
    assert src.norm("https://EN.wikipedia.org") == "en.wikipedia.org"
    assert src.norm("https://m.example.org/x") == "example.org/x"


def test_home_is_the_mirror_s_specify_and_the_env_moves_it(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert src.home() == _home()
    monkeypatch.delenv("L7R_SOURCES_HOME")
    clone = tmp_path / "mirror" / ".clones" / "c"
    assert src.home(clone) == tmp_path / "mirror" / ".specify"
    assert src.home(tmp_path / "mirror") == tmp_path / "mirror" / ".specify"
    monkeypatch.chdir(REPO)
    assert src.home() == src.home(REPO)


def test_repo_root_walks_up_to_git(tmp_path: pathlib.Path) -> None:
    (tmp_path / "r" / ".git").mkdir(parents=True)
    (tmp_path / "r" / "a" / "b").mkdir(parents=True)
    assert src.repo_root(tmp_path / "r" / "a" / "b") == tmp_path / "r"


def test_context_reads_the_feature_pointer_and_the_session(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SPECIFY_FEATURE", raising=False)
    monkeypatch.delenv("L7R_PAGE_SESSION", raising=False)
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "harness-id")
    root = tmp_path / "clone"
    (root / ".specify").mkdir(parents=True)
    assert src.context(root) == {"feature": "", "clone": "clone", "session": "harness-id"}
    (root / ".specify" / "feature.json").write_text('{"feature_directory": "specs/280-modern-only"}', encoding="utf-8")
    monkeypatch.setenv("L7R_PAGE_SESSION", "page-7")
    assert src.context(root) == {"feature": "280", "clone": "clone", "session": "page-7"}
    (root / ".specify" / "feature.json").write_text("{broken", encoding="utf-8")
    monkeypatch.setenv("SPECIFY_FEATURE", "288-sources-ledger-and-page-cache")
    assert src.context(root)["feature"] == "288"


# ---- the ledger ----


def test_a_line_is_appended_and_read_back_and_a_torn_line_is_skipped() -> None:
    where = _home()
    src.append(where, [])
    assert not (where / src.LEDGER).exists(), "nothing to write writes nothing"
    src.append(where, [src.line(CTX, "https://www.example.org/p", "pending", ["0016"])])
    with open(where / src.LEDGER, "a", encoding="utf-8") as f:
        f.write("{torn\n")
    rows = src.read(where)
    assert len(rows) == 1
    assert rows[0] | {"utc": ""} == {"url": "example.org/p", "raw": "https://www.example.org/p", "utc": "", **CTX, "questions": ["0016"], "outcome": "pending"}
    assert src.read(where / "nowhere") == []


def _append_many(where: str) -> int:
    mod = _load()
    for i in range(50):
        mod.append(pathlib.Path(where), [mod.line(CTX, f"https://example.org/{i}", "pending")])
    return 50


def test_appends_from_several_processes_never_tear_a_line() -> None:
    where = _home()
    with multiprocessing.get_context("spawn").Pool(4) as pool:
        assert sum(pool.map(_append_many, [str(where)] * 4)) == 200
    assert len(src.read(where)) == 200 and len((where / src.LEDGER).read_text(encoding="utf-8").splitlines()) == 200


def test_a_held_lock_is_an_error_not_a_hang() -> None:
    with src.locked(_home()), pytest.raises(TimeoutError), src.locked(_home(), timeout=0.05):
        pass  # pragma: no cover - the inner lock is never taken


@pytest.mark.parametrize(
    ("outcome", "ok"),
    [
        ("cited:edo-enwiki", True),
        ("rejected: no dimensions", True),
        ("nothing-found", True),
        ("unreadable", True),
        ("pending", True),
        ("rejected:", False),
        ("cited:Edo Wiki", False),
        ("maybe", False),
        ("unknown-outcome", False),
    ],
)
def test_only_the_five_outcome_forms_are_recorded(outcome: str, ok: bool) -> None:
    assert src.valid_outcome(outcome) is ok


def test_show_names_when_who_what_for_and_what_came_of_it() -> None:
    row = {**src.line(CTX, "https://example.org/p", "rejected: no widths", ["a/010", "b/020"]), "utc": "2026-09-27T01:02:03+00:00"}
    assert src.show(row) == "  2026-09-27  f288 c s:s-123456  rejected: no widths  q: a/010; b/020"
    assert src.show({"utc": "2026-09-26T00:00:00+00:00", "feature": "", "clone": "", "session": "", "outcome": "unknown-outcome", "reads": 4}) == "  2026-09-26  - x4  unknown-outcome"


def test_the_lookup_finds_a_url_in_any_spelling_and_a_key_by_regex() -> None:
    where = _home()
    src.append(
        where,
        [
            src.line(CTX, "https://example.org/p", "rejected: nothing on widths"),
            src.line(CTX, "https://example.org/q", "cited:edo-enwiki"),
            src.line(CTX, "https://example.org/r", "cited:kyoto-jawiki"),
        ],
    )
    assert [r["outcome"] for r in src.earlier(where, "http://www.example.org/p/")] == ["rejected: nothing on widths"]
    assert [r["url"] for r in src.by_key(where, "^edo")] == ["example.org/q"]
    assert src.by_key(where, "wiki$") == src.read(where)[1:]


# ---- the registry and the fill pass ----


def test_the_fill_pass_marks_each_filled_entry_once(tmp_path: pathlib.Path) -> None:
    root = tmp_path / "clone"
    _registry(
        root,
        {
            "edo-enwiki": '<p>en.wikipedia "Edo" (https://en.wikipedia.org/wiki/Edo) - see also https://example.org/other</p>',
            "a-book": "<p>a book, no pointer</p>",
        },
    )
    (root / src.REGISTRY / "README.txt").write_text("not an entry", encoding="utf-8")
    assert src.registry(root) == {"edo-enwiki": "https://en.wikipedia.org/wiki/Edo"}
    assert src.registry_urls(root) == {"en.wikipedia.org/wiki/Edo": "edo-enwiki", "example.org/other": "edo-enwiki"}
    where = _home()
    got = src.mark_filled(root, where)
    assert [(r["url"], r["outcome"]) for r in got] == [("en.wikipedia.org/wiki/Edo", "cited:edo-enwiki")]
    assert src.mark_filled(root, where) == [], "a second pass appends nothing"


def test_a_file_not_named_as_an_entry_is_skipped(tmp_path: pathlib.Path) -> None:
    root = tmp_path / "clone"
    _registry(root, {})
    (root / src.REGISTRY / "0010-.html").write_text("<p>(https://example.org/x)</p>", encoding="utf-8")
    (root / src.REGISTRY / "0020-ok.html").write_text("<p>(https://example.org/y)</p>", encoding="utf-8")
    assert src.registry(root) == {"ok": "https://example.org/y"}
    assert src.registry_urls(root) == {"example.org/y": "ok"}


# ---- the cache ----


def test_wrapping_keeps_a_decimal_on_its_line() -> None:
    assert src.wrapped("A dike is 3.5 m wide. Next! 三。四") == "A dike is 3.5 m wide.\nNext!\n三。\n四\n"
    assert src.parts("ab\ncd\n", size=3) == ["ab\n", "cd\n"]
    assert src.parts("abcdefg\nh\n", size=3) == ["abc", "def", "g\n", "h\n"]
    assert src.parts("x\nabcd\n", size=3) == ["x\n", "abc", "d\n"]


def test_a_page_is_stored_once_and_read_back(tmp_path: pathlib.Path) -> None:
    where = _home()
    got = src.put(where, "https://www.example.org/p", "One. Two.")
    assert got["files"] == ["page.txt"]
    d = src.entry_dir(where, "http://example.org/p/")
    assert d == got["dir"] and d.parent.name == d.name[:2]
    hit = src.cached(where, "example.org/p")
    assert hit is not None and hit["text"] == "One. Two." and hit["exact"] and hit["files"] == ["page.txt"]
    assert (d / "page.txt").read_text(encoding="utf-8") == "One.\nTwo.\n"
    long = " ".join(f"Sentence {i} is here." for i in range(3000))
    got = src.put(where, "https://example.org/p", long)
    assert got["files"][0] == "page.p1.txt" and len(got["files"]) > 1
    assert not (d / "page.txt").exists(), "a re-save replaces the old parts"
    assert src.cached(where, "https://example.org/p")["files"] == got["files"]
    assert not list(d.glob(".*.tmp")), "no temporary file is left"


def test_an_old_copy_an_absent_one_and_a_broken_one_are_misses() -> None:
    where = _home()
    assert src.cached(where, "https://example.org/none") is None
    old = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=src.MAX_AGE_DAYS + 1)).isoformat()
    src.put(where, "https://example.org/old", "Old.", fetched=old)
    assert src.cached(where, "https://example.org/old") is None
    assert src.cached(where, "https://example.org/old", max_age_days=30) is not None
    src.put(where, "https://example.org/broken", "x")
    (src.entry_dir(where, "https://example.org/broken") / "meta.json").write_text("{", encoding="utf-8")
    assert src.cached(where, "https://example.org/broken") is None


def test_an_imported_copy_never_serves_an_exact_check() -> None:
    where = _home()
    src.put(where, "https://example.org/imp", "One.\nTwo.\n", exact=False, origin="import:/tmp/x")
    assert src.cached(where, "https://example.org/imp") is not None
    assert src.cached(where, "https://example.org/imp", exact=True) is None


def test_cached_pages_fetches_once_then_serves_the_copy(monkeypatch: pytest.MonkeyPatch) -> None:
    where, fake = _home(), _Fake()
    pages = src.CachedPages(fake, where)
    first, second = pages.get("https://example.org/p"), pages.get("http://www.example.org/p/")
    assert fake.calls == ["https://example.org/p"]
    assert first == {"state": "FETCHED", "text": fake.text}
    assert pages.refused == {}, "a fetcher with no record of refusals reports none"
    assert second["text"] == fake.text and second["cached"]
    src.CachedPages(fake, where, refresh=True).get("https://example.org/p")
    assert len(fake.calls) == 2, "REFRESH fetches again"
    monkeypatch.setenv("REFRESH", "1")
    assert src.refresh_wanted()
    monkeypatch.setenv("REFRESH", "0")
    assert not src.refresh_wanted()


def test_a_failure_is_never_cached() -> None:
    where, fake = _home(), _Fake(state="UNFETCHABLE")
    pages = src.CachedPages(fake, where)
    assert pages.get("https://example.org/down")["state"] == "UNFETCHABLE"
    assert pages.get("https://example.org/down")["state"] == "UNFETCHABLE"
    assert len(fake.calls) == 2 and src.cached(where, "https://example.org/down") is None


def test_an_exact_reader_replaces_an_imported_copy() -> None:
    where, fake = _home(), _Fake()
    src.put(where, "https://example.org/imp", "One.\nTwo.\n", exact=False)
    assert src.CachedPages(fake, where, exact=True).get("https://example.org/imp")["text"] == fake.text
    assert src.cached(where, "https://example.org/imp", exact=True)["text"] == fake.text


# ---- the seed and the import ----


def test_the_seed_writes_one_line_per_url_feature_and_session_once(tmp_path: pathlib.Path) -> None:
    root = tmp_path / "clone"
    _registry(root, {"edo-enwiki": "<p>(https://en.wikipedia.org/wiki/Edo)</p>"})
    per_url = tmp_path / "per_url.json"
    ev = {"ts": "2026-09-27T10:00:00.000Z", "session": "s1", "feature": "271", "why": "Give  the widths"}
    per_url.write_text(
        json.dumps(
            {
                "en.wikipedia.org/wiki/Edo": [ev, {**ev, "ts": "2026-09-26T09:00:00.000Z"}, {**ev, "session": "s2", "why": None}],
                "example.org/x": [{**ev, "feature": None}],
            }
        ),
        encoding="utf-8",
    )
    where = _home()
    assert src.seed(per_url, root, where) == 3
    rows = src.read(where)
    assert [(r["url"], r["session"], r["reads"], r["outcome"]) for r in rows] == [
        ("en.wikipedia.org/wiki/Edo", "s1", 2, "cited:edo-enwiki"),
        ("en.wikipedia.org/wiki/Edo", "s2", 1, "cited:edo-enwiki"),
        ("example.org/x", "s1", 1, "unknown-outcome"),
    ]
    assert rows[0]["utc"] == "2026-09-26T09:00:00+00:00" and rows[0]["questions"] == ["Give the widths"]
    assert rows[0]["seed"] == src.SEED and rows[2]["feature"] == ""
    assert src.seed(per_url, root, where) == 0, "a seeded ledger is not seeded again"


def _save(run: pathlib.Path, rows: list[tuple[str, str, str]], files: dict[str, str]) -> None:
    run.mkdir(parents=True)
    (run / "MANIFEST.txt").write_text("pointer | file | state\n" + "".join(f"{p} | {f} | {s}\n" for p, f, s in rows), encoding="utf-8")
    for name, text in files.items():
        (run / name).write_text(text, encoding="utf-8")


def test_the_import_keeps_the_newest_whole_save_of_each_page(tmp_path: pathlib.Path) -> None:
    scratch = tmp_path / "l7r-check"
    _save(
        scratch / "a",
        [
            ("https://example.org/p", "01-example.org.txt", "FETCHED - 9 chars"),
            ("https://example.org/long", "02-example.org.p1.txt ... .p2.txt (2 parts - grep them all)", "FETCHED - 12 chars"),
            ("https://example.org/ex", "03-example.org.txt", "FETCHED - 90000 chars, saved as an excerpt of 9,000"),
            ("https://example.org/ex2", "04-example.org.txt", "FETCHED - 90000 chars"),
            ("https://example.org/gone", "05-example.org.txt", "FETCHED - 9 chars"),
            ("https://example.org/down", "-", "UNFETCHABLE - 403"),
            ("own/link", "06-x.txt", "FETCHED - 1 chars"),
        ],
        {
            "01-example.org.txt": "Old copy.\n",
            "02-example.org.p2.txt": "Part two.\n",
            "02-example.org.p1.txt": "Part one.\n",
            "03-example.org.txt": "cut",
            "04-example.org.txt": "[EXCERPT of a 90,000-character page]\n",
        },
    )
    _save(scratch / "b", [("https://www.example.org/p/", "01-example.org.txt", "FETCHED - 9 chars")], {"01-example.org.txt": "New copy.\n"})
    os.utime(scratch / "a" / "01-example.org.txt", (1_000_000_000, 1_000_000_000))
    _save(scratch / "c", [("https://example.org/p", "01-example.org.txt", "FETCHED - 9 chars")], {"01-example.org.txt": "Oldest.\n"})
    os.utime(scratch / "c" / "01-example.org.txt", (900_000_000, 900_000_000))
    where = _home()
    src.put(where, "https://example.org/already", "Here.")
    _save(scratch / "d", [("https://example.org/already", "01-example.org.txt", "FETCHED - 5 chars")], {"01-example.org.txt": "Here.\n"})
    got = src.import_saves(scratch, where)
    assert got == {"manifests": 4, "rows": 8, "excerpts": 2, "missing": 1, "distinct": 3, "imported": 2, "already": 1}
    p = src.cached(where, "https://example.org/p", max_age_days=10_000)
    assert p["text"] == "New copy.\n" and not p["exact"] and p["origin"] == f"import:{scratch / 'b'}"
    assert src.cached(where, "https://example.org/long", max_age_days=10_000)["text"] == "Part one.\nPart two.\n"
    assert src.import_saves(scratch, where)["imported"] == 0, "run again, nothing new"


# ---- the command line ----


def test_the_outcome_command_records_and_refuses(capsys: pytest.CaptureFixture[str]) -> None:
    assert src.main(["outcome", "https://example.org/p", "maybe"]) == 2
    assert "is not one of" in capsys.readouterr().err
    assert src.main(["outcome", "https://example.org/p", "rejected: only prices", "--question", "0005"]) == 0
    assert "recorded" in capsys.readouterr().out
    assert src.main(["outcome", "https://example.org/q", "nothing-found"]) == 0
    rows = src.read(_home())
    assert rows[0]["outcome"] == "rejected: only prices" and rows[0]["questions"] == ["0005"] and rows[1]["questions"] == []


def test_only_a_cited_outcome_archives_its_page(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    archived = []
    monkeypatch.setattr(src, "archive_reads", lambda root, urls: archived.extend(urls) or 0)
    for outcome in ("rejected: only prices", "nothing-found", "unreadable", "pending"):
        assert src.main(["outcome", "https://example.org/r", outcome]) == 0
    assert archived == [], "feature 309 Amendment 2: an uncited read is recorded, never archived"
    assert src.main(["outcome", "https://example.org/c", "cited:edo-enwiki"]) == 0
    assert archived == ["https://example.org/c"]
    capsys.readouterr()


def test_the_lookup_command(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "clone"
    (root / ".git").mkdir(parents=True)
    _registry(root, {"edo-enwiki": "<p>(https://en.wikipedia.org/wiki/Edo)</p>", "kyo-jawiki": "<p>(https://ja.wikipedia.org/wiki/Kyo)</p>"})
    monkeypatch.chdir(root)
    assert src.main(["lookup"]) == 2
    assert "required" in capsys.readouterr().err
    assert src.main(["lookup", "--url", "https://en.m.wikipedia.org/wiki/Edo"]) == 0
    out = capsys.readouterr().out
    assert "1 line(s) for en.wikipedia.org/wiki/Edo (2 newly filled registry entries marked cited first)" in out and "cited:edo-enwiki" in out
    _registry(root, {"a": "", "b": "", "new-one": "<p>(https://example.org/new)</p>"})
    assert src.main(["lookup", "--key", "wiki$"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("sources-consulted: 2 line(s) for keys matching 'wiki$' (1 newly filled registry entry marked cited first)")
    assert "  en.wikipedia.org/wiki/Edo\n" in out
    assert src.main(["mark-filled"]) == 0
    assert "0 filled registry entries marked cited" in capsys.readouterr().out
    (root / src.REGISTRY / "0040-late.html").write_text("<p>(https://example.org/late)</p>", encoding="utf-8")
    assert src.main(["mark-filled"]) == 0
    assert "1 filled registry entry marked cited" in capsys.readouterr().out


def test_the_import_command(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    per_url = tmp_path / "per_url.json"
    per_url.write_text(json.dumps({"example.org/x": [{"ts": "2026-09-27T10:00:00Z", "session": "s", "feature": "1"}]}), encoding="utf-8")
    scratch = tmp_path / "scratch"
    _save(scratch / "a", [("https://example.org/x", "01-example.org.txt", "FETCHED - 2 chars")], {"01-example.org.txt": "X.\n"})
    assert src.main(["import", "--per-url", str(per_url), "--scratch", str(scratch)]) == 0
    out = capsys.readouterr().out
    assert "seeded 1 ledger line(s)" in out and '"imported": 1' in out
    assert src.main(["import", "--per-url", str(tmp_path / "none.json"), "--scratch", str(tmp_path / "none")]) == 0
    assert "seeded 0" in capsys.readouterr().out
