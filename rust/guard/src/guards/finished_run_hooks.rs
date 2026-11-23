//! `finished-run-hooks` (features 170, 246, 295; ported from the shell of the same name, feature 449 T017): A RUN THAT HAS FINISHED
//! CANNOT BE REPORTED AS STILL GOING. A session reported a gate as waiting that had failed four hours earlier (2026-08-30). Three rules:
//! a finished run nobody was told about is surfaced at the next prompt and at turn end; a turn may not close over a make run that is
//! still going and that nothing will wake the session for (the GM, 2026-09-12: refused once per root make, a second attempt closes the
//! turn, and a Stop payload carries no command, so there is no token escape); a waiter whose producer is dead is reported.
//!
//! Plan T017's decisions: (a) every mode and all the shell's Python ported, the rest of the modes [`cli`]; (b) the script stays a
//! forwarder until T051 for `review_prereq.py`'s `live`; (c) `writer-alive.sh` stays theirs.

use std::path::{Path, PathBuf};

use serde_json::Value;

use crate::protocol::{Answer, Event, Guard, Reply};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;

pub(crate) mod runs;

use runs::{Procs, Root, Starter, Status};

/// The guard.
pub const GUARD: Guard = Guard {
    name: "finished-run-hooks",
    // SessionStart: a compaction forgets what was said in one line (451 T171, `once::forget`)
    events: &["UserPromptSubmit", "Stop", "SessionStart"],
    matcher: "*",
    decide,
};

/// What one decision reads.
pub(crate) struct Ctx {
    pub procs: Procs,
    pub tree: PathBuf,
    pub now: i64,
    /// The working directory, for a payload that names none.
    pub pwd: String,
}

impl Ctx {
    fn real() -> Self {
        Self {
            procs: Procs {
                root: PathBuf::from("/proc"),
                mine: std::process::id(),
            },
            tree: std::env::var("L7R_GUARD_TREE")
                .map_or_else(|_| PathBuf::from("/diagram"), PathBuf::from),
            now: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map_or(0, |d| i64::try_from(d.as_secs()).unwrap_or(0)),
            pwd: std::env::current_dir()
                .unwrap_or_default()
                .to_string_lossy()
                .into_owned(),
        }
    }
}

/// A duration a person reads.
pub(crate) fn human(secs: i64) -> String {
    if secs < 90 {
        format!("{secs}s")
    } else if secs < 5400 {
        format!("{} min", secs / 60)
    } else {
        format!("{} h", secs / 3600)
    }
}

/// The newest run record under the log, by modification time then path: the run log is in month folders.
fn newest(dir: &Path) -> Option<PathBuf> {
    let mut best: Option<(std::time::SystemTime, PathBuf)> = None;
    let mut stack = vec![dir.to_path_buf()];
    while let Some(d) = stack.pop() {
        for p in std::fs::read_dir(d)
            .into_iter()
            .flatten()
            .filter_map(Result::ok)
            .map(|e| e.path())
        {
            if p.is_dir() {
                stack.push(p);
            } else if p.extension().is_some_and(|x| x == "json") {
                let at = std::fs::metadata(&p)
                    .and_then(|m| m.modified())
                    .unwrap_or(std::time::UNIX_EPOCH);
                if best.as_ref().is_none_or(|b| (at, &p) > (b.0, &b.1)) {
                    best = Some((at, p));
                }
            }
        }
    }
    best.map(|b| b.1)
}

/// One line about the newest finished run the session has not been told about, or nothing.
pub(crate) fn report(clone: &Path, mark: bool, now: i64) -> Option<String> {
    let last = newest(&clone.join("dev/run-log"))?;
    let name = last.file_name()?.to_string_lossy().into_owned();
    let seen = clone.join(".git/finished-run.seen");
    if std::fs::read_to_string(&seen).is_ok_and(|s| s == name) {
        return None;
    }
    let doc: Value = std::fs::read_to_string(&last)
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or(Value::Null);
    let get = |k: &str| {
        doc.get(k).map_or_else(String::new, |v| {
            v.as_str().map_or_else(|| v.to_string(), str::to_owned)
        })
    };
    let age = crate::guards::measure_hooks::parse_utc(&get("utc")).map_or(0, |at| now - at);
    if mark {
        let _ = std::fs::write(&seen, &name);
    }
    let (target, result, seconds, when) =
        (get("target"), get("result"), get("seconds"), human(age));
    Some(if result == "green" || result == "already-verified" {
        format!("finished-run: `make {target}` finished {when} ago: {result} ({seconds}s). It is NOT still running.")
    } else {
        format!("finished-run: `make {target}` finished {when} ago and it is {result} ({seconds}s) - NOT still running. Read it before you report on it.")
    })
}

/// The working tree a directory stands in.
fn clone_of(dir: &str) -> Option<PathBuf> {
    runs::owner(Path::new(dir)).filter(|_| Path::new(dir).is_dir())
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    judge(event, session, &Ctx::real())
}

pub(crate) fn judge(event: &Event, session: &Session, c: &Ctx) -> Vec<Answer> {
    let cwd = Some(field(&event.input, "cwd"))
        .filter(|s| !s.is_empty())
        .unwrap_or(&c.pwd)
        .to_owned();
    let Some(clone) = clone_of(&cwd) else {
        return Vec::new();
    };
    // A COMPACTION FORGETS WHAT WAS SAID (451 T171): a SessionStart reports nothing; after a compaction, a clear or a resume, the next
    // Stop says the refusal in full
    if event.name == "SessionStart" {
        let git_dir = crate::guards::event_log_hooks::common_git_dir(&clone);
        let said = crate::shared::once::file(&git_dir, &event.input);
        crate::shared::once::forget(said.as_deref(), field(&event.input, "source"));
        return Vec::new();
    }
    let stop = event.name == "Stop";
    let fire = |kind: &str, detail: &str, rule: &str| {
        log::fire("finished-run", kind, detail, rule, &event.input, session);
    };
    let mut lines = Vec::new();
    if let Some(out) = report(&clone, true, c.now) {
        lines.push(out.clone());
        if stop {
            lines.push(
                "finished-run: do not end a turn saying a run is still going when this one is not."
                    .to_owned(),
            );
        }
        fire("reminded", &out, "finished-not-running");
    }
    if stop {
        let transcript = Path::new(field(&event.input, "transcript_path"));
        let me = field(&event.input, "session_id");
        // AN UNCHANGED REFUSAL IS SAID ONCE (451 T171): in full, then in one line until it changes or a Stop passes without it
        let said = crate::shared::once::file(
            &crate::guards::event_log_hooks::common_git_dir(&clone),
            &event.input,
        );
        if let Some(refusal) = hold(&clone, c, (transcript, me), &mut lines, &fire) {
            let words = crate::shared::once::say(said.as_deref(), "finished-run", &refusal, c.now);
            return vec![Answer::Refuse(words)];
        }
        crate::shared::once::clear(said.as_deref(), "finished-run");
    }
    if lines.is_empty() {
        Vec::new()
    } else {
        vec![Answer::Print(lines.join("\n"))]
    }
}

/// The task id a run's output names: the harness's shell writes `<tmp>/<project>/<session>/tasks/<id>.output` (measured 2026-11-21:
/// a builder's own Bash call's fd 1, `.../c6fd72d1-.../tasks/bnawljeqh.output`).
fn task_id(output: &str) -> Option<&str> {
    let path = Path::new(output);
    (path.parent()?.file_name()? == "tasks")
        .then(|| path.file_name()?.to_str()?.strip_suffix(".output"))
        .flatten()
}

/// The agent whose call launched a background task, from the event log's line for its launch (451 T85): `event_log_hooks` writes a
/// backgrounded call's `PostToolUse` with the task's id as `bg` and, for a subagent's call, the hook payload's own `agent_id` as
/// `by` (none for the session's own call). The clone's logs are read newest first, a line at a time, and only a line naming the id
/// is parsed: the line's `by` (None for a session's own call) and its `sid`, or None for a launch no log names.
fn launch_of(logs: &Path, id: &str) -> Option<(Option<String>, String)> {
    use std::io::BufRead as _;
    let needle = format!("\"bg\":\"{id}\"");
    let mut files: Vec<(std::time::SystemTime, PathBuf)> = std::fs::read_dir(logs)
        .into_iter()
        .flatten()
        .filter_map(Result::ok)
        .map(|e| e.path())
        .filter(|p| p.extension().is_some_and(|x| x == "jsonl"))
        .map(|p| {
            (
                p.metadata()
                    .and_then(|m| m.modified())
                    .unwrap_or(std::time::UNIX_EPOCH),
                p,
            )
        })
        .collect();
    files.sort_unstable();
    files.reverse();
    let row = files.into_iter().find_map(|(_, file)| {
        let f = std::fs::File::open(file).ok()?;
        std::io::BufReader::new(f)
            .lines()
            .map_while(Result::ok)
            .filter(|l| l.contains(&needle))
            .map(|l| serde_json::from_str::<Value>(&l).unwrap_or(Value::Null))
            .find(|row| row.get("ev").and_then(Value::as_str) == Some("PostToolUse"))
    })?;
    let by = row.get("by").and_then(Value::as_str).map(str::to_owned);
    Some((by, field(&row, "sid").to_owned()))
}

/// WHO STARTED A RUN THE HARNESS HOLDS (451 T85), by its output: the session itself - or a call no launch line names, which an agent
/// mid-call holds (a foreground call; or a background one whose `PostToolUse` has not come, 4 s after its run started on 2026-11-20
/// 23:22:49) - is the harness's to wake (feature 246); a builder still running by `set_down_hooks`' reading of the session's transcript
/// (T65: launched or resumed, or interim with its own work going) is the builder's, whose own notice wakes the session; any other
/// builder has stopped, or the transcript cannot say, and its run is judged as a detached one. `known` holds each builder's answer, so
/// a transcript is read once a turn's end however many of a builder's runs are live.
///
/// A RUN IS ITS STARTER'S TO WAIT ON (451 T171): a launch line whose `sid` is another session's - a page session's, in the same clone -
/// is that session's run, which its own Stop names; and an agent the session's transcript never names, a builder's own sub-agent, runs
/// while its dispatcher does (`set_down_hooks::still_running`). `me` is the Stop's own session id, "" where the payload names none.
fn starter(
    logs: &Path,
    transcript: &Path,
    (me, output): (&str, &str),
    known: &std::cell::RefCell<std::collections::HashMap<String, bool>>,
) -> Starter {
    let Some((by, sid)) = task_id(output).and_then(|id| launch_of(logs, id)) else {
        return Starter::Harness;
    };
    if !me.is_empty() && !sid.is_empty() && sid != me {
        return Starter::Session(sid);
    }
    let Some(agent) = by else {
        return Starter::Harness;
    };
    let running = *known.borrow_mut().entry(agent.clone()).or_insert_with(|| {
        crate::guards::set_down_hooks::still_running(transcript, &agent).unwrap_or(false)
    });
    if running {
        Starter::Builder(agent)
    } else {
        Starter::Stopped
    }
}

/// THE TURN MAY NOT CLOSE OVER A RUN THAT IS STILL GOING, unless the run will wake the session (feature 246) or a builder still
/// running started it (451 T85); and a waiter on a dead producer is reported. The refusal's words, when there is one.
fn hold(
    clone: &Path,
    c: &Ctx,
    (transcript, me): (&Path, &str),
    lines: &mut Vec<String>,
    fire: &dyn Fn(&str, &str, &str),
) -> Option<String> {
    let told = clone.join(".git/live-run.told");
    let live = c.procs.live_runs(clone);
    if live.is_empty() {
        let _ = std::fs::remove_file(&told);
        let stale = c.procs.stale_waiters(&c.tree, Some(clone));
        if !stale.is_empty() {
            lines.push(
                "A WAITER IS SPINNING ON A DEAD PRODUCER - it will never finish on its own:"
                    .to_owned(),
            );
            lines.extend(stale.iter().map(|s| format!("  pid {s}")));
            lines.push("Nothing is writing that file any more. Read what it DOES have, then stop the loop by its pid.".to_owned());
            fire("reminded", &stale.join("\n"), "waiter-on-a-dead-producer");
        }
        return None;
    }
    let logs = crate::guards::event_log_hooks::log_path(clone, "_");
    let logs = logs.parent().unwrap_or(clone);
    let known = std::cell::RefCell::default();
    let roots = c
        .procs
        .judge_runs_by(clone, &|out| starter(logs, transcript, (me, out), &known));
    let unwatched: Vec<&Root> = roots
        .iter()
        .filter(|r| matches!(r.status, Status::Unwatched(_)))
        .collect();
    if unwatched.is_empty() {
        roots.iter().for_each(|r| woken(r, lines, fire));
        return None;
    }
    let earlier = std::fs::read_to_string(&told).unwrap_or_default();
    let known: Vec<&str> = earlier.split(',').collect();
    let pids: Vec<String> = unwatched.iter().map(|r| r.pid.to_string()).collect();
    if pids.iter().all(|p| known.contains(&p.as_str())) {
        return None; // already told for every one of these runs: a turn may close deliberately
    }
    let _ = std::fs::write(&told, pids.join(","));
    let listed = live
        .iter()
        .map(|(p, t)| format!("{p} {t}"))
        .collect::<Vec<_>>()
        .join("\n");
    fire("blocked", &listed, "run-still-going");
    Some(refusal(
        &unwatched,
        &crate::shared::checks::common_dir(clone),
    ))
}

/// One line for a run that will wake the session, recorded.
fn woken(r: &Root, lines: &mut Vec<String>, fire: &dyn Fn(&str, &str, &str)) {
    let (pid, target) = (r.pid, &r.target);
    let (line, rule) = if let Status::Watched(waiter, file) = &r.status {
        (format!("finished-run: `make {target}` (pid {pid}) is still going; a waiter (pid {waiter}) is watching {file} and will wake this session. Nothing more to arm."), "waiter-armed")
    } else if let Status::Builder(agent, out) = &r.status {
        (format!("finished-run: `make {target}` (pid {pid}) is still going; its builder {agent} is still running, which the run will wake, and the builder's own notice will wake this session (its output: {out}). Nothing more to arm."), "builder-running")
    } else if let Status::Session(sid, out) = &r.status {
        (format!("finished-run: `make {target}` (pid {pid}) is still going; session {sid} started it, and that session's own Stop names it, not this one's (its output: {out}). Nothing more to arm."), "another-session")
    } else {
        (format!("finished-run: `make {target}` (pid {pid}) is still going; the harness will wake this session when it finishes (its output: {}). Nothing more to arm.", r.detail()), "tracked-run")
    };
    lines.push(line);
    fire("permitted", &format!("{pid} {target} {}", r.detail()), rule);
}

fn refusal(unwatched: &[&Root], git_dir: &Path) -> String {
    let runs: Vec<String> = unwatched
        .iter()
        .map(|r| run_said(r.pid, &r.target, &r.detail()))
        .collect();
    refusal_of(&runs, git_dir)
}

/// One run left unwatched: its pid, target and output, and the wait on it.
pub(crate) fn run_said(pid: u32, target: &str, detail: &str) -> String {
    let wait = if detail.contains("/verify-gate") {
        "  wait on it: `make verify-wait`, run_in_background - it ends when the gate does"
            .to_owned()
    } else {
        format!("  wait on it in the background: until grep -qE \"gate green|GATE NOT GREEN|GATE FAILED\" {detail}; do sleep 20; done")
    };
    format!("  pid {pid} `make {target}`, output in {detail}\n{wait}")
}

/// The block over the runs said: the first few and the file holding them all (451 T170: the list grows two lines a run).
pub(crate) fn refusal_of(runs: &[String], git_dir: &Path) -> String {
    format!(
        "A MAKE RUN THIS SESSION STARTED IS STILL GOING, DETACHED, AND NOTHING WILL WAKE THIS SESSION FOR IT:\n{}\n\
Then REPORT WHAT IT SAID. (A run started with run_in_background needs NO loop.) Ending the turn on purpose: end it again.",
        crate::shared::listed::capped_kept(runs, "  ", git_dir)
    )
}

/// `--finished-run check <clone>`, `seen <clone>`, `live <clone>`, `judge <clone>`, `stale [clone]`, `alive <file>`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    with(args, &Ctx::real())
}

pub(crate) fn with(args: &[String], c: &Ctx) -> Reply {
    let say = |lines: Vec<String>| Reply {
        stdout: lines.into_iter().map(|l| l + "\n").collect(),
        stderr: String::new(),
        code: 0,
    };
    let arg = args.get(1).map_or("", String::as_str);
    let clone = Path::new(arg);
    match (args.first().map_or("", String::as_str), arg.is_empty()) {
        ("check", false) => say(report(clone, false, c.now).into_iter().collect()),
        ("seen", false) => {
            let _ = report(clone, true, c.now);
            say(Vec::new())
        }
        ("live", false) => say(c.procs.live_runs(clone).iter().map(|(p, t)| format!("{p} {t}")).collect()),
        ("judge", false) => say(c.procs.judge_runs(clone).iter().map(Root::line).collect()),
        ("stale", _) => say(c.procs.stale_waiters(&c.tree, (!arg.is_empty()).then_some(clone))),
        // `writer-alive.sh`'s last question before "gone" (451 T61): `alive <pid> <how>` where a run names the file, exit 1 where none does
        ("alive", false) => c.procs.runner_of(clone).map_or_else(
            || Reply {
                stdout: String::new(),
                stderr: String::new(),
                code: 1,
            },
            |r| say(vec![format!("alive {r}")]),
        ),
        _ => Reply {
            stdout: String::new(),
            stderr: "usage: l7r-guard --finished-run check <clone>|seen <clone>|live <clone>|judge <clone>|stale [clone]|alive <file>\n".to_owned(),
            code: 2,
        },
    }
}

#[cfg(test)]
mod tests;
