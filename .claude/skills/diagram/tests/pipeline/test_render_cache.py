"""Tests for render_cache - the content-hash short-circuit that regenerates the pool renders in
main. External boundaries (real git check-ignore, real generator subprocesses) are exercised
against a throwaway git repo and trivial fake generators, per the project's fixture-not-mock rule.
"""

from __future__ import annotations

import glob
import os
import subprocess
from pathlib import Path

import pytest

from l7r.diagram.pipeline import render_cache as rc

HERE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))  # the skill root: tests/pipeline/ -> two up

# A trivial stand-in generator: writes <stem>.svg + <stem>.png next to itself (the Mode B naming
# convention render_cache predicts) and records whether the main-tree override reached it.
FAKE_GEN = (
    "import os\n"
    "base = os.path.abspath(__file__)[:-len('.gen.py')]\n"
    "open(base + '.svg', 'w').write('<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 10 10\">\\n<rect/>\\n</svg>')\n"
    "open(base + '.png', 'wb').write(b'PNGDATA')\n"
    "open(base + '.ran', 'w').write(os.environ.get('GM_ASSISTANT_ALLOW_MAIN', 'unset'))\n"
)


def _make_gen(skill: str, tier: str, stem: str, tree: str = "pool") -> str:
    """One map bundle in its OWN folder: <skill>/<tree>/<tier>/<stem>/<stem>.gen.py (feature 161)."""
    d = os.path.join(skill, tree, tier, stem)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, stem + ".gen.py")
    with open(path, "w") as fh:
        fh.write(FAKE_GEN)
    return path


@pytest.fixture
def repo(tmp_path):
    """A throwaway git repo whose .gitignore ignores derived (Mode B) renders under
    pool/villages but keeps pool/magistracies svgs tracked (Mode A source), mirroring the real
    skill. Returns (repo_dir, skill_dir, pool_dir)."""
    repo_dir = str(tmp_path)
    subprocess.run(["git", "-C", repo_dir, "init", "-q"], check=True)
    skill = os.path.join(repo_dir, "skill")
    pool = os.path.join(skill, "pool")
    os.makedirs(pool)
    # engine sources + files the fingerprint must SKIP (non-.py, test_, and the module's own name)
    with open(os.path.join(skill, "settlement.py"), "w") as fh:
        fh.write("# engine v1\n")
    # a PACKAGE engine (feature 025: settlement/ split) - subdir .py files must be fingerprinted
    os.makedirs(os.path.join(skill, "engine_pkg"))
    with open(os.path.join(skill, "engine_pkg", "core.py"), "w") as fh:
        fh.write("# pkg engine v1\n")
    # ...but test packages and the pool/wip trees must not be
    os.makedirs(os.path.join(skill, "test_pkg"))
    with open(os.path.join(skill, "test_pkg", "_builders.py"), "w") as fh:
        fh.write("# excluded: test package helper\n")
    # ...and the tests/ tree, whose files do NOT start with `test_` (the 2026-08-16 reorg moved
    # every test under tests/, so the `test_`-prefix prune alone stopped covering them)
    os.makedirs(os.path.join(skill, "tests", "pipeline"))
    with open(os.path.join(skill, "tests", "__init__.py"), "w") as fh:
        fh.write("# excluded: the tests tree\n")
    with open(os.path.join(skill, "tests", "pipeline", "_builders.py"), "w") as fh:
        fh.write("# excluded: a tests-tree helper\n")
    os.makedirs(os.path.join(skill, "wip"))
    with open(os.path.join(skill, "wip", "draft.gen.py"), "w") as fh:
        fh.write("# excluded: wip\n")
    with open(os.path.join(skill, "waterfields.py"), "w") as fh:
        fh.write("# engine\n")
    with open(os.path.join(skill, "test_engine.py"), "w") as fh:
        fh.write("# excluded: a test file\n")
    with open(os.path.join(skill, "render_cache.py"), "w") as fh:
        fh.write("# excluded: the cache module itself\n")
    with open(os.path.join(skill, "notes.md"), "w") as fh:
        fh.write("excluded: not python\n")
    with open(os.path.join(repo_dir, ".gitignore"), "w") as fh:
        # The real rules are patterns over <tree>/<tier>/<map>/ since feature 161; mirror that
        # depth here, or `is_cacheable` cannot tell Mode A from Mode B.
        fh.write("skill/pool/*/*/*.svg\nskill/pool/*/*/*.png\nskill/pool/*/*/*.html\n!skill/pool/magistracies/*/*.svg\n")
    return repo_dir, skill, pool


def test_sha256_and_predicted_svg():
    assert rc._sha256(b"abc") == rc._sha256(b"abc") != rc._sha256(b"abd")
    assert rc._predicted_svg("/x/foo.gen.py") == "/x/foo.svg"


def test_engine_fingerprint_covers_and_skips(repo):
    _, skill, _ = repo
    fp1 = rc.engine_fingerprint(skill)
    assert len(fp1) == 64
    # editing an engine file changes the fingerprint...
    with open(os.path.join(skill, "settlement.py"), "w") as fh:
        fh.write("# engine v2\n")
    assert rc.engine_fingerprint(skill) != fp1
    # editing a PACKAGE engine file changes it too (feature 025: settlement/ is a package)
    fp_pkg_before = rc.engine_fingerprint(skill)
    with open(os.path.join(skill, "engine_pkg", "core.py"), "w") as fh:
        fh.write("# pkg engine v2\n")
    assert rc.engine_fingerprint(skill) != fp_pkg_before
    # ...but editing a skipped file (test_/non-.py/the module itself/test packages/pool+wip) does not
    with open(os.path.join(skill, "settlement.py"), "w") as fh:
        fh.write("# engine v2\n")
    fp2 = rc.engine_fingerprint(skill)
    for skipped in (
        "test_engine.py",
        "notes.md",
        "render_cache.py",
        os.path.join("test_pkg", "_builders.py"),
        os.path.join("wip", "draft.gen.py"),
        os.path.join("tests", "__init__.py"),
        os.path.join("tests", "pipeline", "_builders.py"),
    ):
        with open(os.path.join(skill, skipped), "w") as fh:
            fh.write("# changed but irrelevant\n")
    assert rc.engine_fingerprint(skill) == fp2


def test_engine_fingerprint_moves_on_a_page_asset(repo):
    """Feature 187 (GM 2026-09-05: "still see the dotted lines. Why is the fix not there?"): the page's
    stylesheet and script are inlined into every <map>.html, so an asset-only landing must stale every
    render. It did not - the walk took .py only - and the mirror served a page from before the change."""
    _, skill, _ = repo
    assets = os.path.join(skill, "interactive", "assets")
    os.makedirs(assets, exist_ok=True)
    for name in ("page.css", "page.js"):
        with open(os.path.join(assets, name), "w") as fh:
            fh.write("/* v1 */\n")
    fp1 = rc.engine_fingerprint(skill)
    with open(os.path.join(assets, "page.css"), "w") as fh:
        fh.write("/* v2: text-decoration: none */\n")
    fp2 = rc.engine_fingerprint(skill)
    assert fp2 != fp1, "a stylesheet edit changes every page and must move the fingerprint"
    with open(os.path.join(assets, "page.js"), "w") as fh:
        fh.write("// v2\n")
    assert rc.engine_fingerprint(skill) != fp2
    # the directory prunes still hold for assets: one under tests/ or a pool tree is not engine content
    fp3 = rc.engine_fingerprint(skill)
    for skipped in (os.path.join("tests", "fixture.css"), os.path.join("wip", "draft.js")):
        with open(os.path.join(skill, skipped), "w") as fh:
            fh.write("/* irrelevant */\n")
    assert rc.engine_fingerprint(skill) == fp3


def test_input_hash_depends_on_gen_and_fingerprint(repo, tmp_path):
    gen = tmp_path / "m.gen.py"
    gen.write_text("A\n")
    h_a = rc.input_hash(str(gen), "fp1")
    assert h_a != rc.input_hash(str(gen), "fp2")  # fingerprint matters
    gen.write_text("B\n")
    assert rc.input_hash(str(gen), "fp1") != h_a  # gen source matters


def test_stamp_roundtrip_and_restamp(tmp_path):
    svg = tmp_path / "m.svg"
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">\n<rect/>\n</svg>')
    h = "a" * 64
    rc.stamp_svg(str(svg), h)
    assert rc.read_stamp(str(svg)) == h
    assert svg.read_text().startswith('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">')
    assert "<rect/>" in svg.read_text()  # body preserved
    # re-stamping replaces cleanly, does not accumulate
    h2 = "b" * 64
    rc.stamp_svg(str(svg), h2)
    assert rc.read_stamp(str(svg)) == h2
    assert svg.read_text().count("render-cache") == 1


def test_read_stamp_missing_and_unstamped(tmp_path):
    assert rc.read_stamp(str(tmp_path / "nope.svg")) is None
    plain = tmp_path / "plain.svg"
    plain.write_text("<svg></svg>")
    assert rc.read_stamp(str(plain)) is None


def test_is_cacheable_reads_gitignore(repo):
    repo_dir, skill, _pool = repo
    mode_b = _make_gen(skill, "villages", "hoshi")
    mode_a = _make_gen(skill, "magistracies", "ochiba")
    assert rc.is_cacheable(mode_b, repo_dir) is True
    assert rc.is_cacheable(mode_a, repo_dir) is False


def test_is_fresh_all_paths(repo):
    _, skill, _pool = repo
    gen = _make_gen(skill, "villages", "hoshi")
    fp = rc.engine_fingerprint(skill)
    svg = rc._predicted_svg(gen)
    png = svg[:-4] + ".png"
    assert rc._is_fresh(gen, fp) is False  # no svg/png yet
    with open(svg, "w") as fh:
        fh.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"></svg>')
    with open(png, "wb") as fh:
        fh.write(b"x")
    assert rc._is_fresh(gen, fp) is False  # svg+png but unstamped
    rc.stamp_svg(svg, "0" * 64)
    assert rc._is_fresh(gen, fp) is False  # stamped, but wrong hash
    rc.stamp_svg(svg, rc.input_hash(gen, fp))
    assert rc._is_fresh(gen, fp) is False  # right hash, but the interactive page is missing (feature 134)
    with open(svg[:-4] + ".html", "w") as fh:
        fh.write("<!DOCTYPE html>")
    assert rc._is_fresh(gen, fp) is True  # stamped with the right hash, all three renders present


def test_regen_pool_runs_stale_skips_fresh_and_exempts_mode_a(repo):
    repo_dir, skill, _pool = repo
    fp = rc.render_fingerprint(skill)
    stale = _make_gen(skill, "villages", "stale")
    fresh = _make_gen(skill, "villages", "fresh")
    mode_a = _make_gen(skill, "magistracies", "ochiba")
    # pre-satisfy the fresh one so it is skipped (svg stamped correctly + png present)
    fsvg = rc._predicted_svg(fresh)
    with open(fsvg, "w") as fh:
        fh.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><SENTINEL/></svg>')
    with open(fsvg[:-4] + ".png", "wb") as fh:
        fh.write(b"OLD")
    with open(fsvg[:-4] + ".html", "w") as fh:
        fh.write("<!DOCTYPE html>")  # the interactive page is the third derived render (feature 134)
    rc.stamp_svg(fsvg, rc.input_hash(fresh, fp))

    skipped, ran, frozen = rc.regen_pool(skill, repo_dir, jobs=2)

    assert skipped == [fresh]
    assert ran == sorted([stale, mode_a])
    assert frozen == []
    # fresh was not re-run: its sentinel svg body survived and its png is untouched
    assert "<SENTINEL/>" in Path(fsvg).read_text()
    assert Path(fsvg[:-4] + ".png").read_bytes() == b"OLD"
    # stale (Mode B) ran and got stamped with the current input hash
    assert rc.read_stamp(rc._predicted_svg(stale)) == rc.input_hash(stale, fp)
    assert Path(rc._predicted_svg(stale)[:-4] + ".ran").read_text() == "1"  # allow_main reached it
    # Mode A ran but its (tracked) svg was NOT stamped
    assert rc.read_stamp(rc._predicted_svg(mode_a)) is None


def test_regen_pool_no_allow_main(repo):
    repo_dir, skill, _pool = repo
    gen = _make_gen(skill, "villages", "m")
    skipped, ran, frozen = rc.regen_pool(skill, repo_dir, jobs=None, allow_main=False)
    assert skipped == [] and ran == [gen] and frozen == []
    assert Path(rc._predicted_svg(gen)[:-4] + ".ran").read_text() == "unset"


def test_engine_fingerprint_moves_on_an_engine_data_file(repo):
    """2026-10-02: `buildings/types.json` decides the kinds a sheet's page writes up, and the walk hashed `.py` only."""
    _, skill, _ = repo
    data = os.path.join(skill, "l7r", "diagram", "buildings")
    os.makedirs(data)
    with open(os.path.join(data, "types.json"), "w") as fh:
        fh.write("{}\n")
    fp1 = rc.engine_fingerprint(skill)
    with open(os.path.join(data, "types.json"), "w") as fh:
        fh.write('{"shrine": {}}\n')
    assert rc.engine_fingerprint(skill) != fp1
    # a data file outside the engine package is not engine content
    fp2 = rc.engine_fingerprint(skill)
    with open(os.path.join(skill, "elsewhere.json"), "w") as fh:
        fh.write("{}\n")
    assert rc.engine_fingerprint(skill) == fp2


def _question(skill: str, name: str, text: str) -> None:
    qdir = os.path.join(skill, "research", "questions")
    os.makedirs(qdir, exist_ok=True)
    with open(os.path.join(qdir, name), "w") as fh:
        fh.write(text)


def test_record_headings_fingerprint_moves_on_a_heading_and_not_on_a_body(repo):
    """A map's page shows each named question's heading, so a renamed heading must re-render the pool; a body edit
    must not, or every research push would re-render every map."""
    _, skill, _ = repo
    empty = rc.record_headings_fingerprint(skill)  # no record at all: the fixture case
    _question(skill, "0001-a.html", '<!-- <h2 id="old">a note</h2> -->\n<h2 id="a">How wide?</h2>\n<p>Body.</p>\n')
    _question(skill, "0002-b.html", "<p>no heading at all</p>\n")
    _question(skill, "notes.txt", "not a question\n")
    fp1 = rc.record_headings_fingerprint(skill)
    assert fp1 != empty
    _question(skill, "0001-a.html", '<!-- <h2 id="old">a note</h2> -->\n<h2 id="a">How wide?</h2>\n<p>New body.</p>\n')
    _question(skill, "notes.txt", "changed\n")
    assert rc.record_headings_fingerprint(skill) == fp1  # body and non-question edits re-render nothing
    _question(skill, "0001-a.html", '<!-- <h2 id="old">changed note</h2> -->\n<h2 id="a">How wide?</h2>\n<p>New body.</p>\n')
    assert rc.record_headings_fingerprint(skill) == fp1  # a commented-out heading is not the heading
    _question(skill, "0001-a.html", '<h2 id="a">How wide was it?</h2>\n<p>New body.</p>\n')
    fp2 = rc.record_headings_fingerprint(skill)
    assert fp2 != fp1
    assert rc.render_fingerprint(skill) != rc.engine_fingerprint(skill)
    before = rc.render_fingerprint(skill)
    _question(skill, "0001-a.html", '<h2 id="a">How wide, really?</h2>\n')
    assert rc.render_fingerprint(skill) != before


# A stand-in Mode A sheet gen: READS its tracked svg and writes the png and page beside it, as the real sheets do.
FAKE_SHEET_GEN = (
    "import os\n"
    "base = os.path.abspath(__file__)[:-len('.gen.py')]\n"
    "svg = open(base + '.svg').read()\n"
    "open(base + '.png', 'w').write('PNG of ' + svg)\n"
    "open(base + '.html', 'w').write('<!DOCTYPE html>')\n"
    "open(base + '.ran', 'a').write('x')\n"
)


def _make_sheet(skill: str, stem: str = "ubame") -> str:
    gen = _make_gen(skill, "magistracies", stem)
    with open(gen, "w") as fh:
        fh.write(FAKE_SHEET_GEN)
    with open(rc._predicted_svg(gen), "w") as fh:
        fh.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect/></svg>')
    return gen


def test_sheet_hash_and_freshness_all_paths(repo):
    _, skill, _ = repo
    gen = _make_sheet(skill)
    fp = rc.render_fingerprint(skill)
    base = gen[: -len(".gen.py")]
    assert rc._sidecar(gen) == os.path.join(os.path.dirname(gen), ".ubame.render-cache")
    h = rc.sheet_hash(gen, fp)
    assert h is not None and h != rc.input_hash(gen, fp)
    assert rc.sheet_hash(gen, "other") != h  # the fingerprint matters
    assert rc._is_fresh_sheet(gen, fp) is False  # no png or page
    Path(base + ".png").write_text("x")
    Path(base + ".html").write_text("x")
    assert rc._is_fresh_sheet(gen, fp) is False  # no sidecar
    Path(rc._sidecar(gen)).write_text("0" * 64 + "\n")
    assert rc._is_fresh_sheet(gen, fp) is False  # wrong value
    Path(rc._sidecar(gen)).write_text(h + "\n")
    assert rc._is_fresh_sheet(gen, fp) is True
    Path(base + ".svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><circle/></svg>')
    assert rc._is_fresh_sheet(gen, fp) is False  # the sheet itself was redrawn
    os.remove(base + ".svg")
    assert rc.sheet_hash(gen, fp) is None
    assert rc._is_fresh_sheet(gen, fp) is False


def test_regen_pool_reruns_a_sheet_only_when_its_inputs_move(repo):
    """The 2026-10-02 timeout: four sheets re-ran on every render-sync (17-28 s), inside every session's prompt hook.
    A sheet now runs once, is stamped beside its tracked svg, and runs again only when the sheet or the engine moves."""
    repo_dir, skill, _pool = repo
    gen = _make_sheet(skill)
    ran_marker = Path(gen[: -len(".gen.py")] + ".ran")
    tracked_svg = Path(rc._predicted_svg(gen)).read_text()
    assert rc.regen_pool(skill, repo_dir, jobs=1)[1] == [gen]
    assert Path(rc._sidecar(gen)).read_text().strip() == rc.sheet_hash(gen, rc.render_fingerprint(skill))
    assert Path(rc._predicted_svg(gen)).read_text() == tracked_svg  # the tracked svg is never stamped
    skipped, ran, _ = rc.regen_pool(skill, repo_dir, jobs=1)
    assert (skipped, ran) == ([gen], [])
    assert ran_marker.read_text() == "x"
    Path(rc._predicted_svg(gen)).write_text('<svg xmlns="http://www.w3.org/2000/svg"><circle/></svg>')
    assert rc.regen_pool(skill, repo_dir, jobs=1)[1] == [gen]  # the sheet redrawn
    with open(os.path.join(skill, "settlement.py"), "w") as fh:
        fh.write("# engine v9\n")
    assert rc.regen_pool(skill, repo_dir, jobs=1)[1] == [gen]  # the engine moved
    assert ran_marker.read_text() == "xxx"


def test_regen_pool_writes_no_sidecar_for_a_sheet_whose_svg_vanished(repo):
    repo_dir, skill, _pool = repo
    gen = _make_gen(skill, "magistracies", "gone")
    with open(gen, "w") as fh:
        fh.write("import os\nopen(os.path.abspath(__file__)[:-len('.gen.py')] + '.png', 'w').write('x')\n")
    assert rc.regen_pool(skill, repo_dir, jobs=1)[1] == [gen]
    assert not os.path.exists(rc._sidecar(gen))


def test_main_reports_and_returns_zero(repo, capsys):
    repo_dir, skill, _pool = repo
    _make_gen(skill, "villages", "m")
    rv = rc.main(["--main-repo", repo_dir, "--skill-dir", skill, "--jobs", "2"])
    assert rv == 0
    out = capsys.readouterr().out
    assert "1 regenerated, 0 cached" in out
    assert "regen  pool/villages/m/m.gen.py" in out


def test_regen_pool_never_reruns_a_frozen_legacy_map(repo, capsys):
    """The 2026-08-16 legacy freeze at the render-sync layer: a gen whose basename is on
    poolmaps.LEGACY_FROZEN_GENS is never re-run - even with no stamp and no renders at all - so
    main's exhibit renders can never be replaced by a drifted engine (a rerun would also rewrite
    the exhibit's tracked .json). A frozen map with a MISSING render is reported loudly by main()
    instead of healed, because healing it with today's engine IS the drift."""
    repo_dir, skill, _pool = repo
    # The basename is what puts it on the frozen list - and it now lives in the legacy TREE,
    # which is where regen_pool has to look to warn about a missing exhibit at all (feature 161).
    frozen_gen = _make_gen(skill, "villages", "minami", tree="legacy-hand-authored-pool")
    live = _make_gen(skill, "villages", "live")
    skipped, ran, frozen = rc.regen_pool(skill, repo_dir, jobs=2)
    assert frozen == [frozen_gen] and ran == [live] and skipped == []
    assert not os.path.exists(rc._predicted_svg(frozen_gen)), "the frozen gen must not even have been run"
    assert rc.main(["--main-repo", repo_dir, "--skill-dir", skill]) == 0
    out = capsys.readouterr().out
    assert "1 frozen" in out and "WARNING: frozen map" in out and "minami.gen.py" in out and "NOT healed" in out
    assert "git checkout" in out  # the renders are committed exhibits, so checkout IS the restore path


def test_main_no_allow_main_flag(repo):
    repo_dir, skill, _pool = repo
    gen = _make_gen(skill, "villages", "m")
    assert rc.main(["--main-repo", repo_dir, "--skill-dir", skill, "--no-allow-main"]) == 0
    assert Path(rc._predicted_svg(gen)[:-4] + ".ran").read_text() == "unset"


@pytest.mark.skipif(
    os.environ.get("L7R_TESTS_FULL") == "1",
    reason="the FULL run regenerates every pool map in parallel workers (the sweep, the cache round trip), so a PNG and its SVG are routinely mid-rewrite when this reads them (feature 145: inashiro.png 44 s older than its SVG); the gate, where nothing rewrites the pool, is where the pairing is judged",
)
def test_every_live_pool_png_matches_its_own_svg_viewbox(pool_tier_glob):
    """A shipped PNG must depict the SVG beside it - the guard that would have caught four hamlets
    shipping the PREVIOUS roll's image while their manifests were current (2026-08-17).

    `render_png` fixes the width at 2600 and lets the height follow the viewBox, so
    `png_h / png_w` must equal `viewBox_h / viewBox_w` to within rounding. That is a cheap,
    decisive test: any mechanism that lets the two drift - the gencache store/load bug this
    accompanies, an interrupted render, a hand-copied file - changes the aspect and fails here.
    Nothing else notices, because the gate reads manifests and never opens the PNG, and
    `crop_map.py` reads the viewBox from the SVG and the pixels from the PNG without checking
    they agree, so a stale render silently mis-registers every crop taken for review."""
    import re
    import struct

    from l7r.diagram.pipeline import poolmaps

    checked = 0
    for gen in sorted(glob.glob(os.path.join(HERE, "pool", pool_tier_glob, "*", "*.gen.py"))):  # the tier's own maps under --tier
        if poolmaps.classify(gen) != "scripted":
            continue  # frozen legacy renders are committed exhibits; Mode A compounds have no viewBox contract here
        stem = gen[: -len(".gen.py")]
        svg_path, png_path = stem + ".svg", stem + ".png"
        if not (os.path.isfile(svg_path) and os.path.isfile(png_path)):
            continue  # renders are gitignored for live maps; a clean checkout simply has none to check
        vb = re.search(r'viewBox="([\d.eE+\- ]+)"', Path(svg_path).read_text()[:4000])
        assert vb, f"{svg_path} has no viewBox"
        _x, _y, vw, vh = (float(v) for v in vb.group(1).split())
        pw, ph = struct.unpack(">II", Path(png_path).read_bytes()[16:24])
        assert abs(round(pw * vh / vw) - ph) <= 2, f"{os.path.basename(png_path)} is {pw}x{ph} but its own SVG renders to {pw}x{round(pw * vh / vw)} - the PNG is not this SVG"
        checked += 1
    # A FRESH CLONE HAS NO LIVE RENDERS AT ALL (they are gitignored, and `make done` never draws one),
    # so this used to fail on every new checkout and read as a regression - feature 131's first gate in
    # the split repository ledgered it as one of two "known gitignored-artifact gap" failures. A guard
    # with nothing to check is not a failed guard; it is a SKIPPED one, and the skip says how to arm it.
    if not checked:
        pytest.skip("no live scripted map has both a .svg and a .png in this checkout - `make map` regenerates the reference hamlet with its render, then this guard has something to check")


def test_main_derives_main_repo_from_this_checkout_when_not_given(tmp_path, monkeypatch):
    # feature 131: the default is the checkout this module lives in, never a hardcoded /gm-assistant
    seen = {}

    def fake_regen(pool_dir, main_repo, **kw):
        seen["main_repo"] = main_repo
        return [], [], []

    monkeypatch.setattr(rc, "regen_pool", fake_regen)
    monkeypatch.setattr(rc.pool_index, "write_index", lambda skill: os.path.join(skill, "index.html"))
    assert rc.main(["--skill-dir", str(tmp_path)]) == 0
    here = os.path.dirname(os.path.abspath(rc.__file__))
    expected = subprocess.run(["git", "-C", here, "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip()
    # `.git` is a directory in a clone and a FILE in a detached worktree (the baseline tree CLAUDE.md
    # prescribes), so test for existence: the assertion is "this is a git checkout", not its shape
    assert seen["main_repo"] == expected and os.path.exists(os.path.join(expected, ".git"))


def test_stale_flat_renders_finds_the_pre_161_leftovers_and_nothing_else(repo):
    """A render left at the OLD flat path is REPORTED, not deleted (feature 161).

    The case is real and hits every tree that had rendered a map before the move: a live map's
    renders are gitignored, so they were never in the commit that moved everything into per-map
    folders - they just stayed put, beside the new folder, no longer ignored and no longer written.
    """
    _, skill, _pool = repo
    gen = _make_gen(skill, "villages", "hoshi")
    d = os.path.dirname(gen)
    assert rc.stale_flat_renders(skill) == [], "a clean tree has no leftovers"

    # the pre-161 shape: <tree>/<tier>/<map>.<ext>, beside the map's own folder
    flat_png = os.path.join(os.path.dirname(d), "hoshi.png")
    Path(flat_png).write_bytes(b"OLD")
    assert rc.stale_flat_renders(skill) == [flat_png]

    # a render INSIDE the map's folder is the current layout and must never be reported
    Path(os.path.join(d, "hoshi.png")).write_bytes(b"NEW")
    assert rc.stale_flat_renders(skill) == [flat_png]

    # a loose render whose map does not exist is something else (a draft, a hand copy): left alone
    Path(os.path.join(os.path.dirname(d), "nosuchmap.png")).write_bytes(b"?")
    assert rc.stale_flat_renders(skill) == [flat_png]

    Path(flat_png).unlink()
    assert rc.stale_flat_renders(skill) == []


def test_main_names_a_stale_flat_render_and_says_it_is_safe_to_delete(repo, capsys):
    repo_dir, skill, _pool = repo
    _make_gen(skill, "villages", "hoshi")
    flat = os.path.join(skill, "pool", "villages", "hoshi.svg")
    Path(flat).write_text("<svg/>")
    assert rc.main(["--main-repo", repo_dir, "--skill-dir", skill]) == 0
    out = capsys.readouterr().out
    assert "ORPHAN" in out and "pool/villages/hoshi.svg" in out and "safe to delete" in out


def test_replate_page_rolls_the_page_when_the_fingerprint_moved_and_skips_when_it_did_not(repo, monkeypatch):
    """Feature 227 FR-005: the placement page is re-plated by the landing when the engine (docstrings included - the
    fingerprint is over bytes) moved, and left alone when the stamp beside it holds the current fingerprint."""
    import os

    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        os.makedirs(os.path.join(repo, rc.PAGE_DIR), exist_ok=True)
        with open(os.path.join(repo, rc.PAGE_DIR, "hamlet-placement.html"), "w") as fh:
            fh.write("<title>x</title>")

    _repo_dir, repo, _pool = repo  # the fixture's skill dir
    monkeypatch.setattr(rc.subprocess, "run", fake_run)
    assert rc.replate_page(repo, "fp-1") is True and len(calls) == 1 and calls[0][1:3] == ["-m", "l7r.diagram.tools.placement_stages"]
    assert rc.replate_page(repo, "fp-1") is False and len(calls) == 1, "the stamp matches: no roll"
    assert rc.replate_page(repo, "fp-2") is True and len(calls) == 2, "the engine moved: re-plated"


def test_main_replates_the_placement_page_in_a_tree_that_carries_the_tool(repo, monkeypatch, capsys):
    """Feature 227 FR-005: the landing's render step re-plates the walk-through page (a fixture without the tool
    skips it, as the other main tests do)."""
    import os

    repo_dir, skill, _pool = repo
    _make_gen(skill, "villages", "m")
    os.makedirs(os.path.join(skill, "l7r", "diagram", "tools"), exist_ok=True)
    with open(os.path.join(skill, "l7r", "diagram", "tools", "placement_stages.py"), "w") as fh:
        fh.write("# the page tool\n")
    monkeypatch.setattr(rc, "replate_page", lambda skill_dir, fingerprint, allow_main=True: True)
    assert rc.main(["--main-repo", repo_dir, "--skill-dir", skill, "--jobs", "2"]) == 0
    assert "placement page re-plated" in capsys.readouterr().out


def test_the_page_is_re_plated_only_when_the_class_registry_moved(tmp_path, monkeypatch):
    """Feature 278 (FR-013): sync-in re-plates the placement page when the classes it was plated from differ from the
    registry - a page with a stale stamp or none is re-plated, a current one is not, and a clone with no page is left
    alone (the test that reads it skips)."""
    calls: list[str] = []
    page_dir = tmp_path / rc.PAGE_DIR
    monkeypatch.setattr(rc, "engine_fingerprint", lambda skill: "fp")

    def fake_replate(skill, fingerprint, allow_main=True):
        calls.append(fingerprint)
        (page_dir / ".classes").write_text(rc.classes_fingerprint() + "\n")
        return True

    monkeypatch.setattr(rc, "replate_page", fake_replate)
    assert rc.replate_if_classes_moved(str(tmp_path)) is False and calls == [], "no page yet: nothing to refresh"
    page_dir.mkdir(parents=True)
    (page_dir / "hamlet-placement.html").write_text("<html></html>")
    assert rc.replate_if_classes_moved(str(tmp_path)) is True and calls == ["fp"], "a page plated before the stamp existed"
    assert rc.replate_if_classes_moved(str(tmp_path)) is False and calls == ["fp"], "the stamp matches the registry"
    (page_dir / ".classes").write_text("an older registry\n")
    assert rc.replate_if_classes_moved(str(tmp_path)) is True and len(calls) == 2, "the registry moved"


def test_main_page_if_classes_reports_and_stops(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(rc, "replate_if_classes_moved", lambda skill, allow_main=False: False)
    assert rc.main(["--skill-dir", str(tmp_path), "--page-if-classes"]) == 0
    assert "placement page current" in capsys.readouterr().out


def test_regen_pool_runs_at_most_render_jobs_maps_by_default(repo, monkeypatch):
    """Feature 324 FR-003: no `jobs` means RENDER_JOBS generators at once - never more than the cores; `jobs` still sets it."""
    import concurrent.futures  # noqa: PLC0415

    repo_dir, skill, _pool = repo
    _make_gen(skill, "villages", "m")
    seen: list[int] = []
    real = concurrent.futures.ThreadPoolExecutor

    class Recorded(real):  # type: ignore[misc, valid-type]
        def __init__(self, max_workers=None, *a, **k):  # type: ignore[no-untyped-def]
            seen.append(max_workers)
            super().__init__(max_workers, *a, **k)

    monkeypatch.setattr(concurrent.futures, "ThreadPoolExecutor", Recorded)
    monkeypatch.setattr(rc.os, "cpu_count", lambda: 22)
    rc.regen_pool(skill, repo_dir, allow_main=False)
    monkeypatch.setattr(rc.os, "cpu_count", lambda: 2)
    rc.regen_pool(skill, repo_dir, allow_main=False)
    rc.regen_pool(skill, repo_dir, jobs=7, allow_main=False)
    assert seen == [rc.RENDER_JOBS, 2, 7] and rc.RENDER_JOBS == 4, seen
