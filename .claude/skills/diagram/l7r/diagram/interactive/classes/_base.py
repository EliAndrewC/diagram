"""The feature-class vocabulary of the interactive map, and what each class tells its reader.

Feature 134 (GM 2026-08-27): a player mousing over the HTML map highlights every feature OF A KIND,
and a click opens a modal that says what the kind is, why it stands where it does, whether that is
historically ACCURATE, a deliberate DEVIATION, a map drawing CONVENTION or a GUESS (constitution XII), and which research
entries it rests on. This PACKAGE is the ONE place the vocabulary lives (a single module until feature 189 - see below):
the engine tags ink with a class KEY (`Settlement.add(..., cls=...)`), the page reads the entry for
every key present on the map, and nothing hamlet-specific is written anywhere - the explanations are
per KIND, not per map.

THE EXPLANATION IS THE DOCSTRING (feature 189, GM 2026-09-05: *"why [is] a modal's explanation stored
in a string constant rather than being stored in a docstring ... the documentation within the code is
literally the documentation that is visible in the user interface"*). Each class is a small Python
class deriving from `Kind`; its docstring carries `What:`, `Why:`, `Note:` and an optional `Caveat:`,
parsed at import into the `FeatureClass` the page reads. Two things follow. The gate's key is the
docstring-stripped AST (`gate-stamp.py semantic_bytes`), so rewording an explanation no longer re-opens
the nine-minute gate: it owes `make page-check` (the registry's tests and the browser test, ~26 s),
which the `page` stamp demands at push. And both caches still see the edit - the generation cache hashes
a class body by its source text and the render fingerprint hashes bytes - so the page regenerates.

The vocabulary is the spec's FR-007 table (`specs/134-interactive-html-map/spec.md`), verbatim:
those rows are the GM's judgment calls, listed so any can be overruled BY NAME. The distinguishing
text is keyed by SIBLING PAIR and is SYMMETRIC (if A names B, B names A - the fidelity review's
round-1 finding), and the page includes a sibling paragraph only when BOTH classes are on the map,
so a hamlet with no woodland commons never claims the windbreak differs from one.

Every explanation is written FROM a `research/` entry and carries that entry's label; where the
record is silent the entry says GUESS in so many words. The record's rule (in its README until the GM retired it,
2026-10-01): "an entry that presents reasoning as a finding is the one failure".

`NOT_HIGHLIGHTED` is the pseudo-class for ink the GM has ruled OUT of highlighting (FR-002:
"judgment calls to make about what things get highlighted and which things do not"). It is a
ruling, not an omission: the census in `page.py` reports only ink that carries NO class at all, so
a `"-"` tag keeps the frame off the report while a forgotten tag still fails the gate.

Research:
    modal vocabulary plumbing - NONE: the FeatureClass, the labels, the lead sentence, the docstring parser
    highlighting rulings - CONVENTION: which ink the page lights on hover, and which it rules out
"""

from __future__ import annotations

import inspect
import re
from dataclasses import dataclass, field
from typing import ClassVar, Literal, cast

from ..content import content

#: The page's fixed phrases and the rulings record - DATA in `assets/page-text.json` (feature 207; see `content.py`).
_TEXT = content("page-text.json")

#: FOUR labels since feature 183 (GM 2026-09-05). The GM's line between the two in the middle, verbatim:
#: a DEVIATION is *"our fictional setting being different from the actual history and historical places
#: it is based on"*; a map drawing CONVENTION is *"rendering glyphs on a map which are differently scaled
#: or differently colored than what the features would be in order to make the map more readable and
#: legible to human eyes."* Until then both wore `deviation`, and the bund beans' modal opened with "This
#: is a deliberate deviation - ... the bead color is a deliberate deviation" - *"But this is not a
#: 'deviation', This is a map rendering convention, and we should distinguish in our write up between
#: these."* A convention's `label_note` is written in the GM's form (see `lead_sentence`).
Label = Literal["accurate", "deviation", "convention", "guess"]

#: The labels the PAGE announces. `accurate` is not among them, and that is the whole of feature 156's
#: first change (GM 2026-08-29): *"I would like to not explicitly say that things are historically
#: accurate when they are because I want the presumption to be that things are always historically
#: accurate unless stated otherwise. In other words, we should call out liberties that we have taken."*
#: A claim made about nearly every feature on the map carries no information; a liberty does. The
#: three-way classification itself is UNCHANGED and still recorded on every class (constitution XII) -
#: only its presentation changed, and it still reaches the page as `data-label`.
ANNOUNCED: frozenset[Label] = frozenset({"deviation", "convention", "guess"})

#: The pseudo-class of ink ruled out of highlighting. Recorded, never wrapped, never reported.
NOT_HIGHLIGHTED = "-"

#: The reserved pseudo-class of the TITLE PLACARD (feature 156). Not a row of `CLASSES` - it is not a
#: kind of feature and has no research entry of its own - but a key the census and the page both know,
#: so the placard is highlightable, clickable, and never reported as ink nobody ruled on. Its modal is
#: built per map by `place.py` from the manifest, the setting's canon and the map's own notes file.
PLACE = "place"

#: Each ruling that put a kind of ink on the not-highlighted list: (what, who, when, why).
NOT_HIGHLIGHTED_RULINGS: tuple[tuple[str, str, str, str], ...] = tuple((what, who, when, why) for what, who, when, why in _TEXT["not_highlighted_rulings"])

#: A ruling that was OVERTURNED, kept beside the list rather than deleted from it - the record should
#: show that a decision was made and then remade, not quietly lose one: (what, who, when, why).
NOT_HIGHLIGHTED_OVERTURNED: tuple[tuple[str, str, str, str], ...] = tuple((what, who, when, why) for what, who, when, why in _TEXT["not_highlighted_overturned"])


@dataclass(frozen=True)
class FeatureClass:
    """One highlightable KIND of thing on the map, and what its modal says."""

    key: str  # the tag the engine writes; also the CSS token (`f-<key>` after slugging)
    name: str  # the class's display name - FR-007's row name, verbatim
    covers: str  # which manifest features it draws - documentation for the next reader
    what: str  # what the thing IS
    why: str  # why it stands where it does on the map
    label: Label | None  # constitution XII: accurate | deviation | convention | guess - None in the About form (feature 319), whose classification is per statement
    label_note: str  # the one line that justifies the label (a deviation says what deviates; a convention says what is drawn otherwise and what the real thing is; a guess says what is silent)
    sources: tuple[str, ...]  # `research/sources/` keys, or ("not recorded",)
    entry: str  # the research/ entry (file + heading) the text was written FROM
    # THE LIBERTY HALF of `label_note`, and only that (feature 156, GM 2026-08-29). An `accurate`
    # class's note usually says two things at once - which parts are READ, and which parts are a
    # drawing convention, a derived number or a sub-guess. The first half is the accuracy claim in
    # other words and the page no longer prints it; the second is exactly what the GM asked to have
    # called out, so it survives, shown AFTER the what and the why instead of ahead of them. Always a
    # verbatim substring of `label_note` (a registry test proves it, so the two cannot drift), and
    # empty both for a class whose note discloses no liberty at all and for every `deviation` or
    # `guess`, whose lead sentence already carries theirs.
    caveat: str = ""
    siblings: dict[str, str] = field(default_factory=dict)  # sibling key -> how THIS class differs from it
    # THE ABOUT FORM (feature 319, GM 2026-10-03: *"we could have an overview tab and a guesses tab and a references tab"*,
    # the first named "About"). `about` is the About tab's paragraphs, `guesses` the Guesses tab's bullets (empty: no tab),
    # `form` which guidelines hold it - `dev/modals.md` (standard) or `dev/modals-particular.md` (particular). An old-form
    # class has `about == ()` and keeps `what`/`why`/`label_note`/`caveat`; the rollout's last task retires that form.
    about: tuple[str, ...] = ()
    guesses: tuple[str, ...] = ()
    form: str = "standard"


_LABEL_WORDS: dict[Label, str] = {cast(Label, label): words for label, words in _TEXT["label_words"].items()}

#: What a convention's lead-in is (feature 183): the GM's own example opens *"Note: we have rendered the
#: bund beans as larger and darker in color than they actually are, in order to make them visible on the
#: map at this this scale. <More information about the actual size and color goes here.>"* - so the note
#: itself is written as that sentence and this is all that precedes it.
CONVENTION_LEAD: str = _TEXT["convention_lead"]


def label_phrase(label: Label) -> str:
    """The words the modal uses for a label - constitution XII's three, in the GM's own phrasing."""
    return _LABEL_WORDS[label]


def lead_sentence(label: Label | None, note: str) -> str:
    """The sentence a modal OPENS with, or "" when there is nothing to announce.

    Only a liberty is announced (`ANNOUNCED`). An `accurate` class returns "" and its modal leads
    with what the feature IS - the presumption of accuracy the GM asked for, which is enforced HERE,
    at the one place the sentence is built, rather than by asking every caller to remember it."""
    if label is None or label not in ANNOUNCED:  # None: the About form, which announces nothing (feature 319)
        return ""
    if label == "convention":
        return CONVENTION_LEAD + note
    return "This is " + _LABEL_WORDS[label] + (" - " + note if note else ".")


def slug(key: str) -> str:
    """The CSS token for a class key: `storage shed` -> `storage-shed`, `karo's house` -> `karo-s-house`.

    EVERY CHARACTER OUTSIDE `[a-z0-9-]` BECOMES A HYPHEN (feature 262). It used to replace spaces only, which was
    enough for the hamlet vocabulary; the first Mode A keys with an apostrophe produced `f-karo's-house`, which the
    raster id map's group pattern does not read - so every such kind silently fell out of the pointer map below
    the raster switch and the ground beneath it answered instead (measured on the Ochiba page: a click inside the
    karo's house opened the inner court). The key itself, on `data-k`, is unchanged."""
    return re.sub(r"[^a-z0-9-]", "-", key.lower())


# ---- the class form (feature 189) -----------------------------------------------------------------

#: The prose tags, then the DATA tags (feature 207: `Name:`, `Covers:`, `Label:`, `Sources:`, `Entry:` moved
#: from class attributes into the docstring, so a relabeling or a repointed research entry is a page-content
#: edit like any rewording - `make page-check`, not the gate; only `key` stays code, being what the engine
#: writes on the ink and what the stylesheet matches).
_TAGS: tuple[str, ...] = ("What", "Why", "Note", "Caveat", "About", "Guesses", "Name", "Covers", "Label", "Sources", "Entry", "Form")
_TAG_LINE = re.compile(r"^(What|Why|Note|Caveat|About|Guesses|Name|Covers|Label|Sources|Entry|Form):\s?(.*)$")
_DATA_TAGS: tuple[str, ...] = ("Name", "Covers", "Label", "Sources", "Entry", "Form")
#: The About form's data tags: `Label:` goes (a guess is a bullet, not the feature's label - `dev/modals.md` M11) and `Form:`
#: is optional (default `standard`).
_ABOUT_DATA_TAGS: tuple[str, ...] = ("Name", "Covers", "Sources", "Entry")
_OLD_PROSE: tuple[str, ...] = ("What", "Why", "Note", "Caveat")
FORMS: frozenset[str] = frozenset({"standard", "particular"})
#: A paragraph break inside `About:` - a blank line, kept (only there) so the About tab has paragraphs (`dev/modals.md` M2).
_PARA = "\n\n"


def parse_explanation(doc: str | None, name: str) -> dict[str, str]:
    """The tagged sections of a `Kind`'s docstring: `What:`, `Why:`, `Note:` and an optional `Caveat:`,
    each tag at the start of a line, each value running to the next tag, wrapped lines joined with one
    space. A missing docstring or a missing required tag raises, naming the class - a registry error is
    loud, never a blank modal (spec 189 FR-001)."""
    if not doc or not doc.strip():
        raise ValueError(f"{name}: the explanation is the docstring, and there is none")
    out: dict[str, list[str]] = {}
    cur: str | None = None
    for raw in inspect.cleandoc(doc).splitlines():
        line = raw.strip()
        m = _TAG_LINE.match(line)
        if m:
            cur = m.group(1)
            out[cur] = [m.group(2)] if m.group(2) else []
            continue
        if not line:
            if cur == "About" and out[cur]:
                out[cur].append("")  # a paragraph break, kept for the About tab
            continue
        if cur is None:
            raise ValueError(f"{name}: text before the first tag ({line[:40]!r}) - every line belongs to What/Why/Note/Caveat or About/Guesses")
        out[cur].append(line)
    got = {k: _join(k, v) for k, v in out.items()}
    required = ("About",) if "About" in got else ("What", "Why", "Note")
    for tag in required:
        if not got.get(tag):
            raise ValueError(f"{name}: the docstring has no {tag}: section")
    return got


def _join(tag: str, lines: list[str]) -> str:
    """One tag's value: wrapped lines joined with one space; `About:` keeps its paragraph breaks and `Guesses:` its
    bullets, one to a line.
    Research: modal vocabulary plumbing - NONE"""
    if tag == "About":
        paras: list[list[str]] = [[]]
        for line in lines:
            if line:
                paras[-1].append(line)
            elif paras[-1]:
                paras.append([])
        return _PARA.join(" ".join(p) for p in paras if p).strip()
    if tag == "Guesses":
        bullets: list[list[str]] = []
        for line in lines:
            if line.startswith("- ") or not bullets:
                bullets.append([line])
            else:
                bullets[-1].append(line)
        return "\n".join(" ".join(b) for b in bullets).strip()
    return " ".join(lines).strip()


def about_paragraphs(text: str) -> tuple[str, ...]:
    """The About tab's paragraphs from a parsed `About:` value.
    Research: modal vocabulary plumbing - NONE"""
    return tuple(" ".join(p.split()) for p in text.split(_PARA) if p.strip())


def guess_bullets(text: str) -> tuple[str, ...]:
    """The Guesses tab's bullets from a parsed `Guesses:` value, each without its `- `.
    Research: modal vocabulary plumbing - NONE"""
    return tuple(line[2:].strip() for line in text.splitlines() if line.strip())


class Kind:
    """Base of every feature class: the DATA as class attributes, the PROSE as the docstring.

    Subclasses register themselves in definition order (`__init_subclass__`), which - with the family
    modules imported in the spec's FR-007 order by `__init__.py` - is `CLASSES`'s insertion order."""

    key: str  # the ONE attribute: the tag the engine writes on the ink, and the CSS token - everything else is in the docstring
    registry: ClassVar[list[type[Kind]]] = []

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Kind.registry.append(cls)

    @classmethod
    def feature(cls) -> FeatureClass:
        """The `FeatureClass` the page reads, built from the class attributes and the parsed docstring."""
        parts = parse_explanation(cls.__doc__, cls.__name__)
        if "About" in parts:
            return _about_feature(cls.__name__, cls.key, parts)
        for tag in _DATA_TAGS:
            if tag == "Form":
                continue
            if not parts.get(tag):
                raise ValueError(f"{cls.__name__}: the docstring has no {tag}: section")
        if parts["Label"] not in _LABEL_WORDS:
            raise ValueError(f"{cls.__name__}: Label: {parts['Label']!r} is not one of {sorted(_LABEL_WORDS)}")
        return FeatureClass(
            key=cls.key,
            name=parts["Name"],
            covers=parts["Covers"],
            what=parts["What"],
            why=parts["Why"],
            label=cast(Label, parts["Label"]),
            label_note=parts["Note"],
            sources=tuple(s.strip() for s in parts["Sources"].split(",") if s.strip()),
            entry=parts["Entry"],
            caveat=parts.get("Caveat", ""),
        )


def _about_feature(name: str, key: str, parts: dict[str, str]) -> FeatureClass:
    """A class in the About form (feature 319): its paragraphs, its guesses, no feature-level label (`dev/modals.md` M11).
    The old prose tags and `Label:` are refused rather than ignored, so a half-converted class fails at import.
    Research: modal vocabulary plumbing - NONE"""
    for tag in _ABOUT_DATA_TAGS:
        if not parts.get(tag):
            raise ValueError(f"{name}: the docstring has no {tag}: section")
    if "Label" in parts:
        raise ValueError(f"{name}: the About form takes no Label: - a guess is a bullet under Guesses: (dev/modals.md M11)")
    old = [t for t in _OLD_PROSE if t in parts]
    if old:
        raise ValueError(f"{name}: the About form replaces What/Why/Note/Caveat - remove {', '.join(t + ':' for t in old)}")
    form = parts.get("Form", "standard")
    if form not in FORMS:
        raise ValueError(f"{name}: Form: {form!r} is not one of {sorted(FORMS)}")
    raw_guesses = parts.get("Guesses", "")
    if raw_guesses and not all(line.startswith("- ") for line in raw_guesses.splitlines()):
        raise ValueError(f"{name}: each guess is a bullet - start every line under Guesses: with '- '")
    return FeatureClass(
        key=key,
        name=parts["Name"],
        covers=parts["Covers"],
        what="",
        why="",
        label=None,
        label_note="",
        sources=tuple(s.strip() for s in parts["Sources"].split(",") if s.strip()),
        entry=parts["Entry"],
        about=about_paragraphs(parts["About"]),
        guesses=guess_bullets(raw_guesses),
        form=form,
    )


def install_siblings(defs: list[FeatureClass], pairs: dict[tuple[str, str], str]) -> dict[str, FeatureClass]:
    """The registry by key, with each sibling pair's text installed in both directions."""
    by_key = {d.key: d for d in defs}
    for (a, b), text in pairs.items():
        if a not in by_key or b not in by_key:
            raise KeyError(f"sibling pair names an unknown class: {(a, b)}")
        by_key[a].siblings[b] = text
        by_key[b].siblings[a] = text
    return by_key
