#!/usr/bin/env python3
"""Feature 305, one-time: apply the registry-wide sweeps the sample check called for (plan D11, SC-004/SC-005).

    python3 specs/305-source-tags/migrate/apply_sweep.py DIR [--write]

Reads, under DIR: `adjudicated-A.jsonl` (tags judged again: premodern-only entries whose write-up names a modern date),
`restored-C.jsonl` (trims that may have lost a source-specific limit: the paragraph rebuilt from the ORIGINAL's words),
and `retrimmed-*.jsonl` (paragraphs that still restated a label, trimmed again). Every paragraph change is held to
research R4 as `apply.py` holds it - against the current paragraph for a re-trim, and against the original for a
restore, whose words it may only take back. A change that fails is listed, never written.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("_apply", HERE / "apply.py")
assert _spec and _spec.loader
ap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ap)

MARKER = re.compile(r"<!-- tags: .*? -->")


def rows(path: pathlib.Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []


def main() -> int:
    d = pathlib.Path(sys.argv[1])
    write = "--write" in sys.argv
    files = {re.search(r'<h3 id="([^"]+)"', p.read_text(encoding="utf-8")).group(1): p for p in ap.REGISTRY.glob("*.html")}  # type: ignore[union-attr]
    originals = {}
    for p in sorted((d / "batches").glob("batch-*.jsonl")):
        originals.update({r["key"]: r["why"] for r in rows(p)})
    texts = {k: files[k].read_text(encoding="utf-8") for k in files}
    retagged = trimmed = restored = 0
    refused: list[str] = []
    for r in rows(d / "adjudicated-A.jsonl"):
        if r.get("changed"):
            marker = "<!-- tags: " + "; ".join(f"{f}={','.join(r[f])}" for f in ap.FACETS) + " -->"
            texts[r["key"]] = MARKER.sub(marker, texts[r["key"]], count=1)
            retagged += 1

    def replace_why(key: str, new: str, against: str, label: str) -> bool:
        m = re.search(re.escape(ap.WHY) + r"(.*?)</p>", texts[key], re.S)
        if m is None:
            refused.append(f"`{key}` ({label}): no limits paragraph")
            return False
        problems = ap.trim_problems(against, new)
        if label == "restore":  # a restore may be longer than the trim it undoes, never longer than the original
            problems = [p for p in problems if not p.startswith("longer")] + ([f"longer than the original"] if len(new) > len(against) else [])
        if problems:
            refused.append(f"`{key}` ({label}): " + "; ".join(problems))
            return False
        texts[key] = texts[key].replace(ap.WHY + m.group(1), ap.WHY + new.strip(), 1)
        return True

    for r in rows(d / "restored-C.jsonl"):
        if r.get("why") and replace_why(r["key"], r["why"], originals[r["key"]], "restore"):
            restored += 1
    for p in sorted(d.glob("retrimmed-*.jsonl")):
        for r in rows(p):
            if r.get("why"):
                m = re.search(re.escape(ap.WHY) + r"(.*?)</p>", texts[r["key"]], re.S)
                if m and r["why"].strip() != m.group(1).strip() and replace_why(r["key"], r["why"], m.group(1).strip(), "re-trim"):
                    trimmed += 1
    if write:
        for k, p in files.items():
            if texts[k] != p.read_text(encoding="utf-8"):
                p.write_text(texts[k], encoding="utf-8")
    print(f"# Feature 305 sweep ({'written' if write else 'dry run'})\n")
    print(f"- tags changed: {retagged}; limits restored: {restored}; re-trimmed: {trimmed}; refused: {len(refused)}\n")
    print("\n".join(f"- {x}" for x in refused) or "- nothing refused")
    return 0


if __name__ == "__main__":
    sys.exit(main())
