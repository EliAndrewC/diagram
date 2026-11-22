//! 451 T156: A BUILDER'S BRIEF, READ AS THE SESSION WRITES IT, AND A LANDING HOLDS THE SLOTS. The five descriptions the Stop hook's
//! free-slot check misread on 2026-11-22 (a landing agent with no task id, a word between the feature and the first id, a range, a range
//! inside a list), and a landing in flight - an agent whose brief runs `make land`, or this clone's `l7r-gate land` or `land-alone.sh`
//! process - naming no task-start.

use std::path::Path;

use super::super::builders::{builder_brief, landing_process};
use super::{agent, said, world};

fn ids(from: &str, to: u32) -> Vec<String> {
    let start: u32 = from.parse().unwrap();
    (start..=to).map(|n| format!("T{n}")).collect()
}

/// The brief of an agent whose meta file holds `description` alone.
fn brief(dir: &Path, description: &str) -> Option<(String, Vec<String>)> {
    std::fs::write(
        dir.join("agent-x.meta.json"),
        serde_json::json!({"spawnDepth": 1, "description": description}).to_string(),
    )
    .unwrap();
    builder_brief(dir, "x")
}

#[test]
fn every_task_id_before_the_colon_is_read_words_between_and_ranges_expanded() {
    let d = crate::tempdir::TempDir::new("guard-setdown-briefs");
    let s = |v: &[&str]| v.iter().map(|t| (*t).to_owned()).collect::<Vec<_>>();
    let got = brief(&d, "449 bundle T259, T277: the two bundle follow-ups");
    assert_eq!(got, Some(("449".to_owned(), s(&["T259", "T277"]))));
    let got = brief(&d, "449 T289-T300 bundle (fresh): twelve tasks");
    assert_eq!(got, Some(("449".to_owned(), ids("289", 300))));
    let mut list = s(&["T275", "T276"]);
    list.extend(ids("278", 281));
    let got = brief(&d, "449 bundle T275, T276, T278-T281: the six");
    assert_eq!(got, Some(("449".to_owned(), list)));
    let mut shrine = s(&["T260"]);
    shrine.extend(ids("282", 287));
    let got = brief(
        &d,
        "449 shrine bundle T260, T282-T287 (fresh): the shrine's",
    );
    assert_eq!(got, Some(("449".to_owned(), shrine)));
    // a range keeps its ids' width; one written backwards, or past a sane span, is its two ends
    let got = brief(&d, "385 T02-T04: three");
    assert_eq!(got, Some(("385".to_owned(), s(&["T02", "T03", "T04"]))));
    let got = brief(&d, "385 T09-T03, T05a: backwards");
    assert_eq!(got, Some(("385".to_owned(), s(&["T09", "T03", "T05a"]))));
    let got = brief(&d, "385 T1-T9999: past a span");
    assert_eq!(got, Some(("385".to_owned(), s(&["T1", "T9999"]))));
    // a landing agent names no task before its colon: no builder of a task
    assert_eq!(
        brief(&d, "449 batch landing: clear the six refusals and land"),
        None
    );
}

/// A range's member never task-started is its builder's, never the next named (`449 T289-T300 bundle`'s ten between).
#[test]
fn a_running_builder_s_range_member_is_never_the_next_named() {
    let (_dir, c, tr) = world("range", "no");
    crate::env::unset("L7R_BUILDERS");
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        "- [ ] T02 two\n- [ ] T03 three\n- [ ] T04 four\n- [ ] T07 seven\n",
    )
    .unwrap();
    agent(&tr, "r1", 1, "385 T03-T05 bundle (fresh): three");
    let text = said(&c, &tr).unwrap();
    assert!(
        text.contains("1 of 3 builders running (385 T03+T04+T05)"),
        "{text}"
    );
    assert!(text.contains("make task-start F=385 T=T07,"), "{text}");
}

/// A clone with one builder running and an independent task free: the free slot is named until a landing runs.
#[test]
fn a_landing_agent_or_a_landing_process_holds_the_slots() {
    let (_dir, c, tr) = world("landing", "no");
    crate::env::unset("L7R_BUILDERS");
    let proc = c.parent().unwrap().join("proc");
    std::fs::create_dir_all(&proc).unwrap();
    crate::env::set("L7R_PROC_ROOT", &proc);
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        "- [ ] T02 two\n- [ ] T03 three\n- [ ] T07 seven\n",
    )
    .unwrap();
    agent(&tr, "a1", 1, "385 T02: two");
    let text = said(&c, &tr).unwrap();
    assert!(text.contains("1 of 3 builders running (385 T02)"), "{text}");
    assert!(text.contains("make task-start F=385 T=T07,"), "{text}");
    // a landing agent: no task-start named mid-landing (the round arbiter, ask:set-down-449-mid-landing)
    agent(
        &tr,
        "l1",
        1,
        "385 batch landing: clear the six refusals and land",
    );
    assert_eq!(said(&c, &tr), None);
    // its end frees the slot again; a builder's brief whose prompt's first line runs make land holds it too
    append_end(&tr, "l1");
    assert!(said(&c, &tr).is_some());
    agent(&tr, "l2", 1, "385 T03: three");
    super::own(
        &tr,
        "l2",
        r#"{"type":"user","message":{"role":"user","content":"Run make land F=385 T=T03 NOTE=\"x\" and report.\nmake land-tooling is another's."}}"#,
    );
    assert_eq!(said(&c, &tr), None);
    append_end(&tr, "l2");
    assert!(said(&c, &tr).is_some());
    // a landing process in this clone holds the slots: l7r-gate land, or land-alone.sh
    process(&proc, 41, &c, &["/x/l7r-gate", "land", "385", "T02"]);
    assert_eq!(said(&c, &tr), None);
    crate::env::unset("L7R_PROC_ROOT");
}

#[test]
fn a_landing_process_is_this_clone_s_land_or_land_alone_never_land_stop() {
    let d = crate::tempdir::TempDir::new("guard-setdown-proc");
    let d = d.canonicalize().unwrap();
    let (root, land, other, proc) = (d.join("c"), d.join("c-land"), d.join("o"), d.join("proc"));
    for p in [&root, &land, &other, &proc] {
        std::fs::create_dir_all(p).unwrap();
    }
    assert!(!landing_process(&root, &proc));
    assert!(!landing_process(&root, &d.join("no-proc")));
    process(&proc, 1, &root, &["/x/l7r-gate", "land", "--stop"]);
    process(&proc, 2, &other, &["/x/l7r-gate", "land", "385", "T02"]);
    process(&proc, 3, &root, &["/x/l7r-gate", "check", "land"]);
    process(&proc, 4, &root, &["bash"]);
    std::fs::create_dir_all(proc.join("self")).unwrap();
    std::fs::create_dir_all(proc.join("5")).unwrap();
    assert!(!landing_process(&root, &proc));
    process(
        &proc,
        6,
        &land,
        &["bash", "/c/scripts/land-alone.sh", "385", "T02"],
    );
    assert!(landing_process(&root, &proc));
    std::fs::remove_dir_all(proc.join("6")).unwrap();
    process(&proc, 7, &root, &["/x/l7r-gate", "land", "385", "T02"]);
    assert!(landing_process(&root, &proc));
}

/// A process under a fake `/proc`: its command line and its working directory.
fn process(proc: &Path, pid: u32, cwd: &Path, args: &[&str]) {
    let at = proc.join(pid.to_string());
    std::fs::create_dir_all(&at).unwrap();
    std::fs::write(at.join("cmdline"), format!("{}\0", args.join("\0"))).unwrap();
    std::os::unix::fs::symlink(cwd, at.join("cwd")).unwrap();
}

fn append_end(tr: &Path, id: &str) {
    let old = std::fs::read_to_string(tr).unwrap();
    std::fs::write(
        tr,
        format!("{old}{{\"type\":\"user\",\"message\":{{\"role\":\"user\",\"content\":\"<task-notification>\\n<task-id>{id}</task-id>\\n<status>completed</status>\\n<summary>Agent finished</summary>\\n</task-notification>\"}}}}\n"),
    )
    .unwrap();
}
