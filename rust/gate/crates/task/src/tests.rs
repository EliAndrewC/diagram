//! What the task gate's tests share: a repository holding a feature whose every task answers its approach block, an `origin/main`,
//! the guard census kept off the live log, and a stand-in `codeid.py`; and the crate's own helpers.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::OnceLock;

use l7r_gate_core::ci::fixtures::{git, put, scratch};
use l7r_guard::shared::tempdir::TempDir;

use crate::tick::Ask;

pub(crate) const SPEC: &str = "# Feature 9001\n\n**Status**: In progress\n**Affects**: tooling\n";
pub(crate) const TASKS: &str = "# Tasks\n\n- [ ] T01 the first\n      research: rendering\n      verify: old\n- [ ] T02 the second\n- [ ] T03 physical\n      research: physical\n      - [ ] research pass\n- [x] T09 done\n";
pub(crate) const REASON: &str = "a test of the task gate";

/// The guard census of these tests, never the live one: one directory for the process (the plan crate's `quiet_census`).
pub(crate) fn quiet_census() -> PathBuf {
    static DIR: OnceLock<PathBuf> = OnceLock::new();
    DIR.get_or_init(|| {
        let dir = l7r_guard::shared::tempdir::beside_binary("gate-task-census");
        std::env::set_var("GUARD_LOG_DIR", &dir);
        dir
    })
    .clone()
}

/// A plan answering part A for each of `tasks`, as the checklist the fixture writes asks.
pub(crate) fn plan(tasks: &[&str]) -> String {
    tasks.iter().fold(String::new(), |mut all, t| {
        let _ = write!(
            all,
            "## {t} the task\n\n### {t} Approach (checklist part A)\n\n1. **one** answered\n\n"
        );
        all
    })
}

/// A repository at its first commit, `origin/main` a bare clone's, with `specs/9001-x` (spec, tasks, a plan answering every task),
/// the approach checklist, `dev/` and a stand-in `scripts/gates/codeid.py` (each file's id its bytes' length and its first line).
pub(crate) fn repo(tag: &str) -> TempDir {
    quiet_census();
    let dir = scratch(&format!("task-{tag}"));
    let root = dir.join("repo");
    std::fs::create_dir_all(&root).unwrap();
    git(&root, &["init", "-q", "-b", "main"]);
    git(&root, &["config", "user.email", "t@t"]);
    git(&root, &["config", "user.name", "t"]);
    git(&root, &["config", "commit.gpgsign", "false"]);
    put(&root, "specs/9001-x/spec.md", SPEC);
    put(&root, "specs/9001-x/tasks.md", TASKS);
    put(
        &root,
        "specs/9001-x/plan.md",
        &plan(&["T01", "T02", "T03", "T09"]),
    );
    put(
        &root,
        "docs/approach-checklist.md",
        "## A. the approach\n\n1. one\n",
    );
    put(&root, "dev/bypass-log/.keep", "");
    put(&root, "scripts/a.py", "x = 1\n");
    put(
        &root,
        "scripts/gates/codeid.py",
        "import sys\nfor n in sys.argv[2:]:\n    d = open(n, 'rb').read()\n    print(d.split(b'#')[0].strip().hex() or 'empty')\n",
    );
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "base"]);
    let origin = dir.join("origin.git");
    git(&dir, &["init", "-q", "--bare", &origin.to_string_lossy()]);
    git(
        &root,
        &["remote", "add", "origin", &origin.to_string_lossy()],
    );
    git(&root, &["push", "-q", "origin", "main"]);
    git(&root, &["fetch", "-q", "origin"]);
    dir
}

/// The repository of a [`repo`] fixture.
pub(crate) fn root_of(dir: &Path) -> PathBuf {
    dir.join("repo")
}

/// A tick's ask in the fixture: the plan gate escaped with a reason, the tools the fixture's own.
pub(crate) fn ask<'a>(root: &'a Path, dir: &'a Path, task: &'a str, note: &'a str) -> Ask<'a> {
    Ask {
        root,
        dir,
        task,
        note,
        escaped: Some(REASON.to_owned()),
        tree: root.to_path_buf(),
    }
}

/// An environment of the given names alone.
pub(crate) fn env_of(pairs: &[(&str, &str)]) -> impl Fn(&str) -> Option<String> {
    let owned: Vec<(String, String)> = pairs
        .iter()
        .map(|(k, v)| ((*k).to_owned(), (*v).to_owned()))
        .collect();
    move |k: &str| owned.iter().find(|(n, _)| n == k).map(|(_, v)| v.clone())
}

#[test]
fn the_binary_s_three_verbs_are_dispatched() {
    let dir = repo("dispatch");
    let root = root_of(&dir);
    assert!(crate::cli("tick", &[], &root)
        .stderr
        .starts_with("usage: tick-task.py"));
    assert!(crate::cli("task-start", &[], &root)
        .stderr
        .starts_with("usage: task_start.py"));
    assert!(crate::cli("phase-read", &[], &root)
        .stderr
        .starts_with("usage: phase_sources.py"));
}

#[test]
fn the_crate_s_helpers_read_as_python_reads() {
    let dir = scratch("task-helpers");
    put(&dir, "a.txt", "one\r\ntwo\rthree\n");
    assert_eq!(
        crate::read_strict(&dir.join("a.txt")).unwrap(),
        "one\ntwo\nthree\n"
    );
    std::fs::write(dir.join("b.txt"), [0xff]).unwrap();
    assert!(crate::read_strict(&dir.join("b.txt"))
        .unwrap_err()
        .starts_with("UnicodeDecodeError"));
    assert!(crate::read_strict(&dir.join("none")).is_err());
    // outside a repository: no common directory, and the top level is `.`
    assert_eq!(crate::common_text(&dir), "");
    assert_eq!(crate::toplevel_or_dot(&dir), PathBuf::from("."));
    assert_eq!(
        crate::git(Path::new("/nonexistent-dir"), &["status"]).0,
        Some(128)
    );
    assert_eq!(crate::utc_text(0), "1970-01-01T00:00:00Z");
    assert!(crate::now_secs() > 0);
    assert!(crate::write_file(&dir.join("no/such/dir/x"), b"x").is_err());
    assert!(crate::write_file(&dir.join("x"), b"x").is_ok());
    let r = crate::raised("tick", "out\n".to_owned(), "err\n", "why");
    assert_eq!((r.code, r.stdout.as_str()), (1, "out\n"));
    assert_eq!(
        r.stderr,
        "err\nTraceback (most recent call last):\n  l7r-gate tick\nwhy\n"
    );
}
