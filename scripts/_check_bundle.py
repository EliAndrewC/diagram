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
The agent writes its whole report to `REPORT.md` here and replies with one line (feature 250 D8).

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
DEFAULT_ROOT = pathlib.Path("/tmp/l7r-check")
REPORT = "REPORT.md"
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
    url = found.group(0)
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
    The class, not its file: a classes module holds a dozen modals, and the check is about one."""
    for path in sorted((root / CLASSES).glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == name:
                return f"{path.relative_to(root)}:{node.lineno}", ast.get_docstring(node) or ""
    return None


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
        "| file | origin | what it is for |",
        "|---|---|---|",
        *(f"| `{f}` | `{o}` | {w} |" for f, o, w in rows),
        "",
        f"**Write your whole report to `{out / REPORT}`** and reply with ONE line (your contract gives its form).",
        "",
    ]
    return "\n".join(lines)


def copy(src: pathlib.Path, out: pathlib.Path, name: str | None = None) -> str:
    dest = out / (name or src.name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    return str(dest.relative_to(out))


def entry_bundle(root: pathlib.Path, page: str, section: str, out: pathlib.Path, extra: list[str], quotes: bool, kind: str = "") -> int:
    sys.path.insert(0, str(HERE))
    from _hm_record import fragments_for  # noqa: PLC0415

    fragments = fragments_for(page, section, str(root))
    if not fragments:
        print(f"check-bundle: SECTION={section!r} matched no question of {page}", file=sys.stderr)
        return 2
    found_kind = kind_docstring(root, kind) if kind else None
    if kind and found_kind is None:
        print(f"check-bundle: no modal class {kind!r} under {CLASSES}", file=sys.stderr)
        return 2
    fresh(out)
    rows: list[tuple[str, str, str]] = []
    keys: list[str] = []
    if found_kind:
        (out / "kind.txt").write_text(f"class {kind}  ({found_kind[0]})\n\n{found_kind[1]}\n", encoding="utf-8")
        rows.append(("kind.txt", found_kind[0], f"for entry-drift: the modal `{kind}` - its docstring, which IS what the map says"))
    for rel in fragments:
        what = "the question's footnotes" if rel.endswith(".notes.html") else "the question, as its reader meets it"
        rows.append((copy(root / rel, out), rel, what))
        if rel.endswith(".notes.html"):
            keys += cited_keys((root / rel).read_text(encoding="utf-8"))
    code, text = run_script("_record_prepass.py", [page, "--root", str(root), "--section", section], root)
    (out / "prepass.txt").write_text(text, encoding="utf-8")
    rows.append(("prepass.txt", f"make record-prepass PAGE={page} SECTION={section}", "for record-format: the WORDS TO RULE ON and the pattern candidates"))
    if code:
        print(text, file=sys.stderr)
        return code
    if quotes:
        code, text = run_script("_quote_verbatim.py", [page, "--root", str(root), "--section", section, "--json", str(out / "quote-verbatim.json")], root)
        (out / "quote-verbatim.txt").write_text(text, encoding="utf-8")
        rows.append(("quote-verbatim.txt", f"make quote-verbatim PAGE={page} SECTION={section}", "for quote-check: which quotations are on their pages, character for character"))
        if code:
            print(text, file=sys.stderr)
            return code
    for key in dict.fromkeys(keys):
        src = registry_entry(root, key)
        if src is not None:
            rows.append((copy(src, out, f"sources/{key}.html"), str(src.relative_to(root)), f"the registry entry of `{key}`"))
    rows.append((copy(root / VARIANTS, out), str(VARIANTS), "the glossary's variant index: one line per defined word - grep it"))
    for path in extra:
        src = (root / path) if not pathlib.Path(path).is_absolute() else pathlib.Path(path)
        rows.append((copy(src, out, f"extra/{src.name}"), str(path), "named by the dispatcher"))
    (out / MANIFEST).write_text(manifest(out, f"{page}, question {section}", rows), encoding="utf-8")
    print(f"check-bundle: {len(rows)} file(s) in {out} - hand the agent {out / MANIFEST}")
    return 0


def key_bundle(root: pathlib.Path, key: str, out: pathlib.Path) -> int:
    entry = registry_entry(root, key)
    if entry is None:
        print(f"check-bundle: no registry entry for {key!r}", file=sys.stderr)
        return 2
    fresh(out)
    rows = [(copy(entry, out, f"sources/{key}.html"), str(entry.relative_to(root)), f"the registry entry of `{key}`: its two write-ups")]
    url = url_of(entry.read_text(encoding="utf-8"))
    if url:
        code, text = run_script("_source_pages.py", [str(out / "pages"), url], root)
        rows.append(("pages/", url, "the page's full visible text, saved - grep it; MANIFEST.txt says whether it was fetched"))
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
    ap.add_argument("--out", default="", help=f"the bundle directory (default under {DEFAULT_ROOT})")
    ap.add_argument("--extra", nargs="*", default=[], help="further files to copy in, relative to the root")
    ap.add_argument("--kind", default="", help="a modal class name, for entry-drift: its docstring is copied in")
    ap.add_argument("--no-quotes", action="store_true", help="skip the quote-verbatim report (it fetches every cited page)")
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    if args.key:
        return key_bundle(root, args.key, pathlib.Path(args.out or DEFAULT_ROOT / f"key-{args.key}"))
    if not args.page or not args.section:
        ap.error("PAGE and --section, or --key")
    out = pathlib.Path(args.out or DEFAULT_ROOT / f"{slug(args.page)}-{slug(args.section)}")
    return entry_bundle(root, args.page.removesuffix(".html"), args.section, out, args.extra, not args.no_quotes, args.kind)


if __name__ == "__main__":
    sys.exit(main())
