//! The page sessions' tools (feature 449 T137, `ask:449-phase3-remainder`, ported whole with no door, FR-003), from `scripts/pages/`:
//! `l7r-gate page-session` (the detached runner `page-session.sh` execs, [`runner`], `page_session_runner.py`), `l7r-gate brief-load`
//! (the write cap's count, [`brief_load`], `brief_load.py`, which the runner asks in process), `l7r-gate coord lines|append` (`make
//! lines`, `make append`, [`coord`], `coord.py`), `l7r-gate research-claims claim|query|sweep` (`make research-claim`, `make
//! research-claims`, [`research_claims`], `research_claims.py`) and `l7r-gate escape take` (an escape taken outside a hook, logged as a
//! hook's is, [`escape_log`], `escape_log.py`: the runner's write cap in process, `make reserve`'s key cap by command).

pub mod brief_load;
pub mod coord;
pub mod escape_log;
pub mod research_claims;
pub mod runner;

use std::path::{Path, PathBuf};

use l7r_gate_core::Reply;

/// `l7r-gate <verb> ...` for the page sessions' tools, each reading this process's environment, working directory and binary: `page-session`,
/// `brief-load`, `coord`, `research-claims`, and `escape-take` (the binary's `escape take`).
#[must_use]
pub fn cli(verb: &str, args: &[String]) -> Reply {
    let cwd = std::env::current_dir().unwrap_or_default();
    match verb {
        "page-session" => runner::cli(
            args,
            &std::env::current_exe().unwrap_or_default(),
            &escape_log::Env::of_process(),
            std::env::vars().collect(),
        ),
        "brief-load" => brief_load::cli(args),
        "coord" => coord::cli(
            args,
            &coord::Env {
                cwd,
                var: &|k| std::env::var(k).ok(),
            },
        ),
        "research-claims" => research_claims::cli(
            args,
            &research_claims::Env {
                cwd,
                sheet: research_claims::sheet(std::env::var("L7R_CLAIMS_SHEET").ok()),
                today: l7r_gate_core::record::bundle::today,
            },
        ),
        _ => escape_log::cli(args, &escape_log::Env::of_process()),
    }
}

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// A raise: what was printed before it, then its message after a `Traceback` line, exit 1, as the Python's uncaught exception ended (the
/// form the other ports answer one in, `ask:449-usage-text`).
fn raised(tool: &str, stdout: String, why: &str) -> Reply {
    reply(
        stdout,
        format!("Traceback (most recent call last):\n  l7r-gate {tool}\n{why}\n"),
        1,
    )
}

/// A file as `read_text(encoding="utf-8")` reads it: strictly UTF-8, its newlines universal; the error what the Python raised.
fn read_strict(path: &Path) -> Result<String, String> {
    let bytes = std::fs::read(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let text = String::from_utf8(bytes)
        .map_err(|e| format!("UnicodeDecodeError: {}: {e}", path.display()))?;
    Ok(l7r_gate_core::record::repo::universal(&text))
}

/// A file as `read_text(errors="replace")` reads it, "" where it cannot be read (the runner's `_read`).
fn read_lossy(path: &Path) -> String {
    l7r_guard::shared::speckit::read_text(path).unwrap_or_default()
}

/// `(path.stem, path.suffix)` as Python 3.14 reads them: the suffix from the last dot of the name, unless the name starts with it (a
/// name ending in a dot has the suffix `.`).
fn py_suffix_stem(path: &Path) -> (String, String) {
    let name = l7r_guard::shared::speckit::py_name(path);
    match name.rfind('.') {
        Some(i) if i > 0 => (name[..i].to_owned(), name[i..].to_owned()),
        _ => (name, String::new()),
    }
}

/// `os.path.join(a, b)` for a `b` that is a plain relative name: one slash between, none added after one.
fn py_join(a: &str, b: &str) -> String {
    if a.is_empty() || a.ends_with('/') {
        format!("{a}{b}")
    } else {
        format!("{a}/{b}")
    }
}

/// `os.path.basename`: what follows the last slash.
fn basename(path: &str) -> &str {
    path.rsplit('/').next().unwrap_or(path)
}

/// `os.path.dirname`: what precedes the last slash, its trailing slashes dropped unless it is all slashes.
fn dirname(path: &str) -> &str {
    let head = path.rfind('/').map_or("", |i| &path[..=i]);
    let trimmed = head.trim_end_matches('/');
    if trimmed.is_empty() {
        head
    } else {
        trimmed
    }
}

/// The working directory, as `os.getcwd()` gives it.
fn cwd() -> String {
    std::env::current_dir()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned()
}

/// `os.path.normpath(os.path.abspath(path))`: absolute, `.` and `..` resolved by the text alone.
fn abspath(path: &str, cwd: &str) -> String {
    let full = if path.starts_with('/') {
        path.to_owned()
    } else {
        py_join(cwd, path)
    };
    let mut parts: Vec<&str> = Vec::new();
    for part in full.split('/') {
        match part {
            "" | "." => {}
            ".." => {
                parts.pop();
            }
            p => parts.push(p),
        }
    }
    format!("/{}", parts.join("/"))
}

/// `os.path.relpath(path, start)`.
fn relpath(path: &str, start: &str, cwd: &str) -> String {
    let from = abspath(start, cwd);
    let to = abspath(path, cwd);
    let a: Vec<&str> = from.split('/').filter(|p| !p.is_empty()).collect();
    let b: Vec<&str> = to.split('/').filter(|p| !p.is_empty()).collect();
    let common = a.iter().zip(&b).take_while(|(x, y)| x == y).count();
    let rel: Vec<&str> = std::iter::repeat_n("..", a.len() - common)
        .chain(b[common..].iter().copied())
        .collect();
    if rel.is_empty() {
        ".".to_owned()
    } else {
        rel.join("/")
    }
}

/// `os.path.realpath(path)` (Python 3.14, not strict): absolute, each existing symlink resolved as it is met, a `..` applied to what
/// is resolved so far, a missing part kept as written, a loop left where it closed.
fn realpath(path: &str, cwd: &str) -> String {
    let mut rest: Vec<Option<String>> = path.split('/').rev().map(|p| Some(p.to_owned())).collect();
    let mut seen: std::collections::HashMap<String, Option<String>> =
        std::collections::HashMap::new();
    let mut at = if path.starts_with('/') {
        "/".to_owned()
    } else {
        cwd.to_owned()
    };
    while let Some(name) = rest.pop() {
        let Some(name) = name else {
            // a symlink's target resolved: the link stands for where it led
            if let Some(Some(link)) = rest.pop() {
                seen.insert(link, Some(at.clone()));
            }
            continue;
        };
        if name.is_empty() || name == "." {
            continue;
        }
        if name == ".." {
            at = at.rfind('/').map_or("/", |i| &at[..i]).to_owned();
            if at.is_empty() {
                "/".clone_into(&mut at);
            }
            continue;
        }
        let next = py_join(&at, &name);
        // `readlink` answers only a symlink: a missing part or any other file is kept as written, as the Python's `lstat` read them
        let Ok(target) = std::fs::read_link(&next).map(|t| t.to_string_lossy().into_owned()) else {
            at = next;
            continue;
        };
        if let Some(known) = seen.get(&next) {
            at = known.clone().unwrap_or(next);
            continue;
        }
        seen.insert(next.clone(), None);
        if target.starts_with('/') {
            "/".clone_into(&mut at);
        }
        rest.push(Some(next));
        rest.push(None);
        rest.extend(target.split('/').rev().map(|p| Some(p.to_owned())));
    }
    at
}

/// A path's text, for a path Python held as `str`.
fn text(path: &Path) -> String {
    path.to_string_lossy().into_owned()
}

/// `pathlib.Path(text)` of a path given as text.
fn py_path(text: &str) -> PathBuf {
    l7r_guard::shared::speckit::py_path(text)
}

#[cfg(test)]
mod tests;
