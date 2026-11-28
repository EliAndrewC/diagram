//! The batch run end to end (feature 461 T14) on a scratch world: a clone, a bare `origin`, the lane's tree in the pool's registry
//! and two pool trees, the landing a stand-in `make land` in the clone's own Makefile that ticks and pushes as the real one does. Two
//! hand-ins, one batch, one push, both ticked, both done refs deleted, one `owed` line; a killed runner's batch resumed as attempt 2;
//! a resumed batch already on `origin/main` landed with no run; a carry that stops; the errors. T15's red path: a red the gate's
//! record places ejected as a repair entry and the other change landed on the next run; a red it cannot place ejecting the whole
//! batch as one entry; a killed `make` stopping the runner with the batch open. T19's failed push: twice, one `integrate` entry and
//! one `owed` line; once, the set run again on the new `origin/main` and landed; a resumed batch's earlier failure counted.

use std::fmt::Write as _;
use std::path::PathBuf;

use l7r_gate_core::ci::fixtures::{git, put, scratch};
use l7r_shared::builder_pool::{self, Tree};
use l7r_shared::tempdir::TempDir;
use serde_json::{json, Value};

use super::{resume, step, Lane};
use crate::log::{self, Batch};
use crate::repairs;

/// The gate's red test of the crate `lib/two`, as `make done` writes it in the lane's tree (`@T@` and `@TREE@` the stand-in's).
const PHASE: &str = r#"{"ev":"Phase","src":"rust","step":"test","t0":"@T@","t1":"@T@","code":101,"clone":"@TREE@","crates":["lib/two"]}"#;

/// A task's `phase-<task>` file in the common directory: its line written to the feature's event log as the checks write theirs,
/// stamped now and in the tree the landing runs in, and the landing red; a `kill` file: `make` itself killed, so no exit code; a
/// `refuse` file: the first pass's refusal, its text printed and the landing red (with `refuse-once`, at the first attempt alone).
const RED_LINES: &str = concat!(
    "\t",
    r#"@c=$$(git rev-parse --path-format=absolute --git-common-dir); fail=; for t in $(T); do if [ -f "$$c/phase-$$t" ]; then mkdir -p "$$c/l7r-events"; now=$$(date -u +%Y-%m-%dT%H:%M:%S.%N | cut -c1-23)Z; sed "s|@TREE@|$$(pwd)|; s|@T@|$$now|g" "$$c/phase-$$t" >> "$$c/l7r-events/$$SPECIFY_FEATURE.jsonl"; fail=1; fi; done; [ -z "$$fail" ]"#,
    "\n\t",
    r#"@if [ -f "$$(git rev-parse --git-common-dir)/kill" ]; then kill -9 $$PPID; fi"#,
    "\n\t",
    r#"@c=$$(git rev-parse --git-common-dir); if [ -f "$$c/refuse" ]; then cat "$$c/refuse"; if [ -f "$$c/refuse-once" ]; then rm "$$c/refuse" "$$c/refuse-once"; fi; exit 1; fi"#,
    "\n"
);

/// A `push-fail` file in the common directory: the push fails after a green gate, as the landing's own push says it (`land: the
/// push failed (exit 1) - ...`, `land.rs`); with `push-fail-once`, at the first attempt alone, another writer's commit pushed to
/// `origin/main` meanwhile, so only a tree brought to the new main pushes the second time.
const PUSH_LINES: &str = concat!(
    "\t",
    r#"@c=$$(git rev-parse --path-format=absolute --git-common-dir); if [ -f "$$c/push-fail" ]; then echo "land: the push failed (exit 1) - its ticks reverted" >&2; if [ -f "$$c/push-fail-once" ]; then rm "$$c/push-fail" "$$c/push-fail-once"; git -C "$$c/.." commit -q --allow-empty -m other; git -C "$$c/.." push -q origin HEAD:main; fi; exit 1; fi"#,
    "\n"
);

const MAKEFILE: &str = "carry:\n\tgit cherry-pick $(COMMIT)\nland:\n@RED@\t@if [ -f \"$$(git rev-parse --git-common-dir)/red\" ]; then echo red; exit 1; fi\n\t@echo \"land F=$(F) T=$(T) NOTE=$(NOTE) batch=$$L7R_LANE_BATCH spec=$$SPECIFY_FEATURE alone=$$L7R_LAND_ALONE backup=$$SYNC_BACKUP\"\n\tfor t in $(T); do sed -i \"s/^- \\[ \\] $$t /- [x] $$t /\" specs/461-x/tasks.md; done\n\tgit commit -qam \"461-x: $(T) ticked (make land)\"\n@PUSH@\tgit push -q origin HEAD:main\n\t@if [ -f \"$$(git rev-parse --git-common-dir)/merged\" ]; then exit 3; fi\n";

/// The round arbiter's ask (461 T18), as the lane runs it in its tree: its words kept in the common directory's `asked` file, the
/// bundle named on stdout; with an `ask-fails` file there, refused.
const ASK: &str = concat!(
    "arbiter-ask:\n\t",
    r#"@c=$$(git rev-parse --git-common-dir); printf '%s\n' "SUBJECT=$(SUBJECT) FILES=$(FILES) spec=$$SPECIFY_FEATURE dir=$$SPECIFY_FEATURE_DIRECTORY" '$(WHY)' >> "$$c/asked"; if [ -f "$$c/ask-fails" ]; then echo refused >&2; exit 1; fi; echo "bundle: /tmp/arbiter-$(SUBJECT)/MANIFEST.md""#,
    "\n"
);

struct World {
    dir: TempDir,
    clone: PathBuf,
    common: PathBuf,
}

fn world(tag: &str) -> World {
    let dir = scratch(tag);
    let origin = dir.path().join("origin.git");
    let clone = dir.path().join("repo");
    std::fs::create_dir_all(&clone).unwrap();
    git(
        dir.path(),
        &[
            "init",
            "-q",
            "--bare",
            "-b",
            "main",
            &origin.to_string_lossy(),
        ],
    );
    git(&clone, &["init", "-q", "-b", "main"]);
    git(&clone, &["config", "user.email", "t@t"]);
    git(&clone, &["config", "user.name", "t"]);
    put(
        &clone,
        "Makefile",
        &(MAKEFILE
            .replace("@RED@", RED_LINES)
            .replace("@PUSH@", PUSH_LINES)
            + ASK),
    );
    put(
        &clone,
        "specs/461-x/tasks.md",
        "- [ ] T01 one\n- [ ] T02 two\n- [ ] T03 three\n",
    );
    git(&clone, &["add", "-A"]);
    git(&clone, &["commit", "-qm", "the world"]);
    git(
        &clone,
        &["remote", "add", "origin", &origin.to_string_lossy()],
    );
    git(&clone, &["push", "-q", "origin", "main"]);
    git(&clone, &["fetch", "-q", "origin"]);
    let land = dir.path().join("repo-land");
    git(
        &clone,
        &[
            "worktree",
            "add",
            "-q",
            "--detach",
            &land.to_string_lossy(),
            "origin/main",
        ],
    );
    let common = clone.join(".git");
    let held_by_lane = Tree {
        tree: land,
        feature: String::new(),
        tasks: vec![builder_pool::LANE.to_owned()],
        since: "2026-11-28T00:00:00Z".to_owned(),
    };
    builder_pool::write(&common, &[held_by_lane]).unwrap();
    World { dir, clone, common }
}

impl World {
    /// A builder's hand-in of `task` from a pool tree of its own on `origin/main`: `file` written, committed, kept under its done ref
    /// and on the pool's log as `make builder-done` keeps it.
    fn hand_in(&self, feature: &str, task: &str, file: &str, text: &str) -> String {
        let tree = self.dir.path().join(format!("b-{task}-{file}"));
        git(
            &self.clone,
            &[
                "worktree",
                "add",
                "-q",
                "--detach",
                &tree.to_string_lossy(),
                "origin/main",
            ],
        );
        put(&tree, file, text);
        git(&tree, &["add", "-A"]);
        git(
            &tree,
            &["commit", "-qm", &format!("{feature} {task}: work")],
        );
        let sha = git(&tree, &["rev-parse", "HEAD"]);
        git(
            &self.clone,
            &[
                "update-ref",
                &format!("refs/l7r/done/{feature}-{task}"),
                &sha,
            ],
        );
        let line = json!({"utc": "2026-11-28T01:00:00Z", "event": "done", "handed_in": true, "detail": format!("{feature} {task}"), "commit": sha});
        let log = self.common.join(l7r_shared::builder_queue::LOG);
        let mut text = std::fs::read_to_string(&log).unwrap_or_default();
        let _ = writeln!(text, "{line}");
        std::fs::write(&log, text).unwrap();
        sha
    }

    fn lane(&self) -> Vec<Value> {
        log::read(&self.common)
    }

    fn events(&self) -> Vec<String> {
        self.lane()
            .iter()
            .map(|l| l["event"].as_str().unwrap().to_owned())
            .collect()
    }

    fn refs(&self) -> String {
        git(
            &self.clone,
            &["for-each-ref", "--format=%(refname)", "refs/l7r/done/"],
        )
    }

    fn origin_holds(&self, rel: &str) -> String {
        git(&self.clone, &["fetch", "-q", "origin"]);
        git(&self.clone, &["show", &format!("origin/main:{rel}")])
    }
}

fn no_env(_: &str) -> Option<String> {
    None
}

fn now() -> f64 {
    1000.0
}

fn lane_of(w: &World) -> Lane<'_> {
    Lane {
        common: &w.common,
        now: &now,
        env: &no_env,
    }
}

fn open(w: &World) -> Batch {
    log::batches(&w.lane()).pop().filter(Batch::open).unwrap()
}

#[test]
fn two_hand_ins_land_as_one_batch_one_push_both_ticked_both_refs_deleted_one_owed_line() {
    let w = world("lane-run-green");
    let one = w.hand_in("461", "T01", "a.txt", "a\n");
    let two = w.hand_in("461", "T02", "b.txt", "b\n");
    // a done ref no batch names is kept
    let other = git(&w.clone, &["rev-parse", "HEAD"]);
    git(&w.clone, &["update-ref", "refs/l7r/done/461-T09", &other]);
    let l = lane_of(&w);
    assert_eq!(step(&l), Ok(true));
    assert_eq!(
        w.events(),
        ["batch", "carry", "run", "push", "landed", "owed"]
    );
    let lines = w.lane();
    assert_eq!(lines[0]["changes"], json!([one, two]));
    assert_eq!(lines[2]["code"], 0);
    assert_eq!(lines[2]["set"], json!([&one[..10], &two[..10]]));
    assert_eq!(lines[4]["landed"], json!([one, two]));
    assert_eq!(lines[4]["runs"], 1);
    assert_eq!(
        lines[5]["line"],
        "lane: batch 461-1 landed - 461 T01 T02 (2 change(s), 1 run(s), 0 minutes)"
    );
    let attempt = std::fs::read_to_string(lines[2]["attempt"].as_str().unwrap()).unwrap();
    assert!(attempt.contains("land F=461 T=T01 T02 NOTE=461 T01: work; 461 T02: work - landed by the lane, batch 461-1 batch=461-1 spec=461-x alone=1 backup=off"), "{attempt}");
    assert!(lines[2]["attempt"]
        .as_str()
        .unwrap()
        .ends_with("l7r-lane/attempts/461-1-1.log"));
    assert_eq!(w.origin_holds("a.txt"), "a");
    assert_eq!(w.origin_holds("b.txt"), "b");
    assert!(w
        .origin_holds("specs/461-x/tasks.md")
        .starts_with("- [x] T01 one\n- [x] T02 two\n- [ ] T03"));
    assert_eq!(w.refs(), "refs/l7r/done/461-T09");
    // nothing waits: no batch, no line
    assert_eq!(step(&l), Ok(false));
    assert_eq!(w.lane().len(), 6);
}

#[test]
fn a_red_the_record_places_ejects_its_change_as_a_repair_entry_and_the_other_lands_on_the_next_run()
{
    let w = world("lane-run-placed");
    let one = w.hand_in("461", "T01", "a.txt", "a\n");
    let two = w.hand_in("461", "T02", "lib/two/x.rs", "x\n");
    std::fs::write(w.common.join("phase-T02"), PHASE).unwrap();
    let l = lane_of(&w);
    assert_eq!(step(&l), Ok(true));
    assert_eq!(
        w.events(),
        [
            "batch",
            "carry",
            "run",
            "attribute",
            "eject",
            "owed",
            "carry",
            "run",
            "push",
            "landed",
            "owed"
        ]
    );
    let lines = w.lane();
    let attempt = lines[2]["attempt"].as_str().unwrap().to_owned();
    assert!(attempt.ends_with("l7r-lane/attempts/461-1-1.log"));
    assert_eq!(lines[2]["code"], 2);
    assert_eq!(lines[2]["red"], json!(["lib/two test"]));
    assert_eq!(lines[3]["candidates"], json!([two]));
    assert_eq!(lines[3]["how"], "record");
    assert_eq!(lines[4]["change"], json!(two));
    assert_eq!(lines[4]["repair"], "r1");
    assert_eq!(lines[4]["why"], "red");
    assert_eq!(
        lines[5]["line"],
        format!("lane: batch 461-1 red at attempt 1 - 461 T02 ejected as repair r1 (red: lib/two test) - make builder-next hands it to a fresh builder: {attempt}")
    );
    assert_eq!(lines[7]["n"], 2);
    assert_eq!(lines[7]["set"], json!([&one[..10]]));
    assert_eq!(lines[7]["red"], json!([]));
    assert_eq!(lines[9]["landed"], json!([one]));
    assert_eq!(lines[9]["ejected"], json!([two]));
    assert_eq!(lines[9]["runs"], 2);
    assert_eq!(
        lines[10]["line"],
        "lane: batch 461-1 landed - 461 T01 (1 change(s), 1 ejected, 2 run(s), 0 minutes)"
    );
    let entries = repairs::read(&w.common);
    assert_eq!(entries.len(), 1);
    let mut entry = entries[0].clone();
    entry.as_object_mut().unwrap().remove("utc");
    assert_eq!(
        entry,
        json!({"repair": "r1", "feature": "461-x", "tasks": ["T02"], "kind": "fix", "ejected": [two], "batch": "461-1",
            "why": "red", "units": ["lib/two test"], "attempt": attempt})
    );
    assert_eq!(w.origin_holds("a.txt"), "a");
    assert!(w
        .origin_holds("specs/461-x/tasks.md")
        .starts_with("- [x] T01 one\n- [ ] T02 two"));
    // the ejected change's done ref kept for its repair; it forms no batch again
    assert_eq!(w.refs(), "refs/l7r/done/461-T02");
    assert_eq!(step(&l), Ok(false));
}

#[test]
fn a_red_the_record_cannot_place_ejects_the_whole_batch_as_one_repair_entry_and_forms_no_batch_again(
) {
    let w = world("lane-run-unplaced");
    let one = w.hand_in("461", "T01", "a.txt", "a\n");
    let two = w.hand_in("461", "T02", "b.txt", "b\n");
    std::fs::write(w.common.join("red"), "").unwrap();
    let l = lane_of(&w);
    assert_eq!(step(&l), Ok(true));
    assert_eq!(
        w.events(),
        [
            "batch",
            "carry",
            "run",
            "attribute",
            "eject",
            "eject",
            "owed",
            "landed",
            "owed"
        ]
    );
    let lines = w.lane();
    let attempt = lines[2]["attempt"].as_str().unwrap().to_owned();
    assert_eq!(lines[2]["red"], json!([]));
    assert_eq!(lines[3]["candidates"], json!([one, two]));
    assert_eq!(lines[3]["how"], "none");
    for (line, sha) in [(&lines[4], &one), (&lines[5], &two)] {
        assert_eq!(line["change"], json!(sha));
        assert_eq!(line["repair"], "r1");
        assert_eq!(line["why"], "unplaced");
    }
    assert_eq!(
        lines[6]["line"],
        format!("lane: batch 461-1 red at attempt 1 - 461 T01 T02 ejected as repair r1 (unplaced: the record names none) - make builder-next hands it to a fresh builder: {attempt}")
    );
    assert_eq!(lines[7]["landed"], json!([]));
    assert_eq!(lines[7]["ejected"], json!([one, two]));
    assert_eq!(
        lines[8]["line"],
        "lane: batch 461-1 ended - nothing landed, 2 ejected (1 run(s), 0 minutes)"
    );
    let entries = repairs::read(&w.common);
    assert_eq!(entries.len(), 1);
    assert_eq!(entries[0]["ejected"], json!([one, two]));
    assert_eq!(entries[0]["tasks"], json!(["T01", "T02"]));
    assert_eq!(entries[0]["why"], "unplaced");
    assert_eq!(entries[0]["units"], json!([]));
    assert_eq!(w.refs(), "refs/l7r/done/461-T01\nrefs/l7r/done/461-T02");
    // no batch is formed again from the same hand-ins, red or not
    std::fs::remove_file(w.common.join("red")).unwrap();
    assert_eq!(step(&l), Ok(false));
    // a later hand-in of T01 (its repair) supersedes the ejected one and lands alone
    w.hand_in("461", "T01", "c.txt", "c\n");
    assert_eq!(step(&l), Ok(true));
    assert_eq!(
        w.lane().last().unwrap()["line"],
        "lane: batch 461-2 landed - 461 T01 (1 change(s), 1 run(s), 0 minutes)"
    );
    assert_eq!(w.refs(), "refs/l7r/done/461-T02");
}

#[test]
fn a_make_killed_mid_landing_stops_the_runner_with_the_batch_open_and_ejects_nothing() {
    let w = world("lane-run-killed");
    w.hand_in("461", "T01", "a.txt", "a\n");
    std::fs::write(w.common.join("kill"), "").unwrap();
    let l = lane_of(&w);
    let err = step(&l).unwrap_err();
    let head = "lane: batch 461-1: make land ended with no exit code at attempt 1";
    assert!(err.starts_with(head), "{err}");
    assert_eq!(w.events(), ["batch", "carry", "run", "owed"]);
    assert_eq!(w.lane()[2]["code"], -1);
    assert_eq!(w.lane()[3]["line"], err);
    // the runner's own word that it stopped with the batch open, so `make lane-wait` writes no death line after it (461 T15)
    assert_eq!(w.lane()[3][crate::wake::STOPPED], true);
    assert!(repairs::read(&w.common).is_empty());
    assert!(open(&w).open());
    // the batch open: no step forms or runs again, every poll, and none writes a line - though a hand-in waits
    std::fs::remove_file(w.common.join("kill")).unwrap();
    w.hand_in("461", "T02", "b.txt", "b\n");
    let before = w.lane().len();
    assert_eq!(step(&l), Ok(false));
    assert_eq!(w.lane().len(), before);
}

/// A runner killed after a repair entry was filed and before all its `eject` lines were written (461 T15, the decision this labels):
/// the resume runs what the log has not ejected as a new attempt, so a change the entry lists may land. The entry is then no open
/// repair of that change: only an `eject` line naming the entry's id makes a change the entry's, which T16's queue must read.
#[test]
fn a_kill_between_a_repair_entry_and_its_eject_lines_resumes_what_the_log_has_not_ejected() {
    let w = world("lane-run-entry-kill");
    let one = w.hand_in("461", "T01", "a.txt", "a\n");
    let two = w.hand_in("461", "T02", "b.txt", "b\n");
    let l = lane_of(&w);
    let entry = repairs::Entry {
        feature: "461-x".into(),
        tasks: vec!["T01".into(), "T02".into()],
        kind: "fix".into(),
        ejected: vec![one.clone(), two.clone()],
        batch: "461-1".into(),
        why: "unplaced".into(),
        units: Vec::new(),
        attempt: "a.log".into(),
    };
    assert_eq!(repairs::file(&w.common, "t", &entry), Ok("r1".into()));
    for (event, fields) in [
        ("batch", json!({"batch": "461-1", "changes": [one, two]})),
        ("run", json!({"batch": "461-1", "n": 1, "code": 2})),
        (
            "attribute",
            json!({"batch": "461-1", "candidates": [one, two], "how": "none"}),
        ),
        (
            "eject",
            json!({"batch": "461-1", "change": one, "repair": "r1", "why": "unplaced"}),
        ),
    ] {
        log::append(&w.common, "t", event, &fields).unwrap();
    }
    let b = open(&w);
    let left = crate::runner::remaining(&b, &std::collections::BTreeSet::new());
    assert_eq!(left, [two.clone()]);
    resume(&l, &b, &left).unwrap();
    let lines = w.lane();
    let end = lines.iter().rev().find(|x| x["event"] == "landed").unwrap();
    assert_eq!(end["landed"], json!([two]));
    assert_eq!(end["ejected"], json!([one]));
    assert_eq!(w.origin_holds("b.txt"), "b");
    // no second entry; the one entry names both, but only T01's `eject` line makes it T01's repair
    assert_eq!(repairs::read(&w.common).len(), 1);
    assert_eq!(log::repairs_open(&w.common), ["r1"]);
    let ejected: Vec<&Value> = lines.iter().filter(|x| x["event"] == "eject").collect();
    assert_eq!(ejected.len(), 1);
}

/// WHERE THE GATE'S OWN WRITER FILES A CHECK'S LINE IN THE LANE'S TREE (461 T15's closing half): a `Phase` line written through
/// `append_row_with` with no task and no feature of its own, under the runner's `SPECIFY_FEATURE` and with a stale `feature.json`
/// naming another feature, lands in the log the attribution reads - the registry's lane tree is no pool tree, so no holder files it.
#[test]
fn a_check_s_phase_line_in_the_lane_s_tree_is_filed_where_the_attribution_reads_it() {
    use l7r_shared::guards::event_log_hooks::{append_row_with, log_path_in, now_stamp, phase_row};
    let w = world("lane-run-filed");
    let land = w.dir.path().join("repo-land");
    put(&land, "specs/999-other/tasks.md", "- [ ] T01 x\n");
    put(
        &land,
        ".specify/feature.json",
        r#"{"feature_directory": "specs/999-other"}"#,
    );
    let env = |k: &str| (k == "SPECIFY_FEATURE").then(|| "461-x".to_owned());
    let t0 = now_stamp(std::time::SystemTime::now());
    let began = std::time::SystemTime::now();
    let mut row = phase_row(
        "rust",
        "test",
        (began, std::time::SystemTime::now()),
        101,
        "done",
        &land,
    );
    row.insert("crates".into(), json!(["lib/two"]));
    let filed = append_row_with(&land, None, row, &env).unwrap();
    let read = log_path_in(&land, "461-x", &env);
    assert_eq!(filed, read);
    let t1 = now_stamp(std::time::SystemTime::now() + std::time::Duration::from_millis(5));
    let units: Vec<String> = crate::attribute::reds(&log::lines_of(&read), (&t0, &t1), &land, "")
        .into_iter()
        .map(|r| r.unit)
        .collect();
    assert_eq!(units, ["lib/two test"]);
}

/// 461 T15's plan review: a first-pass refusal naming no change of the batch (a hold, a lock) ejects nothing - the runner stops with
/// the batch open, its line the runner's own `stopped` one; a refusal whose row names a task of the batch ejects that change alone.
#[test]
fn a_first_pass_refusal_naming_no_change_ejects_nothing_and_one_naming_a_task_ejects_its_change() {
    let refusal = "land: refused before anything ran - nothing landed, nothing ticked. Every refusal:\n  @ROW@\n";
    let w = world("lane-run-refused");
    w.hand_in("461", "T01", "a.txt", "a\n");
    w.hand_in("461", "T02", "b.txt", "b\n");
    let row = "another landing holds the clone's lock (pid 42)";
    std::fs::write(w.common.join("refuse"), refusal.replace("@ROW@", row)).unwrap();
    let l = lane_of(&w);
    let err = step(&l).unwrap_err();
    assert!(err.contains("first pass refused at attempt 1, a row naming no change"));
    assert!(err.contains(row), "{err}");
    assert_eq!(w.events(), ["batch", "carry", "run", "owed"]);
    assert_eq!(w.lane()[3][crate::wake::STOPPED], true);
    assert!(repairs::read(&w.common).is_empty());
    assert!(open(&w).open());

    let w = world("lane-run-refused-task");
    let one = w.hand_in("461", "T01", "a.txt", "a\n");
    let two = w.hand_in("461", "T02", "b.txt", "b\n");
    let named = refusal.replace("@ROW@", "T02: owes its claims round");
    std::fs::write(w.common.join("refuse"), named).unwrap();
    let l = lane_of(&w);
    // the refusal names T02, whose change is ejected; the next attempt, refused again, names no change left, so the runner stops
    let err = step(&l).unwrap_err();
    assert!(err.contains("first pass refused at attempt 2"), "{err}");
    let lines = w.lane();
    let eject = lines.iter().find(|x| x["event"] == "eject").unwrap();
    assert_eq!(eject["change"], json!(two));
    assert_eq!(eject["why"], "red");
    let units = repairs::read(&w.common)[0]["units"].clone();
    assert_eq!(units, json!(["first-pass T02: owes its claims round"]));
    let b = open(&w);
    let left = crate::runner::remaining(&b, &std::collections::BTreeSet::new());
    assert_eq!(left, [one]);
}

/// 461 T15's plan review, round 2: a first-pass row naming two changes of the batch ejects those two as one entry and the rest runs
/// again; a row naming one beside a row naming none stops the batch, nothing ejected.
#[test]
fn a_first_pass_row_naming_two_changes_ejects_both_and_the_rest_lands() {
    let refusal = "land: refused before anything ran - nothing landed, nothing ticked. Every refusal:\n  @ROW@\n";
    let w = world("lane-run-refused-two");
    let one = w.hand_in("461", "T01", "a.txt", "a\n");
    let two = w.hand_in("461", "T02", "b.txt", "b\n");
    let three = w.hand_in("461", "T03", "c.txt", "c\n");
    let row = refusal.replace("@ROW@", "T01, T02: owe their claims round");
    std::fs::write(w.common.join("refuse"), &row).unwrap();
    // the refusal is the first attempt's alone: the stand-in's own rule drops it once a run reads it
    std::fs::write(w.common.join("refuse-once"), "").unwrap();
    let l = lane_of(&w);
    assert_eq!(step(&l), Ok(true));
    let lines = w.lane();
    let ejected: Vec<&Value> = lines
        .iter()
        .filter(|x| x["event"] == "eject")
        .map(|x| &x["change"])
        .collect();
    assert_eq!(ejected, [&json!(one), &json!(two)]);
    let entries = repairs::read(&w.common);
    assert_eq!(entries.len(), 1);
    assert_eq!(entries[0]["ejected"], json!([one, two]));
    assert_eq!(entries[0]["why"], "unplaced");
    let end = lines.iter().rev().find(|x| x["event"] == "landed").unwrap();
    assert_eq!(end["landed"], json!([three]));

    let w = world("lane-run-refused-mixed");
    w.hand_in("461", "T01", "a.txt", "a\n");
    let mixed = refusal.replace(
        "@ROW@",
        "T01: owes its claims round\n  the clone's lock is held (pid 42)",
    );
    std::fs::write(w.common.join("refuse"), mixed).unwrap();
    let err = step(&lane_of(&w)).unwrap_err();
    assert!(err.contains("(first-pass the clone's lock is held (pid 42))"));
    assert!(repairs::read(&w.common).is_empty());
}

#[test]
fn the_runner_s_environment_is_the_process_s() {
    assert_eq!(super::process_env("PATH"), std::env::var("PATH").ok());
}

#[test]
fn a_killed_runner_s_open_batch_resumes_as_its_next_attempt() {
    let w = world("lane-run-resume-two");
    let one = w.hand_in("461", "T01", "a.txt", "a\n");
    let l = lane_of(&w);
    for (event, fields) in [
        ("batch", json!({"batch": "461-1", "changes": [one]})),
        (
            "run",
            json!({"batch": "461-1", "n": 1, "set": [&one[..10]], "code": -1}),
        ),
    ] {
        log::append(&w.common, "t", event, &fields).unwrap();
    }
    let b = open(&w);
    resume(&l, &b, &b.changes).unwrap();
    let lines = w.lane();
    let run = lines.iter().rev().find(|x| x["event"] == "run").unwrap();
    assert_eq!(run["n"], 2);
    assert!(run["attempt"].as_str().unwrap().ends_with("461-1-2.log"));
    assert_eq!(lines.last().unwrap()["event"], "owed");
    assert!(lines
        .iter()
        .any(|x| x["event"] == "landed" && x["runs"] == 2));
    assert_eq!(w.origin_holds("a.txt"), "a");
}

#[test]
fn a_resumed_batch_origin_main_already_holds_lands_with_no_run() {
    let w = world("lane-run-resumed");
    let one = w.hand_in("461", "T01", "a.txt", "a\n");
    let l = lane_of(&w);
    assert_eq!(step(&l), Ok(true));
    // a batch whose push went out before its runner was killed: its change on origin/main, its ref still standing
    git(&w.clone, &["update-ref", "refs/l7r/done/461-T01", &one]);
    log::append(
        &w.common,
        "t",
        "batch",
        &json!({"batch": "461-2", "changes": [one]}),
    )
    .unwrap();
    let b = open(&w);
    resume(&l, &b, &b.changes).unwrap();
    assert_eq!(&w.events()[6..], ["batch", "landed", "owed"]);
    assert_eq!(w.lane()[7]["runs"], 0);
    assert_eq!(w.refs(), "");
}

#[test]
fn a_carry_that_stops_names_its_conflict_and_leaves_the_batch_open() {
    let w = world("lane-run-conflict");
    w.hand_in("461", "T01", "a.txt", "one\n");
    w.hand_in("461", "T02", "a.txt", "two\n");
    let stopped = step(&lane_of(&w)).unwrap_err();
    assert!(stopped.contains("the carry of"), "{stopped}");
    assert!(stopped.contains("conflicting: a.txt"), "{stopped}");
    let carry = w.lane().pop().unwrap();
    assert_eq!(carry["event"], "carry");
    assert_eq!(carry["conflict"], json!(["a.txt"]));
    assert_ne!(carry["code"], 0);
    assert!(open(&w).open());
}

#[test]
fn a_batch_with_no_lane_s_tree_no_spec_directory_or_an_unknown_change_is_an_error() {
    let w = world("lane-run-errors");
    w.hand_in("999", "T01", "a.txt", "a\n");
    let l = lane_of(&w);
    // the spec directory missing from the lane's tree: the error names it, the batch open
    let none = step(&l).unwrap_err();
    assert!(none.contains("no single specs/999-* directory"), "{none}");
    let b = open(&w);
    // a change no hand-in names
    let unknown = resume(&l, &b, &["ffffffffff".to_owned()]).unwrap_err();
    assert!(unknown.contains("change ffffffffff is no hand-in"));
    // no lane's tree in the pool: builder-tree lane's refusal
    builder_pool::write(&w.common, &[]).unwrap();
    let gone = resume(&l, &b, &b.changes).unwrap_err();
    assert!(gone.contains("no lane's tree is in the pool"), "{gone}");
}

#[test]
fn an_attempt_file_that_cannot_be_written_is_an_error_naming_it() {
    let w = world("lane-run-attempt");
    w.hand_in("461", "T01", "a.txt", "a\n");
    std::fs::create_dir_all(w.common.join("l7r-lane")).unwrap();
    std::fs::write(w.common.join("l7r-lane/attempts"), "").unwrap();
    let err = step(&lane_of(&w)).unwrap_err();
    assert!(err.contains("attempts/461-1-1.log"), "{err}");
}

#[test]
fn a_landing_that_pushed_with_other_edits_merged_is_landed_though_make_ends_two() {
    let w = world("lane-run-merged");
    let one = w.hand_in("461", "T01", "a.txt", "a\n");
    std::fs::write(w.common.join("merged"), "").unwrap();
    assert_eq!(step(&lane_of(&w)), Ok(true));
    let lines = w.lane();
    assert_eq!(lines[2]["code"], 2);
    assert_eq!(lines[3]["event"], "push");
    assert_eq!(lines[4]["landed"], json!([one]));
    assert_eq!(w.refs(), "");
}

/// A stand-in for the lane tree's `scripts/gates/l7r-gate.sh`, committed into the world so the reset keeps it: it "builds" where the
/// tree's HEAD is not the one it last built at (a line in `<common>/builds`), or fails as cargo does where `<common>/build-fails`
/// exists - its marks in the git common directory, which the reset's `clean` does not reach.
const LAUNCHER: &str = "#!/bin/sh\n\
t=$(cd \"$(dirname \"$0\")/../..\" && pwd)\n\
c=$(git -C \"$t\" rev-parse --path-format=absolute --git-common-dir)\n\
[ -e \"$c/build-fails\" ] && { echo 'error[E0425]: cannot find value `x`' >&2; exit 1; }\n\
h=$(git -C \"$t\" rev-parse HEAD)\n\
[ \"$(cat \"$c/built\" 2>/dev/null)\" = \"$h\" ] || { echo \"$h\" > \"$c/built\"; echo \"built $h\" >> \"$c/builds\"; }\n\
echo \"$0\"\n";

impl World {
    /// `origin/main` moved by a commit of `file` that no batch carries, as another landing moves it.
    fn origin_moves(&self, file: &str) -> String {
        git(&self.clone, &["fetch", "-q", "origin"]);
        git(&self.clone, &["checkout", "-q", "--detach", "origin/main"]);
        put(&self.clone, file, "moved\n");
        git(&self.clone, &["add", "-A"]);
        git(&self.clone, &["commit", "-qm", "landed elsewhere"]);
        git(&self.clone, &["push", "-q", "origin", "HEAD:main"]);
        git(&self.clone, &["rev-parse", "HEAD"])
    }

    fn builds(&self) -> Vec<String> {
        std::fs::read_to_string(self.common.join("builds"))
            .unwrap_or_default()
            .lines()
            .map(str::to_owned)
            .collect()
    }
}

#[test]
fn a_reset_with_nothing_to_carry_leaves_the_lane_tree_s_launcher_built_so_the_next_start_builds_nothing(
) {
    let w = world("lane-run-prebuild");
    let script = w.clone.join("scripts/gates/l7r-gate.sh");
    std::fs::create_dir_all(script.parent().unwrap()).unwrap();
    l7r_gate_core::write_executable(&script, LAUNCHER);
    git(&w.clone, &["add", "-A"]);
    git(&w.clone, &["commit", "-qm", "the launcher"]);
    git(&w.clone, &["push", "-q", "origin", "main"]);
    let one = w.hand_in("461", "T01", "a.txt", "a\n");
    let l = lane_of(&w);
    assert_eq!(step(&l), Ok(true));
    // a batch whose change origin/main already holds, after a landing elsewhere moved it: the reset moves the tree, nothing is carried
    let moved = w.origin_moves("rust/x.rs");
    log::append(
        &w.common,
        "t",
        "batch",
        &json!({"batch": "461-2", "changes": [one]}),
    )
    .unwrap();
    resume(&l, &open(&w), &[one.clone()]).unwrap();
    assert_eq!(&w.events()[6..], ["batch", "landed", "owed"]);
    assert_eq!(w.builds().last().cloned(), Some(format!("built {moved}")));
    // the next start's own build (461 T51) finds the launcher fresh: no build in a hand-in's foreground
    let tree = builder_pool::read_all(&w.common)[0].tree.clone();
    let before = w.builds().len();
    assert_eq!(
        crate::runner::prebuild(&tree.join("scripts/gates/l7r-gate.sh")),
        Ok(())
    );
    assert_eq!(w.builds().len(), before);
    // a build that fails at the reset stops no batch: the carry's own launcher, or the next start, says why
    std::fs::write(w.common.join("build-fails"), "").unwrap();
    w.origin_moves("rust/y.rs");
    log::append(
        &w.common,
        "t",
        "batch",
        &json!({"batch": "461-3", "changes": [one]}),
    )
    .unwrap();
    resume(&l, &open(&w), &[one]).unwrap();
    assert_eq!(&w.events()[9..], ["batch", "landed", "owed"]);
    assert_eq!(w.builds().len(), before);
}

/// The push's own line the stand-in prints, as a repair entry of kind `integrate` names it.
const PUSH_FAILED: &str = "land: the push failed (exit 1) - its ticks reverted";

#[test]
fn a_green_batch_whose_push_fails_twice_files_one_integrate_entry_and_one_owed_line() {
    let w = world("lane-run-push-twice");
    let one = w.hand_in("461", "T01", "a.txt", "a\n");
    let two = w.hand_in("461", "T02", "b.txt", "b\n");
    std::fs::write(w.common.join("push-fail"), "").unwrap();
    let l = lane_of(&w);
    assert_eq!(step(&l), Ok(true));
    assert_eq!(
        w.events(),
        [
            "batch", "carry", "run", "push", "carry", "run", "push", "eject", "eject", "landed",
            "owed"
        ]
    );
    let lines = w.lane();
    for (run, push, n) in [(&lines[2], &lines[3], 1), (&lines[5], &lines[6], 2)] {
        assert_eq!(run["n"], n);
        assert_eq!(run["red"], json!([]));
        assert_eq!(push["failed"], true);
        assert_eq!(push["set"], json!([&one[..10], &two[..10]]));
    }
    let attempt = lines[5]["attempt"].as_str().unwrap().to_owned();
    assert!(attempt.ends_with("l7r-lane/attempts/461-1-2.log"));
    for (line, sha) in [(&lines[7], &one), (&lines[8], &two)] {
        assert_eq!(line["change"], json!(sha));
        assert_eq!(line["repair"], "r1");
        assert_eq!(line["why"], "push");
    }
    let owed: Vec<&Value> = lines.iter().filter(|x| x["event"] == "owed").collect();
    assert_eq!(owed.len(), 1);
    assert_eq!(owed[0].get(crate::wake::STOPPED), None);
    assert_eq!(
        owed[0]["line"],
        format!("lane: batch 461-1 green but its push failed twice - 461 T01 T02 filed as repair r1 (integrate, push: {PUSH_FAILED}) - make builder-next hands it to a fresh builder: {attempt}")
    );
    assert_eq!(lines[9]["landed"], json!([]));
    assert_eq!(lines[9]["ejected"], json!([one, two]));
    assert_eq!(lines[9]["runs"], 2);
    let entries = repairs::read(&w.common);
    assert_eq!(entries.len(), 1);
    let mut entry = entries[0].clone();
    entry.as_object_mut().unwrap().remove("utc");
    assert_eq!(
        entry,
        json!({"repair": "r1", "feature": "461-x", "tasks": ["T01", "T02"], "kind": "integrate", "ejected": [one, two],
            "batch": "461-1", "why": "push", "units": [PUSH_FAILED], "attempt": attempt})
    );
    // the batch ended, not stopped: nothing ticked on origin, both refs kept for the repair, no batch formed again
    assert!(w
        .origin_holds("specs/461-x/tasks.md")
        .starts_with("- [ ] T01 one\n- [ ] T02 two"));
    assert_eq!(w.refs(), "refs/l7r/done/461-T01\nrefs/l7r/done/461-T02");
    assert!(!log::batches(&w.lane()).iter().any(Batch::open));
    std::fs::remove_file(w.common.join("push-fail")).unwrap();
    assert_eq!(step(&l), Ok(false));
}

#[test]
fn a_push_that_fails_once_runs_the_batch_again_on_the_new_origin_main_and_lands() {
    let w = world("lane-run-push-once");
    let one = w.hand_in("461", "T01", "a.txt", "a\n");
    for f in ["push-fail", "push-fail-once"] {
        std::fs::write(w.common.join(f), "").unwrap();
    }
    assert_eq!(step(&lane_of(&w)), Ok(true));
    assert_eq!(
        w.events(),
        ["batch", "carry", "run", "push", "carry", "run", "push", "landed", "owed"]
    );
    let lines = w.lane();
    assert_eq!(lines[3]["failed"], true);
    assert_eq!(lines[6].get("failed"), None);
    assert_eq!(lines[7]["landed"], json!([one]));
    assert_eq!(
        lines[8]["line"],
        "lane: batch 461-1 landed - 461 T01 (1 change(s), 2 run(s), 0 minutes)"
    );
    // another writer's commit, pushed while the first push failed, is under the landing: the tree was brought to the new main
    assert_eq!(w.origin_holds("a.txt"), "a");
    git(&w.clone, &["fetch", "-q", "origin"]);
    assert_eq!(
        git(&w.clone, &["log", "--format=%s", "-3", "origin/main"]),
        "461-x: T01 ticked (make land)\n461 T01: work\nother"
    );
    assert!(repairs::read(&w.common).is_empty());
}

#[test]
fn a_resumed_batch_whose_push_had_failed_once_files_the_integrate_entry_at_its_next_failure() {
    let w = world("lane-run-push-resumed");
    let one = w.hand_in("461", "T01", "a.txt", "a\n");
    let set = json!([&one[..10]]);
    for (event, fields) in [
        ("batch", json!({"batch": "461-1", "changes": [one]})),
        (
            "run",
            json!({"batch": "461-1", "n": 1, "set": set, "code": 2}),
        ),
        (
            "push",
            json!({"batch": "461-1", "set": set, "code": 2, "failed": true}),
        ),
    ] {
        log::append(&w.common, "t", event, &fields).unwrap();
    }
    std::fs::write(w.common.join("push-fail"), "").unwrap();
    let b = open(&w);
    resume(&lane_of(&w), &b, &b.changes).unwrap();
    assert_eq!(
        &w.events()[3..],
        ["carry", "run", "push", "eject", "landed", "owed"]
    );
    let entries = repairs::read(&w.common);
    assert_eq!(entries.len(), 1);
    assert_eq!(entries[0]["kind"], "integrate");
    assert_eq!(entries[0]["why"], "push");
    assert!(entries[0]["attempt"]
        .as_str()
        .unwrap()
        .ends_with("461-1-2.log"));
}

mod tripwire;
