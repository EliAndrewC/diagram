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


def test_the_command_scopes_to_one_question(capsys) -> None:  # noqa: ANN001
    assert to.main(["--root", str(REPO), "--q", "0041"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("translation-owed: ") and all(line.startswith(("translation-owed", "==", "  ")) for line in out.splitlines())
