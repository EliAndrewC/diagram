"""A copy of a few of the real record's questions and registry entries, for a test whose subject is a tool, not the record.

Feature 383 amendment 5 (plan D33): a test of the bundler or the owed list ran the tool over the real record, and so read
all of it - 1,400 to 4,600 files - and re-ran on an edit to any page anywhere. The tool reads only what its root holds, so a
root holding the pages the test names reads only those: the test still runs on real pages, the ones its assertions were
written against, and re-runs when one of THEM changes, not when another does. The record's own files (`tags.json`,
`contents.json`, `STYLE.md`, the section pages, the assets) come with it, because every tool reads them, and so do the
modals and the glossary the bundles carry (`INTERACTIVE`): a glossary edit still re-runs such a test, a record edit does not.
"""

from __future__ import annotations

import json
import pathlib
import re
import shutil

REPO = pathlib.Path(__file__).resolve().parents[2]
RECORD = REPO / "research"
INTERACTIVE = ("classes", "compound_kinds", "assets/modals", "assets/glossary")


def subset(dst: pathlib.Path, questions: tuple[str, ...] = (), keys: tuple[str, ...] = ()) -> pathlib.Path:
    """A repository root under `dst` holding the record's own files, every file of each question numbered in `questions`
    (`"0087"`), and the registry entry of each key in `keys` and of each key those questions' notes cite; returns the root."""
    rec = dst / "research"
    rec.mkdir(parents=True)
    for f in RECORD.iterdir():
        if f.is_file():
            shutil.copyfile(f, rec / f.name)
    shutil.copytree(RECORD / "assets", rec / "assets")
    src = rec / "sources"
    src.mkdir()
    for f in (RECORD / "sources").iterdir():
        if f.is_file():
            shutil.copyfile(f, src / f.name)
    q = rec / "questions"
    q.mkdir()
    for n in questions:
        for f in (RECORD / "questions").glob(f"{n}-*"):
            shutil.copyfile(f, q / f.name)
    _prune_contents(rec)
    have = {f.name for f in q.iterdir()}  # a confusable pair names two questions; keep the pairs both of whose are copied
    pairs = json.loads((rec / "confusables.json").read_text(encoding="utf-8"))
    kept = [c for c in pairs if c["a"].split("#")[0] in have and c["b"].split("#")[0] in have]
    (rec / "confusables.json").write_text(json.dumps(kept), encoding="utf-8")
    cited = {k for f in q.glob("*.notes.html") for k in re.findall(r"<code>([a-z0-9][a-z0-9-]*)</code>", f.read_text(encoding="utf-8"))}
    for key in sorted(set(keys) | cited):
        found = [e for e in (RECORD / "sources").glob(f"*/[0-9]*-{key}.html") if e.name.split("-", 1)[1] == f"{key}.html"]
        assert found or key not in keys, f"no registry entry for the key `{key}` the test named"
        if not found:
            continue  # a `<code>` in a note that names no work (a term, a key since retired)
        entry = found[0]
        (src / entry.parent.name).mkdir(exist_ok=True)
        shutil.copyfile(entry, src / entry.parent.name / entry.name)
    for d in INTERACTIVE:
        shutil.copytree(REPO / "l7r/diagram/interactive" / d, dst / "l7r/diagram/interactive" / d)
    return dst


def _prune_contents(rec: pathlib.Path) -> None:
    """Keep only the sections of `contents.json` some copied question falls in: the record refuses a section clause that
    matches no question (a typo there), and a copy of five questions leaves most of them empty."""
    primaries = set()
    for f in (rec / "questions").glob("*.html"):
        m = re.search(r"<!-- tags: subject=([a-z0-9-]+)", f.read_text(encoding="utf-8"))
        primaries |= {m.group(1)} if m else set()

    def keep(sections: list[dict]) -> list[dict]:
        out = []
        for s in sections:
            p = [c for c in s.get("takes", []) if set([c["primary"]] if isinstance(c["primary"], str) else c["primary"]) & primaries]
            kids = keep(s.get("sections", []))
            if p or kids:
                out.append({**s, "takes": p, "sections": kids})
        return out

    path = rec / "contents.json"
    contents = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps({**contents, "sections": keep(contents["sections"])}), encoding="utf-8")
