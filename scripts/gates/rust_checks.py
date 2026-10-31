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

The build goes to one target directory outside the tree (`~/.cache/l7r-cargo-target`), so a check never writes `target/` into a
checkout and every clone shares the compiled dependencies.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CRATES = "rust"
TARGET = pathlib.Path.home() / ".cache" / "l7r-cargo-target"
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


def cover(
    manifest: pathlib.Path, driver: pathlib.Path | None, work: pathlib.Path, report: list[str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Instrument, run the crate's tests and its Python driver, and report at the 100% floor (measured on the fixture 2026-10-30:
    its own tests reach 40% of its lines, its Python driver the rest)."""
    base = {**os.environ, "PATH": f"{CARGO.parent}:{os.environ.get('PATH', '')}", "CARGO_TARGET_DIR": str(work / "target")}
    shown = _env_run([str(_exe()), "llvm-cov", "show-env", "--manifest-path", str(manifest)], base)
    env = dict(base)
    for line in shown.stdout.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            env[k.removeprefix("export ")] = v.strip().strip("'\"")
    steps = [_env_run([str(_exe()), "llvm-cov", "clean", "--workspace", "--manifest-path", str(manifest)], env), _env_run([str(_exe()), "test", "--quiet", "--all-features", "--manifest-path", str(manifest)], env)]
    if driver is not None and driver.is_file():
        steps.append(_env_run(["maturin", "build", "--quiet", "--all-features", "-o", str(work / "dist"), "-m", str(manifest)], env))
        wheels = sorted((work / "dist").glob("*.whl"))
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
        return {str(manifest.parent): [0]}  # the run itself failed: the crate, not a line, is uncovered
    out: dict[str, list[int]] = {}
    path = ""
    for line in lcov.read_text(encoding="utf-8").splitlines():
        if line.startswith("SF:"):
            path = line[3:]
        elif line.startswith("DA:") and line[3:].split(",")[1] == "0":
            out.setdefault(path, []).append(int(line[3:].split(",")[0]))
    return out


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
    py = "\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for base in (root / "l7r", root / "tests", manifest.parent / "tests")
        if base.is_dir()
        for p in base.rglob("*.py")
    )
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
    work = TARGET.parent / f"l7r-callers-{manifest.parent.name}"
    env = {**os.environ, "PATH": f"{CARGO.parent}:{os.environ.get('PATH', '')}", "CARGO_TARGET_DIR": str(TARGET)}
    built = _env_run(["maturin", "build", "--quiet", "-o", str(work / "dist"), "-m", str(manifest)], env)
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
    dist = TARGET.parent / f"l7r-dist-{name}"
    built = _env_run(["maturin", "build", "--release", "--quiet", "--features", "counters", "-o", str(dist), "-m", str(manifest)], env)
    wheels = sorted(dist.glob(f"{name}-*.whl"), key=lambda w: w.stat().st_mtime)
    if built.returncode != 0 or not wheels:
        return built
    put = _env_run([sys.executable, "-m", "pip", "install", "--quiet", "--upgrade", "--no-deps", "--target", str(ext), str(wheels[-1])], dict(os.environ))
    if put.returncode == 0:
        mark.write_text(now + "\n", encoding="utf-8")
    return put


def _exe() -> pathlib.Path | str:
    return CARGO if CARGO.is_file() else "cargo"


def _env_run(cmd: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)


def run(cmd: str, manifest: pathlib.Path, check: bool) -> subprocess.CompletedProcess[str]:
    if cmd == "lint":
        return cargo(["clippy", "--quiet", "--all-targets", "--all-features"], manifest, ["-D", "warnings"])
    if cmd == "test":
        return cargo(["test", "--quiet", "--all-features"], manifest)
    return cargo(["fmt", *(["--check"] if check else [])], manifest)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("cmd", choices=["lint", "format", "test", "cover", "dead", "callers", "build"])
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
            work = TARGET.parent / f"l7r-cover-{m.parent.name}"
            r = cover(m, pathlib.Path(args.driver) if args.driver else m.parent / "tests" / "py_driver.py", work)
        else:
            r = run(args.cmd, m, args.check)
        if r.returncode != 0:
            bad += 1
            print(f"rust-checks: {args.cmd} FAILED on {m.parent.relative_to(ROOT)}\n{r.stdout}{r.stderr}", file=sys.stderr)
    if bad:
        fix = {"lint": "fix what clippy names (an exception is `#[expect(lint, reason = \"...\")]`)", "format": "run `make format`", "test": "fix the failing test cargo names", "cover": "test the lines llvm-cov names, from the crate's tests or its Python driver"}[args.cmd]
        print(f"rust-checks: {bad} crate(s) failed {args.cmd} - {fix}", file=sys.stderr)
        return 1
    print(f"rust-checks: {args.cmd} clean on {len(found)} crate(s)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.path.insert(0, str(ROOT / "scripts" / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406 T03 (D162): every refusing check records its run

    sys.exit(usage_log.exited("rust_checks", main()))
