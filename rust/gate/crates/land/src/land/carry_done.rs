//! THE LANDING CARRIES ITS TASKS' DONE COMMITS FIRST (feature 451 T397 part (c)). WHY: since 451 T394 a builder's work is one commit
//! `make builder-done` keeps at `refs/l7r/done/<feature>-<task>`, and the session carried each with `make carry COMMIT=` before `make
//! land` - a hand step for every task of a batch, each its own round trip while the next landing waited, and a landing whose carry was
//! forgotten landed its tick without its code (451 T270's, which 451 T294's named-file refusal catches only where the carry ADDS a file
//! its words name; 451 T447).
//!
//! So `make land F= T="<tasks>"` carries, before anything else asks the tree, the done commits of the tasks it lands that the landing
//! tree's HEAD does not hold (`l7r_gate_task::builder_done::to_carry`: by the author's time and subject a cherry-pick keeps), each
//! once, oldest first, through `make carry COMMIT=`'s own code ([`super::carry::cli`], its conflict rules and its verified end - which
//! deletes the done ref where it runs in the clone). Any carry that does not end verified stops the landing with nothing landed and
//! nothing ticked, naming the commit and the hand command; the carries before it stay carried, in HEAD and verified, and are named.
//! A task with no done ref carries nothing and writes no `carry` phase line.
//!
//! THE ORDER HOLDS BY WHERE IT IS CALLED ([`super::Land::land`]): after the unfinished-work refusal (a pick standing is finished by
//! hand first - the carry would refuse it anyway) and BEFORE the land-alone choice, the first pass and the gate. Before the gate,
//! because a write to the clone while its gate runs voids the gate ("tree moved"); before the land-alone choice, because a dirty clone
//! lands in the landing worktree checked out at the clone's HEAD, which must already hold the carried commits (a carry run in that
//! linked worktree would keep the ref, 451 T404); before the first pass, so its refusals - each task's tick check, 451 T294's named
//! files - read the carried HEAD, every one of them asking git afresh (nothing of HEAD is read or cached before this step).
//!
//! A LANE BATCH CARRIES ONLY WHAT ITS BATCH LINE NAMED (461 T52, plan D14): under `L7R_LANE_BATCH` the done refs are still read live,
//! but a commit is carried only where the batch's `batch` line in `l7r-lane/lane.jsonl` (the git common directory) names its sha,
//! in full or shortened; the rest - a task's ref a later hand-in moved after the batch formed - are left, their refs kept, for a later
//! batch, and said. WHY: the lane carries the batch's shas itself before `make land` (its `runner/run.rs`), so the live read carried
//! the moved ref's NEW sha on top - a hand-in landed inside a batch that never named it, unbounded on a resumed batch. The line is
//! read here, not through the lane crate, which builds on this one's neighbor `task` (as the `tree` crate's T17 reads it). A batch no
//! line names, or one a `landed` line ended (the variable exported by hand, or no log), is no lane batch: the landing carries as
//! before.

use std::path::Path;

use super::{name_of, Land};

impl Land {
    /// Each done commit of `tasks` the landing tree's HEAD lacks, carried oldest first; 0 where all carried (or none waits), else 2
    /// with the stop said.
    pub(super) fn carry_done(&self, d: &Path, tasks: &[String]) -> Result<i32, String> {
        let mut waiting = l7r_gate_task::builder_done::to_carry(&self.root, &name_of(d), tasks);
        let batch = self.root.var("L7R_LANE_BATCH");
        if let Some(named) = batch_named(&self.root, &batch) {
            let (kept, left): (Vec<_>, Vec<_>) = waiting.into_iter().partition(|(sha, _)| {
                named
                    .iter()
                    .any(|n| !n.is_empty() && sha.starts_with(n.as_str()))
            });
            if !left.is_empty() {
                let shorts: Vec<String> = left
                    .iter()
                    .map(|(sha, _)| sha.chars().take(10).collect())
                    .collect();
                self.say(&format!(
                    "land: lane batch {batch}: left {} done commit(s) its batch line does not name, for a later batch (461 T52, D14): {}",
                    left.len(),
                    shorts.join(", ")
                ));
            }
            waiting = kept;
        }
        if waiting.is_empty() {
            return Ok(0);
        }
        self.phase("carry", || {
            self.say(&format!(
                "land: carrying {} done commit(s) of {} that HEAD does not hold, oldest first (451 T397)",
                waiting.len(),
                tasks.join(" ")
            ));
            let mut carried: Vec<String> = Vec::new();
            for (sha, refs) in &waiting {
                let said = super::carry::cli(&[String::new(), sha.clone()], &self.root);
                self.pass_through(&said);
                let short: String = sha.chars().take(10).collect();
                if said.code != 0 {
                    let before = Some(carried.join(", "))
                        .filter(|c| !c.is_empty())
                        .map_or_else(String::new, |c| format!("; carried before it, in HEAD and verified: {c}"));
                    self.warn(&format!(
                        "land: refused before anything ran - nothing landed, nothing ticked: the done commit {short} ({}) did not carry (the carry's lines above){before}. Finish it by hand - what the carry names above, then `make carry COMMIT={sha}`, which verifies it and ends its wait - then make land again",
                        refs.join(", ")
                    ));
                    return Ok(2);
                }
                carried.push(short);
            }
            Ok(0)
        })
    }
}

/// The changes the last `batch` line of `batch` in `l7r-lane/lane.jsonl` names, None where `batch` is empty, no line names it or a
/// `landed` line of it follows (a batch done is no lane batch: a by-hand run naming it carries as before; a `stop` ends no batch, which
/// the lane resumes); a line that does not parse is skipped, as the lane skips it.
fn batch_named(root: &Path, batch: &str) -> Option<Vec<String>> {
    if batch.is_empty() {
        return None;
    }
    let common = l7r_shared::checks::common_dir(root);
    let text = std::fs::read_to_string(common.join("l7r-lane/lane.jsonl")).unwrap_or_default();
    let mut named = None;
    for l in text
        .lines()
        .filter_map(|l| serde_json::from_str::<serde_json::Value>(l).ok())
        .filter(|l| l["batch"] == batch)
    {
        match l["event"].as_str().unwrap_or_default() {
            "batch" => {
                named = Some(
                    l["changes"]
                        .as_array()
                        .map(|c| {
                            c.iter()
                                .filter_map(|s| s.as_str().map(str::to_owned))
                                .collect()
                        })
                        .unwrap_or_default(),
                );
            }
            "landed" => named = None,
            _ => {}
        }
    }
    named
}

#[cfg(test)]
mod tests;
