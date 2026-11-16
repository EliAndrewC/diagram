//! THE ONE WRITER OF THE PAGE CACHE FOR THE PYTHON THAT STAYS (feature 449 T145, the plan review's FR-003 finding: one live writer
//! per shared file): `uncited.py` and `uncited_imports.py` still store a page they read, and `sources.put` - their one name for it -
//! is a forwarder to `l7r-gate record sources put`, so the `research` crate's `pages::put` is the cache's only writer (the
//! `claims_door`/`plan_door` pattern, `ask:449-T86-door`). The text comes on stdin; the stored page's meta, directory and files go
//! back as JSON, which the forwarder returns as `put` returned them.

use std::io::Read;
use std::path::Path;

use l7r_gate_research::pages::{put, Stored};
use l7r_guard::shared::pyjson::dumps;
use serde_json::{json, Value};

use super::{record_dir, reply};
use crate::record::args::{parse_with, Spec};
use crate::Reply;

/// `l7r-gate record sources put --home W --url U [--fetched F] [--inexact] [--origin O]`, the page's text on `input`.
pub fn put_cli(rest: &[String], cwd: &Path, input: &mut dyn Read) -> Reply {
    let specs = [
        Spec::value("--home"),
        Spec::value("--url"),
        Spec::value("--fetched"),
        Spec::flag("--inexact"),
        Spec::value("--origin"),
    ];
    let p = match parse_with(rest, &specs, 0) {
        Ok(p) if p.has("--home") && p.has("--url") => p,
        Ok(_) => {
            return reply(
                String::new(),
                "sources put: error: --home and --url are required\n".to_owned(),
                2,
            )
        }
        Err(e) => return reply(String::new(), format!("sources put: error: {e}\n"), 2),
    };
    let mut text = String::new();
    if let Err(e) = input.read_to_string(&mut text) {
        return reply(String::new(), format!("UnicodeDecodeError: {e}\n"), 1);
    }
    // `fetched or now()`: an empty time is the Python's falsy one
    let fetched = Some(p.text("--fetched", "")).filter(|f| !f.is_empty());
    let how = Stored {
        fetched,
        exact: !p.on("--inexact"),
        origin: p.text("--origin", "fetch"),
    };
    let root = l7r_guard::shared::consulted::repo_root(Some(cwd));
    match put(
        &cwd.join(p.text("--home", "")),
        p.text("--url", ""),
        &text,
        &how,
        &record_dir(&root),
    ) {
        Ok(c) => {
            let mut out = c.meta.clone();
            out.insert("dir".into(), json!(c.dir.to_string_lossy()));
            out.insert("files".into(), json!(c.files));
            reply(
                dumps(&Value::Object(out), None, false) + "\n",
                String::new(),
                0,
            )
        }
        Err(e) => reply(String::new(), format!("{}: {}\n", e.kind, e.message), 1),
    }
}

#[cfg(test)]
mod tests;
