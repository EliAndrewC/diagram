//! The stall watchdog's one pass (`lib/stall_watchdog.py`, ported in T016): every live session judged from outside it.
//!
//! WHAT IS A STALL (spec 295 FR-005a, plan D5). All of: silent an hour or more (the newest write to its transcript or any of its
//! subagents'); not waiting on the GM (registry status `waiting`, or a pending `AskUserQuestion`); unfinished work in its clone
//! (uncommitted changes, commits not on main, or a live make - the mirror is never a workspace and never counts); and not one of a
//! page-session queue's own sessions while that queue is in its usage-limit retry wait, which holds only while the queue's runner lives
//! and its retry line is younger than the wait it states (plan review round 1 found three stale retry lines that must exempt nothing);
//! nor the session that waits on its clone's landing lane by design (feature 461 T12: [`lane_works`] - the runner's exact argv live,
//! and a `l7r-gate lane wait` in the clone that the session itself started).
//!
//! WHAT IT DOES (the GM, 2026-09-30: "Tab title + bell"; "Nudge if prompt empty"; plan D6). The stalled session's tab is retitled and
//! the bell rung, once per stall; in the session's OWN pane, when the input line is empty, one nudge is typed, once per stall. A
//! session with no pane of its own is marked on its host's tab and never nudged: the GM approved typing into a stalled session's own
//! pane only. Its log line carries the command that resumes it.
//!
//! A MAKE THAT RUNS TOO LONG IS TOLD TO ITS SESSION (the GM, 2026-11-09: "I thought we had tooling to prevent a stuck command from
//! blocking us from doing work for that amount of time"). A stall is a SILENT session; a session that answers the GM while its
//! background `make static` spins is not silent, and a spinning check ran four hours and ten minutes that way. So each pass also
//! looks for a `make` running in the session's clone past [`LONG_RUN`], whatever the session is doing, and says so once per make:
//! the tab and the bell, and, in its own pane with the input line empty, one nudge. It reports and kills nothing: only the session
//! knows whether the run is meant to be long.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use fancy_regex::Regex;
use serde_json::{json, Value};

use crate::shared::log::civil;
use crate::shared::tool::{ask_within, Said};

/// The runner resumes a minute or so after the wait it logged; five minutes of slack covers that and no more.
const RETRY_SLACK: f64 = 300.0;

static RETRY: LazyLock<Regex> = LazyLock::new(|| {
    crate::shared::regex::build(r"^failed (\S+) .* - waiting (\d+) min")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// CONVENTION, a knob (`STALL_LONG_RUN`): a gate run took at most 1,300 s in 1,051 of the 1,052 recorded in `dev/run-log/` for
/// October and November 2026; the one over it, 27,900 s, is an outlier. Thirty minutes is past every one of those.
const LONG_RUN: f64 = 1800.0;

/// Every path and the tmux binary, from the environment when set, so a suite drives a pass against fixtures.
pub(crate) struct Paths {
    pub sessions: PathBuf,
    pub projects: PathBuf,
    pub state: PathBuf,
    pub clones: PathBuf,
    pub mirror: PathBuf,
    pub proc: PathBuf,
    pub tmux: Vec<String>,
    pub stall_after: f64,
    pub long_run: f64,
    pub dry: bool,
}

impl Paths {
    pub(crate) fn from_env(env: &dyn Fn(&str) -> Option<String>) -> Self {
        let set = |k: &str| env(k).filter(|v| !v.is_empty());
        let home = set("HOME").unwrap_or_default();
        let under =
            |k: &str, rel: &str| set(k).map_or_else(|| Path::new(&home).join(rel), PathBuf::from);
        let or = |k: &str, d: &str| PathBuf::from(set(k).unwrap_or_else(|| d.to_owned()));
        Self {
            sessions: under("STALL_SESSIONS_DIR", ".claude/sessions"),
            projects: under("STALL_PROJECTS_DIR", ".claude/projects"),
            state: under("STALL_STATE_DIR", ".claude/stall-watchdog"),
            clones: or("STALL_CLONES_MAP", "/diagram/.clones/.session-clones"),
            mirror: or("STALL_MIRROR", "/diagram"),
            proc: or("STALL_PROC", "/proc"),
            tmux: set("STALL_TMUX")
                .unwrap_or_else(|| "tmux".to_owned())
                .split_whitespace()
                .map(str::to_owned)
                .collect(),
            stall_after: set("STALL_AFTER")
                .and_then(|v| v.parse().ok())
                .unwrap_or(3600.0),
            long_run: set("STALL_LONG_RUN")
                .and_then(|v| v.parse().ok())
                .unwrap_or(LONG_RUN),
            dry: set("STALL_DRYRUN").is_some(),
        }
    }
}

#[expect(
    clippy::cast_precision_loss,
    reason = "a wall clock's seconds, far inside f64's exact range"
)]
fn float(secs: u64) -> f64 {
    secs as f64
}

#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    reason = "whole seconds of a wall clock, as the Python's int() took them"
)]
fn whole(secs: f64) -> u64 {
    secs as u64
}

/// A file's JSON, or None.
fn read_json(p: &Path) -> Option<Value> {
    serde_json::from_str(&std::fs::read_to_string(p).ok()?).ok()
}

fn text<'a>(v: &'a Value, k: &str) -> &'a str {
    v.get(k).and_then(Value::as_str).unwrap_or("")
}

/// The sorted entries of a directory that are not hidden, as a glob's `*` lists them.
fn listed(dir: &Path) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = std::fs::read_dir(dir)
        .map(|d| d.filter_map(Result::ok).map(|e| e.path()).collect())
        .unwrap_or_default();
    out.retain(|p| {
        p.file_name()
            .is_some_and(|n| !n.to_string_lossy().starts_with('.'))
    });
    out.sort();
    out
}

fn has_ext(p: &Path, ext: &str) -> bool {
    p.extension().is_some_and(|x| x == ext)
}

/// The modification time as `CPython`'s `st_mtime` reads it, so a stall recorded before the port is still the same stall.
fn mtime(p: &Path) -> Option<f64> {
    let d = std::fs::metadata(p)
        .ok()?
        .modified()
        .ok()?
        .duration_since(UNIX_EPOCH)
        .ok()?;
    Some(float(d.as_secs()) + 1e-9 * f64::from(d.subsec_nanos()))
}

fn alive(pid: Option<&Value>) -> bool {
    pid.map(|v| v.as_str().map_or_else(|| v.to_string(), str::to_owned))
        .filter(|p| !p.is_empty() && p.chars().all(|c| c.is_ascii_digit()))
        .is_some_and(|p| Path::new("/proc").join(p).is_dir())
}

/// Every registry entry whose process lives: stale files of dead pids stay behind and are skipped.
pub(crate) fn live_sessions(p: &Paths) -> Vec<Value> {
    listed(&p.sessions)
        .iter()
        .filter(|f| has_ext(f, "json"))
        .filter_map(|f| read_json(f))
        .filter(|d| d.is_object() && !text(d, "sessionId").is_empty() && alive(d.get("pid")))
        .collect()
}

fn transcripts(p: &Paths, sid: &str) -> Vec<PathBuf> {
    let mut out = Vec::new();
    for project in listed(&p.projects) {
        let main = project.join(format!("{sid}.jsonl"));
        if main.exists() {
            out.push(main);
        }
        out.extend(
            listed(&project.join(sid).join("subagents"))
                .into_iter()
                .filter(|f| has_ext(f, "jsonl")),
        );
    }
    out
}

/// Is the transcript's last record an `AskUserQuestion` call still waiting for its answer?
pub(crate) fn asking_gm(transcript: &Path) -> bool {
    const TAIL: usize = 262_144;
    let Ok(bytes) = std::fs::read(transcript) else {
        return false;
    };
    let body = String::from_utf8_lossy(&bytes[bytes.len().saturating_sub(TAIL)..]).into_owned();
    for line in body.lines().rev() {
        let Ok(rec) = serde_json::from_str::<Value>(line) else {
            continue;
        };
        let kind = text(&rec, "type");
        let Some(msg) = rec
            .get("message")
            .filter(|m| m.is_object())
            .filter(|_| kind == "assistant" || kind == "user")
        else {
            continue;
        };
        if kind == "user" {
            return false;
        }
        return msg
            .get("content")
            .and_then(Value::as_array)
            .is_some_and(|c| {
                c.iter()
                    .any(|b| text(b, "type") == "tool_use" && text(b, "name") == "AskUserQuestion")
            });
    }
    false
}

/// `git -C <clone> args`, bounded as the Python was.
fn git(clone: &str, args: &[&str]) -> Said {
    let all: Vec<&str> = ["-C", clone]
        .into_iter()
        .chain(args.iter().copied())
        .collect();
    ask_within(Path::new("/"), "git", &all, Duration::from_secs(30))
}

fn real(p: &Path) -> PathBuf {
    std::fs::canonicalize(p).unwrap_or_else(|_| p.to_path_buf())
}

/// The working tree the session works in: its claim in the session-clone map, else its cwd's - never the mirror.
pub(crate) fn clone_of(p: &Paths, entry: &Value) -> String {
    let claimed =
        std::fs::read_to_string(p.clones.join(text(entry, "sessionId"))).unwrap_or_default();
    let claimed = claimed.trim();
    let cwd = Some(text(entry, "cwd"))
        .filter(|c| !c.is_empty())
        .unwrap_or("/");
    let clone = if claimed.is_empty() {
        git(cwd, &["rev-parse", "--show-toplevel"]).out
    } else {
        claimed.to_owned()
    };
    if clone.is_empty() || real(Path::new(&clone)) == real(&p.mirror) {
        return String::new();
    }
    clone
}

/// What is unfinished in the clone, in words, or nothing. LANDED is asked of the mirror, which fast-forwards from GitHub main: a
/// clone's own `origin/main` is only as fresh as its last fetch (a dry run on 2026-09-30 read a landed clone as 147 commits behind).
pub(crate) fn unfinished(p: &Paths, clone: &str) -> String {
    let mut what = Vec::new();
    if !git(clone, &["status", "--porcelain"]).out.is_empty() {
        what.push("uncommitted changes");
    }
    let head = git(clone, &["rev-parse", "HEAD"]).out;
    let mirror = p.mirror.to_string_lossy();
    if !head.is_empty() && !git(&mirror, &["merge-base", "--is-ancestor", &head, "main"]).ok() {
        what.push("commits not on main");
    }
    let procs = crate::guards::finished_run_hooks::runs::Procs {
        root: p.proc.clone(),
        mine: std::process::id(),
    };
    if !procs.live_runs(Path::new(clone)).is_empty() {
        what.push("a live make");
    }
    what.join(", ")
}

fn cmdlines(p: &Paths) -> Vec<Vec<String>> {
    listed(&p.proc)
        .iter()
        .filter(|d| {
            d.file_name().is_some_and(|n| {
                n.to_string_lossy()
                    .starts_with(|c: char| c.is_ascii_digit())
            })
        })
        .filter_map(|d| std::fs::read(d.join("cmdline")).ok())
        .map(|b| {
            b.split(|c| *c == 0)
                .map(|a| String::from_utf8_lossy(a).into_owned())
                .collect()
        })
        .collect()
}

/// Is `sid` a session of a page-session queue whose live runner is in a current usage-limit retry wait?
pub(crate) fn in_retry_wait(p: &Paths, clone: &str, sid: &str, now: f64) -> bool {
    let runs = listed(&Path::new(clone).join(".git/page-sessions"));
    runs.iter()
        .filter(|f| {
            f.file_name()
                .is_some_and(|n| n.to_string_lossy().starts_with("run-"))
                && has_ext(f, "log")
        })
        .any(|log| {
            let bytes = std::fs::read(log).unwrap_or_default();
            let body = String::from_utf8_lossy(&bytes);
            let lines: Vec<&str> = body.lines().filter(|l| !l.trim().is_empty()).collect();
            let waited = lines
                .last()
                .and_then(|l| RETRY.captures(l).ok().flatten())
                .and_then(|m| m[2].parse::<f64>().ok());
            let named = log.to_string_lossy();
            lines.iter().any(|l| l.contains(&format!("started {sid}")))
                && waited
                    .is_some_and(|min| now - mtime(log).unwrap_or(0.0) <= min * 60.0 + RETRY_SLACK)
                && cmdlines(p).iter().any(|argv| runs_queue(argv, &named))
        })
}

/// Is `argv` the page-session runner's detached queue writing the run log `log`? Exactly its own command line, `<dir>/l7r-gate
/// page-session --work <root> <name> <extra> <queue> <log>` (feature 449 T137: the runner is the gate binary's `page-session` since
/// `page_session_runner.py` was ported, and it starts itself again by that argv), never a process that merely names the log.
pub(crate) fn runs_queue(argv: &[String], log: &str) -> bool {
    // `/proc/<pid>/cmdline` ends each argument with a NUL, so its split ends with an empty one
    let argv = argv.strip_suffix(&[String::new()]).unwrap_or(argv);
    matches!(argv, [exe, verb, work, _, _, _, _, at]
        if exe.rsplit('/').next() == Some("l7r-gate") && verb == "page-session" && work == "--work" && at == log)
}

/// Is `argv` the landing lane's runner of the git common directory `common`? Exactly its own command line, `<dir>/l7r-gate lane
/// --work <common>` (feature 461 T12, the gate's `lane` crate, `runner::argv`), never a process that merely names the directory.
pub(crate) fn runs_lane(argv: &[String], common: &Path) -> bool {
    let argv = argv.strip_suffix(&[String::new()]).unwrap_or(argv);
    matches!(argv, [exe, verb, work, at]
        if exe.rsplit('/').next() == Some("l7r-gate") && verb == "lane" && work == "--work" && real(Path::new(at)) == real(common))
}

/// Is `argv` the landing lane's wake-up, exactly `<dir>/l7r-gate lane wait` (feature 461 T20's command, D9)?
pub(crate) fn waits_on_lane(argv: &[String]) -> bool {
    let argv = argv.strip_suffix(&[String::new()]).unwrap_or(argv);
    matches!(argv, [exe, verb, wait] if exe.rsplit('/').next() == Some("l7r-gate") && verb == "lane" && wait == "wait")
}

/// Is `argv` (a make's, its trailing NUL's empty word kept or not) `make lane-wait` - its one target `lane-wait`, past its flags and
/// `VAR=` words, a valued flag's value too (feature 461 T21, T47)? It stands for the wait from its start, while `l7r-gate.sh` may still be building the binary
/// that runs `l7r-gate lane wait` (461 T54: 2 to 112 s).
pub(crate) fn lane_wait_make(argv: &[String]) -> bool {
    let Some((exe, rest)) = argv.split_first() else {
        return false;
    };
    // a flag that takes the next word as its value (`make -C <clone> lane-wait`, the Stop rule's command)
    let valued = ["-C", "-f", "-I", "-o", "-W"];
    let targets: Vec<&String> = rest
        .iter()
        .enumerate()
        .filter(|(i, _)| *i == 0 || !valued.contains(&rest[i - 1].as_str()))
        .map(|(_, a)| a)
        .filter(|a| !a.is_empty() && !a.starts_with('-') && !a.contains('='))
        .collect();
    exe.rsplit('/').next() == Some("make") && targets == ["lane-wait"]
}

/// Does the session whose process is `session` wait on `clone`'s landing lane by design (461 T12, narrowed at its plan review)?
/// D9: the coordinator ends its turn on a backgrounded `make lane-wait` while a batch runs, so its silence is not a stall. Both hold:
/// the clone's runner lives (its exact argv, [`runs_lane`]); and a `l7r-gate lane wait` THIS session started (a descendant of its
/// registry pid, [`descends`]) runs with its working directory in the clone - T20's command, so before T20 this exempts no one, and
/// another session of the clone, whose process the wait does not descend from, is judged as before. It ends with the wait or the runner.
pub(crate) fn lane_works(p: &Paths, clone: &str, session: Option<u64>) -> bool {
    let Some(session) = session else {
        return false;
    };
    let common = Path::new(clone).join(".git");
    cmdlines(p).iter().any(|argv| runs_lane(argv, &common))
        && listed(&p.proc).iter().any(|d| {
            let bytes = std::fs::read(d.join("cmdline")).unwrap_or_default();
            let argv: Vec<String> = bytes
                .split(|c| *c == 0)
                .map(|a| String::from_utf8_lossy(a).into_owned())
                .collect();
            waits_on_lane(&argv)
                && std::fs::read_link(d.join("cwd")).is_ok_and(|c| c.starts_with(clone))
                && descends(p, d, session)
        })
}

/// Does the process at `dir` (a `/proc/<pid>`) descend from `ancestor`, by its parents' `stat` (the field after the state)? Bounded
/// at 64 steps, a GUESS well past any shell's nesting, so a cycle in a fake or racing `/proc` ends.
fn descends(p: &Paths, dir: &Path, ancestor: u64) -> bool {
    let mut at = dir.to_path_buf();
    for _ in 0..64 {
        let stat = std::fs::read_to_string(at.join("stat")).unwrap_or_default();
        let parent = stat
            .rsplit(')')
            .next()
            .and_then(|rest| rest.split_whitespace().nth(1))
            .and_then(|f| f.parse::<u64>().ok());
        match parent {
            Some(pid) if pid == ancestor => return true,
            Some(pid) if pid > 1 => at = p.proc.join(pid.to_string()),
            _ => return false,
        }
    }
    false
}

fn dispatcher_of(p: &Paths, pid: Option<&Value>) -> String {
    let id = pid.map_or_else(String::new, |v| {
        v.as_str().map_or_else(|| v.to_string(), str::to_owned)
    });
    let bytes = std::fs::read(p.proc.join(id).join("environ")).unwrap_or_default();
    bytes
        .split(|c| *c == 0)
        .find_map(|e| {
            e.strip_prefix(b"L7R_DISPATCHER=")
                .map(|v| String::from_utf8_lossy(v).into_owned())
        })
        .unwrap_or_default()
}

fn pane(entry: &Value) -> String {
    text(entry, "tmux")
        .rsplit('.')
        .next()
        .unwrap_or("")
        .to_owned()
}

/// The pane the stall lands on, and whether it is the session's OWN (plan D6, spec FR-005c).
pub(crate) fn host_pane(p: &Paths, entry: &Value, regs: &[Value], clone: &str) -> (String, bool) {
    if !text(entry, "tmux").is_empty() {
        return (pane(entry), true);
    }
    let with_pane = |r: &&Value| !text(r, "tmux").is_empty();
    let disp = dispatcher_of(p, entry.get("pid"));
    let job = text(entry, "jobId");
    let dispatched = regs
        .iter()
        .filter(with_pane)
        .find(|r| !disp.is_empty() && text(r, "sessionId") == disp);
    let parked = regs
        .iter()
        .filter(with_pane)
        .find(|r| !job.is_empty() && text(r, "parkedJobId") == job);
    let shared = || {
        regs.iter().filter(with_pane).find(|r| {
            *r != entry
                && text(r, "kind") == "interactive"
                && !clone.is_empty()
                && clone_of(p, r) == clone
        })
    };
    dispatched
        .or(parked)
        .or_else(shared)
        .map_or_else(|| (String::new(), false), |r| (pane(r), false))
}

/// A stall.
pub(crate) struct Stall {
    pub last: f64,
    pub idle: u64,
    pub clone: String,
    pub what: String,
}

/// The stall, or None.
pub(crate) fn judge(p: &Paths, entry: &Value, now: f64) -> Option<Stall> {
    let sid = text(entry, "sessionId");
    let all = transcripts(p, sid);
    let last = all
        .iter()
        .filter_map(|t| mtime(t))
        .fold(None, |m: Option<f64>, t| Some(m.map_or(t, |x| x.max(t))))?;
    if now - last < p.stall_after || text(entry, "status") == "waiting" {
        return None;
    }
    let name = format!("{sid}.jsonl");
    if all
        .iter()
        .find(|t| t.file_name().is_some_and(|n| n.to_string_lossy() == name))
        .is_some_and(|t| asking_gm(t))
    {
        return None;
    }
    let clone = clone_of(p, entry);
    let what = if clone.is_empty() {
        String::new()
    } else {
        unfinished(p, &clone)
    };
    if what.is_empty()
        || in_retry_wait(p, &clone, sid, now)
        || lane_works(p, &clone, entry.get("pid").and_then(Value::as_u64))
    {
        return None;
    }
    Some(Stall {
        last,
        idle: whole(now - last),
        clone,
        what,
    })
}

pub(crate) fn human(seconds: u64) -> String {
    let (h, m) = (seconds / 3600, seconds / 60 % 60);
    if h > 0 {
        format!("{h}h{m:02}m")
    } else {
        format!("{m}m")
    }
}

fn tmux(p: &Paths, args: &[&str]) -> String {
    let all: Vec<&str> = p.tmux[1..]
        .iter()
        .map(String::as_str)
        .chain(args.iter().copied())
        .collect();
    ask_within(Path::new("/"), &p.tmux[0], &all, Duration::from_secs(10)).out
}

/// One line between the last two rules, and it is the prompt mark with nothing typed after it.
pub(crate) fn input_empty(p: &Paths, target: &str) -> bool {
    let screen = tmux(p, &["capture-pane", "-p", "-t", target]);
    let lines: Vec<&str> = screen.lines().collect();
    let rules: Vec<usize> = lines
        .iter()
        .enumerate()
        .filter(|(_, l)| l.trim_start().chars().take_while(|c| *c == '─').count() >= 10)
        .map(|(i, _)| i)
        .collect();
    let [.., a, b] = rules[..] else {
        return false;
    };
    let between = &lines[a + 1..b];
    between.len() == 1 && between[0].trim() == "❯"
}

fn mark(p: &Paths, target: &str, name: &str, idle: u64, bell: bool) -> bool {
    let tty = tmux(p, &["display", "-p", "-t", target, "#{pane_tty}"]);
    let title = format!(
        "\u{1b}]0;\u{26a0} STALLED {} - {name}\u{7}{}",
        human(idle),
        if bell { "\u{7}" } else { "" }
    );
    !tty.trim().is_empty() && std::fs::write(tty.trim(), title).is_ok()
}

/// The command that resumes a session with no pane of its own.
pub(crate) fn resume_command(entry: &Value, clone: &str) -> String {
    let sid = text(entry, "sessionId");
    let index = std::fs::read_to_string(Path::new(clone).join(".git/page-sessions/index.txt"))
        .unwrap_or_default();
    let prefix = format!("{sid} ");
    let brief = index
        .lines()
        .find_map(|l| l.strip_prefix(&prefix))
        .map_or("", str::trim);
    if brief.is_empty() {
        let cwd = Some(text(entry, "cwd"))
            .filter(|c| !c.is_empty())
            .unwrap_or(clone);
        return format!("cd {cwd} && claude --resume {sid}");
    }
    format!("make page-session BRIEF=\"resume:{sid}:{brief}\"")
}

/// The stall's tab, bell and nudge, and the record of them: the log line.
fn act(p: &Paths, entry: &Value, regs: &[Value], stall: &Stall, now: f64) -> String {
    let sid = text(entry, "sessionId");
    let path = p.state.join(format!("{sid}.json"));
    let earlier = read_json(&path).unwrap_or(Value::Null);
    // activity since the last stall makes a new one; within a microsecond, because JSON's float does not come back to the last bit
    let same = earlier
        .get("stall")
        .and_then(Value::as_f64)
        .is_some_and(|at| (at - stall.last).abs() < 1e-6);
    let flag = |k: &str| same && earlier.get(k).and_then(Value::as_bool).unwrap_or(false);
    let (mut belled, mut nudged) = (flag("belled"), flag("nudged"));
    let name = Some(text(entry, "name"))
        .filter(|n| !n.is_empty())
        .map_or_else(
            || {
                Path::new(&stall.clone)
                    .file_name()
                    .map(|n| n.to_string_lossy().into_owned())
                    .unwrap_or_default()
            },
            str::to_owned,
        );
    let (target, own) = host_pane(p, entry, regs, &stall.clone);
    let marked = !target.is_empty() && mark(p, &target, &name, stall.idle, !belled);
    belled = belled || marked;
    let mut said_nudge = "";
    if own && marked && !nudged && input_empty(p, &target) {
        let words = format!(
            "watchdog (feature 295): this session has been idle {} min with unfinished work in {} ({}). If you are waiting on the GM, say so in one line and stop; otherwise check your background work and carry on.",
            stall.idle / 60, stall.clone, stall.what
        );
        tmux(p, &["send-keys", "-t", &target, "-l", &words]);
        tmux(p, &["send-keys", "-t", &target, "Enter"]);
        nudged = true;
        said_nudge = "; nudged";
    }
    let place = if !marked {
        "no tab, logged only".to_owned()
    } else if own {
        format!("marked {target} (own)")
    } else {
        format!("marked {target} (host)")
    };
    let resume = if own {
        String::new()
    } else {
        format!("; resume: {}", resume_command(entry, &stall.clone))
    };
    let _ = std::fs::write(
        &path,
        json!({"stall": stall.last, "belled": belled, "nudged": nudged}).to_string(),
    );
    let (year, month, day, hour, minute, second) = civil(whole(now));
    format!(
        "{year:04}-{month:02}-{day:02}T{hour:02}:{minute:02}:{second:02}Z stalled {name} ({sid}) idle {} min, {} in {}; {place}{said_nudge}{resume}",
        stall.idle / 60, stall.what, stall.clone
    )
}

/// A `make` in a clone: its pid, how long it has run, its command line.
struct LongRun {
    pid: String,
    seconds: u64,
    command: String,
    argv: Vec<String>,
}

/// The make at `dir` (a `/proc/<pid>`), when it is one and runs inside `clone`.
fn make_in(dir: &Path, clone: &str, boot: u64, now: f64) -> Option<LongRun> {
    let bytes = std::fs::read(dir.join("cmdline")).ok()?;
    let command = String::from_utf8_lossy(&bytes).replace('\0', " ");
    if Path::new(command.split(' ').next()?).file_name()? != "make" {
        return None;
    }
    if !std::fs::read_link(dir.join("cwd")).ok()?.starts_with(clone) {
        return None;
    }
    let stat = std::fs::read_to_string(dir.join("stat")).ok()?;
    // the fields after the name in parentheses, the state first: the start time, in ticks since boot, is the twentieth of them
    let ticks: u64 = stat
        .rsplit(')')
        .next()?
        .split_whitespace()
        .nth(19)?
        .parse()
        .ok()?;
    Some(LongRun {
        pid: dir.file_name()?.to_string_lossy().into_owned(),
        seconds: whole(now).saturating_sub(boot + ticks / 100),
        command: command.trim().to_owned(),
        argv: bytes
            .split(|c| *c == 0)
            .map(|a| String::from_utf8_lossy(a).into_owned())
            .collect(),
    })
}

/// The oldest `make` in the clone that has run past the limit; a `make lane-wait` passed over where `waits` (461 T47).
fn long_run(p: &Paths, clone: &str, now: f64, waits: bool) -> Option<LongRun> {
    let stat = std::fs::read_to_string(p.proc.join("stat")).ok()?;
    let boot: u64 = stat
        .lines()
        .find_map(|l| l.strip_prefix("btime "))?
        .trim()
        .parse()
        .ok()?;
    listed(&p.proc)
        .iter()
        .filter_map(|d| make_in(d, clone, boot, now))
        .filter(|r| r.seconds >= whole(p.long_run))
        .filter(|r| !(waits && lane_wait_make(&r.argv)))
        .max_by_key(|r| r.seconds)
}

/// Tell the session once about this make, or wait for its input line to be empty; the log line when told.
fn warn_long(
    p: &Paths,
    entry: &Value,
    regs: &[Value],
    clone: &str,
    run: &LongRun,
    now: f64,
) -> Option<String> {
    let sid = text(entry, "sessionId");
    let path = p.state.join(format!("{sid}.long-run"));
    if std::fs::read_to_string(&path).is_ok_and(|told| told == run.pid) {
        return None;
    }
    let (target, own) = host_pane(p, entry, regs, clone);
    if own && !input_empty(p, &target) {
        return None;
    }
    let name = text(entry, "name");
    let marked = !target.is_empty() && mark(p, &target, name, run.seconds, true);
    if own && marked {
        let words = format!(
            "watchdog: `{}` (pid {}) has been running {} in {clone}, past any recorded gate run. Check that it is still making progress; if it is stuck, kill it by pid and fix the cause, and if it is meant to run this long, say why in one line and carry on.",
            run.command, run.pid, human(run.seconds)
        );
        tmux(p, &["send-keys", "-t", &target, "-l", &words]);
        tmux(p, &["send-keys", "-t", &target, "Enter"]);
    }
    let _ = std::fs::write(&path, &run.pid);
    let (year, month, day, hour, minute, second) = civil(whole(now));
    Some(format!(
        "{year:04}-{month:02}-{day:02}T{hour:02}:{minute:02}:{second:02}Z long run {name} ({sid}): {} (pid {}) {} in {clone}",
        run.command, run.pid, human(run.seconds)
    ))
}

/// What a pass says about a long make in this session's clone, if anything.
fn long_run_line(p: &Paths, entry: &Value, regs: &[Value], now: f64) -> Option<String> {
    let clone = clone_of(p, entry);
    if clone.is_empty() {
        return None;
    }
    // THE COORDINATOR'S `make lane-wait` RUNS AS LONG AS A BATCH, BY DESIGN (461 T47, D9): passed over while its lane works - the
    // runner live and the wait the session's own (T12's `lane_works`) - or each long batch would cost a wake FR-005 does not list
    // (540k-966k tokens a wake, D9). Only that make: another long make beside it is told, and with the runner gone the wait is too.
    let waits = lane_works(p, &clone, entry.get("pid").and_then(Value::as_u64));
    let run = long_run(p, &clone, now, waits)?;
    if p.dry {
        return Some(format!(
            "would warn {} of {} (pid {})",
            text(entry, "name"),
            run.command,
            run.pid
        ));
    }
    warn_long(p, entry, regs, &clone, &run, now)
}

/// One pass over every live session; the log lines it wrote.
pub(crate) fn run_pass(p: &Paths, now: f64) -> Vec<String> {
    let _ = std::fs::create_dir_all(&p.state);
    let regs = live_sessions(p);
    let mut said = Vec::new();
    for entry in &regs {
        said.extend(long_run_line(p, entry, &regs, now));
        let Some(stall) = judge(p, entry, now) else {
            continue;
        };
        if p.dry {
            said.push(format!(
                "would mark {} ({}) idle {} min, {} in {}",
                text(entry, "name"),
                text(entry, "sessionId"),
                stall.idle / 60,
                stall.what,
                stall.clone
            ));
            continue;
        }
        said.push(act(p, entry, &regs, &stall, now));
    }
    if !said.is_empty() && !p.dry {
        let log = p.state.join("log");
        let earlier = std::fs::read_to_string(&log).unwrap_or_default();
        let added: String = said.iter().map(|s| s.clone() + "\n").collect();
        let _ = std::fs::write(&log, earlier + &added);
    }
    said
}

/// The time now, for a pass.
pub(crate) fn now() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0.0, |d| d.as_secs_f64())
}

#[cfg(test)]
mod tests;
