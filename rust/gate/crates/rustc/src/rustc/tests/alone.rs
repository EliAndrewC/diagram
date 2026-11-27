//! The small lane (feature 451 T347): a test build told to compile its crate alone - its key standing in the target directory and
//! no input newer than it - takes the lane and never waits for a wide build slot, at both of a test run's builds; anything else a
//! wide slot.

use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::mpsc::channel;
use std::time::{Duration, SystemTime};

use serde_json::Value;

use super::phases::phases;
use super::runlock::Stepped;
use super::slot::{quick, quiet, telling};
use super::stale::{cache, link_error};
use super::{answer, kept_crates, test_binary, world_with, Reads, World, BINARY_CARGO};
use crate::checks::scratch;
use crate::rustc::kept::alone::{DIR, STEP};
use crate::rustc::slot::{around_small, take, Slots, COUNT, MARK, SMALL, USE};
use crate::rustc::{Kept, Told};
use l7r_shared::tempdir::{Held, TempDir};

const ARGS: [&str; 2] = ["test", "--no-run"];
/// A fake cargo whose test builds fail while a file `fail` lies beside it.
const FAILS: &str = "[ \"$1\" = test ] && [ -f \"$(dirname \"$0\")/fail\" ] && exit 101\nexit 0";
pub(super) const A_BUILDS_FROM_B: &str = "[package]\n[dependencies]\nb = { path = \"../b\" }\n";
/// A fake cargo whose first test build after a file `link-error` lies beside it fails as the linker does, in that file's words.
const LINKS_ONCE: &str = "d=$(dirname \"$0\")\nif [ \"$1\" = test ] && [ -f \"$d/link-error\" ] && [ ! -f \"$d/failed\" ]; then touch \"$d/failed\"; cat \"$d/link-error\" >&2; exit 101; fi\nexit 0";
const B_COMPILES_IN: &str = "const T: &str = include_str!(\"../../../data/table.tsv\");\n";

fn at(path: &Path, when: SystemTime) {
    let file = std::fs::File::options().write(true).open(path).unwrap();
    file.set_modified(when).unwrap();
}

/// `text` at `path`, written long before any build of the test's.
pub(super) fn put(root: &Path, path: &str, text: &str) {
    std::fs::write(root.join(path), text).unwrap();
    at(
        &root.join(path),
        SystemTime::now() - Duration::from_secs(1000),
    );
}

/// Crate `a`, which builds from `b`, which compiles in a table outside both; every file older than any build.
pub(super) fn fixture() -> (TempDir, PathBuf) {
    let (root, a, _) = kept_crates();
    std::fs::create_dir_all(root.join("data")).unwrap();
    for (path, text) in [
        ("rust/Cargo.toml", "[workspace]\n"),
        ("rust/a/Cargo.toml", A_BUILDS_FROM_B),
        ("rust/a/src/lib.rs", "//! x\n"),
        ("rust/b/Cargo.toml", "[package]\n"),
        ("rust/b/src/lib.rs", B_COMPILES_IN),
        ("data/table.tsv", "one\n"),
    ] {
        put(&root, path, text);
    }
    (root, a)
}

/// `count` places in the small lane under `dir`. A wait for one ends at 30 s: a hold a test leaked fails it (`slot-small 1`),
/// and never holds the suite for the real ceiling.
fn lane(dir: &Path, count: usize) -> Slots {
    Slots {
        ceiling: Duration::from_secs(30),
        stem: "small",
        knob: SMALL,
        ..quick(dir, count)
    }
}

/// A world with two wide slots, which a call that finds both held runs without at once (its wait a `slot-wait` line, code 1), and
/// a lane one wide.
pub(super) fn lane_world(root: &Path, body: &str, dir: &Path) -> Held<World> {
    world_with(root, body).map(|w| World {
        slots: Slots {
            ceiling: Duration::ZERO,
            ..quick(dir, 2)
        },
        small: lane(dir, 1),
        ..w
    })
}

fn kept(world: &World, a: &Path) -> Kept {
    Kept::read(world, "test", Reads::Tests, &[a.to_path_buf()])
}

fn alone(world: &World, a: &Path) -> bool {
    Told::of(world, "test", a, &kept(world, a), &ARGS).alone()
}

/// The slot lines written past the first `before`, each as `<step> <code>`.
pub(super) fn since(root: &Path, before: usize) -> Vec<String> {
    let all: Vec<Value> = phases(root);
    all[before..]
        .iter()
        .map(|l| format!("{} {}", l["step"].as_str().unwrap(), l["code"]))
        .filter(|l| l.starts_with("slot-"))
        .collect()
}

#[test]
fn a_build_is_told_alone_only_while_its_key_stands_and_no_input_is_newer() {
    let (root, a) = fixture();
    let dir = scratch("alone-key");
    let world = lane_world(&root, FAILS, &dir);
    let key = world.target.join(DIR).join("rust_a-test");
    // a target directory with no key is not told alone; its build, in a wide slot, keeps its key where it passes
    let first = Told::of(&world, "test", &a, &kept(&world, &a), &ARGS);
    assert!(!first.alone());
    assert_eq!(first.cargo(&world, &ARGS, &a).code, 0);
    assert!(key.is_file() && !key.with_extension("new").exists());
    assert_eq!(since(&root, 0), [format!("{STEP} 1")]);
    assert!(alone(&world, &a));
    assert_eq!(since(&root, 1), [format!("{STEP} 0")]);
    // the crate's own sources and a file no crate owns are not in it
    std::fs::write(root.join("rust/a/src/lib.rs"), "//! moved\n").unwrap();
    std::fs::write(root.join("notes.txt"), "x\n").unwrap();
    assert!(alone(&world, &a));
    // a dependency's content, whatever its time
    put(&root, "rust/b/src/extra.rs", "//! new\n");
    assert!(!alone(&world, &a));
    std::fs::remove_file(root.join("rust/b/src/extra.rs")).unwrap();
    assert!(alone(&world, &a));
    // a dependency's time, whatever its content: newer than the key's file, or at its very instant
    let lib = root.join("rust/b/src/lib.rs");
    at(&lib, SystemTime::now());
    assert!(!alone(&world, &a));
    at(&lib, std::fs::metadata(&key).unwrap().modified().unwrap());
    assert!(!alone(&world, &a));
    put(&root, "rust/b/src/lib.rs", B_COMPILES_IN);
    assert!(alone(&world, &a));
    // a file a dependency compiles in
    put(&root, "data/table.tsv", "two\n");
    assert!(!alone(&world, &a));
    put(&root, "data/table.tsv", "one\n");
    // the workspace's manifest rewritten, and a lockfile
    at(&root.join("rust/Cargo.toml"), SystemTime::now());
    assert!(!alone(&world, &a));
    put(&root, "rust/Cargo.toml", "[workspace]\n");
    put(&root, "rust/Cargo.lock", "x\n");
    assert!(!alone(&world, &a));
    std::fs::remove_file(root.join("rust/Cargo.lock")).unwrap();
    // the crate's own manifest
    put(
        &root,
        "rust/a/Cargo.toml",
        &format!("{A_BUILDS_FROM_B}# c\n"),
    );
    assert!(!alone(&world, &a));
    put(&root, "rust/a/Cargo.toml", A_BUILDS_FROM_B);
    assert!(alone(&world, &a));
    // the compiler, the build's words and the flags it inherits
    let mut other = kept(&world, &a);
    other.compiler.push('2');
    assert!(!Told::of(&world, "test", &a, &other, &ARGS).alone());
    let featured = ["test", "--no-run", "--all-features"];
    assert!(!Told::of(&world, "test", &a, &kept(&world, &a), &featured).alone());
    let flagged = world.map(|w| World {
        root: l7r_shared::env::Rooted::with(root.to_path_buf(), &[("RUSTFLAGS", "-g")]),
        ..w
    });
    assert!(!alone(&flagged, &a));
}

#[test]
fn a_red_build_told_alone_keeps_its_key_and_a_red_wide_build_keeps_none_of_its_own() {
    let (root, a) = fixture();
    let dir = scratch("alone-red");
    let world = lane_world(&root, FAILS, &dir);
    let build = |w: &World| Told::of(w, "test", &a, &kept(w, &a), &ARGS).cargo(w, &ARGS, &a);
    let key = world.target.join(DIR).join("rust_a-test");
    assert_eq!(build(&world).code, 0);
    assert!(alone(&world, &a));
    // told alone and red: no dependency moved, so the key is still true and the next run is told alone again
    std::fs::write(world.target.join("fail"), "").unwrap();
    assert_eq!(build(&world).code, 101);
    assert!(alone(&world, &a));
    // a dependency moved and the build is red: its new key is not kept, and the old one no longer stands
    put(&root, "rust/b/src/extra.rs", "//! new\n");
    let stood = std::fs::read_to_string(&key).unwrap();
    assert_eq!(build(&world).code, 101);
    assert!(!key.with_extension("new").exists());
    assert_eq!(std::fs::read_to_string(&key).unwrap(), stood);
    assert!(!alone(&world, &a));
    std::fs::remove_file(world.target.join("fail")).unwrap();
    assert_eq!(build(&world).code, 0);
    assert!(alone(&world, &a));
    // a file a dependency had and has no more is in the key as gone, and has no time to ask
    put(&root, "rust/b/src/gone.rs", "//! x\n");
    let git = Command::new("git")
        .arg("-C")
        .arg(&*root)
        .args(["add", "rust/b/src/gone.rs"])
        .status();
    assert!(git.unwrap().success());
    std::fs::remove_file(root.join("rust/b/src/gone.rs")).unwrap();
    assert!(!alone(&world, &a));
    assert_eq!(build(&world).code, 0);
    assert!(alone(&world, &a));
    // the key lies in the target directory the build writes: another one holds none
    let other = scratch("alone-other-target");
    let elsewhere = world.map(|w| World {
        target_override: Some(other.display().to_string()),
        ..w
    });
    assert!(!alone(&elsewhere, &a));
    assert_eq!(build(&elsewhere).code, 0);
    assert!(other.join(DIR).join("rust_a-test").is_file());
    assert!(alone(&elsewhere, &a));
    // with no lane nothing is told and nothing kept
    let before = phases(&root).len();
    let plain = world_with(&root, "exit 0");
    let untold = Told::of(&plain, "test", &a, &kept(&plain, &a), &ARGS);
    assert!(!untold.alone());
    assert_eq!(untold.cargo(&plain, &ARGS, &a).code, 0);
    assert!(!plain.target.join(DIR).exists());
    assert_eq!(phases(&root).len(), before);
}

#[test]
fn a_build_told_alone_takes_the_lane_while_both_wide_slots_are_held_and_a_second_waits_behind_it() {
    let (root, a) = fixture();
    let dir = scratch("alone-lane");
    let world = lane_world(&root, "exit 0", &dir);
    let first = Told::of(&world, "test", &a, &kept(&world, &a), &ARGS);
    assert_eq!(first.cargo(&world, &ARGS, &a).code, 0);
    assert_eq!(since(&root, 0), [format!("{STEP} 1")]);
    // both wide slots held
    let one = take(&quick(&dir, 2), "one\n", &mut quiet);
    let two = take(&quick(&dir, 2), "two\n", &mut quiet);
    assert!(one.hold.is_some() && two.hold.is_some());
    // told alone: the lane, at once, and no wide slot asked
    let told = Told::of(&world, "test", &a, &kept(&world, &a), &ARGS);
    assert!(told.alone());
    assert_eq!(told.cargo(&world, &ARGS, &a).code, 0);
    assert_eq!(since(&root, 1), [format!("{STEP} 0"), format!("{USE} 0")]);
    let used = phases(&root).pop().unwrap();
    assert_eq!(used["crates"], serde_json::json!(["rust/a"]));
    let signed = |name: &str| std::fs::read_to_string(dir.join(name)).unwrap();
    assert!(signed("small-0").ends_with("cargo test --no-run\n"));
    // the wide slots are still their holders', whichever took which (a slot the first build let go can read held for a moment,
    // while a child another test's thread is starting has not yet made its exec, so `one` is not always in `slot-0`)
    let mut wide = [signed("slot-0"), signed("slot-1")];
    wide.sort_unstable();
    assert_eq!(wide, ["one\n".to_owned(), "two\n".to_owned()]);
    // a build nothing told is a wide one: both held, so it runs without at its ceiling, and no lane is used
    assert_eq!(Told::wide().cargo(&world, &ARGS, &a).code, 0);
    assert_eq!(since(&root, 3), ["slot-wait 1"]);
    // two small builds at once: the second waits in the lane for the first, and its wait is a `slot-wait` line
    let holder = take(&lane(&dir, 1), "holder\n", &mut quiet).hold;
    assert!(holder.is_some());
    let (slots, waiting) = telling(&dir, 1);
    let patient = world.map(|w| World {
        small: Slots {
            ceiling: Duration::from_secs(30),
            stem: "small",
            knob: SMALL,
            ..slots
        },
        ..w
    });
    let (tell, done) = channel();
    std::thread::scope(|s| {
        s.spawn(|| {
            let _ = tell.send(told.cargo(&patient, &ARGS, &a).code);
        });
        waiting.recv_timeout(Duration::from_secs(30)).unwrap();
        assert!(done.try_recv().is_err());
        drop(holder);
        assert_eq!(done.recv_timeout(Duration::from_secs(30)).unwrap(), 0);
    });
    assert_eq!(
        since(&root, 4),
        ["slot-wait 0".to_owned(), format!("{USE} 0")]
    );
}

#[test]
fn both_builds_of_a_test_run_take_the_lane_they_were_told() {
    let (root, _) = fixture();
    let dir = scratch("alone-run");
    let world = lane_world(&root, BINARY_CARGO, &dir);
    test_binary(&world.target.join("exe"), "binary one");
    let one = take(&quick(&dir, 2), "one\n", &mut quiet);
    let two = take(&quick(&dir, 2), "two\n", &mut quiet);
    assert!(one.hold.is_some() && two.hold.is_some());
    let named = ["rust/a".to_owned()];
    let run = |text: &str| {
        let before = phases(&root).len();
        let code = format!("pub const N: &str = \"{text}\";\n");
        std::fs::write(root.join("rust/a/src/lib.rs"), code).unwrap();
        let code = answer(&world, "test", &named, false).code;
        // a wide wait here ends at its ceiling, code 1; a `slot-wait 0` is a moment's wait in the lane this run's own build before
        // just let go (a slot let go may read held until a child another thread is starting has made its exec, `slot.rs`)
        let mut slots = since(&root, before);
        slots.retain(|l| l != "slot-wait 0");
        (code, slots)
    };
    let lines = |words: &[&str]| -> Vec<String> { words.iter().map(|w| (*w).to_owned()).collect() };
    // the first build in the target directory: a wide slot (both held: it runs without at its ceiling)
    let (code, slots) = run("one");
    assert_eq!(code, 0);
    assert_eq!(slots[..2], lines(&["slot-tell 1", "slot-wait 1"]));
    assert!(!slots.contains(&"slot-small 0".to_owned()), "{slots:?}");
    // the crate's own edit: the binary key's build takes the lane and waits on no wide slot
    assert_eq!(run("two"), (0, lines(&["slot-tell 0", "slot-small 0"])));
    // a red build is asked twice (the binary key's, then `stepped`'s in cargo's own words), both in the lane
    std::fs::write(world.target.join("nobuild"), "").unwrap();
    assert_eq!(
        run("three"),
        (1, lines(&["slot-tell 0", "slot-small 0", "slot-small 0"]))
    );
    // and the run after a red one is told alone still
    std::fs::remove_file(world.target.join("nobuild")).unwrap();
    assert_eq!(run("four"), (0, lines(&["slot-tell 0", "slot-small 0"])));
    // a dependency moved: both askings of a red build are wide ones
    std::fs::write(world.target.join("nobuild"), "").unwrap();
    std::fs::write(
        root.join("rust/b/src/lib.rs"),
        format!("{B_COMPILES_IN}pub const M: u8 = 1;\n"),
    )
    .unwrap();
    assert_eq!(
        run("five"),
        (1, lines(&["slot-tell 1", "slot-wait 1", "slot-wait 1"]))
    );
}

#[test]
fn the_lane_is_a_knob_and_there_is_none_without_wide_slots() {
    let home = Path::new("/home/x");
    let plain = Slots::small(&|_| None, home);
    assert_eq!((plain.count, plain.stem, plain.knob), (1, "small", SMALL));
    assert_eq!(plain.dir, home.join(".cache/l7r-build-slots"));
    let set = |k: &str| (k == SMALL).then(|| "3".to_owned());
    assert_eq!(Slots::small(&set, home).count, 3);
    let words = |k: &str| (k == SMALL).then(|| "many".to_owned());
    assert_eq!(Slots::small(&words, home).count, 1);
    let zero = |k: &str| (k == SMALL).then(|| "0".to_owned());
    assert_eq!(Slots::small(&zero, home).count, 0);
    // no wide slots, or a run under a holder: no lane either
    let no_wide = |k: &str| (k == COUNT).then(|| "0".to_owned());
    assert_eq!(Slots::small(&no_wide, home).count, 0);
    let under = |k: &str| (k == MARK).then(|| "1".to_owned());
    assert_eq!(Slots::small(&under, home).count, 0);
    // a wait in the lane names the lane's knob
    let dir = scratch("alone-knob");
    let held = take(&lane(&dir, 1), "first\n", &mut quiet);
    assert!(held.hold.is_some());
    let slow = Slots {
        ceiling: Duration::from_secs(90),
        poll: Duration::from_secs(30),
        clock: Box::new(Stepped::default()),
        ..lane(&dir, 1)
    };
    let mut said = Vec::new();
    assert!(take(&slow, "me\n", &mut |l| said.push(l.to_owned()))
        .hold
        .is_none());
    assert_eq!(said[0], "rust-checks: waiting on a build slot, 60 s so far - 1 compiling cargo call(s) run at once on this machine (L7R_BUILD_SLOTS_SMALL, feature 451 T284); held by: first\n");
}

#[test]
fn a_lane_of_none_is_a_wide_slot_and_a_lane_that_cannot_be_taken_is_said_in_its_line() {
    let (root, a) = fixture();
    let dir = scratch("alone-none");
    let args = ["test".to_owned(), "--no-run".to_owned()];
    // no lane: the wide slot, and no `slot-small` line
    let world = world_with(&root, "exit 0").map(|w| World {
        slots: quick(&dir, 1),
        ..w
    });
    let mut env = std::collections::BTreeMap::new();
    let held = around_small(&world, &a, &args, &mut env);
    assert!(held.is_some() && dir.join("slot-0").is_file() && !dir.join("small-0").exists());
    assert_eq!(phases(&root).len(), 0);
    // a lane with no `flock` to ask: the build runs without, and its line says so
    let broken = world.map(|w| World {
        small: Slots {
            flock: "/nonexistent/flock".to_owned(),
            ..lane(&dir, 1)
        },
        ..w
    });
    let mut env = std::collections::BTreeMap::new();
    assert!(around_small(&broken, &a, &args, &mut env).is_none());
    assert_eq!(since(&root, 0), [format!("{USE} 1")]);
}

#[test]
fn a_file_is_its_nearest_crate_s_so_a_crate_inside_a_dependency_is_told_apart_from_it() {
    let (root, a) = fixture();
    std::fs::create_dir_all(root.join("rust/b/inner/src")).unwrap();
    put(&root, "rust/b/inner/Cargo.toml", "[package]\n");
    put(&root, "rust/b/inner/src/lib.rs", "//! x\n");
    let dir = scratch("alone-nearest");
    let world = lane_world(&root, "exit 0", &dir);
    let build = |w: &World| Told::of(w, "test", &a, &kept(w, &a), &ARGS).cargo(w, &ARGS, &a);
    // `a` builds from `b` and not from the crate inside it: that crate's file is no input, `b`'s own is
    assert_eq!(build(&world).code, 0);
    assert!(alone(&world, &a));
    put(&root, "rust/b/inner/src/more.rs", "//! new\n");
    assert!(alone(&world, &a));
    put(&root, "rust/b/src/more.rs", "//! new\n");
    assert!(!alone(&world, &a));
    // `a` builds from the crate inside and not from `b`: the other way about
    let from_inner = "[package]\n[dependencies]\ninner = { path = \"../b/inner\" }\n";
    put(&root, "rust/a/Cargo.toml", from_inner);
    assert_eq!(build(&world).code, 0);
    assert!(alone(&world, &a));
    put(&root, "rust/b/src/other.rs", "//! new\n");
    assert!(alone(&world, &a));
    put(&root, "rust/b/inner/src/other.rs", "//! new\n");
    assert!(!alone(&world, &a));
}

#[test]
fn a_keyed_file_that_cannot_be_asked_its_time_is_not_alone() {
    let (root, a) = fixture();
    put(&root, "rust/b/src/extra.rs", "//! x\n");
    let dir = scratch("alone-unasked");
    let world = lane_world(&root, "exit 0", &dir);
    let read = kept(&world, &a);
    assert_eq!(
        Told::of(&world, "test", &a, &read, &ARGS)
            .cargo(&world, &ARGS, &a)
            .code,
        0
    );
    assert!(Told::of(&world, "test", &a, &read, &ARGS).alone());
    // the file goes after the tree was read: its id still stands in the key, and it has no time to compare
    std::fs::remove_file(root.join("rust/b/src/extra.rs")).unwrap();
    assert!(!Told::of(&world, "test", &a, &read, &ARGS).alone());
}

#[test]
fn a_healed_link_s_first_build_takes_the_lane_it_was_told_and_its_second_a_wide_slot() {
    let (root, a) = fixture();
    let dir = scratch("alone-heal");
    let world = lane_world(&root, LINKS_ONCE, &dir);
    let first = Told::of(&world, "test", &a, &kept(&world, &a), &ARGS);
    assert_eq!(first.cargo(&world, &ARGS, &a).code, 0);
    let one = take(&quick(&dir, 2), "one\n", &mut quiet);
    let two = take(&quick(&dir, 2), "two\n", &mut quiet);
    assert!(one.hold.is_some() && two.hold.is_some());
    let profile = world.target.join("debug");
    cache(&profile);
    std::fs::write(world.target.join("link-error"), link_error(&profile)).unwrap();
    let told = Told::of(&world, "test", &a, &kept(&world, &a), &ARGS);
    assert!(told.alone());
    let before = phases(&root).len();
    let done = crate::rustc::stale::built(&world, &ARGS, &a, &told);
    assert_eq!(done.code, 0, "{}", done.stderr);
    // the build told alone in the lane; the heal dropped fingerprints, so the build after it is no crate alone: a wide slot, both
    // held, and it runs without at its ceiling
    assert_eq!(
        since(&root, before),
        [format!("{USE} 0"), "slot-wait 1".to_owned()]
    );
}
