#!/usr/bin/env python3
"""Feature 329's one-shot pointer sweep (plan D5). Run ONCE, from the repository root, after the `git mv`.

Rewrites every LIVE tracked text file:
  1. `<x>/.claude/skills/diagram/...` -> `<x>/...`, and a closing `<x>/.claude/skills/diagram` -> `<x>`;
  2. a token-initial `.claude/skills/diagram/...` -> `...`;
  3. in a file that MOVED, a relative path that climbed out of the old skill directory (`../../../../docs/x` from
     `dev/`) is recomputed from the new place; one that stays inside never changes;
  4. in a moved `.py`, `Path(__file__).resolve().parents[k]` that climbed past the old skill root drops by three.
Everything it cannot judge (a bare `.claude/skills/diagram`, a `"skills" / "diagram"` Path form, `.parents[2]` off a
root constant) is LISTED for a hand edit, never guessed. Every rewrite of kinds 3 and 4 is logged for review.

Not live, never touched (FR-004's verbatim records): specs/, scripts/fixtures/, dev/*-log/, docs/review-ledger.md.

    python3 specs/329-unskill-the-repo/sweep.py <moved-list> <log>
<moved-list> is the post-move paths of the files the `git mv` moved, one per line.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import PurePosixPath

OLD = ".claude/skills/" + "diagram"
EXEMPT = (re.compile(r"^specs/"), re.compile(r"^scripts/fixtures/"), re.compile(r"^dev/[a-z]+-log/"),
          re.compile(r"^docs/review-ledger\.md$"))

R_INNER = re.compile(r"(?<=[^\s\"'`(\[=:,])/" + re.escape(OLD) + r"/")
R_CLOSE = re.compile(r"(?<=[^\s\"'`(\[=:,])/" + re.escape(OLD) + r"(?![\w/.-])")
R_HEAD = re.compile(r"(?<![\w./-])" + re.escape(OLD) + r"/")
R_UP = re.compile(r"(?<![\w./-])((?:\.\./)+)([\w@.{}$-][^\s\"'`)\]>|;,]*)?")
R_UP_BARE = re.compile(r"(?<![\w./-])((?:\.\./)*\.\.)(?![\w./-])")
R_PARENTS = re.compile(r"(Path\(__file__\)\.resolve\(\)\.parents\[)(\d+)(\])")


def live(path: str) -> bool:
    return not any(r.search(path) for r in EXEMPT)


def climb(rel_dir: str, ups: int, rest: str) -> str | None:
    """The new relative form of `ups` climbs + `rest` written in old `.claude/skills/diagram/<rel_dir>`, or None
    when it stays inside the old skill directory (unchanged by the move)."""
    depth = 0 if rel_dir in ("", ".") else len(PurePosixPath(rel_dir).parts)
    if ups <= depth:
        return None
    old_dir = PurePosixPath(OLD) / rel_dir
    target = os.path.normpath(os.path.join(str(old_dir), "../" * ups + rest))
    if target.startswith(OLD + "/") or target == OLD:
        target = target[len(OLD) + 1:] or "."
    new = os.path.relpath(target, rel_dir or ".")
    return new


def main() -> int:
    moved = set(open(sys.argv[1]).read().splitlines())
    log = open(sys.argv[2], "w")
    files = subprocess.run(["git", "ls-files", "-z"], capture_output=True, text=True, check=True).stdout.split("\0")
    leftovers: list[str] = []
    for f in filter(None, files):
        if not live(f) or not os.path.isfile(f):
            continue
        try:
            text = open(f, encoding="utf-8").read()
        except (UnicodeDecodeError, IsADirectoryError):
            continue
        new = R_INNER.sub("/", text)
        new = R_CLOSE.sub("", new)
        new = R_HEAD.sub("", new)
        if f in moved:
            rel_dir = str(PurePosixPath(f).parent)
            rel_dir = "" if rel_dir == "." else rel_dir

            def up(m: re.Match[str]) -> str:
                ups = m.group(1).count("../")
                rest = m.group(2) or ""
                out = climb(rel_dir, ups, rest)
                if out is None:
                    return m.group(0)
                out = out + ("/" if rest == "" else "")
                log.write(f"UP {f}: {m.group(0)} -> {out}\n")
                return out

            def up_bare(m: re.Match[str]) -> str:
                ups = m.group(1).count("..")
                out = climb(rel_dir, ups, "")
                if out is None:
                    return m.group(0)
                log.write(f"UPBARE {f}: {m.group(0)} -> {out}\n")
                return out

            new = R_UP.sub(up, new)
            new = R_UP_BARE.sub(up_bare, new)
            if f.endswith(".py"):
                depth = len(PurePosixPath(f).parent.parts) if rel_dir else 0

                def par(m: re.Match[str]) -> str:
                    k = int(m.group(2))
                    if k <= depth:
                        return m.group(0)
                    log.write(f"PARENTS {f}: parents[{k}] -> parents[{k - 3}]\n")
                    return f"{m.group(1)}{k - 3}{m.group(3)}"

                new = R_PARENTS.sub(par, new)
        if new != text:
            open(f, "w", encoding="utf-8").write(new)
        for n, line in enumerate(new.splitlines(), 1):
            if OLD in line or '"skills" / "diagram"' in line or re.search(r"\.parents\[2\]", line):
                leftovers.append(f"{f}:{n}: {line.strip()[:160]}")
    for line in leftovers:
        log.write(f"HAND {line}\n")
    print(f"sweep: {len(leftovers)} lines for a hand edit; log {sys.argv[2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
