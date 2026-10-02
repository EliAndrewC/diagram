"""The registry's source tags and the sections they group the works into (feature 305).

The GM, 2026-10-02: tag the sources so the works are *"put into sections based on their tags, like `Present day` or
`Premodern Japan` or `Premodern China` or `Modern preindustrial`"*, and let the assembly apply *"the correct labels with
... tooltips to convey the standardized explanation of the strengths and limitations inherent to the category of
source, in addition to the specific explanation"* - so a write-up no longer repeats its category's limits.

So every keyed work states its tags in a marker on its entry's last line,
`<!-- tags: period=a[,b]; region=x; kind=k -->` (the grammar feature 303 gave questions; last, because the citation
line is read as the paragraph straight after the heading - specs/305-source-tags/research.md R6). The FIRST value of a
facet is primary. `research/source-tags.json` holds every value with its label and its standard explanation, and
`research/source-sections.json` the sections in order, each with a rule over a work's primary tags: a work lives in the
first section whose rule takes it. The GM's own campaign notes are canon, not evidence: they carry no tags, one fixed
label, and the section marked `canon`. Nothing about grouping or wording is written anywhere else.

Every refusal names the file and the problem, and a build gathers them all (spec FR-010).
"""

from __future__ import annotations

import html
import json
import os
import re
from dataclasses import dataclass

VOCABULARY = "source-tags.json"
SECTIONS = "source-sections.json"
FACETS = ("period", "region", "kind")
#: The marker an entry states its tags in, on its last line.
MARKER = re.compile(r"\n?<!-- tags: (.*?) -->[ \t]*")
#: A section id's prefix, so no section heading can collide with a registry key in the one-page record.
SECTION_PREFIX = "works-"
_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class SourceTagError(Exception):
    """A refusal about the source vocabulary or the sections file. Its message names the file."""


@dataclass(frozen=True)
class Label:
    id: str
    name: str
    description: str


@dataclass(frozen=True)
class SourceTags:
    """A work's tags, each facet's values in order, the first primary."""

    period: tuple[str, ...]
    region: tuple[str, ...]
    kind: tuple[str, ...]

    def values(self, facet: str) -> tuple[str, ...]:
        return getattr(self, facet)

    def primary(self, facet: str) -> str:
        return self.values(facet)[0]

    def marker(self) -> str:
        return "<!-- tags: " + "; ".join(f"{f}={','.join(self.values(f))}" for f in FACETS) + " -->"


@dataclass
class Vocabulary:
    facets: dict[str, list[Label]]
    canon: Label

    def known(self, facet: str) -> dict[str, Label]:
        return {lab.id: lab for lab in self.facets[facet]}


@dataclass(frozen=True)
class Section:
    """A works section: its heading, its description, and the clauses it takes works by (none for the canon one)."""

    id: str
    title: str
    description: str
    canon: bool
    takes: tuple[dict[str, tuple[str, ...]], ...]


def _read_json(record_dir: str, name: str) -> object:
    path = os.path.join(record_dir, name)
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except OSError:
        raise SourceTagError(f"{name}: missing - the record's source {'vocabulary' if name == VOCABULARY else 'sections'} is a file, and the build will not invent it") from None
    except json.JSONDecodeError as e:
        raise SourceTagError(f"{name}: not JSON ({e})") from None


def _label(where: str, raw: object) -> Label:
    if not isinstance(raw, dict) or not _ID.match(str(raw.get("id", ""))) or not isinstance(raw.get("name"), str) or not isinstance(raw.get("description"), str):
        raise SourceTagError(f"{where}: a value is an object with a lower-case `id`, a `name` and a `description`")
    return Label(raw["id"], raw["name"], raw["description"])


def load_vocabulary(record_dir: str) -> Vocabulary:
    """`source-tags.json`: each facet a list of values in the order their labels show, and the canon label."""
    data = _read_json(record_dir, VOCABULARY)
    if not isinstance(data, dict) or set(data) != {*FACETS, "canon"}:
        raise SourceTagError(f"{VOCABULARY}: holds exactly {', '.join(FACETS)} and canon")
    facets: dict[str, list[Label]] = {}
    for facet in FACETS:
        if not isinstance(data[facet], list) or not data[facet]:
            raise SourceTagError(f"{VOCABULARY}: `{facet}` is a non-empty list, in the order its labels show")
        facets[facet] = [_label(f"{VOCABULARY} {facet}", v) for v in data[facet]]
        ids = [lab.id for lab in facets[facet]]
        if len(set(ids)) != len(ids):
            raise SourceTagError(f"{VOCABULARY}: a {facet} value is declared twice")
    return Vocabulary(facets, _label(f"{VOCABULARY} canon", data["canon"]))


def _clause(where: str, raw: object, vocab: Vocabulary) -> dict[str, tuple[str, ...]]:
    if not isinstance(raw, dict) or not raw:
        raise SourceTagError(f"{where}: a clause is an object of {', '.join(FACETS)}")
    out: dict[str, tuple[str, ...]] = {}
    for facet, value in raw.items():
        if facet not in FACETS:
            raise SourceTagError(f"{where}: `{facet}` - a clause tests only {', '.join(FACETS)}")
        values = (value,) if isinstance(value, str) else tuple(value)
        for v in values:
            if v not in vocab.known(facet):
                raise SourceTagError(f"{where}: `{facet}: {v}` - no {facet} value `{v}` in {VOCABULARY}")
        out[facet] = values
    return out


def load_sections(record_dir: str, vocab: Vocabulary) -> list[Section]:
    """`source-sections.json`: the sections in order, each rule checked against the vocabulary; exactly one canon."""
    data = _read_json(record_dir, SECTIONS)
    if not isinstance(data, dict) or not isinstance(data.get("sections"), list):
        raise SourceTagError(f"{SECTIONS}: an object with a `sections` list")
    out: list[Section] = []
    for raw in data["sections"]:
        sid = str(raw.get("id", "")) if isinstance(raw, dict) else ""
        if not isinstance(raw, dict) or not _ID.match(sid) or not sid.startswith(SECTION_PREFIX):
            raise SourceTagError(f"{SECTIONS}: a section is an object with a lower-case `id` starting `{SECTION_PREFIX}`")
        where = f"{SECTIONS} section `{sid}`"
        if any(s.id == sid for s in out):
            raise SourceTagError(f"{where}: the id is used twice")
        if not isinstance(raw.get("title"), str) or not raw["title"]:
            raise SourceTagError(f"{where}: no `title`")
        canon = raw.get("canon") is True
        takes = tuple(_clause(where, c, vocab) for c in raw.get("takes", []))
        if canon == bool(takes):
            raise SourceTagError(f"{where}: a section takes works by clauses, or is the canon section with none - not both, not neither")
        out.append(Section(sid, raw["title"], str(raw.get("description", "")), canon, takes))
    if sum(s.canon for s in out) != 1:
        raise SourceTagError(f"{SECTIONS}: exactly one section is the canon section")
    return out


def parse(text: str, where: str, vocab: Vocabulary) -> SourceTags | None:
    """The tags an entry states, checked against the vocabulary; None if it states none. Refuses two markers, a facet
    missing, repeated or unknown, a value stated twice, or a value not in the vocabulary (naming the allowed ones)."""
    found = MARKER.findall(text)
    if not found:
        return None
    if len(found) > 1:
        raise SourceTagError(f"{where}: two tags markers")
    parts: dict[str, list[str]] = {}
    for chunk in found[0].split(";"):
        key, eq, value = chunk.strip().partition("=")
        if not eq or key not in FACETS or key in parts:
            raise SourceTagError(f"{where}: `{chunk.strip()}` - the marker is `period=a; region=x,y; kind=k`, each facet once")
        parts[key] = [v.strip() for v in value.split(",") if v.strip()]
    for facet in FACETS:
        if not parts.get(facet):
            raise SourceTagError(f"{where}: no {facet} in its tags")
        known = vocab.known(facet)
        for v in parts[facet]:
            if v not in known:
                raise SourceTagError(f"{where}: `{facet}={v}` - not a {facet} value; the values are {', '.join(known)} ({VOCABULARY})")
        if len(set(parts[facet])) != len(parts[facet]):
            raise SourceTagError(f"{where}: a {facet} value is stated twice")
    return SourceTags(tuple(parts["period"]), tuple(parts["region"]), tuple(parts["kind"]))


def takes(section: Section, tags: SourceTags) -> bool:
    """Does any clause of the section take these tags: every facet a clause names matches the primary value."""
    return any(all(tags.primary(f) in values for f, values in clause.items()) for clause in section.takes)


def home(sections: list[Section], tags: SourceTags | None) -> Section | None:
    """The section a work lives in: the canon section for a canon work (`tags` None), else the first that takes it."""
    if tags is None:
        return next(s for s in sections if s.canon)
    return next((s for s in sections if not s.canon and takes(s, tags)), None)


def strip_marker(entry_html: str) -> str:
    """An entry as the reader sees it: without its tags marker."""
    return MARKER.sub("", entry_html)


def _chip(facet: str, label: Label) -> str:
    text = html.escape(label.description, quote=True)
    return f'<span class="srctag srctag-{facet}" data-def="{text}" title="{text}">{html.escape(label.name)}</span>'


def labels_html(tags: SourceTags | None, vocab: Vocabulary) -> str:
    """A work's labels, one per value in facet order (the canon label alone for a canon work), each carrying its
    standard explanation - shown in the record's tooltip box on hover, and as the native tooltip without scripts."""
    if tags is None:
        chips = [_chip("canon", vocab.canon)]
    else:
        chips = [_chip(f, vocab.known(f)[v]) for f in FACETS for v in tags.values(f)]
    return '<p class="srctags">' + " ".join(chips) + "</p>"


def section_heading(section: Section, level: int, anchor: str) -> str:
    """A section's heading in a list of works, with its description beneath."""
    desc = f'\n<p class="works-section-desc"><em>{section.description}</em></p>' if section.description else ""
    return f'<h{level} class="works-section" id="{anchor}">{html.escape(section.title)}</h{level}>{desc}'


#: The markers of the vocabulary block derived into the `source-applicability` contract (spec FR-012): a defined agent
#: launches without the record's CLAUDE.md files, so the explanations it judges against are written into its contract,
#: derived from the one vocabulary by `make source-tags-contract` and held current by a test.
CONTRACT_OPEN = "<!-- source-tags: DERIVED by make source-tags-contract from research/source-tags.json - edit the vocabulary, never here -->"
CONTRACT_CLOSE = "<!-- /source-tags -->"


def contract_block(vocab: Vocabulary) -> str:
    """Every value and its explanation, as the contract lists them, between the markers."""
    rows = [f"- `{f}={lab.id}` - **{lab.name}**: {lab.description}" for f in FACETS for lab in vocab.facets[f]]
    rows.append(f"- (no marker) - **{vocab.canon.name}**: {vocab.canon.description}")
    return CONTRACT_OPEN + "\n" + "\n".join(rows) + "\n" + CONTRACT_CLOSE


def synced_contract(text: str, vocab: Vocabulary) -> str:
    """`text` with its derived block rewritten from the vocabulary; refused when the markers are missing."""
    start, end = text.find(CONTRACT_OPEN), text.find(CONTRACT_CLOSE)
    if start < 0 or end < start:
        raise SourceTagError("the contract has no derived source-tags block - its two markers are missing")
    return text[:start] + contract_block(vocab) + text[end + len(CONTRACT_CLOSE) :]


class Catalog:
    """Every registry entry's tags and section, read once per build. `errors` holds every refusal, each naming its
    entry, so one build names them all; an entry refused has no section and is left out of every list."""

    def __init__(self, record_dir: str, entries: dict[str, str], canon: set[str], where: str) -> None:
        self.vocab = load_vocabulary(record_dir)
        self.sections = load_sections(record_dir, self.vocab)
        self.tags: dict[str, SourceTags | None] = {}
        self.section: dict[str, Section] = {}
        self.errors: list[str] = []
        for key, text in entries.items():
            at = f"{where}/ {key}"
            try:
                tags = parse(text, at, self.vocab)
            except SourceTagError as e:
                self.errors.append(str(e))
                continue
            if key in canon:
                if tags is not None:
                    self.errors.append(f"{at}: a canon entry (the GM's own notes) carries no tags - remove its marker")
                    continue
            elif tags is None:
                self.errors.append(f"{at}: no tags - every keyed work states `<!-- tags: period=...; region=...; kind=... -->` on its last line ({VOCABULARY})")
                continue
            sec = home(self.sections, tags)
            if sec is None:
                assert tags is not None
                combo = ", ".join(f"{f}={tags.primary(f)}" for f in FACETS)
                self.errors.append(f"{at}: no section of {SECTIONS} takes the primary tags {combo}")
                continue
            self.tags[key], self.section[key] = tags, sec

    def labels(self, key: str) -> str:
        return labels_html(self.tags[key], self.vocab) if key in self.section else ""

    def grouped(self, keys: list[str]) -> list[tuple[Section, list[str]]]:
        """`keys` under their sections in the sections' order, each keeping the order it was given; an empty section
        and a refused key are left out."""
        return [(s, [k for k in keys if self.section.get(k) is s]) for s in self.sections if any(self.section.get(k) is s for k in keys)]
