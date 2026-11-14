//! The detached loop (`page_session_runner.py`'s `work`, `dispatcher`, `headless_env`, `session_env` and `ledger_rows`, ported by
//! feature 449 T137): each session in turn; a `then` step's printed briefs join the queue where it stood.
//!
//! THE RUN LOG (feature 250, 2026-09-26): one file, held OPEN for the whole queue, with a line as each session starts and ends and `ALL
//! DONE` last. A caller waits on it with the ordinary backgrounded file-watch, and the liveness check the no-poll guard adds finds the
//! runner holding it - so the wait ends when the runner does, finished or killed. Before it, a page's sessions left no one file to wait
//! on, and a wait on `tasks.md` (edited, never held open) was declared dead after two minutes while the sessions ran on. Each line is one
//! write, as the Python's line-buffered file wrote it.

use std::collections::BTreeMap;
use std::fs::File;
use std::io::Write as _;
use std::path::{Path, PathBuf};

use serde_json::Value;

use super::retry::{failed, first_line, resume_command, wait_for, RETRIES};
use super::watch::{now, projects_dir, returned_file, undelivered, Times, Watch, STALL_RESUMES};
use super::{admit, brief_feature, new_item, Ctx, Stop, KEY_CAP};
use crate::{basename, brief_load, dirname, py_join, read_lossy, relpath};

/// What the loop reads of its process beside the launch's own.
pub struct Run<'a> {
    pub ctx: &'a Ctx<'a>,
    /// The process's environment (`os.environ`), which every session's is made from.
    pub environ: Vec<(String, String)>,
    /// `$HOME`, under which the transcripts are found.
    pub home: String,
    /// `/proc`, where a stalled session's processes are found.
    pub proc: PathBuf,
    pub times: Times,
}

/// The session dispatching this queue into its own clone: `own` (the caller's `CLAUDE_CODE_SESSION_ID`) where it claims `root`, else the
/// session whose claim on `root` was written last.
///
/// WHY (feature 250 D14, 2026-09-26): the clone guard refuses an edit in a clone a LIVE other session claims, and the dispatcher is live,
/// waiting on the queue - so a queued session was refused whenever the dispatcher's tree was clean. Its id goes to each session as
/// `L7R_DISPATCHER`, which the guard lets through and nothing else. ...AND THE CALLER FIRST (feature 319, 2026-10-04): every queued
/// session claims the clone too, so after one queue the newest claim was a FINISHED page session's, not the dispatcher's (claimed once,
/// hours before). The next queue named that dead session, and its check session was refused every edit by the live dispatcher it was
/// meant to let through.
#[must_use]
pub fn dispatcher(root: &str, own: &str) -> String {
    let root = root.trim_end_matches('/');
    let parts: Vec<&str> = root.split('/').collect();
    let Some(i) = parts.iter().position(|p| *p == ".clones") else {
        return String::new();
    };
    let mapdir = PathBuf::from(format!("{}/.session-clones", parts[..=i].join("/")));
    let claims: Vec<(String, f64)> = std::fs::read_dir(&mapdir)
        .map(|d| d.filter_map(Result::ok).collect::<Vec<_>>())
        .unwrap_or_default()
        .iter()
        .map(|e| (e.file_name().to_string_lossy().into_owned(), e.path()))
        // `Path.glob("*")`, which takes a hidden name too
        .filter(|(_, p)| p.is_file() && l7r_guard::shared::py_text::strip(&read_lossy(p)) == root)
        .map(|(n, p)| {
            let at = std::fs::metadata(&p)
                .and_then(|m| m.modified())
                .ok()
                .and_then(|t| t.duration_since(std::time::SystemTime::UNIX_EPOCH).ok())
                .map_or(0.0, |d| d.as_secs_f64());
            (n, at)
        })
        .collect();
    if !own.is_empty() && claims.iter().any(|(n, _)| n == own) {
        return own.to_owned();
    }
    // `max(claims, key=mtime)`: the first of the newest, in the directory's order
    claims
        .into_iter()
        .reduce(|best, c| if c.1 > best.1 { c } else { best })
        .map_or_else(String::new, |(n, _)| n)
}

/// The environment a queued session runs in: the dispatcher's, with its id added and its TMUX variables removed.
///
/// WHY (2026-09-27): a queued session is headless and has no tab, but it inherited `TMUX`/`TMUX_PANE` from the session that started the
/// queue, so it registered itself as living in THAT session's tmux pane - and the tab-title hook, finding a pane, retitled the GM's tab
/// with the queued session's name (`diagram-research`).
#[must_use]
pub fn headless_env(parent: &[(String, String)], dispatcher_id: &str) -> BTreeMap<String, String> {
    let mut out: BTreeMap<String, String> = parent
        .iter()
        .filter(|(k, _)| k != "TMUX" && k != "TMUX_PANE")
        .cloned()
        .collect();
    out.insert("L7R_DISPATCHER".to_owned(), dispatcher_id.to_owned());
    out
}

fn field<'v>(item: &'v Value, key: &str) -> &'v str {
    item.get(key).and_then(Value::as_str).unwrap_or("")
}

/// The queue's environment for one session: its id, its continuation path, and the key cap if it writes.
#[must_use]
pub fn session_env(
    env: &BTreeMap<String, String>,
    item: &Value,
    cwd: &str,
) -> BTreeMap<String, String> {
    let mut out = env.clone();
    out.remove("L7R_KEY_CAP");
    out.insert("L7R_PAGE_SESSION".to_owned(), field(item, "sid").to_owned());
    out.insert(
        "L7R_CONTINUE".to_owned(),
        py_join(field(item, "log"), "continue.md"),
    );
    // an `assertions` brief writes too - only its QUESTION count is exempt (feature 428, 2026-10-26: the money write briefs declared it,
    // and a session reserved an eleventh registry key unrefused)
    let brief = field(item, "brief");
    let write = super::retry::truthy(item.get("write"));
    if write
        || (!brief.is_empty()
            && brief_load::declared(&read_lossy(Path::new(brief))) == "assertions")
    {
        out.insert("L7R_KEY_CAP".to_owned(), KEY_CAP.to_string());
    }
    let fd = brief_feature(brief, cwd);
    if !fd.is_empty() {
        // its checks and rulings are its brief's feature's (the arbiter's feature directory)
        out.insert("L7R_FEATURE_DIRECTORY".to_owned(), fd);
    }
    out
}

/// Each check pass of the session that ended gets its review-ledger row, filled from the agent's own reply, its acted-on cell naming
/// the brief's directory (where the session records its checks). Headless sessions wrote none: 343's and 368's owed 124 rows at landing
/// (2026-10-11), and the push refuses until each pass has one (feature 371). The write is the `reviews` crate's `ledger-owed`, asked in
/// process where the Python ran the root's `l7r-gate.sh reviews ledger-owed` (feature 449 T83's command, `ask:449-T83-scope`); a root
/// with no gate of its own (the runner's own tests) writes none, as the Python skipped it, and what the write answers is not read.
pub fn ledger_rows(run: &Run, item: &Value) {
    let root = &run.ctx.root;
    if !Path::new(&py_join(
        &py_join(&py_join(root, "scripts"), "gates"),
        "l7r-gate.sh",
    ))
    .is_file()
    {
        return;
    }
    let brief = field(item, "brief");
    let where_ = if brief.starts_with('/') {
        relpath(dirname(brief), root, &run.ctx.cwd)
    } else {
        dirname(brief).to_owned()
    };
    let what = if where_.is_empty() {
        "the brief"
    } else {
        &where_
    };
    let args = [
        "--ledger".to_owned(),
        py_join(&py_join(root, "dev"), "review-ledger.md"),
        "--log".to_owned(),
        py_join(&py_join(root, ".git"), "check-passes.jsonl"),
        "--write".to_owned(),
        format!("{what}'s checks file"),
        "--session".to_owned(),
        field(item, "sid").to_owned(),
    ];
    let get = |k: &str| {
        run.environ
            .iter()
            .find(|(n, _)| n == k)
            .map(|(_, v)| v.clone())
    };
    let env = l7r_gate_reviews::reviews::ledger_passes::Env {
        cwd: PathBuf::from(root),
        tree: PathBuf::from(root),
        home: run.home.clone(),
        cache_off: get("L7R_CACHE_OFF").is_some_and(|v| !v.is_empty() && v != "0"),
        claims_sheet: get("L7R_CLAIMS_SHEET"),
    };
    let _ = l7r_gate_reviews::reviews::ledger_passes::cli(&args, &env);
}

/// A line written to the run log; a failed write is the Python's raise.
fn say(log: &mut File, line: &str) -> Result<(), String> {
    log.write_all(format!("{line}\n").as_bytes())
        .map_err(|e| format!("the run log: {e}"))
}

/// The exit code as Python's `returncode` gives it: the code, or minus the signal that ended the process.
fn code_of(status: std::process::ExitStatus) -> i32 {
    use std::os::unix::process::ExitStatusExt as _;
    status
        .code()
        .unwrap_or_else(|| -status.signal().unwrap_or(0))
}

/// A `then` step run in the root: the briefs it printed, one a line.
fn then_briefs(script: &str, root: &str) -> Result<Vec<String>, String> {
    let got = std::process::Command::new(script)
        .current_dir(root)
        .stdin(std::process::Stdio::inherit())
        .output()
        .map_err(|e| format!("{script}: {e}"))?;
    let text = String::from_utf8(got.stdout).map_err(|e| format!("UnicodeDecodeError: {e}"))?;
    Ok(l7r_guard::shared::speckit::splitlines(&text)
        .iter()
        .map(|l| l7r_guard::shared::py_text::strip(l))
        .filter(|l| !l.is_empty())
        .map(str::to_owned)
        .collect())
}

/// One session run to its end: its attempts, each beside a watch, resumed after a stall at once and after a failure past its wait.
fn run_session(
    run: &Run,
    item: &Value,
    env: &BTreeMap<String, String>,
    runlog: &mut File,
) -> Result<i32, String> {
    let ctx = run.ctx;
    let (sid, log) = (field(item, "sid"), field(item, "log"));
    let first: Vec<String> = item
        .get("cmd")
        .and_then(Value::as_array)
        .map(|c| {
            c.iter()
                .map(|a| a.as_str().unwrap_or("").to_owned())
                .collect()
        })
        .unwrap_or_default();
    let projects = projects_dir(&ctx.root, &run.home);
    let mut cmd = first.clone();
    let (mut attempt, mut stalls) = (0u32, 0u32);
    let mut rc;
    loop {
        let watch = Watch::start(
            projects.clone(),
            sid.to_owned(),
            run.times,
            run.proc.clone(),
        );
        let (result, stderr) = (py_join(log, "result.json"), py_join(log, "stderr.txt"));
        let opened = File::create(&result).and_then(|o| Ok((o, File::create(&stderr)?)));
        let status = opened
            .and_then(|(out, err)| {
                std::process::Command::new(&cmd[0])
                    .args(&cmd[1..])
                    .current_dir(&ctx.root)
                    .env_clear()
                    .envs(session_env(env, item, &ctx.cwd))
                    .stdin(std::process::Stdio::null())
                    .stdout(out)
                    .stderr(err)
                    .status()
            })
            .map_err(|e| format!("{}: {e}", cmd[0]));
        let (stalled, idle) = watch.stop();
        rc = code_of(status?);
        let text = read_lossy(Path::new(&result)) + &read_lossy(Path::new(&stderr));
        if stalled {
            // A STALL IS RESUMED AT ONCE (feature 295 item 3): it is not the usage limit, so no backoff is owed
            if stalls == STALL_RESUMES {
                say(runlog, &format!("stalled {sid} - idle {} min, resumed {STALL_RESUMES} times already; moving on", idle / 60))?;
                break;
            }
            stalls += 1;
            say(
                runlog,
                &format!(
                    "stalled {sid} - idle {} min, resuming it ({stalls} of {STALL_RESUMES})",
                    idle / 60
                ),
            )?;
            let returned = returned_file(log, &undelivered(&projects, sid))?;
            cmd = resume_command(&first, sid, returned.as_deref());
            continue;
        }
        if !failed(rc, &text) || attempt == RETRIES {
            break;
        }
        let wait = wait_for(&text, attempt, now());
        #[allow(clippy::cast_possible_truncation, reason = "a quarter hour's seconds")]
        let every = run.times.retry_every as i64;
        let nap = wait.min(every);
        say(
            runlog,
            &format!(
                "failed {sid} rc={rc} - waiting {} min (reset in {}), then resuming it ({})",
                nap / 60,
                wait / 60,
                first_line(&text)
            ),
        )?;
        #[allow(clippy::cast_precision_loss, reason = "a few hours' seconds")]
        std::thread::sleep(std::time::Duration::from_secs_f64(
            (wait as f64).min(run.times.retry_every),
        ));
        attempt += 1;
        let returned = returned_file(log, &undelivered(&projects, sid))?;
        cmd = resume_command(&first, sid, returned.as_deref());
    }
    Ok(rc)
}

/// The detached loop over `queue`, its lines in `run_log`, `ALL DONE` last.
///
/// # Errors
///
/// What the Python raised and ended the queue on (a step that cannot run, a session command that cannot start, a directory or log that
/// cannot be written): no `ALL DONE` is written after one.
pub fn work(run: &Run, queue: Vec<Value>, run_log: &str) -> Result<(), String> {
    let ctx = run.ctx;
    let mut queue: std::collections::VecDeque<Value> = queue.into();
    let index = py_join(
        &py_join(&py_join(&ctx.root, ".git"), "page-sessions"),
        "index.txt",
    );
    let open = |p: &str| {
        std::fs::OpenOptions::new()
            .append(true)
            .create(true)
            .open(p)
            .map_err(|e| format!("{p}: {e}"))
    };
    let mut log = open(run_log)?;
    let own = run
        .environ
        .iter()
        .find(|(k, _)| k == "CLAUDE_CODE_SESSION_ID")
        .map_or("", |(_, v)| v.as_str());
    let env = headless_env(&run.environ, &dispatcher(&ctx.root, own));
    let stopped =
        |runlog: &mut File, e: Stop, queue: &mut std::collections::VecDeque<Value>| match e {
            Stop::Refused(why) => {
                queue.clear();
                say(runlog, &format!("STOPPED {why}"))
            }
            Stop::Raised(why) => Err(why),
        };
    while let Some(item) = queue.pop_front() {
        if let Some(then) = item.get("then").and_then(Value::as_str) {
            let briefs = then_briefs(then, &ctx.root)?;
            let late: Result<Vec<Value>, Stop> = briefs
                .iter()
                .map(|b| admit(ctx, b).map(|w| (b, w)))
                .collect::<Result<Vec<_>, _>>()
                .and_then(|admitted| {
                    admitted
                        .into_iter()
                        .map(|(b, w)| new_item(ctx, b, w))
                        .collect()
                });
            match late {
                Ok(late) => {
                    let n = late.len();
                    for (i, made) in late.into_iter().enumerate() {
                        queue.insert(i, made);
                    }
                    say(
                        &mut log,
                        &format!("planned {n} session(s) from {}", basename(then)),
                    )?;
                }
                Err(e) => stopped(&mut log, e, &mut queue)?,
            }
            continue;
        }
        let (sid, brief) = (field(&item, "sid"), field(&item, "brief"));
        open(&index)?
            .write_all(format!("{sid} {brief}\n").as_bytes())
            .map_err(|e| format!("{index}: {e}"))?;
        say(&mut log, &format!("started {sid} {}", basename(brief)))?;
        let rc = run_session(run, &item, &env, &mut log)?;
        say(&mut log, &format!("ended {sid} rc={rc}"))?;
        ledger_rows(run, &item);
        let cont = py_join(field(&item, "log"), "continue.md");
        if Path::new(&cont).is_file() {
            let next = admit(ctx, &cont)
                .map(|w| w || super::retry::truthy(item.get("write")))
                .and_then(|w| new_item(ctx, &cont, w));
            match next {
                Ok(next) => {
                    let line = format!("continued {sid} -> {}", field(&next, "sid"));
                    queue.push_front(next);
                    say(&mut log, &line)?;
                }
                Err(e) => stopped(&mut log, e, &mut queue)?,
            }
        }
    }
    say(&mut log, "ALL DONE")
}

#[cfg(test)]
mod tests;
