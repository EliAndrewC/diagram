"""`scripts/_check_bundle.py` (feature 250, D6): what one check agent reads, copied out of the repository.

WHAT THESE PROVE. The keys a question's notes cite are read off their links; a registry entry's pointer is read
whole, with the parenthesis that WRAPS it dropped and one that belongs to it kept; a directory that is not a
bundle is never cleared; and on the real record a question's bundle holds its fragment, its notes, the prepass,
the registry entries it cites and the variant index, all outside the repository, with a MANIFEST naming each
copy's origin. The quote-verbatim half fetches, so the real-record test skips it; `test_quote_verbatim.py` owns it.
"""

from __future__ import annotations

import importlib.util
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
    assert str(out / "REPORT.md") in manifest


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
    assert fetched == [["_source_pages.py", str(out / "pages"), "https://en.wikipedia.org/wiki/Edo"]]
    assert cb.main(["--key", "no-such-key", "--out", str(tmp_path / "none"), "--root", str(REPO)]) == 2
