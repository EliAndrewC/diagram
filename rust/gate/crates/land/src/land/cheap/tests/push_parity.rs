//! 451 T413: the push's questions the first pass did not ask - its unrelated-history refusal and its in-progress rule over every spec
//! directory the delta touches and the feature pointer - and the two cases of 2026-11-26/27 pinned: a ledger row owed for a pass made
//! after the first pass, and a block of a batch's second task changed since its review.

use l7r_gate_core::ci::fixtures::{git, put};

use super::super::super::tests::{fx, has, Fx, NOTE};
use super::tasks;

/// The first pass of `T` over the fixture's feature.
fn first_pass(fx: &Fx, t: &[&str]) -> Vec<String> {
    let d = fx.root.join("specs/449-x");
    fx.land.cheap_refusals(&d, &tasks(t), NOTE, None).unwrap()
}

/// THE PUSH'S `refuse_unrelated_history`: a clone on a history main no longer shares (feature 301's scrub) is refused in the first
/// pass, before the pass commits anything of its own - the cure is a re-clone, and the push would refuse it before its ledger write.
#[test]
fn a_clone_whose_history_shares_no_commit_with_main_s_is_refused_before_anything_is_written() {
    let fx = fx("parity-unrelated");
    git(&fx.root, &["checkout", "-q", "--orphan", "old"]);
    git(&fx.root, &["commit", "-qm", "the old history"]);
    let before = git(&fx.root, &["rev-parse", "HEAD"]);
    let stops = first_pass(&fx, &["T1"]);
    assert_eq!(stops.len(), 1, "{stops:?}");
    has(
        &stops[0],
        "this clone's history shares no commit with main's",
    );
    has(&stops[0], "git clone ");
    assert_eq!(git(&fx.root, &["rev-parse", "HEAD"]), before);
    // no origin/main to judge against (a fresh repository's case, as the shell's first line has it): nothing refused
    git(&fx.root, &["remote", "remove", "origin"]);
    assert_eq!(fx.land.unrelated_history(), Ok(String::new()));
}

/// THE PUSH'S IN-PROGRESS RULE OVER EVERY TOUCHED SPEC DIRECTORY: another feature the delta touches with a task holding it refuses the
/// push, asked with none of the landing's ticks (here T1), which the push's environment names the landed feature's alone (451 T479:
/// feature 449's landing of T5 leaves 450's started T5 holding); a status line that closes it holds nothing, and a holding answer that
/// fails holds, as the push fails closed.
#[test]
fn another_feature_in_progress_that_the_delta_touches_is_refused_unless_its_status_closes_it() {
    let fx = fx("parity-other");
    fx.in_delta("specs/450-y/tasks.md", "- [ ] T5 five\n");
    let held = "T5 five  <- the active task (make task-start)\n";
    fx.answers
        .holding_by
        .borrow_mut()
        .insert("450-y".to_owned(), held.to_owned());
    let stops = first_pass(&fx, &["T1"]);
    assert_eq!(stops.len(), 1, "{stops:?}");
    has(&stops[0], "specs/450-y has a task IN PROGRESS");
    has(&stops[0], "T5 five");
    let asked = fx.answers.asked.borrow().join("\n");
    has(
        &asked,
        &format!("holding {}/specs/450-y []", fx.root.display()),
    );
    drop(asked);
    // a spec directory with no tasks.md asks nothing
    fx.in_delta("specs/450-z/notes.md", "z\n");
    fx.in_delta("specs/450-y/spec.md", "# y\n\n**Status**: Done - closed\n");
    assert_eq!(first_pass(&fx, &["T1"]), Vec::<String>::new());
    fx.in_delta("specs/450-y/spec.md", "# y\n\n**Status**: Open\n");
    fx.answers
        .holding_by
        .borrow_mut()
        .insert("450-y".to_owned(), "fails".to_owned());
    let stops = first_pass(&fx, &["T1"]);
    assert_eq!(stops.len(), 1, "{stops:?}");
    has(&stops[0], "specs/450-y has a task IN PROGRESS");
}

/// ...AND THE FEATURE POINTER: `.specify/feature.json` naming a feature in progress the delta does not touch refuses the push too; the
/// pointer naming the landed feature asks nothing more.
#[test]
fn the_feature_pointer_naming_a_feature_in_progress_is_refused() {
    let fx = fx("parity-pointer");
    put(&fx.root, "specs/450-y/tasks.md", "- [ ] T5 five\n");
    git(&fx.root, &["add", "-A"]);
    git(&fx.root, &["commit", "-qm", "450 on main"]);
    git(&fx.root, &["push", "-q", "origin", "HEAD:main"]);
    fx.answers
        .holding_by
        .borrow_mut()
        .insert("450-y".to_owned(), "T5 five\n".to_owned());
    let pointer = ".specify/feature.json";
    fx.in_delta(pointer, "{\"feature_directory\": \"specs/450-y/\"}\n");
    let stops = first_pass(&fx, &["T1"]);
    assert_eq!(stops.len(), 1, "{stops:?}");
    has(&stops[0], "specs/450-y has a task IN PROGRESS");
    fx.in_delta(pointer, "{\"feature_directory\": \"specs/449-x\"}\n");
    assert_eq!(first_pass(&fx, &["T1"]), Vec::<String>::new());
    // an empty pointer (`json-field`'s `-`) names none
    fx.in_delta(pointer, "{\"feature_directory\": \"\"}\n");
    assert_eq!(first_pass(&fx, &["T1"]), Vec::<String>::new());
}

/// A landing ruled ready beside the mark's task (451 T101) is told so to the push in `L7R_LAND_READY`, which exempts the landed
/// feature's hold alone (451 T432): the first pass still asks every other feature, and refuses one that holds, as the push does.
#[test]
fn a_landing_ruled_ready_still_asks_every_other_feature_as_the_push_does() {
    let fx = fx("parity-ready");
    fx.in_delta("specs/450-y/tasks.md", "- [ ] T5 five\n");
    fx.answers
        .holding_by
        .borrow_mut()
        .insert("450-y".to_owned(), "T5 five\n".to_owned());
    fx.land.ready.set(true);
    let stops = first_pass(&fx, &["T1"]);
    assert_eq!(stops.len(), 1, "{stops:?}");
    has(&stops[0], "specs/450-y has a task IN PROGRESS");
    let asked = fx.answers.asked.borrow().join("\n");
    assert!(asked.contains("450-y"), "{asked}");
}

/// THE CASE OF 2026-11-26/27 (a): a pass made while the gate ran that the landing's last write does not take (traced to no task it
/// lands) was met by the push's ledger row after the gate. Asked again after that write, it refuses before the ticks, naming the cure.
#[test]
fn a_pass_the_landing_s_last_write_does_not_take_refuses_before_the_ticks() {
    let fx = fx("parity-ledger");
    *fx.answers.ledger_seq.borrow_mut() = vec![String::new(), "| ? | owed |\n".to_owned()];
    let d = fx.root.join("specs/449-x");
    assert_eq!(fx.land.land(&d, &tasks(&["T1"]), NOTE), Ok(2));
    let err = fx.said().1;
    has(
        &err,
        "land: refused before the ticks - nothing ticked, nothing pushed",
    );
    has(&err, "make ledger-owed WRITE=");
    assert!(!fx.subjects().contains("T1 ticked"));
    assert!(!fx.log().contains("sync-with-main.sh done"));
    let asked = fx.answers.asked.borrow().join("\n");
    assert_eq!(asked.matches("ledger --write specs/449-x/ ").count(), 2);
}

/// What the landing's write does with each pass, through the real ledger: its own task's pass is written whatever its reply (no
/// transcript: `see reply`), and a pass traced to nothing it lands is left owed - the one row its refusal then names.
#[test]
fn the_landing_s_write_takes_its_own_pass_and_leaves_an_untraced_one_owed() {
    use super::super::super::inproc::{Inproc as _, Real};
    let fx = fx("parity-ledger-real");
    let root = fx.root.clone();
    let line = |agent: &str, check: &str, subject: &str| {
        format!("{{\"date\": \"2026-11-27\", \"check\": \"{check}\", \"subject\": \"{subject}\", \"agent\": \"{agent}\", \"segment\": 0, \"wall\": \"5 s\", \"tokens\": \"1k in (0k cached) / 0.5k out\"}}\n")
    };
    let own = line(
        "m1",
        "quote-check",
        "449 T1 quote-check of the landing's own page",
    );
    let other = line("o1", "glyph-check", "the well glyph of pool/a.svg");
    let start = "{\"feature\": \"449-x\", \"task\": \"T1\", \"utc\": \"2026-11-27T01:00:00Z\"}\n";
    put(&root, ".git/task-starts.jsonl", start);
    let heading = l7r_shared::ledger::MEASURED_HEADING;
    put(&root, "dev/review-ledger.md", &format!("{heading}\n\n"));
    put(&root, "passes.jsonl", &[own, other].concat());
    let (log, ledger) = (root.join("passes.jsonl"), root.join("dev/review-ledger.md"));
    let (log, ledger) = (log.to_string_lossy(), ledger.to_string_lossy());
    let none = root.join("no-transcripts");
    let none = none.to_string_lossy();
    let ask = |head: &[&str]| {
        let mut words: Vec<String> = head.iter().map(|s| (*s).to_owned()).collect();
        let tail = [
            "--log",
            &log,
            "--transcripts",
            &none,
            "--ledger",
            &ledger,
            "--landing",
            "449-x",
            "--tasks",
            "T1",
        ];
        words.extend(tail.map(str::to_owned));
        Real.ledger(&words, &root)
    };
    let wrote = ask(&["--write", "specs/449-x/"]);
    has(
        &wrote.stdout,
        "ledger-owed: 1 row(s) written for feature 449",
    );
    let rows = std::fs::read_to_string(root.join("dev/review-ledger.md")).unwrap();
    has(&rows, "| quote-check |");
    has(&rows, "see reply");
    let left = ask(&["--refuse"]);
    assert_eq!(left.code, 1);
    has(&left.stderr, "| glyph-check |");
    assert!(!left.stderr.contains("| quote-check |"), "{}", left.stderr);
}

/// The plan of two decided task sections, its review recorded whole and CLEAR (`record`'s own digest of every block).
fn reviewed_plan(fx: &Fx) {
    let d = fx.root.join("specs/449-x");
    let plan = "# Plan\n\nThe fixture's plan.\n\n## T1 one\n\n- one decided\n\n## T2 two\n\n- two decided\n";
    put(&d, "plan.md", plan);
    let sum = std::process::Command::new("sha256sum")
        .arg(d.join("plan.md"))
        .output()
        .unwrap();
    let sha = String::from_utf8_lossy(&sum.stdout)[..64].to_owned();
    let review = format!("{{\"plan_sha256\": \"{sha}\", \"decisions\": []}}");
    put(&fx.root, "review-in.json", &review);
    let src = fx
        .root
        .join("review-in.json")
        .to_string_lossy()
        .into_owned();
    let words = ["record", "449", &src, "--as", "spec-fidelity"].map(str::to_owned);
    let claims = |_: &[String]| l7r_gate_core::Reply {
        stdout: String::new(),
        stderr: String::new(),
        code: 0,
    };
    let recorded = l7r_gate_plan::plan::cli(&words, &fx.root, &claims);
    has(&recorded.stdout, "CLEAR recorded");
    std::fs::remove_file(fx.root.join("review-in.json")).unwrap();
    fx.in_delta("specs/449-x/plan.md", plan);
}

/// THE CASE OF 2026-11-26/27 (b): a batch landing of two tasks, the second's section changed since its review, is refused in the first
/// pass - each task's tick check asks its own section (`held_for`), so the batch's second is asked as the push will ask it once ticked
/// - naming `make plan-delta`; the first task, its section unchanged, is not refused. It held on the code before 451 T413: pinned.
#[test]
fn a_batch_landing_whose_second_task_s_block_changed_since_its_review_is_refused_in_the_first_pass()
{
    let fx = fx("parity-plan-batch");
    // the feature's report, so the batch's tick of its last open boxes is not refused for the closing check
    fx.in_delta("specs/449-x/report.md", "# r\n");
    reviewed_plan(&fx);
    assert_eq!(first_pass(&fx, &["T1", "T2"]), Vec::<String>::new());
    let d = fx.root.join("specs/449-x");
    let changed = std::fs::read_to_string(d.join("plan.md"))
        .unwrap()
        .replace("- two decided", "- two decided again, another way");
    fx.in_delta("specs/449-x/plan.md", &changed);
    let stops = first_pass(&fx, &["T1", "T2"]);
    assert_eq!(stops.len(), 1, "{stops:?}");
    assert!(stops[0].starts_with("T2: "), "{stops:?}");
    has(&stops[0], "block(s) of plan.md changed since their review");
    has(&stops[0], "make plan-delta F=");
    has(&stops[0], "## T2 two");
}
