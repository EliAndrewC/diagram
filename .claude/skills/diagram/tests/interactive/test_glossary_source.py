"""The glossary, written one word per file (feature 259).

The property everything rests on, over the REAL glossary rather than a fixture: taking it apart one
term at a time and putting it back gives the same bytes. `glossary.json` is read by the engine at
import, by the page writer, and by every test over the record's visible text, so a byte that moved
would move under all of them at once.

Term ORDER is asserted too, and separately, because it is load-bearing in a way that byte-identity
alone would not explain to the next reader: 7 variants are claimed by two terms each, and the page's
matcher lets the later one win (`specs/259-glossary-per-term/research.md` R2).
"""

from __future__ import annotations

import json
import pathlib

import pytest

from l7r.diagram.interactive.glossary_source import (
    GlossaryError,
    SOURCE,
    TERMS,
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
    """FR-003: sorting them would change which definition a reader is shown for 7 variants (R2)."""
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
    for name, body in (("0010-a.json", {"term": "a", "variants": ["a"], "def": "first"}),
                       ("0020-b.json", {"term": "b", "variants": ["b"], "def": "second"})):
        (tmp_path / TERMS / name).write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
    assert [t["term"] for t in term_files(str(tmp_path))] == ["a", "b"]

    (tmp_path / TERMS / "0020-c.json").write_text(
        json.dumps({"term": "c", "variants": ["c"], "def": "third"}, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(GlossaryError, match="both claim prefix"):
        term_files(str(tmp_path))
    (tmp_path / TERMS / "0020-c.json").unlink()

    (tmp_path / TERMS / "notes.txt").write_text("stray", encoding="utf-8")
    with pytest.raises(GlossaryError, match="not a term file"):
        term_files(str(tmp_path))
    (tmp_path / TERMS / "notes.txt").unlink()

    (tmp_path / TERMS / "0030-d.json").write_text(
        json.dumps({"term": "different", "variants": ["d"], "def": "fourth"}, ensure_ascii=False),
        encoding="utf-8")
    with pytest.raises(GlossaryError, match="its filename says"):
        term_files(str(tmp_path))


def test_a_committed_glossary_that_differs_from_its_term_files_is_reported() -> None:
    """FR-005, FR-006: what the gate and the push run."""
    assert check() == [], "run `make glossary`"
