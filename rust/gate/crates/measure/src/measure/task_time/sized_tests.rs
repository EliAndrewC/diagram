//! Feature 451 T512: a landed task's size, counts, turns and tokens beside its minutes, each with its share - the subject forms, the
//! line classes, and the command over a fixture task with a test-and-source diff, a bundle, a tick and two test runs.

use std::fmt::Write as _;
use std::path::Path;

use serde_json::json;

use super::super::events::ts;
use super::super::feature_report::tests::{git, put};
use super::beside::{group, GROUPS};
use super::sized::{class_of, inline_tests, named, parse, renamed_to, Class};
use super::tests::{args, world};
use super::*;

#[test]
fn a_subject_names_its_tasks_in_the_builders_and_the_repairs_forms() {
    let one = |n: &str, ts: &[&str]| {
        Some((
            n.to_owned(),
            ts.iter().map(|t| (*t).to_owned()).collect::<Vec<_>>(),
        ))
    };
    assert_eq!(named("451 T510: make task-time ..."), one("451", &["T510"]));
    assert_eq!(
        named("451 T470 T363: a slow test"),
        one("451", &["T470", "T363"])
    );
    assert_eq!(
        named("451 T363's coverage repair before its gate"),
        one("451", &["T363"])
    );
    assert_eq!(
        named("451: T490's coverage repair before its gate"),
        one("451", &["T490"])
    );
    assert_eq!(
        named("451: T492's and T495's coverage repair"),
        one("451", &["T492", "T495"])
    );
    let and = one("451", &["T143", "T342"]);
    assert_eq!(named("451 T143 and T342's close"), and);
    assert_eq!(
        named("451 T313 (with T395 built here): x"),
        one("451", &["T313"])
    );
    assert_eq!(named("451 T397 part (c): x"), one("451", &["T397"]));
    assert_eq!(named("451 T1, T2: x"), one("451", &["T1", "T2"]));
    for none in [
        "451-time-retro-and-efficiency: T507 T508 ticked (make land)",
        "451: the plan review's verdict on T490's removed stub block",
        "451: T490's removed stub",
        "451: T490's and the rest",
        "the gate's run record (green)",
        "451 the GM's words",
        "x1 T1: no number",
        ": empty",
        "451:",
    ] {
        assert_eq!(named(none), None, "{none}");
    }
}

#[test]
fn a_files_lines_are_test_prose_or_non_test() {
    for (p, want) in [
        ("tests/hooks/x.sh", Class::Test),
        ("rust/a/src/x/tests.rs", Class::Test),
        ("rust/a/src/x/cross_tests.rs", Class::Test),
        ("rust/a/src/x/tests/one.rs", Class::Test),
        ("specs/451-x/plan.md", Class::Prose),
        ("docs/guards.md", Class::Prose),
        ("rust/a/src/x.rs", Class::Code),
        ("rust/a/src/{old => x}/tests.rs", Class::Test),
        ("old.rs => tests/new.rs", Class::Test),
    ] {
        assert_eq!(class_of(p), want, "{p}");
    }
    assert_eq!(renamed_to("a/{b => }/c.rs"), "a/c.rs");
    assert!(inline_tests("fn a() {}\n\n#[cfg(test)]\nmod tests {\n}\n"));
    assert!(inline_tests("#[cfg(test)]\npub(crate) mod t {\n"));
    assert!(inline_tests("#[cfg(test)]\npub mod t {\n"));
    assert!(!inline_tests("#[cfg(test)]\nmod tests;\n"));
    assert!(!inline_tests("#[cfg(test)]\nfn helper() {\n"));
    let c = parse("\u{1e}451 T1: x\n\n3\t1\ta.rs\n-\t-\tpic.png\nnot a row\n\u{1e}\n");
    assert_eq!(c.len(), 1);
    assert_eq!(
        c[0].files,
        vec![("a.rs".to_owned(), 3, 1), ("pic.png".to_owned(), 0, 0)]
    );
}

#[test]
fn every_category_has_its_group() {
    for (cat, want) in [
        (
            "builders: running a command (the model's turn)",
            Some("builder thinking"),
        ),
        ("builders: reading code", Some("code read/write")),
        ("main session: writing code", Some("code read/write")),
        ("shell reads and file edits", Some("code read/write")),
        ("hook suites", Some("tests")),
        ("waiting on a build slot", Some("compile")),
        ("plan review: agents", Some("review")),
        ("arbiter: agents", Some("review")),
        ("main session: writing its reply", Some("session")),
        ("git", Some("other")),
        ("the GM away", None),
        (CARRY, None),
    ] {
        assert_eq!(group(cat), want, "{cat}");
    }
    assert_eq!(GROUPS.len(), 7);
}

/// The turns' edges: an agent with no task is the feature's `-`, a page session's transcript is no main session's, and the session's
/// calls booked to no task carry their tokens; a transcript that is no `.jsonl` is read as nothing.
#[test]
fn an_untasked_agent_a_page_session_and_the_unbooked_calls_tokens() {
    use super::super::where_time::columns::{spent, Agent};
    let tok = |out: f64, cached: f64| spent::Tok {
        cached,
        out,
        ..spent::Tok::default()
    };
    let agents = [Agent {
        aid: "A".to_owned(),
        kind: "general-purpose".to_owned(),
        ..Agent::default()
    }];
    let stream: Vec<Event> = [
        json!({"t": "2026-11-25T10:00:00Z", "aid": "A", "feature": "451-x"}),
        json!({"t": "2026-11-25T10:00:10Z", "sid": "s", "ev": "Stop"}),
    ]
    .iter()
    .map(|v| v.as_object().unwrap().clone())
    .collect();
    let at = ts("2026-11-25T10:00:05Z").unwrap();
    let session = HashMap::from([
        ("s".to_owned(), vec![(at, tok(10.0, 1000.0))]),
        ("p".to_owned(), vec![(at, tok(99.0, 0.0))]),
    ]);
    let read = turns::Read {
        calls: &HashMap::from([("A".to_owned(), 3)]),
        tokens: &HashMap::new(),
        session: &session,
        paged: &std::collections::HashSet::from(["p".to_owned()]),
    };
    let (got, unbooked) = turns::of(&stream, &agents, &read, &HashMap::new());
    assert_eq!(got[&("451-x".to_owned(), "-".to_owned())].builders, 3);
    assert_eq!(unbooked, (1, tok(10.0, 1000.0)));
    let mut t = spent::Tokens::default();
    t.read(
        Path::new("s/subagents/agent-A.meta.json"),
        &usage("m1", "00:01", (1, 0, 0, 0)),
        (0.0, f64::MAX),
    );
    assert!(t.calls().is_empty() && t.session().is_empty());
}

/// One commit in `root`, its files written and added, at a time inside the read-back.
fn commit(root: &Path, subject: &str, files: &[(&str, &str)]) {
    for (p, text) in files {
        put(root, p, text);
        git(root, "2026-11-25T10:03:00Z", &["add", p]);
    }
    git(
        root,
        "2026-11-25T10:03:00Z",
        &["commit", "-q", "-m", subject],
    );
}

/// A usage row of a transcript.
fn usage(id: &str, t: &str, (out, fresh, cached, created): (u64, u64, u64, u64)) -> String {
    format!(
        "{}\n",
        json!({"timestamp": format!("2026-11-25T10:{t}Z"), "message": {"id": id, "usage": {"output_tokens": out, "input_tokens": fresh,
            "cache_read_input_tokens": cached, "cache_creation_input_tokens": created}}})
    )
}

fn append(p: &Path, text: &str) {
    let mut t = std::fs::read_to_string(p).unwrap_or_default();
    t.push_str(text);
    std::fs::write(p, t).unwrap();
}

/// The red-first fixture: 451-x T1 lands with a test-and-source diff, a bundle's commit naming it and T9, a tick commit and another
/// feature's repair of its own T1; its `make static` run holds a build and two test runs; its builder made two calls (one written
/// twice), its plan review one, and the session three - one before its own line, one after the task's own table ended, one after
/// its last line.
#[test]
fn a_landed_task_carries_its_size_counts_turns_and_tokens_with_their_shares() {
    let (d, root) = world();
    let r = Path::new(&root);
    git(r, "2026-11-25T10:03:00Z", &["init", "-q"]);
    commit(
        r,
        "451 T1: a source and its test",
        &[
            ("src/a.rs", "fn a() {}\n#[cfg(test)]\nmod tests {\n}\n\n"),
            ("src/b_tests.rs", "1\n2\n"),
            ("specs/451-x/plan.md", "a\n"),
        ],
    );
    commit(r, "451 T1 T9: a bundle", &[("src/c.rs", "c\n")]);
    commit(
        r,
        "451-x: T1 ticked (make land)",
        &[("specs/451-x/tasks.md", "1\n2\n3\n4\n")],
    );
    commit(
        r,
        "449: T1's coverage repair before its gate",
        &[("tests/x.sh", "1\n2\n")],
    );
    let log = d.join("root/.git/l7r-events/451-x.jsonl");
    let mut text = std::fs::read_to_string(&log).unwrap();
    for (t0, t1) in [("01:05", "01:10"), ("01:15", "01:20")] {
        let _ = writeln!(
            text,
            "{}",
            json!({"t": format!("2026-11-25T10:{t1}Z"), "ev": "Phase", "src": "rust", "step": "test", "t0": format!("2026-11-25T10:{t0}Z"),
                "t1": format!("2026-11-25T10:{t1}Z"), "make": "static", "sid": "s", "task": "T1"})
        );
    }
    std::fs::write(&log, text).unwrap();
    let home = d.join("home/p");
    append(
        &home.join("s/subagents/agent-B.jsonl"),
        &[
            usage("m1", "02:05", (100, 10, 1000, 0)),
            usage("m1", "02:05", (100, 10, 1000, 0)),
            usage("m2", "05:15", (100, 0, 1000, 0)),
        ]
        .concat(),
    );
    std::fs::write(
        home.join("s/subagents/agent-C.jsonl"),
        usage("m3", "04:30", (50, 0, 400, 40)),
    )
    .unwrap();
    append(
        &home.join("s.jsonl"),
        &[
            usage("m4", "00:09", (50, 0, 0, 0)),
            usage("m5", "06:08", (10, 0, 0, 0)),
            usage("m6", "06:49", (10, 0, 0, 0)),
        ]
        .concat(),
    );
    let (projects, clones) = (d.join("home"), d.join("clones"));
    let now = ts("2026-11-25T10:30:00Z").unwrap();
    let got = cli(
        &args(&[
            "--root",
            &root,
            "--since",
            "2026-11-25T10:00:00Z",
            "--until",
            "2026-11-25T10:06:50Z",
        ]),
        &projects,
        &clones,
        now,
    );
    assert_eq!(got.code, 0, "{}", got.stderr);
    let out = got.stdout;
    for want in [
        // 9 changed lines: test 2, non-test 6 (the inline block's among them), prose 1; the tick left out, the bundle shared
        "| 451-x T1 | 2 (shared with T9) | +2 -0 (22.2%) | +6 -0 (66.7%) | +1 -0 (11.1%) | 2 (66.7%) | 1 (33.3%) | 2 | 2 (50.0%) | \
         1 (25.0%) | 1 (25.0%) | 0.3k (10.9%) | 0.0k (0.4%) | 2.4k (87.3%) | 0.0k (1.5%) | 80.4% / 17.8% / 1.8% |",
        // the other feature's T1: its repair only
        "| 449-z T1 | 1 | +2 -0 (100.0%) | +0 -0 (0.0%) | +0 -0 (0.0%) |",
        "The main session's calls booked to no task: 2, their tokens 0.0k (output 0.0k, cache read 0.0k).",
        super::beside::SOURCES,
        "## Each landed task's minutes by group, each its % of the task (451 T512)",
        super::beside::GROUPING,
        "| the window, the tasks' side | ",
        "Beside its minutes (451 T512): `tests` ",
        "in 2 (66.7%) test runs, `compile` ",
        "1 of its non-test `.rs` files holding an inline test block",
        "| make static | tests | 1 | 1.0 | ",
        // the builder's own clock, 10:01:41 to 10:06:00, each second once (451 T512's own path)
        "Its own path (451 T512): 4.3 min.",
        "| task | own-path minutes | builder thinking |",
        super::beside::OWN_PATH,
        super::beside::STOPPED_BESIDE,
        "| task | stopped minutes |",
        "Beside its path, its builders stopped (451 T512): ",
    ] {
        assert!(out.contains(want), "{want}\n---\n{out}");
    }
}

/// A landed task whose builders stopped (451 T512's own table): its own path beside its stopped stretches, each category's minutes
/// largest first, summed - another task's stopped seconds never in its line.
#[test]
fn a_tasks_own_table_lists_its_stopped_stretches_by_what_was_in_flight() {
    let key: Key = ("451-x".to_owned(), "T1".to_owned());
    let other: Key = ("451-x".to_owned(), "T2".to_owned());
    let cell = |k: &Key, cat: &str| (k.clone(), cat.to_owned(), String::new());
    let mut l = Ledger::default();
    l.own.insert(cell(&key, "builders: reading code"), 60.0);
    l.stopped.insert(cell(&key, "tests"), 120.0);
    l.stopped.insert(cell(&key, book::STOPPED), 30.0);
    l.stopped.insert(cell(&other, "tests"), 600.0);
    let mut out = String::new();
    beside::own_table(&mut out, &l, &key);
    assert!(out.contains("Its own path (451 T512): 1.0 min."), "{out}");
    let row = "| builders: reading code | 1.0 | 100.0% |";
    assert!(out.contains(row), "{out}");
    let want = format!(
        "\nBeside its path, its builders stopped (451 T512): 2.5 min - tests 2.0 - {} 0.5.\n\n",
        book::STOPPED
    );
    assert!(out.ends_with(&want), "{out}");
}
