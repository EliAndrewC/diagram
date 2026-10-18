"""Feature 389: the record's money section, declared before its first question, and the protocol a money request is
worked by (`research/money-requests.md`).

A section `awaiting` its first question builds empty; a question tagged only `money`, with no drawing page, is homed in
it; once one is, the `awaiting` line is refused as stale. The real record carries the tag, the section and the protocol."""

from __future__ import annotations

import json
import pathlib

import pytest

from l7r.diagram.interactive.record import contents as ct
from l7r.diagram.interactive.record import questions as qs
from l7r.diagram.interactive.sources import RESEARCH_DIR
from tests import _flat_record as fr

MONEY = {"name": "Money and prices", "description": "Coinage, prices, wages."}


def _money_record(tmp: pathlib.Path, *, awaiting: str, question: bool) -> pathlib.Path:
    rec = fr.write(tmp)
    tags = json.loads((rec / "tags.json").read_text(encoding="utf-8"))
    tags["subject"]["money"] = MONEY
    (rec / "tags.json").write_text(json.dumps(tags), encoding="utf-8")
    data = json.loads((rec / "contents.json").read_text(encoding="utf-8"))
    section = {"id": "money", "title": "Money and prices", "takes": [{"primary": "money"}], "sections": []}
    if awaiting:
        section["awaiting"] = awaiting
    data["sections"].append(section)
    (rec / "contents.json").write_text(json.dumps(data), encoding="utf-8")
    if question:
        (rec / "questions" / "0005-land-prices.html").write_text(
            '<h2 id="land-prices">Land prices</h2>\n<!-- tags: subject=money; setting=countryside; level=foundational -->\n<p>Land sold for its yield.</p>\n',
            encoding="utf-8",
        )
    return rec


def test_a_section_awaiting_its_first_question_builds_empty(tmp_path: pathlib.Path) -> None:
    record = qs.load(str(_money_record(tmp_path, awaiting="declared before its first request", question=False)))
    money = next(s for s in ct.walk(record.sections) if s.id == "money")
    assert money.awaiting and not record.holds(money, "research"), "declared, and empty"


def test_without_awaiting_an_empty_rule_is_still_refused(tmp_path: pathlib.Path) -> None:
    rec = _money_record(tmp_path, awaiting="", question=False)
    with pytest.raises(qs.QuestionError) as e:
        qs.load(str(rec))
    assert 'section `money`: the clause {"primary": ["money"]} matches no question' in str(e.value)


def test_a_money_question_with_no_drawing_page_is_homed_and_awaiting_goes_stale(tmp_path: pathlib.Path) -> None:
    rec = _money_record(tmp_path, awaiting="declared before its first request", question=True)
    with pytest.raises(qs.QuestionError) as e:
        qs.load(str(rec))
    assert "section `money`: it holds a question now - delete its `awaiting`" in str(e.value)
    data = json.loads((rec / "contents.json").read_text(encoding="utf-8"))
    del data["sections"][-1]["awaiting"]
    (rec / "contents.json").write_text(json.dumps(data), encoding="utf-8")
    record = qs.load(str(rec))
    land = record.by_stem["0005-land-prices"]
    assert land.home.id == "money" and land.drawing is None and land.research is not None  # type: ignore[union-attr]


def test_the_real_record_declares_the_money_section_and_its_protocol() -> None:
    root = pathlib.Path(RESEARCH_DIR)
    assert "money" in json.loads((root / "tags.json").read_text(encoding="utf-8"))["subject"]
    money = next(s for s in ct.walk(qs.load(RESEARCH_DIR).sections) if s.id == "money")
    assert money.takes == [{"primary": ["money"]}]
    protocol = (root / "money-requests.md").read_text(encoding="utf-8")
    for words in (
        "**A request carries** three things",
        "the question;",
        "the figure the skill needs",
        "the canon it must sit beside",
        "**An answer returns** three things",
        "fragment FILE",
        "ATTESTED ONLY FOR",
        "what is still open",
        "no code implements it - consumed by gm-assistant's money skill; searched:",
        "deletes the section's `awaiting` line",
    ):
        assert words in protocol, words
    assert "money-requests.md" in (root / "CLAUDE.md").read_text(encoding="utf-8"), "the load table points at it"
