"""Feature 297, FR-005 (research R11): a later settle round runs only the repairs the law names broken."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from l7r.diagram.hamletgen.ways import settle


def test_a_broken_rule_selects_its_steps_and_the_unmapped_ones_and_an_unmapped_rule_selects_every_step() -> None:
    picked = {st.__name__ for st in settle.steps_for({"width_steps": [1]})}
    assert "settle_widths" in picked and "settle_shapes" not in picked
    assert {"settle_reach", "settle_shadows", "settle_defer", "prune_the_tree"} <= picked, "a step no rule maps is asked every round"
    assert settle.steps_for({"a rule no step mends": 1}) == settle.STEPS
    assert settle.steps_for({}) == tuple(st for st in settle.STEPS if st.__name__ not in settle.STEP_RULES)


def test_a_later_round_runs_only_the_steps_for_what_is_still_broken(monkeypatch: pytest.MonkeyPatch) -> None:
    ran: list[list[str]] = []

    def step(name: str, edits: list[int]):  # each call returns its next edit count
        def run(s):  # type: ignore[no-untyped-def]
            ran[-1].append(name)
            return edits.pop(0) if edits else 0

        run.__name__ = name
        return run

    steps = (step("settle_shapes", [1, 0]), step("settle_widths", [0, 1, 0]), step("settle_shadows", []))
    monkeypatch.setattr(settle, "STEPS", steps)
    answers = [{"width_steps": [1]}, {}]
    monkeypatch.setattr(settle, "unsettled", lambda M, ground=None: answers.pop(0))
    monkeypatch.setattr(settle, "memo_ground", lambda s, k, f: None)
    monkeypatch.setattr(settle, "unreached_houses", lambda M: [])
    monkeypatch.setattr(settle.law, "unreached_targets", lambda M: [])
    monkeypatch.setattr(settle.law, "field_unreached", lambda M: False)
    import l7r.diagram.hamletgen.ways.last_resort as lr

    monkeypatch.setattr(lr, "refuse_unreached", lambda M: None)
    ran.append([])
    got = settle.settle_the_web(SimpleNamespace(M={"lanes": []}))
    assert got["rounds"] == 2 and got["dropped"] == 0
    flat = ran[0]
    assert flat[:3] == ["settle_shapes", "settle_widths", "settle_shadows"], "the first round: every step"
    assert flat[3:] == ["settle_widths", "settle_shadows"], "the second: the width rule's step and the unmapped one"
