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
        ch = " " if raw[i] in "\n\t\r" else raw[i]           # a wrap is whitespace to the sentence
        if ch == " " and out and out[-1] == " ":           # ...and a wrap's indent is one space, like the reader's copy
            i += 1
            continue
        out.append(ch)
        idx.append(i)
        i += 1
    return "".join(out), idx


_BLOCK_OPEN = re.compile(r"^\s*<(p|li|td|th|h[1-6]|dd|dt|blockquote|figcaption)\b")
_BLOCK_CLOSE = re.compile(r"</(p|li|td|th|h[1-6]|dd|dt|blockquote|figcaption)>\s*$")


def block_span(lines: list[str], i: int) -> tuple[int, int]:
    """(first, last) line indices of the wrapped HTML block that line i belongs to.

    THE RECORD WRAPS ITS PARAGRAPHS. A sentence the reader quoted often runs over a line break, and
    a note placed on one physical line lands mid-sentence; so the placement works on the whole block
    - from the line that opens the element to the line that closes it - joined with its newlines kept,
    which the visible map reads as spaces. Nothing is inserted across a newline, so the block keeps its
    line count and every other note's line number stays valid.
    """
    a = i
    while a > 0 and not _BLOCK_OPEN.match(lines[a]) and not _BLOCK_CLOSE.search(lines[a - 1]):
        a -= 1
    b = i
    while b < len(lines) - 1 and not _BLOCK_CLOSE.search(lines[b]) and not _BLOCK_OPEN.match(lines[b + 1]):
        b += 1
    return a, b


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
            # a terminator is also one followed at once by the digits of a mark already placed there
            # ...but a period INSIDE a figure (2.5 cm, 0.87, 31.6%) is not one: the digit alternative needs
            # a non-digit before the period, or the mark lands between the halves of a decimal.
            m2 = re.compile(r'(?<!\d)[.;!?](?=["”」)]*\d{1,3}(?!\d))|[.;!?](?=["”」)]*(?:\s+[A-Z0-9(<「"“]|\s*$))').search(vis, end_vis, min(len(vis), end_vis + 300))
            if m2:
                end_vis = m2.start()
        # advance past closing punctuation the reader may have dropped
        while end_vis < len(vis) and vis[end_vis] in '.;:,)"”」':
            end_vis += 1
        # THE END OF THE LAST CONSUMED CHARACTER, never the start of the next visible one: the next visible
        # character may sit inside a tag that follows the sentence (the digit of a footnote already placed,
        # the first word of the next paragraph), and mapping to it put a mark outside its own element.
        if end_vis == 0:
            return -1
        last = idx[end_vis - 1]
        raw_i = raw.find(";", last) + 1 if raw[last] == "&" else last + 1
        # step past an immediately following closing inline tag
        m = re.match(r"(</(?:strong|em|code|q|a)>)+", raw[raw_i:])
        if m:
            raw_i += m.end()
        return raw_i
    return -1


def locate_line(lines: list[str], sentence: str) -> int | None:
    """The index of the one line whose visible text holds the sentence's last words, or None."""
    words = norm(html.unescape(re.sub(r"<[^>]+>", "", sentence))).replace("...", " ").split()
    for size in (6, 5, 4):
        if len(words) < size:
            continue
        tail = " ".join(words[-size:]).rstrip('."\')')
        hits = [i for i, ln in enumerate(lines) if tail in visible_map(ln)[0]]
        if len(hits) == 1:
            return hits[0]
    return None


def li_for(n: int, note: dict, back: str) -> str:
    form = note["form"]
    if form == "citation":
        q = (note.get("quote") or note.get("original") or "").strip()
        if note.get("translation"):
            body = f"「{note['translation'].strip()}」 (translated from the {note.get('language', 'original')} by this project; original: 「{note['original'].strip() if note.get('original') else q}」)"
        else:
            body = f"「{q}」"
        gloss = f" ({note['gloss'].strip()})" if note.get("gloss") else ""
        text = f'<a href="{note["url"]}"><code>{note["key"]}</code></a> - {body}'
        # A SENTENCE MAY REST ON TWO WORKS: a second key follows after "; " in the same note, the form
        # fields.html fn-6 already uses, so one reference at the assertion carries both passages.
        for x in note.get("extra", []):
            xq = (x.get("quote") or x.get("original") or "").strip()
            xb = f"「{x['translation'].strip()}」 (translated from the {x.get('language', 'original')} by this project; original: 「{x['original'].strip() if x.get('original') else xq}」)" if x.get("translation") else f"「{xq}」"
            text += f'; <a href="{x["url"]}"><code>{x["key"]}</code></a> - {xb}'
        text += gloss
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

    def registry_url(key: str) -> str:
        m = re.search(rf'<h3 id="{re.escape(key)}"><code>{re.escape(key)}</code></h3>\n<p>(.*?)</p>', stext, re.S)
        if not m:
            return ""
        body = re.sub(r"<!--.*?-->", "", m.group(1))
        # THE TESTS WANT THE ENTRY'S FIRST LINK (tests/interactive/test_sources.py): where the citation
        # paragraph links its title and then names another address in parentheses, the link wins.
        u = re.search(r'href="(https?://[^"]+)"', body) or re.search(r"\((https?://[^\s)]+)", body)
        return u.group(1) if u else ""

    # AN EXISTING KEY LINKS WHERE ITS REGISTRY ENTRY LINKS (tests/interactive/test_sources.py): the
    # reader may spell the same page percent-encoded where the registry has it in kanji, or the reverse.
    for note in notes:
        for src in [note] + list(note.get("extra", [])):
            if src.get("key"):
                u = registry_url(src["key"])
                if u:
                    src["url"] = u
    new_lis: list[str] = []
    new_entries: list[str] = []
    report: list[str] = []
    def roster_add(line_no: int, key: str, url: str) -> None:
        # THE ROSTER MAY WRAP. The first version read only the line that opens it, so a roster that ran on
        # to a second line lost the rest of its first line and gained a `</p>` (five homesteads rosters,
        # found by record-format on 2026-09-14): the whole paragraph is read, and the key is added on the
        # line that closes it, or right after the label when the roster names no key yet.
        for j in range(line_no - 2, -1, -1):
            if "<p><strong>Sources:</strong>" in lines[j]:
                k = j
                while k < len(lines) and "</p>" not in lines[k]:
                    k += 1
                if k >= len(lines):
                    report.append(f"UNCLOSED-ROSTER at line {j + 1}")
                    return
                para = "\n".join(lines[j : k + 1])
                if f"<code>{key}</code>" in para:
                    return
                link = f'<a href="{url}"><code>{key}</code></a>'
                if "<code>" in para:
                    lines[k] = lines[k].replace("</p>", f", {link}</p>", 1)
                else:
                    lines[j] = lines[j].replace("<p><strong>Sources:</strong>", f"<p><strong>Sources:</strong> {link};", 1)
                return
            if lines[j].lstrip().startswith(("<h3", "<h2")):
                report.append(f"NO-ROSTER for {key} above line {line_no}")
                return

    def registry_add(note: dict) -> None:
        nonlocal stext
        for src in [note] + list(note.get("extra", [])):
            reg = src.get("registry")
            key = src.get("key")
            if reg and key and f'<h3 id="{key}">' not in stext and not any(f'<h3 id="{key}">' in e for e in new_entries):
                citation = re.sub(r"「([^」]*)」", r"<em>\1</em>", reg["citation"])   # a title, not a quotation
                new_entries.append(
                    f'<h3 id="{key}"><code>{key}</code></h3>\n'
                    f'<p><!-- READ {TODAY} by a source-reader (feature 242) -->{citation}</p>\n'
                    f'<p><em>What it is:</em> {reg["what"]}</p>\n'
                    f'<p><em>Why it applies, and its limits:</em> {reg["why"]}</p>\n'
                    f'<p><em>Used for:</em> {reg["used"]}</p>'
                )

    # AN EXISTING NOTE REWRITTEN IN PLACE (feature 242 T18): a never-searched absence note that the
    # research pass has now answered keeps its number and its reference; only its body changes.
    for note in [d for d in notes if d.get("fn")]:
        fnn = int(note["fn"])
        pat = re.compile(rf'<li id="fn-{fnn}">.*?</li>', re.S)
        if not pat.search(ctext):
            report.append(f"NO-SUCH-NOTE fn-{fnn}")
            continue
        ctext = pat.sub(lambda _m: li_for(fnn, note, back), ctext, count=1)
        report.append(f"fn-{fnn} REPLACED as {note['form']}")
        if note["form"] == "citation":
            roster_add(note["line"], note["key"], note["url"])
            for x in note.get("extra", []):
                roster_add(note["line"], x["key"], x["url"])
            registry_add(note)
    notes = [d for d in notes if not d.get("fn")]
    for note in sorted(notes, key=lambda d: -d["line"]):  # bottom-up so line numbers stay valid
        nmax += 1
        n = nmax
        a, b = block_span(lines, note["line"] - 1)
        li = "\n".join(lines[a : b + 1])
        at = insertion_point(li, note["sentence"])
        if at < 0:
            # THE LINE NUMBER IS A HINT, THE SENTENCE IS THE ANCHOR: a correction above may have joined or
            # split a line since the work list was derived, so the sentence's own last words are searched
            # for across the page and the block that holds them is used.
            found = locate_line(lines, note["sentence"])
            if found is not None and found != note["line"] - 1:
                a, b = block_span(lines, found)
                li = "\n".join(lines[a : b + 1])
                at = insertion_point(li, note["sentence"])
                report.append(f"RELOCATED line {note['line']} -> {found + 1}")
        if at < 0:
            report.append(f"NOT-PLACED fn-{n} line {note['line']}: {note['sentence'][:80]}")
            nmax -= 1
            continue
        sup = f'<sup class="fn"><a id="fnref-{n}" href="{cite_href}#fn-{n}">{n}</a></sup>'
        li = li[:at] + sup + li[at:]
        lines[a : b + 1] = li.split("\n")
        new_lis.append(li_for(n, note, back))
        report.append(f"fn-{n} {note['form']} line {note['line']} after {li[max(0, at - 44):at]!r}")
        if note["form"] == "citation":
            roster_add(note["line"], note["key"], note["url"])
            for x in note.get("extra", []):
                roster_add(note["line"], x["key"], x["url"])
            registry_add(note)
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
