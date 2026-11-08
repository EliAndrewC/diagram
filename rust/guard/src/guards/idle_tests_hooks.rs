//! `idle-tests-hooks` (feature 136; ported from `scripts/hooks/idle-tests-hooks.sh`, feature 449 T014): AN IDLE SESSION RUNS THE
//! EXPENSIVE TESTS IN THE BACKGROUND. A Stop arms a detached timer; a prompt disarms it, aborts a run in progress (D9) and says the
//! last verdict once. The timer waits 60 to 120 minutes of AWAKE time, staggered by the session's name so a laptop's resume does not
//! start every session at once (the GM, 2026-08-27), a wall-clock jump restarting the wait; then the host-wide lock, never while a
//! make runs in the clone, then `make idle-tests`, its verdict in `dev/idle-log/`. Only a Stop arms, so one idle is at most one run,
//! and a clone unchanged since its last green run is recorded as skipped (D10).
//!
//! Plan T014's decisions: (a) every mode ported, the timer the binary's `--idle-tests timer`; (b) git, `setsid`, `nohup`, `kill`,
//! `pgrep`, `flock` and the run stay theirs, asked by path; (c) the shell's Python and `cksum` are in-process; (d) the suite's
//! `stagger` reaches [`cli`], and its read of the shipped default reads [`DEF_ARM`].

use std::fs::File;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::LazyLock;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use fancy_regex::Regex;
use serde_json::{json, Value};

use crate::protocol::{Answer, Event, Guard, Reply};
use crate::shared::log::civil;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "idle-tests-hooks",
    events: &["Stop", "UserPromptSubmit"],
    matcher: "*",
    decide,
};

/// DISABLED BY THE GM, 2026-09-06 ("disable idle-tests but do not eliminate it"): a Stop arms nothing, so no timer starts and no
/// unattended gate runs. `make idle-tests` still works by hand, and a prompt still disarms a timer armed before the switch. Re-enable
/// by setting this to true; a fixture arms by default, so every case still tests the machinery.
pub const DEF_ARM: bool = false;

static FAILED: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^\s*FAIL\S*\s+(\S+)").unwrap_or_else(|e| unreachable!("{e}")));
static TRIPWIRE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"tripwire seed\s+(\d+): (?!ok|expected)(.+)")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// The configuration (D2, D4), and the seams, which are honored only in a fixture outside this repository's own tree.
#[derive(Debug, Clone)]
pub(crate) struct Config {
    pub tick: f64,
    pub wait_min: u64,
    pub wait_span: u64,
    pub suspend_s: i64,
    pub defer_min: u64,
    pub defer_span: u64,
    pub give_up_s: i64,
    pub clock: String,
    pub run: String,
    pub home: PathBuf,
    pub sessions: PathBuf,
    pub wait_s: Option<u64>,
    pub defer_s: Option<u64>,
    pub busy: String,
    pub arm: bool,
    pub warning: Option<String>,
    /// `IDLE_ROOT`, the arming's handoff to its timer.
    pub root: Option<String>,
    /// How long an aborted run gets between TERM and KILL.
    pub grace: Duration,
    /// What the armed timer runs as (the binary; a test's stand-in).
    pub exe: PathBuf,
}

impl Config {
    /// The configuration from `vars`, this repository being `own_root` and the working directory `pwd`.
    pub(crate) fn from_vars(vars: &[(String, String)], own_root: &Path, pwd: &str) -> Self {
        let get = |k: &str| {
            vars.iter()
                .find(|(n, v)| n == k && !v.is_empty())
                .map(|(_, v)| v.clone())
        };
        let root = get("IDLE_ROOT").unwrap_or_else(|| pwd.to_owned());
        let seams =
            get("IDLE_FIXTURE").as_deref() == Some("1") && !Path::new(&root).starts_with(own_root);
        let seam = |k: &str| get(k).filter(|_| seams);
        let num = |k: &str, d: u64| seam(k).and_then(|v| v.parse().ok()).unwrap_or(d);
        let signed = |k: &str, d: i64| seam(k).and_then(|v| v.parse().ok()).unwrap_or(d);
        let home = get("HOME").unwrap_or_else(|| "/home/agent".to_owned());
        let stray = vars
            .iter()
            .any(|(n, _)| is_seam_name(n) && n != "IDLE_ROOT");
        Self {
            tick: seam("IDLE_TICK").and_then(|v| v.parse().ok()).unwrap_or(60.0),
            wait_min: num("IDLE_WAIT_MIN", 60),
            wait_span: num("IDLE_WAIT_SPAN", 60),
            suspend_s: signed("IDLE_SUSPEND_S", 300),
            defer_min: num("IDLE_DEFER_MIN", 5),
            defer_span: num("IDLE_DEFER_SPAN", 10),
            give_up_s: signed("IDLE_GIVE_UP_S", 21_600),
            clock: seam("IDLE_CLOCK").unwrap_or_default(),
            run: seam("IDLE_RUN").unwrap_or_default(),
            home: seam("IDLE_HOME").map_or_else(|| Path::new(&home).join(".claude"), PathBuf::from),
            sessions: seam("IDLE_SESSIONS_DIR").map_or_else(|| Path::new(&home).join(".claude/sessions"), PathBuf::from),
            wait_s: seam("IDLE_WAIT_S").and_then(|v| v.parse().ok()),
            defer_s: seam("IDLE_DEFER_S").and_then(|v| v.parse().ok()),
            busy: seam("IDLE_BUSY_CMD").unwrap_or_default(),
            arm: if seams { get("IDLE_ARM").is_none_or(|v| v == "1") } else { DEF_ARM },
            warning: (!seams && stray).then(|| {
                format!(
                    "idle-tests: IDLE_* seams are honored only inside a fixture (IDLE_FIXTURE=1, outside {}) - ignored",
                    own_root.display()
                )
            }),
            root: get("IDLE_ROOT"),
            grace: Duration::from_millis(200),
            exe: std::env::current_exe().unwrap_or_default(),
        }
    }

    fn read() -> Self {
        let vars: Vec<(String, String)> = std::env::vars_os()
            .map(|(k, v)| {
                (
                    k.to_string_lossy().into_owned(),
                    v.to_string_lossy().into_owned(),
                )
            })
            .collect();
        let pwd = std::env::current_dir().unwrap_or_default();
        let own = std::env::var("L7R_GUARD_TREE").map_or_else(|_| pwd.clone(), PathBuf::from);
        Self::from_vars(&vars, &own, &pwd.to_string_lossy())
    }

    fn now(&self) -> i64 {
        if self.clock.is_empty() {
            return now_secs();
        }
        let words: Vec<&str> = self.clock.split_whitespace().collect();
        ask(Path::new("/"), words[0], &words[1..], "")
            .out
            .trim()
            .parse()
            .unwrap_or(0)
    }

    fn stagger(&self, name: &str) -> u64 {
        self.wait_min + u64::from(cksum(name)) % (self.wait_span + 1)
    }

    fn deferral(&self, name: &str) -> u64 {
        self.defer_min + u64::from(cksum(name)) % (self.defer_span + 1)
    }
}

/// `IDLE_` and a capital: a name `grep '^IDLE_[A-Z]'` keeps.
fn is_seam_name(n: &str) -> bool {
    n.strip_prefix("IDLE_")
        .is_some_and(|r| r.starts_with(|c: char| c.is_ascii_uppercase()))
}

fn now_secs() -> i64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0, |d| i64::try_from(d.as_secs()).unwrap_or(0))
}

/// `date -u +%Y%m%dT%H%M%SZ`.
fn utc() -> String {
    let (y, mo, d, h, mi, s) = civil(u64::try_from(now_secs()).unwrap_or(0));
    format!("{y:04}{mo:02}{d:02}T{h:02}{mi:02}{s:02}Z")
}

/// POSIX `cksum` of the text: the CRC of its bytes then its length's, inverted - the value the shell's stagger hashed, so every
/// session keeps the stagger it had.
pub(crate) fn cksum(text: &str) -> u32 {
    let step = |crc: u32, byte: u8| {
        (0..8).fold(crc ^ (u32::from(byte) << 24), |c, _| {
            if c & 0x8000_0000 == 0 {
                c << 1
            } else {
                (c << 1) ^ 0x04C1_1DB7
            }
        })
    };
    let body = text.bytes().fold(0, step);
    let (mut crc, mut n) = (body, text.len());
    while n > 0 {
        crc = step(crc, u8::try_from(n & 0xff).unwrap_or(0));
        n >>= 8;
    }
    !crc
}

/// A field of a JSON state file as the shell's `state_of` printed it: nothing for a missing or null one, and a 0 reads as 0.
fn state_of(path: &Path, key: &str) -> String {
    let doc: Option<Value> = std::fs::read_to_string(path)
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok());
    match doc.as_ref().and_then(|d| d.get(key)) {
        None | Some(Value::Null) => String::new(),
        Some(Value::String(s)) => s.clone(),
        Some(v) => v.to_string(),
    }
}

/// The session clone a directory stands in - its git root, inside `<main>/.clones/` - and that clone's name (`locate`).
fn locate(cwd: &str) -> Option<(PathBuf, String)> {
    if !Path::new(cwd).is_dir() {
        return None;
    }
    let top = Path::new(cwd)
        .ancestors()
        .find(|d| d.join(".git").exists())?;
    if !top.to_string_lossy().contains("/.clones/") {
        return None;
    }
    let name = top.file_name()?.to_string_lossy().into_owned();
    Some((top.to_path_buf(), name))
}

/// The seams' warning, as the shell said it on stderr.
fn warn(c: &Config) {
    c.warning.iter().for_each(|w| eprintln!("{w}"));
}

fn decide(event: &Event, _session: &Session) -> Vec<Answer> {
    judge(
        event,
        &Config::read(),
        &std::env::current_dir()
            .unwrap_or_default()
            .to_string_lossy(),
    )
}

pub(crate) fn judge(event: &Event, c: &Config, pwd: &str) -> Vec<Answer> {
    warn(c);
    if event.name == "Stop" && !c.arm {
        return Vec::new(); // the GM's disable, before any look at the tree: a Stop hook runs on every turn end
    }
    let cwd = Some(field(&event.input, "cwd"))
        .filter(|s| !s.is_empty())
        .unwrap_or(pwd);
    let Some((clone, session)) = locate(cwd) else {
        return Vec::new(); // main, or no git: nothing to arm
    };
    if event.name == "Stop" {
        arm(c, &clone, &session, field(&event.input, "session_id"));
        return Vec::new();
    }
    prompt(c, &clone, &session)
        .map(Answer::Print)
        .into_iter()
        .collect()
}

fn write_json(path: &Path, v: &Value) {
    let _ = std::fs::write(path, serde_json::to_string_pretty(v).unwrap_or_default());
}

/// ARM: the state file and a detached timer; a no-op while one is armed and alive.
fn arm(c: &Config, clone: &Path, session: &str, sid: &str) {
    let sf = clone.join(".git/idle-tests.json");
    if sf.is_file() {
        let pid = state_of(&sf, "timer_pid");
        if !pid.is_empty() && Path::new(&format!("/proc/{pid}")).is_dir() {
            return;
        }
    }
    let mut state = json!({
        "session": session, "session_id": sid, "armed_at": c.now(), "wait_min": c.stagger(session), "timer_pid": null
    });
    write_json(&sf, &state);
    let Ok(log) = File::create(clone.join(".git/idle-tests.log")) else {
        return;
    };
    let root = c
        .root
        .clone()
        .unwrap_or(clone.to_string_lossy().into_owned());
    let spawned = Command::new("setsid")
        .arg("nohup")
        .arg(&c.exe)
        .args(["--idle-tests", "timer"])
        .arg(clone)
        .args([session, sid])
        .env("IDLE_ROOT", root)
        .current_dir(clone)
        .stdin(Stdio::null())
        .stdout(log.try_clone().map_or(Stdio::null(), Stdio::from))
        .stderr(log)
        .spawn();
    state["timer_pid"] = spawned.map_or(Value::Null, |child| json!(child.id()));
    write_json(&sf, &state);
}

/// The newest record of this session, as `ls -t ... | head -1` names it.
fn latest_record(clone: &Path, session: &str) -> Option<PathBuf> {
    let suffix = format!("-{session}.json");
    std::fs::read_dir(clone.join("dev/idle-log"))
        .ok()?
        .filter_map(Result::ok)
        .map(|e| e.path())
        .filter(|p| {
            p.file_name()
                .is_some_and(|n| n.to_string_lossy().ends_with(&suffix))
        })
        .max_by_key(|p| {
            let at = std::fs::metadata(p)
                .and_then(|m| m.modified())
                .unwrap_or(UNIX_EPOCH);
            (at, std::cmp::Reverse(p.clone()))
        })
}

/// DISARM: the state gone (the timer sees that and exits), a run in progress aborted (D9), and the last verdict said once.
fn prompt(c: &Config, clone: &Path, session: &str) -> Option<String> {
    let sf = clone.join(".git/idle-tests.json");
    if sf.is_file() {
        let pid = state_of(&sf, "timer_pid");
        let _ = std::fs::remove_file(&sf);
        let running = clone.join(".git/idle-tests.running");
        if running.is_file() {
            abort(c, clone, session, &pid, &running);
        } else if !pid.is_empty() && Path::new(&format!("/proc/{pid}")).is_dir() {
            let _ = ask(Path::new("/"), "kill", &[&pid], "");
        }
    }
    let latest = latest_record(clone, session)?;
    let seen = clone.join(".git/idle-tests.seen");
    let named = latest.to_string_lossy().into_owned();
    if std::fs::read_to_string(&seen).is_ok_and(|s| s.trim_end_matches('\n') == named) {
        return None;
    }
    let _ = std::fs::write(&seen, format!("{named}\n"));
    verdict(&latest)
}

/// A run in progress is ABORTED (D9): nothing of the session's ever waits on it.
fn abort(c: &Config, clone: &Path, session: &str, pid: &str, running: &Path) {
    let group = format!("-{pid}");
    let _ = ask(Path::new("/"), "kill", &["-TERM", "--", &group], "");
    let _ = ask(Path::new("/"), "kill", &["-TERM", pid], "");
    std::thread::sleep(c.grace);
    let _ = ask(Path::new("/"), "kill", &["-KILL", "--", &group], "");
    let _ = std::fs::remove_file(running);
    let at = utc();
    let dir = clone.join("dev/idle-log");
    let _ = std::fs::create_dir_all(&dir);
    write_json(
        &dir.join(format!("{at}-{session}.json")),
        &json!({
            "utc": at, "session": session, "commit": short_head(clone), "target": "make idle-tests", "rc": -1,
            "aborted": "on-prompt", "wall_s": 0, "suspends": 0, "deferrals": 0, "failures": [], "log": ""
        }),
    );
}

fn short_head(clone: &Path) -> String {
    let d = clone.to_string_lossy();
    ask(
        Path::new("/"),
        "git",
        &["-C", &d, "rev-parse", "--short", "HEAD"],
        "",
    )
    .out
}

/// A record's one line, the shell's words.
fn verdict(rec: &Path) -> Option<String> {
    let d: Value = serde_json::from_str(&std::fs::read_to_string(rec).ok()?).ok()?;
    let s = |k: &str| {
        d.get(k).map_or_else(
            || "None".to_owned(),
            |v| v.as_str().map_or_else(|| v.to_string(), str::to_owned),
        )
    };
    let truthy = |k: &str| {
        d.get(k)
            .is_some_and(|v| !v.is_null() && v.as_str() != Some("") && v != &json!(0))
    };
    let tail = if truthy("aborted") {
        "aborted on your prompt (D9) - nothing waited on it".to_owned()
    } else if truthy("skipped") {
        format!("skipped - {} (D10)", s("skipped"))
    } else if d.get("rc") == Some(&json!(0)) {
        "clean".to_owned()
    } else {
        let names: Vec<&str> = d
            .get("failures")
            .and_then(Value::as_array)
            .map(|a| a.iter().filter_map(Value::as_str).collect())
            .unwrap_or_default();
        let joined: String = names.join(", ").chars().take(200).collect();
        let shown = if joined.is_empty() {
            format!("see {}", d.get("log").and_then(Value::as_str).unwrap_or(""))
        } else {
            joined
        };
        format!("FAILED (rc {}): {shown}", s("rc"))
    };
    Some(format!(
        "idle-tests: ran {} in {}s on {} ({}; suspends {}, deferrals {}): {tail}",
        s("utc"),
        s("wall_s"),
        s("commit"),
        s("target"),
        s("suspends"),
        s("deferrals")
    ))
}

/// A live process backs this session id (the sessions-json FILE NAME is its pid); no id known counts as live.
fn sid_is_live(sid: &str, sessions: &Path) -> bool {
    if sid.is_empty() {
        return true;
    }
    let Ok(entries) = std::fs::read_dir(sessions) else {
        return false;
    };
    let mut files: Vec<PathBuf> = entries
        .filter_map(Result::ok)
        .map(|e| e.path())
        .filter(|p| p.extension().is_some_and(|x| x == "json"))
        .collect();
    files.sort();
    let named = files.iter().find(|p| {
        let doc: Option<Value> = std::fs::read_to_string(p)
            .ok()
            .and_then(|t| serde_json::from_str(&t).ok());
        doc.is_some_and(|d| {
            ["sessionId", "session_id"]
                .iter()
                .any(|k| d.get(k).and_then(Value::as_str) == Some(sid))
        })
    });
    named.and_then(|p| p.file_name()).is_some_and(|n| {
        let pid = n.to_string_lossy();
        Path::new("/proc")
            .join(pid.split('.').next().unwrap_or(""))
            .is_dir()
    })
}

/// Whether one of these make processes (`pgrep`'s output) has its cwd inside the clone.
fn make_in(pids: &str, clone: &Path) -> bool {
    pids.split_whitespace()
        .any(|p| std::fs::read_link(format!("/proc/{p}/cwd")).is_ok_and(|c| c.starts_with(clone)))
}

/// One armed wait: what it reads, and the two counts its record keeps.
struct Timer<'a> {
    c: &'a Config,
    clone: &'a Path,
    session: &'a str,
    sid: &'a str,
    sf: PathBuf,
    armed: String,
    suspends: u64,
    deferrals: u64,
}

impl Timer<'_> {
    /// The arming still stands, the session still exists, the arming has not lapsed.
    fn alive(&self) -> bool {
        self.sf.is_file()
            && state_of(&self.sf, "armed_at") == self.armed
            && sid_is_live(self.sid, &self.c.sessions)
            && self.c.now() - self.armed.parse::<i64>().unwrap_or(0) < self.c.give_up_s
    }

    /// Wait `secs` of AWAKE time; a wall jump past the ticks restarts the count (D2, D3). False: the arming is gone.
    fn wait_awake(&mut self, secs: u64) -> bool {
        self.wait_ms(i64::try_from(secs).unwrap_or(i64::MAX / 1000) * 1000)
    }

    fn wait_ms(&mut self, need: i64) -> bool {
        let tick_ms = i64::try_from(Duration::from_secs_f64(self.c.tick).as_millis())
            .unwrap_or(1)
            .max(1);
        let (mut awake, mut last) = (0, self.c.now());
        while awake < need {
            std::thread::sleep(Duration::from_secs_f64(self.c.tick));
            if !self.alive() {
                return false;
            }
            let t = self.c.now();
            let drift = (t - last) * 1000 - tick_ms;
            last = t;
            if drift > self.c.suspend_s * 1000 {
                awake = 0;
                self.suspends += 1;
                println!(
                    "suspend detected (wall jumped {}s past the ticks): the wait restarts",
                    drift / 1000
                );
                continue;
            }
            awake += tick_ms;
        }
        true
    }

    fn busy(&self) -> bool {
        if self.c.busy.is_empty() {
            return make_in(
                &ask(Path::new("/"), "pgrep", &["-x", "make"], "").out,
                self.clone,
            );
        }
        let mut words: Vec<&str> = self.c.busy.split_whitespace().collect();
        let program = words.remove(0);
        let c = self.clone.to_string_lossy();
        words.push(&c);
        ask(Path::new("/"), program, &words, "").ok()
    }

    /// The lock taken, or None when the arming went while waiting for it: one runner at a time, never beside a make in the clone.
    fn hold(&mut self, lock: &File, defer: u64) -> Option<()> {
        loop {
            if !flock(lock, "-n") {
                self.deferrals += 1;
                println!("another session's idle run holds the lock: deferring {defer}s");
            } else if self.busy() {
                self.deferrals += 1;
                println!("a make is running in this clone: deferring {defer}s");
                let _ = flock(lock, "-u");
            } else {
                return Some(());
            }
            if !self.wait_awake(defer) {
                return None;
            }
        }
    }

    /// A clone unchanged since its last GREEN run is recorded as skipped (D10, the GM 2026-08-28: "once we've gotten a single set of
    /// results, then our expectation is that that is good enough"). True when it was.
    fn skipped(&self, at: &str, commit: &str, target: &str) -> bool {
        let Some(last) = latest_record(self.clone, self.session) else {
            return false;
        };
        let d = self.clone.to_string_lossy();
        if state_of(&last, "rc") != "0"
            || state_of(&last, "commit") != commit
            || !ask(
                Path::new("/"),
                "git",
                &["-C", &d, "status", "--porcelain", "--untracked-files=no"],
                "",
            )
            .out
            .is_empty()
        {
            return false;
        }
        let name = last
            .file_name()
            .map(|n| n.to_string_lossy().into_owned())
            .unwrap_or_default();
        let dir = self.clone.join("dev/idle-log");
        let _ = std::fs::create_dir_all(&dir);
        write_json(
            &dir.join(format!("{at}-{}.json", self.session)),
            &json!({
                "utc": at, "session": self.session, "commit": commit, "target": target, "rc": 0,
                "skipped": format!("unchanged since the green run {name}"), "wall_s": 0, "suspends": 0, "deferrals": 0, "failures": [], "log": ""
            }),
        );
        let _ = std::fs::remove_file(&self.sf);
        println!("idle-tests: skipped - unchanged since the green run {name}");
        true
    }

    fn run(&self, at: &str, commit: &str, target: &str) {
        let log = self.clone.join(".git/idle-tests.run.log");
        let running = self.clone.join(".git/idle-tests.running");
        let _ = std::fs::write(&running, format!("{}\n", std::process::id()));
        let t0 = self.c.now();
        let rc = launch(target, self.clone, &log);
        let wall = self.c.now() - t0;
        let _ = std::fs::remove_file(&running);
        let dir = self.clone.join("dev/idle-log");
        let _ = std::fs::create_dir_all(&dir);
        let rec = dir.join(format!("{at}-{}.json", self.session));
        write_json(
            &rec,
            &json!({
                "utc": at, "session": self.session, "commit": commit, "target": target, "rc": rc, "wall_s": wall,
                "suspends": self.suspends, "deferrals": self.deferrals, "failures": failures(&log), "log": log.to_string_lossy()
            }),
        );
        let _ = std::fs::remove_file(&self.sf); // the arming is consumed: only a Stop arms again (D6)
        println!("idle-tests: recorded {} (rc {rc})", rec.display());
    }
}

/// `flock <mode> 0` on the lock's open file, handed over as stdin: the lock belongs to that open file, which the timer holds, as the
/// shell's fd 9 did (`File::try_lock` is past this toolchain, T014 decision (b)).
fn flock(lock: &File, mode: &str) -> bool {
    lock.try_clone().is_ok_and(|f| {
        Command::new("flock")
            .args([mode, "0"])
            .stdin(f)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status()
            .is_ok_and(|s| s.success())
    })
}

/// Run `target`, its words split as the shell split them, in the clone, its output in `log`: its exit code, 127 when it cannot start.
fn launch(target: &str, clone: &Path, log: &Path) -> i32 {
    let words: Vec<&str> = target.split_whitespace().collect();
    let Ok(out) = File::create(log) else {
        return 127;
    };
    let status = Command::new(words[0])
        .args(&words[1..])
        .current_dir(clone)
        .stdout(out.try_clone().map_or(Stdio::null(), Stdio::from))
        .stderr(out)
        .status();
    status.map_or(127, |s| s.code().unwrap_or(-1))
}

/// The failures a run's log names.
fn failures(log: &Path) -> Vec<String> {
    let bytes = std::fs::read(log).unwrap_or_default();
    let text = String::from_utf8_lossy(&bytes);
    let mut out: Vec<String> = Vec::new();
    for line in text.lines() {
        if let Ok(Some(m)) = FAILED.captures(line) {
            let name = m[1].to_owned();
            if !out.contains(&name) {
                out.push(name);
            }
        }
        if let Ok(Some(m)) = TRIPWIRE.captures(line) {
            let why: String = m[2].trim().chars().take(80).collect();
            out.push(format!("seed{}: {why}", &m[1]));
        }
    }
    out
}

/// The detached wait: the stagger, the lock, then the run and its record.
pub(crate) fn timer(c: &Config, clone: &Path, session: &str, sid: &str) {
    let sf = clone.join(".git/idle-tests.json");
    let armed = state_of(&sf, "armed_at");
    if armed.is_empty() {
        return;
    }
    let mut t = Timer {
        c,
        clone,
        session,
        sid,
        sf,
        armed,
        suspends: 0,
        deferrals: 0,
    };
    let wait = c.wait_s.unwrap_or_else(|| c.stagger(session) * 60);
    let defer = c.defer_s.unwrap_or_else(|| c.deferral(session) * 60);
    if !t.wait_awake(wait) {
        return;
    }
    let _ = std::fs::create_dir_all(&c.home);
    let Ok(lock) = File::create(c.home.join("idle-tests.lock")) else {
        return;
    };
    if t.hold(&lock, defer).is_none() || !t.alive() {
        return;
    }
    let target = if c.run.is_empty() {
        "make idle-tests"
    } else {
        c.run.as_str()
    };
    let (at, commit) = (utc(), short_head(clone));
    if !t.skipped(&at, &commit, target) {
        t.run(&at, &commit, target);
    }
}

/// `--idle-tests stagger <name>` and `--idle-tests timer <clone> <session> [sid]`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let c = Config::read();
    let arg = |i: usize| args.get(i).map_or("", String::as_str);
    match arg(0) {
        "stagger" => {
            warn(&c);
            Reply {
                stdout: format!("{}\n", c.stagger(arg(1))),
                stderr: String::new(),
                code: 0,
            }
        }
        "timer" => {
            timer(&c, Path::new(arg(1)), arg(2), arg(3));
            Reply {
                stdout: String::new(),
                stderr: String::new(),
                code: 0,
            }
        }
        _ => Reply {
            stdout: String::new(),
            stderr:
                "usage: l7r-guard --idle-tests stagger <session> | timer <clone> <session> [sid]"
                    .to_owned(),
            code: 1,
        },
    }
}

#[cfg(test)]
mod tests;
