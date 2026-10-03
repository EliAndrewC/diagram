"""`scripts/_check_bundle.py` (feature 250, D6): what one check agent reads, copied out of the repository.

WHAT THESE PROVE. The keys a question's notes cite are read off their links; a registry entry's pointer is read
whole, with the parenthesis that WRAPS it dropped and one that belongs to it kept; a directory that is not a
bundle is never cleared; and on the real record a question's bundle holds its fragment, its notes, the prepass,
the registry entries it cites and the variant index, all outside the repository, with a MANIFEST naming each
copy's origin. The quote-verbatim half fetches, so the real-record test skips it; `test_quote_verbatim.py` owns it.
"""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_check_bundle", REPO / "scripts" / "_check_bundle.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cb = _load()


@pytest.fixture(autouse=True)
def _owed_everywhere(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    """These tests prove a bundle's SHAPE on the real record, where this clone's delta owes nothing; the owed refusal
    (feature 311) is `test_bundle_owed.py`'s, so here every bundle is owed."""
    monkeypatch.setattr(cb.bo, "owed_for_question", lambda root, q, for_, ok: ([], for_, ""))
    monkeypatch.setattr(cb.bo, "owed_for_key", lambda root, key, whole, ok, new: ([], "source-reader" if whole else "source-applicability", ""))


def test_the_keys_a_question_cites_are_read_off_its_links() -> None:
    notes = (
        '<li data-note="edo-enwiki"><a href="https://en.wikipedia.org/wiki/Edo"><code>edo-enwiki</code></a> - x</li>\n'
        '<li data-note="edo-enwiki-2"><a href="https://en.wikipedia.org/wiki/Edo"><code>edo-enwiki</code></a> - y</li>\n'
        '<li data-note="q-2">no publicly readable source (searched 2026-09-21: <code>not-a-link</code>)</li>\n'
    )
    assert cb.cited_keys(notes) == ["edo-enwiki"], "a repeat is one key, and a bare <code> is not a citation"


@pytest.mark.parametrize(
    ("entry", "want"),
    [
        ('<p>en.wikipedia "Edo" (https://en.wikipedia.org/wiki/Edo)</p>', "https://en.wikipedia.org/wiki/Edo"),
        ("<p>kotobank (https://ja.wikipedia.org/wiki/町屋_(商家))</p>", "https://ja.wikipedia.org/wiki/町屋_(商家)"),
        ("<p>a book, no pointer</p>", ""),
        ("<p>a paper (in Japanese; https://www.agrinews.co.jp/news/index/174809), 5 August 2023</p>", "https://www.agrinews.co.jp/news/index/174809"),
        ("<p>a reference answer (https://crd.ndl.go.jp/entry/index.php?id=1&amp;page=ref_view)</p>", "https://crd.ndl.go.jp/entry/index.php?id=1&page=ref_view"),
        ('<p>NDL (https://crd.ndl.go.jp/reference/entry/index.php?page=ref_view&amp;id=1000130073)</p>', "https://crd.ndl.go.jp/reference/entry/index.php?page=ref_view&id=1000130073"),
        ("<p>an archive page (https://1073shoso.jp/www/sankyo/detail.jsp?id=18666): the survey</p>", "https://1073shoso.jp/www/sankyo/detail.jsp?id=18666"),
    ],
)
def test_a_registry_pointer_keeps_its_own_parenthesis_and_drops_the_wrapping_one(entry: str, want: str) -> None:
    assert cb.url_of(entry) == want


def test_a_key_finds_its_own_entry_and_not_a_longer_key_ending_in_it() -> None:
    assert cb.registry_entry(REPO, "edo-enwiki").name == "4220-edo-enwiki.html", "not 5780-fires-in-edo-enwiki.html"
    assert cb.registry_entry(REPO, "no-such-key") is None


def test_a_directory_that_is_not_a_bundle_is_never_cleared(tmp_path: pathlib.Path) -> None:
    (tmp_path / "keep.txt").write_text("mine", encoding="utf-8")
    with pytest.raises(SystemExit, match="not a bundle"):
        cb.fresh(tmp_path)
    assert (tmp_path / "keep.txt").is_file()
    (tmp_path / cb.MANIFEST).write_text("# Check bundle", encoding="utf-8")
    cb.fresh(tmp_path)
    assert list(tmp_path.iterdir()) == [], "a bundle is cleared before it is rewritten"


def test_a_question_bundle_on_the_real_record(tmp_path: pathlib.Path) -> None:
    out = tmp_path / "bundle"
    assert cb.main(["0087", "--out", str(out), "--no-quotes", "--root", str(REPO)]) == 0
    names = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()}
    assert {"0087-road-bridges-over-rivers-and-canals-hashi.html", "0087-road-bridges-over-rivers-and-canals-hashi.notes.html"} <= names
    assert {"prepass.txt", "glossary-variants.txt", "MANIFEST.md"} <= names
    assert "sources/ritter-timber-bridges.html" in names, "non-vacuity: the entry cites a registered work"
    assert "WORDS TO RULE ON" in (out / "prepass.txt").read_text(encoding="utf-8")
    manifest = (out / "MANIFEST.md").read_text(encoding="utf-8")
    assert ".claude/skills/diagram/research/questions/0087-road-bridges-over-rivers-and-canals-hashi.html" in manifest, "the origin is named"
    assert "counts on the first line" in manifest


def test_a_number_bundles_both_pages_of_a_question(tmp_path: pathlib.Path) -> None:
    """Feature 303: a question's number names its research page and its drawing page, each with its notes."""
    out = tmp_path / "bundle"
    assert cb.main(["0087", "--out", str(out), "--no-quotes", "--for", "record-format", "--root", str(REPO)]) == 0
    names = {p.name for p in out.iterdir()}
    assert {"0087-road-bridges-over-rivers-and-canals-hashi.html", "0087-road-bridges-over-rivers-and-canals-hashi.drawing.html"} <= names


def test_an_unmatched_question_writes_nothing(tmp_path: pathlib.Path) -> None:
    out = tmp_path / "bundle"
    assert cb.main(["9999", "--out", str(out), "--no-quotes", "--root", str(REPO)]) == 2
    assert not out.exists()


def test_a_source_bundle_holds_the_entry(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fetched: list[list[str]] = []
    monkeypatch.setattr(cb, "run_script", lambda name, args, root: fetched.append([name, *args]) or (0, ""))
    out = tmp_path / "key"
    assert cb.main(["--key", "edo-enwiki", "--out", str(out), "--root", str(REPO)]) == 0
    assert (out / "sources" / "edo-enwiki.html").is_file()
    # D19: the bundle hands source-pages the passages the record quotes from the key, so a long page is excerpted
    assert fetched == [["_source_pages.py", str(out / "pages"), "https://en.wikipedia.org/wiki/Edo", "--quotes", str(out / "quotes.json"), "--no-ledger"]]
    assert isinstance(json.loads((out / "quotes.json").read_text(encoding="utf-8")), list)
    fetched.clear()
    whole = tmp_path / "whole"
    assert cb.main(["--key", "edo-enwiki", "--whole", "--out", str(whole), "--root", str(REPO)]) == 0
    sought = ["--sought", "source-reader: the passage behind a new claim on edo-enwiki"]
    assert fetched == [["_source_pages.py", str(whole / "pages"), "https://en.wikipedia.org/wiki/Edo", "--question", "none", *sought]], "source-reader's form: the whole page, no excerpt"
    assert not (whole / "quotes.json").exists()
    fetched.clear()
    assert cb.main(["--key", "edo-enwiki", "--whole", "--question", "ways/010", "--out", str(whole), "--root", str(REPO)]) == 0
    assert fetched == [["_source_pages.py", str(whole / "pages"), "https://en.wikipedia.org/wiki/Edo", "--question", "ways/010", *sought]], "a WHOLE read carries its question to the ledger"
    assert cb.main(["--key", "no-such-key", "--out", str(tmp_path / "none"), "--root", str(REPO)]) == 2


def test_the_manifest_holds_every_copy_so_a_check_reads_one_file(tmp_path: pathlib.Path) -> None:
    out = tmp_path / "bundle"
    assert cb.main(["0087", "--out", str(out), "--no-quotes", "--root", str(REPO)]) == 0
    manifest = (out / "MANIFEST.md").read_text(encoding="utf-8")
    fragment = (out / "0087-road-bridges-over-rivers-and-canals-hashi.html").read_text(encoding="utf-8").rstrip()
    assert fragment in manifest and "WORDS TO RULE ON" in manifest, "the fragment and the prepass are inline"
    assert "sources/ritter-timber-bridges.html` - origin" in manifest
    assert "glossary-variants.txt` - origin" not in manifest, "the grep target stays a file of its own"


def test_a_recheck_bundle_carries_only_the_named_notes_and_their_blocks() -> None:
    fragment = '<h2 id="q">Q</h2>\n<p>One.<sup class="fn" data-note="a"></sup></p>\n<p>Two.<sup class="fn" data-note="b"></sup></p>\n<ul><li>Three.<sup class="fn" data-note="a-2"></sup></li></ul>\n'
    notes = '<li data-note="a">A</li>\n<li data-note="b">B</li>\n<li data-note="a-2">A2</li>\n'
    cut = cb.excerpt(fragment, {"a", "a-2"})
    assert '<h2 id="q">' in cut and "One." in cut and "Three." in cut and "Two." not in cut
    assert cb.notes_subset(notes, {"a-2"}) == '<li data-note="a-2">A2</li>\n'


def test_an_excerpt_for_the_unfootnoted_blocks_keeps_every_block_that_carries_no_note() -> None:
    """Feature 314: a batched quote-check owed `#unfootnoted` read only its notes' blocks, and the note-less block the unit was
    owed for was in no batch - with `bare`, the excerpt keeps every block carrying no note as well."""
    fragment = '<h2 id="q">Q</h2>\n<p>One.<sup class="fn" data-note="a"></sup></p>\n<p>Bare claim.</p>\n<p>Two.<sup class="fn" data-note="b"></sup></p>\n'
    assert "Bare claim." not in cb.excerpt(fragment, {"a"}), "a note's re-check reads only its blocks"
    cut = cb.excerpt(fragment, {"a"}, bare=True)
    assert "One." in cut and "Bare claim." in cut and "Two." not in cut and "every block carrying none" in cut


def test_the_unfootnoted_check_is_owed_only_where_a_quote_check_unit_names_it() -> None:
    bo = cb.bo
    unit = lambda check, subject: type("U", (), {"check": check, "subject": subject})()  # noqa: E731
    assert bo.unfootnoted_owed([unit("quote-check", "0081.drawing#unfootnoted")])
    assert not bo.unfootnoted_owed([unit("quote-check", "0081.drawing#aze-jawiki"), unit("record-format", "0081#unfootnoted")])


def test_a_recheck_excerpt_keeps_a_block_whose_close_tag_is_implicit() -> None:
    fragment = '<h2 id="q">Q</h2>\n<p>One.<sup class="fn" data-note="b"></sup>\n<p>Last.<sup class="fn" data-note="a"></sup>\n'
    cut = cb.excerpt(fragment, {"a"})
    assert "Last." in cut and "One." not in cut, "an unclosed last paragraph is still a block"


def test_a_recheck_verbatim_report_keeps_the_notes_the_excerpt_quotes(tmp_path: pathlib.Path) -> None:
    # passages are dicts and the excerpt wraps its lines: the cut used to keep nothing (feature 250, 2d)
    (tmp_path / "q.notes.html").write_text('<li data-note="a">「Zuihoden, in Otamayashita, Aoba-ku,\n  Sendai, is a mausoleum.」</li>\n', encoding="utf-8")
    (tmp_path / "q.html").write_text("<p>The daimyo pattern is an ancestral\n  mortuary precinct at Sendai.</p>\n", encoding="utf-8")
    entries = [
        {"id": "fn-1", "key": "a", "readability": "READABLE", "passages": [{"quote": "Zuihoden, in Otamayashita, Aoba-ku, Sendai, is a mausoleum.", "original": "x"}]},
        {"id": "fn-2", "key": "b", "readability": "READABLE", "passages": [], "assertion": "The daimyo pattern is an ancestral mortuary precinct at Sendai."},
        {"id": "fn-3", "key": "c", "readability": "READABLE", "passages": [{"quote": "Nothing in this bundle quotes this line at all."}], "assertion": "Elsewhere."},
    ]
    (tmp_path / "quote-verbatim.json").write_text(json.dumps({"footnotes": entries}), encoding="utf-8")
    text = cb.scoped_verbatim(tmp_path, "quote-verbatim: q\n  fn-1 a - READABLE\n")
    kept = json.loads((tmp_path / "quote-verbatim.json").read_text(encoding="utf-8"))["footnotes"]
    assert [e["id"] for e in kept] == ["fn-1", "fn-2"], "a quoted passage and a wrapped assertion both keep their note"
    assert "fn-3" not in text


def test_make_notes_prints_the_named_notes_and_refuses_without_keys(capsys: pytest.CaptureFixture[str]) -> None:
    assert cb.main(["0087-road-bridges-over-rivers-and-canals-hashi.html", "--notes", "ritter-timber-bridges", "--print-notes", "--root", str(REPO)]) == 0
    out = capsys.readouterr().out
    assert 'data-note="ritter-timber-bridges"' in out and out.count("<li data-note=") == 1
    assert cb.main(["0087", "--print-notes", "--root", str(REPO)]) == 2


def test_each_check_gets_only_its_own_parts(tmp_path: pathlib.Path) -> None:
    """D14: a quote-check bundle holds no word list, variant index or registry entries; a record-format bundle holds no
    quote report or registry entries - the question and its notes are in both."""
    rf = tmp_path / "rf"
    assert cb.main(["0087", "--out", str(rf), "--no-quotes", "--for", "record-format", "--root", str(REPO)]) == 0
    names = {p.relative_to(rf).as_posix() for p in rf.rglob("*") if p.is_file()}
    assert {"prepass.txt", "glossary-variants.txt"} <= names and not any(n.startswith("sources/") for n in names)
    qc = tmp_path / "qc"
    assert cb.main(["0086-ferries-and-fords-watashi.html", "--out", str(qc), "--no-quotes", "--for", "quote-check", "--root", str(REPO)]) == 0
    names = {p.relative_to(qc).as_posix() for p in qc.rglob("*") if p.is_file()}
    assert "prepass.txt" not in names and "glossary-variants.txt" not in names and not any(n.startswith("sources/") for n in names)
    assert "0086-ferries-and-fords-watashi.notes.html" in names
    rs = tmp_path / "rs"
    assert cb.main(["0087", "--out", str(rs), "--no-quotes", "--for", "record-style", "--root", str(REPO)]) == 0
    names = {p.relative_to(rs).as_posix() for p in rs.rglob("*") if p.is_file()}
    assert {"STYLE.md", "style-prepass.txt", "glossary-variants.txt"} <= names and "prepass.txt" not in names, "feature 292: record-style reads the guide itself, and its own prepass"
    assert not any(n.endswith(".notes.html") for n in names), "feature 292: record-style judges prose - no notes unless it audits a merge"
    rsx = tmp_path / "rsx"
    old = REPO / ".claude/skills/diagram/research/questions" / next(n for n in names if n.endswith(".html") and n[:4].isdigit())
    assert cb.main(["0087", "--out", str(rsx), "--no-quotes", "--for", "record-style", "--extra", str(old), "--root", str(REPO)]) == 0
    assert any(p.name.endswith(".notes.html") for p in rsx.iterdir()), "a merge audit accounts for the notes, so it is handed them"
    ed = tmp_path / "ed"
    assert cb.main(["0087", "--out", str(ed), "--no-quotes", "--for", "entry-drift", "--root", str(REPO)]) == 0
    assert not any(p.name.endswith(".notes.html") for p in ed.iterdir()), "entry-drift compares a modal with the prose"
    tc = tmp_path / "tc"
    assert cb.main(["0036", "--out", str(tc), "--no-quotes", "--for", "translation-check", "--root", str(REPO)]) == 0
    assert (tc / "translations.txt").read_text(encoding="utf-8").startswith("translation-owed: "), "the owed pairs, nothing else"
    assert not any(p.name.endswith(".notes.html") for p in tc.iterdir())


def test_a_quote_check_on_notes_over_the_budget_is_split_into_batches(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 292: the size cap counts prose only, so a large topic's notes are bounded where they are read - the
    quote-check gets them in runs of at most `NOTES_BUDGET` bytes, one bundle (and one agent) each."""
    monkeypatch.setattr(cb, "NOTES_BUDGET", 1_000)
    batches = cb.note_batches(REPO, "0036-groves-of-trees-around-farmhouses-yashikirin.html")
    assert len(batches) > 1 and len({k for b in batches for k in b}) == sum(len(b) for b in batches), "every note once"
    out = tmp_path / "qc"
    assert cb.main(["0036-groves-of-trees-around-farmhouses-yashikirin.html", "--out", str(out), "--no-quotes", "--for", "quote-check", "--root", str(REPO)]) == 0
    assert {p.name for p in out.iterdir()} == {f"batch-{i}" for i in range(1, len(batches) + 1)}
    notes = (out / "batch-1").glob("*.notes.html")
    assert all('data-orig="' in n.read_text(encoding="utf-8") or "original:" not in n.read_text(encoding="utf-8") for n in notes), "no original in a check's notes"
    monkeypatch.setattr(cb, "NOTES_BUDGET", 10**9)
    assert len(cb.note_batches(REPO, "0036-groves-of-trees-around-farmhouses-yashikirin.html")) == 1


def test_a_mode_a_compound_kind_is_a_modal_the_drift_bundle_can_find() -> None:
    """Feature 268: the compound kinds (feature 262) are modals too, and entry-drift could not be pointed at one."""
    found = cb.kind_docstring(REPO, "ShrineGrove")
    assert found is not None and "compound_kinds/grounds.py" in found[0]


def test_a_shared_modal_name_is_qualified_by_its_module() -> None:
    """Feature 265: the map's `Well` (classes/water_and_ways.py) and the sheet's (compound_kinds/household.py) share a
    name, and the bare name only ever reached the first; `household.Well` reaches the sheet's."""
    bare = cb.kind_docstring(REPO, "Well")
    sheet = cb.kind_docstring(REPO, "household.Well")
    assert bare and sheet and "classes/water_and_ways.py" in bare[0] and "compound_kinds/household.py" in sheet[0]
    assert cb.kind_docstring(REPO, "nosuchmodule.Well") is None


# ---- feature 288: a WHOLE read is a research read and is ledgered; an excerpt is a re-check and is not ----


def test_the_whole_bundle_prints_and_ledgers_and_the_excerpt_does_not(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """SC-001, end to end with no network: the key's page is in the page cache, so the real `_source_pages.py` run
    reads it from there. The WHOLE bundle prints the page's earlier read and appends `pending` with its question; the
    excerpt bundle of the same key appends nothing."""
    src = _load_sources()
    where = pathlib.Path(os.environ["L7R_SOURCES_HOME"])
    url = cb.url_of(cb.registry_entry(REPO, "edo-enwiki").read_text(encoding="utf-8"))
    src.put(where, url, "Edo was the seat of the shogunate. It grew large.")
    src.append(where, [src.line({"feature": "250", "clone": "x", "session": "s"}, url, "nothing-found", ["ways/010"])])
    assert cb.main(["--key", "edo-enwiki", "--whole", "--question", "0081", "--out", str(tmp_path / "w"), "--root", str(REPO)]) == 0
    out = capsys.readouterr().out
    assert "read 1 time(s) before:" in out and "nothing-found  q: ways/010" in out
    assert "from the page cache" in (tmp_path / "w" / "pages" / "MANIFEST.txt").read_text(encoding="utf-8")
    assert [(r["outcome"], r["questions"]) for r in src.read(where)][1:] == [("pending", ["0081"])]
    assert cb.main(["--key", "edo-enwiki", "--out", str(tmp_path / "e"), "--root", str(REPO)]) == 0
    assert "sources-consulted:" not in capsys.readouterr().out
    assert len(src.read(where)) == 2, "the excerpt bundle wrote no ledger line"
    assert cb.ledger_part("pointer | file | state\nx\n") == ""


def _load_sources():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_sources", REPO / "scripts" / "_sources.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_quote_check_s_bundle_carries_the_cached_text_of_each_residue_page(tmp_path: pathlib.Path) -> None:
    """Feature 288 FR-010, FR-011: the pages a quotation was NOT found verbatim on are saved into the bundle from the
    page cache only - a page it does not hold is named NOT-CACHED, never fetched - and a clean report saves nothing."""
    src = _load_sources()
    out = tmp_path / "b"
    out.mkdir()
    assert cb.residue_pages(out) == 0, "no report, nothing to save"
    report = {
        "footnotes": [
            {"links": ["https://example.org/ok"], "passages": [{"quotation": "VERBATIM"}]},
            {"links": ["https://example.org/differs", "SOURCES.html#own"], "passages": [{"quotation": "VERBATIM"}, {"quotation": "DIFFERS"}]},
            {"links": ["https://example.org/gone", "https://example.org/differs"], "passages": [{"quotation": "UNFETCHABLE"}]},
            {"links": ["https://example.org/nothing-quoted"], "passages": []},
        ]
    }
    (out / "quote-verbatim.json").write_text(json.dumps(report), encoding="utf-8")
    src.put(pathlib.Path(os.environ["L7R_SOURCES_HOME"]), "https://example.org/differs", "The page. Its own words.")
    assert cb.residue_pages(out) == 2
    manifest = (out / "pages" / "MANIFEST.txt").read_text(encoding="utf-8").splitlines()
    assert manifest[1].startswith("https://example.org/differs | 01-example.org.txt | FETCHED - ") and "from the page cache" in manifest[1]
    assert manifest[2].startswith("https://example.org/gone | - | NOT-CACHED - not in the page cache")
    assert (out / "pages" / "01-example.org.txt").read_text(encoding="utf-8") == "The page.\nIts own words.\n"
    assert cb.NotCached.refused == {}


def test_an_entry_bundle_lists_its_residue_pages(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The quote-check bundle names its `pages/` in the MANIFEST when the report left a residue (no network: the
    quote-verbatim run is replaced by the report it would write)."""
    src = _load_sources()
    src.put(pathlib.Path(os.environ["L7R_SOURCES_HOME"]), "https://example.org/differs", "Its own words.")
    real = cb.run_script

    def run(name: str, args: list[str], root: pathlib.Path) -> tuple[int, str]:
        if name != "_quote_verbatim.py":
            return real(name, args, root)
        report = {"footnotes": [{"links": ["https://example.org/differs"], "passages": [{"quotation": "DIFFERS"}]}]}
        pathlib.Path(args[args.index("--json") + 1]).write_text(json.dumps(report), encoding="utf-8")
        return 0, "quote-verbatim: 1 footnote"

    monkeypatch.setattr(cb, "run_script", run)
    out = tmp_path / "q"
    assert cb.main(["0086-ferries-and-fords-watashi.html", "--for", "quote-check", "--out", str(out), "--root", str(REPO)]) == 0
    assert "| `pages/` | `the host's page cache (feature 288)` |" in (out / "MANIFEST.md").read_text(encoding="utf-8")
    assert (out / "pages" / "01-example.org.txt").is_file()
