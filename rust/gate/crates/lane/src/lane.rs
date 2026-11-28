//! `l7r-gate lane <verb>` (feature 461 T11, `contracts/lane-cli.md`): the lane's command line. T11 builds `status` (`make lane`):
//! each hand-in on the lane and its state, each open batch and its state, the last landed batch's line and the repairs open, all
//! COMPUTED (`log.rs`) from the pool's log, the done refs, `origin/main` and the lane's log (the repairs by the queue's reader, 461 T65). It only reads: no fetch (the
//! `origin/main` the clone last fetched), nothing created, and an empty lane ends 0. T12 adds the runner's verbs (`runner.rs`):
//! `start` (`make lane-start`), `stop [--now]` (`make lane-stop`, `NOW=1`) and the runner's own `--work <common>`; T20 `wait`
//! (`make lane-wait`, `wake.rs`), the coordinator's wake-up.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;

use l7r_gate_core::Reply;
use l7r_gate_task::builder_done::{held_by, REFS};

use crate::log::{self, HandInState, World};
use crate::runner;
use crate::wake;

const USAGE: &str = "usage: l7r-gate lane status|start|stop [--now]|wait (make lane, make lane-start, make lane-stop [NOW=1], make lane-wait)\n";

/// `l7r-gate lane <args>` from `cwd`, any tree of the clone; `exe` is this binary, which `start` runs again as the runner, and `env`
/// the process's environment (the runner's knobs).
#[must_use]
pub fn cli(args: &[String], cwd: &Path, exe: &Path, env: &dyn Fn(&str) -> Option<String>) -> Reply {
    let in_clone = |verb: &dyn Fn(&Path) -> Reply| {
        common_dir(cwd).map_or_else(|| nowhere(cwd), |common| verb(&common))
    };
    let words: Vec<&str> = args.iter().map(String::as_str).collect();
    match words.as_slice() {
        ["status", ..] => status(cwd),
        ["start"] => in_clone(&|c| {
            runner::start(
                c,
                &runner::runner_exe(c, exe),
                "setsid",
                runner::START_WAIT_S,
            )
        }),
        ["stop"] => in_clone(&|c| runner::stop(c, false, runner::STOP_WAIT_S)),
        ["stop", "--now"] => in_clone(&|c| runner::stop(c, true, runner::STOP_WAIT_S)),
        ["wait"] => in_clone(&|c| wake::wait_cli(c, env)),
        ["--work", common] => runner::work_cli(Path::new(common), env),
        _ => reply(String::new(), USAGE.to_owned(), 2),
    }
}

/// The absolute git common directory of the clone `cwd` belongs to, shared by its pool trees and the lane's tree.
pub(crate) fn common_dir(cwd: &Path) -> Option<PathBuf> {
    git(
        cwd,
        &["rev-parse", "--path-format=absolute", "--git-common-dir"],
    )
    .map(|c| PathBuf::from(c.trim()))
}

fn nowhere(cwd: &Path) -> Reply {
    reply(
        String::new(),
        format!("lane: {} is in no git repository\n", cwd.display()),
        1,
    )
}

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// `git -C cwd args`'s stdout, where it succeeded.
pub(crate) fn git(cwd: &Path, args: &[&str]) -> Option<String> {
    let done = Command::new("git").arg("-C").arg(cwd).args(args).output();
    done.ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
}

/// `make lane`: the lane as it stands, read from the clone `cwd` belongs to.
fn status(cwd: &Path) -> Reply {
    let Some(common) = common_dir(cwd) else {
        return nowhere(cwd);
    };
    let pool = log::lines_of(&common.join(l7r_shared::builder_queue::LOG));
    let lane = log::read(&common);
    let refs: BTreeSet<String> = git(cwd, &["for-each-ref", "--format=%(objectname)", REFS])
        .unwrap_or_default()
        .lines()
        .map(str::to_owned)
        .collect();
    let hand_ins = log::on_lane(log::hand_ins(&pool), &refs, &lane);
    let commits: Vec<String> = hand_ins.iter().map(|h| h.commit.clone()).collect();
    let on_main = held_by(cwd, "origin/main", &commits);
    let mut args = vec!["log", "--no-walk", "--ignore-missing", "--format=%H%x09%s"];
    args.extend(commits.iter().map(String::as_str));
    let subjects: BTreeMap<String, String> = git(cwd, &args)
        .unwrap_or_default()
        .lines()
        .filter_map(|l| l.split_once('\t'))
        .map(|(sha, s)| (sha.to_owned(), s.to_owned()))
        .collect();
    let batches = log::batches(&lane);
    let world = World {
        hand_ins: &hand_ins,
        on_main: &on_main,
        log: &lane,
        batches: &batches,
    };
    let repairs = log::repairs_open(&common);
    reply(report(&world, &subjects, &repairs), String::new(), 0)
}

/// What `make lane` prints of `w`: the hand-ins not yet landed or superseded (the landed are history, the log's), each with its
/// state; each open batch; the last landed batch's line; the repairs open (`repairs`, [`log::repairs_open`]'s).
#[must_use]
pub fn report(w: &World, subjects: &BTreeMap<String, String>, repairs: &[String]) -> String {
    let live: Vec<_> = w
        .hand_ins
        .iter()
        .map(|h| (h, log::state(h, w)))
        .filter(|(_, s)| !matches!(s, HandInState::Landed | HandInState::Superseded))
        .collect();
    let waiting = live
        .iter()
        .filter(|(_, s)| *s == HandInState::Waiting)
        .count();
    let mut out = format!(
        "lane: {} hand-in(s) on the lane, {waiting} waiting\n",
        live.len()
    );
    for (h, s) in &live {
        let _ = writeln!(
            out,
            "  {} {}  {}  {s}  {}  \"{}\"",
            h.feature,
            h.tasks.join(","),
            h.commit.get(..10).unwrap_or(&h.commit),
            h.at,
            subjects.get(&h.commit).map_or("", String::as_str)
        );
    }
    let open: Vec<_> = w.batches.iter().filter(|b| b.open()).collect();
    if open.is_empty() {
        out.push_str("lane: no batch open\n");
    }
    for b in open {
        let _ = writeln!(
            out,
            "lane: batch {} {}, {} change(s)",
            b.id,
            b.state,
            b.changes.len()
        );
    }
    let last = w.log.iter().rev().find(|l| l["event"] == "landed");
    match last {
        Some(l) => {
            let count = |k: &str| l[k].as_array().map_or(0, Vec::len);
            let _ = writeln!(
                out,
                "lane: the last landed batch {}: {} landed, {} ejected, {} run(s), {} minutes",
                l["batch"].as_str().unwrap_or_default(),
                count("landed"),
                count("ejected"),
                l["runs"],
                l["minutes"]
            );
        }
        None => out.push_str("lane: no batch landed yet\n"),
    }
    if repairs.is_empty() {
        out.push_str("lane: no repair open\n");
    } else {
        let _ = writeln!(out, "lane: repairs open: {}", repairs.join(", "));
    }
    out
}

#[cfg(test)]
mod tests;
