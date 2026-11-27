//! The lint's passes (feature 451 T325): a crate that names itself in its `[dev-dependencies]` is linted a third time with none read.

use super::super::{check, names_itself};
use super::{calls, two_crates, world_with};
use crate::rustc::World;

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
