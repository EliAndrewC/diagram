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
use l7r_shared::tempdir::TempDir;

use super::inproc::Inproc;
use super::Land;
use crate::Reply;

/// Every stub: logs `<name> <args>` to `$STUB_DIR/log`, answers from `$STUB_DIR/<key>.{out,err,rcs,rc,sh}` (the key: the line, every
/// character but `[A-Za-z0-9._=-]` an underscore). Run as `python`, its name is the script's, or the module's after `-m`; as `ruff`
/// with no `.out` it echoes its input. The shell's builtins alone, no process of its own (feature 449 T167): it ran `basename`, `tr`,
/// `cat`, `head`, `tail` and `mv`, about 6 ms a call where this takes under 1, and a landing's test calls ten or more. `emit` passes a
/// file through as `cat` did, its last line's newline or its lack kept.
const STUB: &str = r#"#!/bin/sh
emit() { while IFS= read -r l; do printf '%s\n' "$l"; done; printf '%s' "$l"; }
name=${0##*/}
if [ "$name" = python ]; then
  if [ "$1" = -m ]; then name="$2"; shift 2; else name=${1##*/}; shift; fi
fi
if [ $# -gt 0 ]; then line="$name $*"; else line="$name"; fi
printf '%s\n' "$line" >> "$STUB_DIR/log"
key= rest=$line
while [ -n "$rest" ]; do
  c=${rest%"${rest#?}"}; rest=${rest#?}
  case $c in [A-Za-z0-9._=-]) key=$key$c;; *) key=${key}_;; esac
done
f="$STUB_DIR/$key"
[ -f "$f.sh" ] && . "$f.sh"
if [ "$name" = ruff ] && [ ! -f "$f.out" ] && [ ! -f "$f.rc" ]; then emit; exit 0; fi
[ -f "$f.out" ] && emit < "$f.out"
[ -f "$f.err" ] && emit < "$f.err" >&2
if [ -f "$f.rcs" ]; then
  { IFS= read -r rc; left=; while IFS= read -r l; do left="$left$l
"; done; } < "$f.rcs"
  printf '%s' "$left$l" > "$f.rcs"; exit "${rc:-0}"
fi
if [ -f "$f.rc" ]; then read -r rc < "$f.rc"; exit "$rc"; fi
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

/// The landing as the landing worktree's own run (451 T88, `L7R_LAND_ALONE`): a dirty tree is refused there, never sent to land alone.
pub(super) fn inner(fx: &mut Fx) {
    fx.land.root = l7r_shared::env::Rooted::with(fx.root.clone(), &[(super::alone::INNER, "1")]);
}

/// A tool of the stub tree as its stub logs it: its file name.
pub(super) fn tool(rel: &str) -> String {
    rel.rsplit('/').next().unwrap_or_default().to_owned()
}

/// The feature every fixture lands.
const PLAN: &str = "# Plan\n\nThe fixture's plan, reviewed CLEAR.\n";
const PLAN_SHA: &str = "8c79c7a920ecbecd5310903d3d791bb5aa08b592d49e976db64a1860cf4334bb";
pub(super) const TASKS: &str = "# Tasks\n\n- [ ] T1 one\n      verify: \n- [ ] T2 two\n";

/// The stub tools every landing runs, each a hard link to the one stub `install` wrote: its name is the link's (`basename "$0"`).
const TOOLS: [&str; 7] = [
    "tree/scripts/gates/l7r-gate.sh",
    "tree/scripts/gates/claims-gate.sh",
    "tree/scripts/gates/review-gate.sh",
    "tree/scripts/gates/plan-gate.sh",
    "tree/scripts/sync-with-main.sh",
    "bin/python",
    "bin/make",
];

/// The guard census of these tests, never the live one (451 T94: a landing's tick wrote its fixture's `plan-gate` rows into
/// `~/.claude/guard-log`, 978 of them by 2026-11-22): one directory for the process, set before the fixture is built, so every test
/// whose landing ticks writes there (the plan and task crates' `quiet_census`).
pub(super) fn quiet_census() -> PathBuf {
    static DIR: std::sync::OnceLock<PathBuf> = std::sync::OnceLock::new();
    DIR.get_or_init(|| {
        let dir = l7r_shared::tempdir::beside_binary("land-census");
        std::env::set_var("GUARD_LOG_DIR", &dir);
        dir
    })
    .clone()
}

/// THE FIXTURE BUILT ONCE A TEST BINARY (feature 449 T167, as T164 built the owed crate's): a clone holding `specs/449-x/tasks.md` and
/// its bare origin, and the stub tree, made by three git calls and one `install` where each landing's own took nine and seven - a
/// third of a short landing test's time. The origin is the clone's objects and refs copied, as a local `clone --bare` lays them out,
/// and `origin/main` its first commit; the remote is named per copy ([`fx`]), its path being the copy's. Under `make rust-test` it lives
/// in the run's own temporary directory, removed whole with it (`beside_binary`).
fn template() -> &'static Path {
    static DIR: std::sync::OnceLock<PathBuf> = std::sync::OnceLock::new();
    DIR.get_or_init(|| {
        quiet_census();
        let dir = l7r_shared::tempdir::beside_binary("land-template");
        let root = dir.join("repo");
        std::fs::create_dir_all(&root).unwrap();
        // the repository as `git init -b main` lays out what git reads of it - its HEAD, its object and ref directories and its config -
        // written without the process; the committer and the signing in the config itself, where three `git config` processes set them;
        // and no automatic maintenance, which each commit and fetch otherwise starts as a `git maintenance run --auto` process of its own
        for sub in ["objects", "refs/heads", "refs/tags"] {
            std::fs::create_dir_all(root.join(".git").join(sub)).unwrap();
        }
        put(&root, ".git/HEAD", "ref: refs/heads/main\n");
        put(
            &root,
            ".git/config",
            "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = true\n\
             [user]\n\temail = t@t\n\tname = t\n[commit]\n\tgpgsign = false\n[maintenance]\n\tauto = false\n",
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
        // a Makefile and its make-targets page current, so a landing's first pass does not try to regenerate and commit it each time: a
        // git process fewer a landing (feature 449 T167); `the_first_pass_commits_its_own_records` makes it stale
        put(&root, "Makefile", "x:   ## [tests] the fixture's target\n\techo x\n");
        assert_eq!(l7r_gate_cohort::make_docs::write(&root).code, 0);
        git(&root, &["add", "-A"]);
        git(&root, &["commit", "-qm", "start"]);
        let git_dir = root.join(".git");
        let origin = dir.join("origin.git");
        copy_tree(&git_dir.join("objects"), &origin.join("objects"));
        copy_tree(&git_dir.join("refs"), &origin.join("refs"));
        put(&origin, "HEAD", "ref: refs/heads/main\n");
        put(
            &origin,
            "config",
            "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = true\n",
        );
        let head = std::fs::read_to_string(git_dir.join("refs/heads/main")).unwrap();
        put(&git_dir, "refs/remotes/origin/main", &head);
        std::fs::create_dir_all(dir.join("stub")).unwrap();
        for tool in TOOLS {
            std::fs::create_dir_all(dir.join(tool).parent().unwrap()).unwrap();
        }
        write_executable(&dir.join(TOOLS[0]), STUB);
        for tool in &TOOLS[1..] {
            std::fs::hard_link(dir.join(TOOLS[0]), dir.join(tool)).unwrap();
        }
        dir
    })
}

/// `from` copied to `to`: an executable hard-linked, never written, so no test's spawn can inherit it open for writing ("Text file
/// busy", feature 449 T160's reason for `install`); every other file copied, as a test writes into its own.
fn copy_tree(from: &Path, to: &Path) {
    use std::os::unix::fs::PermissionsExt as _;
    std::fs::create_dir_all(to).unwrap();
    for e in std::fs::read_dir(from).unwrap().flatten() {
        let (src, dest) = (e.path(), to.join(e.file_name()));
        let meta = e.metadata().unwrap();
        if meta.is_dir() {
            copy_tree(&src, &dest);
        } else if meta.permissions().mode() & 0o111 != 0 {
            std::fs::hard_link(&src, &dest).unwrap();
        } else {
            std::fs::copy(&src, &dest).unwrap();
        }
    }
}

/// `hay` holds `needle`, else the test fails saying what it held. One line, so the message a pass never prints is no line of its own
/// for the cover to miss (an `assert!` rustfmt splits leaves it on one, 451 T101).
pub(super) fn has(hay: &str, needle: &str) {
    assert!(hay.contains(needle), "{needle:?} is not in:\n{hay}");
}

/// A clone of a bare origin holding `specs/449-x/tasks.md`, the stub tools, the landing with its output captured: a copy of
/// [`template`], its remote named.
pub(super) fn fx(tag: &str) -> Fx {
    let dir = scratch(tag);
    copy_tree(template(), &dir);
    let origin = dir.join("origin.git");
    let root = dir.join("repo");
    let config = root.join(".git/config");
    let text = std::fs::read_to_string(&config).unwrap();
    std::fs::write(
        &config,
        text + &format!(
            "[remote \"origin\"]\n\turl = {}\n\tfetch = +refs/heads/*:refs/remotes/origin/*\n[branch \"main\"]\n\tremote = origin\n\tmerge = refs/heads/main\n",
            origin.display()
        ),
    )
    .unwrap();
    let stub = dir.join("stub");
    let scripts = dir.join("tree/scripts");
    let bin = dir.join("bin");
    let answers = Rc::new(Answers::default());
    let mut land = Land::new_in(&l7r_shared::env::Rooted::with(root.clone(), &[]), &scripts);
    land.make = bin.join("make").to_string_lossy().into_owned();
    land.said = Some(RefCell::default());
    // a clock that moves only when the wait sleeps (feature 449 T160's, every landing's since T167): a wait that runs out does so after
    // its two polls, never after 400 real ms of a gate asked every 20 - the claims-owed landing's test spent most of its 589 ms so
    land.clock = Rc::new(Stepped(std::cell::Cell::new(std::time::Instant::now())));
    land.claims_wait = Duration::from_millis(400);
    land.claims_poll = land.claims_wait / 2;
    land.cgroup = dir.join("cgroup");
    land.memwatch = dir.join("memwatch");
    land.meminfo = dir.join("meminfo");
    land.cpus = Some(16);
    land.boxes = false;
    land.arbiter_ok = false;
    // the make target a landing names in its phase lines: `make land`'s, whatever make runs the tests (feature 451 T06)
    land.make_target = "land".to_owned();
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

/// A clock that stands still but for the sleeps it is asked for (feature 449 T160).
pub(super) struct Stepped(pub std::cell::Cell<std::time::Instant>);

impl super::Clock for Stepped {
    fn now(&self) -> std::time::Instant {
        self.0.get()
    }
    fn sleep(&self, d: Duration) {
        self.0.set(self.0.get() + d);
    }
}

mod bundle;
mod fix;

/// The real clock the landing runs on, every fixture standing [`Stepped`] in its place (feature 449 T167).
#[test]
fn the_real_clock_reads_the_time_and_sleeps() {
    use super::Clock as _;
    let before = super::RealClock.now();
    super::RealClock.sleep(Duration::from_millis(1));
    assert!(super::RealClock.now() > before);
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
    // the ticked task is archived at its tick, and the tick's commit carries the new file (feature 449 T142)
    let tasks = std::fs::read_to_string(fx.root.join("specs/449-x/tasks-done.md")).unwrap();
    assert!(tasks.contains("- [x] T1 one\n      verify: DONE. landed: checked\n"));
    // the log read once for both checks of it, nothing moving between them (feature 449 T167: a git process fewer)
    let subjects = fx.subjects();
    assert!(subjects.contains("449-x: T1 ticked (make land)"));
    let shown = std::process::Command::new("git")
        .args([
            "-C",
            &fx.root.to_string_lossy(),
            "log",
            "--format=%s",
            "--",
            "specs/449-x/tasks-done.md",
        ])
        .output()
        .unwrap();
    assert!(String::from_utf8_lossy(&shown.stdout).contains("449-x: T1 ticked (make land)"));
    assert!(err.is_empty());
    assert!(subjects.contains("449-x: T1 ticked (make land)"));
    let log = fx.log();
    assert!(log.contains("sync-with-main.sh done"));
    assert!(log.contains("stamp --check origin/main"));
    let asked = fx.answers.asked.borrow().join("\n");
    assert!(asked.contains("holding"));
    assert!(asked.contains("claims rekey"));
}

#[test]
fn every_cheap_refusal_is_said_together_and_nothing_runs_long() {
    let mut fx = fx("land-refused");
    inner(&mut fx); // in the clone, uncommitted work sends the landing to land alone (451 T88)
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
    let asked = fx.answers.asked.borrow().join("\n");
    assert!(asked.contains("/dev/review-ledger.md --refuse --landing 449-x --tasks T1"));
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
    // ...and T1's archive, which its tick created, is gone with it (feature 449 T142)
    assert!(out.contains("tick: archived the ticked task(s) T1 to tasks-done.md"));
    assert!(!d.join("tasks-done.md").exists());
}

/// The second half of [`a_refused_tick_puts_every_tick_back_and_a_raise_ends_the_landing`], on a landing of its own (feature 449 T167:
/// two landings in one test ran over FR-008's tenth of a second).
#[test]
fn a_closing_check_that_raises_ends_the_landing() {
    let fx = fx("land-tick-raise");
    let two = tasks(&["T1", "T2"]);
    let d = fx.root.join("specs/449-x");
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
}

/// The second half of [`a_push_that_merged_keeps_its_ticks_and_one_that_failed_reverts_them`], on a landing of its own, T1 open as a
/// fresh landing finds it (feature 449 T167: two landings in one test ran over FR-008's tenth of a second).
#[test]
fn a_push_that_failed_reverts_its_ticks() {
    let fx = fx("land-push-failed");
    fx.answer(&format!("{} done", tool("sync-with-main.sh")), "rc", "1");
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
    // the fresh block's `make cohort`, started in the background, has run before the test's directory goes: it logs into it, and the
    // second landing that once followed here no longer holds the directory while it does (feature 449 T167)
    let ran = (0..10_000).any(|_| {
        std::thread::sleep(Duration::from_millis(1));
        fx.log()
            .contains("make --no-print-directory cohort N=0 FRESH=48 JOBS=8")
    });
    assert!(ran, "the fresh block never ran");
}

/// The second landing of [`an_engine_landing_starts_the_fresh_block_and_shows_the_work_budget`], a test of its own (feature 449 T167:
/// the two landings together ran over FR-008's tenth of a second).
#[test]
fn a_work_budget_run_that_is_no_json_fails_the_landing_after_its_push() {
    // a work-budget run that is no JSON fails the landing after its push, as the import raised
    let fx = fx_engine_with_budget("land-engine-budget", "{");
    assert!(land(&fx).is_err());
}

pub(super) fn fx_engine_with_budget(tag: &str, run: &str) -> Fx {
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
    broken.land.root = broken.land.root.at(broken.dir.join("no-such"));
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
    let blank = l7r_shared::env::Rooted::with(".", &[("LAND_BOXES", "  ")]);
    assert!(!super::set(&blank, "LAND_BOXES"));
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
        super::main(
            &args(&["449"]),
            &fx.root,
            NOTE,
            &scripts,
            &nothing,
            &l7r_shared::env::Rooted::with(".", &[(super::alone::INNER, "1")])
        ),
        Ok(2)
    );
    assert_eq!(
        super::main(
            &args(&["449", " "]),
            &fx.root,
            NOTE,
            &scripts,
            &nothing,
            &l7r_shared::env::Rooted::with(".", &[(super::alone::INNER, "1")])
        ),
        Ok(2)
    );
    assert_eq!(
        super::main(
            &args(&["449", "T1"]),
            &fx.root,
            "  ",
            &scripts,
            &nothing,
            &l7r_shared::env::Rooted::with(".", &[(super::alone::INNER, "1")])
        ),
        Ok(2)
    );
    assert_eq!(
        super::main(
            &args(&["7", "T1"]),
            &fx.root,
            NOTE,
            &scripts,
            &nothing,
            &l7r_shared::env::Rooted::with(".", &[(super::alone::INNER, "1")])
        ),
        Ok(2)
    );
    // a landing from main whose tasks.md cannot be read: the first pass raises before any tool runs
    std::fs::write(fx.root.join("specs/449-x/tasks.md"), [0xff]).unwrap();
    assert!(super::main(
        &args(&["449", "T1"]),
        &fx.root,
        NOTE,
        &scripts,
        &nothing,
        &l7r_shared::env::Rooted::with(".", &[(super::alone::INNER, "1")])
    )
    .is_err());
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
    let mut land = Land::new_in(
        &l7r_shared::env::Rooted::with(fx.root.clone(), &[]),
        &fx.dir.join("tree/scripts"),
    );
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
    assert!(std::fs::read_to_string(d.join("tasks-done.md"))
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

/// The process's landing reads the process's environment, its root as given (feature 451 T38: every other test reads its own).
#[test]
fn the_process_landing_keeps_its_root() {
    let land = Land::new(Path::new("/r"), Path::new("/r/scripts"));
    assert_eq!(land.root.path(), Path::new("/r"));
}

/// The census's entries holding `needle`.
fn census_holding(needle: &str) -> usize {
    let dir = quiet_census();
    let entries = std::fs::read_dir(dir).unwrap().flatten();
    entries
        .filter(|e| {
            std::fs::read_to_string(e.path())
                .unwrap_or_default()
                .contains(needle)
        })
        .count()
}

/// 451 T94: a landing's escapes are its root's environment, never the process's - a test's own map, so a session's exported
/// `PLAN_REVIEW_OK`, `ARBITER_OK` or `BOXES=1` reaches no test - and its tick's firings go to the census, never `~/.claude/guard-log`.
#[test]
fn a_landing_reads_its_own_escapes_and_logs_to_the_census() {
    let mut fx = fx("land-own-escapes");
    let d = fx.root.join("specs/449-x");
    put(
        &d,
        "plan.md",
        "# Plan\n\nThe fixture's plan, changed since its review.\n",
    );
    let refused = fx.land.tick(&d, "T1", NOTE).unwrap();
    let (_, err) = fx.said();
    assert_ne!(refused, 0, "{err}");
    has(&err, "plan decisions have no current CLEAR review");
    // read before this test names the census itself: the fixture's own build set it, or the tick wrote the live log
    let logged = l7r_shared::log::dir();
    let census = quiet_census();
    assert_eq!(logged, census);
    let why = "a test's own escape, 451 T94 pin";
    fx.land.root = l7r_shared::env::Rooted::with(fx.root.clone(), &[("PLAN_REVIEW_OK", why)]);
    let ticked = fx.land.tick(&d, "T1", NOTE).unwrap();
    let (out, _) = fx.said();
    assert_eq!(ticked, 0, "{out}");
    has(&out, &format!("plan gate BYPASSED - {why}"));
    let escaped = census_holding(why);
    assert_eq!(escaped, 1);
    let named = [("LAND_BOXES", "1"), ("ARBITER_OK", "a test's own")];
    let own = Land::new_in(
        &l7r_shared::env::Rooted::with(fx.root.clone(), &named),
        Path::new("/s"),
    );
    let none = Land::new_in(
        &l7r_shared::env::Rooted::with(fx.root.clone(), &[]),
        Path::new("/s"),
    );
    let read = (own.boxes, own.arbiter_ok, none.boxes, none.arbiter_ok);
    assert_eq!(read, (true, true, false, false));
}
