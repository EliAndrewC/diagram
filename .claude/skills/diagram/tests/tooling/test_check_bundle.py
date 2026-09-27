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
        ('<p>NDL (https://crd.ndl.go.jp/reference/entry/index.php?page=ref_view&amp;id=1000130073)</p>', "https://crd.ndl.go.jp/reference/entry/index.php?page=ref_view&id=1000130073"),
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
    assert cb.main(["ways", "--section", "010", "--out", str(out), "--no-quotes", "--root", str(REPO)]) == 0
    names = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()}
    assert {"010-how-far-past-the-bank-does-a-bridge-land.html", "010-how-far-past-the-bank-does-a-bridge-land.notes.html"} <= names
    assert {"prepass.txt", "glossary-variants.txt", "MANIFEST.md"} <= names
    assert "sources/ritter-timber-bridges.html" in names, "non-vacuity: the entry cites a registered work"
    assert "WORDS TO RULE ON" in (out / "prepass.txt").read_text(encoding="utf-8")
    manifest = (out / "MANIFEST.md").read_text(encoding="utf-8")
    assert ".claude/skills/diagram/research/ways/010-how-far-past-the-bank-does-a-bridge-land.html" in manifest, "the origin is named"
    assert "counts on the first line" in manifest


def test_an_unmatched_question_writes_nothing(tmp_path: pathlib.Path) -> None:
    out = tmp_path / "bundle"
    assert cb.main(["ways", "--section", "no-such-question", "--out", str(out), "--no-quotes", "--root", str(REPO)]) == 2
    assert not out.exists()


def test_a_source_bundle_holds_the_entry(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fetched: list[list[str]] = []
    monkeypatch.setattr(cb, "run_script", lambda name, args, root: fetched.append([name, *args]) or (0, ""))
    out = tmp_path / "key"
    assert cb.main(["--key", "edo-enwiki", "--out", str(out), "--root", str(REPO)]) == 0
    assert (out / "sources" / "edo-enwiki.html").is_file()
    # D19: the bundle hands source-pages the passages the record quotes from the key, so a long page is excerpted
    assert fetched == [["_source_pages.py", str(out / "pages"), "https://en.wikipedia.org/wiki/Edo", "--quotes", str(out / "quotes.json")]]
    assert isinstance(json.loads((out / "quotes.json").read_text(encoding="utf-8")), list)
    fetched.clear()
    whole = tmp_path / "whole"
    assert cb.main(["--key", "edo-enwiki", "--whole", "--out", str(whole), "--root", str(REPO)]) == 0
    assert fetched == [["_source_pages.py", str(whole / "pages"), "https://en.wikipedia.org/wiki/Edo"]], "source-reader's form: the whole page, no excerpt"
    assert not (whole / "quotes.json").exists()
    assert cb.main(["--key", "no-such-key", "--out", str(tmp_path / "none"), "--root", str(REPO)]) == 2


def test_the_manifest_holds_every_copy_so_a_check_reads_one_file(tmp_path: pathlib.Path) -> None:
    out = tmp_path / "bundle"
    assert cb.main(["ways", "--section", "010", "--out", str(out), "--no-quotes", "--root", str(REPO)]) == 0
    manifest = (out / "MANIFEST.md").read_text(encoding="utf-8")
    fragment = (out / "010-how-far-past-the-bank-does-a-bridge-land.html").read_text(encoding="utf-8").rstrip()
    assert fragment in manifest and "WORDS TO RULE ON" in manifest, "the fragment and the prepass are inline"
    assert "sources/ritter-timber-bridges.html` - origin" in manifest
    assert "glossary-variants.txt` - origin" not in manifest, "the grep target stays a file of its own"


def test_a_recheck_bundle_carries_only_the_named_notes_and_their_blocks() -> None:
    fragment = '<h2 id="q">Q</h2>\n<p>One.<sup class="fn" data-note="a"></sup></p>\n<p>Two.<sup class="fn" data-note="b"></sup></p>\n<ul><li>Three.<sup class="fn" data-note="a-2"></sup></li></ul>\n'
    notes = '<li data-note="a">A</li>\n<li data-note="b">B</li>\n<li data-note="a-2">A2</li>\n'
    cut = cb.excerpt(fragment, {"a", "a-2"})
    assert '<h2 id="q">' in cut and "One." in cut and "Three." in cut and "Two." not in cut
    assert cb.notes_subset(notes, {"a-2"}) == '<li data-note="a-2">A2</li>\n'


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
    assert cb.main(["ways", "--section", "010", "--notes", "ritter-timber-bridges", "--print-notes", "--root", str(REPO)]) == 0
    out = capsys.readouterr().out
    assert 'data-note="ritter-timber-bridges"' in out and out.count("<li data-note=") == 1
    assert cb.main(["ways", "--section", "010", "--print-notes", "--root", str(REPO)]) == 2


def test_each_check_gets_only_its_own_parts(tmp_path: pathlib.Path) -> None:
    """D14: a quote-check bundle holds no word list, variant index or registry entries; a record-format bundle holds no
    quote report or registry entries - the question and its notes are in both."""
    rf = tmp_path / "rf"
    assert cb.main(["ways", "--section", "010", "--out", str(rf), "--no-quotes", "--for", "record-format", "--root", str(REPO)]) == 0
    names = {p.relative_to(rf).as_posix() for p in rf.rglob("*") if p.is_file()}
    assert {"prepass.txt", "glossary-variants.txt"} <= names and not any(n.startswith("sources/") for n in names)
    qc = tmp_path / "qc"
    assert cb.main(["ways", "--section", "010", "--out", str(qc), "--no-quotes", "--for", "quote-check", "--root", str(REPO)]) == 0
    names = {p.relative_to(qc).as_posix() for p in qc.rglob("*") if p.is_file()}
    assert "prepass.txt" not in names and "glossary-variants.txt" not in names and not any(n.startswith("sources/") for n in names)
    assert "010-how-far-past-the-bank-does-a-bridge-land.notes.html" in names


def test_a_mode_a_compound_kind_is_a_modal_the_drift_bundle_can_find() -> None:
    """Feature 268: the compound kinds (feature 262) are modals too, and entry-drift could not be pointed at one."""
    found = cb.kind_docstring(REPO, "ShrineGrove")
    assert found is not None and "compound_kinds/grounds.py" in found[0]
