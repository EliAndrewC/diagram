//! THE BUILDER BRIEF'S MARKER (feature 451 T334; the GM, 2026-11-26: "is this also part of our checklist-based process for kicking
//! off and managing builders? Or do we not have such a checklist? ... I just want to make sure that we're putting the instructions in
//! the right place"). The standing part of a builder's brief is printed by `make builder-brief`
//! (`rust/gate/crates/task/src/builder_brief.rs`), which sizes the brief and takes the pool tree, and its first line is this marker:
//!
//! `BUILDER-BRIEF <feature> <task> KIND=<kind> JOBS=<n> TREE=<path>`
//!
//! The guard (`rust/guard/src/guards/builder_brief_hooks.rs`) reads it back from a builder's dispatch. One format, written and read
//! here, so the command and the guard cannot drift. WHY a line of its own: a brief that MENTIONS the marker in a sentence (this
//! task's own brief did) carries no block.
// GUARD_EDIT_OK: feature 451 T334 - a new operation, the builder brief's marker, which the gate writes and the new guard reads

use std::path::PathBuf;

/// The marker line's first word.
pub const MARKER: &str = "BUILDER-BRIEF";
/// The kinds of builder a brief is made for.
pub const KINDS: [&str; 4] = ["fix", "measurement", "build-half", "closing-half"];
/// The most jobs one brief holds (`scripts/container/builder-brief.md`, SIZING: a GUESS knob set where the measured hand-off rate
/// steps up - 52% at four or more jobs against 16-22% at one to three, 97 builders, 2026-11-24/25).
pub const JOBS_MAX: usize = 3;
/// The most THINGS one measurement brief measures. GUESS: 451 T315's "one job" measured seven crates and priced eight levers and
/// ended at 308k of context; no brief was ever sized by this count, so the bound is set under the smaller of the two and is a knob
/// to move on the first measurement builders it sizes (`dev/audits/builder-brief-command.md`).
pub const MEASURES_MAX: usize = 6;

/// A brief's marker: the feature (its number) and task it is for, its kind, its jobs and the pool tree it works in.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Marker {
    pub feature: String,
    pub task: String,
    pub kind: String,
    pub jobs: usize,
    pub tree: PathBuf,
}

impl Marker {
    /// The marker as the block's first line.
    #[must_use]
    pub fn line(&self) -> String {
        let (feature, task, kind, jobs) = (&self.feature, &self.task, &self.kind, self.jobs);
        let tree = self.tree.display();
        format!("{MARKER} {feature} {task} KIND={kind} JOBS={jobs} TREE={tree}")
    }
}

/// One line read as a marker: `BUILDER-BRIEF`, the feature, the task, then `KIND=`, `JOBS=` and `TREE=` in any order.
fn of_line(line: &str) -> Option<Marker> {
    let mut words = line.split_whitespace();
    if words.next() != Some(MARKER) {
        return None;
    }
    let (feature, task) = (words.next()?, words.next()?);
    let rest: Vec<&str> = words.collect();
    let value = |key: &str| rest.iter().find_map(|w| w.strip_prefix(key));
    Some(Marker {
        feature: feature.to_owned(),
        task: task.to_owned(),
        kind: value("KIND=")?.to_owned(),
        jobs: value("JOBS=")?.parse().ok()?,
        tree: PathBuf::from(value("TREE=")?),
    })
}

/// The first marker `prompt` holds on a line of its own; none where it only mentions one, or the line is not a whole marker.
#[must_use]
pub fn parse(prompt: &str) -> Option<Marker> {
    prompt.lines().find_map(of_line)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_marker_round_trips_and_a_mention_is_none() {
        let m = Marker {
            feature: "451".to_owned(),
            task: "T334".to_owned(),
            kind: "build-half".to_owned(),
            jobs: 2,
            tree: PathBuf::from("/c/x-t271"),
        };
        let line = m.line();
        let want = "BUILDER-BRIEF 451 T334 KIND=build-half JOBS=2 TREE=/c/x-t271";
        assert_eq!(line, want);
        let brief = format!("the task\n  {line}\nBlocks: none\n");
        assert_eq!(parse(&brief), Some(m));
        // a sentence naming the marker, and a line short of a field, are no marker
        for text in [
            "a first line marker `BUILDER-BRIEF <feature> <task> KIND=<kind> JOBS=<n> TREE=<path>`",
            "BUILDER-BRIEF",
            "BUILDER-BRIEF 451",
            "BUILDER-BRIEF 451 T1 KIND=fix TREE=/c/x",
            "BUILDER-BRIEF 451 T1 JOBS=1 TREE=/c/x",
            "BUILDER-BRIEF 451 T1 KIND=fix JOBS=1",
            "BUILDER-BRIEF 451 T1 KIND=fix JOBS=many TREE=/c/x",
            "",
        ] {
            assert_eq!(parse(text), None, "{text}");
        }
    }
}
