#!/usr/bin/env python3
"""THE CHECK CENSUS (feature 141, GM 2026-08-28): which automated checks still earn their keep.

    python3 -m l7r.diagram.tools.check_census --out specs/141-checks-and-corpus-audit/ledger

The GM's question, per check: *"If our placement algorithm guarantees that a thing is correct, then I do
not believe that there is value in running an automated check afterwards to ensure that that exact same
thing is correct"* - against *"we place a label and then later on things are added to the map, then an
automated check to see whether the label's placement is still valid is an example of a useful automated
check."* So the test is SAME MEASURE vs SAME FACT, and it is measured, not assumed:

  1. INPUTS - the manifest keys a check reads: its own `M["key"]` / `M.get("key")` reads plus those of every
     derivation it `needs` (the registry's dataflow, feature 109), transitively.
  2. STAGES - the scripted hamlet is built stage by stage (the driver's `STAGES`, then `finish`) on the
     reference and on a polder, the manifest snapshotted after each; per key, the FIRST stage it exists
     and the LAST stage its content changes. A check whose inputs all settle at the stage that placed
     them is measuring what that placer guaranteed; a check with an input that a later stage rewrites is
     measuring a later fact.
  3. READERS - who reads the verdict besides the gate: the generator's re-roll ladder, the cohort and
     tripwire tools, waivers in pool gens, tests naming the check.
  4. FIXTURES - the frozen bad maps in pool/regressions/ pinning the check, by tier.

The output is a ledger (markdown + json), one row per check that runs on the reference hamlet, with a
VERDICT the session then acts on: RETIRE-CANDIDATE (same measure, gate-only reader, not meta) or KEEP
with its reason. A by-hand tool, not under the 100% rule (pyproject's coverage source list).
"""

from __future__ import annotations

import argparse
import copy
import glob
import inspect
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from typing import Any

HERE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
# A READER is a consumer whose BEHAVIOR branches on the verdict (the spec's round-1 review): the generator
# packages. The tools (cohort_audit, mapcheck's tripwire) only run and report checks and are NOT readers;
# neither is a test that asserts a check passes. Waiver mentions are listed for information only.
GENERATOR_READERS = ("l7r/diagram/hamletgen", "l7r/diagram/settlement", "l7r/diagram/sitegen", "l7r/diagram/waterfields")


def _key_reads(src: str) -> set[str]:
    return set(re.findall(r'\bM(?:\.get\(|\[)\s*"([a-z_]+)"', src))


def inputs_per_check() -> tuple[dict[str, set[str]], dict[str, Any]]:
    """{check name: manifest keys read, transitively through `needs`}, plus the segment per check."""
    from l7r.diagram.check_village import registry as reg

    segs = list(reg.GATE_SEGMENTS)
    by_write: dict[str, list[Any]] = defaultdict(list)
    for s in segs:
        for w in s.writes:
            by_write[w].append(s)
    own: dict[int, set[str]] = {id(s): _key_reads(inspect.getsource(s.fn)) for s in segs}
    memo: dict[int, set[str]] = {}

    def keys_of(s: Any, stack: tuple[int, ...] = ()) -> set[str]:
        if id(s) in memo:
            return memo[id(s)]
        if id(s) in stack:
            return set()
        out = set(own[id(s)])
        for n in s.needs:
            for src in by_write.get(n, ()):
                if src is not s:
                    out |= keys_of(src, (*stack, id(s)))
        memo[id(s)] = out
        return out

    checks: dict[str, set[str]] = {}
    seg_of: dict[str, Any] = {}
    for s in segs:
        for c in s.checks:
            checks[c] = keys_of(s)
            seg_of[c] = s
    return checks, seg_of


def stage_snapshots(spec: Any) -> list[tuple[str, dict[str, Any]]]:
    """[(stage name, manifest copy)] after each driver stage and after finish."""
    from l7r.diagram.hamletgen import build as _build  # noqa: F401 - ensure the package is importable
    from l7r.diagram.hamletgen import plan_site
    from l7r.diagram.hamletgen.driver import STAGES
    from l7r.diagram.settlement import Settlement

    plan = plan_site(spec)
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s._avoid_seats = []  # type: ignore[attr-defined]
    out: list[tuple[str, dict[str, Any]]] = []
    for st in STAGES:
        st(s, plan)
        out.append((st.__name__.replace("stage_", ""), copy.deepcopy(s.M)))
    with tempfile.TemporaryDirectory() as tmp:
        s.finish(os.path.join(tmp, "x"), render=False)
    out.append(("finish", copy.deepcopy(s.M)))
    return out


def key_lifecycle(snaps: list[tuple[str, dict[str, Any]]]) -> dict[str, tuple[int, int]]:
    """{key: (first stage index it exists non-empty, last stage index its content changed)}."""
    life: dict[str, tuple[int, int]] = {}
    prev: dict[str, str] = {}
    for i, (_name, M) in enumerate(snaps):
        for k, v in M.items():
            cur = json.dumps(v, sort_keys=True, default=str)
            if k not in prev:
                if v not in (None, [], {}, "", 0):
                    life[k] = (i, i)
                    prev[k] = cur
                continue
            if cur != prev[k]:
                life[k] = (life[k][0], i)
                prev[k] = cur
    return life


def readers(check: str) -> list[str]:
    out: list[str] = []
    for rel in GENERATOR_READERS:
        r = subprocess.run(["grep", "-rl", "--include=*.py", f'"{check}"', os.path.join(HERE, rel)], capture_output=True, text=True)
        for f in r.stdout.split():
            if "check_village" not in f and "check_census" not in f:
                out.append(os.path.relpath(f, HERE))
    r = subprocess.run(["grep", "-rl", "--include=*.py", f'"{check}"', os.path.join(HERE, "pool")], capture_output=True, text=True)
    out += [os.path.relpath(f, HERE) + " (waiver)" for f in r.stdout.split()]
    r = subprocess.run(["grep", "-rl", "--include=*.py", check, os.path.join(HERE, "tests")], capture_output=True, text=True)
    out += [os.path.relpath(f, HERE) + " (test)" for f in r.stdout.split()]
    return sorted(set(out))


def fixtures_by_check() -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for p in glob.glob(os.path.join(HERE, "pool", "regressions", "*.json")):
        with open(p) as fh:
            head = fh.read(4096)
        m = re.search(r'"scale":\s*"(hamlet|village|town|city|capital)"', head)
        tier = m.group(1) if m else "?"
        with open(p) as fh:
            M = json.load(fh)
        for f in (M.get("_regression") or {}).get("fires", []):
            out[f.split("[")[0]][tier] += 1
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="path stem: <stem>.md and <stem>.json are written")
    a = ap.parse_args(argv)
    # A RELATIVE --out IS RESOLVED FROM THE REPO ROOT, not from the cwd (feature 163). `make
    # check-census` runs from the skill directory, and every ledger this tool has ever written lives
    # under `specs/` at the REPO root - so its own default OUT (`specs/141-.../ledger`) could not be
    # written from the target that carries it: the run rolled the reference and a polder stage by
    # stage, then died on FileNotFoundError at the write. Found by pointing OUT at a new feature's
    # directory; the 141 run must have been driven by hand from elsewhere. Same resolution as
    # `tools/firing_census.py`, so the two ledgers are addressed the same way.
    if not os.path.isabs(a.out):
        a.out = os.path.abspath(os.path.join(HERE, "..", "..", "..", a.out))
    sys.path.insert(0, HERE)
    from l7r.diagram import hamletgen as hg
    from l7r.diagram.check_village import gate

    specs = {
        "reference": hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond"),
        "polder19": hg.HamletSpec(name="Polder", seed=19, households=16, field_archetype="polder_grid", down_deg=90),
    }
    inputs, seg_of = inputs_per_check()
    fixtures = fixtures_by_check()
    lifecycles: dict[str, tuple[list[str], dict[str, tuple[int, int]]]] = {}
    ran: dict[str, set[str]] = {}
    snaps_final: dict[str, dict[str, Any]] = {}
    for name, spec in specs.items():
        snaps = stage_snapshots(spec)
        lifecycles[name] = ([n for n, _ in snaps], key_lifecycle(snaps))
        M = snaps[-1][1]
        snaps_final[name] = M
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            gate(M, verbose=True)
        # NORMALIZE THE EMITTED NAME (feature 163). Two checks are emitted with an INDEX -
        # `check(f"stream_source_anchored[{idx}]", ...)` - so a literal comparison against the check
        # roster says no scripted map ever ran them, and this census labeled both stream anchors
        # NO-SCRIPTED-EXECUTOR ("a legacy-tier check") while the gate fires them on every hamlet that
        # has a stream. `firing_census` had the identical bug and is where the one definition lives;
        # importing it rather than restating it is the rule this directory already keeps - a
        # diagnostic OBSERVES, it never restates (tools/CLAUDE.md).
        from l7r.diagram.tools.firing_census import base_name

        ran[name] = {base_name(ln.split()[1]) for ln in buf.getvalue().splitlines() if ln.startswith(("PASS ", "FAIL "))}
    live = ran["reference"] | ran["polder19"]
    rows: list[dict[str, Any]] = []
    for c in sorted(inputs):
        if c not in live:
            fx = dict(fixtures.get(c, {}))
            rows.append(
                {
                    "check": c,
                    "keys": sorted(inputs.get(c, set())),
                    "stages": {},
                    "readers": readers(c),
                    "fixtures": fx,
                    "verdict": "NO-SCRIPTED-EXECUTOR",
                    "why": "no scripted map exercises it (a legacy-tier check: town / city / capital / village hand-authored maps only); no measured verdict is possible - the GM's choice at acceptance",
                    "on": [],
                }
            )
            continue
        keys = sorted(inputs.get(c, set()))
        placer, settle, per_map = 0, 0, {}
        for name, (stage_names, life) in lifecycles.items():
            first = max((life[k][0] for k in keys if k in life), default=0)
            last = max((life[k][1] for k in keys if k in life), default=0)
            per_map[name] = (stage_names[first] if keys else "-", stage_names[last] if keys else "-")
            placer, settle = max(placer, first), max(settle, last)
        later = settle > placer
        # VACUOUS ON THE SCRIPTED TIER: every input key is absent or empty on both final manifests - the check
        # measures a feature no hamlet has (a manor, a moat, a farrier) and passes by having nothing to judge.
        # It belongs with the legacy tiers' choice, not with the placer-guarantee question.
        finals = {n: snaps_final[n] for n in specs}
        vacuous = bool(keys) and all(not finals[n].get(k) for n in specs for k in keys)
        rd = readers(c)
        gen_readers = [r for r in rd if not r.endswith(("(test)", "(waiver)"))]
        fx = dict(fixtures.get(c, {}))
        if vacuous:
            verdict, why = (
                "VACUOUS-ON-SCRIPTED",
                "every input is absent on both scripted maps (" + ", ".join(keys) + ") - a legacy-tier feature; passes with nothing to judge; the GM's choice with the legacy set",
            )
        elif gen_readers:
            verdict, why = "KEEP", "a consumer branches on the verdict: " + ", ".join(gen_readers)
        elif not keys:
            verdict, why = "KEEP", "reads no manifest key the census can see (derived entirely) - judge by hand"
        elif later:
            verdict, why = "KEEP", "an input changes after its placer: " + ", ".join(f"{n}: placed at {p}, last changed at {q}" for n, (p, q) in per_map.items() if p != q)
        else:
            verdict, why = "RETIRE-CANDIDATE", "inputs settle at their placer on both maps: " + ", ".join(f"{n}: {p}" for n, (p, _l) in per_map.items())
        rows.append({"check": c, "keys": keys, "stages": per_map, "readers": rd, "fixtures": fx, "verdict": verdict, "why": why, "on": [n for n in specs if c in ran[n]]})
    with open(a.out + ".json", "w") as fh:
        json.dump({"stages": lifecycles["reference"][0], "rows": rows}, fh, indent=1)
    cand = [r for r in rows if r["verdict"].startswith("RETIRE")]
    md = [
        f"# Check census - {len(rows)} checks run on the reference hamlet and the seed-19 polder; {len(cand)} retire-candidates\n",
        "| check | inputs | placed / last changed (reference) | readers beyond the gate | fixtures | verdict | why |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        p, q = r["stages"].get("reference", ("-", "-"))
        md.append(
            f"| `{r['check']}` | {', '.join(r['keys']) or '-'} | {p} / {q} | {', '.join(x for x in r['readers'] if not x.endswith('(test)')) or '-'} | {', '.join(f'{k} {v}' for k, v in r['fixtures'].items()) or '-'} | **{r['verdict']}** | {r['why']} |"
        )
    with open(a.out + ".md", "w") as fh:
        fh.write("\n".join(md) + "\n")
    print(f"{len(rows)} checks; {len(cand)} retire-candidates; ledger -> {a.out}.md/.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
