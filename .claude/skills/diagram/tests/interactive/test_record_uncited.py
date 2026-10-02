"""The "Uncited sources" part of the built record (feature 312, FR-012 - FR-014).

WHAT THESE PROVE. An entry in `sources/040-uncited-works/` builds into its own part of Sources, grouped by the same works
sections as the cited works, its anchors scoped so the two parts' sections never collide, with a page of its own, a
sidebar node of its own and a place on the home page and the one-page record; the build refuses a footnote that cites an
uncited entry, naming `make cite-uncited`, and an uncited entry that links the GM's own notes.
"""

from __future__ import annotations

import pathlib

import pytest

from l7r.diagram.interactive.record import site
from l7r.diagram.interactive.record.store import RecordError
from tests import _flat_record as fr

ENTRY = (
    '<h3 id="{key}"><code>{key}</code></h3>\n<p>{title}, a page ({url})</p>\n<p><em>What it is:</em> a page.</p>\n'
    "<p><em>Why it applies, and its limits:</em> it holds a figure.</p>\n<!-- tags: period=premodern; region=japan; kind=reference -->\n"
)


def _uncited(rec: pathlib.Path, key: str = "delta", url: str = "https://d.org/x", n: int = 40) -> pathlib.Path:
    src = rec / "sources"
    (src / "040-uncited-works.html").write_text('<h2 id="uncited-works">Uncited sources</h2>\n<p>Kept, not cited.</p>\n', encoding="utf-8")
    (src / "040-uncited-works").mkdir(exist_ok=True)
    (src / "040-uncited-works" / f"00{n}-{key}.html").write_text(ENTRY.format(key=key, title=key.title(), url=url), encoding="utf-8")
    return rec


def test_an_uncited_entry_builds_into_its_own_part_under_the_same_sections(tmp_path: pathlib.Path) -> None:
    files = site.build(str(_uncited(fr.write(tmp_path))))
    index = files["sources/index.html"]
    assert index.index('id="works-cited"') < index.index('id="uncited-works"'), "the uncited part follows the works cited"
    assert 'id="works-premodern-japan"' in index and 'id="uncited-works-premodern-japan"' in index, "the same section, scoped"
    assert 'id="uncited-works-premodern-japan-reference"' in index
    assert index.count('id="works-premodern-japan"') == 1
    assert "sources/delta.html" in files and "Delta, a page" in files["sources/delta.html"]
    nav = files["nav.js"]
    assert '"key": "sources/uncited", "title": "Uncited sources"' in nav and '"sources/uncited-works-premodern-japan"' in nav
    assert 'sources/uncited sources/uncited-works-premodern-japan' in files["sources/delta.html"], "its page opens its own nodes"
    assert "Uncited sources" in files["index.html"] and 'href="#uncited-works-premodern-japan"' in files["all.html"]


def test_a_footnote_citing_an_uncited_entry_is_refused_with_the_command(tmp_path: pathlib.Path) -> None:
    rec = _uncited(fr.write(tmp_path))
    fr.edit(rec, "0001-lanes.notes.html", '<a href="https://a"><code>alpha</code></a>', '<a href="https://d.org/x"><code>delta</code></a>')
    fr.edit(rec, "0001-lanes.notes.html", 'data-note="alpha"', 'data-note="delta"')
    fr.edit(rec, "0001-lanes.html", 'data-note="alpha"', 'data-note="delta"')
    with pytest.raises(RecordError, match="cites `delta`, an uncited source's entry - `make cite-uncited KEY=delta`"):
        site.build(str(rec))


def test_an_uncited_entry_linking_the_gms_notes_is_refused(tmp_path: pathlib.Path) -> None:
    rec = _uncited(fr.write(tmp_path), key="eps", url="https://github.com/EliAndrewC/gm-assistant/blob/main/setting/l7r.md")
    with pytest.raises(RecordError, match="eps: an uncited entry links the GM's own campaign notes"):
        site.build(str(rec))


def test_a_record_with_no_uncited_entry_builds_as_before(tmp_path: pathlib.Path) -> None:
    rec = fr.write(tmp_path)
    (rec / "sources" / "040-uncited-works.html").write_text('<h2 id="uncited-works">Uncited sources</h2>\n', encoding="utf-8")
    files = site.build(str(rec))
    assert '"sources/uncited"' not in files["nav.js"] and 'id="uncited-works-' not in files["sources/index.html"]
