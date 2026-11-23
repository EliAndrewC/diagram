//! The builder-slot block's words (451 T177): moved out of `set_down_hooks.rs`, which its bundle cap put past the file-scale bar,
//! and held at their worst case in `suite_tools/messages/worst.rs`.

use std::path::Path;

/// A running builder as the slot block names it: its feature and its tasks joined by `+`, a bundle past [`crate::listed::SHOWN`]
/// tasks said as its first few, how many more and the `cat` of a file holding them all, where that is the shorter (451 T177,
/// message-check: a bundle's every task said whole grew the block without bound; 449's T351 bundle held 21).
#[must_use]
pub fn builder_said(feature: &str, tasks: &[String], git_dir: &Path) -> String {
    let all = tasks.join("+");
    let shown = crate::listed::SHOWN;
    if tasks.len() > shown {
        let head = tasks[..shown].join("+");
        let more = tasks.len() - shown;
        // the kept file's path is its key's length whatever the key, so the short form is priced before the file is written
        let probe = git_dir
            .join("l7r-lists")
            .join(format!("{}.txt", "0".repeat(16)));
        let short = format!("{head} and {more} more: `cat {}`", probe.display());
        if short.chars().count() < all.chars().count() {
            let rest = crate::listed::kept(git_dir, tasks);
            if !rest.is_empty() {
                return format!("{feature} {head} and {more} more: `{rest}`");
            }
        }
    }
    format!("{feature} {all}")
}

/// The builder-slot block's words. Its list, `who`, is the running builders, fewer than the knob, each said by [`builder_said`].
/// 451 T177 (message-check): "(feature 451 T88, `L7R_BUILDERS`=<knob>)" after "dispatch its builder" is cut, a citation its reader
/// could not act on; the knob is the "of <knob>".
#[must_use]
pub fn slot_said(
    running: usize,
    knob: usize,
    who: &[String],
    (id, short): (&str, &str),
    later: &str,
    number: &str,
    down: &str,
) -> String {
    format!(
        "BLOCKED: a builder slot is free - {running} of {knob} builders running ({}) - start the next independent open task, one touching none of their files ({id} {short}): {later}make task-start F={number} T={id}, then dispatch its builder; or set the feature down: make set-down F={down} WHY=\"<why it stops here>\"",
        if who.is_empty() { "none".to_owned() } else { who.join(", ") },
    )
}
