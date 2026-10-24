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
    # ...and quote-check's is its own, the note and its claim sentences (feature 395, ask:395-round3-all), never source-reader's
    assert units["quote-check:0036#otsubo"].reading not in ("", units["source-reader:0036#otsubo"].reading)


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


def test_a_route_question_must_state_the_pool(tmp_path: pathlib.Path) -> None:
    """The round arbiter's tooling fix (feature 374 wave 149, ask:b13-w149-route-matrix): a question offering routes, or about a
    regression, states each route's pool result - an accept taken on the cohort and the 44 rolls alone was overturned when the
    pool then refused the reference map. Other questions pass untouched."""
    a, b = tmp_path / "routeA.txt", tmp_path / "routeB.txt"
    a.write_text("pool: Inashiro refused; cohort 16/16\n")
    b.write_text("cohort seed 7 fails\n")
    assert ab.pool_unstated("may the cap be raised?", []) == []
    assert ab.pool_unstated("which route lands seed 49?", [])[0].startswith("the question names a route")
    assert ab.pool_unstated("which route lands seed 49?", [str(a)]) == []
    assert ab.pool_unstated("which route lands the map? A or B", [str(a), str(b)]) == [f"{b}: a route's evidence states no pool result"]
    # "route" in its process sense, no map named: no pool owed (the round arbiter's tooling fix, ask:t14-plan-round4)
    assert ab.pool_unstated("tooling only: does the process route differently after a third plan round?", []) == []
    assert ab.main(["--check-ask", "a regression on seed 10: waive it?"]) == 2
    assert ab.main(["--check-ask", "a regression on seed 10, the pool clean: waive it?"]) == 0


def test_an_ask_about_a_plan_review_carries_its_rounds_and_the_plan_s_diffs(tmp_path: pathlib.Path) -> None:
    """The round arbiter's tooling fix on ask:t14-plan-round4: the ask's bundle held none of T14's three plan rounds, so "each
    fixed as written" was ruled on the session's account. An ask naming a plan review now carries every recorded round of the
    newest round's blocks - its verdict and each decision not ruled within - and the plan's history as `edits.diff`."""
    import subprocess

    root = _clone(tmp_path, "385-x")
    d = root / "specs" / "385-x"
    d.mkdir(parents=True)
    (d / "plan.md").write_text("# plan\n")
    rounds = [
        {"reviewed": "r0", "blocks": ["### T01 Decisions"], "verdict": "CLEAR", "decisions": []},
        {
            "reviewed": "r1",
            "blocks": ["### T14 Decisions"],
            "verdict": "BLOCKED",
            "decisions": [{"id": "D30", "class": "narrowing, NOT LEGITIMATE", "summary": "the window dropped", "why": "the GM named it"}],
        },
        {"reviewed": "r2", "blocks": ["### T14 Decisions", "## Landing"], "verdict": "BLOCKED", "decisions": [{"id": "D31", "class": "within"}]},
    ]
    (d / "plan-review.json").write_text(json.dumps({"block_reviews": rounds}))
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    ha.trip(root, "ask:t14-plan-round4", "ask", "", "T14's plan review has run three rounds: may a fourth run?")
    text = ab.bundle(root, "ask:t14-plan-round4", tmp_path / "out").read_text()
    assert "## The plan review's rounds" in text and "### Round 1: BLOCKED (r1)" in text and "### Round 2: BLOCKED (r2)" in text
    assert "D30 - narrowing, NOT LEGITIMATE: the window dropped the GM named it" in text and "- every decision within" in text
    assert "(r0)" not in text, "another block's rounds are not this review's"
    assert (tmp_path / "out" / "edits.diff").is_file() and "specs/385-x/plan.md" in text
    assert ab.plan_rounds(tmp_path)[0] == ["## The plan review's rounds\n\n- (none recorded in plan-review.json)\n"]


def test_a_plan_round_trigger_s_bundle_carries_the_plan_s_rounds(tmp_path: pathlib.Path) -> None:
    """The round arbiter's tooling fix on round:spec-fidelity|plan:385-approach-checklist#T17@3: the plan-round cap's bundle (T16)
    pointed at spec.md's Review history, which holds no plan rounds - the arbiter ruled with no verdicts and a counter of 0 of 0."""
    import subprocess

    root = _clone(tmp_path, "385-x")
    d = root / "specs" / "385-x"
    d.mkdir(parents=True)
    (d / "plan.md").write_text("# plan\n")
    rounds = [
        {"reviewed": "r1", "blocks": ["### T17 Decisions"], "verdict": "BLOCKED", "decisions": [{"id": "D39", "class": "narrowing, NOT LEGITIMATE", "summary": "two steps", "why": "all three"}]},
        {"reviewed": "r2", "blocks": ["### T17 Decisions"], "verdict": "BLOCKED", "decisions": []},
    ]
    (d / "plan-review.json").write_text(json.dumps({"block_reviews": rounds}))
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    trig = "round:spec-fidelity|plan:385-x#T17@3"
    ha.trip(root, trig, "round", "spec-fidelity|plan:385-x#T17", "round 3 of T17's plan review")
    text = ab.bundle(root, trig, tmp_path / "out", allow_missing="a fixture").read_text()
    assert "### Round 1: BLOCKED (r1)" in text and "D39 - narrowing, NOT LEGITIMATE: two steps all three" in text
    assert "spec.md`'s Review history" not in text, "a plan round is not the spec's"


def test_an_asks_bundle_carries_the_claims_on_the_numbers_it_names() -> None:
    """Feature 385 T28 (the round arbiter's tooling fix on ask:t06-scattered-single-file): whether the field's size and the
    farmstead pitch were researched decided the route, and the bundle held only the session's word for it."""
    root = pathlib.Path(__file__).resolve().parents[2]
    out = "\n".join(ab.claims_section(root, ["the area is researched (`GROSS_ACRES_PER_HOUSEHOLD`, 0017), and BUNDLE_PITCH"]))
    assert "consts.py::GROSS_ACRES_PER_HOUSEHOLD#paddy per household` - a research page" in out
    assert "consts.py::BUNDLE_PITCH#" in out and "(last verdict " in out
    assert ab.claims_section(root, ["nothing named here"]) == []
    assert ab.claims_section(root, ["`NO_SUCH_NAME_ANYWHERE`"]) == []
    # the ruled ask's own words (ask:t06-scattered-single-file): the field's size and the pitch, given only as numbers
    words = "\n".join(ab.claims_section(root, ["The ruling's first lever, the field's size, is researched (0017's 1.3 acres a household); the farmstead pitch 273 ft"]))
    assert "- `1.3 acres`: `l7r/diagram/hamletgen/consts.py::GROSS_ACRES_PER_HOUSEHOLD#paddy per household` - a research page" in words, words
    assert "- `273 ft`: no claim states it" in words, "a value no claim states is said to be one, never left out"


def test_a_spec_round_trigger_s_bundle_carries_each_round_s_reply_with_its_findings_marked(tmp_path: pathlib.Path) -> None:
    """The round arbiter's tooling fix on round:spec-fidelity|387-scale-the-placement-loops#1@6: the spec-round cap's bundle
    pointed at the session's own Review history and held no reviewer verdict, so reversals and duplicate dispatches had to be
    inferred. Each spec review dispatch's reply is now beside the MANIFEST, its findings marked; a plan review is not a round."""
    subs = tmp_path / "transcripts" / "-proj" / "sess" / "subagents"
    subs.mkdir(parents=True)

    def agent(n: int, prompt: str, reply: str | None) -> None:
        recs = [{"message": {"role": "user", "content": prompt}}]
        if reply is not None:
            recs.append({"message": {"role": "assistant", "content": [{"type": "text", "text": reply}]}})
        f = subs / f"agent-a{n}.jsonl"
        f.write_text("\n".join(json.dumps(r) for r in recs) + "\n")
        import os

        os.utime(f, (1000 + n, 1000 + n))

    agent(1, "MODE 2: SPECIFICATION REVIEW of feature 9. Spec: /x/specs/9-x/spec.md", "**Verdict: CHANGES REQUIRED**\n\n1. FR-002's premise is wrong: the rounds do not grow.\n")
    agent(2, "MODE 4: PLAN REVIEW of 3 changed block(s) of specs/9-x", "Verdict: BLOCKED\n\n1. D1 narrows.\n")
    agent(3, "MODE 3 (VERIFY) - round 2 of specs/9-x", "Verdict: CHANGES REQUIRED\n\n1. FR-002's premise is wrong: the rounds do not grow.\n")
    agent(4, "MODE 2: SPECIFICATION REVIEW of specs/9-x", None)
    agent(5, "MODE 2: SPECIFICATION REVIEW of specs/10-other", "Verdict: FAITHFUL\n")
    out = tmp_path / "out"
    out.mkdir()
    text = "".join(ab.spec_rounds(out, "9-x", tmp_path / "transcripts"))
    r1, r2 = text.split("### Round 2")[0], text.split("### Round 2")[1].split("### Round 3")[0]
    assert "### Round 1: spec-fidelity (CHANGES REQUIRED)" in r1 and "- NEW: " in r1 and "FR-002's premise is wrong" in r1
    assert ": spec-fidelity (CHANGES REQUIRED)" in r2 and "- REPEATED: " in r2 and "FR-002's premise is wrong" in r2, "the plan review is no round"
    assert "### Round 3: spec-fidelity (no reply (stopped))" in text and "Round 4" not in text, "another feature's review is not this one's"
    assert (out / "round-1-spec-fidelity.md").read_text().startswith("**Verdict: CHANGES REQUIRED**")
    assert ab.spec_rounds(out, "11-none", tmp_path / "transcripts") == ["- (no spec review dispatch found in the subagent transcripts - read the Review history)\n"]


def test_an_ask_naming_a_fit_failure_carries_the_room_table(tmp_path: pathlib.Path) -> None:
    """405 T113 (the round arbiter's tooling_fix on ask:set-down-T26): the arbiter ruled on "room fails" without the table that
    says which knobs grow the seating band; an ask naming a knot, a refusal or room now carries it, and one that does not, not."""
    import subprocess

    root = _clone(tmp_path, "385-x")
    (root / "specs" / "385-x").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    ha.trip(root, "ask:t26-seeds", "ask", "", "T26 resisted: seeds 10 and 36 newly fail on lane_knots; set it down?")
    text = ab.bundle(root, "ask:t26-seeds", tmp_path / "out").read_text()
    assert "## The room table (405 T113)" in text and "| `SEATING_GROUND_FT`" in text
    ha.trip(root, "ask:t27-wording", "ask", "", "May the modal's About tab keep its second paragraph?")
    assert "room table" not in ab.bundle(root, "ask:t27-wording", tmp_path / "out2").read_text()


def test_a_ruling_is_recorded_in_the_house_style() -> None:
    """The GM 2026-10-24 (405 T26): a ruling wrote a British spelling into arbiter.jsonl and gm-review.jsonl, and the gate's preflight
    refused the landing on it; the recorder americanizes a ruling's text, every field, before it is written."""
    british = {"why": "the step label" + "led UNRESEARCHED", "what": ["a col" + "our"]}  # built, so the house-style check reads no word
    got = ha.house_styled({"ruling": "accept", **british, "n": 3})
    assert got == {"ruling": "accept", "why": "the step labeled UNRESEARCHED", "what": ["a color"], "n": 3}


def test_an_accept_on_claims_is_recorded_as_their_verdict(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """The GM 2026-10-24 (405 T26): the claims gate refused a claim the round arbiter had accepted with no third round, at the
    landing and again at the stop-work push. An accept on an ask filed with REVIEW=claims:<keys> records those claims IN-STEP,
    at their current fingerprints, citing the ruling."""
    import argparse
    import json

    ca = _load("claims_accept")
    saved: dict = {}

    def bundle(root, cur, keys, out):  # noqa: ANN001, ANN202
        (out / "units.json").write_text(json.dumps({k: {**cur[k], "uid": k.split("#")[0]} for k in keys}))

    monkeypatch.setattr(ca.claims, "bundle", bundle)
    monkeypatch.setattr(ca.claims, "save_index", lambda path, rows: saved.update(rows))
    monkeypatch.setattr(ca.claims, "live_rows", lambda cur, rows: rows)
    cur = {"m.py::f#a claim": {"code": "c", "core": "k", "research": "r"}}
    args = argparse.Namespace(keys="m.py::f#a claim", trigger="ask:x")
    assert ca.accept(tmp_path, cur, {}, args) == 0
    assert saved["m.py::f#a claim"]["verdict"] == "IN-STEP" and "ask:x" in saved["m.py::f#a claim"]["note"]
    assert ca.accept(tmp_path, cur, {}, argparse.Namespace(keys="nope", trigger="ask:x")) == 2, "an unknown claim is refused"


def test_a_spec_round_bundle_is_the_trigger_s_feature_and_only_its_reviews(tmp_path: pathlib.Path) -> None:
    """The round arbiter's tooling fix on round:spec-fidelity|413-money-tooltip-on-the-record#1@6 (2026-10-24): the bundle took the
    ACTIVE feature (by then 414) for 413's spec and request, and counted 412's reviews - which named 413's directory as context -
    as 413's rounds. The trigger's own feature is bundled, and only reviews OF it are its rounds."""
    (tmp_path / "clone").mkdir()
    root = _clone(tmp_path / "clone", "414-active")
    for f, words in (("413-tip", "THE 413 SPEC"), ("414-active", "THE 414 SPEC")):
        (root / "specs" / f).mkdir(parents=True)
        (root / "specs" / f / "spec.md").write_text(words)
        (root / "specs" / f / "request.md").write_text(words + " REQUEST")
    assert ab.trigger_feature_dir(root, "round:spec-fidelity|413-tip#1@6") == root / "specs" / "413-tip"
    assert ab.trigger_feature_dir(root, "round:spec-fidelity|999-none#1@6") is None
    out = tmp_path / "out"
    out.mkdir()
    ab.feature_section(root, out, ab.trigger_feature_dir(root, "round:spec-fidelity|413-tip#1@6"), "round:spec-fidelity|413-tip#1@6")
    assert (out / "spec.md").read_text() == "THE 413 SPEC" and (out / "request.md").read_text() == "THE 413 SPEC REQUEST"
    assert ab.reviewed_feature("MODE 2: SPECIFICATION REVIEW. Spec: /c/specs/412-basket/spec.md; its sibling is specs/413-tip/") == "412-basket"
    assert ab.reviewed_feature("MODE 3 (VERIFY) - round 4 of feature 413-tip, assembled ... specs/412-basket ...") == "413-tip"
    subs = tmp_path / "transcripts" / "-proj" / "sess" / "subagents"
    subs.mkdir(parents=True)
    for n, prompt, reply in (
        (1, "MODE 2: SPECIFICATION REVIEW of specs/413-tip", "Verdict: FAITHFUL\n"),
        (2, "MODE 2: SPECIFICATION REVIEW. Spec: /c/specs/412-basket/spec.md; sibling specs/413-tip", "Verdict: NOT FAITHFUL\n\n1. SIBLING.\n"),
    ):
        f = subs / f"agent-b{n}.jsonl"
        f.write_text(json.dumps({"message": {"role": "user", "content": prompt}}) + "\n" + json.dumps({"message": {"role": "assistant", "content": [{"type": "text", "text": reply}]}}) + "\n")
    text = "".join(ab.spec_rounds(out, "413-tip", tmp_path / "transcripts"))
    assert "### Round 1: spec-fidelity (FAITHFUL)" in text and "Round 2" not in text and "SIBLING" not in text
