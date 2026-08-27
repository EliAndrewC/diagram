#!/usr/bin/env python3
"""Replay the captured regression corpus (pool/regressions/*.json).

The third leg of the Mode B testing discipline (see settlements.md "Three testing disciplines"):

  - tests/test_villages.py    - the GOOD maps still PASS the whole gate (integration).
  - tests/check_village/      - each check still FIRES on a minimal synthetic break (unit).
  - tests/test_regressions.py (this) - the actual BAD manifests we hit while iterating a map stay
                        caught: every fixture lists the checks it MUST trip, and we assert they
                        still do. A permanent, growing guard - drop the manifest of any map that
                        slips past a check (or that a newly-tightened check should have caught)
                        into pool/regressions/ with a `_regression` block and it is pinned forever.

Each fixture is a normal manifest plus a top-level `_regression` block:
    "_regression": {"fires": ["check_name", ...], "source": "where it came from"}
We pop that block and assert the gate still trips every name in `fires`.

TARGETED since feature 022 (specs/022-gate-check-registry/): the replay runs
`gate(M, only=<fires' base names>)`, which executes just those checks plus the shared derivations
they depend on - a 210-strong cohort of frozen whole-city fixtures used to pay a full 189-check
gate apiece (~61% of suite CPU) to verify one check each. Verdict identity between targeted and
full runs is held by the 022 oracle sweeps and by
`test_feature_022_targeted_verdict_matches_the_full_gate` (in tests/check_village/); a fixture naming a
META check (whole-run state, e.g. waivers_are_live) falls back to the full gate.

Regenerate the backfilled corpus from the in-test fixtures with `python3 -m l7r.diagram.tools.make_regressions`;
hand-dropped real-map captures are replayed identically and survive regeneration if named
distinctly from the auto-captured ones.

    python3 -m pytest test_regressions.py -q
    python3 test_regressions.py
"""

import glob
import json
import os

import pytest

from l7r.diagram import check_village
from tests._scope import EXHAUSTIVE

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the skill root; this file lives two levels down in tests/gate/
CORPUS = sorted(glob.glob(os.path.join(HERE, "pool", "regressions", "*.json")))


def _fixture_tier(path):
    """The fixture's own settlement tier, read cheaply from the head of the file (meta is the first
    key of every manifest), so the corpus participates in `--tier` (GM 2026-08-26, T19): a hamlet
    run replays the hamlet and village fixtures, not the 352 city ones."""
    import re

    with open(path) as fh:
        m = re.search(r'"scale":\s*"(hamlet|village|town|city|capital)"', fh.read(4096))
    return m.group(1) if m else None


def _corpus_params():
    out = []
    for p in CORPUS:
        tier = _fixture_tier(p)
        marks = [pytest.mark.tiers(tier)] if tier else []
        out.append(pytest.param(p, marks=marks, id=os.path.basename(p)))
    return out


def _load(path):
    with open(path) as fh:
        M = json.load(fh)
    fires = M.pop("_regression")["fires"]
    return M, fires


def _replay(M, fires):
    """The fixture's verdicts, via the targeted gate (full-gate fallback for meta-checks)."""
    bases = {f.split("[")[0] for f in fires}
    if bases & check_village.META_CHECKS:
        return set(check_village.gate(M, verbose=False))
    return set(check_village.gate(M, verbose=False, only=bases))


def test_corpus_is_not_empty():
    assert CORPUS, "no regression fixtures found in pool/regressions/"


@pytest.mark.skipif(not EXHAUSTIVE, reason="the bad-map corpus replays at the GATE, not in quick (GM 2026-08-26, T22: most fixtures date from hand placement; every one still runs at every make done)")
@pytest.mark.parametrize("path", _corpus_params())
def test_regression_fixture_still_fires(path):
    M, fires = _load(path)
    failed = _replay(M, fires)
    missing = [c for c in fires if c not in failed]
    assert not missing, f"{os.path.basename(path)} no longer trips: {missing}"


if __name__ == "__main__":
    rc = 0
    for p in CORPUS:
        M, fires = _load(p)
        failed = _replay(M, fires)
        missing = [c for c in fires if c not in failed]
        print(("PASS " if not missing else "FAIL ") + os.path.basename(p) + (f"  missing={missing}" if missing else ""))
        rc |= 0 if not missing else 1
    raise SystemExit(rc)
