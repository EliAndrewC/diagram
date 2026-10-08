"""`scripts/record/record_units.py` and `scripts/record/record_owed.py` - which record checks a delta owes (feature 311).

The GM, 2026-10-02: *"it would be a waste of time and tokens for us to add the kind of paragraph that I just explained and
then rerun all of the other subagent checks"*, and *"not just do the correct thing, to kind of enforce us doing the correct
thing"*. One case per row of the spec's FR-004 table and per Edge Case."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

from tests._scripts import script

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, script(name))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = sys.modules[name.lstrip("_")] = mod  # the old name and the one a sibling imports it by (2026-10-08)
    spec.loader.exec_module(mod)
    return mod


ru = _load("_record_units")
ro = _load("_record_owed")
Q = ru.QUESTIONS

PAGE = (
    '<h2 id="rooms">Rooms for a parley</h2>\n<!-- tags: subject=x -->\n'
    '<p>No page we read has them meeting on the line.<sup class="fn" data-note="absence"></sup></p>\n'
    "<ul>\n<li><strong>At Kyakhta each side built a post.</strong><br>The Russians built theirs at the border."
    '<sup class="fn" data-note="kyakhta"></sup></li>\n</ul>\n'
)
NOTES = '<li data-note="absence">no publicly readable source</li>\n<li data-note="kyakhta">「The Russians quickly built」</li>\n'
DRAWING = '<h2 id="how-our-maps-draw-rooms">How our maps draw rooms</h2>\n<p>A parley room stands on the line.<sup class="fn" data-note="absence"></sup></p>\n'
INTRO = '<p class="intro">In Rokugan, some negotiations take place in a parley room on a border. This is an invention of the setting.</p>\n'


def _with_intro(page: str, intro: str = INTRO) -> str:
    head, rest = page.split("\n", 1)
    return head + "\n" + intro + rest


def _units(base: dict[str, str], now: dict[str, str], sources_base: dict[str, str] | None = None, sources_now: dict[str, str] | None = None) -> list[str]:
    return sorted(u.slug for u in ru.owed(ru.Record.of(now, sources_now or {}), ru.Record.of(base, sources_base or {})))


def _q(page: str = PAGE, notes: str = NOTES, drawing: str = DRAWING, stem: str = "0094-rooms") -> dict[str, str]:
    return {f"{stem}.html": page, f"{stem}.notes.html": notes, f"{stem}.drawing.html": drawing, f"{stem}.drawing.notes.html": NOTES}


# --- the words ----------------------------------------------------------------------------------------------------------


def test_words_drop_comments_markup_and_whitespace_and_keep_the_note_marks() -> None:
    a = '<p>The  <strong>post</strong>\n stood.<!-- a note --><sup class="fn" data-note="k"></sup></p>'
    assert ru.words(a) == "The post stood. [^k]"
    assert ru.words("<p>A &amp; B</p>") == "A & B"
    assert ru.words("<li><strong>A lead.</strong><br>Its body.</li>") == "A lead. Its body."


def test_a_page_is_read_as_heading_intro_and_blocks() -> None:
    p = ru.read_page(_with_intro(PAGE))
    assert p.heading == "Rooms for a parley"
    assert p.intro.startswith("In Rokugan")
    assert [b.marks for b in p.blocks] == [(), ("absence",), ("kyakhta",)]
    assert p.blocks[0].intro and not p.blocks[1].intro


# --- FR-004, row by row ---------------------------------------------------------------------------------------------------


def test_the_intro_alone_owes_the_intro_check_and_record_format_and_nothing_that_reads_a_source() -> None:
    """SC-001: the GM's own example."""
    assert _units(_q(), _q(page=_with_intro(PAGE))) == ["intro-check:0094", "record-format:0094"]


def test_a_changed_intro_owes_the_same_two_and_a_removed_one_the_intro_check() -> None:
    base = _q(page=_with_intro(PAGE))
    changed = _q(page=_with_intro(PAGE, INTRO.replace("some negotiations", "certain negotiations")))
    assert _units(base, changed) == ["intro-check:0094", "record-format:0094"]
    assert _units(base, _q()) == ["intro-check:0094"]


def test_a_changed_heading_owes_the_intro_check_alone() -> None:
    assert _units(_q(), _q(page=PAGE.replace("Rooms for a parley<", "Rooms for a parley across a border<"))) == ["intro-check:0094"]


def test_a_changed_note_owes_the_source_reader_and_quote_check_on_it_and_record_format() -> None:
    now = _q(notes=NOTES.replace("quickly built", "quickly built the post"))
    assert _units(_q(), now) == ["quote-check:0094#kyakhta", "record-format:0094", "source-reader:0094#kyakhta"]


def test_a_note_cites_its_linked_keys_and_never_a_bare_code_symbol() -> None:
    """Feature 319 (G4): Sugiura's table letters went into `<code>` to keep the glossary's tooltips off them, and
    `make record-owed` then asked for a source-reader bundle of a source named `be`."""
    notes = '<li data-note="kyakhta"><a href="https://x.org/k"><code>kyakhta</code></a> - 「privy <code>be</code>」</li>\n'
    assert ru.Record.of({"0094-rooms.notes.html": notes}, {}).cites["0094"] == {"kyakhta": ("kyakhta",)}


def test_a_reworded_noted_block_owes_quote_check_on_its_notes_and_record_format() -> None:
    now = _q(page=PAGE.replace("built theirs at the border", "built their post at the border"))
    assert _units(_q(), now) == ["quote-check:0094#kyakhta", "record-format:0094"]


def test_a_new_unmarked_block_owes_the_unfootnoted_reading_and_record_format() -> None:
    now = _q(page=PAGE + "<p>Both sides traded furs.</p>\n")
    assert _units(_q(), now) == ["quote-check:0094#unfootnoted", "record-format:0094"]


def test_comments_tags_and_formatting_owe_nothing() -> None:
    """US2 scenario 4 and the formatting-only edge case: a sweep that changes no words owes no check."""
    now = _q(page=PAGE.replace("subject=x", "subject=y").replace("<strong>At Kyakhta", "<strong> At  Kyakhta").replace("</p>", "<!-- seen --></p>", 1))
    assert _units(_q(), now) == []


def test_the_drawing_page_owes_by_its_own_stem_and_never_the_intro_check() -> None:
    now = _q(drawing=DRAWING.replace("stands on the line", "stands astride the line"))
    assert _units(_q(), now) == ["quote-check:0094.drawing#absence", "record-format:0094"]


def test_a_new_question_owes_every_check() -> None:
    assert _units({}, _q()) == [
        "intro-check:0094",
        "quote-check:0094#absence",
        "quote-check:0094#kyakhta",
        "quote-check:0094.drawing#absence",
        "quote-check:0094.drawing#kyakhta",
        "record-format:0094",
        "source-reader:0094#absence",
        "source-reader:0094#kyakhta",
        "source-reader:0094.drawing#absence",
        "source-reader:0094.drawing#kyakhta",
    ]


def test_a_question_moved_or_renumbered_owes_the_intro_check_on_its_heading_alone() -> None:
    """Edge case: the words stand elsewhere in the record at the base, so only the new heading is owed."""
    moved = _q(page=PAGE.replace('id="rooms">Rooms for a parley', 'id="rooms-x">Rooms for a parley at a border'), stem="0120-rooms-x")
    assert _units(_q(), moved) == ["intro-check:0120"]
    renumbered = _q(stem="0120-rooms")
    assert _units(_q(), renumbered) == []


def test_a_deleted_note_owes_nothing_itself_but_its_block_owes_the_unfootnoted_reading() -> None:
    now = _q(page=PAGE.replace('<sup class="fn" data-note="kyakhta"></sup>', ""), notes=NOTES.split("\n")[0] + "\n")
    assert _units(_q(), now) == ["quote-check:0094#unfootnoted", "record-format:0094"]


def test_a_source_write_up_owes_source_applicability_on_its_visible_text_only() -> None:
    w = "<h3 id=\"k\">k</h3>\n<p><em>What it is:</em> a page.<!-- READ --></p>\n"
    assert _units(_q(), _q(), {"k": w}, {"k": w.replace("READ", "READ again")}) == []
    assert _units(_q(), _q(), {"k": w}, {"k": w.replace("a page.", "a city history page.")}) == ["source-applicability:k"]
    assert _units(_q(), _q(), {}, {"k": w}) == ["source-applicability:k"]


# --- fingerprints and the answer record -----------------------------------------------------------------------------------


def test_a_fingerprint_moves_with_the_words_the_check_reads_and_only_those() -> None:
    rec = ru.Record.of(_q(), {})
    other = ru.Record.of(_q(notes=NOTES.replace("quickly built", "built")), {})
    assert ru.fingerprint(rec, "record-format:0094") != ru.fingerprint(other, "record-format:0094")
    assert ru.fingerprint(rec, "quote-check:0094#absence") == ru.fingerprint(other, "quote-check:0094#absence")
    assert ru.fingerprint(rec, "intro-check:0094") == ru.fingerprint(other, "intro-check:0094")


def test_an_answer_record_is_current_until_its_content_moves(tmp_path: pathlib.Path) -> None:
    store = tmp_path / "record-checks"
    ro.write_answer(store, "record-format:0094", "fp1", "0/0/0")
    assert ro.answered(store, "record-format:0094", "fp1")
    assert not ro.answered(store, "record-format:0094", "fp2")
    assert not ro.answered(store, "quote-check:0094#k", "fp1")
    ro.write_answer(store, "record-format:0094", "fp2", "0/0/0")
    assert ro.answered(store, "record-format:0094", "fp1") and ro.answered(store, "record-format:0094", "fp2"), "reverted words stay answered"
    assert not ro.answered(store, "record-format:0094", "fp3")
    saved = json.loads(next(store.iterdir()).read_text(encoding="utf-8"))
    assert saved["unit"] == "record-format:0094" and saved["result"] == "0/0/0"


def test_a_bundle_answers_a_modal_key_with_a_space(tmp_path: pathlib.Path) -> None:
    """Feature 317: `unit: entry-drift:cart yard <fp>` was skipped by a `\\S+` slug, so the unit stayed owed forever."""
    bundle = tmp_path / "b"
    bundle.mkdir()
    (bundle / "MANIFEST.md").write_text("## Owed\n\nunit: entry-drift:cart yard fp1\nunit: entry-drift:road fp2\n", encoding="utf-8")
    assert ro.answer(tmp_path, "entry-drift", "IN-STEP", bundle=str(bundle)) == ["entry-drift:cart yard", "entry-drift:road"]
    assert ro.answered(ro.store(tmp_path), "entry-drift:cart yard", "fp1")


# --- the whole command, on a real repository ------------------------------------------------------------------------------


def _git(d: pathlib.Path, *a: str) -> str:
    return subprocess.run(["git", *a], cwd=d, check=True, capture_output=True, text=True).stdout


def _repo(tmp_path: pathlib.Path) -> pathlib.Path:
    d = tmp_path / "r"
    d.mkdir()
    _git(d, "init", "-q", "-b", "main")
    _git(d, "config", "user.email", "t@t")
    _git(d, "config", "user.name", "t")
    for name, text in _q().items():
        f = d / Q / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")
    _git(d, "add", "-A")
    _git(d, "commit", "-qm", "base")
    _git(d, "update-ref", "refs/remotes/origin/main", "HEAD")
    return d


def test_the_command_names_the_units_and_drops_the_answered_ones(tmp_path: pathlib.Path) -> None:
    d = _repo(tmp_path)
    (d / Q / "0094-rooms.html").write_text(_with_intro(PAGE), encoding="utf-8")
    _git(d, "commit", "-qam", "intro")
    units = ro.units(d)
    assert [u.slug for u in units] == ["intro-check:0094", "record-format:0094"]
    assert "make check-bundle Q=0094 FOR=intro-check" in ro.report(units)
    for u in units:
        ro.write_answer(ro.store(d), u.slug, u.fingerprint, "0/0/0")
    assert ro.unanswered(d) == []
    (d / Q / "0094-rooms.html").write_text(_with_intro(PAGE, INTRO.replace("some", "certain")), encoding="utf-8")
    assert [u.slug for u in ro.unanswered(d)] == ["intro-check:0094", "record-format:0094"]


def test_the_command_replays_a_commit_pair(tmp_path: pathlib.Path) -> None:
    d = _repo(tmp_path)
    (d / Q / "0094-rooms.notes.html").write_text(NOTES.replace("quickly built", "built"), encoding="utf-8")
    _git(d, "commit", "-qam", "note")
    assert [u.slug for u in ro.units(d, "HEAD~1", "HEAD")] == ["quote-check:0094#kyakhta", "record-format:0094", "source-reader:0094#kyakhta"]


def test_the_cli_prints_the_units_and_the_unanswered_ones(tmp_path: pathlib.Path, capsys) -> None:  # noqa: ANN001
    d = _repo(tmp_path)
    (d / Q / "0094-rooms.html").write_text(_with_intro(PAGE), encoding="utf-8")
    assert ro.main(["--root", str(d)]) == 0
    assert "intro-check:0094" in capsys.readouterr().out
    assert ro.main(["--root", str(d), "--unanswered", "--slugs"]) == 0
    assert capsys.readouterr().out.split() == ["intro-check:0094", "record-format:0094"]
    assert ro.main(["--root", str(d), "--q", "0095", "--slugs"]) == 0
    assert capsys.readouterr().out == ""


def test_a_write_up_numbered_past_four_digits_owes_its_check(tmp_path: pathlib.Path) -> None:
    """Half the registry is numbered 1xxxx/2xxxx (`20500-visitbeijing-zhili-yamen.html`); a four-digit pattern read none of
    them, so a new write-up there owed nothing - found by the SC-002 replay."""
    d = _repo(tmp_path)
    f = d / ru.SOURCES / "20500-some-key.html"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text('<h3 id="some-key">some-key</h3>\n<p><em>What it is:</em> a page.</p>\n', encoding="utf-8")
    assert [u.slug for u in ro.units(d)] == ["source-applicability:some-key"]


def test_an_entry_drift_unit_names_its_sections_number_and_its_answer() -> None:
    """Its subject is a modal's key, never a question: the hint once read `make check-bundle Q=vegetable garden`, refused."""
    u = ru.Unit("entry-drift:vegetable garden", "its section's findings moved (0038-sunlight-and-shade-on-the-farm.drawing.html)")
    cmd = ro.command(u)
    assert "Q=0038 FOR=entry-drift" in cmd and 'CHECK=entry-drift KIND="vegetable garden"' in cmd
    assert "Q=<its section>" in ro.command(ru.Unit("entry-drift:well", "its section's findings moved ()"))


def test_kind_names_several_modals_at_once(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 319: answering 248 modals one `make record-checked KIND=` at a time took over an hour (every call
    recomputes the owed tree), so KIND takes a comma-separated list and one call answers them all."""
    from types import SimpleNamespace

    us = [SimpleNamespace(check="modal-form", subject=s, slug=f"modal-form:{s}", fingerprint="fp") for s in ("hamlet/a", "choice/b--T", "sheet/c")]
    monkeypatch.setattr(ro, "units", lambda root: us)
    assert ro.answer(tmp_path, "modal-form", "ok", kind="hamlet/a,choice/b--T") == ["modal-form:hamlet/a", "modal-form:choice/b--T"]
    assert ro.answer(tmp_path, "modal-form", "ok", kind="sheet/c") == ["modal-form:sheet/c"], "one unit, as before"
