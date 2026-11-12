//! `l7r-gate close-check`: the closing check's command line (feature 375 FR-009/FR-014), ported from `scripts/gates/close_check.py` by
//! feature 449 T127. The reasons are `reviews::closing`'s, which `gm_review` asks in process; the command lives here, beside the push
//! that runs its `--push` row and the `touched_features` and speckit state that form reads in process (where the Python asked
//! `plan_door.py` and `l7r-gate speckit-todo --each-state` by command).
//!
//! ```text
//! close-check <feature dir>              the reasons it may not close, one a line (none: it may)
//! close-check --push [<range>]           the same, for every touched feature that reads closed (origin/main...HEAD by default)
//! close-check --carries                  every carry
//! close-check --write-grandfathered      the features closed now, written to scripts/gates/closed-before-375.txt
//! close-check --reasons-json DIR SPECS   the reasons of DIR as JSON, its carries read under SPECS (`make tick`'s last tick until
//!                                        feature 449 T131 asked `reviews::closing` in process; kept as the reasons' command form)
//! ```
//!
//! The usage log records a run as `usage_log.exited` did: `passed`, or `refused` on a non-zero exit (a usage error's 2 among them), in
//! the working directory's repository, none where the Python raised. `--reasons-json` records nothing, as `tick-task.py`'s import of
//! the module recorded nothing (that file is `l7r-gate tick` since feature 449 T131) (the T118 precedent of `--each-state`). The usage text is the Python's, byte for byte
//! (`ask:449-usage-text`); a raise is exit 1 after a `Traceback` line, as the other ports answer one.

use std::fmt::Write as _;
use std::path::{Component, Path, PathBuf};

use l7r_gate_reviews::reviews::closing::{
    carries, reasons, Closing, ImplCheck, Tools, GRANDFATHERED,
};
use l7r_guard::shared::pyjson::dumps;
use l7r_guard::shared::speckit::{py_path, state};
use serde_json::Value;

use crate::Reply;

/// The name the usage log records a run under (feature 406 T01; `scripts/tool-registry.json`).
const USAGE_LOG_TOOL: &str = "close_check";

const USAGE: &str = "    close_check.py <feature dir>        the reasons it may not close, one a line (none: it may)
    close_check.py --push <range>       the same, for every touched feature that reads closed
    close_check.py --carries            every carry, with whether it is met

";

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// `Path(p).resolve()`: absolute from `cwd`, each link that exists followed, a part that does not taken as written.
fn resolve(p: &str, cwd: &Path) -> PathBuf {
    let mut out = PathBuf::from("/");
    for c in cwd.join(p).components() {
        match c {
            Component::ParentDir => {
                out.pop();
            }
            Component::Normal(n) => {
                out.push(n);
                if let Ok(real) = std::fs::canonicalize(&out) {
                    out = real;
                }
            }
            _ => {}
        }
    }
    out
}

/// Each directory's state by `make speckit-todo`'s one rule, all before any is asked, as `_states` ran one process for them all.
fn states(dirs: &[PathBuf]) -> Result<Vec<String>, String> {
    dirs.iter()
        .map(|d| state(d).map_err(|e| format!("speckit-todo --each-state: {}: {e}", d.display())))
        .collect()
}

/// Every touched feature that reads closed (its tasks all ticked, or a closing status word) and may not close.
fn push_reasons(tools: &Tools, root: &Path, range: &str) -> Result<Closing, String> {
    let dirs: Vec<PathBuf> = crate::plan::touched_features(root, range)
        .into_iter()
        .map(|name| root.join(name))
        .filter(|d| d.is_dir())
        .collect();
    let closed: Vec<PathBuf> = dirs
        .iter()
        .zip(states(&dirs)?)
        .filter(|(_, s)| s == "closed")
        .map(|(d, _)| d.clone())
        .collect();
    reasons(tools, &root.join("specs"), &closed)
}

/// The features closed when the check lands - the only ones it does not ask (plan D13); run once, at that commit.
fn write_grandfathered(tools: &Tools, specs: &Path) -> Result<usize, String> {
    let mut dirs: Vec<PathBuf> = if specs.is_dir() {
        std::fs::read_dir(specs)
            .map_err(|e| format!("OSError: {e}: {}", specs.display()))?
            .flatten()
            .map(|e| e.path())
            .filter(|p| p.is_dir())
            .collect()
    } else {
        Vec::new()
    };
    dirs.sort();
    let names: Vec<String> = dirs
        .iter()
        .zip(states(&dirs)?)
        .filter(|(_, s)| s == "closed")
        .map(|(d, _)| {
            d.file_name()
                .unwrap_or_default()
                .to_string_lossy()
                .into_owned()
        })
        .collect();
    let path = tools.tree.join(GRANDFATHERED);
    std::fs::write(&path, names.join("\n") + "\n")
        .map_err(|e| format!("OSError: {e}: {}", path.display()))?;
    Ok(names.len())
}

/// `main`: what it prints and its exit, or what it raised.
fn main(args: &[String], tools: &Tools, cwd: &Path) -> Result<Reply, String> {
    let root = resolve(".", cwd);
    let found = match args.first().map(String::as_str) {
        Some("--push") => push_reasons(
            tools,
            &root,
            args.get(1).map_or("origin/main...HEAD", String::as_str),
        )?,
        Some("--carries") => {
            let mut listed = String::new();
            for (decl, sc, n, key) in carries(&root.join("specs"))? {
                let _ = writeln!(listed, "{decl} {sc} -> {n} `{key}`");
            }
            return Ok(reply(listed, String::new(), 0));
        }
        Some("--write-grandfathered") => {
            let n = write_grandfathered(tools, &root.join("specs"))?;
            return Ok(reply(
                format!("close-check: {n} feature(s) closed before the check\n"),
                String::new(),
                0,
            ));
        }
        Some(one) if args.len() == 1 => {
            let d = resolve(one, cwd);
            let specs = d.parent().unwrap_or(&d).to_path_buf(); // `/`'s parent is itself
            reasons(tools, &specs, &[d])?
        }
        _ => return Ok(reply(String::new(), USAGE.to_owned(), 2)),
    };
    let found_all = found.each.concat();
    let code = i32::from(!found_all.is_empty());
    Ok(reply(
        found_all.iter().flat_map(|f| [f.as_str(), "\n"]).collect(),
        String::new(),
        code,
    ))
}

/// A raise: what the implementation check raised comes first, as the in-process import's traceback did, and the command's own trace
/// closes it (`why`'s last line, feature 449 T127; the implementation check in process since T132).
fn raised(why: &str) -> Reply {
    let (said, last) = why.rsplit_once('\n').map_or(("", why), |(s, l)| (s, l));
    let said = if said.is_empty() {
        String::new()
    } else {
        format!("{said}\n")
    };
    reply(
        String::new(),
        format!("{said}Traceback (most recent call last):\n  l7r-gate close-check\n{last}\n"),
        1,
    )
}

/// `l7r-gate close-check ...` in `cwd`, with the tools of `tools`.
#[must_use]
pub fn cli_in(args: &[String], tools: &Tools, cwd: &Path) -> Reply {
    if args.len() == 3 && args[0] == "--reasons-json" {
        let d = py_path(&args[1]);
        return match reasons(tools, &py_path(&args[2]), &[d]) {
            Ok(mut found) => {
                let list = found.each.pop().unwrap_or_default();
                let value = Value::from(list);
                reply(format!("{}\n", dumps(&value, None, true)), String::new(), 0)
            }
            Err(why) => raised(&why),
        };
    }
    match main(args, tools, cwd) {
        Ok(r) => {
            crate::stamp::record_for(
                cwd,
                USAGE_LOG_TOOL,
                if r.code == 0 { "passed" } else { "refused" },
            );
            r
        }
        Err(why) => raised(&why),
    }
}

/// `l7r-gate close-check ...` in the working directory, the closing list the gate's own tree's (`L7R_GATE_TREE`), `impl_check` the
/// implementation check the binary hands in (`claims` builds on `reviews`, below this crate; feature 449 T132).
#[must_use]
pub fn cli(args: &[String], impl_check: ImplCheck) -> Reply {
    let cwd = std::env::current_dir().unwrap_or_default();
    let tree = std::env::var_os("L7R_GATE_TREE").map_or_else(|| cwd.clone(), PathBuf::from);
    let tools = Tools {
        tree: &tree,
        impl_check,
    };
    cli_in(args, &tools, &cwd)
}

#[cfg(test)]
mod tests;
