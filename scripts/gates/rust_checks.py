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
    cover    100% of the crate's lines (`cargo llvm-cov --fail-under-lines 100`) by its own tests; no Python reaches the crate
             since the PyO3 doors went with the Python hamlet engine (feature 444 T39)

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


def cover(manifest: pathlib.Path, work: pathlib.Path, report: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    """Instrument, run the crate's tests, and report at the 100% floor."""
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
    # ...and the library an earlier full build left beside it, which llvm-cov's report would read too -
    # its lines from older source, uncovered (measured 2026-11-07: lines past a file's end)
    for old in [*(work / "target" / "debug" / "deps").glob("libl7r_*")]:
        old.unlink() if old.is_file() else shutil.rmtree(old, ignore_errors=True)
    lib = ["--lib", "--quiet", "--all-features", "--manifest-path", str(manifest)]
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
    failed = next((s for s in steps if s.returncode != 0), None)
    if failed is not None:
        return failed
    return _env_run([str(_exe()), "llvm-cov", "report", *(report or ["--fail-under-lines", "100"]), "--manifest-path", str(manifest)], env)


def uncovered(manifest: pathlib.Path, work: pathlib.Path) -> dict[str, list[int]]:
    """Each source file of the crate with the lines its tests do not reach (`make cover-changed`'s Rust
    form, `dev/rust-tooling.md` "changed modules' coverage"), read from llvm-cov's LCOV report."""
    lcov = work / "lcov.info"
    r = cover(manifest, work, ["--lcov", "--output-path", str(lcov)])
    if r.returncode != 0 or not lcov.is_file():
        # ...and says why: a failing test otherwise reads as every file uncovered at line 0
        print(
            f"rust-checks: the coverage run failed on {manifest.parent.name} - fix what it names (a failing test), then ask again:\n{r.stdout[-4000:]}{r.stderr[-4000:]}",
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
    # took: two builds of the crate each carry their own copy)
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


def dead_public(root: pathlib.Path, manifest: pathlib.Path) -> list[str]:
    """DEAD CLOSURE'S PUBLIC HALF (`dev/rust-tooling.md` "dead closure"): each `pub fn` of the crate that nothing calls - no other
    use of its name in the crate's Rust, its binaries (`src/bin/`) among it. rustc's `dead_code` sees only private items."""
    src = sorted((manifest.parent / "src").rglob("*.rs"))
    rust = "\n".join(p.read_text(encoding="utf-8") for p in src)
    out = []
    for name in sorted(set(_PUB_FN.findall(rust))):
        uses = len(re.findall(rf"\b{re.escape(name)}\b", rust)) - 1  # its own definition
        if uses <= 0:
            out.append(name)
    return out


def _listing(manifest: pathlib.Path) -> subprocess.CompletedProcess[str]:
    """`dead`: refuse a crate with a `pub fn` nothing calls."""
    dead = dead_public(ROOT, manifest)
    why = "".join(f"  pub fn {n}: nothing in Rust calls it - delete it, or call it\n" for n in dead)
    return subprocess.CompletedProcess([], 1 if dead else 0, "", why)


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
    if cmd == "hamlet":
        # THE RUST DRIVER (feature 444 T42): a pool hamlet rolled from its spec, built optimized, no Python feature
        # (HAMLET_FEATURES=counters for `make work-budget`'s count: its own build, cached beside the plain one)
        feats = ["--features", os.environ["HAMLET_FEATURES"]] if os.environ.get("HAMLET_FEATURES") else []
        return cargo(["run", "--release", "--quiet", *feats, "--bin", "hamlet"], manifest,os.environ.get("HAMLET_ARGS", "").split() or [os.environ.get("HAMLET_SPEC", "")])
    if cmd == "test-no-counters":
        # THE COUNTERS CHANGE NO OUTPUT (feature 443 T02, its Rust half since the Python roll's deletion, feature 444 T39): the tests,
        # whose expected values are the same in both builds, pass with the counters compiled out
        return cargo(["test", "--quiet", *features_but(manifest, "counters")], manifest)
    return cargo(["fmt", *(["--check"] if check else [])], manifest)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("cmd", choices=["lint", "format", "test", "test-no-counters", "hamlet", "cover", "dead"])
    ap.add_argument("--crate", action="append", default=[], help="a crate directory, relative to the repository")
    ap.add_argument("--check", action="store_true", help="format: refuse, do not rewrite")
    args = ap.parse_args(argv)
    found = crates(ROOT, args.crate)
    if not found:
        print(f"rust-checks: no Rust crate under {CRATES}/ - nothing to {args.cmd}")
        return 0
    bad = 0
    for m in found:
        if args.cmd == "dead":
            r = _listing(m)
        elif args.cmd == "cover":
            # ...THE FLOOR READ AS `make cover-changed` READS IT, a line run at least once (the LCOV lines; measured 2026-11-07:
            # llvm-cov's summary counted 7 lines missed where six closures never called share a line with code that runs, and every
            # line of the crate ran - the gate refused what cover-changed passed)
            work = TARGET / f"cover-{m.parent.name}"
            got = uncovered(m, work)
            listing = "".join(f"{p} - lines no test reaches: {', '.join(map(str, v))}\n" for p, v in sorted(got.items()))
            r = subprocess.CompletedProcess([], 1 if got else 0, listing, "")
        else:
            r = run(args.cmd, m, args.check)
        if args.cmd == "hamlet":
            print(r.stdout, end="")
        if r.returncode != 0:
            bad += 1
            print(f"rust-checks: {args.cmd} FAILED on {m.parent.relative_to(ROOT)}\n{r.stdout}{r.stderr}", file=sys.stderr)
    if bad:
        fix = {
            "lint": "fix what clippy names (an exception is `#[expect(lint, reason = \"...\")]`)",
            "format": "run `make format`",
            "test": "fix the failing test cargo names",
            "cover": "test the lines llvm-cov names, from the crate's tests",
            "dead": "delete the pub fn it names, or call it",
            "hamlet": "fix the stage or the spec the driver names above",
            "test-no-counters": "fix the test whose result hangs on the counters",
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
