"""The feature-class vocabulary of the interactive map, and what each class tells its reader.

Feature 134 (GM 2026-08-27): a player mousing over the HTML map highlights every feature OF A KIND,
and a click opens a modal that says what the kind is, why it stands where it does, whether that is
historically ACCURATE, a deliberate DEVIATION, a map drawing CONVENTION or a GUESS (constitution XII), and which research
entries it rests on. This PACKAGE is the ONE place the vocabulary lives (a single module until feature 189 - see below):
the engine tags ink with a class KEY (`Settlement.add(..., cls=...)`), the page reads the entry for
every key present on the map, and nothing hamlet-specific is written anywhere - the explanations are
per KIND, not per map.

THE EXPLANATION IS A TAGGED TEXT, ONE FILE PER KIND (feature 189 made it the docstring; feature 319, plan D12, moved it
to `assets/modals/`): `About:` paragraphs, an optional `Guesses:` list, an optional `Depiction:` and `Drawing:`, then the
data tags `Name:` / `Covers:` / `Sources:` / `Entry:` and an optional `Form:`, parsed into the `FeatureClass` the page
reads. Page content, not engine: an edit owes `make page-check`, not the gate.

The vocabulary is the spec's FR-007 table (`specs/134-interactive-html-map/spec.md`), verbatim:
those rows are the GM's judgment calls, listed so any can be overruled BY NAME. The distinguishing
text is keyed by SIBLING PAIR and is SYMMETRIC (if A names B, B names A - the fidelity review's
round-1 finding), and the page includes a sibling paragraph only when BOTH classes are on the map,
so a hamlet with no woodland commons never claims the windbreak differs from one.

Every explanation is written FROM a `research/` entry. Constitution XII's classification is PER STATEMENT (feature 319,
`dev/modals.md` M11-M13): a guess is a Guesses bullet, a deviation is said in the About text, a convention on the Depiction
tab. The class-level label, its lead sentence and the caveat (features 156, 183) were retired with the old
`What:`/`Why:`/`Note:`/`Caveat:` form; those tags and `Label:` are refused by name, so a stale file fails at import.

`NOT_HIGHLIGHTED` is the pseudo-class for ink the GM has ruled OUT of highlighting (FR-002:
"judgment calls to make about what things get highlighted and which things do not"). It is a
ruling, not an omission: the census in `page.py` reports only ink that carries NO class at all, so
a `"-"` tag keeps the frame off the report while a forgotten tag still fails the gate.

Research:
    modal vocabulary plumbing - NONE: the FeatureClass and the modal text's parser
    highlighting rulings - CONVENTION: which ink the page lights on hover, and which it rules out
"""

from __future__ import annotations

import inspect
import os
import re

from .. import conditions
from dataclasses import dataclass, field
from typing import ClassVar

from ..content import content

#: The page's fixed phrases and the rulings record - DATA in `assets/page-text.json` (feature 207; see `content.py`).
_TEXT = content("page-text.json")

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
    sources: tuple[str, ...]  # `research/sources/` keys, or ("not recorded",)
    entry: str  # the research/ entry (file + heading) the text was written FROM
    siblings: dict[str, str] = field(default_factory=dict)  # sibling key -> how THIS class differs from it
    # THE ABOUT FORM (feature 319, GM 2026-10-03: *"we could have an overview tab and a guesses tab and a references tab"*,
    # the first named "About"). `about` is the About tab's paragraphs, `guesses` the Guesses tab's bullets (empty: no tab),
    # `form` which guidelines hold it - `dev/modals.md` (standard) or `dev/modals-particular.md` (particular). There is no
    # class-level label: the classification is per statement (`dev/modals.md` M11-M13).
    about: tuple[str, ...] = ()
    guesses: tuple[str, ...] = ()
    form: str = "standard"
    # THE DEPICTION TAB (feature 319 plan D13, GM 2026-10-04): how the map draws the thing - its paragraphs, and the "how our
    # maps draw it" pages it rests on (`Drawing:`, in the form `Entry:` takes), which leave the References tab
    depiction: tuple[str, ...] = ()
    drawing: str = ""


def slug(key: str) -> str:
    """The CSS token for a class key: `storage shed` -> `storage-shed`, `karo's house` -> `karo-s-house`.

    EVERY CHARACTER OUTSIDE `[a-z0-9-]` BECOMES A HYPHEN (feature 262). It used to replace spaces only, which was
    enough for the hamlet vocabulary; the first Mode A keys with an apostrophe produced `f-karo's-house`, which the
    raster id map's group pattern does not read - so every such kind silently fell out of the pointer map below
    the raster switch and the ground beneath it answered instead (measured on the Ochiba page: a click inside the
    karo's house opened the inner court). The key itself, on `data-k`, is unchanged."""
    return re.sub(r"[^a-z0-9-]", "-", key.lower())


# ---- the class form (feature 189) -----------------------------------------------------------------

#: The prose tags, then the DATA tags (feature 207: the data moved from class attributes into the text, so a repointed
#: research entry is a page-content edit like any rewording - `make page-check`, not the gate; only `key` stays code, being
#: what the engine writes on the ink and what the stylesheet matches).
_TAGS: tuple[str, ...] = ("About", "Guesses", "Depiction", "Name", "Covers", "Sources", "Entry", "Drawing", "Form")
_DATA_TAGS: tuple[str, ...] = ("Name", "Covers", "Sources", "Entry", "Drawing", "Form")
#: THE RETIRED TAGS (feature 319): the old form's prose and its class-level label. Still recognized so a file that carries
#: one is REFUSED by name, never read as part of the paragraph above it - don't drop them from the pattern, because an
#: unrecognized `Why:` line would silently join the About text.
_RETIRED: tuple[str, ...] = ("What", "Why", "Note", "Caveat", "Label")
_TAG_LINE = re.compile(r"^(" + "|".join(_TAGS + _RETIRED) + r"):\s?(.*)$")
#: the tags whose blank lines are paragraph breaks (the About and Depiction tabs)
_PARAGRAPHED: frozenset[str] = frozenset({"About", "Depiction"})
#: The required data tags; `Form:` is optional (default `standard`) and `Drawing:` too (plan D13).
_ABOUT_DATA_TAGS: tuple[str, ...] = ("Name", "Covers", "Sources", "Entry")
FORMS: frozenset[str] = frozenset({"standard", "particular"})
#: A paragraph break inside `About:` - a blank line, kept (only there) so the About tab has paragraphs (`dev/modals.md` M2).
_PARA = "\n\n"


def parse_explanation(doc: str | None, name: str) -> dict[str, str]:
    """The tagged sections of a modal's text (`_TAGS`), each tag at the start of a line, each value running to the next
    tag, wrapped lines joined with one space. A missing text or a missing `About:` raises, naming the class - a registry
    error is loud, never a blank modal (spec 189 FR-001)."""
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
            if cur in _PARAGRAPHED and out[cur]:
                out[cur].append("")  # a paragraph break, kept for the About tab
            continue
        if cur is None:
            raise ValueError(f"{name}: text before the first tag ({line[:40]!r}) - every line belongs to a tag, About: first")
        out[cur].append(line)
    got = {k: _join(k, v) for k, v in out.items()}
    if not got.get("About"):
        raise ValueError(f"{name}: the docstring has no About: section")
    return got


def _join(tag: str, lines: list[str]) -> str:
    """One tag's value: wrapped lines joined with one space; `About:` keeps its paragraph breaks and `Guesses:` its
    bullets, one to a line.
    Research: modal vocabulary plumbing - NONE"""
    if tag in _PARAGRAPHED:
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


#: WHERE A MODAL'S TEXT LIVES (feature 319, plan D12, GM 2026-10-03: *"Yes, I agree with that. So please go ahead and make
#: that change now"*): one file per kind, `assets/modals/<hamlet|sheet>/<slug of its key>.md`, in the docstring's tagged form.
#: It was the class docstring (feature 189); editing one modal then meant reading a module of 14 to 27, and a check could not
#: quote a docstring's line breaks. Under `assets/` the text is page content - gate-stamp's `page` area, the render
#: fingerprint, a gen child's recorded reads - exactly as the glossary is.
MODALS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "modals")


def modal_path(module: str, key: str) -> str:
    """The modal file of the kind `key` defined in `module`: a Mode A sheet's kinds (`compound_kinds`) under `sheet/`, the
    hamlet vocabulary under `hamlet/` - two registries, so a sheet's `well` and a hamlet's `well` are two files.
    Research: modal vocabulary plumbing - NONE"""
    registry = "sheet" if ".compound_kinds" in module else "hamlet"
    return os.path.join(MODALS_DIR, registry, slug(key) + ".md")


def modal_text(cls: type) -> str | None:
    """A kind's modal text: its file, or - for a class with no file, a test's probe - its docstring.
    Research: modal vocabulary plumbing - NONE"""
    path = modal_path(cls.__module__, getattr(cls, "key", ""))
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    return cls.__doc__


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
        return _about_feature(cls.__name__, cls.key, parse_explanation(modal_text(cls), cls.__name__))


#: THE OLDER MAPS ARE NEVER MENTIONED (the GM, 2026-10-04, of the garden's "Except on the older hand-drawn maps": *"by the time
#: any one other than me looks at these, then those older hand-drawn maps will no longer exist. They will have all been replaced
#: by scripted maps ... that can probably be a mechanical check"*). The ways a write-up has named them: older, earlier, legacy,
#: frozen or hand-drawn/-authored MAPS, and the frozen or legacy POOL. A sheet's "hand-drawn plans" are building plans, which
#: stay, so the pattern wants "map" or "pool"; `dev/modals.md` M21.
OLDER_MAPS = re.compile(r"\b(?:older|earlier|legacy|frozen|hand[- ](?:drawn|authored|made))\b(?:[ -]\w+){0,2}[ -](?:maps?|pool)\b", re.I)
"""Research: older maps unmentioned - NONE"""


def _about_feature(name: str, key: str, parts: dict[str, str]) -> FeatureClass:
    """A kind's `FeatureClass` from its parsed text (feature 319): its paragraphs, its guesses, no feature-level label
    (`dev/modals.md` M11). The retired tags are refused rather than ignored, so a stale file fails at import.
    Research: modal vocabulary plumbing - NONE"""
    for tag in _ABOUT_DATA_TAGS:
        if not parts.get(tag):
            raise ValueError(f"{name}: the docstring has no {tag}: section")
    if "Label" in parts:
        raise ValueError(f"{name}: the About form takes no Label: - a guess is a bullet under Guesses: (dev/modals.md M11)")
    old = [t for t in _RETIRED if t in parts and t != "Label"]
    if old:
        raise ValueError(f"{name}: the About form replaces What/Why/Note/Caveat - remove {', '.join(t + ':' for t in old)}")
    form = parts.get("Form", "standard")
    if form not in FORMS:
        raise ValueError(f"{name}: Form: {form!r} is not one of {sorted(FORMS)}")
    if ".drawing.html" in parts["Entry"]:
        raise ValueError(f"{name}: a 'how our maps draw it' page belongs under Drawing:, not Entry: (the Depiction tab - dev/modals.md D-rules)")
    for tag in ("About", "Guesses", "Depiction"):
        hit = OLDER_MAPS.search(parts.get(tag, ""))
        if hit:
            raise ValueError(f"{name}: {tag}: names the older maps ({hit.group(0)!r}) - they will all be scripted before anyone else reads this; say what the scripted maps do and drop the exception (dev/modals.md M21)")
    raw_guesses = parts.get("Guesses", "")
    if raw_guesses and not all(line.startswith("- ") for line in raw_guesses.splitlines()):
        raise ValueError(f"{name}: each guess is a bullet - start every line under Guesses: with '- '")
    # A KNOB CONDITION (FR-015, plan D14) opens an item: its form is checked here, its knob and values when a page is written
    for item in (*about_paragraphs(parts["About"]), *about_paragraphs(parts.get("Depiction", "")), *guess_bullets(raw_guesses)):
        try:
            conditions.split(item)
        except ValueError as err:
            raise ValueError(f"{name}: {err}") from None
    return FeatureClass(
        key=key,
        name=parts["Name"],
        covers=parts["Covers"],
        sources=tuple(s.strip() for s in parts["Sources"].split(",") if s.strip()),
        entry=parts["Entry"],
        about=about_paragraphs(parts["About"]),
        depiction=about_paragraphs(parts.get("Depiction", "")),
        drawing=parts.get("Drawing", ""),
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
