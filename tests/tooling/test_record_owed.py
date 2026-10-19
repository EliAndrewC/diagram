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


def test_a_reworded_absence_note_owes_no_source_reader() -> None:
    """Feature 385 T42 (the round arbiter on round:source-reader|q:0081@5): a "no publicly readable source" note names no page, so
    a change to its words owes its quote-check and the page's record-format, never a source-reader round on nothing."""
    now = _q(notes=NOTES.replace("no publicly readable source", "no publicly readable source<!-- searched again --> beyond the post"))
    assert _units(_q(), now) == ["quote-check:0094#absence", "record-format:0094"]


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
        "source-reader:0094#kyakhta",
        "source-reader:0094.drawing#kyakhta",
    ], "an absence note names no page: no source-reader on it (feature 385 T42)"


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


def test_a_note_read_at_its_words_is_netted_and_an_absence_note_owes_no_reading(tmp_path: pathlib.Path) -> None:
    """Feature 385 T42 (q:0081@5): the round that READ a note with no edit since answers it at its fingerprint, so it leaves the
    owed list (measured: 0081.drawing#wang-2021-qing-huabei-dishui-2 and 0247's -6 and -7 carry round 6's "9 READ" at their
    current fingerprints); an absence note re-worded in the same round owes its quote-check, never a source-reader."""
    d = _repo(tmp_path)
    notes = NOTES.replace("quickly built", "built").replace("no publicly readable source", "no publicly readable source, beyond the post")
    (d / Q / "0094-rooms.notes.html").write_text(notes, encoding="utf-8")
    _git(d, "commit", "-qam", "notes")
    slugs = [u.slug for u in ro.unanswered(d)]
    assert "source-reader:0094#kyakhta" in slugs and "source-reader:0094#absence" not in slugs and "quote-check:0094#absence" in slugs
    for u in ro.units(d):
        if u.slug == "source-reader:0094#kyakhta":
            ro.write_answer(ro.store(d), u.slug, u.fingerprint, "1 READ, 0 CONTRADICTED")
    assert "source-reader:0094#kyakhta" not in [u.slug for u in ro.unanswered(d)], "READ at its words: netted"


def test_a_quote_check_answered_stands_when_only_another_note_s_sentence_in_its_block_changes(tmp_path: pathlib.Path) -> None:
    """Feature 395 (the round arbiter on ask:395-round3-all): 43 notes answered SUPPORTS were owed quote-check again because
    another note's sentence in the same block was reworded. An answer now also holds the note's words and the sentences
    carrying its mark, so a change elsewhere in the block owes nothing, and a change to its own claim sentence still does."""
    two = PAGE.replace("The Russians built theirs at the border.", "The Russians built theirs at the border. The Qing post faced it.")
    two = two.replace('<sup class="fn" data-note="kyakhta"></sup></li>', '<sup class="fn" data-note="kyakhta"></sup> It was small.<sup class="fn" data-note="absence"></sup></li>')
    d = _repo(tmp_path)
    (d / Q / "0094-rooms.html").write_text(two, encoding="utf-8")
    _git(d, "commit", "-qam", "page")
    assert ro.answer(d, "quote-check", "SUPPORTS", q="0094", notes="kyakhta") == ["quote-check:0094#kyakhta"]
    (d / Q / "0094-rooms.html").write_text(two.replace("It was small.", "It was very small."), encoding="utf-8")
    assert "quote-check:0094#kyakhta" not in [u.slug for u in ro.unanswered(d)], "another note's sentence changed: still answered"
    (d / Q / "0094-rooms.html").write_text(two.replace("The Qing post faced it.", "The Qing post faced it squarely."), encoding="utf-8")
    assert "quote-check:0094#kyakhta" in [u.slug for u in ro.unanswered(d)], "its own claim sentence changed: owed again"
    assert ru.claims_of("At p. 28 the wall was 3 ft. high. [^a] B rose. [^b]", "a") == ["At p. 28 the wall was 3 ft. high. [^a]"]


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


def test_an_entry_drift_tip_names_its_question_and_the_modal_class(tmp_path: pathlib.Path) -> None:
    """The subject is a modal key with a space in it; the tip gives the question from the occasion and the class by name,
    module-qualified where two modules share the key (2026-10-03: it printed `Q=threshing yard` and left the class to find)."""
    (tmp_path / "classes").mkdir()
    (tmp_path / "compound_kinds").mkdir()
    (tmp_path / "classes" / "homestead.py").write_text("class ThreshingYard(Kind):\n    key = 'threshing yard'\n", encoding="utf-8")
    (tmp_path / "classes" / "water.py").write_text('class Well(Kind):\n    key = "well"\n', encoding="utf-8")
    (tmp_path / "compound_kinds" / "household.py").write_text('class Well(Kind):\n    key = "well"\n', encoding="utf-8")
    assert ro.modal_classes("threshing yard", tmp_path) == ["ThreshingYard"]
    assert ro.modal_classes("well", tmp_path) == ["water.Well", "household.Well"] and ro.modal_classes("none", tmp_path) == []
    u = ru.Unit("entry-drift:threshing yard", "its section's findings moved (0037-threshing.html)", "f")
    tip = ro.command(u)
    assert tip.startswith('make check-bundle Q=0037 FOR=entry-drift KIND="ThreshingYard"') and 'KIND="threshing yard" BUNDLE=' in tip


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


def test_a_depiction_answer_under_the_old_formula_answers_the_same_words(tmp_path: pathlib.Path) -> None:
    """Feature 375 amendment 1 changed the depiction fingerprint's formula, and every depiction answer recorded before it read
    as owed again on the merge (31 units in 343's and 368's clone, 2026-10-11). An old-formula answer still answers the words
    it read - unless the Entry: line, which only the new formula covers, moved since it was recorded."""
    mo = _load("_modal_owed")
    root = tmp_path / "c"
    choice = root / mo.MODALS / "choice"
    choice.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)

    def commit(entry: str, date: str) -> None:
        (choice / "pit.md").write_text(f"About: a pit.\n\nGuesses: its depth.\n\nDepiction: a dark ring.\n\nName: pit\nEntry: {entry}\n")
        env = {"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "PATH": "/usr/bin:/bin"}
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, env=env)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", entry], check=True, env=env)

    commit("research/questions/0047-privies.html", "2026-01-01T00:00:00Z")
    store = tmp_path / "record-checks"
    m = mo.find(root, "choice/pit")
    old = mo.legacy_depiction_fingerprint(root, m)
    assert old != mo.depiction_fingerprint(root, m), "the two formulas differ"
    ro.write_answer(store, "modal-depiction:choice/pit", old, "0/0/0")
    rec = json.loads(next(store.iterdir()).read_text())
    next(store.iterdir()).write_text(json.dumps({**rec, "utc": "2026-01-02T00:00:00Z"}))
    assert ro.legacy_depiction_answered(root, store, "modal-depiction:choice/pit"), "same words, old formula: answered"
    assert not ro.legacy_depiction_answered(root, store, "record-format:0047"), "only depiction units"
    commit("research/questions/0006-dry-fields.html", "2026-01-03T00:00:00Z")
    assert not ro.legacy_depiction_answered(root, store, "modal-depiction:choice/pit"), "Entry: moved: the new formula's part is unread"


def test_a_depiction_answer_under_amendment_1s_formula_survives_an_about_edit(tmp_path: pathlib.Path) -> None:
    """Feature 375 amendment 6 (FR-028, SC-021): the fingerprint dropped About. An answer recorded under amendment 1's formula
    (About in it) still answers its pop-up after an About edit - the formula change re-owes nothing by itself - and not after
    an Entry: edit, which the check still judges."""
    mo = _load("_modal_owed")
    root = tmp_path / "c"
    choice = root / mo.MODALS / "choice"
    choice.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)

    def commit(about: str, entry: str, date: str) -> None:
        (choice / "pit.md").write_text(f"About: {about}\n\nGuesses: its depth.\n\nDepiction: a dark ring.\n\nName: pit\nEntry: {entry}\n")
        env = {"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "PATH": "/usr/bin:/bin"}
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, env=env)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", about], check=True, env=env)

    commit("a pit.", "research/questions/0047-privies.html", "2026-01-01T00:00:00Z")
    store = tmp_path / "record-checks"
    slug = "modal-depiction:choice/pit"
    m = mo.find(root, "choice/pit")
    a1 = mo.amendment1_depiction_fingerprint(root, m)
    assert a1 != mo.depiction_fingerprint(root, m), "the two formulas differ"
    ro.write_answer(store, slug, a1, "0/0/0")
    rec = json.loads(next(store.iterdir()).read_text())
    next(store.iterdir()).write_text(json.dumps({**rec, "utc": "2026-01-02T00:00:00Z"}))
    assert ro.amendment1_depiction_answered(root, store, slug), "the same words: answered"
    assert not ro.amendment1_depiction_answered(root, store, "record-format:0047"), "only depiction units"
    commit("a pit, dug by hand.", "research/questions/0047-privies.html", "2026-01-03T00:00:00Z")
    assert not ro.answered(store, slug, mo.amendment1_depiction_fingerprint(root, mo.find(root, "choice/pit"))), "today's words differ"
    assert ro.amendment1_depiction_answered(root, store, slug), "an About edit since: still answered (FR-028)"
    commit("a pit, dug by hand.", "research/questions/0006-dry-fields.html", "2026-01-04T00:00:00Z")
    assert not ro.amendment1_depiction_answered(root, store, slug), "an Entry: edit since: owed again"
    assert not ro.amendment1_depiction_answered(root, tmp_path / "empty", slug), "no answer recorded"


def test_pop_ups_one_check_owes_are_named_as_one_batch_and_kept_for_the_guard() -> None:
    """Feature 385 T81 (plan D100; the GM's approved change 1): T10's checks sent 90 agents, each on a single pop-up."""
    u = ru.Unit
    rows = [
        u("modal-form:choice/split--0.6", "its words changed"),
        u("modal-form:choice/split--0.4", "its words changed"),
        u("modal-depiction:choice/split--0.6", "its words changed"),
        u("modal-research-accuracy:choice/split--0.6", "its words changed"),
        u("modal-research-gaps:choice/split--0.4", "its words changed"),
        u("modal-form:choice/split--0.7", "a page its References name moved (0018-x.html)"),  # triage first
    ]
    assert ro.modal_batches(rows) == {"modal-form": ["choice/split--0.6", "choice/split--0.4"], "modal-research": ["choice/split--0.6", "choice/split--0.4"]}
    assert ro.modal_batches(rows, {"modal-form:choice/split--0.4"}) == {"modal-research": ["choice/split--0.6", "choice/split--0.4"]}, "an answered one leaves"
    assert 'batched: make modal-bundle KIND="choice/split--0.6 choice/split--0.4" FOR=modal-form' in ro.report(rows)


def test_a_pop_up_the_triage_sent_on_joins_its_checks_batch() -> None:
    """Feature 385 T93 (plan D115): T31's six pop-ups the triage marked touched kept naming `make modal-triage`, out of the batch."""
    why = "a page its References name moved (0246-x.html)"
    a, b, c = (ru.Unit(f"modal-depiction:choice/lane--{k}", why, "fp") for k in ("spine", "cross", "loop"))
    touched = {a.slug: "fp", b.slug: "fp", c.slug: "an older fingerprint"}
    assert ro.modal_batches([a, b, c]) == {}, "untriaged: triage first"
    assert ro.modal_batches([a, b, c], (), touched) == {"modal-depiction": ["choice/lane--spine", "choice/lane--cross"]}
    assert "make modal-bundle" in ro.command(a, None, touched) and "make modal-triage" in ro.command(c, None, touched)
    text = ro.report([a, b, c], None, (), touched)
    assert 'batched: make modal-bundle KIND="choice/lane--spine choice/lane--cross" FOR=modal-depiction' in text
