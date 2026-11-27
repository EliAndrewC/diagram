//! `make queue`, `make queue-add` and `make builder-next` on a real repository and its pool (feature 451 T313, T395, T297): the
//! queue listed with each state computed, an entry appended or refused, the next entry named with what it passed over and why.

use std::path::{Path, PathBuf};

use l7r_gate_core::ci::fixtures::put;
use l7r_gate_core::Reply;

use super::run;
use crate::builder_tree::tests::{env, words, world};
use crate::builder_tree::{self, Env};

const QUEUE: &str = "# the order\nT01 fix crates=rust/guard files=-\nT02 fix files=rust/guard/src/lib.rs\nT03 fix files=docs/a.md waits=T05\nT05 measurement measures=2 files=- waits=GM\nT08 fix files=docs/b.md\n";

fn ask(verb: &str, args: &[&str], root: &Path) -> Reply {
    run(verb, &words(args), root, "", 3)
}

/// The fixture's clone with [`QUEUE`], T08 ticked, and T01 holding a pool tree.
fn queued(tag: &str) -> (l7r_shared::tempdir::TempDir, PathBuf, Env, PathBuf) {
    let (dir, root) = world(tag);
    put(&root, "specs/9001-x/queue.txt", QUEUE);
    let tasks = std::fs::read_to_string(root.join("specs/9001-x/tasks.md")).unwrap();
    put(
        &root,
        "specs/9001-x/tasks.md",
        &format!("{tasks}- [ ] T05 open\n- [x] T08 landed\n"),
    );
    let mut e = env(&dir);
    e.prewarm = false;
    let took = builder_tree::run(&words(&["take", "T01", "9001"]), &root, &e);
    let tree = PathBuf::from(took.stdout.trim());
    assert!(tree.is_dir());
    (dir, root, e, tree)
}

#[test]
fn the_queue_is_listed_with_each_state_computed() {
    let (_dir, root, _e, tree) = queued("queue-list");
    let said = ask("queue", &["9001"], &root);
    assert_eq!(said.code, 0);
    let want = format!(
        "queue: specs/9001-x/queue.txt - 5 entries: 1 landed, 0 built, 1 in flight, 2 waiting, 1 READY\n  line   2  T01            fix           in flight ({})\n  line   3  T02            fix           READY\n  line   4  T03            fix           waiting on T05\n  line   5  T05            measurement   waiting on the GM\n  line   6  T08            fix           landed\n",
        tree.display()
    );
    assert_eq!(said.stdout, want);
    // no feature named: every queue of the clone, from a pool tree too
    assert_eq!(ask("queue", &[], &tree).stdout, want);
    assert_eq!(ask("queue", &[""], &root).stdout, want);
    // an entry whose make builder-done commit is on the pool's log reads built, its landing owed
    let log = root.join(".git").join(l7r_shared::builder_queue::LOG);
    let mut lines = std::fs::read_to_string(&log).unwrap();
    lines.push_str("{\"event\":\"done\",\"detail\":\"9001 T02\"}\n");
    std::fs::write(&log, lines).unwrap();
    let said = ask("queue", &["9001"], &root).stdout;
    assert!(said.contains("1 landed, 1 built, 1 in flight, 2 waiting, 0 READY\n"));
    assert!(said
        .contains("  line   3  T02            fix           built (carried, its landing owed)\n"));
}

#[test]
fn the_next_entry_is_named_with_its_command_and_what_it_passed_over() {
    let (_dir, root, e, _tree) = queued("queue-next");
    // T02 overlaps T01 in flight; nothing else is ready
    let said = ask("builder-next", &["9001"], &root);
    assert_eq!(said.code, 0);
    assert_eq!(
        said.stdout,
        "builder-next: no entry of specs/9001-x/queue.txt to hand out - every READY entry is held back by a task in flight\n  passed over: T02 (line 3) - it overlaps T01 in flight at rust/guard\n  (two entries overlap where a crate or path of one is the other's, or lies under it by whole path components)\nbuilder-next: 1 of 3 builders in flight (L7R_BUILDERS), 0 pool tree(s) free\n"
    );
    // T01's tree released, a tree held for a task the queue does not list: T01 is next, the other tree named
    builder_tree::run(&words(&["release", "T01", "9001"]), &root, &e);
    builder_tree::run(&words(&["take", "T07", "9001"]), &root, &e);
    let said = ask("builder-next", &[], &root);
    assert_eq!(
        said.stdout,
        "builder-next: 9001 T01 (line 2 of specs/9001-x/queue.txt), the next READY entry that overlaps no task in flight, performance work first (FR-013):\n  make builder-brief T=T01 F=9001 KIND=fix CRATE=\"rust/guard\" ENTRY=1\n  not checked: 9001 T07 holds a tree and the queue lists no entry in flight for it - its files are unknown\nbuilder-next: 1 of 3 builders in flight (L7R_BUILDERS), 0 pool tree(s) free\n"
    );
    // the count reached is said
    let full = run("builder-next", &words(&["9001"]), &root, "", 1);
    assert!(full.stdout.ends_with(
        "builder-next: 1 of 1 builders in flight (L7R_BUILDERS), 0 pool tree(s) free\n"
    ));
}

#[test]
fn a_queue_that_is_missing_or_malformed_is_an_error_naming_the_line() {
    let (_dir, root) = world("queue-bad");
    for verb in ["queue", "builder-next"] {
        // no queue in the clone, none in the feature named, no such feature
        let none = ask(verb, &[], &root);
        assert_eq!(none.code, 2);
        assert!(none.stderr.contains("no specs/*/queue.txt in"));
        assert!(none.stderr.contains("make queue-add T=<task(s)> KIND="));
        let missing = ask(verb, &["9001"], &root);
        assert_eq!(missing.code, 2);
        assert!(missing.stderr.contains("specs/9001-x/queue.txt: "));
        let nowhere = ask(verb, &["77"], &root);
        assert!(nowhere.stderr.contains("no specs/77-* directory"));
    }
    put(
        &root,
        "specs/9001-x/queue.txt",
        "T01 fix files=-\nT02 mend files=-\nT03 fix\n",
    );
    let bad = ask("queue", &["9001"], &root);
    assert_eq!((bad.code, bad.stdout.as_str()), (2, ""));
    assert_eq!(
        bad.stderr.lines().next().unwrap(),
        "queue: specs/9001-x/queue.txt line 2: `mend` is no kind (fix, measurement, build-half, closing-half): T02 mend files=-"
    );
    assert!(bad
        .stderr
        .contains("specs/9001-x/queue.txt line 3: 2 field(s) found, at least 3 expected"));
    // outside a repository
    let out = l7r_shared::tempdir::TempDir::new("task-queue-nowhere");
    assert_eq!(
        ask("queue", &[], &out).stderr,
        "queue: not in a git repository\n"
    );
}

#[test]
fn an_entry_is_appended_as_one_line_or_refused() {
    let (dir, root) = world("queue-add");
    // the first entry starts the file under its header
    let args = [
        "T01,T02",
        "9001",
        "build-half",
        "2",
        "",
        "rust/gate/crates/task rust/guard/",
        "Makefile, docs/guards.md",
        "T03 GM alone",
        "",
    ];
    let said = run(
        "queue-add",
        &words(&args),
        &root,
        " the pool\n kept full ",
        3,
    );
    assert_eq!(said.code, 0);
    let line = "T01,T02 build-half jobs=2 crates=rust/gate/crates/task,rust/guard files=Makefile,docs/guards.md waits=T03,GM,alone note=the pool kept full";
    let text = std::fs::read_to_string(root.join("specs/9001-x/queue.txt")).unwrap();
    assert!(text.starts_with("# The builders' queue"));
    assert_eq!(text.lines().count(), 6);
    assert_eq!(text.lines().last().unwrap(), line);
    assert_eq!(
        said.stdout,
        format!("queue-add: specs/9001-x/queue.txt line 6: {line}\n")
    );
    // the second after it, a file left without its last newline healed
    put(&root, "specs/9001-x/queue.txt", text.trim_end());
    let said = run(
        "queue-add",
        &words(&[
            "T03",
            "specs/9001-x",
            "measurement",
            "",
            "3",
            "",
            "",
            "",
            "1",
        ]),
        &root,
        "",
        3,
    );
    assert_eq!(said.stdout, "queue-add: specs/9001-x/queue.txt line 7: T03 measurement measures=3 load=1 crates=- files=-\n");
    let listed = ask("queue", &["9001"], &root);
    assert!(listed
        .stdout
        .starts_with("queue: specs/9001-x/queue.txt - 2 entries: "));
    // refused, the file untouched: a malformed field, no task, a task with no box, no feature
    let before = std::fs::read_to_string(root.join("specs/9001-x/queue.txt")).unwrap();
    let bad = [
        (vec!["T01", "9001", "mend"], "`mend` is no kind"),
        (vec!["T01", "9001", "fix", "9"], "`jobs=9` is no field"),
        (vec!["", "9001", "fix"], "usage: make queue-add"),
        (vec!["#T01", "9001", "fix"], "usage: make queue-add"),
        (
            vec!["T01,T777", "9001", "fix"],
            "T777 has no box in specs/9001-x/tasks.md",
        ),
        (vec!["T01", "77", "fix"], "no specs/77-* directory"),
        (vec!["T01", "", "fix"], "F=<feature> (or SPECIFY_FEATURE)"),
    ];
    for (args, why) in bad {
        let said = ask("queue-add", &args, &root);
        assert_eq!(said.code, 2);
        let refused = said.stderr.starts_with("queue-add: refused - ") && said.stderr.contains(why);
        assert!(refused, "{}", said.stderr);
    }
    assert_eq!(
        std::fs::read_to_string(root.join("specs/9001-x/queue.txt")).unwrap(),
        before
    );
    // from a pool tree: the queue is the clone's
    let mut e = env(&dir);
    e.prewarm = false;
    let took = builder_tree::run(&words(&["take", "T01", "9001"]), &root, &e);
    let from_tree = ask(
        "queue-add",
        &["T01", "9001", "fix"],
        Path::new(took.stdout.trim()),
    );
    assert_eq!(from_tree.code, 2);
    assert!(from_tree
        .stderr
        .starts_with("queue-add: refused - run it in the clone, "));
    // a file that cannot be written
    std::fs::remove_file(root.join("specs/9001-x/queue.txt")).unwrap();
    std::fs::create_dir(root.join("specs/9001-x/queue.txt")).unwrap();
    let said = ask("queue-add", &["T01", "9001", "fix"], &root);
    assert_eq!(said.code, 1);
    assert!(said
        .stderr
        .starts_with("queue-add: specs/9001-x/queue.txt: "));
}

/// The started feature 9001 with an open `[perf]` task T06 on top of [`queued`]'s fixture.
fn with_perf(tag: &str, queue: &str) -> (l7r_shared::tempdir::TempDir, PathBuf, Env) {
    let (dir, root, e, _tree) = queued(tag);
    let tasks = std::fs::read_to_string(root.join("specs/9001-x/tasks.md")).unwrap();
    put(
        &root,
        "specs/9001-x/tasks.md",
        &format!("{tasks}- [ ] T06 [perf] the faster gate\n"),
    );
    put(&root, "specs/9001-x/queue.txt", queue);
    put(
        &root,
        ".git/task-starts.jsonl",
        "{\"feature\": \"9001-x\", \"task\": \"T02\", \"utc\": \"2026-11-27T01:00:00Z\"}\n",
    );
    (dir, root, e)
}

/// A printed `make <verb> K=V ...` command's values by name, as make would hand them over.
fn values(command: &str) -> std::collections::BTreeMap<String, String> {
    command
        .split_whitespace()
        .filter_map(|w| w.split_once('='))
        .map(|(k, v)| (k.to_owned(), v.trim_matches('"').to_owned()))
        .collect()
}

/// 451 T313's round-3 ruling (T421): `make builder-next` and `make queue` name an open performance task no queue line names FIRST,
/// with the `make queue-add` command that writes its line; that command, run as printed, writes a line that quiets it.
#[test]
fn an_open_performance_task_with_no_line_is_named_first_and_its_command_runs_as_printed() {
    let (_dir, root, _e) = with_perf("queue-unlisted", QUEUE);
    let block = "FIRST, open performance work (FR-013) no queue line names - write each one's line (CRATE= and FILES= as its task line names them, WAITS= where it waits, which quiets it):\n  make queue-add F=9001 T=T06 KIND=fix   (9001 T06, KIND by make builder-brief's mechanism test)\n";
    let next = ask("builder-next", &["9001"], &root).stdout;
    let first = next.starts_with(&format!("{block}builder-next: "));
    assert!(first, "{next}");
    let listed = ask("queue", &["9001"], &root).stdout;
    assert!(listed.ends_with(block), "{listed}");
    // the command as printed
    let command = block
        .lines()
        .nth(1)
        .unwrap()
        .trim()
        .split("   (")
        .next()
        .unwrap();
    let v = values(command);
    let args = [v["T"].as_str(), v["F"].as_str(), v["KIND"].as_str()];
    let added = ask("queue-add", &args, &root);
    assert_eq!(added.code, 0, "{}", added.stderr);
    assert!(!ask("builder-next", &["9001"], &root)
        .stdout
        .contains("FIRST"));
    assert!(!ask("queue", &[], &root).stdout.contains("FIRST"));
}

/// The reviewer's "not assumed" point (451 T313's round 3): the `make builder-brief` command the queue names for a performance entry,
/// run as named, takes its tree, and that task's `make task-start` meets no FR-013 refusal - builder-brief itself runs no task-start
/// (neither it nor builder-tree calls it), and the refusal passes any task FR-013's own test calls performance work. The converse: a
/// non-performance task started while one is open is refused, `PERF_LATER_OK` its route.
#[test]
fn the_named_brief_for_performance_work_meets_no_performance_first_refusal() {
    let (dir, root, mut e) = with_perf(
        "queue-perf-start",
        "T02 fix files=docs/a.md\nT06 fix files=docs/b.md\n",
    );
    e.prewarm = false;
    let next = ask("builder-next", &["9001"], &root).stdout;
    let command = next
        .lines()
        .find(|l| l.trim_start().starts_with("make builder-brief"))
        .unwrap()
        .trim();
    assert_eq!(command, "make builder-brief T=T06 F=9001 KIND=fix ENTRY=1");
    let over =
        "passed over: T02 (line 1) - T06 (line 2) is performance work, offered first (FR-013)";
    assert!(next.contains(over), "{next}");
    let v = values(command);
    let args = words(&[
        &v["T"],
        &v["F"],
        &v["KIND"],
        "",
        "",
        "",
        "",
        "",
        &v["ENTRY"],
    ]);
    let brief = crate::builder_brief::run(&args, &root, &e, "");
    assert_eq!(brief.code, 0, "{}", brief.stderr);
    assert!(brief
        .stdout
        .starts_with("BUILDER-BRIEF 9001 T06 KIND=fix JOBS=1 TREE="));
    let tree = root.to_string_lossy().into_owned();
    let env = crate::tests::env_of(&[("L7R_GATE_TREE", &tree)]);
    let started = crate::task_start::cli_with(&words(&["9001", "T06"]), &root, &env);
    assert_eq!(started.code, 0, "{}", started.stderr);
    let other = crate::task_start::cli_with(&words(&["9001", "T02"]), &root, &env);
    assert_eq!(other.code, 2);
    assert!(
        other
            .stderr
            .contains("is not performance work, and 9001-x T06 is"),
        "{}",
        other.stderr
    );
    let later = crate::tests::env_of(&[
        ("L7R_GATE_TREE", &tree),
        ("PERF_LATER_OK", "T06 waits on a landing, a queue test"),
    ]);
    assert_eq!(
        crate::task_start::cli_with(&words(&["9001", "T02"]), &root, &later).code,
        0
    );
    drop(dir);
}
