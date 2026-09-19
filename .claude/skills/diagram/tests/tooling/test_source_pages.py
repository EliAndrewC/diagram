"""`scripts/_source_pages.py` (feature 255, FR-006): the pages `source-reader` greps instead of fetching.

WHAT THESE PROVE. A reachable page is saved as its visible text, one sentence to a line (Latin and CJK stops), under
a name that carries its order and host; a page the fetcher could not reach is LISTED with its state and why and no
file, so the reader knows what is left to it; a pointer given twice is saved once; no pointer is a usage error.

NO NETWORK: `Pages` is handed a fake opener, the same seam `test_quote_verbatim.py` uses.
"""

from __future__ import annotations

import importlib.util
import io
import pathlib
import urllib.error

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_source_pages", REPO / "scripts" / "_source_pages.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sp = _load()


class _Resp(io.BytesIO):
    class headers:  # noqa: N801
        @staticmethod
        def get(_name: str, default: str = "") -> str:
            return "text/html; charset=utf-8"

        @staticmethod
        def get_content_charset() -> str:
            return "utf-8"

    def __enter__(self):  # noqa: ANN204
        return self

    def __exit__(self, *_a: object) -> None:
        self.close()


def _opener(req, timeout: int = 0):  # noqa: ANN001, ANN202
    if "refuses" in req.full_url:
        raise urllib.error.URLError("403")
    return _Resp("<html><body><p>A dike is five meters wide. One with a sty is wider! 堤は広い。池は深い。</p></body></html>".encode())


def test_file_names_and_wrapping() -> None:
    assert sp.file_for(3, "https://www.FAO.org/4/x.htm") == "03-www.fao.org.txt"
    assert sp.file_for(1, "not a url") == "01-page.txt"
    assert sp.wrapped("One. Two! 三。四") == "One.\nTwo!\n三。\n四\n"


def test_save_writes_pages_and_a_manifest(tmp_path: pathlib.Path) -> None:
    pages = sp.qv.Pages(opener=_opener)
    urls = ["https://ok.example/a", "https://refuses.example/b", "https://ok.example/a", "https://ok.example/c.pdf"]
    rows = sp.save(urls, tmp_path / "out", pages)
    assert [r["state"] for r in rows] == ["FETCHED", "UNFETCHABLE", "NOT-CHECKED"], "a repeated pointer is saved once"
    text = (tmp_path / "out" / "01-ok.example.txt").read_text(encoding="utf-8")
    assert text.splitlines() == ["A dike is five meters wide.", "One with a sty is wider!", "堤は広い。", "池は深い。"]
    manifest = (tmp_path / "out" / "MANIFEST.txt").read_text(encoding="utf-8").splitlines()
    assert manifest[0] == "pointer | file | state" and manifest[1].startswith("https://ok.example/a | 01-ok.example.txt | FETCHED - ")
    assert manifest[2].startswith("https://refuses.example/b | - | UNFETCHABLE - ") and "| - | NOT-CHECKED - a PDF" in manifest[3]


def test_main(tmp_path: pathlib.Path, capsys) -> None:  # noqa: ANN001
    assert sp.main([str(tmp_path / "o"), "https://ok.example/a"], pages=sp.qv.Pages(opener=_opener)) == 0
    assert "saved 1 of 1" in capsys.readouterr().out
    assert sp.main([str(tmp_path / "o")]) == 2
    assert "no pointer given" in capsys.readouterr().err
