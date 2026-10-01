"""Feature 301: the record as a manual - a site of small pages with a navigation tree, and the whole record on one page.

SC-001: one small page per question and per registry entry, one page per part, the home page and the single page, and
the navigation names every page. SC-002: a small page's notes run 1..n with its foot listing exactly the notes and works
it cites; the single page's notes run 1..N through the record. SC-003: every link in both forms resolves, and the build
refuses one that does not, a duplicated id, a note nothing cites and a cited work with no write-up."""

from __future__ import annotations

import json
import pathlib
import posixpath
import re

import pytest

from l7r.diagram.interactive.record import site
from l7r.diagram.interactive.record import site_links as links
from l7r.diagram.interactive.record import site_notes as sn
from l7r.diagram.interactive.record.notes import NoteError, Placed
from l7r.diagram.interactive.record.store import RecordError, record_pages
from l7r.diagram.interactive.sources import RESEARCH_DIR

_HREF = re.compile(r'\shref="([^"]*)"')
_ID = re.compile(r'\sid="([^"]+)"')
_FN = re.compile(r'<li id="fn-(\d+)">')


# ------------------------------------------------------------------------------------------------- the real record


@pytest.fixture(scope="module")
def built() -> dict[str, str]:
    return site.build(RESEARCH_DIR)


def test_every_question_entry_and_part_has_its_page_and_the_navigation_names_them(built: dict[str, str]) -> None:
    """SC-001."""
    parts = site.load(RESEARCH_DIR)
    assert {p.page_rel for p in parts} == set(record_pages(RESEARCH_DIR))
    for part in parts:
        assert f"{part.dir}/index.html" in built, part.dir
        for item in part.all_items():
            assert f"{part.dir}/{item.id}.html" in built, (part.dir, item.id)
    questions = sum(len(p.items) for p in parts if not p.is_registry)
    entries = sum(len(p.all_items()) for p in parts if p.is_registry)
    assert questions > 400 and entries > 1000, (questions, entries)
    assert {"index.html", "all.html", "nav.js", "assets/glossary.js", "assets/record.js", "assets/site.js"} <= set(built)
    nav = json.loads(built["nav.js"].split("window.RECORD_NAV = ", 1)[1].rstrip(";\n"))
    named = {href for g in nav["groups"] for p in g["parts"] for _t, href in p["items"]} | {f"{p['dir']}/index.html" for g in nav["groups"] for p in g["parts"]}
    pages = {f for f in built if f.endswith(".html") and f not in ("index.html", "all.html")}
    assert named == pages, sorted(pages ^ named)[:10]
    assert nav["all"] == "all.html" and nav["home"] == "index.html"
    for f in ("fields/rice-paddies-and-their-plots-suiden.html", "sources/index.html", "index.html", "all.html"):
        page = built[f]
        assert 'id="sidebar"' in page and "nav.js" in page and "site.js" in page and "glossary.js" in page, f


def test_a_small_page_numbers_its_notes_from_one_and_its_foot_lists_what_it_cites(built: dict[str, str]) -> None:
    """SC-002, on every small page."""
    checked = 0
    for name, page in built.items():
        if not name.endswith(".html") or name.endswith("index.html") or name == "all.html":
            continue
        refs = [int(n) for n in re.findall(r'href="#fn-(\d+)"', page)]
        notes = [int(n) for n in _FN.findall(page)]
        assert notes == list(range(1, len(notes) + 1)), name
        assert sorted(set(refs)) == notes, f"{name}: the foot lists exactly the notes the page cites"
        works = re.findall(r'<h3 id="work-([a-z0-9-]+)">', page)
        cited = {k for k in re.findall(r'href="#work-([a-z0-9-]+)"', page)}
        assert set(works) == cited, f"{name}: the works at the foot are exactly the ones its notes cite"
        checked += bool(notes)
    assert checked > 300, "non-vacuity: most questions carry notes"


def test_the_single_page_numbers_once_through_the_whole_record(built: dict[str, str]) -> None:
    """SC-002's other half, and the single page's table of contents."""
    page = built["all.html"]
    notes = [int(n) for n in _FN.findall(page)]
    assert len(notes) > 3000 and notes == list(range(1, len(notes) + 1))
    assert '<nav class="toc">' in page and 'href="#citations"' in page and "data-lazy-glossary" in page
    ids = _ID.findall(page)
    assert len(ids) == len(set(ids)), "every id on the single page is unique"


def test_every_link_in_both_forms_resolves(built: dict[str, str]) -> None:
    """SC-003: a link into the site names a page that was built and an id on it; the single page's anchors exist."""
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
                continue  # an asset of the record outside the site (none today, and not the site's to hold)
            if target not in built:
                bad.append(f"{name}: {href} - no such page")
            elif anchor and target in ids and anchor not in ids[target]:
                bad.append(f"{name}: {href} - no id {anchor!r}")
    assert not bad, "\n".join(bad[:20])


# ------------------------------------------------------------------------------------------------- a small record


def _record(tmp: pathlib.Path) -> pathlib.Path:
    """Two research pages (one in a collection), a registry with a section and two entries, notes and assets."""
    page = '<!DOCTYPE html>\n<html>\n<body>\n<main>\n<h1 id="{0}">{1}</h1>\n<p id="{0}-intro"><em>{1}, the intro.</em></p>\n<hr>\n'
    tail = "</main>\n</body>\n</html>\n"
    ways = tmp / "ways"
    ways.mkdir(parents=True)
    (ways / "_front.html").write_text(page.format("ways", "Ways"), encoding="utf-8")
    (ways / "_tail.html").write_text(tail, encoding="utf-8")
    (ways / "010-lanes.html").write_text(
        '<h2 id="lanes">Lanes</h2>\n<div class="confusables"><p>Not to be confused with:</p></div>\n'
        '<p>A lane is narrow.<sup class="fn" data-note="alpha"></sup> See <a href="cities/fabric.html#rows">the rows</a>'
        ' and <a href="#bridges">bridges</a> and <a href="https://x.org">out</a>.<!-- <a href="nowhere.html">x</a> --></p>\n',
        encoding="utf-8",
    )
    (ways / "010-lanes.notes.html").write_text(
        '<li data-note="alpha"><a href="https://a"><code>alpha</code></a> - 「q」</li>\n<li data-note="beta"><a href="../SOURCES.html#beta"><code>beta</code></a> - 「r」</li>\n', encoding="utf-8"
    )
    (ways / "020-bridges.html").write_text(
        '<h2 id="bridges">Bridges</h2>\n<p>One span.<sup class="fn" data-note="beta"></sup> Again.<sup class="fn" data-note="beta"></sup>'
        ' <a href="ways.html">the page</a> <a href="SOURCES.html#alpha">a source</a> <img src="assets/x.png"></p>\n',
        encoding="utf-8",
    )
    fabric = tmp / "cities" / "fabric"
    fabric.mkdir(parents=True)
    (fabric / "_front.html").write_text(page.format("fabric", "Fabric"), encoding="utf-8")
    (fabric / "_tail.html").write_text(tail, encoding="utf-8")
    (fabric / "010-rows.html").write_text(
        '<h2 id="rows">Rows</h2>\n<p>Shops in a row. <a href="../citations/ways.html#work-alpha">w</a> <a href="../ways/020-bridges.html">b</a> <a href="../citations/ways.html">its notes</a></p>\n',
        encoding="utf-8",
    )
    src = tmp / "sources"
    (src / "010-works-cited").mkdir(parents=True)
    (src / "_front.html").write_text(page.format("sources", "Sources"), encoding="utf-8")
    (src / "_tail.html").write_text(tail, encoding="utf-8")
    (src / "010-works-cited.html").write_text('<h2 id="works-cited">Works cited</h2>\n<p>Every work.</p>\n', encoding="utf-8")
    for n, key, url in ((10, "alpha", "https://a"), (20, "beta", "https://b; SUMMARY-ONLY")):
        (src / "010-works-cited" / f"00{n}-{key}.html").write_text(
            f'<h3 id="{key}"><code>{key}</code></h3>\n<p>{key.title()}, a work ({url})</p>\n<p><em>What it is:</em> a work.</p>\n<p><em>Why it applies, and its limits:</em> it does.</p>\n',
            encoding="utf-8",
        )
    (tmp / "assets").mkdir()
    for name in site.ASSETS:
        (tmp / "assets" / name).write_text(f"/* {name} */", encoding="utf-8")
    return tmp


def test_a_small_record_builds_both_forms(tmp_path: pathlib.Path) -> None:
    rec = _record(tmp_path)
    files = site.build(str(rec))
    lanes, bridges = files["ways/lanes.html"], files["ways/bridges.html"]
    assert '<h1 id="lanes">Lanes</h1>' in lanes and 'href="../cities/fabric/rows.html"' in lanes and 'href="bridges.html"' in lanes
    assert 'href="https://x.org"' in lanes and '<a href="nowhere.html">' in lanes, "an external link and a comment are left alone"
    assert '<li id="fn-1">' in bridges and 'id="fnref-1-2"' in bridges, "numbered from 1 on its own page; the repeat its own id"
    assert 'href="index.html"' in bridges and 'href="../sources/alpha.html"' in bridges and 'src="../../assets/x.png"' in bridges
    assert 'href="#work-beta"' in bridges and 'href="../sources/beta.html"' in bridges, "a key links its work at the foot, which links its entry"
    assert 'rel="prev"' in bridges and 'rel="next"' in lanes, "the pages of a part are chained"
    rows = files["cities/fabric/rows.html"]
    assert 'href="../../sources/alpha.html"' in rows and 'href="../../ways/bridges.html"' in rows
    assert 'href="../../ways/index.html"' in rows, "a citations page is its research page's part"
    single = files["all.html"]
    assert 'href="#rows"' in single and 'href="#bridges"' in single and 'href="#alpha"' in single and 'href="#ways"' in single
    assert single.count('<li id="fn-') == 2, "two notes, numbered once through the record"
    assert "Works cited" in files["sources/index.html"] and 'href="alpha.html"' in files["sources/index.html"]
    assert "A lane is narrow." in files["ways/index.html"] and "Not to be confused" not in files["ways/index.html"], "the lead skips the box"
    assert files["index.html"].index("Research") < files["index.html"].index("Cities") < files["index.html"].index("Sources")


def test_the_build_refuses_what_lands_nowhere_and_names_it(tmp_path: pathlib.Path) -> None:
    rec = _record(tmp_path)
    q = rec / "ways" / "020-bridges.html"
    q.write_text(
        q.read_text(encoding="utf-8")
        + '<p><a href="ways.html#gone">x</a> <a href="citations/ways.html#fn-3">n</a> <a href="citations/towns.html">t</a> <a href="cities/fabric/090-gone.html">g</a></p>\n',
        encoding="utf-8",
    )
    with pytest.raises(RecordError) as e:
        site.build(str(rec))
    for words in ("no id `gone`", "not addressable", "no research page towns.html", "no question `gone`"):
        assert words in str(e.value), words


def test_the_build_refuses_a_duplicate_id_a_reserved_one_an_orphan_note_and_a_work_with_no_write_up(tmp_path: pathlib.Path) -> None:
    rec = _record(tmp_path)
    (rec / "cities" / "fabric" / "020-lanes.html").write_text('<h2 id="lanes">Lanes again</h2>\n', encoding="utf-8")
    with pytest.raises(RecordError, match="the id `lanes` is used in"):
        site.build(str(rec))
    (rec / "cities" / "fabric" / "020-lanes.html").write_text('<h2 id="contents">Contents</h2>\n', encoding="utf-8")
    with pytest.raises(RecordError, match="one the site's own pages use"):
        site.build(str(rec))
    (rec / "cities" / "fabric" / "020-lanes.html").unlink()
    notes = rec / "ways" / "010-lanes.notes.html"
    notes.write_text(notes.read_text(encoding="utf-8") + '<li data-note="lonely">x</li>\n', encoding="utf-8")
    with pytest.raises(RecordError, match="lonely - defined as a note, referenced nowhere"):
        site.build(str(rec))
    notes.write_text(notes.read_text(encoding="utf-8").replace('<li data-note="lonely">x</li>\n', ""), encoding="utf-8")
    entry = rec / "sources" / "010-works-cited" / "0010-alpha.html"
    entry.write_text(entry.read_text(encoding="utf-8").replace("<p><em>What it is:</em> a work.</p>\n", ""), encoding="utf-8")
    with pytest.raises(RecordError, match="cites `alpha`, whose registry entry has no write-up"):
        site.build(str(rec))


def test_a_reference_to_no_note_is_refused_on_both_forms(tmp_path: pathlib.Path) -> None:
    rec = _record(tmp_path)
    q = rec / "ways" / "020-bridges.html"
    q.write_text(q.read_text(encoding="utf-8").replace("One span.", 'One span.<sup class="fn" data-note="nobody"></sup>'), encoding="utf-8")
    with pytest.raises(RecordError) as e:
        site.build(str(rec))
    assert "which no note" in str(e.value) and str(e.value).count("nobody") >= 2


def test_a_part_without_its_title_is_refused(tmp_path: pathlib.Path) -> None:
    rec = _record(tmp_path)
    (rec / "ways" / "_front.html").write_text("<!DOCTYPE html>\n<p>no main, no title</p>\n", encoding="utf-8")
    with pytest.raises(RecordError, match="a part needs its title"):
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
    assert site.collection_of("rendering/cities/sizing.html") == "rendering/cities" and site.collection_of("ways.html") == ""


def test_the_link_resolver_on_plain_strings() -> None:
    index = links.Index()
    index.add_part("ways.html", "ways", "ways")
    index.add("ways.html", "ways", None, '<p id="intro">x</p>')
    index.add("ways.html", "ways", "lanes", '<h2 id="lanes">L</h2><span id="inner"></span>')
    assert index.resolve("https://x", "") is None and index.resolve("//x/y", "") is None and index.resolve("", "") is None
    assert index.resolve("ways.html#inner", "") == links.Loc("ways", "lanes", "inner")
    assert index.resolve("ways.html#intro", "") == links.Loc("ways", None, "intro")
    assert index.resolve("assets/x.css", "") == "assets/x.css"
    with pytest.raises(links.LinkError, match="in-page anchor"):
        index.resolve("#x", "")
    assert links.site_href(links.Loc("ways", "lanes", "inner"), "cities/fabric/rows.html") == "../../ways/lanes.html#inner"
    assert links.single_href(links.Loc("ways", None, None), index) == "#ways" and links.single_href(links.Loc("ways", None, "intro"), index) == "#intro"
    assert links.asset_href("assets/x.css#y", "ways/lanes.html") == "../../assets/x.css#y"
    assert links.part_dir("SOURCES.html") == "sources" and links.part_dir("cities/fabric.html") == "cities/fabric"
    out, errs = links.rewrite('<a href="#nope">x</a>', page_rel="ways.html", from_dir="", index=index, here="ways/lanes.html", single=False, where="w")
    assert errs and "no id `nope`" in errs[0] and out == '<a href="#nope">x</a>'
    assert index.anchor("ways.html", "", "#") == links.Loc("ways", None)


def test_the_notes_of_a_small_page_and_of_the_single_page() -> None:
    page = {"a": "<a href=\"https://x\"><code>k</code></a> - 「q」", "b": "no source"}
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


def test_the_shell_and_the_navigation_data(tmp_path: pathlib.Path) -> None:
    page = site.shell("T", "cities/fabric/rows.html", "cities/fabric", "<p>x</p>", lazy_glossary=True)
    assert 'data-root="../../"' in page and 'href="../../assets/site.css"' in page and "data-lazy-glossary" in page
    assert "data-lazy-glossary" not in site.shell("T", "index.html", "", "x")
    parts = site.load(str(_record(tmp_path)))
    assert site.nav_js(parts).startswith("// DERIVED FILE") and site.grouped(parts)[-1][0] == site.REGISTRY_GROUP
