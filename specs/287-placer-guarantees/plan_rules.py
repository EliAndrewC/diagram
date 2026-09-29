"""Writes plan-rules.md from design/*.json (feature 287): one row per distinct rule, the owner, the mechanism and the risk."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    def esc(s: object) -> str:
        return str(s or "").replace("|", "/").replace("\n", " ")

    out = ["# Feature 287 - the rules, one row each (generated from design/*.json)", "",
           "Every distinct rule the five area designs found, with its owner and mechanism; the full design (fallback, later stages,",
           "unit test, what it retires, risk) is the design file's row of the same id. Regenerate with `python3 plan_rules.py`.", ""]
    for area in ("water", "ways", "homes", "woods", "labels"):
        d = json.loads((HERE / "design" / f"design-{area}.json").read_text())
        out += [f"## {area} ({len(d['rules'])} rules)", "", "| id | rule | owner | mechanism | risk |", "|---|---|---|---|---|"]
        for r in d["rules"]:
            out.append(f"| {esc(r.get('id'))} | {esc(r.get('rule'))[:220]} | `{esc(r.get('owner'))[:90]}` | {esc(r.get('mechanism'))[:300]} | {esc(r.get('risk'))} |")
        out.append("")
    (HERE / "plan-rules.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
