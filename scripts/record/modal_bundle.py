#!/usr/bin/env python3
"""A modal check's BUNDLE and its PREPASS (feature 319, plan D5) - what `modal-form` or `modal-research` reads, copied OUT of the
repository as every record check's bundle is (feature 250: an agent that reads a file under the repository is handed every
`CLAUDE.md` above it).

    modal_bundle.py KIND [--for modal-form|modal-research] [--out DIR]    the bundle; KIND is a class name or key
    modal_bundle.py KIND --prepass                                         the prepass alone, printed

THE BUNDLE. `modal.md` - the modal as its reader meets it, tab by tab, with its origin; `guidelines.txt`, naming which guidelines its form takes (the rules themselves are in the agent files, feature 383 amendment 6)
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
import os
import pathlib
import re
import shutil
import sys
from collections.abc import Sequence
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import earlier_rounds  # noqa: E402
import modal_owed as mo  # noqa: E402

QUESTIONS = pathlib.Path("research/questions")
VARIANTS = pathlib.Path("research/assets/glossary-variants.txt")
GUIDELINES = {"standard": pathlib.Path("dev/modals.md"), "particular": pathlib.Path("dev/modals-particular.md")}
#: the About tab's word band, per form (`dev/modals.md` M3, `dev/modals-particular.md` P3)
BAND = {"standard": (120, 500), "particular": (80, 400)}  # raised from 250 / 200 by the GM, 2026-10-09
#: record talk and the old feature-level label, barred from the About tab (`dev/modals.md` M11, M16)
BARRED = (
    r"\bthis project\b",
    r"\bthe record\b",
    r"\bpages? (we )?read\b",
    r"\bno page\b",
    r"\bGUESS\b",
    r"\bThis is a guess\b",
    r"\bthis is a deliberate deviation\b",
    r"\bhistorically accurate\b",
    r"\ba survey (of|found)\b",
    r"\bsource(s)? (say|says|states)\b",
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
    tags = {t for f in entry if (root / f).is_file() for t in subjects((root / f).read_text(encoding="utf-8"))}
    terms = terms_of(root, m)
    pat = re.compile(r"\b(" + "|".join(re.escape(t) for t in terms) + r")\b", re.I) if terms else None
    out = []
    for p in question_pages(root):
        rel = str(p.relative_to(root))
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


#: a knob condition opening a modal item (FR-015, plan D14), shown to a check as "(only where <knob> is <value>)" - the
#: same form `interactive/conditions.py` reads; this is tooling, so it does not import the engine
_COND = re.compile(r"(^|^- )((?:\[[a-z_]+=[a-z_0-9-]+(?:\|[a-z_0-9-]+)*\])+)\s*", re.M)
_ONE = re.compile(r"\[([a-z_]+)=([a-z_0-9-]+(?:\|[a-z_0-9-]+)*)\]")


def _conditions_shown(text: str) -> str:
    def words(m: re.Match[str]) -> str:
        parts = [f"{k} is {' or '.join(v.split('|'))}" for k, v in _ONE.findall(m.group(2))]
        return f"{m.group(1)}(only where {' and '.join(parts)}) "

    return _COND.sub(words, text)


def render(root: pathlib.Path, m: mo.Modal) -> str:
    """The modal as its reader meets it: the heading, each tab's text, and the questions the References tab lists."""
    lines = [f"# {m.tags.get('Name', m.key)}", "", f"class `{m.cls}` (key `{m.key}`), form `{m.form}`, origin `{m.origin}`", "", "## About", ""]
    lines += [p + "\n" for p in m.tags.get("About", "").split("\n\n") if p.strip()]
    lines.append("(The page adds the generated sibling line - 'Not to be confused with ...' - at the foot of About.)\n")
    guesses = [g[2:] for g in m.tags.get("Guesses", "").splitlines() if g.strip()]
    lines += ["## Guesses", ""] + ([f"- {g}" for g in guesses] if guesses else ["(no Guesses tab - nothing guessed)"]) + [""]
    dep = [p for p in m.tags.get("Depiction", "").split("\n\n") if p.strip()]
    lines += ["## Depiction", ""]
    lines += [p + "\n" for p in dep] if dep else ["(no Depiction paragraphs)\n"]
    for f in m.drawing_files():
        p = root / f
        lines.append(f"- {heading(p.read_text(encoding='utf-8')) if p.is_file() else '(MISSING FILE)'}  - `{f}`")
    if not dep and not m.drawing_files():
        lines.append("(no Depiction tab - nothing to say and no drawing page)")
    lines += ["", "## References", ""]
    for f in m.entry_files():
        p = root / f
        lines.append(f"- {heading(p.read_text(encoding='utf-8')) if p.is_file() else '(MISSING FILE)'}  - `{f}`")
    lines += ["", f"Sources: {m.tags.get('Sources', '')}", ""]
    return _conditions_shown("\n".join(lines))


def prepass(root: pathlib.Path, m: mo.Modal) -> str:
    about = m.tags.get("About", "")
    n = len(about.split())
    lo, hi = BAND.get(m.form, BAND["standard"])
    out = [f"prepass - {m.cls} ({m.form})", f"- About words: {n} (band {lo}-{hi}){'' if lo <= n <= hi else '  <- OUTSIDE THE BAND'}"]
    for pat in BARRED:
        for hit in re.finditer(pat, about, re.I):
            out.append(f"- barred phrase in About (M11/M16): {hit.group(0)!r} - ...{about[max(0, hit.start() - 50) : hit.end() + 50]}...")
    for g in (g[2:] for g in m.tags.get("Guesses", "").splitlines() if g.strip()):
        if len(re.findall(r"[.!?](\s|$)", g)) > 2:
            out.append(f"- a guess past two sentences (M3): {g[:90]}...")
    for f in m.entry_files():
        if not (root / f).is_file():
            out.append(f"- Entry names no file: {f}")
    if not m.entry_files():
        out.append("- Entry names no question file")
    if len(out) == 2:
        out.append("- nothing else found")
    return "\n".join(out) + "\n"


CLAIMS_INDEX = pathlib.Path("dev/claims-index.json")
#: where the pool pages a glyph is cropped from live; the hamlets are searched first (the standardized kinds), then every other
#: pool tree - read off the directory, never named here (a building type is named only in its declaration, `buildings/types.json`)
POOL = pathlib.Path("pool")
HAMLETS = "hamlets"


def claims_citing(root: pathlib.Path, files: Sequence[str]) -> list[str]:
    """The claims-index rows whose cited pages include any of `files` - the engine's own account of how it draws the kind,
    each with its verdict (a DRIFTED row is a variety the record names and the code does not draw - plan D13)."""
    import json  # noqa: PLC0415

    path = root / CLAIMS_INDEX
    if not path.is_file() or not files:
        return []
    names = {pathlib.Path(f).name for f in files}
    out = []
    for key, row in sorted(json.loads(path.read_text(encoding="utf-8")).items()):
        if any(n in str(row.get("pages", "")) for n in names):
            out.append(f"- {row.get('verdict', '?')} | `{key.split('l7r/diagram/', 1)[-1]}` | {row.get('note', '')}")
    return out


def pool_page_with(root: pathlib.Path, key: str, sheet: bool = False) -> pathlib.Path | None:
    """The first pool page that draws the kind `key` (its page carries `data-k="<key>"`), hamlets first, and a sheet the GM
    drew before a placer's draft: a `-test` page (the round trip of feature 008, whose divergence from the hand sheet is the
    point of it) is never the crop, and an `-example` page comes after the hand sheets (feature 319, sheet round 1: the
    cinnabar workshop was judged against the round-trip's plain rect). A SHEET kind is looked for on the sheets alone: its
    key may name a hamlet kind too, and the compound garden's crop came out a hamlet's kitchen garden."""
    # the page writes its attribute values ESCAPED: every key with an apostrophe (`clerks' seats`, `magistrate's dais`) was on
    # no page by the raw mark, and its depiction check ran with no crop (343's clerks--seats ruling, 2026-10-11)
    marks = {f'data-k="{key}"', f'data-k="{html.escape(key, quote=True)}"'}
    trees = sorted((p for p in (root / POOL).iterdir() if p.is_dir()), key=lambda p: (p.name != HAMLETS, p.name)) if (root / POOL).is_dir() else []
    for d in (t for t in trees if not (sheet and t.name == HAMLETS)):
        pages = [p for p in d.glob("*/*.html") if not p.parent.name.endswith("-test")]
        for page in sorted(pages, key=lambda p: (p.parent.name.endswith("-example"), p.name)):
            with open(page, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
                if any(mk in text for mk in marks):
                    return page
    return None


_CROP = """
import sys
from playwright.sync_api import sync_playwright
page_path, key, out = sys.argv[1], sys.argv[2], sys.argv[3]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 900})
    pg.goto("file://" + page_path); pg.wait_for_timeout(2500)
    sel = 'g.f[data-k="' + key + '"]'
    # THE FIRST GLYPH, not the class group: the group spans every instance on the map (a hamlet's gardens run its whole
    # width), so measuring it never zoomed - the garden's crop came out as the whole hamlet (feature 319, the garden pilot).
    # The first leaf shape with a box on screen is one glyph's part; the group is the fallback.
    JS = ("(s) => { const g = document.querySelector(s); if (!g) return null;"
          " const leaf = [...g.querySelectorAll('polygon,rect,path,ellipse,circle,line')].find(e => e.getBoundingClientRect().width > 0);"
          " const r = (leaf || g).getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }")
    # ...AND MEASURED WHILE SHOWN: below the raster scale the page hides every class group (0 x 0), so a measure there found
    # nothing and the zoom never centered on a glyph. The kind is shown for the measure alone and hidden again for the shot.
    SHOW = "(s) => { const st = document.createElement('style'); st.id = 'crop-probe'; st.textContent = s + ', ' + s + ' * { display: inline !important; }'; document.head.appendChild(st); }"
    HIDE = "() => { const st = document.getElementById('crop-probe'); if (st) st.remove(); }"
    def rect():
        pg.evaluate(SHOW, sel)
        got = pg.evaluate(JS, sel)
        pg.evaluate(HIDE)
        return got
    for _ in range(14):
        x, y, w, h = rect()
        if w > 200 or h > 200: break
        pg.mouse.move(x + w / 2, y + h / 2)
        pg.keyboard.down("Control"); pg.mouse.wheel(0, -240); pg.keyboard.up("Control")
        pg.wait_for_timeout(200)
    x, y, w, h = rect()
    pg.mouse.move(2, 2); pg.wait_for_timeout(150)  # off the glyph, so it is not drawn lit
    # ...AND NEVER LIT: zoomed in, a large glyph (a Mode A kitchen, an archive) fills the viewport, so the corner the mouse
    # leaves for is ON it and the shot showed the page's highlight, not the drawn fill (feature 372 wave 105; fixed feature
    # 374 wave 113, FR-007). The lit state is cleared outright, and the clip takes the glyph's whole box, at least 600 x 500.
    pg.evaluate("() => document.querySelectorAll('g.f.on').forEach(g => g.classList.remove('on'))"); pg.wait_for_timeout(100)
    cx, cy = x + w / 2, y + h / 2
    cw, ch = min(1200, max(600, w + 60)), min(900, max(500, h + 60))
    clip = {"x": max(0, min(cx - cw / 2, 1200 - cw)), "y": max(0, min(cy - ch / 2, 900 - ch)), "width": cw, "height": ch}
    pg.screenshot(path=out, clip=clip)
    # every kind with a part inside the crop: a click on it opens that kind's pop-up (343's office-hall ruling - the check could
    # not tell whether the hall's front band opens office-hall or magistrate's dais)
    KINDS = ("(c) => { const st = document.createElement('style'); st.textContent = 'g.f, g.f * { display: inline !important; }';"
             " document.head.appendChild(st); const out = new Set();"
             " document.querySelectorAll('g.f[data-k]').forEach(g => { for (const e of g.querySelectorAll('polygon,rect,path,ellipse,circle,line')) {"
             " const r = e.getBoundingClientRect(); if (r.width > 0 && r.x < c.x + c.width && r.x + r.width > c.x && r.y < c.y + c.height && r.y + r.height > c.y) { out.add(g.dataset.k); break; } } });"
             " st.remove(); return [...out]; }")
    open(out + ".kinds", "w").write(chr(10).join(sorted(pg.evaluate(KINDS, clip))))
    b.close()
"""


def drawn_geometry(page: pathlib.Path, key: str) -> str:
    """The kind's first glyph's drawn parts as the sheet's markup gives them (each shape's tag and geometry attributes, in the
    page's own units, with its viewBox) - so a size the pop-up states ("27 by 7 ft") can be checked against what is drawn even
    with no crop (343's clerks--seats ruling, 2026-10-11)."""
    text = page.read_text(encoding="utf-8", errors="replace")
    at = max(text.find(f'data-k="{key}"'), text.find(f'data-k="{html.escape(key, quote=True)}"'))
    if at < 0:
        return ""
    chunk = text[at : at + 4000]
    chunk = chunk[: m.start()] if (m := re.search(r"<g[^>]*\bclass=\"f ", chunk[1:])) else chunk
    shapes = re.findall(r"<(rect|polygon|path|ellipse|circle|line)\b([^>]*)>", chunk)[:8]
    keep = re.compile(r'(?<![\w-])(x|y|width|height|points|d|cx|cy|r|rx|ry|x1|y1|x2|y2|transform)="([^"]{0,200})"')  # not stroke-width
    lines = [f"- <{tag}> " + " ".join(f'{a}="{v}"' for a, v in keep.findall(attrs)) for tag, attrs in shapes]
    box = re.search(r'viewBox="([^"]*)"', text)
    return (f"\nThe first glyph's drawn parts on `{page.name}` (the page's units; viewBox {box.group(1) if box else '?'}; its scale bar names the feet):\n" + "\n".join(lines) + "\n") if lines else ""


def click_target(root: pathlib.Path, key: str, m: mo.Modal) -> str:
    """The pop-up a click on kind `key` opens: the About-form modal of that key in the same registry as `m`, or the key."""
    registry = m.uid.split("/", 1)[0]
    hit = next((x for x in mo.modals_now(root) if x.key == key and x.uid.startswith(registry + "/")), None)
    return f"`{hit.uid}`" if hit else f"the `{key}` pop-up"


def glyph_crop(page: pathlib.Path, key: str, out: pathlib.Path) -> bool:
    """A 600 x 500 crop of the kind's first glyph on a pool page, zoomed until it is about 200 px across - what
    `modal-depiction` compares the tab with (plan D13). False when the browser is not there or the glyph cannot be found."""
    import subprocess  # noqa: PLC0415

    got = subprocess.run([sys.executable, "-c", _CROP, str(page), key, str(out)], capture_output=True, text=True, check=False, timeout=180)
    return got.returncode == 0 and out.is_file()


def drawing_candidates(root: pathlib.Path, m: mo.Modal) -> list[str]:
    """The drawing pages the modal's KIND may rest on beyond its own `Drawing:` list (the plan review of D13, round 2: a
    conversion that leaves `Drawing:` empty must still be judged against the pages its kind has): the "how our maps draw it"
    page beside each research question its `Entry:` names, and any drawing page its file listed at the merge base."""
    import record_owed as ro  # noqa: PLC0415

    out: list[str] = []
    for f in m.entry_files():
        if f.endswith(".html") and not f.endswith(".drawing.html"):
            sibling = f[: -len(".html")] + ".drawing.html"
            if (root / sibling).is_file():
                out.append(sibling)
    base = ro.merge_base(root)
    # in EITHER form: FR-012 keeps every conversion off main, so at the base a kind is in the old form and its drawing pages
    # sit under its `Entry:` (plan review of D13, round 3: the About-only read made this leg blind for every modal)
    was = mo.modals_at(root, base, about_only=False).get(m.uid) if base else None
    if was is not None:
        out += [f for f in (*was.entry_files(), *was.drawing_files()) if f.endswith(".drawing.html")]
    # ...and every drawing page a LISTED one links to: the windbreak's 0072 sends its reader to 0080 for the crowns it draws,
    # and the check was never shown 0080 (feature 319, the windbreak's modal-depiction round 1)
    for f in m.drawing_files():
        p = root / f
        if p.is_file():
            out += [f"research/questions/{h}" for h in re.findall(r'href="(?:[^"]*/)?(\d{4}-[^"/#]+\.drawing\.html)', p.read_text(encoding="utf-8"))]
    listed = set(m.drawing_files())
    return [f for f in dict.fromkeys(out) if f not in listed and (root / f).is_file()]


ENGINE = HERE.parents[1] / "l7r" / "diagram"


def knobs_note(doc: str) -> str:
    """Where the kind is drawn, for each knob the modal's conditions name: its forms and default, the typing rule that says
    which settlements may take each form, and the engine lines that set or read it. A LINKS finding on a conditional Drawing:
    link was ruled without knowing whether a whole dike-pond hamlet carries `land_use_overlay=mulberry_fishpond` (feature 374,
    the round arbiter's tooling fix). '' when the modal names no knob."""
    names = list(dict.fromkeys(re.findall(r"\[([a-z_]+)=[a-z_0-9|-]+\]", doc)))
    if not names:
        return ""
    import inspect  # noqa: PLC0415

    sys.path.insert(0, str(HERE.parents[1]))
    from l7r.diagram.interactive import conditions  # noqa: PLC0415
    from l7r.diagram.settlement._knobs import KNOBS  # noqa: PLC0415

    forms = conditions.knobs()  # populates the registry
    parts = ["# The knobs this modal's conditions name - which maps draw what it conditions\n"]
    for name in names:
        k = KNOBS.get(name)
        parts.append(f"## {name}\n\nforms: {', '.join(forms.get(name, ())) or '(not registered)'}" + (f"; default {k.default}" if k else "") + "\n")
        if k is not None and getattr(k, "typing_rule", None) is not None:
            parts.append("The typing rule (which settlements may take each form):\n\n```python\n" + inspect.getsource(k.typing_rule) + "```\n")
        hits = [
            f"{f.relative_to(ENGINE.parents[1])}:{i}: {line.strip()}"
            for f in sorted(ENGINE.rglob("*.py"))
            for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1)
            if f'"{name}"' in line and " - " not in line
        ][:15]
        parts.append("Where the engine sets or reads it:\n\n" + ("\n".join(f"- `{h}`" for h in hits) or "- (no line names it)") + "\n")
    return "\n".join(parts)


def stale_page(page: pathlib.Path, root: pathlib.Path) -> str:
    """Why a pool page is older than the drawing it was written from, or '' (feature 374 wave 126: a stables crop came from
    a page rendered before the sheet's redraw, and the check judged the old stable). The page is written beside its `.svg`
    by the map's generator; an `.svg` edited later is not on the page until the map is regenerated."""
    svg = page.with_suffix(".svg")
    if svg.is_file() and svg.stat().st_mtime > page.stat().st_mtime + 1.0:
        return f"{page.name} is older than {svg.name} - its crop would show the drawing before the edit; regenerate it first: make map GEN={page.with_suffix('.gen.py').relative_to(root)}"
    return ""


def depiction_parts(root: pathlib.Path, m: mo.Modal, put, out: pathlib.Path, grep_targets: list[str]) -> None:  # noqa: ANN001
    """What `modal-depiction` reads beyond the modal and the rules: each drawing page its `Drawing:` lists and each CANDIDATE
    its kind has (`drawing_candidates`), whole; the claims citing any of them; and the glyph's crop (plan D13)."""
    for f in m.drawing_files():
        p = root / f
        if p.is_file():
            put(f"drawing/{p.name}", p.read_text(encoding="utf-8"), f, "LISTED - a page the modal's Drawing: names - how our maps draw it")
    candidates = drawing_candidates(root, m)
    for f in candidates:
        p = root / f
        put(
            f"drawing/{p.name}",
            p.read_text(encoding="utf-8"),
            f,
            "CANDIDATE - NOT on the modal's Drawing: list, but its kind's (beside an Entry question, or listed before this change): is it owed a link?",
        )
    if note := knobs_note(m.doc):
        put(
            "knobs.md",
            note,
            "l7r/diagram/settlement/_knobs.py",
            "which maps draw what the modal's conditions name: each knob's forms, typing rule and engine lines - read it before ruling on a conditional link",
        )
    rows = claims_citing(root, [*m.drawing_files(), *candidates])
    put(
        "claims.md",
        "# The engine's research claims citing these drawing pages (verdict | unit | note)\n\n" + ("\n".join(rows) if rows else "(none)") + "\n",
        str(CLAIMS_INDEX),
        "the code's own account of how it draws the kind - a DRIFTED row is a variety the record names and the code does not draw",
    )
    page = pool_page_with(root, m.key, sheet=m.uid.startswith("sheet/"))
    if page is not None and (why := stale_page(page, root)):
        raise SystemExit(f"modal-bundle: {why}")
    crop = out / "glyph.png"
    shape = drawn_geometry(page, m.key) if page is not None else ""
    if page is not None and glyph_crop(page, m.key, crop):
        grep_targets.append("glyph.png")
        kinds_file = pathlib.Path(str(crop) + ".kinds")
        kinds = [k for k in kinds_file.read_text(encoding="utf-8").splitlines() if k] if kinds_file.is_file() else []
        kinds_file.unlink(missing_ok=True)
        clicks = "".join(f"\n- `{k}` opens {click_target(root, k, m)}" for k in kinds)
        put(
            "glyph.txt",
            f"glyph.png beside this MANIFEST: the kind `{m.key}` as drawn on `{page.relative_to(root)}`, zoomed until its first glyph is about 200 px across; Read it as an image.\n"
            + (f"\nThe kinds with a part in the crop - a click on each opens its own pop-up:{clicks}\n" if clicks else "")
            + shape,
            str(page.relative_to(root)),
            "where the crop came from - Read glyph.png",
        )
    else:
        why = f"the browser could not crop it from `{page.relative_to(root)}` (the kind IS drawn there)" if page is not None else f"the kind `{m.key}` is drawn on no pool page"
        put(
            "glyph.txt",
            f"no crop: {why} - judge from the drawing pages, the claims and the geometry below, and say so.\n" + shape,
            "scripts/record/modal_bundle.py",
            "why there is no crop, and the drawn geometry",
        )


def research_held(root: pathlib.Path, uid: str, text: str) -> list[str]:
    """The wording `modal-research` rounds fixed on the pop-up `uid` that still stands in `text`: each research EDIT's new text,
    from the replies the check state kept. A form round may not drop or widen it - on 343's border-court a form fix undid a
    research fix's scope words unseen ("no page on the formal entrance" -> "nothing known of the formal entrance"; the round
    arbiter's ruling, 2026-10-11). `apply_edits.py` refuses a modal-form EDIT that drops one."""
    sys.path.insert(0, str(HERE.parent / "hooks" / "lib"))
    import hm_checks as hc  # noqa: PLC0415

    state = hc.load(hc.state_path(str(root)) or pathlib.Path("/nonexistent"))
    out: list[str] = []
    for v in sorted(state.get("dispatches", {}).values(), key=lambda v: v.get("t", 0)):
        if v.get("check") != "modal-research" or f"modal:{uid}" not in v.get("subjects", []):
            continue
        rp = pathlib.Path(str(v.get("reply") or ""))
        reply = rp.read_text(encoding="utf-8") if v.get("reply") and rp.is_file() else ""
        if not reply and v.get("aid"):  # a background check's reply is its transcript's last text (a page session kept no file)
            found = sorted((pathlib.Path.home() / ".claude" / "projects").glob(f"*/*/subagents/agent-{v['aid']}.jsonl"))
            reply = hc._reply_of(str(found[0]), "") if found else ""
        for _p, _o, new in hc._blocks(reply):
            if new.strip() and new in text and new not in out:
                out.append(new)
    return out


def order_hold(root: pathlib.Path, m: mo.Modal, for_: str, units: Sequence[Any]) -> str:
    """Why `for_` must wait on `m`: a check BEFORE it in `modal_owed.ORDER` has a unit on the pop-up owed now and unanswered
    (feature 375 amendment 3, FR-019a) - with the command that answers it; '' when nothing before it is owed."""
    import record_owed  # noqa: PLC0415

    store = record_owed.store(root)
    by_slug = {u.slug: u for u in units}
    for agent in mo.ORDER[: mo.ORDER.index(for_)]:
        for c in mo.AGENT_UNITS[agent]:
            u = by_slug.get(f"{c}:{m.uid}")
            if u is not None and not record_owed.answered(store, u.slug, u.fingerprint, u.reading):
                return (
                    f"{u.slug} is owed and unanswered - a pop-up's checks run in order, form, then research, then depiction "
                    f"(feature 375 amendment 3: run together, each one's edits re-owed the others). First: make modal-bundle "
                    f'KIND="{m.uid}" FOR={agent}'
                )
    return ""


def owed_lines(root: pathlib.Path, m: mo.Modal, for_: str, owed: Sequence[Any] | None = None) -> str:
    """The MANIFEST's owed section in `_bundle_owed`'s shape: `owed-checks:` for the dispatch guard, `unit:` lines for
    `make record-checked BUNDLE=` - each unit this bundle answers, at the fingerprint of the words copied."""
    fp_form, fp_research = mo.fingerprints(root, m)
    if for_ == "modal-form":
        units = [(f"{mo.FORM_CHECK}:{m.uid}", fp_form)]
    elif for_ == mo.DEPICTION_CHECK:
        units = [(f"{mo.DEPICTION_CHECK}:{m.uid}", mo.depiction_fingerprint(root, m))]
    else:
        units = [(f"{c}:{m.uid}", fp_research) for c in mo.RESEARCH_CHECKS]
    # feature 375 (plan D1): the pages this check reads, kept as blobs - a later triage shows what changed since THIS read
    import modal_triage as mt  # noqa: PLC0415

    files = m.drawing_files() if for_ == mo.DEPICTION_CHECK else m.entry_files() if for_ == mo.RESEARCH_AGENT else []
    pages = [(f, b) for f in files if (b := mt.keep(root, f))]
    import record_owed  # noqa: PLC0415 - what made each unit due, read back per round by the arbiter's bundle (374)

    why = {u.slug: u.occasion for u in (owed if owed is not None else record_owed.units(root))}
    return (
        "## Owed (feature 311)\n\n"
        + f"owed-checks: {for_}\n"
        + "".join(f"unit: {s} {fp}\n" for s, fp in units)
        + "".join(f"page: {f} {b}\n" for f, b in pages)
        + "".join(f"owed: {s} - {why[s]}\n" for s, _fp in units if why.get(s))
    )


def bundle(root: pathlib.Path, kind: str, for_: str, out_arg: str, reason: str = "") -> int:
    m = mo.find(root, kind)
    if m is None:
        print(f"modal-bundle: no About-form modal {kind!r} (a class name or key) under {', '.join(mo.MODAL_DIRS)}", file=sys.stderr)
        return 2
    import modal_triage as mt  # noqa: PLC0415 - feature 375 FR-001: a unit owed only a triage is triaged first
    import record_owed  # noqa: PLC0415

    units = record_owed.units(root, families=("modal",), uid=m.uid)  # this pop-up's, once: the triage, the order and the owed lines all read it (amendment 3, plan D27)
    modal_rows = [(u.slug, u.occasion, u.fingerprint) for u in units if u.check in (mo.FORM_CHECK, mo.DEPICTION_CHECK, *mo.RESEARCH_CHECKS)]
    refused = mt.refusal(root, m, for_, modal_rows)
    if refused and len(reason.split()) < 2:
        print(f'modal-bundle: {refused}. A check the GM asked for, or a backfill: REASON="<why>"', file=sys.stderr)
        return 3
    if refused:
        print(f"modal-bundle: bundled without its triage, because: {reason}")
    held, first = order_hold(root, m, for_, units), os.environ.get("CHECK_ORDER_OK", "").strip()
    if held and len(first.split()) < 2:
        print(f'modal-bundle: {held}. To bundle it anyway: CHECK_ORDER_OK="<why>" (two words or more; the MANIFEST records it)', file=sys.stderr)
        return 3
    if held:
        print(f"modal-bundle: bundled out of order, because: {first}")
    out = pathlib.Path(out_arg) if out_arg else DEFAULT_ROOT / f"modal-{m.uid.replace('/', '-')}-{for_}"
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
    put("text.md", m.doc.rstrip() + "\n", m.origin, "the modal's file line for line - an EDIT block's old text is one of these lines (or part of one), exactly, and its target is this origin")
    guide = GUIDELINES.get(m.form, GUIDELINES["standard"])
    # the rules themselves are in the agent's file, its system prompt, which every dispatch of the check reads from the prompt
    # cache; a copy here followed the unique prompt and was written fresh by every dispatch (feature 383 amendment 6, plan D35)
    put(
        "guidelines.txt",
        f"This modal is of the {'particular' if guide == GUIDELINES['particular'] else 'standard'} form: rule on it by "
        f"the guidelines from `{guide}` at the end of your agent file (`make agent-sync` writes them from that source).\n",
        str(guide),
        "which guidelines govern this modal - the rules are in your contract; name a rule (M#/P#) in every finding",
    )
    put("prepass.txt", prepass(root, m), "scripts/record/modal_bundle.py", "the mechanical findings - rule on each")
    grep_targets: list[str] = []
    if for_ == mo.DEPICTION_CHECK:
        depiction_parts(root, m, put, out, grep_targets)
    if for_ == mo.FORM_CHECK and (held := research_held(root, m.uid, m.doc)):
        put(
            "research-held.md",
            "# Wording the research rounds fixed - keep it\n\n" + "\n".join(f"- {h!r}" for h in held) + "\n",
            "scripts/record/modal_bundle.py",
            "what modal-research rounds wrote and the record backs: a form EDIT never drops or widens these words",
        )
    if for_ == "modal-research":
        for f in m.entry_files():
            p = root / f
            if p.is_file():
                # the page itself, not its notes: accuracy is judged against what the page TELLS its reader; whether a
                # footnote's passage says it is quote-check's (feature 319 T07: the notes made the bundle 380 KB)
                put(f"entry/{p.name}", p.read_text(encoding="utf-8"), f, "a page the modal's Entry names - what its statements must rest on")
        cands = candidates(root, m) if m.form == "standard" else []
        listing = [f"# Candidates for {m.cls} - {len(cands)}, best first (the UNION rule; never cut)", ""]
        for i, (score, rel, head, tags, hits, first) in enumerate(cands):
            listing.append(f"{i + 1}. `{rel}` - {head}  [tags {','.join(tags) or '-'}; term hits {hits}; score {score}]")
            if i < 30:
                listing.append(f"   {first}")
        put(
            "candidates.md",
            "\n".join(listing) + "\n",
            "scripts/record/modal_bundle.py",
            "every question that may answer what the modal leaves open (gaps) - the top ten are files under cand/, every page under record/",
        )
        (out / "cand").mkdir()
        for _score, rel, *_ in cands[:TOP]:
            shutil.copyfile(root / rel, out / "cand" / pathlib.Path(rel).name)
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
        + (
            " Beside it, NOT inlined: `cand/` (the top ten candidates, each a file to Read when its line in `candidates.md` looks"
            " like an answer) and `record/` (every question page - a GREP target; never read it whole)."
            if grep_targets
            else ""
        ),
        "",
        "| file | origin | what it is for |",
        "|---|---|---|",
        *(f"| `{f}` | `{o}` | {w} |" for f, o, w in rows),
        "",
    ]
    for name, origin, _what in rows:
        manifest.append(f"## `{name}` - origin `{origin}`\n\n```\n{(out / name).read_text(encoding='utf-8').rstrip()}\n```\n")
    manifest.append("Reply with your report: the counts on the first line, then only what the session must act on (your contract gives the form).\n")
    escape = f"check-order-escape: {first}\n" if held else ""
    text = "\n".join(manifest) + "\n" + owed_lines(root, m, for_, units) + escape
    (out / "MANIFEST.md").write_text(text + earlier_rounds.section(root, out, text), encoding="utf-8")  # feature 393
    print(f"modal-bundle: {len(rows)} file(s) in {out} - hand the {for_} agent {out / 'MANIFEST.md'}")
    return 0


def bundles(root: pathlib.Path, kinds: Sequence[str], for_: str, out_arg: str, reason: str = "") -> int:
    """ONE AGENT FOR SEVERAL POP-UPS OF ONE CHECK (feature 385 T02, plan D12): T01 sent ten agents, one per pop-up, to judge one
    changed page's bullets, each reading the same drawing pages. Each pop-up keeps its own bundle (`bundle`, under `out/<n>-<kind>`),
    answered unit by unit by `make record-checked BUNDLE=<its bundle>` as before; the top MANIFEST hands all of them to one agent
    and carries their `unit:` lines, so the dispatch guard sees what is owed."""
    out = pathlib.Path(out_arg) if out_arg else pathlib.Path("/tmp/l7r-check") / f"modal-batch-{for_}"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    subs: list[pathlib.Path] = []
    for n, kind in enumerate(kinds, start=1):
        sub = out / f"{n:02d}-{re.sub(r'[^A-Za-z0-9]+', '-', kind).strip('-')}"
        code = bundle(root, kind, for_, str(sub), reason)
        if code:
            return code
        subs.append(sub)
    units = [ln for s in subs for ln in (s / "MANIFEST.md").read_text(encoding="utf-8").splitlines() if ln.startswith("unit: ")]
    parts = [
        f"# {len(subs)} pop-ups for {for_}, one agent (feature 385, plan D12)\n",
        f"owed-checks: {for_}\n",
        "Judge EACH pop-up below from its own bundle, as your contract says, and reply with one section per pop-up, headed by "
        "its `unit:` line. The drawing pages repeat from bundle to bundle: read each page once.\n",
        *[f"- `{s / 'MANIFEST.md'}`" for s in subs],
        "",
        # feature 393: the earlier rounds are in each pop-up's own MANIFEST, beside the replies it copied
        *([f"Earlier rounds: {', '.join(f'`{s.name}`' for s in held)} - each MANIFEST's `{earlier_rounds.HEAD}` section.", ""]
          if (held := [s for s in subs if earlier_rounds.HEAD in (s / "MANIFEST.md").read_text(encoding="utf-8")]) else []),
        *units,
    ]
    (out / "MANIFEST.md").write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"modal-bundle: {len(subs)} pop-ups in one bundle - dispatch ONE {for_} agent on {out / 'MANIFEST.md'}; record each with "
          f"make record-checked CHECK={for_} BUNDLE=<its own bundle>")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("kind")
    ap.add_argument("--for", dest="for_", default="modal-form", choices=("modal-form", "modal-research", "modal-depiction"))
    ap.add_argument("--out", default="")
    ap.add_argument("--root", default=".")
    ap.add_argument("--prepass", action="store_true")
    ap.add_argument("--reason", default="", help="bundle a unit owed only a triage anyway (feature 375): why")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    if args.prepass:
        m = mo.find(root, args.kind)
        if m is None:
            print(f"modal-prepass: no About-form modal {args.kind!r}", file=sys.stderr)
            return 2
        sys.stdout.write(prepass(root, m))
        return 0
    kinds = args.kind.split()
    if len(kinds) > 1:  # ...several KIND=s for one check: one agent (feature 385, plan D12)
        return bundles(root, kinds, args.for_, args.out, args.reason)
    return bundle(root, args.kind, args.for_, args.out, args.reason)


if __name__ == "__main__":
    raise SystemExit(main())
