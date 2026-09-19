"""`scripts/_quote_verbatim.py` (feature 251, FR-003): the character-for-character half of quote-check.

WHAT THESE PROVE (SC-002). The two differences a language model blurs and the record must not - a
hyphen written for the source's dash, an American spelling for the source's British one - are each
reported DIFFERS with the page's own text shown, and the same passage quoted exactly is VERBATIM. Then
the shapes the real citations pages carry: a translated quotation is matched by its ORIGINAL, a quote
nested in a quote is one passage, an absence note and a grounds note fetch nothing, a PDF and a refused
host go to the agent, and a host that refused once is never asked again.

NO NETWORK. `Pages(offline=dir)` reads saved pages named by the URL's hash, and the one test of the live
path hands `Pages` a fake opener.
"""

from __future__ import annotations

import importlib.util
import io
import json
import pathlib
import urllib.error

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_quote_verbatim", REPO / "scripts" / "_quote_verbatim.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


qv = _load()

# The fixture is BUILT, not written: the house-style hook rewrites a literal dash or British spelling in any file it
# sees, this one included, which is the very normalization the script exists to catch.
DASH, BRIT = chr(0x2014), "colo" + "ur"
EXACT = f"The {BRIT} of the grove {DASH} dark in winter {DASH} was remarked by every traveller."
SOURCE = f"<html><body><p>The {BRIT} of the grove {DASH} dark in winter {DASH} was\n   remarked by every traveller.</p><script>var x = 'never seen';</script></body></html>"
PAGE = qv.visible_text(SOURCE)


def test_an_exact_quotation_is_verbatim_across_a_line_wrap():
    assert qv.verdict(EXACT, PAGE) == {"quotation": "VERBATIM"}


def test_a_hyphen_for_the_sources_dash_differs_and_shows_the_page():
    got = qv.verdict(EXACT.replace(DASH, "-"), PAGE)
    assert got["quotation"] == "DIFFERS"
    assert DASH in got["page_text"]
    assert any("'-'" in d and DASH in d for d in got["differences"])
    assert got["only_reference_markers"] is False


def test_an_american_spelling_for_the_sources_british_one_differs():
    got = qv.verdict(EXACT.replace(BRIT, "color").replace("traveller", "traveler"), PAGE)
    assert got["quotation"] == "DIFFERS"
    assert any("page 'u'" in d for d in got["differences"])


def test_a_passage_the_page_does_not_carry_is_not_on_page():
    got = qv.verdict("Rice was transplanted in the fifth month by the whole hamlet together.", PAGE)
    assert got["quotation"] == "NOT-ON-PAGE"
    assert qv.verdict("anything", "")["quotation"] == "NOT-ON-PAGE"
    assert qv.verdict("", PAGE)["quotation"] == "NOT-ON-PAGE", "an empty passage proves nothing"
    assert qv.nearest("xyz", "abc") == (0.0, "")


def test_an_elided_quotation_matches_piece_by_piece_in_order():
    assert qv.verdict(f"The {BRIT} of the grove [...] was remarked by every traveller.", PAGE)["quotation"] == "VERBATIM"
    assert qv.verdict(f"was remarked ... The {BRIT} of the grove", PAGE)["quotation"] != "VERBATIM", "the pieces must come in the quoted order"


def test_the_pages_reference_markers_are_not_forgiven_but_are_named():
    page = qv.visible_text("<p>The pond was dug in 1581.[3] It fed forty fields.</p>")
    got = qv.verdict("The pond was dug in 1581. It fed forty fields.", page)
    assert got["quotation"] == "DIFFERS" and got["only_reference_markers"] is True


def test_visible_text_drops_script_and_breaks_at_blocks_not_inside_words():
    assert "never seen" not in PAGE
    assert qv.visible_text("<p>one</p><p>two</p>") == "one two"
    assert qv.visible_text("<p>菜の<a href='x'>花</a>（ナバナ）</p>") == "菜の花（ナバナ）", "an inline tag adds no space"
    assert qv.visible_text("<noscript>x</noscript></script>kept") == "kept", "a stray closing tag does not underflow"


def test_decode_honors_the_declared_charset_then_the_meta_then_falls_back():
    sjis = "<meta charset='shift_jis'><p>屋敷林</p>".encode("shift_jis")
    assert "屋敷林" in (qv.decode(sjis) or "")
    assert "屋敷林" in (qv.decode("屋敷林".encode("euc_jp"), "euc-jp") or "")
    assert qv.decode(b"plain", "no-such-charset") == "plain"


def test_a_nested_japanese_quote_is_one_passage():
    text = "title 「世界農業遺産「能登の里山里海」を代表する棚田」 and “curly one” and \"straight\" and 「unclosed"
    got = [text[a:b] for a, b in qv.top_level_quotes(text)]
    assert got == ["「世界農業遺産「能登の里山里海」を代表する棚田」", "“curly one”", '"straight"']


NOTE = (
    '<li id="fn-1"><a href="https://ja.example/wiki/アブラナ"><code>aburana</code></a> - 「Sown in autumn.」 '
    "(translated from the Japanese by this project; original: 「秋に種をまき」) and 「English kept as is」 "
    '<a class="fnback" href="../x.html#fnref-1">back</a></li>\n'
    '<li id="fn-2">no publicly readable source (searched 2026-09-12: 「a quote inside an absence note」) <a class="fnback" href="../x.html#fnref-2">back</a></li>\n'
    '<li id="fn-3">no source is owed: measured on our own maps<!-- a session note --> <a class="fnback" href="../x.html#fnref-3">back</a></li>\n'
    '<li id="fn-4"><a href="https://paper.example/a.pdf"><code>paper</code></a> - 「From a PDF.」 <a class="fnback" href="../x.html#fnref-4">back</a></li>\n'
    '<li id="fn-5"><a href="https://ja.example/wiki/アブラナ"><code>bare</code></a> - cited and quotes nothing <a class="fnback" href="../x.html#fnref-5">back</a></li>\n'
    '<li id="fn-6"><a href="SOURCES.html#own"><code>own</code></a> - 「Only in our registry.」 <a class="fnback" href="../x.html#fnref-6">back</a></li>\n'
    '<li id="fn-7">「a quote with no link at all」 <a class="fnback" href="../x.html#fnref-7">back</a></li>\n'
)
RESEARCH = (
    "<p>Rape is an autumn crop. It is sown into the drained stubble"
    '<sup class="fn"><a id="fnref-1" href="citations/x.html#fn-1">1</a></sup> and cut in spring'
    '<sup class="fn"><a id="fnref-2" href="citations/x.html#fn-2">2</a></sup>.</p>'
    '<!-- <sup class="fn"><a href="citations/x.html#fn-9">9</a></sup> a commented-out claim -->'
)


def test_footnotes_are_classified_and_a_translation_is_paired_with_its_original():
    notes = {n["id"]: n for n in qv.footnotes(NOTE)}
    assert [notes[f"fn-{i}"]["class"] for i in range(1, 8)] == ["citation", "absence", "grounds", "citation", "citation", "citation", "unlinked"]
    first = notes["fn-1"]["passages"]
    assert first[0] == {"quote": "Sown in autumn.", "original": "秋に種をまき", "language": "the Japanese"}
    assert first[1] == {"quote": "English kept as is", "original": "", "language": ""}
    assert notes["fn-2"]["passages"] == [], "an absence note's own quotations are not citations"
    assert notes["fn-1"]["links"] == ["https://ja.example/wiki/アブラナ"], "the back link is not a source"


def test_the_assertion_is_the_sentence_the_marker_closes():
    claims = qv.assertions(RESEARCH)
    assert claims["fn-1"] == "It is sown into the drained stubble"
    assert claims["fn-2"].endswith("and cut in spring")
    assert "fn-9" not in claims, "a commented-out marker is not on the page"


def _offline(tmp_path: pathlib.Path, url: str, body: str) -> None:
    (tmp_path / qv.Pages.name_for(url)).write_text(body, encoding="utf-8")


def test_the_report_matches_the_original_and_sends_the_residue_to_the_agent(tmp_path):
    _offline(tmp_path, "https://ja.example/wiki/アブラナ", "<p>菜の花は、秋に種をまき、冬を越す。</p><p>English kept as is, mostly.</p>")
    pages = qv.Pages(offline=tmp_path)
    entries = {e["id"]: e for e in qv.report(qv.footnotes(NOTE), qv.assertions(RESEARCH), pages)}
    one = entries["fn-1"]
    assert [p["quotation"] for p in one["passages"]] == ["VERBATIM", "VERBATIM"]
    assert one["passages"][0]["matched"] == "original" and one["passages"][1]["matched"] == "quote"
    assert one["readability"] == "READABLE" and one["assertion"] == "It is sown into the drained stubble"
    assert entries["fn-2"]["readability"] == "-" and entries["fn-3"]["class"] == "grounds"
    assert entries["fn-4"]["passages"][0]["quotation"] == "NOT-CHECKED" and "PDF" in entries["fn-4"]["passages"][0]["why"]
    assert entries["fn-5"]["passages"] == [] and entries["fn-5"]["readability"] == "-"
    assert entries["fn-6"]["readability"].startswith("NOT-READABLE (the link is this project's own page)")
    text = qv.render("x", list(entries.values()), {"bad.example": "URLError: refused"})
    assert "NO-QUOTE" in text and "NOT-CHECKED" in text and "refused: bad.example" in text and "VERBATIM 2" in text


def test_a_page_that_was_read_and_lacks_the_passage_is_not_readable(tmp_path):
    url = "https://en.example/page"
    _offline(tmp_path, url, f"<p>The {BRIT} of the grove {DASH} dark in winter.</p>")
    note = {
        "id": "fn-1",
        "key": "k",
        "links": [url, "https://en.example/missing"],
        "class": "citation",
        "passages": [{"quote": "The color of the grove - dark in winter.", "original": "", "language": ""}],
    }
    got = qv.judge_note(note, qv.Pages(offline=tmp_path))
    assert got["passages"][0]["quotation"] == "DIFFERS"
    assert got["readability"].startswith("NOT-READABLE (the page was read")
    text = qv.render("x", [{**got, "assertion": ""}], {})
    assert "page has:" in text and "DIFFERS" in text
    gone = qv.judge_note({**note, "links": ["https://en.example/missing"]}, qv.Pages(offline=tmp_path))
    assert gone["passages"][0]["quotation"] == "UNFETCHABLE" and gone["readability"] == "-"


class _Resp(io.BytesIO):
    def __init__(self, body: bytes, ctype: str) -> None:
        super().__init__(body)
        import email.message

        self.headers = email.message.Message()
        self.headers["Content-Type"] = ctype

    def __enter__(self):  # noqa: ANN204
        return self

    def __exit__(self, *a: object) -> None:
        self.close()


def test_the_live_path_asks_a_refusing_host_once_and_reads_pdf_by_content_type():
    calls: list[str] = []

    def opener(req, timeout):  # noqa: ANN001, ANN202
        calls.append(req.full_url)
        if "refuses" in req.full_url:
            raise urllib.error.URLError("certificate verify failed")
        if "download" in req.full_url:
            return _Resp(b"%PDF-1.7", "application/pdf")
        if "garbled" in req.full_url:
            return _Resp(b"\xff\xfe\x00\xd8\x00", "text/html; charset=utf-8")
        return _Resp("<p>屋敷林 stands north.</p>".encode("shift_jis"), "text/html; charset=Shift_JIS")

    pages = qv.Pages(opener=opener)
    assert pages.get("https://refuses.example/a")["state"] == "UNFETCHABLE"
    assert "already refused" in pages.get("https://refuses.example/b")["why"]
    assert pages.get("https://refuses.example/a")["state"] == "UNFETCHABLE" and len(calls) == 1, "one attempt per host, and a URL is never fetched twice"
    assert pages.get("https://ok.example/download?id=3")["state"] == "NOT-CHECKED"
    assert pages.get("https://ok.example/wiki/屋敷林")["text"] == "屋敷林 stands north."
    assert "%E5%B1%8B" in calls[-1], "a non-ASCII path is percent-encoded for the request"
    assert pages.get("https://ok.example/garbled")["state"] in ("NOT-CHECKED", "FETCHED")
    assert pages.get("SOURCES.html#key")["state"] == "OWN"


def test_main_writes_the_report_the_agent_is_handed(tmp_path, capsys):
    research = tmp_path / ".claude/skills/diagram/research"
    (research / "citations").mkdir(parents=True)
    (research / "x.html").write_text(RESEARCH, encoding="utf-8")
    (research / "citations" / "x.html").write_text(NOTE, encoding="utf-8")
    saved = tmp_path / "pages"
    saved.mkdir()
    _offline(saved, "https://ja.example/wiki/アブラナ", "<p>秋に種をまき</p>")
    out = tmp_path / "report.json"
    assert qv.main(["x", "--root", str(tmp_path), "--offline", str(saved), "--json", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["page"] == "x" and len(data["footnotes"]) == 7
    assert "report for quote-check" in capsys.readouterr().out
    assert qv.main(["absent", "--root", str(tmp_path)]) == 2
    assert qv.main(["x", "--root", str(tmp_path), "--offline", str(saved)]) == 0, "with no --json the report lands under .git/quote-verbatim/"
    assert (tmp_path / ".git" / "quote-verbatim" / "x.json").is_file()


def test_a_scoped_check_names_its_notes_and_fetches_nothing_else(tmp_path, capsys):
    assert qv.wanted("") is None and qv.wanted("fn-2, 4-6") == {"fn-2", "fn-4", "fn-5", "fn-6"}
    research = tmp_path / ".claude/skills/diagram/research"
    (research / "citations").mkdir(parents=True)
    (research / "x.html").write_text(RESEARCH, encoding="utf-8")
    (research / "citations" / "x.html").write_text(NOTE, encoding="utf-8")
    out = tmp_path / "r.json"
    assert qv.main(["x", "--root", str(tmp_path), "--offline", str(tmp_path), "--notes", "3-4", "--json", str(out)]) == 0
    capsys.readouterr()
    assert [f["id"] for f in json.loads(out.read_text(encoding="utf-8"))["footnotes"]] == ["fn-3", "fn-4"]


def test_a_phrase_quoted_inside_the_notes_own_gloss_is_not_a_passage():
    """Found on `ways` fn-23: "(the path on the baulk; 「never crosses row crops」 is this page's)" is the note's gloss."""
    got = qv.passages("「Sown in autumn.」 (translated from the Japanese by this project; original: 「秋に種をまき」) (a gloss; 「our own phrase」 is this page's) and 「a second passage」")
    assert [p["quote"] for p in got] == ["Sown in autumn.", "a second passage"]
    assert got[0]["original"] == "秋に種をまき"
