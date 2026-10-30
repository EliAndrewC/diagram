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
    steps = [_env_run([str(_exe()), "llvm-cov", "clean", "--workspace", "--manifest-path", str(manifest)], env), _env_run([str(_exe()), "test", "--quiet", "--manifest-path", str(manifest)], env)]
    if driver is not None and driver.is_file():
        steps.append(_env_run(["maturin", "build", "--quiet", "-o", str(work / "dist"), "-m", str(manifest)], env))
        wheels = sorted((work / "dist").glob("*.whl"))
        if wheels:
            steps.append(_env_run([sys.executable, "-m", "pip", "install", "--quiet", "--target", str(work / "site"), str(wheels[-1])], env))
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


def _exe() -> pathlib.Path | str:
    return CARGO if CARGO.is_file() else "cargo"


def _env_run(cmd: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)


def run(cmd: str, manifest: pathlib.Path, check: bool) -> subprocess.CompletedProcess[str]:
    if cmd == "lint":
        return cargo(["clippy", "--quiet", "--all-targets"], manifest, ["-D", "warnings"])
    if cmd == "test":
        return cargo(["test", "--quiet"], manifest)
    return cargo(["fmt", *(["--check"] if check else [])], manifest)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("cmd", choices=["lint", "format", "test", "cover"])
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
        if args.cmd == "cover":
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
