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

    /// 461 T05 (plan D4): a claims round dispatched from a BUILDER's pool tree is seen in flight by the landing asked from another
    /// tree of the same clone - the lane's tree, the clone itself - because `make claims-bundle` marks it under `--root` its own
    /// toplevel and the mark lives in that tree's `git rev-parse --git-common-dir` (`claims/flight.rs`'s `dir`), which every linked
    /// worktree of a clone shares; a separate clone does not see it. The pool trees and the `-land` worktree are linked worktrees of the
    /// session clone (observed 2026-11-27, method: `git worktree list` in /diagram/.clones/diagram-backlog). RED FIRST: with the mark
    /// written in the builder tree's own `--git-dir` (a worktree's private directory) the lane's ask sees nothing, 2026-11-27.
    #[test]
    fn a_claims_round_marked_in_a_builder_s_tree_is_in_flight_from_the_lane_s_tree() {
        use l7r_gate_core::ci::fixtures::git;
        let dir = repo("inproc-flight");
        put(&dir, "a", "a\n");
        git(&dir, &["add", "-A"]);
        git(&dir, &["commit", "-qm", "base"]);
        let builder = dir.join("pool-tree");
        let lane = dir.join("lane-tree");
        for tree in [&builder, &lane] {
            git(
                &dir,
                &["worktree", "add", "-q", "--detach", &tree.to_string_lossy()],
            );
        }
        let common = std::path::PathBuf::from(git(
            &builder,
            &["rev-parse", "--path-format=absolute", "--git-common-dir"],
        ));
        let marks = common.join("claims-in-flight");
        std::fs::create_dir_all(&marks).unwrap();
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs_f64();
        let mark = format!("{{\"bundle\": \"/tmp/l7r-claims/t05\", \"at\": {now}}}");
        std::fs::write(marks.join("0123456789abcdef.json"), mark).unwrap();
        let seen = Ok(vec!["/tmp/l7r-claims/t05".to_owned()]);
        assert_eq!(Real.in_flight(&lane), seen);
        assert_eq!(Real.in_flight(&dir), seen);
        let other = repo("inproc-flight-other");
        assert_eq!(Real.in_flight(&other), Ok(Vec::new()));
    }

    /// 451 T157: the first pass's own ask (`cheap.rs`'s `--refuse --landing --tasks`), through the real ledger, lands past a record
    /// pass of another started task (449-x T2, named by its bundle) and still refuses one naming the landing's own T1.
    #[test]
    fn the_first_pass_leaves_another_started_task_s_record_pass_and_refuses_its_own() {
        let dir = repo("inproc-t157");
        let root = dir.to_path_buf();
        put(&dir, "dev/review-ledger.md", "| a |\n");
        put(&dir, "specs/449-x/tasks.md", "- [ ] T1 one\n- [ ] T2 two\n");
        let starts = ["T1", "T2"].map(|t| format!("{{\"feature\": \"449-x\", \"task\": \"{t}\", \"utc\": \"2026-11-22T16:16:21Z\"}}\n"));
        put(&dir, ".git/task-starts.jsonl", &starts.concat());
        let line = |agent: &str, subject: &str| {
            format!("{{\"date\": \"2026-11-22\", \"check\": \"quote-check\", \"subject\": \"{subject}\", \"agent\": \"{agent}\", \"segment\": 0, \"wall\": \"5 s\", \"tokens\": \"1k in (0k cached) / 0.5k out\"}}\n")
        };
        let other = line(
            "o1",
            "Run quote-check on the bundle /tmp/l7r-check/q-0229-quote-check-t2/MANIFEST.md",
        );
        put(&dir, "passes.jsonl", &other);
        let (log, ledger) = (root.join("passes.jsonl"), root.join("dev/review-ledger.md"));
        let (log, ledger, none) = (
            log.to_string_lossy(),
            ledger.to_string_lossy(),
            root.join("no-transcripts"),
        );
        let none = none.to_string_lossy();
        let ask = |tasks: &str| {
            let words = [
                "--log",
                &log,
                "--transcripts",
                &none,
                "--ledger",
                &ledger,
                "--refuse",
                "--landing",
                "449-x",
                "--tasks",
                tasks,
            ];
            Real.ledger(&words.map(str::to_owned), &root)
        };
        let left = ask("T1");
        let (code, owed) = (left.code, left.stderr.contains("| ? |"));
        assert_eq!((code, owed), (0, false));
        assert!(left.stdout.contains("449-x T2"), "{}", left.stdout);
        let own = line("m1", "449 T1 quote-check of the landing's own page");
        put(&dir, "passes.jsonl", &[other, own].concat());
        let refused = ask("T1");
        let (code, owed) = (refused.code, refused.stderr.contains("449 T1 quote-check"));
        assert_eq!((code, owed), (1, true));
    }
}
