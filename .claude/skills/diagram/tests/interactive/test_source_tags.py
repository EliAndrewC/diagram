"""Feature 305: the registry's source tags - the vocabulary, the sections, the marker, the labels and every refusal.

FR-010: an entry missing a facet, carrying a value the vocabulary does not hold, or whose primary tags no section takes
is refused, naming the entry (SC-002's three seeded faults are the Catalog tests below and the build test in
test_record_site.py). The files themselves are refused when malformed, naming the file."""

from __future__ import annotations

import json
import pathlib

import pytest

from l7r.diagram.interactive.record import source_tags as st
from l7r.diagram.interactive.sources import RESEARCH_DIR
from tests import _flat_record as fr


@pytest.fixture
def rec(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / st.VOCABULARY).write_text(json.dumps(fr.SOURCE_TAGS), encoding="utf-8")
    (tmp_path / st.SECTIONS).write_text(json.dumps(fr.SOURCE_SECTIONS), encoding="utf-8")
    return tmp_path


def _vocab(rec: pathlib.Path) -> st.Vocabulary:
    return st.load_vocabulary(str(rec))


def _write(rec: pathlib.Path, name: str, data: object) -> None:
    (rec / name).write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")


# ------------------------------------------------------------------------------------------------- the real files


def test_the_real_vocabulary_and_sections_load_and_every_period_states_every_regions_cut_off() -> None:
    """FR-003 (GM message 2): each period explanation states its cut-off and why, by region."""
    vocab = st.load_vocabulary(RESEARCH_DIR)
    sections = st.load_sections(RESEARCH_DIR, vocab)
    assert [s.id for s in sections][0] == "works-canon" and sections[0].canon
    premodern = vocab.known("period")["premodern"].description
    for words in ("1868", "1895", "1876", "Ryukyu", "Vietnam", "Taiwan", "1800", "elsewhere", "General"):
        assert words in premodern, words
    assert "1950" in vocab.known("period")["modern-preindustrial"].description and "1955" in vocab.known("period")["present-day"].description


def test_every_combination_of_real_primary_tags_has_a_section() -> None:
    """FR-007's closing rule: the last section takes the regions Europe, elsewhere and general whatever the period, so
    no combination of vocabulary values is left without a home."""
    vocab = st.load_vocabulary(RESEARCH_DIR)
    sections = st.load_sections(RESEARCH_DIR, vocab)
    for p in vocab.known("period"):
        for r in vocab.known("region"):
            for k in vocab.known("kind"):
                assert st.home(sections, st.SourceTags((p,), (r,), (k,))) is not None, (p, r, k)


# ------------------------------------------------------------------------------------------------- the files' refusals


@pytest.mark.parametrize(
    ("data", "words"),
    [
        ("{nope", "not JSON"),
        ({"period": []}, "holds exactly period, region, kind and canon"),
        ({**fr.SOURCE_TAGS, "period": []}, "`period` is a non-empty list"),
        ({**fr.SOURCE_TAGS, "kind": [{"id": "Bad Id", "name": "x", "description": "y"}]}, "a value is an object"),
        ({**fr.SOURCE_TAGS, "kind": [{"id": "a", "name": "x", "description": "y"}, {"id": "a", "name": "x", "description": "y"}]}, "declared twice"),
        ({**fr.SOURCE_TAGS, "canon": {"id": "canon", "name": "x"}}, "canon: a value is an object"),
    ],
)
def test_a_malformed_vocabulary_is_refused_by_name(rec: pathlib.Path, data: object, words: str) -> None:
    _write(rec, st.VOCABULARY, data)
    with pytest.raises(st.SourceTagError, match=words):
        _vocab(rec)


def test_a_missing_file_is_refused_by_name(tmp_path: pathlib.Path) -> None:
    with pytest.raises(st.SourceTagError, match="source-tags.json: missing"):
        st.load_vocabulary(str(tmp_path))
    (tmp_path / st.VOCABULARY).write_text(json.dumps(fr.SOURCE_TAGS), encoding="utf-8")
    with pytest.raises(st.SourceTagError, match="source-sections.json: missing - the record's source sections"):
        st.load_sections(str(tmp_path), st.load_vocabulary(str(tmp_path)))


_CANON = {"id": "works-canon", "title": "Canon", "canon": True}
_JAPAN = {"id": "works-japan", "title": "Japan", "takes": [{"region": "japan"}]}


@pytest.mark.parametrize(
    ("data", "words"),
    [
        ([], "an object with a `sections` list"),
        ({"sections": [{"id": "japan", "title": "J", "takes": [{"region": "japan"}]}]}, "starting `works-`"),
        ({"sections": [_CANON, _JAPAN, _JAPAN]}, "the id is used twice"),
        ({"sections": [_CANON, {"id": "works-x", "takes": [{"region": "japan"}]}]}, "no `title`"),
        ({"sections": [_CANON, {"id": "works-x", "title": "X"}]}, "takes nothing - a section other than the canon one"),
        ({"sections": [_JAPAN]}, "exactly one section is the canon section"),
        ({"sections": [_CANON, {**_CANON, "id": "works-canon-2"}]}, "exactly one section is the canon section"),
        ({"sections": [_CANON, {"id": "works-x", "title": "X", "takes": ["japan"]}]}, "a clause is an object"),
        ({"sections": [_CANON, {"id": "works-x", "title": "X", "takes": [{"level": "detail"}]}]}, "`level` - a clause tests only"),
        ({"sections": [_CANON, {"id": "works-x", "title": "X", "takes": [{"region": ["japan", "korea"]}]}]}, "no region value `korea`"),
    ],
)
def test_malformed_sections_are_refused_by_name(rec: pathlib.Path, data: object, words: str) -> None:
    _write(rec, st.SECTIONS, data)
    with pytest.raises(st.SourceTagError, match=words):
        st.load_sections(str(rec), _vocab(rec))


# ------------------------------------------------------------------------------------------------- the marker


def test_a_marker_parses_with_its_first_value_primary_and_writes_back_the_same(rec: pathlib.Path) -> None:
    tags = st.parse("<p>x</p>\n<!-- tags: kind=primary; region=japan,china; period=premodern -->\n", "e", _vocab(rec))
    assert tags == st.SourceTags(("premodern",), ("japan", "china"), ("primary",))
    assert tags.primary("region") == "japan"
    assert tags.marker() == "<!-- tags: period=premodern; region=japan,china; kind=primary -->"
    assert st.parse("<p>no marker</p>", "e", _vocab(rec)) is None


@pytest.mark.parametrize(
    ("marker", "words"),
    [
        ("<!-- tags: period=premodern; region=japan; kind=primary --><!-- tags: period=timeless; region=japan; kind=primary -->", "two tags markers"),
        ("<!-- tags: period=premodern; region=japan; kind=primary; level=detail -->", "each facet once"),
        ("<!-- tags: period=premodern; period=timeless; region=japan; kind=primary -->", "each facet once"),
        ("<!-- tags: period=premodern; region=japan -->", "e: no kind in its tags"),
        ("<!-- tags: period=<period>; region=japan; kind=primary -->", "`period=<period>` - not a period value; the values are premodern, present-day, timeless"),
        ("<!-- tags: period=premodern; region=japan,japan; kind=primary -->", "a region value is stated twice"),
    ],
)
def test_a_bad_marker_is_refused_naming_the_entry(rec: pathlib.Path, marker: str, words: str) -> None:
    with pytest.raises(st.SourceTagError, match=words):
        st.parse(marker, "e", _vocab(rec))


# ------------------------------------------------------------------------------------------------- homing and labels


def test_a_work_lives_in_the_first_section_its_primary_tags_match(rec: pathlib.Path) -> None:
    vocab = _vocab(rec)
    sections = st.load_sections(str(rec), vocab)
    assert st.home(sections, None).id == "works-canon"  # type: ignore[union-attr]
    assert st.home(sections, st.SourceTags(("premodern",), ("japan", "general"), ("primary",))).id == "works-premodern-japan"  # type: ignore[union-attr]
    assert st.home(sections, st.SourceTags(("timeless",), ("general",), ("reference",))).id == "works-general"  # type: ignore[union-attr]
    assert st.home(sections, st.SourceTags(("premodern",), ("china", "japan"), ("primary",))) is None, "the primary region decides, not the second"
    with_clauses = [st.Section("works-canon", "Canon", "", True, ({"period": ("timeless",)},)), *sections[1:]]
    assert st.home(with_clauses, st.SourceTags(("timeless",), ("general",), ("reference",))).id == "works-canon", "the canon section's clauses take works too"  # type: ignore[union-attr]


def test_labels_carry_their_explanations_escaped_and_the_marker_is_stripped(rec: pathlib.Path) -> None:
    vocab = _vocab(rec)
    chips = st.labels_html(st.SourceTags(("premodern",), ("japan", "china"), ("reference",)), vocab)
    assert chips.startswith('<p class="srctags">') and chips.count('class="srctag ') == 4
    assert 'class="srctag srctag-period" data-def="Before the factories." title="Before the factories.">Premodern</span>' in chips
    assert chips.index("Japan<") < chips.index("China<") < chips.index("Reference<"), "facet order, then each facet's own order"
    assert 'data-def="An encyclopedia &amp; co."' in chips
    assert st.labels_html(None, vocab) == '<p class="srctags"><span class="srctag srctag-canon" data-def="The GM&#x27;s notes." title="The GM&#x27;s notes.">Setting canon</span></p>'
    assert st.strip_marker("<p>a</p>\n<!-- tags: period=premodern; region=japan; kind=primary -->\n") == "<p>a</p>\n"


def test_a_section_heading_carries_its_description_only_when_it_has_one(rec: pathlib.Path) -> None:
    sections = {s.id: s for s in st.load_sections(str(rec), _vocab(rec))}
    assert st.section_heading(sections["works-canon"], 3, "x") == '<h3 class="works-section" id="x">Setting canon</h3>\n<p class="works-section-desc"><em>The notes.</em></p>'
    assert st.section_heading(sections["works-present-day"], 3, "y") == '<h3 class="works-section" id="y">Present day</h3>'


# ------------------------------------------------------------------------------------------------- the catalog (SC-002)


def test_the_catalog_refuses_each_fault_by_entry_and_groups_the_rest(rec: pathlib.Path) -> None:
    good = "<!-- tags: period=premodern; region=japan; kind=primary -->"
    entries = {
        "ok": good,
        "now": "<!-- tags: period=present-day; region=china; kind=reference -->",
        "canon": "<p>l7r.md</p>",
        "untagged": "<p>no marker</p>",
        "unknown": "<!-- tags: period=medieval; region=japan; kind=primary -->",
        "homeless": "<!-- tags: period=timeless; region=japan; kind=primary -->",
        "tagged-canon": good,
    }
    cat = st.Catalog(str(rec), entries, {"canon", "tagged-canon"}, "sources")
    errors = "\n".join(cat.errors)
    assert "sources/ untagged: no tags - every keyed work states" in errors
    assert "sources/ unknown: `period=medieval` - not a period value" in errors
    assert "sources/ homeless: no section of source-sections.json takes the primary tags period=timeless, region=japan, kind=primary" in errors
    assert "sources/ tagged-canon: a canon entry (the GM's own notes) carries no tags" in errors
    assert len(cat.errors) == 4
    assert [(s.id, keys) for s, keys in cat.grouped(["now", "untagged", "ok", "canon"])] == [("works-canon", ["canon"]), ("works-premodern-japan", ["ok"]), ("works-present-day", ["now"])]
    assert "Setting canon" in cat.labels("canon") and cat.labels("untagged") == ""


# ------------------------------------------------------------------------------------------------- the agent contract (FR-012)


def test_the_source_applicability_contract_carries_the_current_vocabulary() -> None:
    """A defined agent launches without the record's CLAUDE.md files, so its contract carries the explanations it
    judges tags against; they are derived, and this fails while they are stale."""
    from l7r.diagram.tools import source_tags_contract as tool  # noqa: PLC0415

    assert tool.main(["--check"]) == 0, "run make source-tags-contract"


def test_the_contract_tool_rewrites_a_stale_block_checks_and_refuses_one_with_no_markers(rec: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    from l7r.diagram.tools import source_tags_contract as tool  # noqa: PLC0415

    contract = rec / "agent.md"
    contract.write_text(f"head\n{st.CONTRACT_OPEN}\nold\n{st.CONTRACT_CLOSE}\ntail\n", encoding="utf-8")
    args = ["--contract", str(contract), "--research-dir", str(rec)]
    assert tool.main([*args, "--check"]) == 1 and "stale" in capsys.readouterr().err
    assert tool.main(args) == 0 and "rewrote" in capsys.readouterr().out
    text = contract.read_text(encoding="utf-8")
    assert "- `period=premodern` - **Premodern**: Before the factories." in text and "- (no marker) - **Setting canon**: The GM's notes." in text
    assert text.startswith("head\n") and text.endswith("tail\n") and "old" not in text
    assert tool.main([*args, "--check"]) == 0 and "current" in capsys.readouterr().out
    contract.write_text("no markers\n", encoding="utf-8")
    assert tool.main(args) == 1 and "two markers are missing" in capsys.readouterr().err
