"""`make placement-stages` - the stage-by-stage walk-through page is written from `NOTES` (feature 176).

The GM, 2026-09-02: *"I think the hamlet placement order HTML file is outdated. For example, it does not
mention anything about adding labels being its own final step."* It did not because `stage_labels` had
no `NOTES` entry, and the page rendered "(no note yet)" for it - and for two other stages - with nothing
red. A stage added to `STAGES` without a note is a page that has gone stale the moment it is re-plated,
so the roster of notes is held to the roster of stages in both directions.
"""

from l7r.diagram.hamletgen.driver import STAGES
from l7r.diagram.tools.placement_stages import NOTES


def test_every_stage_has_a_note():
    missing = [stage.__name__ for stage in STAGES if stage.__name__ not in NOTES]
    assert missing == [], f"stages the placement page would render as '(no note yet)': {missing}"


def test_every_note_names_a_stage():
    stages = {stage.__name__ for stage in STAGES}
    orphans = sorted(set(NOTES) - stages)
    assert orphans == [], f"notes for stages that no longer exist: {orphans}"


def test_every_note_has_a_title_and_a_why():
    for name, (title, why) in NOTES.items():
        assert title.strip() and why.strip(), name
        assert "(no note yet)" not in title, name
