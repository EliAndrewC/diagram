//! THE RUNS OF THE CHECKS' PROGRAMS (moved from `rustc.rs` by feature 451 T463, which took it past the 1,000-line bar): a program run to
//! its exit (`run_in`; its pipes read to their end by `drain.rs`), watched past its bound where a test run asks (`run_seen`, `alive.rs`),
//! every cargo call's words, environment and build slot (`cargo_call`, `cargo_in`, `cargo_small`), a crate's watched `cargo test`
//! (`tested`), and the leak pin on a test run's `TMPDIR` (`leak_checked`).

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

use l7r_shared::tempdir::TempDir;

use super::{alive, drain, left, own, slot, test_args, World};

pub(super) struct Ran {
    pub(super) code: i32,
    pub(super) stdout: String,
    pub(super) stderr: String,
}

pub(super) fn run(program: &str, args: &[String], env: &BTreeMap<String, String>) -> Ran {
    run_in(None, program, args, env)
}

/// `run`, from `dir` when one is given: cargo reads `.cargo/config.toml` (rust-lld, feature 449 T96) from its working directory up, so
/// every cargo call runs from the tree's root, whatever directory started `l7r-gate rust`.
pub(super) fn run_in(
    dir: Option<&Path>,
    program: &str,
    args: &[String],
    env: &BTreeMap<String, String>,
) -> Ran {
    run_seen(dir, program, args, env, None).0
}

/// `run_in`, watched where a `bound` is given (a test run, `alive.rs`, feature 451 T463): the record of a run past its bound, its path.
pub(super) fn run_seen(
    dir: Option<&Path>,
    program: &str,
    args: &[String],
    env: &BTreeMap<String, String>,
    bound: Option<&alive::Bound>,
) -> (Ran, Option<PathBuf>) {
    let mut command = Command::new(program);
    if let Some(dir) = dir {
        command.current_dir(dir);
    }
    // a crate's own tests read this tree-from-wrapper variable, and it is this run's, not theirs; the run ends at the program's exit,
    // not at its pipes' end, which a process it left behind can hold (451 T364, `drain.rs`)
    let started = command
        .args(args)
        .envs(env)
        .env_remove("L7R_GATE_TREE")
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn();
    match started {
        Ok(mut child) => {
            let out =
                drain::Reader::start(child.stdout.take().unwrap_or_else(|| unreachable!("piped")));
            let err =
                drain::Reader::start(child.stderr.take().unwrap_or_else(|| unreachable!("piped")));
            let watch = bound.map(|b| b.watch(child.id(), program));
            let status = child.wait();
            let caught = watch.and_then(alive::Watch::ended);
            let (stdout, stderr) = drain::ended(program, &out, &err);
            let code = status.ok().and_then(|s| s.code()).unwrap_or(1);
            (
                Ran {
                    code,
                    stdout,
                    stderr,
                },
                caught,
            )
        }
        Err(e) => (
            Ran {
                code: 127,
                stdout: String::new(),
                stderr: format!("cannot start {program}: {e}\n"),
            },
            None,
        ),
    }
}

pub(super) fn cargo(world: &World, args: &[&str], manifest: &Path, after: &[&str]) -> Ran {
    cargo_in(world, args, manifest, after, None)
}

/// A cargo call's words and its environment, as every cargo call of the checks has them: the manifest named, the tree's own target
/// directory, its tests' `TMPDIR` set to `tmp` where one is given. One builder of both (feature 451 T316), so the pre-warm's test build
/// (`prewarm.rs`) is the build a real run then finds fresh: a word or a variable apart and cargo would build the crate twice.
pub(super) fn cargo_call(
    world: &World,
    args: &[&str],
    manifest: &Path,
    after: &[&str],
    tmp: Option<&Path>,
) -> (Vec<String>, BTreeMap<String, String>) {
    let mut all = own(args);
    all.push("--manifest-path".to_owned());
    all.push(manifest.display().to_string());
    if !after.is_empty() {
        all.push("--".to_owned());
        all.extend(own(after));
    }
    let target = world
        .target_override
        .clone()
        .unwrap_or_else(|| world.target.display().to_string());
    let mut env = BTreeMap::from([("CARGO_TARGET_DIR".to_owned(), target)]);
    if let Some(tmp) = tmp {
        env.insert("TMPDIR".to_owned(), tmp.display().to_string());
    }
    (all, env)
}

/// `cargo`, its tests' `TMPDIR` set to `tmp` where one is given (`leak_checked`).
pub(super) fn cargo_in(
    world: &World,
    args: &[&str],
    manifest: &Path,
    after: &[&str],
    tmp: Option<&Path>,
) -> Ran {
    cargo_seen(world, args, manifest, after, tmp, None).0
}

/// `cargo_in`, watched where a `bound` is given (`run_seen`).
pub(super) fn cargo_seen(
    world: &World,
    args: &[&str],
    manifest: &Path,
    after: &[&str],
    tmp: Option<&Path>,
    bound: Option<&alive::Bound>,
) -> (Ran, Option<PathBuf>) {
    let (all, mut env) = cargo_call(world, args, manifest, after, tmp);
    // every cargo call that compiles holds a build slot for its length (feature 451 T284); `cargo fmt` compiles nothing
    let _slot = (args.first() != Some(&"fmt")).then(|| slot::around(world, &all, &mut env));
    run_seen(Some(&world.root), &world.cargo, &all, &env, bound)
}

/// A crate's `cargo test`, watched (`alive.rs`, feature 451 T463): its result, and the record of a run past its bound.
pub(super) fn tested(world: &World, cmd: &str, manifest: &Path) -> (Ran, Option<PathBuf>) {
    let words = test_args(cmd, manifest, false);
    let args: Vec<&str> = words.iter().map(String::as_str).collect();
    // a filtered run's words after cargo's `--`, to every test binary (`only.rs`, feature 451 T435)
    let only: Vec<&str> = world.only.iter().map(String::as_str).collect();
    let bound = alive::Bound::of(world, manifest);
    let mut caught = None;
    let ran = leak_checked(manifest, |tmp| {
        let (ran, got) = cargo_seen(world, &args, manifest, &only, Some(tmp), Some(&bound));
        caught = got;
        ran
    });
    (ran, caught)
}

/// `cargo`, for a test build or a lint pass told to compile its crate alone (feature 451 T347 and T355, `kept/alone.rs`): the small
/// lane, or a wide slot free at that instant where the lane is held (feature 451 T425, `slot.rs`'s `around_small`), never a place
/// in the wide queue.
pub(super) fn cargo_small(world: &World, args: &[&str], manifest: &Path, after: &[&str]) -> Ran {
    let (all, mut env) = cargo_call(world, args, manifest, after, None);
    let _slot = slot::around_small(world, manifest, &all, &mut env);
    run_in(Some(&world.root), &world.cargo, &all, &env)
}

/// THE LEAK PIN (feature 449 T101): a crate's tests run with their own `TMPDIR`, a fresh directory of this run, and anything a test
/// leaves in it fails the crate, by name, with the fix. The checks and tests that never removed their scratch directories left about
/// 329,000 of them, roughly 126 GB, in the GM's `/tmp` (2026-11-11).
///
/// The directory is under the temp directory itself, so a fixture check that knows a test by its `/tmp/` path still does. A SIGKILL
/// cannot be caught, so a killed test's `Drop` never runs: this runner holds the directory in a `TempDir` and removes it whole after
/// every run, so a killed test's leftovers go too (only a SIGKILL of the runner itself leaves its one directory). A process the tests
/// left running, found by that `TMPDIR` in its environment, fails the crate too, named, and is ended (`left.rs`, 451 T363).
pub(super) fn leak_checked(manifest: &Path, go: impl FnOnce(&Path) -> Ran) -> Ran {
    let name = manifest
        .parent()
        .and_then(Path::file_name)
        .unwrap_or_default();
    let tmp = TempDir::new(&format!("rust-tests-{}", name.to_string_lossy()));
    let mut done = go(&tmp);
    let mut left: Vec<String> = std::fs::read_dir(&tmp)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        // the one directory a whole test process shares (`beside_binary`), which nothing in the process outlives to remove: it goes
        // with this run's directory on the next line
        .filter(|n| n != l7r_shared::tempdir::SHARED)
        .collect();
    // a process the tests left running, found by this run's TMPDIR in its environment, named and ended (`left.rs`, 451 T363)
    let procs = left::ended(&tmp);
    drop(tmp);
    if !procs.is_empty() {
        done.code = 1;
        let _ = writeln!(
            done.stderr,
            "rust-checks: the tests left {} process{} running after they ended, now killed: {}\n  fix: kill and wait what a test \
             starts (`child.kill()` then `child.wait()`, or a guard whose Drop does both), and a stand-in shell that starts a \
             background process waits on it before it exits",
            procs.len(),
            if procs.len() == 1 { "" } else { "es" },
            procs.join(", ")
        );
    }
    if !left.is_empty() {
        left.sort();
        done.code = 1;
        let _ = writeln!(
            done.stderr,
            "rust-checks: the tests left {} entr{} in their TMPDIR, which they must remove: {}\n  fix: hold the directory in an \
             `l7r_shared::tempdir::TempDir` (`TempDir::new(tag)`, or `checks::scratch(tag)`) for as long as the test uses it, so \
             its Drop removes it on a return, a `?` or a panic",
            left.len(),
            if left.len() == 1 { "y" } else { "ies" },
            left.join(", ")
        );
    }
    done
}
