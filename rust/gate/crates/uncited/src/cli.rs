//! `l7r-gate record uncited <command>` (feature 449 T147): `uncited.py`'s command line, which `make uncited DO=...` and `make cite-uncited`
//! run - its subcommands, flags and refusals read as its argparse read them (`ask:449-usage-text`: a refusal's words are the port's, its
//! exit 2 and empty stdout the Python's).
//!
//! - `set [--write FILE]`, `rule`, `fetch [--limit N] [--workers N]`, `bundle OUT [--limit N] [--start N]`, `apply DIR ...`,
//!   `score DIR ANSWERS`, `report`
//! - `verify [--limit N] [--sample N] [--all-imported] [--workers N]`, `copy-verdicts`, `stands URL NOTE` (`uncited_imports.py`'s)
//! - `draft OUT [--start N]`, `install DIR ...`, `cite KEY`, `merge KEY INTO`, `unkeep URL REASONS NOTE`, `dedupe [--dry]`,
//!   `requeue URL`, `retire-cited KEY ACCESS NOTE`

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_gate_archive::ops::{head, py_int};
use l7r_gate_core::record::args::{parse_with, Parsed, Spec};
use l7r_guard::shared::consulted;
use l7r_guard::shared::pyjson::dumps;

use crate::bundles::{apply, bundle, draft_bundles, score, Contracts};
use crate::dupes::dedupe;
use crate::entries::{cite, install, merge, report, requeue, retire_cited, Reserve};
use crate::fetch::{fetch_all, Start};
use crate::imports::{copy_verdicts, imported, imported_urls, stands, verify_all};
use crate::lists::{field, get, read, unkeep};
use crate::rule::{needs_fetch, no_substance, rule, wellformed};
use crate::set::uncited_set;
use crate::{loads, read_text, write_text, Error, Reply, Result, KEPT, MISFILED, NOT_KEPT};

/// What the commands reach beyond the record: the browser, where a lane's lines go as they are said, the reservation `install` makes,
/// and the tree whose contracts the bundles copy (the real ones in [`cli`], a test's stand-ins otherwise).
pub struct Reach<'a> {
    pub start: &'a Start,
    pub say: &'a (dyn Fn(&str) + Sync),
    pub reserve: &'a Reserve,
    pub tree: PathBuf,
}

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// argparse's refusal: exit 2, one line.
fn usage(said: &str) -> Reply {
    reply(
        String::new(),
        format!("l7r-gate record uncited: error: {said}\n"),
        2,
    )
}

/// A raise: what was printed before it, and the exception's one line (the Python's traceback, `ask:449-usage-text`).
fn raised(stdout: String, stderr: &str, e: &Error) -> Reply {
    reply(stdout, format!("{stderr}{e}\n"), 1)
}

/// The subcommands: each one's flags (`int` ones named apart) and how many positionals it takes (`usize::MAX`: one or more).
fn grammar(verb: &str) -> Option<(Vec<Spec>, &'static [&'static str], usize)> {
    let v = Spec::value;
    Some(match verb {
        "set" => (vec![v("--write")], &[], 0),
        "rule" | "report" | "copy-verdicts" => (vec![], &[], 0),
        "fetch" => (
            vec![v("--limit"), v("--workers")],
            &["--limit", "--workers"],
            0,
        ),
        "bundle" => (vec![v("--limit"), v("--start")], &["--limit", "--start"], 1),
        "apply" | "install" => (vec![], &[], usize::MAX),
        "score" | "merge" | "stands" => (vec![], &[], 2),
        "verify" => (
            vec![
                v("--limit"),
                v("--sample"),
                Spec::flag("--all-imported"),
                v("--workers"),
            ],
            &["--limit", "--sample", "--workers"],
            0,
        ),
        "draft" => (vec![v("--start")], &["--start"], 1),
        "cite" | "requeue" => (vec![], &[], 1),
        "unkeep" | "retire-cited" => (vec![], &[], 3),
        "dedupe" => (vec![Spec::flag("--dry")], &[], 0),
        _ => return None,
    })
}

/// The names argparse gives each positional, for its "required" refusal.
fn positional_names(verb: &str) -> &'static str {
    match verb {
        "bundle" | "draft" => "out",
        "apply" | "install" => "dirs",
        "score" => "dir, answers",
        "cite" => "key",
        "merge" => "key, into",
        "unkeep" => "url, reasons, note",
        "requeue" => "url",
        "retire-cited" => "key, access, note",
        _ => "url, note",
    }
}

/// An `int` flag's value (its default where it is not given).
fn int(p: &Parsed, name: &str, default: i64) -> i64 {
    py_int(p.text(name, "")).unwrap_or(default)
}

/// `l7r-gate record uncited <args>` from `cwd`'s repository: the real browser, lines printed as they are said, the reservation `record`
/// hands in.
#[cfg(not(test))]
#[must_use]
pub fn cli(args: &[String], cwd: &Path, reserve: &Reserve) -> Reply {
    let reach = Reach {
        start: &|root: &Path| l7r_gate_archive::cli::start_browser(root),
        say: &l7r_gate_archive::cli::print_now,
        reserve,
        tree: l7r_gate_core::record::repo::tree_of(&consulted::repo_root(Some(cwd))),
    };
    cli_with(args, cwd, &reach)
}

/// [`cli`] with what it reaches handed in.
#[must_use]
pub fn cli_with(args: &[String], cwd: &Path, reach: &Reach<'_>) -> Reply {
    let Some(verb) = args.first() else {
        return usage("the following arguments are required: cmd");
    };
    let Some((specs, ints, n)) = grammar(verb) else {
        return usage(&format!("argument cmd: invalid choice: '{verb}'"));
    };
    let p = match parse_with(&args[1..], &specs, n) {
        Ok(p) => p,
        Err(e) => return usage(&e),
    };
    let wanted = if n == usize::MAX { 1 } else { n };
    if p.positional.len() < wanted {
        return usage(&format!(
            "the following arguments are required: {}",
            positional_names(verb)
        ));
    }
    for name in ints {
        if p.has(name) && py_int(p.text(name, "")).is_none() {
            return usage(&format!(
                "argument {name}: invalid int value: '{}'",
                p.text(name, "")
            ));
        }
    }
    let root = consulted::repo_root(Some(cwd));
    let mut out = String::new();
    let mut err = String::new();
    match run(verb, &p, cwd, &root, reach, &mut out, &mut err) {
        Ok(()) => reply(out, err, 0),
        Err(mut e) => {
            // a bundle named relative to where the command ran is named so in a refusal too, as the Python opened it from there
            let relative = matches!(verb.as_str(), "apply" | "score" | "install")
                && p.positional.iter().all(|d| Path::new(d).is_relative());
            if relative {
                e.message = e.message.replace(&format!("{}/", cwd.display()), "");
            }
            raised(out, &err, &e)
        }
    }
}

/// `dest.relative_to(root)`, or its `ValueError` (the record's base moved off the root, `L7R_ATTEMPTS_ROOT`).
///
/// # Errors
/// `dest` is not under `root`.
pub fn relative<'a>(dest: &'a Path, root: &Path) -> Result<&'a Path> {
    dest.strip_prefix(root).map_err(|_| {
        Error::new(
            "ValueError",
            format!(
                "'{}' is not in the subpath of '{}'",
                dest.display(),
                root.display()
            ),
        )
    })
}

/// A command-line path, read from `cwd` as the Python's relative paths were.
fn at(cwd: &Path, p: &str) -> PathBuf {
    cwd.join(p)
}

#[expect(
    clippy::too_many_lines,
    reason = "uncited.py's `main`: one arm a subcommand, in its order"
)]
fn run(
    verb: &str,
    p: &Parsed,
    cwd: &Path,
    root: &Path,
    reach: &Reach<'_>,
    out: &mut String,
    err: &mut String,
) -> Result<()> {
    let pos = |i: usize| p.positional.get(i).map_or("", String::as_str);
    let home = consulted::home(root);
    let contracts = Contracts {
        tree: reach.tree.clone(),
    };
    match verb {
        "set" => {
            let urls = uncited_set(root)?;
            let write = p.text("--write", "");
            if !write.is_empty() {
                write_text(&at(cwd, write), &(urls.join("\n") + "\n"))?;
            }
            let _ = writeln!(out, "uncited: {} page(s) in the set", urls.len());
        }
        "rule" => {
            let counts = rule(root, &uncited_set(root)?)?;
            let _ = writeln!(out, "uncited: the rule - {}", dumps(&counts, None, true));
        }
        "fetch" => {
            let mut urls = Vec::new();
            for u in uncited_set(root)? {
                if !no_substance(&u) && wellformed(&u) && needs_fetch(&home, &u)? {
                    urls.push(u);
                }
            }
            let limit = int(p, "--limit", 0);
            let urls = if limit == 0 { urls } else { head(&urls, limit) };
            let workers = int(p, "--workers", 4);
            (reach.say)(&format!(
                "uncited: fetching {} page(s) in up to {workers} lane(s)",
                urls.len()
            ));
            let total = fetch_all(root, &urls, workers, reach.start, reach.say)?;
            let _ = writeln!(out, "uncited: {}", dumps(&total, None, true));
        }
        "bundle" => {
            let urls = uncited_set(root)?;
            let limit = int(p, "--limit", 0);
            let urls = if limit == 0 { urls } else { head(&urls, limit) };
            let dirs = bundle(
                root,
                &urls,
                &at(cwd, pos(0)),
                int(p, "--start", 1),
                &contracts,
            )?;
            let _ = writeln!(out, "uncited: {} bundle(s) under {}", dirs.len(), pos(0));
        }
        "apply" => {
            for d in &p.positional {
                let counts = apply(root, &at(cwd, d), out)?;
                let _ = writeln!(out, "uncited: {d} - {}", dumps(&counts, None, true));
            }
        }
        "score" => {
            let answers = loads(&read_text(&at(cwd, pos(1)))?)?;
            let _ = writeln!(
                out,
                "{}",
                dumps(&score(&at(cwd, pos(0)), &answers)?, None, true)
            );
        }
        "verify" => {
            let mut judged = Vec::new();
            for x in read(root, KEPT)? {
                judged.push(field(&x, "raw")?);
            }
            for x in read(root, NOT_KEPT)? {
                if get(&x, "basis")?.and_then(serde_json::Value::as_str) == Some("source-filter") {
                    judged.push(field(&x, "raw")?);
                }
            }
            let done = crate::lists::urls_of(&read(root, MISFILED)?)?;
            let pool = if p.on("--all-imported") {
                imported_urls(&home)?
            } else {
                judged
            };
            let mut todo = Vec::new();
            let mut seen = std::collections::HashSet::new();
            for u in pool {
                if seen.insert(u.clone())
                    && !done.contains(&l7r_guard::shared::consulted::norm(&u))
                    && imported(&home, &u)?.is_some()
                    && wellformed(&u)
                {
                    todo.push(u);
                }
            }
            let sample = int(p, "--sample", 0);
            if sample != 0 {
                let mut t = crate::random::Twister::seeded(312);
                todo = crate::random::sample(
                    &mut t,
                    &todo,
                    sample.min(i64::try_from(todo.len()).unwrap_or(i64::MAX)),
                )?;
            }
            let limit = int(p, "--limit", 0);
            let todo = if limit == 0 { todo } else { head(&todo, limit) };
            let workers = int(p, "--workers", 3);
            (reach.say)(&format!(
                "uncited: verifying {} imported cop(ies) in up to {workers} lane(s)",
                todo.len()
            ));
            let total = verify_all(root, &todo, workers, reach.start, reach.say)?;
            let _ = writeln!(out, "uncited: {}", dumps(&total, None, true));
        }
        "draft" => {
            let retired = dedupe(root, false)?
                .iter()
                .filter(|d| !d.contains(" ~ "))
                .count();
            let dirs = draft_bundles(root, &at(cwd, pos(0)), int(p, "--start", 1), &contracts)?;
            let _ = writeln!(
                out,
                "uncited: {retired} duplicate(s) retired first; {} draft bundle(s) under {}",
                dirs.len(),
                pos(0)
            );
        }
        "cite" => {
            let dest = cite(root, pos(0))?;
            let rel = relative(&dest, root)?;
            let _ = writeln!(
                out,
                "uncited: {} moved to {} - write its Used for: line (the build refuses the placeholder), then `git add -A` the move",
                pos(0),
                rel.display()
            );
        }
        "dedupe" => {
            let dry = p.on("--dry");
            let done = dedupe(root, dry)?;
            let verb = if dry { "would be retired" } else { "retired" };
            let (read_pairs, gone): (Vec<&String>, Vec<&String>) =
                done.iter().partition(|d| d.contains(" ~ "));
            let mut shown: Vec<String> = gone
                .iter()
                .map(|d| format!("uncited: duplicate {verb} - {d}"))
                .collect();
            shown.extend(read_pairs.iter().map(|d| format!("uncited: to read - {d}")));
            let _ = writeln!(
                out,
                "{}\nuncited: {} duplicate(s) {verb}, {} similar pair(s) to read",
                shown.join("\n"),
                gone.len(),
                read_pairs.len()
            );
        }
        "retire-cited" => {
            let gone = retire_cited(root, pos(0), pos(1), pos(2))?;
            let _ = writeln!(
                out,
                "uncited: {} left the works cited ({} removed), not kept as unreadable ({}), its state recorded",
                pos(0),
                crate::name_of(&gone),
                pos(1)
            );
        }
        "copy-verdicts" => {
            let found = copy_verdicts(root)?;
            let _ = writeln!(
                out,
                "{}\nuncited: {} verdict(s) blame a saved copy on a page now read live - read each; requeue a readable one with `make \
                 uncited DO=requeue URL=<u>`, or `make uncited DO=stands URL=<u> NOTE=<why>`",
                found.join("\n"),
                found.len()
            );
        }
        "stands" => {
            stands(root, pos(0), pos(1))?;
            let _ = writeln!(out, "uncited: {} - its verdict stands ({})", pos(0), pos(1));
        }
        "requeue" => {
            let key = requeue(root, pos(0))?;
            let retired = key.map_or_else(String::new, |k| format!(", its entry {k} retired"));
            let _ = writeln!(out, "uncited: {} requeued - its verdict cleared{retired}; `make uncited DO=bundle` judges it again", pos(0));
        }
        "unkeep" => {
            let reasons: Vec<String> = pos(1).split(',').map(str::to_owned).collect();
            unkeep(root, pos(0), &reasons, "session", pos(2))?;
            let _ = writeln!(
                out,
                "uncited: {} moved to the not-kept list ({})",
                pos(0),
                pos(1)
            );
        }
        "merge" => {
            let gone = merge(root, pos(0), pos(1))?;
            let _ = writeln!(
                out,
                "uncited: {} retired ({}) as a duplicate of {}; its page is on the not-kept list",
                pos(0),
                crate::name_of(&gone),
                pos(1)
            );
        }
        "install" => {
            for d in &p.positional {
                let counts = install(root, &at(cwd, d), reach.reserve, err)?;
                let _ = writeln!(out, "uncited: {d} - {}", dumps(&counts.json(), None, true));
            }
        }
        _ => {
            let _ = writeln!(out, "{}", report(root)?);
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests;
