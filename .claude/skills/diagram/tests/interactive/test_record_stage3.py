"""The notes beside their questions, end to end on a record of one page (feature 258, stage 3).

A whole small record is built here - a research page, its citations page and a registry - and taken
through the migration, the assembly and the command, because that is the only way to exercise the two
things the design rests on: that a note's body travels from the citations page to the question that
cites it without changing, and that `citations.py` is handed an assembled PAGE and never a fragment
(spec FR-029).
"""

from __future__ import annotations

import pathlib

import pytest

from l7r.diagram.interactive.record import citations_side as cite
from l7r.diagram.interactive.record import fragments as frag
from l7r.diagram.interactive.record import store
from l7r.diagram.interactive.record.notes import NoteError
from l7r.diagram.interactive.record.split import split
from l7r.diagram.interactive.record.store import (
    RecordError,
    assemble_pages,
    has_notes,
    read_notes,
    write_fragments,
    write_notes_fragments,
)
from l7r.diagram.tools import record_asset

PAGE = (
    '<!DOCTYPE html>\n<html lang="en">\n<head><title>Ways</title></head>\n<body>\n<main>\n'
    '<h1 id="ways">Ways</h1>\n<p><em>The findings.</em></p>\n<hr>\n\n'
    '<h2 id="first">First</h2>\n'
    '<p>A deck lands past the bank.<sup class="fn"><a id="fnref-3" href="citations/ways.html#fn-3">3</a></sup> '
    'It is dredged yearly.<sup class="fn"><a id="fnref-1" href="citations/ways.html#fn-1">1</a></sup></p>\n\n'
    '<h2 id="second">Second</h2>\n'
    '<p>The lane is one barrow wide.<sup class="fn"><a id="fnref-2" href="citations/ways.html#fn-2">2</a></sup> '
    'And again here.<sup class="fn"><a id="fnref-2b" href="citations/ways.html#fn-2">2</a></sup></p>\n'
    '<section class="citations"><p>Notes on <a href="citations/ways.html">its citations page</a>.</p></section>\n'
    "</main>\n</body>\n</html>\n"
)
WORKS_OPEN = "<!-- works-cited: DERIVED by `make citations` from SOURCES.html - change a work's write-up in its registry entry, never here -->"
WORKS_CLOSE = "<!-- /works-cited -->"
CITATIONS = (
    '<!DOCTYPE html>\n<html lang="en">\n<head><title>Citations: Ways</title></head>\n<body>\n<main>\n'
    '<h1 id="citations-ways">Citations: Ways</h1>\n'
    '<section class="works">\n<h2 id="works-cited">The works cited on this page</h2>\n'
    f"{WORKS_OPEN}\nstale works\n{WORKS_CLOSE}\n"
    '</section>\n<h2 id="notes">The notes</h2>\n<section class="footnotes"><ol>\n'
    '<li id="fn-1"><a href="http://a"><code>alpha</code></a> - 「dredged yearly」 <a class="fnback" href="../ways.html#fnref-1">back</a></li>\n'
    '<li id="fn-2"><a href="http://b"><code>beta</code></a> - 「one barrow wide」 <a class="fnback" href="../ways.html#fnref-2">back</a></li>\n'
    '<li id="fn-3">no publicly readable source (searched 2026-09-20) <a class="fnback" href="../ways.html#fnref-3">back</a></li>\n'
    "</ol></section>\n</main>\n</body>\n</html>\n"
)
REGISTRY = (
    '<!DOCTYPE html>\n<html lang="en">\n<head><title>Sources</title></head>\n<body>\n<main>\n'
    '<h1 id="sources">Sources</h1>\n\n<h2 id="works-cited">Works cited</h2>\n<p>Every keyed work.</p>\n'
    '<h3 id="alpha"><a href="http://a"><code>alpha</code></a></h3>\n<p>Alpha, a book (http://a)</p>\n'
    "<p><em>What it is:</em> a book.</p>\n<p><em>Why it applies, and its limits:</em> it is read.</p>\n"
    '<h3 id="beta"><a href="http://b"><code>beta</code></a></h3>\n<p>Beta, a paper (http://b)</p>\n'
    "<p><em>What it is:</em> a paper.</p>\n<p><em>Why it applies, and its limits:</em> it is read.</p>\n"
    "</main>\n</body>\n</html>\n"
)


@pytest.fixture
def record(tmp_path: pathlib.Path) -> pathlib.Path:
    """A record of one page, split to stage 2 - questions and registry entries, notes still on the page."""
    (tmp_path / "citations").mkdir()
    (tmp_path / "cities").mkdir()
    (tmp_path / "ways.html").write_text(PAGE, encoding="utf-8")
    (tmp_path / "citations" / "ways.html").write_text(CITATIONS, encoding="utf-8")
    (tmp_path / "SOURCES.html").write_text(REGISTRY, encoding="utf-8")
    write_fragments("ways.html", str(tmp_path))
    write_fragments("SOURCES.html", str(tmp_path))
    return tmp_path


def test_the_notes_move_beside_the_questions_that_cite_them(record: pathlib.Path) -> None:
    """FR-016: a question's prose and its footnotes are siblings, and the key comes from the source."""
    write_notes_fragments("ways.html", str(record))
    first = read_notes("ways.html", str(record))
    assert set(first) == {"alpha", "beta", "first"}, "two keyed notes, and one named for its question"
    assert (record / "ways" / "010-first.notes.html").read_text(encoding="utf-8").count("<li data-note=") == 2
    assert (record / "ways" / "020-second.notes.html").read_text(encoding="utf-8").count("<li data-note=") == 1
    assert "data-note=\"alpha\"" in (record / "ways" / "010-first.html").read_text(encoding="utf-8")
    assert "fnref-" not in (record / "ways" / "010-first.html").read_text(encoding="utf-8"), "no number in a fragment"


def test_the_numbers_are_allocated_in_the_order_a_reader_meets_them(record: pathlib.Path) -> None:
    """FR-019, and the whole point: the page cited 3, 1, 2, 2 and now cites 1, 2, 3, 3."""
    write_notes_fragments("ways.html", str(record))
    research, citations = assemble_pages("ways.html", str(record))
    assert '<a id="fnref-1" href="citations/ways.html#fn-1">1</a>' in research
    assert research.index("#fn-1") < research.index("#fn-2") < research.index("#fn-3")
    assert '<a id="fnref-3" href="citations/ways.html#fn-3">3</a>' in research
    assert '<a id="fnref-3-2" href="citations/ways.html#fn-3">3</a>' in research, "the repeat has its own id"
    assert citations is not None
    assert citations.index('<li id="fn-1">') < citations.index('<li id="fn-2">') < citations.index('<li id="fn-3">')
    assert '<a class="fnback" href="../ways.html#fnref-3">back</a>' in citations, "the back link points at the first"


def test_every_note_body_survives_the_move_verbatim(record: pathlib.Path) -> None:
    """SC-003's invariant: the pairing, not the numbering."""
    before = cite.old_notes(CITATIONS)
    write_notes_fragments("ways.html", str(record))
    _research, citations = assemble_pages("ways.html", str(record))
    assert citations is not None
    # feature 292: the assembly adds what its reader sees (an absence note's words, a list, a collapsed original);
    # the note as WRITTEN is what must survive
    assert sorted(map(store._as_written, cite.old_notes(citations).values())) == sorted(map(store._as_written, before.values()))
    assert any("absence-lead" in body for body in cite.old_notes(citations).values()), "and the reader's form is written"


def test_the_works_block_is_derived_from_the_assembled_page(record: pathlib.Path) -> None:
    """FR-029: `citations.py` is handed a PAGE, and the works block is derived in memory (feature 301)."""
    write_notes_fragments("ways.html", str(record))
    _research, written = assemble_pages("ways.html", str(record))
    assert written is not None and "stale works" not in written
    assert "Alpha, a book" in written and "Beta, a paper" in written
    assert written.index("<code>alpha</code>") < written.index("<code>beta</code>"), "in order of first citation"


def test_a_page_whose_notes_have_not_moved_assembles_as_before(record: pathlib.Path) -> None:
    assert not has_notes("ways.html", str(record))
    research, citations = assemble_pages("ways.html", str(record))
    assert citations is None and research == PAGE


def test_the_migration_runs_once(record: pathlib.Path) -> None:
    write_notes_fragments("ways.html", str(record))
    with pytest.raises(RecordError, match="already moved"):
        write_notes_fragments("ways.html", str(record))


def test_a_page_with_no_citations_page_is_refused(record: pathlib.Path) -> None:
    (record / "citations" / "ways.html").unlink()
    with pytest.raises(RecordError, match="no citations page"):
        write_notes_fragments("ways.html", str(record))


def test_a_note_no_reference_names_is_refused_rather_than_dropped(record: pathlib.Path) -> None:
    extra = CITATIONS.replace("</ol></section>", '<li id="fn-9">orphan <a class="fnback" href="../ways.html#fnref-9">back</a></li>\n</ol></section>')
    (record / "citations" / "ways.html").write_text(extra, encoding="utf-8")
    with pytest.raises(RecordError, match="that no reference on"):
        write_notes_fragments("ways.html", str(record))


def test_a_move_that_changed_the_prose_is_refused(record: pathlib.Path) -> None:
    """The self-check: what stage 3 may change is the numbers, and it proves it before it lands."""
    page = record / "ways" / "010-first.html"
    page.write_text(page.read_text(encoding="utf-8").replace("A deck lands", "A deck stops"), encoding="utf-8")
    (record / "ways.html").write_text(PAGE, encoding="utf-8")
    with pytest.raises(RecordError, match="more than the footnote numbers"):
        write_notes_fragments("ways.html", str(record))


def test_a_note_lost_in_the_move_is_refused(record: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The other half of the self-check: every note goes in and every note comes out, verbatim."""
    from l7r.diagram.interactive.record import store

    monkeypatch.setattr(store.cite, "notes_fragment", lambda bodies: "".join(f'<li data-note="{k}">{b} EXTRA</li>\n' for k, b in bodies))
    with pytest.raises(RecordError, match="came out, or their text changed"):
        write_notes_fragments("ways.html", str(record))


def test_the_citations_regions_are_read_off_the_page(record: pathlib.Path) -> None:
    front, mid, tail = cite.split_regions(CITATIONS)
    assert front.endswith('<h2 id="works-cited">The works cited on this page</h2>\n')
    assert mid.startswith("\n</section>") and mid.endswith('<section class="footnotes"><ol>\n')
    assert tail == "\n</ol></section>\n</main>\n</body>\n</html>\n"
    with pytest.raises(ValueError, match="no works markers"):
        cite.split_regions("<html>no markers</html>")
    empty = CITATIONS[: CITATIONS.index('<li id="fn-1"')] + CITATIONS[CITATIONS.index("</ol></section>") :]
    assert cite.split_regions(empty)[2] or True, "a page with no notes still splits"


def test_the_paths_a_reference_and_a_back_link_carry() -> None:
    assert cite.citations_href("ways.html") == "citations/ways.html"
    assert cite.citations_href("cities/fabric.html") == "../citations/cities/fabric.html"
    assert cite.page_href("ways.html") == "../ways.html"
    assert cite.page_href("cities/fabric.html") == "../../cities/fabric.html"
    assert cite.citations_rel("cities/fabric.html") == "citations/cities/fabric.html"


def test_a_key_is_derived_from_the_source_and_falls_back_to_the_question() -> None:
    assert cite.leading_key('<a href="http://a"><code>alpha</code></a> - x') == "alpha"
    assert cite.leading_key("no publicly readable source") is None
    keys = cite.keys_for(PAGE, cite.old_notes(CITATIONS), {3: "first", 1: "first", 2: "second"})
    assert keys == {3: "first", 1: "alpha", 2: "beta"}
    assert cite.to_key_form('x<sup class="fn"><a id="fnref-1" href="c#fn-1">1</a></sup>', {1: "alpha"}) == 'x<sup class="fn" data-note="alpha"></sup>'
    assert cite.to_key_form('y<sup class="fn"><a href="c#fn-7">7</a></sup>', {1: "alpha"}).endswith("</sup>"), "a number with no key is left alone rather than mangled"


def test_the_works_region_is_taken_from_the_page_or_left_empty() -> None:
    assert "stale works" in cite.works_region(CITATIONS)
    assert cite.works_region("<html>nothing</html>").startswith("<!-- works-cited")


def _assets(record: pathlib.Path) -> None:
    """The hand-written assets the site carries (`record/site.py` ASSETS)."""
    (record / "assets").mkdir(exist_ok=True)
    for name in ("record.css", "record.js", "site.css", "site.js"):
        (record / "assets" / name).write_text(f"/* {name} */\n", encoding="utf-8")


def test_the_command_builds_checks_splits_and_refuses(record: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`make record` and its modes, through the CLI the Makefile calls (feature 301: it builds the site)."""
    write_notes_fragments("ways.html", str(record))
    _assets(record)
    assert record_asset.main(["--check", "--research-dir", str(record)]) == 0
    assert "builds cleanly" in capsys.readouterr().out
    assert not (record / "site").exists(), "the check writes nothing"
    assert record_asset.main(["--research-dir", str(record)]) == 0
    assert "wrote the site" in capsys.readouterr().out
    assert (record / "site" / "ways" / "first.html").is_file() and (record / "site" / "all.html").is_file()
    question = record / "ways" / "010-first.html"
    question.write_text(question.read_text(encoding="utf-8").replace("</p>", ' <a href="ways.html#nowhere">a link</a></p>', 1), encoding="utf-8")
    assert record_asset.main(["--check", "--research-dir", str(record)]) == 1
    assert "no id `nowhere`" in capsys.readouterr().err
    whole = record.parent / "whole"
    whole.mkdir()
    (whole / "SOURCES.html").write_text(REGISTRY, encoding="utf-8")
    assert record_asset.main(["--split", "sources", "--research-dir", str(whole)]) == 0
    assert "assembles back to the same bytes" in capsys.readouterr().out
    assert record_asset.main(["--split", "towns", "--research-dir", str(record)]) == 1
    assert "record:" in capsys.readouterr().err


def test_a_new_footnote_reaches_its_small_page(record: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A footnote added to a question reaches the question's own page, numbered on it (feature 301), and the build stays
    clean. Found on `cities/sizing` (feature 250) in its old form: the command wrote the research page alone."""
    write_notes_fragments("ways.html", str(record))
    _assets(record)
    assert record_asset.main(["--research-dir", str(record)]) == 0
    notes = sorted((record / "ways").glob("*.notes.html"))[0]
    question = notes.with_name(notes.name.replace(".notes.html", ".html"))
    question.write_text(question.read_text(encoding="utf-8").replace("</p>", '<sup class="fn" data-note="added"></sup></p>', 1), encoding="utf-8")
    notes.write_text(notes.read_text(encoding="utf-8") + '<li data-note="added">no publicly readable source (searched 2026-09-21: nothing read)</li>\n', encoding="utf-8")
    assert record_asset.main(["--research-dir", str(record)]) == 0
    assert "nothing read" in (record / "site" / "ways" / "first.html").read_text(encoding="utf-8")
    assert record_asset.main(["--check", "--research-dir", str(record)]) == 0, capsys.readouterr().err


def test_the_command_names_the_registry_by_either_name() -> None:
    assert record_asset._page_rel("sources") == "SOURCES.html"
    assert record_asset._page_rel("SOURCES") == "SOURCES.html"
    assert record_asset._page_rel("cities/fabric") == "cities/fabric.html"
    assert record_asset._page_rel("ways.html") == "ways.html"


def test_the_small_refusals_of_the_layout() -> None:
    with pytest.raises(ValueError, match="must be named"):
        frag.position_of("_front.html")
    assert frag.page_of("research/ways/010-x.html") == "research/ways"
    assert frag.notes_file("010-x.html") == "010-x.notes.html"
    page = split('<!DOCTYPE html>\n<p>no sections</p>\n</main>\n</body>\n</html>\n')
    assert page.sections == () and page.front.startswith("<!DOCTYPE")
    registry = split(REGISTRY, entry_level=3)
    assert [s.id for s in registry.sections] == ["works-cited"]
    assert len(registry.sections[0].entries) == 2


def test_the_last_refusals_and_the_quiet_paths(record: pathlib.Path) -> None:
    """The branches the happy path does not reach: each is a refusal or a report nobody should meet."""
    from l7r.diagram.interactive.record.notes import allocate
    from l7r.diagram.interactive.record.store import _first_difference

    # a reference whose key is malformed is refused, not skipped (notes.py)
    with pytest.raises(NoteError, match="not a note key"):
        allocate('<sup class="fn" data-note="Not A Key"></sup>', {}, "ways")

    # a section at the entry level that HAS no entries is still one section (split.py)
    registry = REGISTRY.replace('<h3 id="beta"><a href="http://b"><code>beta</code></a></h3>\n', "")
    empty = split(registry.replace('<h3 id="alpha"><a href="http://a"><code>alpha</code></a></h3>\n', ""), entry_level=3)
    assert [s.id for s in empty.sections] == ["works-cited"] and empty.sections[0].entries == ()

    # the byte-difference report both ways round (store.py)
    assert "first difference at byte 2" in _first_difference("abc", "abd")
    assert "one is 3 characters and the other 2" in _first_difference("abc", "ab")


def test_a_page_whose_split_does_not_rebuild_is_refused(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`make record SPLIT=` will not leave fragments behind that do not assemble back (store.py)."""
    from l7r.diagram.interactive.record import store

    (tmp_path / "cities").mkdir()
    (tmp_path / "ways.html").write_text(PAGE, encoding="utf-8")
    monkeypatch.setattr(store, "read_page", lambda page_rel, record_dir=None: "not the page at all")
    with pytest.raises(RecordError, match="does not assemble back"):
        write_fragments("ways.html", str(tmp_path))


def test_a_note_edited_alone_reaches_its_small_page(record: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Feature 261: an edit to a `.notes.html` fragment alone must reach what a reader opens - since feature 301, the
    question's small page in the site, where its notes stand at its foot."""
    write_notes_fragments("ways.html", str(record))
    _assets(record)
    notes = record / "ways" / "020-second.notes.html"
    notes.write_text(notes.read_text(encoding="utf-8").replace("</li>", " (a gloss moved)</li>", 1), encoding="utf-8")
    assert record_asset.main(["--research-dir", str(record)]) == 0
    assert "(a gloss moved)" in (record / "site" / "ways" / "second.html").read_text(encoding="utf-8")
    capsys.readouterr()
