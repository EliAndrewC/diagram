#!/usr/bin/env python3
"""What a pattern can find against the style guide, listed for `record-style` (feature 292).

WHY. The style guide (`research/STYLE.md`) is mostly judgment - whether a title is plain English, whether a lead line
should be a statement or a question - and that is the `record-style` agent's. Two of its rules have a mechanical half,
found exactly and for no tokens, so they are found here and handed over:

- **METRIC WITHOUT A CONVERSION** (STYLE.md 6, GM 2026-09-29: *"any time we expressed something in meters, then we also
  convert it to feet"*): every metric figure in the section's OWN prose - never a quotation, a footnote or a comment -
  with no `(~N ft)`, `(~N in)` or acre/square-foot conversion right after it. This one is a finding, not a candidate.
- **GM IN THE VISIBLE TEXT** (STYLE.md 1, GM 2026-09-29: *"you should not refer to this as a GM ruling"*): every
  visible "GM" - a ruling, a quotation, an acceptance. The ruling belongs in a comment; each is a finding.
- **PARAGRAPH OVER 150 WORDS** (STYLE.md 3, GM 2026-09-29: *"that paragraph is way too long ... that could probably be
  a mechanical check"*): every paragraph, and every bullet's own text, longer than `MAX_WORDS` - a finding. The bar
  sits between the GM's examples: the grove section's two opening paragraphs (133 and 68 words) are fine, its old rule
  paragraph (364) was not; over the whole record on 2026-09-29, the median paragraph was 82 words, the 90th percentile
  192, and 487 of 2,549 were over 150.
- **ABSENCE NOTE IN THE OLD FORM** (STYLE.md 7, GM 2026-09-29: *"the date we searched and what the web searches were is
  not information the human reader needs to see"*): a note of the question opening `no publicly readable source (searched`
  - its search belongs in a comment after the marker and its findings in the visible text, a list where several. A finding.
- **KANJI WITHOUT ITS GLOSS** (STYLE.md 5, GM 2026-09-29/30: *"a transliteration is not a translation"* - kanji in our
  own words must be followed by its translation, in one format, so that a script can hold it): every run of CJK, kana
  or hangul in the question's or its notes' visible text, outside a quotation, an original and a comment, that is not
  immediately followed by `(romaji, "English meaning")`. A finding.
- **SENTENCES RESTING ON AN ABSENCE NOTE** (STYLE.md 4, GM 2026-09-30: *"we explicitly call out pages that we assert exist
  and that we further assert contain data ... but which we are saying do not load ... it looks very suspicious"*): every
  sentence of our prose whose footnote is an absence note - to rule on: it may state what no source gives (a silence) or
  a GUESS of our own, and never what a page we could not read says.
- **LEAD LINES** (STYLE.md 3): every bullet's bold lead line, marked `Q` (a question) or `S` (a statement), with the
  start of its body - the list the agent rules on, statement or question, and whether a newcomer could read it.

    _style_prepass.py <q> --root <repo>      q: a question's number (`0412`, both its pages) or a page's file name (feature 303)
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

#: A metric figure: a number (or a range of two) and a metric unit. `m` alone is matched only as a word, so `5 min` and
#: `2 mm` are told apart by the unit list rather than by luck.
METRIC = re.compile(
    r"(?<![\w.])(\d[\d,]*(?:\.\d+)?(?:\s*(?:-|to)\s*\d[\d,]*(?:\.\d+)?)?)\s*"
    r"(km2|km|ha|m2|cm|mm|m|kilometers?|hectares?|meters?|centimeters?|millimeters?|square meters?)(?![\w])"
)
#: The conversion the guide asks for, right after the figure: `(~36-92 ft)`, `(~4 in)`, `(~2.5 acres)`, `(~120 sq ft)`.
CONVERTED = re.compile(r"^\s*\(~[\d,.\-\sx]+(?:ft|in|acres?|sq ft|square feet|miles?)\b")  # `(~3 x 6 ft)` too
_COMMENT = re.compile(r"<!--.*?-->", re.S)
#: Quoted text keeps its source's own units: a GM ruling in `<q>`, a source's words in corner brackets or quotes.
_QUOTED = re.compile(r"<q>.*?</q>|「.*?」|&quot;.*?&quot;|\"[^\"]*\"", re.S)
_TAG = re.compile(r"<[^>]+>")
#: The longest a paragraph or a bullet's own text may run, in words of visible text (footnote references and comments
#: not counted) - between the GM's accepted 133 and rejected 364; see the module docstring.
MAX_WORDS = 150
_BLOCK = re.compile(r"<p[^>]*>(.*?)</p>|<li[^>]*>(.*?)(?=<ul>|<ol>|</li>)", re.S)
_SUP = re.compile(r"<sup[^>]*>.*?</sup>", re.S)
_OLD_ABSENCE = re.compile(r'<li data-note="([^"]+)">\s*no publicly readable source\s*\(searched', re.S)
_FOREIGN = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af\uf900-\ufaff]+")
#: The one form a term in its own script takes in our words: `垣根 (kakine, "hedge")` - the characters, then the reading
#: and the English meaning, quoted. `translation-check` judges the meaning against the characters when either changes.
GLOSS = re.compile(r'^\s*\(([^()",]+), «([^»]+)»\)')
_ORIG = re.compile(r'<span class="orig"[^>]*>.*?</span>', re.S)


def old_absence(notes_html: str) -> list[str]:
    """The key of each absence note still in the old form - its search visible, in parentheses after the marker."""
    return _OLD_ABSENCE.findall(notes_html)


_GLOSS_QUOTES = re.compile(r'(\([^()",]+, )(?:"|&quot;|“)([^"“”&]+)(?:"|&quot;|”)(\))')


def own_text(html: str) -> str:
    """Our own visible words: quotations, originals (and their placeholders), comments and tags taken out. A gloss's
    quoted meaning is our own English, so its quote marks are set aside (as guillemets) before quotations are cut."""
    kept = _GLOSS_QUOTES.sub(lambda m: f"{m.group(1)}«{m.group(2)}»{m.group(3)}", _ORIG.sub(" ", _COMMENT.sub(" ", html)))
    return re.sub(r"\s+", " ", _TAG.sub(" ", _QUOTED.sub(" ", kept)))


def foreign_in_own_text(html: str) -> list[str]:
    """Each run of CJK, kana or hangul in our own words NOT followed by its `(romaji, "meaning")` gloss, in context."""
    text = own_text(html)
    return [f"{m.group(0)} - ...{text[max(0, m.start() - 40) : m.end() + 20].strip()}..." for m in _FOREIGN.finditer(text) if not GLOSS.match(text[m.end() :])]


def glosses(html: str) -> list[tuple[str, str, str]]:
    """(characters, reading, meaning) for every glossed term in our own words."""
    text = own_text(html)
    out = []
    for m in _FOREIGN.finditer(text):
        g = GLOSS.match(text[m.end() :])
        if g:
            out.append((m.group(0), g.group(1).strip(), g.group(2).strip()))
    return out


_GM = re.compile(r"\bGM(?:'s)?\b")
_LEAD = re.compile(r"<li>\s*<strong>(.*?)</strong>\s*<br>\s*(.*?)(?=</li>|<ul>)", re.S)


def visible_prose(html: str) -> str:
    """The section's own words as its reader meets them, less every quotation and comment."""
    return re.sub(r"\s+", " ", _TAG.sub(" ", _QUOTED.sub(" ", _COMMENT.sub(" ", html))))


def unconverted(html: str) -> list[str]:
    """Each metric figure in the prose with no conversion after it, as `<figure> - ...context...`."""
    text = visible_prose(html)
    out = []
    for m in METRIC.finditer(text):
        if not CONVERTED.match(text[m.end() :]):
            out.append(f"{m.group(0)} - ...{text[max(0, m.start() - 50) : m.end() + 30].strip()}...")
    return out


def gm_mentions(html: str) -> list[str]:
    """Each visible "GM" in the section - quotations included, since a quoted ruling is the thing that must go."""
    text = re.sub(r"\s+", " ", _TAG.sub(" ", _COMMENT.sub(" ", html)))
    return [f"...{text[max(0, m.start() - 40) : m.end() + 60].strip()}..." for m in _GM.finditer(text)]


def long_paragraphs(html: str) -> list[str]:
    """Each paragraph or bullet text over `MAX_WORDS` words, as `<n> words - <its start>`."""
    out = []
    for m in _BLOCK.finditer(_COMMENT.sub("", html)):
        words = _TAG.sub(" ", _SUP.sub("", m.group(1) or m.group(2) or "")).split()
        if len(words) > MAX_WORDS:
            out.append(f"{len(words)} words - {' '.join(words[:14])}...")
    return out


_YEAR = re.compile(r"(?<![\d-])1[0-9]{3}(?![\d])")


_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z<(\"“「])")


def absence_sentences(html: str, notes_html: str) -> list[str]:
    """Each sentence of the prose carrying a footnote whose note is an absence note, with the note's key."""
    absent = set(re.findall(r'<li data-note="([^"]+)">\s*no publicly readable source', notes_html))
    out = []
    for block in re.split(r"</?(?:p|li)\b[^>]*>", _COMMENT.sub("", html)):
        block = re.sub(r"([.!?])((?:<sup[^>]*></sup>)+)", r"\2\1", block)  # a sentence's footnotes stay with it
        for sentence in _SENTENCE_END.split(block):
            keys = [k for k in re.findall(r'data-note="([^"]+)"', sentence) if k in absent]
            if keys:
                words = re.sub(r"\s+", " ", _TAG.sub("", sentence)).strip()
                out.append(f"[{', '.join(keys)}] {words[:220]}")
    return out


def lead_line_years(html: str, glossary_words: set[str]) -> list[str]:
    """Each year in a lead line, and whether the glossary defines it - a skimmer meets the lead line alone (STYLE.md 3,
    GM 2026-09-29), so a year it leans on is explained in the line or is a tooltip."""
    out = []
    for m in _LEAD.finditer(_COMMENT.sub("", html)):
        lead = re.sub(r"\s+", " ", _TAG.sub("", m.group(1))).strip()
        for y in _YEAR.findall(lead):
            out.append(f"{y} ({'a glossary tooltip' if y in glossary_words else 'NOT in the glossary'}) - {lead}")
    return out


def lead_lines(html: str) -> list[str]:
    """Each bullet's lead line, `Q` or `S`, with the start of its body."""
    out = []
    for m in _LEAD.finditer(_COMMENT.sub("", html)):
        lead = re.sub(r"\s+", " ", _TAG.sub("", m.group(1))).strip()
        body = re.sub(r"\s+", " ", _TAG.sub("", m.group(2))).strip()
        out.append(f"{'Q' if lead.endswith('?') else 'S'}  {lead}  |  {body[:110]}")
    return out


def report(fragments: dict[str, str], glossary_words: set[str] | None = None, notes: dict[str, str] | None = None) -> str:
    """The prepass text for the named question fragments; `notes` (their notes files, by question name) add the two
    lists read from the footnotes - the old-form absence notes and foreign script in our own words."""
    lines = []
    for name, html in fragments.items():
        note_html = (notes or {}).get(name, "")
        old, foreign = old_absence(note_html), foreign_in_own_text(html) + foreign_in_own_text(note_html)
        metric, leads, gm, long = unconverted(html), lead_lines(html), gm_mentions(html), long_paragraphs(html)
        years = lead_line_years(html, glossary_words or set())
        resting = absence_sentences(html, note_html)
        lines.append(f"== {name}")
        lines.append(f"METRIC WITHOUT A CONVERSION ({len(metric)}) - each is a FAIL of STYLE.md 6:")
        lines += [f"  {x}" for x in metric] or ["  none"]
        lines.append(f"GM IN THE VISIBLE TEXT ({len(gm)}) - each is a FAIL of STYLE.md 1 (the ruling goes in a comment):")
        lines += [f"  {x}" for x in gm] or ["  none"]
        lines.append(f"PARAGRAPH OVER {MAX_WORDS} WORDS ({len(long)}) - each is a FAIL of STYLE.md 3 (split it, or make it a list):")
        lines += [f"  {x}" for x in long] or ["  none"]
        lines.append(f"ABSENCE NOTE IN THE OLD FORM ({len(old)}) - each is a FAIL of STYLE.md 7 (search into a comment, findings visible):")
        lines += [f"  {x}" for x in old] or ["  none"]
        lines.append(f"KANJI WITHOUT ITS GLOSS ({len(foreign)}) - each is a FAIL of STYLE.md 5: follow it with (romaji, \"English meaning\"), or drop it:")
        lines += [f"  {x}" for x in foreign] or ["  none"]
        lines.append(f"SENTENCES RESTING ON AN ABSENCE NOTE ({len(resting)}) - rule on each: a silence or our own GUESS, never what an unread page says:")
        lines += [f"  {x}" for x in resting] or ["  none"]
        lines.append(f"YEARS IN LEAD LINES ({len(years)}) - rule on each: is its significance given in the line, or by its tooltip?")
        lines += [f"  {x}" for x in years] or ["  none"]
        lines.append(f"LEAD LINES ({len(leads)}) - rule on each: statement or question (STYLE.md 3), and readable from what precedes it:")
        lines += [f"  {x}" for x in leads] or ["  none"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("q", help="a question's number (0412) or a page's file name, comma-separated for several")
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _hm_record import fragments_for  # noqa: PLC0415

    rels = [r for r in fragments_for(args.q, str(root)) if not r.endswith(".notes.html")]
    if not rels:
        print(f"style-prepass: no question is {args.q!r} - name one by its number, e.g. make style-prepass Q=0041", file=sys.stderr)
        return 2
    variants = root / ".claude/skills/diagram/research/assets/glossary-variants.txt"
    words = {line.split("\t", 1)[0] for line in variants.read_text(encoding="utf-8").splitlines()} if variants.is_file() else set()
    notes = {}
    for r in rels:
        n = root / (r[: -len(".html")] + ".notes.html")
        if n.is_file():
            notes[pathlib.Path(r).name] = n.read_text(encoding="utf-8")
    print(report({pathlib.Path(r).name: (root / r).read_text(encoding="utf-8") for r in rels}, words, notes), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
