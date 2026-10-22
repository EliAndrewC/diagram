"""The room table (405 T113): one row per spacing or size knob - its label, what it measures, its research ceiling, and
whether the band the seats are dealt over grows with it - printed into part B's prompt (`approach_gate.cohort`) and the round
arbiter's bundle (`arbiter_bundle.bundle`) when what failed is a FIT failure: a knot, a refused seat or web, an unreached house.

WHY (the GM, 2026-10-21, the third process fix; the round arbiter's tooling_fix on ask:set-down-T26): two room probes widened
`grow_gap` by 5 and 10 ft while the seating band stayed the same size, so they dealt the same seats into the same band - tighter
packing, not more room - and were read as "room fails". The table says which knobs grow the band, and how far the research
lets each go, at the moment the session weighs more room (part B's B6). The rows are `room_table.json` beside this file."""

from __future__ import annotations

import json
import pathlib
import re

TABLE = pathlib.Path(__file__).resolve().with_name("room_table.json")
FIT = ("refused", "lane_knots", "groves_crossed_by_lanes", "fixtures_on_groves")
"""The cohort failures that are a fit failure: something did not fit where it stands (a seat or the web refused, two ways' ends
left unjoined, a lane or fixture on a grove). Not: row_rules, water_rules, farmstead_across_brook, trees_shading_plots."""
_FIT_WORDS = re.compile(r"\b(?:knots?|lane_knots|refused|unreached|room)\b", re.I)


def is_fit(failures: list[str]) -> bool:
    """Is any of a cohort seed's `failures` a fit failure (`FIT`; a refusal is `refused:<kind>`)?"""
    return any(f.split(":", 1)[0] in FIT for f in failures)


def names_fit(text: str) -> bool:
    """Does a question put to the arbiter name a fit failure?"""
    return bool(_FIT_WORDS.search(text))


def render(path: pathlib.Path = TABLE) -> str:
    """The table as Markdown, headed with what to do with it."""
    rows = json.loads(path.read_text(encoding="utf-8"))["rows"]
    out = ["## The room table (405 T113) - a fit failure: weigh more room within these ceilings before packing (B6)", "",
           "A room probe grows the BAND with the gap: a knob marked DOES NOT GROW, widened alone, deals the same seats into the same "
           "band - packing, not room.", "",
           "| knob | value | label | measures | research ceiling | the seating band |", "|---|---|---|---|---|---|"]
    out += [f"| `{r['knob']}` ({r['where']}) | {r['value']} | {r['label']} | {r['measures']} | {r['ceiling']} | {r['band']} |" for r in rows]
    return "\n".join(out) + "\n"
