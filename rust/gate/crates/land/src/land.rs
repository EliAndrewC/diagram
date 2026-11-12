//! `l7r-gate land <feature> "<T1 [T2 ...]>"` (`make land F=<feature> T="<T1 [T2 ...]>" NOTE="<what was verified>"`) - one command lands
//! one task or several and ticks them (feature 405 T33, D5; it grew from 385 T117's `land-batch`, which `make land-batch` still names).
//! Ported from `scripts/land.py` by feature 449 T121 (`ask:449-T83-scope`, T83's fifth slice), every refusal, check and line as the Python
//! had them; `land.py` landed its own deletion, the commit that put this behind `make land`.
//!
//! WHY (the GM 2026-10-20, after 405's first claim: "It sounds like the landing being the biggest cost is something that we need to do
//! something about"). T12's fix took 5 minutes and its landing 15: six refusals met one at a time, each a session round trip, and `make
//! done` and `make cohort-landing` each started by hand only after a refusal named it - while the checks themselves take seconds
//! (`specs/405-engine-findings-from-385/landing-analysis.md`).
//!
//! Pass 1 runs nothing long and prints EVERY refusal together ([`cheap`]): each task's tick refusals but "not landed yet", uncommitted
//! work, owed ledger rows, the claims gate, what holds the landing (with the tasks named, `L7R_LAND_TICKS`), the review gate and the plan
//! gate. Pass 2 ([`long_runs`]): `make done` when the green-gate stamp does not cover this content; `make cohort-landing` when the delta
//! carries engine code and the cohort gate would refuse - BESIDE the gate when both are owed (405 T48, D21); what those runs regenerate
//! under `pool/` is committed; then the claims gate, waited on ([`claims_wait`]) - its round runs beside the gate (405 T50); then each
//! tick, committed, and ONE `scripts/sync-with-main.sh done` with `L7R_LAND_TICKS` set carries work and ticks (405 T51). A failed landing
//! ticks nothing (a failed push reverts its ticks).
//!
//! What the port asks in process, by the ruling: the review ledger's owed rows (`reviews ledger-owed`, T117), the holding box
//! (`speckit-todo --holding`, T118) and the claims (`claims carry|known|rekey|report`, the scope split and the claims in flight, T82),
//! each through the same function its command runs, so its reply and its usage line are the command's. What stays a process, as
//! `land.py` ran it: `scripts/tick-task.py` by path (Python, `ask:449-T89-reviews`: `--land-check` in the first pass, the tick itself at
//! the end), `scripts/make-docs.py` and `python3 -m ruff`, `make`, `scripts/sync-with-main.sh`, the three `*-gate.sh`, and the gate's
//! other subcommands through `l7r-gate.sh` (the stamp, `coverage-exempt stale`, `arbiter gate-held`, `cohort counter-only|port|check|
//! rust-owed`). `codeid.py` is no longer started: the engine paths are the cohort's one copy of `codeid.ENGINE`
//! ([`l7r_gate_cohort::cohort::is_landing_engine`]).

mod cheap;
mod claims_wait;
mod inproc;
mod long_runs;
mod memory;
mod stop;

use std::cell::RefCell;
use std::fmt::Write as _;
use std::io::Write as _;
use std::os::unix::process::ExitStatusExt as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::Duration;

use l7r_guard::shared::py_text::strip;

use crate::Reply;

/// How long the landing waits for the claims round after its gate, asking every `CLAIMS_POLL_S` (405 T50, D23).
const CLAIMS_WAIT_S: f64 = 1200.0;
const CLAIMS_POLL_S: f64 = 15.0;
/// `sync-with-main.sh done`'s exit when it PUSHED but the pull merged other sessions' edits into the files the push touched.
const MERGED: i32 = 3;
/// The name a run is recorded under in the usage log (`usage_log.exited("land", ...)` in `land.py`; feature 406), which
/// `scripts/tool-registry.json` registers.
const USAGE_LOG_TOOL: &str = "land";
const USAGE: &str =
    "usage: land.py <feature> \"<T1 [T2 ...]>\"   (make land F=405 T=T12 NOTE=\"what was verified\")";

/// One landing: the tree it lands, where its tools are, and what it has exported to the commands it runs.
pub struct Land {
    /// The repository root.
    root: PathBuf,
    /// The gate tree's `scripts/` (`L7R_GATE_TREE`, which `l7r-gate.sh` sets; the root's where unset): `land.py`'s own `HERE`.
    scripts: PathBuf,
    /// The interpreter `make-docs.py`, `tick-task.py` and ruff run under (`sys.executable` in the Python).
    python: String,
    /// `make`.
    make: String,
    /// What the landing has put in its environment since it started (`os.environ[...] = ...` in the Python), handed to every
    /// command it runs after.
    exported: RefCell<Vec<(String, String)>>,
    /// A test's capture of the two streams; `None` prints them, each line flushed as `print(..., flush=True)` did.
    said: Option<RefCell<(String, String)>>,
    /// The claims wait's bound and its poll.
    claims_wait: Duration,
    claims_poll: Duration,
    /// Where the container's memory is read (`/sys/fs/cgroup`, `~/.claude/memwatch`), and `/proc/meminfo`.
    cgroup: PathBuf,
    memwatch: PathBuf,
    meminfo: PathBuf,
    /// The processors online (`os.cpu_count()`), or `None` where they cannot be read.
    cpus: Option<i64>,
    /// `make land ... BOXES=1` (`LAND_BOXES`): the landing ticks a physical task's research boxes, as `make tick BOXES=1` does (410 T01
    /// was refused with a pointer to BOXES=1, which `make land` did not pass on).
    boxes: bool,
    /// The tasks with a research box still open, as the first pass's `tick-task.py --land-check` read them (`box_open`): the tick's
    /// `--boxes` choice under `BOXES=1`, `land.py`'s `_box_flag`, made here in the land (feature 449 T121, its plan review: the
    /// choice is the land's, the reading of the boxes `tick-task.py`'s one `boxes_refusal`, asked in the process the pass already starts).
    box_open: RefCell<Vec<String>>,
    /// `ARBITER_OK` set: the red-gate tripwire's hold not asked.
    arbiter_ok: bool,
    /// What the landing asks in process ([`inproc`]).
    inproc: Box<dyn inproc::Inproc>,
}

impl Land {
    /// The landing of `root`, its tools under `scripts`, as the process runs it.
    #[must_use]
    pub fn new(root: &Path, scripts: &Path) -> Self {
        Self {
            root: root.to_path_buf(),
            scripts: scripts.to_path_buf(),
            python: "python3".to_owned(),
            make: "make".to_owned(),
            exported: RefCell::new(Vec::new()),
            said: None,
            claims_wait: Duration::from_secs_f64(CLAIMS_WAIT_S),
            claims_poll: Duration::from_secs_f64(CLAIMS_POLL_S),
            cgroup: PathBuf::from("/sys/fs/cgroup"),
            memwatch: PathBuf::from(std::env::var("HOME").unwrap_or_default())
                .join(".claude/memwatch"),
            meminfo: PathBuf::from("/proc/meminfo"),
            cpus: memory::cpus_online(Path::new("/sys/devices/system/cpu/online")),
            boxes: set("LAND_BOXES"),
            box_open: RefCell::new(Vec::new()),
            arbiter_ok: !std::env::var("ARBITER_OK").unwrap_or_default().is_empty(),
            inproc: Box::new(inproc::Real),
        }
    }

    /// A line on stdout.
    fn say(&self, line: &str) {
        if let Some(said) = &self.said {
            let _ = writeln!(said.borrow_mut().0, "{line}");
        } else {
            println!("{line}");
            let _ = std::io::stdout().flush();
        }
    }

    /// A line on stderr.
    fn warn(&self, line: &str) {
        if let Some(said) = &self.said {
            let _ = writeln!(said.borrow_mut().1, "{line}");
        } else {
            eprintln!("{line}");
        }
    }

    /// A tool of the gate tree's `scripts/`.
    fn script(&self, rel: &str) -> String {
        self.scripts.join(rel).to_string_lossy().into_owned()
    }

    /// `scripts/gates/l7r-gate.sh`.
    fn gate(&self) -> String {
        self.script("gates/l7r-gate.sh")
    }

    /// A command from the clone, with what the landing has exported.
    fn command(&self, cmd: &[&str]) -> Command {
        let mut c = Command::new(cmd[0]);
        c.args(&cmd[1..]).current_dir(&self.root);
        for (k, v) in self.exported.borrow().iter() {
            c.env(k, v);
        }
        c
    }

    /// `export K=V` for every command from here on.
    fn export(&self, key: &str, value: &str) {
        self.exported
            .borrow_mut()
            .push((key.to_owned(), value.to_owned()));
    }

    /// `run(root, cmd, env)`: a command from the clone, its exit code and its output (stdout then stderr), each decoded as text strictly,
    /// as `subprocess.run(..., text=True)` raised on bytes it could not decode.
    fn run(&self, cmd: &[&str], env: &[(&str, &str)]) -> Result<(i32, String), String> {
        let out = self
            .command(cmd)
            .envs(env.iter().copied())
            .stdin(Stdio::inherit())
            .output()
            .map_err(|e| spawn_error(cmd[0], &e))?;
        Ok((
            code_of(out.status),
            decode(&out.stdout)? + &decode(&out.stderr)?,
        ))
    }

    /// `run(root, cmd, quiet=False)` and `subprocess.run(cmd, cwd=root)`: its output passed through, its exit code.
    fn loud(&self, cmd: &[&str], env: &[(&str, &str)]) -> Result<i32, String> {
        let status = self
            .command(cmd)
            .envs(env.iter().copied())
            .status()
            .map_err(|e| spawn_error(cmd[0], &e))?;
        Ok(code_of(status))
    }

    /// A make target from the clone, its output passed through.
    fn make(&self, target: &str) -> Result<i32, String> {
        self.loud(&[&self.make, "--no-print-directory", target], &[])
    }

    /// `git status --porcelain -- <paths>`, stripped: what is dirty there.
    fn dirty(&self, paths: &[&str]) -> Result<String, String> {
        let mut cmd = vec!["git", "status", "--porcelain"];
        if !paths.is_empty() {
            cmd.push("--");
            cmd.extend(paths);
        }
        Ok(strip(&self.run(&cmd, &[])?.1).to_owned())
    }

    /// Every path the delta against origin/main changes.
    fn delta_names(&self) -> Result<Vec<String>, String> {
        self.run(&["git", "fetch", "-q", "origin"], &[])?;
        let out = self
            .run(&["git", "diff", "--name-only", "origin/main...HEAD"], &[])?
            .1;
        Ok(l7r_guard::shared::py_text::split(&out)
            .into_iter()
            .map(str::to_owned)
            .collect())
    }

    /// Does the delta against origin/main carry engine code (`codeid.ENGINE`)?
    fn engine_delta(&self) -> Result<bool, String> {
        Ok(self
            .delta_names()?
            .iter()
            .any(|n| l7r_gate_cohort::cohort::is_landing_engine(n)))
    }

    /// The port switch's state (`l7r-gate cohort port`, feature 444 FR-023).
    fn port(&self) -> Result<String, String> {
        Ok(strip(&self.run(&[&self.gate(), "cohort", "port"], &[])?.1).to_owned())
    }

    /// `git rev-parse --absolute-git-dir`, or the root's `.git`.
    fn git_dir(&self) -> Result<PathBuf, String> {
        let out = self
            .run(&["git", "rev-parse", "--absolute-git-dir"], &[])?
            .1;
        Ok(git_dir_of(&out, &self.root))
    }

    /// THE LANDING'S OWN ESCAPES ARE COMMITTED, NOT REFUSED (feature 408): an escape a tick or a gate honored (`PLAN_REVIEW_OK`) writes
    /// its dev/bypass-log record during the landing, and the tree checks refused every rerun - and held the claims wait to its bound -
    /// on records of the landing's own.
    fn commit_escape_records(&self) -> Result<(), String> {
        if !self.dirty(&["dev/bypass-log"])?.is_empty() {
            self.run(&["git", "add", "--", "dev/bypass-log"], &[])?;
            self.run(
                &[
                    "git",
                    "commit",
                    "-q",
                    "-m",
                    "the landing's escape records (make land, 408)",
                    "--",
                    "dev/bypass-log",
                ],
                &[],
            )?;
        }
        Ok(())
    }

    /// The landing, after its arguments: every pass, the ticks and the push; the exit code.
    fn land(&self, feature: &str, d: &Path, tasks: &[String], note: &str) -> Result<i32, String> {
        let mut claims: Vec<String> = Vec::new();
        let stops = self.cheap_refusals(feature, d, tasks, note, Some(&mut claims))?;
        if !stops.is_empty() {
            let every: Vec<String> = stops.into_iter().chain(claims).collect();
            self.warn(&format!(
                "land: refused before anything ran - nothing landed, nothing ticked. Every refusal:\n  {}",
                every.join("\n  ")
            ));
            return Ok(2);
        }
        if let Some(first) = claims.first() {
            self.say(&format!(
                "land: the claims round is owed ({}) - the gate runs beside it; the push waits for it",
                head(first, 160)
            ));
        }
        // the fresh block follows an engine landing, after its push (D5) - unless it only adds counter blocks (feature 446, FR-002),
        // asked before the push moves the merge base
        let engine_landed = self.engine_delta()?;
        let counter_landed = engine_landed && self.counter_only()?;
        let rc = self.long_runs()?;
        if rc != 0 {
            return Ok(rc);
        }
        let why = self.wait_for_claims(tasks, Some(d))?;
        if !why.is_empty() {
            self.warn(&claims_wait::claims_stop_line(&why));
            return Ok(2);
        }
        self.write_ledger(d)?; // the passes the claims round made beside the gate (405 T52, D27)
        self.tick_and_push(feature, d, tasks, note, engine_landed, counter_landed)
    }

    /// ONE PUSH, THE TICKS IN IT (405 T51, D24): T13's landing pushed its work, then its ticks - two runs of every push check.
    fn tick_and_push(
        &self,
        feature: &str,
        d: &Path,
        tasks: &[String],
        note: &str,
        engine_landed: bool,
        counter_landed: bool,
    ) -> Result<i32, String> {
        let rel = rel_of(&self.root, d);
        let how = if tasks.len() > 1 {
            format!("landed in batch {}", tasks.join("+"))
        } else {
            "landed".to_owned()
        };
        // the tasks the landing ticks: `--landing` is honored for these alone - AND THE FEATURE BEING LANDED, named to the push: its
        // gated merge read `.specify/feature.json`, which `make claim` points at a feature filed mid-task - 443 T12's landing ran its
        // whole gate, then refused as 445's (2026-10-28)
        self.export("L7R_LAND_TICKS", &tasks.join(" "));
        self.export("SPECIFY_FEATURE", &name_of(d));
        let mut failed = Vec::new();
        for task in tasks {
            let rc = self.tick(feature, task, &format!("{how}: {note}"))?;
            if rc != 0 {
                failed.push(task.as_str());
            }
        }
        if !failed.is_empty() {
            // the ticks already written put back: a landing that does not push ticks nothing
            self.run(&["git", "checkout", "--", &rel], &[])?;
            self.warn(&format!(
                "land: {} refused its tick (above) - nothing landed, nothing ticked",
                failed.join(", ")
            ));
            return Ok(2);
        }
        // a tick's honored escape writes its record too (feature 408)
        self.run(&["git", "add", "--", &rel, "dev/bypass-log"], &[])?;
        let message = format!("{}: {} ticked (make land)", name_of(d), tasks.join(" "));
        self.run(&["git", "commit", "-q", "-m", &message], &[])?;
        let tick_sha = strip(&self.run(&["git", "rev-parse", "HEAD"], &[])?.1).to_owned();
        let rc = self.loud(
            &[&self.script("sync-with-main.sh"), "done"],
            &[("L7R_LAND_TICKS", &tasks.join(" "))],
        )?;
        if rc == MERGED {
            // PUSHED, WITH OTHER SESSIONS' EDITS MERGED INTO FILES IT TOUCHED (405 T107: T107's landing pushed its tick, then reverted it
            // in the clone as if nothing had landed, so the clone's next push would have unticked main): the ticks stand
            self.warn(&format!("land: {} landed and ticked - but the pull merged other sessions' edits into files it touched: rerun the gate now (MEASURE_OK names it), then scripts/sync-with-main.sh render-sync", tasks.join(" ")));
            return Ok(rc);
        }
        if rc != 0 {
            let back = self.revert_ticks(&tick_sha)?;
            self.warn(&format!("land: the push failed (exit {rc}) - {back}"));
            return Ok(rc);
        }
        self.say(&format!("land: {} landed and ticked", tasks.join(" ")));
        let line = self.fresh_block_after(engine_landed, counter_landed)?;
        if !line.is_empty() {
            self.say(&line);
        }
        if engine_landed {
            // the distance from the goal, at every engine landing (443 FR-007, plan D8)
            let view = l7r_gate_cohort::speckit_todo::work_budget_view::lines(&self.root)?;
            self.say(&view.join("\n"));
        }
        Ok(0)
    }

    /// One task ticked by `tick-task.py` by path (`ask:449-T89-reviews`), its output passed through; its exit code. Under `BOXES=1`,
    /// `--boxes` where the first pass found the task's research box open ([`Land::box_open`]), as `land.py`'s `_box_flag` chose (410 T01 was refused with a
    /// pointer to BOXES=1, which `make land` did not pass on). A raise in the tick (exit 1) ends the landing there, as the import's raise
    /// ended `land.py`, nothing put back.
    fn tick(&self, feature: &str, task: &str, note: &str) -> Result<i32, String> {
        let script = self.script("tick-task.py");
        let mut cmd = vec![
            self.python.as_str(),
            script.as_str(),
            feature,
            task,
            note,
            "--landing",
        ];
        if self.boxes && self.box_open.borrow().iter().any(|t| t == task) {
            cmd.push("--boxes");
        }
        match self.loud(&cmd, &[])? {
            1 => Err(format!("tick-task.py raised on {task} (above)")),
            rc => Ok(rc),
        }
    }

    /// Put a failed push's ticks back with a new commit (nothing rewritten), and say what happened. A push whose pull stopped on a merge
    /// conflict leaves the merge in progress, and git refuses the revert then (2026-10-25, 422 T02: the message said "its ticks reverted"
    /// while the tick commit stood, and the retry found T02 already ticked) - so the revert's own exit code decides the message.
    fn revert_ticks(&self, tick_sha: &str) -> Result<String, String> {
        let (rc, out) = self.run(&["git", "revert", "--no-edit", tick_sha], &[])?;
        Ok(reverted(rc, &out, tick_sha))
    }

    /// Does the delta against the merge base with origin/main only add counter blocks (`l7r-gate cohort counter-only`, feature 446)?
    fn counter_only(&self) -> Result<bool, String> {
        Ok(self.run(&[&self.gate(), "cohort", "counter-only"], &[])?.0 == 0)
    }

    /// The fresh block after the push (feature 415 T03): started after an engine landing, never after a counter-only one (feature 446,
    /// FR-002) or a landing with no engine code; the line the landing prints, "" for none.
    fn fresh_block_after(&self, engine: bool, counter: bool) -> Result<String, String> {
        if engine && counter {
            return Ok("land: the delta is counter-only (feature 446): no fresh block owed - a counter block changes no map".to_owned());
        }
        // no Python cohort to roll since the hamlet engine's deletion (feature 444 T41)
        if engine && self.port()? == "rust-only" {
            return Ok(String::new());
        }
        if engine {
            let log = self.start_fresh_block()?;
            return Ok(format!("land: the cohort's fresh block started after the push - a rate, never a refusal; its log {}", log.display()));
        }
        Ok(String::new())
    }

    /// THE COHORT'S FRESH BLOCK, AFTER THE PUSH (feature 415 T03, D5; the GM 2026-10-24 - a rate, never a refusal, and T26's landing
    /// waited 1.4 min for it past the gate): `make cohort N=0 FRESH=48` in its own process group under a lock, so a later landing's
    /// block WAITS for a running one, never skipped; its record is committed by the cohort and goes out with the next push. Its log.
    fn start_fresh_block(&self) -> Result<PathBuf, String> {
        let gd = self.git_dir()?;
        let log = gd.join("land-fresh.log");
        let jobs = format!("JOBS={}", (self.cpus.unwrap_or(4) / 2).max(2));
        let sink = std::fs::OpenOptions::new()
            .append(true)
            .create(true)
            .open(&log)
            .map_err(io)?;
        let lock = gd.join("land-fresh.lock").to_string_lossy().into_owned();
        let err = sink.try_clone().map_err(io)?;
        let cmd = [
            "flock",
            &lock,
            &self.make,
            "--no-print-directory",
            "cohort",
            "N=0",
            "FRESH=48",
            &jobs,
        ];
        std::os::unix::process::CommandExt::process_group(&mut self.command(&cmd), 0)
            .stdout(sink)
            .stderr(err)
            .spawn()
            .map_err(io)?;
        Ok(log)
    }
}

/// What `git rev-parse --absolute-git-dir` said (stdout and stderr), stripped - or the root's `.git` where it said nothing.
fn git_dir_of(said: &str, root: &Path) -> PathBuf {
    let out = strip(said);
    if out.is_empty() {
        root.join(".git")
    } else {
        PathBuf::from(out)
    }
}

/// What the revert of a failed push's ticks says, by its exit code and output.
fn reverted(rc: i32, out: &str, tick_sha: &str) -> String {
    if rc == 0 {
        return "its ticks reverted, nothing landed; fix it and run make land again".to_owned();
    }
    let out = strip(out);
    let why = if out.is_empty() {
        format!("git revert exited {rc}")
    } else {
        l7r_guard::shared::speckit::splitlines(out)[0].to_owned()
    };
    let short = head(tick_sha, 9);
    format!("its ticks could NOT be reverted ({why}): the tick commit {short} stands in the clone. Resolve what the push left (a merge in progress: fix the conflicts and commit), then push it with scripts/sync-with-main.sh done - the tick goes with it - or drop it with git revert --no-edit {short}")
}

/// A variable set to something but blanks (`LAND_BOXES`, as `_boxes()` read it); `ARBITER_OK` was read with no strip, so a blank
/// value counts there.
fn set(key: &str) -> bool {
    !strip(&std::env::var(key).unwrap_or_default()).is_empty()
}

/// The exit code `subprocess` reports: the process's own, or minus the signal that ended it.
fn code_of(status: std::process::ExitStatus) -> i32 {
    status
        .code()
        .unwrap_or_else(|| -status.signal().unwrap_or(0))
}

/// Bytes as `text=True` reads them: UTF-8, strictly.
fn decode(bytes: &[u8]) -> Result<String, String> {
    String::from_utf8(bytes.to_vec())
        .map_err(|e| format!("UnicodeDecodeError: 'utf-8' codec can't decode the output: {e}"))
}

/// An I/O failure's text: what a raise said (the landing's own file and process errors, none of which a caller reads but as its
/// failure).
fn io<E: std::fmt::Display>(e: E) -> String {
    e.to_string()
}

/// What `subprocess` raised on a program it could not start.
fn spawn_error(program: &str, e: &std::io::Error) -> String {
    format!("FileNotFoundError: {e}: '{program}'")
}

/// The first `n` characters (Python's `s[:n]`).
fn head(text: &str, n: usize) -> String {
    text.chars().take(n).collect()
}

/// The last `n` characters (Python's `s[-n:]`).
fn tail(text: &str, n: usize) -> String {
    let count = text.chars().count();
    text.chars().skip(count.saturating_sub(n)).collect()
}

/// A directory's last component, as `Path.name`.
fn name_of(d: &Path) -> String {
    d.file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default()
}

/// `d.relative_to(root)`, as text.
fn rel_of(root: &Path, d: &Path) -> String {
    d.strip_prefix(root)
        .unwrap_or(d)
        .to_string_lossy()
        .into_owned()
}

/// A file as `read_text(encoding="utf-8")` reads it: strictly UTF-8, its newlines universal.
fn py_read(path: &Path) -> Result<String, String> {
    let bytes = std::fs::read(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let text = String::from_utf8(bytes)
        .map_err(|e| format!("UnicodeDecodeError: {}: {e}", path.display()))?;
    Ok(text.replace("\r\n", "\n").replace('\r', "\n"))
}

/// The repository root: git's answer, or the nearest ancestor holding `specs/` (`tick-task.repo_root`).
fn repo_root(start: &Path) -> PathBuf {
    let out = Command::new("git")
        .args(["rev-parse", "--show-toplevel"])
        .current_dir(start)
        .output();
    match out {
        Ok(o) if o.status.success() => PathBuf::from(strip(&String::from_utf8_lossy(&o.stdout))),
        _ => {
            let here = start.canonicalize().unwrap_or(start.to_path_buf());
            here.ancestors()
                .find(|c| c.join("specs").is_dir())
                .map_or(here.clone(), Path::to_path_buf)
        }
    }
}

/// `specs/<feature>` when that exists, else the ONE `specs/<feature>-*` - None when neither, or several (`tick-task.spec_dir`).
fn spec_dir(root: &Path, feature: &str) -> Option<PathBuf> {
    let specs = root.join("specs");
    let exact = specs.join(feature);
    if exact.is_dir() {
        return Some(exact);
    }
    let prefix = format!("{feature}-");
    let mut hits: Vec<PathBuf> = std::fs::read_dir(&specs)
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| {
            let n = e.file_name().to_string_lossy().into_owned();
            n.starts_with(&prefix) && e.path().is_dir()
        })
        .map(|e| e.path())
        .collect();
    hits.sort();
    (hits.len() == 1).then(|| hits.remove(0))
}

/// The run recorded in the working directory's repository (`usage_log.exited("land", code)`), by the one writer (feature 449 T129).
fn record(cwd: &Path, code: i32) {
    l7r_guard::shared::usage::record(
        cwd,
        USAGE_LOG_TOOL,
        "check",
        l7r_guard::shared::usage::exited(code),
    );
}

fn reply(code: i32) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: String::new(),
        code,
    }
}

/// A raise: what `land.py` printed before it, its message after a `Traceback` line, exit 1, no run recorded.
fn raised(why: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("Traceback (most recent call last):\n  l7r-gate land\n{why}\n"),
        code: 1,
    }
}

/// The gate tree's `scripts/`: `L7R_GATE_TREE`'s, which `l7r-gate.sh` sets, else the root's.
fn scripts_of(root: &Path) -> PathBuf {
    std::env::var_os("L7R_GATE_TREE")
        .map_or(root.to_path_buf(), PathBuf::from)
        .join("scripts")
}

/// A line on stdout, as `print` wrote it.
fn print_line(line: &str) {
    println!("{line}");
}

/// The reply of a run: its exit code recorded, or a raise's place.
fn finish(done: Result<i32, String>, cwd: &Path) -> Reply {
    match done {
        Ok(code) => {
            record(cwd, code);
            reply(code)
        }
        Err(why) => raised(&why),
    }
}

/// `l7r-gate land <feature> "<T1 [T2 ...]>"` (the note from `$LAND_NOTE`) and `l7r-gate land --stop`: the landing prints as it goes,
/// so the reply carries only its exit code - or, on a raise, the traceback's place.
/// Run from `cwd`, the process's working directory, where the run is recorded.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    let done = if args == ["--stop"] {
        stop::stop(&repo_root(cwd), Path::new("/proc"), &mut print_line)
    } else {
        main(
            args,
            cwd,
            &std::env::var("LAND_NOTE").unwrap_or_default(),
            &scripts_of,
            &stop::catch_term,
        )
    };
    finish(done, cwd)
}

/// `main`: the arguments, the note and the feature checked, then the landing.
fn main(
    args: &[String],
    cwd: &Path,
    note: &str,
    scripts: &dyn Fn(&Path) -> PathBuf,
    catch_term: &dyn Fn(),
) -> Result<i32, String> {
    let tasks: Vec<String> = args.get(1).map_or_else(Vec::new, |t| {
        l7r_guard::shared::py_text::split(t)
            .into_iter()
            .map(str::to_owned)
            .collect()
    });
    if args.len() != 2 || tasks.is_empty() {
        eprintln!("{USAGE}");
        return Ok(2);
    }
    // A STOPPED LANDING STOPS ITS RUNS (405 T79), from here on, as `land.py` installed its handler past the usage check
    catch_term();
    let note = strip(note).to_owned();
    if note.is_empty() {
        eprintln!("land: refused - NOTE= is empty; say what was verified, as make tick asks");
        return Ok(2);
    }
    let root = repo_root(cwd);
    let Some(d) = spec_dir(&root, &args[0]).filter(|d| d.join("tasks.md").is_file()) else {
        eprintln!(
            "land: no single specs/{}* directory with a tasks.md under {}",
            args[0],
            root.display()
        );
        return Ok(2);
    };
    Land::new(&root, &scripts(&root)).land(&args[0], &d, &tasks, &note)
}

#[cfg(test)]
mod tests;
