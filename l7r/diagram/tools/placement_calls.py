"""The placement-stages page's call counts (feature 434): each stage's in its heading, and the table that ends the page.

The counts are the record `make phase-calls` keeps (`tools/phase_calls.py`, `dev/phase-calls.json`), the newest measurement
of each map type. The page breaks down the reference hamlet's roll: each stage shows the reference's calls and their share
of its total, or a dash where the reference's record lacks the stage. Every roll runs every stage - one that does not apply
returns after a handful of calls - so another recorded type is shown beside a stage, named, never in its place, where it
spent more calls in the stage than the reference (a polder's `waterward`). Calls only: no time is shown (the GM, 2026-10-27).
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from html import escape
from typing import Any

from l7r.diagram.tools.perf_snapshot import REFERENCE
from l7r.diagram.tools.phase_calls import RECORD, type_key

DASH = "–"
CSS = """
.hd .calls{margin-left:auto;font-variant-numeric:tabular-nums;color:var(--dim);font-size:.85em;white-space:nowrap}
#calls table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
#calls th,#calls td{padding:3px 8px;border-bottom:1px solid var(--rule);text-align:right}
#calls th:nth-child(2),#calls td:nth-child(2){text-align:left}
#calls tr.stage-row[data-stage]{cursor:pointer}
#calls tr.stage-row[data-stage]:hover{background:var(--step)}
#calls tr.stage-row[data-stage] td:nth-child(2)::before{content:"\\25B8  ";color:var(--dim)}
#calls tr.stage-row.open td:nth-child(2)::before{content:"\\25BE  "}
#calls tr.step-row{background:var(--step);color:var(--dim)}
#calls tr.step-row td:nth-child(2){padding-left:28px}
#calls tr.step-row[hidden]{display:none}
#calls tr.total td{font-weight:600;border-top:2px solid var(--rule)}
"""
SCRIPT = """<script>
document.querySelectorAll('#calls tr.stage-row[data-stage]').forEach(function (row) {
  row.addEventListener('click', function () {
    var open = row.classList.toggle('open');
    document.querySelectorAll('#calls tr.step-row[data-of="' + row.dataset.stage + '"]').forEach(function (r) { r.hidden = !open; });
  });
});
</script>"""


def load(path: str = RECORD) -> dict[str, Any]:
    """The record, or none."""
    try:
        with open(path, encoding="utf-8") as fh:
            return dict(json.load(fh))
    except OSError:
        return {}


def reference(record: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """The reference hamlet's measurement, or None."""
    return record.get(type_key(REFERENCE))


def beside(record: Mapping[str, Any], stage: str) -> list[tuple[str, Mapping[str, Any], int]]:
    """The other recorded types that spent more calls in `stage` than the reference: (type, its measurement, its calls)."""
    ref = reference(record)
    floor = ref["stages"][stage]["calls"] if ref and stage in ref.get("stages", {}) else 0
    others = [(t, m, int(m["stages"][stage]["calls"])) for t, m in record.items() if t != type_key(REFERENCE) and stage in m.get("stages", {})]
    return sorted((o for o in others if o[2] > floor), key=lambda o: -o[2])


def _pct(n: int, of: int) -> str:
    return f"{100 * n / of:.1f}%" if of else DASH


def _also(record: Mapping[str, Any], stage: str) -> str:
    return "".join(f"; {kind}: {n:,} ({_pct(n, m['total'])})" for kind, m, n in beside(record, stage))


def heading(record: Mapping[str, Any], fn: str) -> str:
    """The calls a stage heading carries: the reference's count and share (or a dash), and any type beside it."""
    stage, ref = fn.replace("stage_", ""), reference(record)
    also = escape(_also(record, stage))
    if ref is None or stage not in ref.get("stages", {}):
        return f'<span class="calls">{DASH} calls{also}</span>'
    v = ref["stages"][stage]
    return f'<span class="calls" title="the reference hamlet, seed {ref["seed"]}, {ref["households"]} households, measured {escape(str(ref.get("date", "")))}">{v["calls"]:,} calls &middot; {_pct(v["calls"], ref["total"])}{also}</span>'


def section(record: Mapping[str, Any], stages: Sequence[tuple[int, str, str, Sequence[tuple[str, str]]]]) -> list[str]:
    """The page's last section: every stage (number, function, title, its steps as (dotted path, short name)) with its calls,
    each row opening onto its steps and its own work."""
    ref = reference(record)
    out = [
        '<section class="stage" id="calls">',
        '<div class="hd"><span class="t">Calls by stage and step</span></div>',
        "<p class=\"why\">The Python calls each stage made in the newest recorded 40-household hamlet (<code>make phase-calls</code>; "
        "cProfile's count, as <code>make perf-fanout</code> takes it), breaking down the reference hamlet's roll; another map type "
        "measured is named beside a stage where it spent more calls there, with its share of its own roll. Click a stage to open its steps: a "
        "step's calls are those made while it was the innermost listed step running, so a step that contains another shows only "
        "its own share, and the stage's own work is what ran outside every listed step.</p>",
        "<table><thead><tr><th>#</th><th>stage or step</th><th>calls</th><th>of the stage</th><th>of the roll</th></tr></thead><tbody>",
    ]
    for i, fn, title, steps in stages:
        stage = fn.replace("stage_", "")
        also = escape(_also(record, stage))
        if ref is None or stage not in ref.get("stages", {}):
            out.append(f'<tr class="stage-row"><td>{i:02d}</td><td>{escape(title)}{also}</td><td>{DASH}</td><td></td><td>{DASH}</td></tr>')
            continue
        v, key = ref["stages"][stage], f"s{i:02d}"
        out.append(f'<tr class="stage-row" data-stage="{key}"><td>{i:02d}</td><td>{escape(title)}{also}</td><td>{v["calls"]:,}</td><td></td><td>{_pct(v["calls"], ref["total"])}</td></tr>')
        rows = [(name, v["steps"].get(path, 0)) for path, name in steps] + [("(the stage's own work)", v["own"])]
        out += [f'<tr class="step-row" data-of="{key}" hidden><td></td><td>{escape(name)}</td><td>{n:,}</td><td>{_pct(n, v["calls"])}</td><td>{_pct(n, ref["total"])}</td></tr>' for name, n in rows]
    if ref is not None:
        out.append(
            f'<tr class="total"><td></td><td>the reference hamlet, all stages (seed {ref["seed"]}, {ref["households"]} households, measured {escape(str(ref.get("date", "")))})</td><td>{ref["total"]:,}</td><td></td><td>100%</td></tr>'
        )
    out += ["</tbody></table>", SCRIPT, "</section>"]
    return out
