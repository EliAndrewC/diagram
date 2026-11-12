//! What the landing asks in process, by the ruling (`ask:449-T83-scope`: "calling the ledger, `speckit-todo` and the claims
//! in-process"): the review ledger's owed rows (T117), the holding box (T118), and the claims' commands, scope split and checks in flight
//! (T82). Behind one seam so the landing's tests hand in the answers a scratch tree cannot give (a claims round, a ledger pass); the
//! real answers are each the function the command runs, so the reply and the usage line are the command's.

use std::path::Path;

use crate::Reply;

/// The landing's in-process questions.
pub(super) trait Inproc {
    /// `l7r-gate claims <args>`.
    fn claims(&self, args: &[String]) -> Reply;
    /// `l7r-gate reviews ledger-owed <args>`, run from `root`.
    fn ledger(&self, args: &[String], root: &Path) -> Reply;
    /// `l7r-gate speckit-todo --holding <dir>`, the landing's tasks in `L7R_LAND_TICKS`, run from `root`.
    fn holding(&self, dir: &str, ticks: &str, root: &Path) -> Reply;
    /// The claims bundles in flight (`claims_flight.live`).
    fn in_flight(&self, root: &Path) -> Result<Vec<String>, String>;
    /// The open findings a Rust stage's landing answers for, and the rest (`claims_scope.split`).
    fn scope_split(
        &self,
        root: &Path,
        report: &str,
        changed: &[String],
        seam: &[String],
    ) -> Result<(Vec<String>, Vec<String>), String>;
}

/// The ports themselves.
pub(super) struct Real;

impl Inproc for Real {
    fn claims(&self, args: &[String]) -> Reply {
        l7r_gate_claims::claims::cli(args)
    }

    fn ledger(&self, args: &[String], root: &Path) -> Reply {
        use l7r_gate_reviews::reviews::ledger_passes::{cli, Env};
        let mut env = Env::of_process();
        // the command's tree is the wrapper's `L7R_GATE_TREE`, else its working directory: the root, where `land.py` ran it
        if std::env::var_os("L7R_GATE_TREE").is_none() {
            env.tree = root.to_path_buf();
        }
        env.cwd = root.to_path_buf();
        cli(args, &env)
    }

    fn holding(&self, dir: &str, ticks: &str, root: &Path) -> Reply {
        l7r_gate_cohort::speckit_todo::holding_reply(dir, ticks, root)
    }

    fn in_flight(&self, root: &Path) -> Result<Vec<String>, String> {
        l7r_gate_claims::claims::flight_live(root)
    }

    fn scope_split(
        &self,
        root: &Path,
        report: &str,
        changed: &[String],
        seam: &[String],
    ) -> Result<(Vec<String>, Vec<String>), String> {
        l7r_gate_claims::claims::scope_split(root, report, changed, seam)
    }
}

#[cfg(test)]
mod tests {
    use super::{Inproc, Real};
    use l7r_gate_core::ci::fixtures::{put, repo};

    /// Each real answer is its port's: on a scratch tree with no claims, no ledger and no active task, each answers as its command does.
    #[test]
    fn each_real_answer_is_its_port_s() {
        let dir = repo("inproc-real");
        let args = |a: &[&str]| a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
        assert_eq!(
            Real.claims(&args(&["--root", &dir.to_string_lossy(), "nope"]))
                .code,
            2
        );
        put(&dir, "dev/review-ledger.md", "| a |\n");
        let ledger = dir
            .join("dev/review-ledger.md")
            .to_string_lossy()
            .into_owned();
        assert_eq!(Real.ledger(&args(&["--ledger", &ledger]), &dir).code, 0);
        put(&dir, "specs/1-x/tasks.md", "- [ ] T1 a\n");
        let held = Real.holding(&dir.join("specs/1-x").to_string_lossy(), "", &dir);
        assert_eq!((held.code, held.stdout.as_str()), (0, ""));
        assert_eq!(Real.in_flight(&dir), Ok(Vec::new()));
        let _ = Real.scope_split(&dir, "", &[], &[]);
    }
}
