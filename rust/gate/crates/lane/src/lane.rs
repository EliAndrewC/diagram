//! `l7r-gate lane <verb>` (feature 461 T11, `contracts/lane-cli.md`): the lane's command line. T11 builds `status` (`make lane`):
//! each hand-in on the lane and its state, each open batch and its state, the last landed batch's line and the repairs open, all
//! COMPUTED (`log.rs`) from the pool's log, the done refs, `origin/main` and the lane's log. It only reads: no fetch (the
//! `origin/main` the clone last fetched), nothing created, and an empty lane ends 0. `start`, `wait`, `stop` and the runner's own
//! `--work` come with the runner (T12) and the wake-up (T19); until then they are refused with the usage.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;

use l7r_gate_core::Reply;
use l7r_gate_task::builder_done::{held_by, REFS};

use crate::log::{self, HandInState, World};

const USAGE: &str = "usage: l7r-gate lane status (make lane); start, wait, stop and --work come with the runner (461 T12)\n";

/// `l7r-gate lane <args>` from `cwd`, any tree of the clone.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    match args.first().map(String::as_str) {
        Some("status") => status(cwd),
        _ => reply(String::new(), USAGE.to_owned(), 2),
    }
}

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// `git -C cwd args`'s stdout, where it succeeded.
fn git(cwd: &Path, args: &[&str]) -> Option<String> {
    let done = Command::new("git").arg("-C").arg(cwd).args(args).output();
    done.ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
}

/// `make lane`: the lane as it stands, read from the clone `cwd` belongs to.
fn status(cwd: &Path) -> Reply {
    let common = ["rev-parse", "--path-format=absolute", "--git-common-dir"];
    let Some(common) = git(cwd, &common) else {
        return reply(
            String::new(),
            format!("lane: {} is in no git repository\n", cwd.display()),
            1,
        );
    };
    let common = PathBuf::from(common.trim());
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
    reply(report(&world, &subjects), String::new(), 0)
}

/// What `make lane` prints of `w`: the hand-ins not yet landed or superseded (the landed are history, the log's), each with its
/// state; each open batch; the last landed batch's line; the repairs open.
#[must_use]
pub fn report(w: &World, subjects: &BTreeMap<String, String>) -> String {
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
    let repairs = log::repairs_open(w.log, w.hand_ins);
    if repairs.is_empty() {
        out.push_str("lane: no repair open\n");
    } else {
        let _ = writeln!(out, "lane: repairs open: {}", repairs.join(", "));
    }
    out
}

#[cfg(test)]
mod tests;
