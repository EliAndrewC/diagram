#!/usr/bin/env python3
"""The one-time flattening of the research record (feature 303) - deleted once it has run and landed.

The GM, 2026-10-01: the topic directories go (*"are we actually getting anything out of having a directory called
cities? Or is that just literally confusing things?"*), every question gets one stem with a number of its own, and the
record is grouped by tags. This script moves every question out of its page directory into `research/questions/`,
rewrites every link inside the record by resolving it with the OLD link index (so nothing is rewritten by guesswork,
spec research R4), writes the tags each question was given (the tagging pass, R8), and writes the mapping the pointer
sweep and the pointer check read (`research/moved-303.json`).

    _record_flatten.py --root <repo> --tags <tags.tsv> [--dry-run]

It refuses to run twice (there must be no `research/questions/` yet) and refuses, before writing anything, on any link
it cannot resolve, any question with no tags, or any note it cannot place.
"""

from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import shutil
import sys
from dataclasses import dataclass, field

SKILL = ".claude/skills/diagram"
SETTING_ORDER = ("countryside", "town", "city")
#: The part a page directory was, as the section its questions mostly became - for whole-page pointers and openings.
PART_SECTION = {
    "archetypes": "field-archetypes",
    "buildings": "compounds",
    "fields": "fields",
    "homesteads": "homesteads",
    "presentation": "map-conventions",
    "religion-and-death": "religion-and-the-dead",
    "settlements": "tiers",
    "towns": "towns",
    "urban-features": "trades-and-services",
    "vegetation": "vegetation",
    "water": "water",
    "ways": "ways",
    "cities": "cities",
    "cities/capitals": "capitals",
    "cities/defenses": "city-defenses",
    "cities/fabric": "urban-fabric",
    "cities/government": "government",
    "cities/hinterland": "outside-the-walls",
    "cities/river-cities": "river-cities",
    "cities/sizing": "city-sizing",
}
CONVENTION_PARTS = ("presentation",)
_ATTR = re.compile(r'(<(?:a|img)\b[^>]*?\s(?:href|src)=")([^"]*)(")', re.S)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_ABOUT_OLD = re.compile(r"\n?<!-- about: ((?:[a-z-]+/)?[a-z-]+\.html)#([^\s]+) -->")
_H2_END = re.compile(r"</h2>")
_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)
_REF = re.compile(r'<sup class="fn" data-note="([^"]*)"></sup>')
_NOTE = re.compile(r'<li data-note="([^"]+)">.*?</li>\n?', re.S)
_ORIG = re.compile(r'<li data-orig="([^"#]+)#\d+">.*?</li>\n?', re.S)
_P_EM = re.compile(r"^\s*<p><em>(.*)</em></p>\s*$", re.S)


@dataclass
class Old:
    """One question page as it was."""

    part: str  # `fields`, `cities/defenses`, `rendering/fields`
    file: str  # `010-x.html`
    heading_id: str
    text: str
    drawing: bool
    about: tuple[str, str] | None = None  # (research page_rel, research heading id)

    @property
    def path(self) -> str:
        return f"{self.part}/{self.file}"

    @property
    def page_rel(self) -> str:
        return f"{self.part}.html"

    @property
    def prefix(self) -> str:
        return self.file.split("-", 1)[0]


@dataclass
class Stem:
    research: Old | None
    drawing: Old | None = None
    about: Stem | None = None
    tags: dict[str, list[str]] = field(default_factory=dict)
    convention: str = ""
    number: int = 0

    @property
    def owner(self) -> Old:
        page = self.research or self.drawing
        assert page is not None
        return page

    @property
    def name(self) -> str:
        return f"{self.number:04d}-{self.owner.heading_id}"


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _questions(record: str) -> list[Old]:
    """Every question fragment of every page directory, with its heading id and (a drawing page's) `about:`."""
    sys.path.insert(0, os.path.join(record, ".."))
    from l7r.diagram.interactive.record import fragments as frag  # noqa: PLC0415
    from l7r.diagram.interactive.record.store import record_pages  # noqa: PLC0415

    out = []
    for page_rel in record_pages(record):
        if page_rel == "SOURCES.html":
            continue
        part = frag.page_dir(page_rel)
        for name in frag.ordered(os.listdir(os.path.join(record, part))):
            text = _read(os.path.join(record, part, name))
            m = re.search(r'<h2 id="([^"]+)">', text)
            assert m, f"{part}/{name}: no heading"
            a = _ABOUT_OLD.search(text)
            out.append(Old(part, name, m.group(1), text, part.startswith("rendering/"), (a.group(1), a.group(2)) if a else None))
    return out


def _stems(olds: list[Old], tags: dict[str, list[str]]) -> tuple[list[Stem], list[str]]:
    errors: list[str] = []
    by_id = {o.heading_id: o for o in olds}
    stems: dict[str, Stem] = {}
    for o in olds:
        if o.drawing:
            continue
        s = Stem(research=None if o.part in CONVENTION_PARTS else o)
        if o.part in CONVENTION_PARTS:
            s.drawing = o
        row = tags.get(o.path)
        if row is None:
            errors.append(f"{o.path}: no row in the tag table")
            continue
        s.tags = {"subject": row[0].split(","), "setting": sorted(row[1].split(","), key=SETTING_ORDER.index), "level": [row[2]]}
        s.convention = row[3]
        stems[o.heading_id] = s
    extra: list[Stem] = []
    for o in olds:
        if not o.drawing:
            continue
        if o.about is None:
            errors.append(f"{o.path}: a drawing page with no `about:`")
            continue
        target = stems.get(o.about[1])
        if target is None or by_id.get(o.about[1]) is None:
            errors.append(f"{o.path}: about `{o.about[1]}`, which is no research question")
            continue
        research = target.research
        assert research is not None
        same = o.part == f"rendering/{research.part}" and o.prefix == research.prefix
        if same and target.drawing is None:
            target.drawing = o
        else:
            extra.append(Stem(research=None, drawing=o, about=target))
    return list(stems.values()) + extra, errors


def _number(stems: list[Stem], record: str, olds: list[Old]) -> list[Stem]:
    """Numbers in the order the new contents reads: section, then level, then old part order, then old prefix; a second
    drawing page right after the question it draws (plan D1)."""
    sys.path.insert(0, os.path.join(record, ".."))
    from l7r.diagram.interactive.record import contents as ct  # noqa: PLC0415

    vocab = ct.load_vocabulary(record)
    sections = ct.load_contents(record, vocab)
    rank = {s.id: i for i, s in enumerate(ct.walk(sections))}
    part_rank = {p: i for i, p in enumerate(dict.fromkeys(o.part for o in olds))}

    def key(s: Stem) -> tuple[int, int, int, str]:
        t = ct.Tags(tuple(s.tags["subject"]), tuple(s.tags["setting"]), s.tags["level"][0])
        h = ct.home(sections, t)
        return (rank[h.id] if h else 10**6, vocab.level_rank(t.level), part_rank[s.owner.part], s.owner.prefix)

    primary = sorted((s for s in stems if s.about is None), key=key)
    ordered: list[Stem] = []
    for s in primary:
        ordered.append(s)
        ordered += sorted((x for x in stems if x.about is s), key=lambda x: x.owner.prefix)
    for n, s in enumerate(ordered, start=1):
        s.number = n
    return ordered


class Links:
    """Every link of the old record resolved with the old index and written for `questions/`."""

    def __init__(self, record: str, new_file: dict[str, str]) -> None:
        sys.path.insert(0, os.path.join(record, ".."))
        from l7r.diagram.interactive.record import site  # noqa: PLC0415

        self.index = site.build_index(site.load(record))
        self.new_file = new_file  # old heading id -> new file name
        self.errors: list[str] = []

    def rewrite(self, markup: str, page_rel: str, from_dir: str, own_file: str, where: str) -> str:
        from l7r.diagram.interactive.record.site_links import LinkError, Loc  # noqa: PLC0415

        hidden = [(m.start(), m.end()) for m in _COMMENT.finditer(markup)]

        def one(m: re.Match[str]) -> str:
            if any(a <= m.start() < b for a, b in hidden):
                return m.group(0)
            href = m.group(2)
            if not href or _SCHEME.match(href) or href.startswith("//"):
                return m.group(0)
            try:
                target = self.index.anchor(page_rel, href[1:], href) if href.startswith("#") else self.index.resolve(href, from_dir)
            except LinkError as e:
                self.errors.append(f"{where}: {e}")
                return m.group(0)
            if isinstance(target, str):
                return m.group(1) + "../" + target + m.group(3)
            assert isinstance(target, Loc)
            if target.part == "sources":
                return m.group(1) + "../SOURCES.html#" + (target.anchor or target.page or "") + m.group(3)
            if target.page is None:
                self.errors.append(f"{where}: `{href}` links a whole page ({target.part}) - a part is no longer a place to link")
                return m.group(0)
            file = self.new_file[target.page]
            anchor = target.anchor or ""
            if file == own_file:
                return m.group(1) + "#" + (anchor or target.page) + m.group(3)
            return m.group(1) + file + (f"#{anchor}" if anchor else "") + m.group(3)

        return _ATTR.sub(one, markup)


def _with_marker(text: str, marker: str) -> str:
    m = _H2_END.search(text)
    assert m
    return text[: m.end()] + "\n" + marker + text[m.end() :]


def _tags_marker(t: dict[str, list[str]]) -> str:
    return f"<!-- tags: subject={','.join(t['subject'])}; setting={','.join(t['setting'])}; level={t['level'][0]} -->"


def _note_bodies(record: str, part: str) -> dict[str, tuple[str, str]]:
    """{key: (the notes file it is in, its `<li>`)} over one old page directory."""
    out: dict[str, tuple[str, str]] = {}
    root = os.path.join(record, part)
    for name in sorted(os.listdir(root)):
        if name.endswith(".notes.html"):
            for m in _NOTE.finditer(_read(os.path.join(root, name))):
                out.setdefault(m.group(1), (name, m.group(0)))
    return out


def _companions(record: str, o: Old) -> tuple[str, str]:
    base = os.path.join(record, o.part, o.file[: -len(".html")])
    notes = _read(base + ".notes.html") if os.path.isfile(base + ".notes.html") else ""
    orig = _read(base + ".originals.html") if os.path.isfile(base + ".originals.html") else ""
    return notes, orig


def _opening(record: str, part: str) -> str:
    front = _read(os.path.join(record, part, "_front.html"))
    body = _COMMENT.sub("", front.split("</h1>", 1)[1].split("<hr>", 1)[0]).strip()
    m = _P_EM.match(body)
    return m.group(1).strip() if m else body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--tags", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    record = os.path.join(args.root, SKILL, "research")
    qdir = os.path.join(record, "questions")
    if os.path.exists(qdir):
        print("record-flatten: research/questions/ exists - the flattening has run; it runs once", file=sys.stderr)
        return 2
    tags = {}
    for line in _read(args.tags).splitlines():
        if line.strip():
            path, subjects, settings, level, conv = line.split("\t")
            tags[path] = [subjects, settings, level, conv]
    olds = _questions(record)
    stems, errors = _stems(olds, tags)
    if errors:
        print("record-flatten: refused\n  " + "\n  ".join(errors), file=sys.stderr)
        return 1
    stems = _number(stems, record, olds)
    new_file: dict[str, str] = {}
    for s in stems:
        if s.research:
            new_file[s.research.heading_id] = f"{s.name}.html"
        if s.drawing:
            new_file[s.drawing.heading_id] = f"{s.name}.drawing.html"
    links = Links(record, new_file)
    out: dict[str, str] = {}
    moved: dict[str, str] = {}
    copied: list[str] = []
    for s in stems:
        for o, suffix in ((s.research, ""), (s.drawing, ".drawing")):
            if o is None:
                continue
            new_base = f"{s.name}{suffix}"
            own = f"{new_base}.html"
            text = links.rewrite(o.text, o.page_rel, posixpath.dirname(o.page_rel), own, o.path)
            text = _ABOUT_OLD.sub("", text)
            if s.about is not None:
                text = _with_marker(text, f"<!-- about: {s.about.name} -->")
            elif o is s.research or s.research is None:
                text = _with_marker(text, _tags_marker(s.tags))
            notes, orig = _companions(record, o)
            defined = {m.group(1) for m in _NOTE.finditer(notes)}
            for key in dict.fromkeys(_REF.findall(o.text)):
                if key in defined:
                    continue
                found = _note_bodies(record, o.part).get(key)
                if found is None:
                    links.errors.append(f"{o.path}: a reference to `{key}`, which no note of {o.part}/ defines")
                    continue
                notes += found[1] if found[1].endswith("\n") else found[1] + "\n"
                src_orig = os.path.join(record, o.part, found[0].replace(".notes.html", ".originals.html"))
                if os.path.isfile(src_orig):
                    orig += "".join(m.group(0) for m in _ORIG.finditer(_read(src_orig)) if m.group(1) == key)
                copied.append(f"{key}: {o.part}/{found[0]} -> {new_base}.notes.html")
            notes_from = posixpath.join("citations", posixpath.dirname(o.page_rel)).rstrip("/")
            out[own] = text
            moved[o.path] = f"questions/{own}"
            for kind, body in ((".notes.html", notes), (".originals.html", orig)):
                if body:
                    out[new_base + kind] = links.rewrite(body, o.page_rel, notes_from, own, o.path[: -len(".html")] + kind)
                    moved[o.path[: -len(".html")] + kind] = f"questions/{new_base}{kind}"
    if links.errors:
        print(f"record-flatten: refused ({len(links.errors)})\n  " + "\n  ".join(links.errors), file=sys.stderr)
        return 1
    # the openings into the contents, the confusables to stems, the mapping
    contents_path = os.path.join(record, "contents.json")
    contents = json.loads(_read(contents_path))
    by_id: dict[str, dict] = {}

    def index(sections: list[dict]) -> None:
        for sec in sections:
            by_id[sec["id"]] = sec
            index(sec["sections"])

    index(contents["sections"])
    parts = sorted({o.part for o in olds})
    openings = []
    for part in parts:
        drawing = part.startswith("rendering/")
        base = part[len("rendering/") :] if drawing else part
        sec = by_id[PART_SECTION[base]]
        text = _opening(record, part)
        sec["drawing_description" if drawing else "description"] = text
        openings.append((part, PART_SECTION[base], "drawing_description" if drawing else "description", text))
    conf_path = os.path.join(record, "confusables.json")
    conf = json.loads(_read(conf_path))
    for pair in conf:
        for side in ("a", "b"):
            page, _, anchor = pair[side].partition("#")
            pair[side] = f"{new_file[anchor]}#{anchor}"
    numbers = {}
    for o in olds:
        numbers[f"{o.part} {o.prefix}"] = moved[o.path].split("/", 1)[1].split("-", 1)[0]
    mapping = {
        "files": moved,
        "pages": {**{p: PART_SECTION[p[len("rendering/") :] if p.startswith("rendering/") else p] for p in parts}, "cities": "cities", "rendering/cities": "cities"},
        "numbers": numbers,
    }
    report = {"stems": len(stems), "files": len(out), "copied_notes": copied, "openings": openings}
    if args.dry_run:
        print(json.dumps(report, indent=1, ensure_ascii=False))
        return 0
    for name, text in out.items():
        _write(os.path.join(qdir, name), text)
    with open(contents_path, "w", encoding="utf-8") as fh:
        json.dump(contents, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    with open(conf_path, "w", encoding="utf-8") as fh:
        json.dump(conf, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    with open(os.path.join(record, "moved-303.json"), "w", encoding="utf-8") as fh:
        json.dump(mapping, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    for part in parts:
        shutil.rmtree(os.path.join(record, part))
    for gone in ("rendering/cities", "cities", "rendering"):
        p = os.path.join(record, gone)
        if os.path.isdir(p) and not os.listdir(p):
            os.rmdir(p)
    print(json.dumps(report, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
