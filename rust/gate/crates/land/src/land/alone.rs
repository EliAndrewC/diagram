//! A TASK LANDS ON ITS OWN (feature 451 T88). WHY: builders ran three at once 26% of the night's 580 minutes, a mean of 1.65 (measured
//! 2026-11-21 from each agent's span), because the landing refused any uncommitted file (`cheap`'s "uncommitted changes - commit them
//! first", `sync-with-main.sh push`'s "refuse dirty tree"), so a finished task waited until every builder in the clone was done and
//! its batch was committed whole - T48 and T78 CLEAR for hours behind T79.
//!
//! So with other work uncommitted in the clone, `make land` commits nothing and refuses nothing of it: `scripts/land-alone.sh` runs the
//! whole landing (`make land` again, its every refusal and gate) in the clone's persistent landing worktree, checked out at the clone's
//! HEAD - the task's own commit on the last landed tip - apart from the uncommitted work, with the clone's kept check results seeded
//! into it (the kept keys are the files' contents, not their paths), then the clone takes the landed tip, its uncommitted work kept.
//! WHY THE WORKTREE, of the three ways the launcher named (each measured 2026-11-21, T88's plan section): a gate in the clone stops
//! every other builder's writes while it runs (`gate_write_hooks`) and judges their half-done files, and a set-aside of those files
//! takes them from under builders still editing them; a judging of the task's files alone in the clone pushes a tree it did not judge,
//! where the push's own checks refuse a dirty tree anyway.

use std::path::Path;

use super::{name_of, Land};

/// The script that lands a task alone, under the gate tree's `scripts/`.
pub(super) const SCRIPT: &str = "land-alone.sh";
/// Set in the landing worktree's own `make land`: its tree is the landing, so it runs whole there, never sent to land alone again.
pub(super) const INNER: &str = "L7R_LAND_ALONE";
/// The script's exit where it refused before the worktree's landing ran (the task's own files uncommitted, another landing alone
/// running, the worktree not to be had): the one exit whose `end` line the clone's landing writes - every other is the worktree's own
/// landing's, its `end` written there, in the same feature's log.
pub(super) const REFUSED_FIRST: i32 = 6;

impl Land {
    /// Is the landing to run alone: work uncommitted in the clone, and this not the landing worktree's own run?
    pub(super) fn alone_owed(&self) -> Result<bool, String> {
        Ok(self.root.opt(INNER).is_none() && !self.dirty(&[])?.is_empty())
    }

    /// The landing run alone, its output passed through: its exit the worktree's landing's (0 landed, 3 landed with other sessions'
    /// edits merged, 4 landed but the clone could not take the tip), or a refusal before it ran - 2, its `end` written here.
    pub(super) fn alone(&self, d: &Path, tasks: &[String]) -> Result<i32, String> {
        let script = self.scripts.join(SCRIPT);
        self.say(&format!(
            "land: other work is uncommitted in the clone - {} lands alone, its commit gated in the landing worktree (451 T88)",
            tasks.join(" ")
        ));
        let code = self.loud(
            &[
                "bash",
                &script.to_string_lossy(),
                &name_of(d),
                &tasks.join(" "),
            ],
            &[],
        )?;
        if code == REFUSED_FIRST {
            return Ok(2);
        }
        self.ended.set(true);
        Ok(code)
    }
}

#[cfg(test)]
mod tests;
