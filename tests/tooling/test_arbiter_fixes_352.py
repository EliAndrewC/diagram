"""The round arbiter's two tooling fixes on feature 352 (2026-10-11), each on the case it ruled on.

- `round:quote-check|q:0036@3`: feature 368's q:0047 triggers, left in the clone's one owed file, were swept into 352's
  batch; and source-reader was owed again on a READ note whose English alone changed.
- `round:modal-depiction|modal:choice/copse_siting--among_the_houses@3`: the batch let a session name seven modal-form units
  `@3` that had run once, and the REVERSING mark fell on three pure additions.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from tests.tooling.test_modal_checks import _load
from tests.tooling.test_record_owed import ro, ru

ha = _load("hm_arbiter")
ab = _load("arbiter_bundle")


def _clone(tmp: pathlib.Path, feature: str) -> pathlib.Path:
    (tmp / ".git").mkdir(exist_ok=True)
    (tmp / ".specify").mkdir(exist_ok=True)
    (tmp / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": f"specs/{feature}"}))
    return tmp


def test_a_trigger_another_feature_fired_is_not_this_feature_s(tmp_path: pathlib.Path) -> None:
    root = _clone(tmp_path, "368-x")
    ha.trip(root, "round:quote-check|q:0047@3", "round", "quote-check|q:0047", "d", 1)
    assert ha.owed(root)["round:quote-check|q:0047@3"]["feature"] == "368-x"
    _clone(tmp_path, "352-y")
    ha.trip(root, "round:quote-check|q:0036@3", "round", "quote-check|q:0036", "d", 2)
    assert ha.batch_triggers(root) == ["round:quote-check|q:0036@3"], "368's trigger stays out of 352's batch"
    assert ha.blocking(root, "quote-check|q:0047") == [], "nor does it hold 352's dispatches"
    assert ha.aside(root) == ["round:quote-check|q:0047@3 (feature 368-x)"], "it is named, not lost"
    legacy = json.loads((root / ".git" / "arbiter-owed.json").read_text())
    legacy["round:x|q:0001@3"] = {"kind": "round", "unit": "x|q:0001"}
    (root / ".git" / "arbiter-owed.json").write_text(json.dumps(legacy))
    assert "round:x|q:0001@3" in ha.batch_triggers(root), "a trigger recorded before triggers named a feature is everyone's"


def test_a_named_round_must_be_its_unit_s_next(tmp_path: pathlib.Path) -> None:
    root = _clone(tmp_path, "352-y")
    state = {"feature": "352-y", "rounds": {"modal-form|modal:hamlet/copse": 1, "quote-check|q:0036": 2}}
    (root / ".git" / "checks-open.json").write_text(json.dumps(state))
    wrong = ab.misnumbered(root, ["round:modal-form|modal:hamlet/copse@3", "round:quote-check|q:0036@3", "ask:x"])
    assert len(wrong) == 1 and "`round:modal-form|modal:hamlet/copse@2`" in wrong[0], wrong
    with pytest.raises(ValueError, match="not its unit's next"):
        ab.batch(root, tmp_path / "out", extra=("round:modal-form|modal:hamlet/copse@3",))
    assert ab.counted(root, "quote-check|q:0036") == 2
    _clone(tmp_path, "353-z")
    assert ab.counted(root, "quote-check|q:0036") == 0, "another feature's counts are not this one's"
    ha.trip(root, "round:modal-form|modal:hamlet/copse@3", "round", "modal-form|modal:hamlet/copse", "d", 1)
    assert ab.misnumbered(root, ["round:modal-form|modal:hamlet/copse@3"]) == [], "a trigger the counter fired is its own"
    assert ab.main(["round:quote-check|q:0036@5", "--root", str(root)]) == 2


def test_a_pure_addition_reverses_only_a_phrase_an_earlier_edit_took_out() -> None:
    # copse_siting's depiction round 1 (352), as the bundle had it: three additions, each marked REVERSING by loose words it
    # shared with another check's cut of the fengshui-woods sentence or of "trees in the gaps between the farms"
    fengshui = ("leaves for the hearth and for manure. In southern China villagers planted fruit trees and bamboo for their use in their fengshui woods.", "leaves for the hearth and for manure.")
    gaps = ("trees in the gaps between the farms, the dooryard copse. A Japanese homestead's wood was its own", "dooryard copse. A Japanese homestead's wood was its own")
    earlier = [fengshui, gaps]
    added = [
        (
            "its households' woods.",
            "its households' woods. The copse is drawn with fruit and other broadleaf trees only: bamboo grew round the houses too, but the map draws a farm's bamboo as a stand of its own.",
        ),
        ("and off the main road.", "and off the lanes and the main road, so no lane runs between a farm and its own trees."),
        (
            "research/questions/0075-bamboo-groves-chikurin.drawing.html",
            "research/questions/0075-bamboo-groves-chikurin.drawing.html, research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html",
        ),
    ]
    for o, n in added:
        assert not ab._near_reversal(o, n, earlier), n
    earlier = [("the copse stands among the houses beside lanes and the main road", "the copse stands among the houses")]
    assert ab._near_reversal("the copse stands.", "the copse stands. It stands among the houses beside lanes and the main road.", earlier)
    assert ab._insertion("", "x") is None and ab._insertion("a b", "a c") is None and ab._insertion("a b", "a x b") == "x"
    assert ab._near_reversal("drawn with stones", "drawn with gravel paths", [("gravel paths and grove stones", "moss")]), "a rewording still counts"


NOTES = (
    '<ol>\n<li data-note="otsubo"><a href="http://m-sugi.com/o.htm"><code>otsubo</code></a> - 「The approach was a gap at one '
    'corner.」 (translated; <span class="orig" data-orig="otsubo#1"></span>)</li>\n'
    '<li data-note="isa"><a href="https://auf.example/19"><code>isa</code></a> - "Tree lines surround each house." / '
    '"The road is orderly."</li>\n</ol>\n'
)
ORIGS = '<ol>\n<li data-orig="otsubo#1">屋敷林の一角を開けたアプローチ</li>\n</ol>\n'


def test_source_reader_reads_the_pages_and_passages_not_the_english() -> None:
    def rec(notes: str, origs: str = ORIGS) -> ru.Record:
        return ru.Record.of({"0036-groves.html": "<h2>g</h2>", "0036-groves.notes.html": notes, "0036-groves.originals.html": origs}, {})

    base = rec(NOTES)
    english = rec(NOTES.replace("at one corner", "in one part").replace('" / "', '"; "'))
    for k in ("otsubo", "isa"):
        assert english.readings["0036"][k] == base.readings["0036"][k], f"{k}: the English or the separator alone"
    assert rec(NOTES, ORIGS.replace("一角", "二角")).readings["0036"]["otsubo"] != base.readings["0036"]["otsubo"], "the original"
    assert rec(NOTES.replace("orderly", "straight")).readings["0036"]["isa"] != base.readings["0036"]["isa"], "a quoted passage"
    assert rec(NOTES.replace("auf.example/19", "auf.example/20")).readings["0036"]["isa"] != base.readings["0036"]["isa"], "its page"
    assert ru.reading("<a href='x'>no passage</a>", {}) == ""
    units = {u.slug: u for u in ru.owed(english, ru.Record({}, {}, {}, {}))}
    assert units["source-reader:0036#otsubo"].reading == base.readings["0036"]["otsubo"]
    assert units["quote-check:0036#otsubo"].reading == "", "the reading is source-reader's alone"


def test_a_read_note_reworded_in_english_stays_answered(tmp_path: pathlib.Path) -> None:
    slug = "source-reader:0036#otsubo"
    ro.write_answer(tmp_path, slug, "fp-old", "READ")
    ro.keep_reading(tmp_path, slug, "rd")
    ro.keep_reading(tmp_path, slug, "rd")
    ro.keep_reading(tmp_path, "source-reader:0036#none", "rd")
    assert json.loads(ro._file(tmp_path, slug).read_text())["readings"] == ["rd"]
    assert not (tmp_path / ro._file(tmp_path, "source-reader:0036#none").name).exists(), "no answer, no reading kept"
    assert ro.answered(tmp_path, slug, "fp-new", "rd"), "the same pages and passages"
    assert not ro.answered(tmp_path, slug, "fp-new", "other") and not ro.answered(tmp_path, slug, "fp-new")


def test_an_asks_cited_files_are_copied_beside_its_manifest(tmp_path: pathlib.Path) -> None:
    """The round arbiter's tooling fix (feature 374 wave 149, ask:b13-w149-strip-route): the files a question cites - roll
    summaries, probe output, refusal logs - are copied into `evidence/` beside the MANIFEST and named, a missing one named as
    missing, so every figure can be checked without leaving the bundle."""
    out = tmp_path / "bundle"
    out.mkdir()
    a, b = tmp_path / "x" / "rolls.txt", tmp_path / "y" / "rolls.txt"
    a.parent.mkdir()
    b.parent.mkdir()
    a.write_text("v-18 exit=2\n")
    b.write_text("v-18 exit=0\n")
    lines = ab.evidence_section(out, [str(a), str(b), str(tmp_path / "gone.txt")])
    assert (out / "evidence" / "rolls.txt").read_text() == "v-18 exit=2\n" and (out / "evidence" / "rolls-2.txt").read_text() == "v-18 exit=0\n"
    assert "`evidence/rolls.txt`" in lines[0] and "`evidence/rolls-2.txt`" in lines[0] and "MISSING: `" in lines[0]
    assert ab.evidence_section(out, []) == [], "no files cited, no section"
