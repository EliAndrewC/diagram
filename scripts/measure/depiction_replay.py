#!/usr/bin/env python3
"""Replay every edit to an existing pop-up through the depiction re-owe rule, old against new - feature 375 amendment 6, SC-021.

    python3 scripts/measure/depiction_replay.py [--since 2026-10-05] [--until <commit>] [--record <measurements.json> --key <key>]

An EDIT is one pop-up file (`.md` under the modals directory) changed by one non-merge commit (every clone's, as merged into main),
present before and after. Under amendment 1 (FR-015) an edit owed `modal-depiction` when the Depiction tab or `Drawing:`, the
About or the `Entry:` changed; under amendment 6 (FR-028) About is not among them (`modal_owed.depiction_owed_by`). The replay
counts the edits each rule owes and the ABOUT-ONLY edits - owed under the old rule and not the new: what the amendment saves,
one Opus `modal-depiction` round each.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "record"))  # the moved scripts it imports (scripts/CLAUDE.md)
import modal_owed as mo  # noqa: E402


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=False).stdout


def old_rule(was: mo.Modal, m: mo.Modal) -> bool:
    """Amendment 1's rule (FR-015), as `modal_owed.owed` held it until amendment 6."""
    return mo.depiction_owed_by(was, m) or was.tags.get("About", "") != m.tags.get("About", "")


def edits(since: str, until: str) -> list[tuple[str, str, mo.Modal, mo.Modal]]:
    """(commit, file, before, after) for every pop-up file a non-merge commit changed, present on both sides."""
    out = []
    for c in _git("log", "--no-merges", f"--since={since}", "--format=%H", until, "--", mo.MODALS).split():
        for f in _git("diff-tree", "--no-commit-id", "-r", "--name-only", f"{c}^", c, "--", mo.MODALS).split():
            if not f.endswith(".md"):
                continue
            before, after = _git("show", f"{c}^:{f}"), _git("show", f"{c}:{f}")
            was, m = mo.choice_modal(f, before, about_only=False), mo.choice_modal(f, after, about_only=False)
            if was is not None and m is not None and was.tags != m.tags:
                out.append((c, f, was, m))
    return out


def replay(rows: list[tuple[str, str, mo.Modal, mo.Modal]]) -> dict[str, object]:
    old = [r for r in rows if old_rule(r[2], r[3])]
    new = [r for r in rows if mo.depiction_owed_by(r[2], r[3])]
    about_only = [r for r in old if not mo.depiction_owed_by(r[2], r[3])]
    return {
        "edits to existing pop-ups": len(rows),
        "owed modal-depiction, amendment 1": len(old),
        "owed modal-depiction, amendment 6": len(new),
        "About-only edits (owed before, not now)": len(about_only),
        "owed now among the About-only edits": sum(1 for r in about_only if mo.depiction_owed_by(r[2], r[3])),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--since", default="2026-10-05")
    ap.add_argument("--until", default="HEAD")
    ap.add_argument("--record", default="")
    ap.add_argument("--key", default="")
    a = ap.parse_args(argv)
    s = {"since": a.since, "until": _git("rev-parse", "--short", a.until).strip(), **replay(edits(a.since, a.until))}
    if a.record:
        if not a.key:
            print("depiction_replay: --record needs --key", file=sys.stderr)
            return 2
        path = pathlib.Path(a.record)
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault(a.key, {})["value"] = s
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(s, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
