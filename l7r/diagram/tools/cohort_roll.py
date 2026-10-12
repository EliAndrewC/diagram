"""The cohort's roll as the roll child runs it, and the engine's refusal as a payload (feature 375 amendment 6, FR-028).

WHY ITS OWN MODULE. `make cohort` runs `cohort_audit` with `python3 -m`, so there it is `__main__`, and in a process pool's
worker it is `__mp_main__`; a `Refusal` class defined there is a different class object from the one the roll child
unpickles (it imports by the module's real name), and a child target named from `__name__` (`__mp_main__:...`) cannot be
imported by the child at all - every seed came back `refused:RuntimeError` and nothing was stored (the plan review, round 2,
measured both on Python 3.14). Here, imported by name everywhere, the parent, every pool worker and the child share one class
and one target.
"""

from __future__ import annotations

import dataclasses
import importlib
from collections.abc import Callable
from typing import Any

#: The roll child's target for the cohort's roll: `module:function`, importable in any process.
ROLL_TARGET = "l7r.diagram.tools.cohort_roll:roll_or_refusal"


@dataclasses.dataclass(frozen=True)
class Refusal:
    """A roll the engine REFUSED by name - its class and message - as a payload: it crosses the roll child (which turns a
    raised failure into one generic error) and is stored like a report, since the same spec on the same code refuses the
    same way. A crash (the child dies, memory, a timeout) is no refusal: it still raises, and is never stored."""

    module: str
    name: str
    message: str

    def exception(self) -> Exception:
        """The refusal as its own class where it can be imported, so `refused_verdict` names it as before."""
        try:
            cls = getattr(importlib.import_module(self.module), self.name)
            if isinstance(cls, type) and issubclass(cls, Exception):
                return cls(self.message)
        except Exception:  # noqa: BLE001, S110 - an unimportable class is named below all the same
            pass
        return type(self.name, (RuntimeError,), {})(self.message)


def guarded(roll: Callable[[Any], Any], arg: Any) -> Any:
    """`roll(arg)`, or the engine's refusal - a ValueError or RuntimeError, the classes every `...Refused` derives from - as
    a `Refusal`. Anything else raises."""
    try:
        return roll(arg)
    except (ValueError, RuntimeError) as e:
        return Refusal(type(e).__module__, type(e).__name__, str(e))


def roll_or_refusal(hspec: Any) -> Any:
    """THE COHORT'S ROLL, run in the roll child by name: `rollcache._roll_payload` (generate, as the gate rolls it), or the
    engine's refusal as a `Refusal`."""
    from l7r.diagram.pipeline import rollcache  # noqa: PLC0415 - the engine's serving layer, imported where it is used

    return guarded(rollcache._roll_payload, hspec)  # noqa: SLF001 - the gate's own roll, called by name as its child does
