"""`make-docs.py`: the target reference is generated from the Makefile, so it cannot drift.

WHY IT EXISTS (GM 2026-09-05): two hand audits of the make targets disagreed with each other. The
first declared every target valid and was contradicted the moment the GM asked about specific ones -
`tripwire` turned out to be `maps` with a help line that could not be true, and a later pass found
`hamlet-floor-check` and `citybudget` with no live caller at all. A list maintained by hand goes
stale between the writing and the reading; a list derived from the Makefile cannot.

There is no pydoc for make. The `##` help convention was already here and is the de facto standard,
but it yields one flat alphabetical list - no grouping, no argument column, no page. This adds those
and checks the result against its source.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
GUARD = ROOT / "scripts" / "make-docs.py"
PAGE = ROOT / "docs" / "make-targets.html"
MAKEFILE = ROOT / ".claude" / "skills" / "diagram" / "Makefile"


def _mod():
    spec = importlib.util.spec_from_file_location("make_docs", GUARD)
    assert spec and spec.loader
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _check(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(GUARD), str(root), "--check"], capture_output=True, text=True, timeout=300)


def test_the_page_is_current() -> None:
    """The gate runs this; a failure here means someone edited the Makefile and not `make docs`."""
    r = _check(ROOT)
    assert r.returncode == 0, r.stdout + r.stderr


def test_every_documented_target_carries_a_category(tmp_path: Path) -> None:
    """Grouping is EDITORIAL - it exists nowhere else, so it cannot be derived from what code
    declares the way this project derives a roster. The next best thing is to make forgetting it
    impossible: the tag lives on the target's own help line and `--check` fails without it."""
    rows, _ = _mod().parse(MAKEFILE)
    untagged = [r["name"] for r in rows if not r["category"]]
    assert not untagged, f"targets with help text but no [category]: {untagged}"
    assert len(rows) > 50, f"expected the whole target list, parsed {len(rows)}"


def test_it_FIRES_when_the_makefile_gains_a_target(tmp_path: Path) -> None:
    """Delete the guard and this is the test that goes red: a new target must make the page stale."""
    (tmp_path / ".claude" / "skills" / "diagram").mkdir(parents=True)
    (tmp_path / "docs").mkdir()
    mk = tmp_path / ".claude" / "skills" / "diagram" / "Makefile"
    mk.write_text("alpha:          ## [tests] the first one\n\t@true\n", encoding="utf-8")
    subprocess.run([sys.executable, str(GUARD), str(tmp_path), "--write"], capture_output=True, timeout=300)
    assert _check(tmp_path).returncode == 0, "freshly generated, so current"

    mk.write_text(mk.read_text() + "beta:           ## [maps] a target added without regenerating\n\t@true\n", encoding="utf-8")
    r = _check(tmp_path)
    assert r.returncode == 1 and "STALE" in r.stderr, "a new target must make the page stale"


def test_it_FIRES_on_a_target_with_no_category(tmp_path: Path) -> None:
    (tmp_path / ".claude" / "skills" / "diagram").mkdir(parents=True)
    (tmp_path / "docs").mkdir()
    mk = tmp_path / ".claude" / "skills" / "diagram" / "Makefile"
    mk.write_text("alpha:          ## no category tag at all\n\t@true\n", encoding="utf-8")
    r = _check(tmp_path)
    assert r.returncode == 1 and "no [category] tag" in r.stderr


def test_an_undocumented_target_is_REPORTED_not_silently_dropped(tmp_path: Path) -> None:
    """The audit that prompted this found THIRTEEN targets with a recipe and no `##` line - `quick`,
    `maps` and `reference` among them, invisible to `make help` for months. Omitting them quietly is
    how that happened; the page lists them instead."""
    (tmp_path / ".claude" / "skills" / "diagram").mkdir(parents=True)
    (tmp_path / "docs").mkdir()
    mk = tmp_path / ".claude" / "skills" / "diagram" / "Makefile"
    mk.write_text("alpha:          ## [tests] documented\n\t@true\n\nhidden:\n\t@true\n", encoding="utf-8")
    m = _mod()
    rows, undocumented = m.parse(mk)
    assert [r["name"] for r in rows] == ["alpha"] and undocumented == ["hidden"]
    assert "hidden" in m.render(rows, undocumented), "an undocumented target must appear on the page"


def test_the_page_groups_and_names_its_source() -> None:
    page = PAGE.read_text(encoding="utf-8")
    for section in ("Tests", "Maps", "Diagnostics", "Performance", "Remote", "Static checks", "Project state"):
        assert f">{section}" in page or f">{section}<" in page, f"missing section: {section}"
    assert "DO NOT EDIT" in page and "make-docs.py" in page, "the page must say what generates it"
    # `make reference` was here until the GM retired the public rung on 2026-09-06; `static` replaces
    # it as the third probe - a target from a DIFFERENT section, which is what this line is checking.
    assert "make done" in page and "make quick" in page and "make static" in page
