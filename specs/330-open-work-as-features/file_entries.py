#!/usr/bin/env python3
"""Feature 330, T04 (plan D5): file every future-work entry as its own unimplemented feature. Run once, from the clone
root; kept here as the record of what was done (feature 329 kept its sweep the same way).

    file_entries.py <closed.json> [--dry-run]

`closed.json` maps an entry's KEY (`<file>#<heading>`, or `<file>#<heading>#<n>` for the n-th piece of a multi-piece
entry) to the evidence that closes it; every other entry is filed. Writes `filed.json` beside this script: KEY ->
`specs/NNN-slug`, which T05 reads to re-aim the pointers.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FW = ROOT / "future-work"
FILES = ("cities.md", "compounds.md", "cross-cutting.md", "farming-communities.md", "towns.md")
# the one entry the spec names as several pieces (FR-006): each bullet under these subsections is its own feature;
# the section's opening and its "Sources to read" paragraph travel with every question as context
PIECED = ("compounds.md", "Research owed (rewritten by feature 267, 2026-09-27)")
PIECE_SECTIONS = ("Questions the research opened (each needs a pass)", "Drawing and tooling questions left open")
DATE = "2026-10-08"
_STOP = {"a", "an", "the", "of", "and", "or", "to", "in", "on", "at", "by", "for", "is", "its", "it", "what", "does",
         "did", "from", "with", "that", "this", "when", "how", "where", "two", "one", "not", "yet", "still", "s"}


def entries(fw: Path = FW) -> list[tuple[str, str, str]]:
    """(file, heading, body) for every `## ` section of the five entry files."""
    out = []
    for name in FILES:
        text = (fw / name).read_text()
        parts = re.split(r"^## (.+)$", text, flags=re.M)
        for heading, body in zip(parts[1::2], parts[2::2], strict=True):
            out.append((name, heading.strip(), body.strip("\n")))
    return out


def pieces(body: str) -> tuple[str, list[tuple[str, str]]]:
    """The pieced entry's shared context, and (section, bullet) for each bullet under its piece sections."""
    subs = re.split(r"^### (.+)$", body, flags=re.M)
    context = [subs[0].strip()]
    found = []
    for title, text in zip(subs[1::2], subs[2::2], strict=True):
        if title.strip() in PIECE_SECTIONS:
            for bullet in re.split(r"\n(?=- )", "\n" + text.strip()):
                if bullet.strip().startswith("- "):
                    found.append((title.strip(), bullet.strip()))
        else:
            context.append(f"### {title.strip()}\n\n{text.strip()}")
    return "\n\n".join(c for c in context if c), found


def slug(title: str) -> str:
    """A name for the work, not for its bookkeeping: a status prefix (`OPEN 2026-09-28:`, `OWED AT CONVERSION:`,
    `RESEARCH OWED (...):`), a list number, dates and bare numbers go."""
    t = re.sub(r"^\d+\.\s*", "", title)
    if re.match(r"^(OPEN|OWED AT CONVERSION|RESEARCH OWED|DEFERRED)\b", t) and ":" in t:
        t = t.split(":", 1)[1]
    t = re.sub(r"\bfeatures? (\d{3})\b", r"feature\1", t)  # a feature's number names the work; other numbers do not
    t = re.sub(r"\([^)]*\)", " ", t)
    t = re.sub(r"`[^`]*`", lambda m: m.group(0).strip("`").replace(".", " ").replace("_", " "), t)
    words = [w for w in re.findall(r"[a-z0-9]+", t.lower()) if w not in _STOP and not w.isdigit()]
    return "-".join(words[:6]) or "entry"


def spec_text(title: str, source: str, entry: str, history: str = "") -> str:
    return (
        f"# Feature Specification: {title}\n\n"
        f"**Status**: Filed - from {source}, {DATE} (feature 330: the GM retired that directory; this is the entry as it stood)\n\n"
        f"**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings "
        f"(2026-10-08): *\"Everything that is there should instead become an unimplemented spec kit feature.\"*"
        f"{history}\n\n"
        "Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on "
        "this directory); until then `make speckit-todo` lists it as filed.\n\n"
        f"## The entry, as filed\n\n{entry.strip()}\n"
    )


def claim(name: str, dry: bool) -> str:
    if dry:
        return f"specs/NNN-{name}"
    r = subprocess.run(["make", "--no-print-directory", "claim", f"SLUG={name}"], cwd=ROOT, capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise SystemExit(f"make claim SLUG={name} refused:\n{r.stdout}{r.stderr}")
    return "specs/" + r.stdout.strip().splitlines()[-1].strip()


def main(argv: list[str]) -> int:
    closed = json.loads(Path(argv[0]).read_text())
    dry = "--dry-run" in argv
    filed: dict[str, str] = {}
    used: set[str] = set()

    def one(key: str, title: str, source: str, entry: str, history: str = "") -> None:
        if key in closed:
            return
        base = slug(title)
        name, n = base, 2
        while name in used or any(p.name.split("-", 1)[-1] == name for p in (ROOT / "specs").iterdir()):
            name, n = f"{base}-{n}", n + 1
        used.add(name)
        d = claim(name, dry)
        if not dry:
            (ROOT / d / "spec.md").write_text(spec_text(title, source, entry, history))
        filed[key] = d

    for name, heading, body in entries():
        source = f'future-work/{name}, "{heading}"'
        if (name, heading) == PIECED:
            context, found = pieces(body)
            for i, (section, bullet) in enumerate(found, 1):
                m = re.match(r"- \*\*(.+?)\*\*", bullet)
                title = (m.group(1) if m else bullet[2:80]).rstrip(".:?") + ("?" if m and m.group(1).endswith("?") else "")
                entry = f"{bullet}\n\n### The context the entry gave every piece ({section})\n\n{context}"
                one(f"{name}#{heading}#{i}", title.rstrip("?") + ("?" if title.endswith("?") else ""), f"{source}, piece {i}", entry)
            continue
        history = ""
        if "was feature 275, withdrawn" in heading:
            history = ("\n\n**History**: this work was feature 275 (`specs/275-village-burial-ground/`), which the GM withdrew "
                       "on 2026-09-28 (its request.md: \"The number stays spent; nothing is built under it\"); it is filed "
                       "under its own number here rather than reopening 275 (plan D5, the plan review of 2026-10-08).")
        one(f"{name}#{heading}", heading, source, body, history)

    out = HERE / "filed.json"
    if not dry:
        out.write_text(json.dumps(filed, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(filed)} filed, {len(closed)} closed" + (" (dry run)" if dry else f"; mapping in {out.relative_to(ROOT)}"))
    for k, v in filed.items():
        print(f"  {v}  <-  {k[:110]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
