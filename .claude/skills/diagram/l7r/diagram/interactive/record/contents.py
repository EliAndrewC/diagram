"""The record's vocabulary and its table of contents (feature 303).

The GM, 2026-10-01: group the record by what a question is about and order it by how general it is (*"anything with a
'foundational' tag would get presented before anything with a 'subtype' tag or a 'detail' tag or a 'counts and
measurements' tag"*), with a stable tiebreak (*"running the makefile command twice in a row will never give output HTML
files in two different orders"*), so that regrouping later is *"just a straightforward change"* rather than moving files.

So a question carries TAGS - subjects (the first is primary), settings, one level - from the one vocabulary in
`research/tags.json`, and `research/contents.json` declares the sections, their nesting and order, and a RULE over the
tags saying which questions each takes. A question lives in the first section, depth-first, whose rule matches it; inside
a section the order is level, then identity number. Nothing about grouping or order is written anywhere else: the
builder holds no list of groups (spec FR-009).

Every refusal names the file and the problem, and a run gathers them all.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field

TAGS = "tags.json"
CONTENTS = "contents.json"
FACETS = ("subject", "setting", "level")
#: What a clause of a section's rule may test: the primary subject, any subject, any setting, the level.
CLAUSE_KEYS = ("primary", "subject", "setting", "level")
#: The marker a page states its tags in, on the line after its heading.
MARKER = re.compile(r"<!-- tags: (.*?) -->")
_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class ContentsError(Exception):
    """A refusal about the vocabulary, the contents or a page's tags. Its message names the file."""


@dataclass(frozen=True)
class Tags:
    """A question's tags: its subjects (the first is primary), its settings, its level."""

    subjects: tuple[str, ...]
    settings: tuple[str, ...]
    level: str

    @property
    def primary(self) -> str:
        return self.subjects[0]

    def all(self) -> list[tuple[str, str]]:
        """Every (facet, tag) the question carries - what its tag pages are."""
        return [("subject", s) for s in self.subjects] + [("setting", s) for s in self.settings] + [("level", self.level)]

    def marker(self) -> str:
        return f"<!-- tags: subject={','.join(self.subjects)}; setting={','.join(self.settings)}; level={self.level} -->"


@dataclass(frozen=True)
class Tag:
    id: str
    name: str
    description: str


@dataclass
class Vocabulary:
    subject: dict[str, Tag]
    setting: dict[str, Tag]
    level: list[Tag]

    def facet(self, name: str) -> dict[str, Tag]:
        return {t.id: t for t in self.level} if name == "level" else getattr(self, name)

    def level_rank(self, level: str) -> int:
        return [t.id for t in self.level].index(level)


@dataclass
class Section:
    """A section of the table of contents: what it is called, what it says in each half (the research, and how our maps
    draw it), the rule it takes questions by, and its subsections. `takes` empty is a container of subsections."""

    id: str
    title: str
    description: str
    drawing_description: str
    takes: list[dict[str, list[str]]]
    sections: list[Section] = field(default_factory=list)
    parent: Section | None = None

    def path(self) -> list[Section]:
        """This section and its ancestors, outermost first."""
        out: list[Section] = []
        at: Section | None = self
        while at is not None:
            out.insert(0, at)
            at = at.parent
        return out


def _read_json(record_dir: str, name: str) -> object:
    path = os.path.join(record_dir, name)
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except OSError:
        raise ContentsError(f"{name}: missing - the record's {'vocabulary' if name == TAGS else 'table of contents'} is a file, and the build will not invent it") from None
    except json.JSONDecodeError as e:
        raise ContentsError(f"{name}: not JSON ({e})") from None


def _tag(name: str, facet: str, tid: str, body: object) -> Tag:
    if not _ID.match(tid) or not isinstance(body, dict) or not isinstance(body.get("name"), str):
        raise ContentsError(f"{name}: {facet} `{tid}` - a tag is a lower-case id with a `name` and a `description`")
    return Tag(tid, body["name"], str(body.get("description", "")))


def load_vocabulary(record_dir: str) -> Vocabulary:
    """`tags.json`: every tag of the three facets. Levels are a list, because their order is the presentation order."""
    data = _read_json(record_dir, TAGS)
    if not isinstance(data, dict) or set(data) != set(FACETS):
        raise ContentsError(f"{TAGS}: holds exactly the facets {', '.join(FACETS)}")
    subject = {k: _tag(TAGS, "subject", k, v) for k, v in data["subject"].items()}
    setting = {k: _tag(TAGS, "setting", k, v) for k, v in data["setting"].items()}
    if not isinstance(data["level"], list) or not data["level"]:
        raise ContentsError(f"{TAGS}: `level` is a list, in presentation order")
    level = [_tag(TAGS, "level", str(x.get("id", "")) if isinstance(x, dict) else "", x) for x in data["level"]]
    return Vocabulary(subject, setting, level)


def _clause(where: str, raw: object, vocab: Vocabulary) -> dict[str, list[str]]:
    if not isinstance(raw, dict) or not raw:
        raise ContentsError(f"{where}: a clause is an object of {', '.join(CLAUSE_KEYS)}")
    out: dict[str, list[str]] = {}
    for key, value in raw.items():
        if key not in CLAUSE_KEYS:
            raise ContentsError(f"{where}: `{key}` - a clause tests only {', '.join(CLAUSE_KEYS)}")
        values = [value] if isinstance(value, str) else value
        facet = "subject" if key in ("primary", "subject") else key
        known = vocab.facet(facet)
        for v in values:
            if v not in known:
                raise ContentsError(f"{where}: `{key}: {v}` - no {facet} tag `{v}` in {TAGS}")
        out[key] = list(values)
    return out


def _section(raw: object, vocab: Vocabulary, parent: Section | None, seen: set[str]) -> Section:
    if not isinstance(raw, dict) or not _ID.match(str(raw.get("id", ""))):
        raise ContentsError(f"{CONTENTS}: a section is an object with a lower-case `id`")
    sid = raw["id"]
    where = f"{CONTENTS} section `{sid}`"
    if sid in seen:
        raise ContentsError(f"{where}: the id is used twice")
    seen.add(sid)
    if not isinstance(raw.get("title"), str) or not raw["title"]:
        raise ContentsError(f"{where}: no `title`")
    takes = [_clause(where, c, vocab) for c in raw.get("takes", [])]
    section = Section(sid, raw["title"], str(raw.get("description", "")), str(raw.get("drawing_description", "")), takes, parent=parent)
    section.sections = [_section(s, vocab, section, seen) for s in raw.get("sections", [])]
    if not section.takes and not section.sections:
        raise ContentsError(f"{where}: takes nothing and holds nothing")
    return section


def load_contents(record_dir: str, vocab: Vocabulary) -> list[Section]:
    """`contents.json`: the sections in order, each rule checked against the vocabulary."""
    data = _read_json(record_dir, CONTENTS)
    if not isinstance(data, dict) or not isinstance(data.get("sections"), list):
        raise ContentsError(f"{CONTENTS}: an object with a `sections` list")
    seen: set[str] = set()
    return [_section(s, vocab, None, seen) for s in data["sections"]]


def walk(sections: list[Section]) -> list[Section]:
    """Every section, depth-first in contents order - the order a question's home is looked for in."""
    out: list[Section] = []
    for s in sections:
        out.append(s)
        out += walk(s.sections)
    return out


def matches(clause: dict[str, list[str]], tags: Tags) -> bool:
    """Does one clause match: every key it tests."""
    for key, values in clause.items():
        have = {"primary": [tags.primary], "subject": list(tags.subjects), "setting": list(tags.settings), "level": [tags.level]}[key]
        if not set(values) & set(have):
            return False
    return True


def takes(section: Section, tags: Tags) -> bool:
    return any(matches(c, tags) for c in section.takes)


def home(sections: list[Section], tags: Tags) -> Section | None:
    """The first section, depth-first, whose rule takes these tags (spec FR-010)."""
    return next((s for s in walk(sections) if takes(s, tags)), None)


def parse_tags(text: str, where: str, vocab: Vocabulary) -> Tags | None:
    """The tags a page states in its marker, checked against the vocabulary; None if it states none. Refuses a marker
    with a facet missing, repeated or unknown, two levels, or a tag not in the vocabulary (spec FR-007)."""
    found = MARKER.findall(text)
    if not found:
        return None
    if len(found) > 1:
        raise ContentsError(f"{where}: two tags markers")
    parts: dict[str, list[str]] = {}
    for chunk in found[0].split(";"):
        key, eq, value = chunk.strip().partition("=")
        if not eq or key not in FACETS or key in parts:
            raise ContentsError(f"{where}: `{chunk.strip()}` - the marker is `subject=a,b; setting=x; level=y`, each facet once")
        parts[key] = [v.strip() for v in value.split(",") if v.strip()]
    for facet in FACETS:
        if not parts.get(facet):
            raise ContentsError(f"{where}: no {facet} in its tags")
        known = vocab.facet(facet)
        for v in parts[facet]:
            if v not in known:
                raise ContentsError(f"{where}: `{facet}={v}` - no such tag in {TAGS}")
        if len(set(parts[facet])) != len(parts[facet]):
            raise ContentsError(f"{where}: a {facet} tag is stated twice")
    if len(parts["level"]) != 1:
        raise ContentsError(f"{where}: {len(parts['level'])} levels - a question has exactly one")
    return Tags(tuple(parts["subject"]), tuple(parts["setting"]), parts["level"][0])


def idle_rules(sections: list[Section], every: list[Tags]) -> list[str]:
    """A message for each clause that matches no question at all - a typo, not a regrouping (spec FR-010). A section
    whose matches were all homed earlier is not here: it is empty, and the build omits it."""
    bad = []
    for s in walk(sections):
        for c in s.takes:
            if not any(matches(c, t) for t in every):
                bad.append(f"{CONTENTS} section `{s.id}`: the clause {json.dumps(c, sort_keys=True)} matches no question")
    return bad
