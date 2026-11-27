//! The batch run end to end (feature 461 T14) on a scratch world: a clone, a bare `origin`, the lane's tree in the pool's registry
//! and two pool trees, the landing a stand-in `make land` in the clone's own Makefile that ticks and pushes as the real one does. Two
//! hand-ins, one batch, one push, both ticked, both done refs deleted, one `owed` line; a red run left open and resumed as attempt 2;
//! a resumed batch already on `origin/main` landed with no run; a carry that stops; the errors.

use std::fmt::Write as _;
use std::path::PathBuf;

use l7r_gate_core::ci::fixtures::{git, put, scratch};
use l7r_shared::builder_pool::{self, Tree};
use l7r_shared::tempdir::TempDir;
use serde_json::{json, Value};

use super::{resume, step, Lane};
use crate::log::{self, Batch};

const MAKEFILE: &str = "carry:\n\tgit cherry-pick $(COMMIT)\nland:\n\t@if [ -f \"$$(git rev-parse --git-common-dir)/red\" ]; then echo red; exit 1; fi\n\t@echo \"land F=$(F) T=$(T) NOTE=$(NOTE) batch=$$L7R_LANE_BATCH spec=$$SPECIFY_FEATURE alone=$$L7R_LAND_ALONE backup=$$SYNC_BACKUP\"\n\tfor t in $(T); do sed -i \"s/^- \\[ \\] $$t /- [x] $$t /\" specs/461-x/tasks.md; done\n\tgit commit -qam \"461-x: $(T) ticked (make land)\"\n\tgit push -q origin HEAD:main\n\t@if [ -f \"$$(git rev-parse --git-common-dir)/merged\" ]; then exit 3; fi\n";

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
    put(&clone, "Makefile", MAKEFILE);
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

fn now() -> f64 {
    1000.0
}

fn lane_of(w: &World) -> Lane<'_> {
    Lane {
        common: &w.common,
        now: &now,
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
fn a_red_run_stops_the_step_with_its_owed_line_and_its_resume_is_attempt_two() {
    let w = world("lane-run-red");
    w.hand_in("461", "T01", "a.txt", "a\n");
    std::fs::write(w.common.join("red"), "").unwrap();
    let l = lane_of(&w);
    let red = step(&l).unwrap_err();
    assert!(
        red.starts_with("lane: batch 461-1 red at attempt 1 (make land exit 2)"),
        "{red}"
    );
    assert!(red.ends_with("l7r-lane/attempts/461-1-1.log"));
    assert_eq!(w.events(), ["batch", "carry", "run", "owed"]);
    assert_eq!(w.lane()[3]["line"], red);
    // the batch open: no step forms or runs again, every poll
    assert_eq!(step(&l), Ok(false));
    std::fs::remove_file(w.common.join("red")).unwrap();
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
    assert!(
        unknown.contains("change ffffffffff is no hand-in"),
        "{unknown}"
    );
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
