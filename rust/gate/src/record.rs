//! The research record's small tools (feature 449 T79, from `canon.py`, `money_conversions.py` and `found.py`): `l7r-gate record ...`.

use std::collections::HashMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use serde_json::{json, Value};

pub use l7r_gate_core::record::*;
use crate::Reply;

pub(crate) mod access_tags;
mod agent_census;
pub(crate) mod bundle;
mod downloads;
mod fragment_move;
mod leaves;
mod merge_answers;
pub(crate) mod modals;
mod money;
pub(crate) mod owed;
mod stale_terms;
pub(crate) mod translation;
pub(crate) mod triage;


const CANON_ROOTS: [&str; 2] = [
    "/host-l7r-repo/setting",
    "/host-l7r-repo/gm-assistant/setting",
];
const CANON_CAP: usize = 15;
const CANON_WIDTH: usize = 400;
const MONEY_SOURCE: &str = "/host-l7r-repo/gm-assistant/webapp/l7r/money/data/conversions.json";
const MONEY_COPY: &str = "research/assets/money-conversions.json";

/// The repository this runs in (`git rev-parse --show-toplevel`, "." outside one), as the record tools' root.
fn top_level() -> PathBuf {
    let done = crate::cohort::git(Path::new("."), &["rev-parse", "--show-toplevel"]).1;
    PathBuf::from(Some(done.trim()).filter(|t| !t.is_empty()).unwrap_or("."))
}

fn current_dir() -> PathBuf {
    std::env::current_dir().unwrap_or_default()
}

/// The canon: every markdown and text file under the setting directories, their CLAUDE.md files excepted, each root's in path order.
fn canon_files(roots: &[PathBuf]) -> Vec<PathBuf> {
    let mut out = Vec::new();
    for root in roots {
        let mut found = Vec::new();
        let mut todo = vec![root.clone()];
        while let Some(dir) = todo.pop() {
            for path in std::fs::read_dir(&dir)
                .into_iter()
                .flatten()
                .flatten()
                .map(|e| e.path())
            {
                if path.is_dir() {
                    todo.push(path);
                } else if path.extension().is_some_and(|x| x == "md" || x == "txt")
                    && path.file_name().is_some_and(|n| n != "CLAUDE.md")
                {
                    found.push(path);
                }
            }
        }
        found.sort();
        out.extend(found);
    }
    out
}

/// Every hit of each term, `file:line [heading] text`, in file order.
fn canon_search(terms: &[String], files: &[PathBuf]) -> HashMap<String, Vec<String>> {
    let mut hits: HashMap<String, Vec<String>> =
        terms.iter().map(|t| (t.clone(), Vec::new())).collect();
    for file in files {
        let bytes = std::fs::read(file).unwrap_or_default();
        let body = String::from_utf8_lossy(&bytes);
        let mut heading = String::new();
        for (i, line) in py_lines(&body).into_iter().enumerate() {
            if line.starts_with('#') {
                line.trim_start_matches('#').trim().clone_into(&mut heading);
            }
            let low = line.to_lowercase();
            for term in terms {
                if low.contains(&term.to_lowercase()) {
                    let text = line.trim();
                    let more = if text.chars().count() > CANON_WIDTH {
                        "..."
                    } else {
                        ""
                    };
                    let row = format!(
                        "{}:{} [{}] {}{more}",
                        file.display(),
                        i + 1,
                        first_chars(&heading, 60),
                        first_chars(text, CANON_WIDTH)
                    );
                    hits.entry(term.clone()).or_default().push(row);
                }
            }
        }
    }
    hits
}

/// `record canon "a|b|c"`: every term of a claim, in one pass over the GM's canon (feature 250 D16).
fn canon(args: &[String], roots: &[PathBuf]) -> Reply {
    let terms: Vec<String> = args
        .first()
        .map_or("", String::as_str)
        .split('|')
        .map(str::trim)
        .filter(|t| !t.is_empty())
        .map(str::to_owned)
        .collect();
    if terms.is_empty() {
        return reply(
            String::new(),
            "canon: no term given - TERMS=\"<a>|<b>|<c>\", every term of the claim at once\n"
                .to_owned(),
            2,
        );
    }
    let found = canon_search(&terms, &canon_files(roots));
    let mut out = String::new();
    for term in &terms {
        let rows = &found[term];
        let shown = if rows.len() <= CANON_CAP {
            String::new()
        } else {
            format!(", the first {CANON_CAP} shown")
        };
        let _ = writeln!(out, "== {term}: {} hit(s){shown}", rows.len());
        for row in rows.iter().take(CANON_CAP) {
            let _ = writeln!(out, "  {row}");
        }
    }
    reply(out, String::new(), 0)
}

/// `record money-conversions [--check]`: the record's byte-for-byte copy of gm-assistant's money table (feature 413 FR-001).
fn money(args: &[String], source: &Path, root: &Path) -> Reply {
    let Ok(fresh) = std::fs::read(source) else {
        return reply(format!("money-conversions: gm-assistant's table is not here ({}) - nothing to compare; the record builds from {MONEY_COPY}\n", source.display()), String::new(), 0);
    };
    let copy = root.join(MONEY_COPY);
    if std::fs::read(&copy).is_ok_and(|held| held == fresh) {
        return reply(
            format!("money-conversions: {MONEY_COPY} is current\n"),
            String::new(),
            0,
        );
    }
    if args.iter().any(|a| a == "--check") {
        return reply(String::new(), format!("money-conversions: {MONEY_COPY} differs from gm-assistant's {} - run `make money-conversions` and commit the copy\n", source.display()), 1);
    }
    match std::fs::write(&copy, fresh) {
        Ok(()) => reply(
            format!(
                "money-conversions: {MONEY_COPY} refreshed from {}\n",
                source.display()
            ),
            String::new(),
            0,
        ),
        Err(why) => reply(String::new(), format!("money-conversions: {why}\n"), 1),
    }
}

fn now_utc() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, mo, d, h, mi, s) = l7r_guard::shared::log::civil(secs);
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
}

fn is_open(row: &Value) -> bool {
    row["status"].as_str().unwrap_or("open") == "open"
}

fn is_task(task: &str) -> bool {
    let bare = task
        .strip_prefix("385 ")
        .or_else(|| task.strip_prefix("405 "))
        .unwrap_or(task);
    bare.strip_prefix('T')
        .is_some_and(|n| !n.is_empty() && n.bytes().all(|b| b.is_ascii_digit()))
}

/// Close the numbered rows (1-based, file order): filed as `task`, or settled with `why`, refusing a row already closed.
pub(crate) fn close_rows(
    rows: &mut [Value],
    numbers: &[usize],
    task: &str,
    why: &str,
    when: &str,
) -> Result<usize, String> {
    if task.is_empty() == why.is_empty() {
        return Err("one of --task (filed) or --why (settled)".to_owned());
    }
    if numbers.is_empty() {
        return Err(
            "no rows named - make found-close F=<n> ROWS=3,7 (the numbers make found-list prints)"
                .to_owned(),
        );
    }
    if !task.is_empty() && !is_task(task) {
        return Err(format!("--task names a task id - T61, or 385 T12 / 405 T17 (the GM's routing names those two features only) - not '{task}'"));
    }
    // SETTLED ONLY WHERE IT NO LONGER HOLDS (the plan review of 405 D36): a finding that still holds is filed as a task (FR-002)
    let measured =
        why.to_lowercase().starts_with("no longer holds") && why.split_whitespace().count() >= 6;
    if !why.is_empty() && !measured {
        return Err("--why starts \"no longer holds\" and records what was measured against the current file (a finding that still holds is filed as a task)".to_owned());
    }
    for n in numbers {
        if !(1..=rows.len()).contains(n) {
            return Err(format!("no row {n} (the file has {})", rows.len()));
        }
        if !is_open(&rows[n - 1]) {
            return Err(format!(
                "row {n} is already {}",
                rows[n - 1]["status"].as_str().unwrap_or("")
            ));
        }
    }
    for n in numbers {
        let row = &mut rows[n - 1];
        if task.is_empty() {
            row["status"] = json!("settled");
            row["why"] = json!(why);
        } else {
            row["status"] = json!("filed");
            row["task"] = json!(task);
        }
        row["closed_utc"] = json!(when);
    }
    Ok(numbers.len())
}

fn found_list(rows: &[Value], path: &Path) -> String {
    let mut out = String::new();
    let open: Vec<(usize, &Value)> = rows
        .iter()
        .enumerate()
        .filter(|(_, r)| is_open(r))
        .collect();
    for (i, row) in &open {
        let field = |k: &str| row[k].as_str().unwrap_or("?").to_owned();
        let _ = writeln!(
            out,
            "{:3}  {}  {}  {}",
            i + 1,
            field("check"),
            field("file"),
            first_chars(row["finding"].as_str().unwrap_or(""), 160)
        );
    }
    let _ = writeln!(
        out,
        "found: {} open of {} row(s) in {}",
        open.len(),
        rows.len(),
        path.display()
    );
    out
}

/// `record found list|close --feature <dir> ...`: a feature's findings, each `open` until filed as a task or settled (feature 405 T29).
fn found(args: &[String]) -> Reply {
    let (verb, feature) = (
        args.first().map_or("", String::as_str),
        flag(args, "--feature"),
    );
    if !matches!(verb, "list" | "close") || feature.is_empty() {
        return reply(String::new(), "usage: l7r-gate record found list|close --feature <dir> [--rows 3,7] [--task T61] [--why \"...\"]\n".to_owned(), 2);
    }
    let path = Path::new(feature).join("found.jsonl");
    let text = std::fs::read_to_string(&path).unwrap_or_default();
    let parsed: Result<Vec<Value>, _> = text
        .lines()
        .filter(|l| !l.trim().is_empty())
        .map(serde_json::from_str)
        .collect();
    let Ok(mut rows) = parsed else {
        return reply(
            String::new(),
            format!("found: {} does not parse\n", path.display()),
            1,
        );
    };
    if verb == "list" {
        return reply(found_list(&rows, &path), String::new(), 0);
    }
    let compact = flag(args, "--rows").replace(' ', "");
    let numbers: Result<Vec<usize>, _> = compact
        .split(',')
        .filter(|x| !x.is_empty())
        .map(str::parse)
        .collect();
    let (task, why) = (flag(args, "--task"), flag(args, "--why"));
    let closed = numbers
        .map_err(|_| format!("--rows is a list of numbers, not {compact}"))
        .and_then(|n| close_rows(&mut rows, &n, task, why, &now_utc()));
    let count = match closed {
        Ok(count) => count,
        Err(why) => return reply(String::new(), format!("found: refused - {why}\n"), 2),
    };
    let body: String = rows
        .iter()
        .map(|r| crate::logs::one_line_utf8(r) + "\n")
        .collect();
    if let Err(why) = std::fs::write(&path, body) {
        return reply(String::new(), format!("found: {why}\n"), 1);
    }
    let what = if task.is_empty() {
        "settled".to_owned()
    } else {
        format!("filed as {task}")
    };
    reply(
        format!("found: {count} row(s) {what} in {}\n", path.display()),
        String::new(),
        0,
    )
}

/// `l7r-gate record canon | money-conversions | found ...`.
pub(crate) fn cli(args: &[String]) -> Reply {
    let rest = args.get(1..).unwrap_or(&[]);
    match args.first().map(String::as_str) {
        Some("canon") => canon(rest, &CANON_ROOTS.map(PathBuf::from)),
        Some("money-conversions") => money(rest, Path::new(MONEY_SOURCE), Path::new(".")),
        Some("found") => found(rest),
        Some("money-candidates") => money::cli(rest, Path::new(".")),
        Some("stale-terms") => stale_terms::cli(rest),
        Some("stale-dirs") => stale_terms::dirs_cli(rest),
        Some("fragment-move") => fragment_move::cli(rest),
        Some("agent-census") => agent_census::cli(rest, &crate::measure::home()),
        Some("access-tags") => access_tags::cli(rest, &top_level()),
        Some("downloads") => downloads::cli(rest, &top_level()),
        Some(verb @ ("edit-route" | "fragments" | "moved-only" | "americanize")) => {
            leaves::cli(verb, rest, &mut std::io::stdin(), &current_dir())
        }
        Some("record-owed") => owed::cli(rest),
        Some("modal-owed") => modals::cli(rest),
        Some("translation-owed") => translation::cli(rest),
        Some("modal-triage") => triage::cli(rest),
        Some("merge-answers") => merge_answers::cli(rest),
        Some("check-bundle") => bundle::check::cli(rest),
        Some("modal-bundle") => bundle::modal::cli(rest),
        _ => reply(
            String::new(),
            "usage: l7r-gate record canon | money-conversions | found ...\n".to_owned(),
            2,
        ),
    }
}

#[cfg(test)]
mod tests;
