//! The shared differential runner (feature 449 T161, the GM 2026-11-16 and 2026-11-11): `l7r-gate diff-run <cases file> [--only NAME]
//! [--verify] [--twice] [--all --reason "..."] [--jobs N]`, behind `make diff-run`, which every port task's comparison uses in place of a hand-written
//! driver loop. It runs each case on both sides, compares, records, and after a fix reruns only the sides whose key moved; `--jobs N`
//! runs the owed sides on N workers, each in its own world (feature 449 T173, `runner`'s SEVERAL WORKERS).
//!
//! WHY: the differential is the part of a port task's time a script can cut - T145's agent waited on its harness 53.8 min in the background
//! and 10.1 min in the foreground of a 232 min run, every case rerun after each fix by drivers that kept no record of what a case had
//! already shown (the plan's `### T161 (`). The cases file is `docs/diff-run.md`'s; the keys are [`keys`]'; the state directory and the
//! report are [`runner`]'s.

pub mod cases;
pub mod checkout;
pub mod keys;
pub mod norm;
pub mod reuse;
pub mod run;
pub mod runner;

use std::path::Path;
use std::time::SystemTime;

use l7r_gate_core::Reply;
use l7r_shared::escape::enough;
use l7r_shared::log::{civil, place};
use l7r_shared::pyjson::dumps;
use serde_json::json;

use runner::Opts;

const USAGE: &str = "usage: l7r-gate diff-run <cases file> [--only <case name>] [--verify] [--twice] [--all --reason \"<two words or more>\"] [--jobs <workers>] [--fresh-worlds]\n";

fn refused(why: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("diff-run: {why}\n"),
        code: 2,
    }
}

/// What the escape is recorded with: the guard log's directory and the session, handed in so a test never writes the real log.
pub struct Ctx<'a> {
    pub log_dir: &'a Path,
    pub session: String,
    pub cwd: std::path::PathBuf,
}

/// `--all` recorded in the guard log as the gate's escapes are (`make`'s `LOGESCAPE`, `pages::escape_log`'s format): `escaped` with its
/// reason, or `blocked` when the reason is short - taken here and not in the Makefile, so a direct `l7r-gate diff-run --all` is held to
/// the same floor and recorded once.
fn log_escape(ctx: &Ctx, event: &str, rule: &str, reason: &str, file: &str) {
    let now = SystemTime::now();
    let secs = now
        .duration_since(SystemTime::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, mo, d, h, mi, s) = civil(secs);
    let entry = json!({
        "utc": format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z"), "guard": "diff-run", "event": event, "rule": rule,
        "session": ctx.session, "session_name": l7r_shared::speckit::py_name(&ctx.cwd), "cwd": ctx.cwd.to_string_lossy(),
        "tool": "", "transcript": "", "detail": reason.chars().take(200).collect::<String>(),
        "command": format!("l7r-gate diff-run {file} --all"), "context": {"cases": file},
    });
    let _ = place(ctx.log_dir, &dumps(&entry, Some(2), true), now);
}

/// `--jobs`' value (feature 449 T173): a whole number of workers, 1 or more.
fn jobs(v: Option<&String>) -> Result<usize, String> {
    v.and_then(|n| n.parse::<usize>().ok())
        .filter(|&n| n > 0)
        .ok_or_else(|| {
            format!(
                "--jobs takes the number of workers, a whole number 1 or more, not {:?} (make diff-run CASES=... JOBS=4)",
                v.map_or("", String::as_str)
            )
        })
}

fn parse(args: &[String]) -> Result<(String, Opts), String> {
    let mut opts = Opts::default();
    let mut file = None;
    let mut it = args.iter();
    while let Some(a) = it.next() {
        match a.as_str() {
            "--only" => opts.only = Some(it.next().ok_or("--only takes a case name")?.clone()),
            "--reason" => opts.reason = Some(it.next().ok_or("--reason takes the reason")?.clone()),
            "--verify" => opts.verify = true,
            "--twice" => opts.twice = true,
            "--all" => opts.all = true,
            "--jobs" => opts.jobs = jobs(it.next())?,
            "--fresh-worlds" => opts.fresh_worlds = true,
            flag if flag.starts_with('-') => return Err(format!("no flag {flag}")),
            path if file.is_none() => file = Some(path.to_owned()),
            extra => return Err(format!("one cases file, not also {extra}")),
        }
    }
    let file = file.ok_or("the cases file is required")?;
    if opts.verify && opts.only.is_some() {
        // a verify run is every case's new side: its report is what a plan's count cites, so one case's run must not carry that name
        return Err("--verify reruns every case's new side; it takes no --only".to_owned());
    }
    if opts.reason.is_some() && !opts.all {
        return Err("--reason goes with --all".to_owned());
    }
    Ok((file, opts))
}

/// `l7r-gate diff-run ...`: the summary on stdout, each case's line on stderr as it finishes; exit 0 when every case is the same, 1 when
/// any differs, fails or shows run-to-run noise, 2 when the run is refused.
#[must_use]
pub fn cli(args: &[String], ctx: &Ctx) -> Reply {
    let (file, opts) = match parse(args) {
        Ok(p) => p,
        Err(why) => return refused(format!("{why}\n{USAGE}").trim_end()),
    };
    if opts.all {
        let reason = opts.reason.clone().unwrap_or_default();
        if !enough(&reason) {
            log_escape(ctx, "blocked", "all-no-reason", &reason, &file);
            return refused("--all reruns every side of every case, the incremental record thrown away: it needs REASON=\"<two words or more, eight characters>\" (make diff-run CASES=... ALL=1 REASON=\"...\"), recorded in the report and the guard log");
        }
        log_escape(ctx, "escaped", "all", &reason, &file);
    }
    let cases = match cases::load(Path::new(&file)) {
        Ok(c) => c,
        Err(why) => return refused(&why),
    };
    match runner::execute(&cases, &opts, &mut std::io::stderr()) {
        Ok((_, summary, same)) => Reply {
            stdout: summary,
            stderr: String::new(),
            code: i32::from(!same),
        },
        Err(why) => refused(&why),
    }
}

#[cfg(test)]
mod tests;
