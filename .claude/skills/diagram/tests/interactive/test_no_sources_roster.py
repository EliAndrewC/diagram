"""No section of the record keeps a `Sources:` roster (feature 292, T25; the GM, 2026-09-29: the Sources section goes,
and *"we should never be removing a citation ... keep that information just not in a sources section"*).

The sweep rewrote every section under `research/STYLE.md`, which has no roster: a section's sources are the keys its
footnotes cite (`sources.footnote_sources`). This holds the sweep's completion - a roster written back into a section,
or a new section written in the old form, fails here. A roster mentioned inside an HTML comment (a REMOVED note) is
history for the next session and is not shown.
"""

from __future__ import annotations

import pathlib
import re

from l7r.diagram.interactive.sources import RESEARCH_DIR

_COMMENT = re.compile(r"<!--.*?-->", re.S)
_ROSTER = re.compile(r"<strong>\s*Sources:\s*</strong>")


def roster_sections(research_dir: str = RESEARCH_DIR) -> list[str]:
    """The research and rendering fragments whose visible text carries a `Sources:` roster."""
    root = pathlib.Path(research_dir)
    out = []
    for p in sorted(root.rglob("[0-9][0-9][0-9]-*.html")):
        rel = p.relative_to(root).as_posix()
        if rel.split("/")[0] in ("sources", "citations") or p.name.endswith((".notes.html", ".originals.html")):
            continue
        if _ROSTER.search(_COMMENT.sub("", p.read_text(encoding="utf-8"))):
            out.append(rel)
    return out


def test_no_section_keeps_a_sources_roster() -> None:
    assert roster_sections() == []


def test_the_check_sees_a_roster_and_not_a_comment(tmp_path: pathlib.Path) -> None:
    (tmp_path / "ways").mkdir()
    (tmp_path / "ways" / "010-a.html").write_text('<h2 id="a">A</h2>\n<p><strong>Sources:</strong> <a href="x">k</a></p>\n', encoding="utf-8")
    (tmp_path / "ways" / "020-b.html").write_text('<h2 id="b">B</h2>\n<!-- REMOVED: the <strong>Sources:</strong> roster -->\n', encoding="utf-8")
    assert roster_sections(str(tmp_path)) == ["ways/010-a.html"]
