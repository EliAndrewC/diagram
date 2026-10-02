"""`record/blocked.py` - blocked domains and banned citations (feature 312, FR-001 - FR-004).

WHAT THESE PROVE. A blocked domain matches itself and every subdomain and nothing that merely ends with its letters; a URL
written without its scheme is still matched; an entry with no GM approval, with no reason, or a pattern that does not
compile is refused by the loader, naming its file; a banned pattern matches by regular expression and a blocked domain is
banned too; the refusal names the list, the entry and the reason; and the real list blocks Grokipedia.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from l7r.diagram.interactive.record import blocked

APPROVED = {"date": "2026-10-02", "words": "block it"}


def _lists(tmp_path: pathlib.Path, domains: list[dict] | None = None, patterns: list[dict] | None = None) -> str:
    if domains is not None:
        (tmp_path / blocked.DOMAINS).write_text(json.dumps({"domains": domains}), encoding="utf-8")
    if patterns is not None:
        (tmp_path / blocked.CITATIONS).write_text(json.dumps({"patterns": patterns}), encoding="utf-8")
    blocked.domains.cache_clear()
    blocked.patterns.cache_clear()
    return str(tmp_path)


@pytest.mark.parametrize(
    ("url", "hit"),
    [
        ("https://ai-wiki.example/page/X", True),
        ("http://www.ai-wiki.example/page/X", True),
        ("ai-wiki.example/page", True),
        ("https://AI-WIKI.example./x", True),
        ("https://notai-wiki.example/x", False),
        ("https://ai-wiki.example.org/x", False),
        ("https://other.example/ai-wiki.example", False),
    ],
)
def test_a_domain_blocks_itself_and_its_subdomains_only(tmp_path: pathlib.Path, url: str, hit: bool) -> None:
    rd = _lists(tmp_path, [{"domain": "ai-wiki.example", "reason": "AI-generated", "approved": APPROVED}])
    assert (blocked.blocked(url, rd) is not None) is hit


def test_missing_lists_block_nothing(tmp_path: pathlib.Path) -> None:
    rd = _lists(tmp_path)
    assert blocked.blocked("https://anything.example", rd) is None
    assert blocked.banned("https://anything.example", rd) is None


@pytest.mark.parametrize(
    ("entry", "says"),
    [
        ({"domain": "x.example", "reason": "why"}, "carries no approval"),
        ({"domain": "x.example", "reason": "why", "approved": {"date": "2026-10-02"}}, "carries no approval"),
        ({"domain": "x.example", "approved": APPROVED}, "needs its domain and its reason"),
        ("x.example", "needs its domain and its reason"),
    ],
)
def test_the_loader_refuses_an_entry_without_its_approval_or_reason(tmp_path: pathlib.Path, entry: object, says: str) -> None:
    rd = _lists(tmp_path, [entry])  # type: ignore[list-item]
    with pytest.raises(blocked.BlockedListError, match=says) as err:
        blocked.blocked("https://x.example", rd)
    assert blocked.DOMAINS in str(err.value)


def test_a_banned_pattern_bans_the_citation_and_a_blocked_domain_is_banned_too(tmp_path: pathlib.Path) -> None:
    rd = _lists(
        tmp_path,
        [{"domain": "ai-wiki.example", "reason": "AI-generated", "approved": APPROVED}],
        [{"pattern": r"shared\.example/forged/", "reason": "fabricated data", "approved": APPROVED}],
    )
    assert blocked.banned("https://shared.example/forged/paper.pdf", rd).reason == "fabricated data"
    assert blocked.banned("https://shared.example/sound/paper.pdf", rd) is None
    assert blocked.banned("https://ai-wiki.example/x", rd).reason == "AI-generated"
    # banned at the citation, never at the fetch
    assert blocked.blocked("https://shared.example/forged/paper.pdf", rd) is None


def test_a_pattern_that_does_not_compile_is_refused(tmp_path: pathlib.Path) -> None:
    rd = _lists(tmp_path, patterns=[{"pattern": "(", "reason": "x", "approved": APPROVED}])
    with pytest.raises(blocked.BlockedListError, match="does not compile"):
        blocked.banned("https://x.example", rd)


def test_check_raises_with_the_list_the_entry_and_the_reason(tmp_path: pathlib.Path) -> None:
    rd = _lists(tmp_path, [{"domain": "ai-wiki.example", "reason": "AI-generated", "approved": APPROVED}])
    blocked.check("https://ok.example/x", "a fetch", rd)
    with pytest.raises(blocked.Blocked) as err:
        blocked.check("https://ai-wiki.example/x", "a fetch", rd)
    msg = str(err.value)
    assert msg.startswith("a fetch refused: https://ai-wiki.example/x")
    assert all(s in msg for s in (blocked.DOMAINS, "ai-wiki.example", "AI-generated", "2026-10-02: block it"))


def test_the_real_list_blocks_grokipedia_with_the_gms_approval() -> None:
    blocked.domains.cache_clear()
    rule = blocked.blocked("https://grokipedia.com/page/Kaifeng")
    assert rule is not None and "Grokopedia" in rule.approved
    assert blocked.patterns() == ()


def test_the_build_refuses_a_blocked_or_banned_citation_in_an_entry_or_a_footnote(tmp_path: pathlib.Path) -> None:
    """FR-003, FR-004 at the build: an entry's URL on a blocked domain, and a footnote's link matching a banned pattern."""
    from l7r.diagram.interactive.record import site  # noqa: PLC0415
    from l7r.diagram.interactive.record.store import RecordError  # noqa: PLC0415
    from tests import _flat_record as fr  # noqa: PLC0415

    rec = fr.write(tmp_path)
    assert blocked.refusals(str(rec)) == []
    _lists(
        rec,
        [{"domain": "a", "reason": "AI-generated", "approved": APPROVED}],
        [{"pattern": r"^https://b$", "reason": "fabricated data", "approved": APPROVED}],
    )
    got = blocked.refusals(str(rec))
    assert any(r.startswith("banned citation: https://a (alpha, 0001-lanes.notes.html) is on blocked-domains.json (a - AI-generated)") for r in got)
    assert any("https://b (beta) is on banned-citations.json" in r for r in got)
    with pytest.raises(RecordError, match="banned citation: https://a"):
        site.build(str(rec))
    blocked.domains.cache_clear()
    blocked.patterns.cache_clear()
