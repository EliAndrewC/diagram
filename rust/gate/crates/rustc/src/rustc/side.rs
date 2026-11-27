//! THE CRATES' TESTS SIDE BY SIDE (feature 449 T160; the GM 2026-11-16: "performance improvements to how things are compiled or how
//! long unit tests take to run"): `make rust-test` ran each owed crate's `cargo test` one after another, so no two crates' tests
//! overlapped. After a one-line edit of the `owed` crate the 12
//! crates' tests took 9.8 s in a row for 5.3 s inside their binaries, cargo's freshness check and its doctest pass the rest (observed
//! 2026-11-17, a timing shim on cargo, `make rust-test`). The key's own build already named each crate's test binaries
//! (`kept::binary_key`), so they run here directly, as the coverage pass runs its own (T108), several crates at once. A crate whose
//! binaries were not named - a fresh run asks no key, a build that failed names none - is not here: it runs `cargo test` in
//! `answer`'s loop, one crate at a time as before, whose failure is cargo's to tell.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use super::cover::{next, package_name, side_by_side};
use super::kept::{has_doctests, Verdict};
use super::{alive, cargo_in, leak_checked, own, run_seen, Ran, World};

/// Each owed crate's test run, by manifest: the crates whose kept result does not stand and whose binaries the key's build named, run
/// side by side.
pub(super) fn tests_side_by_side(
    world: &World,
    cmd: &str,
    asked: &[(&PathBuf, Option<(Verdict, bool)>)],
) -> BTreeMap<PathBuf, Ran> {
    let owed: Vec<(&PathBuf, &[String])> = asked
        .iter()
        .filter_map(|(m, a)| match a {
            Some((verdict, false)) if !verdict.exes.is_empty() => {
                Some((*m, verdict.exes.as_slice()))
            }
            _ => None,
        })
        .collect();
    let queue = std::sync::Mutex::new(owed.iter());
    let done = std::sync::Mutex::new(BTreeMap::new());
    std::thread::scope(|s| {
        for _ in 0..side_by_side(owed.len()) {
            s.spawn(|| {
                while let Some((manifest, exes)) = next(&queue) {
                    let ran = run_built(world, cmd, manifest, exes);
                    done.lock()
                        .unwrap_or_else(std::sync::PoisonError::into_inner)
                        .insert((*manifest).clone(), ran);
                }
            });
        }
    });
    done.into_inner()
        .unwrap_or_else(std::sync::PoisonError::into_inner)
}

/// One crate's built test binaries run as `cargo test` runs them - from the crate's directory, with cargo's variables and the run's own
/// `TMPDIR` (`leak_checked`, T101) - in cargo's order, stopping at the first that fails as cargo does; then its doctests, where its
/// sources hold a doc comment's code block, through `cargo test --doc`, the one part of `cargo test` that is no binary.
/// Its `test` phase line is the whole crate's run, binaries and doctests (feature 451 T05).
fn run_built(world: &World, cmd: &str, manifest: &Path, exes: &[String]) -> Ran {
    let dir = manifest.parent().unwrap_or(Path::new("."));
    let began = std::time::SystemTime::now();
    // each binary watched: one run past its bound recorded alive, the first record named on the line (`alive.rs`, feature 451 T463)
    let bound = alive::Bound::of(world, manifest);
    let mut caught = None;
    let ran = leak_checked(manifest, |tmp| {
        let target = world
            .target_override
            .clone()
            .unwrap_or_else(|| world.target.display().to_string());
        // cargo's own bin directory first, as the coverage pass's runs have it (`cover_env`): a test that runs cargo finds it, as it
        // did under `cargo test`, whose toolchain proxy puts it there
        let path = format!(
            "{}:{}",
            world.path_dir.display(),
            std::env::var("PATH").unwrap_or_default()
        );
        let env = BTreeMap::from([
            ("PATH".to_owned(), path),
            ("CARGO_TARGET_DIR".to_owned(), target),
            ("TMPDIR".to_owned(), tmp.display().to_string()),
            ("CARGO".to_owned(), world.cargo.clone()),
            ("CARGO_MANIFEST_DIR".to_owned(), dir.display().to_string()),
            (
                "CARGO_PKG_NAME".to_owned(),
                package_name(manifest).unwrap_or_default(),
            ),
        ]);
        let mut all = Ran {
            code: 0,
            stdout: String::new(),
            stderr: String::new(),
        };
        // a filtered run's words after the binary's own `-q` (`only.rs`, feature 451 T435)
        let mut words = own(&["-q"]);
        words.extend(world.only.iter().cloned());
        let only: Vec<&str> = world.only.iter().map(String::as_str).collect();
        for exe in exes {
            let (ran, got) = run_seen(Some(dir), exe, &words, &env, Some(&bound));
            caught = caught.take().or(got);
            all.stdout.push_str(&ran.stdout);
            all.stderr.push_str(&ran.stderr);
            if ran.code != 0 {
                all.code = ran.code;
                return all;
            }
        }
        if has_doctests(manifest) {
            let mut args = vec!["test", "--doc", "--quiet"];
            if cmd == "test-counters" {
                args.push("--all-features");
            }
            let doc = cargo_in(world, &args, manifest, &only, Some(tmp));
            all.stdout.push_str(&doc.stdout);
            all.stderr.push_str(&doc.stderr);
            all.code = doc.code;
        }
        all
    });
    super::phase::wrote_alive(
        world,
        "test",
        &[manifest],
        began,
        ran.code,
        caught.as_deref(),
    );
    ran
}
