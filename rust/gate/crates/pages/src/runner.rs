//! The detached runner behind `page-session.sh` (feature 250 D7): each brief in a fresh headless session, in order. Ported whole from
//! `scripts/pages/page_session_runner.py` by feature 449 T137 (`ask:449-phase3-remainder`); `page-session.sh` execs it through the gate's
//! wrapper, and the brief count ([`crate::brief_load`]), the escape ([`crate::escape_log`]) and the ledger rows (`reviews ledger-owed`)
//! are asked in process where the Python imported two modules and ran one command.
//!
//! ```text
//! l7r-gate page-session <root> <name> <projects dir> [claude args ...] -- <brief | then:<script> | resume:<sid>:<brief>> ...
//! ```
//!
//! Prints every known session's id, transcript and log directory at once, then starts ONE detached process (this binary again,
//! `page-session --work ...`, in a session of its own) that works the queue in order: a brief runs as a fresh session; a `then:<script>`
//! runs the script when it is reached and queues the briefs it prints, one path a line - which is how a page's check sessions are planned
//! from the handoff its write session leaves (feature 250 R3, recommendation 2). Every session started is appended to
//! `<root>/.git/page-sessions/index.txt` as `<session id> <brief>`, so the meter can find the ones planned late. The stall watchdog knows
//! a running queue by that argv (`stall_watchdog_hooks/pass.rs`).
//!
//! THE FLOOR (feature 250 R3, recommendation 1). A page session is launched with only the tools research uses, no MCP servers, no skill
//! listing, and - in a clone - without the MIRROR's root CLAUDE.md, which sits above every clone and otherwise loads beside the clone's
//! own copy. Measured on a probe, 2026-09-26: the first turn of a page session fell from 40,280 tokens to 21,267; every turn carries that
//! floor. Feature 274 (D6) lowers it again: the clone's OWN root CLAUDE.md is excluded too (about 5,200 tokens a turn, most of it
//! spec-kit, the gate and the guard table, which a research session never uses), and `scripts/container/page-session-rules.md` - the
//! rules a research session acts on - is appended after the standing authorizations in one `--append-system-prompt`.
//!
//! THE WRITE CAP (feature 274 D2, D3; research R1: a write session's cost follows its turn count, r = 0.92, and grows roughly with the
//! square of its length). Every brief is counted before its session starts - the ones listed at launch before anything detaches (a
//! refusal exits 2), the ones a `then:` step prints when it runs (a refusal writes `STOPPED <brief>: <reason>` and ends the queue, never
//! a silent skip). `WRITE_CAP_OK='<reason>'` lets a brief through, logged. A write session (a brief declaring no exempt kind, or
//! `assertions`) is told `L7R_KEY_CAP`, which `make reserve` enforces; every session is told its id (`L7R_PAGE_SESSION`) and where to
//! leave a continuation (`L7R_CONTINUE`), and a brief left there is queued next - before the group's `then:` checks step, so the checks
//! see both sessions' handoff.

pub mod retry;
pub mod watch;
pub mod work;

use std::fmt::Write as _;
use std::io::Read as _;
use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use crate::{
    basename, brief_load, escape_log, py_join, py_path, raised, read_lossy, realpath, reply,
};
use l7r_gate_core::Reply;

const PROMPT: &str = "You are a fresh session started to do the work ONE brief describes. Read {brief} first, and do what it says, end to end and unattended. Commit in this clone as you finish each part; never run the stop-work push. When the brief's work is done, or it tells you to stop, write the one-paragraph summary it asks for and stop.";
const TOOLS: &str = "Bash,Read,Edit,Write,Grep,Glob,Agent,WebFetch,WebSearch";
/// New registry keys a write session may reserve (feature 274 FR-001; `reserve-prefix.py` enforces it).
pub const KEY_CAP: u32 = 10;
const PROMPT_FILES: [&str; 2] = [
    "scripts/container/append-system-prompt.md",
    "scripts/container/page-session-rules.md",
];
/// The wait the launch prints, with its escape as an invocation: the no-poll guard refused this wait without it (feature 412,
/// 2026-10-24). `{run_log}` is the run log's path; `tests/hooks/test-no-poll-hooks.sh` reads this line from here and fills it.
pub const WAIT: &str = "    POLL_OK='a detached page-session queue the harness cannot track'; until grep -q '^ALL DONE' {run_log}; do sleep 60; done; tail -20 {run_log}";

/// Why the runner stopped: a brief the write cap does not admit (exit 2 at launch, `STOPPED` in a queue), or what the Python raised.
#[derive(Debug, PartialEq, Eq)]
pub enum Stop {
    Refused(String),
    Raised(String),
}

/// What a launch and its queue read of the process, handed in so a test runs in a scratch tree.
pub struct Ctx<'a> {
    pub root: String,
    pub name: String,
    pub extra: Vec<String>,
    /// The working directory a relative brief is read from.
    pub cwd: String,
    /// The escape's reading of the process (its `WRITE_CAP_OK`, the guard log).
    pub escape: &'a escape_log::Env<'a>,
}

/// A new random (version 4) UUID, as `uuid.uuid4()` writes one.
#[must_use]
pub fn uuid4() -> String {
    let mut b = [0u8; 16];
    let _ = std::fs::File::open("/dev/urandom").and_then(|mut f| f.read_exact(&mut b));
    b[6] = (b[6] & 0x0f) | 0x40;
    b[8] = (b[8] & 0x3f) | 0x80;
    let hex = b.iter().fold(String::new(), |mut s, x| {
        let _ = write!(s, "{x:02x}");
        s
    });
    format!(
        "{}-{}-{}-{}-{}",
        &hex[..8],
        &hex[8..12],
        &hex[12..16],
        &hex[16..20],
        &hex[20..]
    )
}

/// The launch flags that lower a page session's fixed floor, and the reason for each in the module's words above.
#[must_use]
pub fn floor_flags(root: &str) -> Vec<String> {
    let mut flags: Vec<String> = [
        "--disable-slash-commands",
        "--strict-mcp-config",
        "--tools",
        TOOLS,
    ]
    .map(str::to_owned)
    .to_vec();
    let root = root.trim_end_matches('/');
    let mut excludes = vec![format!("{root}/CLAUDE.md")];
    let parts: Vec<&str> = root.split('/').collect();
    if let Some(i) = parts.iter().position(|p| *p == ".clones") {
        excludes.insert(0, format!("{}/CLAUDE.md", parts[..i].join("/")));
    }
    flags.push("--settings".to_owned());
    flags.push(l7r_guard::shared::pyjson::dumps(
        &json!({"claudeMdExcludes": excludes}),
        None,
        true,
    ));
    let appended: Vec<String> = PROMPT_FILES
        .iter()
        .map(|f| {
            l7r_guard::shared::py_text::strip(&read_lossy(Path::new(&py_join(root, f)))).to_owned()
        })
        .filter(|t| !t.is_empty())
        .collect();
    if !appended.is_empty() {
        flags.push("--append-system-prompt".to_owned());
        flags.push(appended.join("\n\n"));
    }
    flags
}

/// Whether the brief is a WRITE session's (it declares no exempt kind).
///
/// # Errors
///
/// [`Stop::Refused`] when the cap refuses it and no `WRITE_CAP_OK` with a reason lets it through; [`Stop::Raised`] where the count
/// raised.
pub fn admit(ctx: &Ctx, brief: &str) -> Result<bool, Stop> {
    if !Path::new(brief).is_file() {
        return Err(Stop::Refused(format!("{brief}: no such brief")));
    }
    let text = read_lossy(Path::new(brief));
    let record = py_path(&ctx.root).join("research");
    let why = brief_load::refusal(&py_path(brief), &text, &record).map_err(Stop::Raised)?;
    if !why.is_empty() {
        let context = json!({"brief": brief, "why": why.chars().take(300).collect::<String>()});
        match escape_log::escape(
            "WRITE_CAP_OK",
            "page-session",
            "write-cap",
            Some(&context),
            ctx.escape,
        ) {
            Err(e) => return Err(Stop::Refused(format!("{}: {e}", basename(brief)))),
            Ok(false) => return Err(Stop::Refused(format!("{}: {why}", basename(brief)))),
            Ok(true) => {}
        }
    }
    Ok(brief_load::declared(&text).is_empty())
}

/// The session's command: a fresh `claude -p` on the brief, named, with its id, the floor's flags and the caller's own.
#[must_use]
pub fn command(ctx: &Ctx, brief: &str, sid: &str) -> Vec<String> {
    let prompt = PROMPT.replace("{brief}", &realpath(brief, &ctx.cwd));
    let mut cmd: Vec<String> = [
        "claude",
        "-p",
        &prompt,
        "-n",
        &ctx.name,
        "--session-id",
        sid,
    ]
    .map(str::to_owned)
    .to_vec();
    cmd.extend(["--permission-mode", "bypassPermissions"].map(str::to_owned));
    cmd.extend(floor_flags(&ctx.root));
    cmd.extend(ctx.extra.iter().cloned());
    cmd.extend(["--output-format", "json"].map(str::to_owned));
    cmd
}

/// A fresh session for `brief`: its id, its log directory (made), its command.
///
/// # Errors
///
/// The log directory cannot be made: what `os.makedirs` raised.
pub fn new_item(ctx: &Ctx, brief: &str, write: bool) -> Result<Value, Stop> {
    let sid = uuid4();
    let log = py_join(&py_join(&py_join(&ctx.root, ".git"), "page-sessions"), &sid);
    std::fs::create_dir_all(&log).map_err(|e| Stop::Raised(format!("{log}: {e}")))?;
    Ok(
        json!({"sid": sid, "log": log, "brief": brief, "cmd": command(ctx, brief, &sid), "write": write}),
    )
}

/// `specs/NNN-slug` for a brief under a feature's directory, else "".
#[must_use]
pub fn brief_feature(brief: &str, cwd: &str) -> String {
    let real = realpath(brief, cwd);
    let parts: Vec<&str> = real.split('/').collect();
    match parts.iter().rposition(|p| *p == "specs") {
        Some(i) if i + 2 < parts.len() => format!("specs/{}", parts[i + 1]),
        _ => String::new(),
    }
}

/// The queue: `{"sid", "log", "brief", "cmd", "write"}` per brief (its log directory made), `{"then": script}` per late step, and what
/// the launch prints of each. Every new brief is admitted first, so a refusal leaves nothing made. A `resume:` is a session already
/// started, so it is not counted again.
///
/// # Errors
///
/// A refusal, or what the Python raised, with what had been printed before it.
pub fn plan(
    ctx: &Ctx,
    projects: &str,
    items: &[String],
    out: &mut String,
) -> Result<Vec<Value>, Stop> {
    let mut writes: Vec<(&str, bool)> = Vec::new();
    for item in items
        .iter()
        .filter(|i| !i.starts_with("then:") && !i.starts_with("resume:"))
    {
        let write = admit(ctx, item)?;
        writes.retain(|(b, _)| b != item);
        writes.push((item, write));
    }
    let mut queue = Vec::new();
    for item in items {
        if let Some(rest) = item.strip_prefix("resume:") {
            // `resume:<sid>:<brief>` - a session whose runner died with it (feature 271, 2026-09-27: the dispatching session's process
            // ended and took five queues' runners with it, each mid-way through a write session with its work uncommitted). The same
            // session is resumed with its own context, never started over.
            let (sid, brief) = rest.split_once(':').ok_or_else(|| {
                Stop::Raised(
                    "ValueError: not enough values to unpack (expected 2, got 1)".to_owned(),
                )
            })?;
            let log = py_join(&py_join(&py_join(&ctx.root, ".git"), "page-sessions"), sid);
            std::fs::create_dir_all(&log).map_err(|e| Stop::Raised(format!("{log}: {e}")))?;
            let write = brief_load::declared(&read_lossy(Path::new(brief))).is_empty();
            let returned = watch::returned_file(&log, &watch::undelivered(projects, sid))
                .map_err(Stop::Raised)?;
            let cmd = retry::resume_command(&command(ctx, brief, sid), sid, returned.as_deref());
            queue.push(json!({"sid": sid, "log": log, "brief": brief, "cmd": cmd, "write": write}));
            let _ = writeln!(out, "page-session: resume {sid} ({})", basename(brief));
            continue;
        }
        if let Some(script) = item.strip_prefix("then:") {
            queue.push(json!({"then": realpath(script, &ctx.cwd)}));
            let _ = writeln!(
                out,
                "page-session: then {} - the sessions it plans are listed in .git/page-sessions/index.txt",
                basename(script)
            );
            continue;
        }
        let write = writes
            .iter()
            .find(|(b, _)| b == item)
            .is_some_and(|(_, w)| *w);
        let made = new_item(ctx, item, write)?;
        let (sid, log) = (
            made["sid"].as_str().unwrap_or(""),
            made["log"].as_str().unwrap_or(""),
        );
        let _ = writeln!(
            out,
            "page-session: {}\n  session:    {sid}\n  transcript: {projects}/{sid}.jsonl\n  log:        {log}",
            basename(item)
        );
        queue.push(made);
    }
    Ok(queue)
}

/// Every descriptor past the standard three marked close-on-exec, so the detached queue holds none of the caller's (the Python's
/// `close_fds=True`): a caller reading the launch through a pipe would otherwise wait for the QUEUE to end - measured on the first run
/// (feature 250 T18), which held its `make` for the whole session.
fn close_inherited() {
    extern "C" {
        fn fcntl(fd: i32, cmd: i32, arg: i32) -> i32;
    }
    let fds: Vec<i32> = std::fs::read_dir("/proc/self/fd")
        .map(|d| {
            d.filter_map(Result::ok)
                .filter_map(|e| e.file_name().to_str()?.parse().ok())
                .collect()
        })
        .unwrap_or_default();
    for fd in fds.into_iter().filter(|fd| *fd > 2) {
        // SAFETY: F_SETFD (2) sets only the descriptor's close-on-exec flag (FD_CLOEXEC, 1); a descriptor gone already is an EBADF
        unsafe {
            fcntl(fd, 2, 1);
        }
    }
}

/// The queue's process started detached: `exe page-session --work <root> <name> <extra> <queue> <run log>` in a session of its own
/// (`launcher`, `setsid`: the Python's `start_new_session`), its standard streams `/dev/null`, holding no descriptor of the caller's.
///
/// # Errors
///
/// What the spawn raised.
pub fn detach(launcher: &str, exe: &Path, root: &str, args: &[String]) -> Result<(), String> {
    close_inherited();
    std::process::Command::new(launcher)
        .arg(exe)
        .args(["page-session", "--work"])
        .args(args)
        .current_dir(root)
        .stdin(std::process::Stdio::null())
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .spawn()
        .map(|_| ())
        .map_err(|e| format!("{launcher}: {e}"))
}

/// The launch: the queue planned (its refusal exit 2, nothing started), the run log made, the queue detached, and the wait printed.
fn launch(args: &[String], exe: &Path, escape: &escape_log::Env, launcher: &str) -> Reply {
    let mut out = String::new();
    let (Some(root), Some(name), Some(projects)) = (args.first(), args.get(1), args.get(2)) else {
        return raised(
            "page-session",
            out,
            "ValueError: not enough values to unpack (expected at least 3)",
        );
    };
    let rest = &args[3..];
    let Some(cut) = rest.iter().position(|a| a == "--") else {
        return raised("page-session", out, "ValueError: '--' is not in list");
    };
    let ctx = Ctx {
        root: root.clone(),
        name: name.clone(),
        extra: rest[..cut].to_vec(),
        cwd: crate::cwd(),
        escape,
    };
    let queue = match plan(&ctx, projects, &rest[cut + 1..], &mut out) {
        Ok(q) => q,
        Err(Stop::Refused(why)) => {
            return reply(
                out,
                format!("page-session: REFUSED, nothing started - {why}\n"),
                2,
            )
        }
        Err(Stop::Raised(why)) => return raised("page-session", out, &why),
    };
    let hex: String = uuid4().chars().filter(|c| *c != '-').take(8).collect();
    let run_log = py_join(
        &py_join(&py_join(root, ".git"), "page-sessions"),
        &format!("run-{hex}.log"),
    );
    // it exists before the wait starts, so the wait never races its creation
    if let Err(e) = std::fs::File::create(&run_log) {
        return raised("page-session", out, &format!("{run_log}: {e}"));
    }
    let dumps = |v: &Value| l7r_guard::shared::pyjson::dumps(v, None, true);
    let work = [
        root.clone(),
        name.clone(),
        dumps(&json!(ctx.extra)),
        dumps(&Value::Array(queue)),
        run_log.clone(),
    ];
    if let Err(why) = detach(launcher, exe, root, &work) {
        return raised("page-session", out, &why);
    }
    out += "page-session: started - each result.json is written when its session ends, and the next session begins\n";
    let _ = writeln!(
        out,
        "page-session: to be told when the whole queue has ended, run this BACKGROUNDED (run_in_background):\n{}",
        WAIT.replace("{run_log}", &run_log)
    );
    reply(out, String::new(), 0)
}

/// `l7r-gate page-session ...`: the launch, or with `--work` the detached queue itself (`exe` is this binary, which the launch starts
/// again).
#[must_use]
pub fn cli(
    args: &[String],
    exe: &Path,
    escape: &escape_log::Env,
    environ: Vec<(String, String)>,
) -> Reply {
    if args.first().map(String::as_str) != Some("--work") {
        return launch(args, exe, escape, "setsid");
    }
    let [_, root, name, extra, queue, run_log] = args else {
        return raised(
            "page-session",
            String::new(),
            "ValueError: --work takes <root> <name> <extra> <queue> <run log>",
        );
    };
    let parsed = serde_json::from_str::<Vec<String>>(extra)
        .and_then(|e| Ok((e, serde_json::from_str::<Vec<Value>>(queue)?)))
        .map_err(|e| format!("json.decoder.JSONDecodeError: {e}"));
    let (extra, queue) = match parsed {
        Ok(got) => got,
        Err(why) => return raised("page-session", String::new(), &why),
    };
    let ctx = Ctx {
        root: root.clone(),
        name: name.clone(),
        extra,
        cwd: crate::cwd(),
        escape,
    };
    let run = work::Run {
        ctx: &ctx,
        environ,
        home: std::env::var("HOME").unwrap_or_default(),
        proc: PathBuf::from("/proc"),
        times: watch::Times::standing(),
    };
    match work::work(&run, queue, run_log) {
        Ok(()) => reply(String::new(), String::new(), 0),
        Err(why) => raised("page-session", String::new(), &why),
    }
}

#[cfg(test)]
mod tests;
