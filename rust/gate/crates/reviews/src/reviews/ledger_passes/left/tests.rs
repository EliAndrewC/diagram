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
    assert!(before.stdout.contains("2 open task(s) left to their own landings, which write their rows (451 T147): 449-x T2, 451-y T9"));
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
        "1 open task(s) left to their own landings, which write their rows (451 T147): 449-x T2",
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
