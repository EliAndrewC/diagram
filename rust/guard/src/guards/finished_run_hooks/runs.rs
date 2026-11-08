//! What runs and who waits: every fact read from `/proc` by pid, never by a pattern over this hook's own command line, which is the
//! 2026-07-25 defect (`pgrep -f "make done"` found the searching shell and looped for 10.9 minutes).

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::os::unix::fs::PermissionsExt;
use std::path::{Component, Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};

use crate::shared::tool::ask;

static LOOP: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\b(until|while)\b.*\bgrep\b").unwrap_or_else(|e| unreachable!("{e}"))
});
static ASSIGN: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r#"(?:^|[\s;&|(])([A-Za-z_]\w*)=("[^"]*"|'[^']*'|[^\s;&|)]*)"#)
        .unwrap_or_else(|e| unreachable!("{e}"))
});
static VAR: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\$\{([A-Za-z_]\w*)\}|\$([A-Za-z_]\w*)").unwrap_or_else(|e| unreachable!("{e}"))
});
static WATCHED_PATH: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?:/[\w.-]+)+\.\w+").unwrap_or_else(|e| unreachable!("{e}")));

/// `os.path.realpath`: a path that need not exist, its existing part's symlinks resolved.
pub(crate) fn realpath(p: &Path) -> PathBuf {
    let mut clean = PathBuf::new();
    for c in p.components() {
        match c {
            Component::ParentDir => {
                clean.pop();
            }
            Component::CurDir => {}
            other => clean.push(other.as_os_str()),
        }
    }
    let mut rest = Vec::new();
    let mut at = clean.as_path();
    loop {
        if let Ok(real) = std::fs::canonicalize(at) {
            return rest
                .iter()
                .rev()
                .fold(real, |acc: PathBuf, n: &&std::ffi::OsStr| acc.join(n));
        }
        let (Some(up), Some(name)) = (at.parent(), at.file_name()) else {
            return clean.clone();
        };
        rest.push(name);
        at = up;
    }
}

/// The working tree a path belongs to: its NEAREST enclosing `.git`, so a clone nested under the mirror is its own.
pub(crate) fn owner(path: &Path) -> Option<PathBuf> {
    let real = realpath(path);
    real.ancestors()
        .find(|d| d.join(".git").exists())
        .map(Path::to_path_buf)
}

/// What a root run's status is: `tracked` and `watched` will wake the session, `unwatched` is the one shape that can go unread.
#[derive(Debug, PartialEq, Eq)]
pub(crate) enum Status {
    Tracked(String),
    Watched(u32, String),
    Unwatched(String),
}

/// A root live make: one none of whose ancestors is a live make.
#[derive(Debug, PartialEq, Eq)]
pub(crate) struct Root {
    pub pid: u32,
    pub target: String,
    pub status: Status,
}

impl Root {
    /// What follows the target on its line: the log, or the waiter and its file.
    pub(crate) fn detail(&self) -> String {
        match &self.status {
            Status::Tracked(d) | Status::Unwatched(d) => d.clone(),
            Status::Watched(pid, file) => format!("{pid} {file}"),
        }
    }

    /// `judge`'s line.
    pub(crate) fn line(&self) -> String {
        let word = match self.status {
            Status::Tracked(_) => "tracked",
            Status::Watched(..) => "watched",
            Status::Unwatched(_) => "unwatched",
        };
        format!("{} {} {word} {}", self.pid, self.target, self.detail())
    }
}

/// The process table: `/proc`, or a test's stand-in, and the pid of this hook.
pub(crate) struct Procs {
    pub root: PathBuf,
    pub mine: u32,
}

impl Procs {
    pub(crate) fn pids(&self) -> Vec<u32> {
        let mut out: Vec<u32> = std::fs::read_dir(&self.root)
            .map(|d| {
                d.filter_map(Result::ok)
                    .filter_map(|e| e.file_name().to_string_lossy().parse().ok())
                    .collect()
            })
            .unwrap_or_default();
        out.sort_unstable();
        out
    }

    pub(crate) fn read(&self, pid: u32, name: &str) -> String {
        std::fs::read(self.root.join(pid.to_string()).join(name)).map_or_else(
            |_| String::new(),
            |b| String::from_utf8_lossy(&b).into_owned(),
        )
    }

    pub(crate) fn link(&self, pid: u32, name: &str) -> Option<PathBuf> {
        std::fs::read_link(self.root.join(pid.to_string()).join(name)).ok()
    }

    fn comm(&self, pid: u32) -> String {
        self.read(pid, "comm").trim().to_owned()
    }

    fn ppid(&self, pid: u32) -> u32 {
        let stat = self.read(pid, "stat");
        stat.rsplit_once(") ")
            .and_then(|(_, r)| r.split_whitespace().nth(1))
            .and_then(|p| p.parse().ok())
            .unwrap_or(0)
    }

    /// A process's parent, grandparent, ... up to init.
    fn ancestors(&self, pid: u32) -> Vec<u32> {
        let mut out = Vec::new();
        let mut q = self.ppid(pid);
        while q > 1 {
            out.push(q);
            q = self.ppid(q);
        }
        out
    }

    fn stdout_of(&self, pid: u32) -> String {
        self.link(pid, "fd/1")
            .map(|p| p.to_string_lossy().into_owned())
            .unwrap_or_default()
    }

    fn cwd_of(&self, pid: u32) -> PathBuf {
        self.link(pid, "cwd").unwrap_or_else(|| PathBuf::from("/"))
    }

    fn cmdline(&self, pid: u32) -> String {
        self.read(pid, "cmdline").replace('\0', " ")
    }

    /// Whether a live make's cwd lies in this clone, by its NEAREST enclosing tree.
    fn belongs(&self, pid: u32, clone: &Path) -> bool {
        self.link(pid, "cwd")
            .is_some_and(|c| owner(&c).as_deref() == Some(clone))
    }

    /// Each live make run whose cwd is inside the clone: its pid and its target, the first bare word after the make binary.
    pub(crate) fn live_runs(&self, clone: &Path) -> BTreeMap<u32, String> {
        let clone = realpath(clone);
        self.pids()
            .into_iter()
            .filter(|p| {
                matches!(self.comm(*p).as_str(), "make" | "gmake") && self.belongs(*p, &clone)
            })
            .map(|p| {
                let argv = self.read(p, "cmdline");
                let target = argv
                    .split('\0')
                    .skip(1)
                    .find(|a| !a.is_empty() && !a.starts_with('-') && !a.contains('='))
                    .unwrap_or("make");
                (p, target.to_owned())
            })
            .collect()
    }

    /// Every file-watching loop outside this hook's own tree, and the files it names.
    fn loops(&self) -> Vec<(u32, BTreeSet<PathBuf>)> {
        let mut tree = self.ancestors(self.mine);
        tree.push(self.mine);
        self.pids()
            .into_iter()
            .filter(|p| !tree.contains(p))
            .filter_map(|p| {
                let cmd = self.cmdline(p);
                (cmd.contains("sleep") && LOOP.is_match(&cmd).unwrap_or(false))
                    .then(|| (p, files_named(&cmd, &self.cwd_of(p))))
            })
            .collect()
    }

    /// One [`Root`] per root live make, answered from the kernel by pid (feature 246): an ancestor named `claude` is the harness,
    /// which wakes the session at exit; a loop naming the file the make writes is a waiter; neither is the run that can go unread.
    pub(crate) fn judge_runs(&self, clone: &Path) -> Vec<Root> {
        let live = self.live_runs(clone);
        let loops = self.loops();
        let mut out = Vec::new();
        for (&pid, target) in &live {
            let anc = self.ancestors(pid);
            if anc.iter().any(|a| live.contains_key(a)) {
                continue; // a phase child: its root speaks for it
            }
            let status = self.status(pid, &anc, &loops);
            out.push(Root {
                pid,
                target: target.clone(),
                status,
            });
        }
        out
    }

    fn status(&self, pid: u32, anc: &[u32], loops: &[(u32, BTreeSet<PathBuf>)]) -> Status {
        if let Some(tracked) = anc.iter().copied().find(|a| self.comm(*a) == "claude") {
            let shell = anc.iter().copied().find(|a| self.ppid(*a) == tracked);
            return Status::Tracked(
                shell.map_or_else(|| "the harness".to_owned(), |s| self.stdout_of(s)),
            );
        }
        let log = self.stdout_of(pid);
        let mut files = BTreeSet::new();
        add_file(&mut files, &log);
        for a in anc
            .iter()
            .copied()
            .take_while(|a| self.comm(*a) != "claude")
        {
            add_file(&mut files, &self.stdout_of(a));
            files.extend(files_named(&self.cmdline(a), &self.cwd_of(a)));
        }
        for (waiter, named) in loops {
            if let Some(hit) = files.intersection(named).next() {
                return Status::Watched(*waiter, hit.to_string_lossy().into_owned());
            }
        }
        Status::Unwatched(if log.is_empty() {
            "(no file)".to_owned()
        } else {
            log
        })
    }

    /// `<pid> <file>` per waiter loop whose producer is dead, this clone's alone when one is named. A waiter is a loop watching a file;
    /// when the thing writing that file dies, the loop spins for ever (the GM found three in their status line, eight hours old).
    pub(crate) fn stale_waiters(&self, tree: &Path, clone: Option<&Path>) -> Vec<String> {
        let clone = clone.map(realpath);
        let mut ancestry = self.ancestors(self.mine);
        ancestry.push(self.mine);
        let alive = tree.join("scripts/hooks/lib/writer-alive.sh");
        let mut out = Vec::new();
        for p in self.pids().into_iter().filter(|p| !ancestry.contains(p)) {
            let cmd = self.cmdline(p);
            if !(cmd.contains("sleep") && LOOP.is_match(&cmd).unwrap_or(false))
                || clone.as_ref().is_some_and(|c| !self.belongs(p, c))
            {
                continue;
            }
            let mut seen = BTreeSet::new();
            for found in WATCHED_PATH
                .find_iter(&cmd)
                .filter_map(Result::ok)
                .map(|m| m.as_str().to_owned())
            {
                let f = Path::new(&found);
                if !seen.insert(found.clone())
                    || !f.exists()
                    || found.contains("/shell-snapshots/")
                    || runnable(f)
                {
                    continue; // the harness's snapshot is first on every Bash line, and a script is run, never watched
                }
                if !ask(
                    Path::new("/"),
                    "bash",
                    &[&alive.to_string_lossy(), &found],
                    "",
                )
                .ok()
                {
                    out.push(format!("{p} {found}"));
                    break;
                }
            }
        }
        out
    }
}

fn runnable(p: &Path) -> bool {
    std::fs::metadata(p).is_ok_and(|m| m.is_file() && m.permissions().mode() & 0o111 != 0)
}

fn add_file(files: &mut BTreeSet<PathBuf>, path: &str) {
    if path.starts_with('/') && Path::new(path).is_file() {
        files.insert(realpath(Path::new(path)));
    }
}

/// `$X`/`${X}` replaced by what `env` holds, an unknown left as it is.
fn expand(text: &str, env: &HashMap<String, String>) -> String {
    VAR.replace_all(text, |c: &Captures| {
        let name = c.get(1).or_else(|| c.get(2)).map_or("", |m| m.as_str());
        env.get(name).cloned().unwrap_or_else(|| c[0].to_owned())
    })
    .into_owned()
}

/// WHAT A COMMAND LINE NAMES, AS FILES (feature 295 item 1): its simple assignments expanded into their uses, a relative path resolved
/// against the process's cwd, only files counted - a log, written or yet to be, never a directory or an executable.
pub(crate) fn files_named(cmd: &str, base: &Path) -> BTreeSet<PathBuf> {
    let mut env: HashMap<String, String> = ASSIGN
        .captures_iter(cmd)
        .filter_map(Result::ok)
        .map(|c| {
            (
                c[1].to_owned(),
                c[2].trim_matches(|q| q == '"' || q == '\'').to_owned(),
            )
        })
        .collect();
    let mut text = cmd.to_owned();
    for _ in 0..3 {
        text = expand(&text, &env);
        env = env
            .iter()
            .map(|(k, v)| (k.clone(), expand(v, &env)))
            .collect();
    }
    let mut out = BTreeSet::new();
    let split = |c: char| c.is_whitespace() || ";&|()<>\"'=".contains(c);
    for tok in text
        .split(split)
        .filter(|t| t.contains('/') && !t.contains('$'))
    {
        let path = realpath(&base.join(tok));
        if !path.is_dir() && !runnable(&path) && path.parent().is_some_and(Path::is_dir) {
            out.insert(path);
        }
    }
    out
}

#[cfg(test)]
mod tests;
