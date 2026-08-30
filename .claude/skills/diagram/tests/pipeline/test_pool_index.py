"""Unit tests for pool_index.py - the pool/index.html generator.

The synthetic-pool tests pin every branch (positive Mode A classification, the manifest-missing
warning, the derived columns, per-section column pruning, the unknown-tier section, missing
renders/notes); the real-pool test at the bottom pins the one property that matters against the
actual pool: every generator in it appears in the index.

Since feature 161 the fixture builds BOTH trees at `<skill>/<tree>/<tier>/<map>/`, because the page
covers both and the cross-tree link is the interesting case: a legacy row has to come out as
`../legacy-hand-authored-pool/...` to resolve from a plain `file://` open of `pool/index.html`.
"""

import os

from l7r.diagram.pipeline import pool_index as pi
from l7r.diagram.pipeline import poolmaps


def _mk(path: str, content: str = "") -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(content)
    return path


def _map(skill: str, tier: str, stem: str, ext: str, content: str = "", tree: str = "pool") -> str:
    """One file of one map bundle, in the map's own folder."""
    return _mk(os.path.join(skill, tree, tier, stem, stem + ext), content)


def _mini_pool(tmp_path):
    """A skill dir with both trees. Returns the SKILL dir - the index spans two trees now, so a
    single pool directory is no longer the unit it is built from."""
    skill = str(tmp_path)
    pool = os.path.join(skill, "pool")
    _mk(
        os.path.join(pool, "hamlets", "aoi", "aoi.json"),
        '{"meta": {"name": "Aoi & Co", "scale": "hamlet", "ftpx": 1.0, "generated_by": "hamletgen",'
        ' "households": 15, "field_archetype": "valley_paddy", "land_use_overlay": "lotus",'
        ' "nucleated": false, "lane_skeleton": "spine", "waivers": {"some_check": "a reason"},'
        ' "capital_dir": [1, 2], "water_source": "head_center", "water_source_position": "head_center"}}',
    )
    _map(skill, "hamlets", "aoi", ".gen.py")
    _map(skill, "hamlets", "aoi", ".notes.md", "# Design notes: Aoi\n")
    _map(skill, "hamlets", "aoi", ".png", "png")
    _map(skill, "hamlets", "burned", ".gen.py")  # settlement map with NO manifest
    _map(
        skill,
        "towns",
        "beni",
        ".json",
        '{"meta": {"scale": "town", "ftpx": 1, "walled": true, "population": 900, "settlement_form": "dispersed"}}',
    )
    _map(skill, "towns", "beni", ".gen.py")
    _map(skill, "magistracies", "kiku-magistracy", ".gen.py")
    _map(
        skill,
        "magistracies",
        "kiku-magistracy",
        ".notes.md",
        "# Design notes\n\n**Program type**: magistrate's manor (county magistracy) - see buildings.md.\n",
    )
    _map(skill, "forts", "castle", ".gen.py")  # an UNKNOWN tier still gets a section
    _map(skill, "forts", "castle", ".json", '{"meta": {"name": "Castle", "walled": false}}')
    _mk(os.path.join(pool, "regressions", "bad.json"))  # a negative fixture, not a map
    os.makedirs(os.path.join(pool, "villages"))  # present but empty -> no section
    # A FROZEN exhibit in the other tree: the cross-tree link is what FR-018 is about.
    _map(skill, "villages", "furu", ".gen.py", tree=poolmaps.LEGACY_TREE)
    _map(skill, "villages", "furu", ".json", '{"meta": {"name": "Furu", "scale": "village", "ftpx": 2}}', tree=poolmaps.LEGACY_TREE)
    _map(skill, "villages", "furu", ".png", "png", tree=poolmaps.LEGACY_TREE)
    return skill


def _bundle(skill: str, tier: str, stem: str, tree: str = poolmaps.LIVE_TREE) -> poolmaps.MapBundle:
    """A bundle pointing at files that may not exist - which is the case these tests are about."""
    d = os.path.join(skill, tree, tier, stem)
    return poolmaps.MapBundle(gen=os.path.join(d, stem + ".gen.py"), stem=stem, tier=tier, tree=tree, directory=d)


def _section(page: str, tier: str, tree: str = poolmaps.LIVE_TREE) -> str:
    start = page.index(f'<h3 id="{pi._anchor(tree, tier)}"')
    return page[start : page.index("</table>", start)]


def test_fmt_val_shapes():
    assert pi._fmt_val({"b_check": "why", "a_check": "why"}) == "a_check, b_check"
    assert pi._fmt_val([1, "S"]) == "1, S"
    assert pi._fmt_val(3.5) == "3.5"


def test_knobs_drops_the_duplicate_water_source_position():
    meta = {"water_source": "head_center", "water_source_position": "head_center", "windward": "W"}
    assert pi._knobs(meta) == "water_source=head_center; windward=W"
    meta2 = {"water_source": "corner_NW", "water_source_position": "head_left"}
    assert "water_source_position=head_left" in pi._knobs(meta2)


def test_mode_a_program_variants(tmp_path):
    """No notes file at all, and a notes file with no `**Program type**:` line - both give ''."""
    skill = str(tmp_path)
    assert pi._mode_a_program(_bundle(skill, "magistracies", "missing")) == ""
    _map(skill, "magistracies", "plain", ".notes.md", "# notes with no program line\n")
    assert pi._mode_a_program(_bundle(skill, "magistracies", "plain")) == ""


def test_subtype_composition():
    assert pi._subtype({"field_archetype": "polder_grid", "walled": True}) == "polder_grid, walled"
    assert pi._subtype({"nucleated": True}) == ""
    assert pi._subtype({"nucleated": False}) == "dispersed"


def test_index_contents(tmp_path):
    skill = _mini_pool(tmp_path)
    page = pi.build_index(skill)

    # Mode B, scripted: name escaped, method, subtype, size, knobs (waivers by check name).
    assert "Aoi &amp; Co" in page
    assert "scripted (hamletgen)" in page
    assert "valley_paddy, overlay: lotus, dispersed" in page
    assert "hamlet (1 ft/px)" in page
    assert "15 households" in page
    assert "lane_skeleton=spine" in page
    assert "waivers=some_check" in page
    assert "capital_dir=1, 2" in page
    assert "water_source_position" not in page  # identical to water_source -> deduplicated
    # Links are relative to the page's own directory (pool/), so a live map is a plain relative path.
    assert 'src="hamlets/aoi/aoi.png"' in page
    # Map thumbnails open in a new tab; in-page nav anchors (pinned above) do not.
    assert '<a href="hamlets/aoi/aoi.png" target="_blank" rel="noopener">' in page
    assert 'href="hamlets/aoi/aoi.notes.md"' in page
    # ...and a FROZEN exhibit links ACROSS, which is what resolves from a file:// open (FR-018).
    assert 'src="../legacy-hand-authored-pool/villages/furu/furu.png"' in page

    # A settlement-tier map with no manifest is reported as WRONG, never guessed at.
    assert "manifest missing" in _section(page, "hamlets")

    # Mode B, hand-authored, no name/notes/png: stem-derived name, population, missing-render text.
    assert "Beni" in page
    assert "hand-authored" in page
    assert "walled, dispersed" in page
    assert "pop 900" in page
    assert "render not synced" in page

    # Mode A: classified by FOLDER (positively), program read from the notes, compound scale.
    magi = _section(page, "magistracies")
    assert "Kiku Magistracy" in magi
    assert "Mode A compound" in magi
    assert "magistrate&#x27;s manor (county magistracy)" in magi
    assert "1/3 ft/px (3 px = 1 ft)" in magi

    # Column pruning: the magistracies section has no Size/Knobs cells to show, so no such columns;
    # the hamlets section keeps them.
    assert "<th>Size</th>" not in magi and "<th>Knobs</th>" not in magi
    assert "<th>Size</th>" in _section(page, "hamlets")

    # Empty cells in a kept column render as a dash, not as blank space.
    assert "<span class=none>-</span>" in page

    # Nav jump links, one per non-empty section, none for the empty villages folder.
    assert '<a href="#hamlets">Hamlets</a>' in page
    assert "#villages" not in page

    # Sections: known tiers in reading order, the unknown folder appended, empty/skip dirs absent.
    # Tier order within a tree; the tree BANNER (an h2) precedes its tiers (h3s).
    assert page.index('<h3 id="hamlets"') < page.index('<h3 id="towns"') < page.index('<h3 id="magistracies"')
    assert page.index('<h2 class="tree">The live pool') < page.index('<h3 id="hamlets"')
    # ...and the whole live tree precedes the frozen one, which is the reading order the GM chose.
    assert page.index('<h3 id="magistracies"') < page.index('<h2 class="tree">Frozen hand-authored exhibits')
    # The frozen villages section exists in the OTHER tree, and its anchor carries the tree so the
    # two `villages` sections cannot collide.
    assert '<h3 id="legacy-hand-authored-pool-villages"' in page
    assert page.index('<h3 id="magistracies"') < page.index('<h3 id="forts"')
    assert "<h2>Villages</h2>" not in page
    assert "Regressions" not in page and "bad" not in page


def test_build_is_deterministic(tmp_path):
    skill = _mini_pool(tmp_path)
    assert pi.build_index(skill) == pi.build_index(skill)


def test_main_writes_the_file(tmp_path, capsys):
    skill = _mini_pool(tmp_path)
    assert pi.main(["--skill-dir", skill]) == 0
    out = capsys.readouterr().out
    assert "pool-index: wrote" in out
    # The page is written into the LIVE tree, where the GM has always opened it.
    with open(os.path.join(skill, poolmaps.LIVE_TREE, "index.html")) as fh:
        assert '<h3 id="hamlets">Hamlets</h3>' in fh.read()


def test_real_pool_every_gen_is_indexed():
    """Every map in BOTH trees appears on the one page (FR-016)."""
    page = pi.build_index(pi.SKILL_DIR)
    bundles = poolmaps.bundles()
    assert bundles, "the real pool has generators"
    assert any(b.tree == poolmaps.LEGACY_TREE for b in bundles), "the frozen exhibits are indexed too"
    for b in bundles:
        assert b.stem in page, f"{b.tree}/{b.tier}/{b.stem} missing from the index"
    # And no real map is in the manifest-missing state (a red cell here means a map lost its json).
    assert "manifest missing" not in page
