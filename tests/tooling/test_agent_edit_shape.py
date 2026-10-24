"""Every check agent that may send an EDIT names the one shape `make apply-edits` reads (feature 412 round 5: source-reader
sent `OLD:`/`NEW:` in a code fence, which the script could not apply, because its file never gave the shape)."""

import pathlib

AGENTS = pathlib.Path(__file__).resolve().parents[2] / ".claude" / "agents"


def test_every_agent_that_mentions_an_edit_gives_its_shape() -> None:
    missing = [p.name for p in sorted(AGENTS.glob("*.md")) if "EDIT" in (t := p.read_text()) and not ("<<<" in t and ">>>" in t)]
    assert not missing, f"agent files mention an EDIT but never give the `EDIT path / <<< / === / >>>` shape: {missing}"
