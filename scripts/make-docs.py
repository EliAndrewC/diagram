#!/usr/bin/env python3
"""Generate the make-target reference from the Makefile itself, so it cannot go stale.

WHY (GM 2026-09-05): after two rounds of auditing targets by hand - one of which declared everything
valid and was then contradicted the moment the GM asked about specific targets - the durable answer
is to stop hand-maintaining the list. *"our makefile can create its own documentation ... the make
targets and the explanation of what they do is pulled from the makefile and its comments
automatically."*

THERE IS NO PYDOC FOR MAKE, and it is worth saying so rather than implying a library was found. The
`##` help convention this Makefile already used is the de facto standard ("self-documenting
makefile") and it is a PARSING BASE, not a generator: it produces one flat alphabetical list with no
grouping, no arguments column and no HTML. This adds the three things it lacks, and nothing else.

THE CATEGORY LIVES ON THE TARGET, DELIBERATELY. Grouping is editorial - it exists nowhere else in the
code, so it cannot be derived the way this project derives a roster from what code already declares
(constitution X clause 14). The next best thing is to put it where it cannot be forgotten: a
`[category]` tag inside the target's own `##` line, three characters from the thing it describes.
`--check` FAILS on a target with help text and no tag, so adding a target without a category is
caught at the gate rather than noticed months later.

WHAT COUNTS AS A TARGET is derived, not listed: every rule with a recipe and a `##` line. A target
with no help text is REPORTED by `--check` rather than silently omitted - the audit that prompted
this found thirteen such targets, `quick`, `maps` and `reference` among them, invisible to
`make help` for months.

    python3 scripts/make-docs.py --write     # regenerate docs/make-targets.html
    python3 scripts/make-docs.py --check     # fail if it is stale, untagged, or undocumented
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

MAKEFILE = Path(".claude/skills/diagram/Makefile")
OUT = Path("docs/make-targets.html")

# Order and prose for the sections. A category the Makefile uses that is missing here is an ERROR,
# not a silent "other" bucket - an unrecognised tag is almost always a typo.
SECTIONS: list[tuple[str, str, str]] = [
    ("tests", "Tests", "The four tiers, cheapest first. Where a test LIVES decides when it runs, so these differ by scope rather than by filter."),
    ("maps", "Maps", "Generating and checking the pool. `maps` picks its own scope - the reference hamlet alone after a failure, the whole tier after a clean run."),
    ("diagnostics", "Diagnostics", "Read-only questions about a finished map or a generator's decisions. None of these decides what ships."),
    ("performance", "Performance", "The bookends and the three bands. A run that got slower owes records before the push."),
    ("remote", "Remote (AWS CodeBuild)", "Everything except `ci-status` costs money. Remote is currently OFF; `make switches` says so."),
    ("static", "Static checks", "What the gate runs before it spends anything on a map roll."),
    ("project", "Project state", "Switches, audits and the records that make the tooling's own behavior reviewable."),
]


def parse(makefile: Path) -> tuple[list[dict[str, str]], list[str]]:
    """Every documented target, plus the names that have a recipe but no `##` line."""
    text = makefile.read_text(encoding="utf-8")
    documented: list[dict[str, str]] = []
    for m in re.finditer(r"^([a-z][\w-]*):(?!=)[^\n#]*##\s*(.*)$", text, re.M):
        name, rest = m.group(1), m.group(2).strip()
        cat, flag, why = "", "", ""
        tag = re.match(r"\[([\w-]+)\]\s*(.*)", rest)
        if tag:
            cat, rest = tag.group(1), tag.group(2).strip()
        # {internal} - nobody types this; a recipe or a script calls it.
        # {inactive: why} - the target exists and is kept on purpose, but currently does nothing.
        # Two SEPARATE designations because they answer different questions (GM 2026-09-06): "would I
        # ever run this?" and "does running it do anything today?". A target can be neither, either,
        # or both, and collapsing them would hide a disabled thing behind an internal label.
        fl = re.match(r"\{(internal|inactive)(?::\s*([^}]*))?\}\s*(.*)", rest)
        if fl:
            flag, why, rest = fl.group(1), (fl.group(2) or "").strip(), fl.group(3).strip()
        # Arguments are written as WORD= in the help line; the prose is what remains.
        args = re.findall(r"\b([A-Z][A-Z0-9_]*)=", rest)
        documented.append({"name": name, "category": cat, "help": rest, "args": " ".join(sorted(set(args))), "flag": flag, "why": why})
    with_rule = set()
    for m in re.finditer(r"^([a-z][\w-]*(?:\s+[a-z][\w-]*)*):(?!=)[^\n]*\n(?:\t[^\n]*\n)+", text, re.M):
        with_rule.update(m.group(1).split())
    undocumented = sorted(with_rule - {d["name"] for d in documented})
    return sorted(documented, key=lambda d: d["name"]), undocumented


def render(rows: list[dict[str, str]], undocumented: list[str]) -> str:
    by_cat: dict[str, list[dict[str, str]]] = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r)
    parts = [
        "<!-- GENERATED BY scripts/make-docs.py FROM THE MAKEFILE - DO NOT EDIT.",
        "     Edit the target's `##` line in .claude/skills/diagram/Makefile and run `make docs`.",
        "     `make-docs.py --check` fails the gate when this file is stale. -->",
        "<title>make targets</title>",
        "<style>",
        ":root{--bg:#fbfaf7;--fg:#1d1b17;--mut:#6b6560;--line:#ded8cf;--acc:#7a4a20;--code:#f2eee7}",
        "@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#171614;--fg:#e9e5de;--mut:#a09a92;--line:#33302b;--acc:#d0a06a;--code:#22201d}}",
        ":root[data-theme=dark]{--bg:#171614;--fg:#e9e5de;--mut:#a09a92;--line:#33302b;--acc:#d0a06a;--code:#22201d}",
        "body{background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;margin:0;padding:2.5rem 1.25rem 5rem}",
        "main{max-width:62rem;margin:0 auto}",
        "h1{font-size:1.7rem;margin:0 0 .3rem}h2{font-size:1.15rem;margin:2.6rem 0 .3rem;color:var(--acc)}",
        "p.lede{color:var(--mut);margin:.2rem 0 1.4rem}p.sec{color:var(--mut);margin:.2rem 0 .8rem;font-size:.93rem}",
        "div.scroll{overflow-x:auto}",
        "table{border-collapse:collapse;width:100%;margin:.4rem 0 .6rem;font-size:.93rem}",
        "th,td{text-align:left;vertical-align:top;padding:.42rem .6rem;border-bottom:1px solid var(--line)}",
        "th{font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;color:var(--mut);font-weight:600}",
        "td.n{white-space:nowrap;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}",
        "td.a{white-space:nowrap;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--mut);font-size:.86rem}",
        "code{background:var(--code);padding:.08em .32em;border-radius:3px;font-size:.9em}",
        "span.b{margin-left:.5em;font-size:.68rem;text-transform:uppercase;letter-spacing:.04em;padding:.1em .45em;border-radius:3px;background:var(--code);color:var(--mut);border:1px solid var(--line);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}",
        "span.b.off{color:#9a3d2a;border-color:#c8907f}",
        "@media (prefers-color-scheme:dark){:root:not([data-theme=light]) span.b.off{color:#e0a08c;border-color:#7a4436}}",
        ":root[data-theme=dark] span.b.off{color:#e0a08c;border-color:#7a4436}",
        "span.w{color:var(--mut);font-style:italic}",
        "footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);color:var(--mut);font-size:.86rem}",
        "</style>",
        "<main>",
        "<h1>make targets</h1>",
        f"<p class=lede>Every target in the diagram skill's Makefile, grouped. "
        f"{len(rows)} documented. Generated from the Makefile - edit the target's <code>##</code> line, not this page.</p>",
    ]
    seen = set()
    for key, title, blurb in SECTIONS:
        group = by_cat.get(key, [])
        if not group:
            continue
        seen.add(key)
        parts += [f"<h2>{html.escape(title)}</h2>", f"<p class=sec>{html.escape(blurb)}</p>",
                  "<div class=scroll><table><tr><th>target</th><th>arguments</th><th>what it is</th></tr>"]
        for r in group:
            prose = re.sub(r"\s{2,}[A-Z][A-Z0-9_]*=.*$", "", r["help"]).strip()
            badge = ""
            if r.get("flag") == "internal":
                badge = "<span class=b title='called by a recipe or a script - you would not type this'>internal</span>"
            elif r.get("flag") == "inactive":
                badge = f"<span class='b off' title=\"{html.escape(r.get('why') or 'currently does nothing')}\">inactive</span>"
            note = f" <span class=w>{html.escape(r['why'])}</span>" if r.get("flag") == "inactive" and r.get("why") else ""
            parts.append(
                f"<tr><td class=n>make {html.escape(r['name'])}{badge}</td>"
                f"<td class=a>{html.escape(r['args']) or '&ndash;'}</td>"
                f"<td>{html.escape(prose)}{note}</td></tr>"
            )
        parts.append("</table></div>")
    stray = sorted(set(by_cat) - seen - {""})
    if stray:
        parts.append(f"<p class=sec><b>Unrecognised categories:</b> {html.escape(', '.join(stray))}</p>")
    if undocumented:
        parts += ["<h2>Undocumented</h2>",
                  "<p class=sec>These have a recipe but no <code>##</code> line, so they appear in no help output. "
                  "Each is either an internal helper or an oversight.</p>",
                  "<div class=scroll><table><tr><th>target</th></tr>"]
        parts += [f"<tr><td class=n>make {html.escape(n)}</td></tr>" for n in undocumented]
        parts.append("</table></div>")
    parts += ["<footer>Generated by <code>scripts/make-docs.py</code>. "
              "<code>make docs</code> regenerates it; the gate fails if it is stale.</footer>", "</main>"]
    return "\n".join(parts) + "\n"


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 and not argv[1].startswith("--") else Path(".").resolve()
    mode = next((a for a in argv[1:] if a.startswith("--")), "--check")
    mk, out = root / MAKEFILE, root / OUT
    if not mk.is_file():
        print(f"make-docs: no Makefile at {mk}", file=sys.stderr)
        return 2
    rows, undocumented = parse(mk)
    untagged = [r["name"] for r in rows if not r["category"]]
    body = render(rows, undocumented)

    if mode == "--write":
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
        print(f"make-docs: wrote {OUT} - {len(rows)} targets, {len(undocumented)} undocumented")
        return 0

    problems = []
    if untagged:
        problems.append(f"target(s) with help text but no [category] tag: {', '.join(untagged)}")
    if not out.is_file():
        problems.append(f"{OUT} does not exist")
    elif out.read_text(encoding="utf-8") != body:
        problems.append(f"{OUT} is STALE - the Makefile changed since it was generated")
    if problems:
        print("\n\033[1mmake-docs: the target reference is out of date.\033[0m\n", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print("\n  Fix: add the [category] tag to the target's `##` line if it is missing, then\n"
              "       run `make docs`. The page is generated from the Makefile so it cannot drift;\n"
              "       that is the whole point of it being checked here.\n", file=sys.stderr)
        return 1
    print(f"make-docs: {OUT} is current ({len(rows)} targets)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
