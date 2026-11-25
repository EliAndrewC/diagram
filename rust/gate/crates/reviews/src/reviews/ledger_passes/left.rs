//! ANOTHER TASK'S PLAN REVIEW IS ITS OWN LANDING'S (feature 451 T147). WHY: every refusal of owed rows (`make land`'s first pass, the
//! push's `ledger-owed` row, `make land-tooling`) refused on every owed pass in the clone's log, and a plan review of a task not yet
//! landed is owed until that task's landing writes it: its verdict, committed with the task alone (land-alone, 451 T101), is not in a
//! landing worktree's `plan-review.json`, so `--write-plan-reviews` passes it over there, another feature's `--write specs/<n>-...`
//! does not trace it, and since 451 T105 `make ledger-owed WRITE=` refuses it as the landing's own. Measured 2026-11-22 (a worktree at
//! the clone's HEAD bdb111b827, the landing's two writes run on a copy of its ledger): a 451 landing left 449's T158, T241, T250 and
//! T197 plan reviews owed, and nothing but `LEDGER_ROWS_OK` at the push and nothing at all in the first pass could get it through.
//!
//! So a refusal leaves out a MODE 4 pass whose subject names its feature and task, where that task is not ticked in the feature's
//! `tasks.md` or `tasks-done.md` and is not one the landing lands (`--landing <feature dir> --tasks "<ids>"`); its own landing writes
//! it (a feature's landing traces it, 385 T72's `--write-plan-reviews` takes it once its verdict is committed). A plan review whose
//! subject names no task (a block review), whose task is ticked or whose feature has no specs directory here, and every other pass,
//! still refuses: no landing is left to write it. The landing's two writes are unchanged - a feature's landing still writes every pass
//! traced to it, another open task's among them.
//!
//! Since 451 T157 (`whose.rs`) a pass of any other check is left the same way where its own words, its builder or its page session's
//! brief name another STARTED task, open, that the landing does not land: that task's landing or session writes its row.
//!
//! ONE READING OF WHOSE A ROW IS (451 T231). WHY: this split was the push's and the landing's check alone. The push's own write
//! (`--write-plan-reviews`, sync-with-main) wrote a recorded plan review of ANY task, so a spec-only push carried an open task's rows
//! forward - 451 T243's six plan-review rows were written by four unrelated pushes on 2026-11-25 (d2a61853be, 9a1c8cd121, fdce5cc36f,
//! 546cd2b775) before T243 was ticked at f1458390c3 - while the listing and a commit's notice named the same rows as owed with
//! "make ledger-owed WRITE=", which refuses them as the landing's own (451 T105). The notice was the noise: the coordinator's session
//! read "N check pass(es) have no row" 906 times from 2026-11-12 to 2026-11-25, and on 2026-11-24 it wrote 449 T418's and T422's rows by hand
//! (7f5d85fef7) after the clone's listing named them, though the refused landing had written both in its worktree (3214651875) and was
//! refused on another session's passes. So every reader asks this split: the push's write (no landing) writes no row it leaves, the
//! landing's write (`--landing --tasks`, `cheap.rs`) writes its own tasks', and the listing and notice name a left pass in the note
//! line only. A plan review's row belongs to the push that lands its task (`make land`, the commit carrying its tick); a recorded one
//! whose task has no open line - ticked, withdrawn, a block review - to the next push, whichever it is.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::{text, Pass};

mod whose;

fn re(pattern: &str) -> Regex {
    l7r_shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static FEATURE: LazyLock<Regex> = LazyLock::new(|| re(r"\bfeature (\d{3}-[\w-]+)"));
static TASK: LazyLock<Regex> = LazyLock::new(|| re(r"\btask (T\d+[a-z]?)\b"));
const PLAN_REVIEW: &str = "MODE 4: PLAN REVIEW";

fn group(pattern: &Regex, text: &str) -> Option<String> {
    pattern
        .captures(text)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map(|m| m.as_str().to_owned())
}

/// The landing asking: its feature's directory name and the tasks it lands, both empty for a refusal no landing asks (the push).
pub struct Landing<'a> {
    pub feature: &'a str,
    pub tasks: Vec<&'a str>,
}

/// Is `task` ticked in `text` (a `- [x] T5 ...` line)?
fn ticked_in(text: &str, task: &str) -> bool {
    text.lines().any(|line| {
        line.strip_prefix("- [x] ")
            .or_else(|| line.strip_prefix("- [X] "))
            .is_some_and(|rest| rest.split_whitespace().next() == Some(task))
    })
}

/// Is `task` ticked in `feature`'s `tasks.md` or `tasks-done.md`?
fn ticked(repo: &Path, feature: &str, task: &str) -> bool {
    let dir = repo.join("specs").join(feature);
    let read = |name: &str| std::fs::read_to_string(dir.join(name)).unwrap_or_default();
    ticked_in(&read("tasks.md"), task) || ticked_in(&read("tasks-done.md"), task)
}

/// Has `feature`'s `tasks.md` an open line (`- [ ] T5 ...`) for `task`? Since 451 T231 a plan review is left to its task's landing
/// only while it has one: read as "ticked in neither file", a withdrawn or renumbered task was open for ever, and once the push's write
/// left it too (451 T231) its row would never be written.
fn open(repo: &Path, feature: &str, task: &str) -> bool {
    let text = std::fs::read_to_string(repo.join("specs").join(feature).join("tasks.md"))
        .unwrap_or_default();
    text.lines().any(|line| {
        line.strip_prefix("- [ ] ")
            .is_some_and(|rest| rest.split_whitespace().next() == Some(task))
    })
}

/// The open task whose landing writes this pass's row: a MODE 4 pass naming its feature and task, that task's line open in its
/// feature's `tasks.md` here and not one this landing lands; any other pass, the started task `whose.rs` reads it as serving.
fn left_to(p: &Pass, repo: &Path, clues: &mut whose::Clues, landing: &Landing) -> Option<String> {
    let subject = text(p, "subject");
    if !subject.starts_with(PLAN_REVIEW) {
        return clues.left_to(p, landing);
    }
    let (feature, task) = (group(&FEATURE, subject)?, group(&TASK, subject)?);
    if !open(repo, &feature, &task) {
        return None;
    }
    let landed = landing.feature == feature && landing.tasks.contains(&task.as_str());
    (!landed).then(|| format!("{feature} {task}"))
}

/// The owed passes a refusal counts, and the open tasks (`<feature> <task>`, once each, in order) whose landings or sessions write the
/// rest; `transcripts` is where the passes' transcripts and meta files are found.
#[must_use]
pub fn split(
    owed: &[Pass],
    repo: &Path,
    transcripts: &Path,
    landing: &Landing,
) -> (Vec<Pass>, Vec<String>) {
    let (mut kept, mut left) = (Vec::new(), Vec::new());
    let mut clues = whose::Clues::new(repo, transcripts);
    for p in owed {
        match left_to(p, repo, &mut clues, landing) {
            Some(whose) if !left.contains(&whose) => left.push(whose),
            Some(_) => {}
            None => kept.push(p.clone()),
        }
    }
    (kept, left)
}

/// The line saying which passes were left, and to whom; "" where none was.
#[must_use]
pub fn note(left: &[String]) -> String {
    if left.is_empty() {
        return String::new();
    }
    format!("ledger-owed: the passes of {} open task(s) left to their own landings and sessions (451 T147, T157), which write their rows: {}\n", left.len(), left.join(", "))
}

#[cfg(test)]
mod tests;
