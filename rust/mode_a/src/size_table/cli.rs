//! `make size-table PLAN=<svg>`'s command (feature 449 T174): `l7r-mode-a size-table <plan> [--json PATH]`, the Python script's
//! `argparse` and `main` reproduced - the table printed, then the sized marks, then the JSON written, each step's failure ending the run
//! where the Python's ended it (what was printed before it stays printed).
//!
//! Research:
//!     the size table's command - NONE: its arguments read and its two sections printed, deciding nothing about a building

use std::path::Path;

use l7r_gate_core::Reply;
use l7r_gate_research::Error;
use l7r_shared::py_text::repr;

use super::{render, table, to_json};
use crate::py::{os_error, uncaught};
use crate::size_marks;

const PROG: &str = "l7r-mode-a size-table";
const USAGE: &str = "usage: l7r-mode-a size-table [-h] [--json JSON] plan\n";
const HELP: &str = "
Every drawn thing on a Mode A plan, in feet, for `size-audit` (feature 251,
FR-006).

positional arguments:
  plan         the plan's SVG

options:
  -h, --help   show this help message and exit
  --json JSON
";

/// What the arguments ask.
#[derive(Debug, PartialEq)]
enum Ask {
    Help,
    Refused(String),
    Run { plan: String, json: String },
}

/// argparse's taking of an argument as an option: a dash and more, not a negative number, not a phrase with a space - unless it names an
/// option itself.
fn optional(arg: &str) -> bool {
    let negative = arg.strip_prefix('-').is_some_and(|n| {
        let (int, frac) = n.split_once('.').unwrap_or((n, ""));
        let digits = |s: &str| s.bytes().all(|b| b.is_ascii_digit());
        digits(int) && digits(frac) && (!frac.is_empty() || (!int.is_empty() && !n.contains('.')))
    });
    let known = (arg.starts_with("--") && long(arg.split('=').next().unwrap_or(arg)).is_some())
        || arg.starts_with("-h");
    arg.starts_with('-') && arg.len() > 1 && (known || !(negative || arg.contains(' ')))
}

/// A long option, exact or by a unique prefix (argparse's `allow_abbrev`); `--` itself prefixes both.
fn long(word: &str) -> Option<&'static str> {
    ["--help", "--json"]
        .into_iter()
        .find(|o| word.len() > 2 && o.starts_with(word))
}

/// The Python's `argparse` over `plan` and `--json` (observed 2026-11-17 in `CPython` 3.14.4's argparse, 57 argument forms): a malformed
/// option refused at once, `-h` anywhere before that asking for the help, then a missing plan, then what was not recognized.
fn parse(args: &[String]) -> Ask {
    let (mut plan, mut json, mut extras) = (None::<String>, String::new(), Vec::new());
    let mut positional = |arg: &String, extras: &mut Vec<String>| {
        if plan.is_none() {
            plan = Some(arg.clone());
        } else {
            extras.push(arg.clone());
        }
    };
    let mut rest = args.iter();
    let mut dashed = false;
    while let Some(arg) = rest.next() {
        if !dashed && arg == "--" {
            // the first `--` ends the options and is dropped; a later one is a positional
            dashed = true;
            continue;
        }
        if dashed || !optional(arg) {
            positional(arg, &mut extras);
            continue;
        }
        if let Some(flags) = arg.strip_prefix("-h") {
            // short flags run together: `-h` first prints the help, unless what follows is `=` or another dash (argparse's
            // "ignored explicit argument")
            return match flags.strip_prefix('=') {
                Some(v) => ignored(v),
                None if flags.starts_with('-') => ignored(flags),
                None => Ask::Help,
            };
        }
        let (word, inline) = arg
            .split_once('=')
            .map_or((arg.as_str(), None), |(w, v)| (w, Some(v)));
        if word == "--" {
            return Ask::Refused(format!(
                "ambiguous option: {arg} could match --help, --json"
            ));
        }
        match (long(word), inline) {
            (Some("--help"), None) => return Ask::Help,
            (Some("--help"), Some(v)) => return ignored(v),
            (Some(_), Some(v)) => v.clone_into(&mut json),
            (Some(_), None) => match rest.as_slice().first() {
                Some(v) if !optional(v) && v != "--" => {
                    json.clone_from(v);
                    rest.next();
                }
                _ => return Ask::Refused("argument --json: expected one argument".to_owned()),
            },
            (None, _) => extras.push(arg.clone()),
        }
    }
    let Some(plan) = plan else {
        return Ask::Refused("the following arguments are required: plan".to_owned());
    };
    if extras.is_empty() {
        Ask::Run { plan, json }
    } else {
        Ask::Refused(format!("unrecognized arguments: {}", extras.join(" ")))
    }
}

fn ignored(value: &str) -> Ask {
    Ask::Refused(format!(
        "argument -h/--help: ignored explicit argument {}",
        repr(value)
    ))
}

/// A path as Python's `pathlib.PurePosixPath` writes it: `.` components and repeated or trailing slashes dropped, a leading `//` kept
/// (POSIX leaves it to the system), nothing at all written `.`.
#[must_use]
pub fn pathlib(path: &str) -> String {
    let root = if path.starts_with("//") && !path.starts_with("///") {
        "//"
    } else if path.starts_with('/') {
        "/"
    } else {
        ""
    };
    let parts: Vec<&str> = path
        .split('/')
        .filter(|p| !p.is_empty() && *p != ".")
        .collect();
    let out = format!("{root}{}", parts.join("/"));
    if out.is_empty() {
        ".".to_owned()
    } else {
        out
    }
}

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// The command (`main`).
#[must_use]
pub fn main(args: &[String]) -> Reply {
    let (plan, json) = match parse(args) {
        Ask::Help => return reply(format!("{USAGE}{HELP}"), String::new(), 0),
        Ask::Refused(why) => {
            return reply(String::new(), format!("{USAGE}{PROG}: error: {why}\n"), 2)
        }
        Ask::Run { plan, json } => (pathlib(&plan), json),
    };
    if !Path::new(&plan).is_file() {
        return reply(
            String::new(),
            format!("size-table: no such plan - {plan}\n"),
            2,
        );
    }
    let mut out = String::new();
    match run(&plan, &json, &mut out) {
        Ok(()) => reply(out, String::new(), 0),
        Err(e) => reply(out, uncaught(&e), 1),
    }
}

/// The table, the marks and the JSON, `out` holding what was printed before a failure.
fn run(plan: &str, json: &str, out: &mut String) -> Result<(), Error> {
    let text = l7r_gate_core::record::read_text(Path::new(plan)).map_err(|e| os_error(&e, plan))?;
    let data = table(&text)?;
    let name = plan.rsplit('/').next().unwrap_or(plan);
    *out += &render(name, &data);
    out.push('\n');
    *out += &size_marks::render(&size_marks::mark_rows(&text)?);
    out.push('\n');
    if !json.is_empty() {
        let path = pathlib(json);
        std::fs::write(&path, to_json(&data)).map_err(|e| os_error(&e, &path))?;
    }
    Ok(())
}

#[cfg(test)]
mod tests;
