"""`scripts/gates/check-partial-citations.py` - a footnote citing a source no one can wholly read stands only on a confirmed
passage (feature 312, FR-019, FR-020).

WHAT THESE PROVE. A footnote citing a key in the unreadable set with no confirmation line is named, with the fix; a
confirmed one passes; a key that can be read passes; a malformed confirmation line is skipped; the command exits 1 on a
finding, and the real record's unreadable set comes from feature 313's tags."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("check_partial_citations", REPO / "scripts/gates/check-partial-citations.py")
assert spec and spec.loader
cp = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = cp
spec.loader.exec_module(cp)


def _record(tmp_path: pathlib.Path) -> pathlib.Path:
    q = tmp_path / cp.RECORD / "questions"
    q.mkdir(parents=True)
    (q / "0001-a.notes.html").write_text(
        '<li data-note="pay"><a href="https://p.org"><code>pay</code></a> - 「x」</li>\n'
        '<li data-note="pay-2"><a href="https://p.org"><code>pay</code></a> - 「y」</li>\n'
        '<li data-note="open"><a href="https://o.org"><code>open</code></a> - 「z」</li>\n',
        encoding="utf-8",
    )
    (tmp_path / cp.CONFIRMED).write_text(json.dumps({"key": "pay", "note": "0001-a.notes.html#pay"}) + "\nnot json\n", encoding="utf-8")
    return tmp_path


def test_an_unconfirmed_footnote_on_an_unreadable_source_is_named(tmp_path: pathlib.Path) -> None:
    root = _record(tmp_path)
    got = cp.findings(root, {"pay": "paywalled"}, cp.confirmed(root))
    assert len(got) == 1 and got[0].startswith("0001-a.notes.html#pay-2: cites `pay` (paywalled) with no confirmed passage")
    assert "partial-confirmations.jsonl" in got[0] and "absence note" in got[0]
    assert cp.findings(root, {}, set()) == [], "a readable source owes nothing"


def test_the_command_exits_on_a_finding(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:  # noqa: ANN001
    root = _record(tmp_path)
    monkeypatch.setattr(cp, "unreadable_keys", lambda r: {"pay": "never-read"})
    assert cp.main([str(root)]) == 1 and "cites `pay` (never-read)" in capsys.readouterr().err
    monkeypatch.setattr(cp, "unreadable_keys", lambda r: {})
    assert cp.main([str(root)]) == 0


def test_the_unreadable_set_comes_from_the_access_tags() -> None:
    keys = cp.unreadable_keys(REPO)
    assert set(keys.values()) <= set(cp.UNREADABLE) and not any(k.startswith("download:") for k in keys)


def test_a_tree_with_no_access_states_names_no_unreadable_source(tmp_path: pathlib.Path) -> None:
    """A push fixture carries no `source-access.json`: the check passes it rather than crashing (2026-10-02)."""
    assert cp.unreadable_keys(tmp_path) == {} and cp.main([str(tmp_path)]) == 0
