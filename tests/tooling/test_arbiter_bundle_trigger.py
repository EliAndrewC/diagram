"""A made-up trigger gets a refusal naming the real form, not a bundle with no rounds in it (the round arbiter's fix on `round-3@449-T065-plan`)."""

from __future__ import annotations

import pytest

from tests.tooling.test_modal_checks import _load


def test_a_made_up_round_trigger_is_refused_with_the_real_form(capsys: pytest.CaptureFixture[str]) -> None:
    bundle = _load("arbiter_bundle")
    assert bundle.main(["round-3@449-T065-plan"]) == 2
    err = capsys.readouterr().err
    assert "round:spec-fidelity|plan:" in err and "make arbiter-ask" in err
