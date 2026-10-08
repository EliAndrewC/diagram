"""`scripts/gates/check-question-size.py` (feature 250 D14): a research question's prose stays under the cap (notes uncounted since feature 292)."""

from __future__ import annotations

import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("check_question_size", REPO / "scripts/gates/check-question-size.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


qs = _load()


def test_a_question_s_size_is_its_prose_and_its_notes_and_originals_are_not_counted(tmp_path: pathlib.Path) -> None:
    """Feature 292 (GM 2026-09-29): the cap bounds what every check and editor reads whole - the prose. The notes are
    bounded where they are read (the quote-check's batches), and the originals are read by the translation check alone."""
    q = tmp_path / "0010-a-question.html"
    q.write_text("x" * 100, encoding="utf-8")
    assert qs.size(q) == 100
    (tmp_path / "0010-a-question.notes.html").write_text("y" * 50, encoding="utf-8")
    (tmp_path / "0010-a-question.originals.html").write_text("z" * 70, encoding="utf-8")
    assert qs.size(q) == 100
    assert qs.question_of(tmp_path / "0010-a-question.notes.html") == q
    assert qs.question_of(tmp_path / "0010-a-question.originals.html") == q
    assert qs.question_of(tmp_path / "0010-a-question.drawing.notes.html") == tmp_path / "0010-a-question.drawing.html"


def test_only_questions_count() -> None:
    """Feature 303: a question's page, research or drawing, in `research/questions/` - nothing else."""
    r = pathlib.Path("research")
    assert qs.is_question(r / "questions" / "0010-how-far.html") and qs.is_question(r / "questions" / "0010-how-far.drawing.html")
    assert not qs.is_question(r / "sources" / "010-works-cited" / "4220-edo-enwiki.html")
    assert not qs.is_question(r / "questions" / "0010-how-far.notes.html") and not qs.is_question(r / "questions" / "0010-how-far.originals.html")
    assert not qs.is_question(r / "site" / "q" / "how-far.html")


def test_the_cap_admits_the_first_question_split_under_it() -> None:
    """The split of 0115 is the cap's worked example: its argument whole, under the cap."""
    d = REPO / "research/questions"
    q = next(p for p in d.glob("0115-servants-in-a-samurai-household*.html") if qs.is_question(p))
    assert qs.size(q) <= qs.CAP, qs.size(q)


def test_every_question_page_of_the_record_is_found() -> None:
    root = REPO
    found = qs.every(root)
    assert len(found) > 400 and all(p.parent.name == "questions" for p in found)
