#!/usr/bin/env python3
"""The measurements behind this spec - one subcommand each, re-runnable.

    python3 specs/258-split-the-record-into-per-entry-files/measure.py R1

R1 what the record's files weigh, and what one entry weighs
R2 what the session's own editing of the record costs today (all transcripts on this machine)
R3 what a checking agent reads (the recorded agent runs of features 251, 255 and 256)
R4 the footnote numbers already out of document order, and the duplicated reference ids
R5 what the note keys can be derived from, and the reference defects the allocation fixes

R2 and R3 read `~/.claude/projects/`, which is this machine's transcript store: they re-run only
where those transcripts still exist, and they are reported here because they cannot be recovered
from the repository.
"""

from __future__ import annotations

import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.normpath(os.path.join(HERE, "..", "..", ".claude", "skills", "diagram"))
RECORD = os.path.join(SKILL, "research")
PROJECTS = os.path.expanduser("~/.claude/projects")
H2 = re.compile(r"(?=<h2\b)")
H3 = re.compile(r"(?=<h3\b)")
FNREF = re.compile(r'id="fnref-(\d+)"')
NOTE = re.compile(r'<li id="fn-\d+".*?</li>', re.S)


def pages() -> list[str]:
    """Every research page, as a path relative to the record - the registry and citations excluded."""
    top = sorted(f for f in os.listdir(RECORD) if f.endswith(".html") and f != "SOURCES.html")
    cities = sorted(f"cities/{f}" for f in os.listdir(os.path.join(RECORD, "cities")) if f.endswith(".html"))
    return top + cities


def read(rel: str) -> str:
    with open(os.path.join(RECORD, rel), encoding="utf-8") as fh:
        return fh.read()


def comments(html: str) -> list[tuple[int, int]]:
    """The [start, end) of every HTML comment. A heading inside one is not a section: the registry
    carries an 8,021-byte commented-out block holding two whole `<h2>` groups (R1)."""
    return [(m.start(), m.end()) for m in re.finditer(r"<!--.*?-->", html, re.S)]


def headings(html: str, level: int) -> list[re.Match[str]]:
    """Every `<hN` that opens a real section - not one inside a comment."""
    hidden = comments(html)
    return [m for m in re.finditer(rf"<h{level}\b", html)
            if not any(a <= m.start() < b for a, b in hidden)]


def size(text: str) -> int:
    """BYTES, not characters. The record quotes Chinese and Japanese, where one character is three
    bytes: `len()` understates the registry by 21,893 and every note that carries a quotation."""
    return len(text.encode("utf-8"))


def r1() -> None:
    """File weights, and the weight of one entry of each kind."""
    files = sorted(glob.glob(os.path.join(RECORD, "**", "*.html"), recursive=True), key=os.path.getsize, reverse=True)
    print("THE TEN HEAVIEST FILES")
    for path in files[:10]:
        print(f"  {os.path.getsize(path):>9}  {os.path.relpath(path, RECORD)}")
    print(f"  ({sum(1 for p in files if os.path.getsize(p) > 100_000)} files are over 100,000 bytes)")

    entries = [size(x) for x in H3.split(read("SOURCES.html"))[1:]]
    entries.sort()
    print(f"\nREGISTRY ENTRIES: {len(entries)}  median {entries[len(entries) // 2]}  max {entries[-1]}")

    print("\nQUESTIONS PER PAGE (bytes)")
    for rel in pages():
        sizes = [size(x) for x in H2.split(read(rel))[1:]]
        if sizes:
            print(f"  {rel:28} n={len(sizes):>3}  avg={sum(sizes) // len(sizes):>6}  max={max(sizes):>6}")

    print("\nNOTES PER CITATIONS PAGE (bytes)")
    for rel in pages():
        try:
            body = read(f"citations/{rel}")
        except OSError:
            continue
        notes = NOTE.findall(body)
        if notes:
            print(f"  citations/{rel:28} n={len(notes):>3}  avg={sum(map(size, notes)) // len(notes):>5}")

    print("\nTHE FRAGMENTS SC-001's BAR IS DECIDED BY")
    registry = read("SOURCES.html")
    cuts = [m.start() for m in headings(registry, 2)] + [len(registry)]
    commented = max((size(registry[a:b]) for a, b in comments(registry)), default=0)
    print(f"  registry front matter                {size(registry[:cuts[0]]):>7}   of which a commented-out block: {commented}")
    for start, stop in zip(cuts, cuts[1:]):
        part = registry[start:stop]
        name = re.search(r'id="([^"]*)"', part).group(1)
        print(f"  registry section {name:20}{size(part.split('<h3')[0]):>7}   (its heading and its prose, "
              f"{len(re.findall('<h3', part))} entries)")
    biggest = ("", 0, 0)
    for rel in pages():
        try:
            notes = dict(_numbered_notes(read(f"citations/{rel}")))
        except OSError:
            continue
        for heading, cited in _questions_and_their_notes(read(rel)):
            total = sum(size(notes[n]) for n in cited if n in notes)
            if total > biggest[1]:
                biggest = (f"{rel} - {heading}", total, len(cited))
    print(f"  largest per-question notes file      {biggest[1]:>7}   ({biggest[0]}, {biggest[2]} notes)")


def _numbered_notes(citations_html: str) -> list[tuple[str, str]]:
    """(number, the whole `<li>`) for every note on a citations page."""
    return [(m.group(1), m.group(0)) for m in re.finditer(r'<li id="fn-(\d+)".*?</li>', citations_html, re.S)]


def _questions_and_their_notes(page_html: str) -> list[tuple[str, list[str]]]:
    """(heading text, the note numbers it references) for each question of a research page."""
    out = []
    for section in H2.split(page_html)[1:]:
        heading = re.search(r"<h2[^>]*>(.*?)</h2>", section, re.S)
        out.append(((heading.group(1)[:40] if heading else "?"), FNREF.findall(section)))
    return out


def _results(patterns: list[str]):
    """(transcript tag, result bytes, the file path a Read returned) for every tool result recorded."""
    for pattern in patterns:
        for path in glob.glob(pattern):
            tag = os.path.basename(os.path.dirname(path)).split("scratchpad-")[-1]
            with open(path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if "toolUseResult" not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    out = rec.get("toolUseResult")
                    if out is None:
                        continue
                    blob = out if isinstance(out, str) else json.dumps(out)
                    got = out.get("file") if isinstance(out, dict) else None
                    yield tag, len(blob), str(got.get("filePath", "")) if isinstance(got, dict) else ""


def _reads(patterns: list[str]):
    """(file path, whether the Read asked for a window) for every Read call recorded."""
    for pattern in patterns:
        for path in glob.glob(pattern):
            with open(path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if '"Read"' not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    body = (rec.get("message") or {}).get("content")
                    for part in body if isinstance(body, list) else []:
                        if isinstance(part, dict) and part.get("type") == "tool_use" and part.get("name") == "Read":
                            args = part.get("input") or {}
                            yield str(args.get("file_path", "")), bool(args.get("offset") or args.get("limit"))


def r2() -> None:
    """What the session's own reading of the record costs, against everything else it reads."""
    everything = the_record = 0
    for _, nbytes, path in _results([os.path.join(PROJECTS, "*", "*.jsonl")]):
        everything += nbytes
        if "/research/" in path:
            the_record += nbytes
    share = 100 * the_record / everything if everything else 0
    print(f"all tool result bytes      {everything:>12}")
    print(f"reads of the record        {the_record:>12}   {share:.2f}%")

    windowed = whole = 0
    for path, is_window in _reads([os.path.join(PROJECTS, "*", "*.jsonl")]):
        if "/research/" in path:
            windowed, whole = windowed + is_window, whole + (not is_window)
    total = windowed + whole
    print(f"reads of the record: {total} calls, {windowed} windowed ({100 * windowed // total if total else 0}%), {whole} whole-file")

    calls = payload = 0
    for path, size_of_payload in _writes([os.path.join(PROJECTS, "*", "*.jsonl")]):
        if "/research/" in path:
            calls, payload = calls + 1, payload + size_of_payload
    print(f"edits of the record: {calls} Edit/Write calls, {payload} bytes of payload between them")


def _writes(patterns: list[str]):
    """(file path, payload bytes) for every Edit or Write call recorded."""
    for pattern in patterns:
        for path in glob.glob(pattern):
            with open(path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if '"Edit"' not in line and '"Write"' not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    body = (rec.get("message") or {}).get("content")
                    for part in body if isinstance(body, list) else []:
                        if isinstance(part, dict) and part.get("type") == "tool_use" and part.get("name") in ("Edit", "Write"):
                            args = part.get("input") or {}
                            written = "".join(str(args.get(k, "")) for k in ("old_string", "new_string", "content"))
                            yield str(args.get("file_path", "")), len(written.encode("utf-8"))


def r3() -> None:
    """What one research page was, of everything that entered a recorded agent's context."""
    tot: collections.Counter = collections.Counter()
    record: collections.Counter = collections.Counter()
    for tag, nbytes, path in _results([os.path.join(PROJECTS, "-tmp-*tree", "*.jsonl")]):
        tot[tag] += nbytes
        if "/research/" in path:
            record[tag] += nbytes
    print(f"{'recorded agent run':40}{'all bytes':>11}{'the page':>10}{'share':>7}")
    for tag, total in tot.most_common():
        if record[tag]:
            print(f"{tag:40}{total:>11}{record[tag]:>10}{100 * record[tag] // total:>6}%")


def r4() -> None:
    """Footnote references out of document order, and ids that appear twice."""
    out_of_order = duplicated = 0
    for rel in pages():
        refs = FNREF.findall(read(rel))
        counts = collections.Counter(refs)
        repeats = sorted(k for k, n in counts.items() if n > 1)
        ordered = refs == sorted(refs, key=int)
        out_of_order += not ordered
        duplicated += bool(repeats)
        print(f"  {rel:28} refs={len(refs):>4}  document order={'yes' if ordered else 'NO':<3}"
              + (f"  repeated ids: {', '.join('fnref-' + r for r in repeats)}" if repeats else ""))
    print(f"\n{out_of_order} of {len(pages())} pages carry their references out of document order; "
          f"{duplicated} carry a duplicated reference id.")


def r5() -> None:
    """What the note keys will be derived from, and the two reference defects the allocation fixes."""
    refs = idless = notes = keyless = repeats = 0
    idless_where: list[str] = []
    for rel in pages():
        page = read(rel)
        for ref in re.finditer(r'<sup class="fn">(.*?)</sup>', page, re.S):
            refs += 1
            if 'id="fnref-' not in ref.group(1):
                idless += 1
                idless_where.append(rel)
        try:
            body = read(f"citations/{rel}")
        except OSError:
            continue
        keys: collections.Counter = collections.Counter()
        for _, note in _numbered_notes(body):
            notes += 1
            leading = re.match(r'<li id="fn-\d+">\s*<a href="[^"]*"><code>([a-z0-9-]+)</code></a>', note)
            if leading:
                keys[leading.group(1)] += 1
            else:
                keyless += 1
        repeats += sum(n - 1 for n in keys.values() if n > 1)
    print(f"references: {refs}, of which {idless} carry NO id (on {', '.join(sorted(set(idless_where)))})")
    print(f"notes: {notes}, of which {notes - keyless} lead with a source key and {keyless} do not")
    print(f"a source key repeated within one page: {repeats} times - so a key needs an ordinal")


def main(argv: list[str]) -> int:
    which = {"R1": r1, "R2": r2, "R3": r3, "R4": r4, "R5": r5}
    if len(argv) != 2 or argv[1].upper() not in which:
        print(f"usage: {os.path.basename(__file__)} R1|R2|R3|R4|R5", file=sys.stderr)
        return 2
    which[argv[1].upper()]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
