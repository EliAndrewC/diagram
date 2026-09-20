#!/usr/bin/env python3
"""What an Edit or a Write aimed at an ASSEMBLED record page should become (feature 258).

The record's pages are assembled from per-entry fragments and are never hand-edited: an edit that
landed in a page would be undone by the next `make record`, silently, and the fragment - the thing the
next session and every checking agent reads - would still say the old thing. The gate and the push
catch a page that has drifted; this catches the edit that would drift it, one round trip earlier.

It REWRITES rather than refuses wherever it can (feature 164's ladder, feature 204's measurement): an
Edit whose `old_string` stands in exactly one fragment is re-aimed at that fragment, which is where the
session meant to put it. Only two cases refuse, and both are decisions a guard cannot make - text that
is in no fragment or in several, and a whole-file Write, which cannot be routed anywhere.

A page whose fragments do not exist yet is not this guard's business: a stage that has not landed is
edited the old way.
"""

from __future__ import annotations

import json
import os
import sys

RECORD = os.path.join(".claude", "skills", "diagram", "research")
#: The glossary is the same kind of file in a different tree (feature 259): assembled from one file
#: per term, read by the engine, and never hand-edited. One case here rather than a second guard.
GLOSSARY = os.path.join(".claude", "skills", "diagram", "l7r", "diagram", "interactive", "assets", "glossary.json")
#: Where a page's fragments live. The citations page's notes live in the RESEARCH page's directory -
#: one question's prose and its notes are siblings, which is the whole of stage 3.
_REGISTRY = "SOURCES.html"


def page_dir_for(rel: str) -> str | None:
    """The fragment directory of an assembled page, or None if this path is not one.

    `research/ways.html` and `research/citations/ways.html` -> `research/ways`;
    `research/cities/fabric.html` and `research/citations/cities/fabric.html` -> `research/cities/fabric`;
    `research/SOURCES.html` -> `research/sources`.
    """
    rel = rel.replace(os.sep, "/")
    if rel.endswith(GLOSSARY.replace(os.sep, "/")):
        return rel[: -len(".json")]                   # `.../assets/glossary.json` -> `.../assets/glossary`
    if RECORD.replace(os.sep, "/") + "/" not in rel + "/" or not rel.endswith(".html"):
        return None
    inside = rel.split(RECORD.replace(os.sep, "/") + "/", 1)[1]
    root = rel[: len(rel) - len(inside)]
    if inside == _REGISTRY:
        return root + "sources"
    if inside.startswith("citations/"):
        inside = inside[len("citations/"):]
    parts = inside.split("/")
    if len(parts) > 2 or (len(parts) == 2 and parts[0] != "cities"):
        return None                                   # inside a page directory: this IS a fragment
    return root + inside[: -len(".html")]


def fragments_holding(page_dir: str, needle: str, root: str) -> list[str]:
    """Every fragment of this page whose text contains `needle`, as repository-relative paths."""
    here = os.path.join(root, page_dir)
    out = []
    for base, _dirs, names in os.walk(here):
        for name in sorted(names):
            path = os.path.join(base, name)
            try:
                with open(path, encoding="utf-8") as fh:
                    if needle and needle in fh.read():
                        out.append(os.path.relpath(path, root).replace(os.sep, "/"))
            except (OSError, UnicodeDecodeError):
                continue
    return sorted(out)


def fragments_for(page: str, section: str, root: str) -> list[str]:
    """The fragments a check should READ for one question - the question and its notes, nothing else.

    This is where the saving of feature 258 is actually collected (spec FR-023): a recorded
    `record-format` run spent 88% of its context on one page, and `quote-check` 90% (research R3), to
    check one entry. `section` matches a fragment's name - its prefix, its heading id, or any part of
    either - and an empty one names every question of the page.
    """
    name = page.removesuffix(".html")
    page_dir = os.path.join(RECORD, "sources" if name in ("sources", "SOURCES") else name)
    here = os.path.join(root, page_dir)
    if not os.path.isdir(here):
        return []
    # A caller names a section the way it reads on the page ("the bund runs along the channel bank")
    # or the way the file spells it ("040", "the-bund-runs-along"). Both match: a fragment's name is a
    # convenience, and a lookup that only accepted one of the two forms would be a second thing to learn.
    forms = {section.casefold(), section.casefold().replace(" ", "-")}
    out = []
    for entry in sorted(os.listdir(here)):
        if not entry.endswith(".html") or entry.startswith("_") or entry.endswith(".notes.html"):
            continue
        if section and not any(f in entry.casefold() for f in forms):
            continue
        out.append(f"{page_dir}/{entry}")
        notes = entry[: -len(".html")] + ".notes.html"
        if os.path.isfile(os.path.join(here, notes)):
            out.append(f"{page_dir}/{notes}")
    return out


def _rebuild(rel: str) -> str:
    """The command that rebuilds this assembled file - named in the refusal, because a refusal a
    session cannot act on costs the same round trip as no refusal."""
    return "make glossary" if rel.endswith("glossary.json") else "make record"


def decide(tool: str, file_path: str, tool_input: dict, root: str) -> dict:
    """`{"verdict": "pass"}`, or a rewrite carrying the fragment, or a refusal carrying its message."""
    if tool not in ("Edit", "Write") or not file_path:
        return {"verdict": "pass"}
    rel = os.path.relpath(os.path.abspath(file_path), root).replace(os.sep, "/")
    page_dir = page_dir_for(rel)
    if page_dir is None or not os.path.isdir(os.path.join(root, page_dir)):
        return {"verdict": "pass", "reason": "not an assembled page, or its stage has not landed"}
    if tool == "Write":
        return {"verdict": "refuse", "rule": "write-to-assembled-page", "page": rel, "dir": page_dir,
                "message": f"{rel} is ASSEMBLED from {page_dir}/ and is never written by hand - the next "
                           f"`make record` would overwrite it, and the fragments a session and every "
                           f"checking agent read would still say the old thing. A whole-file write "
                           f"cannot be routed to a fragment: edit the fragments, then run "
                           f"`{_rebuild(rel)}` in .claude/skills/diagram."}
    old = str(tool_input.get("old_string", ""))
    holders = fragments_holding(page_dir, old, root)
    if len(holders) == 1:
        return {"verdict": "rewrite", "rule": "edit-moved-to-fragment", "page": rel, "fragment": holders[0]}
    if not holders:
        why = ("Either it is JSON the assembly WRITES - the object's braces, its one-space indentation, "
               "a term's own key - which no term file carries; or the file is stale"
               if rel.endswith("glossary.json") else
               "Either it is text the assembly WRITES - a footnote number, a reference id, a back link, "
               "the derived works block - which is not edited at all; or the page is stale")
        return {"verdict": "refuse", "rule": "text-in-no-fragment", "page": rel, "dir": page_dir,
                "message": f"{rel} is ASSEMBLED from {page_dir}/, and the text this edit replaces is in "
                           f"none of its fragments. {why}, and `{_rebuild(rel)}` will restore it."}
    return {"verdict": "refuse", "rule": "text-in-several-fragments", "page": rel, "dir": page_dir,
            "message": f"{rel} is ASSEMBLED from {page_dir}/, and the text this edit replaces stands in "
                       f"{len(holders)} fragments:\n  " + "\n  ".join(holders)
                       + "\nThe guard will not choose between them - aim the edit at the one you mean."}


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        return selftest()
    if len(sys.argv) > 2 and sys.argv[1] == "--fragments":
        # `--fragments <page> [section]` - what a check over one question should read
        print("\n".join(fragments_for(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "", os.getcwd())))
        return 0
    payload = json.load(sys.stdin)
    root = payload.get("cwd") or os.getcwd()
    tool_input = payload.get("tool_input") or {}
    verdict = decide(payload.get("tool_name", ""), str(tool_input.get("file_path", "")), tool_input, root)
    if verdict["verdict"] == "rewrite":
        updated = dict(tool_input)
        updated["file_path"] = os.path.join(root, verdict["fragment"])
        verdict["hook"] = {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": updated,
            "additionalContext": (
                f"{verdict['page']} is assembled from {os.path.dirname(verdict['fragment'])}/ and is "
                f"never hand-edited, so this edit was re-aimed at the one fragment holding that text: "
                f"{verdict['fragment']}. Run `make record` in .claude/skills/diagram afterwards - the "
                f"gate and the push both refuse a page that no longer matches its fragments."),
        }}
    print(json.dumps(verdict))
    return 0


def selftest() -> int:
    import tempfile

    assert page_dir_for(f"{RECORD}/ways.html") == f"{RECORD}/ways"
    assert page_dir_for(f"{RECORD}/citations/ways.html") == f"{RECORD}/ways"
    assert page_dir_for(f"{RECORD}/cities/fabric.html") == f"{RECORD}/cities/fabric"
    assert page_dir_for(f"{RECORD}/citations/cities/fabric.html") == f"{RECORD}/cities/fabric"
    assert page_dir_for(f"{RECORD}/SOURCES.html") == f"{RECORD}/sources"
    assert page_dir_for(f"{RECORD}/ways/010-x.html") is None, "a fragment is not an assembled page"
    assert page_dir_for(f"{RECORD}/assets/record.js") is None
    assert page_dir_for("docs/guards.md") is None
    with tempfile.TemporaryDirectory() as root:
        page_dir = os.path.join(root, RECORD, "ways")
        os.makedirs(page_dir)
        with open(os.path.join(page_dir, "010-x.html"), "w", encoding="utf-8") as fh:
            fh.write("<h2 id='x'>X</h2>\nthe deck lands ten feet past the bank\n")
        with open(os.path.join(page_dir, "020-y.html"), "w", encoding="utf-8") as fh:
            fh.write("<h2 id='y'>Y</h2>\nshared sentence\n")
        with open(os.path.join(page_dir, "030-z.html"), "w", encoding="utf-8") as fh:
            fh.write("<h2 id='z'>Z</h2>\nshared sentence\n")
        page = os.path.join(root, RECORD, "ways.html")
        one = decide("Edit", page, {"old_string": "ten feet past the bank"}, root)
        assert one["verdict"] == "rewrite" and one["fragment"].endswith("010-x.html"), one
        assert decide("Edit", page, {"old_string": "shared sentence"}, root)["rule"] == "text-in-several-fragments"
        assert decide("Edit", page, {"old_string": "nowhere at all"}, root)["rule"] == "text-in-no-fragment"
        assert decide("Write", page, {"content": "x"}, root)["rule"] == "write-to-assembled-page"
        assert decide("Edit", os.path.join(page_dir, "010-x.html"), {"old_string": "the deck"}, root)["verdict"] == "pass"
        assert decide("Edit", os.path.join(root, RECORD, "towns.html"), {"old_string": "x"}, root)["verdict"] == "pass", \
            "a page whose stage has not landed is edited the old way"
        terms = os.path.join(root, os.path.dirname(GLOSSARY), "glossary")
        os.makedirs(terms)
        with open(os.path.join(terms, "0010-girder.json"), "w", encoding="utf-8") as fh:
            fh.write('{"term": "girder", "variants": ["girder"], "def": "the main beam"}')
        glossary = os.path.join(root, GLOSSARY)
        moved = decide("Edit", glossary, {"old_string": "the main beam"}, root)
        assert moved["verdict"] == "rewrite" and moved["fragment"].endswith("0010-girder.json"), moved
        assert "make glossary" in decide("Write", glossary, {}, root)["message"]
        with open(os.path.join(page_dir, "010-x.notes.html"), "w", encoding="utf-8") as fh:
            fh.write('<li data-note="k">body</li>\n')
        assert fragments_for("ways", "010", root) == [f"{RECORD}/ways/010-x.html", f"{RECORD}/ways/010-x.notes.html"]
        assert fragments_for("ways", "x", root)[0].endswith("010-x.html")
        assert len(fragments_for("ways", "", root)) == 4, "every question of the page, with its notes"
        assert fragments_for("ways", "nosuch", root) == []
    print("_hm_record selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
