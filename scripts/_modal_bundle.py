#!/usr/bin/env python3
"""A modal check's BUNDLE and its PREPASS (feature 319, plan D5) - what `modal-form` or `modal-research` reads, copied OUT of the
repository as every record check's bundle is (feature 250: an agent that reads a file under the repository is handed every
`CLAUDE.md` above it).

    _modal_bundle.py KIND [--for modal-form|modal-research] [--out DIR]    the bundle; KIND is a class name or key
    _modal_bundle.py KIND --prepass                                         the prepass alone, printed

THE BUNDLE. `modal.md` - the modal as its reader meets it, tab by tab, with its origin; the guidelines its form names
(`dev/modals.md` or `dev/modals-particular.md`); the prepass. For `modal-research` also: each page the `Entry:` names with its
notes; `candidates.md`; the ten best candidates whole; and `record/`, every question page, for grep (never read whole).

THE CANDIDATES (plan D5, the plan review's round-1 ruling). The UNION of every question sharing ANY `subject` tag with the pages
the modal's `Entry:` names and every question whose words carry the modal's name, key or one of their glossary variants -
ranked by the kind's terms it carries and the tags it shares, never cut. The farmhouse's own case is the proof: 0004 ("how many
live in a house") carries `subject=tiers,households` and meets 0029's `households` tag.

THE PREPASS: the About tab's word count against the guidelines' band; phrases the guidelines bar from About (record talk -
`dev/modals.md` M16, the feature-level label - M11); a guess that is longer than two sentences (M3); an `Entry:` that names no
file.
"""

from __future__ import annotations

import argparse
import datetime
import html
import pathlib
import re
import shutil
import sys
from collections.abc import Sequence

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import _modal_owed as mo  # noqa: E402

SKILL = pathlib.Path(mo.SKILL)
QUESTIONS = SKILL / "research" / "questions"
VARIANTS = SKILL / "research" / "assets" / "glossary-variants.txt"
GUIDELINES = {"standard": SKILL / "dev" / "modals.md", "particular": SKILL / "dev" / "modals-particular.md"}
#: the About tab's word band, per form (`dev/modals.md` M3, `dev/modals-particular.md` P3)
BAND = {"standard": (120, 250), "particular": (80, 200)}
#: record talk and the old feature-level label, barred from the About tab (`dev/modals.md` M11, M16)
BARRED = (
    r"\bthis project\b", r"\bthe record\b", r"\bpages? (we )?read\b", r"\bno page\b", r"\bGUESS\b", r"\bThis is a guess\b",
    r"\bthis is a deliberate deviation\b", r"\bhistorically accurate\b", r"\ba survey (of|found)\b", r"\bsource(s)? (say|says|states)\b",
)
TOP = 10
DEFAULT_ROOT = pathlib.Path("/tmp/l7r-check")
_TAGS = re.compile(r"<!--\s*tags:\s*([^>]*?)-->")
_HEAD = re.compile(r"<h[23][^>]*>(.*?)</h[23]>", re.S)


def visible(text: str) -> str:
    """A page's reader-visible words: comments and tags out, entities unescaped, whitespace folded."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<!--.*?-->", " ", text, flags=re.S))).split())


def heading(text: str) -> str:
    m = _HEAD.search(text)
    return visible(m.group(1)) if m else ""


def subjects(text: str) -> list[str]:
    m = _TAGS.search(text)
    if not m:
        return []
    for part in m.group(1).split(";"):
        k, _, v = part.strip().partition("=")
        if k.strip() == "subject":
            return [t.strip() for t in v.split(",") if t.strip()]
    return []


def question_pages(root: pathlib.Path) -> list[pathlib.Path]:
    """Every question and drawing page - not the notes, not the originals."""
    return [p for p in sorted((root / QUESTIONS).glob("*.html")) if not p.name.endswith((".notes.html", ".originals.html"))]


def terms_of(root: pathlib.Path, m: mo.Modal) -> list[str]:
    """The kind's words: its name, its key, and every glossary variant of either."""
    base = {t.lower() for t in (m.tags.get("Name", ""), m.key) if t}
    out = set(base)
    if (root / VARIANTS).is_file():
        for line in (root / VARIANTS).read_text(encoding="utf-8").splitlines():
            variant, _, term = line.partition("\t")
            if term.lower() in base or variant.lower() in base:
                out |= {variant.lower(), term.lower()}
    return sorted(out, key=len, reverse=True)


def candidates(root: pathlib.Path, m: mo.Modal) -> list[tuple[int, str, str, list[str], int, str]]:
    """(score, file, heading, tags, term hits, first words) for every candidate, best first - the UNION rule, never cut."""
    entry = set(m.entry_files())
    tags = {t for f in entry if (root / SKILL / f).is_file() for t in subjects((root / SKILL / f).read_text(encoding="utf-8"))}
    terms = terms_of(root, m)
    pat = re.compile(r"\b(" + "|".join(re.escape(t) for t in terms) + r")\b", re.I) if terms else None
    out = []
    for p in question_pages(root):
        rel = str(p.relative_to(root / SKILL))
        if rel in entry:
            continue
        text = p.read_text(encoding="utf-8")
        words = visible(text)
        page_tags = subjects(text)
        shared = tags & set(page_tags)
        hits = len(pat.findall(words)) if pat else 0
        if not shared and not hits:
            continue
        score = 3 * min(hits, 20) + 5 * len(shared)
        out.append((score, rel, heading(text), page_tags, hits, words[:280]))
    return sorted(out, key=lambda c: (-c[0], c[1]))


def render(root: pathlib.Path, m: mo.Modal) -> str:
    """The modal as its reader meets it: the heading, each tab's text, and the questions the References tab lists."""
    lines = [f"# {m.tags.get('Name', m.key)}", "", f"class `{m.cls}` (key `{m.key}`), form `{m.form}`, origin `{m.origin}`", "", "## About", ""]
    lines += [p + "\n" for p in m.tags.get("About", "").split("\n\n") if p.strip()]
    lines.append("(The page adds the generated sibling line - 'Not to be confused with ...' - at the foot of About.)\n")
    guesses = [g[2:] for g in m.tags.get("Guesses", "").splitlines() if g.strip()]
    lines += ["## Guesses", ""] + ([f"- {g}" for g in guesses] if guesses else ["(no Guesses tab - nothing guessed)"]) + [""]
    lines += ["## References", ""]
    for f in m.entry_files():
        p = root / SKILL / f
        lines.append(f"- {heading(p.read_text(encoding='utf-8')) if p.is_file() else '(MISSING FILE)'}  - `{f}`")
    lines += ["", f"Sources: {m.tags.get('Sources', '')}", ""]
    return "\n".join(lines)


def prepass(root: pathlib.Path, m: mo.Modal) -> str:
    about = m.tags.get("About", "")
    n = len(about.split())
    lo, hi = BAND.get(m.form, BAND["standard"])
    out = [f"prepass - {m.cls} ({m.form})", f"- About words: {n} (band {lo}-{hi}){'' if lo <= n <= hi else '  <- OUTSIDE THE BAND'}"]
    for pat in BARRED:
        for hit in re.finditer(pat, about, re.I):
            out.append(f"- barred phrase in About (M11/M16): {hit.group(0)!r} - ...{about[max(0, hit.start() - 50):hit.end() + 50]}...")
    for g in (g[2:] for g in m.tags.get("Guesses", "").splitlines() if g.strip()):
        if len(re.findall(r"[.!?](\s|$)", g)) > 2:
            out.append(f"- a guess past two sentences (M3): {g[:90]}...")
    for f in m.entry_files():
        if not (root / SKILL / f).is_file():
            out.append(f"- Entry names no file: {f}")
    if not m.entry_files():
        out.append("- Entry names no question file")
    if len(out) == 2:
        out.append("- nothing else found")
    return "\n".join(out) + "\n"


def owed_lines(root: pathlib.Path, m: mo.Modal, for_: str) -> str:
    """The MANIFEST's owed section in `_bundle_owed`'s shape: `owed-checks:` for the dispatch guard, `unit:` lines for
    `make record-checked BUNDLE=` - each unit this bundle answers, at the fingerprint of the words copied."""
    fp_form, fp_research = mo.fingerprints(root, m)
    if for_ == "modal-form":
        units = [(f"{mo.FORM_CHECK}:{m.key}", fp_form)]
    else:
        units = [(f"{c}:{m.key}", fp_research) for c in mo.RESEARCH_CHECKS]
    return "## Owed (feature 311)\n\n" + f"owed-checks: {for_}\n" + "".join(f"unit: {s} {fp}\n" for s, fp in units)


def bundle(root: pathlib.Path, kind: str, for_: str, out_arg: str) -> int:
    m = mo.find(root, kind)
    if m is None:
        print(f"modal-bundle: no About-form modal {kind!r} (a class name or key) under {', '.join(mo.MODAL_DIRS)}", file=sys.stderr)
        return 2
    out = pathlib.Path(out_arg) if out_arg else DEFAULT_ROOT / f"modal-{re.sub(r'[^a-z0-9]+', '-', m.key)}-{for_}"
    if out.exists():
        if not (out / "MANIFEST.md").is_file():
            print(f"modal-bundle: {out} exists and is not a bundle - choose another OUT", file=sys.stderr)
            return 2
        shutil.rmtree(out)
    out.mkdir(parents=True)
    rows: list[tuple[str, str, str]] = []

    def put(name: str, text: str, origin: str, what: str) -> None:
        (out / name).parent.mkdir(parents=True, exist_ok=True)
        (out / name).write_text(text, encoding="utf-8")
        rows.append((name, origin, what))

    put("modal.md", render(root, m), m.origin, "the modal as its reader meets it - the thing you judge")
    guide = GUIDELINES.get(m.form, GUIDELINES["standard"])
    put("guidelines.md", (root / guide).read_text(encoding="utf-8"), str(guide), "the rules - your contract; name a rule (M#/P#) in every finding")
    put("prepass.txt", prepass(root, m), "scripts/_modal_bundle.py", "the mechanical findings - rule on each")
    grep_targets: list[str] = []
    if for_ == "modal-research":
        for f in m.entry_files():
            p = root / SKILL / f
            if p.is_file():
                # the page itself, not its notes: accuracy is judged against what the page TELLS its reader; whether a
                # footnote's passage says it is quote-check's (feature 319 T07: the notes made the bundle 380 KB)
                put(f"entry/{p.name}", p.read_text(encoding="utf-8"), str(SKILL / f), "a page the modal's Entry names - what its statements must rest on")
        cands = candidates(root, m) if m.form == "standard" else []
        listing = [f"# Candidates for {m.cls} - {len(cands)}, best first (the UNION rule; never cut)", ""]
        for i, (score, rel, head, tags, hits, first) in enumerate(cands):
            listing.append(f"{i + 1}. `{rel}` - {head}  [tags {','.join(tags) or '-'}; term hits {hits}; score {score}]")
            if i < 30:
                listing.append(f"   {first}")
        put("candidates.md", "\n".join(listing) + "\n", "scripts/_modal_bundle.py", "every question that may answer what the modal leaves open (gaps) - the top ten are files under cand/, every page under record/")
        (out / "cand").mkdir()
        for _score, rel, *_ in cands[:TOP]:
            shutil.copyfile(root / SKILL / rel, out / "cand" / pathlib.Path(rel).name)
        grep_targets.append("cand/")
        (out / "record").mkdir()
        for p in question_pages(root):
            shutil.copyfile(p, out / "record" / p.name)
        grep_targets.append("record/")
    manifest = [
        f"# Check bundle - modal {m.cls}, for {for_}",
        "",
        f"Written {datetime.date.today().isoformat()} by `make modal-bundle`. Every file here is a COPY. Read these and nothing under "
        "the repository (feature 250). A finding names the ORIGIN column - the file the session will edit.",
        "",
        "**Everything you need is in THIS file**, each copy under its origin below; read it once."
        + (" Beside it, NOT inlined: `cand/` (the top ten candidates, each a file to Read when its line in `candidates.md` looks"
           " like an answer) and `record/` (every question page - a GREP target; never read it whole)." if grep_targets else ""),
        "",
        "| file | origin | what it is for |",
        "|---|---|---|",
        *(f"| `{f}` | `{o}` | {w} |" for f, o, w in rows),
        "",
    ]
    for name, origin, _what in rows:
        manifest.append(f"## `{name}` - origin `{origin}`\n\n```\n{(out / name).read_text(encoding='utf-8').rstrip()}\n```\n")
    manifest.append("Reply with your report: the counts on the first line, then only what the session must act on (your contract gives the form).\n")
    (out / "MANIFEST.md").write_text("\n".join(manifest) + "\n" + owed_lines(root, m, for_), encoding="utf-8")
    print(f"modal-bundle: {len(rows)} file(s) in {out} - hand the {for_} agent {out / 'MANIFEST.md'}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("kind")
    ap.add_argument("--for", dest="for_", default="modal-form", choices=("modal-form", "modal-research"))
    ap.add_argument("--out", default="")
    ap.add_argument("--root", default=".")
    ap.add_argument("--prepass", action="store_true")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    if args.prepass:
        m = mo.find(root, args.kind)
        if m is None:
            print(f"modal-prepass: no About-form modal {args.kind!r}", file=sys.stderr)
            return 2
        sys.stdout.write(prepass(root, m))
        return 0
    return bundle(root, args.kind, args.for_, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
