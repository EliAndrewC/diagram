//! `l7r-gate claim` - the next spec-kit feature number claimed under a host-wide lock: `make claim SLUG=<slug>` (feature 197), and
//! spec-kit's `create-new-feature.sh`. Ported whole from `scripts/claim-feature.py` by feature 449 T135 (`ask:449-phase3-remainder`).
//!
//! WHY (GM 2026-09-07): *"I believe that I have noticed there being times when two different sessions each end up claiming the same
//! spec kit feature number ... we could have a makefile target that selects the next feature number ... using some file locking or
//! other kind of multiprocess locking just to make sure that we always grab the next available feature number."* Measured before it
//! existed (specs/197/research.md R2): fourteen numbers claimed twice, eight renumber commits in a week; a sibling session's claim lived
//! in `<mirror>/.clones/<other>/specs/` until it pushed, and nothing read that directory.
//!
//! WHAT "NEXT AVAILABLE" MEANS. A number is taken when any of these holds it, all read UNDER THE LOCK: the mirror's working tree
//! `specs/` (main as this container last saw it), the mirror's `origin/main` tree (`git ls-tree`, fetched but not fast-forwarded; no
//! network), every clone's `specs/` under `<mirror>/.clones/` (the other sessions' unpushed claims), and the ledger of every claim this
//! tool made. Next is one more than the maximum. THE CLAIM IS THE DIRECTORY: `specs/NNN-slug/` is made in the caller's clone before the
//! lock is released, so the next caller's scan sees it.
//!
//! WHERE THE STATE LIVES, AND WHY IT NEEDS NO REGENERATING. The lock and the ledger sit under the mirror's `.specify/` (the host volume,
//! gitignored). The ledger is a record and a safety net, never the only source: the other three give the right number in every case but
//! a number claimed and then abandoned before any push, which only the ledger holds; with the ledger gone it is reused, which is
//! harmless (a number that never reached main identifies nothing). Nobody should "fix" that with a counter file, which WOULD need
//! regenerating (spec D1/D2).
//!
//! The lock is `flock` on a file (`core`'s [`flock_within`], the one `make download-add` takes too), so a shell holding `flock(1)` on
//! the same path serializes with it. No fetch happens under it: `sync-in` fetches main at every prompt (spec D4).
//!
//! Refusals (exit 2, nothing made, nothing appended): run from the mirror itself (main is never a workspace); a slug that is not
//! lower-case kebab; a slug already in use anywhere the scan reads; the lock not taken within the timeout (a held lock is a hung
//! process, not a queue). A number main holds twice is REPORTED on every claim and never renumbered by one (spec D3); `--renumber`
//! (`make claim RENUMBER=specs/NNN-slug`) is how the GM's call to renumber is carried out, under the same lock - the 195 duplicate's
//! resolution on 2026-09-07. The messages keep the Python's `claim-feature:` label, which the sessions and spec-kit read.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_core::record::args::{parse_with, Spec};
use l7r_gate_core::record::repo::{flock_within, mirror_of, utc_now};
use l7r_gate_core::Reply;
use l7r_guard::shared::checks::resolved;
use l7r_guard::shared::py_text::{fmt_g, py_float_text, repr, strip};
use l7r_guard::shared::pyjson::{dumps, py_str};
use l7r_guard::shared::speckit::{py_name, py_path, splitlines};
use serde_json::{json, Value};

use crate::{raised, read_strict, reply};

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

// Python's `$` also matches before a final newline, so `\n?\z` stands for it; `\d` read as ASCII digits (Python's would take any decimal
// digit, which no directory name here carries)
static SLUG: LazyLock<Regex> = LazyLock::new(|| re(r"^[a-z0-9]+(?:-[a-z0-9]+)*\n?\z"));
static NUMBERED: LazyLock<Regex> = LazyLock::new(|| re(r"^([0-9]{3,})-(.+)\n?\z"));
const LEDGER_NAME: &str = "feature-numbers.jsonl";
const LOCK_NAME: &str = "feature-numbers.lock";
const USAGE: &str = "usage: l7r-gate claim [-h] [--renumber specs/NNN-slug] [--dry-run] [--root ROOT] [--main MAIN] [--lock-timeout LOCK_TIMEOUT] [slug]\n";

/// Why a claim stopped: a refusal (exit 2, nothing written) or what the Python raised (exit 1).
enum Stop {
    Refusal(String),
    Raised(String),
}

fn raise<E: std::fmt::Display>(e: E) -> Stop {
    Stop::Raised(e.to_string())
}

/// `(number, name)` of a `NNN-<slug>` name.
fn numbered(name: &str) -> Option<(i128, String)> {
    let caps = NUMBERED.captures(name).ok()??;
    Some((caps[1].parse().ok()?, name.to_owned()))
}

/// `(number, name)` for every `NNN-*` directory under `specs`, in name order, or nothing when it does not exist.
fn numbered_dirs(specs: &Path) -> Vec<(i128, String)> {
    let mut names: Vec<(String, PathBuf)> = std::fs::read_dir(specs)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| (e.file_name().to_string_lossy().into_owned(), e.path()))
        .collect();
    names.sort();
    names
        .into_iter()
        .filter(|(_, p)| p.is_dir())
        .filter_map(|(n, _)| numbered(&n))
        .collect()
}

/// `specs/NNN-*` in the mirror's fetched `origin/main`: a packfile read, best effort (a mirror without the ref contributes nothing).
fn origin_main_dirs(mirror: &Path) -> Vec<(i128, String)> {
    let said = Command::new("git")
        .arg("-C")
        .arg(mirror)
        .args(["ls-tree", "--name-only", "origin/main", "specs/"])
        .output();
    let Some(out) = said.ok().filter(|o| o.status.success()) else {
        return Vec::new();
    };
    splitlines(&String::from_utf8_lossy(&out.stdout))
        .into_iter()
        .filter_map(|line| numbered(strip(line).split_once('/').map_or(strip(line), |(_, n)| n)))
        .collect()
}

/// `int(value)` of what `json.loads` made: an integer as it is, a float truncated, a bool one or zero, a string as `int(str)` reads it.
fn py_int(v: &Value) -> Result<i128, String> {
    match v {
        Value::Bool(b) => Ok(i128::from(*b)),
        Value::Number(n) => n.as_i64().map(i128::from).map_or_else(
            #[expect(
                clippy::cast_possible_truncation,
                reason = "Python's int() of a float truncates it"
            )]
            || Ok(n.as_f64().unwrap_or(0.0).trunc() as i128),
            Ok,
        ),
        Value::String(s) => {
            let t = strip(s).replace('_', "");
            t.parse().map_err(|_| {
                format!(
                    "ValueError: invalid literal for int() with base 10: {}",
                    repr(s)
                )
            })
        }
        _ => Err(
            "TypeError: int() argument must be a string, a bytes-like object or a real number"
                .to_owned(),
        ),
    }
}

/// Every ledger row's `(number, name)`, as `ledger_rows` and its reader in `collect` took them: a torn line skipped, `"number" in row`
/// asked of whatever the row is.
fn ledger(path: &Path) -> Result<Vec<(i128, String)>, String> {
    if !path.is_file() {
        return Ok(Vec::new());
    }
    let mut out = Vec::new();
    for line in splitlines(&read_strict(path)?) {
        // a torn line is not a reason to refuse every future claim
        let Ok(row) = serde_json::from_str::<Value>(strip(line)) else {
            continue;
        };
        let holds = match &row {
            Value::Object(m) => m.contains_key("number"),
            Value::Array(a) => a.iter().any(|v| v == "number"),
            Value::String(s) => s.contains("number"),
            _ => {
                return Err(format!(
                    "TypeError: argument of type '{}' is not iterable",
                    kind(&row)
                ))
            }
        };
        if !holds {
            continue;
        }
        let Value::Object(m) = &row else {
            return Err(format!(
                "TypeError: {} indices must be integers or slices, not str",
                kind(&row)
            ));
        };
        let n = py_int(&m["number"])?;
        let slug = m.get("slug").map_or_else(String::new, py_str);
        out.push((n, format!("{n:03}-{slug}")));
    }
    Ok(out)
}

/// The Python type name of a JSON value.
fn kind(v: &Value) -> &'static str {
    match v {
        Value::Null => "NoneType",
        Value::Bool(_) => "bool",
        Value::Number(n) if n.is_f64() => "float",
        Value::Number(_) => "int",
        Value::String(_) => "str",
        Value::Array(_) => "list",
        Value::Object(_) => "dict",
    }
}

/// Each source's name and the `(number, name)`s it holds.
type Sources = Vec<(&'static str, Vec<(i128, String)>)>;

/// Every source by its name, in the Python's order - read under the lock.
fn collect(root: &Path, mirror: &Path) -> Result<Sources, String> {
    let mut clones = Vec::new();
    let mut seen = BTreeSet::new();
    let mut each: Vec<PathBuf> = std::fs::read_dir(mirror.join(".clones"))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .collect();
    each.sort();
    for clone in each.into_iter().filter(|c| c.is_dir()) {
        seen.insert(resolved(&clone));
        clones.extend(numbered_dirs(&clone.join("specs")));
    }
    if !seen.contains(root) && root != mirror {
        // a root outside .clones/ (a fixture) still counts itself
        clones.extend(numbered_dirs(&root.join("specs")));
    }
    Ok(vec![
        ("main", numbered_dirs(&mirror.join("specs"))),
        ("origin/main", origin_main_dirs(mirror)),
        ("clones", clones),
        (
            "ledger",
            ledger(&mirror.join(".specify").join(LEDGER_NAME))?,
        ),
    ])
}

/// What one claim is asked.
struct Ask<'a> {
    slug: String,
    root: &'a Path,
    mirror: &'a Path,
    dry_run: bool,
    lock_timeout: f64,
    move_from: Option<PathBuf>,
}

/// The claim: its directory's name, or why it stopped; `err` holds what it printed on the way, as the Python's stderr did.
#[expect(
    clippy::too_many_lines,
    reason = "the Python's `claim`, one function, kept in its order"
)]
fn claim(ask: &Ask, err: &mut String) -> Result<String, Stop> {
    let (root, mirror) = (ask.root, ask.mirror);
    let mut slug = ask.slug.clone();
    let mut old_number = None;
    let moving = ask.move_from.as_deref().map(py_name);
    if let (Some(from), Some(name)) = (&ask.move_from, &moving) {
        let hit = numbered(name).filter(|_| root.join("specs").join(name).is_dir());
        let Some((n, _)) = hit else {
            return Err(Stop::Refusal(format!(
                "{} is not an existing specs/NNN-<slug>/ directory in {}",
                from.display(),
                root.display()
            )));
        };
        old_number = Some(n);
        slug = NUMBERED
            .captures(name)
            .ok()
            .flatten()
            .map_or_else(String::new, |c| c[2].to_owned());
    }
    if !SLUG.is_match(&slug).unwrap_or(false) {
        return Err(Stop::Refusal(format!(
            "slug {} is not lower-case kebab (letters, digits, single hyphens - the house style)",
            repr(&slug)
        )));
    }
    if root == mirror {
        return Err(Stop::Refusal(format!(
            "{} is the MIRROR - main is the integration point, never a workspace; run this from your session clone under {}/.clones/",
            root.display(),
            mirror.display()
        )));
    }
    let lock_path = mirror.join(".specify").join(LOCK_NAME);
    let Some(held) = flock_within(&lock_path, ask.lock_timeout).map_err(raise)? else {
        let shown = lock_path.display();
        return Err(Stop::Refusal(format!(
            "could not take the feature-number lock within {}s: {shown} is held by another process - a hung claim, not a queue; look at who holds it (fuser {shown})",
            fmt_g(ask.lock_timeout)
        )));
    };
    let sources = collect(root, mirror).map_err(raise)?;
    let mut by: BTreeMap<i128, BTreeSet<&str>> = BTreeMap::new();
    for (n, name) in &sources[0].1 {
        by.entry(*n).or_default().insert(name);
    }
    for (n, names) in by.iter().filter(|(_, v)| v.len() > 1) {
        let names: Vec<&str> = names.iter().copied().collect();
        let _ = writeln!(
            err,
            "claim-feature: WARNING - main holds {n:03} twice: {} (reported, never renumbered on a claim - spec 197 D3; `make claim RENUMBER=specs/<one of them>` moves it deliberately)",
            names.join(", ")
        );
    }
    let every: Vec<&(i128, String)> = sources.iter().flat_map(|(_, v)| v).collect();
    let in_use: BTreeSet<&str> = every
        .iter()
        .map(|(_, name)| name.as_str())
        .filter(|name| {
            name.split_once('-').is_some_and(|(_, s)| s == slug) && Some(*name) != moving.as_deref()
        })
        .collect();
    if !in_use.is_empty() {
        return Err(Stop::Refusal(format!(
            "slug {} is already in use: {} - a second directory with the same slug is a mistake nobody wants; pick another",
            repr(&slug),
            in_use.into_iter().collect::<Vec<_>>().join(", ")
        )));
    }
    let top = every.iter().map(|(n, _)| *n).max().unwrap_or(0);
    let name = format!("{:03}-{slug}", top + 1);
    let maxima = sources
        .iter()
        .map(|(k, v)| format!("{k}={:03}", v.iter().map(|(n, _)| *n).max().unwrap_or(0)))
        .collect::<Vec<_>>()
        .join("  ");
    if ask.dry_run {
        let _ = writeln!(err, "claim-feature: DRY RUN - next is {name}  ({maxima})");
        return Ok(name);
    }
    if let Some(from) = &moving {
        let (old, new) = (
            root.join("specs").join(from),
            root.join("specs").join(&name),
        );
        let moved = Command::new("git")
            .arg("-C")
            .arg(root)
            .arg("mv")
            .arg(&old)
            .arg(&new)
            .output()
            .is_ok_and(|o| o.status.success());
        if !moved {
            // untracked (a claim not yet committed): a plain rename is the same move
            std::fs::rename(&old, &new).map_err(raise)?;
        }
    } else {
        std::fs::create_dir_all(root.join("specs")).map_err(raise)?;
        std::fs::create_dir(root.join("specs").join(&name)).map_err(raise)?;
    }
    let mut row =
        json!({"number": top + 1, "slug": slug, "clone": py_name(root), "utc": utc_now()});
    if let Some(n) = old_number {
        row["renumbered_from"] = json!(n);
    }
    std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(mirror.join(".specify").join(LEDGER_NAME))
        .and_then(|mut f| f.write_all(format!("{}\n", dumps(&row, None, true)).as_bytes()))
        .map_err(raise)?;
    drop(held);
    if let Some(from) = &moving {
        let _ = writeln!(
            err,
            "claim-feature: renumbered specs/{from}/ -> specs/{name}/ in {}  ({maxima}); now fix every reference to the old number (grep for it) and commit the move",
            root.display()
        );
        return Ok(name);
    }
    let specify = root.join(".specify");
    if let Err(e) = std::fs::create_dir(&specify) {
        if !specify.is_dir() {
            return Err(raise(e));
        }
    }
    let pointer = json!({"feature_directory": format!("specs/{name}")});
    std::fs::write(
        specify.join("feature.json"),
        format!("{}\n", dumps(&pointer, Some(2), true)),
    )
    .map_err(raise)?;
    let _ = writeln!(
        err,
        "claim-feature: claimed specs/{name}/ in {}  ({maxima}); .specify/feature.json points at it",
        root.display()
    );
    // feature 377 (the GM, 2026-10-10): a feature is filed only with the GM's approval, and the commit guard holds it
    let _ = writeln!(
        err,
        "claim-feature: its spec.md needs the GM's approval, verbatim, on a line of its own - **Approved**: the GM, {}, \"<their words>\" - or no commit will take it (feature-approval-hooks.sh). Not approved yet? Propose it in your final message instead.",
        l7r_gate_core::record::bundle::today()
    );
    let _ = writeln!(err, "export SPECIFY_FEATURE={name}");
    let _ = writeln!(err, "export SPECIFY_FEATURE_DIRECTORY=specs/{name}");
    Ok(name)
}

/// `git rev-parse --show-toplevel` from `cwd`, as `repo_root` ran it with `check=True`.
fn repo_root(cwd: &Path) -> Result<PathBuf, String> {
    let out = Command::new("git")
        .args(["rev-parse", "--show-toplevel"])
        .current_dir(cwd)
        .output()
        .map_err(|e| e.to_string())?;
    if !out.status.success() {
        return Err(format!(
            "subprocess.CalledProcessError: Command '['git', 'rev-parse', '--show-toplevel']' returned non-zero exit status {}.",
            out.status.code().unwrap_or(-1)
        ));
    }
    Ok(PathBuf::from(strip(&String::from_utf8_lossy(&out.stdout))))
}

/// `l7r-gate claim [--dry-run] [--root DIR] [--main DIR] [--lock-timeout S] [--renumber specs/NNN-slug] [--] [slug]` from `cwd`.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    // argparse's `--`: what follows is positional; the parser below takes up to one positional before it
    let (head, tail) = args
        .iter()
        .position(|a| a == "--")
        .map_or((args, &[][..]), |i| (&args[..i], &args[i + 1..]));
    let specs = [
        Spec::value("--renumber"),
        Spec::flag("--dry-run"),
        Spec::value("--root"),
        Spec::value("--main"),
        Spec::value("--lock-timeout"),
    ];
    let usage = |why: &str| {
        reply(
            String::new(),
            format!("{USAGE}l7r-gate claim: error: {why}\n"),
            2,
        )
    };
    let mut parsed = match parse_with(head, &specs, 1) {
        Ok(p) => p,
        Err(why) => return usage(&why),
    };
    parsed.positional.extend(tail.iter().cloned());
    if parsed.positional.len() > 1 {
        return usage(&format!(
            "unrecognized arguments: {}",
            parsed.positional[1..].join(" ")
        ));
    }
    let timeout_text = parsed.text("--lock-timeout", "30.0");
    let Some(lock_timeout) = py_float_text(timeout_text) else {
        return usage(&format!(
            "argument --lock-timeout: invalid float value: {}",
            repr(timeout_text)
        ));
    };
    let slug = parsed.positional.first().cloned();
    let renumber = parsed
        .has("--renumber")
        .then(|| py_path(parsed.text("--renumber", "")));
    if slug.is_none() == renumber.is_none() {
        return reply(String::new(), "claim-feature: REFUSED - give exactly one of a slug (claim a new number) or --renumber specs/NNN-slug (move an existing directory to the next number)\n".to_owned(), 2);
    }
    let root = if parsed.has("--root") {
        resolved(&cwd.join(py_path(parsed.text("--root", ""))))
    } else {
        match repo_root(cwd) {
            Ok(r) => resolved(&r),
            Err(why) => return raised("claim", String::new(), "", &why),
        }
    };
    let mirror = if parsed.has("--main") {
        resolved(&cwd.join(py_path(parsed.text("--main", ""))))
    } else {
        resolved(&mirror_of(&root))
    };
    let ask = Ask {
        slug: slug.unwrap_or_default(),
        root: &root,
        mirror: &mirror,
        dry_run: parsed.on("--dry-run"),
        lock_timeout,
        move_from: renumber,
    };
    let mut err = String::new();
    match claim(&ask, &mut err) {
        Ok(name) => reply(format!("{name}\n"), err, 0),
        Err(Stop::Refusal(why)) => reply(
            String::new(),
            format!("{err}claim-feature: REFUSED - {why}\n"),
            2,
        ),
        Err(Stop::Raised(why)) => raised("claim", String::new(), &err, &why),
    }
}

#[cfg(test)]
mod tests;
