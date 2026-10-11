"""Feature 340's measurement (plan D2): on the declared program example, every caption the composer and the hand-sheet
placer seat differently, attributed to the entry's three sources, and what each of the entry's two fixes removes.

    make spec-harness SPEC=specs/340-program-example-captions-hand-sheet-placer OUT=<json>

Run as a test node (the engine refuses in-process calls outside make). Nothing in the engine is changed: the composer's
functions are wrapped for the test's life only.

C  the composer's seats as `emit_svg` makes them (recorded from `compound._seat_all`)
H  `labels.hand_sheet.seat` on the same declared draft
Composer variants, re-seated by a loop with the composer's own steps (strict, then the soft seat where none is free - no
repair or growth; the loop with every piece the composer's own is checked to reproduce C), each with one source swapped
for the hand-sheet placer's: VIEW (the obstacle index from `hand_sheet.classify` over the drawn sheet, the seated captions
added as the composer adds them; the roofed court's late obstacles dropped), SUBJECT (`hand_sheet.subjects` over the
declared parts, every subject tried in order), WIDTH (`hand_sheet.char_w_of` per caption), and ALL three. FIX 1 is VIEW (the composer
indexing with `classify`). FIX 2 is the hand-sheet placer taking the composer's subjects (`hand_sheet.subjects` patched).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/h340.json")
TOL = 1.0


def _xy(p) -> tuple[float, float]:  # noqa: ANN001
    return (round(p.x, 1), round(p.y, 1))


def _same(a, b) -> bool:  # noqa: ANN001
    return a is not None and b is not None and abs(a.x - b.x) <= TOL and abs(a.y - b.y) <= TOL


def test_measure(monkeypatch) -> None:  # noqa: ANN001
    from l7r.diagram import compound as c
    from l7r.diagram.labels import Obstacle
    from l7r.diagram.labels import hand_sheet as hs
    from l7r.diagram.labels.standard import CHAR_W_EM, WEIGHT_OBSTACLE

    prog = c.county_magistracy_program()
    res = c.place(prog)

    runs: list[tuple] = []
    orig = c._seat_all

    def rec(requests, obstacles, frame, one=None):  # noqa: ANN001, ANN202
        seats, stuck = orig(requests, obstacles, frame, one)
        runs.append((list(requests), list(seats), list(obstacles), frame, {}))
        return seats, stuck

    monkeypatch.setattr(c, "_seat_all", rec)
    svg = c.emit_svg(prog, res)
    requests, C, obstacles, frame, late = runs[-1]
    monkeypatch.setattr(c, "_seat_all", orig)
    monkeypatch.setattr(c, "_seat_captions", lambda *a, **k: ([], 0.0))
    nocap = c.emit_svg(prog, res)
    monkeypatch.undo()

    # the hand-sheet reading of the declared draft
    shapes, view = hs.read_sheet(svg)
    caps = hs.captions_of(shapes)
    assert len(caps) == len(requests), (len(caps), len(requests))
    per_group: dict[int, int] = {}
    for idx in caps:
        per_group[shapes[idx[0]].group] = per_group.get(shapes[idx[0]].group, 0) + 1
    heads = [shapes[idx[0]] for idx in caps]
    owns = [hs.declared_parts(h, shapes, alone=per_group[h.group] == 1) for h in heads]
    H = [p for _caps, p, _per in hs.seat(svg)]

    # the variants' pieces
    ns, nview = hs.read_sheet(nocap)
    named = frozenset(h.kind for h in heads)
    sub_c = [[r[1]] for r in requests]
    sub_h = [hs.subjects(o, h.size) for o, h in zip(owns, heads, strict=True)]  # the whole ordered list, as `one()` tries it
    cw_c = [CHAR_W_EM] * len(requests)
    cw_h = [hs.char_w_of(h.element, h.text, h.size) for h in heads]

    def idx_composer(i, sub, seats):  # noqa: ANN001, ANN202
        return c._caption_index(obstacles, seats, subject=sub)

    def idx_view(i, sub, seats):  # noqa: ANN001, ANN202
        index = hs.classify(ns, nview, subject=list(sub.poly), area=sub.kind == "area", kind=requests[i][5], named=named)
        for p in seats:
            index.add(Obstacle(p.block, WEIGHT_OBSTACLE))
        return index

    def seat_loop(subs, cws, index_fn):  # noqa: ANN001, ANN202
        # each subject in order, the first with a free seat winning (as `hand_sheet.seat`'s `one()` takes them); where none
        # has one, the cheapest seat over all of them
        seats = []
        for i, (text, _s, size, *_r) in enumerate(requests):
            got = None
            for sub in subs[i]:
                got = c.place_caption(text, size, sub, index_fn(i, sub, seats), frame, strict=True, char_w=cws[i])
                if got is not None:
                    break
            if got is None:
                got = min((c.place_caption(text, size, sub, index_fn(i, sub, seats), frame, char_w=cws[i]) for sub in subs[i]), key=lambda q: q.cost)
            seats.append(got)
        return seats

    base = seat_loop(sub_c, cw_c, idx_composer)
    variants = {
        "view": seat_loop(sub_c, cw_c, idx_view),
        "subject": seat_loop(sub_h, cw_c, idx_composer),
        "width": seat_loop(sub_c, cw_h, idx_composer),
        "all": seat_loop(sub_h, cw_h, idx_view),
    }
    switch = variants["all"]  # D3's switch: the view, the subjects and the width all the hand-sheet placer's

    # FIX 2: the hand-sheet placer taking the composer's subjects
    by_own = {id(o): sub_c[k][0] for k, o in enumerate(owns)}
    real_dp, real_sub = hs.declared_parts, hs.subjects
    made: list[list] = []

    def dp(head, sh, alone):  # noqa: ANN001, ANN202
        k = next(j for j, h in enumerate(heads) if h.at == head.at)
        made.append([k])
        return owns[k]

    def sb(own, size=0.0):  # noqa: ANN001, ANN202
        return [by_own[id(own)]] if id(own) in by_own else real_sub(own, size)

    monkeypatch.setattr(hs, "declared_parts", dp)
    monkeypatch.setattr(hs, "subjects", sb)
    H2 = [p for _caps, p, _per in hs.seat(svg)]
    monkeypatch.setattr(hs, "declared_parts", real_dp)
    monkeypatch.setattr(hs, "subjects", real_sub)

    rows = []
    for i, (text, *_r) in enumerate(requests):
        if _same(C[i], H[i]):
            continue
        removes = [k for k in ("view", "subject", "width") if _same(variants[k][i], H[i])]
        explained = bool(removes) or _same(variants["all"][i], H[i])
        cause = None
        if not explained:
            cause = "strictness (the hand-sheet seat covers ink)" if H[i].cost > 0 else "order, clearance or repair"
        rows.append(
            {
                "caption": text,
                "kind": requests[i][5],
                "C": _xy(C[i]),
                "H": _xy(H[i]),
                "moved_px": round(((C[i].x - H[i].x) ** 2 + (C[i].y - H[i].y) ** 2) ** 0.5, 1),
                "removed_by": removes + (["all three together"] if not removes and explained else []),
                "fix1_view_removes": _same(variants["view"][i], H[i]),
                "fix2_hand_sheet_takes_composer_subjects_removes": _same(H2[i], C[i]),
                "residual_cause": cause,
            }
        )
    out = {
        "captions": len(requests),
        "base_loop_reproduces_C": sum(_same(b, x) for b, x in zip(base, C, strict=True)),
        "disagreements": len(rows),
        "explained_by_the_three": sum(1 for r in rows if r["residual_cause"] is None),
        "by_source": {k: sum(1 for r in rows if k in r["removed_by"]) for k in ("view", "subject", "width")},
        "fix1_removes": sum(r["fix1_view_removes"] for r in rows),
        "fix2_removes": sum(r["fix2_hand_sheet_takes_composer_subjects_removes"] for r in rows),
        "rows": rows,
        "after_switch_apart": [requests[i][0] for i in range(len(requests)) if not _same(switch[i], H[i])],
        "after_switch_soft": [requests[i][0] for i in range(len(requests)) if switch[i].cost > 0],
    }
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    assert re.search(r"data-names", svg)
