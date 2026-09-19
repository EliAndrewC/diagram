#!/usr/bin/env python3
"""Is every quoted passage on the page it cites, character for character? (feature 251, FR-003)

WHY A SCRIPT AND NOT A MODEL. The GM, 2026-09-19: "it probably is a perfectly fine model to use to do
what are functionally mechanical checks, such as making sure that a quotation excerpt does accurately
quote the text in question" - and then approved going one step further: a character-for-character
comparison is the one thing a language model is WORSE at than twenty lines of code. It reads tokens,
not characters, so a hyphen where the source has a dash, or "color" where the source has "color", is
exactly what it blurs - and the record keeps a source's own characters (GM 2026-09-06: *"The house
style should not normalize british spellings or em-dashes inside things we are quoting"*). This does
that comparison exactly, for no tokens, and hands the `quote-check` agent what is left: whether the
quotation SUPPORTS the assertion, whether a translation is faithful, and the pages this could not read.

WHAT IT READS. A research page (`research/<name>.html`) for the ASSERTIONS - the sentence carrying each
`<sup class="fn">` - and its citations page (`research/citations/<name>.html`) for the notes:

    <li id="fn-3"><a href="URL"><code>key</code></a> - 「passage」 ... <a class="fnback" ...>back</a></li>

A translated quotation (feature 202) is `「English」 (translated from the ... by this project; original:
「source text」)`: the ORIGINAL is what is matched against the page, and the entry carries both so the
agent can judge the translation. A note with no link reading `no publicly readable source (...)` is an
ABSENCE note and `no source is owed: ...` a GROUNDS note; nothing is fetched for either.

THE MATCH, and the only two liberties it takes. Runs of whitespace are collapsed to one space on both
sides (a page wraps its lines where it likes), and the passage loses the quotation marks that DELIMIT
it (they are the footnote's, not the source's). Nothing else: the verdict is `passage in page_text`.
A passage with an elision (`...`, `…`, `[...]`) is matched piece by piece, in order.

VERDICTS. Quotation: VERBATIM; DIFFERS (the closest stretch of the page, and what differs);
NOT-ON-PAGE; UNFETCHABLE (how); NOT-CHECKED (why - a PDF, a page that would not decode). Readability:
READABLE when the passage was found on a page fetched with no credentials; NOT-READABLE when the link
is this project's own registry or the page was read and does not carry the passage; otherwise left to
the agent (`-`). It decides nothing about support and never edits.

ONE ATTEMPT PER HOST, EVER (GM 2026-08-28): a host that refuses is recorded and never asked again in the
run, and every fetch has a timeout - two readers once stalled for ten hours on a bad certificate.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import html
import json
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

TIMEOUT = 20
#: below this similarity the nearest stretch of the page is not worth showing: NOT-ON-PAGE rather than
#: DIFFERS. It only chooses which of two NON-PASSING words is printed; both go to the session.
NEAR = 0.85
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
BLOCK = {"p", "div", "br", "li", "ul", "ol", "tr", "td", "th", "table", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article", "blockquote", "dd", "dt", "pre", "figcaption"}
PAIRS = {"「": "」", "“": "”", '"': '"', "『": "』"}
TRANSLATED = re.compile(r"^\s*\((?:title\s+)?translated from ([^;()]*(?:\([^()]*\))?[^;()]*?) by this project;\s*original:\s*$")
ELISION = re.compile(r"\s*(?:\[\s*(?:\.\.\.|…)\s*\]|\.\.\.|…)\s*")
REF_MARK = re.compile(r"\s*\[(?:\d{1,3}|注\s*\d+|note\s*\d+|citation needed|要出典)\]")


class _Visible(HTMLParser):
    """The text a reader sees: no script, style or comment; a space at every block boundary."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        elif tag in BLOCK:
            self.out.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "noscript"):
            self.skip = max(0, self.skip - 1)
        elif tag in BLOCK:
            self.out.append(" ")

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.out.append(data)


def squeeze(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def visible_text(markup: str) -> str:
    parser = _Visible()
    parser.feed(markup)
    parser.close()
    return squeeze("".join(parser.out))


def decode(raw: bytes, declared: str = "") -> str | None:
    """`raw` as text by the declared charset, then the page's own `<meta>`, then the usual suspects.

    Strict throughout: a page that decodes only with replacement characters would make every quotation
    on it DIFFER for a reason that is ours, so it is reported as undecodable instead (None).
    """
    meta = re.search(rb"<meta[^>]+charset=[\"']?\s*([\w-]+)", raw[:4096], re.I)
    tried: list[str] = []
    for name in (declared, meta.group(1).decode("ascii", "replace") if meta else "", "utf-8", "shift_jis", "euc_jp", "gb18030", "big5"):
        name = (name or "").strip().lower()
        if not name or name in tried:
            continue
        tried.append(name)
        try:
            return raw.decode(name)
        except (LookupError, UnicodeDecodeError):
            continue
    return None


def top_level_quotes(text: str) -> list[tuple[int, int]]:
    """(start, end) of each OUTERMOST quoted span, delimiters included.

    A Japanese title quotes inside a quote (「世界農業遺産「能登の里山里海」を代表する」), so 「」 is scanned
    with a depth count; a straight or curly pair does not nest.
    """
    spans: list[tuple[int, int]] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch not in PAIRS:
            i += 1
            continue
        close, depth, j = PAIRS[ch], 1, i + 1
        while j < len(text) and depth:
            if text[j] == close:
                depth -= 1
            elif text[j] == ch and close != ch:
                depth += 1
            j += 1
        if depth:
            i += 1
            continue
        spans.append((i, j))
        i = j
    return spans


def passages(note_text: str) -> list[dict]:
    """The quoted passages of one note: each `{quote, original, language}`; `original` is what is matched."""
    spans = top_level_quotes(note_text)
    found: list[dict] = []
    k = 0
    while k < len(spans):
        start, end = spans[k]
        quote = note_text[start + 1 : end - 1]
        entry = {"quote": quote, "original": "", "language": ""}
        if k + 1 < len(spans):
            between = TRANSLATED.match(note_text[end : spans[k + 1][0]])
            if between:
                nxt = spans[k + 1]
                entry["original"] = note_text[nxt[0] + 1 : nxt[1] - 1]
                entry["language"] = squeeze(between.group(1))
                k += 1
        found.append(entry)
        k += 1
    return found


def classify(note_text: str, links: list[str]) -> str:
    lead = squeeze(note_text).lower()
    if lead.startswith("no publicly readable source"):
        return "absence"
    if lead.startswith("no source is owed"):
        return "grounds"
    return "citation" if links else "unlinked"


def _strip(markup: str) -> str:
    return squeeze(html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"<!--.*?-->", "", markup, flags=re.S))))


def footnotes(citations_html: str) -> list[dict]:
    """One entry per `<li id="fn-N">`: id, key, links, class, passages."""
    notes: list[dict] = []
    for m in re.finditer(r'<li id="(fn-\d+)">(.*?)</li>', citations_html, re.S):
        body = re.sub(r'<a class="fnback".*?</a>', "", m.group(2), flags=re.S)
        links = [html.unescape(u) for u in re.findall(r'<a href="([^"]+)"', body)]
        key = re.search(r"<code>([^<]+)</code>", body)
        text = _strip(body)
        kind = classify(text, links)
        notes.append({"id": m.group(1), "key": key.group(1) if key else "", "links": links, "class": kind, "passages": passages(text) if kind == "citation" else []})
    return notes


def assertions(research_html: str) -> dict[str, str]:
    """fn id -> the sentence its `<sup class="fn">` closes, from the research page's visible text."""
    body = re.sub(r"<!--.*?-->", "", research_html, flags=re.S)
    marked = re.sub(r'<sup class="fn">.*?#(fn-\d+)".*?</sup>', lambda m: f"⁣{m.group(1)}⁣", body, flags=re.S)
    out: dict[str, str] = {}
    for block in re.split(r"</?(?:p|li|h[1-6]|td|th|dd|dt|blockquote)\b[^>]*>", marked):
        text = _strip(block)
        for m in re.finditer("⁣(fn-\\d+)⁣", text):
            before = re.sub("⁣fn-\\d+⁣", "", text[: m.start()])
            sentence = re.split(r"(?<=[.!?])\s+(?=[A-Z(\"“「])", before)[-1]
            out.setdefault(m.group(1), squeeze(sentence))
    return out


def nearest(passage: str, page: str) -> tuple[float, str]:
    """(similarity, the stretch of the page closest to `passage`), anchored on their longest shared run."""
    if not passage or not page:
        return 0.0, ""
    sm = difflib.SequenceMatcher(None, page, passage, autojunk=False)
    block = sm.find_longest_match(0, len(page), 0, len(passage))
    if block.size == 0:
        return 0.0, ""
    start = max(0, block.a - block.b)
    window = page[start : start + len(passage) + max(8, len(passage) // 10)]
    best, best_text = 0.0, ""
    for cut in range(len(window), max(0, len(passage) - max(8, len(passage) // 10)) - 1, -1):
        cand = window[:cut]
        ratio = difflib.SequenceMatcher(None, cand, passage, autojunk=False).ratio()
        if ratio > best:
            best, best_text = ratio, cand
    return best, best_text


def differences(passage: str, page_stretch: str) -> list[str]:
    """`quoted 'x' / page 'y'` for each place the two differ."""
    sm = difflib.SequenceMatcher(None, passage, page_stretch, autojunk=False)
    return [f"quoted {passage[i1:i2]!r} / page {page_stretch[j1:j2]!r}" for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]


def verdict(passage: str, page: str) -> dict:
    """VERBATIM, DIFFERS (with the page's text and the differences) or NOT-ON-PAGE for one passage."""
    want, have = squeeze(passage), squeeze(page)
    pieces = [p for p in ELISION.split(want) if p]
    at, ok = 0, bool(pieces)
    for piece in pieces:
        hit = have.find(piece, at)
        if hit < 0:
            ok = False
            break
        at = hit + len(piece)
    if ok:
        return {"quotation": "VERBATIM"}
    ratio, stretch = nearest(want, have)
    if ratio >= NEAR:
        diffs = differences(want, stretch)
        only_marks = squeeze(REF_MARK.sub("", stretch)) == want
        return {"quotation": "DIFFERS", "page_text": stretch, "differences": diffs, "similarity": round(ratio, 3), "only_reference_markers": only_marks}
    return {"quotation": "NOT-ON-PAGE", "similarity": round(ratio, 3)}


def is_pdf(url: str, content_type: str = "") -> bool:
    path = urllib.parse.urlsplit(url).path.lower()
    return "pdf" in content_type.lower() or path.endswith(".pdf") or path.endswith("/_pdf")


def quoted_url(url: str) -> str:
    """`url` with a non-ASCII path or query percent-encoded (ja.wikipedia.org/wiki/アブラナ), nothing else touched."""
    parts = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc.encode("idna").decode("ascii") if parts.netloc else "", urllib.parse.quote(parts.path, safe="/%:@!$&'()*+,;=~-._"), urllib.parse.quote(parts.query, safe="=&%:@!$'()*+,;/?~-._"), ""))


class Pages:
    """Fetch each URL once, each HOST at most once after it refuses; `offline` reads files by URL hash."""

    def __init__(self, offline: pathlib.Path | None = None, opener=urllib.request.urlopen) -> None:  # noqa: ANN001
        self.offline, self.opener = offline, opener
        self.seen: dict[str, dict] = {}
        self.refused: dict[str, str] = {}

    @staticmethod
    def name_for(url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16] + ".html"

    def get(self, url: str) -> dict:
        if url not in self.seen:
            self.seen[url] = self._get(url)
        return self.seen[url]

    def _get(self, url: str) -> dict:
        host = urllib.parse.urlsplit(url).netloc
        if not url.lower().startswith(("http://", "https://")):
            return {"state": "OWN", "why": "a link into this project, not a public page"}
        if is_pdf(url):
            return {"state": "NOT-CHECKED", "why": "a PDF - no text layer can be read here"}
        if self.offline is not None:
            path = self.offline / self.name_for(url)
            if not path.is_file():
                return {"state": "UNFETCHABLE", "why": "no offline copy"}
            raw, declared, ctype = path.read_bytes(), "", "text/html"
        else:
            if host in self.refused:
                return {"state": "UNFETCHABLE", "why": f"{host} already refused this run: {self.refused[host]}"}
            try:
                req = urllib.request.Request(quoted_url(url), headers={"User-Agent": UA, "Accept-Language": "en,ja,zh,ko"})
                with self.opener(req, timeout=TIMEOUT) as resp:
                    ctype = resp.headers.get("Content-Type", "") or ""
                    declared = resp.headers.get_content_charset() or ""
                    raw = b"" if is_pdf(url, ctype) else resp.read()
            except (urllib.error.URLError, OSError, ValueError) as err:
                self.refused[host] = f"{type(err).__name__}: {err}"[:160]
                return {"state": "UNFETCHABLE", "why": self.refused[host]}
        if is_pdf(url, ctype):
            return {"state": "NOT-CHECKED", "why": "a PDF - no text layer can be read here"}
        text = decode(raw, declared)
        if text is None:
            return {"state": "NOT-CHECKED", "why": "the page would not decode in any charset tried"}
        return {"state": "FETCHED", "text": visible_text(text)}


def judge_note(note: dict, pages: Pages) -> dict:
    """The quotation and readability verdicts of one citation, over every passage and every link it carries."""
    results, states = [], [pages.get(u) for u in note["links"]]
    fetched = [s["text"] for s in states if s["state"] == "FETCHED"]
    for p in note["passages"]:
        target = p["original"] or p["quote"]
        if fetched:
            per_page = [verdict(target, t) for t in fetched]
            best = next((v for v in per_page if v["quotation"] == "VERBATIM"), None) or next((v for v in per_page if v["quotation"] == "DIFFERS"), per_page[0])
        else:
            first = states[0]
            best = {"quotation": "UNFETCHABLE" if first["state"] == "UNFETCHABLE" else "NOT-CHECKED", "why": first["why"]}
        results.append({**p, "matched": "original" if p["original"] else "quote", **best})
    words = [r["quotation"] for r in results]
    if not results:
        readable = "-"
    elif all(s["state"] == "OWN" for s in states):
        readable = "NOT-READABLE (the link is this project's own page)"
    elif all(w == "VERBATIM" for w in words):
        readable = "READABLE"
    elif fetched and any(w in ("NOT-ON-PAGE", "DIFFERS") for w in words):
        readable = "NOT-READABLE (the page was read and does not carry the passage as quoted)"
    else:
        readable = "-"
    return {**note, "passages": results, "readability": readable}


def report(notes: list[dict], claims: dict[str, str], pages: Pages) -> list[dict]:
    out = []
    for note in notes:
        entry = judge_note(note, pages) if note["class"] == "citation" else {**note, "readability": "-"}
        entry["assertion"] = claims.get(note["id"], "")
        out.append(entry)
    return out


def render(page: str, entries: list[dict], refused: dict[str, str]) -> str:
    lines = [f"quote-verbatim: {page} - {len(entries)} footnotes"]
    tally: dict[str, int] = {}
    for e in entries:
        if e["class"] != "citation":
            tally[e["class"]] = tally.get(e["class"], 0) + 1
            continue
        for p in e["passages"]:
            tally[p["quotation"]] = tally.get(p["quotation"], 0) + 1
            if p["quotation"] == "VERBATIM":
                continue
            lines.append(f"  {e['id']} {e['key']} - {p['quotation']} ({p['matched']}): {(p['original'] or p['quote'])[:120]}")
            if p["quotation"] == "DIFFERS":
                lines.append(f"      page has: {p['page_text'][:200]}")
                lines.append("      " + "; ".join(p["differences"][:6]) + ("   [only the page's reference markers differ]" if p["only_reference_markers"] else ""))
            elif "why" in p:
                lines.append(f"      {p['why']}")
        if not e["passages"]:
            tally["NO-QUOTE"] = tally.get("NO-QUOTE", 0) + 1
            lines.append(f"  {e['id']} {e['key']} - NO-QUOTE: a citation that quotes nothing")
    lines.append("  " + ", ".join(f"{k} {v}" for k, v in sorted(tally.items())))
    for host, why in sorted(refused.items()):
        lines.append(f"  refused: {host} - {why}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("page", help="a research page name: hamlets, cities/tango")
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", default="")
    ap.add_argument("--offline", default="", help="a directory of saved pages named by Pages.name_for(url)")
    args = ap.parse_args(argv)
    research = pathlib.Path(args.root) / ".claude/skills/diagram/research"
    name = args.page.removesuffix(".html")
    page_file, cite_file = research / f"{name}.html", research / "citations" / f"{name}.html"
    if not page_file.is_file() or not cite_file.is_file():
        print(f"quote-verbatim: no such page - wanted {page_file} and {cite_file}", file=sys.stderr)
        return 2
    pages = Pages(pathlib.Path(args.offline) if args.offline else None)
    entries = report(footnotes(cite_file.read_text(encoding="utf-8")), assertions(page_file.read_text(encoding="utf-8")), pages)
    print(render(name, entries, pages.refused))
    out = pathlib.Path(args.json) if args.json else pathlib.Path(args.root) / ".git" / "quote-verbatim" / (name.replace("/", "-") + ".json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"page": name, "footnotes": entries, "refused": pages.refused}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"  report for quote-check: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
