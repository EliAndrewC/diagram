"""Feature 375's replays of feature 372, kept as tests (SC-006).

SC-006: replaying 372's waves 106 and 108, the tripwires fire on 0105's and 0100's third rounds and on the bath bullet's
A -> B -> A. The rounds are replayed from 372's transcript by `make feature-report` (`m:sc006-replay`); the bath bullet is
replayed here from the page's own history, because it was never an Edit: a script added it at 14:13 UTC, a `git checkout`
withdrew it at 14:17, and a script put it back, re-worded, at 14:30 - so only the versions the checks were dispatched on show
it. The first version was never committed; it is rebuilt from the insertion the session's script made (quoted below from its
transcript, 8d3395e5).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tests.tooling.test_modal_checks import _load

hc = _load("hm_checks")
ru = _load("record_units")
REPO = Path(__file__).resolve().parents[2]
PAGE = "research/questions/0105-baths-furo.drawing.html"
#: the bullet the 14:13 script inserted after the `The bath is drawn 10 by 8 ft` item (transcript 8d3395e5, 2026-10-10T14:13:32Z)
BULLET = (
    "\n<li><strong>A plan may draw its bath larger as one of its resident's particulars - a GUESS.</strong><br>Where a plan's "
    "story gives its magistrate a fondness for the bath, the bath is drawn larger, up to about 18 by 12 ft, still on the "
    "house's service side; no page we read gives a bath's size to draw it from.</li>"
)


def _show(rev: str) -> str:
    r = subprocess.run(["git", "-C", str(REPO), "show", f"{rev}:{PAGE}"], capture_output=True, text=True, check=False)
    if r.returncode:
        pytest.skip(f"{rev} is not in this clone's history")
    return r.stdout


def _blocks(text: str) -> list[str]:
    return [b.words for b in ru.read_page(text).blocks]


def test_the_bath_bullet_s_return_trips_the_oscillation_wire() -> None:
    withdrawn = _show("b0eca1ebd")  # wave 108, 14:19 UTC: the bullet withdrawn
    i = withdrawn.index("The bath is drawn 10 by 8 ft")
    drafted = withdrawn[: withdrawn.index("</li>", i) + 5] + BULLET + withdrawn[withdrawn.index("</li>", i) + 5 :]
    readded = _show("175cca78a")  # wave 108, 14:32 UTC: the bullet back, re-worded
    versions = [_blocks(drafted), _blocks(withdrawn), _blocks(readded)]
    back = hc.oscillation(versions)
    assert back.startswith("A plan may draw its bath larger"), back
    assert hc.oscillation(versions[1:]) == "", "two versions are no oscillation"
    assert hc.oscillation([versions[1], versions[1], versions[2]]) == "", "added once, never dropped: no return"


def test_the_wire_reads_words_not_markup() -> None:
    a = ["the bath is drawn ten by eight feet on the service side"]
    b: list[str] = []
    assert hc.oscillation([a, b, ["The bath is drawn ten by eight feet, on the service side, near the well."]])
    assert not hc.oscillation([a, b, ["a well stands by the kitchen door in the yard"]])
    assert not hc.oscillation([["short"], [], ["short"]]), "a block of a few words is no evidence"
