//! THE PUSH'S OWN HOLDS, ASKED IN THE FIRST PASS (451 T413). WHY: `scripts/sync-with-main.sh`'s push refused two things the landing's
//! first pass never asked, so a landing met them only after its whole gate (451 T307 part 2's parity table): a clone whose history
//! shares no commit with main's (`refuse_unrelated_history`, feature 301), and a feature in progress among EVERY spec directory the
//! delta touches and the one `.specify/feature.json` names (feature 133's rule), where the first pass ([`super::ready`]'s `hold`)
//! asked the landed feature alone.
//!
//! The in-progress rule asks each directory what the push asks it, through the same readers: `speckit-todo --holding` (the landing's
//! in-process `holding`, `shared::speckit::holding_with`, handed the landing's tasks as the push's `L7R_LAND_TICKS` carries them, an
//! error read as held - the push's `|| echo fail-closed`), then `speckit-todo --closed-by-status` (`shared::speckit::closed_by_status`,
//! an error read as not closed), the pointer read by `json-field` (`l7r_gate_core::logs::json_field`). Only the loop over the
//! directories is this file's copy of the shell's; the landed feature is left to `hold`, which asks it with the landing's ready ruling.
//! A directory other than the landed one held is always the push's refusal: its exception is a delta of that feature's own `specs/`
//! directory alone, and a landing's tick commit touches the landed one.
//!
//! The unrelated-history question is a second copy of the shell's two git questions, its words the shell's but for the mirror, named by where it is (the shell's `$MAIN`): the shell function also
//! serves `sync_in`, which runs no Rust before it, and one function both could call would be a new command of the gate.

use std::path::Path;

use l7r_shared::py_text::strip;

use super::{name_of, rel_of, Land};

impl Land {
    /// The push's `refuse_unrelated_history`, after the pass's fetch: '' where HEAD or origin/main is missing or they share a commit.
    pub(super) fn unrelated_history(&self) -> Result<String, String> {
        // the fetch, once a landing (`delta_names`)
        self.delta_names()?;
        for rev in ["HEAD", "origin/main"] {
            if self
                .run(&["git", "rev-parse", "-q", "--verify", rev], &[])?
                .0
                != 0
            {
                return Ok(String::new());
            }
        }
        if self
            .run(&["git", "merge-base", "HEAD", "origin/main"], &[])?
            .0
            == 0
        {
            return Ok(String::new());
        }
        let root = self.root.display();
        Ok(format!("this clone's history shares no commit with main's - main's history was rewritten (feature 301's scrub, dev/history-rewrite-301.md). A pull would merge the old history back in. Re-clone it: git clone <the mirror> {root}.new (the mirror is the directory above .clones/), cherry-pick any unpushed commits (git log --oneline HEAD --not --remotes), then replace {root}"))
    }

    /// The push's in-progress rule over every other spec directory the delta touches and the feature pointer: one refusal for each
    /// held - a landing ruled ready too, since `L7R_LAND_READY` exempts the landed feature's hold alone (451 T432).
    pub(super) fn others_in_progress(
        &self,
        d: &Path,
        tasks: &[String],
    ) -> Result<Vec<String>, String> {
        let own = rel_of(&self.root, d);
        let mut dirs: Vec<String> = self
            .delta_names()?
            .iter()
            .filter_map(|n| {
                let mut parts = n.splitn(3, '/');
                match (parts.next(), parts.next(), parts.next()) {
                    (Some("specs"), Some(dir), Some(_)) => Some(format!("specs/{dir}")),
                    _ => None,
                }
            })
            .collect();
        dirs.push(self.pointer());
        dirs.sort();
        dirs.dedup();
        let (ticks, number) = (tasks.join(" "), name_of(d));
        let number = number.split('-').next().unwrap_or_default();
        let mut out = Vec::new();
        for rel in dirs.iter().filter(|r| !r.is_empty() && **r != own) {
            let dir = self.root.join(rel);
            if !dir.join("tasks.md").is_file() {
                continue;
            }
            let held = self
                .inproc
                .holding(&dir.to_string_lossy(), &ticks, &self.root);
            let said = strip(&(held.stdout + &held.stderr)).to_owned();
            if held.code == 0 && said.is_empty() {
                continue;
            }
            if l7r_shared::speckit::closed_by_status(&dir).unwrap_or(false) {
                continue;
            }
            out.push(format!("{rel} has a task IN PROGRESS and the push lands no feature in progress (feature 133): it holds {said} - land its task with its own make land, or move this landing's change to another clone; feature {number}'s landing waits"));
        }
        Ok(out)
    }

    /// `.specify/feature.json`'s `feature_directory`, its trailing slashes dropped, '' for none - as the push's `json-field` reads it.
    fn pointer(&self) -> String {
        let file = self.root.join(".specify/feature.json");
        let got = l7r_gate_core::logs::json_field(&[
            file.to_string_lossy().into_owned(),
            "feature_directory".to_owned(),
        ]);
        let dir = strip(&got.stdout).trim_end_matches('/');
        if dir == "-" {
            String::new()
        } else {
            dir.to_owned()
        }
    }
}
