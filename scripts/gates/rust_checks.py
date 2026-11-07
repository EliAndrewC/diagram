#!/usr/bin/env python3
"""The Rust phases' lint and format checks (feature 444 T17, FR-011; `dev/rust-tooling.md` "lint", "format", "function cap").

THE CRATES: every `Cargo.toml` under `rust/` (the rebuilt phases' extension module, FR-010), or the ones `--crate` names (the
tooling fixture, `tests/fixtures/rust/fixture`, which the proof runs and the engine never imports). No crate is no work: until the
first Rust phase lands, `make static` and `make format` run these over nothing and pass.

    lint     `cargo clippy --all-targets -- -D warnings`; the crate's `[lints.clippy]` deny `all` and `pedantic`, the function cap
             (`too_many_lines` at the root `clippy.toml`'s 100, the Python cap's figure) and an `#[allow]` or `#[expect]` with no
             reason (`allow_attributes_without_reason`) - the Rust forms of ruff, PLR0915 and the suppression that says why
    format   `cargo fmt`, or with --check the refusal of a file rustfmt would change (ruff format's Rust form)
    test     `cargo test` (`make rust-test`), the crate's own `#[cfg(test)]` tests
    cover    100% of the crate's lines (`cargo llvm-cov --fail-under-lines 100`), counting BOTH its own tests and the lines Python
             reaches through the extension: the crate's tests run instrumented, the module is built instrumented (maturin), the
             crate's Python driver imports it, and one report reads both profiles. The driver is the crate's `tests/py_driver.py`
             (`--driver` for another) - the module's Python callers, so a `#[pyfunction]` only Python calls is not uncovered

The build goes to a target directory outside the tree, ONE A CLONE (`~/.cache/l7r-cargo-target/<the checkout's name>`), so a check
never writes `target/` into a checkout. WHY ONE A CLONE (feature 444 T16, 2026-11-01): cargo keys a path package's build by its name,
not its path, so every clone sharing one directory shared one test binary - a binary built at 08:25 from main's three source files
(6 tests) read as fresh in a clone whose crate held the field's dozens, and `make rust-test` passed a test written to fail.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
CRATES = "rust"
TARGET = pathlib.Path.home() / ".cache" / "l7r-cargo-target" / ROOT.name
CARGO = pathlib.Path.home() / ".cargo" / "bin" / "cargo"


def crates(root: pathlib.Path, named: list[str]) -> list[pathlib.Path]:
    if named:
        return [(root / n / "Cargo.toml") if not n.endswith("Cargo.toml") else root / n for n in named]
    base = root / CRATES
    return sorted(base.rglob("Cargo.toml")) if base.is_dir() else []


def cargo(args: list[str], manifest: pathlib.Path, after: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    """`cargo <args> --manifest-path <manifest> [-- <after>]`, built into the shared target directory."""
    env = {**os.environ, "CARGO_TARGET_DIR": os.environ.get("CARGO_TARGET_DIR", str(TARGET))}
    exe = str(CARGO) if CARGO.is_file() else "cargo"
    cmd = [exe, *args, "--manifest-path", str(manifest), *(["--", *after] if after else [])]
    return subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)


def features_but(manifest: pathlib.Path, left_out: str) -> list[str]:
    """The cargo feature flags naming every feature of the crate but `left_out` (`[]` when that leaves none)."""
    text = manifest.read_text(encoding="utf-8") if manifest.is_file() else ""
    feats = re.search(r"^\[features\]\n(.*?)(?:^\[|\Z)", text, re.M | re.S)
    names = [m.group(1) for m in re.finditer(r"^([A-Za-z_][\w-]*)\s*=", feats.group(1), re.M)] if feats else []
    rest = [n for n in names if n != left_out]
    return ["--features", ",".join(rest)] if rest else []


def rust_only_features(manifest: pathlib.Path) -> list[str]:
    """The cargo feature flags of a Rust-only build: every feature but `python`, whose doors only a Python caller reaches (the GM
    2026-11-07: "Can we get rid of the python driver now that we've turned off the python stages? Can we go Rust only?") - compiled
    out, so the floor measures no door (the round arbiter on red-gate@2026-11-07T12:03:56Z: never dropped by a filename pattern)."""
    text = manifest.read_text(encoding="utf-8") if manifest.is_file() else ""  # (a manifest that is not there fails at cargo, named)
    feats = re.search(r"^\[features\]\n(.*?)(?:^\[|\Z)", text, re.M | re.S)
    names = [m.group(1) for m in re.finditer(r"^([A-Za-z_][\w-]*)\s*=", feats.group(1), re.M)] if feats else []
    rest = [n for n in names if n != "python"]
    if "python" not in names:
        return ["--all-features"]
    return ["--features", ",".join(rest)] if rest else []


def cover(manifest: pathlib.Path, driver: pathlib.Path | None, work: pathlib.Path, report: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    """Instrument, run the crate's tests and its Python driver, and report at the 100% floor (measured on the fixture 2026-10-30:
    its own tests reach 40% of its lines, its Python driver the rest)."""
    base = {**os.environ, "PATH": f"{CARGO.parent}:{os.environ.get('PATH', '')}", "CARGO_TARGET_DIR": str(work / "target")}
    shown = _env_run([str(_exe()), "llvm-cov", "show-env", "--manifest-path", str(manifest)], base)
    env = dict(base)
    for line in shown.stdout.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            env[k.removeprefix("export ")] = v.strip().strip("'\"")
    # ...ONLY THE LAST RUN'S PROFILES CLEARED, THE BUILD KEPT, AND THE TESTS' BINARY ALONE BUILT (the GM 2026-11-07: "Are we
    # recompiling EVERYTHING every time?"): `llvm-cov clean --workspace` - and `--profraw-only` too, which drops the crate's
    # fingerprints - rebuilt the crate from scratch on every run, twice (its library beside its tests' binary, 31 s with nothing
    # changed); the profiles are deleted here and `--lib` builds the one binary the floor runs
    for old in (work / "target").glob("*.profraw"):
        old.unlink()
    # ...and the library an earlier full build (or the driver's maturin build) left beside it, which llvm-cov's report would read too -
    # its lines from older source, uncovered (measured 2026-11-07: lines past a file's end)
    for old in [*(work / "target" / "debug" / "deps").glob("libl7r_*"), *(work / "target" / "debug" / "maturin").glob("*")]:
        old.unlink() if old.is_file() else shutil.rmtree(old, ignore_errors=True)
    lib = ["--lib", "--quiet", *(["--all-features"] if driver is not None else rust_only_features(manifest)), "--manifest-path", str(manifest)]
    built = _timed("build", [str(_exe()), "test", "--no-run", "--message-format=json", *lib], env)
    # ...and every tests' binary but the one just built, which the report would read too: a build under other features leaves its
    # own beside it, every function in it never run (measured 2026-11-07: each test of the crate counted missed, twice over)
    keep = {json.loads(x).get("executable") for x in built.stdout.splitlines() if x.startswith("{")} - {None}
    if keep:
        crate = pathlib.Path(next(iter(keep))).name.rsplit("-", 1)[0]
        for old in (work / "target" / "debug" / "deps").glob(f"{crate}-*"):
            if str(old) not in keep and old.suffix == "" and os.access(old, os.X_OK):
                old.unlink()
    steps = [built, _timed("tests", [str(_exe()), "test", *lib], env)]
    if driver is not None and driver.is_file():
        steps.append(_env_run(["maturin", "build", "--quiet", "--all-features", "-o", str(work / "dist"), "-m", str(manifest)], env))
        wheels = sorted((work / "dist").glob(f"{lib_name(manifest)}-*.whl"), key=lambda w: w.stat().st_mtime)  # (its own, the newest: a
        # shared build directory holds other crates' wheels too)
        if wheels:
            steps.append(_env_run([sys.executable, "-m", "pip", "install", "--quiet", "--upgrade", "--target", str(work / "site"), str(wheels[-1])], env))
            steps.append(_env_run([sys.executable, str(driver)], {**env, "PYTHONPATH": str(work / "site")}))
    failed = next((s for s in steps if s.returncode != 0), None)
    if failed is not None:
        return failed
    return _env_run([str(_exe()), "llvm-cov", "report", *(report or ["--fail-under-lines", "100"]), "--manifest-path", str(manifest)], env)


def uncovered(manifest: pathlib.Path, driver: pathlib.Path | None, work: pathlib.Path) -> dict[str, list[int]]:
    """Each source file of the crate with the lines neither its tests nor its Python driver reach (`make cover-changed`'s Rust
    form, `dev/rust-tooling.md` "changed modules' coverage"), read from llvm-cov's LCOV report."""
    lcov = work / "lcov.info"
    r = cover(manifest, driver, work, ["--lcov", "--output-path", str(lcov)])
    if r.returncode != 0 or not lcov.is_file():
        # ...and says why: a failing test or Python driver line otherwise reads as every file uncovered at line 0
        print(
            f"rust-checks: the coverage run failed on {manifest.parent.name} - fix what it names (a failing test or driver line), then ask again:\n{r.stdout[-4000:]}{r.stderr[-4000:]}",
            file=sys.stderr,
        )
        return {str(manifest.parent): [0]}  # the run itself failed: the crate, not a line, is uncovered
    return lcov_missed(lcov.read_text(encoding="utf-8"))


#: A mangled name's crate hash (`Cs<hash>_` in v0 mangling, `17h<16 hex>E` in the legacy form), which differs build by build.
_BUILD_HASH = re.compile(r"Cs[0-9A-Za-z]+_|17h[0-9a-f]{16}E")


def lcov_missed(text: str) -> dict[str, list[int]]:
    """THE ONE READER OF THE FLOOR, for the gate's `cover` and `make cover-changed` alike (the round arbiter's tooling fix on
    red-gate@2026-11-07T12:03:56Z): each file's lines no test ran (`DA:<line>,0`) and the first line of each function no test called
    (`FNDA:0` - a closure never called counts though its line runs, as llvm-cov's `--fail-under-lines` summary counts it). The gate
    read the summary and cover-changed the lines alone, and refused what cover-changed passed."""
    # (a function is keyed by its file, its first line and its name less the build's crate hash, its calls the most any build of it
    # took: the crate's tests' binary and the driver's extension each carry their own copy, and Python calls only the extension's)
    lines: dict[str, set[int]] = {}
    calls: dict[tuple[str, int, str], int] = {}
    path = ""
    starts: dict[str, int] = {}
    for line in text.splitlines():
        if line.startswith("SF:"):
            path, starts = line[3:], {}
        elif line.startswith("FN:"):
            at, name = line[3:].split(",", 1)
            starts[name] = int(at)
        elif line.startswith("FNDA:"):
            n, name = line[5:].split(",", 1)
            if name in starts:
                key = (path, starts[name], _BUILD_HASH.sub("", name))
                calls[key] = max(calls.get(key, 0), int(n))
        elif line.startswith("DA:") and line[3:].split(",")[1] == "0":
            lines.setdefault(path, set()).add(int(line[3:].split(",")[0]))
    for (p, at, _), n in calls.items():
        if n == 0:
            lines.setdefault(p, set()).add(at)
    return {p: sorted(v) for p, v in lines.items()}


_PUB_FN = re.compile(r"^\s*pub(?:\([^)]*\))?\s+(?:const\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)", re.M)
_PY_FN = re.compile(r"#\[pyfunction\][^{]*?fn\s+([A-Za-z_][A-Za-z0-9_]*)", re.S)


def lib_name(manifest: pathlib.Path) -> str:
    """The module Python imports: the crate's `[lib] name`, else its package name."""
    text = manifest.read_text(encoding="utf-8")
    lib = re.search(r"^\[lib\][^\[]*?^name\s*=\s*\"([^\"]+)\"", text, re.M | re.S)
    pkg = re.search(r"^name\s*=\s*\"([^\"]+)\"", text, re.M)
    return (lib or pkg).group(1).replace("-", "_") if (lib or pkg) else manifest.parent.name


def python_callers(root: pathlib.Path, manifest: pathlib.Path) -> list[pathlib.Path]:
    """THE CHANGE-SELECTED TESTS' PYTHON HALF (`dev/rust-tooling.md` "the change-selected tests"): every Python test - the
    crate's own driver, and every file under `tests/` - that imports the extension; testmon selects by Python lines, so a `.rs`
    change selects none of them unless they are named here."""
    name = lib_name(manifest)
    imports = re.compile(rf"^\s*(?:import|from)\s+(?:[\w.]+\.)?{re.escape(name)}\b", re.M)
    found = [manifest.parent / "tests" / "py_driver.py"]
    found += sorted(p for p in (root / "tests").rglob("*.py") if imports.search(p.read_text(encoding="utf-8", errors="replace"))) if (root / "tests").is_dir() else []
    return [p for p in found if p.is_file()]


def dead_public(root: pathlib.Path, manifest: pathlib.Path) -> list[str]:
    """DEAD CLOSURE'S PUBLIC HALF (`dev/rust-tooling.md` "dead closure"): each `pub fn` of the crate that nothing calls - no other
    use of its name in the crate's Rust, and none in Python (the engine under `l7r/`, the tests, the crate's driver), a
    `#[pyfunction]` counting as called where Python names it. rustc's `dead_code` sees only private items."""
    src = sorted((manifest.parent / "src").rglob("*.rs"))
    rust = "\n".join(p.read_text(encoding="utf-8") for p in src)
    py = "\n".join(p.read_text(encoding="utf-8", errors="replace") for base in (root / "l7r", root / "tests", manifest.parent / "tests") if base.is_dir() for p in base.rglob("*.py"))
    out = []
    for name in sorted(set(_PUB_FN.findall(rust)) | set(_PY_FN.findall(rust))):
        uses = len(re.findall(rf"\b{re.escape(name)}\b", rust)) - 1  # its own definition
        if uses <= 0 and not re.search(rf"\b{re.escape(name)}\b", py):
            out.append(name)
    return out


def _listing(cmd: str, manifest: pathlib.Path) -> subprocess.CompletedProcess[str]:
    """`dead`: refuse a crate with a `pub fn` nothing calls. `callers`: run the Python tests that import the crate's extension
    (`make quick` asks it, so a `.rs` change re-runs its Python callers as testmon cannot)."""
    if cmd == "dead":
        dead = dead_public(ROOT, manifest)
        why = "".join(f"  pub fn {n}: nothing in Rust or Python calls it - delete it, or call it\n" for n in dead)
        return subprocess.CompletedProcess([], 1 if dead else 0, "", why)
    tests = [str(p) for p in python_callers(ROOT, manifest)]
    if not tests:
        return subprocess.CompletedProcess([], 0, "", "")
    work = TARGET / f"callers-{manifest.parent.name}"
    env = {**os.environ, "PATH": f"{CARGO.parent}:{os.environ.get('PATH', '')}", "CARGO_TARGET_DIR": str(TARGET)}
    built = _env_run(["maturin", "build", "--quiet", "--all-features", "-o", str(work / "dist"), "-m", str(manifest)], env)  # as cover builds: the driver reads the counters
    wheels = sorted((work / "dist").glob("*.whl"))
    if built.returncode != 0 or not wheels:
        return built
    _env_run([sys.executable, "-m", "pip", "install", "--quiet", "--upgrade", "--target", str(work / "site"), str(wheels[-1])], dict(os.environ))
    env = {**env, "PYTHONPATH": f"{work / 'site'}{os.pathsep}{ROOT}"}
    runs = [_env_run([sys.executable, t], env) if t.endswith("py_driver.py") else _env_run([sys.executable, "-m", "pytest", "-q", "--no-cov", "-p", "no:cacheprovider", t], env) for t in tests]
    return next((r for r in runs if r.returncode != 0), runs[-1])


EXT = ".rust-ext"  # the built extensions, gitignored: `l7r/diagram/hamletgen/phases_ext.py` puts it on the import path (D8)


def stamp(manifest: pathlib.Path) -> str:
    """The crate's source id: every `.rs` and Cargo file under it, `target/` aside - what a build of it is keyed to."""
    import hashlib  # noqa: PLC0415

    h = hashlib.sha256()
    for p in sorted(manifest.parent.rglob("*")):
        if p.is_file() and "target" not in p.relative_to(manifest.parent).parts and (p.suffix == ".rs" or p.name.startswith("Cargo.")):
            h.update(str(p.relative_to(manifest.parent)).encode() + b"\0" + p.read_bytes())
    return h.hexdigest()[:16]


def build(manifest: pathlib.Path, ext: pathlib.Path) -> subprocess.CompletedProcess[str]:
    """THE BUILD (feature 444 D8): the crate built by maturin with its `counters` feature and installed into `ext`, only when its
    source id moved since the last build there (`<lib>.stamp`)."""
    import fcntl  # noqa: PLC0415

    name = lib_name(manifest)
    mark = ext / f"{name}.stamp"
    now = stamp(manifest)
    ext.mkdir(parents=True, exist_ok=True)
    # ONE BUILD AT A TIME, the stamp read again under the lock (measured 2026-10-30: the test workers each found the stamp stale and
    # ran `pip install --target` into `.rust-ext/` at once, and the installs tore each other's files)
    with (ext / f".{name}.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if mark.is_file() and mark.read_text(encoding="utf-8").strip() == now:
            return subprocess.CompletedProcess([], 0, f"{name}: built\n", "")
        return _build_locked(manifest, ext, name, mark, now)


def _build_locked(manifest: pathlib.Path, ext: pathlib.Path, name: str, mark: pathlib.Path, now: str) -> subprocess.CompletedProcess[str]:
    """`build`'s work, the lock held."""
    env = {**os.environ, "PATH": f"{CARGO.parent}:{os.environ.get('PATH', '')}", "CARGO_TARGET_DIR": str(TARGET)}
    dist = TARGET / f"dist-{name}"
    built = _env_run(["maturin", "build", "--release", "--quiet", "--features", "counters,python", "-o", str(dist), "-m", str(manifest)], env)
    wheels = sorted(dist.glob(f"{name}-*.whl"), key=lambda w: w.stat().st_mtime)
    if built.returncode != 0 or not wheels:
        return built
    put = _env_run([sys.executable, "-m", "pip", "install", "--quiet", "--upgrade", "--no-deps", "--target", str(ext), str(wheels[-1])], dict(os.environ))
    if put.returncode == 0:
        mark.write_text(now + "\n", encoding="utf-8")
    return put


def _exe() -> pathlib.Path | str:
    return CARGO if CARGO.is_file() else "cargo"


def _timed(step: str, cmd: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """`_env_run`, its time printed (the GM 2026-11-07: "the literal most important thing here is making things FAST"): where a
    coverage run's minutes go is read off its own output, not measured again from outside."""
    t = time.monotonic()
    r = _env_run(cmd, env)
    print(f"rust-checks: cover {step} {time.monotonic() - t:.1f} s", file=sys.stderr)
    return r


def _env_run(cmd: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)


def run(cmd: str, manifest: pathlib.Path, check: bool) -> subprocess.CompletedProcess[str]:
    if cmd == "lint":
        return cargo(["clippy", "--quiet", "--all-targets", "--all-features"], manifest, ["-D", "warnings"])
    if cmd == "test":
        return cargo(["test", "--quiet", "--all-features"], manifest)
    if cmd == "test-no-counters":
        # THE COUNTERS CHANGE NO OUTPUT (feature 443 T02, its Rust half since the Python roll's deletion, feature 444 T39): the tests,
        # whose expected values are the same in both builds, pass with the counters compiled out
        return cargo(["test", "--quiet", *features_but(manifest, "counters")], manifest)
    return cargo(["fmt", *(["--check"] if check else [])], manifest)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("cmd", choices=["lint", "format", "test", "test-no-counters", "cover", "dead", "callers", "build"])
    ap.add_argument("--driver", default="", help="cover: the Python driver (default: the crate's tests/py_driver.py)")
    ap.add_argument("--crate", action="append", default=[], help="a crate directory, relative to the repository")
    ap.add_argument("--check", action="store_true", help="format: refuse, do not rewrite")
    args = ap.parse_args(argv)
    found = crates(ROOT, args.crate)
    if not found:
        print(f"rust-checks: no Rust crate under {CRATES}/ - nothing to {args.cmd}")
        return 0
    bad = 0
    for m in found:
        if args.cmd == "build":
            r = build(m, ROOT / EXT)
        elif args.cmd in ("dead", "callers"):
            r = _listing(args.cmd, m)
        elif args.cmd == "cover":
            # ...THE FLOOR READ AS `make cover-changed` READS IT, a line run at least once (the LCOV lines; measured 2026-11-07:
            # llvm-cov's summary counted 7 lines missed where six closures never called share a line with code that runs, and every
            # line of the crate ran - the gate refused what cover-changed passed)
            work = TARGET / f"cover-{m.parent.name}"
            got = uncovered(m, pathlib.Path(args.driver) if args.driver else None, work)
            listing = "".join(f"{p} - lines no test reaches: {', '.join(map(str, v))}\n" for p, v in sorted(got.items()))
            r = subprocess.CompletedProcess([], 1 if got else 0, listing, "")
        else:
            r = run(args.cmd, m, args.check)
        if r.returncode != 0:
            bad += 1
            print(f"rust-checks: {args.cmd} FAILED on {m.parent.relative_to(ROOT)}\n{r.stdout}{r.stderr}", file=sys.stderr)
    if bad:
        fix = {
            "lint": "fix what clippy names (an exception is `#[expect(lint, reason = \"...\")]`)",
            "format": "run `make format`",
            "test": "fix the failing test cargo names",
            "cover": "test the lines llvm-cov names, from the crate's tests or its Python driver",
            "dead": "delete the pub fn it names, or call it",
            "callers": "fix the Python caller that failed (its traceback is above)",
            "build": "fix what maturin names",
        }[args.cmd]
        print(f"rust-checks: {bad} crate(s) failed {args.cmd} - {fix}", file=sys.stderr)
        return 1
    print(f"rust-checks: {args.cmd} clean on {len(found)} crate(s)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.path.insert(0, str(ROOT / "scripts" / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406 T03 (D162): every refusing check records its run

    sys.exit(usage_log.exited("rust_checks", main()))
