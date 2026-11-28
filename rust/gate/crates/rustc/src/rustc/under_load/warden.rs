//! The warden's run (feature 462 T321, `under_load.rs`): the sentinel and its group, the burners and the copies' loops in it, the
//! watch over the bound, the caller's pipe and the load, the group ended, the report and the `Phase` line.

use std::fmt::Write as _;
use std::fs::File;
use std::io::{Read, Write as _};
use std::os::unix::process::CommandExt as _;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::thread::JoinHandle;
use std::time::{Instant, SystemTime};

use l7r_shared::guards::event_log_hooks::now_stamp;
use serde_json::{json, Map, Value};

use super::super::{phase, World};
use super::{Ask, Knobs, STEP, WARDEN};
use crate::Reply;

/// How many red runs' logs the report names.
const NAMED: usize = 10;

/// One run of CMD.
struct Done {
    copy: usize,
    turn: usize,
    /// Its exit code; None where a signal ended it or it never started.
    code: Option<i32>,
    /// Ended by the bound or by the caller's going (the group was being ended when its wait returned), and not green.
    cut: bool,
    log: PathBuf,
}

#[derive(Clone, Copy, PartialEq)]
enum Ended {
    Done,
    Bound,
    Gone,
}

impl Ended {
    fn said(self) -> &'static str {
        match self {
            Self::Done => "every loop ran",
            Self::Bound => "the bound",
            Self::Gone => "the caller went away",
        }
    }
}

/// The 1-minute load, 0 where it cannot be read.
pub(in crate::rustc) fn load(proc_root: &Path) -> f64 {
    std::fs::read_to_string(proc_root.join("loadavg"))
        .ok()
        .and_then(|t| t.split_whitespace().next().and_then(|w| w.parse().ok()))
        .unwrap_or(0.0)
}

/// The sentinel: a process group's first member, which kills its whole group `after` its start whoever else is gone.
pub(in crate::rustc) fn sentinel(shell: &str, after: f64) -> std::io::Result<Child> {
    Command::new(shell)
        .args(["-c", "sleep \"$0\"; kill -s KILL 0", &format!("{after:.3}")])
        .env_remove(WARDEN)
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .process_group(0)
        .spawn()
}

/// `sig` to every process of `group`.
pub(super) fn signal(shell: &str, group: i32, sig: &str) {
    let _ = Command::new(shell)
        .args(["-c", "kill -s \"$0\" -- \"-$1\"", sig, &group.to_string()])
        .stderr(Stdio::null())
        .status();
}

/// A run's standard output and error, both its log; nowhere where the log cannot be made.
fn logged(path: &Path) -> (Stdio, Stdio) {
    File::create(path)
        .and_then(|f| Ok((f.try_clone()?, f)))
        .map_or_else(
            |_| (Stdio::null(), Stdio::null()),
            |(a, b)| (Stdio::from(a), Stdio::from(b)),
        )
}

fn stopped(gate: &Mutex<bool>) -> bool {
    gate.lock().map_or(true, |g| *g)
}

/// What a copy's thread needs.
struct Copy {
    shell: String,
    cmd: String,
    root: PathBuf,
    dir: PathBuf,
    group: i32,
    loops: usize,
    deadline: Instant,
    gate: Arc<Mutex<bool>>,
}

impl Copy {
    /// Copy `copy`'s loops: each started under the gate's lock, so none starts once the group is being ended.
    fn run(&self, copy: usize) -> Vec<Done> {
        let mut done = Vec::new();
        for turn in 1..=self.loops {
            let log = self.dir.join(format!("c{copy}-l{turn}.log"));
            let child = {
                let Ok(gate) = self.gate.lock() else { break };
                if *gate || Instant::now() >= self.deadline {
                    break;
                }
                let (out, err) = logged(&log);
                Command::new(&self.shell)
                    .args(["-c", &self.cmd])
                    .current_dir(&self.root)
                    .env("L7R_UNDER_LOAD_COPY", copy.to_string())
                    .env("L7R_UNDER_LOAD_LOOP", turn.to_string())
                    .env_remove(WARDEN)
                    .stdin(Stdio::null())
                    .stdout(out)
                    .stderr(err)
                    .process_group(self.group)
                    .spawn()
            };
            let code = child
                .ok()
                .and_then(|mut c| c.wait().ok())
                .and_then(|s| s.code());
            let cut = code != Some(0) && stopped(&self.gate);
            done.push(Done {
                copy,
                turn,
                code,
                cut,
                log,
            });
        }
        done
    }
}

/// The burners started in `group`, and the caller's pipe read to its end on a thread left behind: its end is the caller's going.
fn started(
    knobs: &Knobs,
    burners: usize,
    group: i32,
    mut caller: Box<dyn Read + Send>,
) -> (Vec<Child>, Arc<AtomicBool>) {
    let burners: Vec<Child> = (0..burners)
        .filter_map(|_| {
            Command::new(&knobs.shell)
                .args(["-c", &knobs.burner])
                .env_remove(WARDEN)
                .stdin(Stdio::null())
                .stdout(Stdio::null())
                .stderr(Stdio::null())
                .process_group(group)
                .spawn()
                .ok()
        })
        .collect();
    let gone = Arc::new(AtomicBool::new(false));
    let told = Arc::clone(&gone);
    std::thread::spawn(move || {
        let mut buf = [0u8; 64];
        while caller.read(&mut buf).is_ok_and(|n| n > 0) {}
        told.store(true, Ordering::SeqCst);
    });
    (burners, gone)
}

/// The group ended - TERM and a grace for a run cut short, then KILL - and every copy's runs gathered.
fn end(
    knobs: &Knobs,
    group: i32,
    ended: Ended,
    copies: Vec<JoinHandle<Vec<Done>>>,
    gate: &Mutex<bool>,
) -> Vec<Done> {
    if let Ok(mut g) = gate.lock() {
        *g = true;
    }
    if ended != Ended::Done {
        signal(&knobs.shell, group, "TERM");
        let until = Instant::now() + knobs.grace;
        while !copies.iter().all(JoinHandle::is_finished) && Instant::now() < until {
            std::thread::sleep(knobs.poll);
        }
    }
    signal(&knobs.shell, group, "KILL");
    copies
        .into_iter()
        .flat_map(|h| h.join().unwrap_or_default())
        .collect()
}

/// The run: everything in the sentinel's group, watched until every loop ran, the bound or the caller's going, then the group ended.
pub(super) fn run(world: &World, ask: &Ask, knobs: &Knobs, caller: Box<dyn Read + Send>) -> Reply {
    let (began, start) = (SystemTime::now(), Instant::now());
    let deadline = start + ask.max;
    let load0 = load(&knobs.proc_root);
    let dir = knobs.out_root.join(format!(
        "l7r-under-load-{}-{}",
        now_stamp(began).replace([':', '.'], ""),
        std::process::id()
    ));
    let _ = std::fs::create_dir_all(&dir);
    let after = (ask.max + knobs.grace * 2).as_secs_f64();
    let mut sentinel = match sentinel(&knobs.shell, after) {
        Ok(c) => c,
        Err(e) => {
            return Reply {
                stdout: String::new(),
                stderr: format!("under-load: no sentinel ({}): {e}\n", knobs.shell),
                code: 1,
            }
        }
    };
    // a pid fits an i32 (the kernel's pid_t)
    let group = i32::try_from(sentinel.id()).unwrap_or(i32::MAX);
    let _ = std::io::stderr().write_all(
        format!(
            "under-load: group {group}, bound {} (all killed by {}), logs in {}\n",
            now_stamp(began + ask.max),
            now_stamp(began + ask.max + knobs.grace * 2),
            dir.display()
        )
        .as_bytes(),
    );
    let (burners, gone) = started(knobs, ask.burners, group, caller);
    let gate = Arc::new(Mutex::new(false));
    let copy = Arc::new(Copy {
        shell: knobs.shell.clone(),
        cmd: ask.cmd.clone(),
        root: world.root.to_path_buf(),
        dir: dir.clone(),
        group,
        loops: ask.loops,
        deadline,
        gate: Arc::clone(&gate),
    });
    let copies: Vec<JoinHandle<Vec<Done>>> = (1..=ask.copies)
        .map(|i| {
            let c = Arc::clone(&copy);
            std::thread::spawn(move || c.run(i))
        })
        .collect();
    let all_done = |c: &[JoinHandle<Vec<Done>>]| c.iter().all(JoinHandle::is_finished);
    let mut peak = load0;
    let ended = loop {
        peak = peak.max(load(&knobs.proc_root));
        if all_done(&copies) {
            break Ended::Done;
        }
        if gone.load(Ordering::SeqCst) {
            break Ended::Gone;
        }
        if Instant::now() >= deadline {
            break Ended::Bound;
        }
        std::thread::sleep(knobs.poll);
    };
    let runs = end(knobs, group, ended, copies, &gate);
    for mut b in burners {
        let _ = b.wait();
    }
    let _ = sentinel.wait();
    let load1 = load(&knobs.proc_root);
    let report = Report {
        ask,
        knobs,
        runs: &runs,
        group,
        dir: &dir,
        ended,
        loads: (load0, peak.max(load1), load1),
        span: (began, SystemTime::now()),
    };
    report.reply(world)
}

/// What the report and the `Phase` line say.
struct Report<'a> {
    ask: &'a Ask,
    knobs: &'a Knobs,
    runs: &'a [Done],
    group: i32,
    dir: &'a Path,
    ended: Ended,
    /// (at the start, the peak, at the end)
    loads: (f64, f64, f64),
    span: (SystemTime, SystemTime),
}

impl Report<'_> {
    fn reply(&self, world: &World) -> Reply {
        let red: Vec<&Done> = self
            .runs
            .iter()
            .filter(|d| d.code != Some(0) && !d.cut)
            .collect();
        let cut = self.runs.iter().filter(|d| d.cut).count();
        for d in self.runs.iter().filter(|d| d.code == Some(0)) {
            let _ = std::fs::remove_file(&d.log);
        }
        let code = i32::from(!red.is_empty());
        let (ask, (l0, peak, l1)) = (self.ask, self.loads);
        let (t0, t1) = (now_stamp(self.span.0), now_stamp(self.span.1));
        let mut out = format!(
            "under-load: `{}` - {} copies x {} loops beside {} burners, bound {:.1} min, group {}\n  ran {} of {}: {} red, {cut} cut, {} green\n",
            ask.cmd,
            ask.copies,
            ask.loops,
            ask.burners,
            ask.max.as_secs_f64() / 60.0,
            self.group,
            self.runs.len(),
            ask.copies * ask.loops,
            red.len(),
            self.runs.len() - red.len() - cut,
        );
        for d in red.iter().take(NAMED) {
            let how = d
                .code
                .map_or_else(|| "a signal".to_owned(), |c| format!("exit {c}"));
            let _ = writeln!(
                out,
                "  red: copy {} loop {} ({how}): {}",
                d.copy,
                d.turn,
                d.log.display()
            );
        }
        let _ = writeln!(
            out,
            "  load (1-min, {} cores): {l0:.2} at the start {t0}, peak {peak:.2}, {l1:.2} at the end {t1}\n  ended: {}\n  logs: {} (the red and cut runs' output)",
            self.knobs.cores,
            self.ended.said(),
            self.dir.display()
        );
        let fields: Map<String, Value> = [
            ("cmd", json!(ask.cmd)),
            ("copies", json!(ask.copies)),
            ("loops", json!(ask.loops)),
            ("burners", json!(ask.burners)),
            ("max_minutes", json!(ask.max.as_secs_f64() / 60.0)),
            ("runs", json!(self.runs.len())),
            ("red", json!(red.len())),
            ("cut", json!(cut)),
            ("load_start", json!(l0)),
            ("load_peak", json!(peak)),
            ("load_end", json!(l1)),
            ("ended", json!(self.ended.said())),
            ("group", json!(self.group)),
            ("logs", json!(self.dir.display().to_string())),
        ]
        .into_iter()
        .map(|(k, v)| (k.to_owned(), v))
        .collect();
        phase::wrote_with(world, STEP, (self.span.0, code), fields);
        Reply {
            stdout: out,
            stderr: String::new(),
            code,
        }
    }
}
