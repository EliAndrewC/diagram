//! `finished-run-hooks` (features 170, 246, 295; ported from the shell of the same name, feature 449 T017): A RUN THAT HAS FINISHED
//! CANNOT BE REPORTED AS STILL GOING. A session reported a gate as waiting that had failed four hours earlier (2026-08-30). Three rules:
//! a finished run nobody was told about is surfaced at the next prompt and at turn end; a turn may not close over a make run that is
//! still going and that nothing will wake the session for (the GM, 2026-09-12: refused once per root make, a second attempt closes the
//! turn, and a Stop payload carries no command, so there is no token escape); a waiter whose producer is dead is reported.
//!
//! Plan T017's decisions: (a) every mode and all the shell's Python ported, the rest of the modes [`cli`]; (b) the script stays a
//! forwarder until T051 for `review_prereq.py`'s `live`; (c) `writer-alive.sh` stays theirs.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use serde_json::Value;

use crate::protocol::{Answer, Event, Guard, Reply};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;

pub(crate) mod runs;

use runs::{Procs, Root, Status};

/// The guard.
pub const GUARD: Guard = Guard {
    name: "finished-run-hooks",
    events: &["UserPromptSubmit", "Stop"],
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
        if let Some(refusal) = hold(&clone, c, &mut lines, &fire) {
            return vec![Answer::Refuse(refusal)];
        }
    }
    if lines.is_empty() {
        Vec::new()
    } else {
        vec![Answer::Print(lines.join("\n"))]
    }
}

/// THE TURN MAY NOT CLOSE OVER A RUN THAT IS STILL GOING, unless the run will wake the session (feature 246); and a waiter on a dead
/// producer is reported. The refusal's words, when there is one.
fn hold(
    clone: &Path,
    c: &Ctx,
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
    let roots = c.procs.judge_runs(clone);
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
    Some(refusal(&unwatched))
}

/// One line for a run that will wake the session, recorded.
fn woken(r: &Root, lines: &mut Vec<String>, fire: &dyn Fn(&str, &str, &str)) {
    let (pid, target) = (r.pid, &r.target);
    let (line, rule) = if let Status::Watched(waiter, file) = &r.status {
        (format!("finished-run: `make {target}` (pid {pid}) is still going; a waiter (pid {waiter}) is watching {file} and will wake this session. Nothing more to arm."), "waiter-armed")
    } else {
        (format!("finished-run: `make {target}` (pid {pid}) is still going; the harness will wake this session when it finishes (its output: {}). Nothing more to arm.", r.detail()), "tracked-run")
    };
    lines.push(line);
    fire("permitted", &format!("{pid} {target} {}", r.detail()), rule);
}

fn refusal(unwatched: &[&Root]) -> String {
    let mut text = String::from("A MAKE RUN THIS SESSION STARTED IS STILL GOING, DETACHED, AND NOTHING WILL WAKE THIS SESSION FOR IT:\n");
    for r in unwatched {
        let detail = r.detail();
        let _ = writeln!(
            text,
            "  pid {} `make {}`, output in {detail}",
            r.pid, r.target
        );
        if detail.contains("/verify-gate") {
            text += "  wait on it: `make verify-wait`, run_in_background - it ends when the gate does\n";
        } else {
            let _ = writeln!(text, "  wait on it in the background: until grep -qE \"gate green|GATE NOT GREEN|GATE FAILED\" {detail}; do sleep 20; done");
        }
    }
    text + "Then REPORT WHAT IT SAID. (A run started with run_in_background needs NO loop.) Ending the turn on purpose: end it again."
}

/// `--finished-run check <clone>`, `seen <clone>`, `live <clone>`, `judge <clone>`, `stale [clone]`.
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
        _ => Reply {
            stdout: String::new(),
            stderr: "usage: l7r-guard --finished-run check <clone>|seen <clone>|live <clone>|judge <clone>|stale [clone]\n".to_owned(),
            code: 2,
        },
    }
}

#[cfg(test)]
mod tests;
