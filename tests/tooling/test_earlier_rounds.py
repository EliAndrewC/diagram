"""`scripts/record/earlier_rounds.py` (feature 393): a later round of a record or pop-up check reads the earlier rounds.

WHAT THESE PROVE. A question bundle's MANIFEST lists each earlier round of the check it owes on that page - its verdict, its
findings, its EDIT blocks marked APPLIED or NOT APPLIED against the page as it stands, the round arbiter's ruling with its
reasons - and copies each whole reply beside it (SC-001); a pop-up bundle does the same, and with no earlier round it is
byte-identical to the bundle built without this feature (SC-002); an earlier feature's rounds, a running round and another
check's rounds are not handed over; and the contract paragraph is the same words in every check that receives them (SC-003).
"""

from __future__ import annotations

import json
import pathlib

import pytest

from tests._scripts import script
from tests.tooling.test_modal_checks import _load, _tree, mb

er = _load("_earlier_rounds")
cb = _load("_check_bundle")

REPO = pathlib.Path(__file__).resolve().parents[2]
ROUND_1 = """2 findings.

1. The lead says "a household of five" where the page's source says six - the figure must follow the source.
EDIT research/questions/0029-farmhouses-minka.html
<<<
A farmhouse was the dwelling of one household.
===
A farmhouse was the dwelling of one household of six.
>>>
2. The second paragraph names no source for the thatch.
EDIT research/questions/0029-farmhouses-minka.html
<<<
It was thatched.
===
It was thatched with reed.
>>>
"""
ROUND_2 = "1 finding.\n\n1. The second paragraph still names no source for the thatch.\n"
#: the agents whose bundles carry earlier rounds (check_bundle.py's and modal_bundle.py's page checks)
RECEIVERS = ("quote-check", "record-format", "source-reader", "intro-check", "translation-check", "entry-drift", "record-style", "modal-form", "modal-depiction", "modal-research")


def _state(root: pathlib.Path, dispatches: dict, rulings: list[dict] | None = None) -> None:
    (root / ".git" / "checks-open.json").write_text(json.dumps({"feature": "specs/393-x", "dispatches": dispatches}), encoding="utf-8")
    (root / ".specify").mkdir(exist_ok=True)
    (root / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/393-x"}), encoding="utf-8")
    (root / "specs" / "393-x").mkdir(parents=True, exist_ok=True)
    (root / "specs" / "393-x" / "arbiter.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rulings or []), encoding="utf-8")


def _reply(root: pathlib.Path, name: str, text: str) -> str:
    p = root / ".git" / "check-replies" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return str(p)


def _dispatch(check: str, subject: str, t: float, reply: str = "", state: str = "answered") -> dict:
    return {"check": check, "subjects": [subject], "t": t, "state": state, "reply": reply, "aid": ""}


def test_a_question_bundle_lists_the_earlier_rounds_their_edits_and_the_rulings(tmp_path: pathlib.Path) -> None:
    root = _tree(tmp_path)
    _state(
        root,
        {
            "a": _dispatch("quote-check", "q:0029", 10.0, _reply(root, "a.md", ROUND_1)),
            "b": _dispatch("quote-check", "q:0029", 20.0, _reply(root, "b.md", ROUND_2)),
            "c": _dispatch("record-format", "q:0029", 15.0, _reply(root, "c.md", "1 finding.\n\n1. A word the glossary lacks.\n")),
            "d": _dispatch("quote-check", "q:0029", 30.0, state="running"),
            "e": _dispatch("quote-check", "q:0004", 12.0, _reply(root, "e.md", ROUND_2)),
        },
        [{"trigger": "round:quote-check|q:0029@3", "ruling": "continue", "why": "the thatch finding was never answered", "what": "only the thatch sentence"}],
    )
    page = root / "research" / "questions" / "0029-farmhouses-minka.html"
    page.write_text(page.read_text(encoding="utf-8").replace("one household.", "one household of six."), encoding="utf-8")
    out = tmp_path / "bundle"
    out.mkdir()
    text = "# Check bundle\n\n## Owed (feature 311)\n\nowed-checks: quote-check\nunit: quote-check:0029.page#lead abc\n"
    got = cb.with_earlier(root, out, text)
    assert got.startswith(text) and er.HEAD in got
    body = got[len(text) :]
    assert "### quote-check on q:0029" in body and "record-format" not in body and "q:0004" not in body, "this check, this page only"
    assert "**Round 1**" in body and "**Round 2**" in body and "**Round 3**" not in body, "a running round is not an earlier one"
    assert "- APPLIED: research/questions/0029-farmhouses-minka.html" in body and "- NOT APPLIED:" in body
    assert "- NEW: The lead says" in body, "each finding marked as the arbiter's bundle marks it (its own tests own the marks)"
    assert "**continue** - the thatch finding was never answered | what the next round looks at: only the thatch sentence" in body
    assert (out / "earlier" / "quote-check-q-0029-round-1.md").read_text(encoding="utf-8") == ROUND_1
    assert "`earlier/quote-check-q-0029-round-2.md`" in body


def test_no_state_and_no_earlier_round_leave_the_manifest_alone(tmp_path: pathlib.Path) -> None:
    root = _tree(tmp_path)
    text = "owed-checks: quote-check\nunit: quote-check:0029.page#lead abc\n"
    assert cb.with_earlier(root, tmp_path, text) == text, "no state file"
    _state(root, {"a": _dispatch("record-format", "q:0029", 10.0, _reply(root, "a.md", ROUND_2))})
    assert cb.with_earlier(root, tmp_path, text) == text, "another check's round is not this one's"
    assert er.section(root, tmp_path, "unit: quote-check:0029.page#lead abc\n") == "", "no owed-checks line"


def test_an_earlier_features_rounds_are_not_handed_over(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _tree(tmp_path)
    _state(root, {"a": _dispatch("quote-check", "q:0029", 10.0, _reply(root, "a.md", ROUND_2))})
    monkeypatch.setattr(er, "feature_start", lambda _root: 11.0)
    assert er.section(root, tmp_path, "owed-checks: quote-check\nunit: quote-check:0029.page#lead abc\n") == ""


def test_a_note_scoped_bundle_gets_the_rounds_on_its_notes_or_the_whole_page() -> None:
    state = {
        "dispatches": {
            "a": {**_dispatch("source-reader", "q:0029", 1.0), "notes": ["kume"]},
            "b": {**_dispatch("source-reader", "q:0029", 2.0), "notes": ["sato"]},
            "c": {**_dispatch("source-reader", "q:0029", 3.0), "notes": []},
            "d": _dispatch("source-reader", "q:0029", 4.0),
        }
    }
    assert [v["t"] for v in er.rounds(state, "source-reader", "q:0029", 0.0, {"kume"})] == [1.0, 3.0, 4.0]
    assert len(er.rounds(state, "source-reader", "q:0029", 0.0, set())) == 4


def test_a_pop_up_bundle_carries_its_earlier_rounds_and_is_unchanged_without_them(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHECK_ORDER_OK", "the check order is tests/tooling/test_popup_order.py's subject")
    root = _tree(tmp_path)
    before = tmp_path / "before"
    assert mb.bundle(root, "Farmhouse", "modal-form", str(before)) == 0
    _state(root, {"a": _dispatch("modal-form", "modal:hamlet/farmhouse", 10.0, _reply(root, "a.md", ROUND_2))})
    after = tmp_path / "after"
    assert mb.bundle(root, "Farmhouse", "modal-form", str(after)) == 0
    manifest = (after / "MANIFEST.md").read_text(encoding="utf-8")
    assert "### modal-form on modal:hamlet/farmhouse" in manifest and "**Round 1**" in manifest
    assert (after / "earlier" / "modal-form-modal-hamlet-farmhouse-round-1.md").is_file()
    assert manifest.startswith((before / "MANIFEST.md").read_text(encoding="utf-8").replace(str(before), str(after)))
    (root / ".git" / "checks-open.json").unlink()
    again = tmp_path / "again"
    assert mb.bundle(root, "Farmhouse", "modal-form", str(again)) == 0
    assert (again / "MANIFEST.md").read_text(encoding="utf-8") == (before / "MANIFEST.md").read_text(encoding="utf-8").replace(str(before), str(again))


def test_every_receiving_check_carries_the_same_earlier_rounds_paragraph() -> None:
    paragraphs = {}
    for name in RECEIVERS:
        text = (REPO / ".claude" / "agents" / f"{name}.md").read_text(encoding="utf-8")
        start = text.find("**Earlier rounds (feature 393).**")
        assert start >= 0, f"{name}.md has no Earlier rounds paragraph"
        paragraphs[name] = text[start : text.index("\n\n", start)]
    assert len(set(paragraphs.values())) == 1, "the paragraph differs between agent files"
    assert script("earlier_rounds.py").is_file()
