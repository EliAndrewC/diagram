"""`scripts/_open_questions.py` - `make open-questions` (feature 285).

WHAT THESE PROVE: a GUESS (or GUESSES) in a question's visible text is an item, one per sentence however many labels it
carries, and one inside an HTML comment or written lower-case is not; an absence note is an item with the claim it was
searched for, a settled one is marked and kept, a grounds note and a convention label are not items; a question reaches
a map feature through a class's `Entry:`, through a question a class names that links to it, and through an engine file
quoting its heading or anchor, and says so when none does; a GUESS marked outside the record is listed with its file and
line, the tooling's logs skipped; rewriting a guess removes exactly its item. Then the real tree, once: the rack length
per household (0016) reaches the threshing yard through 505, the kitchen postern's GUESS in `compound.py` is
listed, and every visible label in the record falls in a listed sentence.
"""

from __future__ import annotations

import importlib.util
import pathlib
import re
import resource
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[5]
SKILL = REPO / ".claude/skills/diagram"


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # a dataclass resolves its module by name
    spec.loader.exec_module(mod)
    return mod


oq = _load("_open_questions")

QUESTION = """<h2 id="how-long-was-a-rack">How long was a rice-drying rack? As long as the field</h2>
<!-- tags: subject=homesteads; setting=countryside; level=detail -->
<!-- researched 2026-09-28; a GUESS in a session note is not a claim -->
<p><strong>Sources:</strong> <a href="x"><code>k</code></a></p>
<p>A rack ran along the paddy.<sup class="fn" data-note="k"></sup> Its length per household is a GUESS until a figure is
found. The post spacing is a CONVENTION so it reads. How many racks one household put up no page says.<sup class="fn" data-note="absent"></sup></p>
<ul><li>The shares are GUESSES, and the side is a GUESS too.</li></ul>
<p>We could only guess at the rest, in lower case.</p>
<p>A settled search.<sup class="fn" data-note="settled"></sup> Grounded.<sup class="fn" data-note="grounds"></sup></p>
"""
NOTES = """<ol>
<li data-note="k"><a href="x"><code>k</code></a> - 「a rack」</li>
<li data-note="absent">no publicly readable source (searched 2026-09-27: kotobank for 稲架)</li>
<li data-note="settled">no publicly readable source (searched 2026-09-01 and 2026-09-20: two passes) settled 2026-09-20</li>
<li data-note="grounds">no source is owed: a drawing convention</li>
<!-- <li data-note="old">no publicly readable source (a note retired to a comment)</li> -->
</ol>"""
LINKER = """<h2 id="did-a-village-rack-by-the-house">Did a village put its racks by the house?</h2>
<p>By the weather; how long, see <a href="#how-long-was-a-rack">How long was a rice-drying rack?</a>.</p>
"""


def _record(tmp: pathlib.Path) -> pathlib.Path:
    q = tmp / ".claude/skills/diagram/research/questions"
    q.mkdir(parents=True)
    (q / "0500-how-long-was-a-rack.html").write_text(QUESTION)
    (q / "0500-how-long-was-a-rack.notes.html").write_text(NOTES)
    (q / "0505-did-a-village-rack-by-the-house.html").write_text(LINKER)
    (q / "0505-did-a-village-rack-by-the-house.notes.html").write_text("<ol></ol>")
    # a built page repeats the questions and is never read
    (tmp / ".claude/skills/diagram/research/site/q").mkdir(parents=True)
    (tmp / ".claude/skills/diagram/research/site/q/how-long-was-a-rack.html").write_text(QUESTION)
    return tmp


def test_a_question_yields_one_item_per_guess_sentence_and_per_absence_note(tmp_path: pathlib.Path) -> None:
    qs = oq.questions(_record(tmp_path))
    assert [q.anchor for q in qs] == ["how-long-was-a-rack", "did-a-village-rack-by-the-house"], "fragments only, in file order"
    q = qs[0]
    assert q.page == "homesteads" and q.heading == "How long was a rice-drying rack? As long as the field"
    guesses = [i.text for i in q.items if i.kind == "guess"]
    assert guesses == ["Its length per household is a GUESS until a figure is found.", "The shares are GUESSES, and the side is a GUESS too."]
    absences = [(i.kind, i.claim) for i in q.items if i.kind != "guess"]
    assert absences == [("absence", "How many racks one household put up no page says."), ("absence-settled", "A settled search.")]
    assert all("grounds" not in i.text and "CONVENTION" not in i.text for i in q.items), "a grounds note and a convention are not open"
    assert not qs[1].items and "how-long-was-a-rack" in qs[1].links
    assert qs[1].page == "untagged", "a page with no tags, and no research page of its stem, is grouped as untagged"


def test_rewriting_a_guess_removes_exactly_its_item(tmp_path: pathlib.Path) -> None:
    root = _record(tmp_path)
    before = [i.text for i in oq.questions(root)[0].items]
    frag = root / ".claude/skills/diagram/research/questions/0500-how-long-was-a-rack.html"
    frag.write_text(QUESTION.replace("Its length per household is a GUESS until a figure is\nfound.", "Its length was 30 m."))
    after = [i.text for i in oq.questions(root)[0].items]
    assert [t for t in before if t not in after] == ["Its length per household is a GUESS until a figure is found."]
    assert len(after) == len(before) - 1


def test_a_question_reaches_its_map_features_three_ways(tmp_path: pathlib.Path) -> None:
    qs = oq.questions(_record(tmp_path))
    routes = oq.class_routes({"threshing yard": ["did-a-village-rack-by-the-house"], "farmhouse": ["how-long-was-a-rack"]}, qs)
    assert routes["how-long-was-a-rack"] == ["farmhouse", "threshing yard (through 'Did a village put its racks by the house?')"]
    assert routes["did-a-village-rack-by-the-house"] == ["threshing yard"]
    engine = {"l7r/yards.py": "x = 1\n# the rack length: research/questions/0500 'How long was a rice-drying rack?'\n", "l7r/other.py": "# #how-long-was-a-rack\n"}
    key = oq.heading_key(qs[0].heading)
    assert key == "How long was a rice-drying rack?"
    assert oq.heading_key("A castle has TWO gates") == "A castle has TWO gates", "no length floor: a short heading is cited too"
    assert oq.code_citations(engine, qs[0], key) == ["l7r/yards.py:2", "l7r/other.py:1"]
    # the index finds what the per-file scan finds (feature 321: the target's time), a quote inside a longer word included
    wide = {**engine, "l7r/none.py": "y = 2\n", "l7r/edge.py": "s = 'xHow long was a rice-drying rack?'\n"}
    assert oq.cite_all(wide, qs, {q.anchor: oq.heading_key(q.heading) for q in qs}) == {q.anchor: oq.code_citations(wide, q, oq.heading_key(q.heading)) for q in qs}
    assert oq.cite_all(wide, qs[:1], {qs[0].anchor: "?!"}) == {qs[0].anchor: ["l7r/other.py:1"]}, "a key with no word: every file"
    assert oq.cite_all({"l7r/q.py": "a ?! b\n"}, qs[:1], {qs[0].anchor: "?!"}) == {qs[0].anchor: ["l7r/q.py:1"]}
    unreached = oq.Question("homesteads", "x", "X", "p", items=[oq.Item("guess", "a GUESS")])
    text = oq.report([qs[0], unreached], routes, {"how-long-was-a-rack": ["l7r/yards.py:2"]}, [])
    assert "map features: farmhouse; threshing yard (through" in text and "l7r/yards.py:2" in text
    assert "map features: no map feature found depending on it" in text


def test_guesses_outside_the_record_are_listed_with_file_and_line_the_logs_skipped(tmp_path: pathlib.Path) -> None:
    skill = tmp_path / ".claude/skills/diagram"
    for rel, body in {
        "l7r/compound.py": "a = 6  # the postern's 6 ft passage is a GUESS\n",
        "pool/m/m.svg": "<svg><!-- what the east room held is a GUESS --></svg>\n",
        "dev/bypass-log/1.json": '{"reason": "a GUESS repeated"}\n',
        "research/questions/0010-a.html": "<p>a GUESS</p>\n",
        "tests/t.py": "# GUESS\n",
        "icon.png": None,
    }.items():
        (skill / rel).parent.mkdir(parents=True, exist_ok=True)
        if body is None:
            (skill / rel).write_bytes(b"\x89PNG\xff\xfe GUESS")
        else:
            (skill / rel).write_text(body)
    files = oq.outside_files(tmp_path, ["l7r/compound.py", "pool/m/m.svg", "dev/bypass-log/1.json", "research/questions/0010-a.html", "tests/t.py", "icon.png"])
    assert sorted(files) == ["l7r/compound.py", "pool/m/m.svg"], "the record, the tests, the logs and a binary are not read here"
    found = oq.outside_guesses(files)
    assert found == [("l7r/compound.py", 1, "a = 6  # the postern's 6 ft passage is a GUESS"), ("pool/m/m.svg", 1, "<svg><!-- what the east room held is a GUESS --></svg>")]
    text = oq.report([], {}, {}, found)
    assert "GUESS lines outside the record: 2 (l7r 1, pool 1)" in text and "l7r/compound.py\n   1: a = 6" in text


def test_the_report_counts_before_it_lists(tmp_path: pathlib.Path) -> None:
    qs = oq.questions(_record(tmp_path))
    text = oq.report(qs, {}, {}, [])
    head, _, rest = text.partition("\n====")
    assert re.search(r"homesteads\s+1\s+2\s+1\s+1", head) and re.search(r"TOTAL\s+1\s+2\s+1\s+1", head)
    assert "UNSOURCED (searched twice, settled): A settled search." in rest
    assert "(the claim is not marked in the text)" in oq.report([oq.Question("p", "a", "Q", "f", items=[oq.Item("absence", "no publicly readable source")])], {}, {}, [])


def test_a_note_marker_in_no_passage_leaves_the_claim_empty() -> None:
    assert oq.claim_of("<p>nothing here</p>", "k") == ""
    assert oq.claim_of('<p><sup class="fn" data-note="k"></sup></p>', "k") == ""


def test_a_fragment_without_its_heading_is_skipped(tmp_path: pathlib.Path) -> None:
    root = _record(tmp_path)
    (root / ".claude/skills/diagram/research/questions/0510-no-heading.html").write_text("<p>a GUESS with no heading</p>")
    assert [q.anchor for q in oq.questions(root)] == ["how-long-was-a-rack", "did-a-village-rack-by-the-house"]


CALIBRATION = "s = 0\nfor i in range(4_000_000):\n    s += i * i\n"
CALIBRATION_QUIET = 0.44  # its CPU seconds on the GM's laptop, quiet (0.43-0.51 over five runs, 2026-10-04)


def _calibration_cpu() -> float:
    """CPU seconds of the fixed calibration loop in a child, now."""
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    subprocess.run([sys.executable, "-c", CALIBRATION], check=True)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    return (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)


def test_the_real_tree() -> None:
    # ...ITS CPU TIME, NOT THE WALL CLOCK (feature 315): the gate runs it beside four other sessions under one 10 GB cap, and a
    # 2.3 s run read 12.4 s while the machine stalled on memory - the bound is on the work.
    # BUT CPU TIME IS NOT IMMUNE TO CONTENTION EITHER (2026-10-04): the GM's laptop is a hybrid Core Ultra 7 155H (P- and
    # E-cores, two threads a core), and with every core busy the same 3.4 s of work read 8-13 s of CPU - it failed a
    # test-full at 10.0003 s, and ran 9-11 s in every full run measured that day. So the CPU time is SCALED by a
    # calibration loop run beside it: `CALIBRATION_QUIET` s of CPU on a quiet machine, and its lesser reading of the
    # two around the run says how much slower this machine is right now. Measured under 22 busy loops: the scaled
    # reading was 3.4 / 2.5 / 3.9 s against 3.4 s quiet - the 10 s bound (SC-003, a quiet-machine target) still
    # catches a 3x regression and no longer flakes on a loaded gate.
    calibrated = _calibration_cpu()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    out = subprocess.run([sys.executable, str(REPO / "scripts/_open_questions.py"), "--root", str(REPO)], capture_output=True, text=True, check=True).stdout
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    took = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    slowdown = max(1.0, min(calibrated, _calibration_cpu()) / CALIBRATION_QUIET)
    took /= slowdown
    rack = out[out.index("## How our maps draw rice-drying racks (hasa, hasagi)") :]
    rack = rack[: rack.index("\n## ")]
    assert "map features: threshing yard" in rack
    assert "GUESS: A rack by the house runs from the yard's edge to its middle." in rack
    outside = out[out.index("GUESSES MARKED OUTSIDE THE RECORD") :]
    compound = outside[outside.index("\nl7r/diagram/compound.py\n") :].split("\n\n")[0]
    assert any("postern" in line and "GUESS" in line for line in compound.splitlines()), "the postern's GUESS, marked only in code (SC-004)"
    # every visible label in the record falls in a listed sentence (SC-001)
    labels = 0
    for frag in (SKILL / "research" / "questions").glob("*.html"):
        if frag.name.endswith(".notes.html") or not oq._FRAGMENT.match(frag.name):
            continue
        labels += len(oq._GUESS.findall(oq.visible(frag.read_text(encoding="utf-8"))))
    listed = sum(len(oq._GUESS.findall(line)) - 1 for line in out.splitlines() if line.startswith("   - GUESS: "))
    assert labels > 100 and listed == labels, f"{listed} labels listed of {labels} in the record"
    assert took < 10, f"make open-questions took {took:.1f} s (SC-003)"
