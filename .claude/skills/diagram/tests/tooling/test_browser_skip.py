"""Feature 206 (GM 2026-09-07): the synthetic-page browser tests are skipped while nothing they read changed.

Two halves. The KEY (`gate-stamp.py`'s `browser` area): it holds exactly what the tests read, it goes stale
when any one of those files or the installed browser changes, and the push's `--check` never treats it as an
obligation. The WIRING (the Makefile's recipe text, in `test_page_check.py`'s style): the test phase carries
the skip, `page-check` and `done`'s phases-run exit earn the stamp, the short-circuit does not.

The fixture repository is built by hand rather than pointed at this checkout, so a stamp written here never
lands in the real `.git` and the salt can be replaced without touching the machine's Playwright."""

from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess
from typing import Any

import pytest

pytestmark = pytest.mark.tooling

SKILL = pathlib.Path(__file__).resolve().parents[2]
REPO = SKILL.parents[2]
MAKEFILE = (SKILL / "Makefile").read_text(encoding="utf-8")
PACKAGE = "tests/full/interactive/page_browser"


def _gate_stamp() -> Any:
    spec = importlib.util.spec_from_file_location("gate_stamp_206", REPO / "scripts" / "gate-stamp.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _recipe(target: str) -> str:
    start = re.search(rf"^{re.escape(target)}:(?!\s*export\b)", MAKEFILE, re.M)
    assert start, f"the Makefile has a `{target}` target"
    rest = MAKEFILE[start.end() :]
    nxt = re.search(r"^[a-zA-Z][\w-]*:", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


# ---------------------------------------------------------------------------------------------------
# THE KEY
# ---------------------------------------------------------------------------------------------------


def test_the_browser_area_is_what_the_synthetic_tests_read() -> None:
    """FR-001: the page script and stylesheet, the page writer, a registry module (its docstrings are the
    modals), a module of the test package itself, and a research page (the references modal's links) - and
    nothing under tests/ is excluded from it, though the area shares the diagram area's root, whose
    exclusion list drops tests/ (the reason `_excluded` takes the area name)."""
    gs = _gate_stamp()
    files = {str(f.relative_to(REPO)) for f in gs._area_files(REPO, *gs.AREAS["browser"], area="browser")}
    base = ".claude/skills/diagram/"
    for want in (
        "l7r/diagram/interactive/assets/page.js",
        "l7r/diagram/interactive/assets/page.css",
        "l7r/diagram/interactive/page.py",
        "l7r/diagram/interactive/classes/homestead.py",
        f"{PACKAGE}/test_synthetic.py",
        f"{PACKAGE}/conftest.py",
        "research/fields.html",
    ):
        assert base + want in files, want
    assert not [f for f in files if f.startswith(base + "l7r/diagram/settlement/")], "no engine module outside interactive/"
    assert not [f for f in files if f.startswith(base + "pool/")], "no map"
    assert "browser" in gs.RAW_AREAS, "docstrings are page prose: hashed by bytes (spec D3 of 189, carried here)"
    assert "browser" in gs.SKIP_ONLY_AREAS and "page" not in gs.SKIP_ONLY_AREAS and "diagram" not in gs.SKIP_ONLY_AREAS
    assert gs.exclusions("browser") == (), "the browser area excludes nothing - its test package is its own input"


@pytest.fixture
def repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """A checkout with a remote `main`, holding one file of each kind the browser area names."""
    env = {
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }

    def git(*args: str, cwd: pathlib.Path) -> None:
        subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=True,
            capture_output=True,
            env={**env, "PATH": "/usr/bin:/bin"},
        )

    main = tmp_path / "main"
    main.mkdir()
    git("init", "-q", "-b", "main", cwd=main)
    skill = main / ".claude/skills/diagram"
    for rel, text in {
        "l7r/diagram/interactive/page.py": "def render_page():\n    return 1\n",
        "l7r/diagram/interactive/assets/page.css": "body{}\n",
        "l7r/diagram/interactive/assets/page.js": "1;\n",
        f"{PACKAGE}/test_synthetic.py": "def test_x(): pass\n",
        "research/fields.html": "<h2>Why</h2>\n",
        "l7r/diagram/settlement/houses.py": "x = 1\n",
    }.items():
        p = skill / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    (main / "README.md").write_text("doc\n")
    git("add", "-A", cwd=main)
    git("commit", "-qm", "base", cwd=main)
    clone = tmp_path / "clone"
    git("clone", "-q", str(main), str(clone), cwd=tmp_path)
    return clone


def _stale(gs: Any, root: pathlib.Path) -> bool:
    return gs.fresh("browser", root) != 0


def test_the_stamp_goes_stale_when_any_input_or_the_browser_changes(repo: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """FR-001/FR-006: written, the stamp is fresh; one byte in the stylesheet, the page writer's docstring
    (bytes, not the semantic id), the test package, or a research page makes it stale; so does a different
    installed browser; an engine module outside the area does not."""
    gs = _gate_stamp()
    monkeypatch.setattr(
        gs,
        "_salt",
        lambda area: "playwright=1;chromium=chromium-1" if area == "browser" else "",
    )
    assert _stale(gs, repo), "no stamp yet"
    gs.write_stamp("browser", repo)
    assert not _stale(gs, repo)
    skill = repo / ".claude/skills/diagram"
    for rel in (
        "l7r/diagram/interactive/assets/page.css",
        "l7r/diagram/interactive/page.py",
        f"{PACKAGE}/test_synthetic.py",
        "research/fields.html",
    ):
        with open(skill / rel, "a") as fh:
            fh.write("# touched\n" if rel.endswith(".py") else "\n")
        assert _stale(gs, repo), rel
        gs.write_stamp("browser", repo)
        assert not _stale(gs, repo)
    with open(skill / "l7r/diagram/settlement/houses.py", "a") as fh:
        fh.write("y = 2\n")
    assert not _stale(gs, repo), "an engine module the tests never read does not re-run them"
    monkeypatch.setattr(
        gs,
        "_salt",
        lambda area: "playwright=2;chromium=chromium-2" if area == "browser" else "",
    )
    assert _stale(gs, repo), "a browser upgrade is an input to a browser test (spec D3)"


def test_check_never_demands_a_browser_stamp(repo: pathlib.Path) -> None:
    """FR-004: a delta that changes only a research page and a browser test, with NO browser stamp present,
    passes the push's `--check` - the key is what the gate may skip on, never an obligation (a research or
    test edit owes no gate at push, feature 132 FR-024)."""
    gs = _gate_stamp()
    skill = repo / ".claude/skills/diagram"
    with open(skill / "research/fields.html", "a") as fh:
        fh.write("<h2>More</h2>\n")
    with open(skill / f"{PACKAGE}/test_synthetic.py", "a") as fh:
        fh.write("def test_y(): pass\n")
    subprocess.run(
        ["git", "commit", "-qam", "research and a test"],
        cwd=repo,
        check=True,
        capture_output=True,
        env={
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
            "PATH": "/usr/bin:/bin",
        },
    )
    assert gs.check("origin/main", repo) == 0
    assert not (repo / ".git" / "gate-green-browser").exists(), "and no stamp was needed to get there"


def test_the_real_salt_names_the_installed_browser() -> None:
    """D3: the salt is read from the package metadata and the browser cache's directory names, never by
    launching a browser - and every other area has none."""
    gs = _gate_stamp()
    pytest.importorskip("playwright")
    salt = gs._salt("browser")
    assert salt.startswith("playwright=") and ";chromium=" in salt, salt
    assert gs._salt("page") == "" and gs._salt("diagram") == "" and gs._salt("hooks") == ""


# ---------------------------------------------------------------------------------------------------
# THE WIRING
# ---------------------------------------------------------------------------------------------------


def test_the_test_phase_skips_the_package_on_a_fresh_stamp_and_says_so() -> None:
    """FR-002: BROWSER_SKIP asks `--fresh browser` and is the ignore flag; the `test` recipe's pytest line
    carries it and prints one line when it is set; nothing forces either direction."""
    define = re.search(r"^BROWSER_SKIP = (.*)$", MAKEFILE, re.M)
    assert define, "BROWSER_SKIP is defined"
    assert "--fresh browser" in define.group(1) and f"--ignore={PACKAGE}" in define.group(1)
    body = _recipe("test")
    assert body.count("$(BROWSER_SKIP)") >= 2, "both pytest lines (with and without xdist) carry the skip"
    assert "$(if $(BROWSER_SKIP),printf" in body, "the skip is announced in one line"
    assert "BROWSER_ALL" not in MAKEFILE, "no flag forces either direction (the spec review struck one)"


def test_page_check_and_the_phases_run_exit_earn_the_stamp_and_the_short_circuit_does_not() -> None:
    """FR-003: `page-check` always runs the package and writes the browser stamp; `done`'s phases-run exit
    writes it only when BROWSER_SKIP was empty for that run; the already-verified short-circuit, which ran
    nothing, writes none."""
    assert 'gate-stamp.py" --write browser' in _recipe("page-check")
    body = _recipe("done")
    short = re.search(r"verified-done; then(.*?)exit 0;", body, re.S)
    assert short and "--write browser" not in short.group(1), "the short-circuit ran nothing"
    after = body[short.end() :]
    assert '$(if $(BROWSER_SKIP),,[ -n "$$root" ] && python3 "$$root/scripts/gate-stamp.py" --write browser' in after
    assert "--write page" in after and after.index("--write page") < after.index("--write browser"), "after the page stamp, in the phases-run exit"
