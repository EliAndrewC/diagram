//! `make fix-yield F=<feature>` - is each tooling fix doing anything, read by what its tools did since it was made (feature 385 T119;
//! rebuilt on `make tool-yield` by feature 406 T06, D165; feature 449 T120, from `fix_yield.py`, under `ask:449-T83-scope`).
//!
//! WHY (the GM 2026-10-19): each fix's yield measured "so a fix that saves nothing is retired", and "Whether or not it's doing
//! something for us should be a measurable question".
//!
//! A fix's tools are the guards, checks, targets, reviews and registered steps in the files of the commit that settled it (the settling
//! note's leading hash, or the commit naming its trigger), mapped by `tool_yield::tools_of`. Each fix then takes the first reading that
//! holds, in D166's order: too new to say (made under 7 days ago); doing something (a tool with interventions net of its misfires); no
//! outcome record (a tool whose record cannot show one, or no tool found); record too new (a tool first seen under 7 days ago); doing
//! nothing. The step-back bundle's `fix-yield.md` is this report, read in process (`stepback_bundle.rs`).

use std::collections::BTreeSet;
use std::path::{Component, Path, PathBuf};

use l7r_gate_core::measure::tool_inventory::targets;
use l7r_gate_core::record::args::{parse_with, Spec};
use l7r_guard::shared::log::civil;
use l7r_guard::shared::py_text::split;
use l7r_guard::shared::speckit::splitlines;
use serde_json::{json, Map, Value};

use super::events::{git, or_s, py_str, re, truthy, Raised};
use super::reply;
use super::stepback_bundle::lines;
use super::tool_yield::{collect, tools_of, Tally, Tools};
use super::turn_time::ts_of;
use crate::Reply;

const DAY: f64 = 86_400.0;
/// A commit touching only these made no tool change.
const RECORDS: [&str; 5] = ["specs/", "dev/", "docs/", "research/", "tests/"];

type Row = Map<String, Value>;

/// Every ruling naming a fix, with its settling (`fix_of` rows: done or declined): its status, when, and its note.
#[must_use]
pub fn fixes(rows: &[Row]) -> Vec<Row> {
    let mut settled: Vec<(String, &Row)> = Vec::new();
    for r in rows.iter().filter(|r| r.get("fix_of").is_some_and(truthy)) {
        let key = py_str(&r["fix_of"]);
        match settled.iter_mut().find(|(k, _)| *k == key) {
            Some(slot) => slot.1 = r,
            None => settled.push((key, r)),
        }
    }
    let empty = Row::new();
    let mut out = Vec::new();
    for r in rows
        .iter()
        .filter(|r| r.get("tooling_fix").is_some_and(truthy))
    {
        let trigger = r.get("trigger").map_or_else(|| "None".to_owned(), py_str);
        let s = settled
            .iter()
            .find(|(k, _)| *k == trigger)
            .map_or(&empty, |(_, s)| *s);
        let mut row = r.clone();
        for (key, from, default) in [
            ("status", "status", "open"),
            ("settled", "utc", ""),
            ("note", "note", ""),
            ("test", "test", ""),
        ] {
            row.insert(
                key.to_owned(),
                s.get(from).cloned().unwrap_or_else(|| json!(default)),
            );
        }
        out.push(row);
    }
    out
}

/// The commits that may have made the fix, best first: the hash its settling note opens with; the commits up to its settling that
/// name its trigger exactly (`@2` is not `@29`), the clone's own before a landing's; the commits up to then that touched the test its
/// settling names.
///
/// # Errors
///
/// No git to run, or git output that is not UTF-8: the Python's raise.
pub fn candidates(root: &Path, fix: &Row) -> Result<Vec<String>, Raised> {
    let mut out: Vec<String> = Vec::new();
    let note = or_s(fix, "note");
    if let Some(c) = re(r"^\s*([0-9a-f]{7,40})\b").captures(&note).ok().flatten() {
        // `git cat-file -e <hash>^{commit}`'s question, asked as `rev-parse --verify`, which answers the same and prints the commit
        if !git(
            root,
            &[
                "rev-parse",
                "--verify",
                "--quiet",
                &format!("{}^{{commit}}", &c[1]),
            ],
        )?
        .is_empty()
        {
            out.push(c[1].to_owned());
        }
    }
    let until: Vec<String> = if fix.get("settled").is_some_and(truthy) {
        vec![format!("--until={}", py_str(&fix["settled"]))]
    } else {
        Vec::new()
    };
    let trigger: String = or_s(fix, "trigger")
        .chars()
        .map(|c| {
            if c.is_alphanumeric() || "-:@/#_ ,=".contains(c) {
                c.to_string()
            } else if c == '^' {
                "\\^".to_owned()
            } else {
                format!("[{c}]")
            }
        })
        .collect();
    let found: Vec<String> = if trigger.is_empty() {
        Vec::new()
    } else {
        let grep = format!("--grep={trigger}([^0-9]|$)");
        let mut args = vec!["log", "-20", "--format=%h %s"];
        args.extend(until.iter().map(String::as_str));
        args.extend(["-E", &grep, "HEAD"]);
        splitlines(&git(root, &args)?)
            .into_iter()
            .map(str::to_owned)
            .collect()
    };
    let landing = |line: &str| {
        line.split_once(' ')
            .map_or(line, |(_, s)| s)
            .starts_with("Tooling from ")
    };
    let sha = |line: &str| line.split(' ').next().unwrap_or_default().to_owned();
    out.extend(found.iter().filter(|l| !landing(l)).map(|l| sha(l)));
    out.extend(found.iter().filter(|l| landing(l)).map(|l| sha(l)));
    if fix.get("test").is_some_and(truthy) && fix.get("utc").is_some_and(truthy) {
        // between its ruling and its settling only: a test's older commits made other things
        let since = format!("--since={}", py_str(&fix["utc"]));
        let test = py_str(&fix["test"]);
        let mut args = vec!["log", "-5", "--format=%h", &since];
        args.extend(until.iter().map(String::as_str));
        args.extend(["HEAD", "--", &test]);
        out.extend(split(&git(root, &args)?).into_iter().map(str::to_owned));
    }
    let mut seen = BTreeSet::new();
    out.retain(|s| seen.insert(s.clone()));
    Ok(out)
}

/// The tools of the first candidate commit that changed code; one holding only records is passed over, and code that is no tool's
/// reads as no tool found. With no commit found, the `scripts/` files and `make` targets its settling note names.
///
/// # Errors
///
/// As [`candidates`] and [`tools_of`].
pub fn tools_of_fix(root: &Path, fix: &Row) -> Result<BTreeSet<(String, String)>, Raised> {
    for sha in candidates(root, fix)? {
        let files: Vec<String> = split(&git(root, &["show", "--name-only", "--format=", &sha])?)
            .into_iter()
            .map(str::to_owned)
            .collect();
        if files
            .iter()
            .any(|f| !RECORDS.iter().any(|r| f.starts_with(r)))
        {
            let diff = git(root, &["show", "-U0", "--format=", &sha, "--", "Makefile"])?;
            return tools_of(root, &files, &diff);
        }
    }
    let note = or_s(fix, "note");
    let mut made = BTreeSet::new();
    let words: Vec<String> = re(r"\bmake ([a-z][\w-]+)")
        .captures_iter(&note)
        .flatten()
        .map(|c| c[1].to_owned())
        .collect();
    for t in words {
        if targets(root)?.contains(&t) {
            made.insert(("target".to_owned(), t));
        }
    }
    let mut out = tools_of(root, &named_files(root, &note), "")?;
    out.extend(made);
    Ok(out)
}

fn walk(dir: &Path, out: &mut Vec<PathBuf>) {
    for e in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        out.push(e.path());
        // `rglob` does not follow a link to a directory (Python 3.13's `recurse_symlinks=False`)
        if e.file_type().is_ok_and(|t| t.is_dir()) {
            walk(&e.path(), out);
        }
    }
}

/// The `scripts/` files a settling note names, when no commit is found: `module.function`, `name.py` or `name.sh`.
#[must_use]
pub fn named_files(root: &Path, note: &str) -> Vec<String> {
    let mut words = BTreeSet::new();
    for pattern in [r"\b([\w-]+)\.(?:py|sh)\b", r"\b([a-z]\w+)\.[a-z_]\w*\(?"] {
        words.extend(
            re(pattern)
                .captures_iter(note)
                .flatten()
                .map(|c| c[1].to_owned()),
        );
    }
    let mut found = Vec::new();
    walk(&root.join("scripts"), &mut found);
    let mut out: Vec<String> = found
        .iter()
        .filter(|p| {
            p.extension().is_some_and(|x| x == "py" || x == "sh")
                && p.file_stem()
                    .is_some_and(|s| words.contains(s.to_string_lossy().as_ref()))
                && !p.components().any(|c| c.as_os_str() == "__pycache__")
        })
        .map(|p| p.strip_prefix(root).unwrap_or(p).display().to_string())
        .collect();
    out.sort();
    out
}

/// One fix's reading and its tools' numbers since it was made (D165, D166).
///
/// # Errors
///
/// A made fix whose settling time `fromisoformat` cannot read: the Python's `ValueError`.
pub fn verdict(
    fix: &Row,
    tools: &[(&(String, String), &Tally)],
    now: f64,
) -> Result<Value, Raised> {
    let mut row =
        json!({"trigger": fix.get("trigger"), "fix_minutes": fix.get("fix_minutes"), "tools": []});
    if fix.get("status").and_then(Value::as_str) != Some("done") {
        let status = fix.get("status").map_or_else(|| "None".to_owned(), py_str);
        row["reading"] = json!(format!("not made ({status})"));
        return Ok(row);
    }
    let made = ts_of(&Value::String(py_str(&fix["settled"])))?;
    let mut t = Vec::new();
    for ((kind, name), tool) in tools {
        let (uses, hits, misses) = tool.since(made);
        let recorded = tool.outcome_record && tool.first != 0.0;
        t.push(json!({"kind": kind, "name": name, "first": tool.first, "uses": uses, "hits": hits, "misses": misses, "recorded": recorded}));
    }
    let n = |x: &Value, k: &str| x[k].as_i64().unwrap_or(0);
    let reading = if now - made < 7.0 * DAY {
        "too new to say".to_owned()
    } else if t.iter().any(|x| {
        let net = if x["kind"] == "check" || x["kind"] == "step" {
            0
        } else {
            n(x, "misses")
        };
        n(x, "hits") - net > 0
    }) {
        "doing something".to_owned()
    } else if t.is_empty() || t.iter().any(|x| x["recorded"] == false) {
        format!(
            "no outcome record{}",
            if t.is_empty() {
                " (no tool found in its settling commit)"
            } else {
                ""
            }
        )
    } else if t
        .iter()
        .any(|x| now - x["first"].as_f64().unwrap_or(0.0) < 7.0 * DAY)
    {
        "record too new".to_owned()
    } else {
        "doing nothing".to_owned()
    };
    row["tools"] = Value::Array(t);
    row["made"] = json!(made);
    row["reading"] = json!(reading);
    Ok(row)
}

/// `time.strftime("%Y-%m-%d", time.gmtime(t)) if t else "-"`: the seconds floored, as `gmtime` floors them.
fn day(t: f64) -> String {
    if t == 0.0 {
        return "-".to_owned();
    }
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "seconds since the epoch, after it"
    )]
    let (y, m, d, ..) = civil(t.floor().max(0.0) as u64);
    format!("{y:04}-{m:02}-{d:02}")
}

#[must_use]
pub fn table(rows: &[Value]) -> String {
    let mut lines = vec![
        "| fix (trigger) | made | cost ruled (min) | reading | its tools since it was made: uses / interventions / likely misfires |".to_owned(),
        "|---|---|---|---|---|".to_owned(),
    ];
    for r in rows {
        let tools: Vec<String> = r["tools"]
            .as_array()
            .into_iter()
            .flatten()
            .map(|x| {
                let checky = x["kind"] == "check" || x["kind"] == "step";
                let numbers = if x["recorded"] == true {
                    let misses = if checky {
                        "no outcome record".to_owned()
                    } else {
                        x["misses"].to_string()
                    };
                    format!("{} / {} / {misses}", x["uses"], x["hits"])
                } else {
                    "no outcome record".to_owned()
                };
                format!(
                    "{} {} (first seen {}): {numbers}",
                    py_str(&x["kind"]),
                    py_str(&x["name"]),
                    day(x["first"].as_f64().unwrap_or(0.0))
                )
            })
            .collect();
        let minutes = if r["fix_minutes"].is_null() {
            "-".to_owned()
        } else {
            py_str(&r["fix_minutes"])
        };
        let tools = if tools.is_empty() {
            "-".to_owned()
        } else {
            tools.join("; ")
        };
        lines.push(format!(
            "| {} | {} | {minutes} | {} | {tools} |",
            py_str(&r["trigger"]),
            day(r.get("made").and_then(Value::as_f64).unwrap_or(0.0)),
            py_str(&r["reading"])
        ));
    }
    lines.join("\n")
        + "\n\n(the numbers are `make tool-yield`'s, counted from each fix's settling; an intervention is a refusal, a rewrite, a finding or a failed run)\n"
}

/// The yield table of a feature's fixes, read from its arbiter record and `make tool-yield`'s numbers.
///
/// # Errors
///
/// A record that cannot be read, or any raise of the readers above.
pub fn report(
    root: &Path,
    feature_dir: &Path,
    now: f64,
    guard_log: &Path,
) -> Result<String, Raised> {
    let fx = fixes(&lines(&feature_dir.join("arbiter.jsonl"))?);
    if fx.is_empty() {
        return Ok("(no tooling fix ruled)\n".to_owned());
    }
    let every: Tools = collect(root, guard_log)?;
    let mut rows = Vec::new();
    for f in &fx {
        let keys = if f.get("status").and_then(Value::as_str) == Some("done") {
            tools_of_fix(root, f)?
        } else {
            BTreeSet::new()
        };
        let tools: Vec<_> = keys.iter().filter_map(|k| every.get_key_value(k)).collect();
        rows.push(verdict(f, &tools, now)?);
    }
    Ok(table(&rows))
}

/// `Path.resolve()`: absolute, each link resolved as far as the path exists, `..` taken lexically past it.
#[must_use]
pub fn resolve(path: &Path) -> PathBuf {
    let whole = std::env::current_dir().unwrap_or_default().join(path);
    let mut out = PathBuf::from("/");
    for c in whole.components() {
        match c {
            Component::ParentDir => {
                out.pop();
            }
            Component::Normal(name) => {
                out.push(name);
                if out.is_symlink() {
                    if let Ok(real) = std::fs::canonicalize(&out) {
                        out = real;
                    }
                }
            }
            _ => {}
        }
    }
    out
}

/// `l7r-gate measure fix-yield <feature> [--root ROOT]`.
#[must_use]
pub fn cli(args: &[String], home: &Path) -> Reply {
    let p = match parse_with(args, &[Spec::value("--root")], 1) {
        Ok(p) if !p.positional.is_empty() => p,
        Ok(_) => return usage("the following arguments are required: feature"),
        Err(why) => return usage(&why),
    };
    let feature = &p.positional[0];
    let root = resolve(Path::new(p.text("--root", ".")));
    let mut dirs: Vec<PathBuf> = std::fs::read_dir(root.join("specs"))
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| {
            e.file_name()
                .to_string_lossy()
                .starts_with(feature.as_str())
        })
        .map(|e| e.path())
        .collect();
    dirs.sort();
    if dirs.len() != 1 {
        return reply(
            String::new(),
            format!("fix-yield: no single specs/{feature}* directory\n"),
            2,
        );
    }
    match report(
        &root,
        &dirs[0],
        super::tool_yield::now(),
        &home.join(".claude/guard-log"),
    ) {
        Ok(text) => reply(text, String::new(), 0),
        Err(why) => reply(
            String::new(),
            format!("Traceback (most recent call last):\n  l7r-gate measure fix-yield\n{why}\n"),
            1,
        ),
    }
}

fn usage(why: &str) -> Reply {
    reply(
        String::new(),
        format!("usage: l7r-gate measure fix-yield [--root ROOT] feature\nl7r-gate measure fix-yield: error: {why}\n"),
        2,
    )
}

#[cfg(test)]
mod tests;
