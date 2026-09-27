#!/usr/bin/env python3
"""A check's BUNDLE: the files one check agent needs, copied OUT of the repository (feature 250).

WHY. Measured on feature 250's slice (`specs/250-*/research.md` R1): the moment a defined agent READS a
file under `research/`, the harness attaches every `CLAUDE.md` above that file - the root one, the
skill's dev loop and `research/CLAUDE.md`, about 28,400 tokens - to the agent's context as nested
memory. `omitClaudeMd: true` (feature 256) drops only the copy given at LAUNCH, not these. On the slice
that was 55-65% of every check's context and five to twelve times what the check read of the record. A
`record-format` run over copies in a scratch directory attached nothing: peak context 47,700 -> 14,500.

So a check reads COPIES, and this writes them - with the prepass output the check is handed anyway,
and a MANIFEST naming each copy's origin, because a finding has to cite the file the session will edit.
The agent's reply is its report, counts first and passes in one line each (feature 250 D8: the harness refuses a subagent's report file).

    _check_bundle.py PAGE --section S [--out DIR] [--extra PATH ...] [--no-quotes]
        one question: its fragment and notes, the prepass, the quote-verbatim report, the registry
        entries its notes cite, the glossary's variant index - for quote-check and record-format;
        with --kind <Class> (and --no-quotes), the modal written from it too - for entry-drift
    _check_bundle.py --key KEY [--out DIR]
        one source: its registry entry and the saved text of its page - for source-applicability
        and source-reader

The default directory is under `/tmp/l7r-check/`, which no `CLAUDE.md` sits above.
"""

from __future__ import annotations

import argparse
import ast
import datetime
import html
import json
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
RECORD = pathlib.Path(".claude/skills/diagram/research")
REGISTRY = RECORD / "sources" / "010-works-cited"
VARIANTS = RECORD / "assets" / "glossary-variants.txt"
CLASSES = pathlib.Path(".claude/skills/diagram/l7r/diagram/interactive/classes")
# Mode A sheets carry modals too (feature 262): a compound kind is a modal class as much as a settlement one
COMPOUND_KINDS = pathlib.Path(".claude/skills/diagram/l7r/diagram/interactive/compound_kinds")
DEFAULT_ROOT = pathlib.Path("/tmp/l7r-check")
MANIFEST = "MANIFEST.md"
_CITED = re.compile(r'<a href="[^"]*">\s*<code>([a-z0-9][a-z0-9-]*)</code>\s*</a>')
_URL = re.compile(r"https?://[^\s<\"]+")


def cited_keys(notes_html: str) -> list[str]:
    """The registry keys a question's notes cite, in first-cited order."""
    return list(dict.fromkeys(_CITED.findall(notes_html)))


def url_of(entry_html: str) -> str:
    """The pointer a registry entry names. A closing parenthesis ends it unless the URL opened one:
    `(https://.../Edo)` is written around a URL, `町屋_(商家)` is part of one."""
    found = _URL.search(entry_html)
    if not found:
        return ""
    url = html.unescape(found.group(0))  # the entry is HTML: `&amp;` in a query string is `&` (feature 268: the NDL records fetched as the home page)
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1]
    return url.rstrip(".,;")


def registry_entry(root: pathlib.Path, key: str) -> pathlib.Path | None:
    """The one registry file of a key. A glob on `*-<key>.html` also finds `NNNN-fires-in-<key>.html`, which
    is another work's entry; the name is the four-digit prefix and the key, nothing between."""
    exact = re.compile(rf"\d+-{re.escape(key)}\.html")
    return next((p for p in sorted((root / REGISTRY).glob(f"*{key}.html")) if exact.fullmatch(p.name)), None)


def kind_docstring(root: pathlib.Path, name: str) -> tuple[str, str] | None:
    """(origin `file:line`, docstring) of one modal class - what `entry-drift` compares with its section.
    The class, not its file: a classes module holds a dozen modals, and the check is about one. A name two modules
    share (the map's `Well` and the sheet's, feature 265) is qualified by its module: `household.Well`."""
    module, _, cls = name.rpartition(".")
    for path in [*sorted((root / CLASSES).glob("*.py")), *sorted((root / COMPOUND_KINDS).glob("*.py"))]:
        if module and path.stem != module:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == cls:
                return f"{path.relative_to(root)}:{node.lineno}", ast.get_docstring(node) or ""
    return None


# A block ends at its close tag, or - HTML's implicit close - at the next block or the end of the fragment: a
# fragment split off an assembled page can end in a `<p>` the next heading used to close, and matching only the
# close tag emptied a whole re-check bundle without a word (water 170, feature 250 T75).
_BLOCK = re.compile(r"<(p|li|blockquote|td|dd)\b[^>]*>.*?(?:</\1>|(?=<(?:p|li|blockquote|td|dd)\b)|\Z)", re.S)
_NOTE_LI = re.compile(r'<li data-note="([^"]+)">.*?</li>\n?', re.S)


def notes_subset(notes_html: str, keys: set[str]) -> str:
    """Only the named notes of a question's notes file, in their order."""
    return "".join(m.group(0) for m in _NOTE_LI.finditer(notes_html) if m.group(1) in keys)


def excerpt(fragment_html: str, keys: set[str]) -> str:
    """The question's heading and only the blocks whose text carries a mark for one of the keys - what a
    re-check of those notes reads (feature 250, recommendation 5: the second quote-check round of the first
    page session re-read two whole entries to confirm a handful of corrected notes)."""
    head = re.search(r"<h[23][^>]*>.*?</h[23]>", fragment_html, re.S)
    marks = tuple(f'data-note="{k}"' for k in keys)
    blocks = [m.group(0) for m in _BLOCK.finditer(fragment_html) if any(mk in m.group(0) for mk in marks)]
    kept = "\n".join(dict.fromkeys(blocks))
    return (head.group(0) + "\n" if head else "") + "<!-- an EXCERPT: only the blocks carrying the named notes -->\n" + kept + "\n"


def inline(out: pathlib.Path, rows: list[tuple[str, str, str]]) -> str:
    """Every copy written into the MANIFEST under its origin, so a check reads ONE file in ONE turn - the
    seeded runs took up to twice the turns of the tree legs reading a manifest and then each file in turn
    (feature 250, recommendation 1). Grep targets stay files of their own: the variant index and saved pages."""
    parts = []
    for name, origin, _what in rows:
        path = out / name
        if not path.is_file() or name in ("glossary-variants.txt", "quote-verbatim.json") or name.startswith("pages"):
            continue
        parts.append(f"## `{name}` - origin `{origin}`\n\n```\n{path.read_text(encoding='utf-8').rstrip()}\n```\n")
    return "\n".join(parts)


def refresh(out: pathlib.Path) -> None:
    """Rewrite a bundle's MANIFEST from the files now beside it - for a harness that edits a copy after the
    bundle was made (the seeded-fault runs plant their faults this way)."""
    text = (out / MANIFEST).read_text(encoding="utf-8")
    title = text.splitlines()[0].removeprefix("# Check bundle - ")
    rows = [(m.group(1), m.group(2), m.group(3)) for m in re.finditer(r"^\| `([^`]+)` \| `([^`]+)` \| (.*) \|$", text, re.M)]
    (out / MANIFEST).write_text(manifest(out, title, rows), encoding="utf-8")


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")


def fresh(out: pathlib.Path) -> None:
    """An empty bundle directory. An existing one is cleared only if it is a bundle - a MANIFEST of
    ours - so a mistyped OUT can never empty a directory this did not write."""
    if out.exists() and any(out.iterdir()):
        if not (out / MANIFEST).is_file():
            raise SystemExit(f"check-bundle: {out} exists and is not a bundle - choose another OUT")
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)


def run_script(name: str, args: list[str], root: pathlib.Path) -> tuple[int, str]:
    got = subprocess.run([sys.executable, str(HERE / name), *args], cwd=root, capture_output=True, text=True, check=False)
    return got.returncode, got.stdout + got.stderr


def manifest(out: pathlib.Path, title: str, rows: list[tuple[str, str, str]]) -> str:
    lines = [
        f"# Check bundle - {title}",
        "",
        f"Written {datetime.date.today().isoformat()} by `make check-bundle`. Every file here is a COPY. Read these and "
        "nothing under the repository: reading a file there attaches about 28,000 tokens of instruction files "
        "meant for the main session (feature 250). A finding names the ORIGIN column, which is the file the "
        "session will edit.",
        "",
        "**Everything you need is in THIS file**, each copy under its origin below; read it once. The two grep",
        "targets that are not inlined - the glossary's variant index and a source's saved pages - are files beside it.",
        "",
        "| file | origin | what it is for |",
        "|---|---|---|",
        *(f"| `{f}` | `{o}` | {w} |" for f, o, w in rows),
        "",
        inline(out, rows),
        "Reply with your report: the counts on the first line, then only what the session must act on (your contract gives the form).",
        "",
    ]
    return "\n".join(lines)


def copy(src: pathlib.Path, out: pathlib.Path, name: str | None = None) -> str:
    dest = out / (name or src.name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    return str(dest.relative_to(out))


#: WHAT EACH CHECK READS (feature 250 D14, research R5): every agent was handed the same bundle, and on a large
#: question about half of it was material that agent never uses - the quote report and the registry entries for
#: `record-format`, the word list for `quote-check`. `FOR=<agent>` keeps only that agent's parts; the question and
#: its notes are always in, and `all` (the default) is every part, as before.
PARTS = {
    "quote-check": {"quote"},
    "record-format": {"prepass", "variants"},
    "entry-drift": {"kind"},
    "all": {"quote", "prepass", "variants", "registry", "kind"},
}


def entry_bundle(root: pathlib.Path, page: str, section: str, out: pathlib.Path, extra: list[str], quotes: bool, kind: str = "",
                 notes: frozenset[str] = frozenset(), for_: str = "all") -> int:
    sys.path.insert(0, str(HERE))
    from _hm_record import fragments_for  # noqa: PLC0415

    fragments = fragments_for(page, section, str(root))
    if not fragments:
        print(f"check-bundle: SECTION={section!r} matched no question of {page}", file=sys.stderr)
        return 2
    found_kind = kind_docstring(root, kind) if kind else None
    if kind and found_kind is None:
        print(f"check-bundle: no modal class {kind!r} under {CLASSES} or {COMPOUND_KINDS}", file=sys.stderr)
        return 2
    fresh(out)
    rows: list[tuple[str, str, str]] = []
    keys: list[str] = []
    if found_kind:
        (out / "kind.txt").write_text(f"class {kind}  ({found_kind[0]})\n\n{found_kind[1]}\n", encoding="utf-8")
        rows.append(("kind.txt", found_kind[0], f"for entry-drift: the modal `{kind}` - its docstring, which IS what the map says"))
    for rel in fragments:
        what = "the question's footnotes" if rel.endswith(".notes.html") else "the question, as its reader meets it"
        name = copy(root / rel, out)
        if notes:
            dest, text = out / name, (root / rel).read_text(encoding="utf-8")
            dest.write_text(notes_subset(text, set(notes)) if rel.endswith(".notes.html") else excerpt(text, set(notes)), encoding="utf-8")
            what += f" - ONLY the notes {', '.join(sorted(notes))} and the blocks that carry them"
        rows.append((name, rel, what))
        if rel.endswith(".notes.html"):
            keys += cited_keys((out / name).read_text(encoding="utf-8"))
    want = PARTS[for_]
    if "prepass" in want:
        code, text = run_script("_record_prepass.py", [page, "--root", str(root), "--section", section], root)
        (out / "prepass.txt").write_text(text, encoding="utf-8")
        rows.append(("prepass.txt", f"make record-prepass PAGE={page} SECTION={section}", "for record-format: the WORDS TO RULE ON and the pattern candidates"))
        if code:
            print(text, file=sys.stderr)
            return code
    if quotes and "quote" in want:
        code, text = run_script("_quote_verbatim.py", [page, "--root", str(root), "--section", section, "--json", str(out / "quote-verbatim.json")], root)
        if notes and not code:
            text = scoped_verbatim(out, text)
        (out / "quote-verbatim.txt").write_text(text, encoding="utf-8")
        rows.append(("quote-verbatim.txt", f"make quote-verbatim PAGE={page} SECTION={section}", "for quote-check: which quotations are on their pages, character for character"))
        if code:
            print(text, file=sys.stderr)
            return code
    for key in dict.fromkeys(keys) if "registry" in want else ():
        src = registry_entry(root, key)
        if src is not None:
            rows.append((copy(src, out, f"sources/{key}.html"), str(src.relative_to(root)), f"the registry entry of `{key}`"))
    if "variants" in want:
        rows.append((copy(root / VARIANTS, out), str(VARIANTS), "the glossary's variant index: one line per defined word - grep it"))
    for path in extra:
        src = (root / path) if not pathlib.Path(path).is_absolute() else pathlib.Path(path)
        rows.append((copy(src, out, f"extra/{src.name}"), str(path), "named by the dispatcher"))
    (out / MANIFEST).write_text(manifest(out, f"{page}, question {section}" + ("" if for_ == "all" else f", for {for_}"), rows), encoding="utf-8")
    print(f"check-bundle: {len(rows)} file(s) in {out} - hand the agent {out / MANIFEST}")
    return 0


def scoped_verbatim(out: pathlib.Path, full_text: str) -> str:
    """The quote-verbatim report cut to the notes being re-checked: an entry is kept when one of its passages
    is quoted in the cut notes file, or its assertion stands in the excerpt."""
    import json  # noqa: PLC0415

    data = json.loads((out / "quote-verbatim.json").read_text(encoding="utf-8"))
    # A passage is a dict (`quote`, `original`) and the excerpt wraps its lines, so both sides are compared
    # as whitespace-collapsed text: `str(passage)` never occurred in a file, and every re-check report came
    # back empty (feature 250, cities/capitals session 2d).
    def flat(text: str) -> str:
        return " ".join(text.split())

    kept_text = flat("".join(p.read_text(encoding="utf-8") for p in out.glob("*.html")))
    plain = flat(re.sub(r"<[^>]+>", "", kept_text))
    kept = [e for e in data["footnotes"] if any(flat(str(p.get(k) or ""))[:40] in kept_text
                                                for p in e.get("passages") or [] for k in ("quote", "original") if p.get(k))
            or (e.get("assertion") and flat(str(e["assertion"]))[:40] in plain)]
    data["footnotes"] = kept
    (out / "quote-verbatim.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    lines = [ln for ln in full_text.splitlines() if not re.match(r"\s+fn-\d+ ", ln)]
    lines += [f"  {e['id']} {e.get('key') or e.get('class')} - {e.get('readability')}" for e in kept]
    return "\n".join(lines) + f"\n  (scoped to the {len(kept)} footnote(s) of the notes being re-checked)\n"


def print_notes(root: pathlib.Path, page: str, section: str, keys: frozenset[str]) -> int:
    """`make notes`: the named notes of one question and the blocks carrying them, and nothing else - what a
    session needs to edit a few notes, where the first page session dumped whole notes files and wide `sed`
    ranges of large fragments, 17,000 to 20,000 characters apiece (feature 250, recommendation 4)."""
    sys.path.insert(0, str(HERE))
    from _hm_record import fragments_for  # noqa: PLC0415

    found = fragments_for(page, section, str(root))
    if not found or not keys:
        print(f"notes: PAGE={page} SECTION={section} KEYS=<key,key> - {'no such question' if not found else 'name the keys'}", file=sys.stderr)
        return 2
    for rel in found:
        text = (root / rel).read_text(encoding="utf-8")
        body = notes_subset(text, set(keys)) if rel.endswith(".notes.html") else excerpt(text, set(keys))
        print(f"== {rel}\n{body}")
    return 0


def quoted_passages(root: pathlib.Path, key: str) -> list[str]:
    """Every passage the record quotes from `key` - the ORIGINAL where a quote is translated - across every notes file."""
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("_quote_verbatim", HERE / "_quote_verbatim.py")
    assert spec and spec.loader
    qv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(qv)
    li = re.compile(rf'<li data-note="{re.escape(key)}(?:-\d+)?">(.*?)</li>', re.S)
    out: list[str] = []
    for notes in sorted((root / ".claude/skills/diagram/research").rglob("*.notes.html")):
        for m in li.finditer(notes.read_text(encoding="utf-8")):
            # a session note in an HTML comment quotes the record's own reading, never the source (plan review, D19)
            out += [p["original"] or p["quote"] for p in qv.passages(re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S))]
    # a link's href and a short gloss phrase are quoted in the note's markup, not from the source
    return [q for q in dict.fromkeys(out) if not q.startswith(("http://", "https://")) and len(q) >= 20]


def key_bundle(root: pathlib.Path, key: str, out: pathlib.Path, whole: bool = False) -> int:
    entry = registry_entry(root, key)
    if entry is None:
        print(f"check-bundle: no registry entry for {key!r}", file=sys.stderr)
        return 2
    fresh(out)
    rows = [(copy(entry, out, f"sources/{key}.html"), str(entry.relative_to(root)), f"the registry entry of `{key}`: its two write-ups")]
    url = url_of(entry.read_text(encoding="utf-8"))
    if url:
        # D19 (R10): a long page is saved as its front and a window around each passage the record quotes from this
        # key - one book-length source cost 0.73 million tokens in one check when its whole text was copied
        # WHOLE (plan review, D19): a source-reader looks for the passage behind a NEW claim, which by construction
        # is not beside a passage already quoted - it gets the whole page, saved in parts, never the excerpt
        if whole:
            code, text = run_script("_source_pages.py", [str(out / "pages"), url], root)
            rows.append(("pages/", url, "the page's whole visible text, saved - a long page in PARTS; grep them all, read the part a hit is in"))
        else:
            qfile = out / "quotes.json"
            qfile.write_text(json.dumps(quoted_passages(root, key), ensure_ascii=False), encoding="utf-8")
            code, text = run_script("_source_pages.py", [str(out / "pages"), url, "--quotes", str(qfile)], root)
            rows.append(("pages/", url, "the page's visible text, saved - a long page as an EXCERPT (its front and a window around each passage the record quotes); grep it; MANIFEST.txt says which"))
        if code:
            print(text, file=sys.stderr)
    (out / MANIFEST).write_text(manifest(out, f"source {key}", rows), encoding="utf-8")
    print(f"check-bundle: {len(rows)} item(s) in {out} - hand the agent {out / MANIFEST}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("page", nargs="?", default="", help="a research page: ways, cities/sizing")
    ap.add_argument("--section", default="", help="one question: its prefix (010) or part of its heading id")
    ap.add_argument("--key", default="", help="one registry key, for a source bundle")
    ap.add_argument("--whole", action="store_true", help="with --key: the whole page in parts, not the excerpt - for source-reader (D19)")
    ap.add_argument("--out", default="", help=f"the bundle directory (default under {DEFAULT_ROOT})")
    ap.add_argument("--extra", nargs="*", default=[], help="further files to copy in, relative to the root")
    ap.add_argument("--notes", default="", help="re-check only these note keys, comma-separated: the notes file and the fragment are cut to them")
    ap.add_argument("--print-notes", action="store_true", help="print the named notes and the blocks carrying them, and write nothing (make notes)")
    ap.add_argument("--for", dest="for_", default="all", choices=sorted(PARTS), help="keep only what this check reads")
    ap.add_argument("--kind", default="", help="a modal class name, for entry-drift: its docstring is copied in")
    ap.add_argument("--no-quotes", action="store_true", help="skip the quote-verbatim report (it fetches every cited page)")
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    if args.key:
        return key_bundle(root, args.key, pathlib.Path(args.out or DEFAULT_ROOT / f"key-{args.key}{'-whole' if args.whole else ''}"), args.whole)
    if not args.page or not args.section:
        ap.error("PAGE and --section, or --key")
    wanted = frozenset(k.strip() for k in args.notes.split(",") if k.strip())
    if args.print_notes:
        return print_notes(root, args.page.removesuffix(".html"), args.section, wanted)
    out = pathlib.Path(args.out or DEFAULT_ROOT / f"{slug(args.page)}-{slug(args.section)}{'' if args.for_ == 'all' else '-' + args.for_}")
    return entry_bundle(root, args.page.removesuffix(".html"), args.section, out, args.extra, not args.no_quotes, args.kind, wanted, args.for_)


if __name__ == "__main__":
    sys.exit(main())
