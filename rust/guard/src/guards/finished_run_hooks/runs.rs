//! What runs and who waits: every fact read from `/proc` by pid, never by a pattern over this hook's own command line, which is the
//! 2026-07-25 defect (`pgrep -f "make done"` found the searching shell and looped for 10.9 minutes).

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::os::unix::fs::PermissionsExt;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};

use crate::shared::tool::ask;
pub(crate) use crate::shared::tree::realpath;

static LOOP: LazyLock<Regex> = LazyLock::new(|| {
    crate::shared::regex::build(r"(?m:^)(?>.*?\b(until|while)\b).*\bgrep\b")
        .unwrap_or_else(|e| unreachable!("{e}"))
});
static ASSIGN: LazyLock<Regex> = LazyLock::new(|| {
    crate::shared::regex::build(r#"(?:^|[\s;&|(])([A-Za-z_]\w*)=("[^"]*"|'[^']*'|[^\s;&|)]*)"#)
        .unwrap_or_else(|e| unreachable!("{e}"))
});
static VAR: LazyLock<Regex> = LazyLock::new(|| {
    crate::shared::regex::build(r"\$\{([A-Za-z_]\w*)\}|\$([A-Za-z_]\w*)")
        .unwrap_or_else(|e| unreachable!("{e}"))
});
static WATCHED_PATH: LazyLock<Regex> = LazyLock::new(|| {
    crate::shared::regex::build(r"(?:/[\w.-]+)+\.\w+").unwrap_or_else(|e| unreachable!("{e}"))
});

/// A redirection or a `tee` into a file, its target the capture (451 T61): `>`, `>>`, `>|`, `&>` and `2>>` all end in the `>` matched
/// here; a descriptor's copy (`2>&1`, `>&2`) and a process substitution (`>(...)`) capture nothing; and a run of quotes before the
/// target is skipped, since the harness's `eval '...'` writes a quoted path as `'"'"'/a/f'"'"'`.
static INTO: LazyLock<Regex> = LazyLock::new(|| {
    crate::shared::regex::build(r#"(?:>>?\|?|\btee\s+(?:-\S+\s+)*)\s*["']*([^\s;&|()<>"']+)"#)
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// A process that only reads - a `tail -f` (the Monitor tool's shape), a `grep` - runs no script: its argument is the file it reads,
/// whose text may itself write the file asked about (a run's log echoing its recipe, `... >> sum.txt`), so it is not read as one.
const READERS: &[&str] = &[
    "grep",
    "egrep",
    "fgrep",
    "rg",
    "tail",
    "head",
    "cat",
    "less",
    "more",
    "wc",
    "stat",
    "ls",
    "sleep",
    "inotifywait",
];
/// A file larger than this is no script a run was started with (an interpreter's binary, a data file), so it is not read
/// (GUESS, a knob: the largest of the repository's own scripts is 48,086 bytes, `scripts/sync-with-main.sh`, measured 2026-11-21
/// (`find scripts -name '*.sh' -printf '%s %p\n' | sort -n`), so five times that reads every script a session writes).
const SCRIPT_BYTES: u64 = 256 * 1024;

/// Whether a command line, or a script's text, is a waiter: a loop that sleeps on a grep, the shape [`Procs::loops`] counts.
fn waits(text: &str) -> bool {
    text.contains("sleep") && LOOP.is_match(text).unwrap_or(false)
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

    /// WHO RUNS A QUIET FILE (feature 451 T61): the first live process outside this one's own ancestry that WRITES `file` - a
    /// redirection or a `tee` into it on its command line, or in the text of a script it was started with - as `<pid> <how>`, or
    /// None. A run that appends a line between its steps (`for c in a b; do make $c > $c.log; echo "$c rc=$?" >> sum.txt; done`)
    /// holds the summary open only for each echo, so nothing holds it between steps and it ages unwritten while the run goes on:
    /// `writer-alive.sh` called it gone (2026-11-21, T55's builder: `until grep -q ^total seq.times` ended at 55 s, exit 3, while its
    /// run ran; 8 of the 11 firings whose wait's output was still on disk were followed by a write to the file). The run's process is
    /// what it asks, never the file's growth. A waiter, with its children (its `grep`), names the file and is set aside; a reader -
    /// the Monitor tool's `tail -f f | grep`, a file-test wait `until [ -s f ]` - names it too, inside the harness's `bash -c` wrapper,
    /// so naming is no proof: counted, each held a dead run's wait to its 90-minute ceiling. Only a write is.
    pub(crate) fn runner_of(&self, file: &Path) -> Option<String> {
        let file = realpath(file);
        let mut skip: BTreeSet<u32> = self.ancestors(self.mine).into_iter().collect();
        skip.insert(self.mine);
        let pids = self.pids();
        let parent: HashMap<u32, u32> = pids.iter().map(|p| (*p, self.ppid(*p))).collect();
        let waiter: BTreeSet<u32> = pids
            .iter()
            .copied()
            .filter(|p| waits(&self.cmdline(*p)))
            .collect();
        let under_a_waiter = |p: u32| {
            let mut q = p;
            // bounded: a stand-in table can loop where the kernel's cannot
            for _ in 0..64 {
                if waiter.contains(&q) {
                    return true;
                }
                match parent.get(&q) {
                    Some(&up) if up > 1 => q = up,
                    _ => return false,
                }
            }
            false
        };
        for p in pids {
            if skip.contains(&p) || under_a_waiter(p) || READERS.contains(&self.comm(p).as_str()) {
                continue;
            }
            let cwd = self.cwd_of(p);
            if written(&self.cmdline(p), &cwd).contains(&file) {
                return Some(format!("{p} writes it"));
            }
            for arg in self.read(p, "cmdline").split('\0').skip(1) {
                let script = realpath(&cwd.join(arg));
                if !std::fs::metadata(&script).is_ok_and(|m| m.is_file() && m.len() <= SCRIPT_BYTES)
                {
                    continue;
                }
                let text = std::fs::read_to_string(&script).unwrap_or_default();
                if !waits(&text) && written(&text, &cwd).contains(&file) {
                    return Some(format!("{p} runs {} which writes it", script.display()));
                }
            }
        }
        None
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
                .map_while(Result::ok)
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

/// A command line's text with its simple assignments (`S=/a; L=$S/b.log`) expanded into their uses, three rounds deep, so an
/// assignment built from another resolves; an unknown is left as it is.
fn expanded(cmd: &str) -> String {
    let mut env: HashMap<String, String> = ASSIGN
        .captures_iter(cmd)
        .map_while(Result::ok)
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
    text
}

/// WHAT A COMMAND LINE NAMES, AS FILES (feature 295 item 1): its simple assignments expanded into their uses, a relative path resolved
/// against the process's cwd, only files counted - a log, written or yet to be, never a directory or an executable.
pub(crate) fn files_named(cmd: &str, base: &Path) -> BTreeSet<PathBuf> {
    let text = expanded(cmd);
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

/// WHAT A COMMAND LINE, OR A SCRIPT'S TEXT, WRITES (451 T61): the target of each redirection or `tee` ([`INTO`]), its simple
/// assignments expanded first, a relative target resolved against `base`; a target still holding a `$` (a loop's variable, a
/// substitution) names no file.
pub(crate) fn written(text: &str, base: &Path) -> BTreeSet<PathBuf> {
    INTO.captures_iter(&expanded(text))
        .map_while(Result::ok)
        .map(|c| c[1].to_owned())
        .filter(|t| !t.contains('$'))
        .map(|t| realpath(&base.join(t)))
        .collect()
}

#[cfg(test)]
mod tests;
