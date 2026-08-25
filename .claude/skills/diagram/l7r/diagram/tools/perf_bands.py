"""The three performance bands (feature 129): what a before/after pair OWES, per environment.

THE GM'S MATRIX (2026-08-24, superseding constitution VI's two-band rule):

    band               on the TOTAL     on ANY SINGLE SEED   what it takes
    1  explain         any increase     any increase         a written explanation + a perf-audit subagent confirming it
    2  audit           > 5%             > 10%                the subagent adjudicates: necessary, commensurate, no way around it
    3  GM sign-off     > 10%            > 20%                the GM personally, BEFORE the push

A band fires when EITHER measurement crosses its line, each rung keeps everything below it, and the
whole matrix applies to each ENVIRONMENT independently (GM 2026-08-25: *"these thresholds apply to
both of those individually"*) - a local pair against local history, a CodeBuild pair against
CodeBuild history, never one against the other: `evaluate` REFUSES a cross-environment pair rather
than printing a percentage that is arithmetically indistinguishable from a regression (FR-014).

THE CASE THE PER-SEED NUMBERS EXIST FOR: feature 128 finished at total -29.9% with seed 47 at +30.7%.
Under a total-only rule it reached nobody; here it is band 3 and needs the GM (SC-002b).

THIS MODULE DECIDES; IT NEVER ENFORCES. `perf_snapshot.report` prints the verdict, `perf-gate`
prints what is owed at the gate (FR-009b), and `perf_review --check` enforces it at the PUSH - the
GM's words are "before it is committed back to main".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# The lines, pinned by tests/tools/test_perf_bands.py so a drift is a deliberate change.
BAND2_TOTAL_PCT = 5.0
BAND2_SEED_PCT = 10.0
BAND3_TOTAL_PCT = 10.0
BAND3_SEED_PCT = 20.0

OWES = {
    0: "nothing - no increase on the total or on any seed",
    1: "a written explanation (make perf-explain WHY=...) AND a perf-audit confirmation (make perf-confirm ... AS=perf-audit)",
    2: "band 1, plus an escalated audit: necessary, commensurate, no way around it (make perf-audit ... AS=perf-audit)",
    3: "bands 1 and 2, plus the GM's personal sign-off before the push (make perf-signoff, at a terminal)",
}


class EnvironmentMismatch(ValueError):
    """A pair from two environments. Refused, never displayed (FR-014)."""


@dataclass(frozen=True)
class Verdict:
    environment: str
    base: dict[str, str]  # label, utc, commit
    cur: dict[str, str]
    total_pct: float
    seeds: dict[int, float]
    stage_delta: dict[int, dict[str, tuple[float, float]]]
    band: int
    crossed: tuple[str, ...] = field(default_factory=tuple)

    @property
    def owes(self) -> str:
        return OWES[self.band]

    @property
    def measurements(self) -> dict[str, Any]:
        """The numbers a review record is bound to (FR-005)."""
        return {"total_pct": self.total_pct, "seeds": {str(k): v for k, v in sorted(self.seeds.items())}}


def environment_of(snap: dict[str, Any]) -> str:
    """Recorded, never inferred (FR-013) - with ONE transitional reading: a snapshot from between
    features 130 and 129 carries `host: codebuild:...` but no `environment` (build a6e2afe6's in-build
    `-end`); that is the field's own value under its older name, not an inference from a CPU count.
    Anything older than both fields was taken on the laptop: local."""
    env = str(snap.get("environment") or "")
    if env:
        return env
    return "codebuild" if str(snap.get("host", "")).startswith("codebuild:") else "local"


def _pct(was: float, now: float) -> float:
    return round((now - was) / was * 100.0, 1) if was else 0.0


def evaluate(base: dict[str, Any], cur: dict[str, Any]) -> Verdict:
    """The band a `cur` snapshot reaches against `base`, both from ONE environment."""
    e_base, e_cur = environment_of(base), environment_of(cur)
    if e_base != e_cur:
        raise EnvironmentMismatch(
            f"{cur.get('label')} is a {e_cur} snapshot and {base.get('label')} is {e_base} - the bands are evaluated per environment, and a cross-environment percentage is indistinguishable from a regression (FR-014)"
        )
    by_seed = {int(r["seed"]): r for r in base["rows"]}
    seeds: dict[int, float] = {}
    stage_delta: dict[int, dict[str, tuple[float, float]]] = {}
    was_total = now_total = 0.0
    for r in cur["rows"]:
        b = by_seed.get(int(r["seed"]))
        if b is None:
            continue
        was, now = float(b["seconds"]), float(r["seconds"])
        was_total, now_total = was_total + was, now_total + now
        seeds[int(r["seed"])] = _pct(was, now)
        bs, cs = dict(b.get("stages") or {}), dict(r.get("stages") or {})
        stage_delta[int(r["seed"])] = {k: (float(bs.get(k, 0.0)), float(cs.get(k, 0.0))) for k in sorted(set(bs) | set(cs))}
    total_pct = _pct(was_total, now_total)
    crossed: list[str] = []
    band = 0
    if total_pct > 0 or any(p > 0 for p in seeds.values()):
        band = 1
    if total_pct > BAND2_TOTAL_PCT:
        crossed.append(f"total {total_pct:+.1f}% > {BAND2_TOTAL_PCT:.0f}%")
        band = max(band, 2)
    if total_pct > BAND3_TOTAL_PCT:
        crossed.append(f"total {total_pct:+.1f}% > {BAND3_TOTAL_PCT:.0f}%")
        band = 3
    for seed, p in sorted(seeds.items()):
        if p > BAND2_SEED_PCT:
            crossed.append(f"seed {seed} {p:+.1f}% > {BAND2_SEED_PCT:.0f}%")
            band = max(band, 2)
        if p > BAND3_SEED_PCT:
            crossed.append(f"seed {seed} {p:+.1f}% > {BAND3_SEED_PCT:.0f}%")
            band = 3
    return Verdict(environment=e_cur, base=_ident(base), cur=_ident(cur), total_pct=total_pct, seeds=seeds, stage_delta=stage_delta, band=band, crossed=tuple(crossed))


def _ident(s: dict[str, Any]) -> dict[str, str]:
    return {"label": str(s.get("label", "")), "utc": str(s.get("utc", "")), "commit": str(s.get("commit", ""))}


def render(v: Verdict) -> str:
    """What `perf-report` and `perf-gate` print (FR-009b: WHICH measurement, by HOW MUCH)."""
    lines = [f"perf bands [{v.environment}]: {v.cur['label']} vs {v.base['label']} -> band {v.band}"]
    for seed, p in sorted(v.seeds.items()):
        grew = sorted(((c - b, k) for k, (b, c) in v.stage_delta[seed].items() if c - b > 0.05), reverse=True)[:3]
        where = ("; grew: " + ", ".join(f"{k} +{d:.1f}s" for d, k in grew)) if grew and p > 0 else ""
        lines.append(f"  seed {seed:>3}  {p:+6.1f}%{where}")
    lines.append(f"  TOTAL     {v.total_pct:+6.1f}%")
    for c in v.crossed:
        lines.append(f"  crossed: {c}")
    lines.append(f"  owes: {v.owes}")
    return "\n".join(lines)
