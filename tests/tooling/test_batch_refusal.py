"""`hm_checks.batch_refusal` (feature 385 T81, plan D101): a pop-up agent sent on one pop-up while `make record-owed` names it in a
batch of two or more for the same agent is refused, naming the batched command; no record, or a stale one, refuses nothing."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

from tests._scripts import script

pytestmark = pytest.mark.tooling
sys.path.insert(0, str(script("hm_checks.py").parent))
import hm_checks  # noqa: E402

ONE = "owed-checks: modal-form\nunit: modal-form:choice/split--0.6 abc\n"
TWO = ONE + "unit: modal-form:choice/split--0.4 def\n"


def test_a_single_pop_up_dispatch_is_refused_while_its_batch_is_owed(tmp_path: pathlib.Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    assert hm_checks.batch_refusal(tmp_path, "modal-form", ONE, 1000.0) == "", "no record: nothing refused"
    rec = tmp_path / ".git" / hm_checks.BATCHES
    rec.write_text(json.dumps({"utc": 1000.0, "batches": {"modal-form": ["choice/split--0.6", "choice/split--0.4"]}}))
    msg = hm_checks.batch_refusal(tmp_path, "modal-form", ONE, 1100.0)
    assert 'make modal-bundle KIND="choice/split--0.6 choice/split--0.4" FOR=modal-form' in msg
    assert hm_checks.escape_for(msg) == "BATCH_OK"
    assert hm_checks.batch_refusal(tmp_path, "modal-form", TWO, 1100.0) == "", "the batched bundle itself passes"
    assert hm_checks.batch_refusal(tmp_path, "modal-depiction", ONE.replace("modal-form", "modal-depiction"), 1100.0) == "", "another agent's"
    assert hm_checks.batch_refusal(tmp_path, "modal-form", ONE, 1000.0 + hm_checks.BATCHES_FRESH_S + 1) == "", "a stale record"
