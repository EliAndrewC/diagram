//! The gate's own tools (feature 449 phase 2): one binary the Makefile's gate recipes call, each subcommand ported from the Python piece it replaces (T062-T069).

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

pub use l7r_gate_arbiter::{arbiter, checks_door};
pub use l7r_gate_author as author;
pub use l7r_gate_checks::checks;
pub use l7r_gate_ci::ci;
pub use l7r_gate_claims::claims;
pub use l7r_gate_cohort::{close_check, cohort, make_docs, push, speckit_todo};
pub use l7r_gate_core::{codeid, difflib, logs, Reply};
pub use l7r_gate_land::land;
pub use l7r_gate_measure::{measure, preflight};
pub use l7r_gate_pages as pages;
pub use l7r_gate_plan::plan;
pub use l7r_gate_record::record;
pub use l7r_gate_registry as registry;
pub use l7r_gate_reviews::reviews;
pub use l7r_gate_rustc::rustc;
pub use l7r_gate_tree::{delta, exempt, lock, stamp, state, top};

/// `l7r-gate content-ids <path>...`: `<path> <id>` for each file (a tree's code ids, T062; in process since T247 deleted `codeid.py`).
fn content_ids(paths: &[String], root: &Path) -> Reply {
    let mut files: Vec<(PathBuf, Vec<u8>)> = Vec::new();
    for path in paths {
        match std::fs::read(root.join(path)) {
            Ok(data) => files.push((PathBuf::from(path), data)),
            Err(why) => {
                return Reply {
                    stdout: String::new(),
                    stderr: format!("l7r-gate: cannot read {path}: {why}\n"),
                    code: 1,
                }
            }
        }
    }
    let ids = codeid::content_ids(&files, &mut codeid::Cache::at(root));
    let mut stdout = String::new();
    for (p, id) in paths.iter().zip(ids) {
        let _ = writeln!(stdout, "{p} {id}");
    }
    Reply {
        stdout,
        stderr: String::new(),
        code: 0,
    }
}

/// `l7r-gate diff-run ...` (feature 449 T161): `--all`'s escape recorded in the guard log every escape writes to, under the session.
fn diff_run(args: &[String]) -> Reply {
    l7r_gate_diffrun::cli(
        args,
        &l7r_gate_diffrun::Ctx {
            log_dir: &l7r_shared::log::dir(),
            session: std::env::var("CLAUDE_CODE_SESSION_ID").unwrap_or_default(),
            cwd: std::env::current_dir().unwrap_or_default(),
        },
    )
}

/// `l7r-gate plan <verb>`, with `make plan-delta` and `make decide` (`plan delta <F>`, `plan decide <F> <T>`) running the push's
/// spec lint over the feature's every changed file first (451 T527). WHY: both linted plan.md alone where the push's `spec-lint
/// --delta` reads the feature's every file, so 461's three research.md figures passed `make plan-delta` and were refused at the
/// landing (observed 2026-11-27, method: that landing's refusal). Both run and are reported together (451 T25); a red lint turns
/// the verb's success into a refusal, its dispatch prompt withheld. `plan` and `check` are handed in (`plan::cli`, `checks::cli`), so a test asks them of fakes.
fn linted_plan(
    words: &[String],
    root: &Path,
    plan: &dyn Fn(&[String], &Path, &plan::Claims) -> Reply,
    check: &dyn Fn(&[String], &Path) -> Reply,
) -> Reply {
    let plan = |w: &[String]| plan(w, root, &claims::cli);
    let shown = match words.first().map(String::as_str) {
        Some("delta") => "plan-delta",
        Some("decide") => "decide",
        _ => return plan(words),
    };
    let Some(dir) = words.get(1).and_then(|f| plan::resolve_feature(f, root)) else {
        return plan(words);
    };
    let lint = check(
        &[
            "spec-lint".to_owned(),
            "--delta".to_owned(),
            root.display().to_string(),
            dir.display().to_string(),
        ],
        root,
    );
    let done = plan(words);
    if lint.code == 0 {
        return done;
    }
    let stdout = if done.code == 0 {
        String::new()
    } else {
        done.stdout
    };
    Reply {
        stdout,
        stderr: format!("{}{}{}{shown}: refused - the spec lint above, which the push runs over this feature's every changed file (451 T527): fix each finding in the form it names and run make {shown} again\n", done.stderr, lint.stdout, lint.stderr),
        code: 1,
    }
}

/// The tree the wrapper started this binary from (`L7R_GATE_TREE`), else the repository here.
fn gate_tree() -> PathBuf {
    std::env::var_os("L7R_GATE_TREE").map_or_else(top, PathBuf::from)
}

/// `L7R_CACHE_OFF` set to anything but empty or `0` turns the content cache off.
/// The working directory, where the landing, the lane (feature 461 T11: `make lane`, from any tree of the clone), `claim` and
/// `make-docs` start.
fn here() -> PathBuf {
    std::env::current_dir().unwrap_or_default()
}

fn cache_off(value: Option<&str>) -> bool {
    value.is_some_and(|v| !v.is_empty() && v != "0")
}

/// The command line as the process was given it (feature 449 T143): `log guard` reads its arguments' bytes, as `guard_log`'s Python read
/// its `sys.argv` (a gate's detail is `head -c 400` of its output, which can cut a character), and every other subcommand takes UTF-8 as
/// before - an argument that is not is refused with the exit (101) the old `std::env::args` panic gave.
#[must_use]
pub fn cli_os(args: &[std::ffi::OsString]) -> Reply {
    if let [verb, sub, rest @ ..] = args {
        if verb == "log" && sub == "guard" {
            return logs::guard::cli(rest, &mut std::io::stdin(), &l7r_shared::log::dir());
        }
    }
    match args
        .iter()
        .map(|a| a.clone().into_string())
        .collect::<Result<Vec<_>, _>>()
    {
        Ok(text) => cli(&text),
        Err(bad) => Reply {
            stdout: String::new(),
            stderr: format!(
                "l7r-gate: an argument is not UTF-8: {}\n",
                bad.to_string_lossy()
            ),
            code: 101,
        },
    }
}

/// The command line. `--version` is the one subcommand until the first port lands; an unknown one is refused by name, so a recipe that names a tool not yet ported fails rather than passes.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    match args.first().map(String::as_str) {
        Some("stamp") => stamp::cli(
            &args[1..],
            stamp::toplevel().as_deref(),
            &mut std::io::stdin(),
        ),
        Some("delta") => delta::cli(&args[1..], Path::new("."), &mut std::io::stdin()),
        Some("ci") => ci::gated::entry(&args[1..], &top()),
        Some("cohort") => cohort::cli(&args[1..], &top()),
        Some("measure") => measure::cli(&args[1..], &top()),
        Some("switches") => ci::switches::guarded(&args[1..], &top(), &ci::via_make::Live),
        Some("github-token") => ci::config::github_token(&top()),
        Some("check") => checks::cli(&args[1..], &top()),
        Some("plan") => linted_plan(&args[1..], &top(), &plan::cli, &checks::cli),
        Some("rust") => rustc::cli(&args[1..]),
        Some("push-gate") => push::gate_cli(&args[1..], &top()),
        Some("push-checks") => push::checks_cli(
            &args[1..],
            &gate_tree(),
            cache_off(std::env::var("L7R_CACHE_OFF").ok().as_deref()),
        ),
        Some("lock") => lock::cli(&args[1..], Path::new("/proc")),
        Some("own-make") => lock::own_make_cli(&args[1..], Path::new("/proc")),
        Some("state") => state::cli(&args[1..], &top()),
        Some("coverage-exempt") => exempt::cli(&args[1..], &top()),
        Some("content-ids") => content_ids(&args[1..], Path::new(".")),
        Some("log") => logs::log_cli(&args[1..], Path::new(".")),
        // the reason floor's form (`escape take`, an escape taken outside a hook, left with `reserve-prefix.py`'s reservation, T145)
        Some("escape") => logs::usage::escape_cli(&args[1..], &mut std::io::stdin()),
        Some("json-field") => logs::json_field(&args[1..]),
        // spec-kit's JSON reads, `common.sh`'s inline Python (feature 449 T143)
        Some("speckit") => author::speckit::cli(&args[1..]),
        Some("preflight") => preflight::cli(&args[1..]),
        Some("record") => record::cli(&args[1..]),
        Some("registry") => registry::cli::cli(&args[1..]),
        Some("arbiter") => arbiter::cli(&args[1..]),
        Some("checks-close") => checks_door::close_cli(&args[1..]),
        Some("reviews") => reviews::cli(&args[1..]),
        Some("gm-review") => reviews::gm_review::cli(&args[1..], claims::impl_check::missing_each),
        Some("speckit-todo") => speckit_todo::cli(&args[1..], Path::new(".")),
        Some("close-check") => close_check::cli(&args[1..], claims::impl_check::missing_each),
        Some("impl-check") => claims::impl_check::cli(&args[1..], &top()),
        Some("claims") => claims::cli(&args[1..]),
        Some(
            verb @ ("tick" | "task-start" | "task-unstart" | "task-withdraw" | "task-add"
            | "set-down" | "phase-read" | "builder-tree" | "builder-brief" | "builder-done"
            | "queue" | "queue-add" | "builder-next" | "closing-split"),
        ) => l7r_gate_task::cli(
            verb,
            &args[1..],
            &std::env::current_dir().unwrap_or_default(),
        ),
        Some("land") => land::cli(&args[1..], &here()),
        Some("lane") => l7r_gate_lane::cli(&args[1..], &here()),
        Some("tunables") => claims::tunables_cli(&args[1..]),
        Some("research-backlog") => claims::backlog::backlog_cli(&args[1..]),
        Some("work-budget-bundle") => measure::work_budget_bundle::cli(&args[1..], &top()),
        Some("budget-change") => measure::budget_change::cli(&args[1..], &top()),
        // the authoring tools (feature 449 T135): the trials read the tree the wrapper names, as the Python read its own file's tree
        Some("claim") => author::claim::cli(&args[1..], &here()),
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
            &l7r_shared::tempdir::TempDir::new("gate-patch-selftest"),
        ),
        // the page sessions' tools (feature 449 T137): the runner starts this binary again for its detached queue
        Some(verb @ ("page-session" | "brief-load" | "coord" | "research-claims")) => {
            pages::cli(verb, &args[1..])
        }
        // the shared differential runner (feature 449 T161): `--all`'s escape recorded in the guard log every escape writes to
        Some("diff-run") => diff_run(&args[1..]),
        // the pool walk and its index (feature 449 T220): `make pool-index`, and the review gate's `find`
        Some("pool") => {
            let (stdout, stderr, code) = l7r_gate_pool::cli(&args[1..], &top());
            Reply {
                stdout,
                stderr,
                code,
            }
        }
        Some("make-docs") => make_docs::cli(&args[1..], &here()),
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
    use std::path::Path;

    /// The bytes' door (feature 449 T143): `log guard` reached with its arguments as bytes, anything else as text, a byte that is not
    /// UTF-8 refused outside `log guard`.
    #[test]
    fn the_command_line_as_bytes() {
        use std::ffi::OsString;
        use std::os::unix::ffi::OsStringExt as _;
        let os = |a: &[&str]| a.iter().map(OsString::from).collect::<Vec<_>>();
        assert_eq!(
            super::cli_os(&os(&["--version"])).stdout,
            "l7r-gate 0.1.0\n"
        );
        assert_eq!(super::cli_os(&os(&["log", "guard"])).code, 2, "too few");
        let mut bad = os(&["--version"]);
        bad.push(OsString::from_vec(vec![0xff]));
        let r = super::cli_os(&bad);
        assert_eq!((r.code, r.stderr.contains("not UTF-8")), (101, true));
    }

    fn said(stdout: &str, stderr: &str, code: i32) -> super::Reply {
        super::Reply {
            stdout: stdout.to_owned(),
            stderr: stderr.to_owned(),
            code,
        }
    }

    /// 451 T527: `make plan-delta` and `make decide` run the push's spec lint over the feature's every changed file, both reported
    /// together; a red lint withholds the verb's dispatch prompt; another verb, or a feature that names no directory, asks no lint.
    #[test]
    fn plan_delta_and_decide_run_the_spec_lint_over_the_feature() {
        let root = l7r_shared::tempdir::TempDir::new("gate-linted-plan");
        std::fs::create_dir_all(root.join("specs/200-a-feature")).unwrap();
        let words = |w: &[&str]| w.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
        let asked = std::cell::RefCell::new(Vec::new());
        let red = |a: &[String], _: &Path| {
            asked.borrow_mut().push(a.join(" "));
            said(
                "specs/200-a-feature/research.md:3: the figure '40 s' carries no\n",
                "",
                1,
            )
        };
        let green = |_: &[String], _: &Path| said("", "", 0);
        let prompt = |_: &[String], _: &Path, _: &crate::plan::Claims| said("PROMPT\n", "", 0);
        let refused = |_: &[String], _: &Path, _: &crate::plan::Claims| {
            said("", "decide: refused - PLANWHY\n", 2)
        };
        let r = super::linted_plan(&words(&["delta", "200"]), &root, &prompt, &red);
        assert_eq!((r.code, r.stdout.as_str()), (1, ""));
        assert!(r.stderr.contains("'40 s'") && r.stderr.ends_with("run make plan-delta again\n"));
        assert!(
            asked.borrow()[0].starts_with("spec-lint --delta ")
                && asked.borrow()[0].ends_with("specs/200-a-feature")
        );
        let r = super::linted_plan(&words(&["decide", "200", "T01"]), &root, &refused, &red);
        assert_eq!(r.code, 1);
        assert!(
            r.stderr.starts_with("decide: refused - PLANWHY\n")
                && r.stderr.contains("'40 s'")
                && r.stderr.contains("make decide again")
        );
        let r = super::linted_plan(&words(&["decide", "200", "T01"]), &root, &refused, &green);
        assert_eq!(
            (r.code, r.stderr.as_str()),
            (2, "decide: refused - PLANWHY\n")
        );
        let r = super::linted_plan(&words(&["delta", "200"]), &root, &prompt, &green);
        assert_eq!((r.code, r.stdout.as_str()), (0, "PROMPT\n"));
        asked.borrow_mut().clear();
        assert_eq!(
            super::linted_plan(&words(&["section", "200", "T01"]), &root, &prompt, &red).code,
            0
        );
        assert_eq!(
            super::linted_plan(&words(&["delta", "999"]), &root, &prompt, &red).code,
            0
        );
        assert!(asked.borrow().is_empty());
        assert_eq!(cli(&words(&["plan"])).code, 2);
    }

    #[test]
    fn it_says_its_version_and_refuses_what_it_does_not_know() {
        assert_eq!(cli(&["--version".to_owned()]).stdout, "l7r-gate 0.1.0\n");
        let unknown = cli(&["no-such-verb".to_owned()]);
        assert_eq!(unknown.code, 2);
        assert!(unknown.stderr.contains("no subcommand no-such-verb"));
        assert!(cli(&[]).stderr.contains("(none given)"));
        assert_eq!(cli(&["escape".to_owned()]).code, 2);
        // the differential runner's usage refusal (feature 449 T161), reached before any log or file
        assert!(cli(&["diff-run".to_owned()])
            .stderr
            .contains("the cases file is required"));
    }

    /// The lane (feature 461 T11): `lane status` reads the clone's lane from the working directory and ends 0; a verb it lacks is
    /// refused with its usage.
    #[test]
    fn the_lane_is_a_subcommand() {
        let status = cli(&["lane".to_owned(), "status".to_owned()]);
        assert_eq!(status.code, 0, "{}", status.stderr);
        assert!(status.stdout.starts_with("lane: "));
        assert_eq!(cli(&["lane".to_owned()]).code, 2);
    }

    #[test]
    fn the_doors_read_stdin_to_its_end() {
        // every door left with its last caller: `owed-door` with `entry_owed.py` (feature 449 T149), the checks and claims doors with
        // `review_snapshot.py` and `impl_check.py` (feature 449 T132)
        assert_eq!(cli(&["owed-door".to_owned()]).code, 2);
        assert_eq!(cli(&["checks-door".to_owned()]).code, 2);
        assert_eq!(cli(&["claims-door".to_owned()]).code, 2);
        assert_eq!(cli(&["impl-check".to_owned()]).code, 2);
        assert_eq!(cli(&["claims".to_owned()]).code, 2);
        assert_eq!(cli(&["tunables".to_owned(), "--bogus".to_owned()]).code, 2);
        assert_eq!(
            cli(&["research-backlog".to_owned(), "--bogus".to_owned()]).code,
            2
        );
        assert_eq!(cli(&["reviews".to_owned()]).code, 2);
        assert!(cli(&["pool".to_owned()])
            .stderr
            .starts_with("usage: pool index"));
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
            "speckit",
            "claim",
            "trial-start",
            "trial-review",
            "patch",
            "task-add",
            "task-unstart",
            "task-withdraw",
            "set-down",
        ] {
            assert_eq!(ask(&[verb]).code, 2, "{verb}");
        }
        assert_eq!(ask(&["patch", "--selftest"]).code, 0);
        let dir = l7r_shared::tempdir::TempDir::new("gate-cli-docs");
        assert_eq!(ask(&["make-docs", dir.to_str().unwrap()]).code, 2);
        assert!(super::gate_tree().is_absolute());
    }

    /// The page sessions' tools ported by feature 449 T137, each refusing an empty command line (the runner's launch raising on one).
    #[test]
    fn the_page_session_tools_are_subcommands() {
        let ask = |a: &[&str]| cli(&a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>());
        for verb in ["brief-load", "coord", "research-claims"] {
            assert_eq!(ask(&[verb]).code, 2, "{verb}");
        }
        assert_eq!(ask(&["page-session", "a", "b"]).code, 1);
    }

    #[test]
    fn the_stamp_and_the_delta_are_subcommands() {
        let ask = |a: &[&str]| cli(&a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>());
        assert_eq!(ask(&["delta", "nonsense"]).code, 2);
        assert_eq!(ask(&["stamp", "--nonsense"]).code, 2);
        assert_eq!(ask(&["state", "nonsense"]).code, 2);
        assert_eq!(ask(&["coverage-exempt", "nonsense"]).code, 2);
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
        let dir = l7r_shared::tempdir::TempDir::new("gate-cli");
        std::fs::write(dir.join("a.txt"), "x\n").unwrap();
        std::fs::write(dir.join("b.py"), "y = 1\n").unwrap();
        let names = |n: &[&str]| n.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
        let done = super::content_ids(&names(&["a.txt"]), &dir);
        assert_eq!(
            done.stdout,
            "a.txt 587be6b4c3f93f93c489c0111bba5596147a26cb\n"
        );
        let unread = super::content_ids(&names(&["no-such"]), &dir).stderr;
        assert!(unread.contains("cannot read no-such"));
        // a `.py` file's id is its blob id, with no Python asked (feature 449 T247)
        let python = super::content_ids(&names(&["b.py"]), &dir).stdout;
        let blob = super::codeid::git_blob_id(b"y = 1\n");
        assert_eq!(python, format!("b.py {blob}\n"));
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
