"""Features 301 and 303: the record as a manual - a site of small pages with a navigation tree, and the whole record on one
page - organized by the table of contents and the tags rather than by directories.

Feature 301's SC-001..SC-003 (every page built and named by the navigation; notes numbered per page and once on the
single page; every link resolved, and the build refusing one that is not), and feature 303's: the halves follow the
table of contents and open on the settlement tiers (SC-001), each section in level-then-number order and two builds
identical (SC-002), every tag's page exactly its questions (SC-005), and a regrouping that moves no URL (SC-006)."""

from __future__ import annotations

import json
import pathlib
import posixpath
import re

import pytest

from l7r.diagram.interactive.record import contents as ct
from l7r.diagram.interactive.record import site, store
from l7r.diagram.interactive.record import site_links as links
from l7r.diagram.interactive.record import site_notes as sn
from l7r.diagram.interactive.record import site_pages as sp
from l7r.diagram.interactive.record.notes import NoteError, Placed
from l7r.diagram.interactive.record.store import RecordError
from l7r.diagram.interactive.sources import RESEARCH_DIR
from tests import _flat_record as fr

_HREF = re.compile(r'\shref="([^"]*)"')
_ID = re.compile(r'\sid="([^"]+)"')
_FN = re.compile(r'<li id="fn-(\d+)">')


def _nav(files: dict[str, str]) -> dict:
    return json.loads(files["nav.js"].split("window.RECORD_NAV = ", 1)[1].rstrip(";\n"))


def _named(node: dict) -> set[str]:
    return {node["href"]} | {h for _t, h in node["items"]} | {h for s in node["sections"] for h in _named(s)}


# ------------------------------------------------------------------------------------------------- the real record


@pytest.fixture(scope="module")
def built() -> dict[str, str]:
    return site.build(RESEARCH_DIR)


@pytest.fixture(scope="module")
def record() -> store.qs.Record:
    return store.load(RESEARCH_DIR)


def test_every_question_section_tag_and_entry_has_its_page_and_the_navigation_names_them(built: dict[str, str], record: store.qs.Record) -> None:
    """301 SC-001, on the new layout: a page per question page, per section of each half that holds one, per tag."""
    for page in record.pages():
        assert f"q/{page.heading_id}.html" in built, page.file
    for half, _label in sp.HALVES:
        for section in ct.walk(record.sections):
            assert (sp.section_file(half, section) in built) == record.holds(section, half), (half, section.id)
    for facet in ct.FACETS:
        for tag in sp.facet_tags(record.vocab, facet):
            assert sp.tag_file(facet, tag.id) in built, tag.id
    assert len(record.pages()) > 400, "non-vacuity"
    nav = _nav(built)
    named = {h for g in nav["groups"] for s in g["sections"] for h in _named(s)} - {"index.html#tags"}
    pages = {f for f in built if f.endswith(".html") and f not in ("index.html", "all.html")}
    assert named == pages, sorted(pages ^ named)[:10]
    for f in ("q/rice-paddies-and-their-plots-suiden.html", "sources/index.html", "index.html", "all.html", "research/fields.html"):
        assert 'id="sidebar"' in built[f] and "nav.js" in built[f] and "site.js" in built[f] and "glossary.js" in built[f], f


def test_the_halves_follow_the_table_of_contents_and_open_on_the_settlement_tiers(built: dict[str, str], record: store.qs.Record) -> None:
    """303 SC-001: each half's top level is exactly the contents' sections that hold one of its pages, in order, the
    first being the settlement tiers; nothing is named for a directory."""
    nav = _nav(built)
    for (half, label), group in zip(sp.HALVES, nav["groups"], strict=False):
        assert group["label"] == label
        assert [s["key"] for s in group["sections"]] == [sp.node_key(half, s) for s in record.sections if record.holds(s, half)]
        assert group["sections"][0]["title"] == "The settlement tiers"
    assert [g["label"] for g in nav["groups"]] == ["The research", "How our maps draw it", "Tags", "Sources"]
    home = built["index.html"]
    assert home.index("The settlement tiers") < home.index("The countryside") < home.index("Estates and other compounds") < home.index("Map conventions")
    assert "Map conventions" not in home[: home.index('id="drawing"')], "the conventions are in the drawing half only"


def test_every_section_lists_its_questions_by_level_then_number(built: dict[str, str], record: store.qs.Record) -> None:
    """303 SC-002: no question of a later level before one of an earlier level; same-level questions in number order."""
    checked = 0
    for half, _label in sp.HALVES:
        for section in ct.walk(record.sections):
            pages = record.in_section(section, half)
            keys = [(record.vocab.level_rank(record.question_of(p).tags.level), p.number) for p in pages]  # type: ignore[union-attr]
            assert keys == sorted(keys), (half, section.id)
            if pages:
                listed = re.findall(r'<li><a href="\.\./q/([^"]+)\.html"', built[sp.section_file(half, section)])
                assert listed == [p.heading_id for p in pages], (half, section.id)
                checked += 1
    assert checked > 30


def test_two_builds_are_byte_identical(built: dict[str, str]) -> None:
    """303 SC-002's tiebreak (the GM: *"running the makefile command twice in a row will never give output HTML files
    in two different orders"*)."""
    assert site.build(RESEARCH_DIR) == built


def test_every_tag_page_lists_exactly_the_questions_carrying_it(built: dict[str, str], record: store.qs.Record) -> None:
    """303 SC-005, inherited tags included."""
    for facet in ct.FACETS:
        for tag in sp.facet_tags(record.vocab, facet):
            want = {p.heading_id for q in record.questions if (facet, tag.id) in q.tags.all() for p in q.pages()}  # type: ignore[union-attr]
            got = set(re.findall(r'<li><a href="\.\./q/([^"]+)\.html"', built[sp.tag_file(facet, tag.id)]))
            assert got == want, (facet, tag.id)


def test_a_small_page_numbers_its_notes_from_one_and_its_foot_lists_what_it_cites(built: dict[str, str]) -> None:
    """301 SC-002, on every small page."""
    checked = 0
    for name, page in built.items():
        if not name.endswith(".html") or not name.startswith(("q/", "sources/")) or name.endswith("index.html"):
            continue
        refs = [int(n) for n in re.findall(r'href="#fn-(\d+)"', page)]
        notes = [int(n) for n in _FN.findall(page)]
        assert notes == list(range(1, len(notes) + 1)), name
        assert sorted(set(refs)) == notes, f"{name}: the foot lists exactly the notes the page cites"
        works = re.findall(r'<h3 id="work-([a-z0-9-]+)">', page)
        assert set(works) == set(re.findall(r'href="#work-([a-z0-9-]+)"', page)), f"{name}: the works at the foot are exactly the ones its notes cite"
        checked += bool(notes)
    assert checked > 300, "non-vacuity: most questions carry notes"


def test_the_single_page_numbers_once_through_the_whole_record(built: dict[str, str]) -> None:
    page = built["all.html"]
    notes = [int(n) for n in _FN.findall(page)]
    assert len(notes) > 3000 and notes == list(range(1, len(notes) + 1))
    assert '<nav class="toc">' in page and 'href="#citations"' in page and "data-lazy-glossary" in page
    ids = _ID.findall(page)
    assert len(ids) == len(set(ids)), "every id on the single page is unique"
    assert page.index('id="research"') < page.index('id="drawing"') < page.index('id="citations"')


def test_every_link_in_both_forms_resolves(built: dict[str, str]) -> None:
    """301 SC-003: a link into the site names a page that was built and an id on it."""
    ids = {name: set(_ID.findall(page)) for name, page in built.items() if name.endswith(".html")}
    bad = []
    for name, page in built.items():
        if not name.endswith(".html"):
            continue
        for href in _HREF.findall(page):
            if re.match(r"^[a-z][a-z0-9+.-]*:|^//", href) or not href:
                continue
            path, _, anchor = href.partition("#")
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), path)) if path else name
            if target.startswith("../"):
                continue
            if target not in built:
                bad.append(f"{name}: {href} - no such page")
            elif anchor and anchor not in ids[target]:
                bad.append(f"{name}: {href} - no id {anchor!r}")
    assert not bad, "\n".join(bad[:20])


# ------------------------------------------------------------------------------------------------- a small record


def test_a_small_record_builds_both_halves(tmp_path: pathlib.Path) -> None:
    files = site.build(str(fr.write(tmp_path)))
    lanes, bridges, rows = files["q/lanes.html"], files["q/bridges.html"], files["q/rows.html"]
    assert '<h1 id="lanes">' in lanes and 'href="rows.html"' in lanes and 'href="bridges.html#span"' in lanes
    assert 'href="https://x.org"' in lanes and '<a href="nowhere.html">' in lanes, "an external link and a comment are left alone"
    assert 'href="drawing-lanes.html">How it' in lanes and 'href="wide-lanes.html">How it' in lanes, "both drawing pages are linked"
    assert 'href="lanes.html">The history' in files["q/wide-lanes.html"], "a second drawing page links the question it draws"
    assert "Not to be confused with" in lanes and 'href="lanes.html">Lanes</a>' in rows, "a confusable pair is listed both ways"
    assert '<li id="fn-1">' in bridges and 'id="fnref-1-2"' in bridges and 'href="#span"' in bridges
    assert 'href="../sources/alpha.html"' in bridges and 'src="../../assets/x.png"' in bridges
    assert 'href="#work-beta"' in bridges and 'href="../sources/beta.html"' in bridges, "a key links its work at the foot, which links its entry"
    assert 'rel="next"' in lanes and 'rel="prev"' in bridges, "a section's questions are chained"
    assert '<a href="../tags/subject-samurai.html">Samurai</a>' in rows and 'href="../research/fabric.html"' in rows
    assert "Drawn land." in files["drawing/countryside.html"] and "The land." in files["research/countryside.html"]
    assert 'href="../research/ways.html"' in files["research/countryside.html"] and "A lane is narrow." in files["research/ways.html"]
    assert "drawing/cities.html" not in files, "a section with no page of a half is not in that half"
    assert "No question carries this tag yet." not in files["tags/subject-samurai.html"] and "Rows" in files["tags/subject-samurai.html"]
    assert "Works cited" in files["sources/index.html"] and 'href="alpha.html"' in files["sources/index.html"]
    single = files["all.html"]
    assert 'href="#rows"' in single and 'href="#span"' in single and 'href="#alpha"' in single and 'id="research-ways"' in single
    assert single.count('<li id="fn-') == 3, "three notes, numbered once through the record"


def test_a_tag_nobody_carries_has_a_page_saying_so(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    fr.edit(rec, "0003-rows.html", "subject=fabric,samurai", "subject=fabric")
    files = site.build(str(rec))
    assert "No question carries this tag yet." in files["tags/subject-samurai.html"]


def test_a_regrouping_moves_no_url_and_needs_no_question_edited(tmp_path: pathlib.Path) -> None:
    """303 SC-006: swap two sections, and select on a setting and on a subject that is not primary."""
    rec = fr.write(tmp_path)
    before = site.build(str(rec))
    data = json.loads((rec / "contents.json").read_text(encoding="utf-8"))
    data["sections"].reverse()
    (rec / "contents.json").write_text(json.dumps(data), encoding="utf-8")
    after = site.build(str(rec))
    assert {f for f in before if f.startswith("q/")} == {f for f in after if f.startswith("q/")}
    assert [g["sections"][0]["key"] for g in _nav(after)["groups"][:1]] == ["research/cities"]
    data["sections"].insert(0, {"id": "samurai", "title": "Samurai", "takes": [{"subject": "samurai"}, {"setting": "city", "level": "foundational"}]})
    (rec / "contents.json").write_text(json.dumps(data), encoding="utf-8")
    third = site.build(str(rec))
    assert "Rows" in third["research/samurai.html"] and "q/rows.html" in third, "a non-primary subject took the question"
    assert "research/fabric.html" not in third, "the section its first match emptied is omitted"


def test_the_build_refuses_what_lands_nowhere_and_names_it(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    fr.edit(rec, "0002-bridges.html", "<p id=", '<p><a href="0003-rows.html#gone">x</a> <a href="0009-none.html">n</a> <a href="../towns.html">t</a> <a href="#nope">p</a></p>\n<p id=')
    with pytest.raises(RecordError) as e:
        site.build(str(rec))
    for words in ("no id `gone` on 0003-rows.html", "no question page 0009-none.html", "no such page in the record", "no id `nope` on 0002-bridges.html"):
        assert words in str(e.value), words


def test_the_build_refuses_a_duplicate_id_a_reserved_one_an_orphan_note_and_a_work_with_no_write_up(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    fr.edit(rec, "0003-rows.html", "<p>Shops", '<p id="span">Shops')
    with pytest.raises(RecordError, match="the id `span` is used in"):
        site.build(str(rec))
    fr.edit(rec, "0003-rows.html", '<p id="span">Shops', '<p id="tags">Shops')
    with pytest.raises(RecordError, match="one the site's own pages use"):
        site.build(str(rec))
    fr.edit(rec, "0003-rows.html", '<p id="tags">Shops', "<p>Shops")
    notes = rec / "questions" / "0001-lanes.notes.html"
    notes.write_text(notes.read_text(encoding="utf-8") + '<li data-note="lonely">x</li>\n', encoding="utf-8")
    with pytest.raises(RecordError, match="lonely - defined as a note, referenced nowhere"):
        site.build(str(rec))
    notes.write_text(notes.read_text(encoding="utf-8").replace('<li data-note="lonely">x</li>\n', ""), encoding="utf-8")
    entry = rec / "sources" / "010-works-cited" / "0010-alpha.html"
    entry.write_text(entry.read_text(encoding="utf-8").replace("<p><em>What it is:</em> a work.</p>\n", ""), encoding="utf-8")
    with pytest.raises(RecordError, match="cites `alpha`, whose registry entry has no write-up"):
        site.build(str(rec))


def test_a_reference_to_no_note_is_refused_on_both_forms(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    fr.edit(rec, "0002-bridges.html", "One span.", 'One span.<sup class="fn" data-note="nobody"></sup>')
    with pytest.raises(RecordError) as e:
        site.build(str(rec))
    assert "which no note" in str(e.value) and str(e.value).count("nobody") >= 2


def test_a_notes_file_with_a_bad_original_is_refused_by_name(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    (rec / "questions" / "0001-lanes.notes.html").write_text('<li data-note="alpha">x <span class="orig" data-orig="alpha#1"></span></li>\n', encoding="utf-8")
    with pytest.raises(RecordError, match="0001-lanes.notes.html"):
        site.build(str(rec))


def test_a_registry_without_its_title_is_refused(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    (rec / "sources" / "_front.html").write_text("<!DOCTYPE html>\n<p>no main, no title</p>\n", encoding="utf-8")
    with pytest.raises(RecordError, match="the registry needs its title"):
        site.build(str(rec))


def test_the_site_is_written_whole_and_swapped_in(tmp_path: pathlib.Path) -> None:
    out = tmp_path / "research" / "site"
    site.write({"index.html": "one", "a/b.html": "two"}, str(out))
    assert (out / "a" / "b.html").read_text(encoding="utf-8") == "two"
    site.write({"index.html": "three"}, str(out))
    assert (out / "index.html").read_text(encoding="utf-8") == "three" and not (out / "a").exists(), "a page the record no longer has does not linger"
    assert [p.name for p in out.parent.iterdir()] == ["site"], "nothing left beside it"


# ------------------------------------------------------------------------------------------------- the pieces


def test_the_lead_and_the_title() -> None:
    assert site.lead_of("<h2>x</h2><!-- <p>hidden.</p> --><p>First one. Second.</p>") == "First one."
    assert site.lead_of("<h2>x</h2><p>No full stop</p>") == "No full stop" and site.lead_of("<h2>x</h2>") == ""
    assert site._as_title("<p>no heading</p>") == "<p>no heading</p>"
    assert site._item("<p>untitled</p>", "u").title == "u"


def test_the_link_resolver_on_plain_strings() -> None:
    index = links.Index()
    index.add_page("0001-a.html", "a", '<h2 id="a">A</h2><span id="inner"></span>')
    index.add_registry(None, '<p id="intro">x</p>')
    index.add_registry("k", '<h3 id="k">k</h3>')
    assert index.resolve("https://x", "0001-a.html") is None and index.resolve("//x/y", None) is None and index.resolve("", None) is None
    assert index.resolve("0001-a.html#inner", "0001-a.html") == links.Loc("q", "a", "inner")
    assert index.resolve("#a", "0001-a.html") == links.Loc("q", "a", None), "a page's own heading is its top"
    assert index.resolve("../SOURCES.html#intro", "0001-a.html") == links.Loc("source", None, "intro")
    assert index.resolve("../SOURCES.html", "0001-a.html") == links.Loc("source", None)
    assert index.resolve("#k", None) == links.Loc("source", "k") and index.resolve("assets/x.css", None) == "assets/x.css"
    assert index.resolve("../assets/x.css", "0001-a.html") == "assets/x.css"
    for bad, words in (("#zzz", "no id `zzz` on the registry"), ("towns.html", "no such page")):
        with pytest.raises(links.LinkError, match=words):
            index.resolve(bad, None)
    assert links.site_href(links.Loc("q", "a", "inner"), "research/ways.html") == "../q/a.html#inner"
    assert links.site_href(links.Loc("source", None), "q/a.html") == "../sources/index.html"
    assert links.single_href(links.Loc("source", None), "srcs") == "#srcs" and links.single_href(links.Loc("q", "a", None), "s") == "#a"
    assert links.asset_href("assets/x.css#y", "q/a.html") == "../../assets/x.css#y"
    out, errs = links.rewrite('<a href="#nope">x</a> <img src="../assets/i.png">', own="0001-a.html", index=index, here="q/a.html", single=True, where="w")
    assert errs and "no id `nope`" in errs[0] and '<a href="#nope">' in out and 'src="../assets/i.png"' in out


def test_the_notes_of_a_small_page_and_of_the_single_page() -> None:
    page = {"a": '<a href="https://x"><code>k</code></a> - 「q」', "b": "no source"}
    body, placed = sn.small_page('x<sup class="fn" data-note="b"></sup> y<sup class="fn" data-note="a"></sup>', page, "w")
    assert [p.key for p in placed] == ["b", "a"] and 'href="#fn-1">1</a>' in body
    assert sn.foot([], "") == ""
    assert '<a href="#work-k"><code>k</code></a>' in sn.foot([Placed("a", 1, page["a"], 1)], "works"), "a key links its work at the foot"
    count = sn.Numbering()
    one = count.number('x<sup class="fn" data-note="a"></sup><sup class="fn" data-note="a"></sup>', "p.html", page, "w")
    assert 'id="fnref-1"' in one and 'id="fnref-1-2"' in one and len(count.placed) == 1
    count.number('<sup class="fn" data-note="a"></sup>', "q.html", page, "w")
    assert len(count.placed) == 2, "a key is unique within its page, not across the record"
    with pytest.raises(NoteError, match="no note on p.html"):
        count.number('<sup class="fn" data-note="zzz"></sup>', "p.html", page, "w")
    assert sn.keyed_to(page["a"], "#") == '<a href="#k"><code>k</code></a> - 「q」'


def test_the_shell_and_the_trail() -> None:
    page = sp.shell("T", "q/rows.html", "research/cities research/cities/fabric", "<p>x</p>", lazy_glossary=True)
    assert 'data-root="../"' in page and 'href="../assets/site.css"' in page and "data-lazy-glossary" in page
    assert 'data-part="research/cities research/cities/fabric"' in page
    assert "data-lazy-glossary" not in sp.shell("T", "index.html", "", "x")
    assert sp.open_keys("research", None) == "" and sp.crumbs("index.html", []) == '<p class="crumbs"><a href="index.html">The research record</a></p>\n'
    assert sp.nav_js({"a": 1}).startswith("// DERIVED FILE")
