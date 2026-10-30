"""The Rust tooling proven on the fixture crate (feature 444 T17, FR-011): each row of `dev/rust-tooling.md` this file names is
shown to FIRE - the check refuses a fixture written to break it and passes the fixture written to keep it. The fixture is
`tests/fixtures/rust/fixture`, a stand-in for the rebuilt phases' extension module the engine never imports. A test here never
skips for want of cargo: an unproven row is what FR-011 forbids before the first Rust phase lands."""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "gates"))
import rust_checks as rc  # noqa: E402

pytestmark = pytest.mark.tooling
FIXTURE = REPO / "tests" / "fixtures" / "rust" / "fixture"


@pytest.fixture(scope="module")
def crate(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """A copy of the fixture to break, built once (its dependencies cached in the shared target directory)."""
    d = tmp_path_factory.mktemp("rust") / "fixture"
    shutil.copytree(FIXTURE, d)
    return d


def _with(crate: pathlib.Path, extra: str) -> pathlib.Path:
    """The fixture with `extra` appended to its lib.rs, in a sibling copy; the original untouched."""
    d = crate.parent / f"broken-{abs(hash(extra)) % 10**8}"
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(crate, d)
    (d / "src" / "lib.rs").write_text((crate / "src" / "lib.rs").read_text() + extra)
    # ITS OWN PACKAGE NAME (measured 2026-10-30): copies sharing the fixture's name in the one target directory were taken by
    # cargo as already checked - a broken copy passed clippy in 2 s with no output, a different test each run
    toml = d / "Cargo.toml"
    toml.write_text(toml.read_text().replace('name = "l7r_fixture"\nversion', f'name = "l7r_fixture_{d.name.replace("-", "_")}"\nversion', 1))
    return d


def test_lint_passes_the_fixture_and_refuses_a_pedantic_breach(crate: pathlib.Path) -> None:
    """Row "lint": clippy, all and pedantic, warnings refused."""
    assert rc.run("lint", crate / "Cargo.toml", check=False).returncode == 0
    broken = _with(crate, "\n/// Casts.\n#[must_use]\npub fn cast(x: u64) -> u32 {\n    x as u32\n}\n")
    r = rc.run("lint", broken / "Cargo.toml", check=False)
    assert r.returncode != 0 and "cast_possible_truncation" in r.stderr, "a pedantic lint is an error"


def test_the_function_cap_refuses_a_function_past_a_hundred_lines(crate: pathlib.Path) -> None:
    """Row "function cap": clippy `too_many_lines` at the root clippy.toml's 100."""
    body = "".join(f"    let v{i} = {i};\n    let _ = v{i};\n" for i in range(52))
    r = rc.run("lint", _with(crate, f"\n/// Long.\npub fn long() {{\n{body}}}\n") / "Cargo.toml", check=False)
    assert r.returncode != 0 and "too_many_lines" in r.stderr


def test_an_exception_with_no_reason_is_refused(crate: pathlib.Path) -> None:
    """Row "function cap": `#[expect]` / `#[allow]` must say why (`allow_attributes_without_reason`)."""
    r = rc.run("lint", _with(crate, "\n/// Casts.\n#[must_use]\n#[allow(clippy::cast_possible_truncation)]\npub fn cast(x: u64) -> u32 {\n    x as u32\n}\n") / "Cargo.toml", check=False)
    assert r.returncode != 0 and "allow_attributes_without_reason" in r.stderr


def test_format_passes_the_fixture_and_refuses_what_rustfmt_would_change(crate: pathlib.Path) -> None:
    """Row "format": rustfmt."""
    assert rc.run("format", crate / "Cargo.toml", check=True).returncode == 0
    broken = _with(crate, "\npub fn  spaced ( ) {}\n")
    assert rc.run("format", broken / "Cargo.toml", check=True).returncode != 0
    assert rc.run("format", broken / "Cargo.toml", check=False).returncode == 0, "make format rewrites it"
    assert rc.run("format", broken / "Cargo.toml", check=True).returncode == 0


def test_the_file_cap_reads_rust_files(tmp_path: pathlib.Path) -> None:
    """Row "file cap": `check-file-scale.py`, reading `.rs`."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "big.rs").write_text("// a line\n" * 1001)
    (tmp_path / "src" / "small.rs").write_text("// a line\n" * 10)
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "gates" / "check-file-scale.py"), str(tmp_path)], capture_output=True, text=True, check=False)
    assert r.returncode != 0 and "big.rs" in r.stdout + r.stderr and "small.rs" not in r.stdout + r.stderr


def test_main_checks_the_named_crates_and_passes_with_none(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    assert rc.main(["lint", "--crate", "tests/fixtures/rust/fixture"]) == 0
    assert "lint clean on 1 crate(s)" in capsys.readouterr().out
    monkeypatch.setattr(rc, "ROOT", tmp_path)
    assert rc.main(["format"]) == 0 and "no Rust crate under rust/" in capsys.readouterr().out
    (tmp_path / "rust" / "bad" / "src").mkdir(parents=True)
    shutil.copy(FIXTURE / "Cargo.toml", tmp_path / "rust" / "bad" / "Cargo.toml")
    (tmp_path / "rust" / "bad" / "src" / "lib.rs").write_text("pub fn  x ( ) {}\n")
    assert rc.main(["format", "--check"]) == 1 and "run `make format`" in capsys.readouterr().err


def test_rust_test_passes_the_fixture_and_refuses_a_failing_test(crate: pathlib.Path) -> None:
    """Row "the make-only guard": a bare cargo is refused (tests/hooks/test-make-only-hooks.sh); `make rust-test` runs it."""
    assert rc.run("test", crate / "Cargo.toml", check=False).returncode == 0
    broken = _with(crate, "\n#[cfg(test)]\nmod failing {\n    #[test]\n    fn fails() {\n        assert_eq!(1, 2);\n    }\n}\n")
    assert rc.run("test", broken / "Cargo.toml", check=False).returncode != 0


def test_coverage_counts_the_lines_python_reaches_and_refuses_an_untested_line(crate: pathlib.Path, tmp_path: pathlib.Path) -> None:
    """Row "coverage and its floors": `cargo llvm-cov --fail-under-lines 100`, plus the Rust lines pytest reaches through the
    extension - the fixture's own tests reach 40% of its lines, its Python driver the rest (measured 2026-10-30)."""
    m = crate / "Cargo.toml"
    assert rc.cover(m, crate / "tests" / "py_driver.py", tmp_path / "w1").returncode == 0, "its tests and its Python caller: every line"
    r = rc.cover(m, None, tmp_path / "w2")
    assert r.returncode != 0, "its own tests alone leave the #[pyfunction] and the module uncovered"
    broken = _with(crate, "\n/// Never called.\n#[must_use]\npub fn unused() -> u64 {\n    7\n}\n")
    assert rc.cover(broken / "Cargo.toml", broken / "tests" / "py_driver.py", tmp_path / "w3").returncode != 0, "an untested line fails"


def test_uncovered_names_the_lines_of_each_file_no_test_reaches(crate: pathlib.Path, tmp_path: pathlib.Path) -> None:
    """Row "changed modules' coverage": llvm-cov per `.rs` file, for `make cover-changed`."""
    assert rc.uncovered(crate / "Cargo.toml", crate / "tests" / "py_driver.py", tmp_path / "u1") == {}
    broken = _with(crate, "\n/// Never called.\n#[must_use]\npub fn unused() -> u64 {\n    7\n}\n")
    got = rc.uncovered(broken / "Cargo.toml", broken / "tests" / "py_driver.py", tmp_path / "u2")
    lib = str(broken / "src" / "lib.rs")
    assert list(got) == [lib] and got[lib], "the new function's lines, in lib.rs"
    assert rc.uncovered(tmp_path / "none" / "Cargo.toml", None, tmp_path / "u3") == {str(tmp_path / "none"): [0]}, "a run that fails"


def test_a_private_item_nothing_calls_is_refused(crate: pathlib.Path) -> None:
    """Row "dead closure": the compiler's dead-code lint, refused under `-D warnings`, for private items."""
    r = rc.run("lint", _with(crate, "\nfn never_called() -> u8 {\n    1\n}\n") / "Cargo.toml", check=False)
    assert r.returncode != 0 and "never_called" in r.stderr and "dead_code" in r.stderr


def test_a_public_function_nothing_calls_is_refused_and_one_python_calls_is_kept(crate: pathlib.Path) -> None:
    """Row "dead closure", its public half: rustc's `dead_code` sees private items only; `rust_checks.py dead` sees a `pub fn`
    nothing in Rust or Python calls - the fixture's `stage_total` is kept, called by its Python driver."""
    assert rc.dead_public(crate.parent / "noroot", crate / "Cargo.toml") == []
    broken = _with(crate, "\n/// Nothing calls it.\n#[must_use]\npub fn orphan() -> u8 {\n    1\n}\n")
    assert rc.dead_public(crate.parent / "noroot", broken / "Cargo.toml") == ["orphan"]
    (broken / "tests" / "py_driver.py").write_text((broken / "tests" / "py_driver.py").read_text() + "assert not hasattr(l7r_fixture, 'orphan')\n")
    assert rc.dead_public(crate.parent / "noroot", broken / "Cargo.toml") == [], "Python naming it counts as a call"


def test_a_rust_change_selects_every_python_test_that_imports_the_extension(crate: pathlib.Path, tmp_path: pathlib.Path) -> None:
    """Row "the change-selected tests", its Python half: testmon selects by Python lines, so a `.rs` change selects the Python
    callers of the extension by their imports - the crate's driver and any test under `tests/` importing it."""
    root = tmp_path / "repo"
    (root / "tests" / "phases").mkdir(parents=True)
    (root / "tests" / "phases" / "test_calls.py").write_text("import l7r_fixture\n")
    (root / "tests" / "phases" / "test_other.py").write_text("import json\n")
    got = rc.python_callers(root, crate / "Cargo.toml")
    assert got == [crate / "tests" / "py_driver.py", root / "tests" / "phases" / "test_calls.py"]
    assert rc.lib_name(crate / "Cargo.toml") == "l7r_fixture"


def test_the_dead_and_callers_commands_run_on_the_named_crate(capsys: pytest.CaptureFixture[str]) -> None:
    assert rc.main(["dead", "--crate", "tests/fixtures/rust/fixture"]) == 0
    assert rc.main(["callers", "--crate", "tests/fixtures/rust/fixture"]) == 0, "the driver runs against the built extension"
    assert "callers clean on 1 crate(s)" in capsys.readouterr().out
