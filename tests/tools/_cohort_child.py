"""A roll child's target for `test_cohort_audit.py` (feature 375 amendment 7): the engine's refusal raised inside a REAL
child process, through `cohort_roll.guarded` as the cohort's own target runs it - no hamlet rolled."""

from __future__ import annotations

from typing import Any

from l7r.diagram.tools import cohort_roll


class WebRefused(ValueError):
    """Stands for the engine's `...Refused` classes, importable by the parent under this module's name."""


def _refuse(arg: Any) -> Any:
    raise WebRefused(f"no lane reaches the well ({arg})")


def refuse(arg: Any) -> Any:
    return cohort_roll.guarded(_refuse, arg)
