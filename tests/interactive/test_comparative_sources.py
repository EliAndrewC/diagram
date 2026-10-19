"""Feature 391: a COMPARATIVE money source (kind `comparative`) is cited only by a comparative money question (subject
`comparative`), and its label reaches the built page.

The GM, 2026-10-18: such a source is useful "not because we will use it to establish the actual value of a koku", so the
build refuses it anywhere else, whether `comparative` is its first kind or a later one."""

from __future__ import annotations

import json
import pathlib

import pytest

from l7r.diagram.interactive.record import site
from l7r.diagram.interactive.record.store import RecordError
from l7r.diagram.interactive.sources import RESEARCH_DIR
from tests import _flat_record as fr

COMPARATIVE = {"id": "comparative", "name": "Comparative (money)", "description": "Another society's money, a yardstick only."}


def _record(tmp: pathlib.Path, kinds: str, question_subjects: str) -> pathlib.Path:
    """The small record with `alpha` tagged with `kinds` and 0001-lanes (which cites it) with `question_subjects`."""
    rec = fr.write(tmp)
    vocab = json.loads((rec / "source-tags.json").read_text(encoding="utf-8"))
    vocab["kind"].append(COMPARATIVE)
    (rec / "source-tags.json").write_text(json.dumps(vocab), encoding="utf-8")
    tags = json.loads((rec / "tags.json").read_text(encoding="utf-8"))
    tags["subject"]["comparative"] = {"name": "Comparative money", "description": "Another society's money."}
    (rec / "tags.json").write_text(json.dumps(tags), encoding="utf-8")
    fr.edit_entry(rec, "0010-alpha.html", "kind=primary", f"kind={kinds}")
    fr.edit(rec, "0001-lanes.html", "subject=ways", f"subject={question_subjects}")
    return rec


@pytest.mark.parametrize("kinds", ["comparative,primary", "primary,comparative"])
def test_a_comparative_source_outside_a_comparative_question_is_refused(tmp_path: pathlib.Path, kinds: str) -> None:
    with pytest.raises(RecordError) as e:
        site.build(str(_record(tmp_path, kinds, "ways")))
    assert "cites `alpha`, a comparative source - only a comparative money question (subject `comparative`) may cite it" in str(e.value)


def test_a_comparative_question_may_cite_it_and_its_label_shows(tmp_path: pathlib.Path) -> None:
    files = site.build(str(_record(tmp_path, "comparative,primary", "ways,comparative")))
    assert any("Comparative (money)" in text for text in files.values()), "the comparative label reaches a built page"


def test_the_real_record_carries_the_category() -> None:
    root = pathlib.Path(RESEARCH_DIR)
    kinds = {k["id"]: k for k in json.loads((root / "source-tags.json").read_text(encoding="utf-8"))["kind"]}
    assert "never sets a koku's value" in kinds["comparative"]["description"]
    assert "comparative" in json.loads((root / "tags.json").read_text(encoding="utf-8"))["subject"]
    sections = [s["id"] for s in json.loads((root / "source-sections.json").read_text(encoding="utf-8"))["sections"]]
    assert sections.index("works-comparative") < sections.index("works-beyond-east-asia"), "the first section that takes a work is its home"
