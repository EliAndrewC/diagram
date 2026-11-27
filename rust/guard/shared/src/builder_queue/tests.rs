//! The builders' queue (feature 451 T313, T395, T297): a line read or refused by its number, each state computed, the overlap by path
//! prefix and crate, a bundle, `alone` both ways, the next entry and the idle rule.

use std::path::{Path, PathBuf};

use super::*;
use crate::tempdir::TempDir;

fn tree(path: &str, feature: &str, tasks: &[&str]) -> Tree {
    Tree {
        tree: PathBuf::from(path),
        feature: feature.to_owned(),
        tasks: tasks.iter().map(|t| (*t).to_owned()).collect(),
        since: String::new(),
    }
}

fn set(tasks: &[&str]) -> BTreeSet<String> {
    tasks.iter().map(|t| (*t).to_owned()).collect()
}

fn facts_of(
    ticked: &[&str],
    held: Vec<Tree>,
    dones: &[(&str, usize)],
    uncarried: &[&str],
) -> Facts {
    Facts {
        key: "451".to_owned(),
        ticked: set(ticked),
        held,
        dones: dones.iter().map(|(t, n)| ((*t).to_owned(), *n)).collect(),
        uncarried: set(uncarried),
        ..Facts::default()
    }
}

fn put(path: &Path, text: &str) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn git(root: &Path, args: &[&str]) {
    let ran = std::process::Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["-c", "user.name=t", "-c", "user.email=t@t"])
        .args(args)
        .output()
        .unwrap();
    assert!(ran.status.success(), "{args:?}");
}

const QUEUE: &str = "# the queue\n\nT1 fix crates=rust/guard files=- note=the first, with files=none\nT2,T3 build-half jobs=2 crates=rust/gate/crates/task/ files=Makefile,docs/guards.md waits=T1,GM,alone\nT4\tmeasurement measures=4 load=1 files=-\n";

#[test]
fn a_line_is_read_field_by_field_and_written_back_as_it_was_read() {
    let q = parse(QUEUE).unwrap();
    assert_eq!(q.len(), 3);
    assert_eq!(
        (q[0].line, q[0].name(), q[0].kind.as_str()),
        (3, "T1".to_owned(), "fix")
    );
    assert_eq!(q[0].crates, vec!["rust/guard"]);
    assert!(q[0].files.is_empty() && q[0].waits.is_empty() && !q[0].gm && !q[0].alone);
    assert_eq!(q[0].note, "the first, with files=none");
    assert_eq!(q[1].tasks, vec!["T2", "T3"]);
    assert_eq!(q[1].crates, vec!["rust/gate/crates/task"]);
    assert_eq!(q[1].files, vec!["Makefile", "docs/guards.md"]);
    assert_eq!(
        (q[1].waits.clone(), q[1].gm, q[1].alone),
        (vec!["T1".to_owned()], true, true)
    );
    assert_eq!(
        (q[2].measures.as_str(), q[2].load, q[2].line),
        ("4", true, 5)
    );
    // each line written back reads as the same entry
    for e in &q {
        let again = parse(&e.text()).unwrap();
        assert_eq!(
            Entry {
                line: e.line,
                ..again[0].clone()
            },
            *e
        );
    }
    assert_eq!(
        q[0].text(),
        "T1 fix crates=rust/guard files=- note=the first, with files=none"
    );
    assert_eq!(
        q[1].text(),
        "T2,T3 build-half jobs=2 crates=rust/gate/crates/task files=Makefile,docs/guards.md waits=T1,GM,alone"
    );
    assert_eq!(
        q[2].text(),
        "T4 measurement measures=4 load=1 crates=- files=-"
    );
}

#[test]
fn an_entry_s_command_is_the_brief_it_asks_for() {
    let q = parse(QUEUE).unwrap();
    assert_eq!(
        q[0].command("451"),
        "make builder-brief T=T1 F=451 KIND=fix CRATE=\"rust/guard\" ENTRY=1"
    );
    assert_eq!(
        q[1].command("451"),
        "make builder-brief T=T2,T3 F=451 KIND=build-half JOBS=2 CRATE=\"rust/gate/crates/task\" ENTRY=1"
    );
    assert_eq!(
        q[2].command("9"),
        "make builder-brief T=T4 F=9 KIND=measurement MEASURES=4 LOAD=1 ENTRY=1"
    );
}

#[test]
fn a_malformed_line_is_an_error_naming_the_line() {
    let bad = [
        ("T1 fix", "2 field(s) found, at least 3 expected"),
        ("T1", "1 field(s) found"),
        ("task1 fix files=-", "`task1` is no task or bundle"),
        ("T fix files=-", "`T` is no task or bundle"),
        (", fix files=-", "`,` is no task or bundle"),
        (
            "T1 repair files=-",
            "`repair` is no kind (fix, measurement, build-half, closing-half)",
        ),
        ("T1 fix files", "`files` is no key=value field"),
        ("T1 fix files=- files=a", "`files=` is given twice"),
        ("T1 fix files=- jobs=4", "`jobs=4` is no field of an entry"),
        (
            "T1 fix files=- measures=many",
            "`measures=many` is no field",
        ),
        ("T1 fix files=- load=yes", "`load=yes` is no field"),
        (
            "T1 fix files=- waits=T2,soon",
            "`waits=T2,soon` is no field",
        ),
        ("T1 fix files=- after=T2", "`after=T2` is no field"),
        ("T1 fix jobs=1", "names neither crates= nor files="),
        ("T1 measurement files=-", "a measurement names measures="),
    ];
    for (line, why) in bad {
        let said = parse(&format!("# head\n{line}\n")).unwrap_err();
        assert!(said.starts_with("queue.txt line 2: "), "{said}");
        assert!(said.contains(why), "{line}: {said}");
        assert!(said.ends_with(line), "{said}");
    }
    // every bad line is named, not the first alone
    let two = parse("T1 fix\nT2 fix files=-\nT3 mend files=-\n").unwrap_err();
    assert_eq!(two.lines().count(), 2);
    assert!(two.contains("line 1: ") && two.contains("line 3: "));
}

#[test]
fn two_entries_overlap_by_crate_and_by_path_prefix() {
    let q = parse("T1 fix crates=rust/guard files=Makefile\nT2 fix files=rust/guard/src/lib.rs\nT3 fix crates=rust/guardian files=docs/\nT4 fix files=docs/guards.md,Makefile\nT5 measurement measures=1 files=-\n").unwrap();
    // a crate holds the files under it, either way round, and the shorter path is the one named
    assert_eq!(overlap(&q[0], &q[1]), Some("rust/guard".to_owned()));
    assert_eq!(overlap(&q[1], &q[0]), Some("rust/guard".to_owned()));
    // a name that only opens with another's is no prefix
    assert_eq!(overlap(&q[0], &q[2]), None);
    assert_eq!(overlap(&q[1], &q[2]), None);
    // the same file, and a directory's prefix
    assert_eq!(overlap(&q[0], &q[3]), Some("Makefile".to_owned()));
    assert_eq!(overlap(&q[3], &q[2]), Some("docs".to_owned()));
    // no files, no overlap
    assert_eq!(overlap(&q[4], &q[0]), None);
    assert_eq!(overlap(&q[0], &q[4]), None);
}

#[test]
fn each_state_is_computed() {
    let q = parse("T1 fix files=a\nT2 fix files=b\nT3 fix files=c waits=T1,T2\nT4 fix files=d waits=GM\nT5 fix files=e waits=T4\nT6,T7 fix files=f\nT8 fix files=g waits=T9\nT10 fix files=h waits=T11\n").unwrap();
    let held = vec![tree("/p/t1", "451", &["T2"]), tree("/p/t2", "9", &["T3"])];
    let f = facts_of(&["T1", "T6"], held, &[("T9", 1), ("T11", 1)], &["T11"]);
    let s = states(&q, &f);
    assert_eq!(s[0], State::Landed);
    assert_eq!(s[1], State::InFlight(PathBuf::from("/p/t1")));
    // a wait ends at its task's tick; another feature's tree holding the same id is not this task's
    assert_eq!(s[2], State::Waiting("T2".to_owned()));
    assert_eq!(s[3], State::Waiting("the GM".to_owned()));
    assert_eq!(s[4], State::Waiting("T4".to_owned()));
    // a bundle is landed only when each of its tasks is
    assert_eq!(s[5], State::Ready);
    // a wait also ends when its task's done commit is carried, and not before
    assert_eq!(s[6], State::Ready);
    assert_eq!(s[7], State::Waiting("T11".to_owned()));
    let all = states(
        &q,
        &facts_of(&["T1", "T2", "T6", "T7"], Vec::new(), &[], &[]),
    );
    assert_eq!((&all[2], &all[5]), (&State::Ready, &State::Landed));
}

#[test]
fn a_task_just_done_and_the_two_halves_of_one_task_are_never_ready_too_soon() {
    let q = parse("T1 build-half files=a\nT1 closing-half files=a\nT2 fix files=b\n").unwrap();
    let t1 = || vec![tree("/p/t1", "451", &["T1"])];
    // the build half in flight: the closing half waits on the entry before it, though the tree is held for its task
    let s = states(&q, &facts_of(&[], t1(), &[], &[]));
    assert_eq!(s[0], State::InFlight(PathBuf::from("/p/t1")));
    assert_eq!(
        s[1],
        State::Waiting("T1's earlier entry, line 1".to_owned())
    );
    // neither handed out: the same
    let s = states(&q, &facts_of(&[], Vec::new(), &[], &[]));
    assert_eq!(
        (&s[0], &s[1]),
        (
            &State::Ready,
            &State::Waiting("T1's earlier entry, line 1".to_owned())
        )
    );
    // the build half done, its commit not carried: built, and the closing half waits on the carry
    let s = states(&q, &facts_of(&[], Vec::new(), &[("T1", 1)], &["T1"]));
    assert_eq!(
        s[0],
        State::Built("the carry of T1's done commit owed".to_owned())
    );
    assert_eq!(
        s[1],
        State::Waiting("the carry of T1's done commit (make builder-trees)".to_owned())
    );
    // carried: the closing half is ready, then in flight, then built
    let s = states(&q, &facts_of(&[], Vec::new(), &[("T1", 1)], &[]));
    assert_eq!(
        (&s[0], &s[1]),
        (
            &State::Built("carried, its landing owed".to_owned()),
            &State::Ready
        )
    );
    let s = states(&q, &facts_of(&[], t1(), &[("T1", 1)], &[]));
    assert_eq!(s[1], State::InFlight(PathBuf::from("/p/t1")));
    let s = states(&q, &facts_of(&[], Vec::new(), &[("T1", 2)], &["T1"]));
    assert_eq!(
        s[1],
        State::Built("the carry of T1's done commit owed".to_owned())
    );
    // a task with one entry, just done: built, never ready again while its box is open
    let s = states(&q, &facts_of(&[], Vec::new(), &[("T2", 1)], &[]));
    assert_eq!(s[2], State::Built("carried, its landing owed".to_owned()));
}

#[test]
fn the_next_entry_is_the_first_ready_one_overlapping_nothing_in_flight() {
    let q = parse("T1 fix crates=rust/guard\nT2 fix files=rust/guard/src/lib.rs\nT3 fix files=docs/a.md waits=alone\nT4 fix files=docs/b.md\n").unwrap();
    let f = facts_of(
        &[],
        vec![tree("/p/t1", "451", &["T1"]), tree("/p/t2", "9", &["T7"])],
        &[],
        &[],
    );
    let n = next(&q, &states(&q, &f), &f);
    assert_eq!(n.pick, Some(3));
    assert_eq!(
        n.skipped,
        vec![
            (1, "it overlaps T1 in flight at rust/guard".to_owned()),
            (2, "it runs alone, and 2 tree(s) are held".to_owned()),
        ]
    );
    // a held tree whose task the queue does not list is named: its files are unknown
    assert_eq!(n.unchecked, vec!["9 T7".to_owned()]);
    assert_eq!(n.none, "");
    // nothing held: the first entry
    let f = facts_of(&[], Vec::new(), &[], &[]);
    let n = next(&q, &states(&q, &f), &f);
    assert_eq!(
        (n.pick, n.skipped.len(), n.unchecked.len()),
        (Some(0), 0, 0)
    );
    // an alone entry is taken when nothing is held
    let f = facts_of(&["T1", "T2"], Vec::new(), &[], &[]);
    assert_eq!(next(&q, &states(&q, &f), &f).pick, Some(2));
}

#[test]
fn an_alone_task_in_flight_holds_every_other_back_and_no_ready_entry_says_why() {
    let q = parse("T1 fix files=a waits=alone\nT2 fix files=b\nT3 fix files=c waits=GM\n").unwrap();
    let f = facts_of(&[], vec![tree("/p/t1", "451", &["T1"])], &[], &[]);
    let n = next(&q, &states(&q, &f), &f);
    assert_eq!(n.pick, None);
    assert_eq!(n.skipped, vec![(1, "T1 runs alone".to_owned())]);
    assert_eq!(n.none, "every READY entry is held back by a task in flight");
    // every open entry waiting
    let f = facts_of(&["T1", "T2"], Vec::new(), &[], &[]);
    let n = next(&q, &states(&q, &f), &f);
    assert_eq!(
        (n.pick, n.none.as_str()),
        (None, "every open entry waits: T3 on the GM")
    );
    // nothing open
    let f = facts_of(&["T1", "T2", "T3"], Vec::new(), &[], &[]);
    let n = next(&q, &states(&q, &f), &f);
    assert_eq!(
        n.none,
        "the queue is empty: each entry is landed, built or in flight"
    );
    assert_eq!(
        next(&[], &[], &f).none,
        "the queue is empty: each entry is landed, built or in flight"
    );
}

/// A clone with a queue, a pool of two trees and a done commit kept under its ref.
fn world(tag: &str, queue: &str, pool: &str) -> (TempDir, PathBuf) {
    let dir = TempDir::new(&format!("builder-queue-{tag}"));
    let clone = dir.join("c");
    std::fs::create_dir_all(&clone).unwrap();
    git(&clone, &["init", "-q"]);
    put(
        &clone.join("specs/451-x/tasks.md"),
        "- [x] T1 landed\n  - [X] T2 landed, indented\n- [ ] T3 open\nT4 no box\n- [x]\n",
    );
    put(&clone.join("specs/451-x/queue.txt"), queue);
    put(
        &clone.join("specs/9-none/tasks.md"),
        "- [ ] T1 no queue here\n",
    );
    let done = clone.join("specs/451-x/tasks-done.md");
    put(&done, "- [x] T9 archived by its tick\n");
    std::fs::create_dir_all(dir.join("c-b1")).unwrap();
    let pool = pool.replace("<D>", &dir.to_string_lossy());
    put(&clone.join(".git/builder-pool.json"), &pool);
    (dir, clone)
}

const POOL: &str = r#"{"trees": [{"tree": "<D>/c-b0", "feature": "451", "tasks": ["T5"], "since": ""}, {"tree": "<D>/c-b1", "feature": "", "tasks": [], "since": ""}]}"#;

#[test]
fn the_facts_are_read_from_the_clone() {
    let (_dir, clone) = world("facts", "T3 fix files=a\n", POOL);
    let common = clone.join(".git");
    git(&clone, &["commit", "-q", "--allow-empty", "-m", "one"]);
    git(&clone, &["update-ref", "refs/l7r/done/451-T6", "HEAD"]);
    git(&clone, &["update-ref", "refs/l7r/done/9-T8", "HEAD"]);
    put(
        &common.join(LOG),
        "{\"event\":\"take\",\"detail\":\"451 T6\"}\nnot json\n{\"event\":\"done\",\"detail\":\"451 T6,T7\"}\n{\"event\":\"done\",\"detail\":\"451 T6\"}\n{\"event\":\"done\",\"detail\":\"9 T8\"}\n{\"event\":\"done\"}\n",
    );
    let trees = crate::builder_pool::read(&common);
    let f = facts(&clone, &common, &clone.join("specs/451-x"), &trees);
    assert_eq!(f.key, "451");
    // a box the tick archived is ticked too
    assert_eq!(f.ticked, set(&["T1", "T2", "T9"]));
    assert_eq!(f.held.len(), 1);
    assert_eq!(f.held[0].tasks, vec!["T5"]);
    assert_eq!(
        f.dones,
        [("T6".to_owned(), 2), ("T7".to_owned(), 1)]
            .into_iter()
            .collect()
    );
    assert_eq!(f.uncarried, set(&["T6"]));
    assert_eq!(queues(&clone), vec![clone.join("specs/451-x")]);
    assert!(queues(&clone.join("none")).is_empty());
    let b = board(&clone, &common, &clone.join("specs/451-x"), &trees).unwrap();
    assert_eq!(
        (b.key.as_str(), b.entries.len(), b.next.pick),
        ("451", 1, Some(0))
    );
    assert_eq!(b.states, vec![State::Ready]);
    assert_eq!(b.facts, f);
    // a queue that cannot be read, and one with a bad line
    assert!(board(&clone, &common, &clone.join("specs/9-none"), &trees)
        .unwrap_err()
        .contains("queue.txt"));
    put(&clone.join("specs/451-x/queue.txt"), "T3 fix\n");
    let bad = board(&clone, &common, &clone.join("specs/451-x"), &trees).unwrap_err();
    let named = bad.contains("specs/451-x/queue.txt line 1: 2 field(s) found");
    assert!(named, "{bad}");
}

#[test]
fn the_builder_count_is_a_knob() {
    assert_eq!(builders(), BUILDERS);
    crate::env::set("L7R_BUILDERS", "2");
    assert_eq!(builders(), 2);
    crate::env::set("L7R_BUILDERS", "many");
    assert_eq!(builders(), 3);
    crate::env::unset("L7R_BUILDERS");
}

#[test]
fn a_free_tree_with_a_ready_entry_under_the_count_is_idle() {
    let (dir, clone) = world(
        "idle",
        "T1 fix files=a\nT3 fix jobs=1 crates=rust/guard files=a\n",
        POOL,
    );
    let idles = Idle {
        tree: dir.join("c-b1"),
        tasks: "451 T3".to_owned(),
        command: "make builder-brief T=T3 F=451 KIND=fix JOBS=1 CRATE=\"rust/guard\" ENTRY=1"
            .to_owned(),
        unlisted: Vec::new(),
    };
    assert_eq!(idle(&clone, 3), Verdict::Idle(idles.clone()));
    // another feature's file of the same name that is no builders' queue (a page session's, as features 269 and 280 hold) does
    // not hide this one: the readable queue's entry is still reached
    put(
        &clone.join("specs/269-pages/queue.txt"),
        "/c/briefs/h1-write.md then:/c/briefs/h1-checks.sh\n",
    );
    assert_eq!(idle(&clone, 3), Verdict::Idle(idles));
    // the count reached: one tree is held
    assert_eq!(idle(&clone, 1), Verdict::Quiet);
    // the free tree gone from disk
    std::fs::remove_dir(dir.join("c-b1")).unwrap();
    assert_eq!(idle(&clone, 3), Verdict::Quiet);
}

#[test]
fn no_pool_no_free_tree_no_ready_entry_and_an_unread_queue_are_not_idle() {
    // no pool: not this feature's coordinator
    let (_d, clone) = world("idle-none", "T3 fix files=a\n", "{}");
    assert_eq!(idle(&clone, 3), Verdict::Quiet);
    // every tree held
    let full = POOL.replace("\"tasks\": []", "\"tasks\": [\"T9\"]");
    let (_d, clone) = world("idle-full", "T3 fix files=a\n", &full);
    assert_eq!(idle(&clone, 3), Verdict::Quiet);
    // the one open entry waits on the GM
    let (_d, clone) = world("idle-gm", "T3 fix files=a waits=GM\n", POOL);
    assert_eq!(idle(&clone, 3), Verdict::Quiet);
    // the one ready entry runs alone, and a tree is held
    let (_d, clone) = world("idle-alone", "T3 fix files=a waits=alone\n", POOL);
    assert_eq!(idle(&clone, 3), Verdict::Quiet);
    // a malformed line holds no session: said, never idle
    let (_d, clone) = world("idle-bad", "T3 mend files=a\n", POOL);
    let why = format!("{:?}", idle(&clone, 3));
    assert!(why.starts_with("Unread("), "{why}");
    assert!(why.contains("line 1: `mend` is no kind"), "{why}");
    // with no entry to hand out in any readable queue, the first unread one is what is said
    let (_d, clone) = world("idle-foreign", "T3 fix files=a waits=GM\n", POOL);
    put(&clone.join("specs/269-pages/queue.txt"), "/c/w.md then:x\n");
    put(&clone.join("specs/280-pages/queue.txt"), "/c/v.md then:y\n");
    let why = format!("{:?}", idle(&clone, 3));
    assert!(why.starts_with("Unread(\"specs/269-pages/queue.txt line 1: "));
}

/// FR-013 (the GM 2026-11-20) under SC-006: among the READY entries that overlap nothing in flight, an open performance task's
/// entry (its `[perf]` tag, or the checklist `PERF=1` writes into plan.md) is offered first, the queue's order within each class.
#[test]
fn an_open_performance_task_s_entry_is_offered_before_an_earlier_one() {
    let queue = "T3 fix files=a\nT6 fix files=b\nT7 fix files=c\n";
    let (_dir, clone) = world("perf", queue, POOL);
    let common = clone.join(".git");
    let dir = clone.join("specs/451-x");
    put(
        &dir.join("tasks.md"),
        "- [ ] T3 open\n- [ ] T6 open\n- [ ] T7 [perf] the faster gate\n",
    );
    let trees = crate::builder_pool::read(&common);
    let b = board(&clone, &common, &dir, &trees).unwrap();
    assert_eq!(b.next.pick, Some(2));
    let said: Vec<String> = b
        .next
        .skipped
        .iter()
        .map(|(i, w)| format!("{i} {w}"))
        .collect();
    let first = "is performance work, offered first (FR-013)";
    assert_eq!(
        said,
        vec![
            format!("0 T7 (line 3) {first}"),
            format!("1 T7 (line 3) {first}")
        ]
    );
    // PERF=1's mark, the plan's checklist heading, counts as the tag does; the queue's order decides between two
    put(&dir.join("plan.md"), "### T6 Performance checklist\n");
    let b = board(&clone, &common, &dir, &trees).unwrap();
    assert_eq!((b.next.pick, b.next.skipped.len()), (Some(1), 1));
    // a performance entry held back by a task in flight leaves the queue's order: T7 overlaps T5's files
    put(
        &dir.join("queue.txt"),
        "T5 fix files=c\nT3 fix files=a\nT7 fix files=c/d\n",
    );
    put(&dir.join("plan.md"), "");
    let b = board(&clone, &common, &dir, &trees).unwrap();
    assert_eq!(b.next.pick, Some(1));
    // a [perf] the title only quotes, a ticked perf box and a READY task with no box (T7) are not open performance work
    put(&dir.join("queue.txt"), queue);
    put(
        &dir.join("tasks.md"),
        "- [ ] T3 open\n- [ ] T6 names a [perf] tag\n- [x] T8 [perf] done\n",
    );
    let b = board(&clone, &common, &dir, &trees).unwrap();
    assert_eq!((b.next.pick, b.next.skipped.len()), (Some(0), 0));
}

/// The Stop guard's free tree belongs to no feature: a later queue's performance entry is named before an earlier queue's other one.
#[test]
fn the_idle_rule_names_a_performance_entry_of_any_queue_first() {
    let (dir, clone) = world("perf-idle", "T3 fix files=a\n", POOL);
    put(&clone.join("specs/452-y/queue.txt"), "T4 fix files=b\n");
    put(
        &clone.join("specs/452-y/tasks.md"),
        "- [ ] T4 [perf] the faster suite\n",
    );
    let want = Idle {
        tree: dir.join("c-b1"),
        tasks: "452 T4".to_owned(),
        command: "make builder-brief T=T4 F=452 KIND=fix ENTRY=1".to_owned(),
        unlisted: Vec::new(),
    };
    assert_eq!(idle(&clone, 3), Verdict::Idle(want));
    // no performance entry anywhere: the first queue's pick
    put(&clone.join("specs/452-y/tasks.md"), "- [ ] T4 the suite\n");
    let said = format!("{:?}", idle(&clone, 3));
    assert!(said.contains("tasks: \"451 T3\""), "{said}");
}

/// T416's two misfires (451 T313's review, round 1): a done line names the entry it ends (`"entry": k`, the entry's ordinal among
/// its first task's lines), so two `make builder-done` runs for one entry skip no entry, and a kept tree's one run ends the entries
/// through the one it names; a done line naming none counts as before.
#[test]
fn a_done_line_names_the_entry_it_ends() {
    let halves = "T3 build-half files=a\nT3 closing-half files=a\n";
    let (_dir, clone) = world("named", halves, POOL);
    let common = clone.join(".git");
    let dir = clone.join("specs/451-x");
    let trees = crate::builder_pool::read(&common);
    let built = State::Built("carried, its landing owed".to_owned());
    let with = |log: &str| {
        put(&common.join(LOG), log);
        board(&clone, &common, &dir, &trees).unwrap().states
    };
    let one = "{\"event\":\"done\",\"detail\":\"451 T3\",\"entry\":1}\n";
    // a builder at its cap and its successor: two runs, both for the build half - the closing half is still to hand out
    assert_eq!(
        with(&format!("{one}{one}")),
        vec![built.clone(), State::Ready]
    );
    // a kept tree: the build half and the closing half in one tree, one run naming the closing half - both ended
    let two = "{\"event\":\"done\",\"detail\":\"451 T3\",\"entry\":2}\n";
    assert_eq!(with(two), vec![built.clone(), built.clone()]);
    // one run naming the build half ends it alone
    assert_eq!(with(one), vec![built.clone(), State::Ready]);
    // a done line written before entries were named counts, as before; an entry the queue no longer holds counts too
    let plain = "{\"event\":\"done\",\"detail\":\"451 T3\"}\n";
    assert_eq!(
        with(&format!("{plain}{plain}")),
        vec![built.clone(), built.clone()]
    );
    let gone = "{\"event\":\"done\",\"detail\":\"451 T3\",\"entry\":7}\n";
    assert_eq!(with(gone), vec![built.clone(), State::Ready]);
    // a bundle's entry is named by its ordinal among its FIRST task's lines: the second line naming T3 ends T3's two and T6's one
    put(
        &dir.join("queue.txt"),
        "T3 fix files=a\nT3,T6 fix files=b\nT6 fix files=c\n",
    );
    put(&dir.join("tasks.md"), "- [ ] T3 open\n- [ ] T6 open\n");
    let bundle = "{\"event\":\"done\",\"detail\":\"451 T3,T6\",\"entry\":2}\n";
    assert_eq!(with(bundle), vec![built.clone(), built, State::Ready]);
    let b = board(&clone, &common, &dir, &trees).unwrap();
    assert_eq!(
        b.entries[1].command("451"),
        "make builder-brief T=T3,T6 F=451 KIND=fix ENTRY=2"
    );
    assert_eq!(
        b.entries[2].command("451"),
        "make builder-brief T=T6 F=451 KIND=fix ENTRY=2"
    );
}

const STARTED: &str =
    "{\"feature\": \"451-x\", \"task\": \"T3\", \"utc\": \"2026-11-27T01:00:00Z\"}\n";

/// 451 T313's round-3 ruling (T421): an open performance task of an active feature with no queue line is named first, with the
/// `make queue-add` command that writes its line, its KIND by `builder_brief::mechanism`; a line naming it, in any state - `waits=`
/// among them - quiets it; a queue that cannot be parsed names none of its feature's tasks.
#[test]
fn an_open_performance_task_with_no_queue_line_is_named_with_the_command_that_writes_one() {
    let (dir, clone) = world("unlisted", "T3 fix files=a waits=GM\n", POOL);
    let common = clone.join(".git");
    put(&common.join("task-starts.jsonl"), STARTED);
    put(&clone.join("Makefile"), "queue-add:\nland:\n");
    put(
        &clone.join("specs/451-x/tasks.md"),
        "- [ ] T3 open\n- [ ] T6 [perf] the faster gate\n- [ ] T7 [perf] a new command for the pool\n- [ ] T8 the slow one\n",
    );
    let names = |prefer: &str| -> Vec<String> {
        unlisted(&clone, &common, prefer)
            .iter()
            .map(|u| format!("{} {} | {}", u.tasks, u.kind, u.command))
            .collect()
    };
    let both = vec![
        "451 T6 fix | make queue-add F=451 T=T6 KIND=fix".to_owned(),
        "451 T7 build-half | make queue-add F=451 T=T7 KIND=build-half".to_owned(),
    ];
    assert_eq!(names(""), both);
    assert_eq!(names("451"), both);
    // the Stop guard: nothing READY (T3 waits on the GM), and still held, naming them
    let want = Idle {
        tree: dir.join("c-b1"),
        tasks: String::new(),
        command: String::new(),
        unlisted: unlisted(&clone, &common, ""),
    };
    assert_eq!(idle(&clone, 3), Verdict::Idle(want));
    // a line for each - one waiting - quiets both, and the queue's own pick returns
    put(
        &clone.join("specs/451-x/queue.txt"),
        "T3 fix files=a\nT6 fix files=b waits=GM note=after the window\nT7 build-half files=c\n",
    );
    assert!(names("").is_empty());
    let said = format!("{:?}", idle(&clone, 3));
    assert!(said.contains("tasks: \"451 T7\"") && said.contains("unlisted: []"));
    // a queue file that is no builders' queue names none of its feature's tasks; with none listed and nothing READY: quiet
    put(&clone.join("specs/451-x/queue.txt"), "/c/w.md then:x\n");
    assert!(names("").is_empty());
    // a feature never started is not active; a start log that cannot be read names none
    std::fs::remove_file(clone.join("specs/451-x/queue.txt")).unwrap();
    assert_eq!(names("").len(), 2);
    put(&common.join("task-starts.jsonl"), "");
    assert!(names("").is_empty());
    assert_eq!(names("451").len(), 2);
    std::fs::write(common.join("task-starts.jsonl"), [0xff_u8]).unwrap();
    assert!(names("").is_empty());
    assert_eq!(idle(&clone, 3), Verdict::Quiet);
}

/// 451 T313's round-3 ruling: across the queues, a READY performance entry of any queue first, then the preferred queue's pick, then
/// the first queue's - `idle`'s rule, which `make builder-done`'s step 1 takes too.
#[test]
fn the_offer_across_queues_is_performance_first_then_the_preferred_queue() {
    let (_dir, clone) = world("offer", "T3 fix files=a\n", POOL);
    let common = clone.join(".git");
    let trees = crate::builder_pool::read(&common);
    put(&clone.join("specs/452-y/queue.txt"), "T4 fix files=b\n");
    put(&clone.join("specs/452-y/tasks.md"), "- [ ] T4 the suite\n");
    put(
        &clone.join("specs/453-z/queue.txt"),
        "T5 fix files=c waits=GM\n",
    );
    put(&clone.join("specs/453-z/tasks.md"), "- [ ] T5 waits\n");
    let read = || -> Vec<Board> {
        queues(&clone)
            .iter()
            .map(|d| board(&clone, &common, d, &trees).unwrap())
            .collect()
    };
    let picked = |prefer: &str| {
        let all = read();
        offer(&all, prefer).map(|(b, i)| format!("{} {}", b.key, b.entries[i].name()))
    };
    assert_eq!(picked("").as_deref(), Some("451 T3"));
    assert_eq!(picked("452").as_deref(), Some("452 T4"));
    // a preferred queue with nothing to hand out: the first queue's
    assert_eq!(picked("453").as_deref(), Some("451 T3"));
    put(
        &clone.join("specs/452-y/tasks.md"),
        "- [ ] T4 [perf] the suite\n",
    );
    assert_eq!(picked("451").as_deref(), Some("452 T4"));
    assert_eq!(offer(&[], "451"), None);
}
