"""Feature 211: `make citations` writes each citations page's derived script and works section; `--check` tells a stale one."""

from __future__ import annotations

import pathlib

from l7r.diagram.interactive.citations import WORKS_CLOSE, WORKS_OPEN
from l7r.diagram.tools import citations_asset

_SOURCES = (
    '<main><h3 id="k-1"><code>k-1</code></h3>\n<p>Paper X (https://x.y/z)<!-- READ --></p>\n'
    "<p><em>What it is:</em> A paper.</p>\n<p><em>Why it applies, and its limits:</em> It applies.</p>\n"
    '<h3 id="k-2"><code>k-2</code></h3>\n<p>Paper Y (https://a.b/c)</p>\n</main>'
)


def _record(root: pathlib.Path, keys: str = "k-1") -> None:
    (root / "citations").mkdir(parents=True, exist_ok=True)
    (root / "SOURCES.html").write_text(_SOURCES, encoding="utf-8")
    (root / "p.html").write_text("<p>x<sup class=\"fn\"><a id=\"fnref-1\" href=\"citations/p.html#fn-1\">1</a></sup></p>", encoding="utf-8")
    notes = "".join(f'<li id="fn-{i + 1}"><a href="https://x.y/z"><code>{k}</code></a> - 「a quoted passage」 <a class="fnback" href="../p.html#fnref-{i + 1}">back</a></li>' for i, k in enumerate(keys.split()))
    (root / "citations" / "p.html").write_text(f"<h1>c</h1>\n{WORKS_OPEN}\n{WORKS_CLOSE}\n<section class=\"footnotes\"><ol>{notes}</ol></section>", encoding="utf-8")


def test_write_then_check_is_in_sync_and_an_edit_or_an_absence_is_stale(tmp_path: pathlib.Path, capsys: object) -> None:
    _record(tmp_path)
    assert citations_asset.main(["--check", "--research-dir", str(tmp_path)]) == 1, "no script yet, works empty: stale"
    assert citations_asset.main(["--research-dir", str(tmp_path)]) == 0
    js = (tmp_path / "citations" / "p.js").read_text(encoding="utf-8")
    assert js.startswith("// DERIVED FILE") and '"fn-1"' in js
    page = (tmp_path / "citations" / "p.html").read_text(encoding="utf-8")
    assert '<h3 id="work-k-1"><a href="https://x.y/z"><code>k-1</code></a></h3>' in page and "<p><em>What it is:</em> A paper.</p>" in page
    assert citations_asset.main(["--check", "--research-dir", str(tmp_path)]) == 0
    (tmp_path / "citations" / "p.js").write_text(js + "// a hand edit", encoding="utf-8")
    assert citations_asset.main(["--check", "--research-dir", str(tmp_path)]) == 1
    assert citations_asset.main(["--research-dir", str(tmp_path)]) == 0, "rewritten"
    assert citations_asset.main(["--check", "--research-dir", str(tmp_path)]) == 0


def test_a_cited_key_with_no_write_up_fails_both_modes_and_a_missing_citations_page_is_reported(tmp_path: pathlib.Path, capsys: object) -> None:
    _record(tmp_path, "k-1 k-2")
    assert citations_asset.main(["--research-dir", str(tmp_path)]) == 1, "written, but k-2 has no write-up"
    assert citations_asset.main(["--check", "--research-dir", str(tmp_path)]) == 1
    (tmp_path / "q.html").write_text("<p>a page with no citations page</p>", encoding="utf-8")
    assert citations_asset.main(["--check", "--research-dir", str(tmp_path)]) == 1
