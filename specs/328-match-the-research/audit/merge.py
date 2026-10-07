"""Merge the nine batch outputs into specs/328-match-the-research/ranking.json and ranking.md (feature 328, T03)."""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

AUDIT = Path(sys.argv[1])
FEATURE = Path(sys.argv[2])
TIERS = ["E0", "E1", "E2", "E3", "E4"]
findings = json.loads((FEATURE / "findings.json").read_text())
verdict = {f["key"]: f["verdict"] for f in findings}
note = {f["key"]: f["note"] for f in findings}

rows = {}
for n in range(1, 10):
    for line in (AUDIT / f"out{n}.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            r["tier_as_ranked"] = r["tier"]  # the batch's tier, before the re-check and the second reader
            rows[r["key"]] = r
# Findings a wave's re-check exposed (spec Edge Cases: "recorded in the ranking under the tier they take").
for extra in sorted(AUDIT.glob("found-*.jsonl")):
    for line in extra.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            r["tier_as_ranked"] = r["tier"]
            rows[r["key"]] = r
            verdict[r["key"]] = r["verdict"]
            note.setdefault(r["key"], "")
missing = [k for k in verdict if k not in rows]
extra = [k for k in rows if k not in verdict]
if missing or extra:
    sys.exit(f"missing {len(missing)}: {missing[:5]}\nextra {len(extra)}: {extra[:5]}")

# The bounded E0 re-check (plan Phase 1.3) and the second reader's disagreements (plan D4) replace the batch rows.
for extra in ("e0review-out.jsonl",):
    if (AUDIT / extra).exists():
        for line in (AUDIT / extra).read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                r["e0_rechecked"] = True
                r["tier_as_ranked"] = rows[r["key"]]["tier_as_ranked"]
                rows[r["key"]] = r
if (AUDIT / "overrides.json").exists():
    for k, o in json.loads((AUDIT / "overrides.json").read_text()).items():
        rows[k].update(o)

# Bounded E0 (spec round 1): an E0 row must be MISLABELED, or carry an explicit page-already-says reason.
retiered = []
for k, r in rows.items():
    r["verdict"] = verdict[k]
    r.setdefault("after", [])
    r.setdefault("flag", "")
    r["wave"] = ""
    r.setdefault("tier_as_ranked", r["tier"])
    if r["tier"] == "E0" and verdict[k] not in ("MISLABELED", "UNCLAIMED") and not r.get("e0_basis") and not r.get("e0_rechecked"):
        r["needs_e0_review"] = True

# The wave that closed each row (audit/waves.json: written from the claims index at a wave's close).
waves = json.loads((AUDIT / "waves.json").read_text()) if (AUDIT / "waves.json").exists() else {}

# A row waits for its dependencies: it takes at least their tier (an open row only - a closed row keeps the tier it was
# closed at, so re-tiering an open dependency never rewrites a wave's history).
changed = True
while changed:
    changed = False
    for r in rows.values():
        if waves.get(r["key"]):
            continue
        for d in r["after"]:
            if d in rows and TIERS.index(rows[d]["tier"]) > TIERS.index(r["tier"]):
                r["tier"] = rows[d]["tier"]
                changed = True


def module(k):
    return k.split("::")[0]


for r in rows.values():
    r["wave"] = waves.get(r["key"], "")

ordered = sorted(rows.values(), key=lambda r: (TIERS.index(r["tier"]), module(r["key"]), r["key"]))
# within a tier, a row after its dependency
pos = {r["key"]: i for i, r in enumerate(ordered)}
for _ in range(len(ordered)):
    moved = False
    for r in list(ordered):
        for d in [] if r["wave"] else r["after"]:
            if d in pos and pos[d] > pos[r["key"]]:
                ordered.remove(r)
                ordered.insert(ordered.index(rows[d]) + 1, r)
                pos = {x["key"]: i for i, x in enumerate(ordered)}
                moved = True
    if not moved:
        break

(FEATURE / "ranking.json").write_text(json.dumps(ordered, indent=1) + "\n")

c = Counter(r["tier"] for r in ordered)
lines = [
    "# Feature 328: the findings ranked by the implementation work they take",
    "",
    "Load this file when: choosing or reviewing the next wave of feature 328.",
    "",
    "Generated from `ranking.json` (the data; edit that, not this). The audit read `make claims-report` at `a52ff1bcd`",
    "(`findings.json`, 565 findings); nine Opus readers tiered them from `ranking-brief.md`. Tiers, easiest first (spec",
    "FR-003): **E0** the claim alone, **E1** one value, **E2** one rule, **E3** a form or several places, **E4** research",
    "first. Within a tier, rows of one module sit together; a row waits for the rows it names under `after`.",
    "",
    "| tier | rows |",
    "|---|---|",
] + [f"| {t} | {c.get(t, 0)} |" for t in TIERS] + [f"| all | {len(ordered)} |", ""]
for t in TIERS:
    lines += [f"## {t}", "", "| # | finding | verdict | fix | wave |", "|---|---|---|---|---|"]
    for i, r in enumerate([r for r in ordered if r["tier"] == t], 1):
        key = r["key"].replace(".claude/skills/diagram/", "").replace("|", "\\|")
        fix = r["fix"].replace("|", "\\|")
        flag = f" **({r['flag']})**" if r.get("flag") else ""
        lines.append(f"| {i} | `{r['key']}` | {r['verdict']} | {fix}{flag} | {r['wave']} |")
    lines.append("")
(FEATURE / "ranking.md").write_text("\n".join(lines))
print(dict(c), "flags:", sum(1 for r in ordered if r.get("flag")), "E0 to review:", sum(1 for r in ordered if r.get("needs_e0_review")))
