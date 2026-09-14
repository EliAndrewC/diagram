#!/usr/bin/env python3
"""Apply feature 242's footnotes to one research page from a JSON list of notes - mechanically, once.

Usage: python3 .../apply_notes.py <page.html> <notes.json> [--dry-run]

Each note: {"line": N, "sentence": "...", "form": "citation|absence|grounds",
            "key": ..., "url": ..., "quote": ..., "translation": ..., "original": ..., "gloss": ...,
            "searched": "...", "reasons": ["a drawing convention"], "registry": {"citation": ..., "what": ..., "why": ..., "used": ...}}

What it does, per note: allocates the next `fn-n` on the page's citations page; appends the `<li>` in the
exact form the record's tests read (`tests/interactive/test_footnotes.py`: a CITATION carries the key link and a
「」 quotation; an ABSENCE note opens `no publicly readable source (searched YYYY-MM-DD: ...)` and carries no key
or link; a GROUNDS note opens `no source is owed:` with reasons from the closed list); inserts the
`<sup class="fn">` at the END of the located sentence on the research page (visible text mapped back to the raw
HTML, past closing punctuation and a closing inline tag); adds a new key to the section's `Sources:` roster;
and appends a new registry entry to `SOURCES.html`'s Works cited when `registry` is given and the key is new.
The session still reads every diff: this places what the readers returned, it decides nothing.
"""
from __future__ import annotations

import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
RESEARCH = HERE.parents[2] / ".claude" / "skills" / "diagram" / "research"
TODAY = "2026-09-14"


def visible_map(raw: str) -> tuple[str, list[int]]:
    """Visible text of one raw HTML line and, per visible char, its index in raw."""
    out: list[str] = []
    idx: list[int] = []
    i = 0
    n = len(raw)
    while i < n:
        if raw.startswith("<!--", i):
            j = raw.find("-->", i)
            i = n if j < 0 else j + 3
            continue
        if raw[i] == "<":
            j = raw.find(">", i)
            i = n if j < 0 else j + 1
            continue
        if raw[i] == "&":
            j = raw.find(";", i)
            if 0 < j - i <= 8:
                ch = html.unescape(raw[i : j + 1])
                out.append(ch)
                idx.append(i)
                i = j + 1
                continue
        out.append(raw[i])
        idx.append(i)
        i += 1
    return "".join(out), idx


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def insertion_point(raw: str, sentence: str) -> int:
    """Raw index just after the sentence's end (its last words, then punctuation and a closing inline tag)."""
    vis, idx = visible_map(raw)
    words = norm(html.unescape(re.sub(r"<[^>]+>", "", sentence))).replace("...", " ").split()
    for size in (6, 5, 4, 3):
        if len(words) < size:
            continue
        tail = " ".join(words[-size:])
        pos = vis.find(tail)
        if pos < 0:
            # tolerate a stripped trailing quote/period in the reader's copy
            tail2 = tail.rstrip('."\')')
            pos = vis.find(tail2)
            if pos < 0:
                continue
            tail = tail2
        end_vis = pos + len(tail)
        # THE NOTE GOES AT THE END OF THE SENTENCE, not where the reader's quotation stopped: a reader
        # quotes the load-bearing clause, so extend to the next terminator that ends a sentence (a
        # period, semicolon, question or exclamation mark followed by a space and a capital, a quote
        # mark, or the end of the paragraph), within a bound so a fragment in a list stays put.
        if end_vis < len(vis) and vis[end_vis] not in '.;:!?)"”」' and vis[end_vis - 1] not in '.;!?':
            m2 = re.compile(r'[.;!?](?=["”」)]*(?:\s+[A-Z0-9(<「"“]|\s*$))').search(vis, end_vis, min(len(vis), end_vis + 300))
            if m2:
                end_vis = m2.start()
        # advance past closing punctuation the reader may have dropped
        while end_vis < len(vis) and vis[end_vis] in '.;:,)"”」':
            end_vis += 1
        raw_i = idx[end_vis] if end_vis < len(idx) else len(raw)
        # step past an immediately following closing inline tag
        m = re.match(r"(</(?:strong|em|code|q|a)>)+", raw[raw_i:])
        if m:
            raw_i += m.end()
        return raw_i
    return -1


def li_for(n: int, note: dict, back: str) -> str:
    form = note["form"]
    if form == "citation":
        q = note["quote"].strip()
        if note.get("translation"):
            body = f"「{note['translation'].strip()}」 (translated from the {note.get('language', 'original')} by this project; original: 「{note['original'].strip() if note.get('original') else q}」)"
        else:
            body = f"「{q}」"
        gloss = f" ({note['gloss'].strip()})" if note.get("gloss") else ""
        text = f'<a href="{note["url"]}"><code>{note["key"]}</code></a> - {body}{gloss}'
    elif form == "absence":
        text = f"no publicly readable source (searched {note.get('date', TODAY)}: {note['searched'].strip()})"
    elif form == "grounds":
        text = "no source is owed: " + "; ".join(note["reasons"])
        if note.get("comment"):
            text += f"<!-- {note['comment']} -->"
    else:
        raise SystemExit(f"unknown form {form}")
    return f'<li id="fn-{n}">{text} <a class="fnback" href="{back}#fnref-{n}">back</a></li>'


def main() -> int:
    page = sys.argv[1]
    notes = json.loads(pathlib.Path(sys.argv[2]).read_text())
    dry = "--dry-run" in sys.argv
    ppath = RESEARCH / page
    cpath = RESEARCH / "citations" / page
    depth = page.count("/")
    up = "../" * depth
    cite_href = f"{up}citations/{page}"
    back = "../" * (depth + 1) + page
    src_href = f"{up}SOURCES.html"
    lines = ppath.read_text(encoding="utf-8").split("\n")
    ctext = cpath.read_text(encoding="utf-8")
    stext = (RESEARCH / "SOURCES.html").read_text(encoding="utf-8")
    nmax = max(int(x) for x in re.findall(r'<li id="fn-(\d+)"', ctext))
    new_lis: list[str] = []
    new_entries: list[str] = []
    report: list[str] = []
    for note in sorted(notes, key=lambda d: -d["line"]):  # bottom-up so line numbers stay valid
        nmax += 1
        n = nmax
        li = lines[note["line"] - 1]
        at = insertion_point(li, note["sentence"])
        if at < 0:
            report.append(f"NOT-PLACED fn-{n} line {note['line']}: {note['sentence'][:80]}")
            nmax -= 1
            continue
        sup = f'<sup class="fn"><a id="fnref-{n}" href="{cite_href}#fn-{n}">{n}</a></sup>'
        lines[note["line"] - 1] = li[:at] + sup + li[at:]
        new_lis.append(li_for(n, note, back))
        report.append(f"fn-{n} {note['form']} line {note['line']} after ...{visible_map(li)[0][:0]}{li[max(0, at - 40):at][-40:]!r}")
        if note["form"] == "citation":
            key, url = note["key"], note["url"]
            # the section's roster: the nearest Sources: line above
            for j in range(note["line"] - 2, -1, -1):
                if "<p><strong>Sources:</strong>" in lines[j]:
                    if f"<code>{key}</code>" not in lines[j]:
                        link = f'<a href="{url}"><code>{key}</code></a>'
                        body = re.search(r"<p><strong>Sources:</strong>(.*?)</p>", lines[j], re.S)
                        inner = body.group(1) if body else ""
                        if "<code>" in inner:
                            lines[j] = lines[j].replace("</p>", f", {link}</p>", 1) if lines[j].rstrip().endswith("</p>") else lines[j]
                        else:
                            lines[j] = f"<p><strong>Sources:</strong> {link}; {inner.strip()}</p>"
                    break
                if lines[j].lstrip().startswith("<h3") or lines[j].lstrip().startswith("<h2"):
                    report.append(f"NO-ROSTER for {key} above line {note['line']}")
                    break
            reg = note.get("registry")
            if reg and f'<h3 id="{key}">' not in stext and not any(f'<h3 id="{key}">' in e for e in new_entries):
                new_entries.append(
                    f'<h3 id="{key}"><code>{key}</code></h3>\n'
                    f'<p><!-- READ {TODAY} by a source-reader (feature 242) -->{reg["citation"]}</p>\n'
                    f'<p><em>What it is:</em> {reg["what"]}</p>\n'
                    f'<p><em>Why it applies, and its limits:</em> {reg["why"]}</p>\n'
                    f'<p><em>Used for:</em> {reg["used"]}</p>'
                )
    ctext = ctext.replace("</ol></section>", "\n".join(new_lis) + "\n</ol></section>", 1) if new_lis else ctext
    if new_entries:
        marker = '<h2 id="attested-instances-anchors-not-works">'
        stext = stext.replace(marker, "\n".join(new_entries) + "\n" + marker, 1)
    print("\n".join(report))
    print(f"{len(new_lis)} notes placed, {len(new_entries)} registry entries added" + (" (DRY RUN)" if dry else ""))
    if not dry:
        ppath.write_text("\n".join(lines), encoding="utf-8")
        cpath.write_text(ctext, encoding="utf-8")
        (RESEARCH / "SOURCES.html").write_text(stext, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
