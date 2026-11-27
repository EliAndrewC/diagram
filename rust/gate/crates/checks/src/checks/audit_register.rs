//! The audit register (feature 451 T259; `specs/449-rust-codebase/port-talk-agenda.md` item 13, the GM 2026-11-25: "when we make this
//! kind of optimization, then we should be documenting the logic behind it, the measurements that we took, and then also crucially
//! what we would look at that would falsify the notion that this is a good idea"). One Markdown file per entry under `dev/audits/`,
//! its fields a front matter of `key: value` lines between `---` lines, its reasoning the prose below - Markdown because an entry is
//! mostly prose the GM reads, and a `key: value` front matter needs no parser the crate does not already have (JSON would hold the
//! reasoning as escaped strings). An entry is of one of two kinds (`kind:`): `adopted`, a mechanism in force, or `declined`, an option weighed
//! and not built - its `measurement` what declined it and its `falsifier` what would reopen it (the GM 2026-11-25: "We should also make
//! sure our processes record decisions about what NOT to implement for future reference in the same way we record decisions about the
//! processes and tooling we DO implement."). `l7r-gate check audit-register`:
//!
//! - `--delta ROOT` (`make static` and the push): every entry well formed, and each guard module, numeric threshold, gate-chain make
//!   target, landing step (a script newly called from a landing recipe among them, 451 T269) and agent file the delta adds
//!   (`detect.rs`) named by an entry's `covers:` line; else refused with the entry to write.
//!   `AUDIT_ENTRY_OK="<reason>"` passes it, recorded in the guard log;
//! - `--range BASE HEAD [--root R] [--empty-register]`: the same over a past delta, the register read from HEAD (or none) - the replay
//!   that measures whether it fires on correct work;
//! - `--list [--root R] [--today YYYY-MM-DD]` (`make audits`): every entry, the overdue first by its cadence, each with its falsifier
//!   and last audit;
//! - `--selftest`.

use std::fmt::Write as _;
use std::path::Path;
use std::process::Command;

use super::Outcome;

mod detect;

use detect::{Head, Item};

/// The name its runs are recorded under in the `usage_log`.
pub(super) const USAGE_LOG_TOOL: &str = "check-audit-register";
/// The register's directory.
const DIR: &str = "dev/audits";
/// git's empty tree: the base `make audits` reads the whole tree's mechanisms against, for the backfill.
const EMPTY_TREE: &str = "4b825dc642cb6eb9a060e54bf8d69288fbee4904";
/// The escape, whose value is its reason.
const ESCAPE: &str = "AUDIT_ENTRY_OK";
/// The fields every entry holds, in the order an entry writes them.
const FIELDS: [&str; 11] = [
    "kind",
    "title",
    "for",
    "measured",
    "measurement",
    "command",
    "falsifier",
    "threshold",
    "cost",
    "last-audited",
    "cadence-days",
];

/// One entry, as read.
#[derive(Debug, Default)]
struct Entry {
    file: String,
    fields: Vec<(String, String)>,
    covers: Vec<String>,
}

impl Entry {
    fn get(&self, key: &str) -> &str {
        self.fields
            .iter()
            .find(|(k, _)| k == key)
            .map_or("", |(_, v)| v.as_str())
    }
}

/// An entry's text read: its front matter's fields, its `covers:` lines apart.
fn parse(file: &str, text: &str) -> Entry {
    let mut entry = Entry {
        file: file.to_owned(),
        ..Entry::default()
    };
    let mut lines = text.lines();
    if lines.next().map(str::trim) != Some("---") {
        return entry;
    }
    for line in lines {
        if line.trim() == "---" {
            break;
        }
        let Some((key, value)) = line.split_once(':') else {
            continue;
        };
        let (key, value) = (key.trim().to_owned(), value.trim().to_owned());
        if key == "covers" {
            if !value.is_empty() {
                entry.covers.push(value);
            }
        } else {
            entry.fields.push((key, value));
        }
    }
    entry
}

/// The days since 1970-01-01 of a `YYYY-MM-DD` date, or None.
fn days(date: &str) -> Option<i64> {
    let mut parts = date.splitn(3, '-').map(str::parse::<i64>);
    let (y, m, d) = (
        parts.next()?.ok()?,
        parts.next()?.ok()?,
        parts.next()?.ok()?,
    );
    if date.len() != 10 || !(1..=12).contains(&m) || !(1..=31).contains(&d) {
        return None;
    }
    // Howard Hinnant's days_from_civil
    let y = if m <= 2 { y - 1 } else { y };
    let era = y.div_euclid(400);
    let year_of_era = y - era * 400;
    let month_shift = (m + 9) % 12;
    let day_of_year = (153 * month_shift + 2) / 5 + d - 1;
    let day_of_era = year_of_era * 365 + year_of_era / 4 - year_of_era / 100 + day_of_year;
    Some(era * 146_097 + day_of_era - 719_468)
}

/// What is wrong with an entry's form: each a line, empty when it is well formed.
fn problems(entry: &Entry) -> Vec<String> {
    let mut out = Vec::new();
    for key in FIELDS {
        if entry.get(key).is_empty() {
            out.push(format!("{}: `{key}:` is missing or empty", entry.file));
        }
    }
    let kind = entry.get("kind");
    if !kind.is_empty() && kind != "adopted" && kind != "declined" {
        out.push(format!("{}: `kind:` is `adopted` (in force) or `declined` (weighed and not built), not `{kind}`", entry.file));
    }
    let measured = entry.get("measured");
    if measured == "unmeasured" {
        if entry.get("first-audit").is_empty() {
            out.push(format!("{}: `measured: unmeasured` names its first audit in `first-audit:` (the measurement that will be its first)", entry.file));
        }
    } else if !measured.is_empty() && days(measured).is_none() {
        out.push(format!(
            "{}: `measured:` is a date YYYY-MM-DD or `unmeasured`, not `{measured}`",
            entry.file
        ));
    }
    let last = entry.get("last-audited");
    if !last.is_empty() && last != "never" && days(last).is_none() {
        out.push(format!(
            "{}: `last-audited:` is a date YYYY-MM-DD or `never`, not `{last}`",
            entry.file
        ));
    }
    let cadence = entry.get("cadence-days");
    if !cadence.is_empty() && cadence.parse::<u32>().map_or(true, |c| c == 0) {
        out.push(format!(
            "{}: `cadence-days:` is a whole number of days above 0, not `{cadence}`",
            entry.file
        ));
    }
    out
}

/// The register's entries in the working tree, by file name.
fn read_tree(root: &Path) -> Vec<Entry> {
    let Ok(dir) = std::fs::read_dir(root.join(DIR)) else {
        return Vec::new();
    };
    let mut files: Vec<String> = dir
        .map_while(Result::ok)
        .filter_map(|e| e.file_name().to_str().map(str::to_owned))
        .filter(|n| detect::is_markdown(n))
        .collect();
    files.sort();
    files
        .iter()
        .map(|f| {
            let rel = format!("{DIR}/{f}");
            parse(
                &rel,
                &std::fs::read_to_string(root.join(&rel)).unwrap_or_default(),
            )
        })
        .collect()
}

fn git(root: &Path, args: &[&str]) -> String {
    Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
        .unwrap_or_default()
}

/// The register's entries at a commit.
fn read_rev(root: &Path, rev: &str) -> Vec<Entry> {
    git(root, &["ls-tree", "--name-only", &format!("{rev}:{DIR}")])
        .lines()
        .filter(|n| detect::is_markdown(n))
        .map(|n| {
            let path = format!("{DIR}/{n}");
            parse(&path, &git(root, &["show", &format!("{rev}:{path}")]))
        })
        .collect()
}

/// The items no entry's `covers:` line names.
fn uncovered(items: Vec<Item>, entries: &[Entry]) -> Vec<Item> {
    items
        .into_iter()
        .filter(|i| !entries.iter().any(|e| e.covers.contains(&i.name)))
        .collect()
}

/// The refusal: each malformed entry, each item with no entry, and the entry to write.
fn refusal(bad: &[String], missing: &[Item]) -> String {
    let mut err = String::new();
    for line in bad {
        let _ = writeln!(err, "audit-register: {line}");
    }
    for item in missing {
        let _ = writeln!(err, "audit-register: this delta adds a {} `{}` that no entry under {DIR}/ names in a `covers:` line", item.kind, item.name);
    }
    if !missing.is_empty() {
        let _ = writeln!(err, "audit-register: write {DIR}/<slug>.md (or add a `covers:` line to the entry it belongs to), as the others are written:");
        let _ = writeln!(err, "---");
        for key in FIELDS {
            let _ = writeln!(err, "{key}: <{}>", hint(key));
        }
        for item in missing {
            let _ = writeln!(err, "covers: {}", item.name);
        }
        let _ = writeln!(err, "---\n<the reasoning: why it exists, what was weighed>");
    }
    let _ = writeln!(err, "audit-register: an optimization or procedure that costs time or tokens arrives with its measurement and its falsifier (451 T259, the GM 2026-11-25); `make audits` lists the register. A thing this misreads as one: {ESCAPE}=\"<reason>\" (recorded)");
    err
}

/// What a field holds, for the refusal's skeleton.
fn hint(key: &str) -> &'static str {
    match key {
        "kind" => "adopted (in force) or declined (weighed and not built: then measurement is what declined it, falsifier what would reopen it)",
        "title" => "what it is, in a few words",
        "for" => "the outcome it buys, in the world",
        "measured" => "YYYY-MM-DD of the measurement that justified it, or unmeasured (then first-audit: <the measurement that will be>)",
        "measurement" => "the figures, with their method",
        "command" => "the command that reproduces it",
        "falsifier" => "the measurement that would show it costs more than it saves",
        "threshold" => "the falsifier's number (GUESS where no record states one)",
        "cost" => "where make task-time books its cost",
        "last-audited" => "YYYY-MM-DD, or never",
        _ => "a whole number of days between audits",
    }
}

/// Today's date, `YYYY-MM-DD`, in UTC.
fn today() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, m, d, ..) = l7r_shared::log::civil(secs);
    format!("{y:04}-{m:02}-{d:02}")
}

/// `make audits`: every entry, the overdue first (most overdue first), then by the day each falls due.
fn list(entries: &[Entry], today: &str, backfill: &[Item]) -> String {
    let now = days(today).unwrap_or_default();
    let mut rows: Vec<(i64, &Entry)> = entries
        .iter()
        .map(|e| {
            let cadence = e.get("cadence-days").parse::<i64>().unwrap_or(1);
            let due = days(e.get("last-audited")).map_or(i64::MIN, |d| d + cadence);
            (due, e)
        })
        .collect();
    rows.sort_by_key(|(due, e)| (*due, e.file.clone()));
    let overdue = rows.iter().filter(|(due, _)| *due < now).count();
    let mut out = format!(
        "audits: {} entries in {DIR}/, {overdue} overdue (today {today})\n",
        rows.len()
    );
    for (due, e) in rows {
        let when = if due == i64::MIN {
            "NEVER AUDITED".to_owned()
        } else if due < now {
            format!("OVERDUE by {} d", now - due)
        } else {
            format!("due in {} d", due - now)
        };
        let _ = writeln!(
            out,
            "\n{when}  [{}] {}  ({})",
            e.get("kind"),
            e.get("title"),
            e.file
        );
        let _ = writeln!(
            out,
            "    last audited {}, every {} d; measured {}",
            e.get("last-audited"),
            e.get("cadence-days"),
            e.get("measured")
        );
        let _ = writeln!(out, "    falsifier: {}", e.get("falsifier"));
        let _ = writeln!(out, "    threshold: {}", e.get("threshold"));
        for bad in problems(e) {
            let _ = writeln!(out, "    MALFORMED: {bad}");
        }
    }
    if !backfill.is_empty() {
        let _ = writeln!(out, "\nBACKFILL: {} mechanism(s) in force that no entry names yet (the detectors over the whole tree, {EMPTY_TREE}..the tree; agenda item 13's backfill, to be written by cost):", backfill.len());
        for item in backfill {
            let _ = writeln!(out, "    {}: {}", item.kind, item.name);
        }
    }
    out
}

/// The judgment over a delta's items and a register.
fn judge(items: Vec<Item>, entries: &[Entry]) -> Result<usize, String> {
    let bad: Vec<String> = entries.iter().flat_map(problems).collect();
    let count = items.len();
    let missing = uncovered(items, entries);
    if bad.is_empty() && missing.is_empty() {
        Ok(count)
    } else {
        Err(refusal(&bad, &missing))
    }
}

/// The merge base the push judges against (HEAD where there is none); at a hand-in, the base it names (`l7r_gate_core::delta_base`,
/// 461 T37).
fn base(root: &Path) -> String {
    let base = l7r_gate_core::delta_base::named(root)
        .unwrap_or_else(|| git(root, &["merge-base", "HEAD", "origin/main"]));
    let base = base.trim();
    if base.is_empty() {
        "HEAD".to_owned()
    } else {
        base.to_owned()
    }
}

/// `--delta ROOT`, the escape read from `escape`.
fn delta(root: &Path, escape: Option<&str>, log: &Path) -> Outcome {
    let entries = read_tree(root);
    match judge(detect::items(root, &base(root), &Head::Tree), &entries) {
        Ok(n) => Outcome::out(format!("audit-register: {} entries well formed; the delta's {n} mechanism(s) each named by one\n", entries.len())),
        Err(why) => match escape {
            Some(reason) if l7r_shared::escape::enough(reason) => {
                record(log, "escaped", reason);
                Outcome::out(format!("audit-register: ESCAPED ({ESCAPE}: {reason}) - it would have refused:\n{why}"))
            }
            Some(reason) => {
                record(log, "blocked", reason);
                Outcome::refuse(format!("{why}audit-register: {ESCAPE} needs a reason of two words and eight characters, not `{reason}`\n"))
            }
            None => {
                record(log, "blocked", "");
                Outcome::refuse(why)
            }
        },
    }
}

/// A firing, recorded in the guard log.
fn record(log: &Path, event: &str, detail: &str) {
    let _ = l7r_shared::log::write_at(
        log,
        &l7r_shared::log::Entry {
            guard: "audit-register",
            event,
            detail,
            rule: "an-entry-per-mechanism",
            context: None,
            input: &serde_json::Value::Null,
            session_name: "",
        },
        std::time::SystemTime::now(),
    );
}

/// `--range BASE HEAD`: the replay over a past delta.
fn range(root: &Path, base: &str, head: &str, empty: bool) -> Outcome {
    let entries = if empty {
        Vec::new()
    } else {
        read_rev(root, head)
    };
    let items = detect::items(root, base, &Head::Rev(head));
    let mut out = format!("audit-register: {base}..{head}: {} item(s)\n", items.len());
    for item in &items {
        let _ = writeln!(out, "  {}: {}", item.kind, item.name);
    }
    match judge(items, &entries) {
        Ok(_) => Outcome::out(out),
        Err(why) => Outcome {
            stdout: out,
            stderr: why,
            code: 1,
        },
    }
}

/// The self-test: the readers on known text.
fn selftest() -> Outcome {
    let make = "done: export X := 1\ndone: static ## help\n\t$(MAKE) --no-print-directory _quick || exit 1\n_quick:\n\t@true\nstatic:\n\t@x\nother:\n\t@y\n";
    let reach = detect::chain_reach(make);
    let entry = parse("e.md", "---\nkind: adopted\ntitle: t\nfor: f\nmeasured: unmeasured\nmeasurement: m\ncommand: c\nfalsifier: f\nthreshold: t\ncost: c\nlast-audited: never\ncadence-days: 7\ncovers: CAP_X\n---\nwhy\n");
    let passed = detect::const_name("pub(crate) const CAP_X: u64 = 3;") == Some("CAP_X")
        && detect::const_name("    const CAP_X: u64 = 3;").is_none()
        && detect::const_name("const NAME: &str = \"x\";").is_none()
        && detect::is_guard_module("rust/guard/src/guards/x_hooks.rs")
        && !detect::is_guard_module("rust/guard/src/guards/x_hooks/part.rs")
        && reach.contains("_quick")
        && !reach.contains("other")
        && problems(&entry).len() == 1
        && uncovered(
            vec![Item {
                kind: "numeric constant",
                name: "CAP_X".to_owned(),
            }],
            &[entry],
        )
        .is_empty();
    Outcome::selftest(passed, "audit-register selftest passed\n", "audit-register selftest FAILED - the check itself is broken; fix rust/gate/crates/checks/src/checks/audit_register.rs\n".to_owned())
}

/// `l7r-gate check audit-register --delta ROOT | --range BASE HEAD [--root R] [--empty-register] | --list [--root R] [--today D] | --selftest`.
pub(super) fn cli(args: &[String], root: &Path) -> Outcome {
    let after = |flag: &str, n: usize| {
        args.iter()
            .position(|a| a == flag)
            .and_then(|at| args.get(at + n))
            .map(String::as_str)
    };
    let root = after("--root", 1).map_or(root, Path::new);
    match args.first().map(String::as_str) {
        Some("--selftest") => selftest(),
        Some("--delta") => match args.get(1) {
            Some(r) => delta(Path::new(r), std::env::var(ESCAPE).ok().as_deref(), &l7r_shared::log::dir()),
            None => Outcome::usage("usage: l7r-gate check audit-register --delta ROOT\n"),
        },
        Some("--range") => match (args.get(1), args.get(2)) {
            (Some(b), Some(h)) => range(root, b, h, args.iter().any(|a| a == "--empty-register")),
            _ => Outcome::usage("usage: l7r-gate check audit-register --range BASE HEAD [--root R] [--empty-register]\n"),
        },
        Some("--list") => {
            let entries = read_tree(root);
            let backfill = uncovered(detect::items(root, EMPTY_TREE, &Head::Tree), &entries);
            Outcome::out(list(&entries, after("--today", 1).map_or_else(today, str::to_owned).as_str(), &backfill))
        }
        _ => Outcome::usage("usage: l7r-gate check audit-register --delta ROOT | --range BASE HEAD [--root R] [--empty-register] | --list [--root R] [--today YYYY-MM-DD] | --selftest\n"),
    }
}

#[cfg(test)]
mod tests;
