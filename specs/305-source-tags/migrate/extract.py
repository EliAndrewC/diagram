#!/usr/bin/env python3
"""Feature 305, one-time: write the registry's non-canon entries as classification batches (plan D10, research R3).

    python3 specs/305-source-tags/migrate/extract.py OUT_DIR [--size 100]

Each batch is `batch-NN.jsonl`, one entry per line: its file, key, citation line (comments dropped), the host of its
first URL (a hint only - research R2), and its three write-ups as they stand. Canon entries (the citation line names
`l7r.md` or `budgets.md`) are left out: they carry no tags (FR-004).
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

REGISTRY = pathlib.Path(".claude/skills/diagram/research/sources/010-works-cited")
CANON = re.compile(r"\bl7r\.md\b|\bbudgets\.md\b")


def labeled(body: str, label: str) -> str:
    m = re.search(r"<p><em>" + re.escape(label) + r"</em>\s*(.*?)</p>", body, re.S)
    return m.group(1).strip() if m else ""


def entry(path: pathlib.Path) -> dict[str, str] | None:
    text = path.read_text(encoding="utf-8")
    key = re.search(r'<h3 id="([^"]+)"', text).group(1)  # type: ignore[union-attr]
    first = re.search(r"</h3>\s*<p>(.*?)</p>", text, re.S)
    raw = first.group(1) if first else ""
    if CANON.search(raw):
        return None
    cite = re.sub(r"\s+", " ", re.sub(r"<!--.*?-->", "", raw, flags=re.S)).strip()
    url = (re.findall(r"https?://[^\s<>\")]+", cite) or [""])[0]
    host = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
    return {"file": path.name, "key": key, "cite": cite, "host": host, "what": labeled(text, "What it is:"), "why": labeled(text, "Why it applies, and its limits:"), "used": labeled(text, "Used for:")}


def main() -> int:
    out = pathlib.Path(sys.argv[1])
    size = int(sys.argv[sys.argv.index("--size") + 1]) if "--size" in sys.argv else 100
    out.mkdir(parents=True, exist_ok=True)
    rows = [e for e in (entry(p) for p in sorted(REGISTRY.glob("*.html"))) if e is not None]
    for n in range(0, len(rows), size):
        (out / f"batch-{n // size + 1:02d}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows[n : n + size]), encoding="utf-8")
    print(f"{len(rows)} entries in {(len(rows) + size - 1) // size} batches under {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
