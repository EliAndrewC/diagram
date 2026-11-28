//! The builders' scheduling policy (461 T81, FR-011): the record read or refused by its line, its default, the [bugfix] tag, the
//! ranking's five steps, and the 2026-11-28 case it was filed on.

use std::path::{Path, PathBuf};

use super::*;
use crate::tempdir::TempDir;

fn put(path: &Path, text: &str) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn tree(path: &str, feature: &str, tasks: &[&str]) -> Tree {
    Tree {
        tree: PathBuf::from(path),
        feature: feature.to_owned(),
        tasks: tasks.iter().map(|t| (*t).to_owned()).collect(),
        since: String::new(),
    }
}

fn work(key: &str, task: &str, source: Source, perf: bool, bugfix: bool) -> Work {
    Work {
        key: key.to_owned(),
        tasks: vec![task.to_owned()],
        source,
        command: format!("make builder-brief T={task} F={key}"),
        perf,
        bugfix,
    }
}

fn names(r: &[Ranked]) -> Vec<String> {
    r.iter().map(|r| r.work.name()).collect()
}

const WORDS: &str = " note=the GM 2026-11-28: \"his words\"";

#[test]
fn the_record_is_read_line_by_line_and_each_malformed_line_is_named() {
    let text = format!("# the policy\n\nclass bugfix{WORDS}\nclass perf{WORDS}\n461 all{WORDS}\n462 floor 2{WORDS}\n451 share{WORDS}\n");
    let p = parse(&text).unwrap();
    assert_eq!(p.classes, vec![Class::Bugfix, Class::Perf]);
    assert_eq!(
        (p.form("461"), p.form("462"), p.form("451"), p.form("9")),
        (Form::All, Form::Floor(2), Form::Share, Form::Share)
    );
    let bad = format!("461 all\nclass speed{WORDS}\nclass perf{WORDS}\nclass perf{WORDS}\n462 floor 0{WORDS}\n462 floor x{WORDS}\n463 most{WORDS}\nfeature 461 all{WORDS}\n464 all{WORDS}\n464 share{WORDS}\n");
    let why = parse(&bad).unwrap_err();
    let lines: Vec<&str> = why.lines().collect();
    assert_eq!(lines.len(), 8, "{why}");
    assert!(lines[0].starts_with("dev/builder-policy.txt line 1: it carries no note="));
    assert!(lines[1].contains("line 2: `speed` is no class"));
    assert!(lines[2].contains("line 4: class perf is given twice"));
    assert!(lines[3].contains("line 5: `floor 0`: a floor is a count"));
    assert!(lines[4].contains("line 6: `floor x`"));
    assert!(lines[5].contains("line 7: `most` is no form"));
    assert!(lines[6].contains("line 8: no line of the policy"));
    assert!(lines[7].contains("line 10: feature 464 is given twice"));
}

#[test]
fn an_absent_record_is_the_default_and_a_malformed_one_reads_as_it_and_says_why() {
    let dir = TempDir::new("policy-read");
    let r = read(&dir);
    assert!(r.absent && r.why.is_empty());
    assert_eq!(r.policy.classes, vec![Class::Perf, Class::Bugfix]);
    assert!(r.policy.features.is_empty());
    put(&dir.join(FILE), "461 all\n");
    let r = read(&dir);
    assert!(!r.absent);
    assert_eq!(r.policy, Policy::default());
    assert!(r.why.contains("line 1: it carries no note="));
    assert!(r.why.ends_with("every feature share)"));
    put(&dir.join(FILE), &format!("461 all{WORDS}\n"));
    let r = read(&dir);
    assert_eq!((r.why.as_str(), r.absent), ("", false));
    // no class line: the default's two stand
    assert_eq!(r.policy.classes, vec![Class::Perf, Class::Bugfix]);
    assert_eq!(r.policy.form("461"), Form::All);
}

/// The repository's own record parses.
#[test]
fn the_repository_s_record_parses() {
    // parses, whatever lines the GM's words add (the crate's `reads` names `dev/builder-policy.txt`, so an edit re-runs this)
    assert!(parse(include_str!("../../../../../../dev/builder-policy.txt")).is_ok());
}

#[test]
fn class_none_ranks_no_class_and_stands_alone() {
    let p = parse(&format!("class none{WORDS}\n461 all{WORDS}\n")).unwrap();
    assert!(p.classes.is_empty());
    let w = vec![
        work("462", "T1", Source::Entry(1), true, true),
        work("461", "T2", Source::Entry(1), false, false),
    ];
    assert_eq!(names(&rank(&p, w, &[], "")), vec!["461 T2", "462 T1"]);
    for bad in [
        "class none{W}\nclass perf{W}\n",
        "class perf{W}\nclass none{W}\n",
    ] {
        let why = parse(&bad.replace("{W}", WORDS)).unwrap_err();
        assert!(why.contains("line 2: class none stands alone"), "{why}");
    }
}

#[test]
fn the_bugfix_tag_is_read_among_the_tags_after_the_id_and_never_from_the_title() {
    assert!(bugfix("[bugfix] the lane drops a superseded change"));
    assert!(bugfix("[P] [bugfix] a tag after another"));
    assert!(bugfix("[bugfix] [perf] before perf"));
    assert!(bugfix("[bugfix]"));
    assert!(!bugfix("names a [bugfix] tag in its prose"));
    assert!(!bugfix("[P] plain"));
    assert!(!bugfix(""));
    // a tag holding a space is read whole, as PERF_TAG reads it; a tag run into the next word, or left open, ends the scan
    assert!(bugfix("[waits: T80] [bugfix] after a spaced tag"));
    assert!(bugfix("[P]  [bugfix] two spaces"));
    assert!(!bugfix("[bugfix]x run on"));
    assert!(!bugfix("[P]x [bugfix] run on"));
    assert!(!bugfix("[open tag [bugfix]"));
}

/// THE CASE FR-011 WAS FILED ON (2026-11-28): 462's disk entries were handed builders while 461's phase 3 tasks stood ready -
/// asked from a 462 tree (`make builder-done`'s caller) and from the Stop guard (no caller). Under `461 all`, every pick is 461's
/// while one stands ready, and a performance or bugfix task of any feature goes ahead of both.
#[test]
fn the_2026_11_28_case_a_feature_given_every_builder_is_picked_over_the_caller_s_queue() {
    let p = parse(&format!(
        "class perf{WORDS}\nclass bugfix{WORDS}\n461 all{WORDS}\n"
    ))
    .unwrap();
    let ready = || {
        vec![
            work("462", "T533", Source::Entry(1), false, false),
            work("462", "T301", Source::Entry(2), false, false),
            work("461", "T81", Source::Unlisted(3), false, false),
            work("461", "T77", Source::Entry(4), false, false),
        ]
    };
    for prefer in ["462", ""] {
        let r = rank(&p, ready(), &[], prefer);
        let want = ["461 T77", "461 T81", "462 T533", "462 T301"];
        assert_eq!(
            (prefer, names(&r)),
            (prefer, want.map(str::to_owned).to_vec())
        );
        assert_eq!(r[0].why, "feature 461 (all: every builder it can use)");
    }
    // a performance task of 462 and a bugfix of 451 go ahead of 461's: the classes rank across every feature
    let mut w = ready();
    w.push(work("462", "T550", Source::Entry(9), true, false));
    w.push(work("451", "T600", Source::Entry(1), false, true));
    let r = rank(&p, w, &[], "462");
    assert_eq!(&names(&r)[..3], &["462 T550", "451 T600", "461 T77"]);
    assert_eq!(r[0].why, "class perf first, then feature 462 (share)");
    assert_eq!(r[0].class, Some(Class::Perf));
    // with no policy line for 461, the caller's own queue is preferred, as before
    let r = rank(&Policy::default(), ready(), &[], "462");
    assert_eq!(names(&r)[0], "462 T533");
    let r = rank(&Policy::default(), ready(), &[], "");
    assert_eq!(names(&r)[0], "461 T77");
}

/// A floor not yet met ranks first, even over `all`; met, its feature fills only what no other contends for.
#[test]
fn a_floor_is_a_guarantee_until_met_and_then_ranks_last() {
    let p = parse(&format!("461 all{WORDS}\n462 floor 1{WORDS}\n")).unwrap();
    let w = || {
        vec![
            work("451", "T1", Source::Entry(1), false, false),
            work("461", "T2", Source::Entry(1), false, false),
            work("462", "T3", Source::Entry(1), false, false),
        ]
    };
    let r = rank(&p, w(), &[], "");
    assert_eq!(names(&r), vec!["462 T3", "461 T2", "451 T1"]);
    assert_eq!(r[0].why, "feature 462 (floor 1, 0 held: its guarantee)");
    assert_eq!(r[0].form, Form::Floor(1));
    // 462 holds its one tree: it ranks below every share feature; a free tree in the pool counts for nobody
    let held = [tree("/b0", "462", &["T9"]), tree("/b1", "", &[])];
    let r = rank(&p, w(), &held, "462");
    assert_eq!(names(&r), vec!["461 T2", "451 T1", "462 T3"]);
    assert_eq!(
        r[2].why,
        "feature 462 (floor 1, 1 held: only an uncontended tree)"
    );
}

/// Within one feature and form: its repair, then its queue's entries in their order, then its unlisted tasks in their boxes' order;
/// a repair of a class task ranks with the class, never above it by being a repair (`LANE_REPAIR_FIRST` is no rank of the GM's).
#[test]
fn within_a_feature_its_repair_then_its_queue_then_its_unlisted_tasks_and_a_repair_has_no_rank_of_its_own(
) {
    let p = Policy::default();
    let w = vec![
        work("461", "T5", Source::Unlisted(0), false, false),
        work("461", "T4", Source::Entry(7), false, false),
        work("461", "T3", Source::Entry(2), false, false),
        work("461", "T2", Source::Repair("r1".to_owned()), false, false),
        work("451", "T1", Source::Entry(3), true, false),
    ];
    let r = rank(&p, w, &[], "");
    assert_eq!(
        names(&r),
        vec!["451 T1", "461 T2", "461 T3", "461 T4", "461 T5"]
    );
}

/// A clone: 461 with a queue whose entries are landed and phase 3 tasks no line names, 462 with READY disk entries, a pool of four
/// trees with one free, a repair of 462's, and the policy's record as given.
fn world(tag: &str, policy: &str) -> (TempDir, PathBuf) {
    let dir = TempDir::new(&format!("policy-{tag}"));
    let clone = dir.join("c");
    std::fs::create_dir_all(&clone).unwrap();
    let ran = std::process::Command::new("git")
        .arg("-C")
        .arg(&clone)
        .args(["init", "-q"])
        .output()
        .unwrap();
    assert!(ran.status.success());
    put(
        &clone.join("specs/461-landing-lane/tasks.md"),
        "- [x] T09 landed\n- [ ] T76 held by a tree\n- [ ] T81 phase 3, its policy\n- [ ] T82 [bugfix] phase 3, a defect\n- [ ] T83 built, its carry owed\n- [ ] GM the GM's box\n",
    );
    put(
        &clone.join("specs/461-landing-lane/queue.txt"),
        "T09 fix crates=- files=-\n",
    );
    put(
        &clone.join("specs/462-efficiency-backlog/tasks.md"),
        "- [ ] T533 disk\n- [ ] T301 disk\n- [ ] T550 [perf] faster, no line\n",
    );
    put(
        &clone.join("specs/462-efficiency-backlog/queue.txt"),
        "#! order=queue - the GM 2026-11-27: the disk tasks first\nT533 fix crates=- files=a\nT301 fix crates=- files=b\n",
    );
    let pool = r#"{"trees": [{"tree": "<D>/b0", "feature": "461", "tasks": ["T76"], "since": ""}, {"tree": "<D>/b1", "feature": "", "tasks": [], "since": ""}]}"#;
    put(
        &clone.join(".git/builder-pool.json"),
        &pool.replace("<D>", &dir.to_string_lossy()),
    );
    let sha = "0123456789abcdef0123456789abcdef01234567";
    let ran = std::process::Command::new("git")
        .arg("-C")
        .arg(&clone)
        .args([
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "x",
        ])
        .output()
        .unwrap();
    assert!(ran.status.success());
    let head = std::process::Command::new("git")
        .arg("-C")
        .arg(&clone)
        .args(["update-ref", "refs/l7r/done/461-T83", "HEAD"])
        .output()
        .unwrap();
    assert!(head.status.success());
    put(
        &clone.join(".git/l7r-lane/repairs.jsonl"),
        "{\"repair\": \"r1\", \"feature\": \"462-efficiency-backlog\", \"tasks\": [\"T301\"], \"kind\": \"fix\", \"batch\": \"462-1\", \"why\": \"unplaced\", \"units\": [], \"attempt\": \"a.log\"}\n",
    );
    put(
        &clone.join(".git/l7r-lane/lane.jsonl"),
        &format!("{{\"utc\": \"2026-11-28T02:54:14Z\", \"event\": \"eject\", \"batch\": \"462-1\", \"change\": \"{sha}\", \"repair\": \"r1\"}}\n"),
    );
    put(
        &clone.join(".git/task-starts.jsonl"),
        "{\"feature\": \"462-efficiency-backlog\", \"task\": \"T533\", \"utc\": \"2026-11-28T00:38:50Z\"}\n{\"feature\": \"461-landing-lane\", \"task\": \"T76\", \"utc\": \"2026-11-28T03:17:45Z\"}\n",
    );
    if !policy.is_empty() {
        put(&clone.join(FILE), policy);
    }
    (dir, clone)
}

#[test]
fn the_one_reader_ranks_the_clone_s_work_by_its_record() {
    let (_dir, clone) = world(
        "ranked",
        &format!("class perf{WORDS}\nclass bugfix{WORDS}\n461 all{WORDS}\n"),
    );
    let r = ranked(&clone, "462");
    assert_eq!((r.read.why.as_str(), r.unread.len()), ("", 0));
    let said: Vec<String> = r
        .work
        .iter()
        .map(|r| format!("{} {:?} {}", r.work.name(), r.work.source, r.work.command))
        .collect();
    assert_eq!(
        said,
        vec![
            "462 T550 Unlisted(2) make queue-add F=462 T=T550 KIND=fix",
            "461 T82 Unlisted(2) make queue-add F=461 T=T82 KIND=fix",
            "461 T81 Unlisted(1) make queue-add F=461 T=T81 KIND=fix",
            "462 T301 Repair(\"r1\") make builder-brief T=T301 F=462 KIND=fix REPAIR=r1",
            "462 T533 Entry(2) make builder-brief T=T533 F=462 KIND=fix ENTRY=1",
            "462 T301 Entry(3) make builder-brief T=T301 F=462 KIND=fix ENTRY=1",
        ]
    );
    // the record absent: the default, the caller's own queue next after the classes - 461's unlisted T81 is no longer put
    // forward, but its unlisted bugfix still is, with its class, though 461 is a share feature (the class ranks across every
    // feature, as T313 names performance work)
    std::fs::remove_file(clone.join(FILE)).unwrap();
    let r = ranked(&clone, "462");
    assert!(r.read.absent);
    assert_eq!(
        names(&r.work),
        vec!["462 T550", "461 T82", "462 T301", "462 T533", "462 T301"]
    );
    assert_eq!(r.work[1].class, Some(Class::Bugfix));
    // an unreadable queue is said; its feature's tasks are not named unlisted, since its lines cannot be read
    put(
        &clone.join("specs/462-efficiency-backlog/queue.txt"),
        "T1 nokind files=-\n",
    );
    let r = ranked(&clone, "");
    assert_eq!(r.unread.len(), 1);
    assert_eq!(names(&r.work), vec!["461 T82", "462 T301"]);
    // a feature set down offers no unlisted bugfix (the active walk's test)
    put(
        &clone.join(".git/set-downs.jsonl"),
        "{\"feature\": \"461-landing-lane\", \"utc\": \"2026-11-28T09:00:00Z\"}\n",
    );
    assert_eq!(names(&ranked(&clone, "").work), vec!["462 T301"]);
}

/// A repair whose task is a performance task ranks with the class; a repair of a feature with no directory has no class.
#[test]
fn a_repair_is_classed_by_its_own_task_s_box() {
    let (_dir, clone) = world("repair-class", "");
    put(
        &clone.join("specs/462-efficiency-backlog/tasks.md"),
        "- [ ] T533 disk\n- [ ] T301 [perf] disk, faster\n",
    );
    put(&clone.join("specs/462-efficiency-backlog/plan.md"), "");
    let r = ranked(&clone, "");
    assert_eq!(
        names(&r.work)[..2],
        ["462 T301".to_owned(), "462 T301".to_owned()]
    );
    assert_eq!(r.work[0].work.source, Source::Repair("r1".to_owned()));
    assert_eq!(r.work[0].class, Some(Class::Perf));
    let g = Ground {
        clone: &clone,
        held: &[],
        uncarried: BTreeSet::new(),
        repairs: vec![super::super::repairs::Repair {
            id: "r2".to_owned(),
            key: "777".to_owned(),
            tasks: vec!["T1".to_owned()],
            kind: "fix".to_owned(),
            ..Default::default()
        }],
        unlisted: Vec::new(),
        bugfixes: BTreeSet::new(),
        known: BTreeSet::new(),
    };
    let w = repairs_of(&g);
    assert_eq!((w.len(), w[0].perf, w[0].bugfix), (1, false, false));
}

/// A floor not met puts its feature's unlisted tasks forward, met it does not; a new mechanism's unlisted task is listed build-half.
#[test]
fn a_floor_not_met_names_its_unlisted_tasks_and_a_mechanism_is_listed_build_half() {
    let (_dir, clone) = world("floor", &format!("461 floor 2{WORDS}\n"));
    put(
        &clone.join("specs/461-landing-lane/tasks.md"),
        "- [x] T09 landed\n- [ ] T81 a new guard, its policy\n",
    );
    let r = ranked(&clone, "");
    // the class first (462's unlisted performance task), then the floor's guarantee
    assert_eq!(
        names(&r.work)[..2],
        ["462 T550".to_owned(), "461 T81".to_owned()]
    );
    assert_eq!(
        r.work[1].work.command,
        "make queue-add F=461 T=T81 KIND=build-half"
    );
    // met, and a feature the record names with no directory: neither names an unlisted task
    put(
        &clone.join(FILE),
        &format!("461 floor 1{WORDS}\n999 all{WORDS}\n"),
    );
    let r = ranked(&clone, "");
    assert!(names(&r.work).iter().all(|n| n.starts_with("462")));
}
