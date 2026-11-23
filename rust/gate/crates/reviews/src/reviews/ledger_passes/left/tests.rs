//! 451 T147's pin: a landing of T1 with T2's open plan review owed refuses nothing for T2, writes T1's own row, and still refuses a
//! ticked task's, a block review's and any other pass.

use serde_json::json;

use super::super::super::tests::put;
use super::super::cli;
use super::super::tests::{args, pass, transcript, world};

const L: [&str; 2] = ["--ledger", "dev/review-ledger.md"];

/// A plan review of `task` by agent `agent`, whose reply quotes no recorded verdict and whose record holds none.
fn review(agent: &str, subject: &str) -> String {
    pass("spec-fidelity", agent, subject, &json!({}))
}

#[test]
fn a_landing_of_t1_leaves_t2_s_open_plan_review_and_writes_its_own() {
    let log = [
        review(
            "p1",
            "MODE 4: PLAN REVIEW of one task's section - feature 449-x, task T1 (a decision",
        ),
        review(
            "p2",
            "MODE 4: PLAN REVIEW of one task's section - feature 449-x, task T2 (a decision",
        ),
        review(
            "p3",
            "MODE 4: PLAN REVIEW of one task's section - feature 451-y, task T9 (a decision",
        ),
    ];
    let (d, env) = world("left", &log);
    put(
        &env.cwd,
        "specs/449-x/tasks.md",
        "- [ ] T1 one\n- [ ] T2 two\n",
    );
    put(&env.cwd, "specs/451-y/tasks.md", "- [ ] T9 nine\n");
    let sub = d.join("home/.claude/projects/p/s/subagents");
    for a in ["p1", "p2", "p3"] {
        put(
            &sub,
            &format!("agent-{a}.jsonl"),
            &transcript(&json!("MODE 4: PLAN REVIEW"), "CLEAR"),
        );
    }
    let landing = [&L[..], &["--refuse", "--landing", "449-x", "--tasks", "T1"]].concat();
    // before the landing's writes: T1's own pass refuses; T2's and 451's T9 are their own landings'
    let before = cli(&args(&landing), &env);
    let owed_t1 = before.stderr.contains("feature 449-x, task T1");
    let owed_t2 = before.stderr.contains("task T2") || before.stderr.contains("task T9");
    assert_eq!((before.code, owed_t1, owed_t2), (1, true, false));
    assert!(before.stdout.contains("2 open task(s) left to their own landings and sessions (451 T147, T157), which write their rows: 449-x T2, 451-y T9"));
    // the landing's own write (a 449 landing's, as `write_ledger` runs it), then its check: nothing refused, T1's row written
    let wrote = cli(
        &args(&[&L[..], &["--write", "specs/449-x/ (make land)"]].concat()),
        &env,
    );
    assert_eq!(wrote.code, 0);
    let after = cli(&args(&landing), &env);
    assert_eq!((after.code, after.stderr.as_str()), (0, ""));
    let rows = std::fs::read_to_string(env.cwd.join("dev/review-ledger.md")).unwrap();
    let own_row = rows
        .lines()
        .filter(|r| {
            r.contains("feature 449-x, task T1 (")
                && r.contains("applied or filed as specs/449-x/ (make land) records")
        })
        .count();
    assert_eq!(own_row, 1);
    // another feature's landing (451, landing T8) leaves 449's open T1 and T2 too, though its write traces neither
    let other = cli(
        &args(&[&L[..], &["--refuse", "--landing", "451-y", "--tasks", "T8"]].concat()),
        &env,
    );
    assert_eq!(other.code, 0);
}

#[test]
fn a_ticked_task_s_a_block_review_s_and_any_other_pass_still_refuse() {
    let log = [
        review(
            "q1",
            "MODE 4: PLAN REVIEW of one task's section - feature 449-x, task T3 (a decision",
        ),
        review(
            "q2",
            "MODE 4: PLAN REVIEW of one task's section - feature 449-x, task T4 (a decision",
        ),
        review(
            "q3",
            "MODE 4: PLAN REVIEW of feature 449-x's changed blocks",
        ),
        review(
            "q4",
            "MODE 4: PLAN REVIEW of one task's section - feature 452-gone, task T1 (a decision",
        ),
        pass(
            "impl-drift",
            "q5",
            "DECIDE_OK=\"a claims check\"",
            &json!({}),
        ),
    ];
    let (_d, env) = world("left-refused", &log);
    put(&env.cwd, "specs/449-x/tasks.md", "- [x] T3 three\n");
    put(&env.cwd, "specs/449-x/tasks-done.md", "- [X] T4 four\n");
    let got = cli(&args(&[&L[..], &["--refuse"]].concat()), &env);
    let named = [
        "task T3",
        "task T4",
        "changed blocks",
        "452-gone",
        "DECIDE_OK",
    ]
    .map(|s| got.stderr.contains(s));
    assert_eq!((got.code, named), (1, [true; 5]));
    assert!(got.stderr.contains("make ledger-owed WRITE="));
    assert_eq!(got.stdout, "");
    // the listing by hand (no --refuse, no --landing) still names every pass
    let listed = cli(&args(&L), &env);
    assert!(listed.stdout.starts_with("ledger-owed: 5 check pass(es)"));
}

#[test]
fn an_open_task_s_plan_review_alone_refuses_nothing_and_says_so() {
    // two rounds of one task's review, the task named once
    let subject = "MODE 4: PLAN REVIEW of one task's section - feature 449-x, task T2 (a decision";
    let log = [
        review("r1", subject),
        review("r2", subject).replace("\"5 s\"", "\"9 s\""),
    ];
    let (_d, env) = world("left-only", &log);
    put(
        &env.cwd,
        "specs/449-x/tasks.md",
        "- [ ] T2 two\n- [x] T20 twenty\n",
    );
    let got = cli(&args(&[&L[..], &["--refuse"]].concat()), &env);
    assert_eq!((got.code, got.stderr.as_str()), (0, ""));
    let said = got.stdout.contains(
        "1 open task(s) left to their own landings and sessions (451 T147, T157), which write their rows: 449-x T2",
    );
    assert!(said);
    // the same pass the landing of T2 itself lands refuses
    let own = cli(
        &args(
            &[
                &L[..],
                &["--refuse", "--landing", "449-x", "--tasks", "T5 T2"],
            ]
            .concat(),
        ),
        &env,
    );
    assert_eq!(own.code, 1);
}

/// 451 T157's world: feature 449-x with T1-T4 started (T3 ticked) and T5 never started, a page session `ps` whose brief is T2's, and a
/// builder `b1` of the bundle T2, T4; each pass's transcript under `<session>/subagents/`, its meta beside it where `meta` gives one.
fn record_world(
    tag: &str,
    log: &[String],
    metas: &[(&str, &str, serde_json::Value)],
) -> (
    l7r_shared::tempdir::Held<std::path::PathBuf>,
    super::super::Env,
) {
    let (d, env) = world(tag, log);
    put(
        &env.cwd,
        "specs/449-x/tasks.md",
        "- [ ] T1 one\n- [ ] T2 two\n- [x] T3 three\n- [ ] T4 four\n- [ ] T5 five\n",
    );
    put(
        &env.cwd,
        "specs/449-x/briefs/t2-checks.md",
        "# Brief - feature 449 bundle T2 (0229), session 2: check and apply\n",
    );
    let starts = ["T1", "T2", "T3", "T4"]
        .map(|t| {
            json!({"feature": "449-x", "task": t, "utc": "2026-11-22T16:16:21Z"}).to_string() + "\n"
        })
        .concat();
    put(&env.cwd, ".git/task-starts.jsonl", &starts);
    let brief = env.cwd.join("specs/449-x/briefs/t2-checks.md");
    // a brief whose first line names no task is read by its file name
    put(
        &env.cwd,
        "specs/449-x/briefs/t4-write.md",
        "# Brief - the shrine pages\n",
    );
    put(
        &env.cwd,
        ".git/page-sessions/index.txt",
        &format!(
            "old /nowhere/specs/1-y/briefs/t9-checks.md\nps {}\nps2 {}\n",
            brief.display(),
            env.cwd.join("specs/449-x/briefs/t4-write.md").display()
        ),
    );
    let projects = d.join("home/.claude/projects/p");
    for (session, agent, meta) in metas {
        let sub = projects.join(session).join("subagents");
        put(
            &sub,
            &format!("agent-{agent}.jsonl"),
            &transcript(&json!("Run the check"), "CLEAR"),
        );
        if !meta.is_null() {
            put(&sub, &format!("agent-{agent}.meta.json"), &meta.to_string());
        }
    }
    (d, env)
}

#[test]
fn another_started_task_s_record_passes_are_its_own_and_the_landing_s_own_still_refuse() {
    let log = [
        pass("quote-check", "q1", "pass-q1 Run quote-check on the bundle /tmp/l7r-check/q-0229-quote-check-t2/MANIFEST.md (question 0229)", &json!({})),
        pass("record-format", "q2", "pass-q2 Run record-format on the bundle /tmp/l7r-check/q-0229-record-format/MANIFEST.md", &json!({})),
        pass("source-reader", "q3", "pass-q3 Run source-reader on the bundle", &json!({})),
        pass("modal-form", "q4", "pass-q4 Judge the four pop-ups", &json!({})),
        pass("impl-drift", "q5", "pass-q5 Judge the claims", &json!({})),
        pass("quote-check", "q6", "pass-q6 449 T5 quote-check", &json!({})),
        pass("record-format", "q7", "pass-q7 Run record-format", &json!({})),
        pass("impl-drift", "q8", "pass-q8 T1 claims re-check", &json!({})),
        pass("building-review", "q9", "pass-q9 449 T2 building-review", &json!({})),
        pass("source-reader", "q10", "pass-q10 Run source-reader", &json!({})),
    ];
    let metas = [
        ("main", "q1", json!(null)),
        (
            "ps",
            "q2",
            json!({"description": "record-format 0229", "spawnDepth": 1}),
        ),
        (
            "main",
            "q3",
            json!({"description": "449 T3: source-reader x", "spawnDepth": 1}),
        ),
        (
            "main",
            "b1",
            json!({"description": "449 bundle T2, T4: the record bundle", "spawnDepth": 1}),
        ),
        (
            "main",
            "q4",
            json!({"description": "Modal-form on four pop-ups", "spawnDepth": 2, "parentAgentId": "b1"}),
        ),
        (
            "main",
            "q5",
            json!({"description": "449 T1: impl-drift on the claims", "spawnDepth": 1}),
        ),
        (
            "main",
            "q7",
            json!({"description": "record-format 0217", "spawnDepth": 1}),
        ),
        ("main", "q9", json!(null)),
        (
            "ps2",
            "q10",
            json!({"description": "source-reader kuri", "spawnDepth": 1}),
        ),
    ];
    let (_d, env) = record_world("left-record", &log, &metas);
    let landing = [
        &L[..],
        &["--refuse", "--landing", "449-x", "--tasks", "T1 T9"],
    ]
    .concat();
    let got = cli(&args(&landing), &env);
    // T2's bundle-named, page-session and builder passes and its own-words one are T2's; T3 ticked, T5 never started, a pass naming
    // nothing, and the landing's own T1 (by its description, and bare) still refuse
    let owed = ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10"]
        .map(|q| got.stderr.contains(&format!("pass-{q} ")));
    let want = [
        false, false, true, false, true, true, true, true, false, false,
    ];
    assert_eq!((got.code, owed), (1, want));
    let said = got.stdout.contains("the passes of 2 open task(s) left to their own landings and sessions (451 T147, T157), which write their rows: 449-x T2, 449-x T4");
    assert!(said, "{}", got.stdout);
    // the landing of T2 itself owes them all
    let own = cli(
        &args(&[&L[..], &["--refuse", "--landing", "449-x", "--tasks", "T2"]].concat()),
        &env,
    );
    let mine = ["q1", "q2", "q4", "q9"].map(|q| own.stderr.contains(&format!("pass-{q} ")));
    assert_eq!((own.code, mine), (1, [true; 4]));
}

/// 451 T167: a page session's bundle carries its session's letter (`q-0123-quote-check-t330a`), read as a task never started (T330a),
/// and the reading stopped there - so 449 T330's quote-check refused a 451 landing (replayed 2026-11-23 on the landing's tree at
/// af418b90c5 and the pass log as it stood at 02:33Z: T330's one pass not left). A source naming no started task gives way to the next:
/// the page session's brief (`t2a-checks.md`, "feature 449 T2 and T4"), and the brief's own task where it names another than its file
/// (`t2b-checks.md`, its first line naming T4, as `t330b-checks.md` named T333). A pass naming T5, never started, with no page session,
/// still refuses.
#[test]
fn a_page_session_pass_naming_its_session_letter_is_left_to_its_briefs_task() {
    let log = [
        pass("quote-check", "s1", "pass-s1 Run your check on the bundle: /tmp/l7r-check/q-0123-quote-check-t2a/MANIFEST.md", &json!({})),
        pass("quote-check", "s2", "pass-s2 Run your check on the bundle: /tmp/l7r-check/q-0116-quote-check-t2b/MANIFEST.md", &json!({})),
        pass("quote-check", "s3", "pass-s3 Run your check on the bundle: /tmp/l7r-check/q-0116-quote-check-t5/MANIFEST.md", &json!({})),
    ];
    let metas = [
        (
            "psa",
            "s1",
            json!({"description": "quote-check 0123", "spawnDepth": 1}),
        ),
        (
            "psb",
            "s2",
            json!({"description": "quote-check 0116", "spawnDepth": 1}),
        ),
        (
            "main",
            "s3",
            json!({"description": "quote-check 0116", "spawnDepth": 1}),
        ),
    ];
    let (_d, env) = record_world("left-letter", &log, &metas);
    for (name, head) in [
        (
            "t2a-checks.md",
            "# Brief - feature 449 T2 and T4.5 (0123), session 2: check and apply\n",
        ),
        (
            "t2b-checks.md",
            "# Brief - feature 449 T4 and the 0116 pointer, session 2: check and apply\n",
        ),
    ] {
        put(&env.cwd, &format!("specs/449-x/briefs/{name}"), head);
    }
    let index = env.cwd.join(".git/page-sessions/index.txt");
    let more: String = [("psa", "t2a-checks.md"), ("psb", "t2b-checks.md")]
        .map(|(sid, name)| {
            let brief = env.cwd.join("specs/449-x/briefs").join(name);
            format!("{sid} {}\n", brief.display())
        })
        .concat();
    let text = std::fs::read_to_string(&index).unwrap() + &more;
    std::fs::write(&index, text).unwrap();
    let got = cli(
        &args(&[&L[..], &["--refuse", "--landing", "451-y", "--tasks", "T9"]].concat()),
        &env,
    );
    let owed = ["s1", "s2", "s3"].map(|q| got.stderr.contains(&format!("pass-{q} ")));
    assert_eq!((got.code, owed), (1, [false, false, true]));
    assert!(
        got.stdout
            .contains("which write their rows: 449-x T2, 449-x T4"),
        "{}",
        got.stdout
    );
}
