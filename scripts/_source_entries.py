#!/usr/bin/env python3
"""The registry entries and citing footnotes of the sources a check is about, by key (feature 255, FR-002).

WHY. `source-applicability` judges a few sources at a time, and its recorded runs read `SOURCES.html` 10.5 times
a run - paging through a registry of several hundred entries for the handful it was asked about (feature 251,
research R9). What it needs from the record is mechanical to find: each key's entry (the citation line, both
write-ups, the `Used for:` line) and every footnote that cites the key, with the assertion the footnote is
attached to - which is what we USE the source for. This prints exactly that, for no tokens, and the session
puts it in the agent's prompt; the agent opens the registry only for a key this listing lacks.

WHAT IT READS. `research/SOURCES.html`, where an entry is `<h3 id="key"><code>key</code></h3>` and the
paragraphs up to the next heading; every `research/citations/**/*.html` for the notes (`_quote_verbatim.footnotes`
for a note's passages, a note being matched on ANY `<code>` key it carries - one note in five cites more than
one work); and the research page beside each citations page for the assertions (`_quote_verbatim.assertions`).
It judges nothing and never edits.
"""

from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
RESEARCH = ".claude/skills/diagram/research"


def _qv():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_quote_verbatim", HERE / "_quote_verbatim.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


qv = _qv()


def entry(registry_html: str, key: str) -> list[str]:
    """The visible paragraphs of the entry whose anchor or `<code>` key is `key`; empty when there is none."""
    m = re.search(rf'<h3 id="(?:{re.escape(key)})"[^>]*>.*?</h3>|<h3[^>]*>\s*<code>{re.escape(key)}</code>\s*</h3>', registry_html, re.S)
    if not m:
        return []
    rest = registry_html[m.end() :]
    stop = re.search(r"<h[1-3]\b", rest)
    body = rest[: stop.start()] if stop else rest
    return [text for text in (qv._strip(p) for p in re.findall(r"<p\b[^>]*>(.*?)</p>", body, re.S)) if text]


def citing(citations_html: str, research_html: str, keys: set[str]) -> list[dict]:
    """The notes of one citations page that carry any of `keys`: id, the keys matched, passages, assertion."""
    claims = qv.assertions(research_html)
    by_id = {n["id"]: n for n in qv.footnotes(citations_html)}
    found: list[dict] = []
    for m in re.finditer(r'<li id="(fn-\d+)">(.*?)</li>', citations_html, re.S):
        hit = sorted(keys & set(re.findall(r"<code>([^<]+)</code>", m.group(2))))
        if hit:
            note = by_id[m.group(1)]
            found.append({"id": m.group(1), "keys": hit, "passages": note["passages"], "assertion": claims.get(m.group(1), "")})
    return found


def gather(root: pathlib.Path, keys: list[str]) -> dict:
    research = root / RESEARCH
    registry = (research / "SOURCES.html").read_text(encoding="utf-8")
    out: dict = {"entries": {k: entry(registry, k) for k in keys}, "notes": {k: [] for k in keys}}
    for cite_file in sorted((research / "citations").rglob("*.html")):
        name = cite_file.relative_to(research / "citations").with_suffix("").as_posix()
        page_file = research / f"{name}.html"
        page = page_file.read_text(encoding="utf-8") if page_file.is_file() else ""
        for note in citing(cite_file.read_text(encoding="utf-8"), page, set(keys)):
            for k in note["keys"]:
                out["notes"][k].append({**note, "page": name})
    return out


def render(found: dict) -> str:
    lines: list[str] = []
    for key, paragraphs in found["entries"].items():
        lines.append(f"== {key}")
        if not paragraphs:
            lines.append("  NOT IN THE REGISTRY - no entry carries this key; open SOURCES.html for it, or judge it as a new source")
        lines.extend(f"  {p}" for p in paragraphs)
        notes = found["notes"][key]
        lines.append(f"  -- cited by {len(notes)} footnote{'' if len(notes) == 1 else 's'}")
        for n in notes:
            lines.append(f"  {n['page']} {n['id']}  ASSERTION: {n['assertion'] or '(none found beside the note)'}")
            for p in n["passages"]:
                lines.append(f"      QUOTES: {p['quote']}" + (f"  [original, {p['language']}: {p['original']}]" if p["original"] else ""))
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("keys", help="registry keys, comma-separated: kikoba-kenchi,ndl-kokumori")
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    keys = list(dict.fromkeys(k.strip() for k in args.keys.split(",") if k.strip()))
    if not keys:
        print("source-entries: no key given - KEYS=<k1,k2,...>", file=sys.stderr)
        return 2
    print(render(gather(pathlib.Path(args.root), keys)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
