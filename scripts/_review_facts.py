#!/usr/bin/env python3
"""The standard measurements of a settlement review, in one call (feature 255, FR-005).

WHY. `settlement-review` is the most expensive check per run, and feature 251's R9 found where it goes: a median 43
turns, 39 of them Bash calls, the commonest a few lines of inline Python asking the manifest the same opening
questions every pass - what is on this map and how many, what changed against main, what the labels say, what the
notes call settled, whether the renders exist and are fresh. Each answer costs a turn that re-reads the whole
context. This prints them together, once, for no tokens; the session puts the output in the review's prompt. What
is left to the agent is the looking and the judging, which is its whole job (feature 193's ruling: measure, never
adjudicate).

WHAT IT PRINTS, for `pool/<tier>/<map>` (a folder, or the path without its extension):
  FILES       each artifact - render, picture, manifest, page, generator, notes - present or MISSING, size, age
  MANIFEST    `meta`, then every top-level key with its count
  DELTA       against a git ref (default HEAD) or a review snapshot's `main/` side: per key, the count before and
              after and whether its content moved - "what changed" without a diff of 300 kB of JSON
  LABELS      every `<text>` on the render, with its count
  NOTES       the notes file's headings, then its "Settled by the GM" section verbatim
It judges nothing and never edits.
"""

from __future__ import annotations

import argparse
import collections
import html
import json
import pathlib
import re
import subprocess
import sys
import time

ARTIFACTS = (("render", ".svg"), ("picture", ".png"), ("manifest", ".json"), ("page", ".html"), ("generator", ".gen.py"), ("notes", ".notes.md"))


def locate(subject: str) -> tuple[pathlib.Path, str]:
    """`pool/hamlets/kuwabata` (a folder, or a stem beside its files) -> (folder, map name)."""
    path = pathlib.Path(subject)
    if path.is_dir():
        return path, path.name
    return path.parent, path.name


def files(folder: pathlib.Path, name: str, now: float) -> list[str]:
    lines = []
    for label, ext in ARTIFACTS:
        path = folder / f"{name}{ext}"
        if path.is_file():
            stat = path.stat()
            lines.append(f"  {label:10s} {path.name:28s} {stat.st_size:>10,} bytes  {(now - stat.st_mtime) / 3600:8.1f} h old")
        else:
            lines.append(f"  {label:10s} {path.name:28s} MISSING")
    return lines


def count(value: object) -> str:
    return str(len(value)) if isinstance(value, (list, dict, str)) else repr(value)


def inventory(manifest: dict) -> list[str]:
    meta = manifest.get("meta", {})
    lines = ["  meta: " + ", ".join(f"{k}={meta[k]!r}" for k in sorted(meta) if not isinstance(meta[k], (list, dict)))]
    lines += [f"  {key:32s} {count(manifest[key]):>8s}" for key in sorted(manifest) if key != "meta"]
    return lines


def delta(before: dict, after: dict) -> list[str]:
    lines = []
    for key in sorted(set(before) | set(after)):
        if key not in before:
            lines.append(f"  {key:32s} NEW          -> {count(after[key])}")
        elif key not in after:
            lines.append(f"  {key:32s} {count(before[key]):>8s} -> GONE")
        elif before[key] != after[key]:
            lines.append(f"  {key:32s} {count(before[key]):>8s} -> {count(after[key]):<8s} content moved")
    return lines or ["  nothing moved: the two manifests are equal"]


def labels(svg: str) -> list[str]:
    found = collections.Counter(html.unescape(re.sub(r"<[^>]+>", "", m)).strip() for m in re.findall(r"<text\b[^>]*>(.*?)</text>", svg, re.S))
    found.pop("", None)
    return [f"  {n:>3d} x {text}" for text, n in sorted(found.items(), key=lambda kv: (-kv[1], kv[0]))] or ["  none"]


def notes(text: str) -> list[str]:
    lines = ["  " + line for line in text.splitlines() if re.match(r"#{1,4} ", line)]
    settled = re.search(r"(?ms)^(#{1,4}) [^\n]*Settled by the GM[^\n]*\n(.*?)(?=^#{1,4} |\Z)", text)
    lines.append("  -- Settled by the GM (verbatim; do not re-raise what is here):" if settled else "  -- no 'Settled by the GM' section")
    if settled:
        lines += ["  " + line for line in settled.group(2).strip().splitlines()]
    return lines


def at_ref(folder: pathlib.Path, name: str, ref: str, run=subprocess.run) -> dict | None:  # noqa: ANN001
    """The manifest as `ref` holds it, or None when that ref has none (a new map, or no repository)."""
    top = run(["git", "-C", str(folder), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if top.returncode:
        return None
    rel = (folder / f"{name}.json").resolve().relative_to(pathlib.Path(top.stdout.strip()).resolve())
    shown = run(["git", "-C", str(folder), "show", f"{ref}:{rel.as_posix()}"], capture_output=True, text=True)
    return json.loads(shown.stdout) if shown.returncode == 0 else None


def report(subject: str, against: str, snapshot: str, now: float, run=subprocess.run) -> str:  # noqa: ANN001
    folder, name = locate(subject)
    out = [f"review-facts: {name} ({folder}) - measurements only; nothing here is a verdict", "FILES"] + files(folder, name, now)
    manifest_path = folder / f"{name}.json"
    if not manifest_path.is_file():
        return "\n".join(out + ["MANIFEST", "  MISSING - no manifest, so no inventory and no delta"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    out += ["MANIFEST"] + inventory(manifest)
    main_side = pathlib.Path(snapshot) / "main" / f"{name}.json" if snapshot else None
    if main_side is not None and main_side.is_file():
        out += [f"DELTA against the snapshot's main side ({main_side})"] + delta(json.loads(main_side.read_text(encoding="utf-8")), manifest)
    else:
        before = at_ref(folder, name, against, run)
        out += [f"DELTA against {against}"] + (delta(before, manifest) if before is not None else [f"  no manifest at {against} - a new map, or not a repository"])
    svg = folder / f"{name}.svg"
    out += ["LABELS"] + (labels(svg.read_text(encoding="utf-8")) if svg.is_file() else ["  render MISSING"])
    notes_path = folder / f"{name}.notes.md"
    out += ["NOTES"] + (notes(notes_path.read_text(encoding="utf-8")) if notes_path.is_file() else ["  MISSING - itself a finding: every pool subject has a notes file"])
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("map", help="a pool map: pool/hamlets/kuwabata (the folder) or pool/hamlets/kuwabata/kuwabata")
    ap.add_argument("--against", default="HEAD", help="the git ref the manifest is compared with (default HEAD)")
    ap.add_argument("--snapshot", default="", help="a review snapshot folder for this map, holding main/ and clone/")
    args = ap.parse_args(argv)
    folder, name = locate(args.map)
    if not folder.is_dir():
        print(f"review-facts: no such map folder - wanted {folder}", file=sys.stderr)
        return 2
    print(report(args.map, args.against, args.snapshot, time.time()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
