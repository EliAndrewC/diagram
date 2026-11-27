//! `make builder-brief` on a real repository and its pool (feature 451 T334): each sizing refusal before any tree is taken, the block
//! of each kind with its marker and its STOP POINT line, shorter than the prefix guard's block, and the pool's refusals passed on.

use std::path::{Path, PathBuf};

use l7r_gate_core::ci::fixtures::{git, put};
use l7r_gate_core::write_executable;
use l7r_shared::builder_brief::{parse, Marker};
use l7r_shared::builder_pool;

use super::{run, task_line};
use crate::builder_tree::Env;
use crate::tests::{repo, root_of};

const TASKS: &str = "# Tasks\n\n- [ ] T01 the reader misreads a quoted path\n      research: rendering\n- [ ] T02 holds: a guard refuses a hand dispatch, printing the command\n- [x] T09 done\n";

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

fn env(dir: &Path) -> Env {
    Env {
        cache: dir.join("cache"),
        cap: 1,
        now: "2026-11-26T12:00:00Z".to_owned(),
        lock_tries: 1,
        discard: String::new(),
        reason: String::new(),
        guard_secs: "5".to_owned(),
        prewarm: false,
        sampler: Vec::new(),
        lane_tree: String::new(),
        apply: Vec::new(),
    }
}

/// The fixture's clone with a guard wrapper, a Makefile of two targets and three tasks of feature 9001.
fn world(tag: &str) -> (l7r_shared::tempdir::TempDir, PathBuf) {
    let dir = repo(tag);
    let root = root_of(&dir);
    std::fs::create_dir_all(root.join("scripts/hooks")).unwrap();
    write_executable(
        &root.join("scripts/hooks/l7r-guard.sh"),
        "#!/bin/sh\nexit 0\n",
    );
    put(
        &root,
        "Makefile",
        "X := 1\nbuilder-tree:\n\t@echo\nland: export A = 1\nland:\n",
    );
    put(&root, "specs/9001-x/tasks.md", TASKS);
    put(&root, "specs/9001-x/tasks-done.md", "- [x] T08 archived\n");
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "the fixture"]);
    (dir, root)
}

fn pool_of(root: &Path) -> Vec<builder_pool::Tree> {
    builder_pool::read(&root.join(".git"))
}

#[test]
fn a_brief_is_sized_before_any_tree_is_taken() {
    let (dir, root) = world("brief-sizing");
    let e = env(&dir);
    let ask = |a: &[&str]| run(&words(a), &root, &e, "");
    for a in [
        &[][..],
        &["T01"],
        &["T01", "9001"],
        &["", "9001", "fix"],
        &["T01", "", "fix"],
    ] {
        let r = ask(a);
        assert_eq!(r.code, 2);
        assert!(r.stderr.starts_with("usage: make builder-brief T=<task(s)> F=<feature> KIND=fix|measurement|build-half|closing-half"), "{}", r.stderr);
    }
    for (a, said) in [
        (&["T01", "9001", "mechanism-build"][..], "KIND=mechanism-build is none of fix, measurement, build-half, closing-half\nusage: "),
        (&["T01", "9001", "fix", "0"], "JOBS is a count from 1 to 3\nusage: "),
        (&["T01", "9001", "fix", "many"], "JOBS is a count from 1 to 3\n"),
        (&["T01", "9001", "fix", "4"], "JOBS=4: a brief holds at most 3 jobs"),
        (&["T01", "9001", "fix", "4"], "  make builder-brief T=T01 F=9001 KIND=fix JOBS=3\n  make builder-brief T=T01 F=9001 KIND=fix JOBS=1   (after the first reports"),
        (&["T01", "9001", "measurement"], "sized by the THINGS MEASURED as well as its jobs"),
        (&["T01", "9001", "measurement", "1", "some"], "  make builder-brief T=T01 F=9001 KIND=measurement MEASURES=<n>   (at most 6)\n"),
        (&["T01", "9001", "measurement", "", "15"], "MEASURES=15: a measurement brief measures at most 6 things (a GUESS knob"),
        (&["T01", "9001", "measurement", "", "15"], "  make builder-brief T=T01 F=9001 KIND=measurement MEASURES=6\n  make builder-brief T=T01 F=9001 KIND=measurement MEASURES=9   (the rest"),
        (&["T01", "9999", "fix"], "no specs/9999-* in "),
        (&["T07", "9001", "fix"], "specs/9001-x/tasks.md has no task T07 (make task-add F=9001 TITLE=\"...\" files one)\n"),
        // a bundle is sized as one brief: each task's line read, a mechanism among them still two builders
        (&["T01,T07", "9001", "fix"], "tasks.md has no task T07 ("),
        (&["T01 T02", "9001-x", "fix"], "T02's line names a new mechanism (\"a guard refuses\"), which is TWO builders from the start"),
        (&["T01,T02", "9001", "fix"], "  make builder-brief T=T01,T02 F=9001 KIND=build-half   (builds"),
        (&["T01,T09", "9001", "measurement", "", "7"], "  make builder-brief T=T01,T09 F=9001 KIND=measurement MEASURES=6\n"),
    ] {
        let r = ask(a);
        assert_eq!((r.code, r.stdout.as_str()), (2, ""), "{a:?}");
        assert!(r.stderr.starts_with("builder-brief: refused - ") && r.stderr.contains(said), "{}", r.stderr);
    }
    // a mechanism briefed as one fix: two builders, named; the build half, and the fix on its escape, are sized
    let one = ask(&["T02", "9001", "fix"]);
    assert_eq!(one.code, 2);
    assert!(one.stderr.contains("T02's line names a new mechanism (\"a guard refuses\"), which is TWO builders from the start"), "{}", one.stderr);
    assert!(one.stderr.contains("  make builder-brief T=T02 F=9001 KIND=build-half   (builds and tests, ends at a handoff)\n  make builder-brief T=T02 F=9001 KIND=closing-half   (after it reports"), "{}", one.stderr);
    assert!(one
        .stderr
        .contains("SIZING_OK=\"<reason, two words or more>\""));
    assert_eq!(
        run(&words(&["T02", "9001", "fix"]), &root, &e, "short").code,
        2
    );
    // nothing above took a tree
    assert!(pool_of(&root).is_empty());
    let outside = dir.join("outside");
    std::fs::create_dir_all(&outside).unwrap();
    let lost = run(&words(&["T01", "9001", "fix"]), &outside, &e, "");
    assert_eq!(
        (lost.code, lost.stderr.as_str()),
        (2, "builder-brief: not in a git repository\n")
    );
    let escaped = run(
        &words(&["T02", "9001", "fix"]),
        &root,
        &e,
        "the line names the guard it repairs",
    );
    assert_eq!(escaped.code, 0, "{}", escaped.stderr);
    assert!(escaped
        .stderr
        .contains("briefed as one fix on SIZING_OK: the line names the guard it repairs\n"),);
    // the pool's own refusal is this command's: the cap of one is held by T02
    let full = ask(&["T01", "9001", "fix"]);
    assert_eq!((full.code, full.stdout.as_str()), (2, ""));
    assert!(full.stderr.contains("the pool is at its cap of 1"),);
}

#[test]
fn each_kind_s_block_opens_with_its_marker_and_stays_short() {
    let (dir, root) = world("brief-block");
    let e = env(&dir);
    let tree = dir.join("repo-b1");
    let handoff = root.join(".git/l7r-handoffs/T01-build.md");
    let ask = |a: &[&str]| {
        let r = run(&words(a), &root, &e, "");
        assert_eq!(r.code, 0, "{}", r.stderr);
        // shorter than the block `agent-prefix-hooks` refuses a repeat of (its `SHARED`, 2,000 characters), counted with the
        // fixture's temp directory read as the clones directory a real brief names: the fixture's paths under `TempDir`'s own
        // subdirectory (462 T371) are longer than a real tree's, which is not what the cap is about
        let n = r
            .stdout
            .replace(&*dir.to_string_lossy(), "/diagram/.clones")
            .chars()
            .count();
        assert!(n < 2000, "{n}");
        // `context_cap_hooks/split.rs` knows a code builder by this line
        assert!(r.stdout.lines().any(|l| l.starts_with("STOP POINT (")),);
        // 461 T43, T44: every kind hands in itself, through `make builder-done` alone, after what its stop point ends at
        let end = "read at your stop point. Never land or push; never rewrite history.\n";
        assert!(r.stdout.ends_with(end), "{}", r.stdout);
        let after = match a[2] {
            "build-half" => "the handoff written",
            "measurement" => "the record written",
            _ => "review CLEAR",
        };
        let line = format!(
            "HAND IN last, {after}, your one commit: `make builder-done T={} F=9001 MSG=",
            a[0]
        );
        assert!(r.stdout.contains(&line), "{}", r.stdout);
        r
    };
    // the hand-in line (461 T43, US2: "A refusal a builder can answer is answered by the builder that has the context")
    let hand_in = "HAND IN last, review CLEAR, your one commit: `make builder-done T=T01 F=9001 MSG=\"<subject>\"` [GUARD=\"<why>\"]. A conflict: resolve, `git add`, rerun; a refusal: answer, rerun, or report a claims one verbatim.\n";
    let marker = |kind: &str, jobs: usize| Marker {
        feature: "9001".to_owned(),
        task: "T01".to_owned(),
        kind: kind.to_owned(),
        jobs,
        tree: tree.clone(),
    };
    let fix = ask(&["T01", "specs/9001-x/", "fix"]);
    assert!(fix.stderr.contains("is NEW and held by 9001 T01: COLD"),);
    assert_eq!(
        fix.stdout.lines().next(),
        Some(marker("fix", 1).line().as_str())
    );
    assert_eq!(parse(&fix.stdout), Some(marker("fix", 1)));
    let t = tree.display();
    for words in [
        "\nBlocks: none\n".to_owned(),
        format!("Tree (the pool's, held for T01): {t} - `cd` into it in every command, work ONLY there, make or remove no worktree. `export SPECIFY_FEATURE=9001-x SPECIFY_FEATURE_DIRECTORY=specs/9001-x`\n"),
        "Read scripts/container/builder-brief.md first: the rules behind this block. Prefix scratch files `t01-`.\n".to_owned(),
        // 451 T502: the block names the plan read (T501), so a builder takes it without opening the rules file
        "Read your plan sections with `make plan-section T=T01`, never by grep, sed or a Read over plan.md or plan-done.md.\n".to_owned(),
        "STOP POINT (fix): red-first - the test failing on the old code, its counts reported - then the plan section, `make decide`, the plan review (`make plan-delta F=9001`) and `make claims-triage`; you dispatch no claims-triage or impl-drift agent.\n".to_owned(),
        "CHECKS, the first tier only: `make builder-checks CRATE=\"<the crates you changed>\"` and a changed guard's own suite - not closing-checks, static, hooks-test or a coverage run (the one exception: a brief whose JOB is the coverage repair of a red batch gate runs `make crate-checks` on the crates it names).\n".to_owned(),
        "Test every new line as if coverage ran (each closure counts); an assertion's message stays on its own line or is left out.\n".to_owned(),
        "FILE what you find and leave, from your tree: `make task-add F=9001 TITLE=\"<title, paths, figures>\"`; its id goes in your report's CANDIDATES.\n".to_owned(),
        "Report in the fixed format of scripts/container/builder-report-format.md, read at your stop point.".to_owned(),
        hand_in.to_owned(),
    ] {
        assert!(fix.stdout.contains(&words), "{words}\n{}", fix.stdout);
    }
    assert!(!fix.stdout.contains("ORDER:") && !fix.stdout.contains("LOADS"));
    // the tree the task already holds, every option given
    let build = ask(&[
        "T01",
        "9001",
        "build-half",
        "3",
        "",
        "rust/guard rust/gate/crates/task",
        "9001 T02",
        "1",
    ]);
    assert!(build.stderr.contains("9001 T01 already holds it"),);
    assert_eq!(parse(&build.stdout), Some(marker("build-half", 3)));
    for words in [
        "\nBlocks: 9001 T02\n".to_owned(),
        "ORDER: the 3 jobs in this brief's order; if they will not fit, finish one whole, stop, report the rest as not started.\n".to_owned(),
        "This task LOADS the machine: it runs ALONE in its batch, bounded.\n".to_owned(),
        format!("STOP POINT (build half): build and test, red-first, then END at a handoff, {}, by about 200k:", handoff.display()),
        "No plan section, `make decide`, plan review or claims step.\n".to_owned(),
        "`make builder-checks CRATE=\"rust/guard rust/gate/crates/task\"`".to_owned(),
    ] {
        assert!(build.stdout.contains(&words), "{words}\n{}", build.stdout);
    }
    // the closing half reads the handoff first, and is told when none is written yet
    let early = ask(&["T01", "9001", "closing-half", "", "", "rust/guard"]);
    assert!(early.stderr.contains(&format!(
        "NOTE - the build half's handoff {} is not written yet",
        handoff.display()
    )),);
    put(&root, ".git/l7r-handoffs/T01-build.md", "built\n");
    let closing = ask(&["T01", "9001", "closing-half", "", "", "rust/guard"]);
    assert!(!closing.stderr.contains("NOTE"), "{}", closing.stderr);
    assert!(closing.stdout.contains(&format!("STOP POINT (closing half): read {} first. Then the tests it lists as owed, the plan section,", handoff.display())), "{}", closing.stdout);
    assert!(closing.stdout.contains(hand_in), "{}", closing.stdout);
    // TWO TIERS (451 T308): the closing half runs the first tier like every kind, and no coverage - the second tier's alone
    // ...its exception, a batch gate's coverage repair, a fix's alone (461 T44)
    assert!(closing.stdout.contains("CHECKS, the first tier only: `make builder-checks CRATE=\"rust/guard\"` and a changed guard's own suite - not closing-checks, static, hooks-test or a coverage run.\n"), "{}", closing.stdout);
    let was = ["real coverage", "(tests, lint, format, coverage)"];
    assert!(!was.iter().any(|w| closing.stdout.contains(w)));
    // a measurement changes no source and is told of no test
    let measured = ask(&["T01", "9001", "measurement", "2", "6"]);
    assert_eq!(parse(&measured.stdout), Some(marker("measurement", 2)));
    assert!(measured.stdout.contains("STOP POINT (measurement, 6 things): change NO source file. Write the record (commands, figures, units) under dev/measurements/, file each lever you price, and report; no plan section.\nCHECKS: none - you change no source.\nHAND IN last, the record written, your one commit: `make builder-done T=T01 F=9001 MSG="), "{}", measured.stdout);
    assert!(!measured.stdout.contains("as if coverage ran"));
}

#[test]
fn a_task_s_line_is_found_open_or_archived() {
    let all = "# Tasks\n- [ ] T1 one\n  - [x] T2 two\n- [ ] T10 ten\nT3 loose\n- [\n";
    assert_eq!(task_line(all, "T2").as_deref(), Some("  - [x] T2 two"));
    assert_eq!(task_line(all, "T10").as_deref(), Some("- [ ] T10 ten"));
    assert_eq!((task_line(all, "T3"), task_line(all, "T")), (None, None));
}

#[test]
fn a_feature_is_found_by_its_number_and_an_archived_task_by_its_line() {
    let (dir, root) = world("brief-feature");
    let e = env(&dir);
    // a file named like a feature, and a feature directory that is the number alone
    put(&root, "specs/9002-notes", "a file\n");
    put(&root, "specs/9003/tasks.md", "- [ ] T01 the only one\n");
    let file = run(&words(&["T01", "9002", "fix"]), &root, &e, "");
    assert!(file.stderr.contains("no specs/9002-* in "),);
    let bare = run(&words(&["T01", "9003", "fix"]), &root, &e, "");
    assert_eq!(bare.code, 0, "{}", bare.stderr);
    assert!(bare
        .stdout
        .contains("SPECIFY_FEATURE=9003 SPECIFY_FEATURE_DIRECTORY=specs/9003`"));
    // an archived task still has a line (a fix after its landing); the cap of one is held, so the pool refuses
    let done = run(&words(&["T08", "9001", "fix"]), &root, &e, "");
    assert!(done.stderr.contains("the pool is at its cap of 1"),);
    // the binary's verb
    let said = crate::cli("builder-brief", &[], &root);
    assert!(said.stderr.starts_with("usage: make builder-brief"));
}

#[test]
fn a_bundle_is_briefed_as_one_builder_on_the_tree_held_for_it() {
    let (dir, root) = world("brief-bundle");
    let mut e = env(&dir);
    e.cap = 2;
    let tree = dir.join("repo-b1");
    // spaces or commas between the tasks: the marker names them joined by commas, the pool holds the tree for both
    let both = run(&words(&["T01 T09", "9001", "build-half"]), &root, &e, "");
    assert_eq!(both.code, 0, "{}", both.stderr);
    let marker = parse(&both.stdout).unwrap();
    assert_eq!((marker.task.as_str(), &marker.tree), ("T01,T09", &tree));
    assert_eq!(pool_of(&root)[0].tasks, ["T01", "T09"]);
    let handoff = root.join(".git/l7r-handoffs/T01-T09-build.md");
    for words in [
        "Tree (the pool's, held for T01,T09): ".to_owned(),
        "Prefix scratch files `t01-`.\n".to_owned(),
        format!("then END at a handoff, {}, by", handoff.display()),
    ] {
        assert!(both.stdout.contains(&words), "{words}\n{}", both.stdout);
    }
    // the bundle again, and one task of it alone, are handed the tree they hold
    for t in ["T09,T01", "T09"] {
        let again = run(&words(&[t, "9001", "closing-half"]), &root, &e, "");
        assert_eq!(again.code, 0, "{}", again.stderr);
        assert_eq!(parse(&again.stdout).map(|m| m.tree), Some(tree.clone()));
    }
    // a task the hold does not name, bundled with one it does: the pool would hand the held tree out, and the guard refuse its block
    let wider = run(&words(&["T01,T08", "9001", "fix"]), &root, &e, "");
    assert_eq!((wider.code, wider.stdout.as_str()), (2, ""));
    let said = format!("builder-brief: refused - {} is held by 9001 T01,T09, which does not hold T08: a bundle is one hold, taken whole. Brief what holds it, and T08 in a tree of its own:\n  make builder-brief T=T01,T09 F=9001 KIND=fix\n  make builder-brief T=T08 F=9001 KIND=fix\n", tree.display());
    assert_eq!(wider.stderr, said);
    assert_eq!(pool_of(&root).len(), 1);
}

/// THE ENTRY A BUILDER SERVES IS NAMED (451 T313's review, round 1, the T416 case): `ENTRY=` is written on a `brief` line of the
/// pool's log beside the take, a successor briefed by hand without it inherits the entry its tree was briefed for, and `make
/// builder-done` writes that entry on its `done` line; a word that is no entry's number is refused before any tree is taken.
#[test]
fn the_entry_a_brief_serves_is_on_the_log_and_on_its_done_line() {
    let (dir, root) = world("brief-entry");
    let e = env(&dir);
    let at = |entry: &str| words(&["T01", "9001", "closing-half", "", "", "", "", "", entry]);
    let bad = run(&at("two"), &root, &e, "");
    assert_eq!(bad.code, 2);
    assert!(
        bad.stderr.contains("ENTRY=two is no entry's number"),
        "{}",
        bad.stderr
    );
    assert!(pool_of(&root).iter().all(builder_pool::Tree::free));
    let took = run(&at("2"), &root, &e, "");
    assert_eq!(took.code, 0, "{}", took.stderr);
    let tree = dir.join("repo-b1");
    let log = || std::fs::read_to_string(root.join(".git/builder-pool.log")).unwrap();
    let brief = format!("{{\"utc\":\"2026-11-26T12:00:00Z\",\"event\":\"brief\",\"tree\":\"{}\",\"detail\":\"9001 T01\",\"kind\":\"closing-half\",\"entry\":2}}", tree.display());
    assert!(log().contains(&brief), "{}", log());
    // the successor at its cap, briefed by hand with no ENTRY=: its brief line names none, and its done line still names 2
    let again = run(&at(""), &root, &e, "");
    assert_eq!(again.code, 0, "{}", again.stderr);
    put(&tree, "notes/a.md", "one\n");
    let done = crate::builder_done::run(
        &words(&["T01", "9001"]),
        &root,
        &e,
        "9001 T01: the closing half",
        "",
    );
    assert_eq!(done.code, 0, "{}", done.stderr);
    let last = log()
        .lines()
        .rfind(|l| l.contains("\"event\":\"done\""))
        .unwrap()
        .to_owned();
    assert!(last.contains("\"entry\":2"), "{last}");
    // the next take of the tree, briefed for no entry at all: its done line names none (T01's entry is not inherited past the
    // take), and the count reads it, as before
    let plain = run(
        &words(&["T02", "9001", "build-half", "", "", "", "", "", ""]),
        &root,
        &e,
        "",
    );
    assert_eq!(plain.code, 0, "{}", plain.stderr);
    put(&tree, "notes/b.md", "two\n");
    let done = crate::builder_done::run(&words(&["T02", "9001"]), &root, &e, "9001 T02: plain", "");
    assert_eq!(done.code, 0, "{}", done.stderr);
    let last = log()
        .lines()
        .rfind(|l| l.contains("\"event\":\"done\""))
        .unwrap()
        .to_owned();
    assert!(!last.contains("\"entry\""), "{last}");
}
