//! Refuse unless this process runs under this project's make (feature 127; the check for `l7r-gate`'s own binaries, the round arbiter's `ask:449-T064-slices`). `l7r/diagram/_invocation.py` keeps the same check for the Python's
//! own processes until phase 4: each decides for its own process, and neither calls the other.

use std::path::{Path, PathBuf};

const MAKE_COMMS: [&str; 3] = ["make", "gmake", "remake"];
const FLAGS: [&str; 3] = ["-f", "--file", "--makefile"];

/// What this check reads of the process table, so that a test can give it any tree.
pub(crate) trait Procs {
    /// Every pid from this process up to the top, nearest first.
    fn ancestry(&self) -> Vec<u32>;
    fn comm(&self, pid: u32) -> String;
    fn cwd(&self, pid: u32) -> String;
    fn cmdline(&self, pid: u32) -> Vec<String>;
}

pub(crate) struct Live;

/// The parent named by a `/proc/<pid>/stat`: after the last `)`, since a process's name may itself hold spaces or parentheses.
fn parent_of(stat: &str) -> Option<u32> {
    stat.rsplit_once(") ")?
        .1
        .split_whitespace()
        .nth(1)?
        .parse()
        .ok()
}

impl Procs for Live {
    fn ancestry(&self) -> Vec<u32> {
        let mut out = Vec::new();
        let mut pid = std::process::id();
        while let Some(parent) = std::fs::read_to_string(format!("/proc/{pid}/stat"))
            .ok()
            .as_deref()
            .and_then(parent_of)
            .filter(|_| pid > 1)
        {
            out.push(pid);
            pid = parent;
        }
        out
    }

    fn comm(&self, pid: u32) -> String {
        let stat = std::fs::read_to_string(format!("/proc/{pid}/stat")).unwrap_or_default();
        stat.split_once('(')
            .and_then(|(_, r)| r.rsplit_once(')'))
            .map_or_else(String::new, |(c, _)| c.to_owned())
    }

    fn cwd(&self, pid: u32) -> String {
        std::fs::read_link(format!("/proc/{pid}/cwd"))
            .map_or_else(|_| String::new(), |p| p.to_string_lossy().into_owned())
    }

    fn cmdline(&self, pid: u32) -> Vec<String> {
        let raw = std::fs::read(format!("/proc/{pid}/cmdline")).unwrap_or_default();
        raw.split(|b| *b == 0)
            .filter(|a| !a.is_empty())
            .map(|a| String::from_utf8_lossy(a).into_owned())
            .collect()
    }
}

fn inside(path: &str, repo: &Path) -> bool {
    !path.is_empty() && lexical(Path::new(path)).starts_with(repo)
}

/// A path with `.` and `..` resolved, without touching the disk, as `os.path.abspath`.
fn lexical(path: &Path) -> PathBuf {
    let mut out = PathBuf::new();
    for part in path.components() {
        match part {
            std::path::Component::ParentDir => {
                out.pop();
            }
            std::path::Component::CurDir => {}
            other => out.push(other),
        }
    }
    out
}

/// Is this make driven by a makefile outside the repository? A bare ancestry check accepts `make -f /tmp/evil.mk`, and that make really is the parent; it is just not this project's.
fn foreign_makefile(argv: &[String], make_cwd: &str, repo: &Path) -> bool {
    let outside = |value: &str| {
        !value.is_empty() && !inside(&Path::new(make_cwd).join(value).to_string_lossy(), repo)
    };
    for (at, arg) in argv.iter().enumerate() {
        if FLAGS.contains(&arg.as_str()) {
            return outside(argv.get(at + 1).map_or("", String::as_str));
        }
        if let Some(value) = FLAGS
            .iter()
            .find_map(|f| arg.strip_prefix(&format!("{f}=")))
        {
            return outside(value);
        }
        if arg.starts_with("-f") && !arg.starts_with("--") && arg.len() > 2 {
            return outside(&arg[2..]);
        }
    }
    false
}

/// (is this process under this project's make, why not).
pub(crate) fn compute(procs: &dyn Procs, repo: &Path) -> (bool, &'static str) {
    let mut saw_make = false;
    for pid in procs.ancestry() {
        if !MAKE_COMMS.contains(&procs.comm(pid).as_str()) {
            continue;
        }
        saw_make = true;
        let cwd = procs.cwd(pid);
        if inside(&cwd, repo) && !foreign_makefile(&procs.cmdline(pid), &cwd, repo) {
            return (true, "");
        }
    }
    if saw_make {
        (
            false,
            "a make was found in the process tree, but it does not belong to this repository",
        )
    } else {
        (false, "not invoked through make")
    }
}

/// The refusal for `operation`, or None under this project's make; a refusal that does not say what to run instead is a bug.
pub(crate) fn refusal(
    procs: &dyn Procs,
    repo: &Path,
    operation: &str,
    target: &str,
) -> Option<String> {
    let (ok, why) = compute(procs, repo);
    (!ok).then(|| format!("\n\x1b[1mREFUSED: {operation} was not run through make.\x1b[0m\n\n  {why}.\n\n  Run this instead:  \x1b[1mmake {target}\x1b[0m\n\n    Every operation in this project goes through a make target, so the expensive ones can ask\n    whether the cheap one would do first:\n\n        make quick        lint, types, and every test that does not roll a map\n        make help         every operation, with what it does\n        make done         the full gate, NOT the quick check\n\n    "))
}

#[cfg(test)]
mod tests;
