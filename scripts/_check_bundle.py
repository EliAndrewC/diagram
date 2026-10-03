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

    _check_bundle.py Q [--out DIR] [--extra PATH ...] [--no-quotes]
        one question (feature 303: its number, `0412`, or a page's file name): its page(s) and notes, the prepass, the quote-verbatim report, the registry
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
sys.path.insert(0, str(HERE))
import _bundle_owed as bo  # noqa: E402
RECORD = pathlib.Path(".claude/skills/diagram/research")
REGISTRY = RECORD / "sources" / "010-works-cited"
VARIANTS = RECORD / "assets" / "glossary-variants.txt"
CLASSES = pathlib.Path(".claude/skills/diagram/l7r/diagram/interactive/classes")
# Mode A sheets carry modals too (feature 262): a compound kind is a modal class as much as a settlement one
COMPOUND_KINDS = pathlib.Path(".claude/skills/diagram/l7r/diagram/interactive/compound_kinds")
DEFAULT_ROOT = pathlib.Path("/tmp/l7r-check")
MANIFEST = "MANIFEST.md"
#: the MANIFEST section feature 311 appends: what may be dispatched on the bundle, and the units it carries
OWED_HEAD = "## Owed (feature 311)"
_CITED = re.compile(r'<a href="[^"]*">\s*<code>([a-z0-9][a-z0-9-]*)</code>\s*</a>')
_URL = re.compile(r"https?://[^\s<\"]+")


def cited_keys(notes_html: str) -> list[str]:
    """The registry keys a question's notes cite, in first-cited order."""
    return list(dict.fromkeys(_CITED.findall(notes_html)))


def url_of(entry_html: str) -> str:
    """The pointer a registry entry names. A closing parenthesis ends it unless the URL opened one:
    `(https://.../Edo)` is written around a URL, `町屋_(商家)` is part of one. Punctuation after the wrapping
    parenthesis (`.../174809), 5 August`) goes with it, and an entity is unescaped: the entry is HTML, so
    `&amp;page=` is `&page=` - fetched as written it lands on the site's front page (feature 269)."""
    found = _URL.search(entry_html)
    if not found:
        return ""
    url = html.unescape(found.group(0))  # the entry is HTML: `&amp;` in a query string is `&` (feature 268: the NDL records fetched as the home page)
    while url.endswith((".", ",", ";", ":")) or (url.endswith(")") and url.count(")") > url.count("(")):
        url = url[:-1]
    return url


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


def excerpt(fragment_html: str, keys: set[str], bare: bool = False) -> str:
    """The question's heading and only the blocks whose text carries a mark for one of the keys - what a
    re-check of those notes reads (feature 250, recommendation 5: the second quote-check round of the first
    page session re-read two whole entries to confirm a handful of corrected notes). With `bare`, every block that
    carries no note mark too - what a check of the page's UNFOOTNOTED blocks reads (feature 314: a batched bundle owed
    `#unfootnoted` carried only its notes' blocks, and the block the unit was owed for was in none of them)."""
    head = re.search(r"<h[23][^>]*>.*?</h[23]>", fragment_html, re.S)
    marks = tuple(f'data-note="{k}"' for k in keys)
    blocks = [m.group(0) for m in _BLOCK.finditer(fragment_html) if any(mk in m.group(0) for mk in marks) or (bare and "data-note=" not in m.group(0))]
    kept = "\n".join(dict.fromkeys(blocks))
    what = "only the blocks carrying the named notes" + (", and every block carrying none" if bare else "")
    return (head.group(0) + "\n" if head else "") + f"<!-- an EXCERPT: {what} -->\n" + kept + "\n"


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
    owed = text[text.index(OWED_HEAD):] if OWED_HEAD in text else ""
    (out / MANIFEST).write_text(manifest(out, title, rows) + owed, encoding="utf-8")


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
    "quote-check": {"quote", "notes"},
    "record-format": {"prepass", "variants", "notes"},
    "entry-drift": {"kind"},
    "record-style": {"style", "styleprepass", "variants"},
    "translation-check": {"translations"},
    "intro-check": {"intro"},
    "all": {"quote", "prepass", "variants", "registry", "kind", "notes"},
}
#: FEATURE 292 (GM 2026-09-29, approving the session's proposal): the question's NOTES are a part of their own. The
#: quote-check reads them whole and record-format rules on their words; entry-drift compares a modal with the prose and
#: record-style judges the prose, so neither is handed them - record-style only when it audits a merge (`--extra`, the
#: old sections, whose notes it must account for). The notes a check is handed carry each original's PLACEHOLDER, never
#: the original (`record/originals.py`): only `translation-check` reads the originals, and only the pairs owed one.
#: And the quote-check reads notes in BATCHES of at most `NOTES_BUDGET` bytes - the question-size cap counts prose only
#: since 292, so this is where a large topic's notes are bounded: at 12,000 bytes a batch plus its excerpt stays within
#: what the old 20,000-byte cap on prose + notes allowed one check to read (on 2026-09-29 the median notes file was
#: 4,838 bytes, the 90th percentile 8,599, and one over 12,000 - the merged grove topic's 13,637).
NOTES_BUDGET = 12_000
#: The style guide `record-style` judges against (feature 292) - handed in the bundle, so the agent reads the one copy
#: the writers read rather than a paraphrase of it in its contract.
STYLE = pathlib.Path(".claude/skills/diagram/research/STYLE.md")


def entry_bundle(root: pathlib.Path, q: str, out: pathlib.Path, extra: list[str], quotes: bool, kind: str = "",
                 notes: frozenset[str] = frozenset(), for_: str = "all", owed: str = "", bare: bool = False) -> int:
    sys.path.insert(0, str(HERE))
    from _hm_record import fragments_for  # noqa: PLC0415

    fragments = fragments_for(q, str(root))
    if not fragments:
        print(f"check-bundle: Q={q!r} names no question - name one by its number, e.g. make check-bundle Q=0041", file=sys.stderr)
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
        if rel.endswith(".notes.html") and "notes" not in PARTS[for_] and not (for_ == "record-style" and extra):
            continue
        what = "the question's footnotes" if rel.endswith(".notes.html") else "the question, as its reader meets it"
        name = copy(root / rel, out)
        if notes:
            dest, text = out / name, (root / rel).read_text(encoding="utf-8")
            dest.write_text(notes_subset(text, set(notes)) if rel.endswith(".notes.html") else excerpt(text, set(notes), bare), encoding="utf-8")
            what += f" - ONLY the notes {', '.join(sorted(notes))} and the blocks that carry them" + (", and every block that carries no note" if bare else "")
        rows.append((name, rel, what))
        if rel.endswith(".notes.html"):
            keys += cited_keys((out / name).read_text(encoding="utf-8"))
    want = PARTS[for_]
    if "prepass" in want:
        code, text = run_script("_record_prepass.py", [q, "--root", str(root)], root)
        (out / "prepass.txt").write_text(text, encoding="utf-8")
        rows.append(("prepass.txt", f"make record-prepass Q={q}", "for record-format: the WORDS TO RULE ON and the pattern candidates"))
        if code:
            print(text, file=sys.stderr)
            return code
    if quotes and "quote" in want:
        code, text = run_script("_quote_verbatim.py", [q, "--root", str(root), "--json", str(out / "quote-verbatim.json")], root)
        if notes and not code:
            text = scoped_verbatim(out, text)
        (out / "quote-verbatim.txt").write_text(text, encoding="utf-8")
        rows.append(("quote-verbatim.txt", f"make quote-verbatim Q={q}", "for quote-check: which quotations are on their pages, character for character"))
        if code:
            print(text, file=sys.stderr)
            return code
        if residue_pages(out):
            rows.append(("pages/", "the host's page cache (feature 288)", "for quote-check: the saved text of each page a quotation was not found VERBATIM on - grep it before any WebFetch; its MANIFEST.txt names a page the cache did not hold"))
    for key in dict.fromkeys(keys) if "registry" in want else ():
        src = registry_entry(root, key)
        if src is not None:
            rows.append((copy(src, out, f"sources/{key}.html"), str(src.relative_to(root)), f"the registry entry of `{key}`"))
    if "styleprepass" in want:
        code, text = run_script("_style_prepass.py", [q, "--root", str(root)], root)
        (out / "style-prepass.txt").write_text(text, encoding="utf-8")
        rows.append(("style-prepass.txt", f"make style-prepass Q={q}", "for record-style: the metric figures with no conversion (each a FAIL) and every lead line to rule on"))
        if code:
            print(text, file=sys.stderr)
            return code
    if "translations" in want:
        code, text = run_script("_translation_owed.py", ["--root", str(root), "--q", q], root)
        (out / "translations.txt").write_text(text, encoding="utf-8")
        rows.append(("translations.txt", f"make translation-owed Q={q}", "for translation-check: each owed translated quotation, its translation and its original"))
        if code:
            print(text, file=sys.stderr)
            return code
    if "style" in want:
        rows.append((copy(root / STYLE, out), str(STYLE), "for record-style: the style guide - every rule you judge, with the GM's words it comes from"))
    if "variants" in want:
        rows.append((copy(root / VARIANTS, out), str(VARIANTS), "the glossary's variant index: one line per defined word - grep it"))
    for path in extra:
        src = (root / path) if not pathlib.Path(path).is_absolute() else pathlib.Path(path)
        rows.append((copy(src, out, f"extra/{src.name}"), str(path), "named by the dispatcher"))
    (out / MANIFEST).write_text(manifest(out, f"question {q}" + ("" if for_ == "all" else f", for {for_}"), rows) + owed, encoding="utf-8")
    print(f"check-bundle: {len(rows)} file(s) in {out} - hand the agent {out / MANIFEST}")
    return 0


class NotCached:
    """The fetcher behind a cache-only read: a page the cache does not hold is named, never fetched."""

    refused: dict = {}

    @staticmethod
    def get(_url: str) -> dict:
        return {"state": "NOT-CACHED", "why": "not in the page cache (quote-verbatim could not save it) - fetch it yourself"}


def residue_pages(out: pathlib.Path) -> int:
    """The cached text of every page a quotation in the bundle's quote-verbatim report was not found VERBATIM on, saved
    under `out/pages/` from the host's page cache ONLY - quote-verbatim has just read each of them through it, so
    nothing is fetched again (feature 288 FR-010, FR-011: quote-check reads this before any WebFetch). The count of
    pages named; 0 writes nothing. A re-verification read: no ledger line (spec D1)."""
    report = out / "quote-verbatim.json"
    data = json.loads(report.read_text(encoding="utf-8")) if report.is_file() else {}
    urls = [u for e in data.get("footnotes", []) if any(p.get("quotation") != "VERBATIM" for p in e.get("passages", []))
            for u in e.get("links", []) if u.startswith(("http://", "https://"))]
    if not urls:
        return 0
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("_source_pages", HERE / "_source_pages.py")
    assert spec and spec.loader
    sp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sp)
    sp.save(list(dict.fromkeys(urls)), out / "pages", sp.src.CachedPages(NotCached(), sp.src.home()))
    return len(dict.fromkeys(urls))


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


def print_notes(root: pathlib.Path, q: str, keys: frozenset[str]) -> int:
    """`make notes`: the named notes of one question and the blocks carrying them, and nothing else - what a
    session needs to edit a few notes, where the first page session dumped whole notes files and wide `sed`
    ranges of large fragments, 17,000 to 20,000 characters apiece (feature 250, recommendation 4)."""
    sys.path.insert(0, str(HERE))
    from _hm_record import fragments_for  # noqa: PLC0415

    found = fragments_for(q, str(root))
    if not found or not keys:
        print(f"notes: Q={q} KEYS=<key,key> - {'no such question' if not found else 'name the keys'}", file=sys.stderr)
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


def ledger_part(saved: str) -> str:
    """What a `_source_pages.py` run printed before its manifest: the page's earlier reads on the ledger (feature 288)."""
    return saved.split("pointer | file | state", 1)[0].strip("\n")


def claims_read(root: pathlib.Path, units: list) -> str:
    """The claims a WHOLE read is owed for: each owed note and the blocks carrying its mark, per question. Feature 319: a
    WHOLE bundle held only the write-up and the page, so source-reader judged the write-up and the owed notes' sentences
    went unread while their units were answered."""
    wanted: dict[str, set[str]] = {}
    for u in units:
        if u.check == "source-reader":
            stem, _, note = u.subject.partition("#")
            wanted.setdefault(stem, set()).add(note)
    if not wanted:
        return ""
    from _hm_record import fragments_for  # noqa: PLC0415

    parts = ["", "## The claims to read (the owed notes, and the sentences carrying them)", ""]
    for stem, keys in sorted(wanted.items()):
        q, _, page = stem.partition(".")  # `0094` is the research page, `0094.drawing` the drawing page
        for rel in fragments_for(q, str(root)):
            if (".drawing." in rel) != (page == "drawing"):
                continue
            text = (root / rel).read_text(encoding="utf-8")
            body = notes_subset(text, keys) if rel.endswith(".notes.html") else excerpt(text, keys)
            if 'data-note="' in body:
                parts += [f"### `{rel}`", "", "```", body.rstrip("\n"), "```", ""]
    return "\n".join(parts) + "\n"


def key_bundle(root: pathlib.Path, key: str, out: pathlib.Path, whole: bool = False, question: str = "", owed: str = "", units: list | None = None) -> int:
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
        # THE LEDGER (feature 288 D1, spec-fidelity round 1): a WHOLE read is source-reader searching a cited page for a NEW
        # claim - a research read, so its earlier reads are printed and a `pending` line appended, as `make source-pages`
        # does; the excerpt re-checks passages already quoted, and writes no ledger line. Both read the page cache.
        if whole:
            code, text = run_script("_source_pages.py", [str(out / "pages"), url, *(["--question", question] if question else [])], root)
            if ledger_part(text):
                print(ledger_part(text))
            rows.append(("pages/", url, "the page's whole visible text, saved - a long page in PARTS; grep them all, read the part a hit is in"))
        else:
            qfile = out / "quotes.json"
            qfile.write_text(json.dumps(quoted_passages(root, key), ensure_ascii=False), encoding="utf-8")
            code, text = run_script("_source_pages.py", [str(out / "pages"), url, "--quotes", str(qfile), "--no-ledger"], root)
            rows.append(("pages/", url, "the page's visible text, saved - a long page as an EXCERPT (its front and a window around each passage the record quotes); grep it; MANIFEST.txt says which"))
        if code:
            print(text, file=sys.stderr)
    (out / MANIFEST).write_text(manifest(out, f"source {key}", rows) + owed + claims_read(root, units), encoding="utf-8")
    print(f"check-bundle: {len(rows)} item(s) in {out} - hand the agent {out / MANIFEST}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("q", nargs="?", default="", help="one question: its number (0412) or a page's file name (feature 303)")
    ap.add_argument("--key", default="", help="one registry key, for a source bundle")
    ap.add_argument("--whole", action="store_true", help="with --key: the whole page in parts, not the excerpt - for source-reader (D19)")
    ap.add_argument("--question", default="", help="with --whole: the research question the page is read for, recorded on the sources-consulted ledger (feature 288)")
    ap.add_argument("--out", default="", help=f"the bundle directory (default under {DEFAULT_ROOT})")
    ap.add_argument("--extra", nargs="*", default=[], help="further files to copy in, relative to the root")
    ap.add_argument("--notes", default="", help="re-check only these note keys, comma-separated: the notes file and the fragment are cut to them")
    ap.add_argument("--print-notes", action="store_true", help="print the named notes and the blocks carrying them, and write nothing (make notes)")
    ap.add_argument("--for", dest="for_", default="all", choices=sorted(PARTS), help="keep only what this check reads")
    ap.add_argument("--kind", default="", help="a modal class name, for entry-drift: its docstring is copied in")
    ap.add_argument("--no-quotes", action="store_true", help="skip the quote-verbatim report (it fetches every cited page)")
    ap.add_argument("--root", default=".")
    ap.add_argument("--qs", default="", help="for intro-check: several questions in one bundle (the backfill's batches)")
    ap.add_argument("--not-owed-ok", default="", help="build it though nothing owes it: the reason, recorded in the MANIFEST (feature 311)")
    ap.add_argument("--new", default="", help="with --key --whole: the claim, not yet in the record, the read is for (feature 311)")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    escape = args.not_owed_ok or args.new
    if args.key:
        units, checks, refusal = bo.owed_for_key(root, args.key, args.whole, args.not_owed_ok, args.new)
        if refusal:
            print(f"check-bundle: REFUSED - {refusal}", file=sys.stderr)
            return 3
        return key_bundle(root, args.key, pathlib.Path(args.out or DEFAULT_ROOT / f"key-{args.key}{'-whole' if args.whole else ''}"), args.whole, args.question,
                          bo.manifest_lines(units, checks, escape), units)
    if args.for_ == "intro-check":
        return intro_bundle(root, (args.qs or args.q).split(), args.out, args.not_owed_ok)
    if not args.q:
        ap.error("Q (a question's number), or --key")
    wanted = frozenset(k.strip() for k in args.notes.split(",") if k.strip())
    if args.print_notes:
        return print_notes(root, args.q, wanted)
    if not fragments_for_q(root, args.q):
        print(f"check-bundle: Q={args.q!r} names no question - name one by its number, e.g. make check-bundle Q=0041", file=sys.stderr)
        return 2
    units, checks, refusal = bo.owed_for_question(root, args.q, args.for_, args.not_owed_ok)
    if refusal:
        print(f"check-bundle: REFUSED - {refusal}", file=sys.stderr)
        return 3
    if args.for_ == "quote-check" and not wanted and not args.not_owed_ok:
        wanted = bo.owed_notes(units)  # only the notes owed a check (feature 311, plan D9)
    owed = bo.manifest_lines(units, checks, args.not_owed_ok)
    out = pathlib.Path(args.out or DEFAULT_ROOT / f"q-{slug(args.q)}{'' if args.for_ == 'all' else '-' + args.for_}")
    q = args.q
    batches = [] if wanted or args.for_ != "quote-check" else note_batches(root, q)
    # ...AND THE UNFOOTNOTED BLOCKS IN EVERY BATCH where their check is owed: a batch's excerpt keeps only its notes' blocks
    bare = args.for_ == "quote-check" and bo.unfootnoted_owed(units)
    if len(batches) > 1:
        print(f"check-bundle: the notes are over {NOTES_BUDGET:,} bytes - {len(batches)} quote-check bundles, one agent each:")
        codes = [entry_bundle(root, q, out / f"batch-{i}", args.extra, not args.no_quotes, args.kind, frozenset(b), args.for_,
                              bo.manifest_lines(bo.batch_units(units, frozenset(b)), checks, args.not_owed_ok), bare)
                 for i, b in enumerate(batches, start=1)]
        return max(codes)
    return entry_bundle(root, q, out, args.extra, not args.no_quotes, args.kind, wanted, args.for_, owed)


def fragments_for_q(root: pathlib.Path, q: str) -> list[str]:
    from _hm_record import fragments_for  # noqa: PLC0415

    return fragments_for(q, str(root))


def intro_bundle(root: pathlib.Path, questions: list[str], out_arg: str, not_owed_ok: str) -> int:
    """An intro-check bundle over one question or a batch (plan D4, D10): each question's research page whole, its drawing
    page and the map elements written from it - and refused for a question nothing owes it on, unless a reason is given."""
    units: list = []
    every = bo.ro.units(root)
    for q in questions:
        got, _checks, refusal = bo.owed_for_question(root, q, "intro-check", not_owed_ok, every)
        if refusal:
            print(f"check-bundle: REFUSED - {refusal}", file=sys.stderr)
            return 3
        units += got
    texts = [(q, bo.intro_bundle_text(root, q)) for q in questions]
    missing = [q for q, text in texts if not text]
    if missing:
        print(f"check-bundle: no research page for {' '.join(missing)}", file=sys.stderr)
        return 2
    out = pathlib.Path(out_arg or DEFAULT_ROOT / f"intro-{slug(questions[0])}{'-' + str(len(questions)) if len(questions) > 1 else ''}")
    fresh(out)
    rows = []
    for q, text in texts:
        name = f"q-{bo.question_of(q)}.txt"
        (out / name).write_text(text, encoding="utf-8")
        rows.append((name, f"{bo.ru.QUESTIONS}/{bo.question_of(q)}-*.html", "for intro-check: the research page, its drawing page, the map elements written from it"))
    title = f"question {questions[0]}, for intro-check" if len(questions) == 1 else f"{len(questions)} questions, for intro-check"
    (out / MANIFEST).write_text(manifest(out, title, rows) + bo.manifest_lines(units, "intro-check", not_owed_ok), encoding="utf-8")
    print(f"check-bundle: {len(rows)} question(s) in {out} - hand the agent {out / MANIFEST}")
    return 0


def note_batches(root: pathlib.Path, q: str) -> list[list[str]]:
    """The question's note keys in runs of at most `NOTES_BUDGET` bytes of notes each, in note order (a single note
    over the budget is a run of its own). One run when they fit - the ordinary bundle."""
    sys.path.insert(0, str(HERE))
    from _hm_record import fragments_for  # noqa: PLC0415

    batches: list[list[str]] = [[]]
    size = 0
    for rel in fragments_for(q, str(root)):
        if not rel.endswith(".notes.html"):
            continue
        for m in _NOTE_LI.finditer((root / rel).read_text(encoding="utf-8")):
            n = len(m.group(0).encode("utf-8"))
            if batches[-1] and size + n > NOTES_BUDGET:
                batches.append([])
                size = 0
            batches[-1].append(m.group(1))
            size += n
    return [b for b in batches if b]


if __name__ == "__main__":
    sys.exit(main())
