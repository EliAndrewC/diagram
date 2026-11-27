//! The lint's passes (feature 451 T325): a crate that names itself in its `[dev-dependencies]` is linted a third time with none read.
//! And their lanes (feature 451 T355): a pass told to compile its crate alone - its own key standing in the target directory and no
//! input newer than it - takes the small lane and never a wide build slot; anything else a wide slot.

use std::path::Path;

use super::super::{check, names_itself};
use super::alone::{fixture, lane_world, put, since, A_BUILDS_FROM_B};
use super::phases::phases;
use super::slot::{quick, quiet};
use super::{answer, calls, two_crates, world_with};
use crate::checks::scratch;
use crate::rustc::kept::alone::DIR;
use crate::rustc::slot::{take, Taken};
use crate::rustc::World;

/// A fake cargo whose clippy calls fail while a file `fail` lies beside it.
const FAILS: &str = "[ \"$1\" = clippy ] && [ -f \"$(dirname \"$0\")/fail\" ] && exit 101\nexit 0";
pub(super) const WIDE: [&str; 2] = ["slot-tell 1", "slot-wait 1"];
pub(super) const SMALL: [&str; 2] = ["slot-tell 0", "slot-small 0"];

/// Both wide slots under `dir`, held: a wide call of a lane world then runs without one at its ceiling, a `slot-wait 1` line.
pub(super) fn both_held(dir: &Path) -> [Taken; 2] {
    let held = [(); 2].map(|()| take(&quick(dir, 2), "held\n", &mut quiet));
    assert!(held.iter().all(|t| t.hold.is_some()));
    held
}

/// One lint of crate `a` after an edit of its own source (`text` makes its code new, so no kept result stands): how it ended and
/// the slot lines it wrote, a moment's wait in the lane left out (a slot just let go may read held, `slot.rs`).
pub(super) fn lint(world: &World, root: &Path, text: &str) -> (i32, Vec<String>) {
    let before = phases(root).len();
    let code = format!("pub const N: &str = \"{text}\";\n");
    std::fs::write(root.join("rust/a/src/lib.rs"), code).unwrap();
    let code = answer(world, "lint", &["rust/a".to_owned()], false).code;
    let mut slots = since(root, before);
    slots.retain(|l| l != "slot-wait 0");
    (code, slots)
}

/// The clippy calls a world's fake cargo noted, whole.
fn clippy(world: &World) -> Vec<String> {
    let mut said = calls(world);
    said.retain(|c| c.starts_with("clippy "));
    said
}

/// `n` passes, each with the slot lines `each`.
pub(super) fn passes_of(n: usize, each: [&str; 2]) -> Vec<String> {
    each.repeat(n).iter().map(|l| (*l).to_owned()).collect()
}

/// The clippy calls a world's fake cargo noted, each up to its manifest.
fn passes(world: &World) -> Vec<String> {
    let cut = |c: &String| c.split(" --manifest-path").next().map(str::to_owned);
    calls(world).iter().filter_map(cut).collect()
}

#[test]
fn a_crate_that_names_itself_is_linted_a_third_time_with_no_dev_dependency_read() {
    let (root, a, b) = two_crates();
    let itself = "[package]\nname = \"a\"\n\n[dev-dependencies]\nb = { path = \"../b\" }\na = { path = \".\", features = [\"kit\"] }\n\n[lints]\n";
    let another = "[package]\nname = \"b\"\n\n[dependencies]\nc = { path = \".\" }\n\n[dev-dependencies]\na = { path = \"../a\" }\n";
    std::fs::write(&a, itself).unwrap();
    std::fs::write(&b, another).unwrap();
    assert!(names_itself(&a));
    assert!(!names_itself(&b));
    assert!(!names_itself(&root.join("rust/none/Cargo.toml")));
    let world = world_with(&root, "exit 0");
    assert_eq!(check(&world, "lint", &b, false).code, 0);
    let two = [
        "clippy --quiet --all-targets",
        "clippy --quiet --all-targets --all-features",
    ];
    assert_eq!(passes(&world), two);
    assert_eq!(check(&world, "lint", &a, false).code, 0);
    assert_eq!(
        passes(&world)[2..],
        [two[0], two[1], "clippy --quiet --lib"]
    );
    assert!(calls(&world)[4].ends_with("rust/a/Cargo.toml -- -D warnings"));
    // a pass that fails is the answer, and no later pass runs
    let red = world_with(&root, "exit 1");
    assert_eq!(check(&red, "lint", &a, false).code, 1);
    assert_eq!(passes(&red), [two[0]]);
}

#[test]
fn a_lint_told_alone_takes_the_lane_at_each_pass_while_both_wide_slots_are_held() {
    let (root, a) = fixture();
    let dir = scratch("lint-lane");
    let world = lane_world(&root, "exit 0", &dir);
    let _held = both_held(&dir);
    // the first lint in a target directory: each pass a wide slot, its key kept where it passes
    assert_eq!(lint(&world, &root, "one"), (0, passes_of(2, WIDE)));
    let keys = world.target.join(DIR);
    assert!(keys.join("rust_a-lint--all-targets").is_file());
    assert!(keys
        .join("rust_a-lint--all-targets--all-features")
        .is_file());
    // the crate's own edit: each pass takes the lane and asks no wide slot, its words whole
    assert_eq!(lint(&world, &root, "two"), (0, passes_of(2, SMALL)));
    let signed = std::fs::read_to_string(dir.join("small-0")).unwrap();
    assert!(signed.ends_with("cargo clippy --quiet\n"));
    let said = clippy(&world);
    assert_eq!(said.len(), 4);
    assert!(said
        .iter()
        .all(|c| c.ends_with("rust/a/Cargo.toml -- -D warnings")));
    assert_eq!(phases(&root).pop().unwrap()["step"], "lint");
    // a pass's key is its own words': the test build's key in the same directory tells a lint nothing
    std::fs::remove_dir_all(&keys).unwrap();
    assert!(a.is_file());
    assert_eq!(
        answer(&world, "test", &["rust/a".to_owned()], false).code,
        0
    );
    assert!(keys.join("rust_a-test").is_file());
    assert_eq!(lint(&world, &root, "three"), (0, passes_of(2, WIDE)));
}

#[test]
fn a_changed_dependency_sends_the_lint_to_a_wide_slot_and_a_red_pass_told_alone_keeps_its_key() {
    let (root, _) = fixture();
    let dir = scratch("lint-wide");
    let world = lane_world(&root, FAILS, &dir);
    let _held = both_held(&dir);
    assert_eq!(lint(&world, &root, "one"), (0, passes_of(2, WIDE)));
    assert_eq!(lint(&world, &root, "two"), (0, passes_of(2, SMALL)));
    // a dependency's content: wide, and the lint after it in the lane again
    std::fs::write(root.join("rust/b/src/lib.rs"), "pub const M: u8 = 1;\n").unwrap();
    assert_eq!(lint(&world, &root, "three"), (0, passes_of(2, WIDE)));
    assert_eq!(lint(&world, &root, "four"), (0, passes_of(2, SMALL)));
    // a dependency's time alone, its content as it was (a file put back)
    std::fs::write(root.join("rust/b/src/lib.rs"), "pub const M: u8 = 1;\n").unwrap();
    assert_eq!(lint(&world, &root, "five"), (0, passes_of(2, WIDE)));
    // a red pass told alone stops the lint and keeps its key: no dependency moved, so the next lint is told alone again
    std::fs::write(world.target.join("fail"), "").unwrap();
    assert_eq!(lint(&world, &root, "six"), (1, passes_of(1, SMALL)));
    std::fs::remove_file(world.target.join("fail")).unwrap();
    assert_eq!(lint(&world, &root, "seven"), (0, passes_of(2, SMALL)));
    // a red wide pass keeps no key of its own: the next lint's first pass is wide still
    put(
        &root,
        "rust/a/Cargo.toml",
        &format!("{A_BUILDS_FROM_B}# c\n"),
    );
    std::fs::write(world.target.join("fail"), "").unwrap();
    assert_eq!(lint(&world, &root, "eight"), (1, passes_of(1, WIDE)));
    std::fs::remove_file(world.target.join("fail")).unwrap();
    assert_eq!(lint(&world, &root, "nine"), (0, passes_of(2, WIDE)));
    // a fresh run's lint is told like any other: cargo's fingerprints know nothing of it
    let fresh = world.map(|w| World {
        no_reuse: true,
        ..w
    });
    assert_eq!(lint(&fresh, &root, "ten"), (0, passes_of(2, SMALL)));
}

#[test]
fn all_three_passes_of_a_crate_that_names_itself_take_the_lane_each_by_its_own_key() {
    let (root, _) = fixture();
    let itself = format!(
        "{A_BUILDS_FROM_B}\n[dev-dependencies]\na = {{ path = \".\", features = [\"kit\"] }}\n"
    );
    put(&root, "rust/a/Cargo.toml", &itself);
    let dir = scratch("lint-three");
    let world = lane_world(&root, "exit 0", &dir);
    let _held = both_held(&dir);
    assert_eq!(lint(&world, &root, "one"), (0, passes_of(3, WIDE)));
    assert_eq!(lint(&world, &root, "two"), (0, passes_of(3, SMALL)));
    let said = clippy(&world);
    assert!(said[5].starts_with("clippy --quiet --lib --manifest-path"));
    // each pass by its own key: with the third's gone, the first two take the lane and the third a wide slot
    let third = world.target.join(DIR).join("rust_a-lint--lib");
    std::fs::remove_file(&third).unwrap();
    let mixed = [passes_of(2, SMALL), passes_of(1, WIDE)].concat();
    assert_eq!(lint(&world, &root, "three"), (0, mixed));
    assert!(third.is_file());
}

#[test]
fn a_lint_outside_a_repository_is_told_nothing_and_takes_a_wide_slot() {
    let (root, _, _) = two_crates();
    let dir = scratch("lint-no-repository");
    let world = lane_world(&root, "exit 0", &dir);
    let _held = both_held(&dir);
    // no content id is read there, so a key would hold no file and stand whatever moved
    let wide: Vec<String> = vec!["slot-wait 1".to_owned(); 2];
    assert_eq!(lint(&world, &root, "one"), (0, wide.clone()));
    assert_eq!(lint(&world, &root, "two"), (0, wide));
    assert!(!world.target.join(DIR).exists());
}
