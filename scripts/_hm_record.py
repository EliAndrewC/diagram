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
import re
import sys

RECORD = "research"
# GUARD_EDIT_OK: feature 303 - the record's page directories are gone: the questions are one flat directory and the
# registry the one page of fragments left, so an edit aimed at any built page is re-aimed among the questions (or the
# registry's fragments), and a check reads a question's files by its number. A change of layout; nothing loosened.
#: The glossary is the same kind of file in a different tree (feature 259): assembled from one file
#: per term, read by the engine, and never hand-edited. One case here rather than a second guard.
GLOSSARY = os.path.join("l7r", "diagram", "interactive", "assets", "glossary.json")
#: The questions, one stem each (feature 303), and the registry's fragments.
QUESTIONS = "questions"
_REGISTRY = "SOURCES.html"
#: The built site (feature 301): never edited, never searched for a fragment - it is the record again, page by page.
_SITE = "site"
_STEM = re.compile(r"^(\d{4})-[^.]+(?:\.drawing)?\.html$")


def page_dir_for(rel: str) -> str | None:
    """Where the fragments behind a built or assembled page are, or None if this path is not one.

    The registry - `research/SOURCES.html`, `research/site/sources/...` - is `research/sources`; any other page of the
    site (a question's page, a section's, a tag's, the home page, the single page), or a page the record assembled before
    feature 301 at its root, is `research/questions`. A fragment itself is not a page.
    """
    rel = rel.replace(os.sep, "/")
    if rel.endswith(GLOSSARY.replace(os.sep, "/")):
        return rel[: -len(".json")]                   # `.../assets/glossary.json` -> `.../assets/glossary`
    if RECORD.replace(os.sep, "/") + "/" not in rel + "/" or not rel.endswith(".html"):
        return None
    inside = rel.split(RECORD.replace(os.sep, "/") + "/", 1)[1]
    root = rel[: len(rel) - len(inside)]
    if inside.startswith(_SITE + "/"):
        return root + ("sources" if inside.startswith(f"{_SITE}/sources/") else QUESTIONS)
    if inside == _REGISTRY:
        return root + "sources"
    if "/" in inside.removeprefix("citations/"):
        return None                                   # inside a directory of fragments: this IS a fragment
    return root + QUESTIONS


def fragments_holding(page_dir: str, needle: str, root: str) -> list[str]:
    """Every fragment of this page whose text contains `needle`, as repository-relative paths."""
    here = os.path.join(root, page_dir)
    out = []
    for base, dirs, names in os.walk(here):
        dirs[:] = [d for d in dirs if d != _SITE and not d.startswith(".site-")]  # the build, not the record
        for name in sorted(names):
            path = os.path.join(base, name)
            try:
                with open(path, encoding="utf-8") as fh:
                    if needle and needle in fh.read():
                        out.append(os.path.relpath(path, root).replace(os.sep, "/"))
            except (OSError, UnicodeDecodeError):
                continue
    return sorted(out)


def fragments_for(q: str, root: str) -> list[str]:
    """The files a check should READ for the questions `q` names - each page and its notes, nothing else.

    This is where the saving of feature 258 is actually collected (spec FR-023): a recorded `record-format` run spent 88%
    of its context on one page, and `quote-check` 90% (research R3), to check one entry. `q` names a question by its
    number (`0412`, `412` - both its pages) or a page by its file name (`0412-x.drawing.html`), comma- or
    space-separated (feature 303); a section or a tag is the engine's to resolve (`make ... IN=`).
    """
    here = os.path.join(root, RECORD, QUESTIONS)
    if not os.path.isdir(here):
        return []
    names = sorted(n for n in os.listdir(here) if _STEM.match(n))
    out: list[str] = []
    for term in (t for t in re.split(r"[,\s]+", q) if t):
        picked = [term] if term in names else [n for n in names if term.isdigit() and int(_STEM.match(n).group(1)) == int(term)]  # type: ignore[union-attr]
        for name in picked:
            for f in (name, name[: -len(".html")] + ".notes.html"):
                if os.path.isfile(os.path.join(here, f)) and f"{RECORD}/{QUESTIONS}/{f}" not in out:
                    out.append(f"{RECORD}/{QUESTIONS}/{f}")
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
                           f"`{_rebuild(rel)}` at the repository root."}
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
        # `--fragments <Q>` - what a check over one question should read
        print("\n".join(fragments_for(sys.argv[2], os.getcwd())))
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
                f"{verdict['fragment']}. Run `make record` at the repository root afterwards to rebuild "
                f"the site (research/site/) from it."),
        }}
    print(json.dumps(verdict))
    return 0


def selftest() -> int:
    import tempfile

    q = f"{RECORD}/{QUESTIONS}"
    assert page_dir_for(f"{RECORD}/SOURCES.html") == f"{RECORD}/sources"
    assert page_dir_for(f"{RECORD}/site/sources/fei-1939.html") == f"{RECORD}/sources"
    assert page_dir_for(f"{RECORD}/site/q/x.html") == q, "a question's page of the site (features 301, 303)"
    assert page_dir_for(f"{RECORD}/site/research/fields.html") == q and page_dir_for(f"{RECORD}/site/all.html") == q
    assert page_dir_for(f"{RECORD}/ways.html") == q and page_dir_for(f"{RECORD}/citations/ways.html") == q, "a page assembled before 301"
    assert page_dir_for(f"{q}/0010-x.html") is None, "a fragment is not an assembled page"
    assert page_dir_for(f"{RECORD}/sources/010-works-cited.html") is None
    assert page_dir_for(f"{RECORD}/assets/record.js") is None
    assert page_dir_for("docs/guards.md") is None
    with tempfile.TemporaryDirectory() as root:
        qdir = os.path.join(root, q)
        os.makedirs(qdir)
        for name, text in (
            ("0010-x.html", "<h2 id='x'>X</h2>\nthe deck lands ten feet past the bank\n"),
            ("0010-x.notes.html", '<li data-note="k">body</li>\n'),
            ("0010-x.drawing.html", "<h2 id='dx'>DX</h2>\nshared sentence\n"),
            ("0020-y.html", "<h2 id='y'>Y</h2>\nshared sentence\n"),
        ):
            with open(os.path.join(qdir, name), "w", encoding="utf-8") as fh:
                fh.write(text)
        page = os.path.join(root, RECORD, "site", "q", "x.html")
        one = decide("Edit", page, {"old_string": "ten feet past the bank"}, root)
        assert one["verdict"] == "rewrite" and one["fragment"] == f"{q}/0010-x.html", one
        os.makedirs(os.path.join(root, RECORD, "site", "q"))
        with open(page, "w", encoding="utf-8") as fh:
            fh.write("the deck lands ten feet past the bank\n")
        whole = decide("Edit", os.path.join(root, RECORD, "site", "all.html"), {"old_string": "ten feet past the bank"}, root)
        assert whole["verdict"] == "rewrite" and whole["fragment"] == f"{q}/0010-x.html", "the site itself is never a holder"
        assert decide("Edit", page, {"old_string": "shared sentence"}, root)["rule"] == "text-in-several-fragments"
        assert decide("Edit", page, {"old_string": "nowhere at all"}, root)["rule"] == "text-in-no-fragment"
        assert decide("Write", page, {"content": "x"}, root)["rule"] == "write-to-assembled-page"
        assert decide("Edit", os.path.join(qdir, "0010-x.html"), {"old_string": "the deck"}, root)["verdict"] == "pass"
        assert decide("Edit", os.path.join(root, RECORD, "SOURCES.html"), {"old_string": "x"}, root)["verdict"] == "pass", \
            "a registry with no fragment directory is not this guard's"
        terms = os.path.join(root, os.path.dirname(GLOSSARY), "glossary")
        os.makedirs(terms)
        with open(os.path.join(terms, "0010-girder.json"), "w", encoding="utf-8") as fh:
            fh.write('{"term": "girder", "variants": ["girder"], "def": "the main beam"}')
        glossary = os.path.join(root, GLOSSARY)
        moved = decide("Edit", glossary, {"old_string": "the main beam"}, root)
        assert moved["verdict"] == "rewrite" and moved["fragment"].endswith("0010-girder.json"), moved
        assert "make glossary" in decide("Write", glossary, {}, root)["message"]
        assert fragments_for("0010", root) == [f"{q}/0010-x.drawing.html", f"{q}/0010-x.html", f"{q}/0010-x.notes.html"]
        assert fragments_for("10, 0020-y.html", root)[-1] == f"{q}/0020-y.html"
        assert fragments_for("0010-x.drawing.html", root) == [f"{q}/0010-x.drawing.html"]
        assert fragments_for("nosuch", root) == [] and fragments_for("0010", os.path.join(root, "elsewhere")) == []
    print("_hm_record selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
