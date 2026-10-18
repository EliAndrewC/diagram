"""`scripts/record/modal_owed.py` and `scripts/record/modal_bundle.py` - which About-form modals owe the modal checks, and what a check reads
(feature 319, plan D4-D6). The GM, 2026-10-03: the modal guidelines *"should be reviewed by subagents in more or less the same
way that our research is"*; and, of the references, *"I'm actually a little surprised to see as few references as we are
seeing"* - so the candidates are the UNION rule, and the farmhouse's own case (0004 meeting 0029 on `households`) is the test."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

from tests._scripts import script

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, script(name))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = sys.modules[name.lstrip("_")] = mod  # the old name and the one a sibling imports it by (2026-10-08)
    spec.loader.exec_module(mod)
    return mod


mo = _load("_modal_owed")
mb = _load("_modal_bundle")
CLASSES = pathlib.Path(mo.MODAL_DIRS[0])

FARMHOUSE = '''
class Farmhouse(Kind):
    """
    About: A farmhouse was the dwelling of one farming household, who worked on its earth floor.

    It was thatched.

    Guesses:
    - its size on the map: no small house was measured.

    Name: farmhouse
    Covers: houses
    Sources: not recorded
    Entry: research/questions/0029-farmhouses-minka.html
    """

    key = "farmhouse"


class Byre(Kind):
    """
    What: old form.
    Why: old form.
    Note: old form.
    Name: byre
    Covers: x
    Label: accurate
    Sources: not recorded
    Entry: research/questions/0029-farmhouses-minka.html
    """

    key = "byre"
'''
Q0029 = '<h2 id="farmhouses-minka">Farmhouses (minka)</h2>\n<!-- tags: subject=homesteads,buildings,households; level=foundational -->\n<p>A farmhouse was the dwelling of one household.</p>\n'
Q0004 = '<h2 id="households">Households: how many live in a house</h2>\n<!-- tags: subject=tiers,households -->\n<p>A household averaged five.</p>\n'
Q0099 = '<h2 id="ponds">Ponds</h2>\n<!-- tags: subject=water -->\n<p>Nothing about houses here.</p>\n'
Q0100 = '<h2 id="lanes">Lanes</h2>\n<!-- tags: subject=ways -->\n<p>A lane ran past every farmhouse.</p>\n'


def _git(root: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def _tree(tmp: pathlib.Path, homestead: str = FARMHOUSE) -> pathlib.Path:
    root = tmp / "repo"
    (root / CLASSES).mkdir(parents=True)
    (root / CLASSES / "homestead.py").write_text(homestead, encoding="utf-8")
    q = root / "research" / "questions"
    q.mkdir(parents=True)
    for name, text in (
        ("0029-farmhouses-minka.html", Q0029),
        ("0004-households.html", Q0004),
        ("0099-ponds.html", Q0099),
        ("0100-lanes.html", Q0100),
    ):
        (q / name).write_text(text, encoding="utf-8")
    (q / "0029-farmhouses-minka.notes.html").write_text("<li>notes</li>", encoding="utf-8")
    dev = root / "dev"
    dev.mkdir(parents=True)
    (dev / "modals.md").write_text("M1. The reader.\n", encoding="utf-8")
    (dev / "modals-particular.md").write_text("P1. Particular.\n", encoding="utf-8")
    (root / "research" / "assets").mkdir(parents=True)
    (root / "research" / "assets" / "glossary-variants.txt").write_text("minka\tfarmhouse\n", encoding="utf-8")
    _git(root, "init", "-q")
    _git(
        root,
        "-c",
        "user.email=t@t",
        "-c",
        "user.name=t",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "empty",
    )
    return root


def _commit(root: pathlib.Path) -> str:
    _git(root, "add", "-A")
    _git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "c")
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def test_the_about_form_is_read_and_the_old_form_is_not(tmp_path: pathlib.Path) -> None:
    root = _tree(tmp_path)
    found = mo.modals_now(root)
    assert [m.key for m in found] == ["farmhouse"], "only an About-form class owes the modal checks; the byre keeps entry-drift"
    m = found[0]
    assert m.tags["About"] == "A farmhouse was the dwelling of one farming household, who worked on its earth floor.\n\nIt was thatched."
    assert m.tags["Guesses"] == "- its size on the map: no small house was measured."
    assert m.entry_files() == ["research/questions/0029-farmhouses-minka.html"] and m.form == "standard"
    assert mo.find(root, "Farmhouse") == m and mo.find(root, "homestead.Farmhouse") == m and mo.find(root, "farmhouse") == m
    assert mo.find(root, "Nothing") is None and mo.about_keys(root) == {"farmhouse"}


def test_a_class_new_to_the_about_form_owes_all_four_units(
    tmp_path: pathlib.Path,
) -> None:
    root = _tree(tmp_path)
    base = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    slugs = [s for s, _w, _f in mo.owed(root, base)]
    assert slugs == [
        "modal-form:hamlet/farmhouse",
        "modal-accuracy:hamlet/farmhouse",
        "modal-references:hamlet/farmhouse",
        "modal-gaps:hamlet/farmhouse",
        "modal-depiction:hamlet/farmhouse",
    ], "the Depiction check is owed whether or not the modal has the tab (D13)"


def test_nothing_is_owed_while_nothing_moved_and_a_moved_entry_page_owes_only_the_research_units(
    tmp_path: pathlib.Path,
) -> None:
    root = _tree(tmp_path)
    base = _commit(root)
    assert mo.owed(root, base) == [], "a formatting-free delta owes nothing (feature 311)"
    (root / "research/questions/0029-farmhouses-minka.html").write_text(Q0029.replace("one household", "one farming household"), encoding="utf-8")
    rows = mo.owed(root, base)
    assert [s for s, _w, _f in rows] == [
        "modal-accuracy:hamlet/farmhouse",
        "modal-references:hamlet/farmhouse",
        "modal-gaps:hamlet/farmhouse",
    ]
    assert "0029-farmhouses-minka.html" in rows[0][1]


def test_a_comment_or_a_rewrap_of_an_entry_page_owes_nothing(
    tmp_path: pathlib.Path,
) -> None:
    """2026-10-05: a page counted as moved on any byte, so a comment made every modal naming it owed - `test-entry-gate.sh`'s
    "a comment and a re-wrap owe nothing" went red on main. A page moves when its WORDS do."""
    root = _tree(tmp_path)
    base = _commit(root)
    page = root / "research/questions/0029-farmhouses-minka.html"
    page.write_text(Q0029.replace("one household", "one  <!-- probe -->household"), encoding="utf-8")
    assert "probe" in page.read_text(encoding="utf-8")
    assert mo.owed(root, base) == [], "a comment and a re-wrap change no words"
    page.write_text(Q0029.replace("one household", "one farming household"), encoding="utf-8")
    assert [s for s, _w, _f in mo.owed(root, base)] == [
        "modal-accuracy:hamlet/farmhouse",
        "modal-references:hamlet/farmhouse",
        "modal-gaps:hamlet/farmhouse",
    ]


def test_a_reworded_about_owes_the_form_again_and_changes_its_fingerprint(
    tmp_path: pathlib.Path,
) -> None:
    root = _tree(tmp_path)
    base = _commit(root)
    before = mo.fingerprints(root, mo.find(root, "farmhouse"))
    (root / CLASSES / "homestead.py").write_text(
        FARMHOUSE.replace("It was thatched.", "It was thatched with straw."),
        encoding="utf-8",
    )
    assert [s for s, _w, _f in mo.owed(root, base)][0] == "modal-form:hamlet/farmhouse"
    assert mo.fingerprints(root, mo.find(root, "farmhouse")) != before


def test_the_candidates_are_the_union_and_0004_is_a_farmhouse_candidate(
    tmp_path: pathlib.Path,
) -> None:
    """Plan D5 as the plan review ruled it: ANY shared subject tag OR the kind's words - 0004 meets 0029 on `households`;
    0100 shares no tag but names the farmhouse; 0099 shares neither and is not a candidate."""
    root = _tree(tmp_path)
    cands = [c[1].rsplit("/", 1)[1] for c in mb.candidates(root, mo.find(root, "farmhouse"))]
    assert "0004-households.html" in cands and "0100-lanes.html" in cands and "0099-ponds.html" not in cands
    assert "0029-farmhouses-minka.html" not in cands, "an Entry page is not its own candidate"
    assert "minka" in mb.terms_of(root, mo.find(root, "farmhouse")), "the glossary's variants are the kind's words too"


def test_the_prepass_rules_on_the_band_the_barred_phrases_and_the_entry(
    tmp_path: pathlib.Path,
) -> None:
    root = _tree(
        tmp_path,
        FARMHOUSE.replace("It was thatched.", "This is a guess - this project drew it.").replace("0029-farmhouses-minka.html", "0029-missing.html"),
    )
    text = mb.prepass(root, mo.find(root, "farmhouse"))
    assert "OUTSIDE THE BAND" in text and "'this project'" in text and "'This is a guess'" in text and "Entry names no file" in text


def test_the_bundle_carries_the_modal_the_rules_and_its_owed_units(tmp_path: pathlib.Path, monkeypatch) -> None:
    monkeypatch.setenv("CHECK_ORDER_OK", "the check order is tests/tooling/test_popup_order.py's subject")
    root = _tree(tmp_path)
    out = tmp_path / "b"
    assert mb.bundle(root, "Farmhouse", "modal-research", str(out)) == 0
    manifest = (out / "MANIFEST.md").read_text(encoding="utf-8")
    assert "## `modal.md`" in manifest and "## `guidelines.txt` - origin `dev/modals.md`" in manifest
    # the rules live in the agent file (feature 383 amendment 6, plan D35): the bundle names the set, it does not copy it
    assert "standard form" in (out / "guidelines.txt").read_text(encoding="utf-8") and (root / "dev/modals.md").read_text(encoding="utf-8").strip().splitlines()[0] not in manifest
    assert "entry/0029-farmhouses-minka.html" in manifest and "Farmhouses (minka)" in manifest
    assert "owed-checks: modal-research" in manifest and "unit: modal-gaps:hamlet/farmhouse " in manifest and "unit: modal-form:" not in manifest
    assert (out / "record" / "0004-households.html").is_file() and (out / "cand" / "0004-households.html").is_file()
    assert mb.bundle(root, "Farmhouse", "modal-form", str(out)) == 0, "a bundle is rebuilt in place"
    assert "unit: modal-form:hamlet/farmhouse " in (out / "MANIFEST.md").read_text(encoding="utf-8")
    (tmp_path / "notabundle").mkdir()
    (tmp_path / "notabundle" / "x").write_text("x", encoding="utf-8")
    assert mb.bundle(root, "Farmhouse", "modal-form", str(tmp_path / "notabundle")) == 2, "a directory we did not write is never emptied"
    assert mb.bundle(root, "Nothing", "modal-form", str(tmp_path / "c")) == 2


def test_a_modal_in_its_own_file_is_read_from_the_file_and_owed_by_its_edits(
    tmp_path: pathlib.Path,
) -> None:
    """Plan D12: the modal's text is `assets/modals/<hamlet|sheet>/<slug>.md`; the class keeps only its key. The file is read
    (its origin is the file, the EDIT target), the class docstring - here absent - is not, and a file edit owes the form."""
    root = _tree(tmp_path, "class Farmhouse(Kind):\n    key = 'farmhouse'\n")
    f = root / mo.modal_file(str(CLASSES / "homestead.py"), "farmhouse")
    f.parent.mkdir(parents=True)
    doc = FARMHOUSE.split('"""')[1]
    f.write_text(
        "\n".join(line.strip() for line in doc.strip().splitlines()) + "\n",
        encoding="utf-8",
    )
    base = _commit(root)
    m = mo.find(root, "hamlet/farmhouse")
    assert m and m.origin == mo.modal_file(str(CLASSES / "homestead.py"), "farmhouse") and m.uid == "hamlet/farmhouse"
    assert m.tags["About"].startswith("A farmhouse was") and m.doc.startswith("About:")
    assert mo.owed(root, base) == []
    f.write_text(
        f.read_text(encoding="utf-8").replace("It was thatched.", "It was thatched with straw."),
        encoding="utf-8",
    )
    assert [s for s, _w, _f in mo.owed(root, base)][0] == "modal-form:hamlet/farmhouse"
    sheet = mo.modal_file(
        "l7r/diagram/interactive/compound_kinds/household.py",
        "well",
    )
    assert sheet.endswith("/modals/sheet/well.md"), "a sheet's well and a hamlet's well are two files"


def test_the_depiction_tab_owes_its_own_check_and_its_bundle_carries_the_drawing_and_the_claims(
    tmp_path: pathlib.Path,
) -> None:
    """Plan D13 (GM 2026-10-04): a modal with a Depiction tab owes `modal-depiction`, again when a page its Drawing: names
    moves; its bundle carries that page whole and the claims-index rows citing it (a DRIFTED one with its note)."""
    import json

    root = _tree(
        tmp_path,
        FARMHOUSE.replace(
            "    Name: farmhouse",
            "    Depiction: The map draws every house alike.\n\n    Name: farmhouse",
        ).replace(
            "    Entry: research/questions/0029-farmhouses-minka.html",
            "    Entry: research/questions/0029-farmhouses-minka.html\n    Drawing: research/questions/0029-farmhouses-minka.drawing.html",
        ),
    )
    q = root / "research" / "questions"
    (q / "0029-farmhouses-minka.drawing.html").write_text(
        '<h2 id="how-our-maps-draw-farmhouses">How our maps draw farmhouses</h2>\n<p>The roof shape is a knob.</p>\n',
        encoding="utf-8",
    )
    (root / "dev" / "claims-index.json").write_text(
        json.dumps(
            {
                "l7r/diagram/settlement/houses.py::HousesMixin.house#ridge": {
                    "verdict": "DRIFTED",
                    "note": "always hipped",
                    "pages": "{'0029-farmhouses-minka.drawing.html': 'x'}",
                }
            }
        ),
        encoding="utf-8",
    )
    base = _commit(root)
    assert [s for s, _w, _f in mo.owed(root, base)] == [], "nothing moved"
    (q / "0029-farmhouses-minka.drawing.html").write_text(
        '<h2 id="how-our-maps-draw-farmhouses">How our maps draw farmhouses</h2>\n<p>The roof shape is one.</p>\n',
        encoding="utf-8",
    )
    assert [s for s, _w, _f in mo.owed(root, base)] == ["modal-depiction:hamlet/farmhouse"], "a moved drawing page owes the tab's check alone"
    out = tmp_path / "dep"
    assert mb.bundle(root, "Farmhouse", "modal-depiction", str(out)) == 3, "owed only by a moved page: the triage first (feature 375)"
    assert mb.bundle(root, "Farmhouse", "modal-depiction", str(out), reason="the bundle's own test") == 0
    manifest = (out / "MANIFEST.md").read_text(encoding="utf-8")
    assert "page: research/questions/0029-farmhouses-minka.drawing.html " in manifest, "the page it read, kept for a later triage"
    assert "drawing/0029-farmhouses-minka.drawing.html" in manifest and "DRIFTED | `settlement/houses.py::HousesMixin.house#ridge` | always hipped" in manifest
    assert "## Depiction" in manifest and "The map draws every house alike." in manifest and "no crop" in manifest, "no pool page in the fixture"
    assert "unit: modal-depiction:hamlet/farmhouse " in manifest and "owed-checks: modal-depiction" in manifest
    assert "owed: modal-depiction:hamlet/farmhouse - a page its Drawing: names moved" in manifest, "why the unit is due (374)"


def test_a_modal_with_no_drawing_list_is_still_handed_its_kinds_drawing_page_as_a_candidate(
    tmp_path: pathlib.Path,
) -> None:
    """The plan review of D13, round 2: a conversion that leaves `Drawing:` empty must still be judged against the drawing page
    its kind has - the one beside a question its Entry: names - so the bundle carries it, marked CANDIDATE, with the claims."""
    root = _tree(tmp_path)
    q = root / "research" / "questions"
    (q / "0029-farmhouses-minka.drawing.html").write_text(
        '<h2 id="how-our-maps-draw-farmhouses">How our maps draw farmhouses</h2>\n<p>Drawn bold.</p>\n',
        encoding="utf-8",
    )
    _commit(root)
    m = mo.find(root, "farmhouse")
    assert m.drawing_files() == [] and mb.drawing_candidates(root, m) == ["research/questions/0029-farmhouses-minka.drawing.html"]
    out = tmp_path / "dep"
    assert mb.bundle(root, "Farmhouse", "modal-depiction", str(out)) == 0
    manifest = (out / "MANIFEST.md").read_text(encoding="utf-8")
    assert "drawing/0029-farmhouses-minka.drawing.html" in manifest and "CANDIDATE - NOT on the modal's Drawing: list" in manifest


def test_a_drawing_page_the_old_form_listed_at_the_base_is_a_candidate_after_the_conversion(
    tmp_path: pathlib.Path,
) -> None:
    """The plan review of D13, round 3: FR-012 keeps every conversion off main, so at the merge base every kind is in the OLD
    form, its drawing pages under its `Entry:` - the 0038 shape, a page whose sibling question the class does not cite. The
    converted head lists no `Drawing:`; the page the old form named is still handed over, marked CANDIDATE."""
    old = FARMHOUSE.replace("Farmhouse(Kind)", "Farmhouse(Kind)").split('"""')
    old_doc = "\n    What: old form.\n    Why: old form.\n    Name: farmhouse\n    Covers: houses\n    Label: accurate\n    Sources: not recorded\n    Entry: research/questions/0029-farmhouses-minka.html, research/questions/0038-yards.drawing.html\n    "
    root = _tree(tmp_path, old[0] + '"""' + old_doc + '"""' + '"""'.join(old[2:]))
    (root / "research" / "questions" / "0038-yards.drawing.html").write_text(
        '<h2 id="how-our-maps-draw-yards">How our maps draw yards</h2>\n<p>Each house drawn turned.</p>\n',
        encoding="utf-8",
    )
    _commit(root)
    assert mo.find(root, "farmhouse") is None, "the base holds the old form only"
    (root / CLASSES / "homestead.py").write_text(FARMHOUSE, encoding="utf-8")
    m = mo.find(root, "farmhouse")
    assert m.drawing_files() == [] and "research/questions/0038-yards.drawing.html" in mb.drawing_candidates(root, m)


def test_a_drawing_page_a_listed_one_links_to_is_a_candidate(
    tmp_path: pathlib.Path,
) -> None:
    """The windbreak's round 1: 0072's drawing page sends its reader to 0080 for the crowns it draws, and the check was never
    shown 0080. A drawing page a LISTED one links to is handed over as a CANDIDATE."""
    root = _tree(
        tmp_path,
        FARMHOUSE.replace(
            "    Entry: research/questions/0029-farmhouses-minka.html",
            "    Entry: research/questions/0029-farmhouses-minka.html\n    Drawing: research/questions/0029-farmhouses-minka.drawing.html",
        ),
    )
    q = root / "research" / "questions"
    (q / "0029-farmhouses-minka.drawing.html").write_text(
        '<p>Crowns are at <a href="0080-crowns.drawing.html">crowns</a>.</p>\n',
        encoding="utf-8",
    )
    (q / "0080-crowns.drawing.html").write_text("<p>Crowns drawn 17 ft.</p>\n", encoding="utf-8")
    _commit(root)
    assert "research/questions/0080-crowns.drawing.html" in mb.drawing_candidates(root, mo.find(root, "farmhouse"))


def test_a_check_reads_each_conditioned_item_with_its_condition() -> None:
    """FR-015: the bundle shows `[settlement_form=nucleated]` as words a check reads, on a bullet and on a paragraph."""
    got = mb._conditions_shown("- [settlement_form=nucleated|linear] A guess.\n[byre_form=courtyard] A paragraph.\nPlain.")
    assert got == "- (only where settlement_form is nucleated or linear) A guess.\n(only where byre_form is courtyard) A paragraph.\nPlain."


def test_several_conditions_read_as_one_clause() -> None:
    assert mb._conditions_shown("- [settlement_form=nucleated][lane_web=alleys] A.") == "- (only where settlement_form is nucleated and lane_web is alleys) A."


def test_the_glyph_crop_shows_the_drawn_fill_never_the_highlight(tmp_path: pathlib.Path) -> None:
    """Feature 374 FR-007 (carried from 372 wave 105): a glyph that fills the viewport is under the corner the mouse leaves
    for, so the shot showed the page's highlight (the lit `g.f.on` fill), not the drawn fill. Red on the old script."""
    import pytest  # noqa: PLC0415

    pytest.importorskip("playwright")
    page = tmp_path / "sheet.html"
    page.write_text(
        "<html><head><style>body{margin:0} g.f.on rect{fill:#FFC83C !important}</style></head><body>"
        '<svg width="1200" height="900"><g class="f" data-k="kitchen"><rect x="0" y="0" width="1200" height="900" fill="#C9A57A"/></g></svg>'
        "<script>document.querySelectorAll('g.f').forEach(g=>{g.addEventListener('mouseover',()=>g.classList.add('on'));"
        "g.addEventListener('mouseout',()=>g.classList.remove('on'))})</script></body></html>"
    )
    out = tmp_path / "glyph.png"
    assert mb.glyph_crop(page, "kitchen", out)
    assert "kitchen" in pathlib.Path(str(out) + ".kinds").read_text().split(), "the kinds in the crop, each a pop-up a click opens (343 office-hall)"
    from PIL import Image  # noqa: PLC0415

    with Image.open(out) as im:
        r, g, b = im.convert("RGB").getpixel((im.width // 2, im.height // 2))
    assert (r, g, b) == (0xC9, 0xA5, 0x7A), f"the crop shows {r:02X}{g:02X}{b:02X}, not the drawn fill"


def test_a_depiction_bundle_says_which_maps_draw_what_its_conditions_name() -> None:
    """Feature 374 (the round arbiter's tooling fix): a conditional Drawing: link was ruled on without knowing which maps carry
    the knob's form; the bundle now carries each named knob's forms, typing rule and engine lines."""
    note = mb.knobs_note("Drawing: research/questions/0020-x.drawing.html [land_use_overlay=mulberry_fishpond]\n")
    assert "## land_use_overlay" in note and "mulberry_fishpond" in note and "def _land_use_ok" in note
    assert "settlement/fields/landuse.py" in note, "where the engine resolves it (the roller that also did went in feature 388)"
    assert mb.knobs_note("no condition here") == ""


def test_a_key_with_an_apostrophe_is_found_and_its_glyph_s_parts_read(tmp_path: pathlib.Path) -> None:
    """343's clerks--seats ruling, 2026-10-11: the page writes `data-k="clerks&#x27; seats"`, so a key with an apostrophe was
    on no page by its raw mark and its check ran with no crop; and with no crop it had no drawn size to check a stated one."""
    page = tmp_path / "pool" / "magistracies" / "ubame" / "ubame.html"
    page.parent.mkdir(parents=True)
    page.write_text(
        '<svg viewBox="0 0 800 600"><g class="f f-clerks--seats" data-k="clerks&#x27; seats">'
        '<rect x="292" y="418" width="24" height="15" stroke-width="0.5"></rect></g>'
        '<g class="f f-door" data-k="door"><rect x="1" y="1" width="9" height="9"></rect></g></svg>'
    )
    assert mb.pool_page_with(tmp_path, "clerks' seats", sheet=True) == page
    shape = mb.drawn_geometry(page, "clerks' seats")
    assert '<rect> x="292" y="418" width="24" height="15"' in shape and "viewBox 0 0 800 600" in shape
    assert "0.5" not in shape and 'width="9"' not in shape, "not stroke-width, and not the next kind's parts"


def test_research_fixed_wording_is_listed_for_the_form_round(tmp_path: pathlib.Path) -> None:
    """343's border-court ruling: a form fix undid a research fix's scope words unseen. The research rounds' EDITs that still
    stand are what the form round must keep."""
    (tmp_path / ".git").mkdir()
    reply = tmp_path / "r.md"
    reply.write_text("EDIT m.md\n<<<\nnothing known of the formal entrance\n===\nno page on the formal entrance\n>>>\nEDIT m.md\n<<<\nold\n===\nwording later replaced\n>>>\n")
    (tmp_path / ".git" / "checks-open.json").write_text(
        json.dumps(
            {
                "dispatches": {
                    "t1": {"check": "modal-research", "subjects": ["modal:sheet/border-court"], "t": 1, "reply": str(reply)},
                    "t2": {"check": "modal-form", "subjects": ["modal:sheet/border-court"], "t": 2, "reply": str(reply)},
                }
            }
        )
    )
    text = "About: no page on the formal entrance puts a garden there.\n"
    assert mb.research_held(tmp_path, "sheet/border-court", text) == ["no page on the formal entrance"]
    assert mb.research_held(tmp_path, "sheet/door", text) == []
