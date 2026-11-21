//! The caller's files (feature 451 T86): a red crate whose key reads none of the files of the task running `make closing-checks` is
//! reported apart and not counted; a red crate the caller's files reach - its own, one that builds on it - still fails the check.

use std::process::Command;

use super::*;
use crate::rustc::{caller_reads, CALLER};

/// Two crates in a repository, the fake cargo red on `red`'s manifest alone; `a` builds on `b` by path when `linked`.
fn clone_with(red: &str, linked: bool) -> (TempDir, Held<World>) {
    let (root, ..) = two_crates();
    if linked {
        std::fs::write(
            root.join("rust/a/Cargo.toml"),
            "[package]\n\n[dependencies]\nl7r_b = { path = \"../b\" }\n",
        )
        .unwrap();
    }
    assert!(Command::new("git")
        .arg("-C")
        .arg(&root)
        .args(["init", "-q"])
        .status()
        .unwrap()
        .success());
    let world = world_with(
        &root,
        &format!("case \"$*\" in *rust/{red}/Cargo.toml*) echo 'error: {red} is half-done' >&2; exit 1 ;; esac\nexit 0"),
    );
    (root, world)
}

/// The world with the caller's listing: `files` written to a listing, its path in [`CALLER`].
fn as_caller(root: &Path, world: Held<World>, files: &[&str]) -> Held<World> {
    let listing = root.join("caller-files");
    std::fs::write(&listing, files.join("\n") + "\n").unwrap();
    let path = listing.to_string_lossy().into_owned();
    world.map(|w| World {
        root: l7r_shared::env::Rooted::with(root, &[(CALLER, path.as_str())]),
        ..w
    })
}

#[test]
fn another_task_s_red_crate_is_reported_apart_and_not_counted() {
    let (root, world) = clone_with("b", false);
    let whole = answer(&world, "lint", &[], false);
    assert_eq!(whole.code, 1, "with no caller named every crate counts");
    assert!(whole.stderr.contains("lint FAILED on rust/b"));
    let mine = as_caller(&root, world, &["rust/a/src/lib.rs"]);
    let apart = answer(&mine, "lint", &[], false);
    assert_eq!(apart.code, 0, "{}", apart.stderr);
    assert!(
        apart
            .stderr
            .contains("rust-checks: APART lint red on rust/b - another task's")
            && apart.stderr.contains("error: b is half-done")
            && !apart.stderr.contains("FAILED on"),
        "{}",
        apart.stderr
    );
    assert!(apart.stdout.contains(
        "lint clean on 1 crate(s) of this task's; 1 red on another task's files alone, reported apart"
    ));
}

#[test]
fn the_caller_s_own_red_still_fails() {
    let (root, world) = clone_with("b", false);
    let mine = as_caller(&root, world, &["rust/b/src/lib.rs"]);
    let red = answer(&mine, "lint", &[], false);
    assert_eq!(red.code, 1);
    assert!(red.stderr.contains("lint FAILED on rust/b") && !red.stderr.contains("APART"));
}

#[test]
fn a_crate_that_builds_on_the_caller_s_crate_is_the_caller_s() {
    let (root, world) = clone_with("a", true);
    let mine = as_caller(&root, world, &["rust/b/src/lib.rs"]);
    let red = answer(&mine, "lint", &[], false);
    assert_eq!(
        red.code, 1,
        "a builds on b, so b's edit may be what broke it"
    );
    assert!(red.stderr.contains("lint FAILED on rust/a"));
    // its formatting is its own files' alone: b's edit cannot move it
    let format = answer(&mine, "format", &[], true);
    assert_eq!(format.code, 0, "{}", format.stderr);
    assert!(format.stderr.contains("APART format red on rust/a"));
}

#[test]
fn a_listing_it_cannot_judge_by_counts_every_crate() {
    let (root, world) = clone_with("b", false);
    let unread = world.map(|w| World {
        root: l7r_shared::env::Rooted::with(&root, &[(CALLER, "/nonexistent/caller-files")]),
        ..w
    });
    assert_eq!(
        answer(&unread, "lint", &[], false).code,
        1,
        "an unreadable listing"
    );
    let blank = unread.map(|w| World {
        root: l7r_shared::env::Rooted::with(&root, &[(CALLER, "")]),
        ..w
    });
    assert_eq!(answer(&blank, "lint", &[], false).code, 1, "a blank one");
    // no kept key for the check: `hamlet` reads nothing kept
    assert!(caller_reads(
        &blank,
        "hamlet",
        &root.join("rust/b/Cargo.toml"),
        None
    ));
    // outside a repository the tree's ids are empty and no key can be read
    let (bare, ..) = two_crates();
    let world = world_with(&bare, "case \"$*\" in *rust/b/*) exit 1 ;; esac\nexit 0");
    let outside = as_caller(&bare, world, &["rust/a/src/lib.rs"]);
    assert_eq!(
        answer(&outside, "lint", &[], false).code,
        1,
        "no ids, no judgment"
    );
}
