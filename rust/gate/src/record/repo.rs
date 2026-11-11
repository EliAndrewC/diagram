//! What the record's owed checks read of the repository (feature 449 T87): its git commands, a revision's files in one batch, a file read as Python's `read_text` reads it.

use std::io::Write;
use std::path::Path;
use std::process::{Command, Stdio};

/// A failure the Python would have raised: its uncaught exception, the exit status 1 a port holds.
pub(crate) type Fail = String;

/// `text.replace` of `\r\n` and `\r` with `\n`, as Python's text mode and `subprocess` `text=True` read.
pub(crate) fn universal(text: &str) -> String {
    text.replace("\r\n", "\n").replace('\r', "\n")
}

/// `git -C root args...`'s stdout, "" unless it succeeded.
pub(crate) fn git(root: &Path, args: &[&str]) -> String {
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

/// `git show rev:path`, or None where the revision has no such file.
pub(crate) fn git_show(root: &Path, rev: &str, path: &str) -> Option<String> {
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
pub(crate) fn cat_blobs(root: &Path, objects: &[String]) -> Vec<String> {
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

/// `git -C root args...` fed `input`; its stdout's bytes, whatever its exit.
fn git_stdin(root: &Path, args: &[&str], input: &str) -> Vec<u8> {
    let child = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn();
    let Ok(mut child) = child else {
        return Vec::new();
    };
    let stdin = child.stdin.take();
    let body = input.to_owned();
    let writer = std::thread::spawn(move || {
        if let Some(mut pipe) = stdin {
            let _ = pipe.write_all(body.as_bytes());
        }
    });
    let done = child.wait_with_output();
    let _ = writer.join();
    done.map_or_else(|_| Vec::new(), |o| o.stdout)
}

/// `path.read_text(encoding="utf-8")`: `\r\n` and `\r` as `\n`, an unreadable file the failure the Python would raise.
pub(crate) fn read_text(path: &Path) -> Result<String, Fail> {
    std::fs::read_to_string(path)
        .map(|t| universal(&t))
        .map_err(|e| format!("{}: {e}", path.display()))
}

/// [`read_text`], or None where `path` is no file.
pub(crate) fn read_universal(path: &Path) -> Result<Option<String>, Fail> {
    if path.is_file() {
        read_text(path).map(Some)
    } else {
        Ok(None)
    }
}

/// Runs a Python seam: `python3 -c code args...` fed `input`, its stdout on success and the stderr it wrote on failure.
pub(crate) fn python(code: &str, args: &[&str], input: &str) -> Result<String, Fail> {
    let child = Command::new("python3")
        .arg("-c")
        .arg(code)
        .args(args)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| e.to_string())?;
    let mut child = child;
    let stdin = child.stdin.take();
    let body = input.to_owned();
    let writer = std::thread::spawn(move || {
        if let Some(mut pipe) = stdin {
            let _ = pipe.write_all(body.as_bytes());
        }
    });
    let done = child.wait_with_output().map_err(|e| e.to_string())?;
    let _ = writer.join();
    if done.status.success() {
        Ok(String::from_utf8_lossy(&done.stdout).into_owned())
    } else {
        Err(String::from_utf8_lossy(&done.stderr).into_owned())
    }
}

/// The tree the scripts live in: where the wrapper said, else the root.
pub(crate) fn tree_of(root: &Path) -> std::path::PathBuf {
    std::env::var_os("L7R_GATE_TREE").map_or_else(|| root.to_path_buf(), Into::into)
}

/// The current UTC time as `%Y-%m-%dT%H:%M:%SZ`.
pub(crate) fn utc_now() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, mo, d, h, mi, s) = l7r_guard::shared::log::civil(secs);
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
}
