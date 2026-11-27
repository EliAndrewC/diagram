//! ANOTHER WRITER IN THE CLONE (451 T242). WHY: on 2026-11-25 451 T238 landed from the clone while the coordinating session started
//! T240's builder there (its dispatch 12:28:29, nine seconds into the first pass). The gate ran green, the tick was written and staged,
//! and its commit made nothing: the clone's reflog holds no commit between the escape records (12:29:13) and the tick committed by hand
//! (12:29:39), and the exit of the landing's `git commit` was never read. `scripts/sync-with-main.sh done` then refused the dirty
//! clone ("uncommitted changes - commit first"), and the revert, aimed at HEAD - the escape records' commit, not a tick - was refused by
//! the staged tick ("your local changes would be overwritten"). Why the commit made nothing is not measured (a concurrent git's
//! `index.lock` is the likely cause: a held lock fails a commit with exit 128 and leaves what was added staged, observed 2026-11-25 on a
//! scratch repository).
//!
//! So: the changes in the clone that are not the landing's own are named, with an open builder handoff that names the clone, among the
//! first pass's refusals AND again just before the ticks, where a writer that arrived during the gate is met before anything is ticked;
//! and the tick's own commit is checked ([`Land::commit_tick`]), its ticks put back where it fails. A dirty clone at the start still
//! lands alone (451 T88, [`super::alone`]); its worktree's own run asks the same, where nobody else writes.
//!
//! A builder's linked worktree (today's parallel trial: builders in worktrees, their commits carried into the clone by cherry-pick)
//! bears on none of this: its files and its index are its own, never in the clone's `git status`, and a handoff naming the worktree
//! (`<clone>-t235`) does not name the clone.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_shared::py_text::strip;

use super::{rel_of, Land};

/// How many of the foreign changes a refusal shows.
const SHOWN: usize = 6;
/// The handoffs' directory under the common git directory (`context_cap_hooks.rs`'s `HANDOFFS`).
const HANDOFFS: &str = "l7r-handoffs";
/// A commit refused for a lock another git process holds is tried this many times, a poll apart.
const COMMIT_TRIES: u32 = 3;
const COMMIT_POLL_MS: u64 = 500;
/// A handoff older than this is no open builder's (a knob, a CONVENTION: a builder's handoff is read by the fresh builder dispatched
/// after it, within the session's hour or so). WHY: task numbers repeat across features - measured 2026-11-25, 26 of the clone's 538
/// handoffs named the clone, carried a task open in some other feature's tasks.md, and were 2 to 5 days old; none was younger.
const HANDOFF_FRESH_S: u64 = 24 * 3600;

impl Land {
    /// The changes in the clone that are not this landing's own - each `git status --porcelain` line, stripped - asked after the
    /// landing's own escape records are committed (feature 408), so what is left is another writer's.
    fn foreign(&self) -> Result<Vec<String>, String> {
        self.commit_escape_records()?;
        let out = self.run(&["git", "status", "--porcelain"], &[])?.1;
        Ok(out
            .lines()
            .map(strip)
            .filter(|l| !l.is_empty())
            .map(str::to_owned)
            .collect())
    }

    /// The open builder handoffs that name this clone: `<common git dir>/l7r-handoffs/T<n>-<agent>.md` written in the last day
    /// ([`HANDOFF_FRESH_S`]) whose text names the clone's root as a whole path - not a worktree beside it, `<root>-t235` - and whose task
    /// is not landed here and is open in some `specs/*/tasks.md` (a handoff's task ticked is a closed handoff, as the context-cap guard
    /// reads a resume).
    pub(super) fn open_handoffs(&self, tasks: &[String]) -> Result<Vec<PathBuf>, String> {
        let common = strip(
            &self
                .run(
                    &[
                        "git",
                        "rev-parse",
                        "--path-format=absolute",
                        "--git-common-dir",
                    ],
                    &[],
                )?
                .1,
        )
        .to_owned();
        let dir = Path::new(&common).join(HANDOFFS);
        let root = self.root.to_string_lossy().into_owned();
        let open: Vec<String> = self
            .each_spec("tasks.md")
            .iter()
            .filter_map(|rel| std::fs::read_to_string(self.root.join(rel)).ok())
            .flat_map(|text| open_tasks(&text))
            .collect();
        let mut found: Vec<PathBuf> = std::fs::read_dir(&dir)
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.path())
            .filter(|p| {
                fresh(p)
                    && handoff_task(p).is_some_and(|t| !tasks.contains(&t) && open.contains(&t))
                    && std::fs::read_to_string(p).is_ok_and(|text| names_path(&text, &root))
            })
            .collect();
        found.sort();
        Ok(found)
    }

    /// The refusal of another writer's changes in the clone, '' where there are none.
    pub(super) fn writer_refusal(&self, tasks: &[String]) -> Result<String, String> {
        let changes = self.foreign()?;
        if changes.is_empty() {
            return Ok(String::new());
        }
        let mut shown = changes
            .iter()
            .take(SHOWN)
            .cloned()
            .collect::<Vec<_>>()
            .join("; ");
        if changes.len() > SHOWN {
            let _ = write!(shown, " and {} more", changes.len() - SHOWN);
        }
        let handoffs = self.open_handoffs(tasks)?;
        let writer = if handoffs.is_empty() {
            String::new()
        } else {
            let named: Vec<String> = handoffs.iter().map(|p| p.display().to_string()).collect();
            format!(
                "; an open builder handoff names the clone: {}",
                named.join(", ")
            )
        };
        Ok(format!("uncommitted changes in the clone, not this landing's: {shown}{writer} - commit them (or let their writer finish), then land"))
    }

    /// The tick's commit, tried again while another git process holds the index's lock; the commit's id, or what refused it.
    pub(super) fn commit_tick(
        &self,
        add: &[&str],
        message: &str,
    ) -> Result<Result<String, String>, String> {
        let (rc, out) = self.run(add, &[])?;
        if rc != 0 {
            return Ok(Err(first_line(&out, "git add", rc)));
        }
        let mut tries = 0;
        loop {
            tries += 1;
            let (rc, out) = self.run(&["git", "commit", "-q", "-m", message], &[])?;
            if rc == 0 {
                break;
            }
            if !out.contains("index.lock") || tries >= COMMIT_TRIES {
                return Ok(Err(first_line(&out, "git commit", rc)));
            }
            self.clock
                .sleep(std::time::Duration::from_millis(COMMIT_POLL_MS));
        }
        Ok(Ok(
            strip(&self.run(&["git", "rev-parse", "HEAD"], &[])?.1).to_owned()
        ))
    }

    /// The ticks put back where they did not go out: their files as HEAD holds them, in the index and the tree (`git checkout HEAD`,
    /// so nothing the tick staged stays staged), the archives a tick created removed (feature 449 T142), and the fixes' rows pending
    /// again (451 T182). The tick's files hold no other writer's edit: the clone held none just before the ticks ([`Land::writer_refusal`]).
    pub(super) fn put_back(&self, d: &Path, staged: &[&str]) -> Result<(), String> {
        let rel = rel_of(&self.root, d);
        if !staged.is_empty() {
            let mut reset = vec!["git", "reset", "-q", "--"];
            reset.extend(staged);
            self.run(&reset, &[])?;
        }
        self.run(&["git", "checkout", "HEAD", "--", &rel], &[])?;
        self.run(
            &[
                "git",
                "clean",
                "-q",
                "-f",
                "--",
                &format!("{rel}/tasks-done.md"),
                &format!("{rel}/plan-done.md"),
            ],
            &[],
        )?;
        Ok(())
    }
}

/// Was `p` written within [`HANDOFF_FRESH_S`]?
fn fresh(p: &Path) -> bool {
    std::fs::metadata(p)
        .and_then(|m| m.modified())
        .is_ok_and(|t| t.elapsed().is_ok_and(|age| age.as_secs() < HANDOFF_FRESH_S))
}

/// The first line of what a git command said, or its exit.
fn first_line(out: &str, what: &str, rc: i32) -> String {
    let out = strip(out);
    match out.lines().next() {
        Some(l) => format!("{what}: {l}"),
        None => format!("{what} exited {rc}"),
    }
}

/// A handoff's task: its file name's `T<n>` before the first `-`. A FINISHED handoff is none (451 T352): a build half's
/// `<task>-build.md` (a bundle's `<a>-<b>-build.md`), which `make builder-brief` names for a builder that ended as briefed and its
/// closing half reads - its writer has stopped, so it names no writer in the clone; `done-pending-<task>.md`, which a brief names for
/// a builder that stops early, opens with no `T<n>` and is none already. Open is the context cap's own `T<n>-<agent id>.md`.
fn handoff_task(p: &Path) -> Option<String> {
    if p.extension().is_none_or(|e| e != "md") {
        return None;
    }
    let name = p.file_name()?.to_string_lossy().into_owned();
    if name.ends_with("-build.md") {
        return None;
    }
    let task = name.split('-').next()?;
    let digits = task.strip_prefix('T')?;
    let body = digits.trim_end_matches(|c: char| c.is_ascii_lowercase());
    (!body.is_empty() && body.chars().all(|c| c.is_ascii_digit()) && name.contains('-'))
        .then(|| task.to_owned())
}

/// The open tasks of a tasks.md: each `- [ ] T<n>` line's id.
fn open_tasks(text: &str) -> Vec<String> {
    text.lines()
        .filter_map(|l| l.trim_start().strip_prefix("- [ ] "))
        .filter_map(|rest| rest.split_whitespace().next())
        .filter(|t| t.starts_with('T'))
        .map(str::to_owned)
        .collect()
}

/// Does `text` name `path` as a whole path: each place it stands followed by nothing, or by a character no path name goes on with
/// (`/`, a space, a quote, a stop) - never `-`, `_`, `.` followed by a name, or a letter or digit, as `<root>-t235` goes on?
fn names_path(text: &str, path: &str) -> bool {
    text.match_indices(path).any(|(at, _)| {
        let mut rest = text[at + path.len()..].chars();
        match rest.next() {
            Some(c) if c.is_alphanumeric() || c == '-' || c == '_' => false,
            Some('.') => !rest
                .next()
                .is_some_and(|n| n.is_alphanumeric() || n == '_' || n == '-'),
            Some(_) | None => true,
        }
    })
}

#[cfg(test)]
mod tests;
