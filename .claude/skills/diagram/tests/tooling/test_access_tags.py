"""`scripts/_access_tags.py` - what can be got of each source (feature 313, spec FR-011, SC-005).

WHAT THESE PROVE. One key per derivation rule: the GM's mark, each manifest outcome, a READ comment with no row, nothing at
all, and a state recorded by hand. The mark mapping for each allowed combination; several entries naming one key (the
newest state-giving mark, a not-found never overriding); a seeded paywalled key; and a seeded paywalled key whose entry the
GM then marks downloaded showing gm-full. Plus the report over the repository itself: every registry key has a state.
"""

from __future__ import annotations

import importlib.util
import json
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


dl = _load("_downloads")
at = _load("_access_tags")
STATES = json.loads((REPO / at.ACCESS).read_text(encoding="utf-8"))["states"]


def _entry(root: pathlib.Path, key: str, read: str = "") -> None:
    d = root / at.REGISTRY
    d.mkdir(parents=True, exist_ok=True)
    comment = f"<!-- READ {read}, feature 1 -->" if read else ""
    (d / f"0010-{key}.html").write_text(f'<h3 id="{key}"><code>{key}</code></h3>\n<p>A work (https://example.org/{key}){comment}</p>\n', encoding="utf-8")


def _row(root: pathlib.Path, rid: str, key: str, outcome: str, reason: str = "", captured: str = "2026-10-02T12:00:00+00:00") -> None:
    d = root / at.MANIFEST / rid[:2]
    d.mkdir(parents=True, exist_ok=True)
    row = {"url": f"https://example.org/{key}", "keys": [key], "outcome": outcome, "reason": reason, "captured": captured}
    (d / f"{rid}.json").write_text(json.dumps(row), encoding="utf-8")


def _list(root: pathlib.Path, *entries: tuple[str, str, dl.Marks | None, str | None]) -> None:
    """Entries as (id, the key named in its heading or "", marks, the date recorded)."""
    lines = ["# List", ""]
    for eid, key, marks, date in entries:
        lines += [f"### {eid}. A work" + (f" (`{key}`)" if key else ""), "", *(marks or dl.Marks()).lines()]
        lines += [f"- Marks recorded {date}"] if date else []
        lines += ["", "- **[Page](https://example.org/x)**", ""]
    (root / dl.CANON).write_text("\n".join(lines), encoding="utf-8")


def _root(tmp: pathlib.Path, recorded: dict | None = None) -> pathlib.Path:
    (tmp / at.RECORD).mkdir(parents=True, exist_ok=True)
    (tmp / at.ACCESS).write_text(json.dumps({"states": STATES, "recorded": recorded or {}}), encoding="utf-8")
    return tmp


def _tag(root: pathlib.Path, key: str) -> at.Tag:
    return at.tag(at.load(root), key)


def test_the_states_file_declares_the_eight_states_in_order() -> None:
    assert [s["id"] for s in STATES] == ["open", "gm-full", "gm-partial", "paywalled", "bot-refused", "down", "gone", "never-read"]


@pytest.mark.parametrize(
    ("outcome", "reason", "read", "state"),
    [
        ("archived", "", "", "open"),
        ("archived-earlier-snapshot", "HTTP 404", "", "open"),
        ("archived-gm-copy", "HTTP 403", "", "gm-full"),
        ("partial", "the page would not render whole: its served HTML and text are kept", "", "open"),
        ("partial", "HTTP 403", "2026-09-01", "bot-refused"),
        ("partial", "HTTP 403", "", "bot-refused"),
        ("partial", "HTTP 429", "", "bot-refused"),
        ("unreachable", "APIRequestContext.get: Timeout 60000ms exceeded.", "", "down"),
        ("unreachable", "HTTP 520", "", "down"),
        ("unreachable", "Client network socket disconnected", "", "down"),
        ("unreachable", "HTTP 404", "", "gone"),
    ],
)
def test_each_manifest_outcome_gives_its_state(tmp_path: pathlib.Path, outcome: str, reason: str, read: str, state: str) -> None:
    root = _root(tmp_path)
    _entry(root, "k", read)
    _row(root, "aa01", "k", outcome, reason)
    t = _tag(root, "k")
    assert (t.state, t.date) == (state, "2026-10-02")


def test_the_most_open_row_wins(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    _entry(root, "k")
    _row(root, "aa01", "k", "partial", "HTTP 403")
    _row(root, "bb02", "k", "archived", captured="2026-09-01T00:00:00+00:00")
    assert _tag(root, "k") == at.Tag("open", "2026-09-01", "the archive manifest: archived, https://example.org/k")


def test_with_no_row_a_read_comment_is_open_and_nothing_is_never_read(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    _entry(root, "read", "2026-08-28")
    _entry(root, "unread")
    assert _tag(root, "read") == at.Tag("open", "2026-08-28", "a READ comment in its registry entry; no archive row")
    assert _tag(root, "unread").state == "never-read" and _tag(root, "unread").date is None


@pytest.mark.parametrize(
    ("marks", "state"),
    [
        (dl.Marks(downloaded=True), "gm-full"),
        (dl.Marks(downloaded=True, partial=True), "gm-full"),
        (dl.Marks(downloaded=True, paywalled=True), "gm-full"),
        (dl.Marks(downloaded=True, elsewhere=True, where="x"), "gm-full"),
        (dl.Marks(partial=True), "gm-partial"),
        (dl.Marks(partial=True, paywalled=True), "gm-partial"),
        (dl.Marks(partial=True, elsewhere=True, where="x"), "gm-partial"),
        (dl.Marks(paywalled=True), "paywalled"),
        (dl.Marks(not_found=True), "bot-refused"),
    ],
)
def test_each_allowed_mark_combination_gives_its_state(tmp_path: pathlib.Path, marks: dl.Marks, state: str) -> None:
    root = _root(tmp_path)
    _entry(root, "k", "2026-09-01")
    _row(root, "aa01", "k", "partial", "HTTP 403")
    _list(root, ("1", "k", marks, "2026-10-04"))
    t = _tag(root, "k")
    assert t.state == state
    if marks.not_found:
        assert "the GM did not find it (entry 1)" in t.basis and t.date == "2026-10-02"
    else:
        assert t.date == "2026-10-04"


def test_an_unrecorded_mark_decides_nothing(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    _entry(root, "k", "2026-09-01")
    _list(root, ("1", "k", dl.Marks(downloaded=True), None))
    assert _tag(root, "k").state == "open"


def test_several_entries_the_newest_state_giving_mark_decides_and_not_found_never_overrides(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    _entry(root, "k", "2026-09-01")
    _list(
        root,
        ("H7", "k", dl.Marks(partial=True), "2026-10-04"),
        ("9", "k", dl.Marks(not_found=True), "2026-10-06"),
        ("10", "k", dl.Marks(paywalled=True), "2026-10-03"),
    )
    assert _tag(root, "k").state == "gm-partial", "the newest giving a state; the later not-found does not hide it"
    _list(root, ("H7", "k", dl.Marks(paywalled=True), "2026-10-04"), ("9", "k", dl.Marks(downloaded=True), "2026-10-04"))
    assert _tag(root, "k").state == "gm-full", "on the same date, the most open"


def test_a_seeded_paywalled_key_and_the_gms_later_download_over_it(tmp_path: pathlib.Path) -> None:
    seed = {"k": [{"state": "paywalled", "date": "2026-10-02", "reason": "the entry says the full text is paywalled"}]}
    root = _root(tmp_path, seed)
    _entry(root, "k", "2026-09-01")
    _row(root, "aa01", "k", "archived")
    assert _tag(root, "k").state == "paywalled", "a hand state wins over an archive row of the same date"
    _list(root, ("2", "k", dl.Marks(downloaded=True), "2026-10-01"))
    assert _tag(root, "k").state == "gm-full", "and never over a GM mark that gives a state, whatever its date"
    _list(root, ("2", "k", dl.Marks(not_found=True), "2026-10-05"))
    assert _tag(root, "k").state == "paywalled", "a not-found tick alone leaves the hand state in force"


def test_an_older_hand_state_loses_to_a_newer_capture(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path, {"k": [{"state": "paywalled", "date": "2026-09-01", "reason": "two words"}]})
    _entry(root, "k")
    _row(root, "aa01", "k", "archived")
    assert _tag(root, "k").state == "open"


def test_a_keyless_entry_takes_its_mark_then_a_hand_state_then_never_read(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path, {"download:3": [{"state": "paywalled", "date": "2026-10-02", "reason": "Blocked by: paywalled."}]})
    _list(root, ("2", "", dl.Marks(partial=True), "2026-10-04"), ("3", "", None, None), ("4", "", None, None))
    w = at.load(root)
    assert w.keyless == ["download:2", "download:3", "download:4"]
    assert [at.tag(w, f"download:{i}").state for i in (2, 3, 4)] == ["gm-partial", "paywalled", "never-read"]


def test_an_entry_names_its_keys_by_backticks_key_lines_and_links(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    for k in ("alpha", "beta", "gamma"):
        _entry(root, k)
    _row(root, "aa01", "gamma", "archived")
    e = dl.Entry("1", "### 1. Work (`alpha`)", dl.Marks(), None, ["- Key: beta, nonesuch", "- **[x](https://example.org/gamma)**", "`not-a-key`"])
    assert at.entry_keys(e, {"alpha", "beta", "gamma"}, {"https://example.org/gamma": {"gamma"}}) == {"alpha", "beta", "gamma"}


def test_set_records_a_state_and_refuses_bad_input(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    at.set_state(root, "k", "paywalled", "2026-10-02", "the entry says so")
    assert json.loads((root / at.ACCESS).read_text(encoding="utf-8"))["recorded"]["k"][0]["state"] == "paywalled"
    for state, date, reason, said in (("closed", "2026-10-02", "two words", "not a state"), ("open", "Oct 2", "two words", "YYYY-MM-DD"), ("open", "2026-10-02", "x", "two words")):
        with pytest.raises(dl.Refusal, match=said):
            at.set_state(root, "k", state, date, reason)


def test_every_registry_key_in_the_repository_has_a_state() -> None:
    """SC-005 on the record itself."""
    if not (REPO / dl.CANON).is_file():
        pytest.skip("the list is not in this checkout")
    w = at.load(REPO)
    tags = at.every(w)
    assert len(w.keys) > 2000 and all(not k.startswith("download:") or k in w.keyless for k in tags)
    assert {t.state for t in tags.values()} <= set(w.order)
    assert all(t.date for t in tags.values() if t.state not in ("never-read",))


def test_the_command_reports_counts_one_key_and_json(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    root = _root(tmp_path)
    _entry(root, "k", "2026-09-01")
    _list(root, ("1", "", None, None))
    monkeypatch.chdir(root)
    monkeypatch.setattr(at.dl, "git", lambda *_a: type("R", (), {"stdout": str(root)})())
    assert at.main(["report"]) == 0 and "1 registry keys and 1 keyless list entries" in capsys.readouterr().out
    assert at.main(["report", "--key", "k"]) == 0 and "k: open (2026-09-01)" in capsys.readouterr().out
    assert at.main(["report", "--json"]) == 0 and json.loads(capsys.readouterr().out)["download:1"]["state"] == "never-read"
    assert at.main(["report", "--key", "nonesuch"]) == 1 and "download:<id>" in capsys.readouterr().err
    assert at.main(["set", "download:1", "paywalled", "2026-10-02", "Blocked by: paywalled."]) == 0
    assert at.main(["report", "--key", "download:1", "--json"]) == 0 and '"paywalled"' in capsys.readouterr().out
