"""`l7r/diagram/tools/cohort_roll.py` - the cohort's roll as its child runs it, and the engine's refusal as a payload (feature 375
amendment 7, FR-029). Plain inputs, no roll and no child: the quick tier's unit tests (the real child and the module-name
cases are `test_cohort_audit.py`'s, under the tooling marker)."""

from __future__ import annotations

from typing import Any

import pytest

from l7r.diagram.tools import cohort_roll as cr


class _WebRefused(ValueError):
    pass


def _refuse(arg: Any) -> Any:
    raise _WebRefused(f"no lane reaches the well ({arg})")


def test_guarded_turns_the_engines_refusal_into_a_payload_and_lets_a_crash_raise() -> None:
    assert cr.guarded(lambda a: ("plan", "manifest", a), "rep") == ("plan", "manifest", "rep")
    r = cr.guarded(_refuse, "seed 3")
    assert r == cr.Refusal(__name__, "_WebRefused", "no lane reaches the well (seed 3)")
    assert isinstance(cr.guarded(lambda a: (_ for _ in ()).throw(RuntimeError("stuck")), None), cr.Refusal), "RuntimeError too"

    def crash(a: Any) -> Any:
        raise MemoryError(a)

    with pytest.raises(MemoryError):
        cr.guarded(crash, "out of memory")


def test_a_refusal_is_its_own_class_where_that_imports_and_a_named_runtime_error_where_not() -> None:
    e = cr.Refusal(__name__, "_WebRefused", "x").exception()
    assert type(e) is _WebRefused and str(e) == "x"
    assert type(cr.Refusal("builtins", "ValueError", "y").exception()) is ValueError
    gone = cr.Refusal("no.such.module", "SiteRefused", "z").exception()
    assert type(gone).__name__ == "SiteRefused" and isinstance(gone, RuntimeError) and str(gone) == "z"
    not_a_class = cr.Refusal(__name__, "ROLL", "w").exception()
    assert type(not_a_class).__name__ == "ROLL" and isinstance(not_a_class, RuntimeError)


ROLL = "not an exception class"


def test_the_cohorts_roll_is_the_gates_roll_named_for_the_child(monkeypatch: pytest.MonkeyPatch) -> None:
    from l7r.diagram.pipeline import rollcache

    monkeypatch.setattr(rollcache, "_roll_payload", lambda spec: ("plan", "manifest", spec))
    assert cr.roll_or_refusal("spec") == ("plan", "manifest", "spec")
    monkeypatch.setattr(rollcache, "_roll_payload", _refuse)
    assert cr.roll_or_refusal("spec").name == "_WebRefused"
    mod, fn = cr.ROLL_TARGET.rsplit(":", 1)
    assert mod == cr.__name__ and getattr(cr, fn) is cr.roll_or_refusal, "the child imports the target by name"
