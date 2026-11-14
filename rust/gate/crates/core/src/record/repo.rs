//! What the record's owed checks read of the repository (feature 449 T87): its git commands, a revision's files in one batch, a file read as Python's `read_text` reads it.

use std::io::Write;
use std::path::Path;
use std::process::{Command, Stdio};

/// A failure the Python would have raised: its uncaught exception, the exit status 1 a port holds.
pub type Fail = String;

/// Any error as the failure it is.
pub fn fail<E: std::fmt::Display>(e: E) -> Fail {
    e.to_string()
}

/// `text.replace` of `\r\n` and `\r` with `\n`, as Python's text mode and `subprocess` `text=True` read.
#[must_use]
pub fn universal(text: &str) -> String {
    text.replace("\r\n", "\n").replace('\r', "\n")
}

/// `git -C root args...`'s stdout, "" unless it succeeded.
pub fn git(root: &Path, args: &[&str]) -> String {
    Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map_or_else(String::new, |o| {
            universal(&String::from_utf8_lossy(&o.stdout))
        })
}

/// `git -C root args...`'s stdout whatever its exit, as `subprocess.run(...).stdout` reads it.
#[must_use]
pub fn git_out(root: &Path, args: &[&str]) -> String {
    Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .output()
        .map(|o| universal(&String::from_utf8_lossy(&o.stdout)))
        .unwrap_or_default()
}

/// `git show rev:path`, or None where the revision has no such file.
#[must_use]
pub fn git_show(root: &Path, rev: &str, path: &str) -> Option<String> {
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["show", &format!("{rev}:{path}")])
        .output()
        .ok()?;
    done.status
        .success()
        .then(|| universal(&String::from_utf8_lossy(&done.stdout)))
}

/// Each object's text (`<rev>:<path>`), by one `git cat-file --batch`; a missing one is empty.
#[must_use]
pub fn cat_blobs(root: &Path, objects: &[String]) -> Vec<String> {
    if objects.is_empty() {
        return Vec::new();
    }
    let input = objects.join("\n") + "\n";
    let data = git_stdin(root, &["cat-file", "--batch"], &input);
    let (mut out, mut i) = (Vec::with_capacity(objects.len()), 0);
    for _ in objects {
        let Some(newline) = data[i..].iter().position(|b| *b == b'\n') else {
            out.push(String::new());
            continue;
        };
        let head = String::from_utf8_lossy(&data[i..i + newline]).into_owned();
        let parts: Vec<&str> = head.split_whitespace().collect();
        let body_at = i + newline + 1;
        if parts.len() < 3 || parts[1] == "missing" {
            out.push(String::new());
            i = body_at;
            continue;
        }
        let size: usize = parts[2].parse().unwrap_or(0);
        let end = (body_at + size).min(data.len());
        out.push(String::from_utf8_lossy(&data[body_at..end]).into_owned());
        i = (end + 1).min(data.len());
    }
    out
}

/// `cmd` fed `input` on its stdin, written beside the read so neither pipe fills.
fn piped(cmd: &mut Command, input: &str) -> std::io::Result<std::process::Output> {
    let mut child = cmd
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()?;
    let (pipe, body) = (child.stdin.take(), input.to_owned());
    let writer = std::thread::spawn(move || pipe.map(|mut p| p.write_all(body.as_bytes())));
    let done = child.wait_with_output();
    let _ = writer.join();
    done
}

/// `git -C root args...` fed `input`; its stdout's bytes, whatever its exit.
fn git_stdin(root: &Path, args: &[&str], input: &str) -> Vec<u8> {
    piped(Command::new("git").arg("-C").arg(root).args(args), input)
        .map(|o| o.stdout)
        .unwrap_or_default()
}

/// `path.read_text(encoding="utf-8")`: `\r\n` and `\r` as `\n`, an unreadable file the failure the Python would raise.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn read_text(path: &Path) -> Result<String, Fail> {
    std::fs::read_to_string(path)
        .map(|t| universal(&t))
        .map_err(|e| format!("{}: {e}", path.display()))
}

/// [`read_text`], or None where `path` is no file.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn read_universal(path: &Path) -> Result<Option<String>, Fail> {
    if path.is_file() {
        read_text(path).map(Some)
    } else {
        Ok(None)
    }
}

/// Runs a Python seam: `python3 -c code args...` fed `input`, its stdout on success and the stderr it wrote on failure.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn python(code: &str, args: &[&str], input: &str) -> Result<String, Fail> {
    let done = piped(
        Command::new("python3").arg("-c").arg(code).args(args),
        input,
    )
    .map_err(fail)?;
    let (out, err) = (
        String::from_utf8_lossy(&done.stdout).into_owned(),
        String::from_utf8_lossy(&done.stderr).into_owned(),
    );
    if done.status.success() {
        Ok(out)
    } else {
        Err(err)
    }
}

/// The tree the scripts live in: where the wrapper said, else the root.
#[cfg(not(test))]
pub fn tree_of(root: &Path) -> std::path::PathBuf {
    std::env::var_os("L7R_GATE_TREE").map_or_else(|| root.to_path_buf(), Into::into)
}

/// The tests' tree: a scratch record carries its own stubs of the Python seams, so a test never runs the real `entry_owed` on it.
#[cfg(test)]
#[must_use]
pub fn tree_of(root: &Path) -> std::path::PathBuf {
    root.to_path_buf()
}

/// The current UTC time as `%Y-%m-%dT%H:%M:%SZ`.
#[must_use]
pub fn utc_now() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, mo, d, h, mi, s) = l7r_guard::shared::log::civil(secs);
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
}

/// The mirror: a clone's grandparent when its parent is `.clones`, else the root itself - the derivation `sync-with-main.sh` uses. One
/// copy (feature 449 T135, `ask:449-phase3-remainder`, FR-003): `make download-add`'s numbers and `make claim`'s both take their lock
/// under it, where each held its own until the claim's port.
#[must_use]
pub fn mirror_of(root: &Path) -> std::path::PathBuf {
    match root.parent() {
        Some(parent) if parent.file_name().is_some_and(|n| n == ".clones") => {
            parent.parent().unwrap_or(root).to_owned()
        }
        _ => root.to_owned(),
    }
}

/// `flock` on the lock file at `path`, polled every 20 ms so a hung holder is a refusal rather than a hang: the open file holding it
/// (the lock lasts as long as it does), or none when `timeout` seconds passed first. Its directory is made, the file opened `0o644`, as
/// `claim-feature.py`'s and `reserve-prefix.py`'s `Lock` did; the one copy of both since feature 449 T135 (FR-003).
///
/// # Errors
///
/// The directory cannot be made or the file opened: what the Python's `mkdir` or `os.open` raised.
pub fn flock_within(path: &Path, timeout: f64) -> Result<Option<std::fs::File>, Fail> {
    use std::os::unix::fs::OpenOptionsExt as _;
    use std::time::{Duration, Instant};
    std::fs::create_dir_all(path.parent().unwrap_or(Path::new("."))).map_err(fail)?;
    let file = std::fs::OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(false)
        .mode(0o644)
        .open(path)
        .map_err(fail)?;
    // `time.monotonic() + timeout`: a negative timeout a deadline already passed; NaN, or one past what an `Instant` holds (infinity), a
    // deadline the Python's comparison never reached
    let deadline = if timeout.is_nan() {
        None
    } else {
        Duration::try_from_secs_f64(timeout.max(0.0))
            .ok()
            .and_then(|d| Instant::now().checked_add(d))
    };
    while !l7r_guard::shared::tool::flock(&file, "-n") {
        if deadline.is_some_and(|d| Instant::now() >= d) {
            return Ok(None);
        }
        std::thread::sleep(Duration::from_millis(20));
    }
    Ok(Some(file))
}

#[cfg(test)]
mod tests;
