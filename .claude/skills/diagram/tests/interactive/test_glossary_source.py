"""The glossary, written one word per file (feature 259).

The property everything rests on, over the REAL glossary rather than a fixture: taking it apart one
term at a time and putting it back gives the same bytes. `glossary.json` is read by the engine at
import, by the page writer, and by every test over the record's visible text, so a byte that moved
would move under all of them at once.

Term ORDER is asserted too, and separately, because byte-identity alone would not explain to the next
reader why it matters: the assembled key order IS the file's order. It was load-bearing in a sharper
way when this feature began - 7 variants were claimed by two terms each and the page's matcher let the
later one win (R2) - and the last test in this file is what keeps that from returning.
"""

from __future__ import annotations

import json
import os
import pathlib

import pytest

from l7r.diagram.interactive.glossary_source import (
    SOURCE,
    TERMS,
    GlossaryError,
    assemble,
    check,
    file_name,
    split,
    term_files,
)

GLOSSARY = pathlib.Path(SOURCE)


def test_the_glossary_splits_and_assembles_back_to_the_same_bytes() -> None:
    """FR-004, SC-003: the file a reader's tooltips are built from does not move by one byte."""
    raw = GLOSSARY.read_text(encoding="utf-8")
    assert assemble(split(raw)) == raw


def test_the_split_keeps_the_terms_in_their_file_order() -> None:
    """FR-003: the assembled object's key order IS the file's order, so byte-identity needs it kept."""
    raw = GLOSSARY.read_text(encoding="utf-8")
    assert [t["term"] for t in split(raw)] == list(json.loads(raw))


def test_a_term_file_is_named_for_its_term_behind_a_gapped_prefix() -> None:
    """FR-002, and the GM's own form: 'each word in the glossary could be the name of the file'."""
    assert file_name(1, "girder") == "0010-girder.json"
    assert file_name(2, "girder") == "0020-girder.json"
    assert file_name(37, "bettō") == "0370-bettō.json", "a macron is a filename character"
    assert file_name(9, "dS/m") == "0090-dS%2Fm.json", "a slash is not"


def test_the_term_is_read_from_the_file_and_never_from_its_name() -> None:
    """A filename is a convenience; `dS/m` is why it cannot always be the whole truth (R3)."""
    terms = split(GLOSSARY.read_text(encoding="utf-8"))
    encoded = [t for t in terms if t["term"] == "dS/m"]
    assert encoded, "the record still carries the term this rule exists for"
    assert "%2F" not in json.dumps(encoded[0], ensure_ascii=False), "the file records the term itself"


def test_every_term_file_is_small_enough_to_read_whole() -> None:
    """SC-001: the point of the split - a check opens 154 bytes, not 137,059."""
    terms = split(GLOSSARY.read_text(encoding="utf-8"))
    sizes = sorted(len(json.dumps(t, ensure_ascii=False).encode()) for t in terms)
    assert sizes[len(sizes) // 2] < 400 and sizes[-1] < 1000, "the median term and the largest"


def test_no_variant_is_claimed_by_two_terms_or_listed_twice() -> None:
    """FR-011, SC-006: otherwise the order FR-003 preserves stays load-bearing where nobody looks.

    The rule when it fires: the term whose own NAME is the variant keeps it (R2).
    """
    terms = split(GLOSSARY.read_text(encoding="utf-8"))
    claimed: dict[str, list[str]] = {}
    twice = []
    for entry in terms:
        seen = set()
        for variant in entry["variants"]:
            key = variant.lower()
            if key in seen:
                twice.append((entry["term"], variant))
            seen.add(key)
            claimed.setdefault(key, []).append(entry["term"])
    clash = {v: ts for v, ts in claimed.items() if len(set(ts)) > 1}
    assert not clash, f"a variant two terms claim - the page shows whichever is later in the file: {clash}"
    assert not twice, f"a term listing one variant twice: {twice}"


def test_a_directory_of_term_files_is_read_back_in_prefix_order(tmp_path: pathlib.Path) -> None:
    """What the assembly does on disk, and the refusals it makes rather than guessing."""
    (tmp_path / TERMS).mkdir(parents=True)
    for name, body in (("0010-a.json", {"term": "a", "variants": ["a"], "def": "first"}), ("0020-b.json", {"term": "b", "variants": ["b"], "def": "second"})):
        (tmp_path / TERMS / name).write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
    assert [t["term"] for t in term_files(str(tmp_path))] == ["a", "b"]

    (tmp_path / TERMS / "0020-c.json").write_text(json.dumps({"term": "c", "variants": ["c"], "def": "third"}, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(GlossaryError, match="both claim prefix"):
        term_files(str(tmp_path))
    (tmp_path / TERMS / "0020-c.json").unlink()

    (tmp_path / TERMS / "notes.txt").write_text("stray", encoding="utf-8")
    with pytest.raises(GlossaryError, match="not a term file"):
        term_files(str(tmp_path))
    (tmp_path / TERMS / "notes.txt").unlink()

    (tmp_path / TERMS / "0030-d.json").write_text(json.dumps({"term": "different", "variants": ["d"], "def": "fourth"}, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(GlossaryError, match="its filename says"):
        term_files(str(tmp_path))


def test_a_committed_glossary_that_differs_from_its_term_files_is_reported() -> None:
    """FR-005, FR-006: what the gate and the push run."""
    assert check() == [], "run `make glossary`"


def test_the_split_and_the_assembly_on_disk(tmp_path: pathlib.Path) -> None:
    """The one-time split, the write-back, and the refusal that stops a bad split being committed."""
    from l7r.diagram.interactive import glossary_source as gs

    (tmp_path / "assets").mkdir()
    # A SYNTHETIC glossary of two terms. `girder` is not in the real one - `record-format` has
    # proposed it three times and nobody has added it - and it is used here precisely because this
    # tree is not the record: the case under test is the encoding of `dS/m`, which is real.
    small = {"girder": {"def": "the main beam", "variants": ["girder", "girders"]}, "dS/m": {"def": "a salinity unit", "variants": ["dS/m"]}}
    raw = json.dumps(small, ensure_ascii=False, indent=1) + "\n"
    (tmp_path / "assets" / "glossary.json").write_text(raw, encoding="utf-8")
    written = gs.write_term_files(str(tmp_path))
    assert len(written) == 2 and (tmp_path / TERMS / "0020-dS%2Fm.json").is_file()
    index = str(tmp_path / "variants.txt")
    assert gs.write_index(str(tmp_path), index) == 1 and gs.write_index(str(tmp_path), index) == 0
    assert gs.check(str(tmp_path), index) == [], "the split assembles back to the committed bytes"
    assert gs.write_source(str(tmp_path)) == 0, "nothing to write when it already matches"

    # the index, and what it is for
    index = gs.variant_index(gs.term_files(str(tmp_path)))
    assert "girders\tgirder\n" in index and "ds/m\tdS/m\n" in index
    # a term file edited by hand, then assembled back
    one = tmp_path / TERMS / "0010-girder.json"
    one.write_text(one.read_text(encoding="utf-8").replace("the main beam", "the beam"), encoding="utf-8")
    assert gs.check(str(tmp_path), index)[0] == os.path.join("assets", "glossary.json")
    assert gs.write_source(str(tmp_path)) == 1
    assert "the beam" in (tmp_path / "assets" / "glossary.json").read_text(encoding="utf-8")


def test_a_split_that_would_not_rebuild_is_refused(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from l7r.diagram.interactive import glossary_source as gs

    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "glossary.json").write_text(json.dumps({"a": {"def": "x", "variants": ["a"]}}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    monkeypatch.setattr(gs, "assemble", lambda terms: "not the file at all")
    with pytest.raises(GlossaryError, match="does not assemble back"):
        gs.write_term_files(str(tmp_path))


def test_the_refusals_that_name_the_file(tmp_path: pathlib.Path) -> None:
    from l7r.diagram.interactive import glossary_source as gs

    with pytest.raises(GlossaryError, match="no term files"):
        gs.term_files(str(tmp_path))
    with pytest.raises(GlossaryError, match="not a term file"):
        gs.position_of("glossary.json")
    with pytest.raises(GlossaryError, match="one home"):
        gs.assemble([{"term": "a", "def": "x", "variants": []}, {"term": "a", "def": "y", "variants": []}])
    assert gs.check(str(tmp_path)) == [], "a tree with no term files is not stale, it is unsplit"
    assert "first difference at character 1" in gs._first_difference("abc", "axc")
    assert "one is 3 characters" in gs._first_difference("abc", "ab")


def test_the_command_checks_assembles_and_splits(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """`make glossary` and its three modes, through the CLI the Makefile calls."""
    from l7r.diagram.interactive import glossary_source as gs
    from l7r.diagram.tools import glossary_asset

    assert glossary_asset.main(["--check"]) == 0, "the committed tree is in sync"
    assert "in sync" in capsys.readouterr().out

    monkeypatch.setattr(gs, "check", lambda *a, **k: ["assets/glossary.json"])
    assert glossary_asset.main(["--check"]) == 1
    assert "STALE against its per-term files" in capsys.readouterr().err

    monkeypatch.setattr(gs, "check", lambda *a, **k: [])
    out = tmp_path / "glossary.js"
    assert glossary_asset.main(["--path", str(out)]) == 0, "it writes the asset where it is told"
    assert out.read_text(encoding="utf-8").startswith("// DERIVED FILE")
    assert glossary_asset.main(["--check", "--path", str(tmp_path / "missing.js")]) == 1
    assert "glossary.js: STALE" in capsys.readouterr().err

    split_calls = []
    monkeypatch.setattr(gs, "write_term_files", lambda *a, **k: split_calls.append(1) or ["one", "two"])
    assert glossary_asset.main(["--split"]) == 0 and split_calls == [1]
    assert "split into 2 term file(s)" in capsys.readouterr().out

    # THE RELOAD BRANCH: the asset is derived from the file the assembly just wrote, not from the one
    # `interactive/glossary.py` imported at start-up (feature 259, D2).
    reloaded = []
    monkeypatch.setattr(gs, "write_source", lambda *a, **k: 1)
    monkeypatch.setattr(gs, "write_index", lambda *a, **k: 0)
    monkeypatch.setattr(glossary_asset.importlib, "reload", lambda mod: reloaded.append(mod))
    assert glossary_asset.main(["--path", str(out)]) == 0 and reloaded, "it reloads after it assembles"
