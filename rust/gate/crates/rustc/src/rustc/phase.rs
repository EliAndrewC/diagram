//! THE CHECKS' PHASE LINES (feature 451 T05, plan D4, FR-003; the GM: "how much time are we spending on recompiling things"): a
//! `make static` was one span in the event log, its compile and its tests one figure. Each step a check runs writes one `Phase` line at
//! its end, through the writer the hooks use (`append_row`): a test binary's `build` (`kept.rs`'s `binary_key`), its `test` run
//! (`side.rs`, or a `cargo test` after its own `--no-run` build, `stepped`), a family's `cover-build` and each crate's `cover-run`
//! (`cover.rs`), and a crate's `lint` and `format`. A kept result ran nothing and writes none; `dead`, `hamlet` and `test-times` write
//! none either (no cargo; a stage run; a timing tool of its own). The readers book the `build` and `cover-build` spans as compile (T08).
//! A cargo call that waited for a build slot writes its wait as `slot-wait` (feature 451 T284, `slot.rs`), which the readers book as
//! waiting, ahead of the step whose span holds it. A test build whose link was healed (feature 451 T336, `stale.rs`) writes the drop
//! and its second build as `link-heal`, inside its `build` line's span: the readers book it to no category, so its seconds stay the
//! build's and its lines are there to count. A test build's telling (feature 451 T347, `kept/alone.rs`) writes `slot-tell`, and a
//! build that took the small lane `slot-small` (`slot.rs`), its span its wait for the lane, its code 2 where the lane was held and
//! it took a free wide slot instead (feature 451 T425): booked to no category either. Either slot
//! line taken on a scratch slot directory says `"scratch": true` (feature 451 T426), and its wait is booked to no category.

use std::path::Path;
use std::time::SystemTime;

use l7r_shared::guards::event_log_hooks::{append_row_with, phase_row};
use serde_json::json;

use super::{shown, slot, World};

/// The run's make target (plan D4): the outermost `make`'s first goal, read from its command line (the run lock's `run_what`) as the
/// event log's writer reads a Bash call's (D1); with no `make` above, the gate's own form, `rust-<cmd>`, as D1 reads
/// `l7r-gate.sh rust <cmd>`. A word the command line quotes (one holding a space, `NOTE="two words"`) is read as an assignment: the
/// reader blanks a quoted string, and a blank ends the goals. A goal-less make (`invoked`'s `.DEFAULT_GOAL`, feature 451 T15) names
/// no goal, so the gate's own form stands.
pub(super) fn run_target(run_what: &str, cmd: &str) -> String {
    let words: Vec<&str> = run_what.split('\'').step_by(2).collect();
    l7r_shared::make::invoked(&words.join("QUOTED=1"))
        .into_iter()
        .next()
        .filter(|t| t != l7r_shared::make::DEFAULT_GOAL)
        .unwrap_or_else(|| format!("rust-{cmd}"))
}

/// The step a check run in `answer`'s loop is, where it is one: a lint, a format, and a test run's `cargo test` (its build booked
/// apart first, `stepped`).
pub(super) fn step_of(cmd: &str) -> Option<&'static str> {
    match cmd {
        "lint" => Some("lint"),
        "format" => Some("format"),
        c if c.starts_with("test") => Some("test"),
        _ => None,
    }
}

/// One step's line, written at its end: its crates by their directories from the tree's root, `began` its start, `code` how it went;
/// `t` is its end, and the line names the run's make target and the clone it ran in, which the readers tie it to a Bash call by.
/// It feeds the task time breakdown (`make task-time`, 451 T243).
pub(super) fn wrote<P: AsRef<Path>>(
    world: &World,
    step: &str,
    manifests: &[P],
    began: SystemTime,
    code: i32,
) {
    let crates: Vec<String> = manifests.iter().map(|m| shown(world, m.as_ref())).collect();
    let mut row = phase_row(
        "rust",
        step,
        (began, SystemTime::now()),
        code,
        &world.make,
        &world.root,
    );
    row.insert("crates".into(), json!(crates));
    // a filtered test run is a part of its crates' tests, kept as no green (feature 451 T435, `only.rs`): its words said
    if step == "test" && !world.only.is_empty() {
        row.insert("only".into(), json!(world.only.join(" ")));
    }
    // a wait on a scratch slot directory is a measurement's own (feature 451 T426, `slot.rs`): marked, so the readers leave it out
    if world.slots.scratch && (step == slot::STEP || step == slot::USE) {
        row.insert("scratch".into(), json!(true));
    }
    let _ = append_row_with(&world.root, None, row, world.root.reader());
}
