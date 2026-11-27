//! THE LINT'S PASSES, each in the lane it is told (feature 451 T325, T355). Clippy with `-D warnings`, twice a crate - its default
//! features and every feature - and a third time for a crate that names itself in its `[dev-dependencies]`.
//!
//! A PASS TOLD TO COMPILE ITS CRATE ALONE TAKES THE SMALL LANE (feature 451 T355), as a test build does (`kept/alone.rs`, feature
//! 451 T347). Until then every pass took one of the two wide build slots whatever it compiled: with both held, the lint of
//! `rust/gate/crates/reviews` after a body edit waited 55.5 and 49.9 s for 2.6 s of work. Measured 2026-11-27
//! (`dev/measurements/2026-11-27/lint-memory/results.md`): a pass that compiles one crate alone is 0.08-0.37 GiB anonymous after a
//! body edit and 0.66 GiB at the most (every source of the largest crate), one to three `clippy-driver` at once and no link - under
//! the test build's 0.19-0.64 and 1.42 GiB that the lane was sized for, and in the lane in a test build's place, never beside one.
//!
//! ONE KEY A PASS, the test build's kind and never the test build's own. Measured the same day: after a dependency's body edit
//! and a green test build, which kept ITS key, the lint compiled the dependency again (clippy's check units have their own
//! fingerprints); and the `--lib` pass compiled the dependencies again straight after the `--all-targets` pass had (the crate's
//! test-only feature off: other units). So a pass is told alone only by what that pass last built: its key is named by its words
//! (`<crate>-lint--all-targets`, `...--all-features`, `...--lib`) and holds them with `-D warnings`, beside what every such key
//! holds - the dependencies' content ids (dev-dependencies too), the workspace's files (`clippy.toml` among them), the crate's
//! manifest (its `[lints]`), the compiler - and the times. A pass told alone leaves its key as it is, red or green; a wide pass
//! keeps its key where it passes, so a red wide pass and each pass after it are wide at the next lint too.
//!
//! Outside a repository no content id is read, so a key would hold no file and stand whatever moved: nothing is told there.
//! A fresh run's lint (`FRESH=1`) is told like any other: cargo's fingerprints know nothing of it.
//! Each telling writes a `slot-tell` line and each pass in the lane a `slot-small` line, as a test build's do; a lint's are told
//! from a test build's by the span they lie in - the crate's `lint` line, where a test build's lie in its `build` line.

use std::path::Path;

use super::{names_itself, Kept, Ran, Told, World};

/// What every pass denies.
const DENY: [&str; 2] = ["-D", "warnings"];

/// The clippy calls of `manifest`'s crate, in order.
///
/// THE THIRD PASS (feature 451 T325): `--all-targets` reads `[dev-dependencies]`, so a crate that names itself there has its
/// test-only feature on in both passes above, and its lines under that feature's `not(..)` - what the tools compile - would be
/// linted by nothing. `--lib` reads no dev-dependency. Measured 2026-11-26 over the six such crates after a touch of `core` and
/// `l7r_shared`: 7 check compiles and 12.8 s beside the two passes' 14 and 23.9 s
/// (`dev/measurements/2026-11-26/feature-unify/lint-pass.sh`).
fn passes(manifest: &Path) -> Vec<&'static [&'static str]> {
    let mut passes: Vec<&[&str]> = vec![
        &["clippy", "--quiet", "--all-targets"],
        &["clippy", "--quiet", "--all-targets", "--all-features"],
    ];
    if names_itself(manifest) {
        passes.push(&["clippy", "--quiet", "--lib"]);
    }
    passes
}

/// One pass, in the lane it is told by its own key (`inputs`: the run's content ids; none, or none read, is a wide slot).
fn pass(world: &World, words: &[&str], manifest: &Path, inputs: Option<&Kept>) -> Ran {
    let told = inputs
        .filter(|k| !k.git_dir.is_empty())
        .map_or_else(Told::wide, |k| {
            let name = format!("lint{}", words[2..].concat());
            let keyed = [words, &["--"], &DENY].concat();
            Told::of(world, &name, manifest, k, &keyed)
        });
    told.cargo_with(world, words, manifest, &DENY)
}

/// The lint of `manifest`'s crate: a pass that fails is the answer, and no later pass runs.
pub(super) fn linted(world: &World, manifest: &Path, inputs: Option<&Kept>) -> Ran {
    let all = passes(manifest);
    let mut ran = pass(world, all[0], manifest, inputs);
    for words in &all[1..] {
        if ran.code != 0 {
            break;
        }
        ran = pass(world, words, manifest, inputs);
    }
    ran
}
