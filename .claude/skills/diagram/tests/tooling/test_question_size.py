"""`scripts/check-question-size.py` (feature 250 D14): a research question with its notes stays under the cap."""

from __future__ import annotations

import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("check_question_size", REPO / "scripts" / "check-question-size.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


qs = _load()


def test_a_question_is_its_file_and_its_notes(tmp_path: pathlib.Path) -> None:
    q = tmp_path / "010-a-question.html"
    q.write_text("x" * 100, encoding="utf-8")
    assert qs.size(q) == 100
    (tmp_path / "010-a-question.notes.html").write_text("y" * 50, encoding="utf-8")
    assert qs.size(q) == 150
    assert qs.question_of(tmp_path / "010-a-question.notes.html") == q


def test_only_questions_count() -> None:
    r = pathlib.Path(".claude/skills/diagram/research")
    assert qs.is_question(r / "ways" / "010-how-far.html")
    assert not qs.is_question(r / "sources" / "010-works-cited" / "4220-edo-enwiki.html")
    assert not qs.is_question(r / "citations" / "ways.html") and not qs.is_question(r / "ways" / "_front.html")


def test_the_cap_admits_the_first_question_split_under_it() -> None:
    """The split of cities/government 080 is the cap's worked example: its argument whole, under the cap."""
    d = REPO / ".claude/skills/diagram/research/cities/government"
    q = next(p for p in d.glob("080-servant-housing*.html") if not p.name.endswith(".notes.html"))
    assert qs.size(q) <= qs.CAP, qs.size(q)
