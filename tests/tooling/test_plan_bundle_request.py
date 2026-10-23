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


def test_a_requirement_written_as_a_heading_is_cited_whole() -> None:
    """The older specs write a requirement as its own heading (`### FR-006 - ...`, feature 170's among them); the bundle's
    `spec-cited.md` came out empty for a plan citing one, so its reviewer judged FR-006 without its text (170 amendment 1)."""
    spec = "## Requirements\n\n### FR-006 - the reason outside the file\n\nThe body.\n\n- (c) a clause\n\n### FR-007 - next\n\nx\n\n- **SC-008** (FR-006): done.\n"
    got = pb.requirements(spec)
    assert got["FR-006"] == "### FR-006 - the reason outside the file\n\nThe body.\n\n- (c) a clause\n"
    assert got["SC-008"] == "- **SC-008** (FR-006): done.\n" and set(got) == {"FR-006", "FR-007", "SC-008"}


def test_a_list_of_this_features_ids_is_not_read_as_another_features() -> None:
    """Feature 407's plan reviews got an empty spec-cited.md: in "(FR-001, FR-002)" the qualified-id pattern read "001" inside
    FR-001 as a feature number and dropped ", FR-002" as that feature's id, which broke FR-001 too."""
    body = "## D1 - the rule (FR-001, FR-002)\n\nfeature 383 FR-043 is another feature's.\n"
    kept = pb._QUALIFIED.sub(lambda q: "" if q.group(1) != "407" else q.group(2), body)
    assert [m.group(1) for m in pb._IDS.finditer(kept)] == ["D1", "FR-001", "FR-002"]


def test_a_feature_with_no_request_md_gets_no_bundle(tmp_path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 405 T30 (D2): 405's first plan review ran on a bundle naming request.md where the feature had none, and returned
    no verdict. The build refuses before writing anything, naming the file to write."""
    import pytest  # noqa: PLC0415

    d = tmp_path / "specs" / "905-x"
    d.mkdir(parents=True)
    (d / "spec.md").write_text("# Feature 905\n", encoding="utf-8")
    monkeypatch.setattr(pb, "OUT", tmp_path / "out")
    with pytest.raises(SystemExit) as e:
        pb.build(d, "T01", [("T01", "## T01 - x\n")], {}, "task")
    assert "specs/905-x/request.md is missing" in str(e.value) and "verbatim" in str(e.value)
    assert not (tmp_path / "out").exists(), "nothing is written for a bundle that cannot be reviewed"


def test_every_written_form_of_a_decision_is_read() -> None:
    """405 T133: the plans write a decision five ways, and the bundle read only `**D83 - `, so amendment 10's review got an
    empty spec-cited.md for blocks citing D121 (written `- **D121**`). Each form below is a real occurrence's shape."""
    plan = (
        "**D83 - a knot gathered.** body\n\n- **D96 - the tread off a wall.** body\n\n- **D121** The rows released.\n\n"
        "- **D7 The placed-house index**: body\n\n**D8.** `make hooks-test` body\n\n**Dx** not one\n"
    )
    got = pb._paragraphs(plan, pb._DECISION)
    assert sorted(got) == ["D121", "D7", "D8", "D83", "D96"]
    assert got["D121"] == "- **D121** The rows released.\n"
