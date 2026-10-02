"""`scripts/_archive.py` - every cited source archived into the private archive repository (feature 309).

WHAT THESE PROVE. A live fetch that fails is told apart as DEAD or REFUSED, and each takes its own order (plan D2): a dead
page a Wayback snapshot, then the GM's copy, else `unreachable` with the page cache's text kept; a refused one the GM's
copy, then a snapshot, else `partial`. A capture holds the served bytes, the whole page, the text and its record; a big file
is cut into parts that join back; a host's URLs share one lane. The working copy clones once, commits each capture and the
GM's files, and pushes - a push that fails leaves the row `pending-upload` until a later push settles it. The PAT never
reaches git's arguments. The coverage report counts every cited URL. No test fetches anything: the browser is a stand-in
that serves saved fixtures, and the remote is a bare repository on disk.
"""

from __future__ import annotations

import importlib.util
import io
import json
import pathlib
import subprocess
import sys

import pytest

from l7r.diagram.interactive.record import archive as rec
from tests import _flat_record as fr

REPO = pathlib.Path(__file__).resolve().parents[5]
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures" / "archive"


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # a dataclass resolves its module by name
    spec.loader.exec_module(mod)
    return mod


ar = _load("_archive")
HTML = "text/html; charset=utf-8"


class Stand:
    """A browser that serves saved fixtures: `pages` maps a URL to a Fetched (or none - a network error); a rendered
    page's MHTML and text come from `shown`."""

    def __init__(self, pages: dict, shown: dict | None = None) -> None:
        self.pages, self.shown, self.asked = pages, shown or {}, []

    def get(self, url: str):  # noqa: ANN201
        self.asked.append(url)
        got = self.pages.get(url)
        return ar.Fetched(url, error="net::ERR_NAME_NOT_RESOLVED") if got is None else ar.Fetched(**{**got.__dict__})

    def render(self, url: str) -> tuple[str, str]:
        return self.shown.get(url, ("", ""))


def _page(url: str, status: int = 200, body: bytes = b"<p>x</p>", kind: str = HTML, final: str = "") -> ar.Fetched:
    return ar.Fetched(url, status, final or url, kind, body)


def _wayback(url: str, snap: str) -> tuple[str, ar.Fetched]:
    reply = {"archived_snapshots": {"closest": {"available": True, "url": snap, "timestamp": "20230624043456"}}}
    return ar.WAYBACK + ar.urllib.parse.quote(url, safe=""), _page("", body=json.dumps(reply).encode(), kind="application/json")


@pytest.mark.parametrize(
    ("got", "kind"),
    [
        (_page("https://a.org/p"), ""),
        (ar.Fetched("https://a.org/p", error="timeout"), "dead"),
        (_page("https://a.org/p", 404), "dead"),
        (_page("https://a.org/p", 503), "dead"),
        (_page("https://a.org/p", 403), "refused"),
        (_page("https://a.org/p", 200, b""), "dead"),
        (_page("https://a.org/p", 200, final="https://a.org/"), "dead"),
        (ar.Fetched("https://a.org/p", None), "dead"),
    ],
)
def test_a_live_fetch_is_told_apart_as_dead_or_refused(got: ar.Fetched, kind: str) -> None:
    got.text = got.text or ("" if got.status == 200 and got.body == b"" else "shown")
    assert ar.failure("https://a.org/p", got)[0] == kind


def test_a_page_that_renders_no_text_is_refused_and_a_front_page_citation_is_not_a_redirect() -> None:
    assert ar.failure("https://a.org/p", _page("https://a.org/p")) == ("refused", "the page showed no text")
    front = _page("https://a.org/", final="https://a.org/")
    front.text = "home"
    assert ar.failure("https://a.org/", front) == ("", "")


@pytest.mark.parametrize(
    ("kind", "url", "ext"),
    [(HTML, "https://a/x", ".html"), ("application/pdf", "https://a/x", ".pdf"), ("", "https://a/f.PDF", ".pdf"), ("", "https://a/x", ".bin"), ("image/jpeg", "https://a/x", ".jpg")],
)
def test_the_served_file_keeps_its_kind(kind: str, url: str, ext: str) -> None:
    assert ar.ext_of(kind, url) == ext


def test_a_snapshot_is_fetched_raw_and_a_wiki_page_names_its_revision() -> None:
    assert ar.snapshot_raw("https://web.archive.org/web/20230624043456/http://x.org/p") == "https://web.archive.org/web/20230624043456id_/http://x.org/p"
    assert ar.revision((FIXTURES / "wiki.html").read_bytes()) == "104728811" and ar.revision(b"<p>") == ""


def test_a_pdf_keeps_its_text_and_a_web_page_its_whole_page() -> None:
    pdf = (FIXTURES / "yard.pdf").read_bytes()
    wiki = (FIXTURES / "wiki.html").read_bytes()
    stand = Stand({"https://a/y.pdf": _page("https://a/y.pdf", body=pdf, kind="application/pdf"), "https://w/p": _page("https://w/p", body=wiki)}, {"https://w/p": ("MHTML", "散居村は")})
    got = ar.capture(stand, "https://a/y.pdf", False)
    assert got.outcome == "archived" and set(got.files) == {"served.pdf", "text.txt"}
    assert "forty to sixty mats" in got.files["text.txt"].decode()
    page = ar.capture(stand, "https://w/p", False)
    assert set(page.files) == {"served.html", "page.mhtml", "text.txt"} and page.record["revision"] == "104728811"
    assert page.record["sha256"] == ar.hashlib.sha256(wiki).hexdigest() and page.record["whole_page"] is True
    assert ar.pdf_text(b"not a pdf") == ""


def test_a_page_that_will_not_render_keeps_its_served_html_and_text_as_partial() -> None:
    body = b"<html><script>var x=1;</script><style>p{}</style><p>The yard &amp; the mats.</p></html>"
    got = ar.capture(Stand({"https://a/p": _page("https://a/p", body=body)}), "https://a/p", False)
    assert got.outcome == "partial" and got.reason.startswith("the page would not render whole")
    assert set(got.files) == {"served.html", "text.txt"} and got.files["text.txt"] == b"The yard & the mats."
    shown_empty = ar.capture(Stand({"https://a/p": _page("https://a/p", body=body)}, {"https://a/p": ("MHTML", "")}), "https://a/p", False)
    assert shown_empty.outcome == "partial" and shown_empty.reason == "the page showed no text", "a page that renders no text is refused"


def test_a_text_file_is_its_own_text() -> None:
    got = ar.capture(Stand({"https://a/t.txt": _page("https://a/t.txt", body="稲".encode(), kind="text/plain")}), "https://a/t.txt", False)
    assert got.outcome == "archived" and got.files["text.txt"].decode() == "稲"


def test_a_dead_page_takes_a_snapshot_then_the_gm_copy_then_is_unreachable_with_the_cached_text() -> None:
    url, snap = "https://gone.org/p", "https://web.archive.org/web/20230624043456/https://gone.org/p"
    ask, reply = _wayback(url, snap)
    raw = ar.snapshot_raw(snap)
    stand = Stand({url: _page(url, 404), ask: reply, raw: _page(raw, body=b"<p>old</p>")}, {snap: ("MHTML", "old text")})
    got = ar.capture(stand, url, True)
    assert got.outcome == "archived-earlier-snapshot" and got.record["origin"] == "wayback 20230624043456" and got.record["live_failure"] == "HTTP 404"
    assert got.files["page.mhtml"] == b"MHTML" and got.files["text.txt"] == b"old text"
    no_snap = Stand({url: _page(url, 404)})
    assert ar.capture(no_snap, url, True).outcome == "archived-gm-copy"
    lost = ar.capture(no_snap, url, False, cache_text="the cached words")
    assert lost.outcome == "unreachable" and lost.files == {"page-cache-text.txt": b"the cached words"} and lost.reason == "HTTP 404"
    assert ar.capture(Stand({}), url, False).files == {}


def test_a_refused_page_takes_the_gm_copy_first_then_a_snapshot_else_is_partial() -> None:
    url, snap = "https://wall.org/p", "https://web.archive.org/web/20230624043456/https://wall.org/p"
    ask, reply = _wayback(url, snap)
    raw = ar.snapshot_raw(snap)
    pages = {url: _page(url, 403, b"<p>are you human</p>"), ask: reply, raw: _page(raw, body=b"<p>old</p>")}
    gm = ar.capture(Stand(pages), url, True)
    assert gm.outcome == "archived-gm-copy" and "served.html" in gm.files, "what the site served is kept beside the GM's copy"
    snapped = ar.capture(Stand(pages, {snap: ("M", "old")}), url, False)
    assert snapped.outcome == "archived-earlier-snapshot"
    partial = ar.capture(Stand({url: _page(url, 403, b"<p>are you human</p>")}), url, False, cache_text="cached")
    assert partial.outcome == "partial" and set(partial.files) == {"served.html", "page-cache-text.txt"}


@pytest.mark.parametrize("reply", [b"not json", json.dumps({"archived_snapshots": {}}).encode()])
def test_no_snapshot_where_the_wayback_machine_holds_none(reply: bytes) -> None:
    url = "https://gone.org/p"
    ask = ar.WAYBACK + ar.urllib.parse.quote(url, safe="")
    assert ar.wayback(Stand({ask: _page(ask, body=reply, kind="application/json")}), url) is None
    assert ar.wayback(Stand({}), url) is None


def test_a_snapshot_that_will_not_fetch_is_no_copy() -> None:
    url, snap = "https://gone.org/p", "https://web.archive.org/web/20230624043456/https://gone.org/p"
    ask, reply = _wayback(url, snap)
    assert ar.capture(Stand({url: _page(url, 404), ask: reply}), url, False).outcome == "unreachable"


def test_a_big_file_is_cut_into_parts_that_join_back() -> None:
    body = bytes(range(256)) * 5
    files, parts = ar.split_large({"served.pdf": body, "text.txt": b"t"}, part=500)
    assert sorted(files) == ["served.pdf.part1", "served.pdf.part2", "served.pdf.part3", "text.txt"]
    assert b"".join(files[f"served.pdf.part{n}"] for n in (1, 2, 3)) == body
    assert parts == {"served.pdf": {"parts": 3, "sha256": ar.hashlib.sha256(body).hexdigest(), "bytes": len(body)}}


def test_a_hosts_urls_share_one_lane() -> None:
    urls = ["https://a/1", "https://a/2", "https://a/3", "https://b/1", "https://c/1", "https://c/2"]
    lanes = ar.lanes(urls, 2)
    assert sorted(u for lane in lanes for u in lane) == sorted(urls)
    for host in ("a", "b", "c"):
        assert sum(1 for lane in lanes if any(f"//{host}/" in u for u in lane)) == 1
    assert ar.lanes(["https://a/1"], 4) == [["https://a/1"]]


def test_the_token_reaches_git_by_its_environment_only() -> None:
    env = ar.git_env("ghp_secret")
    assert env["GIT_CONFIG_KEY_0"] == "http.https://github.com/.extraheader"
    assert "ghp_secret" not in env["GIT_CONFIG_VALUE_0"] and env["GIT_TERMINAL_PROMPT"] == "0"
    assert ar.base64.b64decode(env["GIT_CONFIG_VALUE_0"].split()[-1]).decode() == "x-access-token:ghp_secret"


def _remote(tmp: pathlib.Path) -> str:
    bare = tmp / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True)
    return str(bare)


def _root(tmp: pathlib.Path) -> pathlib.Path:
    root = tmp / "clone"
    (root / ar.MANIFEST).parent.mkdir(parents=True)
    fr.write(root / ar.MANIFEST.parent)
    (root / ar.MANIFEST).mkdir(parents=True)
    copies = {"files": {"alpha.pdf": {"keys": ["alpha"]}, "pages_files": {"keys": ["alpha"]}, "stray.txt": {"keys": []}}}
    (root / ar.MANIFEST / rec.GM_COPIES).write_text(json.dumps(copies), encoding="utf-8")
    return root


def test_one_url_is_archived_with_its_gm_copy_pushed_and_its_row_written(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    gm = tmp_path / "academic-sources"
    (gm / "pages_files").mkdir(parents=True)
    (gm / "alpha.pdf").write_bytes(b"%PDF-1.4 the GM's copy")
    (gm / "pages_files" / "img.png").write_bytes(b"png")
    monkeypatch.setattr(ar, "GM_DIR", gm)
    root, remote = _root(tmp_path), _remote(tmp_path)
    store = ar.Archive(tmp_path / "home", remote=remote)
    stand = Stand({"https://a": _page("https://a")}, {"https://a": ("MHTML", "A's text")})
    who = rec.cited(str(root / ".claude/skills/diagram/research"))["https://a"]
    row = ar.archive_url(root, "https://a", who, stand, store)
    assert row["outcome"] == "archived" and row["path"].startswith(f"alpha/{rec.url_id('https://a')}/") and row["first"] == row["path"]
    assert row["gm_copies"] == ["alpha/gm-copy/alpha.pdf", "alpha/gm-copy/pages_files"]
    assert ar.read_row(root, "https://a") == row and store.unpushed() == 0
    listed = subprocess.run(["git", "-C", remote, "ls-tree", "-r", "--name-only", "main"], capture_output=True, text=True, check=True).stdout.split()
    assert f"{row['path']}/page.mhtml" in listed and f"{row['path']}/capture.json" in listed
    assert "alpha/gm-copy/alpha.pdf" in listed and "alpha/gm-copy/pages_files/img.png" in listed
    again = ar.archive_url(root, "https://a", who, stand, store)
    assert again["first"] == row["path"] and again["gm_copies"] == row["gm_copies"], "a later capture never replaces the first"
    assert again["path"] != row["path"] and (store.dir / row["path"] / "page.mhtml").is_file()
    assert not store.copy_in("alpha/gm-copy/alpha.pdf", gm / "alpha.pdf"), "a GM file is copied once"


def test_a_failed_push_leaves_the_row_pending_until_a_push_settles_it(tmp_path: pathlib.Path) -> None:
    root, remote = _root(tmp_path), _remote(tmp_path)
    store = ar.Archive(tmp_path / "home", remote=remote)
    with store.locked():
        store.ensure()
    store.git("remote", "set-url", "origin", str(tmp_path / "nowhere.git"))
    who = rec.Cited(notes=["0001-lanes.notes.html"])
    row = ar.archive_url(root, "https://direct.org/p", who, Stand({"https://direct.org/p": _page("https://direct.org/p")}, {"https://direct.org/p": ("M", "t")}), store)
    assert row["outcome"] == "pending-upload" and row["held"] == "archived" and row["reason"].startswith("push failed:")
    assert row["path"].startswith("notes/") and store.unpushed() > 0
    store.git("remote", "set-url", "origin", remote)
    with store.locked():
        assert store.push() == ""
    assert ar.settle(root) == 1 and ar.read_row(root, "https://direct.org/p")["outcome"] == "archived"
    assert ar.settle(root) == 0


def test_an_unreachable_url_with_nothing_to_store_keeps_its_reason_and_writes_no_capture(tmp_path: pathlib.Path) -> None:
    root, remote = _root(tmp_path), _remote(tmp_path)
    store = ar.Archive(tmp_path / "home", remote=remote)
    row = ar.archive_url(root, "https://b", rec.Cited(keys=["beta"]), Stand({}), store)
    assert row["outcome"] == "unreachable" and row["path"] == "" and row["reason"] == "net::ERR_NAME_NOT_RESOLVED"


def test_an_unreadable_row_or_match_table_is_none(tmp_path: pathlib.Path) -> None:
    assert ar.read_row(tmp_path, "https://a") is None and ar.gm_copies(tmp_path) == {}


def test_a_clone_that_fails_is_reported(tmp_path: pathlib.Path) -> None:
    with pytest.raises(RuntimeError, match="could not clone the archive"):
        ar.Archive(tmp_path / "home", remote=str(tmp_path / "missing.git")).ensure()


def test_the_lock_times_out_rather_than_hangs(tmp_path: pathlib.Path) -> None:
    store = ar.Archive(tmp_path)
    with store.locked(), pytest.raises(TimeoutError), ar.Archive(tmp_path).locked(timeout=0.1):
        pass


def test_the_report_counts_every_cited_url(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    ar.write_row(root, "https://a", {"url": "https://a", "outcome": "archived"})
    ar.write_row(root, "https://b", {"url": "https://b", "outcome": "unreachable", "reason": "HTTP 404"})
    out = io.StringIO()
    assert ar.report(root, out) == 0
    text = out.getvalue()
    assert "archive coverage: 2 cited URL(s)" in text and "  unreachable https://b - HTTP 404" in text
    (root / ar.MANIFEST / f"{rec.url_id('https://b')}.json").unlink()
    out = io.StringIO()
    assert ar.report(root, out) == 1 and "no row: https://b" in out.getvalue()
    assert set(ar.owed(root)) == {"https://b"}


def test_the_mirror_is_a_clones_grandparent(tmp_path: pathlib.Path) -> None:
    assert ar.mirror(tmp_path / ".clones" / "x") == tmp_path and ar.mirror(tmp_path) == tmp_path
