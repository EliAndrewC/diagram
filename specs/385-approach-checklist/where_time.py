"""Per-task time by bucket: each event gap goes to the task active at its start (the last `make task-start` before it)."""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/diagram/.clones/diagram-backlog")
sys.path.insert(0, str(ROOT / "scripts" / "measure"))
import feature_report as fr  # noqa: E402

NAME = "385-approach-checklist"
SINCE = sys.argv[1] if len(sys.argv) > 1 else "2026-10-18T03:30:00Z"
events = fr.load_events(fr.event_logs(ROOT, NAME), [], SINCE, "")
common = Path(fr._git(ROOT, "rev-parse", "--path-format=absolute", "--git-common-dir").strip())
starts = []
for raw in (common / "task-starts.jsonl").read_text().splitlines():
    r = json.loads(raw)
    if r.get("feature") == NAME:
        starts.append((fr.parse_t(r["utc"]), r["task"]))
starts.sort()


def task_at(t: float) -> str:
    cur = "-"
    for s, k in starts:
        if s <= t:
            cur = k
        else:
            break
    return cur


BUCKET = {
    "thinking": "model", "writing the spec": "model",
    "waiting: spec-fidelity": "plan review", "waiting: spec-fidelity-verify": "plan review", "dispatching: spec review": "plan review",
    "waiting: impl-drift": "claims check", "waiting: claims-triage": "claims check", "dispatching: claims check": "claims check",
    "waiting: glyph-check": "glyph check",
    "waiting: round-arbiter": "arbiter", "dispatching: round arbiter": "arbiter",
    "gate": "gate/tests", "quick test": "gate/tests", "test file": "gate/tests",
    "waiting: a background run": "background run (gate, page session)",
    "waiting: the GM": "the GM", "idle (over an hour)": "idle",
}
RECORD = ("quote-check", "record-format", "source-reader", "source-applicability", "translation-check", "intro-check", "modal-", "entry-drift", "research-pass")


def bucket(cat: str) -> str:
    if cat in BUCKET:
        return BUCKET[cat]
    if cat.startswith("waiting: ") and any(r in cat for r in RECORD) or cat in ("dispatching: record check", "dispatching: review check"):
        return "record/modal checks"
    if cat.startswith("waiting: ") or cat.startswith("dispatching"):
        return "other subagent"
    return "tools (make, edits)"


out: dict[str, Counter] = defaultdict(Counter)
by_sid = defaultdict(list)
for e in events:
    by_sid[str(e.get("sid"))].append(e)
fg = fr.tp.foreground_spans(events)
for evs in by_sid.values():
    for a, b in zip(evs, evs[1:], strict=False):
        gap = fr.parse_t(b["t"]) - fr.parse_t(a["t"])
        if gap <= 0:
            continue
        task = task_at(fr.parse_t(a["t"]))
        if gap > fr.IDLE_CAP_S:
            cat = "idle (over an hour)"
        elif run := fr.tp.in_span(fr.parse_t(a["t"]), fg):
            cat = f"waiting: {run}"
        elif a["ev"] == "PreToolUse":
            cat = fr._tool_cat(a)
        elif a["ev"] == "Stop":
            cat = fr._waiting(b)
        else:
            cat = "thinking"
        out[task][bucket(cat)] += gap
cols = ["model", "tools (make, edits)", "gate/tests", "background run (gate, page session)", "plan review", "claims check", "record/modal checks", "glyph check", "arbiter", "other subagent", "the GM", "idle"]
print("| task | total | " + " | ".join(cols) + " |")
print("|---|---|" + "---|" * len(cols))
order = sorted(out, key=lambda k: min((s for s, t in starts if t == k), default=0))
tot = Counter()
for k in order:
    c = out[k]
    tot.update(c)
    print(f"| {k} | {sum(c.values())/60:.0f} | " + " | ".join(f"{c[x]/60:.0f}" for x in cols) + " |")
print(f"| all | {sum(tot.values())/60:.0f} | " + " | ".join(f"{tot[x]/60:.0f}" for x in cols) + " |")

print()
agents: dict[str, Counter] = defaultdict(Counter)
amins: dict[str, Counter] = defaultdict(Counter)
open_a = {}
for e in sorted(events, key=lambda e: fr.parse_t(e["t"])):
    if e.get("ev") == "SubagentStart":
        open_a[str(e.get("aid"))] = (fr.parse_t(e["t"]), str(e.get("agent") or "?"), task_at(fr.parse_t(e["t"])))
    elif e.get("ev") == "SubagentStop" and str(e.get("aid")) in open_a:
        t0, kind, task = open_a.pop(str(e.get("aid")))
        agents[task][kind] += 1
        amins[task][kind] += fr.parse_t(e["t"]) - t0
print("| task | agents | agent minutes | by kind (count) |")
print("|---|---|---|---|")
for k in order:
    if agents[k]:
        print(f"| {k} | {sum(agents[k].values())} | {sum(amins[k].values())/60:.0f} | " + ", ".join(f"{a} {n}" for a, n in agents[k].most_common()) + " |")
