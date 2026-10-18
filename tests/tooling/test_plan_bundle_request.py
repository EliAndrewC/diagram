"""Feature 383 amendment 8 (FR-047, SC-035): a plan-review bundle carries the GM's words from the amendment its blocks answer on.

A whole copy of `request.md` grew with every amendment (383's reached ~20k characters) and was read by every plan review. These
prove the trim keeps what a fidelity review needs: the original request always, the amendment under review and every later one
(a later amendment can change what an earlier one asked), the whole request for a block of the original plan or a request with
no amendments, and an index of what was left out.
"""

from __future__ import annotations

import importlib.util
import sys

from tests._scripts import script, script_dir

sys.path.insert(0, script_dir("plan_gate"))
_spec = importlib.util.spec_from_file_location("_plan_bundle_request", script("plan_bundle"))
assert _spec and _spec.loader
pb = importlib.util.module_from_spec(_spec)
sys.modules["_plan_bundle_request"] = pb
_spec.loader.exec_module(pb)

REQUEST = """# Feature 900 - the GM's request

> the original words

## Amendment 1 (2026-10-01)

The first change.

> one

### Amendment 1, extended

> one more

## Amendment 2 (2026-10-02)

The second change.

> two

## Amendment 3 (2026-10-03)

> three
"""
SPEC = """## Requirements

- **FR-001 The original.** x

### Amendment 1 - first (`request.md`, Amendment 1)

- **FR-002 One.** y

### Amendment 2 - second

- **FR-003 Two.** z
- **SC-009** (FR-003) measured

## Success criteria
"""


def test_the_newest_amendment_carries_the_original_and_itself() -> None:
    n = pb.answered([("## Amendment 3 (FR-004)", "## Amendment 3 (FR-004)\n\n**D9 - x.**")], SPEC)
    req, index = pb.trimmed_request(REQUEST, n)
    assert n == 3 and "> the original words" in req and "> three" in req
    assert "> one" not in req and "> two" not in req
    assert "## Amendment 1 (2026-10-01) - The first change." in index and "## Amendment 2 (2026-10-02) - The second change." in index


def test_an_earlier_amendment_carries_every_later_one() -> None:
    n = pb.answered([("plan block", "**D4 - the wave (FR-003, SC-009).** text")], SPEC)
    req, index = pb.trimmed_request(REQUEST, n)
    assert n == 2 and "> two" in req and "> three" in req and "> one" not in req
    assert "### Amendment 1, extended" not in req, "a ### under an earlier amendment goes with it"
    assert index.count("## Amendment") == 1


def test_a_later_amendment_correcting_an_earlier_requirement_carries_the_earlier_words() -> None:
    n = pb.answered([("## Amendment 3, reopened (FR-002 corrected)", "## Amendment 3, reopened (FR-002 corrected)\n\n**D9 - x.**")], SPEC)
    req, _index = pb.trimmed_request(REQUEST, n)
    assert n == 1 and "> one" in req and "> three" in req, "FR-002 is amendment 1's: its words come with the block"
    assert _index == "", "nothing before amendment 1 is left out but the original request, which is always carried"


def test_the_earliest_of_several_blocks_wins() -> None:
    n = pb.answered([("## Amendment 3", "x"), ("## Amendment 1, reopened", "y")], SPEC)
    assert n == 1 and "> one more" in pb.trimmed_request(REQUEST, n)[0]


def test_a_block_of_the_original_plan_and_a_request_with_no_amendments_get_it_whole() -> None:
    assert pb.answered([("## Decisions", "**D1 - the original (FR-001).**")], SPEC) is None
    assert pb.answered([("## Amendment 2", "x"), ("## Phases", "nothing cited")], SPEC) is None, "one original block: whole"
    assert pb.trimmed_request(REQUEST, None) == (REQUEST, "")
    plain = "# Feature 901\n\n> just the words\n"
    assert pb.trimmed_request(plain, 2) == (plain, "")
    assert pb.request_sections(plain) == (plain, [])


def test_spec_amendments_map_each_id_to_its_section() -> None:
    assert pb.spec_amendments(SPEC) == {"FR-002": 1, "FR-003": 2, "SC-009": 2}
