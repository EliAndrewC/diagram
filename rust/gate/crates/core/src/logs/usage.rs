//! The shell's and Python's door to the tool-usage log and the escape reason floor (feature 449 T129, from `usage_log.py`'s and
//! `hm_escape.py`'s command lines): `l7r-gate log usage`, `l7r-gate log goals` and `l7r-gate escape reason-ok`, each over the guard's one
//! implementation (`shared::usage`, `shared::escape`), since the guard crate cannot build on the gate and the shell cannot reach the
//! guard's functions but by a command.

use std::io::Read;
use std::path::Path;

use l7r_guard::shared::{escape, py_text, usage};

use crate::Reply;

const KINDS: [&str; 4] = ["step", "check", "hook", "target"];
const USAGE: &str = "usage: l7r-gate log usage --tool <name> --kind {step,check,hook,target} --outcome OUTCOME [--root ROOT]";

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// An argparse refusal: exit 2, nothing on stdout, one line naming the verb and the complaint (`ask:449-usage-text`).
fn refused(why: &str) -> Reply {
    reply(
        String::new(),
        format!("l7r-gate log usage: error: {why}\n"),
        2,
    )
}

/// The option `arg` names, as argparse resolves a long option: its exact name, or the one option it is a prefix of.
fn option(arg: &str) -> Result<&'static str, String> {
    // `--tool` last: `check tool-signals` reads a `"--tool", "<word>"` pair as a tool this file records
    const NAMES: [&str; 5] = ["--help", "--kind", "--outcome", "--root", "--tool"];
    if let Some(exact) = NAMES.iter().find(|n| **n == arg) {
        return Ok(exact);
    }
    let hits: Vec<&&str> = NAMES
        .iter()
        .filter(|n| arg.len() > 2 && n.starts_with(arg))
        .collect();
    // no two of the five share a prefix past `--`, so a prefix names one option or none
    match hits.as_slice() {
        [one] => Ok(one),
        _ => Err(format!("unrecognized arguments: {arg}")),
    }
}

/// Whether argparse reads `word` as an option rather than a value: a leading `-` and not a negative number.
fn looks_optional(word: &str) -> bool {
    word.starts_with('-') && word.len() > 1 && word[1..].parse::<f64>().is_err()
}

/// `usage_log.py record --tool <name> --kind <step|check|hook|target> --outcome <word> [--root <dir>]`, the root the working
/// directory's repository when none (or an empty one) is given; every refusal argparse made is exit 2.
#[must_use]
pub fn record_cli(args: &[String], cwd: &Path) -> Reply {
    let (mut tool, mut kind, mut outcome, mut root) = (None, None, None, None);
    let mut at = 0;
    while at < args.len() {
        let arg = &args[at];
        let (name, inline) = match arg.split_once('=') {
            Some((n, v)) if n.starts_with("--") => (n, Some(v.to_owned())),
            _ => (arg.as_str(), None),
        };
        if name == "-h" {
            return reply(format!("{USAGE}\n"), String::new(), 0);
        }
        if !name.starts_with("--") {
            return refused(&format!("unrecognized arguments: {arg}"));
        }
        let which = match option(name) {
            Ok(w) => w,
            Err(why) => return refused(&why),
        };
        if which == "--help" {
            return reply(format!("{USAGE}\n"), String::new(), 0);
        }
        let value = if let Some(v) = inline {
            v
        } else {
            at += 1;
            match args.get(at) {
                Some(v) if !looks_optional(v) => v.clone(),
                _ => return refused(&format!("argument {which}: expected one argument")),
            }
        };
        match which {
            "--tool" => tool = Some(value),
            "--kind" if !KINDS.contains(&value.as_str()) => {
                return refused(&format!("argument --kind: invalid choice: '{value}'"))
            }
            "--kind" => kind = Some(value),
            "--outcome" => outcome = Some(value),
            _ => root = Some(value),
        }
        at += 1;
    }
    let missing: Vec<&str> = [
        ("--tool", &tool),
        ("--kind", &kind),
        ("--outcome", &outcome),
    ]
    .iter()
    .filter(|(_, v)| v.is_none())
    .map(|(n, _)| *n)
    .collect();
    if !missing.is_empty() {
        return refused(&format!(
            "the following arguments are required: {}",
            missing.join(", ")
        ));
    }
    let root = root.filter(|r| !r.is_empty());
    usage::record(
        root.as_deref().map_or(cwd, Path::new),
        tool.as_deref().unwrap_or_default(),
        kind.as_deref().unwrap_or_default(),
        outcome.as_deref().unwrap_or_default(),
    );
    reply(String::new(), String::new(), 0)
}

/// `usage_log.py goals <goal>...`: each make goal recorded `ran` in the working directory's repository (the Makefile's parse-time line,
/// feature 406 D161).
#[must_use]
pub fn goals_cli(args: &[String], cwd: &Path) -> Reply {
    for goal in args {
        usage::record(cwd, goal, "target", "ran");
    }
    reply(String::new(), String::new(), 0)
}

/// Stdin as the Python read it under this container's `C.UTF-8` locale, whose stdin decodes with `surrogateescape`: each byte UTF-8
/// cannot take is one character of its own, never whitespace or a word separator (here U+FFFD, standing in for its surrogate).
fn surrogate_escaped(raw: &[u8]) -> String {
    let mut text = String::new();
    for chunk in raw.utf8_chunks() {
        text.push_str(chunk.valid());
        text.extend(chunk.invalid().iter().map(|_| '\u{fffd}'));
    }
    text
}

/// `l7r-gate escape reason-ok`: exit 0 when stdin, stripped as Python strips, clears the reason floor, else 1 (`hm_escape.py
/// reason-ok`); a stdin that cannot be read fails with 1, as the Python's read of it raised.
pub fn escape_cli(args: &[String], stdin: &mut dyn Read) -> Reply {
    if args.first().map(String::as_str) != Some("reason-ok") {
        return reply(
            String::new(),
            "usage: l7r-gate escape reason-ok   (the reason on stdin)\n".to_owned(),
            2,
        );
    }
    let mut raw = Vec::new();
    if let Err(e) = stdin.read_to_end(&mut raw) {
        return reply(
            String::new(),
            format!("l7r-gate escape reason-ok: stdin: {e}\n"),
            1,
        );
    }
    let ok = escape::enough(py_text::strip(&surrogate_escaped(&raw)));
    reply(String::new(), String::new(), i32::from(!ok))
}

#[cfg(test)]
mod tests;
