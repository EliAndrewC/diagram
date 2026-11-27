//! Asking a tool the guards consult (plan T006 decision (a)): a program run in a directory, its stdin given, its exit code and its
//! stdout and stderr kept - the shell's `$(...)`, which strips the trailing newlines, and its `$?`. A program that cannot start
//! answers -1 with nothing, as a guard's `2>/dev/null || true` did; `ask_started` says why it could not (451 T268).

use std::fs::File;
use std::io::{Read, Write};
use std::os::unix::process::CommandExt;
use std::path::Path;
use std::process::{Command, Stdio};
use std::time::{Duration, Instant};

/// What a tool answered.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Said {
    pub code: i32,
    pub out: String,
    pub err: String,
}

impl Said {
    /// Its exit was 0.
    #[must_use]
    pub fn ok(&self) -> bool {
        self.code == 0
    }
}

/// `program`, as every asker here starts it: with `GIT_OPTIONAL_LOCKS=0`, so that a `git status` a guard asks - and one the script
/// or gate it asks runs in turn - only READS the index. WHY (451 T304): `git status` takes `<git dir>/index.lock` for as long as it
/// refreshes the index, to write the refreshed stat data back, and a `git add` or `git commit` that meets the lock dies ("Unable
/// to create ... index.lock: File exists"). The guards ask `git -C <the session clone> status --porcelain` from every agent's calls
/// (`clone_sync_hooks`' `dirty`, on each Bash call naming `make`), so three builders' hooks met the session's own commits three
/// times on 2026-11-26; in a clone of this repository, three loops of that status beside 200 rounds of add and commit refused 190
/// of them, and 0 with the variable. A lock a command NEEDS (an add, a commit, a merge) is still taken: the variable names only
/// the optional ones. NOT covered: `git diff` against the work tree, which in git 2.53 writes its refresh back whatever the
/// variable says, where a file's stat data is stale and its content unchanged (142 of 200 rounds refused with it, 154 without),
/// and `git add --dry-run`, which takes the lock on every call and dies where it is held: those reads go through
/// [`ask_git_private`] (451 T446). The guards' direct `Command::new("git")` calls refresh no index (`rev-parse`, `for-each-ref`, a
/// tree-to-tree diff).
fn command(program: &str) -> Command {
    let mut asked = Command::new(program);
    asked.env("GIT_OPTIONAL_LOCKS", "0");
    asked
}

/// Run `program args` in `dir`, `stdin` written to it.
#[must_use]
pub fn ask(dir: &Path, program: &str, args: &[&str], stdin: &str) -> Said {
    ask_started(dir, program, args, stdin).unwrap_or(Said {
        code: -1,
        ..Said::default()
    })
}

/// `git -C <repo> <args>` run from `dir` on a private copy of the repository's index (`GIT_INDEX_FILE`), so the read takes no
/// `index.lock` of the tree's own and leaves its index as it was; the answer is the plain call's. WHY (451 T446): a work-tree
/// `git diff` writes its refresh back whatever `GIT_OPTIONAL_LOCKS` says where a file's stat data is stale, and `git add
/// --dry-run` takes the lock on every call and dies where another holds it (measured 2026-11-27 in a scratch repository: both
/// wrote or refused, `diff.autoRefreshIndex=false`, `diff-index` and `diff-files` each listed the stale file, and the copy's
/// answers matched the plain ones for a stale, a modified, a staged, a deleted and an untracked file in a linked worktree). The
/// copy keeps the index's mtime, which git's racy-entry test reads. Where no index can be copied (none yet, no repository) the
/// plain call answers: there is then no lock of the tree's for it to meet. A copy of the session clone's 3.7 MB index cost
/// 8.5 ms (20 copies, 2026-11-27).
#[must_use]
pub fn ask_git_private(dir: &Path, repo: &str, args: &[&str]) -> Said {
    let index = ask(
        dir,
        "git",
        &[
            "-C",
            repo,
            "rev-parse",
            "--path-format=absolute",
            "--git-path",
            "index",
        ],
        "",
    )
    .out;
    let scratch = crate::tempdir::TempDir::new("private-index");
    let copy = scratch.path().join("index");
    let mut all = vec!["-C", repo];
    all.extend_from_slice(args);
    let mut git = command("git");
    if copied(Path::new(&index), &copy) {
        git.env("GIT_INDEX_FILE", &copy);
    }
    asked(git, dir, &all, "").unwrap_or(Said {
        code: -1,
        ..Said::default()
    })
}

/// `from` copied to `to` with its mtime kept; false where any step failed.
fn copied(from: &Path, to: &Path) -> bool {
    let kept = std::fs::metadata(from).and_then(|m| m.modified());
    kept.and_then(|t| {
        std::fs::copy(from, to)?;
        File::options().write(true).open(to)?.set_modified(t)
    })
    .is_ok()
}

/// [`ask`], for a caller that tells a program that could not START from one that ran and failed (451 T268): `ask` answers both -1
/// with nothing, so the clone-sync notice of a sync script the kernel refused to run ("Text file busy", T263) ended `FAILED: ` with
/// no reason after it. A code of -1 with no output is not the test for it: a program a signal killed answers the same.
///
/// # Errors
///
/// The program could not be started: what the spawn said (a missing file, one not executable, one open for writing).
pub fn ask_started(dir: &Path, program: &str, args: &[&str], stdin: &str) -> std::io::Result<Said> {
    asked(command(program), dir, args, stdin)
}

thread_local! {
    /// The gate launcher whose call in this process exited 0, and the binary it runs (451 T494).
    static GATE_FRESH: std::cell::RefCell<Option<(std::path::PathBuf, std::path::PathBuf)>> = const { std::cell::RefCell::new(None) };
}

/// `bash <script> <args>`: a tree's gate launcher (`scripts/gates/l7r-gate.sh`) run by `bash`, not by its `#!/usr/bin/env bash`,
/// whose `env` start cost 2.5 ms a call (451 T494, as 451 T456 took it out of `l7r-hook`). AND ITS SOURCE WALK ONCE A PROCESS: the
/// launcher's `stale()` find over `rust/gate` and `rust/guard` (1,859 paths, 17.5 ms a call in T388's sandbox) runs before every
/// call. A call of a plain subcommand that exited 0 means the launcher ran its binary, so that binary was fresh then or was built:
/// its every failure to build exits 1 before the `exec`, and a stale binary it runs anyway (`L7R_GATE_STALE_OK`, an
/// `L7R_GATE_FRESH` already exported) runs for the later call too, under the same environment. So a later call through the same
/// launcher in this process passes `L7R_GATE_FRESH=<that binary>` (449 T205's seam), which the launcher honors only where it names
/// its own binary and that binary is executable - a binary named wrongly here walks as before. The first call always walks. Not a
/// kept stamp (`l7r-guard.sh`'s 451 T439 note says why none can stand for a walk): the proof lasts one hook process, tens of ms, so
/// a source edited inside that window is missed by the later call as it would be by a call started that much earlier. A variant
/// (`rust`, `browser`, `embed`, `mode-a`, `hamlet`) runs another binary from other sources and is neither proof nor proved.
#[must_use]
pub fn ask_gate(dir: &Path, script: &Path, args: &[&str], stdin: &str) -> Said {
    gate_asked(script, args, |bash, all| {
        asked(bash, dir, all, stdin).unwrap_or(Said {
            code: -1,
            ..Said::default()
        })
    })
}

/// [`ask_gate`] with no stdin and a limit, as [`ask_within`] asks a program (451 T500: the gate-write guard's tree check). A call
/// killed at its limit answers -1 and proves nothing.
#[must_use]
pub fn ask_gate_within(dir: &Path, script: &Path, args: &[&str], limit: Duration) -> Said {
    gate_asked(script, args, |bash, all| said_within(bash, dir, all, limit))
}

/// The gate launcher's call made by `run` (the `bash` command and its arguments), its freshness proof passed and kept as
/// [`ask_gate`] says.
fn gate_asked(script: &Path, args: &[&str], run: impl FnOnce(Command, &[&str]) -> Said) -> Said {
    let plain = !matches!(
        args.first().copied(),
        Some("rust" | "browser" | "embed" | "mode-a" | "hamlet")
    );
    let mut bash = command("bash");
    let exported = !crate::env::opt("L7R_GATE_FRESH")
        .unwrap_or_default()
        .is_empty();
    let known = GATE_FRESH.with(|f| f.borrow().clone());
    if let Some((_, bin)) = known.filter(|(s, _)| plain && !exported && s == script) {
        bash.env("L7R_GATE_FRESH", bin);
    }
    let s = script.to_string_lossy();
    let all: Vec<&str> = std::iter::once(s.as_ref())
        .chain(args.iter().copied())
        .collect();
    let said = run(bash, &all);
    if let Some(bin) = gate_binary(script).filter(|_| plain && said.ok()) {
        GATE_FRESH.with(|f| *f.borrow_mut() = Some((script.to_path_buf(), bin)));
    }
    said
}

/// The binary `script`, a tree's `scripts/gates/l7r-gate.sh` named by its absolute path, runs for a plain subcommand, as the launcher
/// names it: `${L7R_GATE_TARGET:-<the account's home in /etc/passwd>/.cache/l7r-cargo-target/<the tree's name>}/tool/l7r-gate`.
fn gate_binary(script: &Path) -> Option<std::path::PathBuf> {
    let tree = script
        .parent()?
        .parent()?
        .parent()
        .filter(|_| script.is_absolute())?;
    let target = match crate::env::opt("L7R_GATE_TARGET").filter(|t| !t.is_empty()) {
        Some(t) => std::path::PathBuf::from(t),
        None => account_home()?
            .join(".cache/l7r-cargo-target")
            .join(tree.file_name()?),
    };
    Some(target.join("tool/l7r-gate"))
}

/// The account's home as `/etc/passwd` holds it for this process's user, which the launcher reads in place of `HOME` (a fixture may
/// set that).
fn account_home() -> Option<std::path::PathBuf> {
    use std::os::unix::fs::MetadataExt;
    let uid = std::fs::metadata("/proc/self").ok()?.uid().to_string();
    let passwd = std::fs::read_to_string("/etc/passwd").ok()?;
    let row = passwd
        .lines()
        .map(|l| l.split(':').collect::<Vec<_>>())
        .find(|f| f.get(2) == Some(&uid.as_str()))?;
    row.get(5).map(std::path::PathBuf::from)
}

/// [`ask_started`] for a command already made, its environment set.
fn asked(mut program: Command, dir: &Path, args: &[&str], stdin: &str) -> std::io::Result<Said> {
    let mut child = program
        .args(args)
        .current_dir(dir)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()?;
    if let Some(mut pipe) = child.stdin.take() {
        let _ = pipe.write_all(stdin.as_bytes());
    }
    let text = |b: &[u8]| String::from_utf8_lossy(b).trim_end_matches('\n').to_owned();
    Ok(child.wait_with_output().map_or(
        Said {
            code: -1,
            ..Said::default()
        },
        |done| Said {
            code: done.status.code().unwrap_or(-1),
            out: text(&done.stdout),
            err: text(&done.stderr),
        },
    ))
}

/// Whether `program args`, run quiet in `dir`, exits 0 within `limit` - `timeout <limit> program args >/dev/null 2>&1`, its own
/// process group sent TERM at the limit as `timeout` sends it, without `timeout`'s own start (106 ms a call against 1 ms, measured
/// 2026-11-08 on `sh -c 'exit 1'`, five runs each; T013).
#[must_use]
pub fn within(dir: &Path, program: &str, args: &[&str], limit: Duration) -> bool {
    let Ok(mut child) = command(program)
        .args(args)
        .current_dir(dir)
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .process_group(0)
        .spawn()
    else {
        return false;
    };
    let start = Instant::now();
    loop {
        if let Ok(Some(done)) = child.try_wait() {
            return done.success();
        }
        if start.elapsed() >= limit {
            let _ = ask(
                dir,
                "kill",
                &["-TERM", "--", &format!("-{}", child.id())],
                "",
            );
            let _ = child.wait();
            return false;
        }
        std::thread::sleep(Duration::from_millis(1));
    }
}

/// [`ask`] with no stdin and a limit, past which the program is killed and what it said so far is its answer, its code -1
/// (`subprocess.run(timeout=)`'s use here, without coreutils `timeout`'s 100 ms a call, measured in T013).
#[must_use]
pub fn ask_within(dir: &Path, program: &str, args: &[&str], limit: Duration) -> Said {
    said_within(command(program), dir, args, limit)
}

/// [`ask_within`] for a command already made, its environment set.
fn said_within(mut program: Command, dir: &Path, args: &[&str], limit: Duration) -> Said {
    let Ok(mut child) = program
        .args(args)
        .current_dir(dir)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
    else {
        return Said {
            code: -1,
            ..Said::default()
        };
    };
    let out = collect(child.stdout.take());
    let err = collect(child.stderr.take());
    let start = Instant::now();
    let code = loop {
        if let Ok(Some(done)) = child.try_wait() {
            break done.code().unwrap_or(-1);
        }
        if start.elapsed() >= limit {
            let _ = child.kill();
            let _ = child.wait();
            break -1;
        }
        std::thread::sleep(Duration::from_millis(1));
    };
    Said {
        code,
        out: out.join().unwrap_or_default(),
        err: err.join().unwrap_or_default(),
    }
}

/// A pipe read to its end on a thread of its own, so that a full pipe cannot stall the wait on its writer.
fn collect<P: Read + Send + 'static>(pipe: Option<P>) -> std::thread::JoinHandle<String> {
    std::thread::spawn(move || {
        let mut out = Vec::new();
        if let Some(mut p) = pipe {
            let _ = p.read_to_end(&mut out);
        }
        String::from_utf8_lossy(&out)
            .trim_end_matches('\n')
            .to_owned()
    })
}

/// `flock <mode> 0` on an open file handed over as stdin: the lock belongs to that open file, which the caller holds, as a shell's
/// fd 9 did (`File::try_lock` is past this toolchain, T014 decision (b)).
#[must_use]
pub fn flock(lock: &File, mode: &str) -> bool {
    lock.try_clone().is_ok_and(|f| {
        Command::new("flock")
            .args([mode, "0"])
            .stdin(f)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status()
            .is_ok_and(|s| s.success())
    })
}

/// `flock` on the lock file at `path`, polled every 20 ms so a hung holder is a refusal rather than a hang: the open file holding it
/// (the lock lasts as long as it does), or none when `timeout` seconds passed first. Its directory is made, the file opened `0o644`, as
/// `claim-feature.py`'s, `reserve-prefix.py`'s and `sources.py`'s locks did; moved here from the gate's `core::record::repo` by feature
/// 449 T145, so the attempts log the blocked-fetch guard writes in process takes the same lock (one copy, FR-003).
///
/// # Errors
///
/// The directory cannot be made or the file opened: what the Python's `mkdir` or `os.open` raised.
pub fn flock_within(path: &Path, timeout: f64) -> std::io::Result<Option<File>> {
    use std::os::unix::fs::OpenOptionsExt as _;
    use std::time::Instant;
    std::fs::create_dir_all(path.parent().unwrap_or(Path::new(".")))?;
    let file = std::fs::OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(false)
        .mode(0o644)
        .open(path)?;
    // `time.monotonic() + timeout`: a negative timeout a deadline already passed; NaN, or one past what an `Instant` holds (infinity), a
    // deadline the Python's comparison never reached
    let deadline = if timeout.is_nan() {
        None
    } else {
        Duration::try_from_secs_f64(timeout.max(0.0))
            .ok()
            .and_then(|d| Instant::now().checked_add(d))
    };
    while !flock(&file, "-n") {
        if deadline.is_some_and(|d| Instant::now() >= d) {
            return Ok(None);
        }
        std::thread::sleep(Duration::from_millis(20));
    }
    Ok(Some(file))
}

/// `file`'s mtime moved to 2001 with its content kept, so the index's stat data for it goes stale: the case in which a work-tree
/// `git diff` writes its refresh back (451 T446's fixtures).
///
/// # Panics
///
/// Where `file` cannot be opened or its mtime set: the fixture would prove nothing.
#[cfg(any(test, feature = "test-env"))]
pub fn stale(file: &Path) {
    let old = std::time::SystemTime::UNIX_EPOCH + Duration::from_secs(1_000_000_000);
    let set = File::options()
        .write(true)
        .open(file)
        .and_then(|f| f.set_modified(old));
    assert!(set.is_ok(), "{} could not be made stale", file.display());
}

#[cfg(test)]
mod tests {
    use std::fs::File;
    use std::path::Path;
    use std::process::Command;
    use std::time::Duration;

    use super::{
        ask, ask_gate, ask_gate_within, ask_git_private, ask_started, ask_within, gate_binary,
        stale, within,
    };

    #[test]
    fn a_git_read_on_a_private_index_leaves_the_index_and_meets_no_lock() {
        let dir = crate::tempdir::TempDir::new("tool-private-index");
        let repo = dir.path();
        let at = repo.to_string_lossy();
        let index = || std::fs::read(repo.join(".git/index")).unwrap();
        let git = |args: &[&str]| ask(repo, "git", args, "");
        assert!(git(&["init", "-q"]).ok());
        std::fs::write(repo.join("a"), "a\n").unwrap();
        // no index yet: the plain call answers
        assert_eq!(
            ask_git_private(repo, &at, &["status", "--porcelain"]).out,
            "?? a"
        );
        std::fs::write(repo.join("b"), "b\n").unwrap();
        assert!(git(&["add", "a", "b"]).ok());
        std::fs::write(repo.join("b"), "b2\n").unwrap();
        stale(&repo.join("a"));
        let before = index();
        let dry = ["add", "--dry-run", "--ignore-missing", "."];
        std::fs::write(repo.join(".git/index.lock"), "").unwrap();
        assert_eq!(git(&dry).code, 128);
        assert_eq!(ask_git_private(repo, &at, &dry).out, "add 'b'");
        std::fs::remove_file(repo.join(".git/index.lock")).unwrap();
        assert_eq!(
            ask_git_private(repo, &at, &["diff", "--name-only"]).out,
            "b"
        );
        assert!(index() == before, "a private read rewrote the index");
        // the fixture does go stale: the plain diff rewrites this index
        assert_eq!(git(&["diff", "--name-only"]).out, "b");
        assert!(index() != before, "the fixture's index was never stale");
        assert_ne!(
            ask_git_private(Path::new("/"), "/no/such/repo", &["status"]).code,
            0
        );
    }

    /// RED FIRST (451 T304): with a bare `Command::new`, each asker's `git status` rewrites the index it refreshed - under
    /// `index.lock`, which a commit beside it dies on. The file is rewritten with its own content and another mtime, so the index's
    /// stat data for it is stale and a status that may lock writes it back.
    #[test]
    fn a_git_asked_takes_no_optional_lock_so_a_status_leaves_the_index_as_it_was() {
        let dir = crate::tempdir::TempDir::new("tool-optional-locks");
        let repo = dir.path();
        let limit = Duration::from_secs(30);
        let index = || std::fs::read(repo.join(".git/index")).unwrap();
        assert!(ask(repo, "git", &["init", "-q"], "").ok());
        std::fs::write(repo.join("a"), "a\n").unwrap();
        assert!(ask(repo, "git", &["add", "a"], "").ok());
        let before = index();
        let old = std::time::SystemTime::UNIX_EPOCH + Duration::from_secs(1_000_000_000);
        std::fs::File::options()
            .write(true)
            .open(repo.join("a"))
            .unwrap()
            .set_modified(old)
            .unwrap();
        let status = ["status", "--porcelain"];
        assert_eq!(ask(repo, "git", &status, "").out, "A  a");
        assert_eq!(ask_within(repo, "git", &status, limit).out, "A  a");
        assert!(within(repo, "git", &status, limit));
        assert!(index() == before, "a status asked here rewrote the index");
        // the fixture does go stale: a status that may lock rewrites this index
        let bare = std::process::Command::new("git")
            .args(status)
            .current_dir(repo)
            .env_remove("GIT_OPTIONAL_LOCKS")
            .output()
            .unwrap();
        assert!(bare.status.success());
        assert!(index() != before, "the fixture's index was never stale");
    }

    #[test]
    fn a_tool_asked_within_a_limit_answers_or_is_killed() {
        let limit = Duration::from_secs(5);
        let said = ask_within(
            Path::new("/"),
            "sh",
            &["-c", "echo out; echo err >&2; exit 3"],
            limit,
        );
        assert_eq!(
            (said.code, said.out.as_str(), said.err.as_str()),
            (3, "out", "err")
        );
        assert_eq!(
            ask_within(Path::new("/"), "/no/such/program", &[], limit).code,
            -1
        );
        assert_eq!(
            ask_within(Path::new("/"), "sleep", &["5"], Duration::from_millis(5)).code,
            -1
        );
    }

    #[test]
    fn a_quiet_tool_is_given_its_limit_and_no_more() {
        let limit = Duration::from_secs(5);
        assert!(within(Path::new("/"), "true", &[], limit));
        assert!(!within(Path::new("/"), "false", &[], limit));
        assert!(!within(Path::new("/"), "/no/such/program", &[], limit));
        assert!(!within(
            Path::new("/"),
            "sleep",
            &["5"],
            Duration::from_millis(20)
        ));
    }

    #[test]
    fn a_tool_answers_its_code_and_output_and_one_that_cannot_start_answers_nothing() {
        let said = ask(
            Path::new("/"),
            "sh",
            &["-c", "cat; echo err >&2; exit 3"],
            "in\n\n",
        );
        assert_eq!(
            (said.code, said.out.as_str(), said.err.as_str(), said.ok()),
            (3, "in", "err", false)
        );
        assert!(ask(Path::new("/"), "true", &[], "").ok());
        assert_eq!(ask(Path::new("/"), "/no/such/program", &[], "").code, -1);
    }

    #[test]
    fn a_tool_that_cannot_start_says_why_and_one_that_ran_answers_as_asked() {
        let why = ask_started(Path::new("/"), "/no/such/program", &[], "").unwrap_err();
        assert_eq!(why.to_string(), "No such file or directory (os error 2)");
        // not executable: the refusal is the exec's, as "Text file busy" is
        assert_eq!(
            ask_started(Path::new("/"), "/etc/hostname", &[], "")
                .unwrap_err()
                .kind(),
            std::io::ErrorKind::PermissionDenied
        );
        let ran = ask_started(Path::new("/"), "sh", &["-c", "cat; exit 3"], "in").unwrap();
        assert_eq!((ran.code, ran.out.as_str()), (3, "in"));
    }

    /// A tree's gate launcher stub at `<d>/<tree>/scripts/gates/l7r-gate.sh` saying the `L7R_GATE_FRESH` it was given and its
    /// first word, and failing on `fail`; not executable, as `bash` needs it not to be.
    fn stub_gate(d: &Path, tree: &str) -> std::path::PathBuf {
        let script = d.join(tree).join("scripts/gates/l7r-gate.sh");
        std::fs::create_dir_all(script.parent().unwrap()).unwrap();
        std::fs::write(
            &script,
            "echo \"fresh=${L7R_GATE_FRESH:-} $1\"; [ \"$1\" != fail ]\n",
        )
        .unwrap();
        script
    }

    /// 451 T494: the launcher is run by bash, and after a plain call through it exits 0 the later calls in this process are told
    /// its binary is fresh; a variant, another launcher, a failed call and an exported `L7R_GATE_FRESH` are not.
    #[test]
    fn a_gate_call_after_one_that_exited_0_skips_the_launcher_s_walk() {
        let d = crate::tempdir::TempDir::new("ask-gate");
        let (a, b) = (stub_gate(d.path(), "a"), stub_gate(d.path(), "b"));
        crate::env::set("L7R_GATE_TARGET", "/t");
        let base = std::env::var("L7R_GATE_FRESH").unwrap_or_default();
        let said = |s: &Path, w: &str| ask_gate(d.path(), s, &[w, "x"], "").out;
        assert_eq!(said(&b, "fail"), format!("fresh={base} fail"));
        assert_eq!(said(&b, "plan"), format!("fresh={base} plan"));
        assert_eq!(said(&b, "plan"), "fresh=/t/tool/l7r-gate plan");
        assert_eq!(said(&b, "rust"), format!("fresh={base} rust"));
        assert_eq!(said(&b, "fail"), "fresh=/t/tool/l7r-gate fail");
        assert_eq!(said(&a, "plan"), format!("fresh={base} plan"));
        assert_eq!(said(&a, "plan"), "fresh=/t/tool/l7r-gate plan");
        assert_eq!(said(&b, "plan"), format!("fresh={base} plan"));
        crate::env::set("L7R_GATE_FRESH", "/elsewhere");
        assert_eq!(said(&b, "plan"), format!("fresh={base} plan"));
        crate::env::unset("L7R_GATE_FRESH");
        assert_eq!(
            ask_gate(d.path(), Path::new("/no/such.sh"), &["plan"], "").code,
            127
        );
    }

    /// 451 T500: the bounded asker runs the launcher by bash and shares the same proof both ways; a call killed at its limit
    /// answers -1, a script that cannot start 127.
    #[test]
    fn a_bounded_gate_call_shares_the_walk_and_stops_at_its_limit() {
        let d = crate::tempdir::TempDir::new("ask-gate-within");
        let a = stub_gate(d.path(), "a");
        std::fs::write(
            &a,
            "[ \"$1\" = sleep ] && exec sleep 5; echo \"fresh=${L7R_GATE_FRESH:-} $1\"\n",
        )
        .unwrap();
        crate::env::set("L7R_GATE_TARGET", "/t");
        let base = std::env::var("L7R_GATE_FRESH").unwrap_or_default();
        let limit = Duration::from_secs(5);
        let within = |w: &str, l: Duration| ask_gate_within(d.path(), &a, &[w], l);
        let slept = within("sleep", Duration::from_millis(100));
        assert_eq!((slept.code, slept.out.as_str()), (-1, ""));
        assert_eq!(within("plan", limit).out, format!("fresh={base} plan"));
        assert_eq!(within("plan", limit).out, "fresh=/t/tool/l7r-gate plan");
        assert_eq!(
            ask_gate(d.path(), &a, &["plan"], "").out,
            "fresh=/t/tool/l7r-gate plan"
        );
        assert_eq!(
            ask_gate_within(d.path(), Path::new("/no/such.sh"), &["plan"], limit).code,
            127
        );
    }

    /// The binary named is the launcher's: its `L7R_GATE_PRINT_FRESH` answer under a target, its own text for the default target, and
    /// none for a launcher named by a relative path (the launcher resolves that, and a name it would not give is never wrong, only
    /// slower).
    #[test]
    fn the_gate_binary_named_is_the_one_the_launcher_runs() {
        let d = crate::tempdir::TempDir::new("gate-binary");
        let launcher = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("../../../scripts/gates/l7r-gate.sh")
            .canonicalize()
            .unwrap();
        let bin = d.path().join("tool/l7r-gate");
        std::fs::create_dir_all(bin.parent().unwrap()).unwrap();
        std::fs::write(&bin, "").unwrap();
        let later = std::time::SystemTime::now() + Duration::from_secs(86_400);
        File::options()
            .write(true)
            .open(&bin)
            .unwrap()
            .set_modified(later)
            .unwrap();
        std::fs::set_permissions(&bin, std::os::unix::fs::PermissionsExt::from_mode(0o755))
            .unwrap();
        crate::env::set("L7R_GATE_TARGET", d.path());
        let printed = Command::new("bash")
            .arg(&launcher)
            .env("L7R_GATE_TARGET", d.path())
            .env("L7R_GATE_PRINT_FRESH", "1")
            .env("L7R_GATE_CARGO", "/bin/false")
            .env_remove("L7R_GATE_FRESH")
            .output()
            .unwrap();
        let printed = String::from_utf8_lossy(&printed.stdout).trim().to_owned();
        assert_eq!(
            gate_binary(&launcher),
            Some(std::path::PathBuf::from(printed))
        );
        crate::env::unset("L7R_GATE_TARGET");
        let text = std::fs::read_to_string(&launcher).unwrap();
        assert!(
            text.contains("TARGET=${L7R_GATE_TARGET:-$real/.cache/l7r-cargo-target/${TREE##*/}}")
                && text.contains("BIN=\"$TARGET/tool/l7r-gate\"")
        );
        let home = ask(
            Path::new("/"),
            "sh",
            &["-c", "getent passwd \"$(id -u)\" | cut -d: -f6"],
            "",
        )
        .out;
        let tree = launcher
            .parent()
            .unwrap()
            .parent()
            .unwrap()
            .parent()
            .unwrap();
        let default = Path::new(&home)
            .join(".cache/l7r-cargo-target")
            .join(tree.file_name().unwrap())
            .join("tool/l7r-gate");
        assert_eq!(gate_binary(&launcher), Some(default));
        assert_eq!(gate_binary(Path::new("scripts/gates/l7r-gate.sh")), None);
    }
}
