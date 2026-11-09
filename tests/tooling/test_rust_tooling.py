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
def cov_work(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """ONE coverage build directory for the module (the GM 2026-11-07: "the literal most important thing here is making things
    FAST"): each call in its own directory rebuilt PyO3 and the crate instrumented from scratch, 35-57 s a test; the fixture's
    copies carry their own package names, so sharing the directory shares the dependencies and nothing else."""
    return tmp_path_factory.mktemp("cov")


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


def test_coverage_counts_every_line_its_tests_reach_and_refuses_an_untested_line(cov_work: pathlib.Path, crate: pathlib.Path, tmp_path: pathlib.Path) -> None:
    """Row "coverage and its floors": `cargo llvm-cov --fail-under-lines 100` over the crate's own tests (no Python reaches the
    crate since its PyO3 doors went, feature 444 T39)."""
    m = crate / "Cargo.toml"
    assert rc.cover(m, cov_work).returncode == 0, "its tests reach every line"
    broken = _with(crate, "\n/// Never called.\n#[must_use]\npub fn unused() -> u64 {\n    7\n}\n")
    assert rc.cover(broken / "Cargo.toml", cov_work).returncode != 0, "an untested line fails"


def test_uncovered_names_the_lines_of_each_file_no_test_reaches(cov_work: pathlib.Path, crate: pathlib.Path, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Row "changed modules' coverage": llvm-cov per `.rs` file, for `make cover-changed`."""
    assert rc.uncovered(crate / "Cargo.toml", cov_work) == {}
    broken = _with(crate, "\n/// Never called.\n#[must_use]\npub fn unused() -> u64 {\n    7\n}\n")
    got = rc.uncovered(broken / "Cargo.toml", cov_work)
    lib = str(broken / "src" / "lib.rs")
    assert list(got) == [lib] and got[lib], "the new function's lines, in lib.rs"
    assert rc.uncovered(tmp_path / "none" / "Cargo.toml", cov_work) == {str(tmp_path / "none"): [0]}, "a run that fails"
    assert "the coverage run failed on none - fix what it names" in capsys.readouterr().err, "and the failure's output shown"


def test_a_private_item_nothing_calls_is_refused(crate: pathlib.Path) -> None:
    """Row "dead closure": the compiler's dead-code lint, refused under `-D warnings`, for private items."""
    r = rc.run("lint", _with(crate, "\nfn never_called() -> u8 {\n    1\n}\n") / "Cargo.toml", check=False)
    assert r.returncode != 0 and "never_called" in r.stderr and "dead_code" in r.stderr


def test_a_public_function_nothing_calls_is_refused(crate: pathlib.Path) -> None:
    """Row "dead closure", its public half: rustc's `dead_code` sees private items only; `rust_checks.py dead` sees a `pub fn`
    nothing in the crate's Rust calls."""
    assert rc.dead_public(crate.parent / "noroot", crate / "Cargo.toml") == []
    broken = _with(crate, "\n/// Nothing calls it.\n#[must_use]\npub fn orphan() -> u8 {\n    1\n}\n")
    assert rc.dead_public(crate.parent / "noroot", broken / "Cargo.toml") == ["orphan"]


def test_the_dead_command_runs_on_the_named_crate(capsys: pytest.CaptureFixture[str]) -> None:
    assert rc.main(["dead", "--crate", "tests/fixtures/rust/fixture"]) == 0
    assert "dead clean on 1 crate(s)" in capsys.readouterr().out


def test_the_counters_inside_rust_refuse_a_port_that_does_work_it_does_not_count(tmp_path: pathlib.Path) -> None:
    """Row "the overlap census", replaced by the work-budget counters counted inside Rust (feature 444 T19, D9; the round
    arbiter's Route A on ask:444-T17-rows-need-a-phase): the water frame's own test holds its count to the derivation's, so a copy
    of the port that rolls a knob without counting it fails `make rust-test`.

    THE WATER FRAME ALONE, not the whole port (feature 444 T36, measured 2026-11-07: the whole crate's tests and then a fresh build
    of its copy took 20.7 s, run on every Rust edit): the water frame imports only `pyrand`, and `counts` stands alone, so the
    three files are its own crate, built as it is first (the harness proven sound) and then without the count."""
    src = REPO / "rust" / "phases" / "src"
    copy = tmp_path / "uncounted"
    (copy / "src").mkdir(parents=True)
    for name in ("water_frame.rs", "pyrand.rs", "counts.rs"):
        shutil.copy(src / name, copy / "src" / name)
    (copy / "src" / "lib.rs").write_text("mod counts;\nmod pyrand;\nmod water_frame;\n")
    toml = copy / "Cargo.toml"
    toml.write_text('[package]\nname = "l7r_phases_uncounted"\nversion = "0.1.0"\nedition = "2021"\n\n[features]\ncounters = []\n')
    # the counting build: a count's own assertion is compiled out of the default one (the GM 2026-11-07)
    assert rc.run("test-counters", toml, check=False).returncode == 0, "the water frame's own tests pass in the three-file crate"
    frame = copy / "src" / "water_frame.rs"
    text = frame.read_text()
    assert 'counts.add("candidate@roll_plan", 3);' in text
    frame.write_text(text.replace('counts.add("candidate@roll_plan", 3);', "", 1))
    failed = rc.run("test-counters", toml, check=False)
    assert failed.returncode != 0, "a roll it does not count fails the port's own test"
    # ...by the count's own assertion, not a build that broke
    said = failed.stdout + failed.stderr
    assert "src/water_frame.rs" in said and "assertion `left == right` failed" in said, said


def test_the_floor_reads_the_lines_cover_changed_reads(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The gate's `cover` refuses on the LCOV lines no test runs, the measure `make cover-changed` reads (2026-11-07: llvm-cov's
    summary counted a line missed where a closure never called shares it with code that runs, and refused what cover-changed
    passed)."""
    monkeypatch.setattr(rc, "uncovered", lambda m, w: {})
    assert rc.main(["cover", "--crate", "tests/fixtures/rust/fixture"]) == 0
    monkeypatch.setattr(rc, "uncovered", lambda m, w: {"src/lib.rs": [3, 4]})
    assert rc.main(["cover", "--crate", "tests/fixtures/rust/fixture"]) == 1
    assert "src/lib.rs - lines no test reaches: 3, 4" in capsys.readouterr().err


def test_the_one_reader_counts_a_closure_never_called_on_a_line_that_runs() -> None:
    """The round arbiter's tooling fix on red-gate@2026-11-07T12:03:56Z: a line no test ran, and the line a function no test called
    starts on, are both missed - the closure on a line whose other code runs is the case the lines alone passed."""
    text = "SF:/c/src/lib.rs\nFN:3,f\nFN:3,f_closure\nFNDA:4,f\nFNDA:0,f_closure\nDA:3,4\nDA:5,0\nDA:6,2\nend_of_record\nSF:/c/src/b.rs\nFN:1,g\nFNDA:1,g\nDA:1,1\nend_of_record\n"
    assert rc.lcov_missed(text) == {"/c/src/lib.rs": [3, 5]}
    # ...but a function two builds carry, under two names, is called where either build called it
    twice = "SF:/c/src/lib.rs\nFN:7,_RNvCsAAA_3lib1h\nFN:7,_RNvCsBBB_3lib1h\nFNDA:0,_RNvCsAAA_3lib1h\nFNDA:2,_RNvCsBBB_3lib1h\nDA:7,2\nend_of_record\n"
    assert rc.lcov_missed(twice) == {}


def test_a_closure_never_called_is_refused_by_both_commands(cov_work: pathlib.Path, crate: pathlib.Path, tmp_path: pathlib.Path) -> None:
    """Planted on the fixture: a closure no test calls, on a line its test runs - `uncovered` (cover-changed's Rust form and the
    gate's `cover` alike) names its line."""
    broken = _with(
        crate, "\n/// Sums one past each.\n#[must_use]\npub fn bumped(v: &[u64]) -> u64 {\n    v.iter().map(|x| x + 1).sum()\n}\n\n#[test]\nfn bumped_empty() {\n    assert_eq!(bumped(&[]), 0);\n}\n"
    )
    got = rc.uncovered(broken / "Cargo.toml", cov_work)
    lib = str(broken / "src" / "lib.rs")
    assert list(got) == [lib] and got[lib], got


def test_the_counters_change_no_output_refuses_a_test_that_reads_them(crate: pathlib.Path) -> None:
    """Row "the counters change no output" (feature 444 T39): the crate's tests pass with the `counters` feature compiled out,
    so a test whose result hangs on the counters is refused - the Rust half of the old two-roll comparison."""
    broken = _with(crate, "\n#[cfg(test)]\nmod counted {\n    #[test]\n    fn reads_the_counters() {\n        assert!(cfg!(feature = \"counters\"));\n    }\n}\n")
    toml = broken / "Cargo.toml"
    toml.write_text(toml.read_text().replace("[lints.clippy]", "[features]\ncounters = []\n\n[lints.clippy]", 1))
    assert rc.run("test-counters", broken / "Cargo.toml", check=False).returncode == 0, "with every feature it passes"
    assert rc.run("test-no-counters", broken / "Cargo.toml", check=False).returncode != 0, "with the counters out it is refused"
    # ...and the default test is the counters-out build (the GM 2026-11-07: "We should probably run with counters compiled out by default")
    assert rc.run("test", broken / "Cargo.toml", check=False).returncode != 0, "the default build has no counters"


def _two_crates(tmp_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    for name in ("a", "b"):
        (tmp_path / "rust" / name).mkdir(parents=True)
        (tmp_path / "rust" / name / "Cargo.toml").write_text("[package]\n")
    return tmp_path / "rust/a/Cargo.toml", tmp_path / "rust/b/Cargo.toml"


def test_a_crates_key_moves_with_its_own_inputs_and_not_the_other_crates(tmp_path: pathlib.Path) -> None:
    """Feature 449 T060: a one-line edit of one crate ran every check of the other (40 s)."""
    a, b = _two_crates(tmp_path)
    both = [a, b]
    ids = {"rust/a/src/l.rs": "1", "rust/b/src/l.rs": "2", "rust/Cargo.lock": "3", "scripts/x.py": "4", "Makefile": "5"}

    def key(cmd: str, manifest: pathlib.Path, **moved: str) -> str:
        return rc.verdict_key(tmp_path, manifest, cmd, both, {**ids, **{k.replace("__", "/"): v for k, v in moved.items()}}, "cargo 1")

    assert key("lint", a) == rc.verdict_key(tmp_path, a, "lint", both, {**ids, "rust/b/src/l.rs": "9"}, "cargo 1"), "the other crate's edit"
    assert key("lint", a) != rc.verdict_key(tmp_path, a, "lint", both, {**ids, "rust/a/src/l.rs": "9"}, "cargo 1"), "its own edit"
    assert key("lint", a) != rc.verdict_key(tmp_path, a, "lint", both, {**ids, "rust/Cargo.lock": "9"}, "cargo 1"), "the lockfile"
    assert key("lint", a) == rc.verdict_key(tmp_path, a, "lint", both, {**ids, "scripts/x.py": "9"}, "cargo 1"), "lint reads no script"
    assert key("cover", a) != rc.verdict_key(tmp_path, a, "cover", both, {**ids, "Makefile": "9"}, "cargo 1"), "a crate's tests read the repository"
    assert key("cover", a) == rc.verdict_key(tmp_path, a, "cover", both, {**ids, "rust/b/src/l.rs": "9"}, "cargo 1"), "but not the other crate"
    assert key("cover", a) == rc.verdict_key(tmp_path, a, "cover", both, {**ids, "dev/run-log/2026-11/r.json": "9"}, "cargo 1"), "a run's own record"
    assert key("lint", a) != rc.verdict_key(tmp_path, a, "lint", both, ids, "cargo 2"), "a new compiler"
    assert key("lint", a) != key("dead", a), "each check its own"


def test_an_unchanged_crate_keeps_its_green_result_and_a_failure_is_never_kept(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    _two_crates(tmp_path)
    ran: list[str] = []
    verdict = {"code": 0}

    def fake(cmd: str, manifest: pathlib.Path, check: bool) -> subprocess.CompletedProcess[str]:
        ran.append(manifest.parent.name)
        return subprocess.CompletedProcess([], verdict["code"], "", "")

    ids = {"rust/a/src/l.rs": "1", "rust/b/src/l.rs": "2"}
    monkeypatch.setattr(rc, "ROOT", tmp_path)
    monkeypatch.setattr(rc, "run", fake)
    monkeypatch.setattr(rc, "_content_ids", lambda root: ids)
    monkeypatch.setattr(rc, "_compiler", lambda: "cargo 1")
    monkeypatch.setattr(rc, "_kept_path", lambda cmd, m: tmp_path / "kept" / f"{cmd}-{m.parent.name}")
    monkeypatch.delenv("INCREMENTAL", raising=False)
    monkeypatch.delenv("FULL", raising=False)
    assert rc.main(["lint"]) == 0 and ran == ["a", "b"]
    ran.clear()
    assert rc.main(["lint"]) == 0 and ran == [], "nothing moved"
    assert "its last green result stands" in capsys.readouterr().out
    ids["rust/a/src/l.rs"] = "9"
    assert rc.main(["lint"]) == 0 and ran == ["a"], "only the crate that moved"
    ran.clear()
    ids["rust/b/src/l.rs"] = "9"
    verdict["code"] = 1
    assert rc.main(["lint"]) == 1 and ran == ["b"]
    ran.clear()
    assert rc.main(["lint"]) == 1 and ran == ["b"], "a failure is run again, never reused"
    verdict["code"] = 0
    ran.clear()
    monkeypatch.setenv("INCREMENTAL", "0")
    assert rc.main(["lint"]) == 0 and ran == ["a", "b"], "a full run runs everything"
