"""Feature 209 (GM 2026-09-07): the research record is written for its READER - the mechanical half.

The GM read the first entry of `research/homesteads.html` as a reader would and ruled, for every entry: a term a
casual reader would not know is a hover tooltip, as on the map (*"apply the same kind of tooltip rules to our
research sections that we have in our diagram HTML pages"*); a note for a session - `Grounds:`, `Evidence:`, a
spec-kit feature, a task id - is an HTML comment (*"anything which is a note for you ... should be hidden in HTML
comments"*); and the document's own history - what a sentence used to say, a correction, a re-read - is not in
the document (*"we can look it up in our version control history"*). What a test can hold: the fields are
comments, the shapes of session-speak and of history that keep recurring are absent from the visible text, every
page loads the glossary, and the committed glossary asset is the derivation. What only the `record-format` agent
can hold - whether a word deserves a tooltip, whether a sentence is addressed to a session, whether a note is
history - is its job, before a research edit lands (`research/CLAUDE.md`, "Written for the reader")."""

from __future__ import annotations

import html
import pathlib
import re

import pytest

from l7r.diagram.interactive.glossary import GLOSSARY, record_glossary_js
from l7r.diagram.interactive.sources import RESEARCH_DIR

_COMMENT = re.compile(r"<!--.*?-->", re.S)
_TAG = re.compile(r"<[^>]+>")
#: The registry has no Grounds/Evidence fields (it is not a finding); every other rule holds over it too.
_NOT_FINDINGS = {"SOURCES.html"}


def _all_pages() -> list[pathlib.Path]:
    root = pathlib.Path(RESEARCH_DIR)
    # the citations pages (feature 211) are record pages a reader meets: the works write-ups and the notes are under
    # every rule here except the Grounds/Evidence one (they are not findings)
    return sorted(root.glob("*.html")) + sorted((root / "cities").glob("*.html")) + sorted((root / "citations").glob("*.html")) + sorted((root / "citations" / "cities").glob("*.html"))


def _finding_files() -> list[pathlib.Path]:
    return [p for p in _all_pages() if p.name not in _NOT_FINDINGS and "citations" not in p.parts]


def visible_text(page: str) -> str:
    """What a reader sees: comments gone, tags gone, entities decoded, whitespace collapsed."""
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub(" ", _COMMENT.sub(" ", page)))).strip()


#: Session-speak and document history in the shapes that recurred across the record before the sweep. Each is
#: unambiguous in a finding's prose: a spec-kit feature or task, a spec directory, a correction with its date, a
#: re-read, a fetch verdict (READ / SUMMARY-ONLY / UNFETCHABLE / NOT-FOUND / CONTRADICTED are the source-reader's
#: words, addressed to the session that dispatched it), the 2026-08-28 re-sourcing pass's "leftover" and "not
#: re-sourced", and "used to say". A claim the record cannot support is labeled a GUESS for the reader, not a
#: verdict for a session.
FORBIDDEN_VISIBLE: tuple[tuple[str, str], ...] = (
    ("a spec-kit feature number", r"\bfeature \d{3}\b"),
    ("a task id", r"\bT\d{2}\b"),
    ("a spec directory", r"\bspecs/"),
    ("a correction note", r"\b[Cc]orrected 20\d\d"),
    ("a re-read note", r"\b[Rr]e-read\b"),
    ("a fetch verdict", r"\b(?:READ|SUMMARY-ONLY|UNFETCHABLE|NOT-FOUND|CONTRADICTED)\b"),
    ("a re-sourcing pass marker", r"\bleftover\b|\bnot re-sourced\b|\bunsourced at the check of\b"),
    ("what the document used to say", r"\bused to (?:say|read)\b"),
    ("a field for a session", r"\b(?:Grounds|Evidence):"),
)


def offenses(text: str) -> list[str]:
    out = []
    for what, pat in FORBIDDEN_VISIBLE:
        for m in re.finditer(pat, text):
            out.append(f"{what}: ...{text[max(0, m.start() - 60) : m.end() + 60]}...")
    return out


@pytest.mark.parametrize("page", _all_pages(), ids=lambda p: str(p.relative_to(RESEARCH_DIR)))
def test_every_record_page_loads_the_glossary_before_the_record_script(page: pathlib.Path) -> None:
    text = page.read_text(encoding="utf-8")
    prefix = "../" * len(page.relative_to(RESEARCH_DIR).parts[:-1]) + "assets/"
    g = text.find(f'<script src="{prefix}glossary.js" defer></script>')
    r = text.find(f'<script src="{prefix}record.js" defer></script>')
    assert 0 <= g < r, f"{page.name}: the glossary asset is loaded, and before record.js (both deferred, so document order is run order)"


def test_the_committed_glossary_asset_is_the_derivation() -> None:
    """`make glossary` writes it from `glossary.py`; the file is committed because the pages are static. A term
    added to the table without the run fails here, with the command that fixes it."""
    committed = pathlib.Path(RESEARCH_DIR, "assets", "glossary.js").read_text(encoding="utf-8")
    assert committed == record_glossary_js(), "research/assets/glossary.js is stale against interactive/glossary.py - run `make glossary`"
    assert committed.startswith("// DERIVED FILE") and "window.RECORD_GLOSSARY = [" in committed
    assert all(term in committed for term in ("yashikirin", "kainyo", "sugi")), "the record's own vocabulary is in it (non-vacuity)"


def _bounded_in(variant: str, text: str) -> bool:
    """Whether `variant` stands in `text` as a word: not after a word character or an apostrophe, not before a word character.

    The same bounded pattern as a whole-text `re.search`, tried only where `str.find` puts the substring. A pattern
    opening with a lookbehind is attempted at EVERY position of the text, and over the whole record that was 12 ms a
    variant and 8.9 of this test's 9.7 s (cProfile, 2026-09-13). `match(text, pos)` still sees the characters before
    `pos`, so the lookbehind decides exactly as it did."""
    pattern = re.compile(r"(?<![\w'])" + re.escape(variant) + r"(?![\w])")
    at = text.find(variant)
    while at != -1:
        if pattern.match(text, at):
            return True
        at = text.find(variant, at + 1)
    return False


_WORDY = re.compile(r"\w+")
_BOUNDED_RUN = re.compile(r"(?<![\w'])\w+")


def bounded_words(text: str) -> set[str]:
    """Every maximal run of word characters in `text` that no apostrophe precedes - built ONCE per text.

    For a variant made only of word characters, `_bounded_in(variant, text)` holds exactly when the variant is one of
    these runs: its boundary rule (no word character or apostrophe before, no word character after) is the definition
    of a maximal run with no apostrophe in front (feature 276, FR-002). The lookbehind is the rule's whole one - no
    word character AND no apostrophe - because a run refused for its apostrophe would otherwise be retried one
    character in, and `o'koku` would record `oku`: the equality test below holds that case."""
    return {m.group(0) for m in _BOUNDED_RUN.finditer(text)}


def bounded_word_starts(text: str) -> dict[str, list[int]]:
    """`bounded_words(text)` with WHERE each run starts - the same runs, as keys (feature 276, FR-002)."""
    out: dict[str, list[int]] = {}
    for m in _BOUNDED_RUN.finditer(text):
        out.setdefault(m.group(0), []).append(m.start())
    return out


_FIRST_RUN = re.compile(r"\w+(?=\W)")


def stands_in(variant: str, text: str, words: set[str] | dict[str, list[int]]) -> bool:
    """`_bounded_in(variant, text)`, answered from `words` (`bounded_words(text)`) whenever the variant is one word.

    A variant of several words that OPENS with a word run followed by a non-word character is searched only when that
    run is itself in `words` (feature 276): where the variant stands bounded, its first run has no word character or
    apostrophe before it and a non-word character after it - a maximal run with no apostrophe in front, which is what
    `words` holds. So a missing first run is a sure NO, and the search decides the rest."""
    if _WORDY.fullmatch(variant):
        return variant in words
    first = _FIRST_RUN.match(variant)
    if first is not None and first.group(0) not in words:
        return False
    if first is not None and isinstance(words, dict):
        # ...and with the starts known, the variant is tried only where its first run starts: a bounded match begins
        # exactly there, so this is the search `_bounded_in` makes without walking the text to find those places.
        pattern = re.compile(r"(?<![\w'])" + re.escape(variant) + r"(?![\w])")
        return any(pattern.match(text, at) for at in words[first.group(0)])
    return _bounded_in(variant, text)


def test_the_word_set_answers_as_the_bounded_search_does() -> None:
    """FR-002's equality: over text built to hit every boundary the rule names - an apostrophe, an underscore, digits,
    a non-ASCII word character, the text's own ends, a variant inside a longer word, a repeated near-miss before a hit."""
    text = "koku o'koku kokudaka xkoku _koku koku_ 2koku koku2 ōkoku kōku sugi. 'sugi sugi's ta-koku (koku) kokukoku koku"
    words = bounded_words(text)
    starts = bounded_word_starts(text)
    assert set(starts) == words
    for variant in ("koku", "sugi", "kokudaka", "kōku", "koku2", "_koku", "ta", "s", "o", "kokukoku", "ōkoku", "oku", "okudaka", "ugi", "missing"):
        assert stands_in(variant, text, words) == _bounded_in(variant, text), variant
    for variant in (
        "ta-koku",
        "sugi's",
        "(koku)",
        "o'koku",
        "oku daka",
        "missing koku",
        "koku koku",
        "kokud-aka",
        "koku.",
        "sugi's s",
    ):  # not one word: the bounded search answers, as before - the prefilter's NO included
        assert stands_in(variant, text, words) == _bounded_in(variant, text) == stands_in(variant, text, starts), variant


def test_bounded_in_reads_the_boundaries_as_the_pattern_did() -> None:
    assert _bounded_in("koku", "the koku of rice") and _bounded_in("koku", "koku")
    assert not _bounded_in("koku", "kokudaka") and not _bounded_in("koku", "o'koku") and not _bounded_in("koku", "xkoku")
    assert _bounded_in("koku", "kokudaka and koku.")


def test_every_glossary_term_is_used_by_a_modal_or_a_record_page() -> None:
    """The map's own test holds the modal half; this is the widened rule (spec FR-001): a term that no modal and no
    record page uses is dead weight, and a term the record uses in a code span only is not a tooltip anywhere."""
    from l7r.diagram.interactive.classes import CLASSES
    from l7r.diagram.interactive.compound_kinds import COMPOUND_CLASSES
    from l7r.diagram.interactive.page import explanations, glossary_for

    in_modals = {g["term"] for g in glossary_for(explanations(set(CLASSES)))} | {g["term"] for g in glossary_for(explanations(set(COMPOUND_CLASSES), registry=COMPOUND_CLASSES))}
    record = " ".join(visible_text(_COMMENT.sub(" ", re.sub(r"<code>.*?</code>", " ", p.read_text(encoding="utf-8"), flags=re.S))) for p in _all_pages()).lower()
    words = bounded_word_starts(record)  # built once: a one-word variant is a set lookup, not a search of the whole record (FR-002)
    in_record = {term for term, (variants, _) in GLOSSARY.items() if any(stands_in(v.lower(), record, words) for v in variants)}
    unused = set(GLOSSARY) - in_modals - in_record
    assert not unused, f"glossary terms no modal and no record page uses: {sorted(unused)}"
    assert {"kainyo", "sugi"} <= in_record - in_modals, "record-only terms are what this test exists for (non-vacuity)"


@pytest.mark.parametrize("page", _finding_files(), ids=lambda p: p.name)
def test_the_fields_for_a_session_are_comments(page: pathlib.Path) -> None:
    text = page.read_text(encoding="utf-8")
    sections = len(re.findall(r"<h2 ", text))
    grounds = len(re.findall(r"<!-- Grounds:", text))
    evidence = len(re.findall(r"<!-- Evidence:", text))
    assert grounds and evidence, f"{page.name}: the Grounds and Evidence fields are kept, as comments (non-vacuity: {sections} sections)"
    assert not re.search(r"\b(?:Grounds|Evidence):", visible_text(text)), f"{page.name}: a field for a session is visible"


@pytest.mark.parametrize("page", _all_pages(), ids=lambda p: str(p.relative_to(RESEARCH_DIR)))
def test_no_session_note_or_document_history_is_visible(page: pathlib.Path) -> None:
    """Every page, the registry included (spec 209 round 1: the GM's rules 2 and 3 are not scoped to finding entries).
    The registry's verification markers - READ, SUMMARY-ONLY, unfetched, the feature - live in a comment inside each
    citation paragraph, where `test_sources.py`'s classifier still reads them and a reader does not see them."""
    found = offenses(visible_text(page.read_text(encoding="utf-8")))
    assert not found, (
        f"{page.name}: {len(found)} visible note(s) for a session or piece(s) of the document's history - move each into an HTML comment or drop it (research/CLAUDE.md, 'Written for the reader'):\n"
        + "\n".join(found[:40])
    )


def test_the_forbidden_shapes_fire_and_stay_quiet_on_a_reader_s_sentence() -> None:
    assert len(offenses("kept as a GUESS (corrected 2026-09-06, feature 194: the page gives 20 bu) READ 2026-08-28; T41; see specs/209")) >= 5
    assert not offenses("The GM ruled between the two readings on 2026-08-28: the sourced shape everywhere. Searched 2026-09-06: mdpi.com refused; a GUESS.")
    assert not offenses(visible_text("<p>x</p><!-- Grounds: feature 209 T03 corrected 2026-09-07 -->"))
