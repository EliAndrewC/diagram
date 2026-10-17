"""Every phrase a hook, a gate or a script quotes from a CLAUDE.md is still in that CLAUDE.md (feature 383 amendment 6,
FR-040, plan D44).

CLAUDE.md is kept to an always-on core plus an index (the GM 2026-10-17), its detail moved verbatim into topic docs; a
refusal that sends a session to `CLAUDE.md "Session clones"` must still find that section there. Three such pointers were
already stale when this test was written - two copied from gm-assistant's hooks ("Canonical Source", "Generation Behavior")
and one naming a heading the root no longer had ("Files stay at human scale").
"""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
QUOTE = re.compile(r"""((?:[\w./-]+/)?CLAUDE\.md)`?[,:]?\s*(?:[-(]\s*)?\\?["']([A-Z][^"'\\\n]{3,80}?)\\?["']""")
NESTED = {"research/CLAUDE.md", "tests/CLAUDE.md", "l7r/diagram/CLAUDE.md", "scripts/CLAUDE.md"}


def sources(root: pathlib.Path) -> list[pathlib.Path]:
    globs = ("scripts/**/*.sh", "scripts/**/*.py", "scripts/**/*.txt", ".claude/agents/*.md")
    found = [p for g in globs for p in root.glob(g) if "__pycache__" not in p.parts]
    return sorted({*found, *(p for p in (root / ".claude" / "settings.json", root / "Makefile") if p.is_file())})


def quotes(root: pathlib.Path) -> list[tuple[str, str, str]]:
    """(the quoting file, the CLAUDE.md it names, the phrase) for each quote in the tooling."""
    out = []
    for p in sources(root):
        for m in QUOTE.finditer(p.read_text(encoding="utf-8", errors="replace")):
            name = next((n for n in NESTED if m.group(1).endswith(n)), "CLAUDE.md")
            out.append((str(p.relative_to(root)), name, m.group(2).strip()))
    return out


def unresolved(root: pathlib.Path) -> list[tuple[str, str, str]]:
    return [(src, name, phrase) for src, name, phrase in quotes(root) if phrase.lower() not in (root / name).read_text(encoding="utf-8").lower()]


def test_every_quoted_claude_md_phrase_resolves() -> None:
    assert len(quotes(REPO)) >= 9, "the extractor finds the tooling's quotes"
    bad = unresolved(REPO)
    assert not bad, "a hook or script quotes a CLAUDE.md phrase that file no longer holds - keep the phrase there, or re-aim the quote:\n" + "\n".join(f"  {s}: {n} '{q}'" for s, n, q in bad)


def test_a_quote_whose_phrase_moved_out_is_caught(tmp_path: pathlib.Path) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "x-hooks.sh").write_text('echo "(scripts/x-hooks.sh; CLAUDE.md \\"Session clones\\")"\n', encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("# Project\n\n## Session clones\n", encoding="utf-8")
    assert unresolved(tmp_path) == []
    (tmp_path / "CLAUDE.md").write_text("# Project\n\nThe clones moved to docs/session-clones.md.\n", encoding="utf-8")
    assert unresolved(tmp_path) == [("scripts/x-hooks.sh", "CLAUDE.md", "Session clones")]
