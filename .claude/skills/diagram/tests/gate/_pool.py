"""THE GATE READS THE POOL'S MAPS (feature 215, GM 2026-09-08).

The reference and Kuwabata are shipped maps: the pool sweep rolls each in a coverage child when its cache key
moved and serves it from the gen cache otherwise, and its manifest is on disk. Until this feature the gate rolled
both AGAIN under specs of their own - the audit (specs/215 research R1) found those rolls reached no engine line
the sweep's children do not. So every gate reader of those two specs comes here: `rolled_map(spec)` is the plan
and the manifest, `rolled_report(spec)` the Report the ratchet judges - both read back from the pool's map, whose
meta carries the roll's own verdict since D3. Any other spec goes to the roll cache as before, so the callers
need not know which kind they hold.

ONE OBTAIN AT A TIME PER GEN: fifteen gate modules ask for the reference at t=0 in six workers, and a cold
`gate_obtain` regenerates on a MISS - six workers arriving together would regenerate six times (the census would
fail the gate: a pool gen rolled more than once). The first-wave lock of the roll cache serializes them; the
second worker's obtain is a HIT on the entry the first published.
"""

from __future__ import annotations

import json
import os
from typing import Any

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import gencache, rollcache

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POOL: dict[tuple[str, int], str] = {
    ("Inashiro", 4): "pool/hamlets/inashiro/inashiro.gen.py",
    ("Kuwabata", 21): "pool/hamlets/kuwabata/kuwabata.gen.py",
}


def gen_of(spec: hg.HamletSpec) -> str | None:
    """The shipped generator of `spec`, or None for a spec the pool does not carry."""
    rel = POOL.get((spec.name, spec.seed))
    return os.path.join(HERE, rel) if rel else None


def obtain(gen: str) -> str:
    """The pool map's manifest path, through the gen cache under the run's per-gen lock."""
    with rollcache._share_lock(rollcache._run_share_path(("pool", gen))):
        manifest, _how, _cpu = gencache.gate_obtain(gen)
    return manifest


def rolled_map(spec: hg.HamletSpec) -> tuple[Any, dict[str, Any]]:
    """`(plan, manifest)` of `spec` - the pool's map for a shipped spec, the roll cache's for any other."""
    gen = gen_of(spec)
    if gen is None:
        return rollcache.hamlet(spec)
    with open(obtain(gen), encoding="utf-8") as fh:
        M: dict[str, Any] = json.load(fh)
    plan = hg.plan_site(spec)
    meta = M.get("meta") or {}
    plan.placed = int(meta.get("roll_placed", len(M.get("houses", []))))
    plan.acres = float(meta.get("roll_acres", 0.0))
    return plan, M


def rolled_report(spec: hg.HamletSpec) -> hg.Report:
    """The Report of `spec`'s roll - read back from the pool map's meta for a shipped spec (D3)."""
    if gen_of(spec) is None:
        return rollcache.report(spec)[0]
    plan, M = rolled_map(spec)
    meta = M.get("meta") or {}
    return hg.Report(plan=plan, failures=list(meta.get("roll_failures", [])), attempt=int(meta.get("roll_attempt", 1)), rerolled_after=list(meta.get("roll_after", [])), manifest=M)
