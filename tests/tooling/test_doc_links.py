"""Every relative Markdown link in a live document resolves (feature 329).

Feature 329 moved the project to the repository root and moved or retired documents beside it; the link check it ran
found 29 links already broken before the move - pool notes still pointing at `../../hamletgen/` from before feature 119,
a sibling's notes linked as if in the same folder, tools long retired. Nothing held them, so nothing noticed. This
does, over every tracked `.md` outside the verbatim records (`specs/`, `scripts/fixtures/`, `dev/*-log/`).
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
_RECORD = re.compile(r"^(specs/|scripts/fixtures/|dev/[a-z]+-log/)")


def broken_links(root: Path, files: list[str]) -> list[str]:
    """`file: target` for each relative link in `files` (repo-relative) that names nothing on disk."""
    out = []
    for f in files:
        text = (root / f).read_text(encoding="utf-8")
        for href in _LINK.findall(text):
            if href.startswith(("http:", "https:", "mailto:", "/")):
                continue
            if not (root / os.path.dirname(f) / href).exists():
                out.append(f"{f}: {href}")
    return out


@pytest.mark.tooling
def test_every_relative_link_in_a_live_document_resolves() -> None:
    tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.md"], capture_output=True, text=True, check=True).stdout.split()
    live = [f for f in tracked if not _RECORD.match(f) and (ROOT / f).is_file()]
    bad = broken_links(ROOT, live)
    assert not bad, "links that name nothing (fix the target, or drop the link and keep the words):\n" + "\n".join(bad[:40])


def test_the_check_fires_on_a_broken_link_and_spares_a_good_one(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text("[ok](b.md) [up](../top.md#x) [web](https://example.org) [gone](../nowhere.md)\n")
    (tmp_path / "docs" / "b.md").write_text("b\n")
    (tmp_path / "top.md").write_text("t\n")
    assert broken_links(tmp_path, ["docs/a.md"]) == ["docs/a.md: ../nowhere.md"]
