//! The `Blocks:` clue read and each piece's blocked task (451 T243, amendment (l); the defaults are `book`'s doc).

use super::{review_cat, Blocks, Cand, Ix, Key, PAGES};

impl Ix<'_> {
    /// A clue read as the task it blocks: `none` none; `<feature> T<n>` that task (a feature's number read as the feature it opens);
    /// `T<n>` alone that task under the feature `home` (the work's own); "" (no clue) `default`.
    pub(super) fn resolve(&self, clue: &str, default: Option<&Key>, home: &str) -> Option<Key> {
        let words: Vec<&str> = clue.split_whitespace().collect();
        match words[..] {
            [] => default.cloned(),
            ["none"] => None,
            [task] => Some((home.to_owned(), task.to_owned())),
            [f, task, ..] => {
                let open = format!("{f}-");
                let feature = self
                    .features
                    .iter()
                    .find(|x| *x == f || x.starts_with(&open))
                    .map_or_else(|| f.to_owned(), Clone::clone);
                Some((feature, task.to_owned()))
            }
        }
    }

    /// The task a candidate's piece blocks, the waiter blocking `blocked` (451 T243's defaults, each the plan's): its clue where it gave
    /// one; else a page session or research pass none, a builder its own task (else the waiter's), a run or review agent the waiter's.
    pub(super) fn target(&self, c: Cand, piece: (f64, f64), blocked: Option<&Key>) -> Option<Key> {
        match c {
            Cand::Run(i) => {
                // with no clue: its waiter's task, but a landing its batch, a session's own check or background command the
                // session's own, and a detached wait loop none (451 T298)
                let default = match &self.run_blocks[i] {
                    Blocks::Waiter => blocked,
                    Blocks::Nothing => None,
                    Blocks::Task(k) => Some(k),
                };
                self.resolve(&self.run_clue[i], default, &self.run_key[i].0)
            }
            Cand::Agent(i) => {
                let a = &self.w.agents[i];
                let own = &self.agent_key[i];
                let default = match review_cat(&a.kind) {
                    Some(PAGES) => None,
                    None if own.1 != "-" => Some(own),
                    _ => blocked,
                };
                self.resolve(&self.agent_clue[i], default, &own.0)
            }
            Cand::Pages => self
                .w
                .pages
                .iter()
                .find(|p| p.t0 <= piece.0 && piece.1 <= p.t1 && !p.blocks.is_empty())
                .and_then(|p| self.resolve(&p.blocks, None, &p.key.0)),
        }
    }
}
