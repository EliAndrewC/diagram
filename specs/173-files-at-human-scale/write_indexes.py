#!/usr/bin/env python3
"""Write each new package's CLAUDE.md from feature 173's cut table.

The "look here when" line for every module is the one written in cuts.py when the cut was CHOSEN -
so the index cannot drift from the reasoning that produced it, and the line counts are read off the
files that actually landed rather than typed in.
"""

from __future__ import annotations

import os
import sys

import cuts

SKILL = "/diagram/.clones/diagram-tooling/.claude/skills/diagram"

BLURB = {
    "module": "Its modules are LAYERS, emitted bottom-up: every cross-module reference points backwards, so the package cannot have an import cycle. Read the last row first if you want the entry point.",
    "names": "Its modules are LAYERS, emitted bottom-up: every cross-module reference points backwards, so the package cannot have an import cycle. **The monolith's source order was not its dependency order** - the stage entry points stood at the top and the primitives they call stood below - which is why the cut is by subject rather than by line range.",
    "mixin": "`{cls}` exists ONLY to preserve the single import and the position in the `class Settlement(...)` base list - the split is meant to be invisible above this line. Sub-mixin methods reach each other through `self.` on the composed Settlement, so a cross-submodule call needs no import and the partition can be re-cut later without touching core.py.",
}


def rows(plan: dict) -> list[tuple[str, str]]:
    if plan["kind"] == "names":
        return [(m, look) for m, _, look in plan["modules"]]
    return [(m, look) for _, m, look in plan["cuts"]]


def main() -> int:
    for rel, plan in sorted(cuts.PLANS.items()):
        pkg = os.path.join(SKILL, rel[:-3])
        if not os.path.isdir(pkg):
            print(f"skip (not split yet): {rel}")
            continue
        name = os.path.basename(pkg)
        was = plan["was"]
        body = rows(plan)
        if plan["kind"] == "mixin":
            body = [(plan.get("helpers", "_helpers"), plan["helpers_look"])] + body
        lines = [
            f"# `{name}/` - {plan['title']}",
            "",
            f"Split from the {was:,}-line `{name}.py` by feature 173 (constitution Principle X clause 13 - "
            "the cost being managed is context-window tokens, and the bar is now GATED by "
            "`scripts/check-file-scale.py`). **Load only the file the task calls for**; this index is the map.",
            "",
            BLURB[plan["kind"]].format(cls=plan.get("class", "")),
            "",
            "## Look here when",
            "",
            "| file | look here when |",
            "|---|---|",
        ]
        for mod, look in body:
            path = os.path.join(pkg, mod + ".py")
            n = sum(1 for _ in open(path)) if os.path.exists(path) else 0
            lines.append(f"| `{mod}.py` ({n}) | {look} |")
        lines += [
            f"| `__init__.py` | the composed surface only - {'the class this package exists to provide, plus the module-level helpers the tests import by name' if plan['kind'] == 'mixin' else 'the re-exports that keep every existing importer working'}. Never add logic here |",
            "",
        ]
        with open(os.path.join(pkg, "CLAUDE.md"), "w") as fh:
            fh.write("\n".join(lines))
        print(f"wrote {rel[:-3]}/CLAUDE.md ({len(body)} modules)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
