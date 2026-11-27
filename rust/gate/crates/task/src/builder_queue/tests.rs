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

/// 451 T408: a tree handed out by hand - `make builder-tree`, or `make builder-brief T=<a task picked by hand>` through it -
/// names on stderr each task in flight its queue entry overlaps, a notice and never a refusal; nothing where it overlaps none or
/// the task has no entry.
#[test]
fn a_handout_by_hand_names_the_tasks_in_flight_its_entry_overlaps() {
    let (dir, root, mut e, held) = queued("queue-take-overlap");
    e.cap = 4;
    // another feature's file of that name in another form is passed, as `make builder-done`'s step 1 passes it
    put(&root, "specs/9002-y/queue.txt", "not a queue line\n");
    let took = builder_tree::run(&words(&["take", "T02", "9001"]), &root, &e);
    assert_eq!(took.code, 0, "{}", took.stderr);
    let notice = format!("builder-tree: NOTICE - 9001 T02's queue entry (line 3 of specs/9001-x/queue.txt) overlaps 9001 T01 in flight at rust/guard ({}): the second of the two to land meets the first's edits; make builder-next names an entry that overlaps nothing in flight\n", held.display());
    assert!(took.stderr.contains(&notice), "{}", took.stderr);
    assert_eq!(took.stderr.matches("NOTICE").count(), 1);
    // its own entry, in flight in the tree just taken, is not named against itself; asked again, the notice again
    let again = builder_tree::run(&words(&["take", "T02", "9001"]), &root, &e);
    assert!(again.stderr.contains(&notice), "{}", again.stderr);
    // no overlap, a landed entry, no entry, a feature with no queue: nothing
    for (task, feature) in [
        ("T03", "9001"),
        ("T08", "9001"),
        ("T09", "9001"),
        ("T01", "77"),
    ] {
        let quiet = builder_tree::run(&words(&["take", task, feature]), &root, &e);
        assert!(!quiet.stderr.contains("NOTICE"), "{task}: {}", quiet.stderr);
        builder_tree::run(&words(&["release", task, feature]), &root, &e);
    }
    drop(dir);
}

/// The fixture's clone with a queue whose fix entries' task lines name a new mechanism (451 T412): T10 by a phrase, T12 by a
/// `make -C` the mechanism test misreads (451 T431's half), T11 typed a measurement, T02 named by no line, and a bundle behind T10.
fn mechanisms(tag: &str) -> (l7r_shared::tempdir::TempDir, PathBuf) {
    let (dir, root) = world(tag);
    let tasks = std::fs::read_to_string(root.join("specs/9001-x/tasks.md")).unwrap();
    put(
        &root,
        "specs/9001-x/tasks.md",
        &format!("{tasks}- [ ] T10 a new guard on rm\n- [ ] T11 a new command, measured first\n- [ ] T12 the lint: make -C rust lint\n"),
    );
    put(
        &root,
        "specs/9001-x/queue.txt",
        "T02 fix files=docs/e.md\nT10 fix files=docs/c.md\nT11 measurement measures=1 files=-\nT02,T10 fix files=docs/f.md\nT12 fix files=docs/d.md\nT09 fix files=-\n",
    );
    (dir, root)
}

const FLAG10: &str = "FLAG: T10 (line 2) is typed fix, but T10's line names a new mechanism (\"a new guard\"), which make builder-brief refuses KIND=fix for: retype the line build-half and add its closing-half line after it, then";
const HALF10: &str = "make builder-brief T=T10 F=9001 KIND=build-half ENTRY=1";
const MISREAD: &str = "or, where the test misreads the line (a quoted refusal phrase, `make -C`), the fix command as printed with SIZING_OK=\"<reason>\"";

/// 451 T412: `make queue` and `make builder-next` flag a fix entry `make builder-brief` would refuse, by the brief's own mechanism
/// test, naming what it read, the build-half command and the escape a misread line takes; the entry stays READY and is still named.
#[test]
fn a_fix_entry_whose_task_line_names_a_mechanism_is_flagged_with_the_build_half_command() {
    let (dir, root) = mechanisms("queue-flag");
    let listed = ask("queue", &["9001"], &root);
    assert_eq!(listed.code, 0);
    let pad = "              ";
    let want = format!("  line   2  T10            fix           READY\n{pad}{FLAG10}\n{pad}  {HALF10}\n{pad}  {MISREAD}\n  line   3  T11");
    assert!(listed.stdout.contains(&want), "{}", listed.stdout);
    // the bundle behind T10, waiting, flagged; `make -C rust lint` no longer misread since 451 T431 reads past make's flags, so T12 is
    // not, nor the plain fix, the measurement and the landed T09
    assert!(listed
        .stdout
        .contains("FLAG: T02,T10 (line 4) is typed fix, but T10's line names"));
    assert!(!listed.stdout.contains("FLAG: T12"));
    assert_eq!(listed.stdout.matches("FLAG: ").count(), 2);
    // builder-next names T02 first, unflagged; with T02 landed, T10 with its flag under its command
    let first = ask("builder-next", &["9001"], &root).stdout;
    assert!(first.contains("KIND=fix ENTRY=1\n") && !first.contains("FLAG"));
    let tasks = std::fs::read_to_string(root.join("specs/9001-x/tasks.md")).unwrap();
    put(
        &root,
        "specs/9001-x/tasks.md",
        &tasks.replace("- [ ] T02 ", "- [x] T02 "),
    );
    let next = ask("builder-next", &["9001"], &root).stdout;
    let want = format!("  make builder-brief T=T10 F=9001 KIND=fix ENTRY=1\n  {FLAG10}\n    {HALF10}\n    {MISREAD}\n");
    assert!(next.contains(&want), "{next}");
    // the flag is the brief's refusal: the fix command printed is refused for the mechanism, the build-half command taken
    let mut e = env(&dir);
    e.prewarm = false;
    let brief = |kind: &str, ok: &str| {
        let args = words(&["T10", "9001", kind, "", "", "", "", "", "1"]);
        crate::builder_brief::run(&args, &root, &e, ok)
    };
    let fix = brief("fix", "");
    assert_eq!(fix.code, 2);
    let refusal = "T10's line names a new mechanism (\"a new guard\")";
    assert!(fix.stderr.contains(refusal), "{}", fix.stderr);
    assert_eq!(brief("build-half", "").code, 0);
    drop(dir);
}

/// 451 T412: `make queue-add` says the same flag when the entry it writes is a fix its brief would refuse, and writes it.
#[test]
fn queue_add_flags_a_fix_entry_whose_task_line_names_a_mechanism() {
    let (_dir, root) = mechanisms("queue-add-flag");
    let said = ask(
        "queue-add",
        &["T10", "9001", "fix", "", "", "", "docs/g.md"],
        &root,
    );
    assert_eq!(said.code, 0);
    let want = "queue-add: specs/9001-x/queue.txt line 7: T10 fix crates=- files=docs/g.md\n  FLAG: T10 (line 7) is typed fix, but T10's line names a new mechanism (\"a new guard\"), which make builder-brief refuses KIND=fix for: retype the line build-half and add its closing-half line after it, then\n    make builder-brief T=T10 F=9001 KIND=build-half ENTRY=3\n";
    assert!(said.stdout.starts_with(want), "{}", said.stdout);
    let plain = ask(
        "queue-add",
        &["T02", "9001", "fix", "", "", "", "docs/h.md"],
        &root,
    );
    assert!(!plain.stdout.contains("FLAG"), "{}", plain.stdout);
}

/// 451 T418: with no feature named, `make queue` and `make builder-next` pass over another feature's `queue.txt` of another form
/// (a page session's, features 269 and 280), saying so once on stderr, and list the builders' queues; named, it is still an error,
/// and where no queue parses the first one's error stands.
#[test]
fn with_no_feature_named_a_queue_of_another_form_is_passed_over_once() {
    let (_dir, root, _e, _tree) = queued("queue-foreign");
    put(
        &root,
        "specs/269-research-backfill/queue.txt",
        "/c/briefs/h1-write.md then:/c/briefs/h1-checks.sh /c/briefs/v1-write.md then:/c/briefs/v1-checks.sh\n/c/x.md then:/c/y.sh\n",
    );
    let passed = "passed over specs/269-research-backfill/queue.txt: it does not parse as a builders' queue (2 line(s) refused; make queue F=269 names each)\n";
    for verb in ["queue", "builder-next"] {
        let said = ask(verb, &[], &root);
        assert_eq!(said.code, 0, "{}", said.stderr);
        assert_eq!(said.stderr, format!("{verb}: {passed}"));
        assert!(said.stdout.contains("specs/9001-x/queue.txt"));
        let named = ask(verb, &["269"], &root);
        assert_eq!(named.code, 2);
        assert!(named
            .stderr
            .contains("specs/269-research-backfill/queue.txt line 1: "));
    }
    std::fs::remove_file(root.join("specs/9001-x/queue.txt")).unwrap();
    let none = ask("queue", &[], &root);
    assert_eq!(none.code, 2);
    let first = "queue: specs/269-research-backfill/queue.txt line 1: ";
    assert!(none.stderr.starts_with(first), "{}", none.stderr);
}

/// The lane's repair entries for 9001: r1 (T02, READY), r2 (T01, in flight in [`queued`]'s tree), r3 (`integrate`) and r4 (T05,
/// READY after r1), each ejected.
fn repaired(root: &Path) {
    let entry = |id: &str, task: &str, kind: &str| {
        format!("{{\"repair\": \"{id}\", \"feature\": \"9001-x\", \"tasks\": [\"{task}\"], \"kind\": \"{kind}\", \"batch\": \"9001-1\", \"why\": \"red\", \"units\": [], \"attempt\": \"/a-{id}.log\"}}\n")
    };
    let eject = |id: &str| {
        format!("{{\"utc\": \"2026-11-26T12:00:00Z\", \"event\": \"eject\", \"change\": \"c-{id}\", \"repair\": \"{id}\"}}\n")
    };
    let all = ["r1", "r2", "r3", "r4"];
    put(
        root,
        ".git/l7r-lane/repairs.jsonl",
        &(entry("r1", "T02", "fix")
            + &entry("r2", "T01", "fix")
            + &entry("r3", "T03", "integrate")
            + &entry("r4", "T05", "fix")),
    );
    put(root, ".git/l7r-lane/lane.jsonl", &all.map(eject).concat());
}

/// 461 T16 (D7): `make builder-next`, `make queue` and `make builder-done`'s step 1 name the lane's open repair entry before the
/// queue's READY one (`LANE_REPAIR_FIRST`), each other open entry READY after it or passed over with why; with the knob at 0 after
/// the queues; and with no queue to read, alone.
#[test]
fn an_open_repair_entry_is_named_before_the_queue_s_next_entry() {
    let (_dir, root, _e, tree) = queued("queue-repair");
    repaired(&root);
    let one = "T03 fix files=docs/a.md\n";
    put(&root, "specs/9001-x/queue.txt", one);
    let r1 = "make builder-brief T=T02 F=9001 KIND=fix REPAIR=r1   (9001 T02 (repair r1): the lane ejected c-r1 from batch 9001-1 (red); the gate's output /a-r1.log - a FRESH builder, never one kept past its report)";
    let rest = format!("  repair READY after it: make builder-brief T=T05 F=9001 KIND=fix REPAIR=r4   (9001 T05 (repair r4))\n  repair passed over: 9001 T01 (repair r2) - in flight (9001 T01 holds {})\n  repair passed over: 9001 T03 (repair r3) - kind integrate is no kind make builder-brief takes yet: brief its builder by hand\n", tree.display());
    let next = ask("builder-next", &["9001"], &root).stdout;
    assert!(next.starts_with(&format!("builder-next: the lane's open repair entry:\n  {r1}\n{rest}builder-next: 9001 T03 (line 1")), "{next}");
    let listed = ask("queue", &["9001"], &root).stdout;
    assert!(
        listed.starts_with(&format!(
            "queue: the lane's open repair, READY:\n  {r1}\n{rest}queue: specs/9001-x/queue.txt"
        )),
        "{listed}"
    );
    // the knob at 0: after the queue's
    let late = super::run_with("builder-next", &words(&["9001"]), &root, "", 3, false).stdout;
    let said = format!("\nbuilder-next: the lane's open repair entry:\n  {r1}\n");
    assert!(late.starts_with("builder-next: 9001 T03 (line 1"), "{late}");
    assert!(late.contains(&said), "{late}");
    // no queue to read: the repairs alone, the queue's error on stderr
    std::fs::remove_file(root.join("specs/9001-x/queue.txt")).unwrap();
    let alone = ask("builder-next", &["9001"], &root);
    assert_eq!(alone.code, 0);
    assert!(
        alone
            .stdout
            .starts_with("builder-next: the lane's open repair entry:\n"),
        "{}",
        alone.stdout
    );
    assert!(
        alone.stderr.starts_with("builder-next: "),
        "{}",
        alone.stderr
    );
    // builder-done's step 1, both ways: first; with the knob at 0 and no queue, the repair still
    let p = crate::builder_tree::pool(&root).unwrap();
    let rest = rest.replace("  repair", "     repair");
    let step = super::dispatch(&p, "9001");
    assert!(step.starts_with(&format!("{r1}\n{rest}")), "{step}");
    let after = super::dispatch_with(&p, "9001", false);
    let tail = format!("{r1}\n{rest}");
    assert!(after.ends_with(&tail), "{after}");
    assert!(after.starts_with("no next dispatch named: "), "{after}");
    // with a queue and the knob at 0: the queue's entry, and no repair named
    put(&root, "specs/9001-x/queue.txt", one);
    let queued = super::dispatch_with(&p, "9001", false);
    let wanted = "make builder-brief T=T03 F=9001 KIND=fix ENTRY=1";
    assert!(queued.starts_with(wanted), "{queued}");
    assert!(!queued.contains("REPAIR"), "{queued}");
    // every open entry answered: nothing of the lane said
    let answered = ["r1", "r2", "r3", "r4"]
        .map(|r| format!("{{\"event\":\"done\",\"detail\":\"9001 T09\",\"repair_of\":\"{r}\"}}\n"))
        .concat();
    let log = root.join(".git").join(l7r_shared::builder_queue::LOG);
    let had = std::fs::read_to_string(&log).unwrap();
    std::fs::write(&log, had + &answered).unwrap();
    assert!(!ask("builder-next", &["9001"], &root)
        .stdout
        .contains("repair"));
}
