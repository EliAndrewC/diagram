//! `l7r-gate record archive ...` (feature 449 T146): `archive.py`'s four commands, which the Makefile's recipes run -
//!
//! - `url <u> [--key K]`: archive one URL now (`make archive URL=`; `make reserve ... URL=` asks [`archive_one`] in process)
//! - `backfill [--workers N]`: archive every cited URL with no row, resumably (`make archive-sources`)
//! - `report`: the coverage table, fetching nothing (`make archive-sources REPORT=1`)
//! - `gm-copies`: the GM's matched files copied in, their rows told (`make archive-sources GM=1`)
//!
//! and `archive_ops.py`'s five since feature 449 T147 (phase 4's S3b, [`crate::ops`]):
//!
//! - `inbox [--match F=K ...] [--none F ...]`: the GM's downloads archived, then removed (`make archive-inbox`; `record downloads
//!   ingest` asks it in process through [`inbox_cli`])
//! - `consulted [--limit N] [--workers N]`: the uncited pages feature 312's filter kept, archived (`make archive-sources CONSULTED=1`)
//! - `find [--url U] [--key K] [--terms "a|b"]`: what the archive holds (`make archive-find`)
//! - `urls <u> ...`: the cited pages read, archived where they have no row (`make source-outcome` asks [`crate::ops::archive_urls`] in
//!   process)
//! - `relayout`: the one-time move to the sharded layout
//!
//! - and the one door left of those Python's `archive.py` forwarded through, `push`, which S4's `semantic_index.py` still reaches
//!   ([`door`]).

use std::fmt::Write as _;
use std::io::Write as _;
use std::path::Path;

use l7r_gate_core::record::args::{parse_with, Spec};
use l7r_gate_research::record::archive::{self as rec, Cited};
use serde_json::Value;

use crate::backfill::backfill;
use crate::fetch::Client;
use crate::manifest::{archive_url, report, sync_gm_copies};
use crate::store::Archive;
use crate::{Error, Reply, Result};

pub mod door;
pub mod ops;

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// A raise: what was printed before it, and the exception's one line (the Python's traceback, `ask:449-usage-text`).
#[must_use]
pub fn raised(stdout: String, e: &Error) -> Reply {
    reply(stdout, format!("{e}\n"), 1)
}

/// argparse's refusal: exit 2, its one line.
fn usage(said: &str) -> Reply {
    reply(
        String::new(),
        format!("l7r-gate record archive: error: {said}\n"),
        2,
    )
}

/// The browser `archive.py` made: `l7r-browser serve`, through the root's tree.
///
/// # Errors
/// It could not start.
#[cfg(not(test))]
pub fn start_browser(root: &Path) -> Result<Box<dyn Client>> {
    crate::client::Process::start(root).map(|p| Box::new(p) as Box<dyn Client>)
}

/// Archive one URL now, as the census sees it (a KEY names a registry entry not yet written): its row's line on `out`, and the attempt
/// on the attempts log.
///
/// # Errors
/// The record, the browser, the capture, or the attempts log, as the Python raised them.
pub fn archive_one(
    root: &Path,
    url: &str,
    key: &str,
    start: &dyn Fn(&Path) -> Result<Box<dyn Client>>,
    store: &dyn Fn(&Path) -> Archive,
    out: &mut String,
) -> Result<()> {
    let research = root.join("research");
    let cleaned = rec::clean(url);
    let mut who: Cited = rec::cited(&research)?
        .into_iter()
        .find(|(u, _)| *u == cleaned)
        .map(|(_, c)| c)
        .unwrap_or_default();
    if !key.is_empty() && !who.keys.iter().any(|k| k == key) {
        who.keys.insert(0, key.to_owned());
    }
    let row = {
        let mut client = start(root)?;
        archive_url(root, url, &who, client.as_mut(), &store(root), true)?
    };
    let sought = format!(
        "archived{} (make archive)",
        if key.is_empty() {
            String::new()
        } else {
            format!(" for {key}")
        }
    );
    let more = l7r_guard::shared::attempts::More {
        key,
        route: "archive",
        ..l7r_guard::shared::attempts::More::default()
    };
    l7r_guard::shared::attempts::add(root, url, "unknown", &sought, "unknown", &more, &research)?;
    let text = |k: &str| {
        row.get(k)
            .map_or_else(String::new, l7r_guard::shared::pyjson::py_str)
    };
    let reason = text("reason");
    let _ = write!(out, "archive: {} - {url}", text("outcome"));
    if !reason.is_empty() {
        let _ = write!(out, " ({reason})");
    }
    if row
        .get("path")
        .is_some_and(l7r_guard::shared::pyjson::truthy)
    {
        let _ = write!(out, "\n  {}", rec::copy_link(&Value::Object(row)));
    }
    out.push('\n');
    Ok(())
}

/// A line printed at once (a backfill's lane prints as it goes, as the Python's pool did).
pub fn print_now(line: &str) {
    let mut o = std::io::stdout().lock();
    let _ = writeln!(o, "{line}");
    let _ = o.flush();
}

/// The working copy the commands write: the archive's home beside the page cache, git authenticated with the push's credential.
#[cfg(not(test))]
#[must_use]
pub fn production_store(root: &Path) -> Archive {
    Archive::new(
        &crate::manifest::home_of(root),
        Some(crate::store::git_env(&crate::store::token(root))),
    )
}

/// What the commands reach beyond the repository: the archive's working copy, the browser and where a lane's lines go (the real ones in
/// [`cli`], a test's stand-ins otherwise).
pub struct Reach<'a> {
    pub store: &'a dyn Fn(&Path) -> Archive,
    pub start: &'a (dyn Fn(&Path) -> Result<Box<dyn Client>> + Sync),
    pub say: &'a (dyn Fn(&str) + Sync),
}

/// `l7r-gate record archive <command>` from `cwd`'s repository: the real working copy and browser (the production wiring, which the
/// crate's tests replace through [`cli_with`]; `record`'s tests reach it on refusals that stop before either).
#[cfg(not(test))]
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    // a lane's line is printed at once, stdout locked a line at a time: the lanes print from their own threads while this one waits
    let reach = Reach {
        store: &production_store,
        start: &start_browser,
        say: &print_now,
    };
    cli_with(args, cwd, &reach)
}

/// `record archive inbox <args>` run as `record downloads ingest` ran `archive_ops.py inbox` (feature 449 T147: in process, where it
/// ran the Python by path), from `root`.
#[cfg(not(test))]
#[must_use]
pub fn inbox_cli(root: &Path, args: &[String]) -> Reply {
    let mut all = vec!["inbox".to_owned()];
    all.extend_from_slice(args);
    cli(&all, root)
}

/// [`cli`] with what it reaches handed in.
#[must_use]
pub fn cli_with(args: &[String], cwd: &Path, reach: &Reach<'_>) -> Reply {
    let root = l7r_guard::shared::consulted::repo_root(Some(cwd));
    let rest = args.get(1..).unwrap_or(&[]);
    let start = reach.start;
    match args.first().map(String::as_str) {
        Some("url") => {
            let p = match parse_with(rest, &[Spec::value("--key")], 1) {
                Ok(p) if p.positional.len() == 1 => p,
                Ok(_) => return usage("the following arguments are required: url"),
                Err(e) => return usage(&e),
            };
            let mut out = String::new();
            match archive_one(
                &root,
                &p.positional[0],
                p.text("--key", ""),
                start,
                reach.store,
                &mut out,
            ) {
                Ok(()) => reply(out, String::new(), 0),
                Err(e) => raised(out, &e),
            }
        }
        Some("backfill") => {
            let p = match parse_with(rest, &[Spec::value("--workers")], 0) {
                Ok(p) => p,
                Err(e) => return usage(&e),
            };
            let raw = p.text("--workers", "4");
            let Ok(workers) = raw.trim().parse::<i64>() else {
                return usage(&format!("argument --workers: invalid int value: '{raw}'"));
            };
            let mut err = String::new();
            let lanes = usize::try_from(workers.max(1)).unwrap_or(1);
            let store = (reach.store)(&root);
            match backfill(&root, lanes, start, reach.say, &mut err, &store) {
                Ok(code) => reply(String::new(), err, code),
                Err(e) => raised(String::new(), &e),
            }
        }
        Some("report") if rest.is_empty() => {
            let mut out = String::new();
            match report(&root, &mut out) {
                Ok(code) => reply(out, String::new(), code),
                Err(e) => raised(out, &e),
            }
        }
        Some("gm-copies") if rest.is_empty() => {
            let store = (reach.store)(&root);
            match sync_gm_copies(&root, &store) {
                Ok(n) => reply(
                    format!("archive: {n} row(s) given the GM's copies\n"),
                    String::new(),
                    0,
                ),
                Err(e) => raised(String::new(), &e),
            }
        }
        Some("report" | "gm-copies") => {
            usage(&format!("unrecognized arguments: {}", rest.join(" ")))
        }
        Some(verb @ ("inbox" | "consulted" | "find" | "urls" | "relayout")) => {
            ops::cli(verb, rest, &root, reach)
        }
        Some("push") => door::cli(rest),
        _ => usage(
            "argument cmd: invalid choice (choose from 'url', 'backfill', 'report', 'gm-copies', 'inbox', 'consulted', 'find', 'urls', 'relayout')",
        ),
    }
}

#[cfg(test)]
mod tests;
