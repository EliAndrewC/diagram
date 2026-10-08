"""Feature 303: the questions in one flat directory, their tags and the table of contents that homes them.

Every refusal of spec FR-007 and FR-010 is fed to the loader here, each naming the file at fault: a page with no tags,
an unknown tag, a facet missing or repeated, two levels, tags on a page that inherits them, an `about:` naming nothing,
a question no section takes, and a rule that takes nothing. And the real record loads clean (SC-004)."""

from __future__ import annotations

import json
import pathlib

import pytest

from l7r.diagram.interactive.record import contents as ct
from l7r.diagram.interactive.record import questions as qs
from l7r.diagram.interactive.sources import RESEARCH_DIR
from tests import _flat_record as fr


def _refused(rec: pathlib.Path, *words: str) -> str:
    with pytest.raises((qs.QuestionError, ct.ContentsError)) as e:
        qs.load(str(rec))
    for w in words:
        assert w in str(e.value), (w, str(e.value))
    return str(e.value)


def test_the_real_record_loads_every_question_tagged_and_homed() -> None:
    """303 SC-004 / SC-003: every question carries tags, every one has a home, and the stems are unique."""
    record = qs.load(RESEARCH_DIR)
    assert len(record.questions) > 200 and all(q.tags is not None and q.home is not None for q in record.questions)
    assert len({q.number for q in record.questions}) == len(record.questions)
    assert record.sections[0].id == "tiers" and record.questions[0].home is record.sections[0], "the record opens on the tiers"
    seconds = [q for q in record.questions if q.about]
    assert seconds and all(record.by_stem[q.about].research is not None for q in seconds), "second drawing pages name a research question"
    conventions = [q for q in record.questions if q.research is None and q.about is None]
    assert conventions and all(q.home.id == "map-conventions" for q in conventions), "the drawing-only questions are the map conventions"  # type: ignore[union-attr]


def test_the_small_record_loads(tmp_path: pathlib.Path) -> None:
    record = qs.load(str(fr.write(tmp_path)))
    lanes, rows, wide = record.by_stem["0001-lanes"], record.by_stem["0003-rows"], record.by_stem["0004-wide-lanes"]
    assert lanes.tags == ct.Tags(("ways",), ("countryside",), "foundational") and lanes.drawing is not None and lanes.home.id == "ways"  # type: ignore[union-attr]
    assert wide.about == "0001-lanes" and wide.tags == lanes.tags and wide.research is None, "a second drawing page inherits"
    assert rows.home.id == "fabric" and rows.tags.primary == "fabric" and ("subject", "samurai") in rows.tags.all()  # type: ignore[union-attr]
    ways = next(s for s in ct.walk(record.sections) if s.id == "ways")
    assert [p.file for p in record.in_section(ways, "research")] == ["0001-lanes.html", "0002-bridges.html"], "level, then number"
    assert [p.file for p in record.in_section(ways, "drawing")] == ["0001-lanes.drawing.html", "0004-wide-lanes.drawing.html"]
    assert record.holds(record.sections[0], "drawing") and not record.holds(record.sections[1], "drawing")
    assert ways.path()[0].id == "countryside" and lanes.research.notes_file == "0001-lanes.notes.html"  # type: ignore[union-attr]
    assert lanes.drawing.half == "drawing" and lanes.drawing.originals_file == "0001-lanes.drawing.originals.html"  # type: ignore[union-attr]


@pytest.mark.parametrize(
    ("file", "old", "new", "words"),
    [
        ("0002-bridges.html", "<!-- tags: subject=ways; setting=countryside; level=detail -->\n", "", ("0002-bridges.html: no tags",)),
        ("0002-bridges.html", "subject=ways", "subject=lanes", ("`subject=lanes` - no such tag",)),
        ("0002-bridges.html", "; setting=countryside", "", ("no setting in its tags",)),
        ("0002-bridges.html", "level=detail", "level=detail,foundational", ("2 levels",)),
        ("0002-bridges.html", "subject=ways;", "subject=ways,ways;", ("a subject tag is stated twice",)),
        ("0002-bridges.html", "subject=ways;", "subject=ways; subject=ways;", ("each facet once",)),
        ("0002-bridges.html", "<!-- tags:", "<!-- tags: subject=ways; setting=city; level=detail -->\n<!-- tags:", ("two tags markers",)),
        ("0002-bridges.html", "<p id=", "<!-- about: 0001-lanes -->\n<p id=", ("an `about:` on a research page",)),
        ("0001-lanes.drawing.html", "<p>", "<!-- tags: subject=ways; setting=city; level=detail -->\n<p>", ("inherits its tags",)),
        ("0004-wide-lanes.drawing.html", "<!-- about: 0001-lanes -->", "<!-- about: 0009-gone -->", ("`about: 0009-gone` names no research question",)),
        ("0004-wide-lanes.drawing.html", "<!-- about: 0001-lanes -->", "", ("no tags and no `about:`",)),
        ("0004-wide-lanes.drawing.html", "<!-- about: 0001-lanes -->", "<!-- about: 0001-lanes -->\n<!-- tags: subject=ways; setting=city; level=detail -->", ("both tags and an `about:`",)),
        ("0003-rows.html", "subject=fabric,samurai", "subject=samurai", ("no section of contents.json takes them",)),
        ("0003-rows.html", '<h2 id="rows">', '<h2 id="row">', ("its name says `rows` and its heading is `row`",)),
        ("0003-rows.html", '<h2 id="rows">', '<h2 id="lanes">', ("heading id `lanes` is also 0001-lanes.html's",)),
    ],
)
def test_a_question_s_tags_and_markers_are_refused_by_name(tmp_path: pathlib.Path, file: str, old: str, new: str, words: tuple[str, ...]) -> None:
    rec = fr.write(tmp_path)
    fr.edit(rec, file, old, new)
    _refused(rec, *words)


def test_a_drawing_only_question_states_its_own_tags(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    fr.edit(rec, "0004-wide-lanes.drawing.html", "<!-- about: 0001-lanes -->", "<!-- tags: subject=fabric; setting=city; level=detail -->")
    record = qs.load(str(rec))
    assert record.by_stem["0004-wide-lanes"].home.id == "fabric"  # type: ignore[union-attr]


def test_files_that_are_not_a_question_s_are_refused(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    (rec / "questions" / "notes.txt").write_text("x", encoding="utf-8")
    (rec / "questions" / "0002-other.html").write_text('<h2 id="other">O</h2>\n', encoding="utf-8")
    (rec / "questions" / "0005-gone.notes.html").write_text("", encoding="utf-8")
    (rec / "questions" / "0006-blank.html").write_text("<p>no heading</p>\n", encoding="utf-8")
    _refused(rec, "notes.txt: not a question's file", "number 0002 is already 0002-bridges", "0005-gone.notes.html: beside no page", "0006-blank.html: no `<h2 id=...>` heading")


def test_a_rule_that_takes_nothing_is_refused_but_an_emptied_section_is_not(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    data = json.loads((rec / "contents.json").read_text(encoding="utf-8"))
    data["sections"][1]["sections"][0]["takes"].append({"setting": "city", "level": "detail"})
    (rec / "contents.json").write_text(json.dumps(data), encoding="utf-8")
    _refused(rec, 'section `fabric`: the clause {"level": ["detail"], "setting": ["city"]} matches no question')
    data["sections"][1]["sections"][0]["takes"].pop()
    data["sections"].insert(0, {"id": "first", "title": "First", "takes": [{"setting": "city"}]})
    (rec / "contents.json").write_text(json.dumps(data), encoding="utf-8")
    record = qs.load(str(rec))
    assert record.by_stem["0003-rows"].home.id == "first" and not record.holds(record.sections[2], "research"), "first match wins; fabric is empty"  # type: ignore[union-attr]


@pytest.mark.parametrize(
    ("name", "body", "words"),
    [
        ("tags.json", "{", "tags.json: not JSON"),
        ("tags.json", '{"subject": {}}', "holds exactly the facets"),
        ("tags.json", '{"subject": {"A": {"name": "a"}}, "setting": {}, "level": [{"id": "x", "name": "x"}]}', "subject `A`"),
        ("tags.json", '{"subject": {}, "setting": {}, "level": []}', "`level` is a list"),
        ("contents.json", "[]", "an object with a `sections` list"),
        ("contents.json", '{"sections": [{"title": "x"}]}', "a section is an object with a lower-case `id`"),
        ("contents.json", '{"sections": [{"id": "a", "title": "A", "takes": [{"primary": "ways"}]}, {"id": "a", "title": "B", "takes": [{"primary": "ways"}]}]}', "the id is used twice"),
        ("contents.json", '{"sections": [{"id": "a", "takes": [{"primary": "ways"}]}]}', "no `title`"),
        ("contents.json", '{"sections": [{"id": "a", "title": "A"}]}', "takes nothing and holds nothing"),
        ("contents.json", '{"sections": [{"id": "a", "title": "A", "takes": [{"hue": "x"}]}]}', "a clause tests only"),
        ("contents.json", '{"sections": [{"id": "a", "title": "A", "takes": [{}]}]}', "a clause is an object"),
        ("contents.json", '{"sections": [{"id": "a", "title": "A", "takes": [{"primary": "nope"}]}]}', "no subject tag `nope`"),
    ],
)
def test_the_vocabulary_and_the_contents_are_refused_when_malformed(tmp_path: pathlib.Path, name: str, body: str, words: str) -> None:
    rec = fr.write(tmp_path)
    (rec / name).write_text(body, encoding="utf-8")
    _refused(rec, words)


def test_a_missing_vocabulary_is_refused(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    (rec / "tags.json").unlink()
    _refused(rec, "tags.json: missing")


def test_the_tag_pieces() -> None:
    tags = ct.Tags(("ways", "samurai"), ("city",), "detail")
    assert tags.marker() == "<!-- tags: subject=ways,samurai; setting=city; level=detail -->"
    assert ct.matches({"subject": ["samurai"], "setting": ["city"]}, tags) and not ct.matches({"primary": ["samurai"]}, tags)
    assert qs.text_of('<span class="xref">x</span>A <b>b</b>') == "A b" and qs.heading("<p>none</p>") is None


def test_a_tool_selects_pages_by_number_file_section_or_tag(tmp_path: pathlib.Path) -> None:
    """Spec FR-019: `Q=` and `IN=` name a stem, a page, a section (with its subsections) or a tag."""
    record = qs.load(str(fr.write(tmp_path)))
    files = lambda term: [p.file for p in record.select(term)]  # noqa: E731
    assert files("1") == ["0001-lanes.html", "0001-lanes.drawing.html"] and files("0003-rows.html") == ["0003-rows.html"]
    assert files("countryside") == ["0001-lanes.html", "0001-lanes.drawing.html", "0004-wide-lanes.drawing.html", "0002-bridges.html"]
    assert files("samurai") == ["0003-rows.html"] and files("0002, 0003") == ["0003-rows.html", "0002-bridges.html"]
    assert files("nothing-by-this-name") == []
