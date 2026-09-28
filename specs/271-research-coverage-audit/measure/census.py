#!/usr/bin/env python3
"""Feature 271 FR-001: the mechanical first pass of the research audit.

Three lists, written as JSON beside this script:
- `kinds.json`: every feature category and sub-kind drawn on any map (the scripted pool, the legacy hand-drawn pool,
  wip/), per tier, with the maps it appears on - a manifest's top-level keys and the `kind`/`type`/`use`/`role`
  values of its items;
- `modals.json`: every modal class (map and sheet) with its label and the research entries it names;
- `questions.json`: every research question with its footnote count, absence-note count and size - a question
  with no quoted evidence is THIN.
"""
from __future__ import annotations

import collections
import importlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parents[2] / ".claude/skills/diagram"
sys.path.insert(0, str(SKILL))


def manifests():
    for base in ("pool", "legacy-hand-authored-pool", "wip"):
        for p in sorted((SKILL / base).rglob("*.json")):
            if "regressions" in p.parts or p.name.endswith((".notes.json", ".timings.json")):
                continue
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if isinstance(d, dict) and len(d) > 3:
                tier = p.parts[len(SKILL.parts) + 1] if base != "wip" else "wip"
                yield base, tier, p.stem, d


def kinds():
    out = collections.defaultdict(lambda: {"maps": set(), "subkinds": collections.Counter()})
    for base, tier, name, d in manifests():
        for key, val in d.items():
            row = out[f"{tier}:{key}"]
            row["maps"].add(f"{base}/{name}")
            items = val if isinstance(val, list) else [val] if isinstance(val, dict) else []
            for it in items:
                if isinstance(it, dict):
                    for f in ("kind", "type", "use", "role", "cls", "program"):
                        v = it.get(f)
                        if isinstance(v, str) and len(v) < 40:
                            row["subkinds"][f"{f}={v}"] += 1
    return {k: {"maps": sorted(v["maps"]), "subkinds": dict(v["subkinds"].most_common(40))} for k, v in sorted(out.items())}


def modals():
    rows = []
    for mod, reg in (("l7r.diagram.interactive.classes", "CLASSES"), ("l7r.diagram.interactive.compound_kinds", "COMPOUND_CLASSES")):
        for key, fc in getattr(importlib.import_module(mod), reg).items():
            rows.append({"registry": reg, "key": key, "label": getattr(fc, "label", ""), "entry": getattr(fc, "entry", "")})
    return rows


def questions():
    rows = []
    rec = SKILL / "research"
    for q in sorted(rec.rglob("[0-9][0-9][0-9]-*.html")):
        if q.name.endswith(".notes.html") or "sources" in q.parts or "citations" in q.parts:
            continue
        n = q.with_name(q.name[:-5] + ".notes.html")
        body = q.read_text(encoding="utf-8")
        notes = n.read_text(encoding="utf-8") if n.exists() else ""
        heading = re.search(r"<h2[^>]*>(.*?)</h2>", body, re.S)
        cites = len(re.findall(r'<li data-note="[^"]+"><a href', notes))
        absent = len(re.findall(r"no publicly readable source|no source is owed", notes))
        rows.append({"page": str(q.parent.relative_to(rec)), "q": q.name[:3],
                     "heading": re.sub(r"<[^>]+>", "", heading.group(1)).strip() if heading else q.stem,
                     "bytes": len(body) + len(notes), "cited_notes": cites, "absence_notes": absent,
                     "status": "THIN" if cites == 0 else ("THIN" if cites <= 1 and len(body) > 4000 else "HAS-EVIDENCE")})
    return rows


if __name__ == "__main__":
    (HERE / "kinds.json").write_text(json.dumps(kinds(), indent=1, ensure_ascii=False), encoding="utf-8")
    (HERE / "modals.json").write_text(json.dumps(modals(), indent=1, ensure_ascii=False), encoding="utf-8")
    qs = questions()
    (HERE / "questions.json").write_text(json.dumps(qs, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"kinds {len(json.load(open(HERE / 'kinds.json')))}, modals {len(modals())}, questions {len(qs)}, "
          f"THIN {sum(r['status'] == 'THIN' for r in qs)}")
