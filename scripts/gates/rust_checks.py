#!/usr/bin/env python3
"""The Rust phases' lint and format checks (feature 444 T17, FR-011; `dev/rust-tooling.md` "lint", "format", "function cap").

THE CRATES: every `Cargo.toml` under `rust/` (the rebuilt phases' extension module, FR-010), or the ones `--crate` names (the
tooling fixture, `tests/fixtures/rust/fixture`, which the proof runs and the engine never imports). No crate is no work: until the
first Rust phase lands, `make static` and `make format` run these over nothing and pass.

    lint     `cargo clippy --all-targets -- -D warnings`; the crate's `[lints.clippy]` deny `all` and `pedantic`, the function cap
             (`too_many_lines` at the root `clippy.toml`'s 100, the Python cap's figure) and an `#[allow]` or `#[expect]` with no
             reason (`allow_attributes_without_reason`) - the Rust forms of ruff, PLR0915 and the suppression that says why
    format   `cargo fmt`, or with --check the refusal of a file rustfmt would change (ruff format's Rust form)

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


def run(cmd: str, manifest: pathlib.Path, check: bool) -> subprocess.CompletedProcess[str]:
    if cmd == "lint":
        return cargo(["clippy", "--quiet", "--all-targets"], manifest, ["-D", "warnings"])
    return cargo(["fmt", *(["--check"] if check else [])], manifest)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("cmd", choices=["lint", "format"])
    ap.add_argument("--crate", action="append", default=[], help="a crate directory, relative to the repository")
    ap.add_argument("--check", action="store_true", help="format: refuse, do not rewrite")
    args = ap.parse_args(argv)
    found = crates(ROOT, args.crate)
    if not found:
        print(f"rust-checks: no Rust crate under {CRATES}/ - nothing to {args.cmd}")
        return 0
    bad = 0
    for m in found:
        r = run(args.cmd, m, args.check)
        if r.returncode != 0:
            bad += 1
            print(f"rust-checks: {args.cmd} FAILED on {m.parent.relative_to(ROOT)}\n{r.stdout}{r.stderr}", file=sys.stderr)
    if bad:
        fix = "fix what clippy names (an exception is `#[expect(lint, reason = \"...\")]`)" if args.cmd == "lint" else "run `make format`"
        print(f"rust-checks: {bad} crate(s) failed {args.cmd} - {fix}", file=sys.stderr)
        return 1
    print(f"rust-checks: {args.cmd} clean on {len(found)} crate(s)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.path.insert(0, str(ROOT / "scripts" / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406 T03 (D162): every refusing check records its run

    sys.exit(usage_log.exited("rust_checks", main()))
