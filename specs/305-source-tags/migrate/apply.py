#!/usr/bin/env python3
"""Feature 305, one-time: apply the classifiers' results to the registry (plan D10, research R3-R4).

    python3 specs/305-source-tags/migrate/apply.py IN_DIR [--write]

Reads every `out-NN.jsonl` under IN_DIR (one line per entry: key, period, region, kind, why or null, unsettled?) and,
for each non-canon registry entry:

- checks the tags against `research/source-tags.json` and that every entry was classified once;
- checks a trimmed limits paragraph against research R4 - no longer than the old, no word the old lacks beyond the
  connectives, every inline tag it carries one the old carried, every HTML comment kept, the tags balanced, and not
  empty - and REFUSES a trim that fails (the entry keeps its old paragraph and is listed for the session);
- lists the consistency flags of research R3 (a host that decides kind, disagreeing; a premodern tag on evidence the
  write-up dates after the cut-off) and every `unsettled` entry;

and with `--write` writes the marker as the entry's last line and the passing trims. Without it, a dry run. The report
goes to stdout as markdown.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(".claude/skills/diagram/research")
REGISTRY = ROOT / "sources" / "010-works-cited"
FACETS = ("period", "region", "kind")
WHY = "<p><em>Why it applies, and its limits:</em> "
CANON = re.compile(r"\bl7r\.md\b|\bbudgets\.md\b")
#: The words a trim may use to mend a joint, which need not appear in the old paragraph (research R4).
CONNECTIVES = set("and but its it the that this is are for of a an to in on as so only which here used".split())
_WORD = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.U)
_TAG = re.compile(r"<(?!!--)[^>]+>")
_COMMENT = re.compile(r"<!--.*?-->", re.S)
#: A host that decides KIND (research R2): the kind every entry on it should carry.
HOST_KIND = {"wikipedia.org": "reference", "kotobank.jp": "reference", "baike.baidu.com": "reference", "wikisource.org": "primary"}
_LATE = re.compile(r"\b(Meiji|Taish[oō]|Sh[oō]wa|Republican|19[0-4]\d|18[7-9]\d)\b")


def words(text: str) -> list[str]:
    return [w.lower() for w in _WORD.findall(_TAG.sub(" ", _COMMENT.sub(" ", text)))]


def trim_problems(old: str, new: str) -> list[str]:
    """Why a trim breaks research R4, or nothing."""
    out = []
    if not new.strip():
        out.append("empty")
    if len(new) > len(old):
        out.append(f"longer ({len(new)} > {len(old)})")
    added = sorted(set(words(new)) - set(words(old)) - CONNECTIVES)
    if added:
        out.append("new words: " + ", ".join(added[:8]))
    old_tags = set(_TAG.findall(_COMMENT.sub("", old)))
    new_tags = _TAG.findall(_COMMENT.sub("", new))
    alien = sorted({t for t in new_tags if t not in old_tags})
    if alien:
        out.append("new markup: " + " ".join(alien[:4]))
    for name in ("em", "code", "a", "span", "strong", "q"):
        if len(re.findall(rf"<{name}[\s>]", new)) != new.count(f"</{name}>"):
            out.append(f"unbalanced <{name}>")
    lost = [c for c in _COMMENT.findall(old) if c not in new]
    if lost:
        out.append(f"{len(lost)} comment(s) lost")
    return out


def main() -> int:
    in_dir = pathlib.Path(sys.argv[1])
    write = "--write" in sys.argv
    vocab = json.loads((ROOT / "source-tags.json").read_text(encoding="utf-8"))
    known = {f: {d["id"] for d in vocab[f]} for f in FACETS}
    results: dict[str, dict] = {}
    dupes = []
    for path in sorted(in_dir.glob("out-*.jsonl")):
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if row["key"] in results:
                dupes.append(row["key"])
            row["_at"] = f"{path.name}:{n}"
            results[row["key"]] = row
    bad_tags, refused, flags, unsettled, missing = [], [], [], [], []
    tagged = trimmed = 0
    old_total = new_total = 0
    for path in sorted(REGISTRY.glob("*.html")):
        text = path.read_text(encoding="utf-8")
        key = re.search(r'<h3 id="([^"]+)"', text).group(1)  # type: ignore[union-attr]
        first = re.search(r"</h3>\s*<p>(.*?)</p>", text, re.S)
        if first and CANON.search(first.group(1)):
            continue
        row = results.get(key)
        if row is None:
            missing.append(key)
            continue
        problems = [f"{f}: {row.get(f)!r}" for f in FACETS if not row.get(f) or not isinstance(row[f], list) or any(v not in known[f] for v in row[f]) or len(set(row[f])) != len(row[f])]
        if problems:
            bad_tags.append(f"`{key}` ({row['_at']}): " + "; ".join(problems))
            continue
        if row.get("unsettled"):
            unsettled.append(f"`{key}`: {row['unsettled']} - tagged {row['period']}/{row['region']}/{row['kind']}")
        cite = first.group(1) if first else ""
        host = next((h for h in HOST_KIND if h in re.sub(r"<!--.*?-->", "", cite)), None)
        if host and row["kind"][0] != HOST_KIND[host]:
            flags.append(f"`{key}`: on {host} but kind {row['kind']}")
        what = re.search(r"<p><em>What it is:</em>(.*?)</p>", text, re.S)
        used = re.search(r"<p><em>Used for:</em>(.*?)</p>", text, re.S)
        body = (what.group(1) if what else "") + " " + (used.group(1) if used else "")
        if row["period"][0] == "premodern" and _LATE.search(body):
            flags.append(f"`{key}`: premodern, but its write-up names {_LATE.search(body).group(0)}")  # type: ignore[union-attr]
        m = re.search(re.escape(WHY) + r"(.*?)</p>", text, re.S)
        old = m.group(1).strip() if m else ""
        old_total += len(old)
        new_why = row.get("why")
        if new_why is not None and m is not None and new_why.strip() != old:
            why_problems = trim_problems(old, new_why)
            if why_problems:
                refused.append(f"`{key}`: " + "; ".join(why_problems))
                new_total += len(old)
            else:
                text = text.replace(WHY + m.group(1), WHY + new_why.strip(), 1)
                trimmed += 1
                new_total += len(new_why.strip())
        else:
            new_total += len(old)
        marker = "<!-- tags: " + "; ".join(f"{f}={','.join(row[f])}" for f in FACETS) + " -->"
        text = re.sub(r"\n?<!-- tags: .*? -->[ \t]*\n?", "\n", text).rstrip("\n") + "\n" + marker + "\n"
        tagged += 1
        if write:
            path.write_text(text, encoding="utf-8")
    print(f"# Feature 305 migration report ({'written' if write else 'dry run'})\n")
    print(f"- tagged: {tagged}; trimmed: {trimmed}; trims refused: {len(refused)}; bad tags: {len(bad_tags)}; unclassified: {len(missing)}; classified twice: {len(dupes)}")
    print(f"- limits paragraphs: {old_total:,} characters before, {new_total:,} after\n")
    for title, rows in (("Bad tags", bad_tags), ("Unclassified", [f"`{k}`" for k in missing]), ("Classified twice", [f"`{k}`" for k in dupes]), ("Trims refused (R4)", refused), ("Unsettled", unsettled), ("Consistency flags (R3)", flags)):
        print(f"## {title} ({len(rows)})\n")
        print("\n".join(f"- {r}" for r in rows) or "- none")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
