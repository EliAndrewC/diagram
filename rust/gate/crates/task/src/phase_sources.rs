//! The old code of a stage being rebuilt, held off-limits while its task runs (feature 444, the GM 2026-10-30); `gates/phase_sources.py`,
//! ported by feature 449 T131. This is the one writer of `<git common dir>/phase-sources.json`, which the guard's `phase_source_hooks`
//! reads.
//!
//! WHY (the GM, 2026-10-30): "a big part of the goal for the rewrite is that we are not trying to re-implement the same algorithms,
//! because the old algorithms were computationally inefficient ... My biggest fear with this ... is that ... you would just end up
//! re-implementing the same bad algorithms." A phase task (a `tasks.md` block carrying `phase: <stage>`) rebuilds its stage in Rust from
//! the stage's greenfield derivation (feature 444 FR-015, FR-017). So `make task-start` on such a task records the stage's old modules
//! here, and the guard refuses a read of them until the task is ticked; `make phase-read FILE= WHY=` (`l7r-gate phase-read allow <file>
//! <why>`, the usage text naming `phase_sources.py` byte for byte) lets one file be read for ten minutes, the reason logged.
//!
//! THE OLD CODE: the stage's Python and every module defining a function its counters name in the newest `make work-budget` run (the
//! work budget's `stage_sources`, asked in process where the Python ran `work-budget-bundle --sources`), and any path or glob the task
//! block names on an `old-code:` line, matched as `Path.glob` matches it.

pub(crate) mod glob;

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::{split, SPACE_CLASS};
use l7r_guard::shared::pyjson::dumps;
use serde_json::{json, Value};

use crate::tick::text::re;
use crate::tick::Raise;
use crate::{common_text, now_secs, raised, read_strict, reply, utc_text, Reply};

/// In the git common directory, beside `active-task`.
const STATE: &str = "phase-sources.json";
const ALLOW_MINUTES: u64 = 10;
/// The name the usage log records `make phase-read` under (`usage_log.exited` in the Python, feature 406 T03, D162), which
/// `scripts/tool-registry.json` registers.
const USAGE_LOG_TOOL: &str = "phase_sources";

static PHASE: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"(?m)^[{SPACE_CLASS}]*phase:[{SPACE_CLASS}]*(\w+)[{SPACE_CLASS}]*$"
    ))
});
static OLD_CODE: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"(?m)^[{SPACE_CLASS}]*old-code:[{SPACE_CLASS}]*(.+)$"
    ))
});

/// `Path(<common dir>) / STATE`, the common directory read from `root`.
fn state_path(root: &Path) -> PathBuf {
    PathBuf::from(common_text(root)).join(STATE)
}

/// The task block's `phase:` stage ('' for none) and its `old-code:` paths or globs.
fn phase_of(block: &str) -> (String, Vec<String>) {
    let phase = PHASE
        .captures(block)
        .ok()
        .flatten()
        .and_then(|c| c.get(1).map(|m| m.as_str().to_owned()))
        .unwrap_or_default();
    let extra = OLD_CODE
        .captures_iter(block)
        .flatten()
        .filter_map(|c| c.get(1).map(|m| m.as_str().to_owned()))
        .flat_map(|line| {
            split(&line)
                .into_iter()
                .map(str::to_owned)
                .collect::<Vec<_>>()
        })
        .collect();
    (phase, extra)
}

/// The stage's old modules, relative to `root`, sorted.
fn sources(root: &Path, phase: &str, extra: &[String]) -> Raise<Vec<String>> {
    // THE OLD CODE IS THE PYTHON (the work budget's `stage_sources` leaves out a Rust phase's `.rs` source, the very code the task
    // writes, which must stay readable)
    // each relative to the root as a found path's own, so already in `Path`'s normal form
    let mut files: Vec<String> =
        l7r_gate_trials::measure::work_budget_bundle::stage_sources(root, phase)?;
    for g in extra {
        for p in glob::glob(root, g)? {
            if p.is_file() {
                let rel = p
                    .strip_prefix(root)
                    .unwrap_or(&p)
                    .to_string_lossy()
                    .into_owned();
                files.push(rel);
            }
        }
    }
    files.sort();
    files.dedup();
    Ok(files)
}

/// Write the state for a phase task, or clear it for any other; the line `make task-start` prints ('' when none).
///
/// # Errors
/// What the Python raised: the stage's sources unreadable, a glob refused, the state not written.
pub(crate) fn record(root: &Path, feature: &str, task: &str, block: &str) -> Raise<String> {
    let path = state_path(root);
    let (phase, extra) = phase_of(block);
    if phase.is_empty() {
        let _ = std::fs::remove_file(&path);
        return Ok(String::new());
    }
    let files = sources(root, &phase, &extra)?;
    let state =
        json!({"feature": feature, "task": task, "phase": phase, "files": files, "allow": []});
    crate::write_file(
        &path,
        format!("{}\n", dumps(&state, Some(1), true)).as_bytes(),
    )?;
    Ok(format!(
        "phase-sources: {task} rebuilds `{phase}` from its derivation - {} file(s) of its old code are not read until it is ticked (`make phase-read FILE= WHY=` for one, ten minutes)",
        files.len()
    ))
}

/// `"x" in value` as Python asks it of the state's `files`: a list's items, a string's substrings, an object's keys.
fn holds(files: Option<&Value>, rel: &str) -> Raise<bool> {
    match files {
        Some(Value::Array(items)) => Ok(items.iter().any(|v| v.as_str() == Some(rel))),
        Some(Value::String(s)) => Ok(s.contains(rel)),
        Some(Value::Object(o)) => Ok(o.contains_key(rel)),
        None => Err("KeyError: 'files'".to_owned()),
        Some(other) => Err(format!(
            "TypeError: argument of type '{other}' is not iterable"
        )),
    }
}

/// `make phase-read`: one held file let through for ten minutes, the reason kept. The exit code, what it printed, and the raise if any.
fn allow(root: &Path, cwd: &Path, file: &str, why: &str, now: u64) -> Raise<(i32, String, String)> {
    let path = state_path(root);
    if !path.is_file() {
        return Ok((
            2,
            String::new(),
            "phase-read: no phase task is started - nothing is held\n".to_owned(),
        ));
    }
    if split(why).len() < 2 {
        return Ok((2, String::new(), "phase-read: WHY=\"<two words or more>\" is required - the reason is what the log keeps\n".to_owned()));
    }
    let mut state: Value =
        serde_json::from_str(&read_strict(&path)?).map_err(|e| format!("JSONDecodeError: {e}"))?;
    let rel = if Path::new(file).is_absolute() {
        let (abs, top) = (resolved(Path::new(file)), resolved(&cwd.join(root)));
        abs.strip_prefix(&top)
            .map_err(|_| {
                format!(
                    "ValueError: {} is not in the subpath of {}",
                    abs.display(),
                    top.display()
                )
            })?
            .to_string_lossy()
            .into_owned()
    } else {
        file.to_owned()
    };
    if !holds(state.get("files"), &rel)? {
        let phase = state.get("phase").ok_or("KeyError: 'phase'")?;
        let phase = l7r_guard::shared::pyjson::py_str(phase);
        return Ok((
            2,
            String::new(),
            format!("phase-read: {rel} is not one of {phase}'s held files - read it as usual\n"),
        ));
    }
    let until = now + ALLOW_MINUTES * 60;
    let until_text = utc_text(until);
    let Some(Value::Array(allowed)) = state.get_mut("allow") else {
        return Err("KeyError or AttributeError: the state's 'allow'".to_owned());
    };
    allowed.push(json!({"file": rel, "until": until_text, "why": why}));
    crate::write_file(
        &path,
        format!("{}\n", dumps(&state, Some(1), true)).as_bytes(),
    )?;
    Ok((
        0,
        format!(
            "phase-read: {rel} may be read until {} UTC - {why}\n",
            &until_text[11..16]
        ),
        String::new(),
    ))
}

/// `Path.resolve()`: absolute, its symlinks followed as far as the path exists, the rest kept as written.
fn resolved(path: &Path) -> PathBuf {
    let mut done = PathBuf::from("/");
    let mut real = true;
    for c in path.components() {
        match c {
            std::path::Component::RootDir
            | std::path::Component::Prefix(_)
            | std::path::Component::CurDir => {}
            std::path::Component::ParentDir => {
                done.pop();
            }
            std::path::Component::Normal(n) => {
                done.push(n);
                if real {
                    match done.canonicalize() {
                        Ok(r) => done = r,
                        Err(_) => real = false,
                    }
                }
            }
        }
    }
    done
}

/// `l7r-gate phase-read allow <file> <why>` from `cwd`; the run recorded in its repository (`passed`, or `refused` on any other exit),
/// none where it raised, as the Python's `__main__` recorded it.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    let root = crate::toplevel_or_dot(cwd);
    let done = if args.len() == 3 && args[0] == "allow" {
        allow(&root, cwd, &args[1], &args[2], now_secs())
    } else {
        Ok((
            2,
            String::new(),
            "usage: phase_sources.py allow <file> <why>\n".to_owned(),
        ))
    };
    match done {
        Ok((code, out, err)) => {
            l7r_guard::shared::usage::record(
                cwd,
                USAGE_LOG_TOOL,
                "check",
                l7r_guard::shared::usage::exited(code),
            );
            reply(out, err, code)
        }
        Err(why) => raised("phase-read", String::new(), "", &why),
    }
}

#[cfg(test)]
mod tests;
