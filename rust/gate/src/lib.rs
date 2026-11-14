//! The gate's own tools (feature 449 phase 2): one binary the Makefile's gate recipes call, each subcommand ported from the Python piece it replaces (T062-T069).

use std::path::{Path, PathBuf};

pub use l7r_gate_arbiter::{arbiter, checks_door};
pub use l7r_gate_author as author;
pub use l7r_gate_bundle::owed_door;
pub use l7r_gate_checks::checks;
pub use l7r_gate_ci::ci;
pub use l7r_gate_claims::claims;
pub use l7r_gate_cohort::{close_check, cohort, make_docs, push, speckit_todo};
pub use l7r_gate_core::{codeid, difflib, logs, Reply};
pub use l7r_gate_land::{land, replay_owing};
pub use l7r_gate_measure::{measure, preflight};
pub use l7r_gate_plan::plan;
pub use l7r_gate_record::record;
pub use l7r_gate_reviews::reviews;
pub use l7r_gate_rustc::rustc;
pub use l7r_gate_tree::{delta, exempt, hashing, lock, stamp, state, top};

/// `l7r-gate content-ids <path>...`: `<path> <id>` for each file (a tree's code ids, T062).
fn content_ids(paths: &[String], root: &Path, python: &str) -> Reply {
    let fail = |stderr: String, code: i32| Reply {
        stdout: String::new(),
        stderr,
        code,
    };
    let mut files: Vec<(PathBuf, Vec<u8>)> = Vec::new();
    for path in paths {
        match std::fs::read(root.join(path)) {
            Ok(data) => files.push((PathBuf::from(path), data)),
            Err(why) => return fail(format!("l7r-gate: cannot read {path}: {why}\n"), 1),
        }
    }
    let script = codeid::script(root);
    match codeid::content_ids(&files, &mut codeid::Cache::at(root), python, &script) {
        Ok(ids) => Reply {
            stdout: paths
                .iter()
                .zip(ids)
                .map(|(p, id)| format!("{p} {id}\n"))
                .collect::<Vec<_>>()
                .concat(),
            stderr: String::new(),
            code: 0,
        },
        Err(why) => fail(format!("l7r-gate: {why}\n"), 1),
    }
}

/// The tree the wrapper started this binary from (`L7R_GATE_TREE`), else the repository here.
fn gate_tree() -> PathBuf {
    std::env::var_os("L7R_GATE_TREE").map_or_else(top, PathBuf::from)
}

/// `L7R_CACHE_OFF` set to anything but empty or `0` turns the content cache off.
fn cache_off(value: Option<&str>) -> bool {
    value.is_some_and(|v| !v.is_empty() && v != "0")
}

/// The command line. `--version` is the one subcommand until the first port lands; an unknown one is refused by name, so a recipe that names a tool not yet ported fails rather than passes.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    match args.first().map(String::as_str) {
        Some("stamp") => stamp::cli(
            &args[1..],
            stamp::toplevel().as_deref(),
            "python3",
            &mut std::io::stdin(),
        ),
        Some("delta") => delta::cli(&args[1..], Path::new("."), "python3", &mut std::io::stdin()),
        Some("ci") => ci::gated::entry(&args[1..], &top()),
        Some("cohort") => cohort::cli(&args[1..], &top(), "python3"),
        Some("measure") => measure::cli(&args[1..], &top()),
        Some("switches") => ci::switches::guarded(&args[1..], &top(), &ci::via_make::Live),
        Some("github-token") => ci::config::github_token(&top()),
        Some("check") => checks::cli(&args[1..], &top()),
        Some("plan") => plan::cli(&args[1..], &top(), &claims::cli),
        Some("rust") => rustc::cli(&args[1..]),
        Some("push-gate") => push::gate_cli(&args[1..], &top()),
        Some("push-checks") => push::checks_cli(
            &args[1..],
            &gate_tree(),
            cache_off(std::env::var("L7R_CACHE_OFF").ok().as_deref()),
        ),
        Some("lock") => lock::cli(&args[1..], Path::new("/proc")),
        Some("own-make") => lock::own_make_cli(&args[1..], Path::new("/proc")),
        Some("state") => state::cli(&args[1..], &top(), "python3"),
        Some("coverage-exempt") => exempt::cli(&args[1..], &top(), "python3"),
        Some("config-hash") => hashing::cli(&args[1..], &top(), "python3"),
        Some("content-ids") => content_ids(&args[1..], Path::new("."), "python3"),
        Some("log") => logs::log_cli(&args[1..], Path::new(".")),
        Some("escape") => logs::usage::escape_cli(&args[1..], &mut std::io::stdin()),
        Some("json-field") => logs::json_field(&args[1..]),
        Some("ruff-toml") => logs::ruff_cli(&mut std::io::stdin()),
        Some("preflight") => preflight::cli(&args[1..]),
        Some("record") => record::cli(&args[1..]),
        Some("arbiter") => arbiter::cli(&args[1..]),
        Some("checks-close") => checks_door::close_cli(&args[1..]),
        Some("owed-door") => {
            owed_door::serve(&mut std::io::stdin().lock(), &mut std::io::stdout().lock())
        }
        Some("reviews") => reviews::cli(&args[1..]),
        Some("gm-review") => reviews::gm_review::cli(&args[1..], claims::impl_check::missing_each),
        Some("speckit-todo") => speckit_todo::cli(&args[1..], Path::new(".")),
        Some("close-check") => close_check::cli(&args[1..], claims::impl_check::missing_each),
        Some("impl-check") => claims::impl_check::cli(&args[1..], &top()),
        Some("claims") => claims::cli(&args[1..]),
        Some(verb @ ("tick" | "task-start" | "task-add" | "set-down" | "phase-read")) => {
            l7r_gate_task::cli(
                verb,
                &args[1..],
                &std::env::current_dir().unwrap_or_default(),
            )
        }
        Some("land") => land::cli(&args[1..], &std::env::current_dir().unwrap_or_default()),
        Some("replay-owing") => replay_owing::cli(&args[1..]),
        Some("tunables") => claims::tunables_cli(&args[1..]),
        Some("work-budget-bundle") => measure::work_budget_bundle::cli(&args[1..], &top()),
        Some("budget-change") => measure::budget_change::cli(&args[1..], &top()),
        // the authoring tools (feature 449 T135): the trials read the tree the wrapper names, as the Python read its own file's tree
        Some("claim") => {
            author::claim::cli(&args[1..], &std::env::current_dir().unwrap_or_default())
        }
        Some("trial-start") => author::trial::start_cli(
            &args[1..],
            &gate_tree(),
            &std::env::var("TRIAL_APPROVED").unwrap_or_default(),
        ),
        Some("trial-review") => {
            author::trial::review_cli(&args[1..], &gate_tree(), Path::new("/tmp/l7r-check"))
        }
        Some("patch") => author::patch::cli(
            &args[1..],
            &mut std::io::stdin(),
            &l7r_guard::shared::tempdir::TempDir::new("gate-patch-selftest"),
        ),
        Some("make-docs") => {
            make_docs::cli(&args[1..], &std::env::current_dir().unwrap_or_default())
        }
        Some("--version") => Reply {
            stdout: format!("l7r-gate {}\n", env!("CARGO_PKG_VERSION")),
            stderr: String::new(),
            code: 0,
        },
        other => Reply {
            stdout: String::new(),
            stderr: format!(
                "l7r-gate: no subcommand {}\n",
                other.unwrap_or("(none given)")
            ),
            code: 2,
        },
    }
}

#[cfg(test)]
mod tests {
    use super::cli;

    #[test]
    fn it_says_its_version_and_refuses_what_it_does_not_know() {
        assert_eq!(cli(&["--version".to_owned()]).stdout, "l7r-gate 0.1.0\n");
        let unknown = cli(&["no-such-verb".to_owned()]);
        assert_eq!(unknown.code, 2);
        assert!(unknown.stderr.contains("no subcommand no-such-verb"));
        assert!(cli(&[]).stderr.contains("(none given)"));
        assert_eq!(cli(&["escape".to_owned()]).code, 2);
    }

    #[test]
    fn the_doors_read_stdin_to_its_end() {
        assert_eq!(cli(&["owed-door".to_owned()]).code, 0);
        // the checks and claims doors left with their last callers, `review_snapshot.py` and `impl_check.py` (feature 449 T132)
        assert_eq!(cli(&["checks-door".to_owned()]).code, 2);
        assert_eq!(cli(&["claims-door".to_owned()]).code, 2);
        assert_eq!(cli(&["impl-check".to_owned()]).code, 2);
        assert_eq!(cli(&["claims".to_owned()]).code, 2);
        assert_eq!(cli(&["tunables".to_owned(), "--bogus".to_owned()]).code, 2);
        assert_eq!(cli(&["reviews".to_owned()]).code, 2);
        assert_eq!(cli(&["tick".to_owned()]).code, 2);
        assert_eq!(
            cli(&["speckit-todo".to_owned(), "--bogus".to_owned()]).code,
            2
        );
    }

    /// The authoring tools and the two task tools ported by feature 449 T135, each refusing an empty command line by its exit 2.
    #[test]
    fn the_authoring_tools_are_subcommands() {
        let ask = |a: &[&str]| cli(&a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>());
        for verb in [
            "claim",
            "trial-start",
            "trial-review",
            "patch",
            "task-add",
            "set-down",
        ] {
            assert_eq!(ask(&[verb]).code, 2, "{verb}");
        }
        assert_eq!(ask(&["patch", "--selftest"]).code, 0);
        let dir = l7r_guard::shared::tempdir::TempDir::new("gate-cli-docs");
        assert_eq!(ask(&["make-docs", dir.to_str().unwrap()]).code, 2);
        assert!(super::gate_tree().is_absolute());
    }

    #[test]
    fn the_stamp_and_the_delta_are_subcommands() {
        let ask = |a: &[&str]| cli(&a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>());
        assert_eq!(ask(&["delta", "nonsense"]).code, 2);
        assert_eq!(ask(&["stamp", "--nonsense"]).code, 2);
        assert_eq!(ask(&["state", "nonsense"]).code, 2);
        assert_eq!(ask(&["coverage-exempt", "nonsense"]).code, 2);
        assert_eq!(ask(&["config-hash", "nonsense"]).code, 2);
        assert_eq!(ask(&["ci", "nonsense"]).code, 2);
        assert_eq!(ask(&["switches", "nonsense"]).code, 2);
        assert!([0, 1].contains(&ask(&["github-token"]).code));
        assert_eq!(ask(&["push-checks"]).code, 2);
        assert!(
            super::cache_off(Some("1"))
                && !super::cache_off(Some("0"))
                && !super::cache_off(Some(""))
                && !super::cache_off(None)
        );
        assert_eq!(ask(&["push-gate"]).code, 2);
        assert_eq!(ask(&["lock"]).code, 2);
        assert_eq!(ask(&["own-make"]).code, 2);
    }

    #[test]
    fn content_ids_answers_each_file_and_names_what_it_cannot_read() {
        let dir = l7r_guard::shared::tempdir::TempDir::new("gate-cli");
        std::fs::create_dir_all(dir.join("scripts/gates")).unwrap();
        std::fs::write(dir.join("a.txt"), "x\n").unwrap();
        std::fs::write(dir.join("b.py"), "y = 1\n").unwrap();
        std::fs::write(
            dir.join("scripts/gates/codeid.py"),
            "import sys\nfor a in sys.argv[2:]: print('id')\n",
        )
        .unwrap();
        let names = |n: &[&str]| n.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
        let done = super::content_ids(&names(&["a.txt"]), &dir, "python3");
        assert_eq!(
            done.stdout,
            "a.txt 587be6b4c3f93f93c489c0111bba5596147a26cb\n"
        );
        assert!(super::content_ids(&names(&["no-such"]), &dir, "python3")
            .stderr
            .contains("cannot read no-such"));
        assert!(
            super::content_ids(&names(&["b.py"]), &dir, "/no/such/python")
                .stderr
                .contains("cannot start")
        );
        assert_eq!(cli(&names(&["content-ids"])).code, 0);
    }
    /// What the claims tools and the modal tools read, each judged by its push gate (moved from `push/tests.rs` by feature 449 T92:
    /// the push's crate sits below the crates that own those paths).
    #[test]
    fn each_push_gate_judges_every_path_the_claims_and_modal_tools_read() {
        use crate::push::{judged, judges};
        let covered = |gate: &str, path: &str| {
            let probe =
                if crate::checks::has_ext(path, "json") || crate::checks::has_ext(path, "md") {
                    path.to_owned()
                } else {
                    format!("{}/x", path.trim_end_matches('/'))
                };
            !judged(judges(gate).unwrap().0, &[probe]).is_empty()
        };
        for p in crate::claims::read_paths() {
            assert!(covered("claims", p), "{p}");
        }
        assert!(covered("entry", crate::record::modals::MODALS));
    }
}
