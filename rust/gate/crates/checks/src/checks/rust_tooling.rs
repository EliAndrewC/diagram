//! Every check that reads Python's syntax, `.py` or `.rs` files, or runs a Python-only tool, has its row in `dev/rust-tooling.md` (feature 444 FR-011; feature 449 T065, from `check-rust-tooling.py`), so that no such check goes
//! unlisted the silent way. A run is recorded by `usage_log` under `USAGE_LOG_TOOL`.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::Path;

use fancy_regex::Regex;

use super::{git_text, Outcome};

pub(super) const USAGE_LOG_TOOL: &str = "check-rust-tooling";
const INVENTORY: &str = "dev/rust-tooling.md";
const SKIP: [&str; 5] = [
    "specs/",
    "research/",
    "dev/",
    "pool/",
    "legacy-hand-authored-pool/",
];
const PROVEN_FATES: [&str; 4] = ["one for one", "partial", "rewritten", "replaced"];

fn pattern(text: &str) -> Regex {
    Regex::new(text).unwrap()
}

/// The tracked files that read Python's syntax tree or `.py` or `.rs` files.
fn readers(root: &Path, files: &[&str]) -> Vec<String> {
    let syntax = pattern(
        r"(?m)^\s*(?:import\s+(?:ast|tokenize|inspect|symtable)\b|from\s+(?:ast|tokenize|inspect|symtable)\s+import\b)",
    );
    let py = pattern(
        r#"["']\*\.py["']|endswith\(\s*["']\.py["']|suffix\s*==\s*["']\.py["']|-name\s+['"]\*\.py['"]|(?<![.\w])compile\("#,
    );
    let rs = pattern(
        r#"["']\*\.rs["']|endswith\(\s*["']\.rs["']|suffix\s*==\s*["']\.rs["']|-name\s+['"]\*\.rs['"]"#,
    );
    files
        .iter()
        .filter(|f| {
            !SKIP.iter().any(|s| f.starts_with(s))
                && (super::has_ext(f, "py") || super::has_ext(f, "sh"))
        })
        .filter(|f| {
            std::fs::read_to_string(root.join(f)).is_ok_and(|t| {
                [&syntax, &py, &rs]
                    .iter()
                    .any(|p| p.is_match(&t).unwrap_or(false))
            })
        })
        .map(|f| (*f).to_owned())
        .collect()
}

/// The Makefile targets whose recipe runs a Python-only tool or globs `*.py`.
fn tool_targets(makefile: &str) -> Vec<String> {
    let tools = pattern(
        r#"\b(?:ruff|pyrefly|pytest|coverage|testmon|vulture|rust_checks|cargo|clippy|rustfmt|llvm-cov)\b|["']\*\.py["']|-name\s+['"]\*\.py['"]"#,
    );
    let target = pattern(r"^([a-z][\w-]*)\s*:(?!=)");
    let mut recipes: BTreeMap<String, String> = BTreeMap::new();
    let mut current: Option<String> = None;
    for line in makefile.lines() {
        let found = (!line.starts_with('\t'))
            .then(|| {
                target
                    .captures(line)
                    .ok()
                    .flatten()
                    .and_then(|c| c.get(1).map(|m| m.as_str().to_owned()))
            })
            .flatten();
        if let Some(name) = found {
            recipes.entry(name.clone()).or_default();
            current = Some(name);
        } else if let (true, Some(name)) = (line.starts_with('\t'), &current) {
            let body = recipes.entry(name.clone()).or_default();
            body.push_str(line);
            body.push('\n');
        }
    }
    recipes
        .into_iter()
        .filter(|(_, r)| tools.is_match(r).unwrap_or(false))
        .map(|(t, _)| t)
        .collect()
}

/// Every key of the inventory's rows: the backticked items of each row's last cell.
fn keys(inventory: &str) -> Vec<String> {
    let mut out = Vec::new();
    for line in inventory
        .lines()
        .filter(|l| l.starts_with("| ") && !l.starts_with("| check |") && !l.starts_with("|---"))
    {
        let last = line
            .trim_end()
            .trim_end_matches('|')
            .rsplit('|')
            .next()
            .unwrap_or_default();
        let mut parts = last.split('`');
        parts.next();
        while let (Some(key), Some(_)) = (parts.next(), parts.next()) {
            out.push(key.to_owned());
        }
    }
    out
}

/// The inventory's rows of a proven fate that the "Proven on the fixture" table does not name exactly.
fn unproven(inventory: &str) -> Vec<String> {
    let (mut rows, mut proven, mut table) = (Vec::new(), BTreeSet::new(), "");
    for line in inventory.lines() {
        if line.starts_with("| check |") {
            table = "inventory";
        } else if line.starts_with("| row |") {
            table = "proven";
        } else if line.starts_with("| ") && !line.starts_with("|---") {
            let cells: Vec<&str> = line
                .trim()
                .trim_matches('|')
                .split('|')
                .map(str::trim)
                .collect();
            if table == "inventory"
                && cells.len() >= 5
                && PROVEN_FATES.iter().any(|f| cells[3].starts_with(f))
            {
                rows.push(cells[0].to_owned());
            } else if table == "proven" {
                proven.insert(cells[0].to_owned());
            }
        }
    }
    rows.into_iter().filter(|r| !proven.contains(r)).collect()
}

/// `fnmatch`: `*` and `?` over the whole text, `/` no different from any other character.
pub(super) fn fnmatches(text: &str, glob: &str) -> bool {
    let body: String = glob
        .chars()
        .map(|c| match c {
            '*' => ".*".to_owned(),
            '?' => ".".to_owned(),
            other => fancy_regex::escape(&other.to_string()).into_owned(),
        })
        .collect();
    pattern(&format!("(?s)^{body}$"))
        .is_match(text)
        .unwrap_or(false)
}

fn problems(root: &Path) -> Vec<String> {
    let listed = git_text(root, &["ls-files"]);
    let files: Vec<&str> = listed.split_whitespace().collect();
    let inventory = std::fs::read_to_string(root.join(INVENTORY)).ok();
    let have = inventory.as_deref().map(keys).unwrap_or_default();
    let paths: Vec<&String> = have.iter().filter(|k| !k.starts_with("make ")).collect();
    let targets: BTreeSet<String> = have
        .iter()
        .filter_map(|k| k.strip_prefix("make ").map(|t| t.trim().to_owned()))
        .collect();
    let mut out: Vec<String> = readers(root, &files).into_iter().filter(|f| !paths.iter().any(|k| fnmatches(f, k))).map(|f| format!("{f}: reads Python's syntax tree, or .py or .rs files, and no row of {INVENTORY} names it")).collect();
    if files
        .iter()
        .any(|f| f.starts_with("rust/") && super::has_ext(f, "rs"))
    {
        out.extend(inventory.as_deref().map(unproven).unwrap_or_default().into_iter().map(|r| format!("a Rust phase is in the tree, and the row `{r}` of {INVENTORY} is not proven - prove it on the phase (its check refuses a copy written to break it), then name it in the \"Proven on the fixture\" table")));
    }
    if let Ok(makefile) = std::fs::read_to_string(root.join("Makefile")) {
        out.extend(tool_targets(&makefile).into_iter().filter(|t| !targets.contains(t)).map(|t| format!("make {t}: its recipe runs a Python-only or Rust tool, and no row of {INVENTORY} names it")));
    }
    out
}

/// `l7r-gate check rust-tooling [--root ROOT]`.
pub(super) fn cli(args: &[String], root: &Path) -> Outcome {
    let root = args
        .iter()
        .position(|a| a == "--root")
        .and_then(|at| args.get(at + 1))
        .map_or(root, |r| Path::new(r));
    let bad = problems(root);
    if bad.is_empty() {
        return Outcome::out(format!(
            "rust-tooling: every Python-only check has its row in {INVENTORY}\n"
        ));
    }
    let mut err = String::new();
    for b in &bad {
        let _ = writeln!(err, "rust-tooling: {b}");
    }
    let _ = writeln!(err, "rust-tooling: add a row to {INVENTORY} - | check | today (Python) | in the Rust phases | fate (one for one, partial, rewritten, replaced, dropped or unchanged) | keys (`<path or glob>` or `make <target>`) | - or name it in an existing row's keys");
    Outcome::refuse(err)
}

#[cfg(test)]
mod tests;
