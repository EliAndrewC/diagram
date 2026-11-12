//! `l7r-gate land` on scratch repositories (feature 449 T121): a clone with a bare origin, every tool the landing runs a stub that logs
//! its call and answers from files a test writes, and the in-process questions answered by [`Fake`]. `scratchpad/t83s5/` compares the
//! port with `land.py` over the same inputs and replays recorded landings through both. The tick and the first pass's tick check are
//! the task gate's own, in process (feature 449 T131): each test's tasks are real, and so are their refusals.

use std::cell::RefCell;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::rc::Rc;
use std::time::Duration;

use l7r_gate_core::ci::fixtures::{git, put, scratch};
use l7r_gate_core::write_executable;
use l7r_guard::shared::tempdir::TempDir;

use super::inproc::Inproc;
use super::Land;
use crate::Reply;

/// Every stub: logs `<name> <args>` to `$STUB_DIR/log`, answers from `$STUB_DIR/<key>.{out,err,rcs,rc,sh}` (the key: the line, every
/// character but `[A-Za-z0-9._=-]` an underscore). Run as `python`, its name is the script's, or the module's after `-m`; as `ruff`
/// with no `.out` it echoes its input.
const STUB: &str = r#"#!/bin/sh
name=$(basename "$0")
if [ "$name" = python ]; then
  if [ "$1" = -m ]; then name="$2"; shift 2; else name=$(basename "$1"); shift; fi
fi
if [ $# -gt 0 ]; then line="$name $*"; else line="$name"; fi
printf '%s\n' "$line" >> "$STUB_DIR/log"
key=$(printf '%s' "$line" | tr -c 'A-Za-z0-9._=-' '_')
f="$STUB_DIR/$key"
[ -f "$f.sh" ] && . "$f.sh"
if [ "$name" = ruff ] && [ ! -f "$f.out" ] && [ ! -f "$f.rc" ]; then cat; exit 0; fi
[ -f "$f.out" ] && cat "$f.out"
[ -f "$f.err" ] && cat "$f.err" >&2
if [ -f "$f.rcs" ]; then
  rc=$(head -n1 "$f.rcs"); tail -n +2 "$f.rcs" > "$f.rcs.t"; mv "$f.rcs.t" "$f.rcs"; exit "${rc:-0}"
fi
[ -f "$f.rc" ] && exit "$(cat "$f.rc")"
exit 0
"#;

/// The stub's key of a call line.
pub(super) fn key(line: &str) -> String {
    line.chars()
        .map(|c| {
            if c.is_ascii_alphanumeric() || "._=-".contains(c) {
                c
            } else {
                '_'
            }
        })
        .collect()
}

/// The in-process answers a test hands the landing, and what it asked.
#[derive(Default)]
pub(super) struct Answers {
    /// `claims <verb>` -> its reply's (code, stdout).
    pub claims: RefCell<HashMap<String, (i32, String)>>,
    /// `ledger-owed`: the reply of a listing (no `--write...`).
    pub ledger: RefCell<String>,
    pub holding: RefCell<String>,
    pub flight: RefCell<Vec<String>>,
    pub flight_fails: RefCell<bool>,
    pub own: RefCell<Vec<String>>,
    pub asked: RefCell<Vec<String>>,
    /// A path the ledger write dirties, as a real write would.
    pub ledger_writes: RefCell<Option<PathBuf>>,
}

pub(super) struct Fake(pub Rc<Answers>);

fn reply(code: i32, stdout: &str) -> Reply {
    Reply {
        stdout: stdout.to_owned(),
        stderr: String::new(),
        code,
    }
}

impl Inproc for Fake {
    fn claims(&self, args: &[String]) -> Reply {
        let verb = args.get(2).cloned().unwrap_or_default();
        self.0
            .asked
            .borrow_mut()
            .push(format!("claims {}", args[2..].join(" ")));
        let (code, out) = self
            .0
            .claims
            .borrow()
            .get(&verb)
            .cloned()
            .unwrap_or((0, String::new()));
        reply(code, &out)
    }

    fn ledger(&self, args: &[String], _root: &Path) -> Reply {
        self.0
            .asked
            .borrow_mut()
            .push(format!("ledger {}", args.join(" ")));
        if args[0].starts_with("--write") {
            if let Some(p) = self.0.ledger_writes.borrow().as_ref() {
                std::fs::write(p, "| a | b |\n").unwrap();
            }
            return reply(0, "");
        }
        reply(0, &self.0.ledger.borrow())
    }

    fn holding(&self, dir: &str, ticks: &str, _root: &Path) -> Reply {
        self.0
            .asked
            .borrow_mut()
            .push(format!("holding {dir} [{ticks}]"));
        reply(0, &self.0.holding.borrow())
    }

    fn in_flight(&self, _root: &Path) -> Result<Vec<String>, String> {
        if *self.0.flight_fails.borrow() {
            return Err("a flight mark that is no JSON".to_owned());
        }
        Ok(self.0.flight.borrow().clone())
    }

    fn scope_split(
        &self,
        _root: &Path,
        report: &str,
        changed: &[String],
        seam: &[String],
    ) -> Result<(Vec<String>, Vec<String>), String> {
        self.0
            .asked
            .borrow_mut()
            .push(format!("split [{report}] {changed:?} {}", seam.len()));
        Ok((self.0.own.borrow().clone(), Vec::new()))
    }
}

/// A landing on a scratch clone.
pub(super) struct Fx {
    pub dir: TempDir,
    pub root: PathBuf,
    pub stub: PathBuf,
    pub answers: Rc<Answers>,
    pub land: Land,
}

impl Fx {
    /// The stub's answer to `line`: `kind` is `out`, `err`, `rc`, `rcs` or `sh`.
    pub fn answer(&self, line: &str, kind: &str, text: &str) {
        std::fs::write(self.stub.join(format!("{}.{kind}", key(line))), text).unwrap();
    }

    /// Every call the stubs logged.
    pub fn log(&self) -> String {
        std::fs::read_to_string(self.stub.join("log")).unwrap_or_default()
    }

    /// What the landing printed: (stdout, stderr).
    pub fn said(&self) -> (String, String) {
        self.land.said.as_ref().unwrap().borrow().clone()
    }

    /// The subjects of the commits since the fixture's first.
    pub fn subjects(&self) -> String {
        git(&self.root, &["log", "--format=%s", "origin/main..HEAD"])
    }

    /// A file committed here, not on origin/main: the delta.
    pub fn in_delta(&self, rel: &str, text: &str) {
        put(&self.root, rel, text);
        git(&self.root, &["add", "-A"]);
        git(&self.root, &["commit", "-qm", rel]);
    }
}

/// A tool of the stub tree as its stub logs it: its file name.
pub(super) fn tool(rel: &str) -> String {
    rel.rsplit('/').next().unwrap_or_default().to_owned()
}

/// The feature every fixture lands.
const PLAN: &str = "# Plan\n\nThe fixture's plan, reviewed CLEAR.\n";
const PLAN_SHA: &str = "8c79c7a920ecbecd5310903d3d791bb5aa08b592d49e976db64a1860cf4334bb";
pub(super) const TASKS: &str = "# Tasks\n\n- [ ] T1 one\n      verify: \n- [ ] T2 two\n";

/// A clone of a bare origin holding `specs/449-x/tasks.md`, the stub tools, the landing with its output captured.
pub(super) fn fx(tag: &str) -> Fx {
    let dir = scratch(tag);
    let origin = dir.join("origin.git");
    let root = dir.join("repo");
    std::fs::create_dir_all(&root).unwrap();
    git(
        &dir,
        &[
            "init",
            "-q",
            "--bare",
            "-b",
            "main",
            &origin.to_string_lossy(),
        ],
    );
    git(&root, &["init", "-q", "-b", "main"]);
    git(&root, &["config", "user.email", "t@t"]);
    git(&root, &["config", "user.name", "t"]);
    git(&root, &["config", "commit.gpgsign", "false"]);
    git(
        &root,
        &["remote", "add", "origin", &origin.to_string_lossy()],
    );
    put(&root, "specs/449-x/tasks.md", TASKS);
    // a plan reviewed CLEAR, so the tick's plan gate passes in process (feature 449 T131); the record's digest is the plan's sha256
    put(&root, "specs/449-x/plan.md", PLAN);
    put(
        &root,
        "specs/449-x/plan-review.json",
        &format!(
            "{{\"plan_sha256\": \"{PLAN_SHA}\", \"verdict\": \"CLEAR\", \"decisions\": []}}\n"
        ),
    );
    put(&root, "dev/review-ledger.md", "| ledger |\n");
    put(&root, "dev/bypass-log/.keep", "");
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "start"]);
    git(&root, &["push", "-q", "-u", "origin", "main"]);
    let stub = dir.join("stub");
    std::fs::create_dir_all(&stub).unwrap();
    let scripts = dir.join("tree/scripts");
    for tool in [
        "gates/l7r-gate.sh",
        "gates/claims-gate.sh",
        "gates/review-gate.sh",
        "gates/plan-gate.sh",
        "sync-with-main.sh",
    ] {
        std::fs::create_dir_all(scripts.join(tool).parent().unwrap()).unwrap();
        write_executable(&scripts.join(tool), STUB);
    }
    let bin = dir.join("bin");
    std::fs::create_dir_all(&bin).unwrap();
    write_executable(&bin.join("python"), STUB);
    write_executable(&bin.join("make"), STUB);
    let answers = Rc::new(Answers::default());
    let mut land = Land::new(&root, &scripts);
    land.python = bin.join("python").to_string_lossy().into_owned();
    land.make = bin.join("make").to_string_lossy().into_owned();
    land.said = Some(RefCell::default());
    land.claims_wait = Duration::from_millis(400);
    land.claims_poll = Duration::from_millis(20);
    land.cgroup = dir.join("cgroup");
    land.memwatch = dir.join("memwatch");
    land.meminfo = dir.join("meminfo");
    land.cpus = Some(16);
    land.boxes = false;
    land.arbiter_ok = false;
    land.inproc = Box::new(Fake(Rc::clone(&answers)));
    land.export("STUB_DIR", &stub.to_string_lossy());
    Fx {
        dir,
        root,
        stub,
        answers,
        land,
    }
}

pub(super) const NOTE: &str = "checked";

fn tasks(t: &[&str]) -> Vec<String> {
    t.iter().map(|s| (*s).to_owned()).collect()
}

/// The landing of `T1`, start to end.
fn land(fx: &Fx) -> Result<i32, String> {
    fx.land
        .land(&fx.root.join("specs/449-x"), &tasks(&["T1"]), NOTE)
}

#[test]
fn a_clean_landing_ticks_pushes_once_and_says_so() {
    let fx = fx("land-clean");
    assert_eq!(land(&fx), Ok(0));
    let (out, err) = fx.said();
    assert!(out.contains("ticked - [x] T1 one\n1 task(s) still open in specs/449-x/tasks.md\n"));
    assert!(out.ends_with("land: T1 landed and ticked\n"));
    let tasks = std::fs::read_to_string(fx.root.join("specs/449-x/tasks.md")).unwrap();
    assert!(tasks.contains("- [x] T1 one\n      verify: DONE. landed: checked\n"));
    assert!(err.is_empty());
    assert!(fx.subjects().contains("449-x: T1 ticked (make land)"));
    let log = fx.log();
    assert!(log.contains("sync-with-main.sh done"));
    assert!(log.contains("stamp --check origin/main"));
    let asked = fx.answers.asked.borrow().join("\n");
    assert!(asked.contains("holding"));
    assert!(asked.contains("claims rekey"));
}

#[test]
fn every_cheap_refusal_is_said_together_and_nothing_runs_long() {
    let fx = fx("land-refused");
    put(&fx.root, "untracked.txt", "x");
    *fx.answers.holding.borrow_mut() = "T9 nine  <- the active task\n".to_owned();
    *fx.answers.ledger.borrow_mut() = "| ? | owed |\n".to_owned();
    fx.answer(&tool("gates/review-gate.sh"), "rc", "1");
    fx.answer(
        &tool("gates/review-gate.sh"),
        "out",
        "a review is owed\npre-existing x\n",
    );
    assert_eq!(land(&fx), Ok(2));
    let err = fx.said().1;
    assert!(err.starts_with("land: refused before anything ran"));
    assert!(err.contains("uncommitted changes - commit them first"));
    assert!(err.contains("held by T9 nine"));
    assert!(err.contains("review passes with no ledger row"));
    assert!(err.contains("review-gate.sh: a review is owed"));
    assert!(!fx.log().contains("stamp --check"));
}

#[test]
fn a_claims_round_owed_runs_beside_the_gate_and_its_wait_can_stop_the_landing() {
    let fx = fx("land-claims-owed");
    fx.answers.flight.borrow_mut().push("bundle".to_owned());
    fx.answer(&tool("gates/claims-gate.sh"), "rc", "1");
    fx.answer(
        &tool("gates/claims-gate.sh"),
        "out",
        "claims-gate: REFUSED owed (impl-drift) k\n",
    );
    assert_eq!(land(&fx), Ok(2));
    let (out, err) = fx.said();
    assert!(out
        .starts_with("land: the claims round is owed (claims-gate.sh: claims-gate: REFUSED owed"));
    assert!(err.contains("did not finish in 20 min"));
}

#[test]
fn a_red_long_run_stops_before_the_ticks() {
    let fx = fx("land-red");
    fx.answer(
        &format!("{} stamp --check origin/main", tool("gates/l7r-gate.sh")),
        "rc",
        "1",
    );
    fx.answer("make --no-print-directory done NO_CUTOFF=1", "rc", "2");
    assert_eq!(land(&fx), Ok(1));
    assert!(fx.said().1.contains("land: make done is red"));
    assert!(!fx.log().contains("sync-with-main.sh"));
}

#[test]
fn a_refused_tick_puts_every_tick_back_and_a_raise_ends_the_landing() {
    // T2's tick would close the feature, and the closing check, asked at the tick alone, refuses it: no report
    let fx = fx("land-tick");
    let two = tasks(&["T1", "T2"]);
    let d = fx.root.join("specs/449-x");
    assert_eq!(fx.land.land(&d, &two, NOTE), Ok(2));
    let (out, err) = fx.said();
    assert!(out.contains("ticked - [x] T1 one"));
    assert!(err.contains("this tick would close the feature, and:\n  449-x has no report.md"));
    assert!(err.contains("land: T2 refused its tick (above)"));
    assert_eq!(std::fs::read_to_string(d.join("tasks.md")).unwrap(), TASKS);
    // a closing check that raises ends the landing
    put(&d, "report.md", "# r\n");
    put(&d, "measurements.json", "5");
    git(&fx.root, &["add", "-A"]);
    git(
        &fx.root,
        &["commit", "-qm", "a record the closing check cannot read"],
    );
    let raised = fx.land.land(&d, &two, NOTE).unwrap_err();
    assert!(raised.contains("the tick raised on T2"));
}

#[test]
fn a_push_that_merged_keeps_its_ticks_and_one_that_failed_reverts_them() {
    let fx = fx("land-push");
    fx.answer(&format!("{} done", tool("sync-with-main.sh")), "rc", "3");
    assert_eq!(land(&fx), Ok(3));
    assert!(fx
        .said()
        .1
        .contains("the pull merged other sessions' edits"));
    fx.answer(&format!("{} done", tool("sync-with-main.sh")), "rc", "1");
    // T1 open again, as a fresh landing finds it
    put(&fx.root, "specs/449-x/tasks.md", TASKS);
    git(&fx.root, &["commit", "-qam", "T1 open again"]);
    assert_eq!(land(&fx), Ok(1));
    assert!(fx
        .said()
        .1
        .contains("land: the push failed (exit 1) - its ticks reverted"));
}

#[test]
fn an_engine_landing_starts_the_fresh_block_and_shows_the_work_budget() {
    let fx = fx("land-engine");
    fx.in_delta("l7r/diagram/a.py", "x = 1\n");
    fx.answer(
        &format!("{} cohort rust-owed", tool("gates/l7r-gate.sh")),
        "rc",
        "1",
    );
    fx.answer(
        &format!("{} cohort counter-only", tool("gates/l7r-gate.sh")),
        "rc",
        "1",
    );
    assert_eq!(land(&fx), Ok(0));
    let out = fx.said().0;
    assert!(out.contains("land: the cohort's fresh block started after the push"));
    assert!(out.contains("work budget: no standing record yet"));
    // a work-budget run that is no JSON fails the landing after its push, as the import raised
    let fx = fx_engine_with_budget("land-engine-budget", "{");
    assert!(land(&fx).is_err());
}

fn fx_engine_with_budget(tag: &str, run: &str) -> Fx {
    let fx = fx(tag);
    fx.in_delta("l7r/diagram/a.py", "x = 1\n");
    put(
        &fx.root,
        "dev/work-budget.md",
        "| stage | status |\n|---|---|\n",
    );
    put(&fx.root, "dev/work-budget/1.json", run);
    put(&fx.root, "dev/work-budget/2.json", run);
    git(&fx.root, &["add", "-A"]);
    git(&fx.root, &["commit", "-qm", "budget"]);
    fx.answer(
        &format!("{} cohort rust-owed", tool("gates/l7r-gate.sh")),
        "rc",
        "1",
    );
    fx.answer(
        &format!("{} cohort port", tool("gates/l7r-gate.sh")),
        "out",
        "rust-only\n",
    );
    fx
}

#[test]
fn the_fresh_block_follows_only_an_engine_landing_that_adds_more_than_counters() {
    let fx = fx("land-fresh");
    assert_eq!(fx.land.fresh_block_after(false, false), Ok(String::new()));
    assert!(fx
        .land
        .fresh_block_after(true, true)
        .unwrap()
        .contains("counter-only"));
    fx.answer(
        &format!("{} cohort port", tool("gates/l7r-gate.sh")),
        "out",
        "rust-only\n",
    );
    assert_eq!(fx.land.fresh_block_after(true, false), Ok(String::new()));
    assert!(fx.land.counter_only().unwrap());
    fx.answer(
        &format!("{} cohort counter-only", tool("gates/l7r-gate.sh")),
        "rc",
        "1",
    );
    assert!(!fx.land.counter_only().unwrap());
    // a git directory the log cannot be opened in
    let mut broken = fx;
    broken.land.root = broken.dir.join("no-such");
    assert!(broken.land.start_fresh_block().is_err());
}

#[test]
fn the_helpers_read_as_the_python_did() {
    assert_eq!(super::head("abcdef", 3), "abc");
    assert_eq!(super::tail("abcdef", 2), "ef");
    assert_eq!(super::tail("ab", 5), "ab");
    assert_eq!(super::rel_of(Path::new("/a"), Path::new("/a/b/c")), "b/c");
    assert_eq!(super::name_of(Path::new("/")), "");
    assert_eq!(
        super::git_dir_of("  \n", Path::new("/r")),
        PathBuf::from("/r/.git")
    );
    assert_eq!(
        super::git_dir_of("/g\n", Path::new("/r")),
        PathBuf::from("/g")
    );
    assert!(super::reverted(0, "", "abc").starts_with("its ticks reverted"));
    assert!(super::reverted(1, "", "0123456789ab")
        .contains("(git revert exited 1): the tick commit 012345678 "));
    assert!(super::reverted(1, "error: x\nmore\n", "abc").contains("(error: x)"));
    assert!(super::decode(&[0xff]).is_err());
    assert!(super::spawn_error("p", &std::io::Error::other("x")).contains("'p'"));
    assert!(!super::set("L7R_LAND_TEST_SURELY_UNSET"));
    let dir = scratch("land-read");
    put(&dir, "a.txt", "a\r\nb\rc");
    assert_eq!(super::py_read(&dir.join("a.txt")).unwrap(), "a\nb\nc");
    std::fs::write(dir.join("b.txt"), [0xff]).unwrap();
    assert!(super::py_read(&dir.join("b.txt")).is_err());
    assert!(super::py_read(&dir.join("none")).is_err());
}

#[test]
fn main_refuses_what_land_py_refused_before_it_landed() {
    let fx = fx("land-main");
    let scripts = |_: &Path| fx.dir.join("tree/scripts");
    let args = |a: &[&str]| a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    assert_eq!(
        super::main(&args(&["449"]), &fx.root, NOTE, &scripts, &nothing),
        Ok(2)
    );
    assert_eq!(
        super::main(&args(&["449", " "]), &fx.root, NOTE, &scripts, &nothing),
        Ok(2)
    );
    assert_eq!(
        super::main(&args(&["449", "T1"]), &fx.root, "  ", &scripts, &nothing),
        Ok(2)
    );
    assert_eq!(
        super::main(&args(&["7", "T1"]), &fx.root, NOTE, &scripts, &nothing),
        Ok(2)
    );
    // a landing from main whose tasks.md cannot be read: the first pass raises before any tool runs
    std::fs::write(fx.root.join("specs/449-x/tasks.md"), [0xff]).unwrap();
    assert!(super::main(&args(&["449", "T1"]), &fx.root, NOTE, &scripts, &nothing).is_err());
}

#[test]
fn the_command_line_records_its_run_and_reports_a_raise() {
    let fx = fx("land-cli");
    assert_eq!(super::reply(3).code, 3);
    let r = super::raised("why");
    assert_eq!((r.code, r.stderr.ends_with("why\n")), (1, true));
    super::record(&fx.root, 0);
    super::record(&fx.root, 2);
    super::record(&fx.dir, 0);
    let usage = std::fs::read_to_string(fx.root.join(".git/tool-usage.jsonl")).unwrap();
    assert!(usage.contains("\"passed\"") && usage.contains("\"refused\""));
    assert_eq!(super::cli(&["only-one".to_owned()], &fx.root).code, 2);
    // `--stop` with no landing running in the tree
    assert_eq!(super::cli(&["--stop".to_owned()], &fx.root).code, 0);
    assert_eq!(super::finish(Err("why".to_owned()), &fx.root).code, 1);
    assert_eq!(super::finish(Ok(0), &fx.root).code, 0);
    assert!(super::scripts_of(&fx.root).ends_with("scripts"));
    super::print_line("a landing's line");
    assert_eq!(super::io(std::io::Error::other("gone")), "gone");
}

/// A TERM catch the tests never install.
fn nothing() {}

#[test]
fn a_landing_with_nothing_captured_prints_its_lines() {
    let fx = fx("land-print");
    let mut land = Land::new(&fx.root, &fx.dir.join("tree/scripts"));
    land.said = None;
    land.say("a line on stdout");
    land.warn("a line on stderr");
    land.pass_through(&crate::Reply {
        stdout: "a tick's stdout\n".to_owned(),
        stderr: "a tick's stderr\n".to_owned(),
        code: 0,
    });
    assert!(land.said.is_none());
}

#[test]
fn a_command_that_cannot_start_or_speaks_no_text_is_a_raise() {
    let fx = fx("land-run");
    assert!(fx.land.run(&["/no/such/tool"], &[]).is_err());
    assert!(fx.land.loud(&["/no/such/tool"], &[]).is_err());
    assert!(fx.land.run(&["printf", "\\377"], &[]).is_err());
    assert_eq!(fx.land.run(&["sh", "-c", "kill -9 $$"], &[]).unwrap().0, -9);
    assert_eq!(fx.land.dirty(&[]).unwrap(), "");
    // `--boxes` only where the first pass found the box open, as `_box_flag` asked
    let d = fx.root.join("specs/449-x");
    put(&d, "tasks.md", "- [ ] T1 one\n      research: physical\n      - [ ] research pass\n- [ ] T2 two\n- [ ] T3 three\n");
    let mut boxed = fx;
    // without BOXES=1 the open box refuses, nor does BOXES=1 tick a box the first pass did not find open
    assert_eq!(boxed.land.tick(&d, "T1", "n"), Ok(2));
    boxed.land.boxes = true;
    assert_eq!(boxed.land.tick(&d, "T1", "n"), Ok(2));
    boxed.land.box_open.borrow_mut().push("T1".to_owned());
    assert_eq!(boxed.land.tick(&d, "T1", "n"), Ok(0));
    assert!(std::fs::read_to_string(d.join("tasks.md"))
        .unwrap()
        .contains("      - [x] research pass\n"));
    // a raise in the tick is the landing's
    std::fs::write(d.join("tasks.md"), b"- [ ] T2 two\n\xff").unwrap();
    assert!(boxed
        .land
        .tick(&d, "T2", "n")
        .unwrap_err()
        .contains("the tick raised on T2"));
}
