//! 451 T305's pin, 2026-11-26's case as it stood: a message-check round the builder of T295 ran from its pool tree, T295 holding the
//! tree and started nowhere, refused the landing of T281. The landing of T281 is not refused on it and does not write its row; the
//! landing of T295 owes it and writes it; a pass no task can be tied to refuses as before.

use serde_json::json;

use super::super::super::super::tests::put;
use super::super::super::cli;
use super::super::super::tests::{args, pass, transcript, world};

const L: [&str; 2] = ["--ledger", "dev/review-ledger.md"];
/// The subject every message-check pass of the day was logged under (cut at 100 characters), which names no task and no tree.
const JUDGE: &str =
    "Judge the guard message unit(s) in the bundle: read /tmp/l7r-check/guard-messages/MANIFEST.md and th";

/// The day's world: feature 451-y with T281, T295 and T303 open and none of them started; the pool tree `<d>/pool-t270` taken by
/// T295 at 15:42, released at 16:54 and taken by T303 at 17:13 (the clone's own log's lines); the builders `ba` (T295) and `bc`
/// (T303), each briefed into that tree with a description that opens "Build" (so `builder_brief` reads neither); and the passes
/// `(agent, when its transcript opens, its meta)`.
fn day(
    tag: &str,
    log: &[String],
    passes: &[(&str, &str, serde_json::Value)],
) -> (
    l7r_shared::tempdir::Held<std::path::PathBuf>,
    super::super::super::Env,
) {
    let (d, env) = world(tag, log);
    put(
        &env.cwd,
        "specs/451-y/tasks.md",
        "- [ ] T281 a\n- [ ] T295 b\n- [ ] T303 c\n- [x] T284 d\n",
    );
    let tree = d.join("pool-t270");
    let event = |utc: &str, event: &str, detail: &str| {
        json!({"utc": utc, "event": event, "tree": tree, "detail": detail}).to_string() + "\n"
    };
    let pool = [
        event("2026-11-26T14:57:25Z", "adopt", "free"),
        "not a line of the log\n".to_owned(),
        event("when", "take", "451 T1"),
        event("2026-11-26T15:42:54Z", "take", "451 T295"),
        event("2026-11-26T15:43:00Z", "discard", "a stale edit"),
        event("2026-11-26T16:54:35Z", "release", "451 T295"),
        event("2026-11-26T17:13:14Z", "take", "451 T303,T284"),
        event("2026-11-26T18:00:00Z", "landed", "451 T303,T284"),
        event("2026-11-26T18:30:00Z", "take", "T9"),
    ]
    .concat();
    put(&env.cwd, ".git/builder-pool.log", &pool);
    let sub = d.join("home/.claude/projects/p/main/subagents");
    for (agent, task) in [("ba", "T295"), ("bc", "T303")] {
        let brief = format!(
            "Build feature 451 task {task} in the pool worktree {} (handed to it by `make builder-tree`)\nBlocks: none",
            tree.display()
        );
        put(
            &sub,
            &format!("agent-{agent}.jsonl"),
            &transcript(&json!([{"type": "text", "text": brief}]), "built"),
        );
        put(
            &sub,
            &format!("agent-{agent}.meta.json"),
            &json!({"description": format!("Build 451 {task} wrong-tree guards"), "spawnDepth": 1})
                .to_string(),
        );
    }
    for (n, (agent, at, meta)) in passes.iter().enumerate() {
        // a time opening `-` is a transcript whose first record carries none
        let (first, at) = at
            .strip_prefix('-')
            .map_or(("", *at), |at| ("{\"type\": \"summary\"}\n", at));
        let text = first.to_owned()
            + &transcript(&json!("Judge the unit"), "KEEP")
                .replace("2026-11-01T00:00:0", &format!("{at}:0"))
                .replace("2026-11-01T00:00:1", &format!("{at}:1"))
                // each pass its own cost: a row answers the pass of its check with its cost cells
                .replace("1650", &format!("{}", 1650 + 100 * n));
        put(&sub, &format!("agent-{agent}.jsonl"), &text);
        put(&sub, &format!("agent-{agent}.meta.json"), &meta.to_string());
    }
    (d, env)
}

/// A check a builder dispatched (`spawnDepth` 2, its parent the builder).
fn by(builder: &str) -> serde_json::Value {
    json!({"description": "Message check static-runs", "spawnDepth": 2, "parentAgentId": builder})
}

/// The nine passes of the day's world, in order, with what ties each (or does not):
/// - m1: T295's builder's round, 16:19, as logged that day; m2: a round T303's builder ran from the same tree once it was handed on;
/// - m3: the main session's own round, tied to no task;
/// - m4, m5: rounds of T295's builder's while the tree was free (17:00) and before the pool's log begins (14:00);
/// - m6: a pass whose own words name the tree and its feature, 16:20 - the feature's trace reaches it, and T295 holds its tree;
/// - m7: a tree beside the pool's (`pool-t270-old`), which is not the pool's; m8: under a hold naming no feature (18:40);
/// - m9: a pass whose transcript's first record carries no time.
fn nine(
    tag: &str,
) -> (
    l7r_shared::tempdir::Held<std::path::PathBuf>,
    super::super::super::Env,
) {
    let main = json!({"description": "Message check", "spawnDepth": 1});
    let passes = [
        ("m1", "2026-11-26T16:19", by("ba")),
        ("m2", "2026-11-26T17:20", by("bc")),
        ("m3", "2026-11-26T16:21", main.clone()),
        ("m4", "2026-11-26T17:00", by("ba")),
        ("m5", "2026-11-26T14:00", by("ba")),
        ("m6", "2026-11-26T16:20", main.clone()),
        ("m7", "2026-11-26T16:22", main.clone()),
        ("m8", "2026-11-26T18:40", by("bc")),
        ("m9", "-2026-11-26T16:25", by("ba")),
    ];
    // the tree's path is the scratch world's, so the pass log is written once the world's directory is known
    let (d, env) = day(tag, &[], &passes);
    let tree = d.join("pool-t270").to_string_lossy().into_owned();
    let log: Vec<String> = (1..=9)
        .map(|n| {
            let (check, subject) = match n {
                6 => (
                    "escalation-check",
                    format!("feature 451-y draft. Tree: {tree} (o"),
                ),
                7 => ("escalation-check", format!("Draft. Tree: {tree}-old (o")),
                _ => ("message-check", JUDGE.to_owned()),
            };
            let subject = format!("pass-m{n} {subject}");
            pass(check, &format!("m{n}"), &subject, &json!({}))
        })
        .collect();
    let log = log.join("\n") + "\n";
    put(&env.cwd, ".git/check-passes.jsonl", &log);
    (d, env)
}

/// Which of the nine `got` names as owed.
fn owed(got: &crate::Reply) -> [bool; 9] {
    ["m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8", "m9"]
        .map(|m| got.stderr.contains(&format!("pass-{m} ")))
}

/// The landing of `tasks` asking what it owes.
fn landing(env: &super::super::super::Env, tasks: &str) -> crate::Reply {
    let asked = ["--refuse", "--landing", "451-y", "--tasks", tasks];
    cli(&args(&[&L[..], &asked[..]].concat()), env)
}

/// The passes tied to no task: the main session's, one made while the tree was free or before its log, a tree beside the pool's, a
/// hold with no feature, a transcript with no time.
const UNTIED: [bool; 9] = [false, false, true, true, true, false, true, true, true];
/// What T295's landing owes: its own two beside the untied.
const T295_S: [bool; 9] = [true, false, true, true, true, true, true, true, true];

#[test]
fn a_builder_s_pass_from_its_pool_tree_is_its_task_s_landing_s_and_no_other_s() {
    let (_d, env) = nine("pool");
    // THE LANDING OF T281 (2026-11-26's refusal): T295's two passes and T303's one are their own landings'; the untied refuse as before
    let b = landing(&env, "T281");
    assert_eq!((b.code, owed(&b)), (1, UNTIED), "{}", b.stderr);
    let said = b.stdout.contains("the passes of 2 open task(s) left to their own landings and sessions (451 T147, T157), which write their rows: 451-y T295, 451-y T303");
    assert!(said, "{}", b.stdout);
    // the push (no landing) leaves them the same way
    let push = cli(&args(&[&L[..], &["--refuse"]].concat()), &env);
    assert_eq!(owed(&push), UNTIED);
    // THE LANDING OF T295 owes its own two, m1 by its builder's tree though T303 holds that tree now; T303's stays T303's
    let a = landing(&env, "T295");
    assert_eq!((a.code, owed(&a)), (1, T295_S), "{}", a.stderr);
    // a bundle's landing (T303 with the ticked T284) owes its builder's pass
    assert!(owed(&landing(&env, "T303 T284"))[1]);
}

#[test]
fn a_landing_s_write_leaves_another_open_task_s_row_and_writes_its_own_tasks() {
    let (_d, env) = nine("pool-write");
    let write = |tasks: &str| {
        let asked = [
            "--write",
            "specs/451-y/ (make land)",
            "--landing",
            "451-y",
            "--tasks",
            tasks,
        ];
        cli(&args(&[&L[..], &asked[..]].concat()), &env).stdout
    };
    // T281'S LANDING WRITES NEITHER: m6 is traced to the feature, and is T295's
    assert!(write("T281").starts_with("ledger-owed: 0 row(s) written for feature 451"));
    assert_eq!(owed(&landing(&env, "T295")), T295_S);
    // T295'S LANDING WRITES ITS OWN - m1, which no trace of the feature reaches, and m6 - and no other task's
    assert!(write("T295").starts_with("ledger-owed: 2 row(s) written for feature 451"));
    assert_eq!(owed(&landing(&env, "T295")), UNTIED);
    assert!(owed(&landing(&env, "T303"))[1]);
    // a write no landing asks (a feature's by hand) is the trace's alone, as before: m6 is written, m1 is not
    let (_d2, env2) = nine("pool-hand");
    let hand = cli(
        &args(&[&L[..], &["--write", "specs/451-y/ (by hand)"]].concat()),
        &env2,
    );
    assert!(hand
        .stdout
        .starts_with("ledger-owed: 1 row(s) written for feature 451"));
    let after = owed(&landing(&env2, "T295"));
    assert_eq!((after[0], after[5]), (true, false));
}

#[test]
fn a_pass_with_no_first_record_and_a_ticked_holder_s_pass_still_refuse() {
    let log = [
        pass(
            "message-check",
            "n1",
            &format!("pass-n1 {JUDGE}"),
            &json!({}),
        ),
        pass(
            "message-check",
            "n2",
            &format!("pass-n2 {JUDGE}"),
            &json!({}),
        ),
    ];
    let (d, env) = day("pool-edge", &log, &[("n2", "2026-11-26T17:20", by("bc"))]);
    let sub = d.join("home/.claude/projects/p/main/subagents");
    // n1's transcript is empty, its builder's unreadable as one
    put(&sub, "agent-n1.jsonl", "");
    put(&sub, "agent-n1.meta.json", &by("ba").to_string());
    // T303 is ticked: its landing is past, so the pass its builder left unrowed holds the next push, as any ticked task's does
    put(
        &env.cwd,
        "specs/451-y/tasks.md",
        "- [x] T303 c\n- [x] T284 d\n- [ ] T281 a\n",
    );
    let got = cli(
        &args(
            &[
                &L[..],
                &["--refuse", "--landing", "451-y", "--tasks", "T281"],
            ]
            .concat(),
        ),
        &env,
    );
    let owed = ["n1", "n2"].map(|n| got.stderr.contains(&format!("pass-{n} ")));
    assert_eq!((got.code, owed, got.stdout.as_str()), (1, [true; 2], ""));
}
