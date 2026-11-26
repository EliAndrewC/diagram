//! The guard on a mirror whose clone has a pool: a builder's dispatch held to its marker, a check, a reader of no pool tree and the
//! claims round passed, the escape taken only on a line of its own.

use std::path::PathBuf;

use serde_json::{json, Value};

use super::{decide, refusal, verdict, Said};
use crate::protocol::{Answer, Event};
use crate::shared::builder_brief::Marker;
use crate::shared::builder_pool::{write, Tree};
use crate::shared::session::Session;

const T271: &str = "/m/.clones/c-t271";

/// The pool: `c-t271` held by 451 T334, `c-t270` free, `c-b1` held by a task that named no feature, `c-t272` by a bundle.
fn pool() -> Vec<Tree> {
    let tree = |name: &str, feature: &str, tasks: &[&str]| Tree {
        tree: PathBuf::from(format!("/m/.clones/{name}")),
        feature: feature.to_owned(),
        tasks: tasks.iter().map(|t| (*t).to_owned()).collect(),
        since: String::new(),
    };
    vec![
        tree("c-t270", "", &[]),
        tree("c-t271", "451", &["T334"]),
        tree("c-b1", "", &["T9"]),
        tree("c-t272", "451", &["T299", "T282"]),
    ]
}

fn call(kind: &str, prompt: &str) -> Value {
    json!({"tool_name": "Agent", "tool_input": {"subagent_type": kind, "prompt": prompt}})
}

fn said(prompt: &str) -> Said {
    verdict(&call("", prompt), &pool())
}

fn marker(kind: &str, jobs: usize, task: &str, tree: &str) -> Marker {
    Marker {
        feature: "451".to_owned(),
        task: task.to_owned(),
        kind: kind.to_owned(),
        jobs,
        tree: PathBuf::from(tree),
    }
}

/// A brief with the block's marker for `kind`, then `body`.
fn brief(kind: &str, body: &str) -> String {
    format!(
        "{}\nBlocks: none\nWork in {T271} only.\n{body}\n",
        marker(kind, 1, "T334", T271).line()
    )
}

#[test]
fn only_a_builder_s_dispatch_is_judged() {
    let named = format!("Build 451 T334 in the pool worktree {T271} (work only there).");
    // a builder: no type, general-purpose or claude, naming a pool tree
    for kind in ["", "general-purpose", "claude"] {
        let v = verdict(&call(kind, &named), &pool());
        let want = Said::NoMarker("T334".to_owned(), "451".to_owned());
        assert_eq!(v, want, "{kind}");
    }
    // a check, a reader that cannot edit, another tool, the claims round, a dispatch naming no pool tree
    for kind in ["spec-fidelity", "Explore", "impl-drift"] {
        assert_eq!(verdict(&call(kind, &named), &pool()), Said::Pass, "{kind}");
    }
    let mut bash = call("", &named);
    bash["tool_name"] = json!("Bash");
    assert_eq!(verdict(&bash, &pool()), Said::Pass);
    assert_eq!(verdict(&json!({"tool_name": "Agent"}), &pool()), Said::Pass);
    for prompt in [
        format!("  Run the claims round for feature 451 T334; the builder's tree is {T271}."),
        "Read /m/.clones/c/docs/x.md and report.".to_owned(),
        // a longer name that only starts as a pool tree's, and the clone itself
        format!("Read {T271}0/x and {T271}-land/y and /m/.clones/c/z."),
        // a sentence that mentions the marker
        "The block opens `BUILDER-BRIEF <feature> <task> KIND=<kind> JOBS=<n> TREE=<path>`."
            .to_owned(),
    ] {
        assert_eq!(said(&prompt), Said::Pass, "{prompt}");
    }
    // a tree named at a sentence's end, and one as a path's parent, are named
    for prompt in [format!("Work in {T271}."), format!("Read {T271}/Makefile")] {
        assert!(matches!(said(&prompt), Said::NoMarker(..)), "{prompt}");
    }
    // a neighbor's free tree named beside the held one: the held one's task is the command's; a free tree alone names none
    let both = "Another builder is in /m/.clones/c-t270. Work in /m/.clones/c-b1.";
    assert_eq!(said(both), Said::NoMarker("T9".to_owned(), String::new()));
    assert_eq!(
        said("Work in /m/.clones/c-t270"),
        Said::NoMarker(String::new(), String::new())
    );
}

#[test]
fn a_marker_is_held_to_its_kind_its_jobs_and_the_pool() {
    assert_eq!(said(&brief("build-half", "Build it.")), Said::Pass);
    assert_eq!(said(&brief("fix", "Job 2: fix the reader.")), Said::Pass);
    let with = |m: &Marker| said(&format!("{}\nthe task", m.line()));
    let odd = marker("mechanism", 1, "T334", T271);
    assert_eq!(with(&odd), Said::Kind(odd.clone()));
    let many = marker("fix", 4, "T334", T271);
    assert_eq!(with(&many), Said::Jobs(many.clone()));
    assert_eq!(with(&marker("fix", 3, "T334", T271)), Said::Pass);
    // a tree no pool holds (no pool tree named either: the marker alone is judged), another task's, a free one, another feature's
    let gone = marker("fix", 1, "T334", "/m/.clones/c-x");
    assert_eq!(
        with(&gone),
        Said::Tree(gone.clone(), "not a pool tree".to_owned())
    );
    let other = marker("fix", 1, "T335", T271);
    assert_eq!(
        with(&other),
        Said::Tree(other.clone(), "held by 451 T334".to_owned())
    );
    let free = marker("fix", 1, "T334", "/m/.clones/c-t270");
    assert_eq!(
        with(&free),
        Said::Tree(free.clone(), "held by free".to_owned())
    );
    let mut theirs = marker("fix", 1, "T334", T271);
    theirs.feature = "449".to_owned();
    assert_eq!(
        with(&theirs),
        Said::Tree(theirs.clone(), "held by 451 T334".to_owned())
    );
    // a bundle: the marker names every task joined by commas, in any order, or one of them; a task the hold lacks is not held
    let t272 = "/m/.clones/c-t272";
    for tasks in ["T299,T282", "T282,T299", "T282"] {
        assert_eq!(with(&marker("fix", 2, tasks, t272)), Said::Pass, "{tasks}");
    }
    let wider = marker("fix", 1, "T299,T300", t272);
    let holder = "held by 451 T299,T282".to_owned();
    assert_eq!(with(&wider), Said::Tree(wider.clone(), holder));
    let prose = format!("Build 451 T299 and T282 as one bundle in {t272}.");
    let want = Said::NoMarker("T299,T282".to_owned(), "451".to_owned());
    assert_eq!(said(&prose), want);
    // a hold that named no feature is held for any
    assert_eq!(with(&marker("fix", 1, "T9", "/m/.clones/c-b1")), Said::Pass);
}

#[test]
fn a_measurement_brief_that_orders_an_edit_is_refused_narrowly() {
    for (body, line) in [
        ("Job 1, the measurement.\nJob 2, only if job 1 shows a safe rule: build it in slot.rs's callers", "Job 2, only if job 1 shows a safe rule: build it in slot.rs's callers"),
        ("  job 2: then FIX what it shows, red-first", "job 2: then FIX what it shows, red-first"),
        ("Part 3 - implement the lever", "Part 3 - implement the lever"),
        ("Step 2: patch the reader", "Step 2: patch the reader"),
        ("Job 3: the tests, red-first", "Job 3: the tests, red-first"),
    ] {
        let m = marker("measurement", 1, "T334", T271);
        assert_eq!(said(&brief("measurement", body)), Said::Edits(m, line.to_owned()), "{body}");
    }
    // what it does not catch, and a measurement that orders none
    for body in [
        "Measure it, then fix what you find.",
        "(2) fix the reader",
        "Job 2: change the reader",
        "Job 1: time the prefix of each build",
        "Measure the seven crates; change no source.",
    ] {
        assert_eq!(said(&brief("measurement", body)), Said::Pass, "{body}");
    }
    // the line shown is cut at 120 characters
    let long = format!("Job 2: fix {}", "x".repeat(200));
    let shown: String = long.chars().take(120).collect();
    let m = marker("measurement", 1, "T334", T271);
    assert_eq!(said(&brief("measurement", &long)), Said::Edits(m, shown));
}

#[test]
fn the_escape_is_a_line_of_its_own_with_a_reason() {
    let named = format!("Read the log under {T271} and report.");
    for (line, want) in [
        (
            "BUILDER_BRIEF_OK: a reader of one log",
            Said::Escaped("a reader of one log".to_owned()),
        ),
        (
            "  BUILDER_BRIEF_OK=\"a reader of one log\"",
            Said::Escaped("a reader of one log".to_owned()),
        ),
        ("BUILDER_BRIEF_OK:", Said::NoReason),
        ("BUILDER_BRIEF_OK: short", Said::NoReason),
        (
            "BUILDER_BRIEF_OK: <reason, two words or more>",
            Said::NoReason,
        ),
    ] {
        assert_eq!(said(&format!("{named}\n{line}\n")), want, "{line}");
    }
    // quoted in a sentence, as this task's own brief did: not taken
    let quoted = format!(
        "{named} The escape is `BUILDER_BRIEF_OK=\"<reason of two words or more>\"` in the prompt."
    );
    assert!(matches!(said(&quoted), Said::NoMarker(..)));
    // checked before the marker's refusals, and never for a dispatch that is no builder's
    let odd = format!(
        "{}\nBUILDER_BRIEF_OK: a fixture for a suite",
        marker("odd", 9, "T1", "/x").line()
    );
    assert_eq!(
        said(&odd),
        Said::Escaped("a fixture for a suite".to_owned())
    );
    assert_eq!(said("BUILDER_BRIEF_OK: a reader of one log"), Said::Pass);
}

#[test]
fn each_refusal_prints_the_command_that_makes_the_brief() {
    assert_eq!(refusal(&Said::Pass), None);
    assert_eq!(refusal(&Said::Escaped("a b c d e".to_owned())), None);
    let m = marker("measurement", 5, "T334", T271);
    let all = "KIND=fix|measurement|build-half|closing-half";
    for (said, rule, words) in [
        (Said::NoReason, "BUILDER_BRIEF_OK-no-reason", "BUILDER_BRIEF_OK with no reason".to_owned()),
        (Said::NoMarker("T334".to_owned(), "451".to_owned()), "no-marker", format!("make builder-brief T=T334 F=451 {all} [JOBS=<n>]")),
        (Said::NoMarker(String::new(), String::new()), "no-marker", format!("make builder-brief T=<task> F=<feature> {all}")),
        (Said::Kind(m.clone()), "unknown-kind", format!("KIND=measurement is no builder's kind.\n\nRun: make builder-brief T=T334 F=451 {all}")),
        (Said::Jobs(m.clone()), "too-many-jobs", "JOBS=5 - a brief holds at most 3 jobs".to_owned()),
        (Said::Jobs(m.clone()), "too-many-jobs", "make builder-brief T=T334 F=451 KIND=measurement JOBS=<1-3>".to_owned()),
        (Said::Tree(m.clone(), "held by 451 T9".to_owned()), "tree-not-held", format!("{T271} is not held by 451 T334 in the pool (held by 451 T9).\n\nRun: make builder-brief T=T334 F=451 KIND=measurement")),
        (Said::Edits(m.clone(), "Job 2: fix it".to_owned()), "measurement-edits", "`Job 2: fix it`".to_owned()),
        (Said::Edits(m.clone(), String::new()), "measurement-edits", "then: make builder-brief T=T334 F=451 KIND=fix".to_owned()),
    ] {
        let (text, named) = refusal(&said).unwrap();
        assert_eq!(named, rule);
        assert!(text.starts_with("BLOCKED (builder-brief): ") && text.contains(&words), "{text}");
        assert_eq!(text.contains("BUILDER_BRIEF_OK: <reason, two words or more>"), rule != "BUILDER_BRIEF_OK-no-reason");
    }
}

#[test]
fn the_guard_reads_the_clones_pools_answers_and_logs() {
    crate::shared::log::quiet();
    let dir = crate::shared::tempdir::TempDir::new("builder-brief-decide");
    let main = dir.join("m");
    std::fs::create_dir_all(main.join(".clones/c/.git")).unwrap();
    let tree = main.join(".clones/c-t271");
    let held = Tree {
        tree: tree.clone(),
        feature: "451".to_owned(),
        tasks: vec!["T334".to_owned()],
        since: String::new(),
    };
    write(&main.join(".clones/c/.git"), &[held]).unwrap();
    let run = |prompt: &str| {
        let input = call("general-purpose", prompt);
        let mut s = Session::from_input(&input);
        s.main_seam = Some(main.to_string_lossy().into_owned());
        decide(
            &Event {
                name: "PreToolUse".to_owned(),
                input,
            },
            &s,
        )
    };
    let named = format!("Build T334 in {}.", tree.display());
    assert!(
        matches!(&run(&named)[..], [Answer::Refuse(t)] if t.contains("make builder-brief T=T334 F=451 KIND="))
    );
    assert!(run(&format!("{named}\nBUILDER_BRIEF_OK: a fixture for a test")).is_empty());
    let good = Marker {
        feature: "451".to_owned(),
        task: "T334".to_owned(),
        kind: "fix".to_owned(),
        jobs: 1,
        tree,
    };
    assert!(run(&format!("{}\n{named}", good.line())).is_empty());
    // a marker for a tree no registry holds, with no clone's path in the prompt: still read
    let stray = marker("fix", 1, "T334", "/elsewhere/x");
    assert!(
        matches!(&run(&stray.line())[..], [Answer::Refuse(t)] if t.contains("not a pool tree"))
    );
    // a dispatch naming neither is answered before any registry is read
    assert!(run("Summarize docs/usage.md").is_empty() && run("").is_empty());
}
