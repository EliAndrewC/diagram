"""`record/archive.py` - the source archive as the record build sees it (feature 309).

WHAT THESE PROVE. The census counts every URL a registry entry holds (its comments' too - where a session recorded the
page it read) and every URL a footnote links (its comments' not); a URL's id is stable across the spellings a citation
gives it; the build refuses a cited URL with no manifest row, or with an upload pending past its week, naming the command
that archives it; a source page shows a link to each archived copy, the GM's downloaded copy once, and says so where no
copy could be archived; the real record carries its manifest, so the refusal can never be skipped by its absence.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib

import pytest

from l7r.diagram.interactive.record import archive, site
from l7r.diagram.interactive.record.store import RecordError
from l7r.diagram.interactive.sources import RESEARCH_DIR
from tests import _flat_record as fr

TODAY = datetime.date(2026, 10, 2)


def _row(url: str, outcome: str = "archived", captured: str = "2026-10-02T12:00:00+00:00", **more: object) -> dict:
    return {"url": url, "outcome": outcome, "captured": captured, "path": f"alpha/{archive.url_id(url)}/20261002T120000Z", **more}


def _manifest(rec: pathlib.Path, *rows: dict) -> None:
    d = rec / archive.ARCHIVE_DIR
    d.mkdir(exist_ok=True)
    for row in rows:
        uid = archive.url_id(row["url"])
        (d / uid[:2]).mkdir(exist_ok=True)
        (d / uid[:2] / f"{uid}.json").write_text(json.dumps(row), encoding="utf-8")


@pytest.mark.parametrize(
    ("cited", "clean"),
    [
        ("https://a.org/x?p=1&amp;q=2", "https://a.org/x?p=1&q=2"),
        ("https://a.org/x#part", "https://a.org/x"),
        ("https://a.org/x).", "https://a.org/x"),
        ("https://ja.wikipedia.org/wiki/町屋_(商家)", "https://ja.wikipedia.org/wiki/町屋_(商家)"),
        ("https://a.org/x;", "https://a.org/x"),
    ],
)
def test_a_url_is_cleaned_as_a_citation_writes_it(cited: str, clean: str) -> None:
    assert archive.clean(cited) == clean
    assert archive.url_id(cited) == archive.url_id(clean) and len(archive.url_id(cited)) == 12


def test_the_census_takes_registry_comments_and_footnote_links_but_not_footnote_comments(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    fr.edit_entry(rec, "0010-alpha.html", "a work (https://a)", "a work (https://a)<!-- READ 2026-10-02 at https://a.org/read.pdf -->")
    (rec / "questions" / "0002-bridges.notes.html").write_text('<li data-note="x"><a href="https://direct.org/p">x</a> - 「q」<!-- searched https://trail.org --></li>\n', encoding="utf-8")
    cited = archive.cited(str(rec))
    assert set(cited) == {"https://a", "https://a.org/read.pdf", "https://b", "https://direct.org/p"}
    assert cited["https://a"].keys == ["alpha"] and cited["https://a"].notes == ["0001-lanes.notes.html"]
    assert cited["https://a.org/read.pdf"].keys == ["alpha"], "the page a session read the passage from is cited"
    assert cited["https://direct.org/p"].keys == [] and cited["https://direct.org/p"].notes == ["0002-bridges.notes.html"]


def test_a_record_with_no_manifest_is_not_held_to_one(tmp_path: pathlib.Path) -> None:
    assert archive.refusals(str(fr.write(tmp_path)), TODAY) == []


def test_a_cited_url_with_no_row_is_refused_with_its_command(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    _manifest(rec, _row("https://a"))
    out = archive.refusals(str(rec), TODAY)
    assert out == ["archive: https://b (beta) has no archived copy - `make archive URL='https://b'` archives it (feature 309)"]


def test_a_pending_upload_is_covered_for_a_week_then_refused(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    _manifest(rec, _row("https://a", "pending-upload", "2026-09-28T00:00:00+00:00"), _row("https://b", "unreachable", reason="HTTP 404"))
    assert archive.refusals(str(rec), TODAY) == []
    late = archive.refusals(str(rec), TODAY + datetime.timedelta(days=archive.PENDING_DAYS))
    assert late == ["archive: https://a (alpha) has its upload pending since 2026-09-28 - `make archive URL='https://a'` archives it (feature 309)"]


def test_a_row_with_an_unknown_outcome_does_not_cover_its_url() -> None:
    assert not archive.covered({"outcome": "maybe"}, TODAY)
    assert archive.covered({"outcome": "partial"}, TODAY)


def test_the_entry_line_links_each_copy_and_the_gm_copy_once() -> None:
    rows = {
        archive.url_id("https://a"): _row("https://a", gm_copies=["alpha/gm-copy/a.pdf"]),
        archive.url_id("https://a.org/read.pdf"): _row("https://a.org/read.pdf", "partial", gm_copies=["alpha/gm-copy/a.pdf"]),
        archive.url_id("https://gone.org"): _row("https://gone.org", "unreachable", path="", reason="HTTP 404"),
    }
    line = archive.entry_line("<p>A (https://a)<!-- READ at https://a.org/read.pdf --> and https://gone.org and https://new.org</p>", rows)
    assert line.startswith('<p class="archived"><em>Archived:</em> ') and line.endswith(" (private)</p>\n")
    assert f'href="{archive.REPO}/tree/main/alpha/{archive.url_id("https://a")}/20261002T120000Z"' in line
    assert "archived copy, 2026-10-02" in line and "archived partial copy, 2026-10-02" in line
    assert line.count("the GM's downloaded copy") == 1 and f"{archive.REPO}/blob/main/alpha/gm-copy/a.pdf" in line
    assert "no copy could be archived (HTTP 404, 2026-10-02)" in line
    assert archive.entry_line("<p>no URL here</p>", rows) == "" and archive.entry_line("<p>https://new.org</p>", rows) == ""


def test_a_source_page_shows_its_archived_copy_and_the_build_refuses_a_missing_one(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    _manifest(rec, _row("https://a"))
    with pytest.raises(RecordError, match=r"https://b \(beta\) has no archived copy"):
        site.build(str(rec))
    _manifest(rec, _row("https://b"))
    files = site.build(str(rec))
    page = files["sources/alpha.html"]
    assert '<p class="archived"><em>Archived:</em> <a href="https://github.com/EliAndrewC/diagram-research/tree/main/alpha/' in page
    assert page.index('class="archived"') > page.index("a work ("), "the line sits under the citation line"
    assert 'class="archived"' not in files["sources/gamma.html"], "the GM's campaign notes cite no URL"


def test_the_real_record_carries_its_manifest() -> None:
    """The refusal is skipped for a record with no `archive/` (a test's small record) - so the real one must have it."""
    assert os.path.isfile(os.path.join(RESEARCH_DIR, archive.ARCHIVE_DIR, archive.GM_COPIES))


def test_an_entry_with_no_heading_or_no_citation_line_takes_no_archived_copy_line() -> None:
    """`Build.entry_html`'s two early returns: an entry with no heading is shown as written, and one with a heading but no
    paragraph gets its labels and nothing else - there is no citation line to hang an archived-copy line under."""
    from l7r.diagram.interactive.record import site_pages as sp  # noqa: PLC0415

    class Labels:
        def labels(self, key: str) -> str:
            return f"<p class=labels>{key}</p>"

    b = site.Build.__new__(site.Build)
    b.catalog, b.archive = Labels(), {}
    assert b.entry_html(sp.Item("k", "<div>no heading</div>", "", "")) == "<div>no heading</div>"
    got = b.entry_html(sp.Item("k", "<h3>Key</h3><ul><li>x</li></ul>", "", ""))
    assert got == "<h3>Key</h3>\n<p class=labels>k</p><ul><li>x</li></ul>"
