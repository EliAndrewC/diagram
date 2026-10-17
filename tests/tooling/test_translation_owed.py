"""`scripts/record/translation_owed.py` - which translated quotations owe a translation-check (feature 292, GM 2026-09-29:
*"when either the text being quoted has changed or the translation has changed. And then otherwise that check doesn't
need to run."*)."""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

from tests._scripts import script

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, script(name))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = sys.modules[name.lstrip("_")] = mod  # the old name and the one a sibling imports it by (2026-10-08)
    spec.loader.exec_module(mod)
    return mod


to = _load("_translation_owed")
R = to.RECORD


def _git(d: pathlib.Path, *a: str) -> None:
    subprocess.run(["git", *a], cwd=d, check=True, capture_output=True)


def _note(d: pathlib.Path, path: str, text: str, originals: str | None = None) -> None:
    f = d / R / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text, encoding="utf-8")
    if originals is not None:
        f.with_name(f.name[: -len(".notes.html")] + ".originals.html").write_text(originals, encoding="utf-8")


def test_a_pair_is_read_with_its_original_put_back_and_the_inline_form_too() -> None:
    inline = '<li data-note="k">「An oak」 (translated from the Japanese by this project; original: 「樫」)</li>'
    held = '<li data-note="k">「An oak」 (translated from the Japanese by this project; <span class="orig" data-orig="k#1"></span>)</li>'
    stored = '<li data-orig="k#1">original: 「樫」</li>\n'
    assert to.pairs(inline, "") == to.pairs(held, stored) == [("k", "the Japanese", "An oak", "樫")]
    assert to.pairs('<li data-note="e">"plain" (the source\'s own English)</li>', "") == []


def test_only_a_new_or_changed_pair_is_owed_and_a_moved_one_is_not(tmp_path: pathlib.Path) -> None:
    d = tmp_path
    _git(d, "init", "-q", "-b", "main")
    _git(d, "config", "user.email", "t@t")
    _git(d, "config", "user.name", "t")
    _note(
        d,
        "questions/0010-a.notes.html",
        '<li data-note="k">「An oak」 (translated from the Japanese by this project; original: 「樫」)</li>\n'
        '<li data-note="j">「A pine」 (translated from the Japanese by this project; original: 「松」)</li>\n',
    )
    _git(d, "add", "-A")
    _git(d, "commit", "-qm", "base")
    _git(d, "update-ref", "refs/remotes/origin/main", "HEAD")
    # the oak moves to another question, split out; the pine's translation changes; a cedar is new
    (d / R / "questions/0010-a.notes.html").unlink()
    _note(
        d,
        "questions/0020-b.notes.html",
        '<li data-note="k">「An oak」 (translated from the Japanese by this project; <span class="orig" data-orig="k#1"></span>)</li>\n'
        '<li data-note="j">「A pine tree」 (translated from the Japanese by this project; original: 「松」)</li>\n'
        '<li data-note="c">「A cedar」 (translated from the Japanese by this project; original: 「杉」)</li>\n',
        '<li data-orig="k#1">original: 「樫」</li>\n',
    )
    rows = to.owed(d)
    assert [(r[1], r[3], r[4]) for r in rows] == [("c", "A cedar", "杉"), ("j", "A pine tree", "松")]
    out = to.report(rows)
    assert out.startswith("translation-owed: 2 ") and "  ORIGINAL:    杉" in out


def test_a_new_term_gloss_in_our_own_words_is_owed_too(tmp_path: pathlib.Path) -> None:
    """Feature 292 (GM 2026-09-30): kanji in our own words carries `(romaji, "meaning")`, and that meaning is a
    translation the check reads when the characters or the meaning change."""
    d = tmp_path
    _git(d, "init", "-q", "-b", "main")
    _git(d, "config", "user.email", "t@t")
    _git(d, "config", "user.name", "t")
    _note(d, "questions/0010-a.notes.html", "")
    (d / R / "questions/0010-a.html").write_text('<p>written 垣根 (kakine, "hedge")</p>', encoding="utf-8")
    _git(d, "add", "-A")
    _git(d, "commit", "-qm", "base")
    _git(d, "update-ref", "refs/remotes/origin/main", "HEAD")
    assert to.owed(d) == []
    (d / R / "questions/0010-a.html").write_text('<p>written 垣根 (kakine, "fence")</p>', encoding="utf-8")
    assert [(r[1], r[4]) for r in to.owed(d)] == [("a term's gloss", "垣根")]


def test_the_command_scopes_to_one_question(capsys, tmp_path: pathlib.Path) -> None:  # noqa: ANN001
    # a record of its own (feature 383 amendment 5, plan D33): the real one made this test re-run on any edit to any of its
    # 1,400 question files, and the command reads only what its root holds
    d = tmp_path
    _git(d, "init", "-q", "-b", "main")
    _git(d, "config", "user.email", "t@t")
    _git(d, "config", "user.name", "t")
    _note(d, "questions/0041-a.notes.html", "")
    _git(d, "add", "-A")
    _git(d, "commit", "-qm", "base")
    _git(d, "update-ref", "refs/remotes/origin/main", "HEAD")
    _note(d, "questions/0041-a.notes.html", '<li data-note="k">「An oak」 (translated from the Japanese by this project; original: 「樫」)</li>\n')
    _note(d, "questions/0042-b.notes.html", '<li data-note="j">「A pine」 (translated from the Japanese by this project; original: 「松」)</li>\n')
    for page in ("0041-a.html", "0042-b.html"):  # a question is found by its page; the notes ride beside it
        (d / R / "questions" / page).write_text('<h2 id="x">X</h2>\n', encoding="utf-8")
    assert to.main(["--root", str(d), "--q", "0041"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("translation-owed: ") and all(line.startswith(("translation-owed", "==", "  ")) for line in out.splitlines())


def test_a_parse_cached_by_another_parser_is_not_served(monkeypatch) -> None:  # noqa: ANN001
    """The round arbiter's tooling fix on 0219 (feature 374 wave 122): the cache was keyed by content alone, so a parse an
    older reader wrote was served after the reader changed, and the base's pair stopped matching the tree's."""
    cache: dict[str, list] = {}
    notes, originals = '<li data-note="k">「Shrine」 (translated; original: 「社」)</li>', ""
    first = to._parsed(cache, notes, originals, "")
    stale = [[["k", "", "Shrine", "OLD READER"]], []]
    for key in cache:
        cache[key] = stale  # what an older parser left under this content's key
    assert to._parsed(cache, notes, originals, "") == stale, "the same parser is served its own cached parse"
    monkeypatch.setattr(to, "PARSER_KEY", "another-parser")
    assert to._parsed(cache, notes, originals, "") == first, "a changed parser parses afresh"
    assert len(to.PARSER_KEY) and to.PARSER_KEY == "another-parser"


def test_a_revisions_pairs_are_read_from_git_once(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 375 amendment 8 (FR-036, plan D49): a commit's tree never changes, so its pairs are kept by the questions'
    tree id - every check bundle's owed check read the merge base's pages again through git."""
    d = tmp_path
    _git(d, "init", "-q", "-b", "main")
    _git(d, "config", "user.email", "t@t")
    _git(d, "config", "user.name", "t")
    _note(d, "questions/0010-a.notes.html", '<li data-note="k">「An oak」 (translated from the Japanese by this project; original: 「樫」)</li>\n')
    _git(d, "add", "-A")
    _git(d, "commit", "-qm", "base")
    calls: list[str | None] = []
    real = to._record_pairs
    monkeypatch.setattr(to, "_record_pairs", lambda root, rev: calls.append(rev) or real(root, rev))
    first = to.record_pairs(d, "HEAD")
    assert to.record_pairs(d, "HEAD") == first and calls == ["HEAD"], "read once, then kept by its tree"
    assert ("An oak", "樫") in first
    to.record_pairs(d, None)
    to.record_pairs(d, None)
    assert calls == ["HEAD", None, None], "the working tree is read every time, as before"
    assert to.record_pairs(d, "no-such-rev") == {} and calls[-1] == "no-such-rev", "a revision git cannot name is read as before"
