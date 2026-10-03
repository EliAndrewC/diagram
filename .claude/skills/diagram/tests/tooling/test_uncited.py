"""`scripts/_uncited.py` - the uncited pages, judged once (feature 312, FR-006 - FR-011).

WHAT THESE PROVE. The set is the ledger's and the cache's URLs with no manifest row, less what a registry entry carries,
what has a verdict and a blocked domain, plus the manifest rows nothing cites; the rule rules a search or listing URL
no-substance (the review's MediaWiki forms included) and a copy of a cited or earlier page a duplicate, and leaves the rest;
a page no route reads is unreadable with its access state, and one the Wayback Machine holds is read from it; bundles
close at their character or token budget, put an oversize page alone and in parts, and name every file; a bundle's
verdicts are refused when an id is missing or a reason unknown, and applied into the not-kept list and the kept list,
a pre-hold capture losing its row; a calibration run is scored per leg. NO NETWORK.
"""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


un = _load("_uncited")
ar, src, at = un.ar, un.src, un.at


def _home() -> pathlib.Path:
    return pathlib.Path(os.environ["L7R_SOURCES_HOME"])


@pytest.fixture(autouse=True)
def _attempts_here(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The conftest's seam pointed at this test's own tree, so a test's log is the tree it builds."""
    monkeypatch.setenv("L7R_ATTEMPTS_ROOT", str(tmp_path))


def _root(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / ".git").mkdir()
    (tmp_path / un.SOURCES / "010-works-cited").mkdir(parents=True)
    (tmp_path / ar.MANIFEST.parent).mkdir(parents=True, exist_ok=True)
    return tmp_path


def _ledger(*urls: str) -> None:
    src.append(_home(), [src.line({"feature": "288"}, u, "pending") for u in urls])


def test_the_set_is_the_unjudged_uncited_reads(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    _ledger("https://a.org/1", "https://b.org/2", "https://c.org/3", "https://d.org/4", "https://github.com/EliAndrewC/l7r/blob/master/setting/l7r.md")
    with open(_home() / src.LEDGER, "a", encoding="utf-8") as fh:  # written past the ledger's own refusal: the set refuses it too
        fh.write(json.dumps({"url": "grokipedia.com/x", "outcome": "pending"}) + "\n")
    (root / un.SOURCES / "010-works-cited" / "0010-c.html").write_text("<p>C (https://www.c.org/3/)</p>", encoding="utf-8")
    ar.write_row(root, "https://b.org/2", {"url": "https://b.org/2", "keys": ["b"], "notes": []})
    ar.write_row(root, "https://e.org/held", {"url": "https://e.org/held", "keys": [], "notes": []})
    at.write(root, [un.line("https://d.org/4", ["off-topic"], "source-filter")], un.NOT_KEPT)
    src.append(_home(), [src.line({}, "https://zh.org/hans/x", "cited:c"), src.line({}, "https://f.org/6", "cited:gone-key")])
    assert un.uncited_set(root) == ["https://a.org/1", "https://e.org/held", "https://f.org/6"], "a mark whose key has an entry is cited"


@pytest.mark.parametrize(
    ("url", "hit"),
    [
        ("https://duckduckgo.com/html/?q=torii", True),
        ("https://zh.wikipedia.org/w/index.php?search=村庙&title=Special:搜索", True),
        ("https://ja.wikipedia.org/wiki/Category:東京都の旧郷社", True),
        ("https://ja.wikipedia.org/wiki/特別:検索", True),
        ("https://ja.wikipedia.org/w/api.php?action=parse", True),
        ("https://zh.wikisource.org/w/index.php?title=齊民要術&action=raw", True),
        ("https://ja.wikipedia.org/wiki/鳥居", False),
        ("https://www.jstage.jst.go.jp/article/x/1/0/1_1/_article", False),
    ],
)
def test_the_no_substance_rule(url: str, hit: bool) -> None:
    assert un.no_substance(url) is hit


def test_the_rule_rules_searches_and_duplicates_and_leaves_the_rest(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    (root / un.SOURCES / "010-works-cited" / "0010-c.html").write_text("<p>C (https://c.org/3)</p>", encoding="utf-8")
    src.put(_home(), "https://c.org/3", "The cited text.")
    src.put(_home(), "https://a.org/1", "The  cited text. ")
    src.put(_home(), "https://b.org/2", "Something else.")
    src.put(_home(), "https://b.org/3", "Something else.")
    got = un.rule(root, ["https://duckduckgo.com/?q=x", "https://a.org/1", "https://b.org/2", "https://b.org/3", "https://z.org/none", "https://[^", "https://kotobank.jp/word/${enc}", "https://jstage.jst.go.jp"])
    assert got == {"no-substance": 1, "duplicate": 2}
    assert {x["raw"]: x["access"] for x in at.read(root, un.NOT_KEPT) if x["reasons"] == ["unreadable"]} == {"https://[^": "gone", "https://kotobank.jp/word/${enc}": "gone"}
    assert not un.wellformed("https://ja.wikipedia.org/wiki/$u") and not un.wellformed("https://localhost/x") and un.wellformed("https://jstage.jst.go.jp")
    nk = {x["raw"]: x for x in at.read(root, un.NOT_KEPT)}
    assert nk["https://a.org/1"]["note"] == "the same text as a cited page"
    assert nk["https://b.org/3"]["note"] == "the same text as https://b.org/2"
    assert "https://b.org/2" not in nk and nk["https://duckduckgo.com/?q=x"]["basis"] == "rule"


def test_a_line_takes_only_known_reasons_and_access_states() -> None:
    with pytest.raises(ValueError, match="at least one"):
        un.line("https://a.org", [], "rule")
    with pytest.raises(ValueError, match="each one of"):
        un.line("https://a.org", ["boring"], "rule")
    with pytest.raises(ValueError, match="access"):
        un.line("https://a.org", ["unreadable"], "rule", access="lost")
    assert un.line("https://a.org", ["unreadable"], "rule", access="gone")["access"] == "gone"


class Stand:
    """A browser serving fixed replies by URL."""

    def __init__(self, pages: dict) -> None:
        self.pages = pages

    def get(self, url: str):  # noqa: ANN201
        return self.pages.get(url) or ar.Fetched(url, error="net::ERR_NAME_NOT_RESOLVED")

    def render(self, url: str) -> tuple[str, str]:
        return "", self.pages[url].body.decode()


def _page(url: str, status: int = 200, body: str = "<p>x</p>") -> ar.Fetched:
    return ar.Fetched(url, status, url, "text/plain", body.encode())


@pytest.mark.parametrize(("status", "state"), [(401, "paywalled"), (402, "paywalled"), (403, "bot-refused"), (429, "bot-refused"), (404, "gone"), (410, "gone"), (503, "down"), (None, "down")])
def test_a_failed_fetch_has_its_access_state(status: int | None, state: str) -> None:
    assert un.access_of(ar.Fetched("https://a.org", status)) == state


def test_the_fetch_reads_live_then_the_snapshot_else_rules_unreadable(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    live, old, shell = "Live text. " * 70, "Old text. " * 20, "百度百科"
    snap = "http://web.archive.org/web/2020/https://b.org/2"
    reply = {"archived_snapshots": {"closest": {"available": True, "url": snap, "timestamp": "20200101000000"}}}
    pages = {
        "https://a.org/1": _page("https://a.org/1", body=live),
        "https://b.org/2": _page("https://b.org/2", 404),
        ar.WAYBACK + ar.urllib.parse.quote("https://b.org/2", safe=""): ar.Fetched("", 200, "", "application/json", json.dumps(reply).encode()),
        snap.replace("http://", "https://", 1): _page(snap, body=old),
        "https://c.org/3": _page("https://c.org/3", 403),
        "https://e.org/5": _page("https://e.org/5", 403),
        "https://f.org/6": _page("https://f.org/6", body="Short."),
    }
    src.put(_home(), "https://d.org/4", "Already saved. " * 50)
    src.put(_home(), "https://e.org/5", shell)
    src.put(_home(), "https://g.org/7", "A short museum record of a charcoal bale, 56 by 31 by 36 cm, of straw, two pieces." * 2)
    got = un.fetch(root, [f"https://{h}" for h in ("a.org/1", "b.org/2", "c.org/3", "d.org/4", "e.org/5", "f.org/6", "x.org/?q=1")], Stand(pages))
    assert got == {"read": 2, "unreadable": 3}
    assert un.text_of(_home(), "https://b.org/2") == old.strip(), "a dead page read from its snapshot"
    assert un.text_of(_home(), "https://a.org/1") == live.strip()
    nk = {x["raw"]: x for x in at.read(root, un.NOT_KEPT)}
    assert (nk["https://c.org/3"]["access"], nk["https://c.org/3"]["note"]) == ("bot-refused", "HTTP 403")
    assert nk["https://e.org/5"]["access"] == "bot-refused" and un.text_of(_home(), "https://e.org/5") == shell, "a shell no route improves"
    assert (nk["https://f.org/6"]["access"], nk["https://f.org/6"]["note"]) == ("down", "an empty page")
    assert not un.needs_fetch(_home(), "https://d.org/4") and un.needs_fetch(_home(), "https://g.org/7")
    assert [(x["raw"], x["outcome"]) for x in at.read(root)][:2] == [("https://a.org/1", "unknown"), ("https://b.org/2", "unknown")], "each read is an attempt"
    assert len(at.read(root)) == 5


def test_bundles_close_at_their_budget_and_an_oversize_page_goes_alone_in_parts(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _root(tmp_path)
    monkeypatch.setattr(un, "BUNDLE_CHARS", 100)
    monkeypatch.setattr(un, "BUNDLE_TOKENS", 20)
    monkeypatch.setattr(un, "PART_TOKENS", 20)
    src.put(_home(), "https://a.org/1", "Title A\n" + "a" * 40)
    src.put(_home(), "https://a.org/2", "Title B\n" + "b" * 40)
    src.put(_home(), "https://b.org/1", "鳥居" * 20 + "\n" + "門" * 30 + "\n")
    src.put(_home(), "https://c.org/1", "   ")
    dirs = un.bundle(root, ["https://a.org/1", "https://a.org/2", "https://b.org/1", "https://c.org/1", "https://z.org/none"], tmp_path / "b")
    assert [d.name for d in dirs] == ["312-filter-0001", "312-filter-0002", "312-filter-0003"]
    assert json.loads((dirs[0] / "ids.json").read_text()) == {"p00001": "https://a.org/1"}, "two pages would pass the token budget"
    assert json.loads((dirs[1] / "ids.json").read_text()) == {"p00002": "https://b.org/1"}, "an oversize page goes alone at once"
    assert json.loads((dirs[2] / "ids.json").read_text()) == {"p00003": "https://a.org/2"}
    parts = sorted(p.name for p in dirs[1].glob("p00002.part*.txt"))
    assert len(parts) >= 3, "70 CJK characters in parts of 20 tokens"
    assert "".join((dirs[1] / p).read_text() for p in sorted(parts, key=lambda n: int(n.split("part")[1][:-4]))) == "鳥居" * 20 + "\n" + "門" * 30 + "\n"
    manifest = (dirs[1] / "MANIFEST.md").read_text()
    assert "- files: p00002.part1.txt, " in manifest and "- url: https://b.org/1" in manifest
    assert "- title: Title A" in (dirs[0] / "MANIFEST.md").read_text()
    contract = (dirs[0] / "CONTRACT.md").read_text()
    assert contract.startswith("## When to dispatch this agent") and "omitClaudeMd" not in contract, "the contract, less its frontmatter"


def test_tokens_and_titles() -> None:
    assert un.tokens("abcdefgh") == 2 and un.tokens("鳥居ab") == 2
    assert un.title_of("\n\n  A title  \nmore") == "A title" and un.title_of("") == "(no text)"
    assert un.split("") == []


def _bundle(tmp_path: pathlib.Path, verdicts: list[dict]) -> pathlib.Path:
    d = tmp_path / "b1"
    un.write_bundle(d, [("p00001", "https://a.org/1", "A"), ("p00002", "https://e.org/held", "B"), ("p00003", "https://c.org/3", "C")])
    (d / "verdicts.jsonl").write_text("".join(json.dumps(v) + "\n" for v in verdicts) + "\n", encoding="utf-8")
    return d


def test_verdicts_are_refused_until_whole_and_well_formed(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    d = _bundle(tmp_path, [{"id": "p00001", "verdict": "KEEP"}, {"id": "p00002", "verdict": "NOT-KEPT", "reasons": ["boring"]},
                           {"id": "p00009", "verdict": "KEEP"}, {"id": "p00003", "verdict": "MAYBE"}])
    (d / "verdicts.jsonl").write_text((d / "verdicts.jsonl").read_text() + "not json\n", encoding="utf-8")
    with pytest.raises(ValueError) as err:
        un.apply(root, d)
    msg = str(err.value)
    assert all(s in msg for s in ("p00002: NOT-KEPT needs reasons", "'p00009' is not an id", "p00003: verdict 'MAYBE'", "not JSON", "p00002: no verdict"))
    with pytest.raises(ValueError, match="no verdict"):
        un.score(tmp_path / "missing" if False else d, {"p00001": "KEEP"})


def test_verdicts_are_applied_and_a_prehold_capture_loses_its_row(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture) -> None:
    root = _root(tmp_path)
    ar.write_row(root, "https://e.org/held", {"url": "https://e.org/held", "keys": [], "notes": []})
    d = _bundle(tmp_path, [{"id": "p00001", "verdict": "KEEP"}, {"id": "p00002", "verdict": "NOT-KEPT", "reasons": ["modern-only"], "note": "mechanized"},
                           {"id": "p00003", "verdict": "NOT-KEPT", "reasons": ["unreliable-kind"], "propose_block": "ai-wiki.example"}])
    assert un.apply(root, d) == {"kept": 1, "not-kept": 2, "proposed": 1}
    assert "proposes blocking ai-wiki.example" in capsys.readouterr().out
    assert [x["raw"] for x in at.read(root, un.KEPT)] == ["https://a.org/1"]
    assert {x["raw"]: x["reasons"] for x in at.read(root, un.NOT_KEPT)} == {"https://e.org/held": ["modern-only"], "https://c.org/3": ["unreliable-kind"]}
    assert not ar.row_path(root, "https://e.org/held").exists()
    assert un.judged(root) == {"a.org/1", "e.org/held", "c.org/3"}
    assert un.report(root).startswith("uncited: 0 page(s) not yet judged (0 with saved text); 1 kept, 2 not kept (modern-only 1, unreliable-kind 1)")


def test_a_calibration_run_is_scored_per_leg(tmp_path: pathlib.Path) -> None:
    d = _bundle(tmp_path, [{"id": "p00001", "verdict": "KEEP"}, {"id": "p00002", "verdict": "KEEP"}, {"id": "p00003", "verdict": "NOT-KEPT", "reasons": ["off-topic"]}])
    assert un.score(d, {"p00001": "KEEP", "p00002": "NOT-KEPT", "p00003": "NOT-KEPT"}) == {"KEEP": {"agreed": 1, "total": 1}, "NOT-KEPT": {"agreed": 1, "total": 2}}


# ---- the write-ups (FR-012) ----

VOCAB = {"period": [{"id": "premodern", "name": "Premodern", "description": "old"}], "region": [{"id": "japan", "name": "Japan", "description": "j"}],
         "kind": [{"id": "reference", "name": "Reference", "description": "r"}], "canon": {"id": "canon", "name": "Canon", "description": "c"}}


def _vocab(root: pathlib.Path) -> None:
    (root / un.at.RESEARCH / "source-tags.json").write_text(json.dumps(VOCAB), encoding="utf-8")


def test_draft_bundles_hold_the_kept_pages_with_no_entry_and_the_contract(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    _vocab(root)
    for n in (1, 2, 3):
        src.put(_home(), f"https://k.org/{n}", f"Page {n} text.")
    un.kept(root, ["https://k.org/1", "https://k.org/2", "https://k.org/3"], "source-filter")
    (root / un.at.UNCITED).mkdir(parents=True)
    (root / un.at.UNCITED / "0010-k-two.html").write_text("<p>K (https://k.org/2)</p>", encoding="utf-8")
    (dr,) = un.draft_bundles(root, tmp_path / "drafts")
    assert json.loads((dr / "ids.json").read_text()) == {"p00001": "https://k.org/1", "p00002": "https://k.org/3"}, "a page written up is not drafted again"
    contract = (dr / "CONTRACT.md").read_text()
    assert contract.startswith("# Writing up kept uncited sources") and "`period=premodern` - **Premodern**" in contract
    assert (dr / "MANIFEST.md").read_text().startswith("# write-up draft bundle") and "entries.jsonl" in (dr / "MANIFEST.md").read_text()
    assert "Keys already taken" in (dr / "MANIFEST.md").read_text() and "k-two" in (dr / "MANIFEST.md").read_text()


def test_install_writes_each_good_entry_and_refuses_the_rest(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture) -> None:
    root = _root(tmp_path)
    _vocab(root)
    (root / un.SOURCES / "010-works-cited" / "0010-taken.html").write_text("<p>x</p>", encoding="utf-8")
    d = tmp_path / "d1"
    un.write_bundle(d, [("p00001", "https://k.org/1", "A"), ("p00002", "https://k.org/2", "B"), ("p00003", "https://k.org/3", "C")])
    good = {"citation": "Kotobank, 'x' (in Japanese; https://k.org/1)", "what": "What it is: A dictionary entry.", "why": "Why it applies, and its limits: It defines a term.", "tags": "period=premodern; region=japan; kind=reference"}
    lines = [
        {"id": "p00001", "key": "taken", **good},
        {"id": "p00002", "key": "Bad Key", **good},
        {"id": "p00003", "key": "k-three", **{**good, "tags": "period=nonsense; region=japan; kind=reference"}},
    ]
    (d / "entries.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines) + "not json\n", encoding="utf-8")
    un.kept(root, ["https://k.org/1", "https://k.org/2", "https://k.org/3"], "source-filter")
    made = []

    def reserve(kind: str, key: str, root_: pathlib.Path, url: str = "") -> pathlib.Path:
        if key == "taken-2":
            raise RuntimeError("'taken-2' is already being defined in another clone")
        p = root_ / un.at.UNCITED / f"{(len(made) + 2) * 10:04d}-{key}.html"
        p.parent.mkdir(parents=True, exist_ok=True)
        made.append((kind, key, url))
        return p

    assert un.install(root, d, reserve) == {"written": 1, "refused": 3, "already": 0, "dropped": 0}
    assert made == [("uncited", "taken-3", "https://k.org/1")], "a taken key gets -2, and -3 when another clone holds -2"
    text = (root / un.at.UNCITED / "0020-taken-3.html").read_text()
    assert text.startswith('<h3 id="taken-3"><code>taken-3</code></h3>') and "<p><em>What it is:</em> A dictionary entry.</p>" in text, "a label the drafter wrote is not doubled"
    assert "<p><em>Why it applies, and its limits:</em> It defines a term.</p>" in text
    assert text.rstrip().endswith("<!-- tags: period=premodern; region=japan; kind=reference -->")
    err = capsys.readouterr().err
    assert "refused p00002" in err and "period" in err
    assert un.install(root, d, reserve)["already"] == 1, "installed twice, written once"
    (d / "entries.jsonl").unlink()
    assert un.install(root, d, reserve) == {"written": 0, "refused": 0, "already": 0, "dropped": 0}, "a bundle the agent wrote nothing for installs nothing"
    (d / "entries.jsonl").write_text(json.dumps({"id": "p00002", "key": "k-two", **{**good, "citation": "K (https://k.org/2)"}}) + "\n", encoding="utf-8")
    (root / un.KEPT).write_text("".join(s for s in (root / un.KEPT).read_text().splitlines(keepends=True) if "k.org/2" not in s))
    assert un.install(root, d, reserve)["dropped"] == 1, "a page retired since its bundle was drafted is not written"


# ---- the imported copies (R5) ----


def test_an_imported_copy_is_checked_against_the_live_page(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    village = "Mura is a village. " * 40
    src.put(_home(), "https://w.org/mura", "Gravel road is a road. " * 40, origin="import:/tmp/x")
    src.put(_home(), "https://w.org/same", village, origin="import:/tmp/x")
    src.put(_home(), "https://w.org/dead", village, origin="import:/tmp/x")
    src.put(_home(), "https://w.org/fetched", village)
    pages = {"https://w.org/mura": _page("https://w.org/mura", body=village), "https://w.org/same": _page("https://w.org/same", body=village + " Edited.")}
    got = un.verify(root, ["https://w.org/mura", "https://w.org/same", "https://w.org/dead", "https://w.org/fetched"], Stand(pages))
    assert got == {"same": 1, "misfiled": 1, "unread": 1}, "a fetched copy is never checked"
    assert {x["raw"]: x["result"] for x in at.read(root, un.MISFILED)} == {"https://w.org/mura": "misfiled", "https://w.org/same": "same", "https://w.org/dead": "unread"}
    assert un.text_of(_home(), "https://w.org/mura") == village.strip() and un.imported(_home(), "https://w.org/mura") is None, "the live text replaces the copy"
    assert (src.entry_dir(_home(), "https://w.org/mura") / "imported.txt").read_text(encoding="utf-8").startswith("Gravel road"), "a misfiled copy is kept to be read"
    assert not (src.entry_dir(_home(), "https://w.org/same") / "imported.txt").exists()
    assert un.imported(_home(), "https://w.org/dead") is not None, "an unread page keeps its copy"
    assert un.imported_urls(_home()) == ["https://w.org/dead"]
    assert not un.same_page("", "x")


def test_cite_moves_an_uncited_entry_to_the_works_cited_with_a_used_for_line(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    (root / un.at.UNCITED).mkdir(parents=True)
    (root / un.at.UNCITED / "20520-k-one.html").write_text("<h3 id=\"k-one\">x</h3>\n<p>K (https://k.org/1)</p>\n<!-- tags: period=premodern; region=japan; kind=reference -->\n", encoding="utf-8")
    dest = un.cite(root, "k-one")
    assert dest == root / un.SOURCES / "010-works-cited" / "20520-k-one.html" and not (root / un.at.UNCITED / "20520-k-one.html").exists()
    text = dest.read_text()
    assert text.index("<em>Used for:</em> TODO") < text.index("<!-- tags:"), "the Used for: line before the marker, which stays last"
    with pytest.raises(ValueError, match="no uncited entry"):
        un.cite(root, "k-two")


def test_merge_retires_a_duplicate_entry_and_moves_its_page_to_not_kept(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    (root / un.at.UNCITED).mkdir(parents=True)
    (root / un.at.UNCITED / "20520-k-one.html").write_text("<p>K (https://k.org/redirect)</p>\n", encoding="utf-8")
    (root / un.at.UNCITED / "20530-k-two.html").write_text("<p>K (https://k.org/target)</p>\n", encoding="utf-8")
    un.kept(root, ["https://k.org/redirect", "https://k.org/target"], "source-filter")
    gone = un.merge(root, "k-one", "k-two")
    assert gone.name == "20520-k-one.html" and not gone.exists() and (root / un.at.UNCITED / "20530-k-two.html").exists()
    assert [x["raw"] for x in un.at.read(root, un.KEPT)] == ["https://k.org/target"]
    (nk,) = un.at.read(root, un.NOT_KEPT)
    assert nk["raw"] == "https://k.org/redirect" and nk["reasons"] == ["duplicate"] and "k-two" in nk["note"]
    with pytest.raises(ValueError, match="no uncited entry"):
        un.merge(root, "k-one", "k-two")
    (root / un.at.UNCITED / "20540-k-three.html").write_text("<p>no kept URL here</p>\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no kept page"):
        un.merge(root, "k-three", "k-two")


def test_work_folds_chinese_wikipedia_script_variants_and_nothing_else() -> None:
    assert un.work("zh.wikipedia.org/zh-hans/平遥城墙") == un.work("zh.wikipedia.org/wiki/平遥城墙") == "zh.wikipedia.org/wiki/平遥城墙"
    assert un.work("zh.wikipedia.org/zh-tw/X") == "zh.wikipedia.org/wiki/X"
    assert un.work("ja.wikipedia.org/wiki/X") == "ja.wikipedia.org/wiki/X" and un.work("a.org/zh-hans/X") == "a.org/zh-hans/X"


def test_fingerprint_is_the_body_past_its_head_and_none_for_a_short_page() -> None:
    body = "x" * 2000
    assert un.fingerprint("Title one " * 20 + body) == un.fingerprint("Title two " * 20 + body) != ""
    assert un.fingerprint("short") == "" and un.fingerprint(None) == ""
    assert un.fingerprint("t" * 200 + body) != un.fingerprint("t" * 200 + body + "y")


def test_dedupe_retires_variants_redirects_and_cited_works_and_keeps_the_first(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    (root / un.at.UNCITED).mkdir(parents=True)
    (root / un.SOURCES / "010-works-cited" / "20100-cited-k.html").write_text("<p>C (https://c.org/cited)</p>\n", encoding="utf-8")
    (root / un.at.UNCITED / "20520-k-hans.html").write_text("<p>K (https://zh.wikipedia.org/zh-hans/X)</p>\n", encoding="utf-8")
    (root / un.at.UNCITED / "20530-k-wiki.html").write_text("<p>K (https://zh.wikipedia.org/wiki/X)</p>\n", encoding="utf-8")
    same = "head " * 50 + "the one article's body " * 100
    src.put(_home(), "https://r.org/redirect-a", "Title A " + same)
    src.put(_home(), "https://r.org/redirect-b", "Title B " + same)
    urls = ["https://zh.wikipedia.org/wiki/X", "https://zh.wikipedia.org/zh-hans/X", "https://r.org/redirect-a", "https://r.org/redirect-b", "https://www.c.org/cited"]
    un.kept(root, urls, "source-filter")
    assert un.dedupe(root, dry=True) and len(un.at.read(root, un.KEPT)) == 5, "a dry run changes nothing"
    done = un.dedupe(root)
    assert done == ["k-hans -> k-wiki", "https://r.org/redirect-b -> https://r.org/redirect-a", "https://www.c.org/cited -> cited-k"]
    assert [x["raw"] for x in un.at.read(root, un.KEPT)] == ["https://zh.wikipedia.org/wiki/X", "https://r.org/redirect-a"]
    assert not (root / un.at.UNCITED / "20520-k-hans.html").exists() and (root / un.at.UNCITED / "20530-k-wiki.html").exists()
    assert {x["raw"] for x in un.at.read(root, un.NOT_KEPT) if x["reasons"] == ["duplicate"]} == set(urls) - {"https://zh.wikipedia.org/wiki/X", "https://r.org/redirect-a"}
    assert un.dedupe(root) == []
    with pytest.raises(ValueError, match="no entry for 'nowhere'"):
        un.merge(root, "k-wiki", "nowhere")


class _Dying(Stand):
    """A browser whose event loop closed under one page (Playwright, 2026-10-02): every call raises until replaced."""

    def __init__(self, pages: dict, bad: str) -> None:
        super().__init__(pages)
        self.bad, self.closed = bad, False

    def get(self, url: str):  # noqa: ANN201
        if url == self.bad:
            raise RuntimeError("Event loop is closed! Is Playwright already stopped?")
        return super().get(url)

    def close(self) -> None:
        self.closed = True
        raise RuntimeError("cannot close a dead browser")


def test_a_browser_that_dies_under_one_page_ends_that_read_not_the_lane(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    root = _root(tmp_path)
    pages = {"https://a.org/1": _page("https://a.org/1", body="Live text. " * 70)}
    fresh = Stand(pages)
    monkeypatch.setattr(ar, "Browser", lambda: fresh)
    dying = _Dying(pages, "https://z.org/9")
    got = un.fetch(root, ["https://z.org/9", "https://a.org/1"], dying)
    assert got == {"read": 1, "unreadable": 0, "error": 1} and dying.closed
    assert un.needs_fetch(_home(), "https://z.org/9"), "the page that broke the browser is left for the next run, not ruled unreadable"
    assert "Event loop is closed" in capsys.readouterr().out


def test_a_part_never_passes_the_read_tools_character_limit() -> None:
    english = ("A plain English line of a long travel book, about the villages on the river. " * 3 + "\n") * 3000
    parts = un.split(english)
    assert len(parts) > 1 and all(len(p) <= un.PART_CHARS for p in parts) and "".join(parts) == english
    one_line = "x" * (un.PART_CHARS * 2 + 7)
    assert [len(p) for p in un.split(one_line)] == [un.PART_CHARS, un.PART_CHARS, 7]


def test_boilerplate_is_what_four_pages_of_a_host_share_and_similar_reads_past_it() -> None:
    nav = un.body_grams("Main menu navigation box of the site " * 20)
    pages = [un.body_grams(f"Main menu navigation box of the site {'x' * i} article number {i} " * 20) for i in range(4)]
    common = un.boilerplate(pages)
    assert nav & common and not un.boilerplate(pages[:3]), "a gram on four pages is boilerplate, on three it is not"
    a = un.body_grams("The levee is a ridge of earth along a river, raised by floods. " * 30)
    b = un.body_grams("Levee - redirect. The levee is a ridge of earth along a river, raised by floods. " * 30)
    c = un.body_grams("A fan-shaped plain of gravel spread where a mountain stream leaves its valley. " * 30)
    assert un.similar(a, b) and not un.similar(a, c) and not un.similar(a, frozenset())
    assert un.overlap(frozenset(), a) == 0.0


def test_dedupe_finds_one_work_saved_in_two_forms_on_one_host(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    article = " ".join(f"Cremation note {i}: the pyre of year {1600 + i} burned {i * 7 % 13} hours." for i in range(150))
    src.put(_home(), "https://w.org/Cremains", "Jump to content Main menu " + article)
    src.put(_home(), "https://w.org/Cremation", "Cremation - Wiki " + article + " Retrieved from")
    src.put(_home(), "https://w.org/Levee", "A levee is a ridge of earth along a river. " * 60)
    (root / un.SOURCES / "010-works-cited" / "20100-cremation-w.html").write_text("<p>C (https://w.org/Cremation)</p>\n", encoding="utf-8")
    un.kept(root, ["https://w.org/Cremains", "https://w.org/Levee"], "source-filter")
    dups = un.duplicate_works(root)
    assert [(raw, into) for raw, into, _ in dups] == [("https://w.org/Cremains", "cremation-w")] and dups[0][2].startswith("similar")


def test_work_folds_one_file_servers_two_names_and_a_github_raw_url() -> None:
    assert un.work("mdpi-res.com/d_attachment/water/x.pdf") == un.work("res.mdpi.com/d_attachment/water/x.pdf")
    assert un.work("online.bunka.go.jp/heritages/detail/1") == "bunka.nii.ac.jp/heritages/detail/1"
    assert un.work("raw.githubusercontent.com/u/r/master/a/b.txt") == "github.com/u/r/blob/master/a/b.txt"
    assert un.work("github.com/u/r/blob/master/a/b.txt") == "github.com/u/r/blob/master/a/b.txt"


def test_work_folds_a_kotobank_entry_to_its_number_whatever_word_is_in_front() -> None:
    assert un.work("kotobank.jp/word/竈-39622") == un.work("kotobank.jp/word/かまど-39622") == "kotobank.jp/word/39622"
    assert un.work("kotobank.jp/word/竈") == "kotobank.jp/word/竈" and un.work("kotobank.jp/word/a-1/x") == "kotobank.jp/word/a-1/x"


def test_the_report_counts_kept_pages_with_no_entry_and_entries_with_no_kept_page(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    assert un.report(root).endswith("0 written up, 0 kept with no entry, 0 entr(ies) whose URL is no kept page's (a citation a check corrected)")
    (root / un.at.UNCITED).mkdir(parents=True)
    (root / un.at.UNCITED / "20520-a.html").write_text("<p>A (https://a.org/1).</p>\n", encoding="utf-8")
    (root / un.at.UNCITED / "20530-b.html").write_text("<p>B (https://b.org/corrected)</p>\n", encoding="utf-8")
    un.kept(root, ["https://a.org/1", "https://c.org/2"], "source-filter")
    assert un.report(root).endswith("2 written up, 1 kept with no entry, 1 entr(ies) whose URL is no kept page's (a citation a check corrected)")


def test_requeue_clears_a_verdict_and_its_entry_so_the_filter_judges_the_page_again(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    (root / un.at.UNCITED).mkdir(parents=True)
    (root / un.at.UNCITED / "20520-mura.html").write_text("<p>Mura (https://w.org/mura)</p>\n", encoding="utf-8")
    un.kept(root, ["https://w.org/mura", "https://w.org/keep"], "source-filter")
    at.write(root, [un.line("https://w.org/stone", ["duplicate"], "rule", "the same work as machiwari")], un.NOT_KEPT)
    assert un.requeue(root, "https://w.org/mura") == "mura" and not (root / un.at.UNCITED / "20520-mura.html").exists()
    assert [x["raw"] for x in at.read(root, un.KEPT)] == ["https://w.org/keep"]
    assert un.requeue(root, "https://w.org/stone") is None and at.read(root, un.NOT_KEPT) == []
    assert un.judged(root) == {src.norm("https://w.org/keep")}
    with pytest.raises(ValueError, match="no verdict and no entry"):
        un.requeue(root, "https://w.org/stone")
