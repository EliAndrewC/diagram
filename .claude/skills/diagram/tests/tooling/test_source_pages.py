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


def test_a_second_save_adds_to_the_directory_and_never_overwrites(tmp_path: pathlib.Path) -> None:
    """D15: a write session's second batch, numbered from 01 again, overwrote the first batch's pages."""
    pages = sp.qv.Pages(opener=_opener)
    out = tmp_path / "out"
    sp.save(["https://ok.example/a", "https://refuses.example/b"], out, pages)
    first = (out / "01-ok.example.txt").read_text(encoding="utf-8")
    rows = sp.save(["https://ok.example/a", "https://refuses.example/b", "https://ok.example/c"], out, sp.qv.Pages(opener=_opener))
    assert [r["pointer"] for r in rows] == ["https://ok.example/a", "https://refuses.example/b", "https://ok.example/c"]
    assert [r["file"] for r in rows] == ["01-ok.example.txt", "-", "04-ok.example.txt"], "a saved page is kept; a failed one is retried past every old number"
    assert (out / "01-ok.example.txt").read_text(encoding="utf-8") == first
    assert "https://ok.example/c | 04-ok.example.txt | FETCHED" in (out / "MANIFEST.txt").read_text(encoding="utf-8")


def test_a_third_save_numbers_past_a_retried_page(tmp_path: pathlib.Path) -> None:
    """267 G7: a retried page took 17-20 while the rows still counted 16, so the next save wrote 17-20 again."""
    down = {"https://refuses.example/b"}

    def opener(req, timeout: int = 0):  # noqa: ANN001, ANN202
        if req.full_url in down:
            raise urllib.error.URLError("403")
        return _Resp(f"<html><body><p>{req.full_url}</p></body></html>".encode())

    out = tmp_path / "out"
    sp.save(["https://ok.example/a", "https://refuses.example/b"], out, sp.qv.Pages(opener=opener))
    down.clear()
    retried = sp.save(["https://refuses.example/b"], out, sp.qv.Pages(opener=opener))
    assert [r["file"] for r in retried] == ["01-ok.example.txt", "03-refuses.example.txt"]
    rows = sp.save(["https://refuses.example/c"], out, sp.qv.Pages(opener=opener))
    assert rows[-1]["file"] == "04-refuses.example.txt", "a new page is numbered past the retried one, never onto it"
    assert "example/b" in (out / "03-refuses.example.txt").read_text(encoding="utf-8"), "the retried page survives"
    assert sp.next_index([{"file": "-"}, {"file": "09-x.txt"}]) == 10


def test_a_long_page_is_saved_in_parts_and_a_quoted_one_as_an_excerpt(tmp_path: pathlib.Path) -> None:
    """D19 (R10): a book-length saved page cost one check 200,026 characters of reading."""
    text = "".join(f"Sentence {i} of the book says little.\n" for i in range(3000))
    pieces = sp.parts(text, 20_000)
    assert len(pieces) > 1 and all(len(p) <= 20_000 for p in pieces) and "".join(pieces) == text
    assert sp.parts("x" * 45, 20) == ["x" * 20, "x" * 20, "x" * 5], "a single long line is cut where it must be"
    assert sp.excerpt("short page", ["q"]) == "short page", "a page under the limit is kept whole"
    quoted = "Sentence 2500 of the book says little."
    ex = sp.excerpt(text, [quoted, "a passage the page does not carry at all"], head=500, window=200, limit=10_000)
    assert ex.startswith("[EXCERPT of a") and "1 of 2 quoted passage(s) found" in ex
    assert quoted in " ".join(ex.split()) and "Sentence 0 of the book" in ex and "characters not copied" in ex
    assert len(ex) < 2_000

    class _Pages:
        @staticmethod
        def get(_url: str) -> dict:
            return {"state": "FETCHED", "text": text}

    rows = sp.save(["https://book.example/a"], tmp_path / "o", _Pages())
    assert "parts" in rows[0]["file"] and (tmp_path / "o" / "01-book.example.p1.txt").is_file()
    rows = sp.save(["https://book.example/b"], tmp_path / "q", _Pages(), [quoted])
    assert "saved as an excerpt" in rows[0]["why"]
