"""Every unit of the hamlet generation's code and of the Mode A procedures carries a research claim (feature 316, FR-002/FR-003).

The GM, 2026-10-02: *"the code that generates a hamlet must have citations for anything that should be research derived"*. The
scope is the import graph from `l7r.diagram.hamletgen` (`claims.scope`), so a module newly imported into hamlet generation comes
into scope with it; the procedures are the magistrate's manor and the country shrine and the building vocabulary they are drawn
with. A unit with no claim of its own takes its module docstring's. The fixture forms of every failure are in
`tests/tools/test_claims.py`; this is the real tree, here in `tests/tooling/` because it reads every in-scope file (~4 s).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from l7r.diagram.tools import claims as cl

pytestmark = pytest.mark.tooling

SKILL = Path(__file__).resolve().parents[2]


def test_every_unit_in_scope_carries_a_claim() -> None:
    questions = {p.name for p in (SKILL / "research" / "questions").glob("*.html")}
    problems = cl.coverage(cl.all_units(SKILL), questions)
    shown = "\n".join(problems[:60]) + (f"\n... and {len(problems) - 60} more" if len(problems) > 60 else "")
    assert not problems, f"{len(problems)} claim problem(s):\n{shown}\n\nThe form: {cl.GRAMMAR}"


def test_the_scope_reaches_the_shared_modules_the_gm_named() -> None:
    mods = cl.scope(SKILL)
    for name in ("l7r.diagram.hamletgen.driver", "l7r.diagram.settlement.fields.grain", "l7r.diagram.settlement.fields.comb", "l7r.diagram.settlement.homestead_parts.grove_sides"):
        assert name in mods
    assert "l7r.diagram.tools.claims" not in mods
