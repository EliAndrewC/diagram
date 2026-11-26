//! AN UNFINISHED CARRY-OVER LANDS NOTHING (feature 451 T292). WHY: on 2026-11-26 the coordinating session ran `git cherry-pick` of a
//! builder worktree's commit (558d9af6ea) and `make land F=451 T=T270` in one shell command. The cherry-pick stopped on a tasks.md
//! conflict - `CHERRY_PICK_HEAD` present, the code staged and uncommitted, one path unmerged - and the landing went through: a dirty
//! clone sends the landing to `scripts/land-alone.sh` ([`super::alone`], 451 T88), which lands the clone's HEAD apart from the
//! uncommitted work, so it committed T270's plan section and tasks.md lines, ticked T270 and pushed (0526d8b7df) WITHOUT the code
//! (repaired by 83f65718d7). It was the third landing over an unfinished carry-over, after 451 T235 and T262.
//!
//! So, before the landing asks whether it lands alone and before its first pass writes anything, the tree is asked three things, each
//! refusal printing the command that finishes it: (a) is a cherry-pick, merge, revert, rebase or mailbox apply in progress, a pick of several commits paused between two
//! of them (`sequencer/todo`) among them (its marker in the tree's
//! OWN git directory - a linked worktree's `.git` is a file, 451 T267, so the directory is `git rev-parse --absolute-git-dir`'s);
//! (b) is any path unmerged; (c) do staged changes stand uncommitted. `l7r-gate land --unfinished <tree>` asks the same of
//! `scripts/sync-with-main.sh`'s push and `scripts/land-tooling.sh`, and `make carry` ([`super::carry`]) starts and ends with it.
//!
//! WHY FIRST AND APART from the first pass's other refusals (this builder, 2026-11-26): that pass COMMITS on its way (the ledger rows,
//! the make-targets page, the escape records), and a `git commit` while a cherry-pick or merge stands concludes it with whatever is
//! staged. Nothing else is asked of a tree in this state.
//!
//! Staged changes with nothing in progress are refused too: the landing and its ticks stage and commit in one step and put back what
//! fails ([`super::writers`], 451 T242), a builder is told never to stage, so a staged change is a commit somebody began.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;

/// How many paths a refusal names.
const SHOWN: usize = 6;

/// An operation git leaves standing in a tree's git directory: its marker there, its name, and git's verb for it.
struct Op {
    marker: &'static str,
    name: &'static str,
    verb: &'static str,
}

/// The operations a `*_HEAD` names, in the order they are named.
const HEADS: [Op; 3] = [
    Op {
        marker: "CHERRY_PICK_HEAD",
        name: "cherry-pick",
        verb: "cherry-pick",
    },
    Op {
        marker: "MERGE_HEAD",
        name: "merge",
        verb: "merge",
    },
    Op {
        marker: "REVERT_HEAD",
        name: "revert",
        verb: "revert",
    },
];
/// A pick or revert of SEVERAL commits paused between two of them: no `*_HEAD` stands (the one it stopped on was committed by hand),
/// the status is clean, and the commits still to come are this file's lines - `pick <sha> ...` or `revert <sha> ...`. Unread, a
/// landing would tick a task without the rest of its code (the plan review's measurement, 2026-11-26).
const SEQUENCER: &str = "sequencer/todo";
/// A rebase's two directories; the second is also a mailbox apply's (`git am`), which its `applying` file tells apart.
const REBASE: [&str; 2] = ["rebase-merge", "rebase-apply"];

/// The operations standing in the git directory `dir`: each one's marker, its name, and the git arguments that finish it (a
/// continue) or - a rebase, an apply - take it back. A rebase is never continued: this project rewrites no history, and its
/// `--abort` is the one form of `git rebase` the history guard lets through (`repo_safety_hooks.rs`).
fn standing(dir: &Path) -> Vec<(String, String, String, bool)> {
    let mut out: Vec<(String, String, String, bool)> = HEADS
        .iter()
        .filter(|op| dir.join(op.marker).exists())
        .map(|op| {
            (
                op.marker.to_owned(),
                op.name.to_owned(),
                format!("-c core.editor=true {} --continue", op.verb),
                true,
            )
        })
        .collect();
    if let Ok(todo) = std::fs::read_to_string(dir.join(SEQUENCER)) {
        let verb = if todo.trim_start().starts_with("revert") {
            "revert"
        } else {
            "cherry-pick"
        };
        if !out.iter().any(|op| op.1 == verb) {
            out.push((
                SEQUENCER.to_owned(),
                format!("{verb} of several commits"),
                format!("-c core.editor=true {verb} --continue"),
                true,
            ));
        }
    }
    if dir.join(REBASE[1]).join("applying").exists() {
        out.push((
            REBASE[1].to_owned(),
            "mailbox apply (git am)".to_owned(),
            "am --abort".to_owned(),
            false,
        ));
    } else if let Some(marker) = REBASE.iter().find(|m| dir.join(m).exists()) {
        out.push((
            (*marker).to_owned(),
            "rebase".to_owned(),
            "rebase --abort".to_owned(),
            false,
        ));
    }
    out
}

/// `git -C <root> <args>`: its exit code, and its stdout then its stderr.
pub(super) fn git(root: &Path, args: &[&str]) -> Result<(i32, String), String> {
    let out = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .output()
        .map_err(|e| format!("git: {e}"))?;
    Ok((
        out.status.code().unwrap_or(-1),
        String::from_utf8_lossy(&out.stdout).into_owned() + &String::from_utf8_lossy(&out.stderr),
    ))
}

/// The lines of what a git command printed, each trimmed, the empty ones dropped.
pub(super) fn lines(out: &str) -> Vec<String> {
    out.lines()
        .map(str::trim)
        .filter(|l| !l.is_empty())
        .map(str::to_owned)
        .collect()
}

/// The tree's own git directory: a linked worktree's `<common>/worktrees/<name>`, where its operations' markers stand.
pub(super) fn git_dir(root: &Path) -> Result<PathBuf, String> {
    let (rc, out) = git(root, &["rev-parse", "--absolute-git-dir"])?;
    if rc != 0 {
        return Err(format!("{} is no git tree: {}", root.display(), out.trim()));
    }
    Ok(PathBuf::from(out.trim()))
}

/// The first [`SHOWN`] of `paths`, and how many more.
fn shown(paths: &[String]) -> String {
    let mut out = paths
        .iter()
        .take(SHOWN)
        .cloned()
        .collect::<Vec<_>>()
        .join(" ");
    if paths.len() > SHOWN {
        let _ = write!(out, " and {} more", paths.len() - SHOWN);
    }
    out
}

/// What stands unfinished in `root`, one line a refusal, each ending in the command that finishes it; empty where nothing does.
///
/// # Errors
///
/// Where `root` is no git tree, or git cannot be run.
pub fn refusals(root: &Path) -> Result<Vec<String>, String> {
    let dir = git_dir(root)?;
    let tree = root.display();
    let unmerged = lines(&git(root, &["diff", "--name-only", "--diff-filter=U"])?.1);
    let staged: Vec<String> = lines(&git(root, &["diff", "--cached", "--name-only"])?.1)
        .into_iter()
        .filter(|p| !unmerged.contains(p))
        .collect();
    // what a stopped operation is owed before its command: each unmerged path resolved and added
    let resolve = if unmerged.is_empty() {
        String::new()
    } else {
        format!(
            "resolve {} unmerged path(s) ({names}), `git -C {tree} add -- {names}`, then ",
            unmerged.len(),
            names = shown(&unmerged)
        )
    };
    // each refusal is pushed onto `stops`: the audit register's check counts those calls in this file (`audit_register/detect.rs`'s
    // `REFUSALS`), so a refusal added here owes its entry
    let mut stops = Vec::new();
    for (marker, name, finish, continued) in standing(&dir) {
        let held = if staged.is_empty() {
            String::new()
        } else {
            format!(", {} staged path(s) uncommitted", staged.len())
        };
        if continued {
            let verb = finish.split(' ').nth(2).unwrap_or_default();
            stops.push(format!(
                "a {name} is in progress in {tree} ({marker}{held}) - finish it: {resolve}`git -C {tree} {finish}` (or take it back: `git -C {tree} {verb} --abort`)"
            ));
        } else {
            stops.push(format!(
                "a {name} is in progress in {tree} ({marker}{held}) - this project rewrites no history, take it back: `git -C {tree} {finish}`"
            ));
        }
    }
    if !stops.is_empty() {
        return Ok(stops);
    }
    if !unmerged.is_empty() {
        stops.push(format!(
            "{} path(s) unmerged in {tree} ({names}) - resolve each, then `git -C {tree} add -- {names}` and commit",
            unmerged.len(),
            names = shown(&unmerged)
        ));
    }
    if !staged.is_empty() {
        stops.push(format!(
            "{} staged path(s) stand uncommitted in {tree} ({names}) - commit them: `git -C {tree} commit -m \"<what they are>\"` (or unstage them: `git -C {tree} restore --staged -- {names}`)",
            staged.len(),
            names = shown(&staged)
        ));
    }
    Ok(stops)
}

/// `l7r-gate land --unfinished [<tree>]`: each refusal on stderr, exit 2; silent, exit 0, where nothing stands unfinished. What
/// `scripts/sync-with-main.sh`'s push and `scripts/land-tooling.sh` ask before anything else.
pub(super) fn cli(root: &Path) -> crate::Reply {
    let (stderr, code) = match refusals(root) {
        Ok(stops) if stops.is_empty() => (String::new(), 0),
        Ok(stops) => (format!("unfinished: {}\n", stops.join("\nunfinished: ")), 2),
        Err(why) => (format!("unfinished: {why}\n"), 2),
    };
    crate::Reply {
        stdout: String::new(),
        stderr,
        code,
    }
}

#[cfg(test)]
pub(super) mod tests;
