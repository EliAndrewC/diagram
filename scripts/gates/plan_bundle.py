#!/usr/bin/env python3
"""The lean bundle a plan review reads (feature 375 amendment 11, FR-046; plan D64).

WHY (the GM 2026-10-13: *"Is feature 374 growing too large in a way that eats tokens"*). A task section's review read the whole
`spec.md` (23 KB on 374) every round, and a whole-plan review the whole plan (94 KB): 32 section reviews of 374 cost 20.8
million input tokens. A section's decisions answer to the requirements they cite, so the bundle carries those in full and a
one-line index of the rest, the GM's own words whole, the blocks under review and their earlier text - built OUT of the
repository, where no `CLAUDE.md` rides along:

    MANIFEST.md     what to judge, and how to record it
    request.md      the GM's words verbatim: the original request and every amendment from the earliest one the blocks answer
                    on (feature 383 amendment 8, FR-047: a whole copy grew with every amendment - 383's reached ~20k characters)
    request-index.md  the heading and first line of each request section left out
    spec-cited.md   each FR, SC and D the blocks name, its paragraph in full
    spec-index.md   the first line of every other FR and SC
    blocks.md       the blocks under review, each with its key and digest
    earlier.md      each changed block's text at its last CLEAR verdict (git), where there was one

`plan_gate.decide_prompt` (`make decide`) and `plan_gate.py delta` (`make plan-delta`) print the dispatch naming the MANIFEST.
"""

from __future__ import annotations

import json
import pathlib
import re
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import plan_gate as pg  # noqa: E402

OUT = pathlib.Path("/tmp/l7r-check")
_IDS = re.compile(r"\b((?:FR|SC)-\d{3}[a-z]?|D\d+[a-z]?)\b")
_ITEM = re.compile(r"^- \*\*((?:FR|SC)-\d{3}[a-z]?)\b", re.M)
_DECISION = re.compile(r"^\*\*(D\d+[a-z]?) - ", re.M)


def _paragraphs(text: str, pattern: re.Pattern[str]) -> dict[str, str]:
    """{id: its paragraph} - each match to the next blank line or the next item."""
    out: dict[str, str] = {}
    starts = list(pattern.finditer(text))
    for i, m in enumerate(starts):
        end = min([x for x in (text.find("\n\n", m.start()), starts[i + 1].start() if i + 1 < len(starts) else -1) if x > 0] or [len(text)])
        out.setdefault(m.group(1), text[m.start():end].rstrip() + "\n")
    return out


_AMEND = re.compile(r"^## Amendment (\d+)\b", re.M)
_SPEC_AMEND = re.compile(r"^### Amendment (\d+)\b", re.M)


def request_sections(text: str) -> tuple[str, list[tuple[int, str]]]:
    """`request.md` as (the original request, [(amendment number, its section)]) - a `###` under an amendment is part of it."""
    starts = list(_AMEND.finditer(text))
    if not starts:
        return text, []
    head = text[: starts[0].start()]
    return head, [(int(m.group(1)), text[m.start() : starts[i + 1].start() if i + 1 < len(starts) else len(text)]) for i, m in enumerate(starts)]


def spec_amendments(spec: str) -> dict[str, int]:
    """{FR or SC id: the amendment whose spec section holds it} - the ids under a `### Amendment N` heading, to the next `##`."""
    out: dict[str, int] = {}
    for m in _SPEC_AMEND.finditer(spec):
        nxt = re.search(r"^##", spec[m.end() :], re.M)
        for i in _ITEM.finditer(spec[m.end() : m.end() + nxt.start() if nxt else len(spec)]):
            out.setdefault(i.group(1), int(m.group(1)))
    return out


def answered(under: list[tuple[str, str]], spec: str) -> int | None:
    """The earliest amendment the blocks answer: per block, the earliest of its heading's `Amendment N` and the amendment of
    every id it cites (a later amendment correcting an earlier one's requirement answers the earlier one too - spec review of
    amendment 8); None when any block answers none - the original plan, which is judged against the whole request."""
    of = spec_amendments(spec)
    found: list[int] = []
    for key, body in under:
        m = re.search(r"\bAmendment (\d+)\b", key) or re.match(r"\s*#+ Amendment (\d+)\b", body)
        ns = ([int(m.group(1))] if m else []) + [of[i.group(1)] for i in _IDS.finditer(key + "\n" + body) if i.group(1) in of]
        if not ns:
            return None
        found.append(min(ns))
    return min(found) if found else None


def trimmed_request(text: str, n: int | None) -> tuple[str, str]:
    """(the request a review of amendment `n` reads, the index of what it leaves out). Every amendment from `n` on is kept: a
    later one can change what an earlier one asked."""
    head, parts = request_sections(text)
    if n is None or not parts:
        return text, ""
    kept = [body for k, body in parts if k >= n]
    left = [body for k, body in parts if k < n]
    index = "".join(f"{body.splitlines()[0]} - {next((ln for ln in body.splitlines()[1:] if ln.strip()), '').strip()[:160]}\n" for body in left)
    return head + "".join(kept), index


def build(spec_dir: pathlib.Path, name: str, under: list[tuple[str, str]], earlier: dict[str, str], how: str) -> pathlib.Path:
    """Write the bundle for the blocks `under` ([(key, text)]) and return its MANIFEST."""
    out = OUT / f"plan-{spec_dir.name}-{name}"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    spec = (spec_dir / "spec.md").read_text(encoding="utf-8") if (spec_dir / "spec.md").is_file() else ""
    plans = "".join((spec_dir / f).read_text(encoding="utf-8") for f in ("plan.md", "plan-done.md") if (spec_dir / f).is_file())
    items, decisions = _paragraphs(spec, _ITEM), _paragraphs(plans, _DECISION)
    cited = list(dict.fromkeys(m.group(1) for _k, body in under for m in _IDS.finditer(body)))
    # a decision's own paragraph is in blocks.md already; the requirements it answers to, and the decisions it leans on, are cited
    own = {m.group(1) for _k, body in under for m in _DECISION.finditer(body)}
    (out / "spec-cited.md").write_text("# The requirements and decisions the blocks name, in full\n\n" + "\n".join(
        (items.get(i) or decisions.get(i) or "") for i in cited if i not in own and (i in items or i in decisions)), encoding="utf-8")
    (out / "spec-index.md").write_text("# Every other requirement, its first line\n\n" + "".join(
        p.splitlines()[0] + "\n" for i, p in items.items() if i not in cited), encoding="utf-8")
    if (spec_dir / "request.md").is_file():
        req, index = trimmed_request((spec_dir / "request.md").read_text(encoding="utf-8"), answered(under, spec))
        (out / "request.md").write_text(req, encoding="utf-8")
        (out / "request-index.md").write_text("# The request's sections left out - each earlier amendment, its heading and first line\n\n" + (index or "(none - the whole request is in request.md)\n"), encoding="utf-8")
    (out / "blocks.md").write_text("".join(f"<!-- block {json.dumps(k)} sha256 {pg.block_digest(b)} -->\n{b}\n" for k, b in under), encoding="utf-8")
    (out / "earlier.md").write_text("# Each changed block's text at its last CLEAR verdict\n\n" + ("".join(
        f"<!-- block {json.dumps(k)} -->\n{t}\n" for k, t in earlier.items()) or "(none - every block here is new)\n"), encoding="utf-8")
    manifest = out / "MANIFEST.md"
    manifest.write_text(f"""# Plan review bundle - {spec_dir.name}, {name}

A MODE 4 plan review of the blocks in `blocks.md` and nothing else of the plan (feature 375 amendment 11). Read the files beside
this MANIFEST and nothing in the repository: `request.md` is the GM's words verbatim - the original request and every amendment
from the one these blocks answer on, the earlier ones indexed in `request-index.md`; `spec-cited.md` holds every requirement and
decision the blocks name, in full; `spec-index.md` the first line of every other requirement - grep it for one the blocks
should have named; `earlier.md` what a changed block said when last judged CLEAR.

Find each decision in the blocks, class it `within` or `narrowing`, and rule on each narrowing (LEGITIMATE / NOT LEGITIMATE).

{how}
""", encoding="utf-8")
    return manifest


def task_prompt(spec_dir: pathlib.Path, task: str) -> str:
    """`make decide`'s dispatch (FR-003(a)) on the bundle of one task's section."""
    plan = spec_dir / "plan.md"
    text = plan.read_text(encoding="utf-8")
    section = pg.task_sections(text).get(task, "")
    try:
        review = json.loads((spec_dir / pg.RECORD).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        review = {}
    entry = (review.get("tasks") or {}).get(task) or {}
    earlier = pg.History(plan).section(task, str(entry["section_sha256"])) if entry.get("section_sha256") else None
    n = spec_dir.name.split("-")[0]
    how = (f"Record it: the JSON is `{{\"section_sha256\": \"{pg.digest(section.encode())}\", \"decisions\": [...]}}`, written under "
           f"/tmp, then `make plan-verdict F={n} TASK={task} FILE=<it> AS=spec-fidelity`.")
    manifest = build(spec_dir, task, [(f"the section of {task}", section)], {task: earlier} if earlier else {}, how)
    return (f"MODE 4: PLAN REVIEW of one task's section - feature {spec_dir.name}, task {task} (a decision preflight, feature 375 "
            f"FR-003a), on its bundle: read {manifest} and the files beside it, and nothing in the repository.")


def delta_prompt(spec_dir: pathlib.Path, keys: list[str]) -> str:
    """`make plan-delta`'s dispatch (FR-043) on the bundle of the plan's changed blocks."""
    plan = spec_dir / "plan.md"
    text = plan.read_text(encoding="utf-8")
    under = [(k, b) for k, b, _a in pg.blocks(text) if k in keys]
    try:
        review = json.loads((spec_dir / pg.RECORD).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        review = {}
    have, hist = pg.reviewed_blocks(review), pg.History(plan)
    removed = [k[len(pg.REMOVED):] for k in keys if k.startswith(pg.REMOVED)]
    earlier = {k: (have[k].get("text") or hist.block(k, str(have[k].get("sha256"))) or "") for k, _b in under if k in have}
    # a block deleted by hand is judged on what it said: its earlier text, and `"removed"` as its digest
    earlier.update({pg.REMOVED + k: (have[k].get("text") or hist.block(k, str(have[k].get("sha256"))) or "") for k in removed if k in have})
    n = spec_dir.name.split("-")[0]
    shas = json.dumps({**{k: pg.block_digest(b) for k, b in under}, **{pg.REMOVED + k: "removed" for k in removed}})
    how = (f"Record it: the JSON is `{{\"blocks\": {shas}, \"decisions\": [...]}}`, written under /tmp, then "
           f"`make plan-verdict F={n} BLOCKS=1 FILE=<it> AS=spec-fidelity`.")
    # EACH BLOCK SET ITS OWN BUNDLE (feature 385 T29, the round arbiter's fix on hour:385-approach-checklist@13): one shared
    # `plan-<feature>-blocks` meant a second plan review could not be built while one was reading - T26 waited on T25 twice, and
    # one round's verdict was lost - so the directory names the tasks its blocks belong to and the blocks' own digest
    tasks = sorted({m.group(1) for k, _b in under for m in [re.match(r"#+ (T\d+)\b", k)] if m})
    name = f"blocks-{'-'.join(tasks) or 'plan'}-{pg.digest(shas.encode())[:8]}"
    manifest = build(spec_dir, name, under, {k: t for k, t in earlier.items() if t}, how)
    return (f"MODE 4: PLAN REVIEW of {len(under) + len(removed)} changed block(s) of feature {spec_dir.name}'s plan (feature 375 FR-043), on their "
            f"bundle: read {manifest} and the files beside it, and nothing in the repository.")
