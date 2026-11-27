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

use std::collections::BTreeSet;
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

/// The make targets a Makefile defines: each `name:` that opens a line (moved here from the gate's `builder_brief` by 451 T313's
/// round 3, so the builders' queue chooses an unlisted task's KIND by this same test, in the gate and in the pool-idle guard).
#[must_use]
pub fn targets(makefile: &str) -> BTreeSet<String> {
    let name = |c: char| c.is_ascii_alphanumeric() || matches!(c, '-' | '_' | '.');
    makefile
        .lines()
        .filter_map(|l| l.split_once(':'))
        .filter(|(head, rest)| !head.is_empty() && head.chars().all(name) && !rest.starts_with('='))
        .map(|(head, _)| head.to_owned())
        .collect()
}

/// What in a task's line names a NEW MECHANISM - a command or a guard, which is two builders from the start - or none. Kept simple:
/// one of four phrases (`a new command`, `a new guard`, `a guard refuses`, `a PreToolUse check`), or a `make <target>` whose target
/// has a hyphen and is no target of the Makefile yet. It MISSES a new command with no hyphen in its name (the hyphen is what tells a
/// target from "make sure"), a guard described in other words ("a hook that stops"), a background step measured before and after,
/// and a new verb of an existing target; it WRONGLY takes a line that names a target a sibling task has not landed yet.
#[must_use]
pub fn mechanism(line: &str, known: &BTreeSet<String>) -> Option<String> {
    let lower = line.to_lowercase();
    let phrase = [
        "a new command",
        "a new guard",
        "a guard refuses",
        "a pretooluse check",
    ]
    .into_iter()
    .find(|p| lower.contains(p));
    if let Some(p) = phrase {
        return Some(format!("\"{p}\""));
    }
    let name = |c: char| c.is_ascii_lowercase() || c.is_ascii_digit() || c == '-';
    line.split("make ")
        .skip(1)
        .map(|rest| {
            first_target(rest)
                .split(|c: char| !name(c))
                .next()
                .unwrap_or("")
        })
        .find(|t| t.contains('-') && !known.contains(*t))
        .map(|t| format!("`make {t}`, no target of the Makefile yet"))
}

/// The make flags whose argument is the next word (GNU make's manual, "Summary of Options": `-C dir`, `-f file`, `-I dir`, `-o file`,
/// `-W file` and their long forms); a flag spelled with its argument attached (`-Crust`, `--directory=rust`) is one word.
const FLAG_ARGS: [&str; 13] = [
    "-C",
    "-f",
    "-I",
    "-o",
    "-W",
    "--directory",
    "--file",
    "--makefile",
    "--include-dir",
    "--old-file",
    "--assume-old",
    "--what-if",
    "--new-file",
];

/// The first word after `make ` that is no flag nor a flag's argument: `-C <tree> task-unstart` is `task-unstart`, never `-`
/// (451 T431: T369's and T437's lines were refused as a new mechanism `make -`); '' where none is.
fn first_target(rest: &str) -> &str {
    let mut words = rest.split_whitespace();
    while let Some(w) = words.next() {
        if !w.starts_with('-') {
            return w;
        }
        if FLAG_ARGS.contains(&w) {
            words.next();
        }
    }
    ""
}

/// The first words of the block's STOP POINT line, which every kind's block holds (`rust/gate/crates/task/src/builder_brief.rs`).
pub const STOP: &str = "STOP POINT";

/// Whether `prompt` holds a line opening [`STOP`] - a builder's brief, as `context_cap_hooks/split.rs` knows a code builder and
/// `builder_brief_hooks` a brief written by hand (451 T353). Measured over the coordinating sessions' 977 dispatches of
/// 2026-11-20..27: 145 carried such a line, every one an ad-hoc builder's.
#[must_use]
pub fn stop_point(prompt: &str) -> bool {
    prompt.lines().any(|l| l.trim_start().starts_with(STOP))
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
        assert!(
            stop_point("x\n  STOP POINT (fix): red-first") && !stop_point("its STOP POINT line")
        );
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

    #[test]
    fn a_task_s_line_names_a_new_mechanism_by_a_phrase_or_an_unknown_target() {
        let known: BTreeSet<String> = targets("X := 1\nA:=2\nbuilder-tree: export D := 1\nbuilder-tree:\n\t@echo a: b\nland:\n: odd\n# a note: x\n");
        assert_eq!(
            known.into_iter().collect::<Vec<_>>(),
            ["builder-tree", "land"]
        );
        let known = targets("builder-tree:\nland:\n");
        for (line, what) in [
            ("- [ ] T1 Build: make builder-brief T=<task> prints the block", Some("`make builder-brief`, no target of the Makefile yet")),
            ("- [ ] T1 and A PreToolUse check on the Agent tool", Some("\"a pretooluse check\"")),
            ("- [ ] T1 a guard refuses git worktree add", Some("\"a guard refuses\"")),
            ("- [ ] T1 a new command for the pool", Some("\"a new command\"")),
            ("- [ ] T1 a new guard on rm", Some("\"a new guard\"")),
            // what it misses, and what is no mechanism
            ("- [ ] T1 make builder-tree hands out a cold tree; I want to make sure it does not, and make land frees it", None),
            ("- [ ] T1 a hook that stops a hand dispatch; make newtarget prints it; make ", None),
            ("- [ ] T1 the guard misreads a quoted path", None),
        ] {
            assert_eq!(mechanism(line, &known).as_deref(), what, "{line}");
        }
    }

    /// 451 T431: a make FLAG is no target - T369's line (`make -C <tree> task-unstart`, read as `make -`) and T437's were refused as
    /// a new mechanism and passed only by `SIZING_OK`, 2026-11-27.
    #[test]
    fn a_make_flag_is_no_new_target() {
        let known = targets("task-start:\ntask-unstart:\ntask-withdraw:\n");
        for (line, what) in [
            ("- [ ] T369 a task started in a second tree; make task-start refuses a task another tree's mark names, with the make -C <tree> task-unstart to run there", None),
            ("- [ ] T437 make task-unstart refuses it with a make -C <tree> that cannot run, make task-withdraw refuses the task as started", None),
            ("- [ ] T1 make -j4 land and make --no-print-directory x; make - alone", None),
            // ...and a new target behind a flag is still read: past a flag's argument (`-C <dir>`, `-f <file>`), past a bare flag
            ("- [ ] T1 make -C <tree> new-thing prints it", Some("`make new-thing`, no target of the Makefile yet")),
            ("- [ ] T1 make --directory rust -f x.mk -j4 task-start, then make -s 2-up", Some("`make 2-up`, no target of the Makefile yet")),
            ("- [ ] T1 make -C", None),
            ("- [ ] T1 make new-thing prints it", Some("`make new-thing`, no target of the Makefile yet")),
        ] {
            assert_eq!(mechanism(line, &known).as_deref(), what, "{line}");
        }
    }
}
